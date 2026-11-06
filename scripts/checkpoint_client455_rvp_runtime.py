"""Accept ordinary RVP camera/timeline evidence, keeping full455 criteria OPEN."""
import hashlib
import json
import re
from pathlib import Path
from audit_client455_own_entry import symbol
from audit_client455_rvp import decode
from audit_client455_scrollbar import assembly_rows
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS, pe


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(name):return json.loads((WS/'inventory'/(name+'.json')).read_text())
def require(value,message):
    if not value:raise ValueError(message)
def check(row):require(bool(row) and sha(WS/row['file'])==row['sha256'],'Changed evidence: '+str(row))


def main():
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS','Normal link failed')
    link_hash=sha(WS/'inventory/client455-normal-link.json');engine=load('client455-startup-engine-build')
    engine_hash=sha(WS/'inventory/client455-startup-engine-build.json');prep=load('client455-normal-preparation')
    require(engine['script_sha256']==sha(WS/'scripts/build_client455_engine_startup.py') and
        prep['script_sha256']==sha(WS/'scripts/prepare_client455_normal.py'),'Stale generators')
    require(engine['objects']==67 and len(engine['derived_sources'])==9,'Unexpected derived engine')
    check(dict(file=engine['library'],sha256=engine['library_sha256']))
    for row in engine['base_sources']+engine['derived_sources']+[engine['baseline_library']]:check(row)
    for row in engine['derived_sources']+[engine['camera_header_overlay']]:
        check(row);check(dict(file=row['original'],sha256=row['original_sha256']))
    check(dict(file=prep['manifest'],sha256=prep['manifest_sha256']))
    for name in ['client455_rvp.h','client455_rvp.cpp','client455_rvp_runtime.h','client455_rvp_runtime.cpp','client455_normal_facade.cpp']:
        require(prep['record_inputs'][name]==sha(WS/'scripts/native'/name),'Stale ordinary source: '+name)
    for key in ['rvp_runtime','movie_state','fullscreen_effect']:
        for name,digest in engine[key].items():require(sha(WS/'scripts/native'/name)==digest,'Stale engine provider')
    reference=load('client455-rvp-runtime-reference')
    require(reference['script_sha256']==sha(WS/'scripts/audit_client455_rvp_runtime.py'),'Stale runtime reference')
    for row in reference['raw_evidence']:check(row)
    body=json.loads((WS/reference['raw_evidence'][0]['file']).read_text())
    require(list(assembly_rows([body[k] for k in ['frameAsm','startAsm','clockAsm','releaseAsm']]))==reference['assemblies'],'Incomplete runtime assembly')
    for folder,pin in zip(['current','reference-backup'],reference['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        require(sha(path)==pin['sha256'] and len(pin['ranges'])==20,'Changed455 runtime pins')
        for row in pin['ranges']:
            require(hashlib.sha256(read_va(raw,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()==row['sha256'],'Changed455 range')

    def run(name,script,structured_source=False):
        value=load(name)
        require(value['normal_link_sha256']==link_hash and value['engine_report_sha256']==engine_hash,'Stale runtime link: '+name)
        require(value['script_sha256']==sha(WS/'scripts'/script) and value['builder_sha256']==sha(WS/'scripts/client455_own_probe.py'),'Stale native script')
        if structured_source:check(value['source'])
        else:check(dict(file=value['source'],sha256=value['source_sha256']))
        for key in ['exe','map','console','output']:check(value[key])
        for row in value['inputs']+value['frames']:check(row)
        require(value['natural_exit']==0 and value['native']['status']=='PASS' and
            value['native']==json.loads((WS/value['output']['file']).read_text()) and
            pe((WS/value['exe']['file']).read_bytes())['architecture']=='x86','Native runtime failed')
        return value

    hashes={};observations=[]
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455'])
    for race in ['bellato','cora','accretia']:
        name=f'client455-rvp-runtime-{race}-native';value=run(name,'probe_client455_rvp_runtime.py',True)
        require(value['runtime_inputs_sha256']==sha(WS/'scripts/client455_runtime_inputs.py'),'Stale shader staging helper')
        check(value['trace']);result=value['native'];doc=decode((client/f'Map/{race}/{race}.rvp').read_bytes())
        for kind,key in [(1,'selected'),(2,'fade_ins'),(3,'fade_outs')]:
            require(result[key]==sum(track['kind']==kind for track in doc['tracks']),'RVP event counts changed')
        require(not doc['actors'] and result['memory_before']==result['memory_after'] and not result['warnings'] and
            value['independent_event_counts_equal'] and value['inputs_unchanged'],'RVP ownership/counts failed')
        require(all(result[k] for k in ['ordinary_RVP_created','float_pause_clock','flag16_gate','nested_renderer_restored','camera_only_and_explicit_refusal']) and
            not result['full_RVP_actor_audio'] and not result['full_Tutorial'],'RVP bounded scope changed')
        trace=[json.loads(line) for line in (WS/value['trace']['file']).read_text().splitlines()]
        require(len(trace)==result['ticks'] and not trace[-1]['playing'] and trace[-1]['cursor']==len(doc['tracks']),'RVP trace incomplete')
        hashes[race]=sha(WS/'inventory'/(name+'.json'))
        root=(WS/value['exe']['file']).parent;original_camera=root/f'Map/{race}/{race}.cam';fixtures=[]
        for filename in ['missing.cam','actors-open.cam']:
            path=root/filename
            require(path.read_bytes()==original_camera.read_bytes(),'Generated camera fixture changed')
            fixtures.append(dict(file=path.relative_to(WS).as_posix(),sha256=sha(path)))
        path=root/'actors-open.rvp'
        require(path.read_bytes()==b'[Object] *unit unit.msh bone unit.bn [PrepareTrack] no_camera [Track]','Generated refusal fixture changed')
        fixtures.append(dict(file=path.relative_to(WS).as_posix(),sha256=sha(path)))
        observations.append(dict(race=race,selected=result['selected'],ticks=result['ticks'],generated_fixtures=fixtures))
    intro_hashes={}
    for race,count in [('bellato',9),('cora',9),('accretia',8)]:
        name=f'client455-tutorial-intro-{race}-native';value=run(name,'probe_client455_tutorial_intro.py')
        result=value['native'];check(value['trace'])
        require(result['selected']==result['captures']==count and result['memory_before']==result['memory_after'] and
            not result['warnings'] and not result['full_stage_QBI_engine_controls'],'Intro regression failed')
        require(value['real_positive_movie_flags'] and value['real_fullscreen_mode_density'],'Intro real backend lost')
        intro_hashes[race]=sha(WS/'inventory'/(name+'.json'))
    display=run('client455-movie-state-native','probe_client455_movie_state.py')
    require(display['native']['flag_combinations']==8 and display['native']['GPU_frames']==6 and
        not display['native']['warnings'] and not display['player_evidence']['compiled_player_stub'],'Movie display or real player entry failed')
    mapping=(WS/display['map']['file']).read_text();raw=(WS/display['exe']['file']).read_bytes()
    entry=symbol(mapping,'?RTMovieFrameMove@@YAXXZ')
    require(read_va(raw,entry,16).hex()==display['player_evidence']['entry_bytes'],'Player entry changed')
    fullscreen=run('client455-fullscreen-effect-native','probe_client455_fullscreen_effect.py')['native']
    require(fullscreen['GPU_frames']==18 and not fullscreen['warnings'] and
        all(fullscreen[k] for k in ['actual_R3Begin_FullScreenEffect_End','current_scene_opaque_final',
        'framebuffer_depth_viewport_UI_restored','texture512_low_video_memory','failed_BeginScene_reported']),'Fullscreen regression failed')

    def review(name,script,count,natives):
        value=load(name)
        require(value['manually_reviewed'] and len(value['frames'])==count and value['script_sha256']==sha(WS/'scripts'/script),'Current frames not reviewed')
        for row in value.get('sheets',[value.get('sheet')]):check(row)
        for row in value['frames']:
            check(row);require(sha(WS/row['preview'])==row['preview_sha256'],'Changed visual preview')
            digest=natives[row['race']] if 'race' in row else natives['all']
            require(row.get('native_sha256',value.get('native_sha256'))==digest,'Stale visual review')
    review('client455-rvp-runtime-visual','review_client455_rvp_runtime.py',6,hashes)
    review('client455-tutorial-intro-visual','review_client455_tutorial_intro.py',29,intro_hashes)
    review('client455-movie-state-visual','review_client455_movie_state.py',6,dict(all=sha(WS/'inventory/client455-movie-state-native.json')))
    review('client455-fullscreen-effect-visual','review_client455_fullscreen_effect.py',5,dict(all=sha(WS/'inventory/client455-fullscreen-effect-native.json')))
    ui=load('client455-ui-startup-native');contracts=load('client455-startup-contracts-native')
    require(ui['normal_link_sha256']==link_hash and ui['completed_existing_client_create'] and ui['markers'][-1]['eax']==1 and
        contracts['build_sha256']==engine_hash,'Exact new PE/Create1 and fresh contracts required')
    mapping=(WS/link['map']['file']).read_text()
    require(re.search(r'RF455_RvpFrameMove@@[^\r\n]*RFClient455Facade:client455_rvp_runtime.obj',mapping,re.I),'Ordinary RVP source provider not retained')
    report=dict(status='PARTIAL',ordinary_RVP_camera_timeline='PASS_BOUNDED',observations=observations,
        RVP_camera_events=27,intro_cameras=26,reviewed_frames=46,fullscreen_GPU_frames=18,
        exactPE_Create1='PASS',normal_link_sha256=link_hash,engine_report_sha256=engine_hash,
        reference_sha256=sha(WS/'inventory/client455-rvp-runtime-reference.json'),script_sha256=sha(Path(__file__)),
        gaps=reference['gaps'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-rvp-runtime-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL:ordinary RVP3maps/27camera events, intro26, reviewed46, exactPE/Create1 PASS;full actor/audio/Tutorial/M9 OPEN')


if __name__=='__main__':main()
