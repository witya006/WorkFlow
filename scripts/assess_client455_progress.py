"""Evidence-backed planning estimate, explicitly distinct from acceptance proof.

Weights and readiness ranges are engineering judgements, not measured function
coverage, time spent, test counts, executable size or a claim of equivalence.
"""
import collections,hashlib,json
from pathlib import Path
from compare_client_binaries import WS,pe

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(name):return json.loads((WS/'inventory'/f'{name}.json').read_text(encoding='utf-8-sig'))

def main():
    #Frozen scope weights sum to100. Change these only with an explained scope
    #revision; do not inflate readiness by splitting already completed work.
    rows=[
        ('startup','Запуск и конфигурация',3,65,80,
         ['Собственная PE,CRT/WinMain,Miles,окно/D3D;обычный запуск достиг создания и отрисовки Login'],
         ['Полный порядок startup/ошибки/профили/launcher и связь с экранами455'],
         ['client455-normal-link','client455-ui-startup-native','client455-startup-native','client455-startup-contracts-native']),
        ('data','Форматы и загрузка данных',7,50,65,
         ['RPK/EDF/helper SPT/BSP/EBP,модели/ANI и выбранные реальные ресурсы читаются'],
         ['Полная опись455,все загрузочные ветки/таблицы/ошибки и обычный bootstrap'],
         ['client455-world-checkpoint','client455-material-layout-checkpoint','client455-item-payloads-checkpoint']),
        ('world','Рендер и мир',12,35,50,
         ['D3D9,выбранные карты Bellato/Cora/Accretia,камера/свет/погода/материалы/эффекты вlab'],
         ['Полные visibility/camera/collision,ILevel/Empty/INS,refraction/FX/device reset и игровой мир'],
         ['client455-world-checkpoint','client455-world-frame-checkpoint','client455-material-shaders-checkpoint','client455-shader-text-checkpoint','client455-fullscreen-effect-native']),
        ('character','Персонажи и анимация',10,30,45,
         ['Исходные MESH/BN/ANI загрузчики,менеджеры,pose/skinning и выбранные normal draw маршруты'],
         ['Полный actor lifecycle,игровой выбор/экипировка/состояния/анимации и все consumers'],
         ['client455-normal-renderer-checkpoint','client455-normal-accounting-checkpoint','client455-animation-checkpoint']),
        ('ui','Ввод и интерфейс',10,20,35,
         ['GDI/Unicode текст,спрайты/атласы,часть окон/таймеров/input/hover'],
         ['Полные455 окна/layout/focus/IME/input,общий UI bootstrap и игровые связи'],
         ['client455-font-checkpoint','client455-gui-input-checkpoint','client455-item-icon-metadata-checkpoint']),
        ('audio','Звук',2,35,55,
         ['Miles init,selected tagged/RVP playback и звук выбранных эффектов'],
         ['Все sound events/3D/music/settings и полный lifecycle'],
         ['client455-tagged-audio-checkpoint','client455-rvp-audio-checkpoint']),
        ('network','Клиентская сеть',12,10,25,
         ['Codec/AES/пакеты/часть transport/rings;selected ordinary Nuclear receiver'],
         ['Полный35-handler dispatch,все реальные потребители,Close/errors/threads/timers'],
         ['client455-network-codec-checkpoint','client455-nuclear-receiver-checkpoint']),
        ('login','Вход и выбор персонажа',10,0,10,
         ['Обычный собственный клиент показывает реальную lobby/логотип/UI;окна перекрываются,455Login не принят'],
         ['Полный Title/Login/character selection/auth→world поток455 не пройден'],
         ['client455-progress-base-checkpoint','client455-network-codec-checkpoint']),
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
    normal,build,engine=load('client455-normal-link'),load('client455-normal-build'),load('client455-startup-engine-build')
    #A new partial build must not silently select an even older checkpoint as
    #current. Preserve the last completed partial checkpoint with its exact build.
    latest='artifacts/client455-progress/before138/inventory/client455-scene-capture-checkpoint.json'
    assert (WS/latest).is_file()
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
    report=dict(schema=1,assessment_date='2026-11-10',scope_version=1,scope='Full client455 behavior/source/build through M9,no graphics modernization,no server work',
        estimate_kind='Engineering planning judgement for known functional scope;not measured equivalence coverage',
        weighted_low=low,weighted_high=high,weighted_midpoint=(low+high)/2,communicated_point_percent=25,communicated_range_percent=[20,35],communicated_remaining_percent=75,
        confidence='Useful planning estimate;unknown455features and integration can change the remaining scope. No calibrated calendar forecast.',
        interpretation='Stage numbers are unequal sizes. M0-M5 completion is not five ninths of the full client. Existing legacy code receives no455credit without evidence.',
        domains=domains,complete_acceptance_domains=0,domain_count=len(domains),evidence=evidence,
        observed_facts=dict(client_compilation_units=182,engine_compilation_units=67,canonical_kernel_objects=build['canonical_kernel_objects'],unresolved_symbols=0,own_executable=normal['executable'],engine_sha256=engine['library_sha256'],references=reference,
            last_completed_checkpoint=latest,last_completed_checkpoint_is_historical_for_current_PE=True,current_work='138 ordinary Title/Login PARTIAL:real lobby/logo/UI rendered;overlapping windows;not455Login acceptance',
            ordinary_login_observation=dict(file='inventory/client455-login-frame-native.json',sha256=sha(WS/'inventory/client455-login-frame-native.json'),fresh_for_current_PE=True,frame=login['captured_frame'],capture=login['capture_result'],stage_state=login['stage_state'],ui_visually_inspected=True,ui_accepted=False,known_visible_problem='Overlapping legacy windows;full455layout/state/input/auth remains open',return_checkpoint='Return after the diagnostic capture;not necessarily the first frame'),
            existing_Create_proved_on_current_PE=load('client455-ui-startup-native').get('completed_existing_client_create',False) and load('client455-ui-startup-native')['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json'),full_Login_character_selection_world_flow_proved=False,normal_movement_combat_inventory_flow_proved=False),
        registry=dict(file='inventory/client-features.json',sha256=sha(WS/'inventory/client-features.json'),entries=len(registry['features']),statuses=dict(status),complete_denominator=False,contains_historical_and_overlapping_records=True,marked_current=[x['id'] for x in registry['features'] if x.get('runtime_gate_current')],note='Historical overlapping local records are not a complete functional inventory;do not use entry count as project percent.'),
        input_readiness=dict(available=['legacy0.7client/R3Engine sources','two pinned455x86reference binaries','installed455assets','working modern x86 build and IDA/HexRays'],
            reconstructed=['Character interface and multiple455source implementations'],
            missing=['original full455source/SDK','complete455feature/packet/state inventory','complete expected end-to-end scenario set/resource manifest'],
            build_blocking_unresolved_dependencies=0,byte_identical_output_required=False,
            assembly_status='Current selected client build is possible;this does not prove full455source completeness',
            behavior_specification_status='Incomplete:complete feature/packet/state/resource/scenario inventory is still missing',
            original455source_completeness_percent=None),
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
        forecast=dict(remaining_to_completed_functional_scope_ratio_approx=[2,4],calendar_deadline=None,reason='Four elapsed days and microscopic tests do not calibrate the larger integration tasks. Re-estimate after first complete Login/character/map scenario.'),
        script=dict(file=Path(__file__).relative_to(WS).as_posix(),sha256=sha(__file__)),M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    output=WS/'inventory/client455-progress-assessment.json';output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(estimate_percent=25,range=[20,35],weighted=[low,high],remaining_percent=75,domains=12,accepted_domains=0,registry=dict(status),client_units=182,engine_units=67,unresolved=0,report=output.relative_to(WS).as_posix()),ensure_ascii=False))

if __name__=='__main__':main()
