"""Run only our full-project helper-lab client; preserve exact pinned real samples.

No input EXE or game DLL is executed. The lab-specific WinMain bypasses normal
engine/GPU/network initialization and original game teardown. Math instruction
identity is proved separately; normal game startup FPU state remains unverified.
"""
import argparse
import hashlib
import json
import os
import shutil
import struct
import subprocess
from pathlib import Path
from compare_client_binaries import WS, pe
from helper_spt import Helper,parse,encode
from apply_client_helper455 import binary_evidence

HEADER = struct.Struct('<8s14I')
USE = struct.Struct('<6f4I')
DELAYED = {'mss32.dll','abuse.dll','adv.dll','pdll.dll'}


def f32(x):
    return struct.unpack('<f',struct.pack('<f',x))[0]


def transform(pos, matrix):
    # Independent binary64 intermediates for the observed x87 PC53/nearest mode.
    # Reference instruction order starts with y*column[1] + x*column[0].
    return tuple(f32(((matrix[j+4]*pos[1]+matrix[j]*pos[0])+
                      matrix[j+8]*pos[2])+matrix[j+12]) for j in range(3))


def import_names(data, index):
    image=pe(data)
    header=struct.unpack_from('<I',data,0x3c)[0]
    if index not in (1,13) or struct.unpack_from('<H',data,header+20)[0]<96+(index+1)*8:
        raise ValueError('Missing or unsupported import directory')
    at=header+24
    rva,size=struct.unpack_from('<II',data,at+96+index*8)
    def offset(value,extent=1):
        s=next((s for s in image['sections'] if s['rva']<=value<s['rva']+s['raw_size']),None)
        if s is None or extent<0 or value+extent>s['rva']+s['raw_size']:
            raise ValueError('Import range outside stored section')
        position=s['raw_offset']+value-s['rva']
        end=s['raw_offset']+s['raw_size']
        if position+extent>len(data) or end>len(data):
            raise ValueError('Truncated import section')
        return position,end
    if not size: return []
    cursor,_=offset(rva,size)
    stride=20 if index==1 else 32
    result=[]
    end=cursor+size
    while cursor+stride<=end:
        descriptor=data[cursor:cursor+stride]
        if not any(descriptor): return result
        name=struct.unpack_from('<I',descriptor,12 if index==1 else 4)[0]
        if index==13 and struct.unpack_from('<I',descriptor)[0]!=1:
            raise ValueError('Expected RVA-based delay imports')
        start,boundary=offset(name)
        terminator=data.find(b'\0',start,boundary)
        if terminator<0: raise ValueError('Unterminated DLL name')
        result.append(data[start:terminator].decode('ascii').lower())
        cursor+=stride
    raise ValueError('Missing import descriptor terminator')


def read_output(path):
    data=path.read_bytes()
    magic,*values=HEADER.unpack_from(data)
    names=['version','loaded','count','record_bytes','use_bytes','checks','failures',
           'missing_called','count_after_missing','clamp_matches','memory_before','memory_after',
           'fp_before','fp_after']
    header=dict(zip(names,values))
    if magic!=b'RFHLP455' or header['version']!=2 or header['record_bytes']!=208 or header['use_bytes']!=40:
        raise ValueError('Unexpected helper-lab output header')
    if len(data)!=HEADER.size+header['count']*248 or header['failures']:
        raise ValueError(f'Incomplete or failed native result: {header}')
    if header['fp_before']!=header['fp_after'] or header['fp_before']&0xf00!=0x200:
        raise ValueError(f'Independent scalar comparison requires unchanged PC53/nearest: {header}')
    records=[]
    for i in range(header['count']):
        at=HEADER.size+248*i
        raw=data[at:at+208]
        records.append({'raw':raw,'name':raw[:32].split(b'\0')[0],
            'flags':struct.unpack_from('<I',raw,32)[0],
            'bounds':struct.unpack_from('<6f',raw,36),
            'id':struct.unpack_from('<I',raw,60)[0],
            'argv':raw[64:80],'matrix':struct.unpack_from('<16f',raw,80),
            'inverse':struct.unpack_from('<16f',raw,144),'use':USE.unpack_from(data,at+208)})
    return header,records


