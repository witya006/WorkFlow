"""Validate link success separately from complete client runtime acceptance."""
import hashlib
from compare_client_binaries import WS,pe

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def validate_normal_link(link):
    if link['other_errors'] or link['unique_unresolved']!=len(link['unresolved']) or link['legacy_character_linked'] or link['unresolved_forced']:raise ValueError('Invalid normal link state')
    if sha(WS/link['log'])!=link['log_sha256'] or sha(WS/'inventory/client455-normal-build.json')!=link['normal_build_sha256']:raise ValueError('Stale normal link evidence')
    if link['link_exit']:
        if not link['unresolved']:raise ValueError('Failed link without known unresolved symbols')
        return 'OPEN'
    if link['unresolved']:raise ValueError('Success with unresolved symbols')
    exe=link['executable'];path=WS/exe['file'];raw=path.read_bytes();image=pe(raw)
    if sha(path)!=exe['sha256'] or len(raw)!=exe['bytes'] or image['architecture']!=exe['architecture'] or hex(image['entry_rva'])!=exe['entry_rva'] or hex(image['image_base'])!=exe['image_base'] or [row['name'] for row in image['sections']]!=exe['sections']:raise ValueError('Changed linked normal executable')
    for key in ['map','link_response']:
        if sha(WS/link[key]['file'])!=link[key]['sha256']:raise ValueError('Changed full link evidence')
    if 'CharacterMR' in (WS/link['map']['file']).read_text(errors='replace') or '/FORCE' in (WS/link['link_response']['file']).read_text().upper():raise ValueError('Old Character/forced link detected')
    return 'PASS'
