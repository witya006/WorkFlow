"""Layer scene-frustum calls over verified work copies;preserve original bytes."""
import hashlib,json
from pathlib import Path
from compare_client_binaries import WS
from apply_client_draw455 import merge_behavior_manifest

def sha(data):return hashlib.sha256(data).hexdigest()
def replace_one(raw,old,new):
    if raw.count(old)!=1:raise ValueError('Nonunique frustum anchor:'+repr(old[:90]))
    return raw.replace(old,new,1)
def main():
    paths=json.loads((WS/'config/paths.json').read_text(encoding='utf-8'));ledger=json.loads((WS/'inventory/client-behavior-patches.json').read_text(encoding='utf-8'));pending=[]
    reference=WS/'inventory/client455-frustum-reference.json';proof=json.loads(reference.read_text(encoding='utf-8'))
    for name in ['global.cpp','cresobject.cpp']:
        path=WS/'work/client-build/source/RF_Client'/name;original=(Path(paths['legacy_source'])/'RF Client Side/RF_Client'/name).read_bytes();current=path.read_bytes();entry=next((p for p in ledger if p['file']==path.relative_to(WS).as_posix()),None)
        if entry and sha(current)!=entry['patched_sha256']:raise ValueError('Changed existing caller:'+name)
        if entry and 'frustum' in entry:
            if entry['frustum']['reference_report_sha256']!=sha(reference.read_bytes()):raise ValueError('Changed frustum reference')
            continue
        if not entry and current!=original:raise ValueError('Unexpected untracked caller:'+name)
        nl=b'\r\n' if b'\r\n' in current else b'\n';flag=b'RF_CLIENT_455_FRUSTUM';anchor=b'#include "Global.h"' if name=='global.cpp' else b'#include "CResObject.h"'
        desired=replace_one(current,anchor,anchor+nl+b'#if defined('+flag+b')'+nl+b'#include "client455_frustum.h"'+(nl+b'#include <cstdlib>' if name=='global.cpp' else b'')+nl+b'#endif')
        if name=='global.cpp':
            old=b'\tD3DXMatrixMultiply( &l_matTemp, &l_matView, &l_matProject);'+nl+nl+b'\tSetFustumNormalPlane( g_pFrustumPlane, l_matTemp );'
            new=b'#if defined('+flag+b')'+nl+b'    if(!RF455_PublishSystemCharacterFrustum(g_pFrustumPlane,'+nl+b'        reinterpret_cast<const float*>(&l_matView),reinterpret_cast<const float*>(&l_matProject))) std::abort();'+nl+b'#else'+nl+old+nl+b'#endif'
        else:
            old=b'\tif( IsBBoxInFrustum( l_BBox.pMin, l_BBox.pMax, g_pFrustumPlane ) )'
            new=b'#if defined('+flag+b')'+nl+b'    if( RF455_IsBBoxInFrustum( l_BBox.pMin, l_BBox.pMax, g_pFrustumPlane ) )'+nl+b'#else'+nl+old+nl+b'#endif'
        desired=replace_one(desired,old,new)
        update=dict(entry) if entry else {'file':path.relative_to(WS).as_posix(),'original_sha256':sha(original),'input_sha256':sha(original),'build_option':'RF_CLIENT_455_FRUSTUM','legacy_branch_preserved':True}
        update['frustum']={'option':'RF_CLIENT_455_FRUSTUM','upstream_sha256':sha(current),'reference_report_sha256':sha(reference.read_bytes()),'binary_evidence':proof['references'],'source_apis':['RF455_PublishSystemCharacterFrustum'] if name=='global.cpp' else ['RF455_IsBBoxInFrustum'],'scope':'Only scene-frustum producer/math consumer;old actor bound-box/lifecycle behavior retained,not full455actor acceptance'}
        update['build_options']=sorted(set(update.get('build_options',[])+[update['build_option'],'RF_CLIENT_455_FRUSTUM']));update['patched_sha256']=sha(desired);pending.append((path,desired,update))
    for path,desired,_ in pending:path.write_bytes(desired)
    merge_behavior_manifest([p[2] for p in pending]);print('PASS:scene SetCharacterClipping andactual CResObject clipping selectsource455;legacy branches/bytes retained')
if __name__=='__main__':main()
