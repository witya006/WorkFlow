# Сверка готовности и текущих исходников — 10.11.2026

Проверенная база остаётся153/3296a413…;25%(20–35%),0/12полных областей.
Незавершённая154 не включена: текущий build_exit1,C2280cavatar.cpp:162,
Avatar copy/Clone после перехода к owned equipment state. Ранее154линковалась,
но runtime не проверена. Exact153 сохранена before154/manifest.json,53файла.
Далее: восстановить корректное копирование, собрать, проверить настоящий
player-owner путь;затем обычные appearance/selection. Никаких shallow owned copies.
Инструмент оценки теперь раздельно фиксирует preserved runtime,current failed
build и intermediate candidate;старый запуск не выдаётся за свежую154.
Свежая опись20:56:14:158.84GiB logical/43.19GiB unique file sizes,ошибок0,
удалений0. Это не точная физическая аллокация. IDA21aeaaf3 сохранена/закрыта,
idb_list0. Подробности:docs/progress-report.md иinventory/client455-progress-assessment.json.
Приоритет отчётов:изменение обычного клиента/standalone/ближайший остаток/
здоровье сборки/основание общей оценки. Полный455feature denominator ещё неизвестен.

# Текущая проверенная база153 — 10.11.2026

Own3296a413…/x86/entry17B430,182client/67engine/20kernels,unresolved0.
Gate inventory/client455-equipment-frame-checkpoint.json PARTIAL.
CMesh/CEquip получили реальные Animation/FrameMove/end transitions,
однократный dummy scan,always state иследование event magic за actor/Spine/yaw.
WAV использует equipment position,не actor position. Virtual120(kind2) false
для обоих текущих wrappers;byte4=2 не означает ground. Полный ground открыт.
Настоящие ANI/модели/Miles и21контролируемая ветка конца проверены.
Обычные6default owners Avatar теперьCEquip;основной12-slot CPlayerProc ещё
не подключён. Это зависимость полного персонажа,не закрытая appearance.
Create/Login/account3Avatar PASS. Login65/3015ms просмотрен:ожидание/Beta0.738,
безauth;профиль9first-chance прежний,unhandled0. Шесть render PNG равны150.
Полные player/condition/UI/particle registry/выбор/мир/gameplay/M9 OPEN.
Оценка25%(20–35%),0/12полных областей,без повышения.
Доизменений exact152 сохранена вbefore153/manifest.json,52файла.
Перед следующими ordinary edits snapshot154 сequipment-frame gate.
OwnedIDA57ba692a сохранена/закрыта ранее;новыеIDA sessions здесь не открывались.
Native jobs завершены. Оригиналы/server неизменны,входныеEXE не исполнялись.
Последнийполный storageaudit16:34:07 —156.14GiB logical/42.96GiB unique file
sizes,не замер кластеров. Первый153pool+280bytes,финальныеframe/renderpool0;
новые собственныеEXE/maps/results есть. Старые стенды не удалялись.
Доказательства research/client455-equipment-frame.md. Ниже сохранена история.

# Текущая проверенная база152 —10.11.2026

Own579bc166…/x86/entry179A40,182client/67engine/20kernels,unresolved0.
Gate inventory/client455-char-info-values-checkpoint.json PARTIAL.
УстраненыWORDусечение Gen/Force/Def и пустые Hit/Avoid setters. Настоящие
valueowners14..18 принимают fullDWORD/float;три ordinarybasic rows используют
ихприInit/childregistration/style/position. Nativeactualwindow/currentAvatar
caller PASS. 70000 сохраняется как70000,не4464. Полные455metric getters,
mount/buff/typedconditions/refresh и23fieldlayout всё ещё не перенесены.
LegacycomparativeWORDarray setters/upgradeannotations иCRT/FP/unsafe domains OPEN.
Primary12-slot CPlayerProc ownership/Animation/FrameMove/Render/providers,
particle registry,выбор/мир/gameplay/M9OPEN. Оценка25%(20–35%) неизменна.
Свежие Create/Login/account3Avatar PASS;Login65/3000ms просмотрен,
ожидание/Beta0.738,безauth;9прежнихfirst-chance,unhandled0.
Exact151runtime сохранена доизменений:before152/manifest.json,52файла.
Перед nextordinaryedits snapshot153 сchar-info-values gate. IDAe3deb20c
savedclosed/list0;nativejobs завершены,установок/удалений нет,originals/server
неизменны. ФинальныйsmallUIprobe:work/m9/5519fe61/char-info-values-001,pool0.
Последнийstorageaudit16:34:07,156,14GiB logical/42,96GiB uniquefiles,не новыйзамер.
Pcode-only26ownerfunctions сохранены рядомсraw длядальнейшего fullplayer bridge.
Доказательства research/client455-char-info-values.md;нижесохраненаистория.

# Текущая проверенная база151 —10.11.2026

Own d1e44bb9…/x86/entry179970,182client/67engine/20kernels,unresolved0.
Gate inventory/client455-premium-state-checkpoint.json PARTIAL.
Установлены owners ранее неизвестных condition providers:442440 —network
PremiumDWORD436028,40BCE0 —Avatar combat bonuses24712/24716. Настоящий
producer57/12 подключён к обычному dispatcher иowned CNetworkMgr/Avatar state.
Проверены включение/отключение/ignoredstatus,12ставок,DWORD иfloat-биты,
границы payload57/49/1;неписаные поля явноunknown. Native actualowners PASS.
Полные Premium UI/window/icon481/post-update condition refresh не подключены.
Full12-slot CPlayerProc/Avatar owner/Animation/Render/condition/UI,particle
registry,выбор/мир/игровойцикл/M9OPEN. Процент25%(20–35%) не меняется.
Свежие normalCreate/Login/account3Avatar PASS;Login65/3016ms просмотрен,
ожидание/Beta0.738,безauth.9прежнихfirst-chance,unhandled0.
Exact150runtime сохранена до изменений:before151/manifest.json,53файла.
Перед nextordinaryedits snapshot152 сpremium-state gate. IDAdfba038a savedclosed,
list0,nativejobs завершены,установок/удалений нет,оригиналы/server неизменны.
Новыефинальныеstaging pool0;полныйstorage audit по-прежнему16:34:07,
156,14GiB logical/42,96GiB unique file sizes,не новый физический замер.
Доказательства research/client455-premium-state.md;нижесохраненаистория.

