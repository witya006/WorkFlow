"""Pin full-width stat text writers;not wholeAvatar refresh or455window layout."""
import json
from pathlib import Path
from compare_client_binaries import WS
from audit_client455_equipment import record
from client455_reference_regions import verify_regions

def main():
    raw=WS/'artifacts/client455-progress/char-info152-reference/session.json';proof=verify_regions(raw)
    assert (proof['full_functions'],proof['full_instructions'],proof['positive_cfg_blocks'])==(6,185,9)
    body=json.loads(raw.read_text());offsets=[5856,5980,6104,6228,6352];assert [(n-4120)//124 for n in offsets]==list(range(14,19))
    for addr,slot in zip(['0x663850','0x6638b0','0x663910','0x663960','0x6639c0'],range(14,19)):
        assert str(4120+124*slot) in body['functions'][addr]['code']
    report=dict(status='PARTIAL_SOURCE',scope='Ordinary CharInfo fullDWORD/float stat writers14..18 andbasicrow binding;full455metric producers/layout remainopen',
        **proof,raw=record(raw),script=record(Path(__file__)),verifier=record(WS/'scripts/client455_reference_regions.py'),decoder=record(WS/'scripts/decode_client455_cfg.py'),
        sources=[record(WS/'scripts'/p) for p in ['client455_char_info_values_port.py','native/client455_char_info_values.inc']],preparer=record(WS/'scripts/prepare_client455_normal.py'),
        prior_runtime=record(WS/'artifacts/client455-progress/before152/manifest.json'),
        facts=['663370 maps23valuefields at4120+124*index;selectedstat fields are14..18',
            '663850/6638B0 format two full32bit words with signed%d - %d;663910 formats full32bit%d',
            '663960 formatsfloat%.2f;6639C0 useslowDWORDof__ftol2_sse thenformats%d',
            'Ordinary publicWORD parameter narrowing andempty Hit/Avoid setters are replaced',
            'Ordinary basicrow layout/child registration/style use455valueowners14..16;oldcoordinates preserved temporarily'],
        gaps=['Full455Avatar metric getters,mount/buff/condition providers andfull41A8B0 refresh are stillopen',
            'Full23field455layout/labels/render,Hit/Avoid visible rows andremaining stat setters',
            'Legacy comparativeWORDarray setters andupgradeannotations remainunported',
            'Target16byte stack-overflow domains notaccepted;legacyNaN/Inf text spelling,allCRT/FP/locale failure fidelity unverified',
            'Fullordinaryplayer/equipment/selection/world/gameplay/M9'],
        full_455_Avatar_refresh=False,full_455_window_layout=False,full_client=False,input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-char-info-values-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL_SOURCE:ordinary32bit/float stat writers andselectedUIvalueowners;fullAvatar455refresh/layout OPEN')

if __name__=='__main__':main()
