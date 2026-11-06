"""Pin normal modal button/outline/input contracts and their real sprite frames."""
import hashlib,json,struct
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def frames(path):
    raw=path.read_bytes();at=0
    def take(size):
        nonlocal at
        if size>len(raw)-at:raise ValueError('Truncated sprite')
        result=raw[at:at+size];at+=size;return result
    if struct.unpack('<I',take(4))[0]!=0x3f8ccccd:raise ValueError('Expected sprite1.1')
    count=struct.unpack('<I',take(4))[0];rows=[]
    for action in range(count):
        for frame in range(struct.unpack('<I',take(4))[0]):
            fmt,w,h,tw,th,size=struct.unpack('<6I',take(24));take(size)
            if (action==0 and frame<3)or(action in [1,2]and frame<4):
                rows.append({'action':action,'frame':frame,'width':w,'height':h,'texture_width':tw,'texture_height':th,'format':fmt})
    if at!=len(raw)or len(rows)!=11:raise ValueError('Incomplete modal sprite data')
    return rows

def main():
    directory=WS/'artifacts/client455-tutorial';source=directory/'modal-reference062.json';evidence=json.loads(source.read_text())
    target=json.loads((WS/'config/client-target.json').read_text());pins=[]
    for folder,pin in [('current',target['behavior_reference']),('reference-backup',target['secondary_reference'])]:
        binary=WS/f'work/client-reference/{folder}/RF_Online.bin'
        if sha(binary)!=pin['sha256']:raise ValueError('Changed455pin')
        raw=binary.read_bytes();ranges=[]
        for row in evidence['ranges']['result']:
            if row['error']:raise ValueError('Missing modal function')
            function=row['fn'];addr,size=int(function['addr'],16),int(function['size'],16)
            ranges.append({'rva':hex(addr-0x400000),'bytes':size,'sha256':hashlib.sha256(read_va(raw,addr,size)).hexdigest()})
        data=[]
        for addr,size,role in [(0xAE4504,208,'CGUIMessagebox_vtable'),(0xAD99A4,116,'CGUIButtonEx_vtable'),(0xADA21C,64,'CGUIOutlineBoard_vtable')]:
            block=read_va(raw,addr,size);data.append({'rva':hex(addr-0x400000),'bytes':size,'role':role,'sha256':hashlib.sha256(block).hexdigest()})
        if pins and(ranges!=pins[0]['ranges']or data!=pins[0]['data']):raise ValueError('Modal contracts differ between pins')
        pins.append({'sha256':pin['sha256'],'architecture':'x86','image_base':'0x400000','ranges':ranges,'data':data})
    assemblies=[]
    for row in evidence['asm']:
        path=WS/row['file'];body=json.loads(path.read_text())
        if not body['cursor']['done']or len(body['asm']['lines'])!=row['instructions']:raise ValueError('Incomplete modal asm')
        assemblies.append({**row,'sha256':sha(path)})
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);inputs=[]
    for nation,folder in [('Korea','ko-kr'),('Russia','ru-ru')]:
        sprite=client/f'SpriteImage/{folder}/common.spr';language=client/f'DataTable/{folder}/NDLanguage.edf'
        inputs.append({'nation':nation,'folder':folder,'sprite':{'file':str(sprite),'sha256':sha(sprite),'frames':frames(sprite)},'language':{'file':str(language),'sha256':sha(language)}})
    report={'scope':'Normal modal controls/outline/input on existing GDI/client GUI;full455 text/scrollbar/frame lifecycle remain OPEN',
            'references':pins,'assemblies':assemblies,'inputs':inputs,
            'raw_evidence':[{'file':p.relative_to(WS).as_posix(),'sha256':sha(p)} for p in [source,directory/'modal-decompile062.json']],
            'script_sha256':sha(Path(__file__)),
            'facts':['Both buttons common spriteID1/action1 frames0,1,2,3 for normal/hover/pressed/disabled',
                     'Button sizes come from original sprite dimensions;labels ND106/107,outline flag32',
                     'Disabled caption FF797979 has priority over hover;Open resets OK label and enables it',
                     'Frame background FF222628,alpha216 initially;outline FF6A6E72,width1,inset2',
                     'Right/bottom button margin7;two-button gap7;SetAlpha preserves background RGB',
                     'Enter result1;Escape result3 only when close-enabled;initial base-window close flag0',
                     'YN only style3 and not the focused/show/active/enabled primary chat input;mouse result1/2/3 unchanged'],
            'gaps':['Full455 text-board wrapping/markup/extent/scroll semantics and shared scrollbar layout/input',
                    'FreeType/ANSI routes and full caption/text metrics parity beyond the current GDI route',
                    'Full frame-window/lifecycle/wrapper variants and ordinary chat-input provider equivalence',
                    'CGUIBriefingWindow/Avatar/world/Tutorial/fourstage and previous unknown/error domains;M6F/M9'],
            'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-modal-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'pinned_ranges':len(pins[0]['ranges']),'assemblies':len(assemblies),'real_sprite_frames':sum(len(row['sprite']['frames'])for row in inputs),'full455GUI':'OPEN'}))
if __name__=='__main__':main()
