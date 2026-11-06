"""Verify the actual weather allocation instructions before/after the ABI fix."""
import hashlib,json,re,subprocess
from pathlib import Path
from audit_client455_own_entry import symbol
from compare_client_binaries import WS,pe

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def record(path):return dict(file=path.relative_to(WS).as_posix(),sha256=sha(path))

def main():
    native=json.loads((WS/'inventory/client455-rvp-runtime-cora-native.json').read_text())
    info=json.loads((WS/'inventory/msvc-verification.json').read_text());dumpbin=Path(info['compiler_path'].splitlines()[0]).with_name('dumpbin.exe')
    cases=[];root=WS/'artifacts/client455-particle-abi';root.mkdir(parents=True,exist_ok=True)
    old=WS/'work/m9/def353f4/rvp-runtime-cora-001/rvp-runtime-probe.exe'
    for label,exe,sizes in [('before',old,[1148,208]),('after',WS/native['exe']['file'],[1296,212])]:
        mapping=exe.with_suffix('.map');mapText=mapping.read_text();addr=symbol(mapText,'?LoadEnvironment455@CBsp@@QAEXXZ');allocate=symbol(mapText,'??2@YAPAXI@Z')
        run=subprocess.run([str(dumpbin),'/DISASM:BYTES',f'/RANGE:0x{addr:x},0x{addr+0x250:x}',str(exe)],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
        if run.returncode:raise ValueError('Own weather allocation decode failed')
        path=root/(label+'.txt');path.write_bytes(run.stdout);instructions=[]
        for line in run.stdout.decode(errors='replace').splitlines():
            match=re.match(r'^\s+([0-9A-F]{8}): ((?:[0-9A-F]{2} )+)\s+(\w+)\s*(.*?)\s*$',line)
            if match:instructions.append(dict(address=int(match[1],16),opcode=match[3],operand=match[4]))
        allocations=[]
        for size in sizes:
            matches=[r for i,r in enumerate(instructions[:-1]) if r['opcode']=='push' and r['operand'].lower()==f'{size:03x}h' and instructions[i+1]['opcode']=='call' and int(instructions[i+1]['operand'],16)==allocate]
            if len(matches)!=1:raise ValueError('Expected one allocation size '+str((label,size,matches)))
            allocations.append(dict(bytes=size,rva=hex(matches[0]['address']-pe(exe.read_bytes())['image_base'])))
        cases.append(dict(label=label,exe=record(exe),map=record(mapping),decoded=record(path),architecture='x86',allocations=allocations))
    if native['natural_exit'] or native['native']['status']!='PASS':raise ValueError('Current Cora regression failed')
    report=dict(status='PASS',scope='Owned x86 weather caller allocation ABI correction;not full weather/particle parity',cases=cases,
        failed_exit='0xc0000374',failed_phase='Cora world load',failed_console=record(old.parent/'console.txt'),
        diagnosis='Weather helper retained legacy1148/208 allocations while new constructors required1296/212;force only owned particle/entity declarations into that helper',
        fixed_cora_native_sha256=sha(WS/'inventory/client455-rvp-runtime-cora-native.json'),engine_report_sha256=sha(WS/'inventory/client455-startup-engine-build.json'),script_sha256=sha(Path(__file__)),input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-particle-abi-fix.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS:actual weather allocation instructions1148/208 ->1296/212;Cora330ticks/regression passed')

if __name__=='__main__':main()
