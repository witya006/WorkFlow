"""Verify the complete text shader loader/compiler/named-binding contracts."""
import copy,hashlib,json,struct
from pathlib import Path
from compare_client_binaries import WS,pe
from build_client455_x87_math import read_va
from audit_client455_item_payloads import record
from audit_client455_lighting_consumers import contracts
from audit_client455_texture_lifetime import archive_objects
from checkpoint_client455_rvp_effects import require,load,check,sha
from client455_normal_link_evidence import validate_normal_link

def main():
    file=WS/'artifacts/client455-progress/shader-text136-reference.json';sessionfile=WS/'artifacts/client455-progress/shader-text136-session.json';raw=json.loads(file.read_text());normalized=copy.deepcopy(raw)
    for row in normalized['assembly']:row['total_instructions']=row['pages'][0]['total_instructions']
    normalized['cfg']=[{**row['result']['result'][0],'addr':row['addr']} for row in raw['cfg']];spans,count=contracts(normalized);require(len(raw['selected'])==7 and count==872,'Seven full shader-loader functions/872instructions')
    session=json.loads(sessionfile.read_text());require(session['saved']['ok'] and session['closed']['success'] and session['closed']['saved'] and session['after']['count']==0,'Owned IDA session saved/closed')
    pins=json.loads((WS/'config/client-target.json').read_text());refs=[];types=['n','b','i','f','v','m44','t','timer']
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';data=path.read_bytes();require(sha(path)==pins[key]['sha256'] and pe(data)['architecture']=='x86','Pinned455 x86 client')
        rows=[dict(owner_rva=hex(int(owner,16)-0x400000),rva=hex(at-0x400000),bytes=n,sha256=hashlib.sha256(read_va(data,at,n)).hexdigest()) for owner,at,n in spans]
        table=read_va(data,0xbf8018,32);strings=[]
        for pointer,name in zip(struct.unpack('<8I',table),types):
            value=read_va(data,pointer,len(name)+1);require(value==name.encode()+b'\0','Actual case-sensitive type table');strings.append(dict(rva=hex(pointer-0x400000),name=name,sha256=hashlib.sha256(value).hexdigest()))
        if refs:require(rows==refs[0]['ranges'] and table.hex()==refs[0]['type_table']['hex'] and strings==refs[0]['type_names'],'Both pinned bodies and parameter type constants agree')
        refs.append(dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=rows,type_table=dict(rva='0x7f8018',hex=table.hex()),type_names=strings))
    before=WS/'artifacts/client455-progress/before136';manifest=json.loads((before/'manifest.json').read_text());require(len(manifest)==51,'Exact135 runtime snapshot')
    for row in manifest:check(row)
    engine=load('client455-startup-engine-build');old=json.loads((before/'inventory/client455-startup-engine-build.json').read_text());require(engine['script_sha256']==sha(WS/'scripts/build_client455_engine_startup.py'),'Current engine generator')
    for row in engine['base_sources']+engine['derived_sources']:check(row)
    for name,value in engine['special_shader_owner'].items():require(value==sha(WS/'scripts/native'/name),'Current binary/text shader source owner')
    for key in ['camera_header_overlay','particle_header_overlay','vertex_header_overlay','material_header_overlay']:
        check(engine[key]);require(engine[key]['sha256']==old[key]['sha256'],'Shared declarations unchanged136')
    a,b=archive_objects(before/old['library'],True),archive_objects(WS/engine['library'],True);require(set(a)==set(b) and len(b)==67,'Same67 engine objects');changed=[];same=[];stamp=[]
    for name in a:
        x,y=a[name]['payload'],b[name]['payload'];(same if x==y else stamp if len(x)==len(y) and x[:4]+x[8:]==y[:4]+y[8:] else changed).append(name)
    require({Path(x).name.lower() for x in changed}=={'r3d3d8.obj'},'Only actual shader/device owner payload changes')
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS' and any(x['sha256']==engine['library_sha256'] for x in link['libraries']),'New text owner in ordinary own PE');mapping=(WS/link['map']['file']).read_text();require('RF455_LoadSpecialShaderText' in mapping,'Fallback retained by normal executable')
    gaps=[x for x in json.loads((before/'inventory/client455-material-shaders-checkpoint.json').read_text())['gaps'] if not x.startswith('Init.r3s fallback')]
    gaps+=['Text Init.r3s/FromFile/named lookup and selected failure/EOF semantics restored. Full numeric CRT parsing,malformed/overflow/OOM and all failure COM ownership remain unverified',
           'Typed object parameters are stored faithfully;no automatic GPU upload was found in8C9230. Actual VS12/13 writers occur in Fraction/refraction render owners8CDE30/8CE0A0;those complete draw owners and their unowned lanes remain open',
           'Positive binary FX/caps/real D3D9 Reset/lost-device/full splat combinations,per-BSP light owner and all remaining client-acceptance gaps remain open']
    out=dict(status='CONFIRMED_SELECTED',scope='Ordinary binary->text special-shader fallback,FromFile compiler,typed object parameters and named program services',script=record(Path(__file__)),contract_verifier=record(WS/'scripts/audit_client455_lighting_consumers.py'),raw=record(file),session=record(sessionfile),references=refs,full_assembly=7,instructions=count,verified_ranges=len(spans),CFG_complete=True,engine=record(WS/engine['library']),normal_executable=link['executable'],normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),snapshot=record(before/'manifest.json'),changed_members=changed,unchanged_members=same,timestamp_only_members=stamp,shared_headers_changed=False,gaps=gaps,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-shader-text-reference.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(functions=7,instructions=count,ranges=len(spans),changed=changed,executable=link['executable'])))
if __name__=='__main__':main()
