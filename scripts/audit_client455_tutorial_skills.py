"""Verify the common shortcut exercise in the shipped TutorialSkill programs."""
import json
import struct
from collections import Counter
from pathlib import Path

from audit_client455_language import decode
from audit_client455_skill_force_items import tables
from audit_client455_tutorial_scripts import WS, inspect, sha


def main():
    root = Path(json.loads((WS / 'config/paths.json').read_text())['client_455']) / 'DataTable'
    edf = (root / 'SkillForce.edf').read_bytes()
    skills = tables(decode(edf))[0][1]
    skills_by_code = {}
    for index in range(skills['count']):
        offset = index * skills['stride']
        row = skills['data'][offset:offset + skills['stride']]
        code = struct.unpack_from('<I', row, 4)[0]
        skills_by_code.setdefault(code, (index, row))

    phases, demos, practice = Counter(), Counter(), Counter()
    codes = set()
    names = {race + role for race in 'bca' for role in 'wrfs'}
    selectors = {0, 1, 4, 5, 19, 20, 21, 27, 29, 32, 44}
    for path in sorted(root.rglob('*.scp')):
        name = path.stem.lower()
        if name not in names:
            continue
        lesson = []
        inspect(path.read_bytes(), lambda quest, label, selector, data: lesson.append((selector, data))
                if quest == 5 and label == b'TutorialSkill' else None)
        if not lesson:
            continue

        first_combat = next((i for i, (op, _) in enumerate(lesson) if op in (12, 14)), len(lesson))
        phases[len(lesson), first_combat] += 1
        race = 'bca'.index(name[0]) * 2
        demo_code = None
        for selector, data in lesson[:first_combat]:
            def require(condition):
                if not condition:
                    raise ValueError(f'{path}: invalid shortcut exercise operand {selector} {data.hex()}')

            def verify_code(code):
                require(code in skills_by_code)
                _, row = skills_by_code[code]
                require(row[452 + race] and row[12] < 5 and struct.unpack_from('<I', row, 1092)[0])
                codes.add(code)

            require(selector in selectors and data[0] == selector)
            if selector in (19, 20, 21):
                require(data[6:8] == b'\x05\0')
            elif selector == 32:
                value = struct.unpack_from('<I', data, 16)[0]
                require(data[14] == 0)
                if data[15] == 5:
                    verify_code(value)
                    demo_code = value
                else:
                    require(data[15] == 3 and demo_code is not None and 1 <= value <= 10)
                    demos[demo_code, value] += 1
            elif selector == 44:
                value = struct.unpack_from('<I', data, 8)[0]
                require(1 <= data[6] <= 10)
                verify_code(value)
                practice[value, data[6]] += 1

    if not phases:
        raise ValueError('No TutorialSkill files')
    print(json.dumps({
        'skill_force_edf_sha256': sha(edf),
        'files': sum(phases.values()),
        'lengths': [{'commands': length, 'shortcut_prefix': prefix, 'files': count}
                    for (length, prefix), count in sorted(phases.items())],
        'demo_links': [{'code': hex(code), 'slot': slot, 'files': count}
                       for (code, slot), count in sorted(demos.items())],
        'required_links': [{'code': hex(code), 'slot': slot, 'files': count}
                           for (code, slot), count in sorted(practice.items())],
        'rows': {hex(code): skills_by_code[code][0] for code in sorted(codes)},
    }, indent=2))


if __name__ == '__main__':
    main()
