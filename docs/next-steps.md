# Ближайшие действия — только клиент

Обновлено 2026-11-06. /Goal — M9: финальная приёмка клиента455 без модернизации
графики. M8 не требуется. Критерии docs/client-acceptance.md. Серверы/БД/GoMMO server
logic не разрабатывать; серверные исходники только читать как справочник.
Оригинальные EXE не исполнять, изменения только в собственных копиях/work/.

## Текущая точка

M0–M4 выполнены в описанных diagnostic compile пределах; M5 закрыт для выбранного
helper/interior/weather участка. M6 в работе. M6F/M7/M9 открыты. Compilation,
загрузка модели и uploads не являются финальной приёмкой клиента.

Последний участок — bootstrap050: FG/USEFG rawint, instance policy и6process/
4endpoint Connect state восстановлены. NetworkMgr.Create перенесён передengine,
позднийдубликат удалён. Ownnative FG/filename/двапроцесса/mutex/state/actualTCP
естественно exit0. Подтверждён455порядокclose→GetLastError:10061доclose,0после,
connectedfalse;это неуспешное соединение. ExactownPE3b93b0eb.../entry149010,
182client/20kernel/19facade,0unresolved;existingCreateвернул1.17scoped gates
PASS/PARTIAL. [Доказательства](../research/client455-bootstrap.md).

Следом051 —455client transport Create/config236/two configured processes,
standard/queued routing,pump/Accept/gate crypto request569CD0,framing/cipher и
packet layouts. Старые12handlers/oneprocess/13byteID-PW ещёне45535handlers/
twoprocess/state50-32. Затем настоящие ConnectToServer7D1150 timeout/wait/pump
передengine;неподменять connected/auth успехом. Послеэтого targetCreate/video/
BGM/managers/fullUI/login иигровыетаблицы. FT/ANSI/IME/layout/ILevel/world/full
shutdown обязательны. Исходникисерверов не изменять и не разрабатывать.

Предыдущий участок — launcher049: CCR93 для9стран,argv дляRussia/Europe,
country check и bounded identifier50/password32 восстановлены. Настоящий
WinMain читает launcher перед language;старый позднийread удалён. Данные
передаются настоящим полям CNetworkMgr;остальные455поля сохранены отдельно.
ExactownPE a64601c8... прошла существующий Create срезультатом1 до filters/
игрового цикла. Native metadata-тесты offline,аутентификация не выполнялась.
16scoped checks PASS/PARTIAL;M6/M6F/M7/M9 открыты.
[Доказательства](../research/client455-launcher.md).

Историческая очередь050 — оставшаяся bootstrap-цепочка455: FG_CB/USEFG,instance policy,
клиентский NetworkMgr.Create/ConnectToServer и его packet/state contracts.
Исходные опорные функции7D0CD0/7CF8A0/7D10A0/7D1150/562350. Послеlanguage
в455 сеть/соединение идут до engine;вownклиенте этот порядок ещё старый.
Восстанавливать по клиенту сoffline transport/packet fixtures;не подменять
connect/auth успешным значением. Legacy sender копирует ID/password по13bytes,
хотя455state уже хранит50/32;не считать wire/auth готовыми. Worldindex/personal/
premium/mode-потребители ещё не перенесены. Далее targetmanagers/video/fullUI/
login/game tables. FT/ANSI/text/IME/layout/ILevel/world/shutdown обязательны.
Серверные проекты/базы не изменять и не разрабатывать.

Предыдущий участок — sprites048: маршрут55target sprite names/localized→Common
восстановлен; только startup IDs0/1 подключены к старым UI consumers. Actual
CMainApp.LoadData/CGUIMouse используют реальные ko-kr/ru-ru packs;DXT5/прочие
форматы,содержимое текстур,кэш,кадр и естественный exit0 проверены. Exact ownPE
d431094d... прошла оставшуюся существующую UI init/LoadData/title allocation
до launcher file API (RVA B354A),без обхода загрузки.15scoped checks PASS/PARTIAL;
полный интерфейс/вход/455Create не приняты.
[Доказательства](../research/client455-sprites.md).

