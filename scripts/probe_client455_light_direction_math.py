"""Build own light-direction source and verify finite PC/RC results independently."""
import json,subprocess
from collections import Counter
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import load,require,sha
from compare_client_binaries import WS
from lit_transform455 import value,bits,normal,direction


def verify(trace):
    rows=[json.loads(x) for x in trace.read_text().splitlines()];counts=Counter(x['kind'] for x in rows)
    require(counts==dict(normal=96,transform=96,guard=48),'Selected 240 CPU cases')
    require({((x['cw']>>8)&3,(x['cw']>>10)&3) for x in rows}=={(p,r) for p in [0,2,3] for r in range(4)},'12 PC/RC modes')
    for row in rows:
        if row['kind']=='guard':require(row['result']==0 and row['output_unchanged'],'Reject before any inverse output mutation');continue
        vector=list(map(value,row['input']))
        expected=normal(vector,row['cw']) if row['kind']=='normal' else direction(list(map(value,row['world'])),vector,row['cw'])
        if expected is None:require(row['output']==[0xffc00000]*3,'Zero vector remains x87 indefinite,without a fallback')
        else:require(row['output']==list(map(bits,expected)),'Exact selected rational direction '+str((row['kind'],row['id'],row['cw'],row['output'],list(map(bits,expected)))))
    return dict(cases=240,normal_vectors=96,affine_directions=96,rejected_affine_guards=48,FP_modes=12,finite_output_bits_exact=True,full_CRT=False,status_flag_equivalence=False)


def main():
    info=load('msvc-verification');math=load('client455-x87-math');root=WS/'work/client455-port/light-direction-math';root.mkdir(parents=True,exist_ok=True)
    source=WS/'scripts/native/client455_light_direction_probe.cpp';exe=root/'light-direction-math.exe';dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat';log=root/'build.txt';batch=root/'build.cmd'
    batch.write_text(f'@echo off\ncall "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1\nif errorlevel 1 exit /b 1\ncl /nologo /MT /O2 /Gy /EHsc /std:c++17 /W4 /I"{WS/"scripts/native"}" "{source}" "{WS/math["library"]}" /Fe"{exe}" /Fo"{root/"math.obj"}" /link /MAP:"{root/"math.map"}" > "{log}" 2>&1\nexit /b %errorlevel%\n',encoding='ascii')
    result=subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=root,creationflags=subprocess.CREATE_NO_WINDOW)
    require(not result.returncode,'Light math build '+str(log));trace=root/'trace.jsonl';result=subprocess.run([str(exe),str(trace)],cwd=root,capture_output=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
    console=root/'console.txt';console.write_bytes(result.stdout+result.stderr);require(not result.returncode,'Own CPU probe exit '+str(console));native=json.loads(result.stdout);verdict=verify(trace)
    out=dict(status='PASS_SELECTED',script=record(Path(__file__)),oracle=record(WS/'scripts/lit_transform455.py'),source=record(source),implementation=[record(WS/'scripts/native'/x) for x in ['client455_light_direction.h','client455_light_direction.inc']],
             exe=record(exe),object=record(root/'math.obj'),map=record(root/'math.map'),console=record(console),trace=record(trace),x87_library=record(WS/math['library']),native=native,verdict=verdict,input_exe_executed=False,server_modified=False)
    (WS/'inventory/client455-light-direction-math.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(verdict))


if __name__=='__main__':main()
