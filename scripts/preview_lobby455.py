"""One reusable offline lobby runtime; no real account or server connection."""
import argparse,ctypes,json,os,shutil,subprocess,time
from pathlib import Path
from ctypes import wintypes
from PIL import Image
from preview_client455 import ROOT,game_window,sha
from client455_asset_staging import stage_asset,staging_stats
from client455_launcher_fixture import stage_launcher
from client455_tcp_fixture import TcpAcceptanceFixture
from client455_normal_link_evidence import validate_normal_link
from workspace_guard import require_budget

INPUT_RECEIPT=ROOT/'artifacts/baseline-20261114/lobby-probe.json'
OMITTED={Path('RF_Online.bin'),Path('RF_Online.map'),Path('device.plan'),
         Path('checkpoint-label.txt'),Path('launcher-commandline.txt'),Path('System/DefaultSet.tmp')}

def memory_sample(game):
    class Counters(ctypes.Structure):
        _fields_=[('cb',wintypes.DWORD),('faults',wintypes.DWORD)]+[(name,ctypes.c_size_t) for name in
            ['peak_working_set','working_set','peak_paged','paged','peak_nonpaged','nonpaged','pagefile','peak_pagefile','private_bytes']]
    api=ctypes.WinDLL('psapi',use_last_error=True)
    api.GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ctypes.c_void_p,wintypes.DWORD]
    value=Counters();value.cb=ctypes.sizeof(value)
    if not api.GetProcessMemoryInfo(int(game._handle),ctypes.byref(value),value.cb):return {'error':ctypes.get_last_error()}
    return {'working_set_bytes':value.working_set,'private_bytes':value.private_bytes,'peak_working_set_bytes':value.peak_working_set}


def private_copy(source,target):
    """Replace only this runtime's file, never write through an asset hard link."""
    temporary=target.with_name(target.name+'.preview-new')
    if temporary.exists():temporary.unlink()
    shutil.copyfile(source,temporary)
    os.replace(temporary,target)


