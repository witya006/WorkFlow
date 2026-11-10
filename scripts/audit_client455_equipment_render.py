"""Preserve full render research; no implementation/appearance acceptance."""
import json
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from client455_reference_regions import verify_regions
from audit_client455_equipment import record

def main():
    path=WS/'artifacts/client455-progress/equipment-render148-reference/session.json'
    raw=json.loads(path.read_text());proof=verify_regions(path)
    row=raw['vtable']['result'][0];table=bytes(int(b,16) for b in row['data'].split())
    assert len(table)==176
    for folder in ['current','reference-backup']:
        binary=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        assert read_va(binary,0xaa8f64,len(table))==table
    slots={offset:hex(int.from_bytes(table[offset:offset+4],'little')) for offset in [24,28,32,148,152,156,172]}
    assert slots=={24:'0x46e120',28:'0x46e520',32:'0x46dbc0',148:'0x46e160',152:'0x46e1e0',156:'0x46e1a0',172:'0x46d8b0'}
    assert proof['full_functions']==27 and proof['full_instructions']==1827 and proof['positive_cfg_blocks']==213
    for addr,body in raw['functions'].items():
        pages=[body]+body.get('pages',[])
        assert pages[-1]['cursor'].get('done'),addr
    report=dict(status='AUDIT_OPEN',scope='Both455equipment render overloads andselected dependencies;implementation andordinary appearance still pending',**proof,
        raw=record(path),script=record(Path(__file__)),decoder_script=record(WS/'scripts/decode_client455_cfg.py'),regions_script=record(WS/'scripts/client455_reference_regions.py'),
        equipment_vtable_rva='0x6a8f64',equipment_vtable_bytes=176,verified_vtable_slots=slots,
        facts=['46E120 advances fade before default render;fade3 returns1 without drawing',
            '46E160 advances fade before matrix render;46C260 and46C2E0 have distinct virtual draw slots',
            '46C470 and46C940 have separate shared time/scroll globals',
            '46D190 is a shared animation function,not equipment Render;equipment Animation slot28 is46E520',
            'Render reads real payload/metadata,unit part andvirtual grade;applies kit/unit/item effects andoptional overlay',
            'Quality byte604 selects up to4 overlay descriptors;full descriptor/texture/backend binding is pending'],
        normal_link=record(WS/'inventory/client455-normal-link.json'),ordinary_runtime_changed=False,full_renderer_implemented=False,full_appearance_or_selection=False,
        next=['Bind complete typed mesh render withreal engine effect/overlay providers','Connect actual CPlayerProc/Avatar slot/animation/frame/render/condition routes'],
        input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-equipment-render-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print('AUDIT_OPEN:27complete functions/1827instructions/213CFG andvtable equal2pins;source render/ordinary appearance still pending')
if __name__=='__main__':main()
