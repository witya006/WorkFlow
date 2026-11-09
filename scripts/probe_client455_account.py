"""Actual account send/ring/dispatch/UI methods on an owned in-memory fixture."""
import ctypes,hashlib,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from client455_own_probe import build_full_object_probe
from client455_asset_staging import stage_asset,staging_stats
from client455_runtime_inputs import copy_character_shaders

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    source=WS/'scripts/native/client455_account_probe.cpp';exe=build_full_object_probe('account',source);client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);parent=WS/'work/m9'/sha(exe)[:8];parent.mkdir(parents=True,exist_ok=True);index=1
    while (parent/f'account-{index:03d}').exists():index+=1
    run=parent/f'account-{index:03d}';run.mkdir();target=run/exe.name;shutil.copyfile(exe,target);inputs=[]
    for name in ['System/shader/Grass1.vsh','System/shader/grass1.vso','System/console.jpg','System/010.TTF','DataTable/ko-kr/NDLanguage.edf','SpriteImage/Common/mouse.spr','SpriteImage/ko-kr/common.spr']:
        original=client/name;copy=run/name;stage_asset(original,copy);inputs.append({'file':copy.relative_to(WS).as_posix(),'sha256':sha(copy)})
    inputs+=copy_character_shaders(run)
    config=run/'R3Engine.ini';config.write_text('[Setup]\nLanguage=Korea\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n',encoding='ascii');inputs.append({'file':config.relative_to(WS).as_posix(),'sha256':sha(config)})
    startup=subprocess.STARTUPINFO();startup.dwFlags=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
    try:result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=35,creationflags=subprocess.CREATE_NO_WINDOW,startupinfo=startup)
    finally:
        remove=ctypes.WinDLL('gdi32.dll').RemoveFontResourceW;remove.argtypes=[ctypes.c_wchar_p];remove.restype=ctypes.c_int;remove(str(run/'System/010.TTF'))
    (run/'console.txt').write_bytes(result.stdout+result.stderr)
    if result.returncode:raise ValueError('Actual account455 runtime:'+str(result.returncode)+':'+str(run))
    output=run/'result.json';report={'scope':'Actual ordinary account methods,send/receive rings,decoded dispatcher and pending dialog on own in-memory fixture;not authentication','architecture':'x86','entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'source':source.relative_to(WS).as_posix(),'source_sha256':sha(source),'script_sha256':sha(Path(__file__)),'builder_sha256':sha(WS/'scripts/client455_own_probe.py'),'sources':{name:sha(WS/'scripts/native'/name) for name in ['client455_account.h','client455_account.cpp','client455_account_bridge.inc','client455_account_dispatch.inc']},'exe':{'file':target.relative_to(WS).as_posix(),'sha256':sha(target)},'map':{'file':exe.with_suffix('.map').relative_to(WS).as_posix(),'sha256':sha(exe.with_suffix('.map'))},'inputs':inputs,'output':{'file':output.relative_to(WS).as_posix(),'sha256':sha(output)},'native':json.loads(output.read_text()),'reference_sha256':sha(WS/'inventory/client455-account-reference.json'),'normal_link_sha256':sha(WS/'inventory/client455-normal-link.json'),'natural_exit':result.returncode,'authentication_performed':False,'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M9':'OPEN'}
    report['world_entry_sources']={name:sha(WS/'scripts/native'/name) for name in ['client455_world_entry.h','client455_world_entry.inc','client455_world_entry_probe.inc']}
    report['registered_character_sources']={name:sha(WS/'scripts/native'/name) for name in ['client455_registered_characters.h','client455_registered_characters.inc','client455_registered_characters_probe.inc']}
    registered_result=run/'registered-characters-result.json';report['registered_character_output']={'file':registered_result.relative_to(WS).as_posix(),'sha256':sha(registered_result)};report['registered_character_native']=json.loads(registered_result.read_text())
    report['world_entry_reference_sha256']=sha(WS/'inventory/client455-world-entry-reference.json')
    world_result=run/'world-entry-result.json';report['world_entry_output']={'file':world_result.relative_to(WS).as_posix(),'sha256':sha(world_result)};report['world_entry_native']=json.loads(world_result.read_text())
    report['shared_asset_staging']=staging_stats();report['asset_staging_script_sha256']=sha(WS/'scripts/client455_asset_staging.py')
    report['scope']+=';58-byte world entry request and bounded12-byte reply via real encrypted/ring dispatcher;not auth/bootstrap/selection acceptance'
    (WS/'inventory/client455-account-native.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report['native']))
if __name__=='__main__':main()
