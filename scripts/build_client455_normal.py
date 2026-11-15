"""Compile real normal 455 consumer and library targets; record the actual outputs."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

from compare_client_binaries import WS
from client455_ninja_msvc import ninja_has_header, prepare_ninja_dependencies


NINJA = 'Ninja'
VISUAL_STUDIO = 'Visual Studio 18 2026'
TARGETS = ('RFClient455Consumers', 'RFClient455Facade', 'RFClient455Kernels')
EXPECTED_CONSUMERS = 182


def normal_build_directory(root, report):
    generator = report.get('generator', VISUAL_STUDIO)
    if generator not in (NINJA, VISUAL_STUDIO):
        raise ValueError(f'Unexpected normal build generator: {generator}')
    build = root / ('ninja-build' if generator == NINJA else 'build')
    recorded = report.get('build_directory')
    if recorded is not None and WS / recorded != build:
        raise ValueError(f'Normal build directory does not match {generator}: {recorded}')
    return build


def _object_directory(build, generator, target):
    if generator == NINJA:
        return build / 'CMakeFiles' / f'{target}.dir'
    return build / f'{target}.dir' / 'Release'


def _objects(directory, generator):
    paths = directory.rglob('*.obj') if generator == NINJA else directory.glob('*.obj')
    return sorted((path for path in paths if path.is_file()), key=lambda path: (path.name, path))


def _library_paths(build, generator):
    library_dir = build if generator == NINJA else build / 'Release'
    return [library_dir / f'{target}.lib' for target in TARGETS[1:]]


def _file_records(paths):
    return [{'file': path.relative_to(WS).as_posix(),
             'sha256': hashlib.sha256(path.read_bytes()).hexdigest()} for path in paths]


def _verify_files(paths, report, field):
    if any(not path.is_file() for path in paths):
        raise ValueError(f'Missing normal build files for {field}')
    recorded = report.get(field)
    if recorded is None:
        if report.get('generator') == NINJA:
            raise ValueError(f'Ninja build receipt lacks {field}')
    elif _file_records(paths) != recorded:
        raise ValueError(f'Current normal build files differ from {field}')


def normal_consumer_objects(root, report, split_names=()):
    build = normal_build_directory(root, report)
    generator = report.get('generator', VISUAL_STUDIO)
    directory = _object_directory(build, generator, TARGETS[0])
    objects = _objects(directory, generator)
    if len(objects) != report['objects']:
        raise ValueError('Current normal consumer object count differs from the build receipt')
    _verify_files(objects, report, 'consumer_object_files')
    if not split_names:
        return objects
    if generator == NINJA:
        selected = [directory / 'generated' / f'{name}.cpp.obj' for name in split_names]
    else:
        selected = [directory / f'{name}.obj' for name in split_names]
    if any(path not in objects for path in selected):
        raise ValueError('Missing compiled normal consumer split')
    return selected


def normal_build_libraries(root, report):
    build = normal_build_directory(root, report)
    libraries = _library_paths(build, report.get('generator', VISUAL_STUDIO))
    _verify_files(libraries, report, 'library_files')
    return libraries


def _compiler_errors(raw, returncode):
    errors = []
    lines = raw.decode('utf-8-sig', errors='replace').splitlines()
    for line in lines:
        match = re.match(r'(.*?)\((\d+)(?:,\d+)?\): (?:fatal )?error ([A-Z]+\d+): (.*?)'
                         r'(?: \[[^\]]+\.vcxproj\])?$', line)
        if match:
            path = Path(match[1])
            file = path.relative_to(WS).as_posix() if path.is_relative_to(WS) else str(path)
            errors.append({'file': file, 'line': int(match[2]), 'code': match[3], 'message': match[4]})
        elif line.startswith('cl:'):
            match = re.search(r'error (D\d+): (.*)', line)
            if match:
                errors.append({'file': '', 'line': 0, 'code': match[1], 'message': match[2]})
    if returncode and not errors:
        errors.append({'file': '', 'line': 0, 'code': 'BUILD',
                       'message': lines[-1] if lines else f'Build exited with code {returncode}'})
    return list({tuple(row.values()): row for row in errors}.values())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--clean-first', action='store_true',
                        help='Recompile client objects from retained source and pinned dependencies')
    parser.add_argument('--ninja', action='store_true',
                        help='Use bundled Ninja from a VS 2026 x86 developer shell')
    args = parser.parse_args()
    from workspace_guard import require_budget
    require_budget()

    root = WS / 'work/client455-port/normal'
    art = WS / 'artifacts/client455-normal'
    info = json.loads((WS / 'inventory/msvc-verification.json').read_text())
    tools = Path(info['installation_path']) / 'Common7/IDE/CommonExtensions/Microsoft/CMake'
    cmake = tools / 'CMake/bin/cmake.exe'
    ninja = tools / 'Ninja/ninja.exe'
    generator = NINJA if args.ninja else VISUAL_STUDIO
    build = normal_build_directory(root, {'generator': generator})
    prefix = 'ninja-' if args.ninja else ''
    if args.ninja:
        compiler = shutil.which('cl.exe')
        if os.environ.get('VSCMD_ARG_TGT_ARCH', '').lower() != 'x86' or not compiler:
            parser.error('--ninja requires a VS 2026 x86 developer shell (cl.exe on PATH)')
        options = ['-DCMAKE_BUILD_TYPE=Release',
                   f'-DCMAKE_MAKE_PROGRAM={ninja}', '-DCMAKE_SUPPRESS_REGENERATION=ON']
    else:
        options = ['-A', 'Win32', '-T', 'v145', '-DCMAKE_SYSTEM_VERSION=10.0.26100.0']

    configure_log = art / f'{prefix}configure.txt'
    config = subprocess.run([str(cmake), '-S', str(root), '-B', str(build), '-G', generator, *options],
                            capture_output=True, timeout=120, creationflags=subprocess.CREATE_NO_WINDOW)
    configure_log.write_bytes(config.stdout + config.stderr)
    if config.returncode:
        raise ValueError(f'Normal 455 configure failed ({generator}): {configure_log}')
    receipt = WS / 'inventory/client455-normal-build.json'
    clean_first = args.clean_first
    if args.ninja:
        cache = (build / 'CMakeCache.txt').read_text(encoding='utf-8')
        if not re.search(r'^CMAKE_BUILD_TYPE:[^=]+=Release$', cache, re.MULTILINE):
            raise ValueError(f'Ninja configure lost the required Release build type: {configure_log}')
        previous = json.loads(receipt.read_text(encoding='utf-8')) if receipt.is_file() else {}
        object_file = (_object_directory(build, generator, TARGETS[0]) /
                       'source/cland.cpp.obj').relative_to(build).as_posix()
        header = 'client455_scene_input.h'
        ninja_dependencies, recover = prepare_ninja_dependencies(ninja, build, previous, object_file, header)
        clean_first = clean_first or recover

    started = time.monotonic()
    command = [str(cmake), '--build', str(build), '--config', 'Release', '--target', *TARGETS, '--parallel', '4']
    if clean_first:
        command.append('--clean-first')
    run = subprocess.run(command, capture_output=True, timeout=300, creationflags=subprocess.CREATE_NO_WINDOW)
    raw = run.stdout + run.stderr
    log = art / f'{prefix}build.txt'
    log.write_bytes(raw)
    errors = _compiler_errors(raw, run.returncode)
    objects = _objects(_object_directory(build, generator, TARGETS[0]), generator)
    kernels = _objects(_object_directory(build, generator, TARGETS[2]), generator)
    libraries = _library_paths(build, generator)
    preparation = json.loads((WS / 'inventory/client455-normal-preparation.json').read_text())
    expected_kernels = len(preparation['canonical_kernel_sources'])

    exit_code = run.returncode
    if not exit_code and args.ninja and not ninja_has_header(ninja, build, object_file, header):
        exit_code = 1
        errors.append({'file': object_file, 'line': 0, 'code': 'NINJA_DEPS',
                       'message': f'Ninja did not record {header} as a dependency'})
    if not exit_code and (len(objects) != EXPECTED_CONSUMERS or len(kernels) != expected_kernels or
                          any(not path.is_file() for path in libraries)):
        exit_code = 1
        errors.append({'file': build.relative_to(WS).as_posix(), 'line': 0, 'code': 'OUTPUT',
                       'message': 'Incomplete normal consumer, canonical kernel, or static library outputs'})

    report = {
        'scope': 'Real normal455consumer compilation,not successful executable link/runtime acceptance',
        'generator': generator,
        'build_directory': build.relative_to(WS).as_posix(),
        'build_exit': exit_code,
        'command_exit': run.returncode,
        'original_sources': 180,
        'expected_sources': EXPECTED_CONSUMERS,
        'objects': len(objects),
        'errors': errors,
        'log': log.relative_to(WS).as_posix(),
        'log_sha256': hashlib.sha256(raw).hexdigest(),
        'source_manifest_sha256': hashlib.sha256((art / 'sources.json').read_bytes()).hexdigest(),
        'legacy_character_linked': False,
        'M6': 'OPEN',
        'M9': 'OPEN',
        'clean_first': clean_first,
        'build_seconds': round(time.monotonic() - started, 2),
        'canonical_kernel_objects': len(kernels),
        'expected_kernel_sources': expected_kernels,
    }
    if not exit_code:
        if args.ninja:
            report['ninja_dependencies'] = ninja_dependencies
        report['consumer_object_files'] = _file_records(objects)
        report['library_files'] = _file_records(libraries)
    receipt.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'exit': exit_code, 'objects': len(objects), 'canonical_kernels': len(kernels),
                      'errors': len(errors)}))
    print(json.dumps(errors[:12], ensure_ascii=False))
    if exit_code:
        raise SystemExit(exit_code)


if __name__ == '__main__':
    main()
