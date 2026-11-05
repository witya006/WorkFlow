# Память проекта

Обновлено 2026-11-05. Root `E:\RFOnlineTrash\Source\WorkFlow`.
Сокращена для продолжения работы без повторного чтения устаревших очередей.
Полная предыдущая память сохранена в research/project-memory-pre-pose.md;
подробные доказательства — research/ и inventory/.

## Цель и ограничения

- Только клиент RF_Online.bin: поддерживаемый source с функционалом и поведением
  закреплённого455. /Goal M9 = финальная приёмка без модернизации графики.
  M0–M4 diagnostic milestones и выбранный M5 закрыты; M6/M6F/M7/M9 открыты.
  Compilation/загрузка модели/вычисление позы не являются готовым клиентом.
- Серверные файлы только справочник для чтения; не менять, не копировать для
  разработки, не собирать серверы/БД/GoMMO server logic. Originals immutable.
  Изменения клиентского кода — под work/; не исполнять входные EXE.
- Git локальный, remote/push/publish не разрешены. Raw assets/IDB/large traces
  ignored work/ и artifacts/. Ignoring не backup. Субагенты не разрешены.
- Пользователь уточнил стоимость159173checks: это assertions в автоматическом
  запуске, не запросы к ИИ. Проверять изменённый участок/зависимости; неизменённые
  большие runtime suites не повторять без конкретного риска. Число проверок
  не показатель готовности; приоритет — работающий восстановленный клиент.

## Последний проверенный результат

Source draw primitives029: client455_draw.{h,cpp},5APIs; initial states91CDE0,
selection91FB90, material92D830, palette91D120, shared branch92E140/92E5F0.
Реальный BELPHEGORHOLIDAY pair9:51parts/46geometry/44skinned,ANIframes160/2160,
3real looseDDS. BN→MESH08→ANI→source pose→GPU,92real draws+4analytic36/64indexed/
nonindexed.596targeted assertions,heap/COM/Dmalloc0. Native и fullclient два frame
SHA равны; previews work/m9/94e327e9/client001/character-frame-{0,1}.bmp просмотрены.
Gate inventory/client455-draw-checkpoint.json; research/client455-draw.md.
Normal2451456B/entry1BC450,SHAbfa9ac62a6c5a320caa6822d302f37d5bad64b2fbbcbc1acca599f591463f6b1,
snapshot character455-draw; unusedAPIs stripped, runtime равенshader snapshot кромеtimestamps.
Lab5328384B/entry8A8A,SHA94e327e99f32ba83d32a53cabcfaad1cc5a1d0f6d9e6b4992c0ed9c6585a61cf,
194clientTUs;normal291modernCOFF/MT/engine archive прежний. Старыеbulk suites не повторялись.
Harness camera/CullNONE/basicshader выбран вручную; full92E5F0 и normal D3D9 не приняты.
Следом full main effect/material routing, sorted930A40/batch92D9D0/CPU92DB60/shadow/
wrapperculling, затем coupled typednormal model/animation/renderer. Rawdraw-*.json
в artifacts/character-animation455; owned96152de8 closed/save. Main914lines: first752,
tailoffset740. 92D3E0 wrong decompiler prototype — проверить instructions до source.

Предыдущий результат:

Source shader bootstrap028: scripts/native/client455_shaders.{h,cpp},7APIs.
12real SHO→12VS+3PS,2declarations; pinned D3DX9_36/realD3D9HAL.119native checks
standalone/fullclient;sameframe,COM release counts0/Dmalloc0/no gameDLLs.15actual
compiler input SHA совпали с независимо извлечёнными stage;flags8008/main/vs_2_0/
ps_3_0.4parser tests passed. Nativeharness рисует synthetic weighted triangle
через originalsh_basic/declaration64, НЕ fullCharacter draw/real animatedmodel.
Preview work/m9/4dc80db8/client001/shader-frame.bmp визуально просмотрен.
Gate inventory/client455-shaders-checkpoint.json;research/client455-shaders.md.
Normal unused APIs stripped/runtime равен предыдущему manager snapshot кромеtimestamps;
normal renderer всё ещё D3D8. BigANI/texture/sharedGPU/Platform01 suites не повторялись.
Normal snapshot character455-shaders:2451456B/entryRVA1BC450,
SHA87db29ad1a4461bbaea2c617633b9eb8df1fb445abc394eea538dd8272cf4253.
Lab5291520B/entryRVA8A6C,
SHA4dc80db8f12e9346ed40beef6f12061fd1917607cebb300d72874e7e3f7e29d1.
Normal291modernCOFF/MT/тот же engine archive;lab193clientTUs.
Raw render-*.json/renderer-start-*.json;owned95159529 closed/save.
Error UI/OOM/device-loss/reset/normal fullrenderer и acceptance ещё открыты.

