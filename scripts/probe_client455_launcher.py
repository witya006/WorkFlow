"""Exercise source launcher/real normal network setters offline,without authentication."""
import hashlib,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from client455_own_probe import build_full_object_probe
from client455_launcher_fixture import encoded_ccr,stage_launcher

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    source=WS/'scripts/native/client455_launcher_probe.cpp';exe=build_full_object_probe('launcher',source);parent=WS/'work/m9'/sha(exe)[:8];parent.mkdir(parents=True,exist_ok=True);runs=[]
    for nation,name in [(0,'Korea'),(7,'Russia'),(3,'Europe')]:
        index=1
        while (parent/f'launcher-{nation}-{index:03d}').exists():index+=1
        run=parent/f'launcher-{nation}-{index:03d}';run.mkdir();target=run/exe.name;shutil.copyfile(exe,target);inputs=[]
        for country in [0,1,2,4,5,6,8,9,10]:
            path=run/f'ccr-{country}.bin';path.write_bytes(encoded_ccr(country));inputs.append(path)
        raw=encoded_ccr(0);extra=run/'extra.bin';extra.write_bytes(raw+b'ignored-synthetic-tail');inputs.append(extra)
        for size in [0,1,4,6,56,57,60,61,76,77,78,79,82,83,86,87,90,91,92]:
            path=run/f'short-{size}.bin';path.write_bytes(raw[:size]);inputs.append(path)
        config=run/'R3Engine.ini';config.write_text('[Setup]\nLanguage='+name+'\n',encoding='ascii');inputs.append(config);fixture=stage_launcher(run,nation,WS)
        args=['127.0.0.1','1','fixture-user','fixture-value'] if nation in [3,7] else []
        result=subprocess.run([str(target),*args],cwd=run,capture_output=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW);(run/'console.txt').write_bytes(result.stdout+result.stderr);output=run/'result.json'
        if result.returncode:raise ValueError('Offline native launcher:'+str(result.returncode)+':'+str(run))
        runs.append({'nation':nation,'exit':result.returncode,'native':json.loads(output.read_text()),'exe':target.relative_to(WS).as_posix(),'exe_sha256':sha(target),'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'inputs':[{'file':p.relative_to(WS).as_posix(),'sha256':sha(p)} for p in inputs]+[fixture]})
    report={'scope':'Syntheticoffline CCR93/argument parser and real normal membernetwork setters;no clientnetwork creation/connect/authentication','architecture':'x86','entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'source':source.relative_to(WS).as_posix(),'source_sha256':sha(source),'script_sha256':sha(Path(__file__)),'builder_sha256':sha(WS/'scripts/client455_own_probe.py'),'fixture_generator_sha256':sha(WS/'scripts/client455_launcher_fixture.py'),'sources':{n:sha(WS/'scripts/native'/n) for n in ['client455_launcher.h','client455_launcher.cpp','client455_launcher_bridge.inc']},'map':exe.with_suffix('.map').relative_to(WS).as_posix(),'map_sha256':sha(exe.with_suffix('.map')),'normal_link_sha256':sha(WS/'inventory/client455-normal-link.json'),'reference_sha256':sha(WS/'inventory/client455-launcher-reference.json'),'runs':runs,'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-launcher-native.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps([{'nation':r['nation'],'exit':r['exit'],**r['native']} for r in runs]))
if __name__=='__main__':main()
