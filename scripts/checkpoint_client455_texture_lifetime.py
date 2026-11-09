"""Current client gate for selected texture teardown and Warning recovery."""
import hashlib,json,re,struct,subprocess
from pathlib import Path
from audit_client455_item_payloads import record
from audit_client455_own_entry import symbol
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check,load,require,sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS,pe


def main():
    ref=load('client455-texture-lifetime-reference');require(ref['script_sha256']==sha(WS/'scripts/audit_client455_texture_lifetime.py') and (ref['full_assembly'],ref['instructions'],ref['new_full_assembly'],ref['new_instructions'])==(18,999,17,874),'Current selected reference')
    for row in [ref['raw'],ref['session'],ref['cached_reference'],ref['old_engine'],ref['old_engine_report'],ref['engine'],ref['warning_source']]:check(row)
    session=json.loads((WS/ref['session']['file']).read_text());require(session['closed']['saved'] and session['after']['count']==0,'IDA saved/closed')
    pins=json.loads((WS/'config/client-target.json').read_text())
    for folder,key,pin in zip(['current','reference-backup'],['behavior_reference','secondary_reference'],ref['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';data=path.read_bytes();require(sha(path)==pins[key]['sha256']==pin['sha256'] and pe(data)['architecture']=='x86','Pinned455')
        for row in pin['ranges']+pin['data_and_shared_tail']:require(hashlib.sha256(read_va(data,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()==row['sha256'],'Pinned body/literal/tail')
        for row in pin['decoded_calls']:
            at=0x400000+int(row['rva'],16);b=read_va(data,at,5);require(b[0]==0xe8 and at+5+struct.unpack('<i',b[1:])[0]==0x400000+int(row['target_rva'],16),'Pinned decoded call')
    engine=load('client455-startup-engine-build');require(engine['script_sha256']==sha(WS/'scripts/build_client455_engine_startup.py') and engine['library_sha256']==sha(WS/engine['library'])==ref['engine']['sha256'] and engine['objects']==67 and len(engine['derived_sources'])==13,'Current67 engine')
    require(len(ref['code_changed_archive_members'])==1 and len(ref['timestamp_only_archive_members'])==1 and len(ref['unchanged_archive_members'])==65,'One code member changed;one timestamp-only/65byteequal')
    for row in engine['derived_sources']+engine['base_sources']+[engine['baseline_library']]:check(row)
    warning=next(x for x in engine['derived_sources'] if x['file'].endswith('/jerror.cpp'));source=(WS/warning['file']).read_bytes();require(b'\\x3c\\x2d\\xb0\\xe6\\xb0\\xed' in source,'Correct generated Warning literal');check(ref['warning_source'])
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS' and link['client_objects']==182 and not link['unique_unresolved'],'Normal link');link_hash=sha(WS/'inventory/client455-normal-link.json')
    require(any(x['file']==engine['library'] and x['sha256']==engine['library_sha256'] for x in link['libraries']),'Actual normal PE links current engine')
    native=load('client455-texture-lifetime-native');require(native['script_sha256']==sha(WS/'scripts/probe_client455_texture_lifetime.py') and native['normal_link_sha256']==link_hash and native['engine_library_sha256']==engine['library_sha256'],'Current texture scenario')
    for row in [native['source'],native['exe'],native['map'],native['console'],native['output'],native['trace'],native['scenario_script']]+native['included_sources']+native['inputs']:check(row)
    require(not native['natural_exit'] and native['native']==json.loads((WS/native['output']['file']).read_text()) and native['native']['status']=='PASS' and native['native']['checks']==109 and native['native']['warnings']==20,'Actual native scenario')
    trace=json.loads((WS/native['trace']['file']).read_text());require(trace['checks']==649 and len(trace['pins'])==20 and len(trace['world_pins'])==132,'Current observed cleanup coverage')
    verification=load('client455-texture-lifetime-verification');require(verification['status']=='PASS' and verification['script_sha256']==sha(WS/'scripts/verify_client455_texture_lifetime.py') and verification['native_sha256']==sha(WS/'inventory/client455-texture-lifetime-native.json') and verification['reference_sha256']==sha(WS/'inventory/client455-texture-lifetime-reference.json'),'Independent target trace oracle');check(verification['oracle'])
    review=load('client455-texture-lifetime-visual-review');require(review['reviewed'] and review['reviewed_frames']==5 and review['script_sha256']==sha(WS/'scripts/review_client455_texture_lifetime.py') and review['native_sha256']==sha(WS/'inventory/client455-texture-lifetime-native.json'),'Viewed current frames');check(review['sheet'])
    for row in review['frames']:check(row);check(row['preview'])
    maps=load('client455-map-data-native');require(maps['normal_link_sha256']==link_hash and maps['script_sha256']==sha(WS/'scripts/probe_client455_map_data.py') and maps['native']['checks']==2692 and maps['native']['geometry_cases']==330 and maps['canonical_equal'] and not maps['natural_exit'],'Current map regression')
    for row in [maps['source'],maps['exe'],maps['map'],maps['output'],maps['console'],maps['canonical_actual']]+maps['inputs']:check(row)
    early,ui,contracts=load('client455-startup-native'),load('client455-ui-startup-native'),load('client455-startup-contracts-native');require(contracts['build_sha256']==sha(WS/'inventory/client455-startup-engine-build.json') and early['normal_link_sha256']==ui['normal_link_sha256']==link_hash and not early['debugger_exit'] and early['sound_return']==1 and not ui['debugger_exit'] and ui['completed_existing_client_create'] and any(x['name']=='after_client_create' and x['eax']==1 for x in ui['markers']) and all(x['first_chance']==1 for x in ui['exceptions']),'Exact own PE startup/device/Create1');check(early['events']);check(ui['events'])
    # Decode the actual ordinary executable's Warning body,not only the probe.
    mapping=(WS/link['map']['file']).read_text();image=(WS/link['executable']['file']).read_bytes();base=pe(image)['image_base'];name=next(x for x in re.findall(r'^\s+0001:[0-9a-fA-F]{8}\s+(\S+)\s+',mapping,re.M) if x.startswith('?Warning@@'));begin=symbol(mapping,name);starts=sorted({int(x,16) for x in re.findall(r'^\s+0001:[0-9a-fA-F]{8}\s+\S+\s+([0-9a-fA-F]{8})\b',mapping,re.M)});end=min(x for x in starts if x>begin)
    dumpbin=Path(load('msvc-verification')['compiler_path'].splitlines()[0]).with_name('dumpbin.exe');run=subprocess.run([str(dumpbin),'/DISASM:BYTES',f'/RANGE:0x{begin:x},0x{end:x}',str(WS/link['executable']['file'])],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW);require(not run.returncode,'Own Warning disassembly');out=WS/'artifacts/client455-progress/texture118-own-warning.txt';out.write_bytes(run.stdout)
    require(b'MessageBox' not in run.stdout,'No old warning dialog branch');instructions=0
    for line in run.stdout.decode(errors='replace').splitlines():
        m=re.match(r'^\s+([0-9A-F]{8}): ((?:[0-9A-F]{2} )+)\s+',line)
        if m and int(m[1],16)<end:require(read_va(image,int(m[1],16),len(bytes.fromhex(m[2])))==bytes.fromhex(m[2]),'Actual own instruction bytes');instructions+=1
    require(instructions>10 and bytes.fromhex(ref['warning_suffix_hex']) in image,'Retained own Warning body/literal')
    historical=WS/'artifacts/client455-progress/client455-map-data-checkpoint-before118.json';require(historical.exists(),'Historical117 snapshot')
    fresh=['texture-lifetime-reference','texture-lifetime-native','texture-lifetime-verification','texture-lifetime-visual-review','startup-engine-build','normal-link','normal-consumers','own-entry','startup-audit','startup-native','startup-contracts-native','ui-startup-native','map-data-native']
    result=dict(status='PARTIAL',scope=ref['scope'],script_sha256=sha(Path(__file__)),normal_executable=link['executable'],normal_link_sha256=link_hash,engine=ref['engine'],old_engine=ref['old_engine'],native_registry_checks=109,native_texture_observations=649,actual_effect_owners=21,texture_calls=24,shared_decrements=4,warning_count=20,effect_COM_releases=20,world_COM_releases=132,tracked_Dmalloc_final=0,viewed_GPU_frames=5,map_checks=2692,map_geometry_cases=330,warning_fixes=['Exact CP949 warning label','Return without dialog when callback absent'],own_warning=dict(symbol=name,rva=hex(begin-base),bytes=end-begin,sha256=hashlib.sha256(read_va(image,begin,end-begin)).hexdigest(),disassembly=record(out)),full_memory_balance=False,full_device_lifecycle=False,previous117_gate=record(historical),old_runtime_gates='HISTORICAL;fresh registry/map/startup on new engine;other older suites not rerun',fresh_evidence={x:record(WS/f'inventory/client455-{x}.json') for x in fresh},gaps=ref['gaps'],unchanged_bulk_suites_rerun=False,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-texture-lifetime-checkpoint.json').write_text(json.dumps(result,indent=2)+'\n');print('PARTIAL:target Warning label/no-dialog fixed;109+649/152COM releases/20exactwarnings/Dmalloc0/5viewedGPU;maps2692/330/Create1;full lifecycle/M9OPEN')


if __name__=='__main__':main()
