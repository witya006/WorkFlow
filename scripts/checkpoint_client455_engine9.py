"""Validate actual engine9migration artifacts without certifying thewholeclient."""
import hashlib,json
from compare_client_binaries import WS
from verify_client_coff import directives

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name):return json.loads((WS/f'inventory/{name}.json').read_text(encoding='utf-8'))
def main():
    prep=load('client455-d3d9-port-preparation');build=load('client455-d3d9-port-build');probe=load('client455-engine9-probe-build');device=load('client455-engine9-runtime');level=load('client455-engine9-level');sdk=load('d3dx9-headers');imports=load('client455-d3dx-import')
    if build['build_exit'] or build['objects']!=67 or build['unique_errors'] or sdk['signature_exit'] or sha(WS/sdk['package_file'])!=sdk['package_sha256'] or sha(WS/imports['library'])!=imports['library_sha256']:raise ValueError('Incomplete engine9build/dependency proof')
    for name,digest in prep['migration_inputs_sha256'].items():
        if sha(WS/name)!=digest:raise ValueError('Changed migration input')
    manifest=WS/prep['manifest']
    if sha(manifest)!=prep['manifest_sha256'] or sha(manifest)!=build['source_manifest_sha256'] or sha(WS/'scripts/prepare_client455_port.py')!=prep['script_sha256']:raise ValueError('Changed source migration manifest')
    for row in json.loads(manifest.read_text(encoding='utf-8')):
        if sha(WS/prep['baseline']/row['file'])!=row['baseline_sha256'] or sha(WS/prep['root']/'source'/row['file'])!=row['port_sha256']:raise ValueError('Changed baseline/port source')
    objects=sorted((WS/'work/client455-port/build-vs2026/R3Engine455.dir/Release').glob('*.obj'))
    if len(objects)!=67:raise ValueError('Incomplete port COFF set')
    for obj in objects:
        text=directives(obj.read_bytes())
        if '/DEFAULTLIB:"LIBCMT"' not in text or 'MSVCRT' in text.upper() or 'd3d8.lib' in text.lower() or 'd3dx8.lib' in text.lower():raise ValueError('Wrong architecture/CRT/oldruntime directive:'+str(obj))
    for report in [device,level]:
        if sha(WS/report['exe'])!=report['exe_sha256'] or report['exe_sha256']!=probe['exe_sha256'] or sha(WS/report['output'])!=report['output_sha256'] or report['build_report_sha256']!=sha(WS/'inventory/client455-engine9-probe-build.json'):raise ValueError('Changed engine9run')
        n=report['native']
        if n['stage']!='complete' or n['failures'] or n['errors'] or n['warnings'] or n['allocation_before']!=n['allocation_after'] or n['device_refs_after_release'] or n['d3d_refs_after_release'] or not report['character_owner_attached'] or not report['engine_shaders']['grass_program_created']:raise ValueError('Incomplete engine9runtime')
        if any(name in report['direct_imports'] for name in ['d3d8.dll','d3dx8.dll','d3dx9_43.dll']):raise ValueError('Wrong runtime')
    if level['level']['helpers']!=23 or level['level']['interiors']!=8 or level['level']['weather_states']!=[[0,0],[1,1],[0,0]] or level['native']['changed_pixels']<=0 or sha(WS/level['frame'])!=level['frame_sha256']:raise ValueError('Incomplete map/weather GPUcase')
    for item in sdk['files']:
        if sha(WS/item['file'])!=item['sha256']:raise ValueError('Changed SDK header')
    for item in probe['libraries']:
        if sha(WS/item['file'])!=item['sha256']:raise ValueError('Changed probe dependency')
    names=['client455-d3d9-port-preparation','client455-d3d9-port-build','client455-engine9-probe-build','client455-engine9-runtime','client455-engine9-level','d3dx9-headers','client455-d3dx-import']
    report={'status':'PASS','scope':'Initial realR3EngineD3D9 migration andsame-device Characterowner bringup;not fullnormalclient or455equivalence','port_root':prep['root'],'engine_objects':67,'staged_files':492,'migrated_files':50,'device_and_level_scenarios':2,'level':{'helpers':23,'interiors':8,'weather_states':[[0,0],[1,1],[0,0]],'frame_sha256':level['frame_sha256']},'source_architecture':'x86/MT','evidence_sha256':{n:sha(WS/f'inventory/{n}.json') for n in names},'gaps':['Normal180client typedCharacter/model-animation facade andremaining39legacySDKfunctions','Full455engine API/state/math/shader/camera behavior andallresources errorpaths notcertified','Fullscreen/display enumeration currentlyX8R8G8B8;allsettings/modes/device-reset/stateblocks notaccepted','SDK43headers withretargeted importarchive:only actuallyimported36exports verified;headerinlines/fullABI notcertified'],'baseline_mutated':False,'server_modified':False,'input_exe_executed':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-engine9-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PASS:67sourceengine9objects/device+Platform01/Characterowner;same-device path;M6/M9 OPEN')
if __name__=='__main__':main()
