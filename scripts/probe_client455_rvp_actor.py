"""Execute the ordinary RVP actor path on real455 assets and D3D9."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
from PIL import Image
from client455_own_probe import build_full_object_probe
from client455_runtime_inputs import copy_character_shaders
from compare_client_binaries import WS

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    source=WS/'scripts/native/client455_rvp_actor_probe.cpp';exe=build_full_object_probe('rvp-actor',source)
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455'])
    holder=WS/'work/m9'/sha(exe)[:8];holder.mkdir(parents=True,exist_ok=True);index=1
    while(holder/f'rvp-actor-{index:03d}').exists():index+=1
    run=holder/f'rvp-actor-{index:03d}';run.mkdir();target=run/exe.name;shutil.copyfile(exe,target);shutil.copyfile(exe.with_suffix('.map'),target.with_suffix('.map'))
    records=[];staged=WS/'work/world455-inputs'
    files=set()
    for folder in ['Map/Entity','Map/neutralAS1','Chef/RealTime_00','Chef/Tex','Chef/Eff/Real']:
        files.update(p for p in (client/folder).rglob('*') if p.is_file())
    files.update(client/name for name in ['Chef/Real/unit.ini','Chef/Real/entity.ini','Chef/Real/particle.ini','System/shader/Grass1.vsh','System/shader/grass1.vso','System/console.jpg'])
    files.update((client/'Chef').glob('*.rpk'))
    for original in sorted(files):
        digest=sha(original);cached=staged/original.relative_to(client);cached.parent.mkdir(parents=True,exist_ok=True)
        if cached.exists():
            if sha(cached)!=digest:raise ValueError('Changed staged input')
        else:shutil.copyfile(original,cached)
        path=run/original.relative_to(client);path.parent.mkdir(parents=True,exist_ok=True);os.link(cached,path)
        records.append(dict(file=path.relative_to(WS).as_posix(),sha256=digest,original=str(original)))
    records+=copy_character_shaders(run)
    config=run/'R3Engine.ini';config.write_text('[Setup]\nLanguage=Korea\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n[Sound]\nSound=FALSE\nMusic=FALSE\n',encoding='ascii')
    records.append(dict(file=config.relative_to(WS).as_posix(),sha256=sha(config)))
    #Keep the stock scene independent. A separate two-actor fixture uses a
    #pinned real animated model and an actual CAM dummy,without the stock ships.
    draw=json.loads((WS/'inventory/client455-draw-reference.json').read_text())
    for row,name in zip(draw['files'],['animated.msh','animated.bn','animated.ani']):
        original=WS/row['path']
        if sha(original)!=row['sha256']:raise ValueError('Changed animation fixture asset')
        path=run/name;shutil.copyfile(original,path);records.append(dict(file=path.relative_to(WS).as_posix(),sha256=sha(path)))
    for row in draw['textures']:
        original=WS/row['copy'];path=run/'tex'/original.name;path.parent.mkdir(exist_ok=True)
        if sha(original)!=row['sha256']:raise ValueError('Changed animation texture')
        shutil.copyfile(original,path);records.append(dict(file=path.relative_to(WS).as_posix(),sha256=sha(path)))
    raw='[Object]\n'+''.join('*'+name+' .\\animated.msh\ntexpath .\\tex\nbone .\\animated.bn\nani .\\animated.ani\ncolor 255 255 255\n' for name in ['first','second'])
    raw+='[PrepareTrack]\n*first *Dummy01\n*second *Dummy01\nani *first 0\nani *second 0\ncamera *camera01\n[Track]\n*frame 1\ncamera *camera01\n*frame 75\nani *first 0\n'
    reset=run/'actor-reset.rvp';reset.write_text(raw,encoding='ascii')
    reset_cam=run/'actor-reset.cam';shutil.copyfile(client/'Map/neutralAS1/neutralAS1.cam',reset_cam)
    records.extend(dict(file=p.relative_to(WS).as_posix(),sha256=sha(p)) for p in [reset,reset_cam])
    console=run/'console.txt'
    with console.open('wb') as stream:
        result=subprocess.run([str(target)],cwd=run,stdout=stream,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
    output=run/'result.json';frames=[]
    for path in sorted(run.glob('*.bgra')):
        preview=path.with_suffix('.png');Image.frombytes('RGBA',(640,480),path.read_bytes(),'raw','BGRA').convert('RGB').save(preview)
        frames.append(dict(file=path.relative_to(WS).as_posix(),sha256=sha(path),preview=preview.relative_to(WS).as_posix(),preview_sha256=sha(preview)))
    def record(path):return dict(file=path.relative_to(WS).as_posix(),sha256=sha(path)) if path.exists() else None
    native=json.loads(output.read_text()) if output.exists() else None
    report=dict(scope='Actual ordinary RVP actors/realBN-MSH-ANI/pose snapshots/model draw/basic particle and entity passes/deferred FX release;full advanced FX/audio/Tutorial remain open',
        source=record(source),script_sha256=sha(Path(__file__)),builder_sha256=sha(WS/'scripts/client455_own_probe.py'),
        runtime_inputs_sha256=sha(WS/'scripts/client455_runtime_inputs.py'),normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),
        engine_report_sha256=sha(WS/'inventory/client455-startup-engine-build.json'),exe=record(target),map=record(target.with_suffix('.map')),
        console=record(console),output=record(output),trace=record(run/'actor-trace.jsonl'),inputs=records,frames=frames,
        natural_exit=result.returncode,native=native,input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    path=WS/'inventory/client455-rvp-actor-native.json';path.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(run=run.relative_to(WS).as_posix(),exit=result.returncode,native=native,stderr=console.read_text(errors='replace')[-2000:])))
    if result.returncode:raise SystemExit(result.returncode)
    if any(sha(WS/r['file'])!=r['sha256'] or ('original' in r and sha(Path(r['original']))!=r['sha256']) for r in records):raise ValueError('Input changed')
    report['inputs_unchanged']=True;path.write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
