"""Build independent record expectations from pinned pseudocode and stock bytes."""
import json,re
from audit_client455_language import decode,records
from audit_client455_item_payloads import record
from compare_client_binaries import WS


def fallback_rows():
    raw=json.loads((WS/'artifacts/client455-progress/chat109-reference.json').read_text())
    code=next(row['code'] for row in raw['functions'] if row['addr']=='0x742840')
    result={};indices=[];block=[]
    for line in code.splitlines():
        match=re.search(r'^    case (\d+):',line)
        if match:indices.append(int(match[1]))
        if line.startswith('    default:'):indices=[0,1]
        if indices:block.append(line)
        if indices and 'break;' in line:
            text='\n'.join(block);calls=[value for value in block if 'sub_495040(' in value]
            colors=[int(re.search(r', (-?\d+), 12, 32\)',value)[1])&0xffffffff for value in calls]
            language=re.search(r'sub_6023B0\([^\n]+, 0x([0-9A-F]+)u\)',text)
            for index in indices:result[index]=dict(colors=colors,body_written=len(calls)>1 and 'this + 3' in calls[1],language=int(language[1],16) if language else 0)
            indices=[];block=[]
    if set(result)!=set(range(36)):raise ValueError('Incomplete target fallback oracle')
    return result


def make_oracles(run,reference,client):
    language,_=records(decode((client/'DataTable/ko-kr/NDLanguage.edf').read_bytes()));fallback=fallback_rows();outputs=[];catalog=[]
    for row in reference['inputs']:
        source=WS/row['file'];parsed={}
        for line in source.read_bytes().splitlines():
            match=re.match(rb'\s*(#[A-Z_]+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+"([^"]*)"',line)
            if match:
                color=[max(0,min(255,int(match[i]))) for i in range(2,6)];parsed.setdefault(match[1].decode(),(color[2]|color[1]<<8|color[0]<<16|color[3]<<24,match[6]))
        expected=[]
        for index,tag in enumerate(reference['style_tags']):
            if tag in parsed:
                color,prefix=parsed[tag];header=body=color;hs=bs=12;hf=bf=32
            else:
                item=fallback[index];color=item['colors'][0] if index!=19 else item['colors'][0 if row['nation']==2 else 2];header=color;body=color if item['body_written'] else 0xffffffff;hs,hf=12,32;bs,bf=(12,32) if item['body_written'] else (0,0);prefix=language[item['language']][1].split(b'\0')[0] if item['language'] else b''
            count=min(len(prefix),15);prefix=prefix[:count];expected.append(f'{index} {header} {body} {hs} {bs} {hf} {bf} {count} {prefix.hex() or "-"}')
        path=run/f'oracle{row["nation"]}.tsv';path.write_text('\n'.join(expected)+'\n',encoding='ascii');outputs.append(record(path));catalog.append(f'{row["nation"]} {row["runtime_relative"]} {path.name}')
    path=run/'oracles.txt';path.write_text('\n'.join(catalog)+'\n',encoding='ascii');outputs.append(record(path));return outputs