# Текущая проверенная база150 —10.11.2026

Own0f671964…/x86/entry179660,182client/67engine/20kernels,unresolved0.
Gate inventory/client455-player-visual-checkpoint.json PARTIAL.
Полные ctor/dtor455 исправили ошибку146:12физических слотов,не13.
Index12 попадает в последующие поля;собственный явный отказ — известное
ограничение,не принятая эквивалентность небезопасной ветке эталона.
Перенесены visibility450810 и PRNG ctor/copy;24ветки видимости/3PRNG контракта
проверены с настоящими ресурсами. Frozen PRNG oracle взят из бинарника.
Свежие Create/Login/account3Avatar иdraw-regression прошли;6кадров совпадают149.
Login65/3016ms просмотрен:lobby/ожидание,Beta0.738,безauth;9прежнихfirst-chance,
unhandled0. Полное владение controller/Animation/Render/condition/UI в обычном
CPlayerProc/Avatar,полный particle registry,выбор/мир/M9 остаются открытыми.
FrameMove4513E0 реально пуст;семантика flag442440/bonus-owner ещё неизвестна.
Точная149runtime сохранена до изменений:before150/manifest.json,52файла.
Перед следующими ordinary edits сохранить150 вbefore151 с новым player-visual gate.
IDA6a9e2ee9 saved/closed/list0;native jobs завершены,установок/удалений нет.
Оригиналы/server неизменны. Оценка25%(20–35%),0/12полных областей без изменения.
Последний полный замер storage остаётся16:34:07:156,14GiB по путям/42,96GiB
уникальных файлов;не точное число занятых кластеров. Новые финальныеstaging pool0.
Доказательства:research/client455-player-visual.md;оценка:docs/progress-report.md.
Ниже сохранена история,её «текущие» формулировки относятся к своим версиям.

# Текущее продолжение149 —10.11.2026

Own f4e62e48…/entry179630/x86,182client-67engine-20kernels,unresolved0.
Gate inventory/client455-equipment-draw-checkpoint.json PARTIAL.
Source Render(default/matrix)/fade/alpha/overlay604 producer иqueue pose/owners
перенесены. Native actualmodel7/14/7draws,2659visible/changedRGB;6frames,
8realunit/siege metadata cases,keyDWORD>255,grade113notbool;queuealiases/Start/
retain/release/cap256 PASS. Base/overlay byte-equal preserved148fixture.
Обычные queue Clear/Render реально вызывают новыеentrypoints;secondarygeometry
теперь удержана PE. Full13-slot CPlayerProc/Avatar route ЕЩЁ НЕ ПОДКЛЮЧЁН.
Particle adapter используетlegacyg_Particle1024/5clones;targetvectors/6clones/
one-attempt failure. Ненулевыеparticle/entitydraws не проверены,полныйrendererOPEN.
Обычные Create/Login/account registered3Avatar PASS;Login65/3016ms просмотрен,
lobby/ожидание,Beta0.738.9прежнихfirst-chance,unhandled0;нетauth/selection/world.
Оценка25%(20–35%) неизменна,0/12полных областей;M6/M6F/M7/M9OPEN.
Далее ordinaryplayer/pose/animation/providers →appearance/selection;registry
миграция отдельнообязательна. Queue/source proof ужеесть,не повторять.
before149 содержитточную148runtime;16exact148sourceinputs дополнительно
сохранены по прежнимSHA вbefore149/recovered-source/. До новыхordinaryedits
snapshot150 сgateequipment-draw. IDA0a6749ce saved/closed/list0,jobsзавершены.
Native final work/m9/0fdac5c0/equipment-draw-001,newpool0;оригиналы/serverнетронуты.
Подробности:research/client455-equipment-draw.md. Нижеистория.

# Текущее продолжение148A — 10.11.2026

Переоценка по запросу пользователя: выбранная сборка обеспечена; полнота
исходников455/ресурсов/спецификации не установлена. Около25%(20–35%) —
плановое суждение по12фиксированным областям, остаток65–80%; не функция
числа проверок или номеров этапов. Полных областей0/12, полный маршрут
вход→выбор→мир→игровые действия не пройден. Надёжной датыM9 пока нет.
Свежая опись16:34:07:156,14GiB по путям/42,96GiB уникальных файлов,
ошибок0,удалений0. Подробные факты/остаток:docs/progress-report.md.

PROGRESS:реальный source/backend иновая обычная сборка,не повтор статуса.
Gate inventory/client455-grade-overlay-checkpoint.json PARTIAL.
Own03637d6a…/entry1771C0;engine4c6652a5…;182/67/20/link0.
4реальныхMST/DDS,UVshader9/10,c92,secondarygeometry92E140/92FBE0,
archive flag8E75D0/E0 иOpen/Exists перенесены;21fullfunc/2863instr/239CFG/5data.
Нативно:2104materialbytes/frozen oracle,shaderstate/lifecycle,layer6/malformed,
7actual geometrydraws/2659bright modelpixels/2659changedRGB иarchiveflag1/0/17.
Обычные source CreateEffect/DestroyEffect действительно CALL load/release.
НО secondary geometry linker удаляет изобычнойPE:нет player-render caller.
Полный mesh-object renderer иCPlayerProc/Avatar ещё отсутствуют;не завышать прогресс.
Create/Login/account3Avatar новойPE PASS;Login66/3031ms просмотрен,ожидание,
Beta0.738. Нетauth/selection/world.9старых first-chance,unhandled0.
Оценка25%(20–35%),0/12полных областей;M6/M6F/M7/M9OPEN.

Следующий148B:CMeshObject/CEquipObject Render()/matrix overloads/queue/shadow
→типизированные146controller/ANI/fade/conditions/effects/positions
→ordinary CPlayerProc/Avatar/frame/render/UI →Bselection.
Не повторять готовый21+27function аудит. Подробности research/client455-grade-overlay.md.
Archive sideeffect — НЕ SetReLoadState:проверены настоящие readers116E518,
первоначальное предположение исправлено до приёмки. Group publication включает
own adapter;полные455producer-writers ещё вM9backlog.

