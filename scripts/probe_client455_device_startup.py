"""Run exact own PE through real window/device init;stop before client Create."""
import argparse,contextlib,ctypes,hashlib,json,os,re,shutil,subprocess
from pathlib import Path
from client455_asset_staging import stage_asset,staging_stats
from compare_client_binaries import WS,pe
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link
from audit_client455_own_entry import validated_entry
from client455_launcher_fixture import stage_launcher
from client455_tcp_fixture import TcpAcceptanceFixture
from client455_runtime_inputs import copy_tagged_sound_providers,copy_sky_resources,copy_grade_overlay_inputs,copy_title_movies

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def symbol(mapping,name):
    match=re.search(re.escape(name)+r'\s+([0-9a-fA-F]{8})',mapping)
    if not match:raise ValueError('Missing own symbol:'+name)
    return int(match[1],16)


def stage_world_map(client, run, index):
    from map_data455 import parse

    evidence = json.loads((WS/'inventory/client455-map-data-reference.json').read_text())
    fixtures = []
    for row in evidence['decoded_fixtures']:
        path = WS/row['file']
        if sha(path) != row['sha256']:
            raise ValueError('Changed decoded map table fixture')
        fixtures.append(path.read_bytes())
    maps = parse(*fixtures)['rows']
    if not 0 <= index < len(maps):
        raise ValueError('Map index outside the 455 table')
    row = maps[index]['record']
    bsp = Path(row[100:228].split(b'\0', 1)[0].decode('ascii'))
    minimap = Path(row[228:356].split(b'\0', 1)[0].decode('ascii'))
    if bsp.is_absolute() or len(bsp.parts) != 3 or bsp.parts[0].lower() != 'map' or bsp.suffix.lower() != '.bsp' or '..' in bsp.parts:
        raise ValueError('Unsupported BSP map path from table')
    if minimap.is_absolute() or '..' in minimap.parts or minimap.suffix.lower() != '.spr':
        raise ValueError('Unsupported minimap path from table')
    extensions = {'.bsp', '.cam', '.dds', '.ebp', '.r3m', '.r3t', '.r3x', '.rvp', '.spt'}
    map_dir = client / bsp.parent
    paths = [p for p in map_dir.iterdir() if p.is_file() and p.suffix.lower() in extensions]
    # CLevel selects sky2 by entity-file existence, otherwise it tries sky.
    # Stage only the selected entity and its same-stem material/texture archives.
    for variant in ('sky2', 'sky'):
        entity = map_dir / variant / f'{bsp.stem}{variant}.r3e'
        if entity.is_file():
            paths.append(entity)
            paths.extend(archive for suffix in ('.r3m', '.r3t')
                         if (archive := entity.with_suffix(suffix)).is_file())
            break
    paths.extend((client/'Map/Entity').glob('*.rpk'))
    paths.append(client/'System/Shader/LitGrass1.vso')
    if (client/minimap).is_file():
        paths.append(client/minimap)
    if not (client/bsp).is_file():
        raise ValueError('Pinned map table BSP is unavailable')
    records = []
    for original in sorted(paths):
        relative = original.relative_to(client)
        copy = run/relative
        owned = WS/'work/world455-inputs'/relative
        stage_asset(original, copy, owned_immutable=owned if owned.is_file() else None)
        records.append({'file': copy.relative_to(WS).as_posix(), 'sha256': sha(copy), 'original': str(original)})
    return records


def world_observation_name(walk, camera, monster, combat):
    if combat:
        return 'world-combat'
    if monster:
        return 'world-monster'
    if camera:
        return 'world-camera'
    return 'world-walk' if walk else 'world-observation'


