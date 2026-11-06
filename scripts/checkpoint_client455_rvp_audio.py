"""Accept measured RVP immediate audio/timer contracts without closing M6/M9."""
import hashlib,json,re
from pathlib import Path
from checkpoint_client455_rvp_effects import sha,load,require,check
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS,pe
def main():
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS','Current normal link')
    linkHash=sha(WS/'inventory/client455-normal-link.json');engineHash=sha(WS/'inventory/client455-startup-engine-build.json');engine=load('client455-startup-engine-build');prep=load('client455-normal-preparation')
    require(engine['script_sha256']==sha(WS/'scripts/build_client455_engine_startup.py') and engine['objects']==67 and len(engine['derived_sources'])==12,'Engine build')
    for row in engine['base_sources']+engine['derived_sources']+engine['particle_headers']+[engine['baseline_library'],engine['camera_header_overlay'],engine['particle_header_overlay']]:check(row)
    check(dict(file=engine['library'],sha256=engine['library_sha256']))
    for name,digest in engine['immediate_sound'].items():require(sha(WS/'scripts/native'/name)==digest,'Changed sound overlay')
    require(prep['script_sha256']==sha(WS/'scripts/prepare_client455_normal.py'),'Preparation')
    for name in ['client455_rvp_runtime.h','client455_rvp_runtime.cpp','client455_rvp_actor.h','client455_rvp_actor.cpp','client455_rvp_audio.h','client455_rvp_audio.cpp']:
        require(prep['record_inputs'][name]==sha(WS/'scripts/native'/name),'Stale source '+name)
    check(dict(file=prep['manifest'],sha256=prep['manifest_sha256']))
    reference=load('client455-rvp-audio-reference');require(reference['script_sha256']==sha(WS/'scripts/audit_client455_rvp_audio.py'),'Static audit')
    for row in reference['raw_evidence']:check(row)
    require(len(reference['references'][0]['ranges'])==18 and sum(r['instructions'] for r in reference['assemblies'])==1665,'Reference scope')
    for folder,pin in zip(['current','reference-backup'],reference['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes();require(sha(path)==pin['sha256'],'Changed pin')
        for row in pin['ranges']:require(hashlib.sha256(read_va(raw,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()==row['sha256'],'Changed reference range')
    inputs=load('client455-rvp-audio-inputs');require(inputs['script_sha256']==sha(WS/'scripts/audit_client455_rvp_audio_inputs.py') and len(inputs['files'])==44 and inputs['events']==210 and inputs['ambient']==0,'Audio input scope')
    for row in inputs['files']+inputs['assets']:require(sha(Path(row['file']))==row['sha256'],'Changed RVP/audio input')
    require(len(inputs['assets'])==2 and all(r['extension']=='.wav' and r['exists'] for r in inputs['assets']),'Actual stock WAV inputs')
    def run(name,script):
        body=load(name);require(body['normal_link_sha256']==linkHash and body['engine_report_sha256']==engineHash,'Stale native '+name)
        require(body['script_sha256']==sha(WS/'scripts'/script) and body['builder_sha256']==sha(WS/'scripts/client455_own_probe.py'),'Probe source drift')
        for key in ['source','exe','map','console','output']:check(body[key])
        for row in body['inputs']:check(row)
        require(body['natural_exit']==0 and body['inputs_unchanged'] and body['native']==json.loads((WS/body['output']['file']).read_text()),'Native execution/evidence')
        require(pe((WS/body['exe']['file']).read_bytes())['architecture']=='x86' and body['native']['status']=='PASS','Native architecture/status')
        require(not body['native']['warnings'] and body['native']['memory_before']==body['native']['memory_after'],'Warnings or memory imbalance')
        return body
    audio=run('client455-rvp-audio-native','probe_client455_rvp_audio.py');a=audio['native']
    require(a['real_Miles'] and a['decoder_elapsed_ms']>0 and a['WAV_no_handle'] and a['MP3_raw_loop_quirk'] and a['capacity_boundary']==129,'Actual decoder/table semantics')
    require(a['ambient_starts']==2 and a['ambient_stops']==2 and a['wave_events']==4 and a['ambient_before_flag16'] and a['timer_rate_actual'] and not a['full_audio_parity'] and not a['full_Tutorial'],'Ordinary RVP audio/timer scope')
    actor=run('client455-rvp-actor-native','probe_client455_rvp_actor.py');r=actor['native']
    require(r['actors']==12 and r['stock_ticks']==269 and r['actor_draws']==185 and r['particle_draws']==148 and r['entity_draws']==6 and r['isolated_entity_pixels']>0 and r['distinct_pose_ticks']==9 and r['restored_parts']==459,'Actor/FX regression')
    hashes={'all':sha(WS/'inventory/client455-rvp-actor-native.json')}
    for race,selected,ticks in [('bellato',10,364),('cora',9,330),('accretia',8,262)]:
        body=run(f'client455-rvp-runtime-{race}-native','probe_client455_rvp_runtime.py');require(body['native']['selected']==selected and body['native']['ticks']==ticks,'Camera regression')
        hashes[race]=sha(WS/f'inventory/client455-rvp-runtime-{race}-native.json')
    for name,count in [('client455-rvp-actor-visual',9),('client455-rvp-runtime-visual',6)]:
        visual=load(name);require(visual['manually_reviewed'] and len(visual['frames'])==count,'Review missing');check(visual['sheet'])
        for row in visual['frames']:check(row);require(sha(WS/row['preview'])==row['preview_sha256'] and row.get('native_sha256',visual.get('native_sha256'))==hashes[row.get('race','all')],'Stale visual evidence')
    ui=load('client455-ui-startup-native');require(ui['normal_link_sha256']==linkHash and ui['completed_existing_client_create'] and ui['markers'][-1]['eax']==1 and not ui['debugger_exit'],'Exact PE Create1');check(ui['events'])
    require(sha(WS/ui['staged_executable'])==link['executable']['sha256'],'Staged executable')
    require(load('client455-startup-contracts-native')['build_sha256']==engineHash and not load('client455-startup-audit')['unresolved_provider_modules'],'Startup contracts/import providers')
    mapping=(WS/link['map']['file']).read_text()
    for symbol,unit in [('RF455_PlayRvpWave','RFClient455Facade:client455_rvp_audio'),('IM_LoadWave','R3Engine455Startup:r3sound'),('_RF455_SetEngineLoopTimeScale','R3Engine455Startup:commonutil')]:
        require(re.search(re.escape(symbol)+r'[^\r\n]*'+re.escape(unit)+r'.obj',mapping,re.I),'Ordinary provider not retained '+symbol)
    report=dict(status='PARTIAL',ordinary_RVP_immediate_audio='PASS_BOUNDED',timer_rate='PASS_BOUNDED',real_Miles_decoder=True,stock_WAV_no_handle='CONFIRMED_COMPILED_BRANCH',stock_audio_events=210,
        ambient_starts=a['ambient_starts'],ambient_stops=a['ambient_stops'],wave_events=a['wave_events'],reviewed_GPU_frames=15,exactPE_Create1='PASS',normal_link_sha256=linkHash,engine_report_sha256=engineHash,
        reference_sha256=sha(WS/'inventory/client455-rvp-audio-reference.json'),audio_native_sha256=sha(WS/'inventory/client455-rvp-audio-native.json'),regression_sha256=hashes,
        script_sha256=sha(Path(__file__)),helper_sha256=sha(WS/'scripts/checkpoint_client455_rvp_effects.py'),gaps=reference['gaps'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-rvp-audio-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:actual Miles/ordinary RVP audio/timer;3maps/actorFX/15GPUframes/exactPE/Create1;M9 OPEN')
if __name__=='__main__':main()
