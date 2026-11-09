"""Check selected source lighting arithmetic against a rational x87 oracle."""
import argparse
import json
import shutil
import subprocess
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check, load, require, sha
from compare_client_binaries import WS, pe
from probe_client455_sky_fade import bits, number, ops, single

MASK = 0xffffffff


def packed(r, g, b):
    return (b | ((g | ((r | 0xffffff00) << 8)) << 8)) & MASK


def verify(trace):
    rows = [json.loads(x) for x in trace.read_text().splitlines()]
    counts = Counter(x['kind'] for x in rows)
    require(counts == dict(sun=36, fog=45, filter=24, divisor=24), '129 selected cases')
    require({(x['cw']>>8)&3 for x in rows} == {0, 2, 3}
            and all(x['cw'] & 0xc00 == 0 for x in rows), 'PC24/53/64 nearest/even')
    zero = 0
    for row in rows:
        r = ops(row['cw'])
        if row['kind'] == 'sun':
            rgb = list(map(number, row['rgb']))
            alpha = number(row['alpha'])
            rr, gg, bb = [int(r(x*255)) & MASK for x in rgb]
            old = row['fog']
            red = ((rr>>2)+((old>>18)&63)+128) | 0xffffff00
            green = (gg&0xfffffffc)+((old>>8)&252)+512
            blue = (bb>>2)+((old>>2)&63)+128
            require(row['tint'] == ((red<<16)|(green<<6)|blue)&MASK,
                    'Exact selected previous-fog tint packing')
            channels = [int(r(r(x*alpha)*255))&MASK for x in rgb]
            require(row['direct'] == packed(*channels), 'Exact selected Sun-alpha packing')
        elif row['kind'] == 'fog':
            w = number(row['weight'])
            complement = r(1-w)
            def mix(day, night):
                return r(r(night*w)+r(day*complement))
            for key, day, night in [('start', 3.125, 30.333334), ('end', 900.125, 7000.3335)]:
                expected = single(mix(number(bits(day)), number(bits(night))))
                require(row[key] == bits(expected), 'Exact fog endpoint float bits')
            channels = [int(mix(Q((row['day']>>s)&255), Q((row['night']>>s)&255)))&MASK
                        for s in [16, 8, 0]]
            require(row['color'] == packed(*channels), 'Exact weighted endpoint color')
        elif row['kind'] == 'filter':
            base, tint = row['base'], row['tint']
            expected = base & 0xff000000
            for shift in [0, 8, 16]:
                expected |= ((((base>>shift)&255)*((tint>>shift)&255))>>8)<<shift
            require(row['value'] == expected, 'Exact /256 color modulation and source alpha')
        else:
            scale = Q(.89999997615814208984375)
            factor = single(r(r(number(row['exposure'])*scale)+scale))
            count = Q(row['count'])
            if row['count'] & 0x80000000:
                count = r(Q(row['count']-0x100000000)+0x100000000)
            expected = int(r(count*factor)) & MASK
            require(row['value'] == expected, 'Exact unsigned sample count/factor spill/divisor')
            zero += expected == 0
    require(zero > 0, 'Zero divisor is exposed; no substitute fallback')
    return dict(status='PASS_COMPONENT', cases=len(rows), cases_by_kind=dict(counts),
                precision_bits=[24, 53, 64], exact_selected_bits=True,
                preserved_control_word=True, zero_divisors=zero,
                ordinary_runtime_integrated=False, full_lighting=False, all_FP_inputs=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify-existing', action='store_true')
    args = parser.parse_args()
    report_file = WS/'inventory/client455-sky-lighting-math-native.json'
    sources = [record(WS/'scripts/native'/name) for name in [
        'client455_sky_lighting_math_probe.cpp', 'client455_sky_lighting_math.h',
        'client455_sky_fade_math.h']]
    if args.verify_existing:
        report = json.loads(report_file.read_text())
        require(report['sources'] == sources, 'Current component sources')
        check(report['exe']); check(report['trace'])
        verdict = verify(WS/report['trace']['file'])
        require(verdict == report['verdict'], 'Reproduced rational oracle')
        print(json.dumps(verdict)); return
    info = load('msvc-verification')
    dev = Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    root = WS/'work/tools/sky-lighting-math127'
    root.mkdir(parents=True, exist_ok=True)
    exe, batch, log = root/'probe.exe', root/'build.cmd', root/'build.txt'
    source = WS/sources[0]['file']
    batch.write_text(f'@echo off\ncall "{dev}" -no_logo -arch=x86 -host_arch=x64 > "{root/"env.txt"}" 2>&1\nif errorlevel 1 exit /b 1\ncl /nologo /MT /O2 /EHsc /std:c++14 /W3 /I"{WS/"scripts/native"}" "{source}" /Fe"{exe}" /Fo"{root/"probe.obj"}" /link /SUBSYSTEM:CONSOLE > "{log}" 2>&1\nexit /b %errorlevel%\n', encoding='ascii')
    result = subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=root,
                            creationflags=subprocess.CREATE_NO_WINDOW)
    require(result.returncode == 0, 'Component build: '+str(log))
    parent = WS/'work/m9'/sha(exe)[:8]
    parent.mkdir(parents=True, exist_ok=True)
    index = 1
    while (parent/f'sky-lighting-math-{index:03d}').exists():
        index += 1
    run = parent/f'sky-lighting-math-{index:03d}'
    run.mkdir()
    target = run/'sky-lighting-math-probe.exe'
    shutil.copyfile(exe, target)
    staged_log = run/'build.txt'
    shutil.copyfile(log, staged_log)
    result = subprocess.run([str(target)], cwd=run, capture_output=True, timeout=15,
                            creationflags=subprocess.CREATE_NO_WINDOW)
    trace = run/'lighting-math.jsonl'
    trace.write_bytes(result.stdout)
    (run/'stderr.txt').write_bytes(result.stderr)
    require(result.returncode == 0, 'Completed component/control-word checks')
    verdict = verify(trace)
    require(pe(exe.read_bytes())['architecture'] == 'x86', 'Actual x86 component')
    engine, link = load('client455-startup-engine-build'), load('client455-normal-link')
    report = dict(scope='Selected lighting arithmetic source component;ordinary runtime remains126',
                  script_sha256=sha(Path(__file__)), sources=sources,
                  oracle=record(WS/'scripts/probe_client455_sky_fade.py'), exe=record(target),
                  trace=record(trace), build_log=record(staged_log), architecture='x86',
                  natural_exit=result.returncode, verdict=verdict,
                  engine=record(WS/engine['library']), normal_executable=link['executable'],
                  ordinary_runtime_integrated=False, input_exe_executed=False,
                  server_modified=False, M6='OPEN', M6F='OPEN', M7='OPEN', M9='OPEN')
    report_file.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(verdict))


if __name__ == '__main__':
    main()
