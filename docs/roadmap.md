# Дорожная карта восстановления клиента RF Online 455

Обновлено 2026-11-06. По прямому указанию пользователя: работа ИСКЛЮЧИТЕЛЬНО НАД КЛИЕНТОМ.
Старые клиентские исходники и R3Engine — база, клиент 455 — объект реверса.
Серверы, БД и серверная логика вне задачи. Прежний серверный план отменён.
Серверные исходники разрешены исключительно для чтения как справочник клиентских
контрактов, без изменений и сборки. Каждый вывод проверяется на клиенте 455.

Конечная цель — исходники RF_Online.bin с полным функционалом и поведением выбранного
455. Этапы ниже — промежуточные результаты. Критерии полноты и начальная матрица:
[client-acceptance.md](client-acceptance.md). Не закрывать проект после сборки/запуска.

## Текущий статус

Новейший участок M6 — sprites048: настоящие mouse/common ресурсы455 загружаются
через CMainApp.LoadData;DXT5 uploader восстановлен. Содержимое GPU текстур,
отрисовка курсора/кнопки и естественный exit0 проверены дляKorea/Russia.
ExactownPE дошла до launcher I/O после существующей UI инициализации иLoadData;
остановлена отладчиком. Полные455UI/Create/вход ещё открыты. Следом049 — target
launcher/bootstrap order,затем полная инициализация/экран входа.
[Доказательства](../research/client455-sprites.md);M6/M6F/M7/M9 открыты.

Новейший участок M6 — lifecycle047: подтверждённый null-level return FALSE
предотвращает падение до Create. Три normal CMainApp/CLand процесса и две GUI
пробы без Land завершились естественно с exit0. Новая PE собирается;14scoped
checkpoints PASS/PARTIAL. Full ILevel/WinMain/мир/shutdown не приняты.
Следом048: normal _CreateCharDataMgr, реальные таблицы455 и дальнейший Create
к интерфейсу входа. [Доказательства](../research/client455-lifecycle.md).
FT/ANSI/text/IME и остальные M6 gaps сохранены; M6/M6F/M7/M9 открыты.

Новейший участок M6 — font046: GDI/Unicode atlas/cache/draw подключены кnormal
engine text calls;actual CGUIText вывел Korean/Russian строки,оба probes exit0.
GDI oracle/цветные регрессии прошли. FT/полныйtext/UI/IME остаются M6.
Следом047 — early-abort/lifecycle CLand/CMainApp и дальнейший Create/data/UI.
research/client455-font.md; checkpoint PARTIAL; M6/M6F/M7/M9 открыты.

Предыдущий участок M6 — language045: EDF/NDLanguage/lookup/DBCS восстановлены,
countryCRT/codepage11cases согласованы. Exact own WinMain загрузил Korean и
Russian packs;normal D3D/Character прошли. Fullfont/text/UI/Create ещё открыты.
Следом046 — actual font/text provider и normal UI consumer.
research/client455-language.md; checkpoint PARTIAL; M6/M6F/M7/M9 открыты.

Предыдущий участок M6 — nationpaths044: country/path selection455 подключён к
WinMain. Exact own PE прошла ранний normal Create: Character/менеджеры созданы,
Character device совпал с device приложения. Стоп до старых data readers.
Полный locale/CRT/font/NDLanguage, Create/UI/launcher/network ещё открыты.
Следом045 — реальная языковая/данная инициализация и дальнейший Create.
research/client455-nation-paths.md; checkpoint PARTIAL; M6/M6F/M7/M9 открыты.

Предыдущий участок M6 — devicestartup043: восстановлены два startup контракта455
(32бит без forcedfullscreen; nonzero Create→exit0). Exact own PE прошла
обычную оконную D3D/device инициализацию, ready1. Остановка перед клиентским
Create. Далее target locale/launcher/bootstrap и normal Create/resources.
research/client455-device-startup.md; checkpoint PARTIAL; M6/M6F/M7/M9 открыты.

Предыдущий участок M6 — startup042: точная собственная полная PE прошла CRT,
обычный WinMain, engine и Miles startup. Провайдеры DLL сверены, процесс
контролируемо остановлен до D3D/window. Далее actual normal graphics/Create/
launcher и сверка startup/locale contracts455. research/client455-startup.md;
checkpoint PARTIAL. M6/M6F/M7/M9 остаются открытыми.

