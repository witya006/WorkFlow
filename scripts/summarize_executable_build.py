"""Extract a compact client compilation status, without committing raw logs."""
import argparse
import collections
import json
import re
from datetime import datetime, timezone
from pathlib import Path

WS = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--build-exit', required=True, type=int)
    args = parser.parse_args()
    log = (WS / 'artifacts/client-executable-build/build.txt').read_text(encoding='utf-8-sig', errors='replace')
    errors = []
    for line in log.splitlines():
        m = re.match(r'(.*?)\((\d+),(\d+)\): (?:fatal )?error ([A-Z]+\d+): (.*?) \[', line)
        if not m:
            continue
        p = Path(m[1])
        try:
            name = p.relative_to(WS).as_posix()
        except ValueError:
            name = str(p)
        errors.append({'file': name, 'line': int(m[2]), 'code': m[4], 'message': m[5]})
    groups = collections.Counter((x['file'], x['line'], x['code'], x['message']) for x in errors)
    report = {'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'target': 'RF_Online',
              'platform': 'Win32', 'configuration': 'Release', 'build_exit': args.build_exit,
              'error_counts': dict(collections.Counter(x['code'] for x in errors)),
              'distinct_diagnostics': [dict(zip(['file', 'line', 'code', 'message', 'count'], [*key, count])) for key, count in groups.items()],
              'generated_objects': len(list((WS / 'work/client-build/build-vs2026/RF_Online.dir/Release').glob('*.obj'))),
              'scope': 'Client-only first full compile. No missing SDK replaced with stubs, no input EXE execution.'}
    (WS / 'inventory/client-executable-build-result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ['build_exit', 'error_counts', 'generated_objects']}, ensure_ascii=True))


if __name__ == '__main__':
    main()
