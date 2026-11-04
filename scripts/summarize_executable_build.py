"""Extract a compact client compilation status, without committing raw logs."""
import argparse
import collections
import json
import re
from datetime import datetime, timezone
from pathlib import Path

WS = Path(__file__).resolve().parents[1]


def unresolved_symbol(message):
    prefix = re.split(r' в функции | referenced in function | in function ', message, maxsplit=1)[0]
    decorated = re.search(r'\((\?[^ )]+)\)', prefix)
    if decorated:
        return decorated[1]
    raw = re.search(r'(?<!\w)(_[A-Za-z_][A-Za-z0-9_@]*)(?=[\s.,"()]|$)', prefix)
    return raw[1] if raw else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--build-exit', required=True, type=int)
    parser.add_argument('--log', default='artifacts/client-executable-build/build.txt')
    parser.add_argument('--build-dir', default='work/client-build/build-vs2026')
    parser.add_argument('--output', default='inventory/client-executable-build-result.json')
    parser.add_argument('--max-details', type=int, default=200)
    args = parser.parse_args()
    log = (WS / args.log).read_text(encoding='utf-8-sig', errors='replace')
    errors = []
    for line in log.splitlines():
        m = re.match(r'(.*?)\((\d+),(\d+)\): (?:fatal )?error ([A-Z]+\d+): (.*?) \[', line)
        if not m:
            link = re.match(r'(.*?): (?:fatal )?error (LNK\d+): (.*?) \[', line)
            if link:
                errors.append({'file': link[1], 'line': None, 'code': link[2], 'message': link[3]})
            continue
        p = Path(m[1])
        try:
            name = p.relative_to(WS).as_posix()
        except ValueError:
            name = str(p)
        errors.append({'file': name, 'line': int(m[2]), 'code': m[4], 'message': m[5]})
    groups = collections.Counter((x['file'], x['line'], x['code'], x['message']) for x in errors)
    cache = WS / args.build_dir / 'CMakeCache.txt'
    settings = {}
    if cache.exists():
        for line in cache.read_text(encoding='utf-8').splitlines():
            m = re.match(r'(RF_(?:RECOVERED_CHARACTER_INCLUDE|CHARACTER_STD_DIAGNOSTIC|LEGACY_NEW_UI|LEGACY_DX8_LIBRARY|JPEG_LIBRARY_DIR|CHARACTER_REFERENCE_LIBRARY|CHARACTER_STDIO_ADAPTER_LIBRARY|CHARACTER_RECOVERED_MANAGERS_LIBRARY|CHARACTER_EXCEPTIONS_LIBRARY|CHARACTER_SETTERS_LIBRARY|DIAGNOSTIC_DEFER_LIBRARIES)):[^=]+=(.*)', line)
            if m:
                settings[m[1]] = m[2]
    report = {'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'target': 'RF_Online',
              'platform': 'Win32', 'configuration': 'Release', 'build_exit': args.build_exit,
              'error_counts': dict(collections.Counter(x['code'] for x in errors)),
              'unresolved_symbols': sorted({symbol for x in errors if x['code'] in {'LNK2001', 'LNK2019'}
                                             if (symbol := unresolved_symbol(x['message']))}),
              'distinct_diagnostics_total': len(groups),
              'distinct_diagnostics': [dict(zip(['file', 'line', 'code', 'message', 'count'], [*key, count])) for key, count in list(groups.items())[:args.max_details]],
              'details_omitted': max(0, len(groups)-args.max_details),
              'generated_objects': len(list((WS / args.build_dir / 'RF_Online.dir/Release').glob('*.obj'))),
              'build_dir': args.build_dir, 'log': args.log,
              'build_settings': settings,
              'scope': 'Client-only compile diagnostic. No input EXE execution; compilation does not prove behavior.'}
    (WS / args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ['build_exit', 'error_counts', 'generated_objects']}, ensure_ascii=True))


if __name__ == '__main__':
    main()
