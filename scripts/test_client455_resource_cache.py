"""Build/run only the resource-cache CPU component; never build or launch RF_Online."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    from workspace_guard import require_budget
    require_budget()
    build = ROOT / 'work/recovered/client455/resource-cache'
    evidence = ROOT / 'artifacts/resource-cache'
    build.mkdir(parents=True, exist_ok=True)
    evidence.mkdir(parents=True, exist_ok=True)
    report = evidence / 'component-check.json'
    report.write_text(json.dumps({'status': 'started', 'full_client_build': False,
                                 'game_launched': False}) + '\n', encoding='utf-8')
    client = ROOT / 'work/client455-port/normal/build/RF_Online.bin'
    before = digest(client)
    native = ROOT / 'scripts/native'
    names = ['client455_character_rfs.cpp', 'client455_character_rfs.h',
             'client455_shared_buffers.cpp', 'client455_shared_buffers.h',
             'client455_texture.cpp', 'client455_texture.h', 'client455_character_manager.cpp',
             'client455_effects.cpp', 'client455_effects.h',
             'client455_animation.cpp', 'client455_legacy_runtime.cpp',
             'client455_legacy_model.cpp', 'test_client455_resource_cache.cpp']
    source_hashes = {name: digest(native / name) for name in names}
    installation = json.loads((ROOT / 'inventory/msvc-verification.json').read_text(encoding='utf-8'))
    dev = Path(installation['installation_path']) / 'Common7/Tools/VsDevCmd.bat'
    sources = ' '.join('"' + str(native / name) + '"' for name in names if name.endswith('.cpp'))
    dependencies = {}
    for name in ('client455-models-build',
                 'client455-mesh-runtime', 'client455-mesh-bindings', 'client455-mesh08'):
        proof = json.loads((ROOT / 'inventory' / f'{name}.json').read_text(encoding='utf-8'))
        library = ROOT / proof['library']
        expected = proof['library_sha256']
        if digest(library) != expected:
            raise ValueError(f'Component dependency differs from its manifest: {library}')
        dependencies[library] = expected
    libraries = ' '.join(f'"{library}"' for library in dependencies)
    batch = build / 'build-component.cmd'
    batch.write_text(
        '@echo off\n'
        f'call "{dev}" -no_logo -arch=x86 -host_arch=x64 > environment.txt 2>&1\n'
        'if errorlevel 1 exit /b 1\n'
        f'cl /nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS '
        f'/I"{native}" {sources} {libraries} /Feresource-cache-test.exe /link /OPT:REF\n'
        'exit /b %errorlevel%\n', encoding='utf-8')
    compiled = subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=build,
                              capture_output=True, timeout=120,
                              creationflags=subprocess.CREATE_NO_WINDOW)
    (evidence / 'component-build.txt').write_bytes(compiled.stdout + compiled.stderr)
    result = {'scope': 'Standalone CPU resource-cache, MSH/BN/ANI readers, mocked textures and Character buffer migration',
              'full_client_build': False, 'game_launched': False, 'architecture': 'x86',
              'source_sha256': source_hashes, 'build_exit': compiled.returncode,
              'library_sha256': {path.relative_to(ROOT).as_posix(): sha for path, sha in dependencies.items()},
              'client_sha256_before': before}
    if compiled.returncode == 0:
        fixtures = build / 'fixtures'
        marker = fixtures / '.resource-cache-test-owned'
        if fixtures.exists():
            if (fixtures.resolve() != build / 'fixtures'
                    or not marker.is_file() or marker.read_text() != 'generated CPU fixtures\n'):
                raise RuntimeError('Refusing to remove an unrecognized fixture directory')
            # Only this exact generated subtree, never runtime or reference inputs.
            # Refuse junctions/symlinks anywhere below it before recursive removal.
            if any(p.is_symlink() or p.is_junction() for p in fixtures.rglob('*')):
                raise RuntimeError('Unexpected link in generated fixtures')
            shutil.rmtree(fixtures)
        fixtures.mkdir()
        marker.write_text('generated CPU fixtures\n')
        checked = subprocess.run([str(build / 'resource-cache-test.exe'), str(fixtures)],
                                 cwd=build, capture_output=True, timeout=30,
                                 creationflags=subprocess.CREATE_NO_WINDOW)
        (evidence / 'component-tests.txt').write_bytes(checked.stdout + checked.stderr)
        result.update(test_exit=checked.returncode,
                      output=checked.stdout.decode('utf-8', errors='replace').strip())
    result['client_sha256_after'] = digest(client)
    result['passed'] = (compiled.returncode == 0 and result.get('test_exit') == 0
                        and before == result['client_sha256_after'])
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))
    if not result['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
