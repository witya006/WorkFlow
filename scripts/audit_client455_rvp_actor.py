"""Verify the pinned RVP actor resource/animation/palette contracts."""
import hashlib,json
from pathlib import Path
from build_client455_x87_math import read_va
from compare_client_binaries import WS

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    files=[WS/'artifacts/client455-progress'/name for name in ['rvp-actor080-initial.json','rvp-actor080-extra.json','rvp-actor080-flow.json']]
    initial,extra,flow=[json.loads(p.read_text()) for p in files]
    pins=json.loads((WS/'config/client-target.json').read_text());references=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        if sha(path)!=pins[key]['sha256']:raise ValueError('Changed455 pin')
        ranges=[]
        for row in extra['ranges']['result']:
            if row['error']:raise ValueError('Missing function')
            addr,size=int(row['fn']['addr'],16),int(row['fn']['size'],16)
            ranges.append(dict(rva=hex(addr-0x400000),bytes=size,sha256=hashlib.sha256(read_va(raw,addr,size)).hexdigest()))
        if references and ranges!=references[0]['ranges']:raise ValueError('Actor contracts differ between pins')
        references.append(dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=ranges))
        if read_va(raw,0xbf7378,4)!=bytes.fromhex('0000ce43'):raise ValueError('Ambient divisor changed')
    assemblies=[]
    for function in extra['assemblies']:
        actual=sum(len(page['asm']['lines']) for page in function['pages'])
        if actual!=function['total']:raise ValueError('Incomplete actual assembly')
        assemblies.append(dict(rva=hex(int(function['addr'],16)-0x400000),instructions=actual,pages=len(function['pages'])))
    fade=next(row for row in flow['fadeXrefs']['result'] if int(row['addr'],16)==0x8d4340)
    if fade['xref_count'] or fade['more']:raise ValueError('Recheck fade flow')
    report=dict(scope='Ordinary RVP actor resource/animation/palette/model-draw bindings;not fullRVP/game acceptance',
        references=references,assemblies=assemblies,raw_evidence=[dict(file=p.relative_to(WS).as_posix(),sha256=sha(p)) for p in files],
        script_sha256=sha(Path(__file__)),facts=[
            '931480/931600 use renderer+4264 bone registry;9313F0/931560 use BODY part manager;registrations append,lookup returns first exact name',
            '8D4020 sets renderer texture directory,registers/loads bone then mesh;BBX fallback uses actual model bounds and swapsY/Z',
            'OneTimeScene loads actors/registers animations then Prepare;Create calls Prepare again;SetAnimation resets frames even without actions,clamps index,doesnot setnowAction',
            'Frame publishes bone frame before wrap;actor frame alone resets160;dummy matrix is multiplied onright by scale;culling precedes pose',
            '8D4700/8D47F0 save and restore each actor palette;counts at2400 and slots at2680,stride256;shared models must not share the saved pose',
            'Render uses base color or BSP lighting,ambient divisor412,negated direction,materialbiases,actual EFF application and transparent flush',
            'FadeIn/FadeOut setters are called by tracks;8D4340 hasno xrefs and ordinary Frame/Render do not call it;adding a tick would change observed455 flow'],
        gaps=[
            'Separate particle/entity DrawEffectMat pass and global effect Create/Release/refcount/deferred lifecycle remain open;EFF binding alone is not fullFX',
            'Magic,collision,shadow,ambient/event audio,swordtrace,screen,timer-rate providers explicitly refused;not waived fromM9',
            'RVP material/light cache-reset8CE5D0 and full failure/undefined numeric domains unaccepted',
            'Actor palette blendcount>4 orparts>70 rejected;original unchecked overflow/fatal policy not reproduced',
            'Resource parser scanner078 and camera-only/pause failure gaps079 remain;full Tutorial/Avatar/QBI/fourstage/auth/gameplay/IME/M6F/M7/M9 open'],
        input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-rvp-actor-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(equal_ranges=len(references[0]['ranges']),full_assembly_instructions=sum(r['instructions'] for r in assemblies),fade_tick_xrefs=0,M9='OPEN')))
if __name__=='__main__':main()