Предыдущий участок M6 — accounting041: реальные process counters и diagnostic
consumer подключены. Новая source Character/D3D9 ветка собирается и полностью
линкуется: RF_Online.bin, 0 unresolved. ANI/multiple owners/mesh lifetime/GPU
counters и прежние кадры прошли. Далее обычный startup/initialization, затем
оставшиеся поведенческие разрывы. research/client455-normal-accounting.md;
checkpoint PARTIAL. M6/M6F/M7/M9 открыты: линковка не закрывает игровую приёмку.

Предыдущий участок M6 — characterclock040: таймер Character и normal bridge
восстановлены отдельно от engine clock. QPC/fallback/округление проверены,
прежние кадры и короткие consumer/effect/shadow сценарии прошли. Полный линк:
один g_ChMemoryInfo. Далее process accounting и полный normal link.
research/client455-character-clock.md; checkpoint PARTIAL; M6/M6F/M7/M9 открыты.

Предыдущий участок M6 — effects039: EFF reader, registry/file lists, применение,
сброс и particle/entity views подключены. Реальный texture/model GPU сценарий
прошёл; предыдущие кадры сохранились. Полный линк: 2 символа вместо 15.
Далее accounting/Character clock и полный normal link; игровая приёмка впереди.
research/client455-effects.md; checkpoint PARTIAL. M6/M6F/M7/M9 открыты.

Предыдущий участок M6 — effecttables038: readerпаттернов/предметов ивыбор эффекта
подключены, реальные таблицы проверены. Полный линк15символов. Неизвестный stack
tail grades9..35 остаётся открытым; загрузка/применение EFF ислоты ещё впереди.
research/client455-effect-tables.md; checkpoint PARTIAL. M6/M6F/M7/M9OPEN.

Новейший участок M6 — normalshadow037: два метода переключения теневых буферов
восстановлены; реальная модель дала силуэт, цветные кадры прежние. Полный линк
20символов. Неоднозначный BOOLcaller/HRESULTконтракт455 сохранён; обычный игровой
теневой цикл и groundprojection открыты. research/client455-normal-shadow.md.
Далее эффекты/слоты/Characterclock/accounting. M6/M6F/M7/M9OPEN.

Новейший участок M6 — normalcontracts036: пять методов reset/parent/eye/path/bounds
восстановлены и подключены. Реальная модель после reset/reattach/rematch даёт
прежние два кадра;182client+3facade+20kernelCPP собираются. Полный линк22символа.
Далее эффекты/слоты/shadowtargets/Characterclock/accounting; timedblend/normal
lifecycle открыты. research/client455-normal-contracts.md. M6/M6F/M7/M9OPEN.

Новейший участок M6 — normal renderer035: обычные CUnity/pose/CRender рисуют
реальную модель на D3D9. Два кадра равны при вызове через координаты и матрицу;
видимость/alpha/material/состояние/очистка проверены. Полный линк ещё требует
27 методов/данных. Далее эффекты/слоты/reset/parent/bounds/shadow/time.
research/client455-normal-renderer.md; checkpoint PARTIAL; M6/M6F/M7/M9 OPEN.

Новейший участок M6 — normal port034: 180 исходных клиентских единиц компилируются
на D3D9 с типами455, после выделения CUnity/CAnimation — 182 объекта x86/MT.
Реальная загрузка ANI через обычные потребители проверена. Полная RF_Online.bin
пока не линкуется:39 методов/данных. Следом обёртки pose/draw/state,
LoadMeshData/setters/reset/bounds/effects; inventory/client455-normal-link.json.
inventory/client455-normal-checkpoint.json PARTIAL; M6/M6F/M7/M9 OPEN.

Новейший участок M6: начальный R3Engine D3D9port033,67units собираются в отдельной
копии work/client455-port. Device/Grassshader/Characterowner same-device иPlatform01
GPU/helpers/interiors/weather прошли. Следом нормальные180clientconsumers иtyped
Character455 facade. Базоваясборка неизменена;fullengine/runtimeparity ещёоткрыта.
Gate inventory/client455-engine9-checkpoint.json; M6/M6F/M7/M9 OPEN.