def main():
    cli=argparse.ArgumentParser()
    cli.add_argument('--limit',type=int,default=0,help='Debug real-sample limit; not a completed audit')
    args=cli.parse_args()
    evidence=binary_evidence()
    build=json.loads((WS/'inventory/client-helper-lab-build.json').read_text(encoding='utf-8'))
    if build['build_exit'] or build['unresolved_symbols'] or build['generated_objects']!=181:
        raise ValueError('A successful complete-project helper-lab build is required')
    if build.get('compiler_flags',{}).get('CMAKE_CXX_FLAGS_RELEASE')!='/O2 /Ob2 /DNDEBUG':
        raise ValueError('Lab engine must use the explicit production Release flags')
    if any(build['build_settings'].get(k)!='ON' for k in ['RF_CLIENT_455_HELPER_LOADER','RF_CLIENT_HELPER_LAB','RF_CLIENT_455_X87_MATH']):
        raise ValueError('Missing 455 loader/lab build selection')
    if len(build.get('lab_input_sha256',{}))!=4:
        raise ValueError('Lab build input hashes are missing')
    for path,digest in build['lab_input_sha256'].items():
        if hashlib.sha256((WS/path).read_bytes()).hexdigest()!=digest:
            raise ValueError(f'Lab build input changed: {path}')
    exe=WS/'work/client-build/build-helper-lab/Release/RF_Online.bin'
    data=exe.read_bytes()
    image=pe(data)
    linked=json.loads((WS/'inventory/client455-x87-link.json').read_text(encoding='utf-8'))['lab']
    if linked['sha256']!=hashlib.sha256(data).hexdigest():
        raise ValueError('Run verify_client_x87_math455.py --lab for the current binary')
    direct,delayed=import_names(data,1),import_names(data,13)
    if set(delayed)!=DELAYED or set(direct)&DELAYED:
        raise ValueError('Input game DLLs must only be delay imports in the lab')
    system={'kernel32.dll','user32.dll','gdi32.dll','advapi32.dll','d3d8.dll',
            'dinput8.dll','winmm.dll','ws2_32.dll','imm32.dll','comdlg32.dll'}
    if set(direct)-system:
        raise ValueError(f'Unexpected eager lab DLL: {set(direct)-system}')
    math_proof=json.loads((WS/'inventory/client455-x87-math.json').read_text(encoding='utf-8'))
    math_library=WS/math_proof['library']
    if hashlib.sha256(math_library.read_bytes()).hexdigest()!=math_proof['library_sha256']:
        raise ValueError('Verified x87 library changed')
    if Path(build['build_settings']['RF_CLIENT_455_X87_MATH_LIBRARY']).resolve()!=math_library.resolve():
        raise ValueError('Lab did not select the verified x87 library')
    lab=WS/'work/client-helper-lab/revisions'/hashlib.sha256(data).hexdigest()[:16]
    lab.mkdir(parents=True,exist_ok=True)
    if any(lab.rglob('*.dll')) or any(exe.parent.glob('*.dll')):
        raise ValueError('The helper lab must contain no local DLL providers')
    identity=(1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.)
    fixtures=[]
    for count in [0,1,15,16,17,47,48,49,80]:
        helpers=[Helper((('UPPERCASE_%03d_'%i)+'X'*35).encode(),(-1.,-2.,-3.,1.,2.,3.),identity) for i in range(count)]
        fixtures.append((f'capacity-{count}',encode(helpers),helpers,None,True))
    fixture=(b'ignored header script_begin [HelperObjectBegin] '
        b'*FIRST -1 -2 -3 1 2 3 -node_tm 1 0 0 0 0 1 0 0 0 0 1 0 10 20 30 1 '
        b'-id -1 -music -interior -fog_start 10 -fog_color 1 2 3 -fog_end 20 '
        b'*SECOND -1 -2 -3 1 2 3 -node_tm 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 '
        b'-fog_color 255 128 64 '
        b'* 0 0 0 1 1 1 -unknown [HelperObjectEnd] script_end')
    fixtures.append(('options-and-defaults',fixture,None,'options',True))
    fixtures.extend([('no-begin',b'no script begin here',[],None,False),
                     ('empty-input',b'',[],None,False)])
    records_report=[]
    total_checks=0
    total_helpers=0
    max_roundtrip_error=0.0
    center_outside=0

    def run(label,raw,expected,mode=None,loaded=True,original=None):
        nonlocal total_checks,total_helpers,max_roundtrip_error,center_outside
        folder=lab/label
        folder.mkdir(parents=True,exist_ok=True)
        source=folder/'input.spt'; output=folder/'output.bin'
        source.write_bytes(raw)
        if output.exists(): output.unlink()
        missing=folder/'deliberately-missing.spt'
        if missing.exists(): raise ValueError('Missing fixture unexpectedly exists')
        env=os.environ.copy()
        env.update(RF_LAB_HELPER_INPUT=str(source),RF_LAB_HELPER_OUTPUT=str(output),RF_LAB_HELPER_MISSING=str(missing))
        process=subprocess.run([str(exe),'--rf-helper-probe'],cwd=folder,env=env,
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
        if process.returncode:
            raise ValueError(f'{label}: helper-lab process exit {process.returncode:#x}')
        header,items=read_output(output)
        if header['loaded']!=int(loaded) or not header['missing_called'] or header['count_after_missing']:
            raise ValueError(f'{label}: loader/reset status changed')
        checks=0
        def check(ok,message):
            nonlocal checks
            checks+=1
            if not ok: raise ValueError(f'{label}: {message}')
        if expected is not None:
            check(len(items)==len(expected),'count')
            for item,ref in zip(items,expected):
                check(item['name']==ref.legacy_name,'lowercase/truncation')
                check(item['raw'][36:60]==struct.pack('<6f',*ref.bounds),'bounds float32 bits')
                check(item['raw'][80:144]==struct.pack('<16f',*ref.matrix),'matrix float32 bits')
                check(item['flags']==0 and item['id']==0 and item['argv']==bytes(16),'zero record defaults')
        if mode=='options':
            check(len(items)==3,'options count')
            check([item['name'] for item in items]==[b'first',b'second',b''],'all record names')
            check(items[0]['flags']==7 and items[0]['id']==0xffffffff,'music/interior/fog/id')
            check(items[0]['argv']==struct.pack('<IffI',0xff010203,123.5,20.,0),'option ordering/fog defaults')
            check(items[1]['argv']==struct.pack('<IffI',0xffff8040,123.5,987.25,0),'second fog defaults')
            check(items[2]['raw'][80:144]==struct.pack('<16f',*identity),'identity default')
            check(items[2]['raw'][144:208]==bytes(64),'absent node_tm keeps zero inverse')
        for item in items:
            use=item['use']; lo,hi=item['bounds'][:3],item['bounds'][3:]
            center=tuple(f32(f32(f32(a+b)*0.5)+f32(f32(b-a)*0.125)) for a,b in zip(lo,hi))
            outside=tuple(f32(f32(b+abs(f32(b-a)))+1.) for a,b in zip(lo,hi))
            world=transform(center,item['matrix'])
            local=transform(world,item['inverse'])
            local_out=transform(transform(outside,item['matrix']),item['inverse'])
            check(struct.pack('<3f',*use[:3])==struct.pack('<3f',*world),'world transform float32 bits')
            check(struct.pack('<3f',*use[3:6])==struct.pack('<3f',*local),'local transform float32 bits')
            check(use[6]==int(all(a<=p<=b for a,p,b in zip(lo,local,hi))),'bbox interior-point classification')
            check(use[7]==int(all(a<=p<=b for a,p,b in zip(lo,local_out,hi))),'bbox outside classification')
            check(use[8:]==(1,1),'valid-index transform success')
            if not use[6]: center_outside+=1
            if item['inverse'][15]==1:
                for r in range(4):
                    for c in range(4):
                        value=sum(item['matrix'][r*4+k]*item['inverse'][k*4+c] for k in range(4))
                        tolerance=0.03 if r==3 else 0.00005
                        check(abs(value-(1. if r==c else 0.))<=tolerance,'matrix * inverse identity tolerance')
                max_roundtrip_error=max(max_roundtrip_error,*[abs(a-b) for a,b in zip(center,local)])
        total_checks+=checks+header['checks']
        total_helpers+=len(items)
        return {'case':label,'path':original,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),
            'helpers':len(items),'native_checks':header['checks'],'comparison_checks':checks,
            'output_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'fp_control':hex(header['fp_before'])}

    for label,raw,expected,mode,loaded in fixtures:
        records_report.append(run('fixtures/'+label,raw,expected,mode,loaded))
    samples=json.loads((WS/'inventory/helper-spt-verification.json').read_text(encoding='utf-8'))['files']
    paths=json.loads((WS/'config/paths.json').read_text(encoding='utf-8'))
    selected=samples[:args.limit] if args.limit else samples
    for i,sample in enumerate(selected):
        raw=(Path(paths['client_455'])/sample['path']).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=sample['sha256']:
            raise ValueError('Pinned helper sample changed')
        records_report.append(run(f'real/{i:03}',raw,parse(raw),original=sample['path']))
        if (i+1)%20==0: print(f'Native helper files: {i+1}/{len(selected)}',flush=True)
    snapshot=lab/'RF_Online.bin'
    shutil.copyfile(exe,snapshot)
    report={'complete_real_sample_audit':not args.limit,'real_files':len(selected),
        'fixtures':len(fixtures),'helpers_including_fixtures':total_helpers,'checks':total_checks,
        'exe':snapshot.relative_to(WS).as_posix(),'exe_sha256':hashlib.sha256(data).hexdigest(),
        'architecture':image['architecture'],'image_base':hex(image['image_base']),'entry_rva':hex(image['entry_rva']),
        'direct_imports':direct,'delayed_imports':delayed,
        'lab_source_sha256':hashlib.sha256((WS/'scripts/native/client_helper_lab.cpp').read_bytes()).hexdigest(),
        'binary_evidence':evidence,'math_proof':'inventory/client455-x87-math.json',
        'max_world_local_error':max_roundtrip_error,
        'probe_point_classified_outside':center_outside,'cases':records_report,
        'limits':'Own full-project CPU-only laboratory entry, not normal LoadLevel/GPU/network startup. Original input EXEs/DLLs not executed. Two math functions match reference instruction bytes under equal x87 environment; actual game startup FPU environment, OOM, unsafe malformed inputs, non-ASCII locale and complete map path not established.'}
    output=WS/('artifacts/client-helper-lab/limited-probe.json' if args.limit else 'inventory/client-helper-runtime.json')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'PASS: {len(selected)} real files, {len(fixtures)} fixtures, {total_checks} native/comparison checks. Normal game startup not run.')


if __name__=='__main__': main()
