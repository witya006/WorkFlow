"""Check current bounded RVP FX evidence; keep full client/M9 acceptance open."""
import hashlib,json,re
from pathlib import Path
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS,pe

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(name):return json.loads((WS/'inventory'/(name+'.json')).read_text())
def require(value,message):
    if not value:raise ValueError(message)
def check(row):require(row and sha(WS/row['file'])==row['sha256'],'Changed evidence '+str(row))

def main():
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS','Normal link')
    linkHash=sha(WS/'inventory/client455-normal-link.json');engineHash=sha(WS/'inventory/client455-startup-engine-build.json')
    engine=load('client455-startup-engine-build');prep=load('client455-normal-preparation')
    require(prep['script_sha256']==sha(WS/'scripts/prepare_client455_normal.py'),'Stale preparation')
    for name in ['Character455.h','client455_rvp_runtime.cpp','client455_rvp_actor.cpp','client455_rvp_actor.h','client455_rvp_effects.cpp','client455_rvp_effects.h','client455_normal_rvp.cpp']:
        require(prep['record_inputs'][name]==sha(WS/'scripts/native'/name),'Stale source '+name)
    check(dict(file=prep['manifest'],sha256=prep['manifest_sha256']))
    require(engine['script_sha256']==sha(WS/'scripts/build_client455_engine_startup.py') and engine['objects']==67 and len(engine['derived_sources'])==11,'Engine build')
    check(dict(file=engine['library'],sha256=engine['library_sha256']))
    for row in engine['base_sources']+engine['derived_sources']+engine['particle_headers']+[engine['baseline_library'],engine['camera_header_overlay'],engine['particle_header_overlay'],engine['particle_port']['script']]:check(row)
    require(engine['particle_header_overlay']['extra_consumer']=='scripts/native/client455_weather.cpp','Weather ABI declaration missing')
    reference=load('client455-rvp-effects-reference');require(reference['script_sha256']==sha(WS/'scripts/audit_client455_rvp_effects.py'),'Static audit')
    for row in reference['raw_evidence']:check(row)
    require(len(reference['references'][0]['ranges'])==18 and sum(r['instructions'] for r in reference['assemblies'])==2960,'Incomplete reference')
    for folder,pin in zip(['current','reference-backup'],reference['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes();require(sha(path)==pin['sha256'],'Changed pin')
        for row in pin['ranges']:require(hashlib.sha256(read_va(raw,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()==row['sha256'],'Changed reference range')
    inputs=load('client455-particle-inputs');require(inputs['script_sha256']==sha(WS/'scripts/audit_client455_particle_inputs.py') and len(inputs['archives'])==17,'Particle input audit')
    for row in inputs['archives']+[d['ini'] for d in inputs['definitions']]:require(sha(Path(row['file']))==row['sha256'],'Changed original FX input')
    require([len(d['rows']) for d in inputs['definitions']]==[300,64] and [sum(r['present'] for r in d['rows']) for d in inputs['definitions']]==[283,61],'Particle/entity resolution')
    require(inputs['RVP_particle_ids']==[294,295,296,297,298] and all(r['present'] and not r['advanced_tokens'] for r in inputs['RVP_definitions']),'RVP basic recipes')
    layout=load('client455-particle-layout');require(layout['script_sha256']==sha(WS/'scripts/probe_client455_particle_layout.py') and layout['normal_link_sha256']==linkHash and layout['engine_report_sha256']==engineHash,'Stale layout')
    check(layout['source']);check(layout['exe']);require(layout['native']['CParticle']==1296 and layout['native']['CEntity']==212 and layout['native']['constructor_1296_equal'],'Particle ABI')
    def run(name,script):
        proof=load(name);require(proof['normal_link_sha256']==linkHash and proof['engine_report_sha256']==engineHash,'Stale runtime '+name)
        require(proof['script_sha256']==sha(WS/'scripts'/script) and proof['builder_sha256']==sha(WS/'scripts/client455_own_probe.py') and proof['runtime_inputs_sha256']==sha(WS/'scripts/client455_runtime_inputs.py'),'Changed runtime sources')
        for key in ['exe','map','source','output','console','trace']:check(proof[key])
        for row in proof['inputs']+proof['frames']:check(row)
        require(proof['natural_exit']==0 and proof['native']['status']=='PASS' and proof['inputs_unchanged'],'Runtime failed')
        require(proof['native']==json.loads((WS/proof['output']['file']).read_text()) and pe((WS/proof['exe']['file']).read_bytes())['architecture']=='x86','Native report/architecture')
        return proof
    actor=run('client455-rvp-actor-native','probe_client455_rvp_actor.py');result=actor['native']
    require(result['actors']==12 and result['unique_models']==4 and result['stock_ticks']==269 and result['pose_updates']==result['actor_draws']==185 and result['stock_clip_completed'],'Full stock clip')
    require(result['loaded_particle_recipes']==1 and result['particle_draws']==148 and result['entity_draws']==6 and result['isolated_entity_pixels']>0 and result['deferred_FX_release'],'Bounded real FX path')
    require(result['distinct_pose_ticks']==9 and result['restored_parts']==459 and result['isolated_animated_pixels']>0,'Actor palette regression')
    require(not result['warnings'] and result['memory_before']==result['memory_after'] and not result['full_particle_audio'] and not result['full_Tutorial'],'FX scope/ownership')
    hashes={'all':sha(WS/'inventory/client455-rvp-actor-native.json')};regressions=[]
    for race,selected,ticks in [('bellato',10,364),('cora',9,330),('accretia',8,262)]:
        value=run(f'client455-rvp-runtime-{race}-native','probe_client455_rvp_runtime.py');native=value['native']
        require(native['selected']==selected and native['ticks']==ticks and not native['warnings'] and native['memory_before']==native['memory_after'],'Camera/weather regression')
        hashes[race]=sha(WS/f'inventory/client455-rvp-runtime-{race}-native.json');regressions.append(dict(race=race,ticks=ticks,native_sha256=hashes[race]))
    abi=load('client455-particle-abi-fix');require(abi['script_sha256']==sha(WS/'scripts/audit_client455_particle_abi.py') and abi['engine_report_sha256']==engineHash and abi['fixed_cora_native_sha256']==hashes['cora'],'Stale ABI fix proof')
    for row in abi['cases']:
        for key in ['exe','map','decoded']:check(row[key])
    require([[a['bytes'] for a in r['allocations']] for r in abi['cases']]==[[1148,208],[1296,212]],'Weather allocation fix')
    for name,script,count in [('client455-rvp-actor-visual','review_client455_rvp_actor.py',9),('client455-rvp-runtime-visual','review_client455_rvp_runtime.py',6)]:
        visual=load(name);require(visual['manually_reviewed'] and len(visual['frames'])==count and visual['script_sha256']==sha(WS/'scripts'/script),'Review missing')
        check(visual['sheet'])
        for row in visual['frames']:
            check(row);require(sha(WS/row['preview'])==row['preview_sha256'] and row.get('native_sha256',visual.get('native_sha256'))==hashes[row.get('race','all')],'Stale frame review')
    ui=load('client455-ui-startup-native');require(ui['normal_link_sha256']==linkHash and ui['completed_existing_client_create'] and ui['markers'][-1]['eax']==1 and not ui['debugger_exit'],'Exact new PE Create1')
    require(sha(WS/ui['staged_executable'])==link['executable']['sha256'],'Staged PE differs');check(ui['events'])
    contracts=load('client455-startup-contracts-native');require(contracts['build_sha256']==engineHash and contracts['status']=='PASS','Startup contracts')
    mapping=(WS/link['map']['file']).read_text()
    for symbol in ['Draw@RF455RvpEffects','Apply@RF455RvpEffects','RF455_AcquireRvpEffects','RF455_ReleaseRvpEffects']:
        require(re.search(re.escape(symbol)+r'[^\r\n]*RFClient455Facade:client455_rvp_effects.obj',mapping,re.I),'Ordinary FX provider not retained '+symbol)
    report=dict(status='PARTIAL',ordinary_RVP_basic_particle_entity='PASS_BOUNDED',particle_size=1296,entity_size=212,weather_allocation_ABI_fixed=True,
        stock_ticks=result['stock_ticks'],stock_actor_draws=result['actor_draws'],particle_draws=result['particle_draws'],entity_draws=result['entity_draws'],reviewed_frames=15,
        visual_limit='Stock actor/particle and isolated entity occupy few pixels;no isolated particle readback or reference-runtime fine pixel equivalence claim',
        regressions=regressions,exactPE_Create1='PASS',normal_link_sha256=linkHash,engine_report_sha256=engineHash,actor_native_sha256=hashes['all'],
        reference_sha256=sha(WS/'inventory/client455-rvp-effects-reference.json'),layout_sha256=sha(WS/'inventory/client455-particle-layout.json'),abi_fix_sha256=sha(WS/'inventory/client455-particle-abi-fix.json'),
        script_sha256=sha(Path(__file__)),gaps=reference['gaps'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-rvp-effects-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL:basic RVP FX148particle/6entity draws,15viewedframes,3maps,weather ABI fix,exactPE/Create1;fullFX/game/M9 OPEN')

if __name__=='__main__':main()