Предыдущий участок M6: renderer owner032 constructor/device/destruction/typedcontexts
теперьsource. Real model/ANI/3textures рисуется через его ресурсы;два кадра равны
component/fullclient,COM/ownheap/Dmalloc0. Normal owner API ещёunused,normalruntime
прежний кромеtimestamps. Следом coupled normal typed ChInterface/model/animation/
engineD3D9 device port. Gate inventory/client455-renderer-owner-checkpoint.json;
M6/M6F/M7/M9 открыты.

Предыдущий участок M6: scene-frustum031 source подключён к обычным camera-plane/
CResObject clipping calls. Численные случаи,9actor scenarios икороткая Platform01
регрессия прошли;normal293MTobjects,lab196TUs. API audit:39oldSDKfunctions ещё
вызываются,150field tokens требуют typed review. Следом coupled typed normal
model/animation/Character owner/D3D9 device lifecycle port. Gate
inventory/client455-frustum-checkpoint.json; M6/M6F/M7/M9 открыты.

Предыдущий участок M6: main Character draw030/effects/transparency/batch/CPU/shadow
теперь source.16targeted сценариев и2реальных кадра прошли standalone/fullclient.
Следом normal interface/caller audit исовместный typedmodel/animation/D3D9engine port;
visibility/scene-frustum/CRT/undefined/device lifecycle domains ещё открыты.
Gate inventory/client455-character-draw-checkpoint.json; M6/M6F/M7/M9 открыты.

Предыдущий участок M6: draw primitives029 source/realHAL/fullclient: реальная модель
с ANI/3textures,46geometry parts/44skinned,два разных кадра совпали отдельно и
в полном client lab. Полный92E5F0/effect/transparent/batch/normal renderer открыт.
Следом full draw routing, затем coupled typed model/animation/renderer migration.
Gate inventory/client455-draw-checkpoint.json; M6/M6F/M7/M9 открыты.

Предыдущий участок M6: shader bootstrap028 source/realHAL/fullclient:12SHO/12VS+3PS/
2declarations и контрольный harness draw. Normal renderer и fullCharacter draw
ещё открыты. Из-за name4/ID260 oldSDK против5/264455 normal integration переносит
typedmodel/animation/draw вместе; изолированная подмена менеджера исключена.
Gate inventory/client455-shaders-checkpoint.json; M6/M6F/M7/M9 открыты.

Новейший участок M6: коллекция AnimationManager4028/11sourceAPIs восстановлена,
проверены cache/owners/один real ANI standalone/fullclient. Normal typed consumers
ещё legacy; normal runtime прежний после исключения timestamps. Gate
inventory/client455-animation-manager-checkpoint.json; M6/M6F/M7/M9 открыты.

Новейшее дополнение M6: elapsed clock восстановлен и подключён к обычному клиенту.
Actual R3CalculateTime→CResObject и короткая Platform01/device проверка прошли.
Gate inventory/client455-loop-clock-checkpoint.json. Full actor/normal455ABI/
AnimationManager-worker/draw/renderer и M6F/M7/M9 остаются открыты.

Актуальное дополнение M6: численный расчёт кадра и CAnimation ctor встроены в
обычный клиент через R3EngineMT; три реальных callsites двух source API проверены.
612 численных случаев/12 FP modes, 16 actual CResObject сценариев и короткая
Platform01/device регрессия прошли. Known84 secondary defaults восстановлены;
полный actor lifecycle, upstream elapsed clock и normal Character455/draw открыты.
Gate inventory/client455-animation-timing-checkpoint.json. M6/M6F/M7/M9 открыты.

