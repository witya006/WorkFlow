"""Real archived impact scheduler -> quake -> map view -> actual D3D device."""
import json,math,struct
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,require,sha
from compare_client_binaries import WS
from probe_client455_nuclear_registry import main as registry
from quake455 import Quake,decode,f

def verify(trace):
    q=Quake();q.sd=f(.4);q.sp=f(.3);q.heading=(decode(trace['base'][10]),decode(trace['base'][8]));camera=list(map(decode,trace['camera']));point=list(map(decode,trace['impact']));x,y,z=[f(a-b) for a,b in zip(point,camera)]
    length=f(math.sqrt(f(y*y+x*x+z*z)));density=f(f(1-f(max(0.,length-200))/600)*150);starts=[];compared=0;exact=0;max_error=0
    def match(actual,expected,label):
        nonlocal compared,exact,max_error
        compared+=1;exact+=actual==expected;error=abs(actual-expected);max_error=max(max_error,error);require(math.isfinite(actual) and error<=2e-5+abs(expected)*5e-7,label+f':{actual} vs{expected}')
    for row in trace['rows']:
        dt=decode(row['dt']);before=row['before'];bv=list(map(decode,before['values']))
        if bv[1]>q.remaining:
            starts.append(row['frame']);require(bv[0]==bv[1]==5 and bv[2]==density,'Actual track duration/attenuated density');q.start([5.,density],dt)
        for state in [before]:
            require((state['phase'],state['period'],state['enabled'])==(q.phase,q.period,q.enabled),'Scheduler pre-camera counters')
            for a,b in zip(map(decode,state['values']),q.state()):match(a,b,'Scheduler pre-camera state')
        expected=q.event(dict(op='view',input=trace['base'],dt=row['dt'],toggle=row['toggle']))[:16]
        after=row['after'];require((after['phase'],after['period'],after['enabled'])==(q.phase,q.period,q.enabled),'Post-camera counters')
        for a,b in zip(map(decode,after['values']),q.state()):match(a,b,'Post-camera state')
        for a,b in zip(map(decode,row['view']),expected):match(a,b,'Actual published device view')
    require(len(starts)==1 and starts[0] in [78,79] and trace['frames']>300 and trace['active_frames']>=150 and trace['moved_frames']>=149 and trace['load_stopped_sway'] and q.remaining==0,'Actual onset/decay/load lifecycle')
    # Pin the observed crossing rather than accepting a broad time window silently.
    require(starts==[79],'Strict upper track interval at float32 frame78 starts on frame79')
    return dict(frames=trace['frames'],quake_onset_frames=starts,duration=5,attenuated_density=density,active_frames=trace['active_frames'],moved_frames=trace['moved_frames'],scalar_comparisons=compared,exact_scalars=exact,max_absolute_error=max_error,device_view_exact=True,successful_map_load_stops_sway=True)

def main():
    report=registry('client455_quake_effect_probe.cpp','quake-effects','client455-quake-effects-native');run=(WS/report['exe']['file']).parent;trace=run/'quake-effects.json';verdict=verify(json.loads(trace.read_text()));report.update(status='PASS',scope='Own full-object actual registry/real archived impact -> quake -> actual CLevel map -> D3D view and 5 effect frames;full world composition/gameplay remains open',trace=record(trace),verdict=verdict,oracle=record(WS/'scripts/quake455.py'),registry_template=record(WS/'scripts/native/client455_nuclear_registry_probe.cpp'),trace_header=record(WS/'scripts/native/client455_quake_trace.h'),driver_script=record(Path(__file__)))
    (WS/'inventory/client455-quake-effects-native.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(verdict))

if __name__=='__main__':main()
