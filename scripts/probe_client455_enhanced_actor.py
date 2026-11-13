"""Real animated model A/B through current production draw, without server/login."""
import json
import shutil
import subprocess
from pathlib import Path
from compare_client_binaries import WS
from client455_asset_staging import sha, stage_asset, staging_stats
from client455_own_probe import build_full_object_probe
from probe_client455_shaders import inputs as shader_inputs


def record(path):
    return dict(file=path.relative_to(WS).as_posix(), sha256=sha(path))


def main():
    shaders, _, compiler = shader_inputs()
    reference_path = WS / 'inventory/client455-draw-reference.json'
    reference = json.loads(reference_path.read_text())
    if sha(WS / 'scripts/audit_client455_draw.py') != reference['script_sha256']:
        raise ValueError('Changed real model reference audit')
    source = WS / 'scripts/native/client455_enhanced_actor_probe.cpp'
    exe = build_full_object_probe('enhanced-actor', source)
    run = WS / 'work/enhanced-actor455' / sha(exe)[:12]
    run.mkdir(parents=True, exist_ok=True)
    target = run / exe.name
    shutil.copyfile(exe, target)
    inputs = []
    for row in shaders['programs']:
        path = run / 'System/shader' / (row['name'] + '.sho')
        stage_asset(WS / row['copy'], path, expected=row['sha256'])
        inputs.append(record(path))
    paths = []
    for row in reference['files']:
        path = run / 'model' / Path(row['path']).name
        stage_asset(WS / row['path'], path, expected=row['sha256'])
        paths.append(path)
        inputs.append(record(path))
    for row in reference['textures']:
        path = run / 'tex' / Path(row['copy']).name
        stage_asset(WS / row['copy'], path, expected=row['sha256'])
        inputs.append(record(path))
    original_fixture = WS / reference['fixture']
    if sha(original_fixture) != reference['fixture_sha256']:
        raise ValueError('Changed real model fixture')
    fixture = run / 'model.txt'
    by_name = {p.name.lower(): p for p in paths}
    fixture.write_text('\n'.join(str(by_name[Path(line).name.lower()])
                                  for line in original_fixture.read_text().splitlines()) + '\n')
    (run / 'R3Engine.ini').write_text('[RenderState]\nScreenXSize=1920\nScreenYSize=1080\n'
                                    'bFullScreen=FALSE\nEnhancedActorLighting=0\n')
    output = run / 'result.json'
    if output.exists():
        output.unlink()
    result = subprocess.run([str(target), str(compiler), str(fixture)], cwd=run,
                            capture_output=True, timeout=60, creationflags=subprocess.CREATE_NO_WINDOW)
    console = run / 'console.txt'
    console.write_bytes(result.stdout + result.stderr)
    native = json.loads(output.read_text()) if output.exists() else None
    frames = [record(p) for p in sorted(run.glob('actor-*.png'))]
    report = dict(status='PASS' if result.returncode == 0 and native and native.get('status') == 'PASS' else 'FAIL',
                  scope='Real model + original textures/ANI through production loading/pose/draw in controlled perspective scene; no live world',
                  source=record(source), included_source=record(WS / 'scripts/native/test_client455_draw.cpp'),
                  runner=record(Path(__file__)), executable=record(target), fixture=record(fixture),
                  reference=record(reference_path), inputs=inputs, native=native,
                  output=record(output) if output.exists() else None,
                  parts=record(run / 'parts.json') if (run / 'parts.json').exists() else None,
                  frames=frames, console=record(console), exit=result.returncode,
                  normal_executable=json.loads((WS / 'inventory/client455-normal-link.json').read_text())['executable'],
                  shared_staging=staging_stats(), server_modified=False, authentication_performed=False,
                  user_session_touched=False, live_world_verified=False)
    (WS / 'inventory/client455-enhanced-actor.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(status=report['status'], native=native, run=str(run), console=console.read_text(errors='replace')[-1000:])))
    if report['status'] != 'PASS':
        raise RuntimeError('Real actor A/B failed; see inventory/client455-enhanced-actor.json')


if __name__ == '__main__':
    main()
