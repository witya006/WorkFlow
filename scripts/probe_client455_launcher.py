"""Exercise source launcher/real normal network setters offline,without authentication."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from client455_own_probe import build_full_object_probe
from client455_launcher_fixture import encoded_ccr,stage_launcher

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--regional',action='store_true');args=parser.parse_args()
    source=WS/'scripts/native/client455_launcher_probe.cpp';exe=build_full_object_probe('launcher',source);parent=WS/'work/m9'/sha(exe)[:8];parent.mkdir(parents=True,exist_ok=True);runs=[]
    cases=[(0,'Korea','ccr'), (7,'Russia','argv'), (3,'Europe','argv')]
    if args.regional:cases += [
        (8,'Taiwan','ccr'),
        (7,'Russia','ccr'), (3,'Europe','ccr'), (7,'Russia','missing'),
        (7,'Russia','truncated'), (7,'Russia','wrong-nation'), (7,'Russia','bad-args'),
    ]
    for nation,name,mode in cases:
        index=1
        while (parent/f'launcher-{nation}-{index:03d}').exists():index+=1
        run=parent/f'launcher-{nation}-{index:03d}';run.mkdir();target=run/exe.name;shutil.copyfile(exe,target);inputs=[]
        for country in [0,1,2,4,5,6,8,9,10]:
            path=run/f'ccr-{country}.bin';path.write_bytes(encoded_ccr(country));inputs.append(path)
        raw=encoded_ccr(0);extra=run/'extra.bin';extra.write_bytes(raw+b'ignored-synthetic-tail');inputs.append(extra)
        for size in [0,1,4,6,56,57,60,61,76,77,78,79,82,83,86,87,90,91,92]:
            path=run/f'short-{size}.bin';path.write_bytes(raw[:size]);inputs.append(path)
        if args.regional and runs:inputs=[] # The parser fixtures are identical for all runs.
        config=run/'R3Engine.ini';config.write_text('[Setup]\nLanguage='+name+'\n',encoding='ascii');inputs.append(config)
        if not args.regional:
            fixture=stage_launcher(run,nation,WS);inputs.append(WS/fixture['file'])
        elif mode!='missing':
            handoff=run/'System/DefaultSet.tmp';handoff.parent.mkdir()
            raw=encoded_ccr(8 if mode=='wrong-nation' else nation)
            handoff.write_bytes(raw[:92] if mode=='truncated' else raw);inputs.append(handoff)
        if mode not in ['argv','ccr']:
            reject=run/'reject-handoff';reject.touch();inputs.append(reject)
        arguments=['127.0.0.1','1','fixture-user','fixture-value'] if mode=='argv' else ['unexpected'] if mode=='bad-args' else []
        result=subprocess.run([str(target),*arguments],cwd=run,capture_output=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW);(run/'console.txt').write_bytes(result.stdout+result.stderr);output=run/'result.json'
        if result.returncode:raise ValueError('Offline native launcher:'+str(result.returncode)+':'+str(run))
        runs.append({'nation':nation,'mode':mode,'exit':result.returncode,'native':json.loads(output.read_text()),'exe':target.relative_to(WS).as_posix(),'exe_sha256':sha(target),'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'inputs':[{'file':p.relative_to(WS).as_posix(),'sha256':sha(p)} for p in inputs]})
    report={'scope':'Syntheticoffline CCR93/argument parser and real normal membernetwork setters;no clientnetwork creation/connect/authentication','architecture':'x86','entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'source':source.relative_to(WS).as_posix(),'source_sha256':sha(source),'script_sha256':sha(Path(__file__)),'builder_sha256':sha(WS/'scripts/client455_own_probe.py'),'fixture_generator_sha256':sha(WS/'scripts/client455_launcher_fixture.py'),'sources':{n:sha(WS/'scripts/native'/n) for n in ['client455_launcher.h','client455_launcher.cpp','client455_launcher_bridge.inc']},'map':exe.with_suffix('.map').relative_to(WS).as_posix(),'map_sha256':sha(exe.with_suffix('.map')),'normal_link_sha256':sha(WS/'inventory/client455-normal-link.json'),'reference_sha256':sha(WS/'inventory/client455-launcher-reference.json'),'runs':runs,'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M9':'OPEN'}
    filename='client455-launcher-regional-native.json' if args.regional else 'client455-launcher-native.json'
    (WS/'inventory'/filename).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps([{'nation':r['nation'],'mode':r['mode'],'exit':r['exit'],**r['native']} for r in runs]))
if __name__=='__main__':main()
