"""Pin the actual premium owners and selected57/12 state branch on both455PEs."""
import json,struct
from pathlib import Path
from compare_client_binaries import WS
from audit_client455_equipment import record
from client455_reference_regions import verify_regions
from build_client455_x87_math import read_va

def main():
    raw=WS/'artifacts/client455-progress/premium151-reference/session.json';proof=verify_regions(raw)
    assert (proof['full_functions'],proof['full_instructions'],proof['positive_cfg_blocks'])==(8,583,64)
    for folder in ['current','reference-backup']:
        binary=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        assert read_va(binary,0xaa8c40,8)==struct.pack('<d',0)
        assert read_va(binary,0x560e65,5)==bytes.fromhex('a3b48a0201')
    report=dict(status='PARTIAL_SOURCE',scope='Actual CNetworkMgr premiumDWORD/Avatar benefit owners andselected57/12 state path;premium UI/refresh notimplemented',
        **proof,raw=record(raw),script=record(Path(__file__)),verifier=record(WS/'scripts/client455_reference_regions.py'),decoder=record(WS/'scripts/decode_client455_cfg.py'),
        sources=[record(WS/'scripts'/p) for p in ['client455_premium_state_port.py','native/client455_premium_state.h','native/client455_premium_state.inc','native/client455_launcher_bridge.inc']],
        preparer=record(WS/'scripts/prepare_client455_normal.py'),prior_runtime=record(WS/'artifacts/client455-progress/before151/manifest.json'),
        facts=['560C60 initializes networkDWORD436028=0 andstoresowner in1028AB4;442440 reads and5977E0 writes fullDWORD',
            '5956C0 handles group57/opcode12 via5975C0;statuses0,1,2 update,otherstatuses ignored',
            'Enabled branches consume57payloadbytes;disabled branch reads49,not57;ignored statuses consume1byte',
            '5975C0 writes two columns of six Avatar benefit families;packet segment offsets9/17/25/33/41/1',
            '40BB50 writes maskFFFF andclamps strictlynegative rates only;testAH5/JP preservesNaN andnegativezero',
            '40BCB0/40BCE0 write/read two Avatar combat bonuses at24712/24716;enabled packet49/53,disabled zero',
            'CCR launcher forced premium0 now reaches the actual network state;otherlauncher fields still have separate gaps'],
        known_gaps=['Target Premium window show/hide andicon481 effects notported','Post-packet owner virtual256 condition/UI refresh andfullcondition host notyetconnected',
            'CompleteCashShop dispatcher/protocol andallpremium benefit producers/consumers remainopen','Constructor-unwritten benefit cells remainunknown;unsafe out-of-column/short-read targetmemorydomains notaccepted',
            'Ordinary fullCPlayerProc/Avatar equipment/frame/render/selection/world/client/M9'],
        full_handler=False,full_client=False,input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-premium-state-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL_SOURCE:premium owners and57/12 state path confirmed onbothpins;UI/condition refresh remainopen')

if __name__=='__main__':main()
