"""Copy verified Character shader inputs needed by real renderer owners."""
import configparser
import hashlib
import json
import shutil
from pathlib import Path
from compare_client_binaries import WS
from client455_asset_staging import sha, stage_asset


def copy_title_movies(client, run, locale):
    profile = Path('DataTable') / locale / 'CcrLogo.dat'
    config = configparser.ConfigParser(interpolation=None)
    config.read(client / profile, encoding='cp1252')
    logo = config.get('PlayAvi', 'Logo', fallback='./Snd/Bgm/ccrinc.avi')
    count = config.getint('PlayAvi', 'PlayedNum', fallback=0)
    openings = [config.get('PlayAvi', f'Play{i}', fallback='./Snd/Bgm/Prologue.avi')
                for i in range(max(1, count))]
    paths = [profile, *(Path(value.replace('\\', '/')) for value in [logo, *openings] if value)]
    records = []
    seen = set()
    for relative in paths:
        source = (client / relative).resolve()
        if not source.is_relative_to(client.resolve()) or not source.is_file() or source in seen:
            continue
        seen.add(source)
        target = run / source.relative_to(client.resolve())
        stage_asset(source, target)
        records.append(dict(file=target.relative_to(WS).as_posix(),
                            sha256=hashlib.sha256(target.read_bytes()).hexdigest(), original=str(source)))
    return records


def copy_lobby_audio(client, run):
    sounds = ('Snd/BGM/Title.mp3', 'Snd/Login/Start.wav', 'Snd/Login/Middle.wav',
              'Snd/Login/End.wav', 'Snd/Login/Stage01.wav')
    records = []
    for name in sounds:
        source, target = client / name, run / name
        stage_asset(source, target)
        records.append({'file': target.relative_to(WS).as_posix(), 'sha256': sha(target),
                        'original': str(source)})
    return records


def copy_grade_overlay_inputs(run,mutable_materials=False):
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);records=[]
    for grade in ['B','A','C','D']:
        for suffix in ['mst','dds']:
            relative=f'Chef/GradeEffect/{grade}grade.{suffix}';original,target=client/relative,run/relative
            target.parent.mkdir(parents=True,exist_ok=True)
            if mutable_materials and suffix=='mst':shutil.copyfile(original,target)
            else:stage_asset(original,target)
            records.append(dict(file=target.relative_to(WS).as_posix(),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),original=str(original),private_mutable_fixture=mutable_materials and suffix=='mst'))
    return records


def copy_tagged_sound_providers(run):
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455'])
    records=[]
    for name in ['Snd/msssoft.m3d','Snd/msseax.m3d','Snd/mssmp3.asi']:
        original,target=client/name,run/name;target.parent.mkdir(parents=True,exist_ok=True)
        stage_asset(original,target)
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
        stage_asset(original,target,row['sha256'],owned_immutable=original)
        records.append(dict(file=target.relative_to(WS).as_posix(), sha256=row['sha256']))
    return records+copy_sky_resources(run)


def copy_sky_resources(run):
    """Device restoration now owns actual455 atmosphere resources as well."""
    reference=json.loads((WS/'inventory/client455-sky-atmosphere-inputs.json').read_text())
    records=[]
    for row in reference['inputs']:
        source=WS/row['file']
        if hashlib.sha256(source.read_bytes()).hexdigest()!=row['sha256']:
            raise ValueError('Changed pinned sky resource')
        target=run/row['runtime_relative'];target.parent.mkdir(parents=True,exist_ok=True)
        stage_asset(source,target,row['sha256'],owned_immutable=source)
        records.append(dict(file=target.relative_to(WS).as_posix(),sha256=row['sha256'],original=row['original']))
    return records+copy_special_shaders(run)


def copy_special_shaders(run):
    """The ordinary restore callback loads the pinned init.r3o shader registry."""
    reference=json.loads((WS/'inventory/client455-special-shaders-inputs.json').read_text());records=[]
    for row in reference['inputs']:
        source=WS/row['file']
        if hashlib.sha256(source.read_bytes()).hexdigest()!=row['sha256']:raise ValueError('Changed special shader input')
        target=run/row['runtime_relative'];target.parent.mkdir(parents=True,exist_ok=True);stage_asset(source,target,row['sha256'],owned_immutable=source)
        records.append(dict(file=target.relative_to(WS).as_posix(),sha256=row['sha256'],original=row['original']))
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
        stage_asset(original,target,row['sha256'],owned_immutable=original)
        records.append(dict(file=target.relative_to(WS).as_posix(), sha256=row['sha256']))
    if len(records) != 1:
        raise ValueError('Actual item-lock sprite input required')
    return records
