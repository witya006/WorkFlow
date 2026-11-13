"""Bounded Windows private-font API check; no client build or visual acceptance."""
import ctypes
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from ctypes import wintypes

WS = Path(__file__).resolve().parents[1]
LAB = WS / 'work/font-private-check'
REPORT = WS / 'inventory/client455-private-font.json'
HELPER = r'''
import ctypes,json,sys
from ctypes import wintypes
gdi=ctypes.WinDLL('gdi32',use_last_error=True)
gdi.AddFontResourceExA.argtypes=[wintypes.LPCSTR,wintypes.DWORD,wintypes.LPVOID]
gdi.AddFontResourceExA.restype=ctypes.c_int
gdi.RemoveFontResourceExA.argtypes=[wintypes.LPCSTR,wintypes.DWORD,wintypes.LPVOID]
gdi.RemoveFontResourceExA.restype=wintypes.BOOL
path=sys.argv[1].encode('ascii')
count=gdi.AddFontResourceExA(path,0x10,None)
print(json.dumps(dict(added=count,error=ctypes.get_last_error())),flush=True)
if count<=0:sys.exit(2)
if sys.stdin.readline().strip()=='remove':
    removed=bool(gdi.RemoveFontResourceExA(path,0x10,None))
    print(json.dumps(dict(removed=removed,error=ctypes.get_last_error())),flush=True)
    sys.exit(0 if removed else 3)
sys.exit(4)
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def delete_access(path):
    """Open DELETE access without deleting, renaming or touching file contents."""
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                  wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    kernel.CreateFileW.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    handle = kernel.CreateFileW(str(path), 0x10000, 7, None, 3, 0, None)
    error = ctypes.get_last_error()
    valid = handle != ctypes.c_void_p(-1).value
    if valid:
        kernel.CloseHandle(handle)
    return dict(available=valid, error=0 if valid else error)


def main():
    if LAB.exists():
        raise RuntimeError('Preserving existing font-private-check directory')
    paths = json.loads((WS / 'config/paths.json').read_text())
    original = Path(paths['client_455']) / 'System/010.TTF'
    LAB.mkdir()
    font = LAB / '010.TTF'
    helper = LAB / 'font_helper.py'
    shutil.copyfile(original, font)
    helper.write_text(HELPER, encoding='ascii')
    report = dict(status='FAIL', scope='Windows Add/RemoveFontResourceExA FR_PRIVATE lifecycle API only; no client integration or visual check',
                  source=dict(file=str(original), sha256=sha(original)),
                  script_sha256=sha(Path(__file__)), helper_sha256=sha(helper),
                  production_font_sha256=sha(WS / 'scripts/native/client455_font.cpp'),
                  flags='FR_PRIVATE (0x10)', temporary_directory=str(LAB), cases=[])
    try:
        for forced in (False, True):
            child = subprocess.Popen([sys.executable, '-I', str(helper), str(font)], cwd=LAB,
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            case = dict(mode='TerminateProcess' if forced else 'matched_remove_and_exit')
            report['cases'].append(case)
            try:
                case['load'] = json.loads(child.stdout.readline())
                if case['load']['added'] <= 0:
                    raise RuntimeError('Font registration failed')
                case['delete_access_while_loaded'] = delete_access(font)
                if forced:
                    child.kill()  # Popen.kill uses TerminateProcess on Windows.
                    child.wait(timeout=15)
                else:
                    child.stdin.write('remove\n')
                    child.stdin.flush()
                    case['remove'] = json.loads(child.stdout.readline())
                    child.wait(timeout=15)
                    if not case['remove']['removed'] or child.returncode:
                        raise RuntimeError('Private font removal failed')
                case['exit_code'] = child.returncode
                case['delete_access_after_exit'] = delete_access(font)
                if not case['delete_access_after_exit']['available']:
                    raise RuntimeError('Font remains locked after child exit')
            finally:
                if child.poll() is None:
                    child.kill()
                    child.wait(timeout=15)
                for pipe in (child.stdin, child.stdout, child.stderr):
                    pipe.close()
        if sha(font) != report['source']['sha256']:
            raise RuntimeError('Copied font changed')
        report['status'] = 'PASS'
    finally:
        # Caller removes exactly the two owned files using native PowerShell.
        REPORT.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
