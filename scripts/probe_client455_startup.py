"""Run exact own normal PE in a private lab, stop before any graphics window."""
import argparse,contextlib,hashlib,json,os,re,shutil,subprocess
from pathlib import Path
from client455_asset_staging import stage_asset,staging_stats
from compare_client_binaries import WS,pe
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link
from audit_client455_own_entry import validated_entry
from client455_launcher_fixture import stage_launcher
from client455_tcp_fixture import TcpAcceptanceFixture

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--nation',default='Korea');parser.add_argument('--live-port',type=int);args=parser.parse_args()
    if args.live_port is not None and not 1<=args.live_port<=65535:raise ValueError('Invalid local live port')
    countries=json.loads((WS/'inventory/client455-nation-paths-reference.json').read_text())['references'][0]['rows'];country=next((row for row in countries if row['setting']==args.nation),None)
    if country is None:raise ValueError('Unknown exact country setting:'+args.nation)
    link=json.loads((WS/'inventory/client455-normal-link.json').read_text());validate_normal_link(link);audit=json.loads((WS/'inventory/client455-startup-audit.json').read_text());info=json.loads((WS/'inventory/msvc-verification.json').read_text())
    if audit['normal_link_sha256']!=sha(WS/'inventory/client455-normal-link.json') or audit['unresolved_provider_modules']:raise ValueError('Current complete import-name audit required')
    source=WS/link['executable']['file'];raw=source.read_bytes();mapping=(WS/link['map']['file']).read_text();match=re.search(r'_WinMain@16\s+([0-9a-fA-F]{8})',mapping)
    if not match:raise ValueError('Own WinMain not present')
    entry=validated_entry();mainVa=int(match[1],16);base=pe(raw)['image_base'];beforeConnect=country['id'] in [3,7];pointName='before_connect' if beforeConnect else 'after_sound';stopVa=base+int(entry['points'][pointName]['rva'],16)
    if args.live_port is not None and beforeConnect:raise ValueError('This profile stops before Connect')
    if mainVa-base!=int(entry['symbols']['main']['rva'],16):raise ValueError('Own WinMain differs from decoded audit')
    toolroot=WS/'work/tools/own-client-startup';toolroot.mkdir(parents=True,exist_ok=True);cpp=WS/'scripts/native/own_client_startup_debugger.cpp';debugger=toolroot/'own-startup-debugger.exe';batch=toolroot/'build.cmd';log=toolroot/'build.txt';dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    batch.write_text(f'@echo off\ncall "{dev}" -no_logo -arch=x86 -host_arch=x64 > "{toolroot/"environment.txt"}" 2>&1\nif errorlevel 1 exit /b 1\ncl /nologo /MT /O2 /EHsc /std:c++14 /W3 "{cpp}" /Fe"{debugger}" /Fo"{toolroot/"debugger.obj"}" /link /SUBSYSTEM:CONSOLE > "{log}" 2>&1\nexit /b %errorlevel%\n',encoding='ascii')
    source_hash = sha(cpp)
    current_hash = sha(debugger) if debugger.is_file() else None
    reports = (WS/'inventory').glob('client455-startup*-native.json')
    reusable = any(cached.get('file') == debugger.relative_to(WS).as_posix()
                   and cached.get('source_sha256') == source_hash and cached.get('sha256') == current_hash
                   for report in reports if (cached := json.loads(report.read_text()).get('debugger')))
    if not reusable:
        result=subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=toolroot,creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode:raise ValueError('Own debugger build:'+str(log))
    parent=WS/'work/m9'/sha(source)[:8];parent.mkdir(parents=True,exist_ok=True);index=1
    prefix='startup' if args.nation=='Korea' else 'startup-'+args.nation.lower()
    if args.live_port is not None:prefix='startup-live-'+args.nation.lower()
    while (parent/f'{prefix}{index:03d}').exists():index+=1
    run=parent/f'{prefix}{index:03d}';run.mkdir();target=run/'RF_Online.bin';shutil.copyfile(source,target);inputs=[{'file':target.relative_to(WS).as_posix(),'sha256':sha(target),'kind':'own executable'}]
    for module in audit['modules']:
        original=Path(module['provider']['file']);copy=run/original.name
        if not module['delayed'] and original.parent==Path('C:/Windows/SysWOW64'):continue
        if sha(original)!=module['provider']['sha256']:raise ValueError('Changed delayed DLL')
        stage_asset(original,copy,module['provider']['sha256']);inputs.append({'file':copy.relative_to(WS).as_posix(),'sha256':sha(copy),'kind':'reference runtime DLL'})
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455'])
    for relative in ['Snd/WaveList.spt','mssmp3.asi','System/010.TTF',f'DataTable/{country["folder"]}/NDLanguage.edf']:
        original=client/relative;copy=run/relative
        if not original.is_file():raise ValueError('Required startup input missing:'+relative)
        copy.parent.mkdir(parents=True,exist_ok=True);stage_asset(original,copy);inputs.append({'file':copy.relative_to(WS).as_posix(),'sha256':sha(copy),'kind':'reference input'})
    config=run/'R3Engine.ini';config.write_text(f'[Setup]\nLanguage={args.nation}\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n[Sound]\nSound=FALSE\nMusic=FALSE\n',encoding='ascii');inputs.append({'file':config.relative_to(WS).as_posix(),'sha256':sha(config),'kind':'own lab config'})
    connectionConfig=run/'DataTable/ClientSystem.ini';connectionConfig.parent.mkdir(parents=True,exist_ok=True);connectionConfig.write_text('[Network]\nConnectTime=5\n',encoding='ascii');inputs.append({'file':connectionConfig.relative_to(WS).as_posix(),'sha256':sha(connectionConfig),'kind':'own transport timeout'})
    if beforeConnect:
        label=run/'checkpoint-label.txt';label.write_text('before_client_connect',encoding='ascii');inputs.append({'file':label.relative_to(WS).as_posix(),'sha256':sha(label),'kind':'owned decoded checkpoint label'})
    output=run/'debug-events.jsonl';command=[str(debugger),str(target),str(output),f'{mainVa-base:x}',f'{stopVa-base:x}']
    with (contextlib.nullcontext(None) if args.live_port is not None else TcpAcceptanceFixture(not beforeConnect)) as transport:
        inputs.append(stage_launcher(run,country['id'],WS,args.live_port if args.live_port is not None else transport.port))
        result=subprocess.run(command,cwd=run,capture_output=True,timeout=40,creationflags=subprocess.CREATE_NO_WINDOW)
    (run/'console.txt').write_bytes(result.stdout+result.stderr)
    events=[json.loads(line) for line in output.read_text(encoding='utf-8').splitlines()] if output.exists() else [];summary=next((e for e in events if e['kind']=='summary'),{});markers=[e for e in events if e['kind']=='checkpoint'];exceptions=[e for e in events if e['kind']=='exception'];sound=next((e['eax'] for e in markers if e['name']=='after_sound_before_d3d'),None)
    modules=[e for e in events if e['kind']=='module'];providers=[]
    for module in audit['modules']:
        for actual in modules:
            path=Path(actual['path'])
            if path.name.lower()!=module['dll']:continue
            providers.append({'dll':module['dll'],'file':str(path),'sha256':sha(path),'expected_sha256':module['provider']['sha256'],'matches_audited_provider':sha(path)==module['provider']['sha256']});break
    report={'scope':'Exact own normal PE CRT/WinMain/engine/sound startup;debugger stops before D3D/window/network;not full normal initialization or455acceptance','executable':link['executable'],'staged_executable':str(target.relative_to(WS)),'normal_link_sha256':sha(WS/'inventory/client455-normal-link.json'),'audit_sha256':sha(WS/'inventory/client455-startup-audit.json'),'debugger':{'file':debugger.relative_to(WS).as_posix(),'sha256':sha(debugger),'source':cpp.relative_to(WS).as_posix(),'source_sha256':sha(cpp)},'lab_inputs':inputs,'events':{'file':output.relative_to(WS).as_posix(),'sha256':sha(output) if output.exists() else None},'debugger_exit':result.returncode,'summary':summary,'markers':markers,'sound_return':sound,'exceptions':exceptions,'loaded_modules':[e for e in events if e['kind']=='module'],'normal_winmain_executed':summary.get('main_reached',False),'input_exe_executed':False,'graphics_window_created':False,'network_stage_reached':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    report['loaded_provider_checks']=providers;report['loaded_module_count']=len(modules)
    report['loaded_modules']=[m for m in modules if Path(m['path']).name.lower() in [p.name.lower() for p in [target,run/'mss32.dll',run/'mssmp3.asi']]]
    point=entry['points'][pointName];report['own_entry_sha256']=sha(WS/'inventory/client455-own-entry.json');report['tcp_fixture']=transport.report() if transport is not None else {'enabled':False};report['before_connect']=beforeConnect;report['network_stage_reached']=any(e.get('value','').startswith('RF455 Network:Create:') for e in events);report['connection_attempted']=not beforeConnect;report['transport_connected']='RF455 Connect:connected' in [e.get('value') for e in events];report['tcp_fixture_sha256']=sha(WS/'scripts/client455_tcp_fixture.py');report['script_sha256']=sha(Path(__file__))
    if args.live_port is not None:
        report['live_server']={'host':'127.0.0.1','port':args.live_port,'authentication_performed':False,'synthetic_launcher_metadata':True,'server_files_modified':False,'full_RF_protocol_verified':False}
        report['scope']='Exact own WinMain connects to the user-started local GoMMO server then engine/Miles;stopped before D3D;not authentication orfullRFprotocol acceptance'
    if args.live_port is None:report['scope']='Exact own WinMain with genuine initialTCP then engine/Miles;stopped before D3D/window;not authentication/fullnetwork or455acceptance'
    report['shared_asset_staging']=staging_stats();report['asset_staging_script_sha256']=sha(WS/'scripts/client455_asset_staging.py')
    if beforeConnect:report['scope']='Exact own WinMain nation/launcher/language/FG/networkCreate/instance;stopped at decoded call before Connect;not sound or successful connection acceptance'
    report['own_checkpoints']=[{'name':'WinMain','rva':hex(mainVa-base),'bytes':1,'sha256':hashlib.sha256(read_va(raw,mainVa,1)).hexdigest()},{'name':'before_client_connect' if beforeConnect else 'after_sound_before_d3d','rva':hex(stopVa-base),'bytes':point['bytes'],'sha256':point['sha256']}]
    report['nation']=args.nation;report['language_debug']=[e for e in events if e['kind']=='debug_string' and (e['value'].startswith('.\\DataTable\\') or e['value'].startswith('RF455 NDLanguage:'))]
    name='client455-startup-native' if args.nation=='Korea' else f'client455-startup-{args.nation.lower()}-native'
    if args.live_port is not None:name=f'client455-startup-live-{args.nation.lower()}-native'
    (WS/f'inventory/{name}.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'summary':summary,'sound_return':sound,'language_debug':report['language_debug'],'debugger_exit':result.returncode,'lab':run.relative_to(WS).as_posix(),'loaded_providers_match':all(p['matches_audited_provider'] for p in providers)}))
    if args.live_port is not None and (not report['transport_connected'] or not summary.get('after_sound_reached')):raise SystemExit(1)
if __name__=='__main__':main()
