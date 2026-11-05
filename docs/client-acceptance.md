# Полнота восстановления RF_Online.bin

Текущий участок M6, accounting041: семь подтверждённых cumulative counters
питаются от настоящих producers и читаются diagnostic consumer через own source
snapshot. Actual ANI/two renderers/mesh lifetime и model/GPU descriptors прошли.
Вся новая normal source ветка компилируется и линкуется в RF_Online.bin, 0 missing
symbols. Это отдельный подтверждённый результат. Normal WinMain, initialization,
device lifecycle и полный UI/network/gameplay ещё не приняты; M6/M6F/M7/M9 открыты.
research/client455-normal-accounting.md; scoped checkpoint PARTIAL.

Предыдущий участок M6, characterclock040: таймер Character и реальный normal bridge
подключены, численные и provider сценарии прошли. Это отдельные миллисекунды,
не повторный update engine clock. Full normal link имеет один g_ChMemoryInfo.
Сам таймер не доказывает новые frame methods924700/9248A0 или полный actor
lifecycle; normal WinMain/UI/network/gameplay приёмка остаётся открытой.
research/client455-character-clock.md; checkpoint PARTIAL; M6/M6F/M7/M9 открыты.

Предыдущий участок M6, effects039: EFF reader/registry/file lists/application,
InitEffect и particle/entity views подключены к обычной сборке. Реальные файлы,
контракты выборки/сброса и применение настоящей DDS к модели на GPU проверены.
Это не приёмка полного particle emitter или игрового lifecycle. Pattern tail
grades9..35 по-прежнему неизвестен. Полный линк: 2 символа; normal WinMain,
клиентская сеть, UI и игровые сценарии ещё не приняты. M6/M6F/M7/M9 открыты.
Подробности: research/client455-effects.md; checkpoint PARTIAL.

Предыдущий участок M6, effecttables038: два загрузчика таблиц иquery подключены
кобычному sourcefacade, реальные2246patterns/4600items проверены. Это определённая
область выбора эффекта. Reader455 оставляет grades9..35 какнеизвестные stackbytes;
нашиqueries явно выявляют эту границу, не принимают её какнулевой эффект.
EFFloading/application/particles иполнаяигровая приёмка ещё открыты. Полныйлинк15
символов. research/client455-effect-tables.md; checkpoint PARTIAL/M9OPEN.

Текущий участок M6, normalshadow037: восстановлены BeginShadow/EndShadow,
текстуры и общий quad. Реальная модель дала силуэт512x512, переключение/
восстановление/reuse прошли, COM0. Это собственный явно завершённый проход:
настоящие callers455 используют BOOL при возвращаемом HRESULT0 и не дают
доказательства нормального shadow lifecycle. Полный линк20символов, M9OPEN.
research/client455-normal-shadow.md; inventory/client455-normal-shadow-checkpoint.json.

Текущий участок M6, normalcontracts036: пять методов модели/сброса/перепривязки
восстановлены. Реальная модель после reset/reattach/rematch рисует прежние два
кадра, BBX/границы проверены. Полный линк ещё22метода/данных. Это собственный
тестовый entry с производственными компонентами; normal WinMain, timedblending
и вся игровая/UI/network приёмка остаются открытыми. Подробности:
research/client455-normal-contracts.md; checkpoint PARTIAL. M9OPEN.

Текущий участок M6, normal renderer035: CUnity → модели/ANI → поза → CRender
подключены и отрисовали выбранную модель на D3D9. Проверены два кадра, обёртки,
видимость и ресурсное завершение. Это не нормальный WinMain и не вся игровая
приёмка. Полный линк ещё требует 27 методов/данных. Подробности и открытые
границы: research/client455-normal-renderer.md, checkpoint со статусом PARTIAL.

Текущий участок M6, normal port034: компилируются 180 исходных клиентских единиц
с типами455/D3D9, после выделения CUnity/CAnimation — 182 объекта x86/MT.
Реальные потребители загружают ANI; это два модуля, а не весь клиент.
Нормальная RF_Online.bin ещё не линкуется:39 методов/данных.
inventory/client455-normal-checkpoint.json имеет статус PARTIAL. Высокоуровневые
обёртки, эффекты, normal runtime и M6/M6F/M7/M9 остаются открытыми.

