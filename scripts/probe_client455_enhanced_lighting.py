"""Full HD shader/actor-route component checks; never authenticates or launches an input EXE."""
import json
import shutil
import subprocess
from pathlib import Path

from compare_client_binaries import WS
from client455_asset_staging import sha, stage_asset, staging_stats
from client455_own_probe import build_full_object_probe
from probe_client455_shaders import inputs as shader_inputs


def record(path):
    path = Path(path)
    return dict(file=path.relative_to(WS).as_posix(), sha256=sha(path))


def main():
    reference, _, compiler = shader_inputs()
    source = WS / 'scripts/native/client455_enhanced_lighting_probe.cpp'
    executable = build_full_object_probe('enhanced-lighting', source)
    run = WS / 'work/enhanced-lighting455' / sha(executable)[:12]
    run.mkdir(parents=True, exist_ok=True)
    target = run / executable.name
    shutil.copyfile(executable, target)
    inputs = []
    for program in reference['programs']:
        destination = run / 'System/shader' / (program['name'] + '.sho')
        stage_asset(WS / program['copy'], destination, expected=program['sha256'])
        inputs.append(record(destination))
    settings = run / 'R3Engine.ini'
    settings.write_text('[RenderState]\nScreenXSize=1920\nScreenYSize=1080\n'
                        'bFullScreen=FALSE\nEnhancedActorLighting=0\n', encoding='ascii')
    output = run / 'result.json'
    if output.exists():
        output.unlink()
    result = subprocess.run([str(target), str(compiler)], cwd=run, capture_output=True,
                            timeout=60, creationflags=subprocess.CREATE_NO_WINDOW)
    console = run / 'console.txt'
    console.write_bytes(result.stdout + result.stderr)
    if result.returncode or not output.exists():
        raise RuntimeError(f'Enhanced lighting exit {result.returncode}: {run}: '
                           f'{console.read_text(errors="replace")}')
    native = json.loads(output.read_text())
    if native.get('status') != 'PASS' or native.get('resolution') != [1920, 1080]:
        raise RuntimeError('Enhanced lighting did not pass at Full HD')
    frames = [record(run / name) for name in ['classic.png', 'enhanced-basic.png',
                                             'enhanced-masked-specular.png', 'route-classic.png',
                                             'route-enhanced.png']]
    report = dict(status='PASS', scope=native['scope'], resolution=[1920, 1080],
                  executable=record(target), source=record(source), runner=record(Path(__file__)),
                  sources=[record(WS / 'scripts/native' / name) for name in
                           ['client455_enhanced_lighting.h', 'client455_enhanced_lighting.inc',
                            'client455_enhanced_lighting_shader.h', 'client455_character_draw.cpp']],
                  normal_executable=json.loads((WS / 'inventory/client455-normal-link.json').read_text())['executable'],
                  shader_reference=record(WS / 'inventory/client455-shaders-reference.json'),
                  shader_build=record(WS / 'inventory/client455-shaders-build.json'),
                  compiler_sha256=sha(compiler), inputs=inputs, frames=frames,
                  result=record(output), native=native, console=record(console),
                  shared_staging=staging_stats(), user_session_touched=False,
                  authentication_performed=False, server_modified=False,
                  live_actor_verified=False, visible_scene_verified=False)
    (WS / 'inventory/client455-enhanced-lighting.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(status='PASS', native=native, run=run.relative_to(WS).as_posix())))


if __name__ == '__main__':
    main()
