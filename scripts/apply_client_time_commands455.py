"""Restore selected local time handling at the real client chat input boundary."""
import hashlib,json
from pathlib import Path
from compare_client_binaries import WS
from apply_client_draw455 import merge_behavior_manifest
from audit_client_time_commands455 import main as audit_commands

def main():
    audit_commands();paths=json.loads((WS/'config/paths.json').read_text(encoding='utf-8'))
    rel='character/avatar/cavatar_relationinfo2.cpp';original=(Path(paths['legacy_source'])/'RF Client Side/RF_Client'/rel).read_bytes()
    nl=b'\r\n' if b'\r\n' in original else b'\n';desired=original
    edits=[(b'#include "../../CCamera.h"',b'#include "../../CCamera.h"\n#if defined(RF_CLIENT_455_TIME_COMMANDS)\n#include "client455_time_commands.h"\n#endif'),
           (b'\tZeroMemory( m_pMessageType, 32 );',b'\tZeroMemory( m_pMessageType, 32 );\n#if defined(RF_CLIENT_455_TIME_COMMANDS)\n    if (_GetNetworkMgr()->GetAvatarGrade() >= 1 && RF455_TryClockCommand(pi_pMessage))\n        return TRUE;\n#endif')]
    for before,after in edits:
        before=before.replace(b'\n',nl);after=after.replace(b'\n',nl)
        if desired.count(before)!=1:raise ValueError('Time input source anchor not unique')
        desired=desired.replace(before,after,1)
    dest=WS/'work/client-build/source/RF_Client'/rel
    if dest.read_bytes() not in (original,desired):raise ValueError('Preserving unexpected time input source')
    if dest.read_bytes()!=desired:dest.write_bytes(desired)
    sha=lambda b:hashlib.sha256(b).hexdigest()
    merge_behavior_manifest([{'file':dest.relative_to(WS).as_posix(),'original_sha256':sha(original),'input_sha256':sha(original),'patched_sha256':sha(desired),
        'build_option':'RF_CLIENT_455_TIME_COMMANDS','legacy_branch_preserved':True,'reason':'Restore selected455time/real_time before chat fallback with explicit grade>=1;existing source history/prefix path remains,whole chat/other directives not certified.',
        'binary_evidence':json.loads((WS/'inventory/client455-time-command-reference.json').read_text(encoding='utf-8'))['binary_evidence']}])
    print('PASS:actual CHAT_INFO::SendMessage selects local time commands under grade>=1;original source branch preserved.')

if __name__=='__main__':main()
