# Ближайшие действия — только клиент

Обновлено 2026-11-05. /Goal — M9: финальная приёмка клиента455 без модернизации
графики. M8 не требуется. Критерии docs/client-acceptance.md. Серверы/БД/GoMMO server
logic не разрабатывать; серверные исходники только читать как справочник.
Оригинальные EXE не исполнять, изменения только в собственных копиях/work/.

## Текущая точка

M0–M4 выполнены в описанных diagnostic compile пределах; M5 закрыт для выбранного
helper/interior/weather участка. M6 в работе. M6F/M7/M9 открыты. Compilation,
загрузка модели и uploads не являются финальной приёмкой клиента.

Последний unit — renderer owner032: source constructor/device binding/destruction
и typed load/draw adapters. Реальная модель проходит через owner managers/pools/
shaders;2frames совпали component/fullclient. Провереныconstructor patterns,caps
gate иRelease order;ownheap/COM/Dmalloc0. Lab197TUs,normal293MTobjects/runtime
прежний кромеtimestamps. Gate inventory/client455-renderer-owner-checkpoint.json;
research/client455-renderer-owner.md. Normal owner API покаunused/stripped.

Следующая работа — normal typed model/animation/ChInterface facade вместе с
движковым D3D9 device path, используя готовые source owner/load/pose/draw/frustum.
Нужны реальные normal callers: не отдельная подмена одного старого менеджера.
Не повторять уже восстановленные ядра.39oldSDKfunctions/150field candidates
остаются ориентиром;full camera/actor visibility/CRTtrig/reset/errorUI ещёоткрыты.

Предыдущий unit — scene frustum031: producer/AABB source подключены к обычным
SetCharacterClipping/ProcessClipping.72matrix/204AABB cases/12FP modes и9actual
CResObject cases прошли; device/Platform01 кадры прежние. Normal293MTobjects,
lab196clientTUs. Gate inventory/client455-frustum-checkpoint.json;
research/client455-frustum.md. Большие неизменённые runtime suites не повторялись.

Normal interface/caller inventory выполнен:139calls/45symbols, из них39functions/
131calls ещё старыйSDK.150field tokens требуют typed review; indirect calls иSDK
internal closure не покрыты. research/client455-normal-character-interface.md.
RTMOVIE macro выключен согласно оригинальным CPP flags, не включать вслепую.
9238A0 — уже source lazy loader, его wrapper92FBA0 не доказывает culling.

Очередь после031 уточнена выше. Согласованный typed normal model/animation/Character
owner иD3D9 device lifecycle port использует восстановленные loading/pose/draw,
проверить оставшиеся normal API/field consumers по инвентарю. Не подменять один
AnimationManager и не rawcast old/new layouts. Затем подключать реальный
model→pose→draw/camera путь в обычном клиенте. Это воспроизведение455, не M8.
Полный actor visibility/simple92E140/CRT/undefined scratch/device reset/unwind
и deployment failure policy остаются открытыми. Делегирование только по запросу.

Предыдущий unit — Character main draw030: main92E5F0/effect stage/transparent
queue+flush/batch capture+flush/CPU retained/shadow теперь source,8APIs.16targeted
scenarios/185assertions и2real model frames прошли standalone/fullclient,COM/heap/
Dmalloc0. Material проверен настоящим red GPU-pixel. Normal291MTobjects/runtime
прежний кромеtimestamps,lab195TUs. Gate inventory/client455-character-draw-checkpoint.json;
research/client455-character-draw.md. Большие неизменённые runtime suites не повторялись.

Историческая очередь после030 уточнена выше. Незавершённые draw contracts:
high-level visibility/simple92E140/device lifecycle. Original first-bump material/zero-weight CPU
scratch undefined,source zero seeds явноотличаются; modernMTsin/cos — explicit lab
provider,неoriginalCRT bits. Этиграницы не считатьзакрытыми при normal integration.
M6/M6F/M7/M9 остаютсяоткрытыми.

