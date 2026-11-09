"""Pin 455 map loader/record layout and independently decode the supplied inputs."""
import hashlib,json,struct
from pathlib import Path
from audit_client455_language import decode,encode_with_envelope
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check,require,sha
from compare_client_binaries import WS,pe
from map_data455 import parse


def record(path):return dict(file=path.relative_to(WS).as_posix() if path.is_relative_to(WS) else str(path),sha256=sha(path),bytes=path.stat().st_size)
def canonical(parsed):
    out=bytearray()
    for row in parsed['rows']:
        data=bytearray(row['record'])
        for offset in [492,500,508]:data[offset:offset+4]=b'\0'*4
        out+=data
        for p in row['portals']:
            p=bytearray(p);p[240:244]=b'\0'*4;out+=p
        out+=b''.join(row['links'])+row['mines']+b''.join(row['areas'])
    for section in parsed['layers']:
        out+=struct.pack('<II',len(section['items']),section['localized_count'])
        for layer in section['items']:
            out+=struct.pack('<III',layer['height'],layer['width'],len(layer['name']))+layer['name']+struct.pack('<I',len(layer['points']))
            for p in layer['points']:out+=p['fields']+struct.pack('<I',len(p['text']))+p['text']
            out+=struct.pack('<I',len(layer['image']))+layer['image']
    return bytes(out)