M1 выполнен: R3Engine.lib, две чистые пересборки, все 58 объектов x86.
M2: бинарный эталон закреплён по SHA-256, различия текущего клиента/backup исследованы.
M3 выполнен для helper-only SPT: 140 файлов, 97 543 объекта, round trip и 7 тестов.
M4: первая полная diagnostic RF_Online.bin из 180 C++ и чистая пересборка успешны.
Это сборочный результат старой базы с выбранными 455 ветками; runtime и canonical
optimized Release не проверены. research/client-first-build.md.
Предыдущая /Goal до начала пункта 4 выполнена (research/goal-checkpoint.md).
Новая активная /Goal — M9: финальная приёмка клиента 455 без модернизации графики.
M8 остаётся отдельным необязательным этапом и не блокирует M9.
Все 180 C++ уже компилируются в диагностической конфигурации с восстановленными
объявлениями Character. Настоящий /MT движок собран отдельно; 238 COFF x86 /MT проверены.
JPEG 6b/Miles подключены; diagnostic link успешен, unresolved symbols нет. CObjectManager
constructor восстановлен, AnimationManager сконструирован через empty state + Init;
реальные SDK операции и empty renderer construction прошли 3630 native проверок.
SetTexPath/SetMipMap восстановлены; 18 дополнительных ABI проверок. Два старых загрузчика прошли
59 проверок с CPU mesh effect application; exception helpers — 770 сравнений с classic exports.
455 draw аргументы подключены отдельным flag/ledger; legacy SetEffect bridge проверен.
455 map/36-grade эффекты ещё не перенесены. Character inline/CRT
ещё не закрыты. research/character-effects-and-exceptions.md.
M5 закрыт для первого выбранного helper-data участка: loader455, две instruction-identical
math функции, RPK доступ и реальное interior/weather использование.140files/97 543records,
2 546 931native/comparison checks,338math checks/12FP modes. Настоящие клиентские
LoadLevel/FrameMove/render/release прошли в own entry на lobby и Platform01;
Platform01:23helpers/8interiors, два weather layers меняют состояния[0,0]→[1,1]→[0,0].
13GPU cases/321checks,703weather,30resource и23 337targeted helper regression checks.
Gate inventory/client-m5-checkpoint.json; research/client-m5-checkpoint.md.
M6 в работе; M6F/M7/M9 открыты.
В M6 восстановлен численный clock:773instruction bytes/8scalar functions+256byte
frame prefix,1275native checks/12FP modes внутри module/полного клиента;287objects /MT.
Actual Platform01 FrameMove/GPU повторно прошёл с новыми clocks (2cases/59checks).
Следом packet8/5,CLand timestamp/tick cache и successful-load hook перенесены:
130byte numeric fragment равен455,314checks/12FP modes/UTC+JST; actual CNetMap/CLand
Platform01 GPU2cases/66checks. Актуальная сборка288objects /MT.
Следом local time/real_time +grade>=1 input перенесены:432cases/2628checks и20actual
CHAT_INFO checks. Clock расширен до10scalar functions+256byte prefix,1037bytes/
1443checks/12FP modes. Commands→actual weather/GPU2cases/69checks;289objects /MT.
Full CLand/transport/calendar/other local commands/chat/lighting domains ещё открыты.
research/client455-clock-source.md.
research/client455-map-time-source.md.
research/client455-time-commands-source.md.
Character:4legacy CPU bindings восстановлены source и подключены normal/lab;
245native checks/4COFFtests,actual InitVertex skinned/unskinned CPU setup/release
и3linked call destinations проверены. Pointer+160 задаётся штатным FindBlendParent;
constructor patch не нужен на подтверждённом пути. Выявлены455mesh5803/vertex64/inline
blends против legacy1072/36/heap иfirst-match vs last-match. Полный Character455
ещё открыт; следующий source unit — InitVertex/vertex conversion и реальные assets.
research/character-mesh-source.md. M6/M6F/M7/M9 не закрыты.
Затем source unit расширен до8functions/full legacy InitVertex:245binding+6732checks/
144cases/12FP modes standalone/full-client,4COFFtests,2actual LoadRealData→source calls.
CPU vertices/triangles/weights/matrices/errors сравниваются с SDK через test-only COM
capture. 455negative normals/vertex64 иотдельный MESH08loader922A00 подтверждены;
Shield065 имеетновый header,old693reader его не читает. Новый приоритет —455MESH08/
CPU data,потом packed layouts/D3D9. research/character-init-source.md. Character455 открыт.
MESH08 framing теперь восстановлен:858real files/12090meshes прошли lossless roundtrip;
6304native checks/12samples/393parts/1309guarded truncations standalone/full-client,
7Python tests. Source dependency доступна, normal model-loader ещё не использует её.
Runtime materials/bones/shared GPU buffers иполный Character455 остаются открытыми.
research/client455-mesh08-format.md. Это завершение формата,не всего loader или M6.
Следом source455parent/bone kernels проверены:2237checks/12real mesh-skeleton pairs/
393meshes/455skeleton records standalone/full-client;20overlap cases31–50. Полный
normal loader иCharacter GPU ещё открыты. research/client455-mesh-bindings-source.md.
Constructor/header/matrices/material-request kernels455 теперь source:14562checks/
12real files/393parts/12FP modes standalone/full-client. Матрицы используютpinned
D3DX9_36 сегоreciprocal quirks;texture provider вtests scripted. Физический
TextureManager/sharedGPU/normal loader ещё открыты. research/client455-mesh-runtime-source.md.
Следом physical Character texture backend восстановлен source ввыбранном domain:
RFS/DDS/lookup/cache/load/delete,actual pinned D3DX9_36+HALD3D9.24body ranges совпали
собоими PE;9Python/333CPU/8440GPU checks standalone/full-client,80DDSprofiles,
68successful texture pairs/137renders,97material parts/59bindings,COM/Dmalloc0.
Normal model-loader ещё legacy;shared buffers/animation/full Character GPU открыты.
research/client455-character-textures.md. Следующий unit93E000/93E180/index rebase/
publication/release,затем normal dispatch. M6/M6F/M7/M9 незакрыты.
Следом sharedGPU sourceunit готов:18pinned bodies,8200byte pools/ctor/Release-only
dtor/first-fit1024/upload36+64+INDEX16/bind/rebase/MESH08GPUfragment.158336CPU/
159173HALchecks standalone/full-client,12files/393parts:276real uploads,
117zero-index skips.4synthetic indexed draws,COM/Dmalloc0. Normal full loader,
owning publication/destructor/unwind,skeleton/skinning/shaders ещё открыты.
research/client455-shared-buffers.md. Следующий unit —owning model lifecycle и
normal dispatch;полныйM6/M6F/M7/M9 не закрыт.
Следом mesh lifetime иconnectedMESH08route source готовы:9953CPU/10021HALchecks,
12files/393parts/276realuploads/59texturebindings,12lifetimecases,ownheap/COM/Dmalloc0.
10bodies equalbothpins. Full-model lab связывает материалы/header/GPU/parents/bones/
publication/release. Normalmanager/filedispatch,полныйmodel ABI,BN/animation/shaders
ещё открыты;known800byte view не заменяетстарыйCHARACTEROBJECT. Next:file/manager
route исогласованныеtypedconsumers. research/client455-model-pipeline.md.
Следом record1188/manager4148/cache/rawMSH/texture refresh восстановлены source:
850CPU/1138HALchecks standalone/fullclient,12models/393parts/276uploads/59pointers.
24bodies equalbothpins;ctor1188byte oracle из92instructions;13APIs linked/called.
Normal dispatcher остаётсяlegacy. Next: BN reader93C2F0/importer93C770/converter93CD60,
dispatcher9238A0/FrameMove923A40, animation иtyped consumers. Current model10021/
Platform01-device69checks прошли,frameSHA сохранены. research/client455-character-manager.md.
Затем intermediate reader93C2F0/part720/model28lifetime source прошли4606standalone
checks/12realBN455records+5synthetic4records,1183guarded prefixes/7allocfailpoints/
12FPmodes/6Python tests. Importer/converter/BNruntime/normal integration ещё впереди.
research/client455-legacy-model-reader.md. Converter теперьcachedвесь578lines.
Затем полныйvalid-input legacyMSH/BN converter/fileIO/weights/indexing/MTG source
подключён:66627capture/14896HALchecks standalone/fullclient,34runs972parts,
832HALindexeduploads/2CPUretained;12realBN→MESH08pairs393parts276uploads.
Fullclient source10APIs verified,heap/COM/Dmalloc0. Normaldispatcher/ANI/animation/
shaders/typedconsumers ещё открыты. Next:ANI93ACD0/dispatcher9238A0/FrameMove923A40.
research/client455-legacy-model-runtime.md. Current manager1138/model10021/graphics69passed.
Очередь M6 уточнена: Character source/ABI перед полным D3D9 port; legacy SDK contract
явно IDirect3DDevice8. Старые InitVertex/loaded mesh/blend kernels уже проверены,
не повторять их исследование. Cached207definitions доступны.
Разница D3D8 базы и D3D9 эталона — обязательное
восстановление M6, а не модернизация M8. Полные particles/clock/Character/UI/network
не сертифицированы; нормальный WinMain и входной455 EXE не запускались.