Предыдущие результаты (исторические checkpoints не переписывать):
- AnimationManager027: source4028/cache/record ownership,11APIs,87checks/oneANI;
  normal CUnity/ChAnimation ещё legacy. research/client455-animation-manager.md;
  gate client455-animation-manager-checkpoint.json. COFFcallers4testsPASS.
  Worker935450 noxref/immediateVA,не доказательство unreachable; оба выбранных
  importer mode синхронные,искать caller перед новым reverse worker.
- LoopClock026: source elapsed update/QPCinit/fallback/duration/clamp/scale/toggles
  подключён normal R3EngineMT;144state cases/3provider/1DAZFTZ прошли. Actual clock
  →CResObject frame309 и Platform01/device69passed. Source x87 compares обязательны.
  research/client455-loop-clock.md; gate client455-loop-clock-checkpoint.json.
- Timing025: CAnimation100 ctor и два численных пути CResObject подключены normal;
  secondary84 defaults известны, normal secondary region ещё не подключён.
  research/client455-animation-timing.md; gate client455-animation-timing-checkpoint.json.
- Secondary024: state84/global28/5effects в source FrameMove; 36scalarcases/2CoraBN,
  6updates прошли. Mandatory sineFloat; lab modernMTsin, не staticCRT bitparity.
  research/client455-secondary-motion.md; gate client455-secondary-checkpoint.json.
- Pose023: key evaluators/transition/ramp/skin matrices;11pairs/132updates. CPU,
  без animated draw. research/client455-pose-source.md и pose-checkpoint.json.

## Следующий шаг

1. Восстановить full Character455 draw/mesh submit/state/constants/palette/material
   и shader selection. Bootstrap028 уже готов. Затем связанный normal typedmodel/
   animation/renderer путь, не отдельная подмена manager. Old ChAnimation name4/
   ID260/size280 против4555/264/284; oldmodel776/mesh1072 против1188/5803. Поэтому
   rawcast/shadow legacy records не добавлять. Коллекция027 готова,не реверсить снова.
   UnityGetAni1E12C0:IDFFFFFFFF guard, lazy load, failure handling различается при
   mode>=2/UI556 versus mode<2/UI1999+3000ms. Это reference, не implementation.
2. Завершить fidelity FrameMove: reference static__CIsin contract (473340 SSE/default
   dispatcher), полный actor lifecycle/secondary binding и transition consumers.
   Численный producer/defaults готовы (025), elapsed clock готов (026); RTMovie
   scale consumer остаётся открытым. Не переделывать готовый clock reverse.
   Secondary flow source уже готов сrequiredmathcontext;RF_POSE_SECONDARY только
   приотсутствующем backend. Не повторять584instruction reverse/golden math безизменений.
   Async worker уточнять по caller,не считать установленным runtime блокером.
   Потом связать pose с
   skinning/draw/declarations/shaders и normal typed consumers на455 D3D9.
   Старый Character SDK — D3D8 и другой layout, rawcast не допускается.
3. Другие M6 client subsystems по client-features.json и client-acceptance.md;
   затем M6F/M7/M9. M8 исключён. Доказательств полноты клиента пока нет.

Девять bodies FrameMove/key/secondary/profile pinned вclient455-pose-reference.json.
Raw artifacts/character-animation455/{framemove-*,key-*-insn,pose-*,scale-axis}.json.
Owned66b26ca4/8115e37c closed/save; живых owned IDA sessions нет. Cached decompiler имеет
неверные D3DX stdcall prototypes/stack locals: использовать инструкции.
Готовый framing/loader/geometry/material/parent reverse не повторять.
Secondary rawsecondary-insn.txt/secondary-*.json втомжеartifactfolder. Borrower
7CD430=this+500→model1184,cleared byFrameMove/no free. Actor ctor7CCFA0 вызывает
CAnimation ctor на+140 и secondary initializer на+500; полный lifecycle ещё открыт.
Timing rawtiming-*.json в той же папке; owned77611a53/23cf5a01 закрыты/save.
У7CD560 elapsed*1000*5+unsignedcarry сначала spill double, затем speed/current,
FISTP signed64/chop и lowDWORD с восстановлением CW. Не заменять float выражением:
при .03f/current160/speed1 PC53nearest получается309, floatshortcut даёт310.
Skirt trigger quaternionW*Z<-.2,timers savedtime,неdecompilerinitialweights/quatbits.
Sharedglobals1189738..50 — left/right/pony timers/XYZ/phase,неperactor.
Elapsed clock: DWORD count/hop wrap, окно только>10, unsigned x87 average/1000double,
float spill→clamp→scale→real→toggles. До нового среднего scale повторно умножает
сохранённое loopSeconds. Пороги float, вычитание widened-float double; exact cancel
при round-down даёт -0. QPC нужен init/duration, elapsed берётся timeGetTime.
Сравнения также x87: ordinary C++ сравнение ломалось на negative subnormal при
SSE DAZ/FTZ. Ошибка воспроизведена и исправлена; один целевой пример есть в native
и actual engine suite. Не заменять эти сравнения на SSE без доказательства.
AnimationManager: self0/preserved allocatorpadding4/vector8-12-16/counter20/nextId24,
cache1000 at28. Constructorcounter0/ID1; reset counters не clear. Release932F30
оставляет cache/self/counters. Не dereference freedcache в tests. Suffix включает
backslash; IDhash sumbytes,3probes;registeredlowercase names,record284,ID264.
Shaders: SHO preferred, key134bytes atRVA739918+3zero,mod137. Literal markers,
externalprefix appended withoutseparator;originalfilepreamble ignored.9vertex-only
и3dualprograms. CompileShader flags8008/main/VS2.0/PS3.0. Managerknownprefix28,
record16/8initialcapacity/doubling,deviceborrowed. PScompilefail strandsVS+VStable;
source preserves,only harness cleans after observing. ModalerrorUI notwired yet.
DrawDynamic92DB60 decompiler prototype неверен; это ещё reference,неsource draw.
Draw palette: skin646+64i *world, count0 pose4830 повторяется4раза c100/104/108/112.
Optional world меняет только translation12/13/14. Shared indexed baseVertex0,
minVertex=(vertexAbsolute%2300000)/(36or64),startIndex=(indexAbsolute%1000000)/2.
State renderer33836 — specularEnable, не fog; numeric29/146/143.

