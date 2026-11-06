"""Pin the measured RVP FX/cache/particle dependency contracts; not full FX parity."""
import hashlib,json,struct
from pathlib import Path
from build_client455_x87_math import read_va
from compare_client_binaries import WS

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    files=[WS/'artifacts/client455-progress'/name for name in ['particle081-initial.json','particle081-extra.json']]
    initial,extra=[json.loads(p.read_text()) for p in files]
    pins=json.loads((WS/'config/client-target.json').read_text());references=[]
    matrix=struct.pack('<16f',1,0,0,0,0,0,1,0,0,1,0,0,0,0,0,1)
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        if sha(path)!=pins[key]['sha256']:raise ValueError('Changed455 pin')
        ranges=[]
        for row in extra['ranges']['result']:
            if row['error']:raise ValueError('Missing function')
            addr,size=int(row['fn']['addr'],16),int(row['fn']['size'],16)
            ranges.append(dict(rva=hex(addr-0x400000),bytes=size,sha256=hashlib.sha256(read_va(raw,addr,size)).hexdigest()))
        if references and ranges!=references[0]['ranges']:raise ValueError('FX contracts differ between pins')
        if read_va(raw,0xbf8148,64)!=matrix:raise ValueError('Entity YZ matrix differs')
        timing=struct.unpack('<d',read_va(raw,0xaab208,8))[0]
        speed=struct.unpack('<d',read_va(raw,0xaa9700,8))[0]
        #The stored double is the promoted float0.0005, not the nearest double0.0005.
        if timing!=struct.unpack('<f',struct.pack('<f',.0005))[0] or speed!=30:raise ValueError('Inspect FX clock constants: '+str((timing,speed)))
        references.append(dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=ranges,
            constants=[dict(rva='0x7f8148',bytes=64,sha256=hashlib.sha256(matrix).hexdigest()),dict(rva='0x6ab208',value=timing,type='double'),dict(rva='0x6a9700',value=speed,type='double')]))
    assemblies=[]
    for function in extra['functions']:
        lines=[line for page in function['pages'] for line in page['asm']['lines']]
        if len(lines)!=function['total'] or len({line['addr'] for line in lines})!=len(lines):raise ValueError('Incomplete or overlapping assembly')
        assemblies.append(dict(rva=hex(int(function['addr'],16)-0x400000),instructions=len(lines),pages=len(function['pages'])))
    report=dict(scope='Bounded ordinary RVP particle/entity draw, shared cache lifecycle and owned dependency layout;not full particle/entity or client acceptance',
        references=references,assemblies=assemblies,raw_evidence=[dict(file=p.relative_to(WS).as_posix(),sha256=sha(p)) for p in files],script_sha256=sha(Path(__file__)),
        facts=[
            '90D4C0 is a second model FX pass after geometry; three particle IDs at effect+220/236/252 and entity ID at+268; mesh matrix+4830 and EFF pointer+5455',
            'Particle slots lazily load once, clone six1296-byte particles and select cycle modulo6; attempted load failure is sticky',
            'Loop precedes new rotation/create position; a false Loop returns from the entire model pass; RGB is forced white preserving alpha',
            'Entity lazy load restores textures; inverse pinned YZ matrix precedes model/world matrix; scrolling timer persists outside cache lifetime',
            '8D6900 creates shared cache if absent and increments refs;8D8340 decrements positive refs without destruction, then a later zero-ref release frees it even without level',
            'Cache reads entity.ini,particle.ini,unit.ini; particle duplicate registration overwrites metadata,entity duplicate registration keeps first; ABSAXIS scans float bits into DWORD',
            'CParticle size1296:elapsed140/live144/curve340/special472/flag1224/createpos1256/combine1268/light1292; ctor zeroes1296 then gravity-15/light-1',
            'CEntity size212:ctor also clears object152,new expanded vertex count168,frame208; legacy sizes1148/208 cannot be used unchanged'],
        gaps=[
            'Advanced curve/trace/light/distortion/azirang/combine-scale and special-particle kernels remain incomplete; selected advanced SPT tokens explicitly refuse loading',
            'Basic SPT/CParticle update and CEntity loader/draw retain legacy implementations with measured overlays; exact455 numeric/render/failure equivalence is unaccepted',
            'Original Chef resource group is process-owned; adapter owns indexes with shared RVP cache and explicitly selects it; global owner/context/enumeration parity remains open',
            'Original dense2000-slot cache replaced by sparse owned slots; failure/locale/OOM/unregistered-index behavior not fully equivalent; constructor unwind remains unaccepted',
            'Render material/light reset8CE5D0,full shader/lighting/reset/resource lifecycle and fine reference-runtime pixel parity remain open',
            'Audio,magic,collision,shadow,trace,screen,timer-rate and fullTutorial/Avatar/QBI/follow/fourstage/Login/auth/gameplay/IME remain required',
            'Prior scanner078,pausedCAM/numeric079,palette bounds080 and all other client-acceptance gaps remain'],
        input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-rvp-effects-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(equal_ranges=len(references[0]['ranges']),full_assembly_instructions=sum(r['instructions'] for r in assemblies),clock_constants=[timing,speed],M9='OPEN')))

if __name__=='__main__':main()
