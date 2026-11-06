"""Run exact own normal PE in a private lab, stop before any graphics window."""
import hashlib,json,os,re,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link
from audit_client455_own_entry import validated_entry

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    link=json.loads((WS/'inventory/client455-normal-link.json').read_text());validate_normal_link(link);audit=json.loads((WS/'inventory/client455-startup-audit.json').read_text());info=json.loads((WS/'inventory/msvc-verification.json').read_text())
    if audit['normal_link_sha256']!=sha(WS/'inventory/client455-normal-link.json') or audit['unresolved_provider_modules']:raise ValueError('Current complete import-name audit required')
    source=WS/link['executable']['file'];raw=source.read_bytes();mapping=(WS/link['map']['file']).read_text();match=re.search(r'_WinMain@16\s+([0-9a-fA-F]{8})',mapping)
    if not match:raise ValueError('Own WinMain not present')
    entry=validated_entry();mainVa=int(match[1],16);base=pe(raw)['image_base'];stopVa=base+int(entry['points']['after_sound']['rva'],16)
    if mainVa-base!=int(entry['symbols']['main']['rva'],16):raise ValueError('Own WinMain differs from decoded audit')
    toolroot=WS/'work/tools/own-client-startup';toolroot.mkdir(parents=True,exist_ok=True);cpp=WS/'scripts/native/own_client_startup_debugger.cpp';debugger=toolroot/'own-startup-debugger.exe';batch=toolroot/'build.cmd';log=toolroot/'build.txt';dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    batch.write_text(f'@echo off\ncall "{dev}" -no_logo -arch=x86 -host_arch=x64 > "{toolroot/"environment.txt"}" 2>&1\nif errorlevel 1 exit /b 1\ncl /nologo /MT /O2 /EHsc /std:c++14 /W3 "{cpp}" /Fe"{debugger}" /Fo"{toolroot/"debugger.obj"}" /link /SUBSYSTEM:CONSOLE > "{log}" 2>&1\nexit /b %errorlevel%\n',encoding='ascii')
    result=subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=toolroot,creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:raise ValueError('Own debugger build:'+str(log))
    parent=WS/'work/m9'/sha(source)[:8];parent.mkdir(parents=True,exist_ok=True);index=1
    while (parent/f'startup{index:03d}').exists():index+=1
    run=parent/f'startup{index:03d}';run.mkdir();target=run/'RF_Online.bin';shutil.copyfile(source,target);inputs=[{'file':target.relative_to(WS).as_posix(),'sha256':sha(target),'kind':'own executable'}]
    for module in audit['modules']:
        original=Path(module['provider']['file']);copy=run/original.name
        if not module['delayed'] and original.parent==Path('C:/Windows/SysWOW64'):continue
        if sha(original)!=module['provider']['sha256']:raise ValueError('Changed delayed DLL')
        shutil.copyfile(original,copy);inputs.append({'file':copy.relative_to(WS).as_posix(),'sha256':sha(copy),'kind':'reference runtime DLL'})
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455'])
    for relative in ['Snd/WaveList.spt','mssmp3.asi']:
        original=client/relative;copy=run/relative
        if not original.is_file():raise ValueError('Required startup input missing:'+relative)
        copy.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original,copy);inputs.append({'file':copy.relative_to(WS).as_posix(),'sha256':sha(copy),'kind':'reference input'})
    config=run/'R3Engine.ini';config.write_text('[Setup]\nLanguage=Korea\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n[Sound]\nSound=FALSE\nMusic=FALSE\n',encoding='ascii');inputs.append({'file':config.relative_to(WS).as_posix(),'sha256':sha(config),'kind':'own lab config'})
    output=run/'debug-events.jsonl';command=[str(debugger),str(target),str(output),f'{mainVa-base:x}',f'{stopVa-base:x}']
    result=subprocess.run(command,cwd=run,capture_output=True,timeout=40,creationflags=subprocess.CREATE_NO_WINDOW);(run/'console.txt').write_bytes(result.stdout+result.stderr)
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
    point=entry['points']['after_sound'];report['own_entry_sha256']=sha(WS/'inventory/client455-own-entry.json')
    report['own_checkpoints']=[{'name':'WinMain','rva':hex(mainVa-base),'bytes':1,'sha256':hashlib.sha256(read_va(raw,mainVa,1)).hexdigest()},{'name':'after_sound_before_d3d','rva':hex(stopVa-base),'bytes':point['bytes'],'sha256':point['sha256']}]
    (WS/'inventory/client455-startup-native.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'summary':summary,'sound_return':sound,'exceptions':exceptions,'debugger_exit':result.returncode,'lab':run.relative_to(WS).as_posix(),'loaded_providers_match':all(p['matches_audited_provider'] for p in providers)}))
if __name__=='__main__':main()