## Контракты, которые легко нарушить

- Current pin SHA b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
  backup46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
  x86/base400000,5bytes/2unrelated ranges отличаются. Документировать RVA+SHA.
- D3DX9_36 provider SysWOW64 равен клиентскому, SHA
  c12f0ab0338eb5031d3d04beaf7208ac848f7e037d21ff963d2af90221cbe935,
  v9.19.949.2111,previous signatureValid. Inverse1654A1/Multiply164F24.
  Inverse отклоняется от идеальной математики на1ULP; причина reciprocal
  approximation — гипотеза. Не подменять идеальным inverse/D3DX8.
- Legacy object parent/count/mesh268/528/532,455272/532/536. Record1188,
  knownprefix800,mesh5803,vertex64,ANIrecord284/descriptor32; private C++ ABI открыт.
- Mesh current5095/previous5099 владеют descriptors, ключи borrowed от ANI raw268.
  Mesh lifetime заканчивать до ANI owner. ANI loading4/model loading264 sticky,
  retry может вернуть true при loaded0. Cache manager оставляет dangling pointers.
- ANI BYTE0 count/BYTE1 ignored/header140/WORDcounts/strides20-16-16-8.
  Scale channel2 linear search, rotation0/translation1 binary search;
  timestamps signed32, numerator wraps signed32,denominator unsigned32,x87 ratio.
  Before/after extrapolate, count1 читает следующий key за declared channel.
  Source допускает это внутри owner span, выход за owner — own bounded failure.
- Quaternion W меняет знак через x87. FrameMove не увеличивает frame672.
  Previous684,blend692/duration(renderer33844),ramp704/708/712/716;
  localpose4830,parentold4894,rampbase4958,skin646=mesh4574*bone4638*bone4830.
  Порядок mesh traversal/previous release observable. Profile933430/933490 не locks.
- Bone pointer table526 пересекается с matrices646 при31+; сохранить подтверждённый
  порядок записей, не считать limit50 гарантией безопасности. Реальные selected
  fixtures не доказывают все unsafe/OOM/unwind/NaN/unmaskedFP/error domains.

## Где искать уже сделанное

- ANI/dispatch: research/client455-animation-dispatch.md, gateclient455-animation-checkpoint.json.
- Legacy converter/MTG/weights: client455-legacy-model-runtime.md; parser/lifetime:
  client455-legacy-model-reader.md. Real BN уже строится source, не только names.
- Manager/rawMSH/refresh: client455-character-manager.md. Model/lifetime:
  client455-model-pipeline.md; texture/RFS:client455-character-textures.md;
  sharedGPU:client455-shared-buffers.md; layouts/bindings:client455-mesh-*.md.
- M5 helper/interior/weather: client-m5-checkpoint.md. Clocks/map/commands/resource:
  client455-clock-source.md,client455-map-time-source.md,client455-time-commands-source.md,
  client455-resource-io-source.md. Historical gates не обновлять массовыми reruns.
- Toolchain VS2026Professional/x86; scripts/Invoke-Python.ps1 — единственный audit
  Python entry. MSBuild/HAL и Git mutations требуют разрешённого escalation.
  IDA tools всегда database sessionID, открывать копии и закрывать owned sessions.
