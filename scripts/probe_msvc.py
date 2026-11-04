"""Discover VS and compile/run only our generated x86 Win32 smoke program.

No RF source or input executable is modified or executed. Logs stay in artifacts.
"""
import hashlib
import json
import os
import struct
import subprocess
from datetime import datetime, timezone
from pathlib import Path

WS = Path(__file__).resolve().parents[1]


def main():
    vswhere = Path(os.environ['ProgramFiles(x86)']) / 'Microsoft Visual Studio/Installer/vswhere.exe'
    found = json.loads(subprocess.check_output([str(vswhere), '-all', '-products', '*', '-format', 'json', '-utf8']).decode('utf-8-sig'))
    instance = next(x for x in found if x.get('isComplete') and x['productId'] == 'Microsoft.VisualStudio.Product.Professional')
    install = Path(instance['installationPath'])
    cmake = install / 'Common7/IDE/CommonExtensions/Microsoft/CMake/CMake/bin/cmake.exe'
    devcmd = install / 'Common7/Tools/VsDevCmd.bat'
    work = WS / 'work/msvc-smoke'
    logs = WS / 'artifacts/msvc-smoke'
    work.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)
    (work / 'smoke.cpp').write_text('''#include <windows.h>
#include <cstdio>
static_assert(sizeof(void*) == 4, "x86 target required");
int main() {
    if (!GetModuleHandleW(nullptr)) return 2;
    std::puts("RF toolchain smoke: x86 Win32 OK");
    return 0;
}
''', encoding='ascii')
    (work / 'CMakeLists.txt').write_text('''cmake_minimum_required(VERSION 3.20)
project(RFToolchainSmoke LANGUAGES CXX)
add_executable(rf_toolchain_smoke smoke.cpp)
target_compile_features(rf_toolchain_smoke PRIVATE cxx_std_17)
''', encoding='ascii')
    batch = work / 'probe.cmd'
    commands = [f'call "{devcmd}" -no_logo -arch=x86 -host_arch=x64 > "{logs / "devcmd.txt"}" 2>&1',
                f'where cl > "{logs / "cl-path.txt"}" 2>&1',
                f'cl /nologo /Bv /c smoke.cpp /Foversion-probe.obj > "{logs / "compiler.txt"}" 2>&1',
                f'"{cmake}" --version > "{logs / "cmake.txt"}" 2>&1',
                f'MSBuild.exe -version -nologo > "{logs / "msbuild.txt"}" 2>&1',
                f'(set VCToolsVersion & set WindowsSDKVersion & set WindowsSdkDir) > "{logs / "sdk.txt"}" 2>&1',
                f'"{cmake}" --fresh -S . -B build -G "Visual Studio 18 2026" -A Win32 > "{logs / "configure.txt"}" 2>&1',
                f'"{cmake}" --build build --config Release > "{logs / "build.txt"}" 2>&1',
                f'build\\Release\\rf_toolchain_smoke.exe > "{logs / "run.txt"}" 2>&1']
    batch.write_text('@echo off\n' + '\n'.join(c + '\nif errorlevel 1 exit /b 1' for c in commands) + '\nexit /b 0\n', encoding='ascii')
    run = subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=work, capture_output=True)
    def log(name):
        p = logs / name
        return p.read_bytes().decode('utf-8', errors='replace').strip() if p.exists() else None
    report = {'checked_at_utc': datetime.now(timezone.utc).isoformat(),
              'display_name': instance['displayName'], 'display_version': instance['catalog']['productDisplayVersion'],
              'installation_version': instance['installationVersion'], 'installation_path': str(install),
              'is_complete': instance['isComplete'], 'reboot_required': instance['isRebootRequired'],
              'exit_code': run.returncode, 'compiler_path': log('cl-path.txt'),
              'sdk_environment': log('sdk.txt'), 'cmake': log('cmake.txt'), 'msbuild': log('msbuild.txt'),
              'run_output': log('run.txt'), 'logs_directory': str(logs),
              'scope': 'Generated smoke program only; does not verify RF code, DirectX SDK or legacy library ABI.'}
    exe = work / 'build/Release/rf_toolchain_smoke.exe'
    if run.returncode == 0 and exe.is_file():
        data = exe.read_bytes()
        pe = struct.unpack_from('<I', data, 0x3c)[0]
        machine = struct.unpack_from('<H', data, pe + 4)[0]
        entry = struct.unpack_from('<I', data, pe + 24 + 16)[0]
        report['generated_executable'] = {'path': str(exe), 'sha256': hashlib.sha256(data).hexdigest(),
                                          'machine': hex(machine), 'architecture': 'x86' if machine == 0x14c else 'unexpected',
                                          'entry_point_rva': hex(entry)}
    (WS / 'inventory/msvc-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=True, indent=2))
    if run.returncode:
        for name in ['devcmd.txt', 'compiler.txt', 'configure.txt', 'build.txt']:
            print(name, (log(name) or '')[-3000:])
    return run.returncode


if __name__ == '__main__':
    raise SystemExit(main())