Предыдущий unit — Character draw primitives029: source states/selection/material/
skinpalette/shared submission. Real BELPHEGORHOLIDAY/ANI/3textures:46geometry parts,
44skinned,кадры160/2160; компонент и полный client lab дали одинаковые кадры.
4analytic buffer draws также прошли;596targeted assertions,COM/heap/Dmalloc0.
Normal291MTobjects/runtime прежний, lab194TUs; нет новой установки или bulk rerun.
Gate inventory/client455-draw-checkpoint.json;research/client455-draw.md.
Сразу продолжать full92E5F0/effect program choice/material-alpha/scrolling, затем
sorted930A40/deferred92D9D0/CPU92DB60/shadow930120/wrapper culling. Raw draw-*.json
сохранены; у draw-main914lines первая страница752, tailoffset740. 92D3E0/92D330/
92D6C0 требуют instructions: decompiler prototypes неверны. В lab сейчас вручную
выбран basic shader/CullNONE/камера для просмотра, это не full game draw acceptance.
После полного source draw — совместный typed normal model/animation/renderer port.

Предыдущий unit — Character shader bootstrap028:12SHO/12VS+3PS/2declarations на
pinnedD3DX9_36 и realD3D9HAL.119checks standalone/fullclient,7APIs и matching
harness frame;COM/Dmalloc0. Это shader resources,не fullCharacter draw.
Gate inventory/client455-shaders-checkpoint.json;research/client455-shaders.md.
Normal unused APIs stripped/runtime прежний;lab193TUs. Большие наборы не повторялись.
Уточнение очереди: old ChAnimation280/name4/ID260 против455284/name5/ID264;
model776/mesh1072 против1188/5803. Переключать один CUnity manager нельзя.
Сначала fullCharacter draw/constants/palette/material и typedmodel/renderer путь,
затем normal integration вместе с animation consumers; без rawcasts/shadow records.

Предыдущий unit — source коллекция AnimationManager4028:11APIs регистрации,
поиска/кэша/удаления/владения.87targeted checks/один real ANI прошли component
и полный client lab; heap/Dmalloc0. Normal runtime равен loop-clock-final после
исключения timestamps, normal CUnity/ChAnimation ещё legacy; lab192clientTUs.
Gate inventory/client455-animation-manager-checkpoint.json;
research/client455-animation-manager.md. Графические/clock/bulk suites не повторялись.
Далее — typed CUnity/CAniData/actor transitions. Для worker935450 не найден caller,
оба проверенных importer mode синхронные; не считать worker доказанным блокером.

Предыдущий unit — source elapsed clock в обычном R3EngineMT: усреднение DWORD,
ограничение/scale, real time, toggles, QPC init/fallback/duration. 144 состояния
в12FPmodes/3provider сценария прошли; полный client lab вызывает настоящий
R3CalculateTime и затем CResObject, результат frame309. Короткая Platform01/device
регрессия прошла с прежними frame SHA. Normal291MTobjects, lab191clientTUs.
Gate inventory/client455-loop-clock-checkpoint.json;research/client455-loop-clock.md.
RTMovie scale consumer/full actor lifecycle/normal455ABI/renderer ещё открыты.
Original scheduling/timer trace не наблюдался; runtime намеренно изменён.
Большие неизменённые наборы не повторялись.

Предыдущий unit — численный расчёт кадра и CAnimation ctor в обычном клиенте.
Два source API из R3EngineMT вызываются в настоящих CResObject/CAnimation:
три callsites подтверждены. 612 численных случаев/12 FP modes и 16 actual actor
сценариев прошли; Platform01/device 2cases/69checks, прежние frame SHA.
Normal290modernCOFF/MT, lab190clientTUs. Runtime намеренно изменён timing/ctor
вызовами; это не полное поведение 455. Known84 secondary defaults восстановлены,
normal actor binding/full lifecycle и upstream elapsed clock ещё открыты.
Gate inventory/client455-animation-timing-checkpoint.json;
research/client455-animation-timing.md. Неизменённые большие тесты не повторялись.

