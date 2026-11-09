"""Capture actual own BSP light draw calls against target-derived boundaries."""
import json,shutil,subprocess
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import require,check,load,sha
from client455_own_probe import build_full_object_probe
from client455_runtime_inputs import copy_character_shaders
from compare_client_binaries import WS
from light_geometry455 import cases,encode,expected

def verify(run):
    spec=cases();rows=[json.loads(x) for x in (run/'geometry.jsonl').read_text().splitlines()];data=(run/'emitted.bin').read_bytes();require(len(rows)==len(spec),'All boundary cases');offset=0;result=[]
    for i,(row,case) in enumerate(zip(rows,spec)):
        raw,batches=expected(case);require(row['id']==i and row['offset']==offset and row['bytes']==len(raw) and row['batches']==batches and row['matrix_exact'] and row['declaration_exact'],'Actual call boundaries:'+case['name']);require(data[offset:offset+len(raw)]==raw,'Every emitted vertex byte:'+case['name']);offset+=len(raw);result.append(dict(name=case['name'],vertices=len(raw)//16,batches=batches))
    require(offset==len(data),'All emitted bytes accounted');return dict(cases=len(spec),emitted_bytes=len(data),case_results=result,every_vertex_byte_equal=True,owned_world_and_inverse_exact=True,actual_declaration_exact=True)

def main():
    source=WS/'scripts/native/client455_light_geometry_probe.cpp';exe=build_full_object_probe('light-geometry',source);holder=WS/'work/m9'/sha(exe)[:8];i=1
    while(holder/f'light-geometry-{i:03d}').exists():i+=1
    run=holder/f'light-geometry-{i:03d}';run.mkdir(parents=True);target=run/exe.name;shutil.copyfile(exe,target);shutil.copyfile(exe.with_suffix('.map'),target.with_suffix('.map'));inputs=copy_character_shaders(run);client=Path(json.loads((WS/'config/paths.json').read_text())['client_455'])
    for name in ['System/console.jpg']:
        dest=run/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(client/name,dest);inputs.append(record(dest))
    ini=run/'R3Engine.ini';ini.write_text('[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\n[Sound]\nSound=FALSE\nMusic=FALSE\n',encoding='ascii');inputs.append(record(ini));fixture=run/'fixtures.bin';fixture.write_bytes(encode(cases()));inputs.append(record(fixture))
    r=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW);(run/'console.txt').write_bytes(r.stdout+r.stderr);require(r.returncode==0,'Native geometry exit:'+str(r.returncode)+' '+r.stderr.decode(errors='replace')[-800:]);verdict=verify(run)
    for row in inputs:check(row)
    report=dict(status='PASS_SELECTED',scope='Actual own CBsp regular/magic geometry,owned matrix and explicit declaration;documented own-device API calls captured for finite synthetic fixtures,not execution of455',script_sha256=sha(Path(__file__)),source=record(source),included_source=record(WS/'scripts/native/client455_world_probe.cpp'),oracle=record(WS/'scripts/light_geometry455.py'),normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),engine_report_sha256=sha(WS/'inventory/client455-startup-engine-build.json'),exe=record(target),map=record(target.with_suffix('.map')),inputs=inputs,trace=record(run/'geometry.jsonl'),vertices=record(run/'emitted.bin'),console=record(run/'console.txt'),output=record(run/'result.json'),native=json.loads((run/'result.json').read_text()),natural_exit=r.returncode,verdict=verdict,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-light-geometry-native.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(run=str(run),cases=verdict['cases'],bytes=verdict['emitted_bytes'])))

if __name__=='__main__':main()