## Требование пользователя

Получить исходный код, из которого воспроизводимо собирается RF_Online.bin,
доведённый до 100% функционала и поведения выбранного эталона 455.
Это конечная цель проекта. Старый собираемый клиент, первый парсер или успешный запуск
являются промежуточными результатами. Идентичность текста оригинальных исходников
и побайтовое совпадение EXE не следуют из функционального соответствия.

Цель 100% фиксируется как требование. Достигнутую степень соответствия устанавливаем
по доказательствам; сейчас она неизвестна. Процент по числу восстановленных функций
не вычислять: функции различаются по объёму и могут быть не найдены.

Число assertions не является мерой готовности клиента. Для изменения проверять
затронутый контракт и зависимые сценарии; неизменённые большие наборы не повторять
без конкретного риска. Общую регрессию выполнять после сквозных изменений и при
приёмке этапа. В отчётах указывать сценарии и их результат, а не только счётчик.

Последний выбранный участок M6: начальный real R3EngineD3D9port в отдельнойкопии,
67x86/MTunits собраны. Device/Grassshader/Characterowner same-device иPlatform01
GPU/helpers/interiors/weather прошли.180normalclientconsumers ещёнеперенесены;
это не полный RF_Online455 и не original game frame parity. Gate
inventory/client455-engine9-checkpoint.json;research/client455-engine9-port.md.

Предыдущий выбранный участок M6: source renderer owner constructor/device binding/
destruction иtypedcontexts проверены нареальной модели/ANI/3textures отдельно и
вполном client lab. Два кадра равны,allocations/COM освобождены. Normalowner API
ещёunused/stripped;fullnormal Character/D3D9 port не принят. Gate
inventory/client455-renderer-owner-checkpoint.json.

Предыдущий выбранный участок M6: scene frustum/AABB source подключены к
SetCharacterClipping/ProcessClipping;72matrix/204AABB cases/9actor scenarios
и короткая Platform01 регрессия прошли. Это не полная game camera/actor visibility
или typed Character455/D3D9 integration. Gate inventory/client455-frustum-checkpoint.json.

Предыдущий результат: расчёт кадра и CAnimation ctor подключены к обычной
сборке, 612 численных случаев/16 actual CResObject сценариев прошли. Это доказательство
выбранного контракта; полный Character455/actor lifecycle/normal draw остаются открыты.
Основание: inventory/client455-animation-timing-checkpoint.json.

Следующий выбранный участок M6: elapsed clock теперь source и подключён к обычному
R3EngineMT. Actual clock→frame caller проверен в полном client lab; остальные
области и полнота клиента открыты. inventory/client455-loop-clock-checkpoint.json.

Следующий участок: source коллекция AnimationManager4028/record ownership проверена
в полном client lab на одном real ANI. Normal CUnity/CAniData ещё legacy; библиотека
сама по себе не закрывает область «Персонажи». inventory/client455-animation-manager-checkpoint.json.

Shader bootstrap455 теперь source:12VS/3PS/2declarations проверены realHAL/fullclient.
Контрольный draw использует synthetic triangle, не full Character draw. Normal
model/animation/renderer migration ещё открыта. inventory/client455-shaders-checkpoint.json.

Следом source draw primitives проверены на реальном BELPHEGORHOLIDAY с ANI и3textures:
46geometry parts/44skinned,кадры160/2160 совпадают в standalone и полном client lab.
Harness выбирает basic shader/камеру/CullNONE: это ещё не full92E5F0/effects/transparent
или normal renderer acceptance. inventory/client455-draw-checkpoint.json.

## Эталон

