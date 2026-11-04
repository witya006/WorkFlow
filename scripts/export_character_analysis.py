"""Batch static decompilation of supplied Character objects via IDA MCP.

Raw analysis is saved only under ignored artifacts/. Every owned session is closed.
"""
import hashlib
import json
import struct
import tomllib
from datetime import datetime, timezone
from pathlib import Path
from mcp_stdio import StdioMCP

WS = Path(__file__).resolve().parents[1]


def coff_function_records(data):
    if len(data) < 20:
        raise ValueError('Truncated COFF header')
    machine, sections = struct.unpack_from('<HH', data)
    optional = struct.unpack_from('<H', data, 16)[0]
    if machine != 0x14c or optional or 20+40*sections > len(data):
        raise ValueError('Expected complete regular x86 COFF object')
    table, count = struct.unpack_from('<II', data, 8)
    strings = table+count*18
    if strings+4 > len(data):
        raise ValueError('Truncated COFF symbol table')
    string_size = struct.unpack_from('<I', data, strings)[0]
    if string_size < 4 or strings+string_size > len(data):
        raise ValueError('Truncated COFF string table')
    found = {}
    index = 0
    while index < count:
        at = table+index*18
        section, kind, storage, auxiliary = struct.unpack_from('<hHBB', data, at+12)
        if data[at:at+4] == b'\0'*4:
            offset = struct.unpack_from('<I', data, at+4)[0]
            if not 4 <= offset < string_size:
                raise ValueError('Bad COFF symbol name offset')
            end = data.find(b'\0', strings+offset, strings+string_size)
            if end < 0:
                raise ValueError('Unterminated COFF symbol name')
            name = data[strings+offset:end]
        else:
            name = data[at:at+8].split(b'\0', 1)[0]
        if section > 0 and storage == 2 and kind & 0x20:
            if section > sections or index+1+auxiliary > count:
                raise ValueError('Invalid function section or auxiliary record')
            value = struct.unpack_from('<I', data, at+8)[0]
            size = struct.unpack_from('<I', data, at+18+4)[0] if auxiliary else None
            section_at = 20+40*(section-1)
            raw_size, raw_at = struct.unpack_from('<II', data, section_at+16)
            if value+(size or 0) > raw_size or raw_at+raw_size > len(data):
                raise ValueError('Function exceeds COFF section')
            found[name.decode('ascii')] = {
                'section': section, 'section_offset': value, 'size': size,
                'file_offset': raw_at+value,
                'bytes': data[raw_at+value:raw_at+value+size] if size is not None else None}
        index += 1+auxiliary
        if index > count:
            raise ValueError('Auxiliary symbols exceed table')
    return found


def defined_function_symbols(data):
    return set(coff_function_records(data))


def main():
    config = tomllib.loads((WS / 'config/ida-mcp.toml').read_text(encoding='utf-8'))['mcp_servers']['ida_mcp']
    contracts = json.loads((WS / 'inventory/character-public-contracts.json').read_text(encoding='utf-8'))
    wanted = {x['mangled'] for x in contracts['contracts']}
    inputs = json.loads((WS / 'inventory/character-codeview.json').read_text(encoding='utf-8'))['objects']
    folder = WS / 'artifacts/character-analysis'
    folder.mkdir(parents=True, exist_ok=True)
    client = StdioMCP([config['command'], *config['args']], WS / 'local/character-analysis-mcp.log')
    session = None
    report = {'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'objects': [], 'sessions_closed': []}
    try:
        client.request('initialize', {'protocolVersion': '2024-11-05', 'capabilities': {}, 'clientInfo': {'name': 'rf-character-static-export', 'version': '1'}})
        client.request('notifications/initialized', notification=True)
        catalog = {x['name']: x['inputSchema'] for x in client.request('tools/list')['tools']}
        def call(name, arguments):
            schema = catalog[name]
            if not set(schema.get('required', [])) <= arguments.keys() or not arguments.keys() <= schema.get('properties', {}).keys():
                raise ValueError(f'Arguments do not match current schema: {name}')
            return client.call(name, arguments)
        for index, item in enumerate(inputs, 1):
            source = WS / item['working_object']
            if hashlib.sha256(source.read_bytes()).hexdigest() != item['sha256']:
                raise ValueError('Object digest changed')
            defined = defined_function_symbols(source.read_bytes())
            cached = folder / f'member_{index:02d}.json'
            if cached.exists():
                previous = json.loads(cached.read_text(encoding='utf-8'))
                if previous.get('sha256') == item['sha256'] and previous.get('export_finished'):
                    if previous.get('symbol_filter_version', 0) < 2:
                        previous['functions'] = [x for x in previous['functions'] if x['function']['name'] in defined]
                        previous['summary']['selected'] = len(previous['functions'])
                        previous['summary']['decompiled'] = sum(x['complete'] for x in previous['functions'])
                        previous['complete'] = all(x['complete'] for x in previous['functions'])
                        previous['symbol_filter_version'] = 2
                        cached.write_text(json.dumps(previous, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
                    report['objects'].append(previous['summary'])
                    print(f'member_{index:02d}: verified cached export', flush=True)
                    continue
            opened = call('idb_open', {'input_path': str(source), 'mode': 'force_headless', 'run_auto_analysis': True,
                                       'init_hexrays': True, 'build_caches': False})
            session = opened['session']['session_id']
            functions = call('list_funcs', {'database': session, 'queries': {'count': 0}})['result'][0]
            if functions.get('next_offset') is not None:
                raise ValueError('Function listing unexpectedly paginated')
            selected = [x for x in functions['data'] if x['name'] in wanted and x['name'] in defined]
            if not selected:
                # Preserve names for diagnosing loader naming without guessing matches.
                (folder / f'member_{index:02d}-names.json').write_text(json.dumps(functions, indent=2), encoding='utf-8')
                raise ValueError(f'No exact public symbol matches in member {index}')
            exported = []
            for function in selected:
                pages = []
                offset = 0
                for _ in range(5):
                    try:
                        result = call('decompile', {'database': session, 'addr': function['addr'], 'max_lines': 1000, 'offset': offset})
                    except RuntimeError as exc:
                        pages.append({'error': str(exc)})
                        next_offset = None
                        break
                    pages.append(result)
                    next_offset = result.get('cursor', {}).get('next')
                    if next_offset is None:
                        break
                    offset = next_offset
                exported.append({'function': function, 'pages': pages, 'complete': next_offset is None and all(x.get('code') and not x.get('error') for x in pages)})
            summary = {'object': source.relative_to(WS).as_posix(), 'sha256': item['sha256'],
                       'functions': len(functions['data']), 'selected': len(selected),
                       'decompiled': sum(x['complete'] for x in exported)}
            complete = all(x['complete'] for x in exported)
            cached.write_text(json.dumps({'sha256': item['sha256'], 'summary': summary, 'complete': complete, 'export_finished': True, 'symbol_filter_version': 2,
                                          'functions': exported}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
            report['objects'].append(summary)
            closed = call('idb_close', {'database': session, 'save': True})
            if not closed.get('success'):
                raise RuntimeError('Session close failed')
            report['sessions_closed'].append(session)
            session = None
            print(f'member_{index:02d}: {summary["decompiled"]}/{len(selected)} public functions exported', flush=True)
        report['selected'] = sum(x['selected'] for x in report['objects'])
        report['decompiled'] = sum(x['decompiled'] for x in report['objects'])
        (WS / 'inventory/character-analysis-export.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    finally:
        if session:
            try:
                client.call('idb_close', {'database': session, 'save': False})
            except Exception:
                pass
        client.close()


if __name__ == '__main__':
    main()
