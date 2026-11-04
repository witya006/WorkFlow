"""Check actual x86 audio import names against the supplied 455 Miles DLL, statically."""
import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path

WS = Path(__file__).resolve().parents[1]


def main():
    verified = json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'))
    dumpbin = Path(verified['compiler_path'].splitlines()[0]).with_name('dumpbin.exe')
    obj = WS/'work/client-build/build-character-diagnostic/R3EngineClientMT.dir/Release/r3sound.obj'
    library = WS/'work/client-build/source/R3Engine/mss32.lib'
    paths = json.loads((WS/'config/paths.json').read_text(encoding='utf-8'))
    dll = Path(paths['client_455'])/'Snd/mss32.dll'
    symbols = subprocess.check_output([str(dumpbin), '/symbols', str(obj)]).decode('ascii', errors='replace')
    required = sorted({x[6:] for x in re.findall(r'UNDEF[^\r\n]*\| (__imp__AIL_[A-Za-z0-9_]+@\d+)', symbols)})
    if not required:
        raise ValueError('No actual audio imports found')
    exports = subprocess.check_output([str(dumpbin), '/exports', str(dll)]).decode('ascii', errors='replace')
    found = {name: (int(ordinal), int(rva, 16)) for ordinal, rva, name in
             re.findall(r'^\s*(\d+)\s+[0-9A-F]+\s+([0-9A-F]+)\s+(\S+)', exports, re.M)}
    missing = sorted(set(required)-found.keys())
    if missing:
        raise ValueError(f'Supplied 455 Miles DLL lacks imports: {missing}')
    raw = dll.read_bytes()
    pe = struct.unpack_from('<I', raw, 0x3c)[0]
    if struct.unpack_from('<H', raw, pe+4)[0] != 0x14c:
        raise ValueError('Expected x86 Miles DLL')
    report = {'source_library': library.relative_to(WS).as_posix(),
        'library_sha256': hashlib.sha256(library.read_bytes()).hexdigest(),
        'dll': str(dll), 'dll_sha256': hashlib.sha256(raw).hexdigest(), 'architecture': 'x86',
        'image_base': hex(struct.unpack_from('<I', raw, pe+24+28)[0]),
        'required_exports': [{'name': name, 'ordinal': found[name][0], 'rva': hex(found[name][1])} for name in required],
        'loaded_or_executed': False, 'limit': 'Names/architecture/stack decoration only; no audio behavior or full runtime ABI verified.'}
    (WS/'inventory/miles-link-audit.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(f'PASS: {len(required)} actual Miles import names exist in supplied x86 455 DLL.')


if __name__ == '__main__':
    main()