## Этапы

Последующий unit ANI/record/attachment/Character dispatcher source готов:
14513CPU/15181HALchecks standalone/fullclient,27ANI1062tracks/22real switches,
11BN→MESH08pairs794parts/660HALuploads.13sourceC APIs verified;legacy14896/
manager1138/Platform01-device69passed,framesunchanged. Normalruntime покаlegacy;
pose/key evaluator/animationmanager/worker/shaders/typedconsumers ещё открыты.
Gate inventory/client455-animation-checkpoint.json;
research/client455-animation-dispatch.md. ДалееFrameMove923A40.

Основная среда теперь VS 2026 Professional / MSVC x86: собственная Win32 smoke-сборка
прошла. Сразу переносим клиентский код на современный компилятор. VC6 — резерв,
его поиск не является предварительным условием. Графику сохраняем на этом этапе.

| Этап | Результат | Критерий готовности | Модель |
|---|---|---|---|
| M0. Основа | Git, IDA MCP, инвентарь клиентского кода/движка | Выполнено; клиент ещё не собран | Sol medium |
| M1. Перенос и сборка движка | Современный проект R3Engine на основе RTMovie Release | MSVC x86, две чистые сборки R3Engine.lib, проверены COFF machine/символы/CRT | Sol medium/high |
| M2. Эталон клиента 455 | Копии текущего RF_Online.bin/backup, IDB и карта различий | SHA-256, x86, image base/RVA, закреплённый эталон | Sol high |
| M3. Первый формат 455 | Клиентская спецификация и парсер | Реальные файлы, границы и повреждённые входы проверены | Sol high |
| M4. Полная старая клиентская сборка | RF_Online с согласованными Character/движком/CRT и SDK | Компиляция/линковка и повторная чистая сборка успешны | Sol high, Astra точечно |
| M5. Первый участок 455 | Восстановленный клиент загружает и использует выбранные данные 455 | Поведение сверено с клиентом-эталоном, регрессии проходят | Sol high |
| M6. Клиентские подсистемы | Ресурсы, персонаж, мир, UI, анимация, звук, ввод, клиентский протокол по одному | Для каждого участка: реализация и подтверждённое клиентское поведение | Sol high |
| M6F. Полнота клиента 455 | Исходники и воспроизводимая сборка RF_Online.bin с полным функционалом/поведением эталона | Все выявленные возможности и сценарии покрыты, известных расхождений нет, непроверенное явно учтено; критерии client-acceptance.md | Sol high, Astra для спорных участков |
| M7. Закрепление сборки | Зафиксированные версии и автоматизация современной клиентской сборки | Сохранены форматы и поведение, проходят те же проверки | Sol high |
| M8. Графика (отдельно от текущей цели) | Модернизация клиентского рендера | Отдельная спецификация; не требуется для M9 | Отдельная спецификация |
| M9. Финальная приёмка клиента 455 | Поддерживаемые исходники и воспроизводимый RF_Online.bin с функционалом и поведением закреплённого эталона | Выполнены M6F/M7 и все критерии client-acceptance.md; известные расхождения закрыты, непроверенное не выдано за соответствие; модернизация графики не входит | Sol high, Astra точечно |