def main(handoff=None,live_port=None,select_character=False,world_map_index=None,
         observe_world=False,observe_walk=False,observe_camera=False,observe_monster=False,observe_combat=False,
         combat_monster_record=None,combat_approach_ms=0):
    parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group();group.add_argument('--create',action='store_true');group.add_argument('--after-create',action='store_true');group.add_argument('--login-create',action='store_true');group.add_argument('--login-render',action='store_true');group.add_argument('--login-frame',action='store_true');parser.add_argument('--settle-ms',type=int,default=0);parser.add_argument('--with-lobby',action='store_true');parser.add_argument('--nation',default='Korea')
    parser.add_argument('--skip-title', choices=('logo', 'prologue'))
    args=parser.parse_args();loginProbe=args.login_create or args.login_render or args.login_frame;partialCreate=args.create or args.after_create or loginProbe
    if args.skip_title and (not args.login_frame or live_port is not None):
        parser.error('--skip-title requires the offline Login frame probe')
    if not 0<=args.settle_ms<=8000 or (args.settle_ms and not args.login_frame) or (args.with_lobby and not loginProbe):raise ValueError('Invalid Login observation options')
    if (handoff is None)!=(live_port is None) or (handoff is not None and (len(handoff)!=93 or live_port!=27830 or args.nation!='Taiwan')):raise ValueError('Invalid live handoff observation')
    countries=json.loads((WS/'inventory/client455-nation-paths-reference.json').read_text())['references'][0]['rows'];country=next((row for row in countries if row['setting']==args.nation),None)
    if country is None:raise ValueError('Unknown exact country setting:'+args.nation)
    earlyFile=WS/'inventory'/('client455-startup-native.json' if args.nation=='Korea' else f'client455-startup-{args.nation.lower()}-native.json')
    link=json.loads((WS/'inventory/client455-normal-link.json').read_text());validate_normal_link(link);early=json.loads(earlyFile.read_text());contracts=json.loads((WS/'inventory/client455-startup-contracts-native.json').read_text());engine=json.loads((WS/'inventory/client455-startup-engine-build.json').read_text())
    if early['normal_link_sha256']!=sha(WS/'inventory/client455-normal-link.json') or contracts['build_sha256']!=sha(WS/'inventory/client455-startup-engine-build.json'):raise ValueError('Current early startup/contracts evidence required')
    entry=validated_entry();source=WS/link['executable']['file'];raw=source.read_bytes();base=pe(raw)['image_base'];mapping=(WS/link['map']['file']).read_text();mainVa=symbol(mapping,'_WinMain@16');stopVa=base+int(entry['points']['after_create' if args.after_create else 'before_char_data' if args.create else 'after_d3d']['rva'],16)
    loginSymbol='?Create@CGP_LogIn@@UAEHXZ' if args.login_create else '?Render@CGP_LogIn@@MAEJXZ'
    if loginProbe:stopVa=symbol(mapping,loginSymbol)
    parent=WS/'work/m9'/sha(source)[:8];parent.mkdir(parents=True,exist_ok=True);index=1
    prefix='ui-startup' if args.after_create else 'create-startup' if args.create else 'device-startup'
    if loginProbe:prefix='login-create' if args.login_create else 'login-render'
    if args.login_frame:prefix='login-frame'
    if args.skip_title:prefix=f'title-escape-{args.skip_title}'
    if select_character:
        if handoff is None or not args.login_frame:raise ValueError('Selection observation needs actual live Login')
        prefix='selection'
    elif world_map_index is not None:
        raise ValueError('World map inputs require a live selection observation')
    if observe_world:
        if world_map_index is None:raise ValueError('World observation needs explicitly staged live map inputs')
        prefix=world_observation_name(observe_walk, observe_camera, observe_monster, observe_combat)
        observation_name=prefix
    if handoff is not None:prefix+='-live'
    if args.nation!='Korea':prefix+='-'+args.nation.lower()
    while (parent/f'{prefix}{index:03d}').exists():index+=1
    run=parent/f'{prefix}{index:03d}';run.mkdir();oldRoot=(WS/early['staged_executable']).parent;inputs=[]
    for item in early['lab_inputs']:
        original=WS/item['file'];relative=original.relative_to(oldRoot);copy=run/relative
        if sha(original)!=item['sha256']:raise ValueError('Changed private startup input')
        copy.parent.mkdir(parents=True,exist_ok=True);stage_asset(original,copy,item['sha256'],owned_immutable=original);inputs.append({'file':copy.relative_to(WS).as_posix(),'sha256':sha(copy)})
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455'])
    for name in ['System/shader/Grass1.vsh','System/shader/grass1.vso','System/console.jpg']:
        original=client/name;copy=run/name
        if not original.is_file():raise ValueError('Missing actual startup resource:'+name)
        copy.parent.mkdir(parents=True,exist_ok=True);stage_asset(original,copy);inputs.append({'file':copy.relative_to(WS).as_posix(),'sha256':sha(copy)})
    inputs+=copy_sky_resources(run)
    if args.after_create or loginProbe:
        inputs+=copy_grade_overlay_inputs(run)
        for name in ['SpriteImage/Common/mouse.spr',f'SpriteImage/{country["folder"]}/common.spr']:
            original=client/name;copy=run/name;copy.parent.mkdir(parents=True,exist_ok=True);stage_asset(original,copy);inputs.append({'file':copy.relative_to(WS).as_posix(),'sha256':sha(copy)})
    if loginProbe:
        inputs += copy_title_movies(client, run, country['folder'])
        for name in ['Effect/EffectEntityList.spt','Effect/MagicSptList.spt']:
            original=client/name;copy=run/name;stage_asset(original,copy);inputs.append({'file':copy.relative_to(WS).as_posix(),'sha256':sha(copy),'original':str(original)})
        for name in [f'SpriteImage/{country["folder"]}/login.spr',f'SpriteImage/{country["folder"]}/loading.spr','SpriteImage/Common/main.spr']:
            original=client/name;copy=run/name;stage_asset(original,copy);inputs.append({'file':copy.relative_to(WS).as_posix(),'sha256':sha(copy),'original':str(original)})
    if select_character:
        # MainGame initializes the confirmed country chat script after its UI.
        # Stage its exact reference input; EDF-only bootstrap intentionally
        # omits .txt files and must not be mistaken for a missing client port.
        chat=json.loads((WS/'inventory/client455-chat-reference.json').read_text())
        row=next(r for r in chat['inputs'] if r['runtime_relative'].startswith(f'DataTable/{country["folder"]}/'))
        original=client/row['runtime_relative'];copy=run/row['runtime_relative']
        stage_asset(original,copy,row['sha256'],owned_immutable=WS/row['file'])
        inputs.append({'file':copy.relative_to(WS).as_posix(),'sha256':sha(copy),'original':str(original)})
        # MainGame loads these panels before asking for base data. Stage their
        # exact localized and Common sprites from the owned shared pool.
        for folder in ['Common',country['folder']]:
            for filename in ['main.spr','EtcUI.spr','charinfo.spr','summon.spr','item.spr','inventory.spr','ItemLock.spr','SocketState.spr','system.spr','unit.spr','skillwindow.spr','forcewindow.spr','shop.spr','trade.spr','oreproc.spr','itemmake.spr','itemupgrade.spr','exchange.spr','mining.spr','class.spr','renewal.spr','dungeon.spr']:
                original=client/'SpriteImage'/folder/filename
                if not original.is_file():continue
                copy=run/original.relative_to(client)
                if any(row['file']==copy.relative_to(WS).as_posix() for row in inputs):continue
                stage_asset(original,copy);inputs.append({'file':copy.relative_to(WS).as_posix(),'sha256':sha(copy),'original':str(original)})
    if observe_combat:
        # Stock arrows for the NeutralB bow scenario and the damage atlas.
        for name in ('Effect/EffectEntity6.rpk', 'Effect/effectfont.dds'):
            original = client / name
            copy = run / name
            stage_asset(original, copy)
            inputs.append({'file': copy.relative_to(WS).as_posix(), 'sha256': sha(copy), 'original': str(original)})
    if world_map_index is not None:
        inputs += stage_world_map(client, run, world_map_index)
    if args.with_lobby:
        world=json.loads((WS/'inventory/client455-graphics-runtime.json').read_text());case=next(x for x in world['cases'] if x['case']=='level-lobby')
        for row in case['archives']:
            if not row['path'].lower().startswith('map/lobby/'):continue
            original=client/row['path'];copy=run/row['path'];owned=WS/'work/world455-inputs'/row['path'];stage_asset(original,copy,row['sha256'],owned_immutable=owned if owned.is_file() else None);inputs.append({'file':copy.relative_to(WS).as_posix(),'sha256':sha(copy),'original':str(original)})
        original=client/'System/titlelogo.tga';copy=run/'System/titlelogo.tga';stage_asset(original,copy);inputs.append({'file':copy.relative_to(WS).as_posix(),'sha256':sha(copy),'original':str(original)})
    if partialCreate:
        inputs+=copy_tagged_sound_providers(run)
        shaders=json.loads((WS/'inventory/client455-shaders-reference.json').read_text())
        for row in shaders['programs']:
            original=WS/row['copy'];copy=run/'System/shader'/(row['name']+'.sho')
            if sha(original)!=row['sha256']:raise ValueError('Changed actual Character shader')
            stage_asset(original,copy,row['sha256'],owned_immutable=original);inputs.append({'file':copy.relative_to(WS).as_posix(),'sha256':sha(copy)})
    if handoff is not None:
        #Only bootstrap data andthis locale,not another fullclient copy.
        table_root=client/'DataTable'
        tables=list(table_root.iterdir())+list((table_root/country['folder']).rglob('*'))
        for original in sorted(tables):
            if not original.is_file() or original.suffix.lower() not in {'.edf','.spt','.dat','.rfs'}:continue
            copy=run/original.relative_to(client)
            if any(r['file']==copy.relative_to(WS).as_posix() for r in inputs):continue
            stage_asset(original,copy);inputs.append({'file':copy.relative_to(WS).as_posix(),'sha256':sha(copy),'original':str(original)})
        #Reuse the established catalog/equipment input lists and shared pool.
        #The catalog needs actual skeletons,not missing-file fallback objects.
        staged={r['file'] for r in inputs}
        for manifest in ['resource-catalog','equipment','equipment-providers','equipment-effects','live-resource-inputs']:
            if manifest=='live-resource-inputs':
                file=WS/'inventory/client455-live-resource-inputs.json'
                if not file.exists():continue
            else:file=WS/f'inventory/client455-{manifest}-reference.json'
            reference=json.loads(file.read_text())
            for row in reference['inputs']:
                original=Path(row['original']);copy=run/original.relative_to(client);relative=copy.relative_to(WS).as_posix()
                if relative in staged:continue
                stage_asset(original,copy,expected=row['sha256']);inputs.append({'file':relative,'sha256':sha(copy),'original':str(original)})
                staged.add(relative)
    layout=contracts['layout'];state=symbol(mapping,'?stState@@3U_R3ENGINE_STATE@@A')-base;app=symbol(mapping,'?g_MainApp@@3VCMainApp@@A')-base
    values=[state+layout['state_fullscreen'],state+layout['state_renderbits'],app,layout['ready'],layout['window'],layout['device'],layout['windowed'],int(entry['points']['after_sound']['rva'],16),int(entry['points']['after_d3d']['rva'],16),symbol(mapping,'?g_ifCharIF@@3PAVChInterface@@A')-base,layout['character_device']]
    plan=run/'device.plan';plan.write_text(' '.join(f'{value:x}' for value in values)+'\n',encoding='ascii');inputs.append({'file':plan.relative_to(WS).as_posix(),'sha256':sha(plan)})
    debugger=WS/early['debugger']['file']
    if sha(debugger)!=early['debugger']['sha256']:raise ValueError('Changed own debugger')
    output=run/'debug-events.jsonl';command=[str(debugger),str(run/'RF_Online.bin'),str(output),f'{mainVa-base:x}',f'{stopVa-base:x}',str(plan)]+(['after_create'] if args.after_create else [])
    if loginProbe:command+=['selection' if select_character else 'login_create' if args.login_create else 'login_frame' if args.login_frame else 'login_render']
    environment=os.environ.copy();environment.pop('RF455_CAPTURE_LOGIN',None);environment.pop('RF455_OBSERVE_PROTOCOL',None)
    environment.pop('RF455_CAPTURE_WORLD',None)
    environment.pop('RF455_OBSERVE_WALK',None)
    environment.pop('RF455_OBSERVE_CAMERA',None)
    environment.pop('RF455_CAPTURE_MONSTERS',None)
    environment.pop('RF455_OBSERVE_COMBAT',None)
    environment.pop('RF455_COMBAT_RECORD',None)
    environment.pop('RF455_COMBAT_APPROACH_MS',None)
    environment.pop('RF455_SKIP_TITLE_STAGE',None)
    if observe_world:environment['RF455_CAPTURE_WORLD']='1'
    if observe_walk:environment['RF455_OBSERVE_WALK']='1'
    if observe_camera:environment['RF455_OBSERVE_CAMERA']='1'
    if observe_monster or observe_combat:environment['RF455_CAPTURE_MONSTERS']='1'
    if observe_combat:environment['RF455_OBSERVE_COMBAT']='1'
    if combat_monster_record is not None:environment['RF455_COMBAT_RECORD']=str(combat_monster_record)
    if combat_approach_ms:environment['RF455_COMBAT_APPROACH_MS']=str(combat_approach_ms)
    if live_port is not None:environment['RF455_OBSERVE_PROTOCOL']='1'
    if args.skip_title:
        environment['RF455_OBSERVE_PROTOCOL']='1'
        environment['RF455_SKIP_TITLE_STAGE']='1' if args.skip_title == 'logo' else '2'
    if args.login_frame:environment['RF455_CAPTURE_LOGIN']='1';environment['RF455_CAPTURE_LOGIN_DELAY_MS']=str(args.settle_ms)
    secretFile=run/'System/DefaultSet.tmp';private_handoff_removed=False
    with (contextlib.nullcontext(None) if handoff is not None else TcpAcceptanceFixture()) as transport:
        if handoff is None:
            fixture=stage_launcher(run,country['id'],WS,transport.port);inputs=[r for r in inputs if r['file']!=fixture['file']]+[fixture]
        else:
            if secretFile.exists() and secretFile.stat().st_nlink!=1:raise ValueError('Live handoff must be a private file')
            secretFile.write_bytes(handoff);handoff=None
            inputs=[r for r in inputs if r['file']!=secretFile.relative_to(WS).as_posix()]
        try:
            result=subprocess.run(command,cwd=run,capture_output=True,timeout=200 if live_port is not None else 40,creationflags=subprocess.CREATE_NO_WINDOW,env=environment)
        finally:
            if live_port is not None:
                if not secretFile.resolve().is_relative_to((WS/'work/m9').resolve()):raise ValueError('Private handoff cleanup escaped lab')
                secretFile.unlink(missing_ok=True);private_handoff_removed=not secretFile.exists()
            removeFont=ctypes.WinDLL('gdi32.dll').RemoveFontResourceW;removeFont.argtypes=[ctypes.c_wchar_p];removeFont.restype=ctypes.c_int
            fontRegistrationRemoved=bool(removeFont(str(run/'System/010.TTF')))
    (run/'console.txt').write_bytes(result.stdout+result.stderr)
    events=[json.loads(line) for line in output.read_text().splitlines()] if output.exists() else [];summary=next((e for e in events if e['kind']=='summary'),{});config=next((e for e in events if e['kind']=='render_configuration'),{});device=next((e for e in events if e['kind']=='device_state'),{});markers=[e for e in events if e['kind']=='checkpoint'];exceptions=[e for e in events if e['kind']=='exception']
    report={'scope':'Exact own normal PE windowed D3D/device/restore callbacks;stop before client Create;not full455startup/game acceptance','executable':link['executable'],'staged_executable':(run/'RF_Online.bin').relative_to(WS).as_posix(),'normal_link_sha256':sha(WS/'inventory/client455-normal-link.json'),'engine_build_sha256':sha(WS/'inventory/client455-startup-engine-build.json'),'contracts_sha256':sha(WS/'inventory/client455-startup-contracts-native.json'),'early_startup_sha256':sha(WS/'inventory/client455-startup-native.json'),'debugger':early['debugger'],'inputs':inputs,'events':{'file':output.relative_to(WS).as_posix(),'sha256':sha(output) if output.exists() else None},'debugger_exit':result.returncode,'summary':summary,'render_configuration':config,'device_state':device,'markers':markers,'exceptions':exceptions,'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    report['own_entry_sha256']=sha(WS/'inventory/client455-own-entry.json');report['partial_client_create']=partialCreate;report['tcp_fixture']=transport.report() if transport is not None else {'enabled':False};report['tcp_fixture_sha256']=sha(WS/'scripts/client455_tcp_fixture.py')
    if live_port is not None:report['live_server']={'host':'127.0.0.1','port':live_port,'real_launcher_handoff':True,'private_handoff_removed':private_handoff_removed,'full_game_authentication_verified':False}
    report['nation']=args.nation;report['early_startup_file']=earlyFile.relative_to(WS).as_posix();report['early_startup_sha256']=sha(earlyFile)
    report['lab_font_registration_removed']=fontRegistrationRemoved
    report['shared_asset_staging']=staging_stats();report['asset_staging_script_sha256']=sha(WS/'scripts/client455_asset_staging.py')
    report['character_owner']=next((e for e in events if e['kind']=='character_owner'),{})
    report['scope']='Exact own normal PE through Character manager creation;stop before character data manager construction;not complete Create or455acceptance' if args.create else report['scope']
    if args.after_create:report['scope']='Exact own normal PE after accepted offline launcher metadata and existing Create returned;stop before filters/game loop;not full455bootstrap/Create/UI acceptance'
    report['completed_existing_client_create']=args.after_create and bool(markers) and markers[-1].get('eax')==1
    report['nation_paths']=[e for e in events if e['kind']=='debug_string' and e.get('value','').startswith(('RF455 ','.\\DataTable\\'))]
    if live_port is not None:report['protocol_observations']=[e['value'] for e in events if e['kind']=='debug_string' and e.get('value','').startswith('RF455 Protocol:')]
    report['script_sha256']=sha(Path(__file__))
    name='client455-ui-startup-native' if args.after_create else 'client455-create-startup-native' if args.create else 'client455-device-startup-native'
    if loginProbe:
        name='client455-login-create-native' if args.login_create else 'client455-login-render-native'
        if args.login_frame:name='client455-login-frame-native'
        report.update(scope='Actual ordinary own WinMain through Title to Login;frame mode captures after the configured delay and observes a following Render return;not455stage/UI/auth acceptance',login_method=loginSymbol,login_checkpoint_rva=hex(stopVa-base),login_checkpoint_bytes_sha256=hashlib.sha256(read_va(raw,stopVa,16)).hexdigest(),stage_state=next((e for e in events if e['kind']=='stage_state'),{}),reached_first_login=bool(summary.get('final_checkpoint_reached')))
        report['login_render_returned_after_capture']=args.login_frame and bool(summary.get('final_checkpoint_reached')) and any(e['name']=='after_login_render_following_capture' for e in markers)
        #Compatibility aliases for earlier local evidence readers;not frame1.
        report['first_login_frame_completed']=report['login_render_returned_after_capture']
        png,meta=run/'login-frame.png',run/'login-frame.json'
        report['captured_frame']={'file':png.relative_to(WS).as_posix(),'sha256':sha(png)} if png.exists() else None
        report['capture_result']=json.loads(meta.read_text()) if meta.exists() else None
        report['capture_metadata']={'file':meta.relative_to(WS).as_posix(),'sha256':sha(meta)} if meta.exists() else None
        report['first_login_frame_captured']=bool(report['first_login_frame_completed'] and report['captured_frame'] and report['capture_result'] and report['capture_result']['result']>=0)
        report['login_frame_captured']=report['first_login_frame_captured']
        report['legacy_first_frame_field_names_are_aliases']=True
        report['observation_delay_ms']=args.settle_ms;report['lobby_inputs_staged']=args.with_lobby
    if select_character:
        name='client455-character-selection-native';report['scope']='Actual own Login then addressed Enter key in own child window;records real selection protocol andfirst following failure,not world acceptance'
        report['selection_input']=[e for e in events if e['kind'] in ['selection_key_posted','selection_observation_end']]
    if observe_world:
        name=f'client455-{observation_name}-native'
        report['scope']=('Ordinary own-client world render, scoped camera drags, monster pick and mapped attack key'
                         if observe_combat else 'Ordinary own-client world render and scoped Win32 keyboard state at the move poll'
                         if observe_walk else 'Ordinary own-client world render and scoped right mouse drags'
                         if observe_camera else 'Ordinary own-client world render and passive state after accepted position mode')
        report['world_observations']=[e['value'] for e in events if e['kind']=='debug_string'
                                      and e['value'].startswith(('RF455 WorldSample:', 'RF455 WorldCapture:'))]
        frames=[run/filename for filename in ('world-post-position.png', 'world-post-position-settled.png')]
        report['world_frames']=[{'file':frame.relative_to(WS).as_posix(),'sha256':sha(frame)}
                                for frame in frames if frame.is_file()]
        if observe_monster or observe_combat:
            report['monster_frames']=[{'file':frame.relative_to(WS).as_posix(),'sha256':sha(frame)}
                                      for frame in sorted(run.glob('world-monster-*.png'))]
        if observe_combat:
            report['combat_monster_record'] = combat_monster_record
            report['combat_approach_ms'] = combat_approach_ms
            report['combat_impact_frames']=[{'file':frame.relative_to(WS).as_posix(),'sha256':sha(frame)}
                                            for frame in sorted(run.glob('world-impact-*.png'))]
    if live_port is not None:name=name.replace('-native','-live-native')
    if args.nation!='Korea':name=name.replace('-native','-'+args.nation.lower()+'-native')
    if args.skip_title:
        report['title_escape']=[e for e in events if e['kind']=='title_escape_posted']
        name=f'client455-title-escape-{args.skip_title}-{args.nation.lower()}-native'
    report_dir='artifacts/client455-progress' if observe_world or args.skip_title else 'inventory'
    (WS/report_dir/f'{name}.json').write_text(json.dumps(report,indent=2)+'\n')
    display={'summary':summary,'config':config,'device':device,'character_owner':report['character_owner'],'exceptions':exceptions,'lab':run.relative_to(WS).as_posix()}
    if loginProbe:display.update(stage_state=report['stage_state'],reached_first_login=report['reached_first_login'],exceptions=[e for e in exceptions if not e.get('first_chance')])
    print(json.dumps(display))
    if loginProbe and (not report['reached_first_login'] or (args.login_frame and not report['first_login_frame_captured'])):raise SystemExit(1)
    return report
if __name__=='__main__':main()
