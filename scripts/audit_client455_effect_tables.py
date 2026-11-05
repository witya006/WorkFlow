"""Pin pattern/item readers and generate a small independent real-file oracle."""
import hashlib,json,struct
from pathlib import Path
from compare_client_binaries import WS,pe
from build_client455_x87_math import read_va

def sha(data):return hashlib.sha256(data).hexdigest()
def loaded(data,va,size):
    image=pe(data);rva=va-image['image_base'];s=next(s for s in image['sections'] if s['rva']<=rva and rva+size<=s['rva']+max(s['virtual_size'],s['raw_size']))
    delta=rva-s['rva'];stored=max(0,min(size,s['raw_size']-delta));start=s['raw_offset']+delta
    return data[start:start+stored]+bytes(size-stored)
def main():
    pins=json.loads((WS/'config/client-target.json').read_text());references=[];previous=None
    functions=[('pattern_reader',0x925710,0xd4),('item_reader',0x929920,0x110),('query',0x927b80,0x58),('item_lookup',0x9276b0,0x62),('first_insert_wins',0x929460,0xb9)]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=pins[key]['sha256']:raise ValueError('Changed455binary')
        bodies=[{'name':name,'rva':hex(at-0x400000),'bytes':size,'sha256':sha(read_va(raw,at,size))} for name,at,size in functions]
        initial=loaded(raw,0x1189820,340400)
        if any(initial):raise ValueError('Pattern table not initially zero in PE image')
        if previous is not None and bodies!=previous:raise ValueError('Reader ranges differ')
        references.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','functions':bodies,'initial_pattern_table':{'rva':'0xd89820','bytes':len(initial),'sha256':sha(initial),'all_zero':True}});previous=bodies
    root=Path(json.loads((WS/'config/paths.json').read_text())['client_455'])/'CHEF';stage=WS/'work/client-reference/normal-effects455';stage.mkdir(parents=True,exist_ok=True);files=[]
    for name in ['PatternList.txt','ItemEffectList.txt']:
        path=root/name;raw=path.read_bytes();copy=stage/name;copy.write_bytes(raw);files.append({'original':str(path),'copy':copy.relative_to(WS).as_posix(),'sha256':sha(raw)})
    tokens=(stage/'PatternList.txt').read_bytes().split();patterns={};duplicates=0
    if len(tokens)%10:raise ValueError('Real pattern stream has incomplete nine-value record;investigate')
    for i in range(0,min(len(tokens),2299*10),10):
        row=[int(t) for t in tokens[i:i+10]];index=row[0]&0xffffffff
        if index<2300:duplicates+=index in patterns;patterns[index]=[v&0xffffffff for v in row[1:]]
    tokens=(stage/'ItemEffectList.txt').read_bytes().split();items={};itemDuplicates=0
    if len(tokens)%7:raise ValueError('Real item stream has incomplete six-selector record;investigate')
    for i in range(0,len(tokens),7):
        index=int(tokens[i],16);row=[int(t)&0xffffffff for t in tokens[i+1:i+7]];itemDuplicates+=index in items;items.setdefault(index,row)
    keys=sorted(items);selected=sorted(set(keys[:6]+keys[max(0,len(keys)//2-3):len(keys)//2+3]+keys[-6:]));cases=[]
    for key in selected:
        for group in [0,5]:
            for grade in [0,8,9,35,36]:
                pattern=items[key][group];status=0;effect=0
                if grade<36:
                    if pattern>=2300:status=2
                    elif pattern in patterns:
                        if grade>=9:status=3
                        else:effect=patterns[pattern][grade]
                cases.append((key,grade,group,status,effect))
    golden=b'EFT1'+struct.pack('<III',len(cases),len(patterns),len(items))+b''.join(struct.pack('<5I',*case) for case in cases);target=stage/'selection.bin';target.write_bytes(golden)
    report={'scope':'455 pattern/item readers and defined item-effect selections;not effect binary loading/application or undefined original stack tail',
        'references':references,'files':files,'pattern_records':len(patterns),'pattern_duplicate_records':duplicates,'item_records':len(items),'item_duplicate_records':itemDuplicates,
        'golden':target.relative_to(WS).as_posix(),'golden_sha256':sha(golden),'selection_cases':len(cases),
        'facts':['Pattern global340400bytes initiallyzero:2300flags+2300rows*36DWORD','925710 attempts1..2299;fscanf ID+9integers then repmovsd36copies;tail27DWORD is uninitialized stack,not file data','Pattern duplicate overwrites row;missing files/reload do not clear table;tokens ignore line boundaries','929920 initializes itemkey+6selectors once;partial reads retain previous fields;duplicates keep first map entry','927B80 ignores model,guards grade36,finds unsigned itemkey,then group selector and pattern row;does not consult present flags'],
        'gaps':['Original row tail grades9..35 is unspecified stack content;owned known-bit metadata makes such queries explicit errors,not zero effects','Group>=6 or pattern>=2300 is unchecked inreference;owned errors do not certify invalid-pointer/OOM behavior','Nonnumeric item token can hang original;owned reader reports malformed input','Effect file map/loading/material/particle slots and complete client acceptance still open'],
        'script_sha256':sha(Path(__file__).read_bytes())}
    (WS/'inventory/client455-effect-tables-reference.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['pattern_records','item_records','selection_cases']}))
if __name__=='__main__':main()
