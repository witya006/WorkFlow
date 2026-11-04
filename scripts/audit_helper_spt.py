import hashlib
import json
from pathlib import Path
from helper_spt import FormatError, encode, fingerprint, parse

WS = Path(__file__).resolve().parents[1]


def main():
    root = Path(json.loads((WS / 'config/paths.json').read_text(encoding='utf-8'))['client_455'])
    records = []
    for path in sorted((root / 'Map').rglob('*.spt')):
        data = path.read_bytes()
        if b'[HelperObjectBegin]' not in data:
            continue
        entry = {'path': path.relative_to(root).as_posix(), 'sha256': hashlib.sha256(data).hexdigest(), 'size': len(data)}
        try:
            helpers = parse(data)
            rebuilt = encode(helpers)
            if fingerprint(helpers) != fingerprint(parse(rebuilt)):
                raise FormatError('Semantic float32 round trip mismatch')
            entry.update({'helpers': len(helpers), 'round_trip': True,
                          'long_names': sum(len(h.name) > 31 for h in helpers)})
        except FormatError as exc:
            entry['error'] = str(exc)
        records.append(entry)
    report = {'format': 'Observed helper-only map SPT subset; not all .spt formats',
              'files': records, 'passed': sum(x.get('round_trip', False) for x in records),
              'total_helpers': sum(x.get('helpers', 0) for x in records)}
    (WS / 'inventory/helper-spt-verification.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'files': len(records), 'passed': report['passed'], 'helpers': report['total_helpers'],
                      'failures': [x for x in records if 'error' in x]}, indent=2))
    if not records or report['passed'] != len(records):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
