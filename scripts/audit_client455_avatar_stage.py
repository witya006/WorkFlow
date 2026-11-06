"""Pin Avatar stage state and inventory actual remaining Tutorial lifecycle calls."""
import hashlib,json,struct
from pathlib import Path
from audit_client455_scrollbar import assembly_rows
from build_client455_x87_math import read_va
from compare_client_binaries import WS,pe
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    root=WS/'artifacts/client455-progress';raw_path=root/'stage-avatar073.json';body=json.loads(raw_path.read_text());rows=body['ranges']['result'];rows+=json.loads((root/'tutorial-dispatch073.json').read_text())['ranges']['result'];target=json.loads((WS/'config/client-target.json').read_text());pins=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        if sha(path)!=target[key]['sha256'] or pe(raw)['architecture']!='x86':raise ValueError('Changed455pin')
        ranges=[]
        for row in rows:
            if row['error']:raise ValueError('Missing stage function')
            addr,size=int(row['fn']['addr'],16),int(row['fn']['size'],16);ranges.append({'rva':hex(addr-0x400000),'bytes':size,'sha256':hashlib.sha256(read_va(raw,addr,size)).hexdigest()})
        tables=[{'rva':hex(addr-0x400000),'bytes':64,'sha256':hashlib.sha256(read_va(raw,addr,64)).hexdigest()} for addr in [0xab0f9c,0xab0324]]
        if pins and (ranges!=pins[0]['ranges'] or tables!=pins[0]['vtables']):raise ValueError('Stage contracts differ betweenpins')
        pins.append({'sha256':sha(path),'architecture':'x86','image_base':'0x400000','ranges':ranges,'vtables':tables})
    evidence=[]
    for name in ['stage-avatar073','stage-avatar-asm073','tutorial-dispatch073']:
        path=root/(name+'.json');row=json.loads(path.read_text());evidence.append({'file':path.relative_to(WS).as_posix(),'sha256':sha(path),'assemblies':list(assembly_rows(row.get('assemblies',[])))})
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);scene_inputs=[]
    for race in ['bellato','cora','accretia']:
        for ext in ['bsp','cam']:
            path=client/f'Map/{race}/{race}.{ext}';raw=path.read_bytes()
            scene_inputs.append({'file':str(path),'relative':path.relative_to(client).as_posix(),'sha256':sha(path),'bytes':len(raw),'header32':hex(struct.unpack_from('<I',raw)[0])})
    report={'scope':'Actual Avatar stage/skip,MainApp Create failure gate and login stage2 predicate;fullTutorial/fourstage stillopen','references':pins,'raw_evidence':evidence,'scene_inputs':scene_inputs,'script_sha256':sha(Path(__file__)),
        'facts':['Avatarctor402110 initializes20165BYTE=0 and20168DWORD=0;copy403330 copies both','41E130 byteequality,4A6160 storebyte;420BB0 stores fullDWORD,420BE0 returns it without normalization','MainApp7D1370 returns0 on failedCreate;successfulCreate writesAvatarstage only once','562E80 skips login transform in stage2 regardless skipDWORD;562BE0 localTutorial route additionally requires skipDWORD0','45FBD0/C0BD64 is Screen singleton,not stage:636C80 called only fromScreenctor62FB40;4F5E40 readsScreenHWND+340','TargetTutorial ctor/mainvirtuals differfromMainGame,loads race-selected BSP/CAM andintro;inheritsRender54A830','LocalTutorial1/17 directly calls transport without changing codec;group21 and manyother messages return1 without send','Localgroup4 handles1/19/31;7handles2/5/9/11/13;13handles2/21/26;17handles4;otherselectors inthese groups ignored','Group5 evaluates active QBI and can emit attack failure feedback even for unknownopcode;not generalized to ignored'],
        'gaps':['Ordinary factory remains legacy3/modulo;source legacyMainGame2 explicitly maps to455AvatarMainGame3 until jointmigration','CGP_Tutorial Create/Destroy/frame/input/world/camera/board/Avatar/localmessage integration notyetimplemented','Avatar network skip flag producer,fullcopy/lifecycle/constructor behavior beyondtwofields unverified','Full localTutorial handlers,realworld/Avatar/GUI/IME/renderer/lifecycle/auth/gameplay/M6F/M9 stillopen'],
        'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-avatar-stage-reference.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'ranges':len(rows),'vtables':len(tables),'full_assemblies':sum(len(x['assemblies']) for x in evidence)}))
if __name__=='__main__':main()
