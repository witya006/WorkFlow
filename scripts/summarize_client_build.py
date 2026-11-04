"""Save a sanitized first-build result and verify staged input integrity."""
import argparse
import collections
import hashlib
import json
import re
import struct
from datetime import datetime, timezone
from pathlib import Path

WS = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--build-exit', type=int, required=True)
    args = parser.parse_args()
    manifest = json.loads((WS / 'inventory/client-build-inputs.json').read_text(encoding='utf-8'))
    original = Path(json.loads((WS / 'config/paths.json').read_text(encoding='utf-8'))['legacy_source'])
    issues = []
    patch_path = WS / 'inventory/client-source-patches.json'
    patches = {x['file']: x for x in json.loads(patch_path.read_text(encoding='utf-8'))} if patch_path.exists() else {}
    for f in manifest['files']:
        for kind, p in [('original', original / f['original']), ('copy', WS / f['copy'])]:
            expected = f['sha256']
            if kind == 'copy' and f['copy'] in patches:
                patch = patches[f['copy']]
                if patch['original_sha256'] != f['sha256']:
                    raise ValueError('Patch baseline does not match input inventory')
                expected = patch['patched_sha256']
            if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != expected:
                issues.append({'kind': kind, 'path': str(p)})
    log = (WS / 'artifacts/client-build/build.txt').read_text(encoding='utf-8-sig', errors='replace')
    diagnostics = []
    for line in log.splitlines():
        m = re.match(r'(.*?)\((\d+),(\d+)\): (?:fatal )?error ([A-Z]+\d+): (.*?) \[', line)
        if m:
            p = Path(m[1])
            try:
                display = p.relative_to(WS).as_posix()
            except ValueError:
                display = str(p)
            diagnostics.append({'file': display, 'line': int(m[2]),
                                'column': int(m[3]), 'code': m[4], 'message': m[5]})
    objects = []
    folder = WS / 'work/client-build/build-vs2026/R3Engine.dir/Release'
    for p in sorted(folder.glob('*.obj')):
        data = p.read_bytes()
        objects.append({'file': p.relative_to(WS).as_posix(), 'sha256': hashlib.sha256(data).hexdigest(),
                        'coff_machine': hex(struct.unpack_from('<H', data)[0]),
                        'rva': None, 'rva_note': 'Relocatable COFF object, no loaded image RVA.'})
    report = {'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'build_exit': args.build_exit,
              'target': 'R3Engine', 'platform': 'Win32', 'configuration': 'Release',
              'staged_files': len(manifest['files']), 'input_integrity_issues': issues,
              'error_counts': dict(collections.Counter(d['code'] for d in diagnostics)),
              'errors': diagnostics, 'generated_objects': objects,
              'scope': 'Client-engine work copies with inventoried patches; no server inputs or RF executable execution.'}
    library = WS / 'work/client-build/build-vs2026/lib/Release/R3Engine.lib'
    if args.build_exit == 0:
        data = library.read_bytes()
        if data[:8] != b'!<arch>\n' or len(objects) != 58 or any(x['coff_machine'] != '0x14c' for x in objects):
            raise ValueError('Unexpected library/archive or object architecture')
        report['library'] = {'file': library.relative_to(WS).as_posix(), 'sha256': hashlib.sha256(data).hexdigest(),
                             'size': len(data), 'architecture': 'x86 (58 verified COFF objects)', 'rva': None}
    (WS / 'inventory/client-build-result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ['build_exit', 'staged_files', 'input_integrity_issues', 'error_counts']}, ensure_ascii=True))
    print('Generated R3Engine objects:', len(objects))
    if issues:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
