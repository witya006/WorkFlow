"""Verify selected realUI resource/upload evidence without closing fullUI/M6."""
import hashlib,json,re
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link
from audit_client455_own_entry import validated_entry

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name):return json.loads((WS/f'inventory/{name}.json').read_text())

def main():
    ref=load('client455-sprites-reference');native=load('client455-sprites-native');ui=load('client455-ui-startup-native');engine=load('client455-startup-engine-build');link=load('client455-normal-link');validate_normal_link(link);entry=validated_entry()
    if ref['script_sha256']!=sha(WS/'scripts/audit_client455_sprites.py') or native['script_sha256']!=sha(WS/'scripts/probe_client455_sprites.py') or native['builder_sha256']!=sha(WS/'scripts/client455_own_probe.py'):raise ValueError('Stale sprite audit/probe')
    for folder,row in zip(['current','reference-backup'],ref['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        if sha(path)!=row['sha256']:raise ValueError('Changed455pin')
        for body in row['ranges']:
            if hashlib.sha256(read_va(raw,0x400000+int(body['rva'],16),body['bytes'])).hexdigest()!=body['sha256']:raise ValueError('Changed455sprite reference')
    for row in ref['selected_inputs']:
        if sha(Path(row['file']))!=row['sha256'] or not row['roundtrip_equal']:raise ValueError('Changed selectedSPR input')
    for name,digest in native['sources'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Changed sprite implementation')
    if native['sources']['client455_sprite_texture.inc']!=engine['sprite_texture']['client455_sprite_texture.inc']:raise ValueError('Wrong engine texture source')
    if native['normal_link_sha256']!=sha(WS/'inventory/client455-normal-link.json') or native['engine_build_sha256']!=sha(WS/'inventory/client455-startup-engine-build.json') or native['reference_sha256']!=sha(WS/'inventory/client455-sprites-reference.json'):raise ValueError('Stale sprite dependency evidence')
    if sha(WS/native['source'])!=native['source_sha256'] or sha(WS/native['map'])!=native['map_sha256']:raise ValueError('Changed actual sprite consumer')
    mapping=(WS/native['map']).read_text()
    for symbol,provider in [('LoadData@CMainApp','mainapp.obj'),('LoadSprite@CSpriteMgr','spritemgr.obj'),('Draw@CGUIMouse','guimouse.obj'),('RestoreTexMemSprite@CSprite','R3Engine455Startup:2dsprite.obj'),('GetDDSTexFromBuffer','R3Engine455Startup:r3d3dtex.obj'),('RF455_SelectSpritePath','RFClient455Facade:client455_sprites.obj')]:
        if not re.search(re.escape(symbol)+r'[^\r\n]+'+re.escape(provider),mapping):raise ValueError('Actual source provider missing:'+symbol)
    for run in native['runs']:
        n=run['native']
        if run['exit'] or n['status']!='PASS' or n['target_names']!=55 or n['frames_payload_equal']!=562 or n['format_bits']!=15 or n['colored_pixels']<=10 or not all(n[k] for k in ['normal_mainapp_load_data','real_gui_mouse','cache_reused','device_refs_preserved']):raise ValueError('Incomplete actual sprite scenario')
        for path,digest in [(run['exe'],run['exe_sha256']),(run['output'],run['output_sha256']),(run['frame'],run['frame_sha256']),(run['preview'],run['preview_sha256'])]+[(r['file'],r['sha256']) for r in run['inputs']]:
            if sha(WS/path)!=digest:raise ValueError('Changed actual UI sprite artifact')
        if len((WS/run['frame']).read_bytes())!=n['width']*n['height']*4:raise ValueError('Short UI frame')
    if ui['script_sha256']!=sha(WS/'scripts/probe_client455_device_startup.py') or ui['normal_link_sha256']!=native['normal_link_sha256'] or ui['own_entry_sha256']!=sha(WS/'inventory/client455-own-entry.json'):raise ValueError('Stale exactPE UI startup')
    if sha(WS/ui['staged_executable'])!=link['executable']['sha256'] or sha(WS/ui['events']['file'])!=ui['events']['sha256'] or sha(WS/ui['debugger']['file'])!=ui['debugger']['sha256']:raise ValueError('Changed exactPE UI run')
    for row in ui['inputs']:
        if sha(WS/row['file'])!=row['sha256']:raise ValueError('Changed UI startup input')
    last=ui['markers'][-1];owner=ui['character_owner'];device=ui['device_state']
    if ui['debugger_exit'] or not all(ui['summary'].values()) or last['name']!='after_client_create' or int(last['rva'],16)!=int(entry['points']['after_create']['rva'],16) or not ui['completed_existing_client_create'] or not owner['read'] or owner['device']!=device['device'] or not ui['lab_font_registration_removed'] or any(not e['first_chance'] for e in ui['exceptions']):raise ValueError('Actual after-Create boundary not reached cleanly')
    events=[json.loads(line) for line in (WS/ui['events']['file']).read_text().splitlines()]
    if not any(e['kind']=='exit' and e['code']=='0xe0434200' for e in events):raise ValueError('Missing controlled own startup stop')
    report={'status':'PARTIAL','target_filename_table_and_route':'PASS','real_spr_roundtrip':'PASS','normal_load_data_and_payloads':'PASS','actual_gui_sprite_frame':'PASS','clean_native_exit_and_refs':'PASS','exact_own_pe_existing_create_returned':'PASS','full455_game_create_accepted':False,'evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in ['client455-sprites-reference','client455-sprites-native','client455-ui-startup-native','client455-startup-engine-build','client455-normal-link']},'gaps':ref['gaps']+['Actual backbuffer640x500 vsviewport480 sizing remainsopen','Existing production Create stilllegacy except scoped ports;returnedownCreate doesnotcertifyall455managers/UI/video/order'],'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-sprites-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:realnormal UI sprites/DXT5/payload/frame/cleanexit and exactPE afterCreate PASS;full455UI/M6/M9 OPEN')
if __name__=='__main__':main()