Main Character draw030 теперь source: эффекты, прозрачность, deferred batch, CPU и
shadow ветки представлены и проверены16targeted сценариями в полном client lab.
Реальная модель рисуется через основной маршрут, два кадра совпали с компонентом.
Это не normal integration/visibility/game frame acceptance; original CRT и
undefined scratch domains явнооткрыты. inventory/client455-character-draw-checkpoint.json.

Бинарный эталон закреплён в config/client-target.json: текущий пользовательский
RF_Online.bin, SHA-256 b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b,
x86, image base 0x400000. Backup — вторичный материал; различия локализованы.
Полный манифест ресурсов/конфигурации ещё требуется дополнить для сравниваемых сценариев.
Условия сравнения включают ресурсы, настройки, ввод, сетевые входы и состояние клиента.
Поведение существующего сервера само по себе не доказывает клиентский алгоритм.
Серверные исходники — справочник для чтения без изменений/сборки; выводы сверять с 455.

## Начальные области покрытия

Это отправная карта для инвентаризации, а не доказанный полный перечень возможностей.
Каждую строку развернуть в конкретные функции и сценарии по данным анализа эталона.

| Область | Что сопоставлять | Текущий статус |
|---|---|---|
| Запуск и конфигурация | Инициализация, параметры, локализация, ошибки | Не проверено |
| Файлы и данные | Форматы, таблицы, ресурсы, загрузка и обработка ошибок | Частично: helper SPT, selected RPK/R3X consumers; область в целом открыта |
| Рендер и мир | Сцена, камера, освещение, эффекты, видимость, коллизии клиента | Частично: selected maps/helpers/weather/clock; D3D9 и полное поведение открыты |
| Персонажи | Модели, экипировка, анимации, клиентские состояния | Частично: selected mesh/texture/buffer/model/manager; normal dispatch/BN/animation/full Character открыты |
| Ввод и интерфейс | Управление, окна, текст/IME, фокус, сочетания клавиш | Не проверено |
| Звук | События, позиционирование, музыка, настройки | Не проверено |
| Клиентская сеть | Пакеты, сериализация, обработчики, порядок состояний/ошибок | Не проверено |
| Вход и выбор персонажа | Клиентские экраны, переходы и обмен сообщениями | Не проверено |
| Игровые действия | Перемещение, выбор цели, атака, умения и отображение результатов | Не проверено |
| Предметы и взаимодействия | Инвентарь, торговля, NPC, квесты и прочие обнаруженные клиентские сценарии | Не проверено |
| Социальные функции | Чат, группы, гильдии и прочие обнаруженные функции | Не проверено |
| Жизненный цикл | Загрузка/смена локаций, разрыв соединения, выход, освобождение ресурсов | Не проверено |

Первый предметный реестр: inventory/client-features.json. M5 закрыт для helper SPT455
и его interior/weather consumer:140files/97 543records; две math функции инструкционно
совпадают с455. Actual LoadLevel/FrameMove/render/release прошли на lobby/Platform01
через own entry полного проекта.23helpers/8interiors управляют двумя real weather layers.
13GPU cases/321checks,703weather/30resource/23 337targeted helper checks прошли.
research/client-m5-checkpoint.md; client455-graphics-runtime.md. Это ограниченный
результат; строки «Файлы и данные»/«Рендер и мир» целиком остаются открыты.
Full particles/clock/lighting/D3D9 parity и normal WinMain не проверены.

Численный clock перенесён следующим участком M6:8scalar functions+256byte frame
prefix,773instruction bytes совпали с обоими PE;1275native checks/12FP modes в
module и полном клиенте, linked code/default provider проверены. Actual Platform01
FrameMove/GPU повторно прошёл. Это закрывает численный участок при равном FPU
окружении; cached client map time/packet/console integration и lighting остаются
открытыми. research/client455-clock-source.md. Критерии полноты не изменены.

Следом selected client map message8/5 →CLand cache→successful-load hook перенесён
и проверен:314native checks/12FP modes/UTC+JST,130instruction bytes equal455,
actual client processor/CLand/Platform01 GPU2cases/66checks. Full byte-index CLand
UI/effects/error path,root network/transport,opaque fields и old-CRT localtime32
timezone/DST/invalid domains остаются открытыми. Это не закрывает строку «Клиентская
сеть» или полный жизненный цикл. research/client455-map-time-source.md.

