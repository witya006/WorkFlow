"""Verify actual record ownership, archived nuclear effects, Miles and shared clock."""
import ctypes,hashlib,json,os,shutil,subprocess
from pathlib import Path
from PIL import Image
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from client455_own_probe import build_full_object_probe
from client455_runtime_inputs import copy_character_shaders,copy_tagged_sound_providers
from compare_client_binaries import WS,pe
from rpk455 import Rpk


def main(source_name='client455_nuclear_registry_probe.cpp',probe_name='nuclear-registry',report_name='client455-nuclear-registry-native',extra_world_manifest=None,extra_runtime_files=()):
    source=WS/'scripts/native'/source_name;exe=build_full_object_probe(probe_name,source);holder=WS/'work/m9'/sha(exe)[:8];index=1
    while(holder/f'{probe_name}-{index:03d}').exists():index+=1
    run=holder/f'{probe_name}-{index:03d}';run.mkdir(parents=True);target=run/exe.name;shutil.copyfile(exe,target);mapping=target.with_suffix('.map');shutil.copyfile(exe.with_suffix('.map'),mapping)
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);inputs=[];paths=set()
    def copy(original,expected=None,immutable=None):
        require(original.is_relative_to(client),'Actual client input');dest=run/original.relative_to(client)
        if dest in paths:return
        paths.add(dest);dest.parent.mkdir(parents=True,exist_ok=True)
        require(not expected or sha(original)==expected,'Pinned original input '+str(original))
        if immutable:os.link(immutable,dest)
        else:shutil.copyfile(original,dest)
        inputs.append(dict(**record(dest),original=str(original)))
    world_manifest=WS/'inventory/client455-rvp-actor-native.json'
    for row in load('client455-rvp-actor-native')['inputs']:
        if 'original' in row:check(row);copy(Path(row['original']),row['sha256'],WS/row['file'])
    if extra_world_manifest:
        for row in load(extra_world_manifest)['inputs']:
            parts=Path(row['file']).parts
            if 'Map' not in parts:continue
            check(row);copy(client.joinpath(*parts[parts.index('Map'):]),row['sha256'],WS/row['file'])
    # Nuclear59 is pinned by the accepted resource reference. Generic entity1
    # has a separate archive: find its actual directory rather than guessing.
    resources=WS/'inventory/client455-map-resources.json';archive_manifest=json.loads(resources.read_text())
    for row in load('client455-effect-resources-reference')['inputs']:
        if Path(row['file']).suffix.lower()=='.rpk':check(row);copy(Path(row['file']),row['sha256'])
    dependencies=[]
    for row in archive_manifest['other_archive_index_search']:
        if not row['path'].lower().startswith('effect/'):continue
        original=client/row['path'];raw=original.read_bytes();archive=Rpk(raw)
        require(hashlib.sha256(raw[:archive.base]).hexdigest()==row['header_tables_sha256'],'Pinned archive directory')
        hits=[name for name in archive.files if name.startswith(b'weapon\\d_act\\dam\\src\\dynamic2\\')]
        if hits:
            copy(original);dependencies.append(dict(archive=row['path'],members=[x.decode('ascii') for x in hits]))
    require(dependencies,'Actual entity1 dynamic-light archive')
    for name in ['mss32.dll','Snd/WaveList.spt','Snd/Character/Newclear/Radar_00.wav','Snd/Character/Newclear/Missile_00.wav','Snd/Character/Newclear/Newclear_00.wav','Effect/EffectEntityList.spt','Effect/MagicSptList.spt','System/console.jpg','System/010.TTF','DataTable/ko-kr/NDLanguage.edf','DataTable/ko-kr/Cska.txt']:
        copy(client/name)
    inputs+=copy_character_shaders(run)+copy_tagged_sound_providers(run)
    for relative in extra_runtime_files:copy(client/relative)
    config=run/'R3Engine.ini';config.write_text('[Setup]\nLanguage=Korea\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n[Path]\nSoundPath=.\\Snd\\\nEffectPath=.\\Effect\\\n[Sound]\nSound=FALSE\nMusic=FALSE\n',encoding='ascii');inputs.append(record(config))
    settings=run/'DataTable/GameSetting.ini';settings.write_text('[ChatMode]\nAll=0\nParty=0\nGuild=0\nSystem=0\n[DefModeOn]\nAll=0\n',encoding='ascii');before=run/'settings-before.ini';shutil.copyfile(settings,before);inputs.append(record(before))
    startup=subprocess.STARTUPINFO();startup.dwFlags=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
    try:result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW,startupinfo=startup)
    finally:
        remove=ctypes.WinDLL('gdi32.dll').RemoveFontResourceW;remove.argtypes=[ctypes.c_wchar_p];remove.restype=ctypes.c_int;remove(str(run/'System/010.TTF'))
    console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json';frames=[]
    for path in sorted(run.glob('*.bgra')):
        preview=path.with_suffix('.png');Image.frombytes('RGBA',(640,480),path.read_bytes(),'raw','BGRA').convert('RGB').save(preview);frames.append(dict(**record(path),preview=record(preview)))
    for row in inputs:check(row)
    report=dict(scope='Actual stage-owned registry record32/FX/tag2/launch/impact/shared process clock in full-object lab;ordinary receiver assessed separately,full stage/world lifecycle remain open',source=record(source),script_sha256=sha(Path(__file__)),builder_sha256=sha(WS/'scripts/client455_own_probe.py'),runtime_inputs_sha256=sha(WS/'scripts/client455_runtime_inputs.py'),world_input_manifest=record(world_manifest),archive_input_manifest=record(resources),generic_entity_dependencies=dependencies,normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),exe=record(target),map=record(mapping),architecture=pe(target.read_bytes())['architecture'],console=record(console),inputs=inputs,inputs_unchanged=True,output=record(output) if output.exists() else None,frames=frames,native=json.loads(output.read_text()) if output.exists() else None,natural_exit=result.returncode,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory'/f'{report_name}.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(exit=result.returncode,run=str(run),native=report['native'],stderr=result.stderr.decode(errors='replace')[-4000:])))
    require(not result.returncode and report['native'] and report['native']['status']=='PASS' and len(frames)==5,'Nuclear registry native failure')
    return report


if __name__=='__main__':main()
