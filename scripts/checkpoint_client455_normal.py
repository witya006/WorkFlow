"""Check normal-port evidence without mistaking open linking for completion."""
import hashlib,json,re
from compare_client_binaries import WS,pe
from coff_references import parse
from verify_client_coff import directives
from prepare_client455_normal import section

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(name):return json.loads((WS/f'inventory/{name}.json').read_text())
def main():
    prep=load('client455-normal-preparation');build=load('client455-normal-build');run=load('client455-normal-consumers');link=load('client455-normal-link');manifest=WS/prep['manifest'];root=WS/'work/client455-port/normal'
    if sha(manifest)!=prep['manifest_sha256'] or sha(manifest)!=build['source_manifest_sha256'] or sha(WS/'scripts/prepare_client455_normal.py')!=prep['script_sha256']:raise ValueError('Changed preparation')
    for name,digest in prep['record_inputs'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Changed facade/record source')
    for item in json.loads(manifest.read_text()):
        if sha(WS/item['file'])!=item['sha256'] or ('input' in item and sha(WS/item['input'])!=item['input_sha256']):raise ValueError('Changed normal source:'+item['file'])
    objects=list((root/'build/RFClient455Consumers.dir/Release').glob('*.obj'))
    if build['build_exit'] or build['objects']!=182 or len(objects)!=182 or build['errors']:raise ValueError('Incomplete normal compilation')
    for obj in objects:
        parsed=parse(obj.read_bytes());flags=directives(obj.read_bytes()).upper()
        if '/DEFAULTLIB:"LIBCMT"' not in flags or 'MSVCRT' in flags or 'D3D8.LIB' in flags or 'D3DX8.LIB' in flags:raise ValueError('Wrong normal CRT/runtime')
        # The parser already rejects non-x86 COFFs; it is not a link/runtime gate.
        if not parsed['sections']:raise ValueError('Empty normal object')
    for original,generated,first,last in [('global.cpp','unity_managers.cpp',b'CUnityBoneMgr::CUnityBoneMgr()',b'_DestroyAnimationMgr( void )'),('cresobject.cpp','animation_control.cpp',b'CAnimation::CAnimation()',b'CAnimation::GetRemainEffectFrameNum( void )')]:
        raw=(WS/'work/client455-port/source/RF_Client'/original).read_bytes();start,end=section(raw,first,last)
        if raw[start:end] not in (root/'generated'/generated).read_bytes():raise ValueError('Production split method bytes changed')
    if sha(WS/'inventory/client455-normal-build.json')!=run['normal_build_sha256'] or run['normal_build_sha256']!=link['normal_build_sha256']:raise ValueError('Stale normal evidence')
    for report in [run,link]:
        for item in report['libraries']:
            if sha(WS/item['file'])!=item['sha256']:raise ValueError('Changed linked library')
    for item in run['objects']:
        if sha(WS/item['file'])!=item['sha256']:raise ValueError('Changed actual consumer object')
    if sha(WS/run['exe'])!=run['exe_sha256'] or sha(WS/run['output'])!=run['output_sha256'] or sha(WS/run['fixture'])!=run['fixture_sha256'] or pe((WS/run['exe']).read_bytes())['entry_rva']!=int(run['entry_rva'],16):raise ValueError('Changed actual normal run')
    if run['native']['status']!='PASS' or run['native']['named_record_sizes']!=[1188,5803,284] or not run['native']['real_ani_loaded'] or run['native']['game_dlls_loaded']:raise ValueError('Incomplete normal consumer cases')
    if not link['link_exit'] or link['other_errors'] or link['unique_unresolved']!=len(link['unresolved']) or not link['unresolved'] or link['legacy_character_linked'] or link['unresolved_forced']:raise ValueError('Unexpected current link state; inspect and update acceptance evidence')
    if sha(WS/link['log'])!=link['log_sha256'] or sha(WS/run['map'])!=run['map_sha256'] or sha(WS/'scripts/native/client455_normal_consumers_probe.cpp')!=run['source_sha256']:raise ValueError('Changed native evidence')
    mapping=(WS/run['map']).read_text(errors='replace')
    for symbol,provider in [(r'\?GetAni@CUnityAniMgr',r'unity_managers\.obj'),(r'\?LoadData@CAnimation',r'animation_control\.obj'),(r'\?LoadRealAnimation@RF455AnimationStorage',r'RFClient455Facade:client455_normal_facade\.obj'),('_RF455_LoadAnimation',r'RFClient455Animation:animation\.obj')]:
        if not re.search(symbol+r'[^\r\n]+\b'+provider+r'\b',mapping):raise ValueError('Actual normal method provider unproven:'+symbol)
    evidence=['client455-normal-preparation','client455-normal-build','client455-normal-consumers','client455-normal-link']
    report={'status':'PARTIAL','compile_status':'PASS','normal_consumer_cases':'PASS','normal_executable_link':'OPEN','original_client_sources':180,'production_split_sources':2,'compiled_client_objects':182,'unresolved_symbols':link['unique_unresolved'],'record_sizes':[1188,5803,284],'evidence_sha256':{n:sha(WS/f'inventory/{n}.json') for n in evidence},'gaps':['Complete39current unresolved named contracts/data;see normal-link.json','Verify high-level455wrapper/state/pose/draw semantics andeffect slot layouts','Screenshot D3D9 readback runtime/multisampling notverified','No full normal WinMain/device loss/gameplay/UI/network acceptance','Hub uses own missing-runtime exceptions/debug logging;original failure/logging notcertified'],'legacy_character_linked':False,'baseline_modified':False,'engine033_modified':False,'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-normal-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL: normal182objects/CUnity-CAnimation realANI PASS;RF_Online link OPEN;M6/M9 OPEN')
if __name__=='__main__':main()