M2/M3 можно вести до получения toolchain. M1 — восстановление сборки зависимости,
не готовый клиент: R3Engine.lib не совпадает по имени с требуемой клиентом R3EngineMT.lib.
Необходимость Character для конкретных веток движка проверить препроцессором.
Для M4 нужны клиентские зависимости B01–B08; инструменты B09–B11 подключать по необходимости.
Серверные B12/B13 из исторического аудита не являются блокерами этого проекта.

Сетевые находки ограничены клиентскими обработчиками/пакетами/состояниями. Наблюдение
ответа существующего внешнего стенда не превращается в задачу разработки сервера.
Сроки уточнять по первому проверенному формату и первой клиентской сборке.

## Ближайшая очередь

1. M6: восстановить fullCharacter draw/state/constants/palette/material и shader
   selection, затем связанный normal typedmodel/animation/renderer путь. Shader
   bootstrap028 готов на HAL; не делать отдельную подмену CUnity manager.
   В той же цепочке завершить staticCRTsin/полный actor lifecycle/transition consumers и
   normal CUnity/CAniData calls. Коллекция AnimationManager/record ownership ready027;
   async worker уточнять по callers, оба выбранных importer mode синхронные.
   Key evaluators/основныеpose/transition/ramp/skinmatrices
   source готовы:11pairs/132updates standalone/fullclient CPU,5sourceC APIs;
   secondary state/effects подключены:36scalarcases/2realCoraBN/6updates;reference
   staticCRTsin parity ещёopen. research/client455-secondary-motion.md. Затем skin/draw и
   normal typed consumers. Framing/material/texture/sharedGPU/lifetime/MESH08route/
   selected manager/rawIO/ANI/attachment/dispatcher source готовы; normal loader не переключать до согласования
   ABI иconsumers. Полный455D3D9renderer иреальные model scenarios остаются в M6.
