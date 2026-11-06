"""Pin the signed64 Avatar/inventory money dependency of Tutorial Create."""
import hashlib,json
from pathlib import Path
from build_client455_x87_math import read_va
from compare_client_binaries import WS
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    files=[WS/'artifacts/client455-progress'/n for n in ['money083-reference.json','money083-assembly.json','tutorial083-initial.json','tutorial083-extra.json']]
    body,assembly,tutorial,extra=[json.loads(p.read_text()) for p in files];pins=json.loads((WS/'config/client-target.json').read_text());references=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        if sha(path)!=pins[key]['sha256']:raise ValueError('Changed455 pin')
        ranges=[]
        for row in assembly['ranges']['result']+tutorial['ranges']['result']:
            if row['error']:raise ValueError('Missing selected function')
            address,size=int(row['fn']['addr'],16),int(row['fn']['size'],16);ranges.append(dict(rva=hex(address-0x400000),bytes=size,sha256=hashlib.sha256(read_va(raw,address,size)).hexdigest()))
        if references and ranges!=references[0]['ranges']:raise ValueError('Money/Tutorial ranges differ between pins')
        if read_va(raw,0xaa9f24,2)!=b',\0':raise ValueError('Grouping separator differs')
        references.append(dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=ranges))
    full=[]
    for fn in assembly['assembly']:
        lines=[line for page in fn['pages'] for line in page['asm']['lines']]
        if len(lines)!=fn['total'] or len({r['addr'] for r in lines})!=len(lines):raise ValueError('Incomplete assembly')
        full.append(dict(rva=hex(int(fn['addr'],16)-0x400000),instructions=len(lines)))
    report=dict(scope='Signed64 Avatar-to-inventory money dependency;Tutorial owner/dependencies remain unfinished',references=references,assemblies=full,
        raw_evidence=[dict(file=p.relative_to(WS).as_posix(),sha256=sha(p)) for p in files],script_sha256=sha(Path(__file__)),facts=[
            '455 Avatar stores Gold at24112/24116,Dalant24120/24124;two-word getters and setters pass full64 bits to optional inventory singleton',
            'Inventory stores Dalant2160/2164,Gold2168/2172;formats signed64 then positions amount at wider-title x minus10 minus amount width;row y is corresponding title y',
            'Formatter7B2780 groups decimal digits by3 with pinned comma;negative path FILD signed64 then double spill/fabs/__ftol2 creates rounding above2^53 and INT64_MIN double-minus output under masked invalid',
            '7B2AB0 clears and returns shared32-byte output;null destination accepted by underlying formatter',
            'Tutorial Create5586D0 invokes shared Avatar preparation5488F0,whose selected getters/setters already use64-bit money;legacy DWORD source storage is not equivalent',
            'Actual Tutorial init has three counters and creates board object0x8F0;Create initializes its window ID38,not an inferred board-manager slot47;47 refers to QBI selector coverage',
            'FullTutorial requires MainGame UI/board/sharedAvatar initialization,world/CAM,Avatar/QBI/follow/localhandlers and lifecycle;source owner/fourstage integration remains open'],gaps=[
            'Full Tutorial Create/Load/Frame/Input/Destroy and ordinary factory still unfinished;money dependency is not stage completion',
            'Legacy login/character DB/network/trade/shop/exchange price producers/consumers still include32-bit orfloat values;not full currency economy/protocol acceptance',
            'Full inventory Init/layout/sprites/other controls not certified455;this unit restores money values/text/alignment only',
            'Selected four x87 rounding modes with masked exceptions tested;unmasked exceptions/status/CRT failure/locale/foreign buffer domains remain open',
            'Fullclient/audio/FX/gameplay and all prior M6F/M7/M9 gaps remain mandatory'],input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-money-reference.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(equal_ranges=len(references[0]['ranges']),actual_full_asm=sum(r['instructions'] for r in full),Tutorial_owner='OPEN')))
if __name__=='__main__':main()
