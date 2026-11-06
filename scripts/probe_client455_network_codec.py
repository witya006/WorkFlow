"""Compare native source AES/packets with Windows CNG and actual normal network consumers."""
import hashlib,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from client455_own_probe import build_full_object_probe
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    source=WS/'scripts/native/client455_network_codec_probe.cpp';exe=build_full_object_probe('network-codec',source);parent=WS/'work/m9'/sha(exe)[:8];parent.mkdir(parents=True,exist_ok=True);index=1
    while (parent/f'network-codec-{index:03d}').exists():index+=1
    run=parent/f'network-codec-{index:03d}';run.mkdir();target=run/exe.name;shutil.copyfile(exe,target)
    result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW);(run/'console.txt').write_bytes(result.stdout+result.stderr)
    if result.returncode:raise ValueError('Native network codec:'+str(result.returncode)+':'+str(run))
    output=run/'result.json';report={'scope':'Source AES/framing and actual normal send/receive rings/configuration;not full455transport/handlers/authentication','source':source.relative_to(WS).as_posix(),'source_sha256':sha(source),'script_sha256':sha(Path(__file__)),'builder_sha256':sha(WS/'scripts/client455_own_probe.py'),'sources':{n:sha(WS/'scripts/native'/n) for n in ['client455_network_codec.h','client455_network_codec.cpp','client455_network_config.inc','client455_network_buffer.inc','client455_network_send.inc']},'reference_sha256':sha(WS/'inventory/client455-network-codec-reference.json'),'normal_link_sha256':sha(WS/'inventory/client455-normal-link.json'),'architecture':'x86','entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'exe':{'file':target.relative_to(WS).as_posix(),'sha256':sha(target)},'map':{'file':exe.with_suffix('.map').relative_to(WS).as_posix(),'sha256':sha(exe.with_suffix('.map'))},'output':{'file':output.relative_to(WS).as_posix(),'sha256':sha(output)},'native':json.loads(output.read_text()),'natural_exit':result.returncode,'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-network-codec-native.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['native']))
if __name__=='__main__':main()
