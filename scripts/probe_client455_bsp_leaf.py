"""Check actual CBsp world-to-local queries against independent finite examples."""
import json,shutil,subprocess,struct
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import require,sha
from client455_own_probe import build_full_object_probe
from compare_client_binaries import WS
from bsp_leaf455 import cases,encode,expected


def verify(run):
    spec=cases();rows=[json.loads(s) for s in (run/'leaf.jsonl').read_text().splitlines()];require(len(rows)==len(spec),'All finite cases')
    for i,(row,case) in enumerate(zip(rows,spec)):
        point,leaf=expected(case);bits=list(struct.unpack('<3I',struct.pack('<3f',*point)));require(row['id']==i and row['leaf']==leaf and row['local_bits']==bits,'Exact local coordinates/leaf:'+case['name'])
    return dict(cases=len(spec),local_scalar_bytes_exact=len(spec)*12,all_leaf_ids_exact=True,independent_owners=True,target_leaf_zero_fallback_preserved=True,affine_no_w_divide=True)


def main():
    source=WS/'scripts/native/client455_bsp_leaf_probe.cpp';exe=build_full_object_probe('bsp-leaf',source);holder=WS/'work/m9'/sha(exe)[:8];i=1
    while(holder/f'bsp-leaf-{i:03d}').exists():i+=1
    run=holder/f'bsp-leaf-{i:03d}';run.mkdir(parents=True);target=run/exe.name;shutil.copyfile(exe,target);shutil.copyfile(exe.with_suffix('.map'),target.with_suffix('.map'));fixture=run/'fixtures.bin';fixture.write_bytes(encode(cases()));r=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW);console=run/'console.txt';console.write_bytes(r.stdout+r.stderr);require(r.returncode==0,'Actual native leaf query:'+r.stderr.decode(errors='replace')[-500:]);verdict=verify(run)
    report=dict(status='PASS_SELECTED',scope='Actual own CBsp::GetLeafNum,owned inverse matrix and selected finite leaf topologies;fullBSP/renderer open',script_sha256=sha(Path(__file__)),source=record(source),included_source=record(WS/'scripts/native/client455_world_probe.cpp'),oracle=record(WS/'scripts/bsp_leaf455.py'),exe=record(target),map=record(target.with_suffix('.map')),fixture=record(fixture),trace=record(run/'leaf.jsonl'),console=record(console),normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),engine_report_sha256=sha(WS/'inventory/client455-startup-engine-build.json'),natural_exit=r.returncode,verdict=verdict,GPU_frames=0,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-bsp-leaf-native.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(run=str(run),verdict=verdict)))


if __name__=='__main__':main()
