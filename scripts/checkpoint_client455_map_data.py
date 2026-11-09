"""Validate current map-data recovery without accepting the remaining client."""
import hashlib,json,re,struct,subprocess
from pathlib import Path
from audit_client455_map_data import record
from audit_client455_own_entry import symbol
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check,load,require,sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS,pe


def main():
    ref=load('client455-map-data-reference');require(ref['script_sha256']==sha(WS/'scripts/audit_client455_map_data.py') and (ref['new_full_assembly'],ref['full_assembly'],ref['instructions'])==(9,12,1850),'Current reference provenance')
    for row in [ref['parser'],ref['raw'],ref['session'],ref['cached_reference'],ref['main'],ref['canonical'],ref['geometry_oracle']]+ref['decoded_fixtures']+[x['input'] for x in ref['locales']]+[x['input'] for x in ref['bsp']]:
        require(sha(WS/row['file'])==row['sha256'],'Changed input/evidence '+row['file'])
    pins=json.loads((WS/'config/client-target.json').read_text())
    for folder,key,pin in zip(['current','reference-backup'],['behavior_reference','secondary_reference'],ref['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';data=path.read_bytes();require(sha(path)==pins[key]['sha256']==pin['sha256'] and pe(data)['architecture']=='x86','Pinned client')
        for row in pin['ranges']+pin['EH_instruction_windows']:require(hashlib.sha256(read_va(data,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()==row['sha256'],'Pinned body/EH bytes')
        for row in pin['decoded_calls']:
            at=0x400000+int(row['rva'],16);b=read_va(data,at,5);require(b[0]==0xe8 and at+5+struct.unpack('<i',b[1:])[0]==0x400000+int(row['target_rva'],16),'Pinned decoded call')
    state=json.loads((WS/ref['session']['file']).read_text());require(state['closed']['saved'] and state['after']['count']==0 and state['supplement']['closed']['saved'] and state['supplement']['after']['count']==0,'Both owned sessions saved/closed')
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS' and link['client_objects']==182 and not link['unique_unresolved'],'Normal link')
    prep,build=load('client455-normal-preparation'),load('client455-normal-build');require(prep['script_sha256']==sha(WS/'scripts/prepare_client455_normal.py') and prep['map_data_port_sha256']==sha(WS/'scripts/client455_map_data_port.py'),'Current preparation')
    require(not build['build_exit'] and not build['errors'] and build['canonical_kernel_objects']==20 and build['source_manifest_sha256']==prep['manifest_sha256'],'Current182client/20kernel build')
    require(len(list((WS/'work/client455-port/normal/build/RFClient455Facade.dir/Release').glob('*.obj')))==70,'70 source facade objects')
    sources=[record(WS/'scripts/native'/name) for name in ['client455_map_data.h','client455_map_data.cpp']]
    for row in sources:require(prep['record_inputs'][Path(row['file']).name]==row['sha256'],'Prepared map sources')
    check(dict(file=prep['manifest'],sha256=prep['manifest_sha256']));manifest=json.loads((WS/prep['manifest']).read_text());providers=[]
    for suffix in ['source/cland.h','source/cland.cpp','source/userinterface/gamewindow/etcwin/guiminimapwindow.cpp','generated/client455_map_data.cpp','include/client455_map_data.h']:
        rows=[x for x in manifest if x['file'].lower().endswith('/'+suffix)];require(len(rows)==1,'Actual generated map provider '+suffix)
        for row in rows:check(row);check(dict(file=row['input'],sha256=row['input_sha256']))
        providers+=rows
    map_source=(WS/'work/client455-port/normal/source/userinterface/gamewindow/etcwin/guiminimapwindow.cpp').read_bytes();require(b'l_ptRealMinimapSize[8]' not in map_source and b'm_byMiniMapIndex > 7' not in map_source,'No legacy8map geometry/clamp')
    mapping=(WS/link['map']['file']).read_text();own=(WS/link['executable']['file']).read_bytes();base=pe(own)['image_base'];starts=sorted({int(x,16) for x in re.findall(r'^\s+0001:[0-9a-fA-F]{8}\s+\S+\s+([0-9a-fA-F]{8})\b',mapping,re.M)});decoded=[]
    def name(prefix):
        values=re.findall(r'^\s+0001:[0-9a-fA-F]{8}\s+('+re.escape(prefix)+r'\S*)\s+[0-9a-fA-F]{8}\b',mapping,re.M);require(len(values)==1,'Unique retained source symbol '+prefix);return values[0]
    dumpbin=Path(load('msvc-verification')['compiler_path'].splitlines()[0]).with_name('dumpbin.exe')
    def edges(prefix):
        full=name(prefix);begin=symbol(mapping,full);end=next(x for x in starts if x>begin);run=subprocess.run([str(dumpbin),'/DISASM:BYTES',f'/RANGE:0x{begin:x},0x{end:x}',str(WS/link['executable']['file'])],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW);require(not run.returncode,'Own decoded source')
        path=WS/f'artifacts/client455-progress/map117-own-{len(decoded)}.txt';path.write_bytes(run.stdout);calls=[]
        for line in run.stdout.decode(errors='replace').splitlines():
            m=re.match(r'^\s+([0-9A-F]{8}): ((?:[0-9A-F]{2} )+)\s+(\w+)\s*(.*?)\s*$',line)
            if not m:continue
            at=int(m[1],16);b=bytes.fromhex(m[2])
            if at>=end:continue
            require(b==read_va(own,at,len(b)),'Own instruction bytes')
            if m[3] in ['call','jmp'] and len(b)==5 and b[0] in [0xe8,0xe9]:calls.append(dict(rva=hex(at-base),target_rva=hex(at+5+struct.unpack('<i',b[1:])[0]-base)))
        decoded.append(dict(function=full,rva=hex(begin-base),disassembly=record(path),edges=calls));return calls
    def edge(caller,callee):require(any(x['target_rva']==hex(symbol(mapping,name(callee))-base) for x in edges(caller)),'Ordinary linked call '+caller+' -> '+callee)
    edge('?LoadData@CLand@@','?RF455_LoadMapData@@');edge('?RF455_LoadMapData@@','?RF455_ParseMapData@@')
    # MSVC inlines ApplyMiniMapGeometry455 into the ordinary UI_SetMinimap.
    edge('?UI_SetMinimap@CLand@@','?SetNuclearMapGeometry455@CGUIMiniMapWindow@@');edge('?UI_SetMinimap@CLand@@','?SetMapBound@CGUIMiniMapWindow@@')
    native=load('client455-map-data-native');require(native['script_sha256']==sha(WS/'scripts/probe_client455_map_data.py') and native['builder_sha256']==sha(WS/'scripts/client455_own_probe.py') and native['reference_sha256']==sha(WS/'inventory/client455-map-data-reference.json') and native['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json'),'Current native evidence')
    for row in [native['source'],native['exe'],native['map'],native['console'],native['output'],native['canonical_actual']]+native['inputs']:check(row)
    actual=json.loads((WS/native['output']['file']).read_text());require(native['native']==actual and not native['natural_exit'] and actual['status']=='PASS' and actual['checks']==2692 and actual['geometry_cases']==330 and actual['ordinary_CLand_LoadData'] and actual['ordinary_geometry_provider'] and actual['GPU_frames']==0,'Real owner/provider assertions')
    require(native['canonical_equal'] and native['canonical_actual']['sha256']==ref['canonical']['sha256'],'Complete independent canonical bytes')
    early,ui=load('client455-startup-native'),load('client455-ui-startup-native');link_hash=sha(WS/'inventory/client455-normal-link.json')
    require(early['normal_link_sha256']==ui['normal_link_sha256']==link_hash and not early['debugger_exit'] and early['sound_return']==1 and not ui['debugger_exit'] and ui['completed_existing_client_create'] and any(x['name']=='after_client_create' and x['eax']==1 for x in ui['markers']) and all(x['first_chance']==1 for x in ui['exceptions']),'Exact own PE/Create1')
    check(early['events']);check(ui['events']);engine=load('client455-startup-engine-build');require(sha(WS/engine['library'])==engine['library_sha256']=='546a7529b51139e856b1a108fcad7849c14b2d00563b7abbfdcc8db10026fa5a','Unchanged engine67')
    historical=WS/'artifacts/client455-progress/client455-nuclear-receiver-checkpoint-before117.json';old=json.loads(historical.read_text());require(old['receiver_checks']==101 and old['viewed_GPU_frames']==20,'Historical116 snapshot')
    fresh=['map-data-reference','map-data-native','normal-preparation','normal-build','normal-consumers','normal-link','own-entry','startup-audit','startup-native','ui-startup-native']
    result=dict(status='PARTIAL',scope=ref['scope'],script_sha256=sha(Path(__file__)),sources=sources,generated_providers=providers,normal_link_sha256=link_hash,normal_executable=link['executable'],own_decoded_calls=decoded,native_checks=actual['checks'],maps=110,layer_counts=[103,7],labels=660,image_bytes=257919,ordinary_CLand_load=True,ordinary_geometry_provider=True,geometry_cases=330,GPU_frames=0,actual_BSP_nodes_as_fixture=True,full_BSP_load_rerun=False,incompatible_locales_rejected=8,current_complete_texture_lifetime=False,previous116_gate=record(historical),previous116_runtime_gate='HISTORICAL_NOT_RERUN',fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in fresh},engine_unchanged=engine['library_sha256'],unchanged_bulk_suites_rerun=False,gaps=ref['gaps'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-map-data-checkpoint.json').write_text(json.dumps(result,indent=2)+'\n');print('PARTIAL:ordinary Map/NDMap110+2layers/660labels/257919imagebytes;2692checks/330geometry/Create1;fullMiniMap/world/texture/M9OPEN')


if __name__=='__main__':main()
