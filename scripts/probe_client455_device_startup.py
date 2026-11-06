"""Run exact own PE through real window/device init;stop before client Create."""
import argparse,ctypes,hashlib,json,re,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link
from audit_client455_own_entry import validated_entry

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def symbol(mapping,name):
    match=re.search(re.escape(name)+r'\s+([0-9a-fA-F]{8})',mapping)
    if not match:raise ValueError('Missing own symbol:'+name)
    return int(match[1],16)
def main():
    parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group();group.add_argument('--create',action='store_true');group.add_argument('--before-launcher',action='store_true');args=parser.parse_args();partialCreate=args.create or args.before_launcher
    link=json.loads((WS/'inventory/client455-normal-link.json').read_text());validate_normal_link(link);early=json.loads((WS/'inventory/client455-startup-native.json').read_text());contracts=json.loads((WS/'inventory/client455-startup-contracts-native.json').read_text());engine=json.loads((WS/'inventory/client455-startup-engine-build.json').read_text())
    if early['normal_link_sha256']!=sha(WS/'inventory/client455-normal-link.json') or contracts['build_sha256']!=sha(WS/'inventory/client455-startup-engine-build.json'):raise ValueError('Current early startup/contracts evidence required')
    entry=validated_entry();source=WS/link['executable']['file'];raw=source.read_bytes();base=pe(raw)['image_base'];mapping=(WS/link['map']['file']).read_text();mainVa=symbol(mapping,'_WinMain@16');stopVa=base+int(entry['points']['before_launcher' if args.before_launcher else 'before_char_data' if args.create else 'after_d3d']['rva'],16)
    parent=WS/'work/m9'/sha(source)[:8];parent.mkdir(parents=True,exist_ok=True);index=1
    prefix='ui-startup' if args.before_launcher else 'create-startup' if args.create else 'device-startup'
    while (parent/f'{prefix}{index:03d}').exists():index+=1
    run=parent/f'{prefix}{index:03d}';run.mkdir();oldRoot=(WS/early['staged_executable']).parent;inputs=[]
    for item in early['lab_inputs']:
        original=WS/item['file'];relative=original.relative_to(oldRoot);copy=run/relative
        if sha(original)!=item['sha256']:raise ValueError('Changed private startup input')
        copy.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original,copy);inputs.append({'file':copy.relative_to(WS).as_posix(),'sha256':sha(copy)})
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455'])
    for name in ['System/shader/Grass1.vsh','System/shader/grass1.vso','System/console.jpg']:
        original=client/name;copy=run/name
        if not original.is_file():raise ValueError('Missing actual startup resource:'+name)
        copy.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original,copy);inputs.append({'file':copy.relative_to(WS).as_posix(),'sha256':sha(copy)})
    if args.before_launcher:
        for name in ['SpriteImage/Common/mouse.spr','SpriteImage/ko-kr/common.spr']:
            original=client/name;copy=run/name;copy.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original,copy);inputs.append({'file':copy.relative_to(WS).as_posix(),'sha256':sha(copy)})
    if partialCreate:
        shaders=json.loads((WS/'inventory/client455-shaders-reference.json').read_text())
        for row in shaders['programs']:
            original=WS/row['copy'];copy=run/'System/shader'/(row['name']+'.sho')
            if sha(original)!=row['sha256']:raise ValueError('Changed actual Character shader')
            shutil.copyfile(original,copy);inputs.append({'file':copy.relative_to(WS).as_posix(),'sha256':sha(copy)})
    layout=contracts['layout'];state=symbol(mapping,'?stState@@3U_R3ENGINE_STATE@@A')-base;app=symbol(mapping,'?g_MainApp@@3VCMainApp@@A')-base
    values=[state+layout['state_fullscreen'],state+layout['state_renderbits'],app,layout['ready'],layout['window'],layout['device'],layout['windowed'],int(entry['points']['after_sound']['rva'],16),int(entry['points']['after_d3d']['rva'],16),symbol(mapping,'?g_ifCharIF@@3PAVChInterface@@A')-base,layout['character_device']]
    plan=run/'device.plan';plan.write_text(' '.join(f'{value:x}' for value in values)+'\n',encoding='ascii');inputs.append({'file':plan.relative_to(WS).as_posix(),'sha256':sha(plan)})
    debugger=WS/early['debugger']['file']
    if sha(debugger)!=early['debugger']['sha256']:raise ValueError('Changed own debugger')
    output=run/'debug-events.jsonl';command=[str(debugger),str(run/'RF_Online.bin'),str(output),f'{mainVa-base:x}',f'{stopVa-base:x}',str(plan)]+(['before_launcher'] if args.before_launcher else [])
    try:
        result=subprocess.run(command,cwd=run,capture_output=True,timeout=40,creationflags=subprocess.CREATE_NO_WINDOW)
    finally:
        removeFont=ctypes.WinDLL('gdi32.dll').RemoveFontResourceW;removeFont.argtypes=[ctypes.c_wchar_p];removeFont.restype=ctypes.c_int
        fontRegistrationRemoved=bool(removeFont(str(run/'System/010.TTF')))
    (run/'console.txt').write_bytes(result.stdout+result.stderr)
    events=[json.loads(line) for line in output.read_text().splitlines()] if output.exists() else [];summary=next((e for e in events if e['kind']=='summary'),{});config=next((e for e in events if e['kind']=='render_configuration'),{});device=next((e for e in events if e['kind']=='device_state'),{});markers=[e for e in events if e['kind']=='checkpoint'];exceptions=[e for e in events if e['kind']=='exception']
    report={'scope':'Exact own normal PE windowed D3D/device/restore callbacks;stop before client Create;not full455startup/game acceptance','executable':link['executable'],'staged_executable':(run/'RF_Online.bin').relative_to(WS).as_posix(),'normal_link_sha256':sha(WS/'inventory/client455-normal-link.json'),'engine_build_sha256':sha(WS/'inventory/client455-startup-engine-build.json'),'contracts_sha256':sha(WS/'inventory/client455-startup-contracts-native.json'),'early_startup_sha256':sha(WS/'inventory/client455-startup-native.json'),'debugger':early['debugger'],'inputs':inputs,'events':{'file':output.relative_to(WS).as_posix(),'sha256':sha(output) if output.exists() else None},'debugger_exit':result.returncode,'summary':summary,'render_configuration':config,'device_state':device,'markers':markers,'exceptions':exceptions,'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    report['own_entry_sha256']=sha(WS/'inventory/client455-own-entry.json');report['partial_client_create']=partialCreate
    report['lab_font_registration_removed']=fontRegistrationRemoved
    report['character_owner']=next((e for e in events if e['kind']=='character_owner'),{})
    report['scope']='Exact own normal PE through Character manager creation;stop before character data manager construction;not complete Create or455acceptance' if args.create else report['scope']
    if args.before_launcher:report['scope']='Exact own normal PE through existing UI initialization/LoadData/title object;stop before legacy launcher data;not full455Create/UI acceptance'
    report['nation_paths']=[e for e in events if e['kind']=='debug_string']
    report['script_sha256']=sha(Path(__file__))
    name='client455-ui-startup-native' if args.before_launcher else 'client455-create-startup-native' if args.create else 'client455-device-startup-native'
    (WS/f'inventory/{name}.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'summary':summary,'config':config,'device':device,'character_owner':report['character_owner'],'exceptions':exceptions,'lab':run.relative_to(WS).as_posix()}))
if __name__=='__main__':main()