Историческая очередь049 — target455 launcher/bootstrap order и клиентский контракт входных
данных. Старый GetDataFromLauncher не проверяет CreateFile/ReadFile и использует
старую DefaultSet.tmp schema;не пропускать эту точку на отсутствующем файле и
не выдавать её за455. Восстановить по7D04E0 связанную последовательность
nation→launcher→language→FG_CB→clientnetwork→engine/BGM и контракты ошибок.
Работать с собственными offline fixtures,не подменять результат/auth и не
разрабатывать серверы. Затем нужные target managers/video/полный Create и UI
входа. Игровые таблицы остаются обязательны: _CreateCharDataMgr только создаёт
объект,реальное IO наступает позже. Остальные UI IDs отличаются от legacy;
не применять старые номера к target55. FT/ANSI/text/IME/layout/ILevel/world/
network/shutdown остаются обязательными доM6F/M7/M9.

Предыдущий участок — lifecycle047: null-level ветка UnloadLevel восстановлена
по обоим 455 PE. Реальный глобальный CMainApp/CLand в трёх состояниях и оба
GUI-приложения без создания Land завершились естественно с exit0. Полная PE
11833d1e... собирается без unresolved; 14 scoped checkpoints PASS/PARTIAL.
Full ILevel/созданный игровой мир/полный WinMain не приняты.
[Доказательства](../research/client455-lifecycle.md).

Историческая очередь 048 — дальнейший normal Create: _CreateCharDataMgr в global.cpp,
его реальные таблицы и соответствующий менеджер 455. Определить подтверждённые
порядок и формат, затем пройти следующую настоящую границу Create на исходных
данных 455. Не обходить загрузку ради запуска. Цель ближайшего последовательного
участка — полная инициализация и реальный интерфейс входа; сеть остаётся только
клиентской. Typed ILevel/мировой lifecycle, FT/ANSI/text/IME/layout, launcher/
FG_CB/network/BGM и полный shutdown обязательны до закрытия M6.

Предыдущий участок — font046: GDI/Unicode font/cache/draw иобычный enginebridge
подключены. Actual CGUIText вывел Hangul/кириллицу изNDLanguage;frames==wideAPI,
GDIoracle atlas/metrics/cacheeviction прошли;обаownGUIprobes exit0. FullPE
88942d08.../entry1485A0 прошлаnormalfont/D3D/Character startup.13scopedchecks
PASS/PARTIAL;M6/M9OPEN. research/client455-font.md.

Историческая очередь 047 — normalearly-abort/lifecycleCLand/CMainApp:oldDestroy доCreate
вызываетnullLevel->ReleaseLevel. Зафиксирован ownRVA7DD9C READnull+158h при
первом неполномlabexit. Не выдумыватьguard радизелёного теста;сверить455 ctor/
destroy/unload/ownership. TargetLandCreate7C7AC0 alloc8wrapper7C7B60;это иной
контракт,чемстарыйfullCLevel. ЗатемдальнейшийnormalCreate/data/UI/launcher.
FTconfiguredfont8C5C60,ANSIcache,полныйtextAPI/wordwrap/IME/UIlayout остаются
обязательнымиM6доM6F. OldCGUIText width6 наbyte несертифицирован;backbuffer
640x500 vsviewport480 —незакрытый sizinggap. Source RAII freesunusedstates
вместоoriginalleak;unsafe/OOM/x87domains невыдаватьзаэквивалентность.

Предыдущий участок — language045. EDF/NDLanguage reader/index lookup и DBCS
восстановлены;9realEDF byte roundtrip и11CRT/codepage cases прошли. Exact own
WinMain загрузил Korean949 иRussian1251,послеKorean normal D3D/Character
сохранился. NewownPE1fc267d5.../x86/entry14A920,13facade CPP,link0unresolved.
Font/text/UI ещё не приняты. research/client455-language.md;M6/M9OPEN.

Историческая очередь046 — actualfont/text provider: setter8C5A80 иconsumers globalsBF7718/
BF7618/BF7818/BF781C/BF7820. Сверить constructor/privateInit/glyphlayout455 с
legacyCR3Font(name85bytes,DEFAULT_CHARSET,fixedheight12). Подключить выбранный
normaltext/UI consumer к455query ипроверитьнастоящий текст/DBCS input.
Не считать загруженные строки отрисованным интерфейсом. Затем полный
Create/data readers/UI,ETCAction factories/launcher/FG_CB/network order/BGM и
обычный lifecycle/shutdown. NDLanguage en-us/th-th в установке не найдены;
не подменять их чужими пакетами,продолжать доступные клиентские участки.

