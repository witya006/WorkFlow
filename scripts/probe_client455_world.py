"""Probe real source world loading on staged client455 maps,never input EXEs."""
import argparse,hashlib,json,shutil,subprocess,os
from pathlib import Path
from PIL import Image
from client455_own_probe import build_full_object_probe
from compare_client_binaries import WS,pe

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--race',choices=['bellato','cora','accretia'],default='bellato');args=parser.parse_args()
    source=WS/'scripts/native/client455_world_probe.cpp';exe=build_full_object_probe('world',source)
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);inputs=WS/'work/world455-inputs';inputs.mkdir(parents=True,exist_ok=True);records=[]
    roots=[client/'Map/Entity',client/f'Map/{args.race}']
    for root in roots:
        for path in sorted(root.rglob('*')):
            if not path.is_file():continue
            relative=path.relative_to(client);destination=inputs/relative;destination.parent.mkdir(parents=True,exist_ok=True);digest=sha(path)
            if destination.exists():
                if sha(destination)!=digest:raise ValueError('Preserving differing staged world input:'+str(destination))
            else:shutil.copyfile(path,destination)
            records.append({'file':destination.relative_to(WS).as_posix(),'sha256':digest,'bytes':path.stat().st_size})
    holder=WS/'work/m9'/sha(exe)[:8];holder.mkdir(parents=True,exist_ok=True);index=1
    while (holder/f'world-{args.race}-{index:03d}').exists():index+=1
    run=holder/f'world-{args.race}-{index:03d}';run.mkdir();target=run/exe.name;shutil.copyfile(exe,target);mapping=target.with_suffix('.map');shutil.copyfile(exe.with_suffix('.map'),mapping)
    for row in records:
        staged=WS/row['file'];destination=run/staged.relative_to(inputs);destination.parent.mkdir(parents=True,exist_ok=True)
        # Reuse copies already under work/,never hardlink the original client.
        os.link(staged,destination);row['file']=destination.relative_to(WS).as_posix()
    for name in ['System/shader/Grass1.vsh','System/shader/grass1.vso','System/console.jpg']:
        path=client/name;destination=run/name;destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,destination);records.append({'file':destination.relative_to(WS).as_posix(),'sha256':sha(destination)})
    config=run/'R3Engine.ini';config.write_text('[Setup]\nLanguage=Korea\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n[Sound]\nSound=FALSE\nMusic=FALSE\n',encoding='ascii');records.append({'file':config.relative_to(WS).as_posix(),'sha256':sha(config)})
    startup=subprocess.STARTUPINFO();startup.dwFlags=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
    result=subprocess.run([str(target),args.race],cwd=run,capture_output=True,timeout=90,creationflags=subprocess.CREATE_NO_WINDOW,startupinfo=startup)
    console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json';frames=[]
    if any(sha(WS/row['file'])!=row['sha256'] for row in records):raise ValueError('Staged world input changed during probe')
    for frame in run.glob('*.bgra'):
        preview=frame.with_suffix('.png');Image.frombytes('RGBA',(640,480),frame.read_bytes(),'raw','BGRA').convert('RGB').save(preview);frames.append({'file':frame.relative_to(WS).as_posix(),'sha256':sha(frame),'preview':preview.relative_to(WS).as_posix(),'preview_sha256':sha(preview)})
    report={'scope':'Real source CLand/CLevel/BSP39/EBP20 load/render/reload diagnostic,not fullILevel/Tutorial/game acceptance','race':args.race,'architecture':'x86','entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'source':source.relative_to(WS).as_posix(),'source_sha256':sha(source),'script_sha256':sha(Path(__file__)),'builder_sha256':sha(WS/'scripts/client455_own_probe.py'),'normal_link_sha256':sha(WS/'inventory/client455-normal-link.json'),'engine_report_sha256':sha(WS/'inventory/client455-startup-engine-build.json'),'exe':{'file':target.relative_to(WS).as_posix(),'sha256':sha(target)},'map':{'file':mapping.relative_to(WS).as_posix(),'sha256':sha(mapping)},'console':{'file':console.relative_to(WS).as_posix(),'sha256':sha(console)},'output':{'file':output.relative_to(WS).as_posix(),'sha256':sha(output)} if output.exists() else None,'inputs':records,'staged_inputs_unchanged':True,'frames':frames,'natural_exit':result.returncode,'native':json.loads(output.read_text()) if output.exists() else None,'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M9':'OPEN'}
    (WS/f'inventory/client455-world-{args.race}-native.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'race':args.race,'exit':result.returncode,'run':run.relative_to(WS).as_posix(),'native':report['native'],'console':result.stderr.decode(errors='replace')[-3000:]}))
    if result.returncode:raise SystemExit(result.returncode)
if __name__=='__main__':main()
