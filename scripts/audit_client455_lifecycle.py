"""Pin the455Land early-unload branch;do not conflate it with full ILevel parity."""
import hashlib,json
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va

def sha(data):return hashlib.sha256(data).hexdigest()

def main():
    ranges=[(0x7c78e0,0x81),(0x7c79f0,0xcc),(0x7c7970,0x79),(0x7c7ac0,0x98),(0x7c7b60,0x2e),(0x7c82c0,0x19f),(0x7c8f30,0x137),(0x7c7cb0,0xf),(0xaecaec,52)]
    pins=json.loads((WS/'config/client-target.json').read_text());refs=[];previous=None
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=pins[key]['sha256']:raise ValueError('Changed455pin')
        rows=[{'rva':hex(at-0x400000),'bytes':n,'sha256':sha(read_va(raw,at,n))} for at,n in ranges]
        if previous is not None and rows!=previous:raise ValueError('Land contracts differ between455pins')
        # CMP [owner],0;JNZ continue;XOR EAX,EAX;JMP return. This is before
        # any virtual level call, effects cleanup or global write.
        branch=read_va(raw,0x7c8f3f,12)
        if branch!=bytes.fromhex('833800750733c0e915010000'):raise ValueError('Changed455uncreated-level branch')
        previous=rows;refs.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','ranges':rows})
    report={'scope':'455Land unload before Create and destructor callchain;only the confirmed null-level branch is ported','references':refs,'script_sha256':sha(Path(__file__).read_bytes()),'facts':['Land ctor7C78E0 callsInit7C79F0;first owner pointer is zero','Land destructor7C7970 callsDestroy7C82C0,which first callsUnload7C8F30','Unload7C8F30 returnsFALSE immediately if level owner is null;no effects cleanup or global writes','Create7C7AC0 allocates8byte ILevel-derived wrapper7C7B60;not oldfullCLevel layout','Default wrapper vtableAECAEC slot40 points7C7CB0,an empty release method;other concrete level types remain to port'],'ported':['Null-level returnFALSE before cleanup,used by real normal CLand/CMainApp global destruction'],'gaps':['Full typed ILevel owner/wrapper/concrete types and world lifecycle','Created-level unload effects order/global-level clearing/extra two containers differ from oldCLand','Normal WinMain early-error paths,full CMainApp Create and full game shutdown','Device loss/reset and whole455UI/gameplay/network acceptance'],'M6':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-lifecycle-reference.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS:455Land entry/destructor/wrapper ranges pinned;uncreated-level FALSE branch confirmed')
if __name__=='__main__':main()