Предыдущий участок — nationpaths044. Выбор11стран/корня данных455 подключён
до engine в normal WinMain; реальные profile/case/ошибки проверены. Новая
own PEcb64af10.../x86/entry1496C0 прошла actual partial CMainApp::Create:
Character/bone/mesh/animation/bounds managers; app device==Character device.
Остановка до _CreateCharDataMgr и старых игровых таблиц. Короткие регрессии/
кадры прошли. research/client455-nation-paths.md; checkpoint PARTIAL/M9OPEN.
Адреса checkpoints брать из current own-entry.json,не main+1D/+30.

Историческая очередь045 — полный locale/data bootstrap перед UI: country factory8321E0,
ETCAction manager8327B0(1) codepage vslot76,CRT locale compare/font8C5A80,
NDLanguage601EF0/603130 и EDF reader5EEC00/5EE900/5EEB90 на реальном файле.
Сейчас CRT/font/charset только metadata; корень опубликован,но full selector
ещё не реализован. setlocale category1=LC_COLLATE;USA uses UK CRTlocale.
Нельзя country7/Russia класть в старые3language arrays или выдавать успешное
path init за язык455. Затем normal data consumers/Create/UI/launcher.
Target WinMain7D04E0 имеет порядок nation→launcher→language→FG_CB.ini→network/
connect→engine→WaveList/BGM→device/Create;legacy пока ему не соответствует.
Восстанавливать подтверждённые реальные consumers без выдуманных root copies.
Дальнейшие network сценарии проверять как клиентский контракт; серверы не
строить/менять, ввод/аккаунты не использовать без необходимости задачи.
Отдельный gap: camera branch455 сбрасывает console index18, а старый table
имеет17entries; не записывать за его границу и не считать весь wrapper готовым.
После bootstrap — UI/resources/launcher и normal lifecycle/shutdown.

Предыдущий участок — startup042. Точная own RF_Online.bin041 (SHA39062b2c...)
действительно прошла CRT и обычный WinMain до успешного InitR3SoundSystem.
Engine bootstrap/Miles return1 и фактические providers проверены. Debugger
останавливает её перед D3D/window/Create; exit подтверждён. Production PE не
менялся, старые runtime suites не повторялись. research/client455-startup.md;
inventory/client455-startup-checkpoint.json PARTIAL; M9 открыт.

Историческая очередь042 — normal D3D/window/device initialization и startup contracts455.
Сначала сопоставить target455 startup/config/locale с legacy WinMain: root
DataTable/cryp.dat/advr.dat отсутствуют, настоящие файлы лежат в ko-kr. Не
копировать их в выдуманные пути до подтверждения locale policy455.
Для дальнейшего own lab запуска обеспечить оконный режим: текущий Release
WinMain принудительно вызывает ForceFullScreen, ini FALSE сам не помогает.
Проверять реальное InitR3D3D/его callbacks и следующий Create, без подмены
успешными no-ops. Не выдавать lab window/config override за восстановленную
production семантику455. Работать из lab с собственными runtime/config копиями.
Полные WaveList/playback/music/3D audio, ABuse/Adv/PDLL runtime ABI, графический
startup/launcher, shutdown и UI/network/gameplay остаются открытыми.

Предыдущий участок — accounting041. Normal mesh/buffer/ANI counters теперь
process-wide; существующие texture counters читаются из их настоящего owner.
Legacy diagnostic consumer читает source snapshot семи подтверждённых полей,
без подстановки пустого global или наложения неизвестного private ABI.
Реальные ANI в двух renderer, mesh lifetime/wrap, реальные model/GPU descriptors
и сохранение cumulative значений после release прошли. 182 client +11 facade
+20 kernel CPP собираются; full normal RF_Online.bin link PASS/0 unresolved.
research/client455-normal-accounting.md; checkpoint PARTIAL. M9 открыт.

Историческая очередь041 — normal startup/initialization. Проверить импорты и delayed DLLs
собственного PE, ранний WinMain/CRT/global construction, нужные client assets/
конфигурацию и логирование в отдельном lab. WinMain сначала InitR3Engine и
InitR3SoundSystem, затем InitR3D3D/Create и фильтры ABuse/Adv; учитывать реальные
DLL API/CRT, не подменять успешными no-ops. Сначала составить воспроизводимый
offline startup набор, затем выполнять только собственную сборку из lab.
Отсутствие .rsrc в PE зафиксировано; найден engine RC с иконкой, необходимость
конкретных ресурсов ещё проверить по callers. Оригинальные EXE не запускать,
серверы не строить, исходную установку не менять. M6F/M7/M9 остаются открытыми.

