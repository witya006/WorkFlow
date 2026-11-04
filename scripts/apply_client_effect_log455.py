"""Select the reconstructed 455 logger while retaining the entire legacy body."""
import hashlib
import json
from pathlib import Path
from compare_client_binaries import WS
from apply_client_draw455 import merge_behavior_manifest
from build_client455_effect_log import binary_evidence


def main():
    evidence = binary_evidence()
    implementation = json.loads((WS/'inventory/client455-effect-log.json').read_text(encoding='utf-8'))
    if hashlib.sha256((WS/implementation['library']).read_bytes()).hexdigest() != implementation['library_sha256']:
        raise ValueError('Logging library changed since native verification')
    paths = json.loads((WS/'config/paths.json').read_text(encoding='utf-8'))
    relative = 'RF_Client/addcodebyjang/effectutil.cpp'
    original = (Path(paths['legacy_source'])/'RF Client Side'/relative).read_bytes()
    signature = b'void EffectLog(char *buf)'
    if original.count(signature) != 1:
        raise ValueError('EffectLog definition is not unique')
    start = original.index(signature)
    end = original.index(b'extern BOOL st_bCmp;',start)
    body = original[start:end]
    if body.count(b'SendLog();') != 1:
        raise ValueError('Unexpected legacy logging implementation')
    newline = b'\r\n' if b'\r\n' in original else b'\n'
    replacement = newline.join([b'#if defined(RF_CLIENT_455_EFFECT_LOG)',
        b'extern void RF455_EffectLog(const char*);',
        b'void EffectLog(char *buf) { RF455_EffectLog(buf); }',b'#else',b''])+body+b'#endif'+newline+newline
    desired = original[:start]+replacement+original[end:]
    destination = WS/'work/client-build/source'/relative
    current = destination.read_bytes()
    if current not in (original,desired):
        raise ValueError('Preserving unexpected effectutil.cpp changes')
    if current != desired:
        destination.write_bytes(desired)
    digest = hashlib.sha256(original).hexdigest()
    merge_behavior_manifest([{'file':destination.relative_to(WS).as_posix(),
        'original_sha256':digest,'input_sha256':digest,
        'patched_sha256':hashlib.sha256(desired).hexdigest(),'build_option':'RF_CLIENT_455_EFFECT_LOG',
        'legacy_branch_preserved':True,'implementation_library_sha256':implementation['library_sha256'],
        'reason':'455 logger appends and rotates via 5/10 MB flag semantics; no direct SendLog call in the corresponding reference entrypoint.',
        'binary_evidence':evidence}])
    print('PASS: selectable 455 logging branch; original SendLog body preserved in legacy branch.')


if __name__=='__main__':
    main()