Диагностика queue527E70/528090/528190,shadow46CF10,ctors46BD60/46BE60/46DB30
есть в grade-overlay148-reference/additional-diagnostics.json (не полный ASM).
Queue physical stride4matrices/node при BlendNumloop:не заменить на30 молча.
Shadow делаетдвойной SetMaterial/SetMeshEffect. EffectList9298D0 keyDWORD,
несмотряна char впсевдокоде:caller push EAX и927790читаетDWORD.
Overlay604 неинициализирован ctor/init,нуженреальныйproducer;virtualgrade
46D8B0→payloadvirtual68 —отдельный путь. 4513C0 пустой/return1,не выдумывать defaults.

Перед ordinary edits:сохранить148 вbefore149;before148 уже содержит147.
Финальный GPUprobe work/m9/6d651ce9/grade-overlay-001;source/native/report/frame.
Послеосновного draw обязателен правильный caller state:одиночный overlay
давалпустойкадр. ПроверкаRGB исключаетложныйуспех. Чёрнаяполосаневходит вмодель.
Всеjobs завершены;IDA c6eeef7e savedclosed/list0;нет server/original изменения.
Ниже история,которая не переопределяет это продолжение.

# Текущее продолжение147/148 — 10.11.2026

Предыдущий goal-turn:PROGRESS — реальная поправка CCharacter,истинные native
иобычный runtime147;карта следующего полного renderer сохранена.
M9 определён:полный клиент455 без модернизации графики;не уточнять повторно.
Цель остаётся активной. Оценка25%(20–35%),0/12полных областей принято.

Последний runtime147:993978ffd58f5be96176f5ae03c36396048d04a27b4741c26582a5013268a5b1,
x86/entry175EA0;182client/67engine/20modules/unresolved0.
Gate:inventory/client455-character-palette-checkpoint.json.
Настоящий CCharacter20parts×30palettes/13dummy проверен:независимость2акторов,
рост/уменьшение/частичный отказ/освобождение. Avatar3локализации иregistered3Avatar PASS.
Own Create/Login PASS,кадр66/3031ms просмотрен:lobby/ожидание,не полный455UI/auth.
Девять известныхfirst-chance имеют тотже профиль145;unhandled0.
C2079 probe исправлен include datatable/cresourcedatamgr.h.
Account/Avatar maps теперь вуникальных run folders. Newassetpoolbytes0.

147 не подключает полный controller146. Следующий148 — полноценный typed mesh
renderer иordinary CPlayerProc/Avatar/slot/frame/animation/conditions/effects.
27fullfunc/1827instructions/213CFG иvtable176bytes равны2pins:
inventory/client455-equipment-render-reference.json;research/client455-equipment-render.md;
raw equipment-render148-reference/session.json. Не повторять готовый аудит27func.
ВАЖНО исправление:46D190 — Animation,НЕ Render;CEquipvtableAA8F64:
24→46E120,28→46E520,32→46DBC0,148→46E160,152→46E1E0,156→46E1A0,172→46D8B0.
46C200 — metadata getter. Render branches имеют отдельные scroll/time,
fade выполняется приRender,не выдумывать общий backend с потерей overloadразличий.
Далее проверить4overlaydescriptor×526bytes@113FC70/textures@11404A8,
их loaders/writers,engine SetMeshEffect/kit/unit/queue иполное подключение.
4513C0 targetпустой/return1:не придумывать здесь создание defaultmesh.

Проверенная147 уже сохранена вbefore148/manifest.json:49точныхфайлов.
Не перезаписыватьbefore148 иbefore146.
Research148 покаAUDIT_OPEN,не реализованная отрисовка. M6/M6F/M7/M9OPEN.
IDAeaa5fe38 saved/closed/list0;nativejobs завершены. Сервер/originals не менялись.
Ниже история;старые «current145»/«candidate147failed» больше не текущие.

# Продолжение после оценки — 10.11.2026

Главная задача следующего отчёта — наблюдаемый результат обычного клиента.
Плановая готовность25%(20–35%), остаток65–80%; 0/12полных областей принято.
Полные исходники/SDK455 отсутствуют. Сборочные входы выбранной конфигурации
обеспечены; полнота ресурсов и спецификации поведения ещё не установлена.
Документы:progress-report.md, roadmap.md, next-steps.md.

Последний проверенный runtime145/1a355372… сохранён в before146.
Кандидат147/993978ff… уже собран182/67/20/link0, но runtime не проверен.
Незавершённые изменения: CCharacter cache20parts×30palettes/13dummy.
Palette probe не компилируется: C2079/CCharResDataMgr в mainapp.h.
Не выдавать candidate за проверенную145. Три source-файла до изменения
сохранены в character-palette147-source-before; отдельный WIP-report в inventory.

Сначала исправить probe include и провести затронутые palette/Avatar/обычный запуск.
Затем соединять уже проверенные146компоненты с CPlayerProc/Avatar/кадром.
4513C0 SetEquipItemToDefaultMesh действительно пустой/return1 в455:
не придумывать default-substitution; найти настоящий producer внешнего вида.
Render diagnostics сохранены в character-palette147-reference/ordinary-render-diagnostic.json.
Они не все имеют полное ASM-подтверждение. Полные ctor/lifecycle ещё открыты.

IDA b6dd2ecb saved/closed/list0; активных native jobs нет.
Новая дисковая опись155,29GiB по путям/42,87GiB уникальных файлов; удаления0.
Сервер/originals не изменены. Большие неизменённые suites не повторять.
Следующий функциональный рубежB: правильный список/внешний вид/выбор;
послеB/C пересмотреть оценку и срок. Надёжного срокаM9 пока нет.
Ниже сохранена история; она не должна перекрывать это продолжение.

# Предыдущее продолжение146:числовая цепочка условий проверена

