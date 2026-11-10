"""Pin complete equipment attachment providers and already-owned real inputs."""
import hashlib,json,os,struct
from pathlib import Path
from compare_client_binaries import WS
from audit_client455_equipment import record,sha
from build_client455_x87_math import read_va
from client455_reference_regions import verify_regions

def main():
    raw=WS/'artifacts/client455-progress/equipment-attachment146-reference/session.json';proof=verify_regions(raw)
    reused_raw=WS/'artifacts/client455-progress/equipment-effects146-reference/session.json';previous=verify_regions(reused_raw)
    for target in proof['references']:
        old=next(x for x in previous['references'] if x['sha256']==target['sha256'])
        reused=[x for x in old['functions'] if x['rva'] in ['0x3e0d10','0x3e22f0']];assert len(reused)==2
        target['functions']+=reused
    proof['full_functions']+=2;proof['full_instructions']+=sum(x['instructions'] for x in reused);proof['positive_cfg_blocks']+=sum(x['positive_cfg_blocks'] for x in reused)
    assert proof['references'][0]['functions']==proof['references'][1]['functions']
    tables=[]
    for reference in proof['references']:
        data=read_va((WS/reference['file']).read_bytes(),0x7e1134,17*4);entries=list(struct.unpack('<17I',data))
        assert entries[9]==0x7e1127 and entries[16]==0x7e10df
        tables.append(dict(rva='0x3e1134',bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),entries=[hex(x) for x in entries]))
    assert tables[0]==tables[1]
    names=['client455-equipment-reference','client455-equipment-effects-reference','client455-resource-catalog-reference'];inputs={}
    for name in names:
        report=json.loads((WS/'inventory'/f'{name}.json').read_text())
        for row in report['inputs']:
            path=Path(row['original']);key=os.path.normcase(str(path.resolve()));size=row.get('bytes',path.stat().st_size)
            inputs[key]=dict(original=str(path),relative=row.get('relative',path.relative_to(Path(json.loads((WS/'config/paths.json').read_text())['client_455'])).as_posix()),sha256=row['sha256'],bytes=size)
    out=dict(status='PARTIAL_COMPONENT_STATIC',scope='455effect creation positions,player part-binding/NPC bone selection,weapon/damage points andreal magic translation;ordinary controller/conditions/appearance open',**proof,
        raw=record(raw),reused_raw=record(reused_raw),reused_functions=2,position_switch=tables[0],
        script=record(Path(__file__)),decoder_script=record(WS/'scripts/decode_client455_cfg.py'),regions_script=record(WS/'scripts/client455_reference_regions.py'),
        sources=[record(WS/'scripts/native'/name) for name in ['client455_effect_positions.h','client455_equipment_attachment_probe.cpp']],
        inputs=list(inputs.values()),input_sets=[record(WS/'inventory'/f'{name}.json') for name in names],
        missing_named_bone_or_weapon_temporaries='Target copies uninitialised local data;own API reports undefined andmagic wrapper rejects it. Failure fidelity isnot accepted.',
        ordinary_runtime_changed=False,full_failure_fidelity=False,ordinary_player_connected=False,full_appearance=False,input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-equipment-attachment-reference.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(functions=proof['full_functions'],instructions=proof['full_instructions'],blocks=proof['positive_cfg_blocks'],inputs=len(inputs),switch_entries=17,ordinary_runtime_changed=False)))
if __name__=='__main__':main()
