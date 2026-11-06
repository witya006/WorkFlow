"""Accept the measured actor slice while keeping full client455/M9 open."""
import hashlib,json,re
from pathlib import Path
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS,pe

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(name):return json.loads((WS/'inventory'/(name+'.json')).read_text())
def require(value,message):
    if not value:raise ValueError(message)
def check(row):require(row and sha(WS/row['file'])==row['sha256'],'Changed evidence: '+str(row))
def main():
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS','Normal link')
    link_hash=sha(WS/'inventory/client455-normal-link.json');engine=load('client455-startup-engine-build')
    engine_hash=sha(WS/'inventory/client455-startup-engine-build.json');prep=load('client455-normal-preparation')
    require(prep['script_sha256']==sha(WS/'scripts/prepare_client455_normal.py'),'Stale preparation')
    for name in ['Character455.h','client455_rvp.h','client455_rvp.cpp','client455_rvp_runtime.h','client455_rvp_runtime.cpp','client455_rvp_actor.h','client455_rvp_actor.cpp','client455_normal_rvp.cpp']:
        require(prep['record_inputs'][name]==sha(WS/'scripts/native'/name),'Stale source '+name)
    check(dict(file=prep['manifest'],sha256=prep['manifest_sha256']))
    require(engine['script_sha256']==sha(WS/'scripts/build_client455_engine_startup.py') and engine['objects']==67,'Changed engine')
    check(dict(file=engine['library'],sha256=engine['library_sha256']))
    for row in engine['base_sources']+engine['derived_sources']+[engine['baseline_library'],engine['camera_header_overlay']]:check(row)
    reference=load('client455-rvp-actor-reference')
    require(reference['script_sha256']==sha(WS/'scripts/audit_client455_rvp_actor.py'),'Stale static audit')
    for row in reference['raw_evidence']:check(row)
    extra=json.loads((WS/reference['raw_evidence'][1]['file']).read_text())
    require(sum(r['instructions'] for r in reference['assemblies'])==1051,'Incomplete actual assembly')
    for function in extra['assemblies']:
        require(sum(len(p['asm']['lines']) for p in function['pages'])==function['total'],'Truncated disassembly')
    for folder,pin in zip(['current','reference-backup'],reference['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes();require(sha(path)==pin['sha256'],'Changed pin')
        for row in pin['ranges']:require(hashlib.sha256(read_va(raw,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()==row['sha256'],'Changed range')
    def run(name,script):
        proof=load(name);require(proof['normal_link_sha256']==link_hash and proof['engine_report_sha256']==engine_hash,'Stale runtime '+name)
        require(proof['script_sha256']==sha(WS/'scripts'/script) and proof['builder_sha256']==sha(WS/'scripts/client455_own_probe.py'),'Changed probe')
        require(proof['runtime_inputs_sha256']==sha(WS/'scripts/client455_runtime_inputs.py'),'Changed inputs helper')
        for key in ['exe','map','source','output','console','trace']:check(proof[key])
        for row in proof['inputs']+proof['frames']:check(row)
        require(proof['natural_exit']==0 and proof['native']['status']=='PASS' and proof['inputs_unchanged'],'Runtime failed')
        require(proof['native']==json.loads((WS/proof['output']['file']).read_text()),'Native report differs')
        require(pe((WS/proof['exe']['file']).read_bytes())['architecture']=='x86','Probe architecture')
        return proof
    actor=run('client455-rvp-actor-native','probe_client455_rvp_actor.py');result=actor['native']
    require(result['actors']==12 and result['unique_models']==4 and result['pose_updates']==result['actor_draws']==70,'Stock actor trace')
    require(result['distinct_pose_ticks']==9 and result['restored_parts']==459 and result['isolated_animated_pixels']>0,'Shared animation/palette proof')
    require(not result['warnings'] and result['memory_before']==result['memory_after'] and not result['full_particle_audio'] and not result['full_Tutorial'],'Actor scope/ownership')
    hashes={'all':sha(WS/'inventory/client455-rvp-actor-native.json')};regressions=[]
    for race,selected,ticks in [('bellato',10,364),('cora',9,330),('accretia',8,262)]:
        value=run(f'client455-rvp-runtime-{race}-native','probe_client455_rvp_runtime.py');native=value['native']
        require(native['selected']==selected and native['ticks']==ticks and not native['warnings'] and native['memory_before']==native['memory_after'],'Camera regression')
        hashes[race]=sha(WS/f'inventory/client455-rvp-runtime-{race}-native.json');regressions.append(dict(race=race,selected=selected,ticks=ticks,native_sha256=hashes[race]))
    for name,script,count in [('client455-rvp-actor-visual','review_client455_rvp_actor.py',5),('client455-rvp-runtime-visual','review_client455_rvp_runtime.py',6)]:
        visual=load(name);require(visual['manually_reviewed'] and len(visual['frames'])==count and visual['script_sha256']==sha(WS/'scripts'/script),'Review missing')
        check(visual['sheet'])
        for row in visual['frames']:
            check(row);require(sha(WS/row['preview'])==row['preview_sha256'],'Changed preview')
            require(row.get('native_sha256',visual.get('native_sha256'))==hashes[row.get('race','all')],'Stale review')
    ui=load('client455-ui-startup-native');require(ui['normal_link_sha256']==link_hash and ui['completed_existing_client_create'] and ui['markers'][-1]['eax']==1,'Exact new PE Create1')
    contracts=load('client455-startup-contracts-native');require(contracts['build_sha256']==engine_hash,'Stale startup contracts')
    mapping=(WS/link['map']['file']).read_text()
    for symbol,unit in [('RF455_RvpActorFrame','client455_rvp_actor'),('RF455_RvpActorDraw','client455_rvp_actor'),('CreatePart455','client455_normal_rvp')]:
        require(re.search(symbol+r'[^\r\n]*RFClient455Facade:'+unit+r'.obj',mapping,re.I),'Ordinary provider not retained '+symbol)
    report=dict(status='PARTIAL',ordinary_RVP_actor_geometry='PASS_BOUNDED',real_actor_count=12,shared_models=4,
        stock_pose_updates=70,distinct_pose_ticks=9,restored_parts=459,reviewed_frames=11,
        visual_limit='Stock ships and isolated animated model occupy few pixels at actual CAM distance;no fine visual parity claim',
        regressions=regressions,exactPE_Create1='PASS',normal_link_sha256=link_hash,engine_report_sha256=engine_hash,
        actor_native_sha256=hashes['all'],reference_sha256=sha(WS/'inventory/client455-rvp-actor-reference.json'),
        script_sha256=sha(Path(__file__)),gaps=reference['gaps'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-rvp-actor-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL:realRVP12 actors/4models;9 distinct-pose ticks/459 restored parts;3camera regressions;11reviewed frames;exactPE/Create1 PASS;M9 OPEN')
if __name__=='__main__':main()
