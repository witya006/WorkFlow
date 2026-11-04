"""Select the recovered engine timer without changing the original byte encoding."""
import hashlib,json
from pathlib import Path
from compare_client_binaries import WS
from apply_client_port_patches import PATCHES
from apply_client_draw455 import merge_behavior_manifest
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    paths=json.loads((WS/'config/paths.json').read_text(encoding='utf-8'));original=(Path(paths['legacy_source'])/'R3Engine/R3Engine/common/commonutil.cpp').read_bytes();baseline=original;nl=b'\r\n' if b'\r\n' in original else b'\n'
    for old,new in PATCHES['R3Engine/common/commonutil.cpp']:
        old=old.replace(b'\r\n',nl);new=new.replace(b'\r\n',nl)
        if baseline.count(old)!=1:raise ValueError('Unexpected port anchor')
        baseline=baseline.replace(old,new,1)
    name='work/client-build/source/R3Engine/common/commonutil.cpp';source=WS/name;patches=json.loads((WS/'inventory/client-source-patches.json').read_text(encoding='utf-8'));port=next(p for p in patches if p['file']==name)
    if port['original_sha256']!=sha(original) or port['patched_sha256']!=sha(baseline):raise ValueError('Changed port baseline')
    anchor=b'static float stLoopTime=0,stTime,stRealTime;';at=baseline.index(anchor);nl=b'\r\n' if b'\r\n' in original else b'\n'
    desired=baseline[:at]+b'#if defined(RF_CLIENT_455_LOOP_CLOCK)'+nl+b'#include "client455_loop_clock_bridge.inc"'+nl+b'#else'+nl+baseline[at:]+nl+b'#endif'+nl
    if source.read_bytes() not in [baseline,desired]:raise ValueError('Preserve unexpected commonutil changes')
    proof=WS/'inventory/client455-loop-clock-reference.json'
    source.write_bytes(desired);merge_behavior_manifest([{'file':name,'original_sha256':sha(original),'input_sha256':sha(baseline),'patched_sha256':sha(desired),'build_option':'RF_CLIENT_455_LOOP_CLOCK','legacy_branches_preserved':True,'reference_report_sha256':sha(proof.read_bytes()),'reason':'Restore full selected elapsed-clock update/OS initialization/toggle flow;legacy branch retained','source_apis':['RF455_UpdateLoopClock','RF455_GetLoopDuration']}]);print('PASS:commonutil timer bridge;original encoding andlegacy branch preserved')
if __name__=='__main__':main()
