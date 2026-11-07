"""Pin Tutorial dependencies and compare target board identities with actual source.

This is an integration audit, not a runtime restoration or a completion score.
Class identities use constructor writes plus PE RTTI; names alone do not prove
behavior. Source construction is measured independently by the native probe.
"""
import hashlib
import json
import re
import struct
from pathlib import Path

from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def record(path):
    return dict(file=path.relative_to(WS).as_posix(), sha256=sha(path))


def u32(raw, address):
    return struct.unpack('<I', read_va(raw, address, 4))[0]


def vptr_store(raw, address):
    """Decode C7 /0 [register+zero],imm32, rejecting globals/register writes."""
    code = read_va(raw, address, 12)
    require(code[0] == 0xc7, 'Expected immediate vptr store at ' + hex(address))
    mod, reg, rm = code[1] >> 6, (code[1] >> 3) & 7, code[1] & 7
    require(reg == 0 and mod != 3 and not (mod == 0 and rm == 5), 'Not an object-memory store')
    at = 2
    if rm == 4:
        sib = code[at]
        require((sib >> 3) & 7 == 4 and not (mod == 0 and sib & 7 == 5), 'Indexed/absolute store')
        at += 1
    if mod == 1:
        require(code[at] == 0, 'Secondary vptr, not the object base')
        at += 1
    elif mod == 2:
        require(struct.unpack_from('<i', code, at)[0] == 0, 'Secondary vptr, not the object base')
        at += 4
    return struct.unpack_from('<I', code, at)[0], code[:at + 4].hex()


def rtti(raw, vtable):
    locator = u32(raw, vtable - 4)
    require(u32(raw, locator) == 0 and u32(raw, locator + 4) == 0, 'Not an x86 primary complete-object locator')
    descriptor = u32(raw, locator + 12)
    name = read_va(raw, descriptor + 8, 160).split(b'\0', 1)[0].decode('ascii')
    match = re.fullmatch(r'\.\?A[UV]((?:\w+@)+)@', name)
    require(match, 'Unsupported RTTI name ' + name)
    qualified = '::'.join(reversed(match.group(1).rstrip('@').split('@')))
    return dict(class_name=qualified, vtable_rva=hex(vtable - 0x400000),
                locator_rva=hex(locator - 0x400000), descriptor_rva=hex(descriptor - 0x400000),
                decorated_type=name)


