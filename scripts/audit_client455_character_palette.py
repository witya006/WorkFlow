"""Pin the ordinary Character palette/dummy migration againstboth455references."""
import json,re
from pathlib import Path
from compare_client_binaries import WS
from audit_client455_equipment import record
from client455_reference_regions import verify_regions

def main():
    raw=WS/'artifacts/client455-progress/character-palette147-reference/session.json';proof=verify_regions(raw)
    reused_raw=WS/'artifacts/client455-progress/equipment-attachment146-reference/session.json';previous=verify_regions(reused_raw)
    wanted={'0x3f390','0x3bfb0','0x3a540'}
    for row in proof['references']:
        older=next(r for r in previous['references'] if r['sha256']==row['sha256']);reused=[f for f in older['functions'] if f['rva'] in wanted];assert len(reused)==3;row['functions']+=reused
    proof['full_functions']+=3;proof['full_instructions']+=sum(f['instructions'] for f in reused);proof['positive_cfg_blocks']+=sum(f['positive_cfg_blocks'] for f in reused)
    assert proof['references'][0]['functions']==proof['references'][1]['functions']
    source_root=WS/'work/client455-port/normal/source/character/character';header=(source_root/'ccharacter.h').read_bytes();body=(source_root/'ccharacter_etc.cpp').read_bytes();ctor=(source_root/'ccharacter.cpp').read_bytes()
    assert re.search(rb'#define MAX_PARTS_RESULT\s+20',header) and b'RF455_PART_PALETTES 30' in header and re.search(rb'#define MAX_EFFECT_DUMMYS\s+\( 13 \)',header)
    assert b'm_pMatResMat[MAX_PARTS_RESULT][RF455_PART_PALETTES]' in header and b'p<mesh.m_BlendNum' in body
    assert ctor.count(b'p<RF455_PART_PALETTES')==2
    report=dict(status='PARTIAL_STATIC_ORDINARY',scope='Actual ordinary Character20parts/30matrixpalettes/13dummyindices;full equipment/actor lifecycle remainsopen',**proof,
        raw=record(raw),reused_raw=record(reused_raw),reused_functions=3,script=record(Path(__file__)),decoder_script=record(WS/'scripts/decode_client455_cfg.py'),regions_script=record(WS/'scripts/client455_reference_regions.py'),
        port_script=record(WS/'scripts/client455_character_palette_port.py'),preparer=record(WS/'scripts/prepare_client455_normal.py'),
        sources=[record(source_root/name) for name in ['ccharacter.h','ccharacter.cpp','ccharacter_etc.cpp']]+[record(WS/'scripts/native/client455_character_palette_probe.cpp')],
        original_source_snapshot=record(WS/'artifacts/client455-progress/character-palette147-source-before/manifest.json'),runtime_base=record(WS/'artifacts/client455-progress/before146/manifest.json'),
        part_groups=20,matrix_palettes=30,character_dummy_slots=13,
        target_default_mesh_helper_4513C0='Verified empty returns1;do not invent default substitution there',
        full_constructor_or_lifecycle=False,full_equipment_or_appearance=False,input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-character-palette-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(functions=proof['full_functions'],instructions=proof['full_instructions'],blocks=proof['positive_cfg_blocks'],part_groups=20,palettes=30,dummies=13)))
if __name__=='__main__':main()