Предыдущий unit — secondary state84/global28/5effects91E270 вsourceFrameMove:
36whole-state scalarcases/2actualCoraBN/6updates component/fullclient;6source APIs,
heap/Dmalloc0. Связаннаяpose проверка11pairs/132updates прошла,прочиеoldbulk suites
неповторялись. Gateinventory/client455-secondary-checkpoint.json;
research/client455-secondary-motion.md. Lab189TUs,normalruntimebytes прежние.
CRTstatic__CIsin не восстановлен:lab явноmodernMTsin;source требуетsineFloat
backend. Не выдавать это за full math/normal runtime/animateddraw acceptance.

Предыдущий unit — source pose evaluators иосновные FrameMove phases:
11realBN→MESH08pairs/22ANI/132updates/2298skin matrices;132selectedkey cases,
8analytic scenarios в12maskedFPmodes. Component иfullclientownentry равны;
5sourceC APIs caller/archiveproof,heap/Dmalloc0. Это CPUpose,неanimateddraw.
Gate inventory/client455-pose-checkpoint.json;research/client455-pose-source.md.
Normal180client/289modernCOFF/MT,lab188clientTUs;normal source APIs unused/stripped,
normalruntimebytes кромеtimestamps прежние. Старые runtime suites не повторялись.

Предыдущий unit — ANI/rawIO/record284/lifetime/attachment/Character dispatcher:
14513CPU/15181HALchecks standalone/fullclient,27ANI1062tracks/6Python tests,
22real ANI matches на11BN→MESH08парах794parts/660HALuploads.13sourceC APIs
проверены. Normalconsumers/pose/shaders открыты. Stickyflags/cumulativecounter/
one rawleak сохранены;harness чистит leak только после явного наблюдения.
Gate inventory/client455-animation-checkpoint.json;
research/client455-animation-dispatch.md. Current legacy14896/manager1138/
Platform01-device69passed,framesunchanged. Normal289modernCOFF/MT,187clientlabTUs.

Предыдущий connected unit —legacyMSH/BN importer/converter/weights/indexing/MTG:
66627capture/14896HALchecks standalone/fullclient;34runs/972parts/832HALuploads,
2CPUretainedparts.12actualBN→MESH08pairs393parts/276uploads. Source8runtime APIs+
reader/delete chain verified,ownheap/COM/Dmalloc0. BN теперь построен source,
а не только names изgolden. Normaldispatcher/ANI/animation/shaders открыты.
Gate inventory/client455-legacy-runtime-checkpoint.json;research/client455-legacy-model-runtime.md.
Промежуточный reader/lifetime:4606standalone checks,6Python tests;
research/client455-legacy-model-reader.md. Не повторять закрытый parser reverse.
Предыдущий connected unit — Character455 record1188/manager4148/cache/rawMSH/refresh.
850CPU/1138HAL checks, полный клиент даёт те же1138;12models/393parts/276uploads/
59texture pointers, ownheap/COM/Dmalloc0.13 APIs вызваны из actual lab TU иsource lib.
24bodies equalbothpins; ctor1188bytes — oracle из92записанных инструкций+констант.
Реальный MESH08 из собственного RFS и11loose моделей проверены до парсинга по байтам.
Normal game dispatcher покаlegacy. Research: client455-character-manager.md;
gate inventory/client455-character-manager-checkpoint.json исторический;
текущие PE identities вновомlegacy-runtime checkpoint.

## Очередь M6 → M9

