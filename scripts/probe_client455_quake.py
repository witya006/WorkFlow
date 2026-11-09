"""Run own full-object quake entry and compare a small event sequence to455 oracle."""
import collections,json,shutil,subprocess,math
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import require,sha
from client455_own_probe import build_full_object_probe
from compare_client_binaries import WS,pe
from quake455 import Quake,decode

def verify(rows):
    q=Quake();comparisons=0;max_error=0.;exact=0
    def same(actual,expected,label,strict=False):
        nonlocal comparisons,max_error,exact
        comparisons+=1;error=abs(actual-expected);max_error=max(max_error,error);exact+=actual==expected
        require(math.isfinite(actual) and math.isfinite(expected) and (actual==expected if strict else error<=2e-5+abs(expected)*5e-7),label+f':{actual} vs{expected}')
    for index,row in enumerate(rows):
        expected=q.event(row);require(len(expected)==len(row['output']),'Output extent')
        for i,(a,b) in enumerate(zip(map(decode,row['output']),expected)):same(a,b,f'event{index} {row["op"]} output{i}')
        require((row['phase'],row['period'],row['enabled'])==(q.phase,q.period,q.enabled),'State branches/counters')
        for i,(a,b) in enumerate(zip(map(decode,row['state']),q.state())):same(a,b,f'event{index} state{i}',i in [0,1,2,6,7,8,9,10,11,12,13,14,15])
    counts=dict(collections.Counter(x['op'] for x in rows));require(counts['view']==8 and counts['density']==10 and counts['vector']>90,'Targeted coverage')
    return dict(events=len(rows),operations=counts,scalar_comparisons=comparisons,exact_scalars=exact,max_absolute_error=max_error,transcendental_absolute_tolerance=2e-5,transcendental_relative_tolerance=5e-7,integer_control_exact=True,nontranscendental_state_exact=True)

def main():
    source=WS/'scripts/native/client455_quake_probe.cpp';exe=build_full_object_probe('quake',source);root=WS/'work/m9'/sha(exe)[:8];i=1
    while(root/f'quake-{i:03d}').exists():i+=1
    run=root/f'quake-{i:03d}';run.mkdir(parents=True);target=run/exe.name;shutil.copyfile(exe,target);shutil.copyfile(exe.with_suffix('.map'),target.with_suffix('.map'))
    result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW);(run/'console.txt').write_bytes(result.stdout+result.stderr);require(result.returncode==0,'Quake native exit:'+str(result.returncode));trace=run/'trace.json';verdict=verify(json.loads(trace.read_text()))
    report=dict(status='PASS',scope='Selected455 quake/sway/attenuation and actual map CLevel view publication order;own native output vs static455 oracle,not execution of455',script_sha256=sha(Path(__file__)),oracle=record(WS/'scripts/quake455.py'),source=record(source),normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),engine_report_sha256=sha(WS/'inventory/client455-startup-engine-build.json'),exe=record(target),map=record(target.with_suffix('.map')),architecture=pe(target.read_bytes())['architecture'],trace=record(trace),console=record(run/'console.txt'),verdict=verdict,input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-quake-native.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(run=str(run),**verdict)))

if __name__=='__main__':main()