Selected local time/real_time input восстановлен с grade>=1,history/prefix boundary
и независимыми clocks:432ASCII cases/2628checks,20actual CHAT_INFO checks,commands→
weather/GPU2cases/69checks. Other local directives/full chat/GUI key events и old-CRT
locale остаются открытыми; это method-boundary проверка. Clock теперь10scalar
functions+256byte prefix/1037instruction bytes,1443checks/12FP modes. Подробности
research/client455-time-commands-source.md; область «Ввод и интерфейс» целиком открыта.

Ресурсный аудит M5 закрепил78MapEntity RPK,70BSP39/93EBP20 и20weather assets.
Header/table round trips,8tool parser tests и DDS mip sizes прошли, native/GPU
load в том цикле не выполнялись. Последующий source RPK/fopen/exists и particle end
подключён и проверен:18 907native module checks и30actual full-project checks;
следом selected consumers прошли actual map/GPU cases. research/client455-resource-io-source.md;
один weather path missing для3Tower R3X. Неверные metadata sizes/offsets не
исправлялись: research/client455-map-resources.md. Полного resource manifest ещё нет.

## Запись каждой возможности

Уникальный ID; источник обнаружения; SHA-256/VA/RVA для бинарного доказательства;
описание входов/состояний/выходов; особенности и ошибки эталона; соответствующий
исходник; способ сравнения; результаты; известные расхождения; уверенность.
Статусы: обнаружено → описано → реализовано → проверено; отдельно блокировано/неизвестно.
Намеренные исправления особенностей эталона согласовывать отдельно от восстановления.

## Известные открытые вопросы после первой сборки

RF_Online.bin получен и чисто пересобран в diagnostic configuration: /Od, reconstructed
Character interface/адаптированная библиотека и отдельные подтверждённые 455 branches.
Обычный WinMain не запускался; own full-project lab выполнял CPU и GPU scenarios.
Pure legacy OFF configurations и canonical optimized Release
не объявлены готовыми. Это сборочный результат M4, не финальная приёмка 455.
research/client-first-build.md; inventory/client-first-build.json.

- Восстановленный Character.h обеспечивает компиляцию; конструкторы, inline/default
  arguments и runtime ABI старой STL/CRT не проверены. research/character-library.md.
- Старый прямой FILE EOF доступ CharacterMR несовместим с UCRT. Изолирующий адаптер
  прошёл 1828 собственных проверок и настоящие text/binary loaders с CPU mesh effects
  (59 checks). Legacy SetEffect bridge bounded; original inline/bad-input behavior
  и 455 map/36 grades не доказаны. 455 draw source calls проверены статически, GPU нет.
  Менеджеры/empty renderer прошли 3630 проверок на unloaded records, setters — 18 ABI
  checks, exception helpers — 770
  сравнений с classic exports. Полный SDK ABI/exception unwind/render не доказан;
  research/character-effects-and-exceptions.md. Одного успешного link недостаточно для M4.
- Старый CLevel::GetFrustumNormalPlane вызывает себя (C4717); есть глобальная функция
  с тем же именем. Не исправлено; поведение/эквивалент в 455 ещё не установлены.
- _NEW_UI_ нужен текущим исходным классам предметов и включён для современной сборки;
  этим не подтверждено соответствие старого UI эталону 455.
- Логирование 455 проверено на 14 own cases/66 checks; lifecycle clear routine неизвестен.
  Success->lobby edge не содержит древнего CheckFiles, но остальные integrity/resource
  checks и полная login sequence ещё требуют аудита. Не считать их покрытыми.

