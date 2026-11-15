"""Compile the real RVP load model; compare all named fields on44 stock inputs."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from audit_client455_rvp import decode
from compare_client_binaries import WS, pe


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path):
    return dict(file=path.relative_to(WS).as_posix(), sha256=sha(path))


def main():
    ref_path = WS / 'inventory/client455-rvp-reference.json'
    ref = json.loads(ref_path.read_text())
    if ref['script_sha256'] != sha(WS / 'scripts/audit_client455_rvp.py'):
        raise ValueError('Refresh RVP reference audit')
    root = WS / 'work/client455-port/rvp-probe'
    root.mkdir(parents=True, exist_ok=True)
    native = WS / 'scripts/native'
    source, header = native / 'client455_rvp.cpp', native / 'client455_rvp.h'
    cache, cache_header = native / 'client455_character_rfs.cpp', native / 'client455_character_rfs.h'
    probe = native / 'client455_rvp_probe.cpp'
    obj, probe_obj, cache_obj = root / 'rvp.obj', root / 'probe.obj', root / 'character-rfs.obj'
    library, exe = root / 'RF455Rvp.lib', root / 'rvp-probe.exe'
    log, mapping = root / 'build.txt', exe.with_suffix('.map')
    info = json.loads((WS / 'inventory/msvc-verification.json').read_text())
    dev = Path(info['installation_path']) / 'Common7/Tools/VsDevCmd.bat'
    batch = root / 'build.cmd'
    lines = ['@echo off', f'call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1',
             'if errorlevel 1 exit /b 1',
             f'cl /c /nologo /MT /O2 /fp:strict /Gy /EHsc /std:c++14 /W4 /I"{native}" "{source}" /Fo"{obj}" > "{log}" 2>&1',
             'if errorlevel 1 exit /b 1',
             f'cl /c /nologo /MT /O2 /fp:strict /Gy /EHsc /std:c++14 /W4 /I"{native}" "{cache}" /Fo"{cache_obj}" >> "{log}" 2>&1',
             'if errorlevel 1 exit /b 1',
             f'lib /nologo /OUT:"{library}" "{obj}" "{cache_obj}" >> "{log}" 2>&1',
             'if errorlevel 1 exit /b 1',
             f'cl /c /nologo /MT /O2 /fp:strict /Gy /EHsc /std:c++14 /W4 /I"{native}" "{probe}" /Fo"{probe_obj}" >> "{log}" 2>&1',
             'if errorlevel 1 exit /b 1',
             f'link /nologo /SUBSYSTEM:CONSOLE /MACHINE:X86 /OUT:"{exe}" /MAP:"{mapping}" "{probe_obj}" "{library}" kernel32.lib >> "{log}" 2>&1',
             'exit /b %errorlevel%']
    batch.write_text('\n'.join(lines) + '\n', encoding='ascii')
    result = subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=root,
                            creationflags=subprocess.CREATE_NO_WINDOW, timeout=90)
    if result.returncode:
        raise ValueError('RVP native build: ' + str(log))
    holder = WS / 'work/m9' / sha(exe)[:8]
    holder.mkdir(parents=True, exist_ok=True)
    index = 1
    while (holder / f'rvp-{index:03d}').exists():
        index += 1
    run = holder / f'rvp-{index:03d}'
    run.mkdir()
    own = run / exe.name
    shutil.copyfile(exe, own)
    shutil.copyfile(mapping, own.with_suffix('.map'))
    inputs = []
    for row in ref['inputs']:
        original, path = Path(row['file']), run / row['relative']
        if sha(original) != row['sha256']:
            raise ValueError('Changed stock RVP')
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, path)
        inputs.append(path)
    fixture = run / 'all-commands.rvp'
    fixture.write_bytes(b'''IgnoredHeader\n[OBJECT]
*FIRST First.msh texpath tex bone first.bn mesh_id 3 color 255 129 1 collision shadow
ani first.ani ani second.ani scale 1.25 x_angle -90 y_angle 15 wav_dist 0 wav Ambient.wav
sword_trace Trace.txt trace_on_off 2 12 55
*second Second.msh bone second.bn
*magic 42 magic_id 0x1e8480 char_link *first char_dummy Bip01 map_dummy *Dummy
[PrepareTrack] total_frame 123.9 *first *Dummy wide logo no_camera screen camera *CAMERA01 fade_out 0
[Track] *frame 5 camera *Camera02 fade_in 30 fade_out 60 quake 2.5 4.5 blur .3 timer_rate .75
ani *first 1 char_fade_in *first 30 char_fade_out *first 90 magic 42
wav *Dummy Sound.wav 5000.0f throw 42 *Dummy throw 42 *first Bip01
*frame 3 blur .9
''')
    inputs.append(fixture)
    # Unknown tokens are scanned, not skipped as comment lines. DOS text EOF
    # prevents the final synthetic command from reaching the455 scanner.
    quirks = run / 'scanner-quirks.rvp'
    quirks.write_bytes(b'[PrepareTrack] ;comment wide _no_camera logo [Track] *frame 2 fade_in 17junk\x1ablur 1')
    inputs.append(quirks)
    (run / 'inputs.txt').write_text(''.join(path.relative_to(run).as_posix() + '\n' for path in inputs))
    result = subprocess.run([str(own)], cwd=run, capture_output=True, timeout=30,
                            creationflags=subprocess.CREATE_NO_WINDOW)
    console = run / 'console.txt'
    console.write_bytes(result.stdout + result.stderr)
    if result.returncode:
        raise ValueError('Native RVP probe: ' + str(console) + ': ' + result.stderr.decode(errors='replace'))
    outputs = []
    for path in inputs:
        expected = decode(path.read_bytes(), dummies=['Dummy'])
        output = Path(str(path) + '.semantic.json')
        actual = json.loads(output.read_text())
        if actual != expected:
            # Keep both representations to investigate; never stamp PASS over a mismatch.
            Path(str(path) + '.expected.json').write_text(json.dumps(expected, indent=2))
            raise ValueError('RVP named-field mismatch: ' + str(path))
        if path == fixture:
            if {row['kind'] for row in actual['tracks']} != {1, 2, 3, 5, 10, 11, 0x84, 0x86, 0x87, 0x88, 0x89, 0x8c}:
                raise ValueError('All twelve455 command kinds must be covered')
            if actual['flags'] != 15 or actual['totalFrame'] != 123 or actual['actors'][0]['color'] != 0xff7f4000:
                raise ValueError('Fixture flags/float-total-frame/color rules')
            if actual['actors'][2]['linkedActor'] != 0 or actual['tracks'][-1]['frame'] >= actual['tracks'][-2]['frame']:
                raise ValueError('Actor link/source track order was lost')
        if path == quirks and (actual['flags'] != 3 or len(actual['tracks']) != 1 or actual['tracks'][0]['value'] != 17):
            raise ValueError('fscanf scanner/prefix integer/DOS EOF rules')
        outputs.append(record(output))
    actual = json.loads((run / 'result.json').read_text())
    if not actual['malformed_transactional'] or not actual['cursor_interpolation'] or actual['full_RVP_player']:
        raise ValueError('Native RVP contract/scope mismatch')
    for row in ref['inputs']:
        if sha(Path(row['file'])) != row['sha256']:
            raise ValueError('Original RVP changed during probe')
    report = dict(scope='RVP load model, not a working RTMovie player or ordinary Tutorial',
                  script_sha256=sha(Path(__file__)), reference_sha256=sha(ref_path),
                  source=record(source), header=record(header), probe=record(probe),
                  camera_header=record(native / 'client455_camera.h'),
                  resource_cache_source=record(cache), resource_cache_header=record(cache_header),
                  library=library.relative_to(WS).as_posix(), library_sha256=sha(library),
                  executable=record(own), map=record(own.with_suffix('.map')), build_log=record(log),
                  inputs=[record(path) for path in inputs], outputs=outputs,
                  result=record(run / 'result.json'), console=record(console), native=actual,
                  natural_exit=result.returncode, independent_named_fields_equal=True,
                  all_twelve_command_kinds=True,
                  normal_client_relinked=False, normal_client_functionality_changed=False,
                  input_exe_executed=False, server_modified=False, M6='OPEN', M6F='OPEN', M9='OPEN')
    (WS / 'inventory/client455-rvp-native.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(run=run.relative_to(WS).as_posix(), native=actual)))


if __name__ == '__main__':
    main()