Предыдущий участок — characterclock040. Таймер Character 91EA80 восстановлен
отдельно от engine clock; actual _R3CalculateTime и mainapp caller подключены.
QPC/fallback/округление/независимость проверены; прежние renderer/ANI/BBX/effect/
shadow сценарии прошли. 182 client + 10 facade + 20 kernel CPP собираются.
Полный линк: только g_ChMemoryInfo. research/client455-character-clock.md;
inventory/client455-character-clock-checkpoint.json: PARTIAL. M9 открыт.

Историческая очередь040 — process-wide Character accounting с настоящими producers.
Подтверждены адреса texture bytes/count11895F8/FC, shared buffer bytes/count
1189600/04, raw ANI cumulative1189608, mesh ctor count/bytes118960C/10.
Debug consumer7F26F1..7F2798 совпадает со смыслом старых семи полей. Отдельный
ctor9312E0 обнуляет32байта, но не имеет найденных xrefs; принадлежность восьмого
поля ещё требует проверки. Texture accounting уже process-wide, mesh/buffer/ANI
в normal Runtime пока per-renderer: исправить владение без подмены live heap total.
Не подставлять пустой глобал; проверить накопление/release/wrap/multiple owners,
затем полный normal link и отдельно normal initialization.

Предыдущий участок — effects039. Чтение EFF, registry, file lists, InitEffect,
SetPartEffect/SetMeshEffect и particle/entity views подключены. Проверены
реальные EFF, выбор/кеширование/сброс и эффект с настоящей DDS на модели/GPU.
182 client + 8 facade + 20 kernel CPP собираются; полный линк: только
g_ChMemoryInfo и _R3CalculateTime. research/client455-effects.md;
inventory/client455-effects-checkpoint.json: PARTIAL. M9 открыт.

Историческая очередь039 — восстановить accounting и Character clock по 455 и
реальным callers; не подставлять пустой глобал или no-op ради линковки.
Проверить layout CHMEMORYINFO (старые 28 байт против замеченного ctor 32),
владение счётчиками и связь Character clock с уже восстановленным engine clock.
Затем получить полный normal link и отдельно проверить normal initialization.
Full particles/entity math, неизвестный pattern tail grades9..35, shadow
lifecycle, blend producers и UI/network/gameplay остаются открытыми.

Предыдущий участок — effecttables038. Чтение PatternList/ItemEffectList и
IsHaveMeshEffect подключены;2246паттернов/4600предметов и выборки проверены.
Особенность455: readerчитает9значений, но копирует36DWORD; tail27 неизвестен.
Он помечен явно, неизвестный query вызывает ошибку. Не считать его восстановленным.
182client/6facade/20kernelCPP собираются; полный линк15символов. M9 открыт.
research/client455-effect-tables.md; checkpoint PARTIAL.

Историческая очередь038 — EffectList/FileList/globals, EFFbinary92B380, SetPartEffect/SetMeshEffect/
InitEffect иparticle/entityslots, modelIsHaveEffect, Characterclock/accounting.
Навигацияraw вartifacts/normal-effects455, не повторять уже готовый table reverse.
SetMeshEffect используетдополнительный renderercontext455 и status-aware selection.
Не подставлять старые offsets или принимать неизвестные grades9..35 за ноль.

Предыдущий участок — normal shadow037. BeginShadow/EndShadow подключены;
реальная модель дала силуэт в512x512 текстуре, прежние два цветных кадра совпали.
182client/4facade/20kernelCPP собираются; полный линк20символов без других ошибок.
research/client455-normal-shadow.md; checkpoint PARTIAL. M9 открыт.

Историческая очередь037: эффекты/таблицы/слоты, _R3CalculateTime и accounting.
Сохранить обнаруженный контракт: Begin возвращает HRESULT, успех0, при этом
оба callers455 используют if(result) и пропускают End. Тест явно завершает
собственный проход. Ground projection/GetShadow/normal actor lifecycle ещё открыты.

Предыдущий участок — normal contracts036. AnimationReset/RematchParent/SetEyeVec,
SetTexPath/ImportBoundBox подключены и проверены. Реальная модель прошла сброс,
повторное назначение ANI и перепривязку родителей; два кадра совпали с035.
Все182client+3facade+20kernelCPP собираются; полный линк22символа без других
ошибок. research/client455-normal-contracts.md; checkpoint PARTIAL. M9 открыт.

