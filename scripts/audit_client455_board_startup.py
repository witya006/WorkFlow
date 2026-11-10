"""Pin the full455 startup bodies and measure the still partial source factory."""
import json
import re
from pathlib import Path

from client455_reference_regions import verify_regions
from compare_client_binaries import WS
from checkpoint_client455_rvp_effects import sha, require
from audit_client455_tutorial_integration import rtti, vptr_store


def record(path):
    return dict(file=path.relative_to(WS).as_posix(), sha256=sha(path))


def main():
    raw_path = WS / 'artifacts/client455-progress/board166-reference.json'
    proof = verify_regions(raw_path)
    require(proof['full_functions'] == 6 and proof['full_instructions'] == 3032,
            'Complete selected startup ASM/CFG')
    raw = json.loads(raw_path.read_text())
    lines = {int(row['addr'], 16): row['instruction']
             for page in raw['asm']['0x5477c0'] for row in page['asm']['lines']}
    for address, instruction in {
        0x54783a: 'push 0Ah', 0x54783c: 'push 5', 0x54783e: 'push 6',
        0x547848: 'mov eax, [edx+20h]', 0x54784b: 'call eax',
        0x54785c: 'push 1F4h', 0x547861: 'push 190h', 0x547866: 'push 3',
        0x547870: 'mov eax, [edx+4]', 0x547873: 'call eax',
        0x547875: 'mov [ebp+var_8], 0', 0x547887: 'cmp [ebp+var_8], 5',
        0x54789c: 'mov al, byte ptr [ebp+var_8]',
        0x5478a8: 'mov eax, [edx+28h]', 0x5478ab: 'call eax',
        0x5478be: 'push 1', 0x5478c8: 'mov eax, [edx+18h]',
        0x5478cb: 'call eax', 0x5478cd: 'push 0Ch',
    }.items():
        require(lines[address] == instruction, 'Measured Linker startup operand ' + hex(address))
    # Direct lookups form a useful address-indexed graph, not an assertion that
    # every following call has been reconstructed. Indirect accessor helpers
    # and their side effects remain in the complete raw listing.
    ordered = sorted(lines.items())
    lookups = []
    for i, (address, instruction) in enumerate(ordered):
        if instruction != 'call sub_4FD860':
            continue
        require(ordered[i-1][1] == 'mov ecx, offset dword_110F800' and
                ordered[i-2][1].startswith('push '), 'Board lookup calling convention')
        value = ordered[i-2][1][5:].split(';', 1)[0].strip()
        require(re.fullmatch(r'[0-9A-Fa-f]+h?', value),
                'Unexpected board lookup operand at ' + hex(address))
        lookups.append(dict(call_rva=hex(address-0x400000),
                            board_id=int(value[:-1], 16) if value.endswith('h') else int(value)))
    target_path = WS / 'inventory/client455-tutorial-integration.json'
    target = json.loads(target_path.read_text())
    factory = {int(row['addr'],16):row['instruction'] for page in raw['asm']['0x4fb920']
               for row in page['asm']['lines']}
    require(sum('call ??2@YAPAXI@Z' in instruction for instruction in factory.values()) == 54,
            'All54factory allocations,including explicit-this constructor')
    for address,instruction in {0x4fc4d5:'push 0Ch; Size',0x4fc4fb:'call sub_4FCF00',
                                0x4fc52e:'mov [ecx+7Ch], edx'}.items():
        require(factory[address] == instruction, 'Small BlackList allocation/constructor/slot30')
    pins=[]
    for folder in ['current','reference-backup']:
        image=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        table,store=vptr_store(image,0x4fcf17)
        pins.append(dict(**rtti(image,table),store_bytes=store))
    require(pins[0] == pins[1] and pins[0]['class_name'] == 'CBlackListBoard',
            'Both-pin actual BlackList constructor vptr/RTTI')
    extra=dict(id=30,object_bytes=12,ctor_rva='0xfcf00',store_rva='0xfcf17',**pins[0])
    boards=sorted(target['target_boards']+[extra],key=lambda row:row['id'])
    require(len({row['id'] for row in boards}) == 54,'Complete unique factory slots')
    manager = WS / 'work/client455-port/normal/source/gameobject/board/common/cboardmanager.cpp'
    classes = re.findall(rb'new\s+(\w+Board)\b', manager.read_bytes())
    require(len(classes) == len(set(classes)) == 17, 'Actual source registry construction changed')
    present = {name.decode() for name in classes}
    missing = [dict(id=row['id'], class_name=row['class_name'], ctor_rva=row['ctor_rva'])
               for row in boards if row['class_name'] not in present]
    require(len(target['target_boards']) == 53 and len(missing) == 37,
            'Target/source factory scope')
    main_path = WS / 'work/client455-port/normal/source/gameprogress/cgp_maingame.cpp'
    source = main_path.read_bytes()
    start = source.index(b'CGP_MainGame::Create_Board(')
    end = source.index(b'\t// init unit tuning board', start)
    prefix = source[start:end]
    require(prefix.count(b'InitializeMainGame455()') == 1 and b'_GetBeltBoard' not in prefix,
            'Ordinary startup must use measured Linker, not removed Belt')
    require(b'RF455_RejectRemovedLegacyBelt()' in
            (manager.parent/'cboardmanager.h').read_bytes(), 'Remaining legacy Belt guard retained')
    files = ['scripts/client455_board_startup_port.py', 'scripts/native/client455_linker_startup.inc',
             'scripts/prepare_client455_normal.py', 'scripts/native/client455_linker_window_probe.cpp']
    report = dict(status='STATIC_CONFIRMED_PARTIAL', raw=record(raw_path), **proof,
                  script=record(Path(__file__)), helpers=[record(WS/'scripts/client455_reference_regions.py'),record(WS/'scripts/audit_client455_tutorial_integration.py')],
                  sources=[record(WS/name) for name in files], generated=[record(manager), record(main_path),
                      record(manager.parent/'clinkboard.cpp'),record(manager.parent/'clinkboard.h')],
                  prior_constructor_identity_evidence=record(target_path),
                  target_constructed_boards=54, source_constructed_boards=17,
                  prior_regex_count_was_incomplete=True,previous_count=53,
                  omitted_explicit_this_constructor=extra,
                  factory_slots_without_allocations=[2,23],
                  missing_target_owners=missing, main_game_direct_board_lookups=lookups,
                  linker_startup=dict(board=6, packs=5, slots_per_pack=10, window_id=3,
                                      initial_position=[400, 500], activated_banks=[0,1,2,3,4],
                                      open_argument=1, next_board=12),
                  factory_initializes_before_main_game_inventory=[20,50,21,5,52],
                  facts=['455 has no separate potion Belt between Linker and UnitTuning startup',
                         'Ordinary MainGame now calls the same measured five-bank startup exercised by the native probe',
                         'Full factory initializes QuestBriefing,QuestFinishReport,QuestReward,Trunk,NpcQuest before returning',
                         'MainGame late Linker binding66CB20 takes one window owner;legacy two-owner binding is not equivalent'],
                  gaps=['Full54-owner factory and its initial five window owners remain unimplemented',
                        'Remaining MainGame board startup dimensions,window IDs and specialized methods require migration',
                        'Later MainGame legacy Belt/hotkey/global window bindings still refuse obsolete access',
                        'Full one-owner hotkey binding66CB20 and shared screen ownership remain open',
                        'All item actions,network producers,world/gameplay and prior M6F acceptance gaps remain mandatory'],
                  full_factory=False, full_Linker=False, input_exe_executed=False,
                  server_modified=False, M6='OPEN', M6F='OPEN', M7='OPEN', M9='OPEN')
    path = WS/'inventory/client455-board-startup-reference.json'
    path.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(functions=6, instructions=3032, registered=17, missing=37,
                          direct_lookups=len(lookups), status=report['status'])))


if __name__ == '__main__':
    main()