1. Восстановить full Character455 draw/mesh submit/state/constants/palette/material
   и shader selection, затем связанный normal typedmodel/animation/renderer путь.
   Bootstrap028 готов на HAL; не подменять только CUnity manager из-за разных ABI.
   Для этого же пути завершить FrameMove fidelity:originalstatic__CIsin473340/SSE/default contract,
   полный actor lifecycle/secondary binding, transition consumers и
   normal CUnity/CAniData calls. Коллекция AnimationManager и record ownership
   готовы в027; async worker уточнять по реальным callers, не по наличию тела.
   Численный producer/known84 defaults готовы в025,
   elapsed clock в026; повторно их не исследовать без новых фактов. RTMovie scale
   caller ещё открыт, весь cinematic subsystem не объявлять восстановленным.
   Основныеpose/skinmatrix иsecondary source готовы;secondary requires mathcontext,
   missingbackend возвращаетRF_POSE_SECONDARY. Raw584secondaryinstructions+borrower
   7CD430cached;неповторятьэтотreverse. State84borrowedfromactor+500→model1184,
   globals28sharedacrosscharacters. CRTlabbackendmodernsin явнонеbitparity.
2. Далее skinning/draw,455declarations/shaders и normal typed consumers.
   Legacy parent/count/mesh268/528/532 отличается от455272/532/536; rawcast запрещён.
3. Восстановить полный D3D9renderer455/lighting/effects/device lifecycle вместе
   с consumers Character. Это обязательное соответствие M6, не модернизация M8.
   Продолжать другие M6 клиентские области по feature/scenario matrix: UI/input,
   клиентская сеть, game states, предметы/действия, звук и остальные выявленные.
4. M6F: полный реестр возможностей и расхождений; сценарии с одинаковыми ресурсами,
   настройками, входами и состояниями. Закрывать пробелы по client-acceptance.md.
5. M7: воспроизводимая поддерживаемая сборка, зависимости и проверки.
   M9: финальная приёмка функционала/поведения455 без модернизации графики.

## Уже выполнено — не повторять без новых входов

- Mesh lifetime и связанный MESH08 route:9953CPU/10021HAL,12pairedfiles/393parts,
  276uploads/59bindings. Последняя регрессия10021 прошла на текущем lab.
  research/client455-model-pipeline.md; inventory/client455-models*.json.
- Shared buffers36/64/INDEX16/first-fit/rebase/bind/lifetime:158336CPU/159173HAL,
  4synthetic draws. research/client455-shared-buffers.md.
- TextureManager/RFS/DDS/mips/fallback/lookup/cache:333CPU/8440GPU,80profiles,
  68texturepairs/137renders/97parts/59bindings. research/client455-character-textures.md.
- Mesh ctor/header/matrices/material requests:14562checks/12FP modes;
  parent/bone bindings2237checks/12pairs;31–50pointer/matrix overlap сохранён.
  research/client455-mesh-runtime-source.md иclient455-mesh-bindings-source.md.
- MESH08 framing:858files/12090parts lossless tooling roundtrip;
  6304native checks/1309guarded truncations/7Python tests.
  research/client455-mesh08-format.md. Не повторять858file/header census.
- Legacy InitVertex/CPU bindings:245+6732checks/144cases/12FP modes,
  4COFFtests/2actualSDKLoadRealData callers. research/character-init-source.md.
- Clock1443/map-time314/weather703/resource30, commands432cases/2628checks
  и20actual input checks прошли на предыдущей lab revision. Подробности в
  research/client455-clock-source.md, client455-map-time-source.md,
  client455-time-commands-source.md, client455-weather-source.md,
  client455-resource-io-source.md. Это исторические результаты, не повторять
  массовые проверки без изменения соответствующих входов/кода/неразрешённого риска.
- Текущие Platform01/device2cases/69checks,0errors/warnings/COM/Dmalloc,
  прежние frameSHA сохранены: inventory/client455-legacy-runtime-graphics.json.
- M5 historical gate: verify_client_m5.py --saved. Старый13case report иего
  immutable lab сохранены. Текущую scoped GPU regression не подменять полным M5.

## Воспроизведение последнего модуля