Gate inventory/client455-equipment-conditions-checkpoint.json PARTIAL_COMPONENT;
research/client455-equipment-conditions.md. Sourceclient455_equipment_conditions.h.
52fullfunctions/2323instructions/357CFG equal2pins;45newhelpers+7reusedcore
fromequipment-providers146.6dataregions:switches,weights,virtualslots pinned.
Native CPU source22realitems(21accepted),independent200modifierbytes/totals,
66smallfrozencontracts PASS/exit0. Actualdetached clone survives originalpayload
release andremoves special+upgrade. Only3assets/17921866logicalbytes,newpool7953.
Own fixture7953bytes,not originalEDF edits. Nativecallbacksare recorders,notUI/game.

Important numeric contracts:
- Modifiers atcondition16/216 are200bytes/7categories;forcepower index3,normal4,
  ranged5(category5/6/8/11),launcher6(category7). Do not reuselegacy5enum.
- Armour weights1..5=.23/.22/.18/.17/.20;legacythird/fourthswapwrong.
- Armour setpredicate virtual68→404EA0 isRUNTIMEpayload113,NOTmetadata160.
  Metadata160stillcontrols460680upgradability. Bothpaths testedasdifferent.
- Combine44C670 readsEMBEDDEDbaseplayerproc(CPlayer+5200),notcurrent44C630
  pointerat5196. TargetCPlayerconstructor confirms currentptr defaults toembedded.
- Specialhelpercase8signedbyte180,casttrunc/wrap thenowner virtual252. UIrefresh
  beforeweakpart;weakdefault1/tiesfirst. Siegephysicalmultiply beforeflatbonus,
  noforce multiply. ResetpreservesSFblock/setlevels/extra708..720.
- Mounteddefence456 uninitialisedbyctor/reset;requireproducer. Mountedpower452
  reset1,profilepower460/def464 reset1. Setvalues672..704 initiallyunknown,
  selectors664/668 start0. Don't silently assign guessedvalues.
- Noowner:outergatecanaccept/upgrade stillmutates;special/combine/weakskip.

Nextpriority:actualordinary CPlayerProc/CPlayer/Avatar/equipment/frame/render/
defaultsubstitution andregistered upgrades. Numericcoreand23positionhelpers
arealreadyimplemented;do not spend anotherturn re-auditing them.
Ownercallback:baseCPlayerAA8DDC/slot252→43E600 emptyverified;AvatarAA8C54/
slot252→41A060→board7/490EB0→490950/412020/463740 updatesSkillpayloadlevels.
AvatarRTTI:locatorB7A210/descriptorBCB0C0. Savedpcode+identities in
equipment-conditions146-reference/owner-bindings-diagnostic.json;thoseAvatar
calleesNOTyetfullASMconfirmed. GlobalAvatarUI41A8B0 andSF/potion/liveupgrades/
setproducers/consumers stillopen. Hostcallbacks cannot remainrecorders inordinary.
Useportrecipes forsourcecopies;do not reinterpretnewrows aslegacyITEM_DATA.
M6/M6F/M7/M9OPEN;ordinary1451a355372…unchanged. Estimate25%(20–35%),0/12accepted,
152overlappinghistoricalrecords. IDA71813681saved/closed/list0;nativejobsfinished.
PreviousgoalturnPROGRESS:typedsource/nativeproof;no server/inputEXEactivity.

# Предыдущее продолжение146:позиции эффектов проверены

inventory/client455-equipment-attachment-checkpoint.json PARTIAL_COMPONENT;
research/client455-equipment-attachment.md.23fullfunc/1953instructions/223CFG
equal2pins;21new +2reused7E0D10/7E22F0.17-entryswitch7E1134pinnedseparately.
Source scripts/native/client455_effect_positions.h. Real25bodymodels/25named
positions/5races/5cloakmagic/onearchivedAccretiaANI pass.28frozen coordinate
contracts coveryaw/scale/fallback/binding-index/NPC/default.1694assetpaths,
197618821logicalbytes,newpool0;ordinary145PE unchanged/no freshLoginneeded.

Important:playernamedbone usesparent/blendnames ofequip0..9 thenFIRSTactorcached
matrix fornode;returnedblendindex isnotused toselect contribution. NPCusesown
mesh names/matrices.17=Spine→Spine1;18default retainsactorposition.7/Damage/
weaponfallback usesworldbboxheight timesactorscaleagain,preserved455double-scale.
Some targetfailurebranches copyuninitialisedtemporary. OwnAPI reportsdefined=false
andmagicwrapperrejects;fullfailurefidelity explicitlynotaccepted. No inventedfallback.
Dummycache initiallyzero;7F2D60 fills255 andmaps effect1/2/fire1..4,lastwins.
Cacheproducer inordinaryframe isstillneeded. Headerrequiresactualnormaltypes.

Next:typed4411E0chain fromexistingfullprovider24proof,thenactualCPlayerProc/
Avatar/registered upgrades/frame/render/effectbackend integration. Do not re-audit
these23position functions. M6/M6F/M7/M9OPEN;estimate25%(20–35%)unchanged.
Registry151historicaloverlappingrecords. IDA5c1cdbca saved/closed/list0;
native90813 terminal0;noothernativejobs/noinputEXE/serveractivity.
PreviousgoalturnwasPROGRESS:sourceproviders+realnativeproof,notstatusonly.

# Предыдущая память —10.11.2026:оценка и146компоненты

Текущая обычная PE145 по-прежнему1a3553721149f8638812d636e2dfa3053d75b58a58c6310df72478050ab5670d;
equipment145gate current.182client/67engine/20modules/unresolved0.
Обычный Login —lobby/ожидание,не успешный вход. M6/M6F/M7/M9 OPEN.
ЦельM9 уже определена:полная приёмка клиента455 без модернизации графики.
Старый текст objective вget_goal не повод повторно спрашивать M9.

Оценка25%(20–35%),остаток65–80% известного функционального объёма.
12фиксированных весов,0/12полных областей приняты.150пересекающихся записей
реестра —не знаменатель возможностей. Статическая описьIDA37865функций
(включая1296library) сохранена,но полной карты переноса всех тел нет.
См.docs/progress-report.md иinventory/client455-progress-assessment.json.
Никакой датыM9 из этих процентов не следует.

