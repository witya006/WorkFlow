"""Actual client ConnectNetwork455 with a TCP-only acceptance fixture and real error UI."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from client455_own_probe import build_full_object_probe
from client455_tcp_fixture import TcpAcceptanceFixture
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--disconnect',action='store_true')
    args=parser.parse_args()
    source=WS/'scripts/native/client455_connection_probe.cpp';exe=build_full_object_probe('connection',source);parent=WS/'work/m9'/sha(exe)[:8];parent.mkdir(parents=True,exist_ok=True);client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);runs=[]
    scenarios=[('disconnect','ko-kr','Korea')] if args.disconnect else [('positive','ko-kr','Korea'),('timeout','ko-kr','Korea'),('russia','ru-ru','Russia')]
    for mode,folder,nation in scenarios:
        index=1
        while (parent/f'connection-{mode}-{index:03d}').exists():index+=1
        run=parent/f'connection-{mode}-{index:03d}';run.mkdir();target=run/exe.name;shutil.copyfile(exe,target);pack=run/f'DataTable/{folder}/NDLanguage.edf';pack.parent.mkdir(parents=True);shutil.copyfile(client/f'DataTable/{folder}/NDLanguage.edf',pack)
        (run/'mode.txt').write_text(mode,encoding='ascii');(run/'R3Engine.ini').write_text('[Setup]\nLanguage='+nation+'\n',encoding='ascii')
        with TcpAcceptanceFixture(mode=='positive') as transport:
            (run/'port.txt').write_text(str(transport.port),encoding='ascii');arguments=['127.0.0.1','1','fixture-user','fixture-value'] if mode=='russia' else []
            try:result=subprocess.run([str(target),*arguments],cwd=run,capture_output=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
            except subprocess.TimeoutExpired as error:
                (run/'console.txt').write_bytes((error.stdout or b'')+(error.stderr or b''));raise
            (run/'console.txt').write_bytes(result.stdout+result.stderr)
        if result.returncode:raise ValueError('Native connection:'+str(result.returncode)+':'+str(run))
        output=run/'result.json';runs.append({'mode':mode,'exit':result.returncode,'native':json.loads(output.read_text()),'tcp_fixture':transport.report(),'exe':{'file':target.relative_to(WS).as_posix(),'sha256':sha(target)},'output':{'file':output.relative_to(WS).as_posix(),'sha256':sha(output)},'language':{'file':pack.relative_to(WS).as_posix(),'sha256':sha(pack)}})
    report={'scope':'Real client wait/events/TCP and own-thread error dialogs;not authentication/login/gameplay','architecture':'x86','entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'source':source.relative_to(WS).as_posix(),'source_sha256':sha(source),'script_sha256':sha(Path(__file__)),'builder_sha256':sha(WS/'scripts/client455_own_probe.py'),'tcp_fixture_sha256':sha(WS/'scripts/client455_tcp_fixture.py'),'sources':{n:sha(WS/'scripts/native'/n) for n in ['client455_connection.h','client455_connection.cpp','client455_connection_bridge.inc','client455_network_receipt.inc']},'normal_link_sha256':sha(WS/'inventory/client455-normal-link.json'),'runs':runs,'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M9':'OPEN'}
    if args.disconnect:
        report['scope']='Loopback TCP close, ordered final frame delivery in the game loop, and transport reconnect.'
        for name in ('client455_network_events.inc','client455_network_receive.inc','client455_network_transport.inc'):
            report['sources'][name]=sha(WS/'scripts/native'/name)
    filename='client455-disconnect-native.json' if args.disconnect else 'client455-connection-native.json'
    (WS/'inventory'/filename).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps([r['native'] for r in runs]))
if __name__=='__main__':main()
