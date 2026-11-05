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

Source коллекция AnimationManager4028: constructor/registration/name-ID-suffix
lookup/3probe cache/deletion/vector+record ownership;11C APIs, отдельный /MT archive.
scripts/native/client455_animation_manager.{h,cpp}. 25диапазонов равны обоим pin;
87targeted assertions/4groups/one real ANI прошли component/fullclient lab.
Heap/Dmalloc0,gameDLLs не загружены. Normal CUnity/ChAnimation ещё legacy: source
APIs в normal unused/stripped;11APIs в lab имеют E8 REL32 caller/provider proof.
Normal runtime равен loop-clock-final после исключения timestamps. Несвязанные
GPU/clock/texture/массовыеANI suites не повторялись. COFF caller parser extension
проверен на real static/external callers и malformed offset/opcode:4testsPASS.
Gate inventory/client455-animation-manager-checkpoint.json;
research/client455-animation-manager.md. Raw manager-*.json;ownedab74ea29/4c43ad92 closed/save.
Normal snapshot character455-animation-manager:2451456B/entryRVA1BC450,
SHAb597d3ef8287197f6de3da1ef4e2ab360fc87ac6b65fb809c3de2e7cf756bbe0.
Lab5258752B/entryRVA89EF,
SHA67d3766c98d5bab983baa7003cc0267b42ca909d1b0898a865b37e809157b6cc.
Normal291modernCOFF/MT/прежний engine archive;lab192clientTUs.
Открыты normal typed consumers/UnityGetAni failureUI и full actor/renderer.
Worker935450:нет IDA xrefs и immediateVA обоим pin,не доказательство unreachable;
оба выбранных importer mode синхронные. Искать caller перед новым reverse worker.

Предыдущие результаты (исторические checkpoints не переписывать):
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

1. Согласовать normal CUnityAniMgr/CAniData/actor typed source boundary. Коллекция
   менеджера и record ownership готовы (027), её не реверсить заново. Old manager24/
   ChAnimation280 нельзя rawcast к new4028/record284; старые SDK consumers ещё живы.
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