146:добавлен отдельныйsourceMagic/sound ownership/cleanup/cloak looptracking.
Gate inventory/client455-equipment-effects-checkpoint.json;research/client455-equipment-effects.md.
22fullfunc/1489instructions/222CFG match2pins;realRPK/MagicSpt/Miles/nativePASS.
4magicstarts/4expires/4waverequests/3samplestops. Attachmentpositionpending,
ordinaryCPlayerProcfalse. Registry только отслеживаетостановку,неautoreplay.
Основные RVA6D3D0/6D660/3DBD50/4BD5E0/4BD6A0/4BD780.

Исправлена ошибкаheight:416940/RVA16940 читаетmetadataDWORD72meshID,
а не индексItemстроки. Headerhelperтеперь принимаетmeshID.
ANIprovider69cases/52ANI/16models/68poses/1expectedfailure/24liftsPASS.
4новыхреальныхdiscriminatorcases отличаютindexотmeshbits8.
Общийheaderзатронулcontroller;егоaudit/native/checkpointобновленыPASS.
Ordinary145PEне менялась,Loginне повторялся.

Общийпул достигNTFS1024links у280byteBBX. client455_asset_staging.py
теперь используетограниченныеownedрепликис900links;nativeповторPASS,+280bytes.
Репликаиrunоднафайловаязапись,оригиналотдельная/nlink1;capacitycheckpointсохранён.
Failedrunнеудалён. Свежаяstorageопись154.86GiBlogical/42.85GiBunique,
work/m9 26.70GiBunique/client-graphics-lab12.39GiB;группынельзяскладыватьиз-зассылок.
Старыефайлынеудалены,новыхполныхclientcopiesнет.

Следующийстык:полныйattachmentposition →typedconditions →actualCPlayerProc/
Avatar/registeredupgrades/frame/render/appearance →bootstrap/selection.
Подробнаяqueue толькоdocs/next-steps.md. Не повторятьуже доказанныеполныеbodies.
Rawattachmentdiagnostic7DD140/7E0B90 сохранён вequipment-effects146-reference.
IDA1049c6e2saved/closed/idb_list0;всенативныеjobsзавершены.
ОригинальныеEXE/серверы не запускались/неизменялись.

Ниже исторические записи. Их «current/next» относятся к своим прошлым версиям.

#146продолжение:реальные ANI/fade готовы;ordinary145не менялся

Новыйcomponentgate inventory/client455-equipment-providers-checkpoint.json;
research/client455-equipment-providers.md.24fullfunctions/2220instructions/
373CFG equal2pins.65realcases/48ANI/12models,64actualCResObject.Animation
posecalls,1expectedinnerfailure,20realownerlifts/fades PASS. Publicwrapper
returnsTRUE evenifinnerANIselectionfailed,targetbehaviorpreserved.
SourceRF455PlayerEquipmentObject implements6DF10/6D2F0/6D730 +6E220/6E3A0
andRF455_MountingHeight455(4B8F0/4B9B0). Do notrewrite theseagain.
Headerchangedclassstate;affected13slotcontroller/clone reference/native/gate
refreshed andPASS. Ordinary145PE1a355372…/engine137unchanged;no newLoginrun.
ActualitemAnimationEffect callback remainsrecorder,typedconditions andordinary
CPlayerProc/Avatar/registeredupgrades/render/selection notconnected. M6/M9OPEN.

RealAccretiaCloakDEFAULT/USE/UNUSE andsiegekitDEFAULT haveANImaximum0;notload
failure. Initialprobeassert(maximum>0) waswrong,correctoraclecomparesrealparsed
maximum. Failedrunwork/m9/476e69b4 retained. No productionforce-successfix.
ExporterpathsKoreanANSI:stripbasenameonbytesbeforeASCIIname decode.
Firstpool+53036735bytes,repeat0;1738assetrefs/219147433logicalbytes;nooldcleanup.
IDA4ce73361 saved/closed/list0;allnativehandles terminal0;noinputEXE/serveractivity.

Next146actualitemeffects:46D3D0/6D660→7E22F0→7D8FF0/GetMagicListFromID
and7E0D10 dummyposition,sound. Savedpcodecomplete inartifacts/client455-progress/
equipment-providers146-reference/item-effects-diagnostic.json;fullASMstillneeded.
406CB0=positionpointer80,4077E0=yaw108,NOTname/scale. IsExistFromMagicSpt
matches7D5A60 family. Existing EffectCore hasrealportedmagic scheduling.
Thenconditions4411E0 chain(fullASM24proof alreadycollected),ordinarycontroller/
GetNormalItem-upgrades/render/selection. Do notclaim equippedappearance yet.

FastfullASMworkflow nowavailable: nativeIDA basic_blocks +lookup_funcs +
func_profile → scripts/decode_client455_cfg.py ownedraw → independentIDA
instructioncount +allCFGbytes decodedbyinstalleddumpbin+bothpincomparison.
Analyze_batch maypreviewonly10asm/blocks despitefalse truncated flag;neveruse
itsASMpreview ascomplete. Newhelper accountswrappedlonginstructionbytes.
This avoidsdozensofsmallMCPdisasm callswhilepreservingfullevidence.
Overall25%(20–35%),0/12accepted;149overlappingrecordsnotdenominator.

## Предыдущий146контроллер иобычная145база

# Продолжение146 —компонент проверен,обычная сборка145

146PARTIAL_COMPONENT:typed13slotcontroller anddetachednormalclone implemented.
Gate inventory/client455-player-equipment-checkpoint.json;research/client455-player-equipment.md.
32fullfunc/1640instructions/225CFG equalbothpins;nativefullobject Item/Resource/
30actualcontrollerbasecreations/aliases8,9,10,11,12/bothwrapperoverloads/removal/
cloneconsumers PASS.32modelrecords/33GPUtextures throughsharedinputs;newpool0.
CurrentPE1a355372… andordinary145runtimegate unchanged;no new Loginrun necessary.

IMPORTANT:4539BD passes equipmentthis andplayerarg into453A80;itstoresowner588.
This is NOT Player.SetPrevAction despite misleadingpcode. Sourceclass exposes
GetOwner455/SetOwner455. Kind=metadata88,notheaderkind12.13storage/diagnostic12render.
Normalclone461CC0→404BC0→405CE0→405E70copieswrittenfields andreferencebyte;
no managerinsertion/nosource retain. Nativeconsumer verifies copiedIDs/data/name/
referencebyte afteroriginalslotrelease. Allocationpadding notnormalized.