def stage_taiwan(run,active):
    """Reuse the Taiwan lobby asset receipt, not the Russian live-world runtime."""
    require_budget()
    report=json.loads(INPUT_RECEIPT.read_text(encoding='utf-8'))
    if report.get('nation')!='Taiwan' or not report.get('lobby_inputs_staged'):
        raise ValueError('Taiwan lobby input receipt required')
    recorded=(ROOT/report['staged_executable']).resolve().parent
    if not recorded.is_relative_to((ROOT/'work/m9').resolve()):
        raise ValueError('Lobby receipt is outside owned runs')
    # Same pinned inputs; prefer the run that reached lobby with prologue skip.
    reference=recorded.parent/'title-escape-prologue-taiwan001'
    source=reference if reference.is_dir() else recorded
    inputs={}
    for row in report['inputs']:
        listed=(ROOT/row['file']).resolve()
        if not listed.is_relative_to(recorded):
            raise ValueError('Lobby input escapes receipt runtime: '+row['file'])
        relative=listed.relative_to(recorded)
        if relative in OMITTED or relative.suffix.lower() in {'.avi','.wmv'}:
            continue
        if relative in inputs and inputs[relative]!=row['sha256']:
            raise ValueError('Conflicting lobby input: '+str(relative))
        original=source/relative
        if not original.resolve().is_relative_to(source.resolve()) or sha(original)!=row['sha256']:
            raise ValueError('Changed pinned Taiwan lobby input: '+str(relative))
        inputs[relative]=row['sha256']
    required={Path('R3Engine.ini'),Path('DataTable/ClientSystem.ini'),
              Path('SpriteImage/zh-tw/login.spr'),Path('Map/lobby/lobby.bsp')}
    if not required.issubset(inputs):raise ValueError('Incomplete Taiwan lobby inputs')
    run.mkdir(parents=True,exist_ok=True)
    for relative,digest in inputs.items():
        original,target=source/relative,run/relative
        if not target.resolve().is_relative_to(run.resolve()):
            raise ValueError('Staging target escapes lobby runtime')
        target.parent.mkdir(parents=True,exist_ok=True)
        if relative.suffix.lower() in {'.ini','.cfg','.tmp'}:
            private_copy(original,target)
        else:
            # Switching this one owned fixture from Russia may change an input.
            if target.exists() and sha(target)!=digest:target.unlink()
            stage_asset(original,target,digest,owned_immutable=original)
    # The new lobby settings window uses the same verified system atlas as the world.
    atlas=Path('SpriteImage/zh-tw/system.spr')
    atlas_sha='75d171995f64ed16d5d4715d1b681b54bfdce328409fd91352389526412f8d36'
    client=Path(json.loads((ROOT/'config/paths.json').read_text())['client_455'])
    stage_asset(client/atlas,run/atlas,atlas_sha)
    # Omit movie files only here, including any leftovers from a previous preview.
    for path in run.rglob('*'):
        if path.is_file() and path.suffix.lower() in {'.avi','.wmv'}:
            if not path.resolve().is_relative_to(run.resolve()):raise ValueError('Movie escapes fixture')
            path.unlink()
    (run/'launcher-commandline.txt').unlink(missing_ok=True)
    executable=ROOT/active['file']
    if sha(executable)!=active['sha256']:raise ValueError('Current executable changed')
    target=run/'RF_Online.bin'
    if not target.exists() or target.stat().st_nlink!=1 or sha(target)!=active['sha256']:
        private_copy(executable,target)
    return dict(sha256=active['sha256'],entry_rva=active['entry_rva'],architecture=active['architecture'],
                staged_executable=target.relative_to(ROOT).as_posix(),nation='Taiwan',
                input_receipt=INPUT_RECEIPT.relative_to(ROOT).as_posix(),input_receipt_sha256=sha(INPUT_RECEIPT),
                asset_source=source.relative_to(ROOT).as_posix(),staged_input_count=len(inputs),
                settings_atlas={'file':atlas.as_posix(),'sha256':atlas_sha},asset_staging=staging_stats(),movies_omitted=True)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--mode',choices=['classic','enhanced'],default='classic')
    parser.add_argument('--seconds',type=int,default=12)
    parser.add_argument('--interactive',action='store_true')
    parser.add_argument('--check-settings',action='store_true')
    parser.add_argument('--camera-seconds',type=float,default=3.2)
    args=parser.parse_args()
    artifact_name='preview' if args.interactive else args.mode
    if not 0<=args.camera_seconds<=30:parser.error('Camera time must be 0..30 seconds')
    if args.camera_seconds!=3.2 and not args.interactive:artifact_name='alternate-view'
    if not 3<=args.seconds<=60:parser.error('Capture duration must be 3..60 seconds')
    link=json.loads((ROOT/'inventory/client455-normal-link.json').read_text())
    if validate_normal_link(link)!='PASS':raise RuntimeError('Current build required')
    active=link['executable']
    run=ROOT/'work/lobby-visual/runtime'
    receipt=run/'preview.json'
    if receipt.exists() and game_window(json.loads(receipt.read_text()).get('pid',0)):
        raise RuntimeError('Previous preview is open; preserve the user session')
    evidence=stage_taiwan(run,active)
    config=run/'R3Engine.ini'
    config.write_text('[Setup]\nLanguage=Taiwan\n[RenderState]\nScreenXSize=1920\nScreenYSize=1080\nbFullScreen=FALSE\nTextureDetail=3\nMSAA=4\nDynamicLight=1\nShadowDetail=1\n'
                      f'LobbyPost={int(args.mode=="enhanced")}\nEnhancedActorLighting={int(args.mode=="enhanced")}\n'
                      '[Sound]\nSound=FALSE\nMusic=FALSE\n',encoding='ascii')
    frame=run/'login-frame.png';frame.unlink(missing_ok=True)
    (run/'login-frame.json').unlink(missing_ok=True)
    (run/'lobby-visual.json').unlink(missing_ok=True)
    (run/'lobby-settings-test.json').unlink(missing_ok=True)
    destination=ROOT/'artifacts/lobby-visual';destination.mkdir(parents=True,exist_ok=True)
    env={k:v for k,v in os.environ.items() if not k.startswith('RF455_')}
    env.update(RF455_CAPTURE_LOGIN='1',RF455_CAPTURE_LOGIN_DELAY_MS='1500',RF455_LOBBY_REFERENCE='1',
               RF455_SKIP_TITLE_STAGE='2',RF455_LOBBY_CAMERA_SECONDS=str(args.camera_seconds))
    if args.check_settings:env['RF455_LOBBY_SETTINGS_TEST']='1'
    api=ctypes.WinDLL('user32',use_last_error=True)
    api.PostMessageW.argtypes=[wintypes.HWND,wintypes.UINT,wintypes.WPARAM,wintypes.LPARAM]
    evidence.update(mode=args.mode,offline=True,real_authentication=False,server_modified=False)
    with TcpAcceptanceFixture() as fixture:
        handoff=run/'System/DefaultSet.tmp'
        # Synthetic Taiwan CCR handoff is private and refreshed for this loopback port.
        handoff.unlink(missing_ok=True)
        evidence['launcher_fixture']=stage_launcher(run,8,ROOT,fixture.port)
        game=subprocess.Popen([str(run/'RF_Online.bin')],
                              cwd=run,env=env,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                              creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        evidence['pid']=game.pid;receipt.write_text(json.dumps(evidence,indent=2))
        try:
            started=time.monotonic()
            while time.monotonic()-started<args.seconds:
                if game.poll() is not None:raise RuntimeError(f'Lobby exited: {game.returncode}')
                if frame.exists():
                    try:
                        with Image.open(frame) as im:
                            im.load()
                            if im.size!=(1920,1080):raise RuntimeError('Unexpected frame size')
                        break
                    except OSError:pass
                time.sleep(.15)
            else:raise RuntimeError('No Full HD lobby frame before deadline')
            saved=destination/f'{artifact_name}.png';shutil.copyfile(frame,saved)
            evidence.update(frame=saved.relative_to(ROOT).as_posix(),frame_sha256=sha(saved),resolution=[1920,1080],capture_seconds=round(time.monotonic()-started,2))
            evidence['memory']=memory_sample(game)
            if (run/'lobby-visual.json').exists():
                evidence['renderer']=json.loads((run/'lobby-visual.json').read_text())
            if args.check_settings:
                while time.monotonic()-started<args.seconds:
                    if game.poll() is not None:raise RuntimeError('Client exited during settings check')
                    check=run/'lobby-settings-test.json'
                    if check.exists():
                        try:
                            evidence['settings_check']=json.loads(check.read_text())
                            if evidence['settings_check']['completed_phases']==6:break
                        except json.JSONDecodeError:pass
                    time.sleep(.15)
                else:raise RuntimeError('Settings check deadline')
                for name in ['lobby-settings.png','lobby-switched.png','lobby-restored.png']:
                    shutil.copyfile(run/name,destination/name)
                if not evidence['settings_check']['passed']:raise RuntimeError('Settings check failed; see receipt')
            print(json.dumps(evidence),flush=True)
            if args.interactive:
                print('Lobby preview is open; close its window to finish.',flush=True)
                game.wait()
        finally:
            if game.poll() is None:
                hwnd=game_window(game.pid)
                if hwnd:api.PostMessageW(hwnd,0x0010,0,0)
                try:game.wait(timeout=8)
                except subprocess.TimeoutExpired:game.terminate();game.wait(timeout=8)
            evidence['exit_code']=game.returncode
            receipt.write_text(json.dumps(evidence,indent=2))
            (destination/f'{artifact_name}.json').write_text(json.dumps(evidence,indent=2))
    print(json.dumps(dict(fixture=fixture.report())),flush=True)

if __name__=='__main__':main()
