"""Pin grade material,shader andsecondary geometry routes againstboth455pins."""
import hashlib,json
from pathlib import Path
from compare_client_binaries import WS
from client455_reference_regions import verify_regions
from build_client455_x87_math import read_va
from audit_client455_equipment import record

def main():
    raw_file=WS/'artifacts/client455-progress/grade-overlay148-reference/session.json';proof=verify_regions(raw_file)
    prior_file=WS/'artifacts/client455-progress/equipment-render148-reference/session.json';prior=verify_regions(prior_file)
    assert proof['full_functions']==19 and proof['full_instructions']==2677 and proof['positive_cfg_blocks']==229
    wanted={'0x3e89e0','0x3e8b60'};selected=[]
    for reference in proof['references']:
        source=next(r for r in prior['references'] if r['sha256']==reference['sha256'])
        selected=[f for f in source['functions'] if f['rva'] in wanted];assert len(selected)==2
        reference['functions']+=selected
    proof['full_functions']+=2;proof['full_instructions']+=sum(f['instructions'] for f in selected);proof['positive_cfg_blocks']+=sum(f['positive_cfg_blocks'] for f in selected)
    primary=(WS/'work/client-reference/current/RF_Online.bin').read_bytes();secondary=(WS/'work/client-reference/reference-backup/RF_Online.bin').read_bytes()
    data=[]
    for address,size in [(0xbddd84,16),(0xaee040,30),(0xaee020,30),(0xaee000,30),(0xaedfe0,30)]:
        value=read_va(primary,address,size);assert read_va(secondary,address,size)==value
        data.append(dict(rva=hex(address-0x400000),bytes=size,sha256=hashlib.sha256(value).hexdigest()))
    names=['client455_equipment_object.h','client455_equipment_object.cpp','client455_grade_overlay.inc','client455_equipment_overlay_lifecycle.h','Character455.h','client455_normal_facade.cpp','client455_character_draw.h','client455_character_draw.cpp','client455_character_draw_core.cpp','client455_resource_io.h','client455_resource_io.cpp','client455_grade_overlay_probe.cpp','client455_equipment_probe.cpp']
    report=dict(status='PARTIAL_SOURCE_BACKEND',scope='Grade materials/UV shaders/secondary geometry andarchive-mode gate;full mesh-object renderer andordinary player stillopen',**proof,
        raw=record(raw_file),reused_raw=record(prior_file),reused_functions=2,data_regions=data,script=record(Path(__file__)),
        decoder=record(WS/'scripts/decode_client455_cfg.py'),region_verifier=record(WS/'scripts/client455_reference_regions.py'),
        sources=[record(WS/'scripts/native'/name) for name in names],port_script=record(WS/'scripts/client455_equipment_port.py'),preparer=record(WS/'scripts/prepare_client455_normal.py'),
        staging_script=record(WS/'scripts/client455_runtime_inputs.py'),runtime_base=record(WS/'artifacts/client455-progress/before148/manifest.json'),
        materials=['Chef/GradeEffect/Bgrade.mst','Chef/GradeEffect/Agrade.mst','Chef/GradeEffect/Cgrade.mst','Chef/GradeEffect/Dgrade.mst'],
        material_bytes=526,layer_bytes=54,shader_indices=[9,10],UV_constant_register=92,archive_flag_rva='0xd6e518',
        full_mesh_object_renderer=False,ordinary_player_connected=False,full_failure_fidelity=False,
        gaps=['CMeshObject/CEquipObject primary andmatrix Render wrappers,complete effects queue andgrade604 producer','Actual CPlayerProc/Avatar/controller/frame/animation/conditions andselection/world','All original archive-mode producers andnested owner policy','Unbounded tokens,malformed/OOM/EOF behavior,repeated load withoutdestroy andcomplete CRT/FP fidelity'],
        input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-grade-overlay-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],functions=proof['full_functions'],instructions=proof['full_instructions'],blocks=proof['positive_cfg_blocks'],data_regions=len(data),full_player=False)))
if __name__=='__main__':main()