2. Восстановить D3D9renderer/shaders/lighting455 вместе с Character consumers.
3. По одному закрывать остальные M6 client subsystems и реальные acceptance scenarios.
4. M6F: завершить реестр возможностей/расхождений и доказательства полноты клиента.
5. M7: закрепить воспроизводимую сборку;M9: финальная приёмка455 без модернизации графики.

## Организация работы и память

Один цикл — одна проверяемая цель: определить входы/критерий готовности, провести
минимальный эксперимент, проверить, записать доказательства, обновить текущий статус.
Непроверенная гипотеза не становится фактом при переходе в новый чат.
Субагенты — только по отдельной просьбе пользователя.

| Файл/каталог | Назначение |
|---|---|
| AGENTS.md | Постоянные правила, границы действий, порядок чтения |
| docs/project-memory.md | Короткое актуальное состояние, решения, следующий шаг |
| docs/environment-audit.md | Подтверждённое окружение и границы проверки |
| docs/build-audit.md | Клиентские зависимости B01–B11 и первая сборка |
| docs/next-steps.md | Ближайшая очередь, обновляемая после этапа |
| docs/roadmap.md | Долгосрочные этапы и критерии перехода |
| docs/client-acceptance.md | Полнота функционала/поведения и проверяемые расхождения |
| inventory/*.json | Воспроизводимые манифесты и сводки |
| research/ | Исследования форматов/подсистем с доказательствами |
| scripts/ | Повторяемые массовые операции и проверки |
| work/, artifacts/ | Копии, IDB, сборки; требуется отдельный backup |

Находка в бинарнике: файл/SHA-256, архитектура, image base, VA/RVA функции,
вход/выход, вызывающие функции, проверка, статус «подтверждено/гипотеза/неизвестно».
Формат данных: хеш образца, смещения/размеры, границы и обработка ошибок.
В Git — небольшие изменения и очищенные сводки, без секретов, БД, игровых бинарников
и сырых логов. Remote/push для этих этапов не нужны.

## Модель и уровень мышления

Это рекомендация для проекта, не гарантия результата на любом участке:

| Работа | Стартовая настройка | Повышение |
|---|---|---|
| Аудит, скрипты, сборка, документация | GPT-6.1 Sol в Codex, medium | high при нескольких взаимодействующих причинах |
| Реверс C++/x86, структуры, пакеты, сравнение версий | GPT-6.1 Sol, high | Astra high при противоречиях после сбора фактов |
| Сложный ABI/неизвестный алгоритм, пересмотр решения | GPT-6 Astra, high | xhigh для конкретного нерешённого вопроса |
| Сводка проверенных данных | GPT-6 Luna, high, либо существующий скрипт | Не поручать окончательные выводы о совместимости |

Codex — рабочая среда с файлами/MCP; GPT — выбранная модель. Для проекта используем
Codex внутри этой папки. Повседневно достаточно начать с Sol medium; на реверсе — high.
Настройки этим документом не изменены; доступность зависит от аккаунта/клиента.

Официальная документация на 2026-11-04 рекомендует Sol для длительной работы при
важности стоимости, Astra для наиболее сложных задач, Luna для узких повторяемых.
Повышение reasoning расходует больше времени/токенов. Конкретные уровни в нашей
таблице — инженерная рекомендация: https://learn.chatgpt.com/docs/models.

Экономия: массовые выгрузки IDA сохранять локально, в контекст давать нужные функции
и различия; не повторять инвентаризацию без изменения входов; не загружать все навыки;
закрывать по одному контракту с проверками. Max/ultra не использовать по умолчанию.
Бюджет и сроки уточнять после M1/M3 по измеренным результатам.
