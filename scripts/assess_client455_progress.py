"""Evidence-backed planning estimate, explicitly distinct from acceptance proof.

Weights and readiness ranges are engineering judgements, not measured function
coverage, time spent, test counts, executable size or a claim of equivalence.
"""
import collections,datetime,hashlib,json
from pathlib import Path
from compare_client_binaries import WS,pe

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(name):return json.loads((WS/'inventory'/f'{name}.json').read_text(encoding='utf-8-sig'))

def linked_build(normal):
    """Use the build actually linked, including when a newer edit is unfinished."""
    current=WS/'inventory/client455-normal-build.json'
    candidates=[current]+sorted((WS/'artifacts/client455-progress').glob('before*/inventory/client455-normal-build.json'),reverse=True)
    for path in candidates:
        if sha(path)==normal['normal_build_sha256']:
            return path,json.loads(path.read_text(encoding='utf-8-sig'))
    raise AssertionError('No exact build evidence for the last linked executable')

def main():
    #Frozen scope weights sum to100. Change these only with an explained scope
    #revision; do not inflate readiness by splitting already completed work.
    rows=[
        ('startup','Запуск и конфигурация',3,65,80,
         ['Собственная PE,CRT/WinMain,Miles,окно/D3D;обычный запуск достиг создания и отрисовки Login'],
         ['Полный порядок startup/ошибки/профили/launcher и связь с экранами455'],
         ['client455-normal-link','client455-ui-startup-native','client455-startup-native','client455-startup-contracts-native']),
        ('data','Форматы и загрузка данных',7,50,65,
         ['RPK/EDF/helper SPT/BSP/EBP,модели/ANI;Resource9groups/5playerBN,cash/set/Item47+ND;обычный CharacterDataMgr/14tables и165class lookups в3локализациях'],
         ['Полная опись455,все загрузочные ветки/таблицы/ошибки и обычный bootstrap'],
         ['client455-world-checkpoint','client455-material-layout-checkpoint','client455-item-payloads-checkpoint','client455-resource-catalog-checkpoint','client455-item-bootstrap-checkpoint','client455-character-tables-checkpoint']),
        ('world','Рендер и мир',12,35,50,
         ['D3D9,выбранные карты Bellato/Cora/Accretia,камера/свет/погода/материалы/эффекты вlab'],
         ['Полные visibility/camera/collision,ILevel/Empty/INS,refraction/FX/device reset и игровой мир'],
         ['client455-world-checkpoint','client455-world-frame-checkpoint','client455-material-shaders-checkpoint','client455-shader-text-checkpoint','client455-fullscreen-effect-native']),
        ('character','Персонажи и анимация',10,30,45,
         ['Исходные MESH/BN/ANI загрузчики,менеджеры,pose/skinning и выбранные normal draw маршруты;список455 применяет имена/уровни/64-битные деньги/обучение к3реальным Avatar'],
         ['Полный actor lifecycle,игровой выбор/экипировка/состояния/анимации и все consumers'],
         ['client455-normal-renderer-checkpoint','client455-normal-accounting-checkpoint','client455-animation-checkpoint','client455-registered-characters-checkpoint','client455-avatar-classes-checkpoint']),
        ('ui','Ввод и интерфейс',10,20,35,
         ['GDI/Unicode текст,спрайты/атласы,часть окон/таймеров/input/hover'],
         ['Полные455 окна/layout/focus/IME/input,общий UI bootstrap и игровые связи'],
         ['client455-font-checkpoint','client455-gui-input-checkpoint','client455-item-icon-metadata-checkpoint']),
        ('audio','Звук',2,35,55,
         ['Miles init,selected tagged/RVP playback и звук выбранных эффектов'],
         ['Все sound events/3D/music/settings и полный lifecycle'],
         ['client455-tagged-audio-checkpoint','client455-rvp-audio-checkpoint']),
        ('network','Клиентская сеть',12,10,25,
         ['Codec/AES/transport/rings,selected Nuclear receiver;обычные world-entry запрос58/ответ12 и registered-character1/8→1/9 payload506'],
         ['Полный35-handler dispatch,все реальные потребители,Close/errors/threads/timers'],
         ['client455-network-codec-checkpoint','client455-nuclear-receiver-checkpoint','client455-world-entry-checkpoint','client455-registered-characters-checkpoint']),
        ('login','Вход и выбор персонажа',10,0,10,
         ['Обычный клиент показывает lobby/окно ожидания;обмен входа и список3персонажей проверены отдельно,полные455Login/bootstrap/selection не приняты'],
         ['Полный Title/Login/character selection/auth→world поток455 не пройден'],
         ['client455-login-checkpoint','client455-world-entry-checkpoint','client455-registered-characters-checkpoint']),
        ('gameplay','Игровые действия',15,0,15,
         ['Selected Character flags/Nuclear aiming и отдельные обработчики'],
         ['Обычные movement/collision/targeting/attack/skills/results в одном игровом цикле455'],
         ['client455-character-flags-checkpoint','client455-nuclear-receiver-checkpoint']),
        ('items','Предметы,NPC,квесты',10,15,30,
         ['Реальные таблицы/payload/owners/icons и выбранный inventory handoff'],
         ['Полный inventory/equipment/use/cooldowns/trade/storage/NPC/quests и все классы предметов'],
         ['client455-item-object-checkpoint','client455-item-icon-metadata-checkpoint','client455-skill-force-items-checkpoint']),
        ('social','Чат,группы,гильдии',4,10,25,
         ['Профиль/фильтры/перенос/вывод в4панели и системные сообщения'],
         ['Полный ввод/отправка/получение чата и клиенские группы/гильдии'],
         ['client455-chat-checkpoint','client455-message-dispatch-checkpoint']),
        ('lifecycle','Переходы и устойчивость',5,10,25,
         ['Selected reload/release карт,моделей иGPU ресурсов'],
         ['Все4stages,смена локаций,disconnect/reconnect,lost/reset,выход/освобождение'],
         ['client455-progress-base-checkpoint','client455-world-checkpoint','client455-fullscreen-effect-native']),
    ]
    domains=[];evidence={}
    for ident,title,weight,lo,hi,done,left,names in rows:
        assert 0<=lo<=hi<=100
        for name in names:
            file=WS/'inventory'/f'{name}.json';assert file.is_file(),file
            body=load(name);evidence[name]=dict(file=file.relative_to(WS).as_posix(),sha256=sha(file),status=body.get('status'),scope=body.get('scope'),fresh_for_current_PE=body.get('normal_link_sha256')==sha(WS/'inventory/client455-normal-link.json'),historical_selected_evidence_may_be_used=True)
        domains.append(dict(id=ident,title=title,weight=weight,estimate_low=lo,estimate_high=hi,completed_full_domain=False,done=done,remaining=left,evidence=names))
    assert sum(x['weight'] for x in domains)==100
    low=sum(x['weight']*x['estimate_low'] for x in domains)/100
    high=sum(x['weight']*x['estimate_high'] for x in domains)/100
    registry=load('client-features');status=collections.Counter(x['status'] for x in registry['features'])
    normal,engine=load('client455-normal-link'),load('client455-startup-engine-build')
    build_file,build=linked_build(normal)
    #A new partial build must not silently select an even older checkpoint as
    #current. Preserve the last completed partial checkpoint with its exact build.
    latest='artifacts/client455-progress/before138/inventory/client455-scene-capture-checkpoint.json'
    assert (WS/latest).is_file()
    if (WS/'inventory/client455-login-checkpoint.json').is_file() and load('client455-login-checkpoint')['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json'):
        latest='inventory/client455-login-checkpoint.json'
    if (WS/'inventory/client455-world-entry-checkpoint.json').is_file() and load('client455-world-entry-checkpoint')['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json'):
        latest='inventory/client455-world-entry-checkpoint.json'
    if (WS/'inventory/client455-registered-characters-checkpoint.json').is_file() and load('client455-registered-characters-checkpoint')['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json'):
        latest='inventory/client455-registered-characters-checkpoint.json'
    if (WS/'inventory/client455-resource-catalog-checkpoint.json').is_file() and load('client455-resource-catalog-checkpoint')['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json'):
        latest='inventory/client455-resource-catalog-checkpoint.json'
    if (WS/'inventory/client455-item-bootstrap-checkpoint.json').is_file() and load('client455-item-bootstrap-checkpoint')['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json'):
        latest='inventory/client455-item-bootstrap-checkpoint.json'
    if (WS/'inventory/client455-character-tables-checkpoint.json').is_file() and load('client455-character-tables-checkpoint')['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json'):
        latest='inventory/client455-character-tables-checkpoint.json'
    if (WS/'inventory/client455-avatar-classes-checkpoint.json').is_file() and load('client455-avatar-classes-checkpoint')['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json'):
        latest='inventory/client455-avatar-classes-checkpoint.json'
    login=load('client455-login-frame-native')
    assert login['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json')
    assert login['executable']['sha256']==normal['executable']['sha256']
    assert login['reached_first_login'] and login['first_login_frame_completed'] and login['first_login_frame_captured']
    assert login['capture_result']['result']==0
    for record in (login['captured_frame'],login['capture_metadata']):
        assert sha(WS/record['file'])==record['sha256']
    assert normal['link_exit']==0 and normal['unique_unresolved']==0 and build['objects']==182 and engine['objects']==67
    assert sha(WS/normal['executable']['file'])==normal['executable']['sha256']
    assert sha(WS/engine['library'])==engine['library_sha256']
    pins=json.loads((WS/'config/client-target.json').read_text());reference=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        file=WS/f'work/client-reference/{folder}/RF_Online.bin';assert sha(file)==pins[key]['sha256'] and pe(file.read_bytes())['architecture']=='x86'
        reference.append(dict(file=file.relative_to(WS).as_posix(),sha256=sha(file),architecture='x86'))
    storage=load('workspace-storage-audit')
    wip_file=WS/'inventory/client455-character-tables-reference.json'
    wip=json.loads(wip_file.read_text()) if wip_file.is_file() else None
    character_native_current=latest=='inventory/client455-character-tables-checkpoint.json'
    report=dict(schema=2,assessment_date=datetime.date.today().isoformat(),scope_version=1,scope='Full client455 behavior/source/build through M9,no graphics modernization,no server work',
        estimate_kind='Engineering planning judgement for known functional scope;not measured equivalence coverage',
        weighted_low=low,weighted_high=high,weighted_midpoint=(low+high)/2,communicated_point_percent=25,communicated_range_percent=[20,35],communicated_remaining_percent=75,
        confidence='Useful planning estimate;unknown455features and integration can change the remaining scope. No calibrated calendar forecast.',
        interpretation='Stage numbers are unequal sizes. M0-M5 completion is not five ninths of the full client. Existing legacy code receives no455credit without evidence.',
        domains=domains,complete_acceptance_domains=0,domain_count=len(domains),evidence=evidence,
        observed_facts=dict(client_compilation_units=182,engine_compilation_units=67,canonical_kernel_objects=build['canonical_kernel_objects'],unresolved_symbols=0,own_executable=normal['executable'],engine_sha256=engine['library_sha256'],references=reference,
            exact_linked_build_evidence=dict(file=build_file.relative_to(WS).as_posix(),sha256=sha(build_file),matches_link_record=True),
            newer_build_is_not_the_accepted_runtime=sha(WS/'inventory/client455-normal-build.json')!=normal['normal_build_sha256'],
            last_completed_checkpoint=latest,last_completed_checkpoint_is_historical_for_current_PE=not latest.startswith('inventory/'),current_work='144 PARTIAL:actual Avatar class index/name writers,3real locales and encrypted receiver applying real classes to3Avatar. Ordinary Login pass;next equipment/appearance/remaining bootstrap/selection. Full skill callback and455CharInfo layout remain open.',
            ordinary_login_observation=dict(file='inventory/client455-login-frame-native.json',sha256=sha(WS/'inventory/client455-login-frame-native.json'),fresh_for_current_PE=True,frame=login['captured_frame'],capture=login['capture_result'],stage_state=login['stage_state'],ui_visually_inspected=True,ui_accepted=False,known_visible_problem='Only lobby/waiting state observed;legacy label and incomplete455layout/state/input/auth remain',return_checkpoint='Return after the diagnostic capture;not necessarily the first frame'),
            existing_Create_proved_on_current_PE=load('client455-ui-startup-native').get('completed_existing_client_create',False) and load('client455-ui-startup-native')['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json'),full_Login_character_selection_world_flow_proved=False,normal_movement_combat_inventory_flow_proved=False),
        registry=dict(file='inventory/client-features.json',sha256=sha(WS/'inventory/client-features.json'),entries=len(registry['features']),statuses=dict(status),complete_denominator=False,contains_historical_and_overlapping_records=True,marked_current=[x['id'] for x in registry['features'] if x.get('runtime_gate_current')],note='Historical overlapping local records are not a complete functional inventory;do not use entry count as project percent.'),
        input_readiness=dict(available=['legacy0.7client/R3Engine sources','two pinned455x86reference binaries','installed455assets','working modern x86 build and IDA/HexRays'],
            reconstructed=['Character interface and multiple455source implementations'],
            missing=['original full455source/SDK','complete455feature/packet/state inventory','complete expected end-to-end scenario set/resource manifest'],
            build_blocking_unresolved_dependencies=0,byte_identical_output_required=False,
            current_build_inputs_ready=True,complete455_behavior_inputs_proven=False,
            available_reference_binaries=2,original_complete455_source_sets=0,
            checked_unresolved_resource_references=load('client455-resource-catalog-checkpoint')['checked_missing_resource_references'],
            resource_inventory_complete=False,
            resource_reference_scope='Catalog bone/BBX references and a selected ANI search,including target RFS lookup;not a complete client asset inventory',
            assembly_status='Current selected client build is possible;this does not prove full455source completeness',
            behavior_specification_status='Incomplete:complete feature/packet/state/resource/scenario inventory is still missing;no defensible percentage for that missing denominator',
            original455source_completeness_percent=None,
            practical_readiness=[
                dict(area='Build inputs for the selected x86 configuration',state='READY',measured='182/182 client and67/67 engine units;0 unresolved symbols in the exact linked build',limit='Not completeness of original455source'),
                dict(area='Binary reference for reverse engineering',state='READY',measured='2 pinned x86 binaries,hashes checked',limit='Not all behavior has been mapped or compared'),
                dict(area='Runtime assets and tables',state='PARTIAL',measured='Resource9groups/30623rows andItem47tables/76049rows;1120 checked unresolved resource references',limit='No complete required-asset denominator;some locale/selector tables disagree'),
                dict(area='Behavioral specification',state='INCOMPLETE',measured='12 domain planning map;144 overlapping historical records',limit='Full feature/packet/state inventory still missing'),
                dict(area='Acceptance scenarios',state='INCOMPLETE',measured='0/12 full domains accepted;ordinary Login lobby/waiting observed',limit='No complete ordinary login/selection/world/gameplay chain')]),
        character_tables143=dict(id='143',status='PARTIAL_NATIVE_VERIFIED' if character_native_current else 'PARTIAL_NATIVE_VERIFIED_ON_PRESERVED143',
            reference_report=dict(file=wip_file.relative_to(WS).as_posix(),sha256=sha(wip_file)) if wip else None,
            static_functions=wip['full_functions'] if wip else None,
            real_input_diagnostics=[dict(name=c['name'],results=c['results'],ignored_character_short_reads=c['ignored_character_short_reads']) for c in wip['cases'] if not c['dbcs_fixture']] if wip else [],
            native_verified_on_current_build=character_native_current,
            not_claimed=['Avatar class/equipment/UI migration','normal successful bootstrap','full class/selection/client acceptance']),
        storage=dict(audit_file='inventory/workspace-storage-audit.json',audit_sha256=sha(WS/'inventory/workspace-storage-audit.json'),audit_time_local=storage['time_local'],
            logical_gib=round(storage['groups']['total']['logical_bytes']/1024**3,2),unique_file_size_gib=round(storage['groups']['total']['unique_content_bytes']/1024**3,2),
            physical_allocation_measured=False,files_deleted=False,note='Hard-linked paths repeat in logical totals. Unique file sizes are not an exact filesystem allocation measurement.'),
        uncertainty=dict(
            known_incomplete=['ordinary455Login/auth/selection','full actor/world/control/combat integration','full protocol consumers','NPC/quests/social and all variants','stage/map/device/disconnect lifecycle'],
            isolated_checks_not_full_acceptance=['world rendering','skinning/animation','item owners/icons/hover','chat/system messages','selected effects/audio/network handlers'],
            not_yet_fully_inventoried=['complete455feature inventory','complete packets/state transitions','all resource families and locale/profile branches','all ordinary end-to-end expected outcomes'],
            range_is_engineering_judgement=True,range_is_statistical_confidence_interval=False),
        next_acceptance_anchors=[
            dict(id='A',result='Ordinary own client displays and handles the455Title/Login UI',status='OPEN',criterion='Real stage factory/Avatar/UI/input/frame/lifecycle integrated;not just Create1'),
            dict(id='B',result='Client auth/character selection reaches and leaves its455screens correctly',status='OPEN',criterion='Pinned expected client packet/state transitions and error paths;server development excluded'),
            dict(id='C',result='Selected character enters a real map and responds to movement/camera/input',status='OPEN',criterion='One ordinary game loop owns stage/world/actor/animation/control/collision'),
            dict(id='D',result='Target/attack/skill/inventory/chat work through ordinary producers and receivers',status='OPEN',criterion='Connected scenarios with explicit expected states;selected lab helpers alone insufficient'),
            dict(id='E',result='Remaining maps/classes/features/lifecycle accepted;repeatable build finalized',status='OPEN',criterion='All12domains/known gaps and docs/client-acceptance.md;M6F/M7/M9 complete')],
        planning_adjustment='Prioritize connected observable client scenarios;keep unresolved numerical/edge/failure fidelity work in backlog until its dependent functional route is integrated. Do not discard any M9 requirement.',
        reporting_contract=dict(
            report_done_remaining_and_next_observable_result=True,
            distinguish_build_readiness_component_verification_and_full_acceptance=True,
            test_or_function_counts_are_not_completion_percent=True,
            recalculate_after='First complete ordinary Login/selection/map scenario,or a material scope discovery',
            unchanged_range_reason='The new packet/Avatar integration closes a local dependency,not a complete functional domain'),
        forecast=dict(remaining_to_completed_functional_scope_ratio_approx=[2,4],ratio_is_functional_scope_not_effort_or_time=True,calendar_deadline=None,remaining_hours=None,
            reason='No defensible throughput sample for a complete integration scenario. Functional percentages do not imply the same ratio of time. Re-estimate after first complete Login/character/map scenario.'),
        script=dict(file=Path(__file__).relative_to(WS).as_posix(),sha256=sha(__file__)),M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    output=WS/'inventory/client455-progress-assessment.json';output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(estimate_percent=25,range=[20,35],weighted=[low,high],remaining_percent=75,domains=12,accepted_domains=0,registry=dict(status),client_units=182,engine_units=67,unresolved=0,report=output.relative_to(WS).as_posix()),ensure_ascii=False))

if __name__=='__main__':main()
