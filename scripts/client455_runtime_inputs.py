"""Copy verified Character shader inputs needed by real renderer owners."""
import hashlib
import json
import shutil
from pathlib import Path
from compare_client_binaries import WS


def copy_tagged_sound_providers(run):
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455'])
    records=[]
    for name in ['Snd/msssoft.m3d','Snd/msseax.m3d','Snd/mssmp3.asi']:
        original,target=client/name,run/name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(original,target)
        records.append(dict(file=target.relative_to(WS).as_posix(),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),original=str(original)))
    return records


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


def copy_item_icon_skins(run):
    reference = json.loads((WS/'inventory/client455-item-lock-reference.json').read_text())
    records = []
    for row in reference['inputs']:
        if row.get('target_id') != 52:
            continue
        original = WS/row['file']
        if hashlib.sha256(original.read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('Changed actual item-lock sprite input')
        target = run/row['runtime_relative']
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, target)
        records.append(dict(file=target.relative_to(WS).as_posix(), sha256=row['sha256']))
    if len(records) != 1:
        raise ValueError('Actual item-lock sprite input required')
    return records
