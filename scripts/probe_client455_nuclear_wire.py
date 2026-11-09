"""Build/test the confirmed nine-layout decoder; no ordinary receiver acceptance."""
import json,shutil,subprocess
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS,pe


def main():
    ref=load('client455-nuclear-protocol-reference');check(ref['raw']);check(ref['session'])
    sources=[WS/'scripts/native'/name for name in ['client455_nuclear_wire.h','client455_nuclear_wire.cpp','test_client455_nuclear_wire.cpp']]
    root=WS/'work/recovered/client455/nuclear-wire';root.mkdir(parents=True,exist_ok=True);info=load('msvc-verification');dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat';obj=root/'wire.obj';lib=root/'RF455NuclearWire.lib';exe=root/'nuclear-wire-probe.exe';log=root/'build.txt'
    flags='/nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /WX /I"'+str(WS/'scripts/native')+'"'
    command=root/'build.cmd';command.write_text('@echo off\ncall "'+str(dev)+'" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1\nif errorlevel 1 exit /b 1\ncl /c '+flags+' "'+str(sources[1])+'" /Fo"'+str(obj)+'" > "'+str(log)+'" 2>&1\nif errorlevel 1 exit /b 1\nlib /nologo /OUT:"'+str(lib)+'" "'+str(obj)+'" >> "'+str(log)+'" 2>&1\nif errorlevel 1 exit /b 1\ncl '+flags+' "'+str(sources[2])+'" "'+str(lib)+'" /Fo"'+str(root/'test.obj')+'" /Fe"'+str(exe)+'" >> "'+str(log)+'" 2>&1\nexit /b %errorlevel%\n',encoding='ascii')
    result=subprocess.run(['cmd.exe','/d','/c',str(command)],cwd=root,creationflags=subprocess.CREATE_NO_WINDOW);require(not result.returncode,'Wire build:'+str(log));require(obj.read_bytes()[:2]==b'\x4c\x01' and lib.read_bytes().startswith(b'!<arch>\n') and pe(exe.read_bytes())['architecture']=='x86','Own x86 build')
    holder=WS/'work/m9'/sha(exe)[:8];n=1
    while(holder/f'nuclear-wire-{n:03d}').exists():n+=1
    run=holder/f'nuclear-wire-{n:03d}';run.mkdir(parents=True);target=run/exe.name;shutil.copyfile(exe,target);result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW);console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);out=run/'result.json';actual=json.loads(out.read_text()) if out.exists() else None
    require(not result.returncode and actual and actual['status']=='PASS','Wire native output:'+str(console))
    report=dict(status='PASS_SELECTED_DECODER',scope='Bounded source decoder for nine native-confirmed group60 layouts; receiver/guard/UI/owner integration not accepted',script_sha256=sha(Path(__file__)),reference_sha256=sha(WS/'inventory/client455-nuclear-protocol-reference.json'),sources=[record(path) for path in sources],object=record(obj),library=record(lib),build_log=record(log),exe=record(target),output=record(out),console=record(console),natural_exit=result.returncode,native=actual,normal_receiver_integrated=False,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-nuclear-wire-native.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(run=str(run),native=actual)))


if __name__=='__main__':main()
