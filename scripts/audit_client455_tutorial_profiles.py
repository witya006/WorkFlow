"""Classify the lesson after equipment and verify the immediate mission ending."""
import json
from collections import Counter
from pathlib import Path

from audit_client455_tutorial_scripts import WS, inspect, sha


def main():
    root = Path(json.loads((WS / 'config/paths.json').read_text())['client_455']) / 'DataTable'
    file_names = {race + role for race in 'bca' for role in 'wrfs'}
    following_equipment = Counter()
    immediate_mission = []
    longer_chains = Counter()
    for path in sorted(root.rglob('*.scp')):
        if path.stem.lower() not in file_names:
            continue
        quests = {}
        mission = []

        def visit(quest, name, selector, data):
            quests[quest] = name.decode('ascii')
            if quest == 5 and name == b'TutorialMission':
                mission.append((selector, data))

        raw = path.read_bytes()
        layout = inspect(raw, visit)
        next_name = quests[5]
        following_equipment[next_name] += 1
        if next_name != 'TutorialMission':
            chain = tuple(name for ordinal, name in quests.items() if ordinal >= 5)
            longer_chains[chain] += 1
            continue
        if layout['quest_count'] != 6 or len(mission) != 2:
            raise ValueError(f'{path}: unexpected immediate mission ending')
        (dialog, message), (wait, operand) = mission
        if dialog != 3 or message[0] != dialog or message[22] == 0 or \
                wait != 5 or operand[0] != wait or operand[6:] != bytes(6):
            raise ValueError(f'{path}: expected a type-3 dialog and an input-0 wait')
        immediate_mission.append({'file': path.relative_to(root).as_posix(), 'sha256': sha(raw)})

    if not immediate_mission:
        raise ValueError('No immediate mission profiles')
    print(json.dumps({'scripts': sum(following_equipment.values()),
                      'following_equipment': dict(sorted(following_equipment.items())),
                      'immediate_mission_ending': immediate_mission,
                      'other_chains': [{'lessons': chain, 'scripts': count}
                                       for chain, count in sorted(longer_chains.items())]},
                     indent=2))


if __name__ == '__main__':
    main()
