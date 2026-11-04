"""Extract demangled public contracts from the supplied library; no header guesses."""
import ctypes
from ctypes import wintypes
import hashlib
import json
import re
import subprocess
from pathlib import Path

WS = Path(__file__).resolve().parents[1]


def main():
    verified = json.loads((WS / 'inventory/msvc-verification.json').read_text(encoding='utf-8'))
    dumpbin = Path(verified['compiler_path'].splitlines()[0]).with_name('dumpbin.exe')
    library = WS / 'work/client-build/source/RF_Client/CharacterMR.lib'
    result = subprocess.check_output([str(dumpbin), '/linkermember:2', str(library)])
    names = re.findall(rb'^\s+[0-9A-F]+ (\?[^\r\n]+)', result, re.M)
    undecorate = ctypes.WinDLL('Dbghelp.dll').UnDecorateSymbolName
    undecorate.argtypes = [ctypes.c_char_p, ctypes.c_char_p, wintypes.DWORD, wintypes.DWORD]
    undecorate.restype = wintypes.DWORD
    entries = []
    for name in names:
        if b'?$' in name or b'@std@@' in name:
            continue
        buf = ctypes.create_string_buffer(8192)
        if not undecorate(name, buf, len(buf), 0):
            raise ValueError(f'Could not demangle {name!r}')
        entries.append({'mangled': name.decode('ascii'), 'declaration': buf.value.decode('ascii')})
    report = {'library_sha256': hashlib.sha256(library.read_bytes()).hexdigest(), 'architecture': 'x86', 'rva': None,
              'source': 'Public symbol index, Microsoft dumpbin + DbgHelp demangler',
              'limit': 'Declarations only, no class layouts or implementations inferred. Not a replacement Character.h.',
              'contracts': entries}
    (WS / 'inventory/character-public-contracts.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print('Non-STL public contracts:', len(entries))
    for entry in entries:
        if 'ChInterface::' in entry['declaration']:
            print(entry['declaration'])


if __name__ == '__main__':
    main()
