"""Pin texture ownership/release/Warning contracts and the single engine change."""
import hashlib,json,struct
from pathlib import Path
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS,pe


def archive_objects(path,include_payload=False):
    data=path.read_bytes();require(data[:8]==b'!<arch>\n','COFF archive');at=8;long=b'';rows={}
    while at<len(data):
        header=data[at:at+60];require(len(header)==60 and header[58:60]==b'`\n','COFF archive header');n=int(header[48:58]);name=header[:16].decode('ascii').strip();payload=data[at+60:at+60+n];require(len(payload)==n,'COFF archive payload');at+=60+n+(n&1)
        if name=='//':long=payload;continue
        if name in ['/','/SYM64/']:continue
        if name.startswith('/'):
            off=int(name[1:]);tail=long[off:];ends=[x for x in [tail.find(b'\0'),tail.find(b'/\n')] if x>=0];require(ends,'COFF long name');name=tail[:min(ends)].decode('ascii')
        else:name=name.rstrip('/')
        require(name not in rows,'Unique COFF member');rows[name]=dict(bytes=n,sha256=hashlib.sha256(payload).hexdigest())
        if include_payload:rows[name]['payload']=payload
    require(at==len(data),'Full archive consumption');return rows


def main():
    raw_file=WS/'artifacts/client455-progress/texture118-reference.json';session_file=WS/'artifacts/client455-progress/texture118-session.json';raw=json.loads(raw_file.read_text());session=json.loads(session_file.read_text());selected=set(raw['selected'])
    functions={x['addr']:x for x in raw['functions'] if x['addr'] in selected};bounds={x['query']:x['fn'] for x in raw['bounds']['result']};assembly={x['addr']:x for x in raw['assembly']}
    require(len(selected)==17 and set(functions)==set(bounds)==set(assembly)==selected,'Selected coverage')
    require(all(x['cursor']['done'] and not x['truncated'] and x['line_count']==x['total_lines'] for x in functions.values()),'Complete selected pcode')
    require(all(x['cursor']['done'] and x['instruction_count']==x['total_instructions']==len(x['asm']['lines']) for x in assembly.values()),'Complete selected assembly')
    require(sum(x['instruction_count'] for x in assembly.values())==874,'New instruction total')
    require(session['closed']['success'] and session['closed']['saved'] and session['after']['count']==0,'Owned IDA saved/closed')
    cached=load('client455-effect-resources-reference');check(cached['raw_evidence']);old=json.loads((WS/cached['raw_evidence']['file']).read_text());address='0x7e4bc0'
    release=next(x for x in old['assembly'] if x['addr']==address);require(release['cursor']['done'] and release['instruction_count']==release['total_instructions']==len(release['asm']['lines']),'Cached full release assembly');assembly[address]=release;bounds[address]=next(x['fn'] for x in old['ranges']['result'] if x['query']==address)
    pins=json.loads((WS/'config/client-target.json').read_text());references=[]
    data_ranges=[(0xb39258,7,'Warning CP949 suffix'),(0xb394c4,37,'R3T release warning'),(0xbf7f8c,20,'Initial count/capacity constants'),(0x8f2de0,55,'Shared ReleaseSystemTexture tail')]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        file=WS/f'work/client-reference/{folder}/RF_Online.bin';image=file.read_bytes();require(sha(file)==pins[key]['sha256'] and pe(image)['architecture']=='x86','Pinned x86 client')
        ranges=[dict(rva=hex(int(addr,16)-0x400000),bytes=int(fn['size'],16),sha256=hashlib.sha256(read_va(image,int(addr,16),int(fn['size'],16))).hexdigest()) for addr,fn in sorted(bounds.items())]
        literal=[dict(rva=hex(at-0x400000),bytes=n,sha256=hashlib.sha256(read_va(image,at,n)).hexdigest(),role=role) for at,n,role in data_ranges]
        require(read_va(image,0xb39258,7)==bytes.fromhex('3c2db0e6b0ed00'),'Target warning suffix is warning,not legacy error')
        require(struct.unpack('<5I',read_va(image,0xbf7f8c,20))==(1,64,1,64,64),'Actual initial table capacities')
        calls=[]
        for fn in assembly.values():
            for line in fn['asm']['lines']:
                if not line['instruction'].startswith('call ') or not line.get('refs'):continue
                at=int(line['addr'],16);b=read_va(image,at,5)
                if b[0]!=0xe8:continue
                target=int(line['refs'][0]['addr'],16);require(at+5+struct.unpack('<i',b[1:])[0]==target,'Decoded actual call');calls.append(dict(rva=hex(at-0x400000),target_rva=hex(target-0x400000)))
        row=dict(sha256=sha(file),architecture='x86',image_base='0x400000',ranges=ranges,data_and_shared_tail=literal,decoded_calls=calls)
        require(not references or {k:v for k,v in row.items() if k!='sha256'}=={k:v for k,v in references[0].items() if k!='sha256'},'Both pin equivalence');references.append(row)
    warning=assembly['0x8f1160']['asm']['lines'];require([x['instruction'].split(' ;')[0] for x in warning if x['instruction'].startswith('call ')]==['call edx','call sub_8722F1'],'Callback/security-cookie only;no legacy MessageBox fallback')
    old_engine_file=WS/'artifacts/client455-progress/client455-startup-engine-build-before118.json';old_engine=json.loads(old_engine_file.read_text());engine=load('client455-startup-engine-build');old_lib=WS/'artifacts/client455-progress/engine-before118.lib';new_lib=WS/engine['library']
    require(sha(old_lib)==old_engine['library_sha256']=='546a7529b51139e856b1a108fcad7849c14b2d00563b7abbfdcc8db10026fa5a','Exact old engine snapshot')
    require(engine['script_sha256']==sha(WS/'scripts/build_client455_engine_startup.py') and engine['objects']==67 and len(engine['derived_sources'])==13,'Current engine build')
    for row in engine['base_sources']+engine['derived_sources']+[engine['baseline_library']]:check(row)
    a,b=archive_objects(old_lib),archive_objects(new_lib);require(set(a)==set(b) and len(a)==67,'Same67 archive members');changed=[name for name in a if a[name]!=b[name]]
    old_payload,new_payload=archive_objects(old_lib,True),archive_objects(new_lib,True);timestamp_only=[];code_changed=[]
    for name in changed:
        x,y=old_payload[name]['payload'],new_payload[name]['payload']
        if len(x)==len(y) and struct.unpack_from('<H',x)[0]==struct.unpack_from('<H',y)[0]==0x14c and x[:4]+x[8:]==y[:4]+y[8:]:
            timestamp_only.append(dict(member=name,old_timestamp=struct.unpack_from('<I',x,4)[0],new_timestamp=struct.unpack_from('<I',y,4)[0],normalized_sha256=hashlib.sha256(x[:4]+b'\0'*4+x[8:]).hexdigest()))
        else:code_changed.append(name)
    require(len(code_changed)==1 and code_changed[0].lower().endswith('jerror.obj'),'Only diagnostic object code changed')
    unchanged=[dict(member=name,**a[name]) for name in a if name not in changed]
    require(engine['warning']['client455_warning.inc']==sha(WS/'scripts/native/client455_warning.inc'),'Prepared Warning source')
    result=dict(status='CONFIRMED_SELECTED',scope='Texture registry/shared counter/cache owner/global table teardown and target Warning callback semantics;full device/texture lifecycle remains open',script_sha256=sha(Path(__file__)),raw=record(raw_file),session=record(session_file),cached_reference=record(WS/'inventory/client455-effect-resources-reference.json'),new_full_assembly=17,new_instructions=874,full_assembly=len(assembly),instructions=sum(x['instruction_count'] for x in assembly.values()),references=references,warning_suffix_hex='3c2db0e6b0ed',warning_base_hex=read_va((WS/'work/client-reference/current/RF_Online.bin').read_bytes(),0xb394c4,36).hex(),old_engine=record(old_lib),old_engine_report=record(old_engine_file),engine=record(new_lib),changed_archive_members=changed,code_changed_archive_members=code_changed,timestamp_only_archive_members=timestamp_only,unchanged_archive_members=unchanged,warning_source=record(WS/'scripts/native/client455_warning.inc'),gaps=['Runtime trace covers managed effect/world textures;independent flag8 branch only static,pointer/OOM/concurrency/reset/reentry/invalid-ID domains remain open','Selected normal teardown and tracked Dmalloc0 do not establish all CRT/COM/GPU memory balance or full device reset/shadow/render-target lifecycle','Unbounded target Warning buffer/null input/unchecked ranges and incidental return/private ABI behavior are not accepted','All previous client acceptance gaps,full world frame/gameplay/auth/normal stage flows and M6/M6F/M7/M9 remain open'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-texture-lifetime-reference.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(fullasm=result['full_assembly'],instructions=result['instructions'],newasm=17,newinstructions=874,changed=code_changed,timestamp_only=len(timestamp_only),unchanged_objects=len(unchanged),engine=engine['library_sha256'])))


if __name__=='__main__':main()