def main():
    raw_path = WS / 'artifacts/client455-progress/tutorial084-integration.json'
    asm_path = WS / 'artifacts/client455-progress/tutorial084-assembly.json'
    body = json.loads(raw_path.read_text())
    assembly = json.loads(asm_path.read_text())
    functions = {row['addr'].lower(): row for row in body['functions']}
    entry_path = WS / 'artifacts/client455-progress/tutorial084-entrypoints.json'
    entries = json.loads(entry_path.read_text())
    previous_path = WS / entries['source']
    previous = json.loads(previous_path.read_text())
    for row in entries['ranges']['result']:
        functions[row['query'].lower()] = previous[row['query']]
    require(entries['close']['success'] and entries['close']['saved'] and entries['after']['count'] == 0,
            'Owned IDA session not saved/closed')
    require(all(not row.get('error') and not row['truncated'] and
                row['line_count'] == row['total_lines'] for row in functions.values()), 'Incomplete pseudocode')
    ranges = body['ranges']['result'] + entries['ranges']['result']
    require(len(ranges) == len(functions) and all(not row['error'] for row in ranges), 'Missing function metadata')
    pins = json.loads((WS / 'config/client-target.json').read_text())
    references = []
    raw = None
    for folder, key in [('current', 'behavior_reference'), ('reference-backup', 'secondary_reference')]:
        path = WS / f'work/client-reference/{folder}/RF_Online.bin'
        image = path.read_bytes()
        require(sha(path) == pins[key]['sha256'], 'Changed reference pin')
        selected = []
        for row in ranges:
            address, size = int(row['fn']['addr'], 16), int(row['fn']['size'], 16)
            selected.append(dict(rva=hex(address - 0x400000), bytes=size,
                                 sha256=hashlib.sha256(read_va(image, address, size)).hexdigest()))
        require(not references or selected == references[0]['ranges'], 'Selected bodies differ between pins')
        references.append(dict(sha256=sha(path), architecture='x86', image_base='0x400000', ranges=selected))
        if folder == 'current':
            raw = image

    assembly_counts = []
    for row in assembly['functions']:
        lines = [line for page in row['pages'] for line in page['asm']['lines']]
        require(len(lines) == row['pages'][0]['total_instructions'] and
                len({line['addr'] for line in lines}) == len(lines), 'Incomplete actual assembly')
        assembly_counts.append(dict(rva=hex(int(row['addr'], 16) - 0x400000), instructions=len(lines)))
    require(sum(row['instructions'] for row in assembly_counts) == 1514, 'Assembly scope drift')
    root_asm = assembly['functions'][0]
    calls = {int(match.group(1), 16) for page in root_asm['pages'] for line in page['asm']['lines']
             for match in re.finditer(r'\bcall\s+sub_([0-9a-f]+)\b', line['instruction'], re.I)}
    globals_by_name = {row['name']: int(row['addr'], 16) for group in body['vtables']['result'] for row in group['data']}

    def identity(address):
        code = functions[address.lower()]['code']
        match = re.search(r"^\s*(?:\*this|\*\(_DWORD \*\)(?:this|v\d+)) = &([^;]+); /\*(0x[0-9a-f]+)\*/", code, re.M | re.I)
        require(match, 'Missing primary vptr assignment ' + address)
        label, store_address = match.group(1), int(match.group(2), 16)
        vtable, instruction = vptr_store(raw, store_address)
        if label.startswith('off_'):
            require(vtable == int(label[4:], 16), 'Vptr operand differs from decompiler label')
        else:
            name = label.removesuffix("::`vftable'")
            prefix = '??_7' + '@'.join(reversed(name.split('::'))) + '@@6B'
            candidates = [value for key, value in globals_by_name.items() if key.startswith(prefix)]
            require(vtable in candidates, f'Named vptr differs: {address} {label} {vtable:x} candidates={candidates}')
        result = rtti(raw, vtable)
        if not label.startswith('off_'):
            require(result['class_name'] == label.removesuffix("::`vftable'"), 'Symbol/RTTI identity differs')
        # Pin both the instruction and the complete-object RTTI on both references.
        for folder in ['current', 'reference-backup']:
            image = (WS / f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
            require(vptr_store(image, store_address)[0] == vtable and rtti(image, vtable) == result, 'RTTI/vptr differs between pins')
        return dict(ctor_rva=hex(int(address, 16) - 0x400000), store_rva=hex(store_address - 0x400000),
                    store_bytes=instruction, **result)

    boards = []
    require(len(body['board_allocations']) == 53, 'Unexpected target allocation count')
    for row in body['board_allocations']:
        require(int(row['ctor'], 16) in calls, 'Constructor absent from actual Create assembly')
        boards.append(dict(id=row['slot'], object_bytes=row['allocation'], **identity(row['ctor'])))
    require(len({row['id'] for row in boards}) == 53 and max(row['id'] for row in boards) == 55, 'Target registry slots')
    tutorial = identity('0x4A5AE0')
    quest = next(row for row in boards if row['id'] == 20)
    require(tutorial['class_name'] == 'CTutorialBoard' and quest['class_name'] == 'CQuestBriefingBoard', 'Distinct briefing owners')

    native_path = WS / 'inventory/client455-tutorial-dependencies-native.json'
    probe = json.loads(native_path.read_text())
    require(probe['script_sha256'] == sha(WS / 'scripts/probe_client455_tutorial_dependencies.py') and
            probe['builder_sha256'] == sha(WS / 'scripts/client455_own_probe.py') and
            probe['normal_link_sha256'] == sha(WS / 'inventory/client455-normal-link.json'), 'Stale source measurement')
    for key in ['source', 'exe', 'map']:
        item = probe[key]
        require(sha(WS / item['file']) == item['sha256'], 'Changed source probe evidence')
    require(probe['all_observed_runs_passed'] and len(probe['runs']) == 8, 'Native source construction failures')
    observed = probe['runs'][0]['native']
    for run in probe['runs']:
        for key in ['exe', 'console']:
            item = run[key]
            require(sha(WS / item['file']) == item['sha256'], 'Changed staged measurement')
        require(run['natural_exit'] == 0 and run['native'] == observed and
                json.loads((WS / run['console']['file']).read_text()) == observed, 'Inconsistent source registry runs')
    require(observed['source_registry_limit'] == 19 and observed['source_objects'] == 18 and
            observed['equipment_alias'] and observed['out_of_range_null'] and not observed['actual_Tutorial'], 'Source registry scope')
    source_by_class = {row['class'].removeprefix('class '): row['id'] for row in observed['boards']}
    for row in boards:
        row['source_same_named_class_id'] = source_by_class.get(row['class_name'])
        row['behavior_equivalence'] = 'UNPROVEN'
    mismatches = [dict(class_name=row['class_name'], target_id=row['id'], source_id=source_by_class[row['class_name']])
                  for row in boards if row['class_name'] in source_by_class and row['id'] != source_by_class[row['class_name']]]
    target_by_class = {row['class_name']: row for row in boards}
    same_named = len(set(source_by_class) & set(target_by_class))
    link = json.loads((WS / 'inventory/client455-normal-link.json').read_text())
    require(validate_normal_link(link) == 'PASS', 'Current source link')
    source_files = ['define.h', 'gameobject/board/common/cboardmanager.cpp',
                    'gameobject/board/common/cboardmanager.h', 'gameprogress/cgp_maingame.cpp',
                    'gameprogress/cgp_maingame.h', 'mainapp.cpp']
    source_records = [record(WS / 'work/client455-port/normal/source' / path) for path in source_files]
    host_requirements = []
    for name in ['client455_tutorial_runtime.h', 'client455_tutorial_spatial.h',
                 'client455_tutorial_actions.h', 'client455_tutorial_board.h', 'client455_tutorial_intro.h']:
        path = WS / 'scripts/native' / name
        text = re.sub(r'//[^\n]*', '', path.read_text())
        for owner, definition in re.findall(r'class\s+(\w*Host)\b[^{};]*\{(.*?)^\};', text, re.S | re.M):
            declarations = [' '.join(match.split()) for match in re.findall(r'virtual\s+([^;]*?)\s*=\s*0\s*;', definition, re.S)]
            if declarations:
                host_requirements.append(dict(**record(path), class_name=owner,
                                              required_pure_virtual_declarations=declarations))
    require(len(host_requirements) == 5, 'Required production host interfaces missing')
    report = dict(
        status='AUDIT_OPEN', scope='Tutorial/shared UI/Avatar dependencies and actual board identities;no runtime restoration',
        references=references, assemblies=assembly_counts,
        raw_evidence=[record(raw_path), record(asm_path), record(entry_path), record(previous_path)],
        script_sha256=sha(Path(__file__)), source_native=record(native_path), source_files=source_records,
        normal_link_sha256=sha(WS / 'inventory/client455-normal-link.json'),
        owned_IDA_session='14d8cac3', owned_IDA_saved_closed=True,
        required_host_contracts=host_requirements,
        target_registry_limit=56, target_constructed_boards=53,
        unassigned_physical_slots=[i for i in range(56) if i not in {row['id'] for row in boards}],
        target_public_equipment_alias=dict(id=2, maps_to=1),
        target_boards=sorted(boards, key=lambda row: row['id']), dedicated_Tutorial=tutorial,
        source_constructed_boards=18, same_named_classes=same_named, different_board_ids=mismatches,
        target_classes_without_same_named_source_registry=[row['class_name'] for row in boards if row['class_name'] not in source_by_class],
        source_registry_classes_without_same_named_target=[name for name in source_by_class if name not in target_by_class],
        facts=[
            '455 GetBoard accepts IDs below56 and maps public2 to equipment1;Create allocates53 physical objects,not56 objects',
            'Common UI5467D0,boards5477C0 and Avatar5488F0 are shared dependencies of actual Tutorial Create5586D0',
            'CQuestBriefingBoard registry20 and dedicated CTutorialBoard are distinct RTTI/constructor/vptr identities;both InitWindow use38',
            'Actual current source constructs18 objects under19 IDs;some same-named classes have different numeric IDs',
            'A same-named class is not evidence of equivalent window layout,controls,networking,inventory or lifecycle',
            'Selected Avatar setters call a fourth gauge and character-info/nameplate consumers absent from the earlier money-only acceptance',
        ],
        gaps=[
            'Actual Tutorial/four-stage factory/QBI host/follow/localhandlers/frame/input/lifecycle still unfinished',
            'Recover 455 storage/board identity contracts and real required classes before forwarding QBI numeric IDs to legacy GetBoard',
            'Restore complete shared UI/board/Avatar init,including real gameplay gauges,character info/nameplate and processor dependencies',
            'Unassigned physical slots do not prove that no other runtime path can publish an object there',
            'Absent same-named registry classes are not a full source-file inventory or proof that all behavior is absent;renames do not prove equivalence',
            'Full game/client M6F/M7/M9 criteria and all previous acceptance gaps remain mandatory',
        ],
        production_runtime_changed=False, input_exe_executed=False, server_modified=False,
        M6='OPEN', M6F='OPEN', M7='OPEN', M9='OPEN',
    )
    (WS / 'inventory/client455-tutorial-integration.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(status=report['status'], ranges=len(references[0]['ranges']),
                         target_boards=53, source_boards=18, same_named=same_named,
                         mismatched_IDs=mismatches, absent_registry_names=report['target_classes_without_same_named_source_registry'])))


if __name__ == '__main__':
    main()
