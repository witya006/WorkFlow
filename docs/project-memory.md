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

Source elapsed clock8B3CC0/RVA4B3CC0 подключён в normal R3EngineMT. Модуль:
scripts/native/client455_loop_clock.{h,cpp}; bridge.inc заменяет выбранную ветку
commonutil.cpp под flag, legacy branch сохранён. Полный update/QPC init/fallback/
duration/get-set/toggles восстановлены для выбранного контракта. В normal PE
UpdateLoopClock RVA1AF700; GetDuration source call есть в COFF, но normal unused
API удалён линкером. RTMovie scale setter готов, event caller ещё не перенесён.
144 whole-state случая/12maskedFPmodes, 3provider сценария и1DAZ/FTZ случай прошли component,
затем через actual R3CalculateTime в полном client lab. Actual clock→R3GetLoopTime
→CResObject даёт frame309; setter/toggle checks прошли. Dmalloc0, gameDLLs не загружены.
Platform01/device2cases69checks прошли, прежние frameSHA; старые большие наборы
не повторялись. Gate inventory/client455-loop-clock-checkpoint.json;
research/client455-loop-clock.md. Raw elapsed-*.json, ownedc215239f closed/save.
Normal snapshot character455-loop-clock-final:2451456B/entryRVA1BC450,
SHAc2ea6d497a4fa2e6ad9aec32d61127a79efb0908b5d44db75a85ec3a588431e8.
Lab5233664B/entryRVA89CC,
SHA66e7d75f977031ecea45da0deb49c9c61e81feb6b14d17a1fff3a2831e82f0d3.
Normal180client+65engine+46JPEG=291modernCOFF/MT; lab191clientTUs.
Normal runtime намеренно изменён. Original process scheduling/timer traces не
снимались; arbitrary NaN/signalling/unmasked FP exception equivalence не доказана.

Предыдущие результаты (исторические checkpoints не переписывать):
- Timing025: CAnimation100 ctor и два численных пути CResObject подключены normal;
  secondary84 defaults известны, normal secondary region ещё не подключён.
  research/client455-animation-timing.md; gate client455-animation-timing-checkpoint.json.
- Secondary024: state84/global28/5effects в source FrameMove; 36scalarcases/2CoraBN,
  6updates прошли. Mandatory sineFloat; lab modernMTsin, не staticCRT bitparity.
  research/client455-secondary-motion.md; gate client455-secondary-checkpoint.json.
- Pose023: key evaluators/transition/ramp/skin matrices;11pairs/132updates. CPU,
  без animated draw. research/client455-pose-source.md и pose-checkpoint.json.

## Следующий шаг

1. Завершить fidelity FrameMove: reference static__CIsin contract (473340 SSE/default
   dispatcher), полный actor lifecycle/secondary binding и transition consumers.
   Численный producer/defaults готовы (025), elapsed clock готов (026); RTMovie
   scale consumer остаётся открытым. Не переделывать готовый clock reverse.
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
Elapsed clock: DWORD count/hop wrap, окно только>10, unsigned x87 average/1000double,
float spill→clamp→scale→real→toggles. До нового среднего scale повторно умножает
сохранённое loopSeconds. Пороги float, вычитание widened-float double; exact cancel
при round-down даёт -0. QPC нужен init/duration, elapsed берётся timeGetTime.
Сравнения также x87: ordinary C++ сравнение ломалось на negative subnormal при
SSE DAZ/FTZ. Ошибка воспроизведена и исправлена; один целевой пример есть в native
и actual engine suite. Не заменять эти сравнения на SSE без доказательства.

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