Python черезscripts/Invoke-Python.ps1:
build_client455_pose.py →probe_client455_pose.py →build_client455_secondary.py →
probe_client455_secondary.py →prepare_client_build.py →
probe_client_character_build.ps1 [обычный/-HelperLab] →
probe_client455_secondary_client.py →probe_client455_pose_client.py →
checkpoint_client455_secondary.py. Normalsnapshotcharacter455-secondary.
Повторять только затронутые области;неизменённыеIO/texture/GPU/manager suites исторические.

Предыдущийpose unit:

Python через scripts/Invoke-Python.ps1:
prepare_client455_pose_inputs.py →build_client455_pose.py →probe_client455_pose.py →
prepare_client_build.py →probe_client_character_build.ps1 [обычный/-HelperLab] →
probe_client455_pose_client.py →checkpoint_client455_pose.py.
Normal snapshot character455-pose-final. Старые suites не повторять без риска;
их исторические gates иimmutable snapshots сохранены. Текущийpose gate не заявляетGPUdraw.

Предыдущий модуль ANI:

Python через scripts/Invoke-Python.ps1:
test_ani455.py →audit_client455_animation.py →build_client455_animation.py →
probe_client455_animation.py [--gpu] →prepare_client_build.py →
probe_client_character_build.ps1 [обычный/-HelperLab] →
verify_client455_animation.py [--lab] →probe_client455_animation_client.py.
После scoped legacy/manager/Platform01 regressions:checkpoint_client455_animation.py.
Normal snapshot character455-animation immutable;normal runtimebytes кромеtimestamps
равны character455-legacy-models. Не повторять unchanged massive corpora.

Предыдущий модуль:

Python через scripts/Invoke-Python.ps1:
audit_client455_legacy_runtime.py →prepare_client455_legacy_runtime_inputs.py →
build_client455_legacy_runtime.py →probe_client455_legacy_runtime.py [--gpu] →
prepare_client_build.py →probe_client_character_build.ps1 [обычный/-HelperLab] →
verify_client455_legacy_runtime.py [--lab] →probe_client455_legacy_runtime_client.py.
Послеmanager/model/Platform01 regressions:checkpoint_client455_legacy_runtime.py.
Последнийпроверенный PE:186clientlabTUs,289normalmodernCOFF/MT. Обычныйsnapshot
character455-legacy-models immutable,normalruntimebytes equalprevious excepttimestamps.

Предыдущий модуль manager (исторический gate,актуальныеregressions отмечены выше):

Python — исключительно scripts/Invoke-Python.ps1:
test_character_ctor_oracle.py → audit_client455_character_manager.py →
build_client455_character_manager.py → probe_client455_character_manager.py [--gpu] →
prepare_client_build.py → probe_client_character_build.ps1 [без флага и с -HelperLab] →
verify_client455_character_manager.py [--lab] → probe_client455_character_manager_client.py.
После сопутствующих model/Platform01 проверок: checkpoint_client455_character_manager.py.
HAL/MSBuild требуют разрешённого запуска вне sandbox; исходные EXE не запускаются.

Нормальный snapshot character455-manager-io immutable; audit_client_executable.py
--label NAME принимает новое короткое имя, не перезаписывает отличающийся snapshot.
289normal modernCOFF x86/MT,185client labTUs. Normal source APIs покаunused/stripped;
runtime bytes равны предыдущему snapshot после исключения двух timestampDWORD.

## Память и ограничения

Детали сохранять в research/ и inventory/, решения — docs/project-memory.md.
Raw IDA/large traces/IDB/исходные копии — ignored artifacts/ и work/. Gitлокальный,
без remote/push. Ignoring не является backup. Дополнительных SDK/PDB/Character.h
у пользователя нет; ожидание этих файлов не следующий шаг.

Cache Character сохраняет freed pointers после delete/clear/dtor; не исправлять
по догадке и не разыменовывать их в tests. Полный ABI/exception unwind/OOM/logger/
unsafe input/failure equivalence ещё открыты. Private source container layout не
доказывает совместимость с heap/STL старого binary SDK. Не объявлять клиент готовым.