Nativehost uses realRematchParent andsourceClone. Animation/fade/action/condition/
effect callbacks are recorders,NOT productionproviders. Controller not yetconnected
actualCPlayerProc. Keepordinaryruntime145current;do notreplacewithcomponentgate.
Next146phase:productionproviders46DF10/46D2F0/46D730/46D3D0 and4411E0typed
condition chain;thenCPlayerProc/CPlayer/Avatar/registered GetNormalItem/upgrades,
actual12slotframe/render/defaultsubstitution/ordinaryappearance andselection.
FullASM32raw saved;providerdiagnostics separate,441AC0needs nextcursor100.
Exact145before146(50files). IDA7c61237d saved/closed/list0;nativehandles terminal0.
No server/originalEXE activity.25%(20–35%),0/12fullaccepted,M6/M6F/M7/M9OPEN.

## Предыдущая актуальная база145 и ограничения

# Актуальная память —10.11.2026,145PARTIAL

Текущий gate:inventory/client455-equipment-checkpoint.json.
Own1a3553721149f8638812d636e2dfa3053d75b58a58c6310df72478050ab5670d,
x86/base400000/entry175F50/2299904bytes;182client/67engine/20modules/unresolved0.
Engine137 unchanged708c892e60c3bf7457389b40ac24b9a466958c9d232d9efaf497d1ac3232b870.
18fullfunc/630instructions/60CFG equal2pins.32realmodels/33GPUtextures/
30actualAvatar.SetDefaultItem calls/6retainedpayloads/0afterteardown PASS.
Strict meshlookup requires both LoadRealData return and m_Load;real type6/index32
metadata mesh00A10320 absent:Create true,mesh/bone null — preserved455quirk.
All33DDS requests resolve to realRFT. Resource group0meshes registered inmanager5.

Ordinary registeredreceiver uses GetDefaultItem455;6sourceownedtypedslots added.
FullCPlayerProc13slots/effects/rematch/fade/animation/draw,legacyGet/Unset/copy,
completeprivate644ABI andequippedappearance not accepted.
Affectedaccount/3Avatarclasses/currentPE PASS. OrdinaryWinMain/Miles/Login
frame70/3235ms viewed:lobby/waiting. Loopback received67bytes,RFresponses0,
authenticationfalse. Ordinarysuccessbootstrap/selection/world/gameplay stillopen.
Exact144before145(50files) preserved. Sharedfirstpool+57,508,702bytes;repeat0.
IDA7dd394bb saved/closed;nativejobs нет. Research:client455-equipment.md.

User requested a candid assessment after4days,not test totals. Current estimate
25%(20–35%),remaining65–80%known functional scope,0/12fullaccepted.
Sources/build dependencies ready for selectedconfiguration;fulloriginal455SDK0,
2pinnedPEavailable;fullfeature/packet/state/resource/scenario inventory incomplete.
Assessment is explicitengineeringjudgement,fixed12weights,not measuredcoverage.
Updated docs/progress-report.md and compactroadmap.md;historicalroadmap retained
inresearch/roadmap-before-assessment-2026-11-10.md. Do not treat oldhistorical
«next143/144/145» as currentwork. Do not reopenM9definition or developservers.

Next146:snapshot145 via snapshot_client455_runtime.py 146 client455-equipment-checkpoint;
thenactualPlayerProc13slots andappearance. Prioritize B selection,Cmap/control,
Dgameplay,EfullM9. ATitle/Login stillpartial. No newbulk159k unchangedsuites.
Reassess afterB/C. CalendarM9 notcalibrated. Current user-facingtask is assessment;
do not claimM9complete or inflate percent for eachsmallpartialcomponent.

## Сохранённая история и постоянные технические ограничения

# Память проекта

Текущий144 PARTIAL — inventory/client455-avatar-classes-checkpoint.json;
research/client455-avatar-classes.md. Own ea25eea5222039073ddf7e7823219336080ae298fd78afa0e99b38a65584f812,
x86/base400000/entry174FC0/2294784bytes;182client/20kernels/link0/unresolved0.
Engine137 unchanged. Before144 сохраняет точную143базу49files.
14fullfunc/460instructions/76CFG equal2pins;actual Avatar/165classes/3locales
и23textwidgets PASS. Numeric slot0/no slot1 меняеттолькоlabel4;string меняет
label4 thenbase/storedname5. Slot0/slot1exists меняетbase5;slot1 base0→label5
thenclass1→label4;slots2/3 namesunchanged. UIabsent storedname не меняется.
Copy32 zeroesall/copies≤31. CharInfolegacy Level/Guild/Attribute не затронуты.
Отдельные23valuewidgets пока НЕ отрисованыкак455layout. CreateClassSkill
callerесть,fullcallback ещёlegacy/unported;native tests board-absent Loginbranch.
Protected test access черезderivedProbeAvatar;public APIрадиtests не меняли.
SetClassName/SetAdvancedClassName455 inlined вproduction,не искатьотдельныйMAP.

Affected account/registered suite fresh:3real classindices fromCharacter165
примененыactualencrypted1/9receiver к3Avatar;UIabsent namesstayempty.
Actualordinaryreceiver CALL кnewsetter декодирован. Probeaccount теперьstages
Character/NDCharacter иAC44oracle. Fullappearance/auth не приняты.
Fresh WinMain/Miles/Login70/3219ms/640x500 viewed:lobby/waiting,nofatal;
ordinarysuccess bootstrap не исполнялся. Classstaging6refs/3.04MB/newpool0.
IDA01ef697a saved/closed;livejobsнет. Оценка25%(20–35%),0/12fullacceptance.

Следующий145:typed item/default/equipment→registered appearance,затем
remainingbootstrap/selection. Snapshot144 черезsnapshot_client455_runtime.py
145 client455-avatar-classes-checkpoint доизменений. LegacyITEM_DATA/CEquipItem
layouts отличаются:не cast455rows и не подменятьappearance syntheticмоделью.
Classskillcallback/полный23labelUI/остальныесценарии остаютсявbacklogM9.

## Историческая база143

