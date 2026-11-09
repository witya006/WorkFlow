"""Current selected quake gate;preserve M6/M6F/M7/M9 gaps explicitly."""
import hashlib,json,re,struct,subprocess
from pathlib import Path
from audit_client455_item_payloads import record
from audit_client455_own_entry import symbol
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check,load,require,sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS,pe
from probe_client455_quake import verify as verify_cpu
from probe_client455_quake_effects import verify as verify_effects

def main():
    ref=load('client455-quake-reference');require(ref['status']=='CONFIRMED_SELECTED' and ref['script_sha256']==sha(WS/'scripts/audit_client455_quake.py') and ref['full_assembly']==18 and ref['instructions']==2600,'Current static target evidence')
    for row in [ref['raw'],ref['session'],ref['cached_scheduler'],ref['engine'],ref['old_engine']]+ref['source']:check(row)
    link=load('client455-normal-link');validate_normal_link(link);lh=sha(WS/'inventory/client455-normal-link.json');engine=load('client455-startup-engine-build');check(link['executable']);check(link['map']);check(ref['engine']);require(engine['library_sha256']==ref['engine']['sha256'] and any(x['file']==engine['library'] and x['sha256']==engine['library_sha256'] for x in link['libraries']),'Normal executable selects current engine')
    cpu=load('client455-quake-native');require(cpu['normal_link_sha256']==lh and cpu['script_sha256']==sha(WS/'scripts/probe_client455_quake.py') and cpu['engine_report_sha256']==sha(WS/'inventory/client455-startup-engine-build.json'),'Current CPU test')
    for row in [cpu['exe'],cpu['map'],cpu['source'],cpu['oracle'],cpu['trace'],cpu['console']]:check(row)
    require(verify_cpu(json.loads((WS/cpu['trace']['file']).read_text()))==cpu['verdict'],'Reproduce CPU oracle')
    fx=load('client455-quake-effects-native');require(fx['status']=='PASS' and fx['normal_link_sha256']==lh and fx['driver_script']['sha256']==sha(WS/'scripts/probe_client455_quake_effects.py') and fx['script_sha256']==sha(WS/'scripts/probe_client455_nuclear_registry.py') and not fx['natural_exit'] and fx['native']['warnings']==20,'Current actual impact scenario')
    for row in [fx['exe'],fx['map'],fx['source'],fx['oracle'],fx['trace'],fx['console'],fx['output'],fx['registry_template'],fx['trace_header'],fx['driver_script']]+fx['inputs']:check(row)
    require(verify_effects(json.loads((WS/fx['trace']['file']).read_text()))==fx['verdict'],'Reproduce actual impact oracle')
    review=load('client455-quake-visual-review');require(review['reviewed'] and review['reviewed_frames']==5 and review['native_sha256']==sha(WS/'inventory/client455-quake-effects-native.json') and review['script_sha256']==sha(WS/'scripts/review_client455_quake.py'),'Current viewed frames');check(review['sheet'])
    for row in review['frames']:check(row);check(row['preview'])
    maps=load('client455-map-data-native');require(maps['normal_link_sha256']==lh and maps['native']['checks']==2692 and maps['native']['geometry_cases']==330 and maps['canonical_equal'] and not maps['natural_exit'],'Fresh map regression')
    for row in [maps['source'],maps['exe'],maps['output'],maps['canonical_actual']]:check(row)
    early,ui,contracts=load('client455-startup-native'),load('client455-ui-startup-native'),load('client455-startup-contracts-native');require(contracts['build_sha256']==sha(WS/'inventory/client455-startup-engine-build.json') and early['normal_link_sha256']==ui['normal_link_sha256']==lh and not early['debugger_exit'] and early['sound_return']==1 and not ui['debugger_exit'] and ui['completed_existing_client_create'] and any(x['name']=='after_client_create' and x['eax']==1 for x in ui['markers']) and all(x['first_chance']==1 for x in ui['exceptions']),'Own PE startup/device/existingCreate1');check(early['events']);check(ui['events'])
    # Confirm actual retained ordinary PE calls from the changed map methods.
    mapping=(WS/link['map']['file']).read_text();image=(WS/link['executable']['file']).read_bytes();base=pe(image)['image_base'];names=re.findall(r'^\s+0001:[0-9a-fA-F]{8}\s+(\S+)\s+',mapping,re.M);starts=sorted({int(x,16) for x in re.findall(r'^\s+0001:[0-9a-fA-F]{8}\s+\S+\s+([0-9a-fA-F]{8})\b',mapping,re.M)});own=[]
    dumpbin=Path(load('msvc-verification')['compiler_path'].splitlines()[0]).with_name('dumpbin.exe')
    for prefix,target_prefix in [('?SetViewMatrix@CLevel@@','?R3GetQuakeVector@@'),('?LoadLevel@CLevel@@','?RF455_StopCameraSway@@')]:
        name=next(x for x in names if x.startswith(prefix));target=next(x for x in names if x.startswith(target_prefix));begin=symbol(mapping,name);end=min(x for x in starts if x>begin);dest=symbol(mapping,target);run=subprocess.run([str(dumpbin),'/DISASM:BYTES',f'/RANGE:0x{begin:x},0x{end:x}',str(WS/link['executable']['file'])],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW);require(not run.returncode,'Own map disassembly');output=WS/'artifacts/client455-progress'/('quake119-own-'+('view' if 'SetView' in prefix else 'load')+'.txt');output.write_bytes(run.stdout);calls=[]
        for line in run.stdout.decode(errors='replace').splitlines():
            m=re.match(r'^\s+([0-9A-F]{8}): ((?:[0-9A-F]{2} )+)\s+',line)
            if not m or int(m[1],16)>=end:continue
            at=int(m[1],16);raw=bytes.fromhex(m[2]);require(read_va(image,at,len(raw))==raw,'Own decoded instruction bytes')
            if raw[:1]==b'\xe8' and len(raw)==5 and at+5+struct.unpack('<i',raw[1:])[0]==dest:calls.append(hex(at-base))
        require(len(calls)==1,'Actual retained ordinary map call');own.append(dict(symbol=name,rva=hex(begin-base),bytes=end-begin,sha256=hashlib.sha256(read_va(image,begin,end-begin)).hexdigest(),target=target,target_rva=hex(dest-base),calls=calls,disassembly=record(output)))
    historical=WS/'artifacts/client455-progress/client455-texture-lifetime-checkpoint-before119.json';require(historical.exists(),'Exact118 historical gate')
    fresh=['quake-reference','quake-native','quake-effects-native','quake-visual-review','startup-engine-build','normal-preparation','normal-link','normal-consumers','own-entry','startup-audit','startup-native','startup-contracts-native','ui-startup-native','map-data-native']
    result=dict(status='PARTIAL',scope=ref['scope'],script_sha256=sha(Path(__file__)),normal_executable=link['executable'],normal_link_sha256=lh,engine=ref['engine'],old_engine=ref['old_engine'],native_cpu=cpu['verdict'],actual_effect=fx['verdict'],viewed_GPU_frames=5,own_retained_calls=own,map_checks=2692,map_geometry_cases=330,warning_count=20,previous118_gate=record(historical),old_runtime_gates='HISTORICAL;new actual registry/camera/map/startup only;older texture649/receivers/Character/bulk not rerun',fresh_evidence={x:record(WS/f'inventory/client455-{x}.json') for x in fresh},gaps=ref['gaps'],unchanged_bulk_suites_rerun=False,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-quake-checkpoint.json').write_text(json.dumps(result,indent=2)+'\n');print('PARTIAL:142CPU events/545actual impact frames/151quake frames/onset79/exact device view/5GPUviewed/maps2692/Create1;M9OPEN')

if __name__=='__main__':main()
