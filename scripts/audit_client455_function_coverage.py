"""Inventory unique pinned client function evidence, not functional readiness."""
import hashlib
import json
import sys
import copy
from datetime import datetime, timezone
from pathlib import Path
from compare_client_binaries import WS, pe
from build_client455_x87_math import read_va


def walk(value, path=()):
    if isinstance(value, dict):
        yield path, value
        for key, child in value.items():
            yield from walk(child, (*path, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, (*path, index))


CODE_KEYS = {'functions', 'ranges', 'bodies', 'related_functions', 'tails',
             'external_assembly_windows', 'particle_fragments', 'transform_context_bytes',
             'EH_instruction_windows'}
OUT = WS/'artifacts/client455-progress/function-coverage'


def integer(value):
    return int(value, 0) if isinstance(value, str) else int(value)


def merge(spans):
    result = []
    for low, high in sorted(spans):
        if result and low <= result[-1][1]:
            result[-1][1] = max(high, result[-1][1])
        else:
            result.append([low, high])
    return result


def scan():
    pin = json.loads((WS/'config/client-target.json').read_text())['behavior_reference']
    primary = pin['sha256']
    binary = (WS/'work/client-reference/current/RF_Online.bin').read_bytes()
    assert hashlib.sha256(binary).hexdigest() == primary
    image = pe(binary)
    assert image['architecture'] == 'x86' and image['image_base'] == 0x400000
    text = next(s for s in image['sections'] if s['name'] == '.text')
    reports = []
    records = []
    linked = {}
    for file in sorted((WS/'inventory').glob('*.json')):
        if file.name == 'client455-function-coverage.json':
            continue
        document = json.loads(file.read_text(encoding='utf-8-sig'))
        found = False
        for pointer, node in walk(document):
            if node.get('sha256') != primary:
                continue
            assert node.get('architecture', 'x86') == 'x86'
            for key in sorted(CODE_KEYS & node.keys()):
                for function in node[key]:
                    if not isinstance(function, dict) or 'rva' not in function:
                        continue
                    owner = integer(function.get('owner_rva', function['rva']))
                    for region in function.get('regions', [function]):
                        rva = integer(region['rva'])
                        size = region.get('bytes', region.get('size'))
                        digest = region.get('sha256', region.get('reference_body_sha256', region.get('reference_code_sha256')))
                        if not isinstance(size, int) or size <= 0 or not digest:
                            continue
                        if not text['rva'] <= rva < rva+size <= text['rva']+text['raw_size']:
                            continue
                        actual = read_va(binary, 0x400000+rva, size)
                        assert hashlib.sha256(actual).hexdigest() == digest, (file.name, hex(rva))
                        records.append(dict(owner=hex(owner), rva=hex(rva), bytes=size,
                                            sha256=digest, report=file.relative_to(WS).as_posix(),
                                            pointer=list(pointer)+[key], prefix_only=bool(function.get('prefix_only'))))
                        found = True
        if found:
            reports.append(dict(file=file.relative_to(WS).as_posix(), sha256=hashlib.sha256(file.read_bytes()).hexdigest()))
            for _, node in walk(document):
                value = node.get('file')
                if isinstance(value, str) and value.startswith('artifacts/') and value.endswith('.json') and node.get('sha256'):
                    if value in linked:
                        assert linked[value] == node['sha256'], ('conflicting private proof', value)
                    linked[value] = node['sha256']
    OUT.mkdir(parents=True, exist_ok=True)
    discovery = dict(pin=primary, architecture='x86', image_base='0x400000', text=text,
                     reports=reports, records=records, linked=linked)
    (OUT/'discovery.json').write_text(json.dumps(discovery, indent=2)+'\n')
    candidates = sorted({integer(r['owner'])+0x400000 for r in records})
    (OUT/'queries.json').write_text(json.dumps([hex(a) for a in candidates])+'\n')
    print(json.dumps(dict(reports=len(reports), records=len(records), unique_queries=len(candidates), linked_json=len(linked))))


def complete_assembly(pages, cfg, covered):
    """Require full pagination and all positive CFG blocks in pinned code evidence."""
    assert pages and pages[-1]['cursor']['done']
    assert cfg['cursor']['done'] and cfg['count'] == cfg['total_blocks'] == len(cfg['blocks'])
    lines = [line for page in pages for line in page['asm']['lines']]
    starts = {int(line['addr'], 16) for line in lines}
    assert len(starts) == len(lines) == pages[0]['total_instructions'] > 0
    assert all(len(page['asm']['lines']) <= 100 for page in pages)
    blocks = [b for b in cfg['blocks'] if b['size'] > 0]
    assert blocks
    for block in blocks:
        low, high = int(block['start'], 16), int(block['end'], 16)
        assert high-low == block['size'] and low in starts
        assert any(a <= low < high <= b for a, b in covered)
    assert all(any(int(b['start'], 16) <= a < int(b['end'], 16) for b in blocks) for a in starts)
    return len(lines)


def assembly_groups(raw):
    """Conservative adapters for the two historical complete-CFG schemas."""
    bounds = raw.get('ranges', raw.get('bounds', {}))
    if not isinstance(bounds, dict) or 'result' not in bounds:
        return
    assembly = raw.get('asm', raw.get('assemblies', raw.get('assembly', {})))
    cfg = raw.get('cfg', {})
    cfg = cfg.get('result', []) if isinstance(cfg, dict) else cfg
    if not isinstance(cfg, list) or not cfg:
        return
    if isinstance(assembly, list):
        assembly = {row['addr']: row.get('pages', []) for row in assembly if isinstance(row, dict) and 'addr' in row}
    if not isinstance(assembly, dict):
        return
    for row in bounds['result']:
        if not row.get('fn') or row.get('error'):
            continue
        address = int(row['fn']['addr'], 16)
        query = row['query']
        pages = assembly.get(query, assembly.get(hex(address), []))
        block = next((x for x in cfg if int(x['addr'], 16) in {address, int(query, 16)}), None)
        if pages and block:
            yield address, pages, block


def report():
    discovery = json.loads((OUT/'discovery.json').read_text())
    for row in discovery['reports']:
        assert hashlib.sha256((WS/row['file']).read_bytes()).hexdigest() == row['sha256'], ('Rescan changed report',row['file'])
    lookups_file = OUT/'ida-lookups.json'
    lookups = json.loads(lookups_file.read_text())
    survey_file = OUT/'ida-survey.json'
    survey = json.loads(survey_file.read_text())
    assert lookups['primary_sha256'] == discovery['pin'] == survey['metadata']['sha256']
    assert survey['metadata']['arch'] == '32' and integer(survey['metadata']['base_address']) == 0x400000
    by_query = {int(row['query'], 16)-0x400000: row for row in lookups['result']}
    assert set(by_query) == {integer(row['owner']) for row in discovery['records']}
    functions = {}
    excluded = []
    spans = []
    for row in discovery['records']:
        lookup = by_query[integer(row['owner'])]
        if not lookup.get('fn') or lookup.get('error'):
            excluded.append(row)
            continue
        address = int(lookup['fn']['addr'], 16)
        function = functions.setdefault(address, dict(rva=hex(address-0x400000), ida_name=lookup['fn']['name'],
                                                     reports=set(), ranges=[], complete_assembly_evidence=[]))
        function['reports'].add(row['report'])
        span = (integer(row['rva'])+0x400000, integer(row['rva'])+0x400000+row['bytes'])
        function['ranges'].append(span)
        spans.append(span)
    covered = merge(spans)
    private_evidence = []
    not_counted = []
    for name, digest in discovery['linked'].items():
        file = WS/name
        if not file.is_file() or file.stat().st_size > 50_000_000:
            not_counted.append(dict(file=name, reason='missing or over50MB'))
            continue
        data = file.read_bytes()
        assert hashlib.sha256(data).hexdigest() == digest, name
        raw = json.loads(data)
        if not isinstance(raw, dict):
            continue
        used = False
        for address, pages, cfg in assembly_groups(raw):
            if address not in functions:
                continue
            try:
                count = complete_assembly(pages, cfg, covered)
            except (AssertionError, KeyError, TypeError):
                continue
            functions[address]['complete_assembly_evidence'].append(dict(file=name, instructions=count))
            used = True
        if used:
            private_evidence.append(dict(file=name, sha256=digest))
    rows = []
    for address, row in sorted(functions.items()):
        row['reports'] = sorted(row['reports'])
        row['ranges'] = [dict(rva=hex(a-0x400000), bytes=b-a) for a,b in merge(row['ranges'])]
        rows.append(row)
    summary = dict(unique_functions_with_pinned_code=len(rows),
                   unique_functions_with_complete_assembly_cfg=sum(bool(row['complete_assembly_evidence']) for row in rows),
                   unique_pinned_code_bytes=sum(b-a for a,b in covered),
                   reports=len(discovery['reports']), code_range_occurrences=len(discovery['records']),
                   unresolved_queries=len({row['owner'] for row in excluded}),
                   implementation_count=None, ordinary_runtime_equivalence_count=None)
    previous_file = WS/'inventory/client455-function-coverage.json'
    history_file = WS/'inventory/client455-function-history.json'
    history_document = json.loads(history_file.read_text()) if history_file.exists() else {'schema_version':1,'measurements':[]}
    history = history_document if isinstance(history_document,list) else history_document['measurements']
    previous = history[-1] if history else None
    now = datetime.now(timezone.utc).isoformat()
    if previous is None or previous['summary'] != summary:
        delta = None if previous is None else {key:summary[key]-previous['summary'][key] for key in ('unique_functions_with_pinned_code','unique_functions_with_complete_assembly_cfg')}
        history.append(dict(measured_at_utc=now, reference_sha256=discovery['pin'],
                            kind='BACKFILL_BASELINE' if previous is None else 'MEASUREMENT', summary=summary, delta=delta))
    history_file.write_text(json.dumps(dict(schema_version=1,measurements=history), indent=2)+'\n')
    out = dict(schema_version=1, measured_at_utc=now, status='EVIDENCE_BASELINE_NOT_READINESS',
               generator=dict(file=Path(__file__).relative_to(WS).as_posix(),sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),
               reference=dict(sha256=discovery['pin'], architecture='x86', image_base='0x400000'),
               ida_statistics=survey['statistics'], summary=summary,
               method=dict(identity='primary binary SHA256 plus current IDA function start RVA',
                           touched='Hash-verified named function bodies or code ranges resolved to their current IDA owner; may be partial/context only',
                           complete='Unique touched owners with full paginated disassembly and complete positive CFG, each block covered by hash-verified primary code ranges',
                           provenance='Existing tracked inventory reports only; linked private JSON checked against recorded hashes; no directory-wide raw dump counted',
                           not_measured=['Semantic understanding of every listed function', 'One-to-one current source implementations', 'Full equivalence per function', 'Time or effort remaining']),
               inventory_inputs=discovery['reports'], private_proofs=private_evidence,
               private_index=[dict(file=p.relative_to(WS).as_posix(), sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in (lookups_file,survey_file)],
               excluded_unresolved=sorted({row['owner'] for row in excluded}, key=integer),
               skipped_private=not_counted, functions=rows,
               last_recorded_delta=history[-1]['delta'],
               M6='OPEN', M9='OPEN', input_exe_executed=False, server_modified=False)
    previous_file.write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps(dict(summary=summary, index_functions=survey['statistics']['total_functions'], private_proofs=len(private_evidence)), indent=2))


def self_test():
    pages = [dict(asm=dict(lines=[dict(addr='400100'),dict(addr='400102')]),
                  total_instructions=2,cursor=dict(done=True))]
    cfg = dict(cursor=dict(done=True),count=1,total_blocks=1,
               blocks=[dict(start='0x400100',end='0x400105',size=5)])
    assert complete_assembly(pages,cfg,[(0x400100,0x400105)]) == 2
    for kind in ('pagination','duplicate','cfg_truncated','unhashed_tail'):
        p,c = copy.deepcopy(pages),copy.deepcopy(cfg)
        spans = [(0x400100,0x400105)]
        if kind == 'pagination':p[-1]['cursor']={'next':2}
        if kind == 'duplicate':p[0]['asm']['lines'][1]['addr']='400100'
        if kind == 'cfg_truncated':c['total_blocks']=2
        if kind == 'unhashed_tail':spans=[(0x400100,0x400104)]
        try:complete_assembly(p,c,spans)
        except (AssertionError,KeyError):pass
        else:raise AssertionError('Accepted incomplete evidence: '+kind)
    assert merge([(8,10),(1,4),(3,6),(6,8)]) == [[1,10]]
    raw=json.loads((WS/'artifacts/client455-progress/combat-transition156-reference/session.json').read_text())
    groups=list(assembly_groups(raw));assert len(groups)==3
    discovery=json.loads((OUT/'discovery.json').read_text())
    covered=merge([(integer(r['rva'])+0x400000,integer(r['rva'])+0x400000+r['bytes']) for r in discovery['records']])
    assert sum(complete_assembly(p,c,covered) for _,p,c in groups)==225
    print('PASS:deduplication,incomplete-evidence rejection and real transition156 proof')


def main():
    if '--self-test' in sys.argv:self_test()
    elif '--report' in sys.argv:report()
    else:scan()


if __name__ == '__main__':
    main()