Обновлено 10.11.2026. **143 PARTIAL; M6/M6F/M7/M9 OPEN.**
Gate: inventory/client455-character-tables-checkpoint.json.
Исследование: research/client455-character-tables.md. Оценка: docs/progress-report.md.
Own b41d50ffb5001c04a54dd0f16bd471c2bc0168e4b8757a52eca7a41067e0b4ec,
x86/base400000/entry174CD0/2293248bytes;182client/20kernels/link0/unresolved0.
Engine137 unchanged. Exact142 сохранён вbefore143.

Обычный CharacterDataMgr теперь читает PlayerCharacter→SF5→Store(selector)→
Character7+ND;реальные skill/force boards7/6packs×20,masteries12/24,SF100.
15fullfunctions/1737instructions/193CFG равны2pins. Четыре stock cases3locales
иодин changed-name DBCS fixture:14tables CRC/165class lookups/5typedSF wrappers
каждый PASS. Player5/Store1595(default),1651(_1);Character165/8/1999/36/324/81/648.
SFko/ru false,Storezh/ru default false,zhStore1 true;prefix/base сохранены.
Target Read1EE900 приshort не пишетdestination/cursor;CharacterND игнорирует
результат,ko203/ru682 failedreads. Не менять наmincounts/repair/resync.
Class lookup exactcase/code@12 илиindex@4,firstmatch;новыйaccessor probe-only.
Legacy CPlayerClass/Player/Monster/Store/SF_DATA consumers НЕ перенесены,
SF countslegacy0;boards выделены,ноне заполнены455items/classskills.

Fresh WinMain/Miles/Login70/3219ms/640x500 inspected:lobby/waiting,
unopenedpanels hidden,legacy label stays;no fatal. Success-response bootstrap
иselection/appearance не приняты. Неизменённые142 suites не повторялись.
Shared staging35refs/35.2MBlogical,+8.51MBnewpool/4.57MBadopt.
IDA5fe0894d saved/closed/list0;nativejobs нет.

Следующий144:actual Avatarclass setters/names,потом equipment/appearance и
остальнойbootstrap/selection. Raw143 содержит diagnostic Avatar pcode,
ноselectedfullASM/CFG дляsetters/UI ещё нужно собрать. MAX_AVATAR_CLASS_NUM=4.
Target412140:slots0/1 имеютразные обновленияимён;412580 storedname@24196
толькоеслиglobal1028B7C UIexists,412640 меняеттолькоUI. TargetUI66337023labels,
legacyCharInfo14labels:slots4/5 тамLevel/Guild,не писатьtargetиндексывних.
Не cast455raw вCPlayerClass. Full actor/item/UI/skills/bootstrap ещёopen.

Оценкаостаётся25%(20–35%),0/12 fullacceptance. Измерять A→B→C→D→E;
неизменённыеbulk suites не повторять ради счётчика. СрокM9 не калиброван.

## Историческая база142

Обновлено 2026-11-10. **142 PARTIAL; M6 открыт.**
Gate: inventory/client455-item-bootstrap-checkpoint.json.
Проверка: scripts/Invoke-Python.ps1 scripts/checkpoint_client455_item_bootstrap.py.
Доказательства: research/client455-item-bootstrap.md.
Последний commit до142: 72f7041 (Resource141).
Подробные старые факты: research/project-memory-before139.md и research/ по участкам.

## Цель и ограничения

CLIENT ONLY: поддерживаемые исходники и собственный RF_Online.bin с полным
функционалом/поведением закреплённого455. M9 уже определён: финальная приёмка
без модернизации графики. Старое goal-описание про M4/неизвестныйM9 не применять.
M0–M4/selectedM5 достигнуты; M6/M6F/M7/M9 OPEN; M8 не требуется.
Server только читать reference; не изменять/строить/восстанавливать даже копии.
Originals immutable; input EXEs никогда не выполнять. Работа под work/.
LocalGit, no push/remote/publication. Не делегировать без прямой просьбы.

## Текущий142

Own PE f0114c80b2a08bdb313113368c729b4a7cb4b4c0c05cdc193ee368edf627f2d1,
x86/base400000/entry172C30/2283520bytes.182client/20kernels/build/link0/unresolved0.
Engine137 SHA708c892e60c3bf7457389b40ac24b9a466958c9d232d9efaf497d1ac3232b870
unchanged. Обязательный normal-consumer proof обновлён.
Primary SHA b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
secondary46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.

Обычный Login вызывает CItemDataMgr.LoadBootstrap455:cash→set→Item47+ND.
Порядок подтверждён декодированными CALL/JMP в production PE.
Cash selector -1/default иначе полный DWORD decimal suffix; ND overlay DWORD16.
При cashND count mismatch/отсутствующем ND base сохраняется; outer продолжает.
Все11 country vslot160=true,включаяKorea;не выводить это только изTaiwan.
4newfullfunctions/257instructions/27positiveCFG regions равны2pins;
RVA1F8EC0 cash,2089E0 set,4329B0/42C490 profile true methods.
Existing588instruction Item1FEE30 evidence089 переиспользован.
Raw artifacts/client455-progress/item-bootstrap142-reference/session.json.

Six real full-object runs:ko-default/zh-default/ru-default/zh1/zh10/ko1.
Cash1000rows,set1373,Item47/76049rows;independent alltable/name/description/
work arrays CRC/consumed bounds PASS. Twelve real CBoardObject/payloads каждый:
borrowed row/name,clone retains,last owner erases. Receiver world-entry supplies
selector through actual12-byte decoder,не реальная auth.
Russia cashND count mismatch иabsentkoND_1 дают false,base retained,Item PASS.
Новый GetData455 accessor сейчас удержан только probe;LoadData inlined вbridge.
Legacy ITEM_DATA/derived CBoardItem/CEquipItem/Avatar default/equipment consumers
НЕ перенесены. Нельзя cast455raw встарые layouts или заявлять appearance/selection.

Fresh WinMain/Miles/providers/ordinary Login PASS:work/m9/f0114c80/login-frame001,
created1/loaded1,frame70/3234ms/640x500,Renderreturn/exit observed,no fatal.
PNG276eb78c… просмотрен:lobby/ожидание,unopened panels hidden.
Обычный success-response bootstrap в этом запуске не выполнялся.
Wide unchanged account/resource/graphics suites не повторялись.
Exact141 snapshot49files before142;140before141 и139before140 сохранены.
IDAb958e3d1 saved/closed/list0;nativejobs нет.