Character prerequisite:8legacy functions/full InitVertex имеют source;245binding+
6732InitVertex checks/144cases/12FP modes standalone/full-client,4COFFtests и2actual
LoadRealData→source call destinations. Mesh/triangles/weights/matrices/errors/release
проверены через test-only COM capture. Это не Character455/GPU acceptance:
legacy1072/36byte vertex/heap blends отличается от4555803/64/inline;455normals negated,
Полный MESH08 runtime loader ещё отсутствует. Его format reader/writer готов:
858real files/12090meshes прошли lossless roundtrip;6304native checks standalone/
full-client,12samples/393parts/1309guarded truncations и7Python tests. Normal loader
ещё не использует модуль. research/client455-mesh08-format.md.
Отдельные packed455parent/bone kernels имеют source:2237checks/12real paired fixtures/
393meshes/455skeleton records и20overlap cases standalone/full-client. Normal
loader иполные skeleton/transform/animation/material/GPU consumers ещё открыты.
research/client455-mesh-bindings-source.md. Сами paired fixtures не доказывают
игровой выбор скелета иполную загрузку BN.
Constructor final state/header/matrix/material-request kernels source готовы:
14562checks/12real files/393parts/12FP modes standalone/full-client. Matrix provider
закреплённаяD3DX9_36;texture callbacks вtests scripted. Arbitrary matrix bitproof,
actual TextureManager/sharedGPU/destructor/full loader остаются открытыми.
research/client455-mesh-runtime-source.md. Проверка матричной DLL не закрывает D3D9renderer.
Последующее: реальный source Character RFS/DDS/TextureManager backend прошёл
8440checks standalone/full-client,80profiles/68texturepairs/all mip contents/
137renders,97real material parts/59bindings,COM/Dmalloc0;9Python tests.
Это выбранный texture domain. Normal model-loader,shared buffers,skinning/draw,
full device reset/unwind/private ABI/malformed/OOM/locale области ещё открыты.
research/client455-character-textures.md;client455-texture*.json. Не считать
приёмкой всего Character или renderer.
SharedGPUsourceunit:159173checks standalone/fullclient,12real files/393parts,
276nonzero-indexGPUuploads и117zero-indexskips. Capture bytes/failure/counter tests,
4physical synthetic indexed draws/rollover,COM/Dmalloc0.18ref bodies equalbothpins.
Это не полный shader/skin/animation/draw coverage:lab POSITIONT/COLOR declaration
не подменяет455declaration. Normal full model-loader/ownership ещё открыты.
research/client455-shared-buffers.md;inventory/client455-shared-buffers*.json.
Connected MESH08 route/lifetime:9953CPU/10021HALchecks standalone/full-client,
12files/393parts/276realuploads/59texturebindings. Dtor5803byte endstate/order,
reverse cookiearray,ownedrelease,reload overwrite иbounded nullallocationcleanup
проверены. Ownheap/COM/Dmalloc0. Это не full manager/filedispatch/BN/animation/
shaders acceptance;пары скелетов —tooling fixtures,known800byteprefix не полныйABI,
OOM/unchecked/full exception unwind открыты. research/client455-model-pipeline.md.
Selected455record/manager/rawMSH/refresh:850CPU/1138HALchecks standalone/fullclient;
whole1188byte ctor vs92instruction oracle/12FPmodes,manager4148/cache/ID/delete/clear/
dtor,18rawreads/12models/393parts/276uploads/59pointers. RealMSHизсобственногоRFS и
11loose models rawбайты равныpins.13APIs source/called,ownheap/COM/Dmalloc0.
Stickydispatcher9238A0 исследован,ещё не реализован;полныйBN/animation/typedconsumers/
shader/draw иunsafefailure equivalence открыты. Cache retains danglingpointers —
поведение сохранено,stale dereferences не сертифицированы. research/client455-character-manager.md;
inventory/client455-character-manager-checkpoint.json. Это не приёмка Character целиком.
Intermediate legacyMSH/BN reader/part720/model28 lifetime отдельно source:
4606standalone checks/12realBN455records+5synthetic4records/1183guarded prefixes/
7allocfailpoints/12FPmodes/6Python tests. File importer/converter/realruntime skeleton
иnormal dispatch этим не подтверждены. research/client455-legacy-model-reader.md.
Следом fullselectedvalid-input legacyMSH/BN converter/fileIO/MTG/weights/indexing/
binding source подключён:66627capture/14896HALchecks standalone/fullclient,
34runs972parts/832HALindexeduploads/2CPUretained.12actualBN→MESH08pairs393parts/
276uploads,heap/COM/Dmalloc0;10sourceAPIs verified. BNinitialmatrices/parent/blend
tables проверены,полныеANI/animation/skinningdraw/shaders/normaldispatcher/typed
consumers всё ещё открыты. Failure/locale/privateABI/unwind gaps явно перечислены
вresearch/client455-legacy-model-runtime.md;gateclient455-legacy-runtime-checkpoint.json.
Приёмка всегоCharacter/M6/M9 не заявлена.

