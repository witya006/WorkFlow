"""Layer verified frame numeric/constructor calls over existing cresobject draw patch."""
import hashlib,json
from pathlib import Path
from compare_client_binaries import WS
from apply_client_draw455 import EDITS,patched,merge_behavior_manifest

def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    paths=json.loads((WS/'config/paths.json').read_text(encoding='utf-8'));name='RF_Client/cresobject.cpp';original=(Path(paths['legacy_source'])/'RF Client Side'/name).read_bytes();baseline=patched(original,*EDITS[name]);desired=baseline;nl=b'\r\n' if b'\r\n' in original else b'\n';flag=b'RF_CLIENT_455_ANIMATION_TIMING';include=b'#include "CResObject.h"'
    if desired.count(include)!=1:raise ValueError('Timing include anchor')
    desired=desired.replace(include,include+nl+b'#if defined('+flag+b')'+nl+b'#include "client455_animation_timing.h"'+nl+b'#endif',1)
    at=desired.index(b'CAnimation::CAnimation()');start=desired.index(b'{',at);depth=1;end=start+1
    while depth:
        if desired[end]==123:depth+=1
        if desired[end]==125:depth-=1
        end+=1
    body=desired[start+1:end-1];replacement=nl+b'#if defined('+flag+b')'+nl+b'    static_assert(sizeof(CAnimation)==100,"455 animation control contract");'+nl+b'    RF455_InitializeAnimationControl(this);'+nl+b'#else'+body+b'#endif'+nl;desired=desired[:start+1]+replacement+desired[end-1:]
    for target in [b'm_dwBoneFrame',b'm_pAniIPInfo->dwAniInterpolationFrame']:
        old=target+b' += ( ( GetCharLoopTime() * 5 ) + m_dwFrameNumForAStopTime ) * m_Animation.GetAnimationSpeed();'
        if desired.count(old)!=1:raise ValueError('Timing expression anchor')
        at=desired.index(old);start=desired.rfind(b'\n',0,at)+1;end=desired.index(b'\n',at)+1;line=desired[start:end];indent=desired[start:at]
        new=indent+target+b' = RF455_AdvanceAnimationFrameValue('+target+b', m_dwFrameNumForAStopTime, R3GetLoopTime(), m_Animation.GetAnimationSpeed());'+nl
        desired=desired[:start]+b'#if defined('+flag+b')'+nl+new+b'#else'+nl+line+b'#endif'+nl+desired[end:]
    destination=WS/'work/client-build/source'/name
    if destination.read_bytes() not in [original,baseline,desired]:raise ValueError('Preserving unexpected cresobject changes')
    ledger=json.loads((WS/'inventory/client-behavior-patches.json').read_text(encoding='utf-8'));entry=next(p for p in ledger if p['file']==destination.relative_to(WS).as_posix())
    if entry['original_sha256']!=sha(original) or entry['input_sha256']!=sha(original):raise ValueError('Unexpected draw baseline')
    reference=WS/'inventory/client455-animation-timing-reference.json';proof=json.loads(reference.read_text(encoding='utf-8'))
    update=dict(entry);update['patched_sha256']=sha(desired);update['build_options']=['RF_CLIENT_455_DRAW_ARGUMENTS','RF_CLIENT_455_ANIMATION_TIMING'];update['animation_timing']={'option':'RF_CLIENT_455_ANIMATION_TIMING','legacy_branches_preserved':True,'reference_report_sha256':sha(reference.read_bytes()),'source_apis':['RF455_AdvanceAnimationFrameValue','RF455_InitializeAnimationControl'],'binary_evidence':proof['references']}
    if destination.read_bytes()!=desired:destination.write_bytes(desired)
    merge_behavior_manifest([update]);print('PASS:actual CAnimation ctor andtwo CResObject numeric paths select source455;original bytes/branches preserved')
if __name__=='__main__':main()
