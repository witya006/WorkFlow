"""Verify restored startup contracts and actual own device init, keeping M9 open."""
import hashlib,json,re,struct
from pathlib import Path
from compare_client_binaries import WS,pe
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link
from audit_client455_own_entry import validated_entry

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(name):return json.loads((WS/f'inventory/{name}.json').read_text())
def main():
    ref=load('client455-startup-contracts-reference');build=load('client455-startup-engine-build');cpu=load('client455-startup-contracts-native');run=load('client455-device-startup-native');link=load('client455-normal-link');validate_normal_link(link)
    validated_entry()
    if run['own_entry_sha256']!=sha(WS/'inventory/client455-own-entry.json'):raise ValueError('Stale decoded device checkpoints')
    for folder,item in zip(['current','reference-backup'],ref['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        if sha(path)!=item['sha256']:raise ValueError('Changed pinned455')
        for row in item['ranges']:
            if hashlib.sha256(read_va(raw,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()!=row['sha256']:raise ValueError('Changed target startup contract')
    if sha(WS/'scripts/audit_client455_startup_contracts.py')!=ref['script_sha256'] or sha(WS/'scripts/build_client455_engine_startup.py')!=build['script_sha256']:raise ValueError('Changed preparation source')
    if build['build_exit'] or build['objects']!=67 or sha(WS/build['library'])!=build['library_sha256']:raise ValueError('Invalid derived engine build')
    for row in build['base_sources']+build['derived_sources']+[build['base_cmake'],build['baseline_library'],build['cmake'],build['log']]:
        if sha(WS/row['file'])!=row['sha256']:raise ValueError('Changed engine input/033baseline')
    for row in build['derived_sources']:
        if sha(WS/row['original'])!=row['original_sha256']:raise ValueError('033source mutated')
    if not any(row['file']==build['library'] and row['sha256']==build['library_sha256'] for row in link['libraries']):raise ValueError('Full client did not link restored startup engine')
    if cpu['build_sha256']!=sha(WS/'inventory/client455-startup-engine-build.json') or cpu['reference_sha256']!=sha(WS/'inventory/client455-startup-contracts-reference.json') or cpu['status']!='PASS' or not cpu['color32_preserves_window_mode'] or not cpu['nonzero_create_exits_zero']:raise ValueError('Incomplete CPU protocol cases')
    for path,digest in [(cpu['exe'],cpu['exe_sha256']),(cpu['source'],cpu['source_sha256']),(cpu['map']['file'],cpu['map']['sha256'])]:
        if sha(WS/path)!=digest:raise ValueError('Changed native contract evidence')
    for row in cpu['cases']+cpu['libraries']:
        if sha(WS/row['file'])!=row['sha256']:raise ValueError('Changed CPU case/dependency')
    if [row['name'] for row in cpu['cases']]!=['success','s_false','e_fail']:raise ValueError('Missing exact exit-domain case')
    if run['normal_link_sha256']!=sha(WS/'inventory/client455-normal-link.json') or run['engine_build_sha256']!=cpu['build_sha256'] or run['contracts_sha256']!=sha(WS/'inventory/client455-startup-contracts-native.json') or run['early_startup_sha256']!=sha(WS/'inventory/client455-startup-native.json'):raise ValueError('Stale exact-PE device evidence')
    if sha(WS/run['staged_executable'])!=link['executable']['sha256'] or sha(WS/run['events']['file'])!=run['events']['sha256'] or sha(WS/run['debugger']['file'])!=run['debugger']['sha256'] or sha(WS/run['debugger']['source'])!=run['debugger']['source_sha256']:raise ValueError('Changed owned process evidence')
    for row in run['inputs']:
        if sha(WS/row['file'])!=row['sha256']:raise ValueError('Changed device lab input')
    events=[json.loads(line) for line in (WS/run['events']['file']).read_text().splitlines()];markers=[e for e in events if e['kind']=='checkpoint'];summary=next(e for e in events if e['kind']=='summary');device=next(e for e in events if e['kind']=='device_state');config=next(e for e in events if e['kind']=='render_configuration')
    if run['debugger_exit'] or summary!=run['summary'] or not all(summary[k] for k in ['main_reached','after_d3d_reached','exit_observed']):raise ValueError('Device marker/exit not reached')
    if [m['name'] for m in markers]!=['WinMain','after_sound_before_d3d','after_d3d_before_create'] or markers[-1]['eax']!=0 or markers!=run['markers']:raise ValueError('Real D3D init did not return success')
    if device!=run['device_state'] or not device['read'] or device['ready']!=1 or device['windowed']!=1 or not int(device['window'],16) or not int(device['device'],16) or config!=run['render_configuration'] or config['fullscreen'] or config['render_bits']!=32:raise ValueError('Actual device/window/config not confirmed')
    if any(e['kind'].endswith('_error') or e['kind'] in ['timeout','termination_timeout'] or (e['kind']=='exception' and not e['first_chance']) for e in events) or next(e['code'] for e in events if e['kind']=='exit')!='0xe0434200':raise ValueError('Unexpected device startup failure')
    raw=(WS/link['executable']['file']).read_bytes();stop=pe(raw)['image_base']+int(markers[-1]['rva'],16);call=read_va(raw,stop-5,5);mapping=(WS/link['map']['file']).read_text();target=re.search(r'\?InitR3D3D@R3D3dWrapper@@[^\s]+\s+([0-9a-fA-F]{8})',mapping)
    if not target or call[0]!=0xe8 or stop+struct.unpack('<i',call[1:])[0]!=int(target[1],16):raise ValueError('Marker not after actual D3D wrapper')
    if not re.search(r'\?ForceFullScreen@@[^\r\n]+R3Engine455Startup:r3enginekernel\.obj',mapping) or not re.search(r'\?InitR3D3D@R3D3dWrapper@@[^\r\n]+R3Engine455Startup:r3d3dwrapper\.obj',mapping):raise ValueError('Wrong production provider')
    names=['client455-startup-contracts-reference','client455-startup-engine-build','client455-startup-contracts-native','client455-device-startup-native','client455-startup-native','client455-normal-link']
    report={'status':'PARTIAL','restored_color32_preserves_window_mode':'PASS','restored_create_nonzero_exit_policy':'PASS','actual_own_window_device_ready':'PASS','actual_config':config,'actual_device_state':device,'full_normal_source_link':'PASS','normal_client_create_reached':False,'evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in names},'gaps':ref['gaps']+['Own client stopped before CMainApp::Create/launcher/UI/gameplay/network/full shutdown;window show behavior not accepted by SW_HIDE lab run','Reference startup orders nation/launcher/network before engine and BGM after WaveList;these flows remain open','Existing renderer/particle/shadow/blend/CRT acceptance gaps remain open'],'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-device-startup-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:455color32/Create contract + exact own D3D/window/device ready PASS;client Create/M9 OPEN')
if __name__=='__main__':main()
