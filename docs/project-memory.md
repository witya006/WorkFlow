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

В scripts/native/client455_animation_timing.{h,cpp} восстановлены расчёт кадра
7CD560/RVA3CD560, конструктор CAnimation 7CCC30/RVA3CCC30 и известный secondary
prefix84 91C490/RVA51C490. Два API встроены в обычный клиент через настоящий
R3EngineMT: ctor и два численных пути CResObject (три E8 REL32 callsites).
612 независимых Fraction случаев/12 masked FP modes, 614 component checks;
16 реальных CResObject сценариев/56 checks в full-client own entry прошли.
Короткая Platform01/device проверка: 2 случая/69 checks, прежние frame SHA,
COM/Dmalloc0. Старые большие runtime suites не повторялись.
Gate inventory/client455-animation-timing-checkpoint.json;
research/client455-animation-timing.md. Normal snapshot character455-animation-timing:
2451456B/entryRVA1BC450,
SHA0aec5bc1ba169988f5bb1778123e2b214af23dc7062c23c776a8edad1fa6d67e.
Lab5225472B/entryRVA89B3,
SHA9e0ad1539a3a01a0964f6d2288167ae9524fe2619f95d8e3c47479159d1eafae.
Normal180client+64engine+46JPEG=290modernCOFF/MT; lab190clientTUs.
Normal runtime намеренно изменён выбранными timing/ctor вызовами.
Elapsed clock upstream и derived actor lifecycle ещё не доказаны; полный actor
ctor/secondary binding/455 ABI/renderer не восстановлены. Known84 default initializer
пока доступен компоненту/lab, но не подключён к normal actor secondary region.

Предыдущий результат:

Source secondary91E270 вscripts/native/client455_secondary.{h,cpp} подключён
вRFClient455Pose.lib/UpdateCharacterPose. State84/global28,5oscillators и5effects,
36whole-state scalarcases;CoraFemale38parts/all5effects иarmor06135parts/3skirts,
6FrameMoveupdates component/fullclientownentry. Heap/Dmalloc0,gameDLLs не загружены.
Шесть pose/secondary APIs имеют actualcaller/archiveproof. Это CPU,безdraw.
Static reference__CIsin ещё не source:mandatory sineFloat callback;lab явно
modernMTsin(double)→float32,не bitparity proof. Secondary unit частичный именно
вэтомnumeric/backend/normalconsumer смысле,не успешная пустая замена.

Historical gateinventory/client455-secondary-checkpoint.json;
research/client455-secondary-motion.md. Связаннаяpose regression пройдена:
11BN→MESH08pairs/132updates/2298skin matrices standalone/fullclient,прежнийрезультат.
Normal snapshotcharacter455-secondary:2451456B/entryRVA1BC4B0,
SHA40575afbd24f9ed9dc6f8e945806a932059c5056873ae300ebfc3a789bd6aef5.
Lab5214208B/entryRVA899F,
SHA9b3e683569b24396cbdd330fea175d03d59623911df3ffc5dd9411e94efc1c12.
Normal180client,lab189TUs;normal APIs unused/stripped,runtimebytes кромеtimestamps
равныpose-final. Прежние289modernCOFF/MT verification исторические,новые source
objects такжеx86/MT. ANI/GPU/manager/Platform01 runtime suites не повторялись.

## Следующий шаг

1. Завершить fidelity FrameMove: reference static__CIsin contract (473340 SSE/default
   dispatcher), полный actor lifecycle/secondary binding, upstream elapsed clock
   и frame/transition consumers. Численный producer и известные defaults готовы (025).
   Secondary flow source уже готов сrequiredmathcontext;RF_POSE_SECONDARY только
   приотсутствующем backend. Не повторять584instruction reverse/golden math безизменений.
2. Полный AnimationManager/async worker/record ownership. Потом связать pose с
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
