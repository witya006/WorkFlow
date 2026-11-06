"""Pin byte metrics/fit and CGUIText geometry before the full TextBoard migration."""
import hashlib,json
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    directory=WS/'artifacts/client455-tutorial';source=directory/'text-metrics-reference063.json';evidence=json.loads(source.read_text());target=json.loads((WS/'config/client-target.json').read_text());pins=[]
    for folder,pin in [('current',target['behavior_reference']),('reference-backup',target['secondary_reference'])]:
        binary=WS/f'work/client-reference/{folder}/RF_Online.bin'
        if sha(binary)!=pin['sha256']:raise ValueError('Changed455pin')
        raw=binary.read_bytes();ranges=[]
        for row in evidence['ranges']['result']:
            if row['error']:raise ValueError('Missing text metric function')
            fn=row['fn'];addr,size=int(fn['addr'],16),int(fn['size'],16)
            ranges.append({'rva':hex(addr-0x400000),'bytes':size,'sha256':hashlib.sha256(read_va(raw,addr,size)).hexdigest()})
        empty=read_va(raw,0xAA8DD4,4)
        if empty!=bytes(4):raise ValueError('Default-height string is not empty')
        data=[{'rva':'0x6a8dd4','bytes':4,'role':'empty_default_height_string','sha256':hashlib.sha256(empty).hexdigest()}]
        if pins and(ranges!=pins[0]['ranges']or data!=pins[0]['data']):raise ValueError('Text contracts differ between pins')
        pins.append({'sha256':pin['sha256'],'architecture':'x86','image_base':'0x400000','ranges':ranges,'data':data})
    assemblies=[]
    for row in evidence['asm']:
        path=WS/row['file'];body=json.loads(path.read_text())
        if not body['cursor']['done']or len(body['asm']['lines'])!=row['instructions']:raise ValueError('Incomplete text metric asm')
        assemblies.append({**row,'sha256':sha(path)})
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);inputs=[]
    for nation,folder in [('Korea','ko-kr'),('Russia','ru-ru')]:
        path=client/f'DataTable/{folder}/NDLanguage.edf';inputs.append({'nation':nation,'folder':folder,'file':str(path),'sha256':sha(path)})
    paths=[source,directory/'textboard-initial063.json',directory/'textboard-metrics063.json']
    report={'scope':'Current GDI/ANSI byte metrics and ordinary CGUIText sizing;fullTextBoard/FreeType/Tutorial OPEN',
            'references':pins,'assemblies':assemblies,'inputs':inputs,'raw_evidence':[{'file':path.relative_to(WS).as_posix(),'sha256':sha(path)}for path in paths],
            'script_sha256':sha(Path(__file__)),
            'facts':['Text width uses exact byte prefix;WORDffff means whole string;zero/null helper width returns0',
                     'GDI fit uses GetTextExtentExPointA,then decrements a final DBCS lead byte',
                     'Default height measures the empty string once and retains that first value',
                     'CGUIText geometry uses measured pixels;80000000 intermediate size is overwritten without40000000',
                     '40000000 final width16*WORD(width/12),height32;SetFont alone does not recalculate size',
                     'Target FONT_INFO is16bytes:extra offset12 is float scale initialized1.0,not a link identifier',
                     'Full TextBoard has distinct fragment and line caches;old byte-count board remains unported'],
            'gaps':['FreeType/Unicode branch908240/908170 and complete metric parity across renderer routes',
                    'Target16byte FONT_INFO scale and full typed draw contracts;legacy prefix only in this unit',
                    'Shared scratch buffer unsafe overflow/foreign-pointer/huge input domains not reproduced',
                    'FullTextBoard fragments/line cache/markup/wrapping/retention/sizing/scroll and shared scrollbar',
                    'CGUIBriefingWindow/real Avatar/world/Tutorial/fourstage and earlier unknown/error domains;M6F/M9'],
            'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-text-metrics-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'pinned_ranges':len(pins[0]['ranges']),'complete_asm':len(assemblies),'fullTextBoard':'OPEN'}))
if __name__=='__main__':main()
