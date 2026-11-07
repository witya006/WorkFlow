"""Pin hover ownership/dual backup contracts before completing game handlers."""
import hashlib
import json
import shutil
from pathlib import Path
from audit_client455_item_payloads import record
from audit_client455_sprites import sprite
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check, load, require, sha
from compare_client_binaries import WS, pe


def main():
    path=WS/'artifacts/client455-progress/board-hover101-reference.json'
    raw=json.loads(path.read_text());functions=[row['fn'] for row in raw['ranges']['result']]
    require(len(functions)==23 and all(functions),'Canonical function coverage')
    require(all(row['cursor']['done'] for row in raw['assembly']+raw['functions']),'Complete assembly/decompilation')
    instructions=sum(row['instruction_count'] for row in raw['assembly'])
    require(instructions==1156,'Instruction coverage')
    pins=json.loads((WS/'config/client-target.json').read_text());references=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        source=WS/f'work/client-reference/{folder}/RF_Online.bin';binary=source.read_bytes()
        require(sha(source)==pins[key]['sha256'] and pe(binary)['architecture']=='x86','Pinned binary')
        ranges=[]
        for function in functions:
            addr,size=int(function['addr'],16),int(function['size'],16)
            ranges.append(dict(rva=hex(addr-0x400000),bytes=size,sha256=hashlib.sha256(read_va(binary,addr,size)).hexdigest()))
        references.append(dict(sha256=sha(source),architecture='x86',image_base='0x400000',ranges=ranges))
    require(references[0]['ranges']==references[1]['ranges'],'Selected pins differ')
    inputs=load('client455-item-lock-reference')['inputs']
    for row in inputs:check(row)
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455'])
    original=client/'SpriteImage/Common/mouse.spr';copy=WS/'work/client-reference/board-hover455/mouse.spr'
    copy.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original,copy)
    inputs=inputs+[dict(**record(copy),original=str(original),target_id=0,runtime_relative='SpriteImage/Common/mouse.spr',**sprite(copy.read_bytes()))]
    report=dict(status='CONFIRMED_SELECTED',scope='Own ordinary typed hover/Copy620/dual backups andscreen icon;liveavatarcancel/fulloperationqueue/game handlers remain open',
                script_sha256=sha(Path(__file__)),raw_evidence=[record(path)],references=references,functions=23,instructions=instructions,inputs=inputs,
                contracts=['Ctor allocates2separate620bytebackups;destroy boards/hover beforebackups;Copy clears destination,memcpy620,retains payload',
                           'GetHoverObject returnsactualhover ORnonemptysecondoperationbackup;firstpreviousbackup isdifferent',
                           'Nullhover copiesactualhover tofirstbackup,clearssecond,thenreleaseshover andremoves screenicon;replacement doesnotcopyfirstbackup',
                           'Screen copiesactualicon,forcesquantity,emptyID→0,shows andcenters beforemanager64/40resize;hidescursor/notifieswindows;Remove empties/hidesicon/showscursor/notifies',
                           'SetHover directlock usesrawflag21;FrameMove updatesactualhovericon beforeboards;managerAdd forwardsrawslots forid<16 or35/36/38/39 butreturns0always'],
                gaps=['Liveavatar action-state/cancellation/effect/sound owner remains explicit refusal;only actualnull-avatar branch admitted',
                      'Full455three-layer tooltip state/producers,fullGUIItemchildren/privateABI/unsafe/OOM/concurrency/shutdown notaccepted',
                      'Mixedlegacyhoverpayloadcasts,nonLinker source-board Add/fullCItemBoard.Add/operationqueue/quantity/network/gameplay handlers/Macro/Vending/bootstrap andallpriorclientgaps mandatory'],
                input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-board-hover-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(functions=23,instructions=instructions,equal_ranges=23,mouse=inputs[-1]['total_frames'])))


if __name__=='__main__':main()
