"""Wire455map message8/5, own cache and the client map-load clock boundary."""
import hashlib,json
from pathlib import Path
from compare_client_binaries import WS
from apply_client_draw455 import merge_behavior_manifest
from audit_client_time455 import main as audit_time

def sha(b):return hashlib.sha256(b).hexdigest()
def edit(relative,edits,evidence):
    paths=json.loads((WS/'config/paths.json').read_text(encoding='utf-8'))
    original=(Path(paths['legacy_source'])/'RF Client Side/RF_Client'/relative).read_bytes()
    nl=b'\r\n' if b'\r\n' in original else b'\n';desired=original
    for before,after in edits:
        before=before.replace(b'\n',nl);after=after.replace(b'\n',nl)
        if desired.count(before)!=1:raise ValueError('Map time source anchor not unique:'+relative)
        desired=desired.replace(before,after,1)
    dest=WS/'work/client-build/source/RF_Client'/relative
    if dest.read_bytes() not in (original,desired):raise ValueError('Preserving unexpected map time source:'+relative)
    if dest.read_bytes()!=desired:dest.write_bytes(desired)
    return {'file':dest.relative_to(WS).as_posix(),'original_sha256':sha(original),'input_sha256':sha(original),'patched_sha256':sha(desired),
            'build_option':'RF_CLIENT_455_MAP_TIME','legacy_branch_preserved':True,'reason':'Restore selected455map time message8/5, timestamp/tick cache and successful map-load clock hook; full CLand/UI/error/CRT timezone domain remains open.','binary_evidence':evidence}

def main():
    audit_time();evidence=json.loads((WS/'inventory/client455-time-callers.json').read_text(encoding='utf-8'))['binary_evidence']
    changes=[edit('cland.h',[
        (b'#define __LAND_H__',b'#define __LAND_H__\n#if defined(RF_CLIENT_455_MAP_TIME)\n#include "client455_map_time.h"\n#endif'),
        (b'public :\n\tCLand();',b'#if defined(RF_CLIENT_455_MAP_TIME)\n    RF455_MapTimeState mClock455;\n#endif\npublic :\n\tCLand();'),
        (b'\t~CLand();',b'\t~CLand();\n#if defined(RF_CLIENT_455_MAP_TIME)\n    void ReceiveMapTime455(const void* payload) { RF455_ReceiveMapTime(&mClock455,payload); }\n    void ApplyMapTime455(unsigned mapIndex) { RF455_ApplyMapTime(&mClock455,mapIndex); }\n    const RF455_MapTimeState& GetMapTime455() const { return mClock455; }\n#endif')],evidence),
      edit('cland.cpp',[
        (b'void\nCLand::Init( void )\n{',b'void\nCLand::Init( void )\n{\n#if defined(RF_CLIENT_455_MAP_TIME)\n    RF455_InitMapTime(&mClock455);\n#endif'),
        (b'\tCreateEffect();\n\n\treturn TRUE;',b'\tCreateEffect();\n#if defined(RF_CLIENT_455_MAP_TIME)\n    if (m_pLevel->IsLoadedBsp()) ApplyMapTime455(pi_byMapIndex);\n#endif\n\n\treturn TRUE;')],evidence),
      edit('network/netmsgprocessor/map/cnetmsgprocessor_map.cpp',[
        (b'\tswitch( pMsgHeader->m_byType[1] )\n\t{',b'\tswitch( pMsgHeader->m_byType[1] )\n\t{\n#if defined(RF_CLIENT_455_MAP_TIME)\n        case 5:\n            _GetLand()->ReceiveMapTime455(pi_pMsg);\n            break;\n#endif')],evidence)]
    merge_behavior_manifest(changes)
    print('PASS:3client source files select455map-time packet/cache/load hook; original branches/bytes preserved.')

if __name__=='__main__':main()