Историческая очередь036: оставшиеся22 включали эффекты/таблицы/слоты/shadowtargets,
_R3CalculateTime и accounting. Готовые методы не восстанавливать повторно.
Отдельно найти normal включение renderer33840/инициализацию33844/продвижение
blendelapsed692 и полный actor lifecycle; включённый reset проверен искусственно,
нормальную инициализацию это не доказывает. Затем полный RF_Online.bin и приёмка.

Предыдущий участок — normal renderer 035.
20 исходных CPP Character теперь собираются в RFClient455Kernels.lib с едиными
типами normal/include; старые отдельные component archives не линковать в эту ветвь.
Кадры до/после пересборки совпали. Происхождение кода — normal-preparation.json.
Обычные CUnity/FrameMove/CRender рисуют
реальную модель на D3D9. Два кадра через координаты/матрицу равны, фильтры видимости,
alpha/material/свет/состояние и освобождение проверены. Полная линковка ещё открыта:
27 методов/данных. research/client455-normal-renderer.md;
inventory/client455-normal-renderer-checkpoint.json PARTIAL. M6/M6F/M7/M9 OPEN.

Историческая очередь035, заменена текущей выше: эффекты/таблицы/слоты,
AnimationReset/RematchParent/SetEyeVec, SetTexPath/ImportBoundBox, shadow target
и _R3CalculateTime. Переиспользовать готовые kernels. Затем полный RF_Online.bin
и настоящий normal lifecycle/игровая приёмка. Отдельно выяснить инициализацию
blendDuration +33844, profiling/static CRT trig, batch/ortho/reset/fullscreen.
Тест задаёт blendDuration=150; нормальную инициализацию это не доказывает.

Предыдущая очередь ниже — история.
Предыдущий участок — normal port 034, work/client455-port/normal. Все 180 исходных
клиентских единиц компилируются с типами 455/D3D9; после выделения CUnity/CAnimation
получены 182 объекта x86/MT. Настоящие CAnimation и CUnityAniMgr загружают ANI.
Полная линковка открыта: 39 методов/данных, без CharacterMR.
inventory/client455-normal-link.json; research/client455-normal-port.md;
inventory/client455-normal-checkpoint.json имеет статус PARTIAL.

Следом подключить готовые pose/draw через подтверждённые normal FrameMove/
DrawCharacter/SetState/UnSetState и состояние камеры/света. Затем LoadMeshData,
setters/reset/bounds, эффекты и слоты частиц. Обёртки проверять по клиенту 455.
Готовые ядра повторно не восстанавливать, старый SDK не возвращать для link.
Далее нормальная RF_Online.bin и приёмка по client-acceptance.md. База
work/client-build и engine033 сохранены. M6/M6F/M7/M9 OPEN.

Очередь ниже — история, заменена текущей очередью выше.
Предыдущий unit — начальный engine9port033 в work/client455-port.67units x86/MT
собраны. Настоящие R3ConfirmDevice/R3InitDevice/Grass shader иsource Characterowner
на одном D3D9 HAL device прошли; Platform01 отрисован с23helpers/8interiors идвумя
weather layers,cleanup0. Gate inventory/client455-engine9-checkpoint.json;
research/client455-engine9-port.md. Базоваяnormalсборка не менялась.

Практический следующий шаг: source Character455.h/facade и реальные180clientTUs
в этой новойкопии, затем RF_Online.bin с R3Engine455. Переносить typed model/
animation consumers вместе;39SDKfunctions/150field candidates ещё открыты.
Не rawcast и не возвращать CharacterMR для успешного link. Готовые source kernels
и владелец ресурсов не требуют повторного восстановления. Fullengine455state/
camera/reset/shaders/allfullscreen modes/ABI/CRT иM6/M6F/M7/M9 ещёоткрыты.

Предыдущий unit — renderer owner032: source constructor/device binding/destruction
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

Актуальный050: audit_client455_bootstrap.py → prepare_client455_normal.py →
build_client455_normal.py → probe_client455_normal_consumers.py →
link_client455_normal.py → audit_client455_own_entry.py / audit_client455_startup.py.
Затем probe_client455_bootstrap.py, актуальные own startup/contracts/device/
--after-create пробы и checkpoint_client455_bootstrap.py. Все Python через
scripts/Invoke-Python.ps1. Native build/run в разрешённом режиме. Старые команды
ниже относятся к историческим участкам; не запускать большие suites без причины.

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
