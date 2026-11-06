"""Run ordinary CLevel->RTMovie against real455 maps and verify its track trace."""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path
from PIL import Image
from audit_client455_rvp import decode
from client455_own_probe import build_full_object_probe
from client455_runtime_inputs import copy_character_shaders
from compare_client_binaries import WS


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--race',choices=['bellato','cora','accretia'],default='bellato');race=parser.parse_args().race
    source=WS/'scripts/native/client455_rvp_runtime_probe.cpp';exe=build_full_object_probe('rvp-runtime',source)
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455'])
    holder=WS/'work/m9'/sha(exe)[:8];holder.mkdir(parents=True,exist_ok=True);index=1
    while(holder/f'rvp-runtime-{race}-{index:03d}').exists():index+=1
    run=holder/f'rvp-runtime-{race}-{index:03d}';run.mkdir();target=run/exe.name;shutil.copyfile(exe,target)
    mapping=target.with_suffix('.map');shutil.copyfile(exe.with_suffix('.map'),mapping);records=[]
    staged=WS/'work/world455-inputs'
    for folder in [client/'Map/Entity',client/f'Map/{race}']:
        for original in sorted(folder.rglob('*')):
            if not original.is_file():continue
            cached=staged/original.relative_to(client);cached.parent.mkdir(parents=True,exist_ok=True);digest=sha(original)
            if cached.exists():
                if sha(cached)!=digest:raise ValueError('Changed staged455 world')
            else:shutil.copyfile(original,cached)
            path=run/original.relative_to(client);path.parent.mkdir(parents=True,exist_ok=True);os.link(cached,path)
            records.append(dict(file=path.relative_to(WS).as_posix(),sha256=digest))
    for name in ['System/shader/Grass1.vsh','System/shader/grass1.vso','System/console.jpg']:
        path=run/name;path.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(client/name,path)
        records.append(dict(file=path.relative_to(WS).as_posix(),sha256=sha(path)))
    records+=copy_character_shaders(run)
    config=run/'R3Engine.ini';config.write_text('[Setup]\nLanguage=Korea\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n[Sound]\nSound=FALSE\nMusic=FALSE\n',encoding='ascii');records.append(dict(file=config.relative_to(WS).as_posix(),sha256=sha(config)))
    result=subprocess.run([str(target),race],cwd=run,capture_output=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
    console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json';trace=run/'rvp-trace.jsonl';frames=[]
    for path in sorted(run.glob('*.bgra')):
        preview=path.with_suffix('.png');Image.frombytes('RGBA',(640,480),path.read_bytes(),'raw','BGRA').convert('RGB').save(preview)
        frames.append(dict(file=path.relative_to(WS).as_posix(),sha256=sha(path),preview=preview.relative_to(WS).as_posix(),preview_sha256=sha(preview)))
    def record(path):return dict(file=path.relative_to(WS).as_posix(),sha256=sha(path)) if path.exists() else None
    native=json.loads(output.read_text()) if output.exists() else None
    report=dict(scope='Actual ordinary RVP camera/timeline/empty-list renderer path;actor/effect/audio/timer providers still open',
        race=race,source=record(source),script_sha256=sha(Path(__file__)),builder_sha256=sha(WS/'scripts/client455_own_probe.py'),
        runtime_inputs_sha256=sha(WS/'scripts/client455_runtime_inputs.py'),normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),
        engine_report_sha256=sha(WS/'inventory/client455-startup-engine-build.json'),
        exe=record(target),map=record(mapping),console=record(console),output=record(output),trace=record(trace),
        inputs=records,frames=frames,natural_exit=result.returncode,native=native,input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    path=WS/f'inventory/client455-rvp-runtime-{race}-native.json';path.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(run=run.relative_to(WS).as_posix(),exit=result.returncode,native=native,stderr=result.stderr.decode(errors='replace')[-1800:])))
    if result.returncode:raise SystemExit(result.returncode)
    expected=decode((client/f'Map/{race}/{race}.rvp').read_bytes())
    for kind,field in [(1,'selected'),(2,'fade_ins'),(3,'fade_outs')]:
        if sum(row['kind']==kind for row in expected['tracks'])!=native[field]:raise ValueError('Ordinary RVP event count mismatch: '+field)
    rows=[json.loads(line) for line in trace.read_text().splitlines()]
    if len(rows)!=native['ticks'] or rows[-1]['playing'] or native['warnings'] or native['memory_before']!=native['memory_after']:raise ValueError('RVP trace/warnings/ownership failure')
    if any(sha(WS/row['file'])!=row['sha256'] for row in records):raise ValueError('RVP input mutated')
    report['independent_event_counts_equal']=True;report['inputs_unchanged']=True;path.write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
