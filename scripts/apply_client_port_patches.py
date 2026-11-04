"""Apply exact ASCII byte edits to working client copies, preserving legacy encoding."""
import hashlib
import json
from pathlib import Path

WS = Path(__file__).resolve().parents[1]
PATCHES = {
    'RF_Client/network/cnetworkmgr.cpp': [],
    'RF_Client/character/character/ccharacter.cpp': [(b'static const MAX_PUSH_OUT_COUNT = 2;', b'static const int MAX_PUSH_OUT_COUNT = 2;')],
    'RF_Client/character/character/ccharacter_relationinfo2.cpp': [(b'static const LIMIT_DEAD_TIME = 2000;', b'static const int LIMIT_DEAD_TIME = 2000;')],
    'RF_Client/gameprogress/cgp_login.cpp': [(b'static endwav = true;', b'static int endwav = true;')],
    'RF_Client/network/cnetworkmgr_initmsg.cpp': [(b'static const EQUIP_ITEM_REQ_TIME = 5000;', b'static const int EQUIP_ITEM_REQ_TIME = 5000;')],
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
        if name == 'RF_Client/network/cnetworkmgr.cpp':
            start = old.index(b'\t\tcase item_msg :')
            end = old.index(b'\t\tcase map_msg :', start)
            block = old[start:end]
            if block.count(b'#endif') != 1 or b'#ifdef _NEW_UI_' not in block:
                raise ValueError('Unexpected legacy item dispatch guard')
            newline = b'\r\n' if b'\r\n' in old else b'\n'
            # The old switch already follows an unconditional break under _NEW_UI_.
            # Exclude it at preprocessing, preserving the existing live dispatch exactly.
            edits = [(block, block.replace(b'#endif', b'#else', 1)+b'#endif'+newline)]
        for before, after in edits:
            newline = b'\r\n' if b'\r\n' in old else b'\n'
            before = before.replace(b'\r\n', newline)
            after = after.replace(b'\r\n', newline)
            if new.count(before) != 1:
                raise ValueError(f'Patch anchor not unique: {name}')
            new = new.replace(before, after, 1)
        dst = WS / 'work/client-build/source' / name
        current = dst.read_bytes()
        if current not in (old, new):
            raise ValueError(f'Preserving unexpected local edits: {dst}')
        if current != new:
            dst.write_bytes(new)
        report.append({'file': dst.relative_to(WS).as_posix(), 'original_sha256': hashlib.sha256(old).hexdigest(),
                       'patched_sha256': hashlib.sha256(new).hexdigest(), 'changes': len(edits),
                       'reason': ('Use current Windows API declarations instead of missing legacy Winable.h; no protection logic changed.' if name.endswith('protect.cpp') else
                                  'Exclude already-unreachable old item dispatch in _NEW_UI_ builds; existing live routing is unchanged.' if name.endswith('cnetworkmgr.cpp') else
                                  'Make VC6 implicit-int static data declarations explicit; preserve int type and values.' if name.startswith('RF_Client/') else
                                  'Explicit void ClearVariable return type; both in-tree callers discard its result.' if name.endswith(('r3bsp.h', 'bsp.cpp')) else
                                  'Restore VC6 function-scope loop variable lifetime in standard C++; no algorithm change.')})
    (WS / 'inventory/client-source-patches.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
