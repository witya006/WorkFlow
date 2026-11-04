"""Apply exact ASCII byte edits to working client copies, preserving legacy encoding."""
import hashlib
import json
from pathlib import Path

WS = Path(__file__).resolve().parents[1]
PATCHES = {
    'RF_Client/addcodebyyun/protect.cpp': [(b'#include <Winable.h>', b'#include <windows.h>')],
    'R3Engine/1stclass/r3bsp.h': [(b'\tClearVariable();', b'\tvoid ClearVariable();')],
    'R3Engine/1stclass/bsp.cpp': [(b'CBsp::ClearVariable()', b'void CBsp::ClearVariable()')],
    'R3Engine/common/cjcache.cpp': [
        (b'\tint j=0;\r\n\r\n\tfor( JCache::iterator i = mCacheList.begin(); i != mCacheList.end(); i++,j++ )',
         b'\tint j=0;\r\n\tJCache::iterator i;\r\n\r\n\tfor( i = mCacheList.begin(); i != mCacheList.end(); i++,j++ )')],
    'R3Engine/common/r3profiler.cpp': [
        (b'\tfor(DWORD i=1; i<m_NowID; i++)', b'\tDWORD i;\r\n\tfor(i=1; i<m_NowID; i++)')],
    'R3Engine/common/commonutil.cpp': [
        (b'void StripPath(char *name)\r\n{\r\n\tchar r_name[256];\r\n\r\n\tfor(int i=',
         b'void StripPath(char *name)\r\n{\r\n\tchar r_name[256];\r\n\tint i;\r\n\r\n\tfor(i='),
        (b'void StripName(char *name)\r\n{\r\n\tfor(int i=',
         b'void StripName(char *name)\r\n{\r\n\tint i;\r\n\tfor(i=')]
}


def main():
    paths = json.loads((WS / 'config/paths.json').read_text(encoding='utf-8'))
    source_root = Path(paths['legacy_source']) / 'R3Engine'
    report = []
    for name, edits in PATCHES.items():
        original = (Path(paths['legacy_source']) / 'RF Client Side' / name) if name.startswith('RF_Client/') else source_root / name
        old = original.read_bytes()
        new = old
        for before, after in edits:
            newline = b'\r\n' if b'\r\n' in old else b'\n'
            before = before.replace(b'\r\n', newline)
            after = after.replace(b'\r\n', newline)
            if new.count(before) != 1:
                raise ValueError(f'Patch anchor not unique: {name}')
            new = new.replace(before, after, 1)
        dst = WS / 'work/client-build/source' / name
        if dst.read_bytes() not in (old, new):
            raise ValueError(f'Preserving unexpected local edits: {dst}')
        dst.write_bytes(new)
        report.append({'file': dst.relative_to(WS).as_posix(), 'original_sha256': hashlib.sha256(old).hexdigest(),
                       'patched_sha256': hashlib.sha256(new).hexdigest(), 'changes': len(edits),
                       'reason': ('Use current Windows API declarations instead of missing legacy Winable.h; no protection logic changed.' if name.endswith('protect.cpp') else
                                  'Explicit void ClearVariable return type; both in-tree callers discard its result.' if name.endswith(('r3bsp.h', 'bsp.cpp')) else
                                  'Restore VC6 function-scope loop variable lifetime in standard C++; no algorithm change.')})
    (WS / 'inventory/client-source-patches.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
