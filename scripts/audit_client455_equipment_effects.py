"""Pin equipment effect ownership and freeze actual cloak magic/sound inputs."""
import json,re
from pathlib import Path
from compare_client_binaries import WS
from audit_client455_equipment import record,sha
from client455_reference_regions import verify_regions
from rpk455 import Rpk

def pairs(path,section):
    active=False;rows={}
    for line in path.read_bytes().splitlines():
        tokens=line.split(b';',1)[0].split()
        if not tokens:continue
        if tokens[0]==section:active=True;continue
        if not active or len(tokens)<2:continue
        try:number=int(tokens[0],16 if tokens[0].lower().startswith(b'0x') else 10)&0xffffffff
        except ValueError:continue
        if number:rows.setdefault(number,tokens[1])
    return rows

def main():
    raw=WS/'artifacts/client455-progress/equipment-effects146-reference/session.json';proof=verify_regions(raw)
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);magic=client/'Effect/MagicSptList.spt';wave=client/'Snd/WaveList.spt'
    names=pairs(magic,b'[MagcicSptList]');waves=pairs(wave,b'[WaveList]');wanted={}
    for identifier in [0x50006003,0x50006004,0x50006005]:
        name=names[identifier].replace(b'/',b'\\').lstrip(b'\\').lower();wanted[identifier]=name
    pending=set(wanted.values());selected={};inputs={}
    def add(path):
        path=path.resolve();assert path.is_relative_to(client.resolve())
        inputs[path.relative_to(client).as_posix()]=dict(original=str(path),relative=path.relative_to(client).as_posix(),sha256=sha(path),bytes=path.stat().st_size)
    for path in [magic,wave,client/'Effect/EffectEntityList.spt']:add(path)
    for archive in sorted((client/'Effect').glob('*.rpk')):
        bundle=Rpk(archive.read_bytes());found=pending.intersection(bundle.files)
        if not found:continue
        add(archive)
        for name in found:
            data=bundle.read(name);selected[name]=dict(archive=archive.relative_to(client).as_posix(),file=name.decode('ascii'),bytes=len(data),content_sha256=__import__('hashlib').sha256(data).hexdigest(),preview=data[:150].decode('ascii',errors='replace'))
        pending-=found
        if not pending:break
    assert not pending,pending
    sounds=[]
    for identifier in [0x50006000,0x50006002,0x50006004,277034]:
        name=waves.get(identifier)
        if name:
            relative=name.decode('ascii').replace('\\','/').removeprefix('./');path=client/relative;assert path.is_file(),path;add(path)
            sounds.append(dict(id=identifier,relative=relative))
    report=dict(status='PARTIAL_COMPONENT_STATIC',scope='Equipment animation effect ownership/cleanup/cloak sound control;ordinary player/typed conditions/complete attachment still open',**proof,
        raw=record(raw),script=record(Path(__file__)),regions_script=record(WS/'scripts/client455_reference_regions.py'),sources=[record(WS/'scripts/native'/name) for name in ['client455_equipment_effects.h','client455_equipment_effects_probe.cpp']],
        inputs=list(inputs.values()),magic=[dict(id=identifier,**selected[name]) for identifier,name in wanted.items()],sounds=sounds,
        sound_registry_capacity=64,sound_tags_per_group=30,physical_row_retention=True,stop_all_preserves_counts=True,
        ordinary_runtime_changed=False,full_attachment_positions=False,full_conditions=False,production_player_connected=False,input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-equipment-effects-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(functions=proof['full_functions'],instructions=proof['full_instructions'],blocks=proof['positive_cfg_blocks'],inputs=len(inputs),magic=report['magic'],sounds=sounds)))
if __name__=='__main__':main()
