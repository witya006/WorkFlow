"""Pin record32/registry/countdown/FX and actual stage calls on both455 images."""
import hashlib,json,re,struct
from pathlib import Path
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS,pe
from rpk455 import Rpk


def main():
    file=WS/'artifacts/client455-progress/nuclear115-reference.json';session_file=file.with_name('nuclear115-session.json');raw=json.loads(file.read_text());session=json.loads(session_file.read_text())
    previous=load('client455-nuclear-protocol-reference');minimap=load('client455-nuclear-minimap-reference')
    for row in [previous['raw'],previous['session'],minimap['raw'],minimap['session']]:check(row)
    cached=json.loads((WS/previous['raw']['file']).read_text());cached114=json.loads((WS/minimap['raw']['file']).read_text())
    selected_old=['52a680','52a750','52a7a0','52a890','52a930','52a9d0','52aa90','52af00','52b080','52b1c0','52b290','52b330','52b4a0','52b540','52b5e0','52b690','52b740','52b7f0','52b870']
    code={x['addr'].lower():x for x in cached['functions'] if x['addr'].lower()[2:] in selected_old};code.update({x['addr'].lower():x for x in raw['functions']});code['0x52b3e0']=next(x for x in cached114['functions'] if x['addr']=='0x52b3e0')
    assembly={x['addr'].lower():x for x in raw['assembly']};assembly['0x52b3e0']=next(x for x in cached114['assembly'] if x['addr']=='0x52b3e0')
    bounds={x['query'].lower():x['fn'] for x in raw['bounds']['result']};bounds['0x52b3e0']=next(x['fn'] for x in cached114['bounds']['result'] if x['query']=='0x52b3e0')
    require(len(code)==len(bounds)==34 and len(assembly)==31,'Selected body/assembly coverage')
    require(all(x['cursor']['done'] and not x['truncated'] and x['line_count']==x['total_lines'] for x in code.values()),'Complete selected pseudocode')
    tails={'0x52ad70':(0xa2a6f0,0xa2a713),'0x52ae00':(0xa2a720,0xa2a74e),'0x52af00':(0xa2a750,0xa2a779)}
    for address,row in assembly.items():
        require(row['cursor']['done'] and row['instruction_count']==row['total_instructions']==len(row['asm']['lines']),'Complete assembly')
        begin=int(address,16);end=begin+int(bounds[address]['size'],16);tail=tails.get(address,(0,0))
        require(all(begin<=int(x['addr'],16)<end or tail[0]<=int(x['addr'],16)<tail[1] for x in row['asm']['lines']),'Body/EH coverage')
    require(session['closed']['success'] and session['closed']['saved'] and session['closed']['owned'] and session['after']['count']==0 and session['closed']['session_id']==session['owned_session_id'],'Owned IDA saved/closed/list0')
    pins=json.loads((WS/'config/client-target.json').read_text());references=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';image=path.read_bytes();require(sha(path)==pins[key]['sha256'] and pe(image)['architecture']=='x86','Pinned455 x86')
        ranges=[dict(rva=hex(int(address,16)-0x400000),bytes=int(fn['size'],16),sha256=hashlib.sha256(read_va(image,int(address,16),int(fn['size'],16))).hexdigest()) for address,fn in sorted(bounds.items())]
        eh=[dict(owner_rva=hex(int(owner,16)-0x400000),rva=hex(begin-0x400000),bytes=end-begin,sha256=hashlib.sha256(read_va(image,begin,end-begin)).hexdigest()) for owner,(begin,end) in tails.items()]
        edges=[]
        for body in assembly.values():
            for line in body['asm']['lines']:
                if not line['instruction'].startswith('call ') or not line.get('refs'):continue
                at=int(line['addr'],16);data=read_va(image,at,5)
                if data[0]!=0xe8:continue
                target=int(line['refs'][0]['addr'],16);require(at+5+struct.unpack('<i',data[1:])[0]==target,'Decoded direct CALL');edges.append(dict(rva=hex(at-0x400000),target_rva=hex(target-0x400000)))
        stage=[]
        for at,target in [(0x54638c,0x52ad70),(0x54b059,0x52ae70)]:
            data=read_va(image,at,5);require(data[0]==0xe8 and at+5+struct.unpack('<i',data[1:])[0]==target,'Actual MainGame init/render calls')
            stage.append(dict(rva=hex(at-0x400000),target_rva=hex(target-0x400000)))
        require(read_va(image,0xaa8dd4,4)==bytes(4),'Unknown race name empty literal')
        row=dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=ranges,tails=eh,decoded_calls=edges,stage_calls=stage,unknown_race_empty_literal=dict(rva='0x6a8dd4',bytes=4,sha256=hashlib.sha256(bytes(4)).hexdigest()))
        require(not references or {k:v for k,v in row.items() if k!='sha256'}=={k:v for k,v in references[0].items() if k!='sha256'},'Two-pin selected equivalence');references.append(row)
    timer=assembly['0x52a7e0']['asm']['lines'];instructions=[x['instruction'] for x in timer]
    require('jle loc_52A880' in instructions and 'cmp eax, 3E8h' in instructions and 'jb short loc_52A880' in instructions and 'add ecx, 1' in instructions,'Signed positive countdown/unsigned1000ms/oldcount message')
    require(sum('__imp_timeGetTime' in x for x in instructions)==2 and any('mov dword_1012854, eax'==x for x in instructions),'Actual shared process clock')
    ctor=assembly['0x52a680']['asm']['lines'];require(not any(re.search(r'\[(?:eax|ecx|edx|esi)\+0?Ch\]',x['instruction']) for x in ctor),'No confirmed DWORD12 initializer')
    require('1358041392' in code['0x52a890']['code'] and '277036' in code['0x52a890']['code'] and '1358041648' in code['0x52a930']['code'] and '277038' in code['0x52a930']['code'],'Actual launch/impact IDs')
    reset=code['0x52aa90']['code'];require(reset.index('sub_8BD590')<reset.index('sub_7D9730') and '277034, 2' in reset and '*(this + 1) = 0' in reset,'Reset audio-before-radar and detached handles')
    require('sub_52AC00(this + 3, 0)' in code['0x52b080']['code'] and 'sub_52AC00(this + 3, 0)' in code['0x52b290']['code'],'Pending0 even missing/empty mutation')
    require('sub_52B1C0(this)' in code['0x52ae00']['code'] and 'sub_52AB30()' in code['0x52ae00']['code'],'Manager destruction clear+empty aiming destructor')
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);archive_path=client/'Effect/EffectEntity59.rpk';archive=Rpk(archive_path.read_bytes());magic_manifest=client/'Effect/MagicSptList.spt';sound_manifest=client/'Snd/WaveList.spt'
    resource_reference=load('client455-effect-resources-reference')
    for row in resource_reference['inputs']:check(row)
    manifest=magic_manifest.read_bytes();scripts=[]
    for ident,member in [(1358041136,b'weapon_1\\nuclear\\c\\nuclear_land_mag02.spt'),(1358041392,b'weapon_1\\nuclear\\i\\nuclear_missile.spt'),(1358041648,b'weapon_1\\nuclear\\d\\nuclear_04\\nuclear_mag.spt')]:
        match=re.findall(rb'^\s*0x'+f'{ident:08x}'.encode()+rb'\s+(\S+)',manifest,re.I|re.M);require(len(match)==1 and match[0].lower().lstrip(b'\\')==member,'Actual magicID manifest route')
        data=archive.read(member);destination=WS/'work/client-reference/nuclear115'/member.split(b'\\')[-1].decode();require(destination.read_bytes()==data,'Saved selected archived script')
        scripts.append(dict(magicID=ident,archive=dict(file=str(archive_path),sha256=sha(archive_path)),member=member.decode(),copy=record(destination),bytes=len(data)))
    report=dict(status='CONFIRMED_SELECTED',scope='Actual record32/registry/FX/tag2/shared countdown and target stage callsites;ordinary receiver/full stage lifecycle/world acceptance remain open',script_sha256=sha(Path(__file__)),raw=record(file),session=record(session_file),cached_reference=[record(WS/'inventory/client455-nuclear-protocol-reference.json'),record(WS/'inventory/client455-nuclear-minimap-reference.json')],selected_functions=len(code),full_assembly_functions=len(assembly),new_assembly_functions=len(raw['assembly']),instructions=sum(x['instruction_count'] for x in assembly.values()),new_instructions=sum(x['instruction_count'] for x in raw['assembly']),references=references,resource_scripts=scripts,magic_manifest=dict(file=str(magic_manifest),sha256=sha(magic_manifest)),sound_manifest=dict(file=str(sound_manifest),sha256=sha(sound_manifest)),countdown='Process clock1012850/1012854 shared across records/containers;positive signedDWORD28 only;two initial reads;unsigned elapsed>=1000;one decrement/no catchup;C17 emits newcount+1;sorted map order consumes first due tick',record='Known handles0/4/8 and float3@16/count28 start0;DWORD12 untouched;empty destructor;map key unsigned(race<<8)|index',cleanup='Remove/Reset clear aiming.pending before empty/missing checks;RadarOff always stops277034/tag2;Reset stops audio before radar disappear0 and detaches launch/impact handles without killing them;position/countdown retained',owner='Target manager is allocated32 in MainGame init and updated late in MainGame render;own current MainApp bridge is temporary,proper stage birth/destruction not yet restored',gaps=['Actual group60 receiver/selected item serial/send/dialog/minimap registry consumers remain open','Proper stage-owned container birth/destruction and full world effects/trajectory/camera quake/compositing/reset acceptance remain open','Full private STL ABI,unknown DWORD12 producers,unsafe/null/OOM/FP/concurrency and all prior client-acceptance gaps remain open'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-nuclear-registry-reference.json').write_text(json.dumps(report,indent=2)+'\n');print(f'CONFIRMED_SELECTED:{len(code)}bodies/{len(assembly)}fullasm/{report["instructions"]}instructions;bothpins/record32/sharedclock/tag2/launch/impact,IDA savedclosed/list0')


if __name__=='__main__':main()