## Приёмка

Secondary91E270 source state84/globals28/5effects подключёнкFrameMove;
36whole-statecases/2actualCoraBN/6updates standalone/fullclient,6source APIs,
heap/Dmalloc0. Relatedpose11pairs passed;неизменённыеbulk suites не повторялись.
Lab используетmodernMTsin callback:reference static__CIsin/SSE bitparity не
подтверждена,actor ctor/frameproducer/normal consumers/draw ещёopen.
CPUonly. Gateinventory/client455-secondary-checkpoint.json;
research/client455-secondary-motion.md. Это не fullFrameMove/M6/M9 acceptance.

Selected pose/FrameMove phases source:11realpairs/22ANI/132updates/2298skinmatrices
standalone/fullclientownentry,132selectedkeycases и8analytic scenes/12maskedFPmodes.
5source APIs,heap/Dmalloc0. CPUpose не является animateddraw. Secondary91E270,
producer кадров/manager/worker/normaltypedconsumers/shaders остаются открытыми.
Часть parent-ramp analytic expectations имеет1e-4допуск из-заpinnedD3DXinverse;
wholematrix skin/parent consistency exact. Не заявлять независимое полное сравнение
с выполнением referenceFrameMove. Gateinventory/client455-pose-checkpoint.json;
research/client455-pose-source.md. Старые runtime suites не повторялись.

Последующий selected ANI/rawIO/record284/lifetime/attachment/Character dispatcher
source:27files1062tracks/6Python tests;14513CPU/15181HALchecks standalone/fullclient,
22real ANI switches на11BN→MESH08pairs794parts/660HALuploads;13sourceC APIs.
Sticky flags/previous-current/borrowed key lifetime/cumulativecounter/raw leak
проверены;тест очищает leak отдельно после наблюдения,не маскируя его.
Normalconsumers/pose math/AnimationManager/asyncworker/shaders/full failure domains
остаются открытыми. Не считать HAL uploads приёмкой анимированного персонажа.
Gate inventory/client455-animation-checkpoint.json;
research/client455-animation-dispatch.md. M6/M6F/M7/M9 открыты.

По уточнению пользователя M9 — финальная приёмка этого клиента 455 без модернизации
графики. M6F и M7 входят в критерии; M8 не требуется. Восстановление рендера/шейдеров,
необходимых для поведения эталона, входит в восстановление клиента. Обновление
визуального стиля или перевод на новый графический API требует отдельной задачи.

- Полные исходники клиентской реализации и необходимых для неё компонентов,
  закреплённые зависимости, команды и повторяемая сборка RF_Online.bin.
- Реестр возможностей эталона с проверками реальных сценариев, граничных состояний
  и ошибок. Для форматов — эталонные образцы и round trip, где применимо.
- Сравнение эталона и восстановленного клиента при одинаковых входах; известные
  расхождения устранены, непроверенные области и недоступные сценарии явно перечислены.
- Все промежуточные замены/заглушки учтены. Заглушка с иным поведением не считается
  завершённой реализацией соответствующей возможности.

Пока остаётся неизвестное или непроверенное поведение, безусловное утверждение
«100% соответствие доказано» недопустимо. Итоговый отчёт должен указывать точные
границы проверки, даже когда весь выявленный реестр закрыт.
