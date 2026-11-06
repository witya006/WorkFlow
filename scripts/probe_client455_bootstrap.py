"""Full-object own probe:FG/instance/native network negative TCP and state contracts."""
import hashlib,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from client455_own_probe import build_full_object_probe

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    source=WS/'scripts/native/client455_bootstrap_probe.cpp';exe=build_full_object_probe('bootstrap',source);parent=WS/'work/m9'/sha(exe)[:8];parent.mkdir(parents=True,exist_ok=True);index=1
    while (parent/f'bootstrap-{index:03d}').exists():index+=1
    run=parent/f'bootstrap-{index:03d}';run.mkdir();target=run/'RF_Online.bin';shutil.copyfile(exe,target)
    data=run/'DataTable/ko-kr';data.mkdir(parents=True);asset=Path(json.loads((WS/'config/paths.json').read_text())['client_455'])/'DataTable/ko-kr/FG_CB.ini';shutil.copyfile(asset,data/'FG_CB.ini')
    config=run/'R3Engine.ini';config.write_text('[Setup]\nLanguage=Korea\n',encoding='ascii')
    wrong=run/'wrong-name.exe';shutil.copyfile(exe,wrong)
    for name,command in [('wrong-name',[str(wrong),'--wrong-name']),('bootstrap',[str(target)])]:
        result=subprocess.run(command,cwd=run,capture_output=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW);(run/(name+'.txt')).write_bytes(result.stdout+result.stderr)
        if result.returncode:raise ValueError(name+':'+str(result.returncode)+':'+str(run))
    native=run/'result.json';report={'scope':'FG/instance/corestate and actual clientnetworkCreate/rawTCP refused;not full455network orauthentication','architecture':'x86','entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'source':source.relative_to(WS).as_posix(),'source_sha256':sha(source),'script_sha256':sha(Path(__file__)),'builder_sha256':sha(WS/'scripts/client455_own_probe.py'),'sources':{n:sha(WS/'scripts/native'/n) for n in ['client455_bootstrap.h','client455_bootstrap.cpp','client455_bootstrap_bridge.inc','client455_network_state.h','client455_network_state.cpp','client455_network_bridge.inc','client455_network_transport.inc']},'normal_link_sha256':sha(WS/'inventory/client455-normal-link.json'),'reference_sha256':sha(WS/'inventory/client455-bootstrap-reference.json'),'native':json.loads(native.read_text()),'output':{'file':native.relative_to(WS).as_posix(),'sha256':sha(native)},'exe':{'file':target.relative_to(WS).as_posix(),'sha256':sha(target)},'map':{'file':exe.with_suffix('.map').relative_to(WS).as_posix(),'sha256':sha(exe.with_suffix('.map'))},'original_fg_sha256':sha(asset),'natural_exit':0,'wrong_filename_exit':0,'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-bootstrap-native.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['native']))
if __name__=='__main__':main()
