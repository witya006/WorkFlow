"""Copy verified Character shader inputs needed by real renderer owners."""
import hashlib
import json
import shutil
from compare_client_binaries import WS


def copy_character_shaders(run):
    reference = json.loads((WS / 'inventory/client455-shaders-reference.json').read_text())
    records = []
    for row in reference['programs']:
        original = WS / row['copy']
        if hashlib.sha256(original.read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('Changed actual Character shader input')
        target = run / 'System/shader' / (row['name'] + '.sho')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, target)
        records.append(dict(file=target.relative_to(WS).as_posix(), sha256=row['sha256']))
    return records