def main():
    raw_path=WS/'artifacts/client455-progress/map117-reference.json';session_path=WS/'artifacts/client455-progress/map117-session.json'
    raw=json.loads(raw_path.read_text());session=json.loads(session_path.read_text());selected=set(raw['selected'])
    code={x['addr']:x for x in raw['functions'] if x['addr'] in selected};bounds={x['query']:x['fn'] for x in raw['bounds']['result']}
    require(set(code)==set(bounds)==selected and len(raw['assembly'])==9,'Selected coverage')
    require(all(x['cursor']['done'] and not x['truncated'] and x['line_count']==x['total_lines'] for x in code.values()),'Full selected pcode')
    require(all(x['cursor']['done'] and x['instruction_count']==x['total_instructions']==len(x['asm']['lines']) for x in raw['assembly']),'Full selected assembly')
    require(session['closed']['success'] and session['closed']['saved'] and session['after']['count']==0,'IDA saved/closed')
    require(session['supplement']['closed']['success'] and session['supplement']['closed']['saved'] and session['supplement']['after']['count']==0,'Loader pagination session saved/closed')
    require([len(x['asm']['lines']) for x in raw['loader_assembly_pages']]==[150,150,150,150,102] and len({x['addr'] for page in raw['loader_assembly_pages'] for x in page['asm']['lines']})==702,'702 actual loader instructions retained despite response size limit')
    old_path=WS/'inventory/client455-nuclear-minimap-reference.json';old=json.loads(old_path.read_text());check(old['raw']);cached=json.loads((WS/old['raw']['file']).read_text())
    cache_asm={x['addr']:x for x in cached['assembly']};cache_bounds={x['query']:x['fn'] for x in cached['bounds']['result']}
    # Reuse already pinned producer/fanout, without repeating IDA work.
    for address in ['0x7c9240','0x706810','0x7067a0']:
        require(address in cache_asm and cache_asm[address]['cursor']['done'],'Cached real geometry assembly');bounds[address]=cache_bounds[address]
    assembly=raw['assembly']+[cache_asm[x] for x in ['0x7c9240','0x706810','0x7067a0']]
    pins=json.loads((WS/'config/client-target.json').read_text());references=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';image=path.read_bytes();require(sha(path)==pins[key]['sha256'] and pe(image)['architecture']=='x86','Pinned x86 client')
        ranges=[dict(rva=hex(int(addr,16)-0x400000),bytes=int(fn['size'],16),sha256=hashlib.sha256(read_va(image,int(addr,16),int(fn['size'],16))).hexdigest()) for addr,fn in sorted(bounds.items())]
        edges=[];outside=[]
        for fn in assembly:
            begin=int(fn['addr'],16);end=begin+int(bounds[fn['addr']]['size'],16)
            for line in fn['asm']['lines']:
                at=int(line['addr'],16)
                if not begin<=at<end:outside.append(at)
                if line['instruction'].startswith('call ') and line.get('refs'):
                    b=read_va(image,at,5)
                    if b[0]==0xe8:
                        target=int(line['refs'][0]['addr'],16);require(at+5+struct.unpack('<i',b[1:])[0]==target,'Decoded actual call')
                        edges.append(dict(rva=hex(at-0x400000),target_rva=hex(target-0x400000)))
        # Keep each decoded EH instruction's containing16byte window, including
        # the final instruction, with the same pin equivalence requirement.
        eh=[dict(rva=hex(at-0x400000),bytes=16,sha256=hashlib.sha256(read_va(image,at,16)).hexdigest()) for at in sorted(set(outside))]
        require(read_va(image,0xadae78,4)==b'Map\0','Literal table stem')
        body=dict(ranges=ranges,EH_instruction_windows=eh,decoded_calls=edges)
        require(not references or body=={k:references[0][k] for k in body},'Selected equivalence between both pins')
        references.append(dict(sha256=sha(path),architecture='x86',image_base='0x400000',**body))
    loader=code['0x7caae0']['code'];require('v40[2] == 110' in loader and 'v40[2] == v33' in loader and 'v32 + 552' in loader and 'v32 + 560' in loader,'Exact map count and geometry lanes')
    root=Path(json.loads((WS/'config/paths.json').read_text())['client_455'])/'DataTable';source=root/'Map.edf';main_bytes=source.read_bytes();main_data=decode(main_bytes)
    require(encode_with_envelope(main_bytes,main_data)==main_bytes,'Exact main EDF round trip');locales=[];accepted=None
    for path in sorted(root.glob('*/NDMap.edf')):
        payload=decode(path.read_bytes());count=struct.unpack_from('<I',payload)[0];result='Complete' if count==110 else 'LocalizedCount'
        if count==110:
            accepted=parse(main_data,payload);require(not accepted['main_tail'] and not accepted['localized_tail'],'Full two-stream consumption')
        require(encode_with_envelope(path.read_bytes(),payload)==path.read_bytes(),'ND EDF round trip')
        locales.append(dict(input=record(path),folder=path.parent.name,count=count,expected=result))
    require(accepted is not None and len(accepted['rows'])==110,'Complete available map/ND pair')
    fixtures=WS/'work/client-reference/map-data455';fixtures.mkdir(parents=True,exist_ok=True)
    oracle=fixtures/'canonical.bin';oracle.write_bytes(canonical(accepted));(fixtures/'main.bin').write_bytes(main_data);(fixtures/'localized.bin').write_bytes(decode((root/'zh-tw/NDMap.edf').read_bytes()))
    # Actual BSP node1 uses signed shorts at node lump +36/40/42/46.
    from map455 import MapFile
    bsp=[];geometry=bytearray()
    for name in ['bellato','cora','accretia']:
        path=root.parent/f'Map/{name}/{name}.bsp';nodes=MapFile(path.read_bytes(),'bsp').read('Node');require(len(nodes)>=48,'Actual BSP nodes')
        bounds_values=struct.unpack_from('<6h',nodes,36);left,top,right,bottom=bounds_values[0],bounds_values[2],bounds_values[3],bounds_values[5]
        require(right>left and bottom>top,'Valid actual world bounds');geometry+=nodes[:48]
        for row in accepted['rows']:
            w,h,x,y=struct.unpack_from('<4i',row['record'],552)
            sx,sy=struct.unpack('<2f',struct.pack('<2f',w/(right-left),h/(bottom-top)))
            px,pz=(left+right)/2,(top+bottom)/2
            geometry+=struct.pack('<4f',sx,sy,x+(px-left)*sx,y+(bottom-pz)*sy)
        bsp.append(dict(input=record(path),name=name,bounds=[left,top,right,bottom]))
    geo=fixtures/'geometry.bin';geo.write_bytes(geometry)
    rows=[]
    for row in accepted['rows']:
        d=row['record'];rows.append(dict(index=struct.unpack_from('<I',d)[0],name=d[4:36].split(b'\0')[0].decode('ascii'),geometry=list(struct.unpack_from('<4i',d,552)),portals=len(row['portals']),mines=len(row['mines'])//96,areas=len(row['areas'])))
    result=dict(status='CONFIRMED_SELECTED',scope='Exact selected Map/NDMap core and both appended layer streams;ordinary geometry producer;full map UI/world/gameplay acceptance open',script_sha256=sha(Path(__file__)),parser=record(WS/'scripts/map_data455.py'),raw=record(raw_path),session=record(session_path),cached_reference=record(old_path),references=references,new_full_assembly=9,new_instructions=sum(x['instruction_count'] for x in raw['assembly']),full_assembly=12,instructions=sum(x['instruction_count'] for x in assembly),main=record(source),locales=locales,rows=rows,layer_counts=[len(x['items']) for x in accepted['layers']],labels=sum(len(y['points']) for x in accepted['layers'] for y in x['items']),images=sum(len(y['image']) for x in accepted['layers'] for y in x['items']),consumed=[accepted['main_consumed'],accepted['localized_consumed']],canonical=record(oracle),decoded_fixtures=[record(fixtures/'main.bin'),record(fixtures/'localized.bin')],geometry_oracle=record(geo),bsp=bsp,gaps=['Only supplied zh-tw NDMap count110 matches rootMap110;other supplied locale counts31/100 must fail,not silently remap','Legacy map UI reset/index/avatar/object/portal behavior remains partially unported;normal geometry connection alone does not accept fullMiniMap','Both layer sections are retained by the source map owner;their actual global manager/UI consumer handoff remains open','Record588/288/96/84 data layout does not certify untraced field semantics,portal race/movement/protocol or private ABI','Checked truncation/path/name/text/allocation guards and atomic failed loads do not accept target unsafe reads/overflow/OOM/partial state/repeated-load leaks','Texture R3T teardown warnings/full world effect lifecycle and all earlier client acceptance gaps remain'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    out=WS/'inventory/client455-map-data-reference.json';out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(bodies=len(ranges),fullasm=12,instructions=result['instructions'],maps=110,labels=result['labels'],images=result['images'],consumed=result['consumed'],accepted_locale='zh-tw',locales={x['folder']:x['count'] for x in locales})))


if __name__=='__main__':main()