## Следующий143: character tables/classes и выбор персонажа

Target53D0F0 result0/state6 calls1E7BE0. Initial item142 иResource141 интегрированы;
остальные таблицы/связи ещё legacy/partial. Далее PlayerCharacter,SkillForce,
Store(selector),Character7 иND/NDW overlays/class-tier lookup/names.
Переиспользовать RF455ItemDataStore.character иRF455SkillForceData;не cast raw
вlegacy CPlayerClass. Class setter412140 отличается отстарого helper.
Затем typed item/Avatar equipment consumers иordinary appearance/selection.
Не bypass waiting/не force success/не писать serverlogic.

Полный порядокbootstrap:ItemCash/ItemSetEffect/Item/Resource/character tables+
boards/Quest/EventShip/NDMsgMonster/ItemTimer/country slot296/NDMsgEvent/
EventSound/SpecialStore/ItemCollection/Map/5default effects/Avatar finalization/
registered request. Рольslot296 неизвестна;ItemTimer/SpecialStore не Exp/Combine.
Pcode root:artifacts/client455-progress/registered140-reference/session.json;
Resource141 raw содержит полный ASM root. All remaining loaders need own evidence.
Затем ordinary world/avatar/control/movement/collision→combat/items/chat/NPC/social.

## Сохранённые реальные участки139–141

World-entry request58/reply12 уже интегрированы. State m_worldEntry455 содержит
cashShop/npcShop/quest selectors (-1 илиuint16). Request keys XOR mask
(k0+k2-k1-k3)*12AB34CC modulo32,version126455,signature33bytes.
Reply result/grade/seen/selectors пишутся даже приerror;ReceiveResponseMsg доkind.
Registered request1/8/reply1/9,payload506=header14+3×164.
Name17/serialDWORD17/race21/slot22/class5@23/level28/dalant64@29/gold64@37/
baseShape45/equipment8×signed16@49/upgrade65/reserved83@73/lastConnection64@156.
Level0→1/skipTutorial0,else skip1;latest signed64 localmax0/strictgreater.
Count0 retainsactors/latest;parts1,2,3,4,5,7,6,8;class/appearance consumers open.
Standalone account skipsWinMain:explicit g_bIsWindowed,не путать сenginewrapper.

Resource.edf9groups/30623rows:1267bones/10484meshes/18872ANI. Registered1267/
10483/18872:oneNPC20483 missingparent skip. Five real playerBN shapes30/25/29/38/30
andfirstmeshname5;real playerANI fromRFS loaded. OtherANI metadata only.
Legacy260/328/244/84 rows match;bounded preflight/missing-player/shape checks added.
Own GetResourceList missingreturn fixed;otherlegacy getters/errorUI/quit open.
1120checked unresolvedrefs503BN/592BBX/25ANI afterloose/RFS lookup;not full asset
inventory or proof each path required. Seven archived members resolved.
Character manager keeps exact case/separate records;ANI normalizes/deduplicates.

## Оценка, память и работа

Около25%,диапазон20–35%,остаток75%:engineering estimate12systems,не tests/bytes.
0/12 full acceptance;144historical/overlapping records не знаменатель.
A Title/Login;B auth/selection;C world/control;D gameplay/NPC/social;E fullM9.
Отчёты разделяют:собирается/проверено отдельно/работает обычно/полностью принято.
Сборочные зависимости обеспечены;fullsource455/SDK0sets,referencePE2.
Feature/packet/state/resource/scenario inventory ещё неполон.
Не повторять159k unchanged suites. Проверять затронутое/обязательные зависимости.
CRT/FP/failures backlog сохраняется,но не заменяет связанный игровой сценарий.

VS2026/MSVCx86. Python scripts/Invoke-Python.ps1 file.py,не-c/-m.
Native/GPU sequential;timeout не termination,poll тотжеhandle.
IDA ownedworkcopies/sessioneverycall/ASM≤100+allpositiveCFG/tails/save-close.
MCP rawchunks≤20k;rg --files --no-ignore для ignored work,перед неизвестнымpath.
Не использовать PowerShell path wildcards вrg;filter через --glob.
Shared staging толькоownedcopies;никакихhardlinks originals;configs/exes private.
BN/BBX/ANI/MSH/RFS добавлены immutable. Resource firstpool+53.1MB,повторы0.
Item142 newpool509445bytes/adopt46.2MBexistingowned,29refs/165MBlogical.
Storage oldsnapshot150.95GiBlogical/42.29GiBunique,старое не удалялось.
Before cleanup verifyevidence/inputreachability. Windowsidentity os.stat(path),
неDirEntry.stat снулевыми inode/linkfields.

## Движок/UI: не потерять ограничения

FullFraction/particle/BBoShasi/INS/Empty/visibility/collision/device lifecycle OPEN.
Scene targets137/capturehelper есть;ordinarycapture caller не доказан.
Capture8CE020 retainsurface ref/ignoresHRESULT;толькоlab компенсирует.
SyntheticPerbMap не455asset;wrapper640x500/viewport640x480 open.
CLevel.SetViewMatrix неinverse/viewproj,publishcamera отдельно;temporaryCLevel
должен переживатьactivemap,destructor freesglobals.
Material526/serialized46/MAX2048;specular_flikering typo/ORbits сохранять.
ShaderPS6 fourthlane/unownedstack lanes не выдумывать.
FullTitle/movie/factory4/explicitnext OPEN;legacyfactory3/modulo остаётся.
Title557F80 exit/jump unconditional,не включатьdeadfade. RealAVI/CcrLogo.dat есть.
Login init5401D0 state6normal/7logout;country slot284false всех11,не force reconnect.
Create53BB20 brokenIDB/JUMPOUT/falseCRT annotation:читать реальныеinstructions.
Full455UI10windows/systemsprite5/layout/focus/input OPEN.
RootAdd138 Show(FALSE)/AlwaysTop ужеперенесён. Legacylabel0.738 косметически не менять.
