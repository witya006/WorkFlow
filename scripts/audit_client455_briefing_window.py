"""Pin full briefing window,outline and actual screen capture consumers."""
import hashlib,json
from pathlib import Path
from audit_client455_briefing_controls import resources
from audit_client455_minimap_opacity import sprite_geometry
from audit_client455_scrollbar import assembly_rows
from build_client455_x87_math import read_va
from compare_client_binaries import WS,pe

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    root=WS/'artifacts/client455-tutorial'
    ranges=json.loads((root/'briefing-window-ranges072.json').read_text())['result']
    target=json.loads((WS/'config/client-target.json').read_text());pins=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        if sha(path)!=target[key]['sha256'] or pe(raw)['architecture']!='x86':raise ValueError('Changed455pin')
        functions=[]
        for row in ranges:
            if row['error']:raise ValueError('Missing function')
            address,size=int(row['fn']['addr'],16),int(row['fn']['size'],16)
            functions.append({'rva':hex(address-0x400000),'bytes':size,'sha256':hashlib.sha256(read_va(raw,address,size)).hexdigest()})
        vtable={'rva':'0x6e6454','bytes':212,'sha256':hashlib.sha256(read_va(raw,0xae6454,212)).hexdigest()}
        if pins and (functions!=pins[0]['ranges'] or vtable!=pins[0]['vtable']):raise ValueError('455window differs betweenpins')
        pins.append({'sha256':sha(path),'architecture':'x86','image_base':'0x400000','ranges':functions,'vtable':vtable})
    inputs=resources();client=Path(json.loads((WS/'config/paths.json').read_text())['client_455'])
    for row in inputs:
        row['portraits']=[]
        for name in ['bel','cor','acc']:
            path=client/f'SpriteImage/{row["folder"]}/npc/{name}.spr'
            if not path.exists():path=client/f'SpriteImage/Common/npc/{name}.spr'
            row['portraits'].append({'relative':path.relative_to(client).as_posix(),'sha256':sha(path),'geometry':sprite_geometry(path,{(a,f) for a in range(3) for f in range(2)})})
    evidence=[]
    for name in ['briefing-core070','briefing-window072','briefing-window-extra072','briefing-window-ranges072']:
        path=root/(name+'.json');body=json.loads(path.read_text());evidence.append({'file':path.relative_to(WS).as_posix(),'sha256':sha(path),'assemblies':list(assembly_rows(body.get('assemblies',[])))})
    report={'scope':'Source CGUIBriefingWindow and screen capture;actual Avatar/world/Tutorial stage remains open','references':pins,'raw_evidence':evidence,'inputs':inputs,'script_sha256':sha(Path(__file__)),
        'facts':['Init462x207,typing143height,main caps462/611,keyframe140x207,portrait134/128','BYTEpageCount,80ms typing,firstpage250delay,continue finishes then advances then posts1201/value1','Portraitrace=AvatarBYTE/2,roles0or2/3/15 mapped0/1/2;31..33sprites,sheets128cells,FPS10','Portrait mode0 waits rand%5+10 periods;mode1 returns afterone;elapsedDWORD/quotientWORD','Screen capture setter validates main-list membership once;visible capture overrides ordinary input and GUIInputID regardless child return','Screen MsgProc:dialogs untilconsumed,visiblecapture else visibleordinary windows;no queued event drain here','Screen Remove/Close have no capture pointer writes;owner must release beforedestruction'],
        'gaps':['Real Avatar race provider and ordinary Tutorial/fourstage/Avatar/world stillopen','Legacy PostUIMessage lacks recovered current-stage gate45FBD0;fullwindow base lifecycle/input/sound/docking stillopen','SetSize base nonvirtual;typedwindow/control sizes coveredonly','OtherGUI layers/IME/oldanimatedimage consumers/renderer modes/unsafe input and failure domains remainopen','Component tests/static pins are not dynamic acceptance against original455'],
        'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-briefing-window-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'ranges':len(functions),'full_assemblies':sum(len(x['assemblies']) for x in evidence),'portraits':inputs[0]['portraits']}))
if __name__=='__main__':main()
