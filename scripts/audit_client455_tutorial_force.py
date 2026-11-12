"""Record the shipped Force lessons and resolve their operands against client tables."""
import json
import struct
from pathlib import Path

from audit_client455_item_payloads import decode, item_tables
from audit_client455_skill_force_items import tables as skill_force_tables
from audit_client455_tutorial_scripts import WS, inspect, sha


def rows_by_code(table):
    rows = {}
    stride = table['stride']
    for offset in range(0, table['count'] * stride, stride):
        row = table['data'][offset:offset + stride]
        index, code = struct.unpack_from('<II', row)
        rows.setdefault(code, (index, row))
    return rows


def audit(root):
    raw_items = (root / 'Item.edf').read_bytes()
    raw_skill_force = (root / 'SkillForce.edf').read_bytes()
    beacons = rows_by_code(item_tables(decode(raw_items))[0][18])
    forces = rows_by_code(skill_force_tables(decode(raw_skill_force))[0][0])
    profiles = []
    referenced_beacons = set()
    referenced_forces = set()
    for path in sorted(root.rglob('*.scp')):
        if path.stem.lower() not in ('bf', 'cf'):
            continue
        chapters = {}
        equipment_beacons = []
        force_operands = []
        combat_waits = []

        def visit(_, name, selector, data):
            name = name.decode('ascii')
            chapters[name] = chapters.get(name, 0) + 1
            identifier = struct.unpack_from('<H', data, 2)[0]
            if name.endswith('TutorialEquipment') and selector == 40 and data[6] == 18:
                equipment_beacons.append(hex(struct.unpack_from('<I', data, 8)[0]))
            if name in ('TutorialHunting', 'TutorialLooting') and selector == 38:
                combat_waits.append(dict(chapter=name, id=identifier, attack_type=data[6],
                                         code=hex(struct.unpack_from('<I', data, 8)[0])))
            if name != 'TutorialForce' or selector not in (19, 20, 21, 32, 40, 41, 42, 46):
                return
            argument = data[15] if selector == 32 else data[6]
            op = dict(id=identifier, selector=selector, argument=argument)
            if selector == 32 or selector >= 40:
                operand = struct.unpack_from('<I', data, 16 if selector == 32 else 8)[0]
                op['operand'] = hex(operand)
                if selector in (40, 41) or (selector == 32 and argument == 0 and operand != 0xffffffff):
                    referenced_beacons.add(operand)
                if selector in (42, 46) or (selector == 32 and argument == 6):
                    referenced_forces.add(operand)
            force_operands.append(op)

        raw = path.read_bytes()
        inspect(raw, visit)
        if force_operands:
            profiles.append(dict(path=path.relative_to(root).as_posix(), sha256=sha(raw),
                                 chapters=list(chapters.items())[5:], force_operands=force_operands,
                                 equipment_beacons=equipment_beacons, combat_waits=combat_waits))

    if not profiles:
        raise ValueError('No Force lessons found')
    shared = {}
    for field in ('force_operands', 'equipment_beacons', 'combat_waits'):
        if all(profile[field] == profiles[0][field] for profile in profiles):
            shared[field] = profiles[0][field]
            for profile in profiles:
                del profile[field]
    beacon_rows = {}
    for code in sorted(referenced_beacons):
        index, row = beacons[code]
        force_code = struct.unpack_from('<I', row, 152)[0]
        referenced_forces.add(force_code)
        beacon_rows[hex(code)] = dict(index=index, force_code=hex(force_code))
    return dict(item_edf_sha256=sha(raw_items), skill_force_edf_sha256=sha(raw_skill_force),
                beacons=beacon_rows, forces={hex(code): forces[code][0] for code in sorted(referenced_forces)},
                shared=shared, profiles=profiles)


if __name__ == '__main__':
    config = json.loads((WS / 'config/paths.json').read_text())
    print(json.dumps(audit(Path(config['client_455']) / 'DataTable'), indent=2))
