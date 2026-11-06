"""Read own PE imports/providers and startup contract inputs;never execute inputs."""
import hashlib,json,struct
from pathlib import Path
from compare_client_binaries import WS,pe
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def string(raw,rva):
    base=pe(raw)['image_base'];value=bytearray()
    for i in range(2048):
        b=read_va(raw,base+rva+i,1)
        if not b[0]:return value.decode('ascii')
        value+=b
    raise ValueError('Unterminated PE name')
def directory(raw,index):
    nt=struct.unpack_from('<I',raw,0x3c)[0]
    return struct.unpack_from('<II',raw,nt+24+96+8*index)
def imports(raw,delay=False):
    image=pe(raw);base=image['image_base'];start,size=directory(raw,13 if delay else 1);result=[]
    if not start:return result
    stride=32 if delay else 20
    for at in range(start,start+size,stride):
        record=struct.unpack('<'+('8I' if delay else '5I'),read_va(raw,base+at,stride))
        if not any(record):break
        if delay:
            attrs,name,handle,iat,lookup,bound,unload,stamp=record
            if attrs&1==0:name-=base;iat-=base;lookup-=base
        else:lookup,stamp,forward,name,iat=record;lookup=lookup or iat
        entries=[];index=0
        while True:
            value=struct.unpack('<I',read_va(raw,base+lookup+4*index,4))[0]
            if not value:break
            if value&0x80000000:entry={'ordinal':value&0xffff}
            else:entry={'name':string(raw,value+2)}
            entry['iat_rva']=hex(iat+4*index);entries.append(entry);index+=1
        result.append({'dll':string(raw,name).lower(),'delayed':delay,'imports':entries})
    return result
def exported(raw):
    image=pe(raw);base=image['image_base'];rva,size=directory(raw,0)
    if not rva:return {},{}
    d=struct.unpack('<IIHH7I',read_va(raw,base+rva,40));ordinalBase,count,names,functions,nameTable,ordinals=d[5:]
    values={ordinalBase+i:struct.unpack('<I',read_va(raw,base+functions+4*i,4))[0] for i in range(count)}
    named={string(raw,struct.unpack('<I',read_va(raw,base+nameTable+4*i,4))[0]):values[ordinalBase+struct.unpack('<H',read_va(raw,base+ordinals+2*i,2))[0]] for i in range(names)}
    return named,values
def main():
    link=json.loads((WS/'inventory/client455-normal-link.json').read_text());validate_normal_link(link);exe=WS/link['executable']['file'];raw=exe.read_bytes();paths=json.loads((WS/'config/paths.json').read_text());client=Path(paths['client_455']);modules=imports(raw)+imports(raw,True);missing=[]
    for module in modules:
        local=client/module['dll'];system=Path('C:/Windows/SysWOW64')/module['dll']
        provider=(local if local.is_file() else system) if module['delayed'] else (system if system.is_file() else local)
        if not provider.is_file():module['provider_status']='NOT_FOUND';missing.append(module['dll']);continue
        data=provider.read_bytes();image=pe(data);named,ordinals=exported(data);absent=[]
        for symbol in module['imports']:
            if not (named.get(symbol['name']) if 'name' in symbol else ordinals.get(symbol['ordinal'])):absent.append(symbol)
        module['provider']={'file':str(provider),'sha256':sha(provider),'architecture':image['architecture'],'missing_exports':absent};module['provider_status']='MISSING_EXPORTS' if absent else 'PRESENT'
        if absent:missing.append(module['dll'])
    if any(row['dll'] in ['d3d8.dll','d3dx8.dll','d3dx9_43.dll'] for row in modules):raise ValueError('Old/wrong Direct3D import in full client')
    inputs=[]
    for relative in ['Snd/WaveList.spt','DataTable/cryp.dat','DataTable/advr.dat']:
        path=client/relative;row={'relative':relative,'exists':path.is_file(),**({'sha256':sha(path),'bytes':path.stat().st_size} if path.is_file() else {})}
        if not path.is_file():row['localized_candidates']=[{'relative':p.relative_to(client).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted((client/'DataTable').glob('*/'+path.name))]
        inputs.append(row)
    engine=json.loads((WS/'inventory/client455-startup-engine-build.json').read_text())
    if not any(row['file']==engine['library'] and row['sha256']==engine['library_sha256'] for row in link['libraries']):raise ValueError('Full client did not select derived startup engine')
    sources=['work/client455-port/normal/source/mainapp.cpp','work/client455-port/source/R3Engine/2ndclass/r3sound.cpp','work/client455-port/source/R3Engine/2ndclass/r3d3dapp.cpp']+[row['file'] for row in engine['derived_sources']]
    report={'scope':'Static own-client startup import/name/provider audit;not DLL ABI/runtime or complete455acceptance','executable':link['executable'],'normal_link_sha256':sha(WS/'inventory/client455-normal-link.json'),'modules':modules,'unresolved_provider_modules':missing,'startup_files':inputs,'source_inputs':[{'file':name,'sha256':sha(WS/name)} for name in sources],'normal_winmain_executed':False,'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M9':'OPEN','script_sha256':sha(WS/'scripts/audit_client455_startup.py')}
    report['startup_engine_build_sha256']=sha(WS/'inventory/client455-startup-engine-build.json')
    (WS/'inventory/client455-startup-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'modules':len(modules),'delayed':[m['dll'] for m in modules if m['delayed']],'unresolved_providers':missing,'startup_files':inputs}))
if __name__=='__main__':main()
