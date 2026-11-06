# Дорожная карта восстановления клиента RF Online 455

Обновлено 2026-11-07. По прямому указанию пользователя: работа ИСКЛЮЧИТЕЛЬНО НАД КЛИЕНТОМ.
Старые клиентские исходники и R3Engine — база, клиент 455 — объект реверса.
Серверы, БД и серверная логика вне задачи. Прежний серверный план отменён.
Серверные исходники разрешены исключительно для чтения как справочник клиентских
контрактов, без изменений и сборки. Каждый вывод проверяется на клиенте 455.

Конечная цель — исходники RF_Online.bin с полным функционалом и поведением выбранного
455. Этапы ниже — промежуточные результаты. Критерии полноты и начальная матрица:
[client-acceptance.md](client-acceptance.md). Не закрывать проект после сборки/запуска.

## Текущий статус

081: подключены базовые particle/entity RVP passes иsharedFX deferred lifecycle.
Stockclip269ticks/148particle/6entitydraws,15reviewedframes,3карты иноваяPE/Create1
прошли. Исправлен ABI weather helper1148/208->1296/212 ипроверены actual allocations.
Далее082 — audio/остальные RVP providers иполныйTutorial/game;advancedFX/global
resource lifecycle ивсе прежние gaps остаются. M6/M6F/M7/M9 OPEN. Процент всего
клиента не измерен;закрытые M0–M5 неравнозначны доле готового поведения455.
[Доказательства](../research/client455-rvp-effects.md).

Предыдущий результат:

080: RVP resources/animation/dummy/culling/отдельные позы общих моделей/
model draw/EFF подключены к обычному клиенту. Real12actors/4models,9distinct
pose ticks/459restoredparts,11reviewedframes,3camera regressions иexactPE/Create1
прошли. Полные particle/audio/Tutorial/game остаются OPEN. Далее081 — настоящий
particle/entity pass иshared-effect lifecycle, затем остальной RVP иTutorial.
M6/M6F/M7/M9 открыты; процент полноты не измерен.
[Доказательства](../research/client455-rvp-actor.md).

Предыдущий результат:

079: ordinary RVP camera/timeline перенесён в production path. Три мира/
27camera events, intro26,46viewedframes иточнаяPE/Create1passed. Actor/effect/
audio/timer providers иполныйTutorial ещёOPEN;далее080. M6/M6F/M7/M9 открыты.
[Доказательства](../research/client455-rvp-runtime.md).

Предыдущий результат:

078: перенесён RVP load-model/interpolation;44 файла/615 описаний объектов/
1569 команд сверены независимо,12 команд проверены native. Ordinary player ещё
compiled stub; PE из077. Далее079 — реальные runtime bindings/исполнение и
CGP_Tutorial. M6/M6F/M7/M9 открыты.
[Доказательства](../research/client455-rvp.md).

Предыдущий результат:

077: восстановлены RTMovie flags, полосы/логотип и default FOV; intro связан
с движком. Flags8/GPU6/intro26/fullscreen18/40 просмотренных кадров/Create1
прошли. Полный RVP player пока compiled stub; Tutorial/game integration открыта.
Далее 078 — реальный RVP и Tutorial owner. M0–M5 закрыты в своих ограниченных
критериях; M6/M6F/M7/M9 открыты. Процент полноты пока не измерен.
[Доказательства](../research/client455-movie-state.md).

Предыдущий результат:

076: восстановлен настоящийfullscreen motion-проход455;intro mode/density
связанысдвижком. GPU18/3worlds26cameras/34viewedframes/failedBegin/lowVRAM512
passed,PE/Create1passed. ActualTutorialowner/QBI/cameraControls/factory ещёOPEN.
Далее077;M6/M6F/M7/M9OPEN.
[Доказательства](../research/client455-fullscreen-effect.md).

Предыдущий участок:

075: перенесенаintrosequence455;26actualcameras на3worlds,fade/skip/reload,
29viewedGPU иDmallocbalancePASS. Normalfacadeproviderещёunusedactualstage;
fullTutorial/QBI/newenginecontrols/factoryOPEN. PE/Create1passed,runtimeequal074
exceptlinktimestamps. Далее076 — настоящийTutorialowner;M6/M6F/M7/M9OPEN.
[Доказательства](../research/client455-tutorial-intro.md).

Предыдущий участок:

074: настоящие Bellato/Cora/Accretia455 загружаются/рисуются черезCLand. Owner
иleveldestructorперенесены;reload/GPU/collision/Dmallocbalance и6кадров проверены.
FinalPE/Create1 passed. FullILevel/Empty/INS иTutorialещёOPEN. Далее075 — actual
Tutorialstage/cameraintro/Avatar/localhandlers/QBI/fourstage.M6/M6F/M7/M9 OPEN.
[Доказательства](../research/client455-world.md).

Предыдущий участок:

073: ordinary Avatar stage/skip,MainApp Create gate,login иlocalTutorial routing
перенесены. Knownignored/1-17transport проверены;полныеlocalhandlers ещёOPEN с
явнымотказом. NewPE/Create1 иwindow/boardpassed;22кадра равныreviewed072.
Factorylegacy3/modulo остаётся. Далее074 — настоящийworld/BSP39/Tutorialcamera,
затемполнаяинтеграцияAvatar/handlers/QBI/fourstage. M6/M6F/M7/M9 OPEN.
[Доказательства](../research/client455-avatar-stage.md).

Предыдущий участок:

Участок072: исходное CGUIBriefingWindow инастоящий screen capture готовы,
CTutorialBoard probe использует actual rich/key provider. Ko/Ru3pages/22GPU,
real mouse queue,portrait timers/cells иexactnewPE/Create1 прошли. Обычный
Tutorial stage/Avatar/world ещёнеподключены. Далее073;M6/M6F/M7/M9 OPEN.
[Доказательства](../research/client455-briefing-window.md).

Предыдущий участок:

Участок071: frame/key/animation sourcecontrols455 восстановлены иKo/Ru/GPU
проверены. Typingbasefillошибка070исправлена. CurrentPECreate1;runtimebyteequal070
excepttimestamps,oldGUI evidence reusedwithoutunchangedsuites. Actualwindow
providerещёOPEN. Далее072 — outline/portrait/window/capture/pages/events/provider.
[Доказательства](../research/client455-briefing-controls.md). M6/M6F/M7/M9 OPEN.

Предыдущий участок:

Участок070: отсутствовавший CGUITextTypingBoard восстановлен как dependency
настоящего брифинга. Ko/Ru componenttraces/GPU иsharedrenderer44unchangedframes
passed,normal8f009924…/Create1. Ordinarybriefing instanceещёнет,10gatesPARTIAL.
Далее071 — полный window/key/portrait/frame/provider,затемAvatar/world/Tutorial.
[Доказательства](../research/client455-text-typing.md). M6/M6F/M7/M9 OPEN.

Предыдущий участок:

Участок069: обычный modal.SetMsg теперьplain/rich,pixel extent,color/order455;
300/250 fallback only. Ordinary rich caller подключён,providersretained.
Ko/RuGDI/12групп,10viewedframes,affectedGUI/Create1 passed. Productionc22502fa…,
9gatesPARTIAL. Emptyfragment extent/basevirtualSetSize/allwrapper domains OPEN.
Далее070 — полныйCGUIBriefingWindow,затемAvatar/world/Tutorial/fourstage.
[Доказательства](../research/client455-message-sizing.md). M6/M6F/M7/M9 OPEN.

Предыдущий участок:

Участок068: базовые GUI mouse/key/focus/queue455 и main-list Add/Remove перенесены.
Double7/right8,300ms/DWORDwrap,modal guard,key dedup/focus order/средняя кнопка
проверены Ko/Ru. Ordinary arrows unbound в target;прежний adapter удалён,EX
binding сохранён. Productionde76223c…/existingCreate1,affectedGUI passed;
другие2lists/render layers/fullGUI/IME/целевыеcallers остаются OPEN. Далее069 —
production message sizing/rich callers,затем полный briefing и actualTutorial/
fourstage. Оставшиеся GUI/lifecycle gaps учитывать в M6F.
[Доказательства](../research/client455-gui-input.md). M6/M6F/M7/M9 OPEN.

Предыдущий участок:

Участок067: EX связан с обычным CGUIMiniMapWindow. Восстановлены opacity
styles0/1,alignment,80/80Init,alpha mappings и Draw455. Настоящий MouseDev→owner→
EX→queue путь,81amount и GPU прошли Ko/Ru;production providers retained,
0def3dce…/existingCreate1. Остальные controls/карта/zoom555940/parent input455
открыты. Далее068 — общий GUIObject/Container input/show/focus/parent wiring;
затем production rich/message sizing/briefing и actual Tutorial/fourstage.
[Доказательства](../research/client455-minimap-opacity.md). M6/M6F/M7/M9 OPEN.

Предыдущий участок:

Участок066: классы scrollbar EX/Var восстановлены в обычном source provider;
Ko/Ru full-object/queued input/GPU проверки прошли. EX имеет подтверждённого
владельца CGUIMiniMapWindow; его helper7B2C60 и настоящие события ещё не перенесены.
Var direct ctor xrefs отсутствуют;action15 не загружается ordinary loader455
(actions<16),horizontal track читает uninitialized local. Пробы сохраняют эти
ограничения. Productionb24f1f09…/existingCreate1;affected GUI PASS. Далее067 —
EX minimap helper/owner и parent input,затем message sizing/rich callers/briefing/
actual Tutorial/fourstage. M6/M6F/M7/M9 OPEN.
[Доказательства](../research/client455-scrollbar-variants.md).

Предыдущий участок:

Участок065: обычный scrollbar получил composite thumb, layout/amount/snapping/
mouse/repeat rules455. Ko/Ru GPU/queued input, затронутые GUI probes и Create1
прошли. EX/Var, полная parent routing и resource/skin parity ещё открыты.
Далее066 — варианты/parent input, затем production rich callers/message sizing/
briefing и actual Tutorial/fourstage. M6/M6F/M7/M9 OPEN.
[Доказательства](../research/client455-scrollbar.md).

Предыдущий участок:

Участок064: обычная текстовая панель получила caches455, pixel wrap/retention/
draw; typed FONT_INFO16/TextInfo28 и rich/extent проверены в full-object probe.
Production rich callers/message sizing ещё открыты. Новая PE сохранила Create1;
затронутые GUI regressions прошли. Далее065 — полный scrollbar, затем реальные
rich callers/briefing и actual Tutorial/fourstage. M6/M6F/M7/M9 OPEN.
[Доказательства](../research/client455-text-board.md).

Предыдущий участок:

Участок063: перенесены GDI byte width/DBCS fit/cache высоты и обычные размеры
CGUIText455. Ранняя геометрия0.7 ожидает создания шрифта. Korea/Russia oracle/
GUI проверки и кадры прошли, новая полная PE сохранила existingCreate1.
Далее064 — полный TextBoard и scrollbar, затем briefing и actual Tutorial/
fourstage. FreeType/16byte font scale ещё открыты. M6/M6F/M7/M9 OPEN.
[Доказательства](../research/client455-text-metrics.md).

Предыдущий участок:

Участок062: обычные модальные окна получили подтверждённые кнопки/подписи/
рамку/отступы и input455. Korea/Russia GUI/D3D/nativeexit0; новая полная PE
прошла existingCreate=1. Далее063 — общий text-board/scrollbar, затем полный
briefing и настоящий Tutorial/fourstage. M6/M6F/M7/M9 OPEN.
[Доказательства](../research/client455-modal.md).

Участок061: CTutorialBoard control и вызов настоящих модальных окон2/3
проверены с обычными клиентскими объектами и D3D. Rich-view и stage/Avatar
в harness тестовые. Видимое расхождение кнопочных спрайтов записано.
Далее062 — обычные модальные окна455, затем полный briefing и реальный
Tutorial/fourstage. [Доказательства](../research/client455-tutorial-board.md).
M6/M6F/M7/M9 открыты.

Участок060: QBI19–46 rules перенесены; composition47families/99programs prepared.
Recording-host проверки прошли. Реальное исполнение сценариев/UI/Avatar/world
и обычный Tutorial ещё открыты. Далее061 — CTutorialBoard/briefing и реальные
providers, затем jointTutorial/fourstage.
[Доказательства](../research/client455-tutorial-actions.md). M6/M6F/M7/M9 открыты.

Участок059: Move6–8/Creation9–11/Position12–18 перенесены и проверены с recording
host. Factory создаёт0–18; остальные28 типов и настоящий world/Avatar host
открыты. Item packet DWORD+25 остаётся неподтверждённым. Далее060 — UI/Equip,
затем Cursor/Combat/Item, board/briefing и Tutorial/fourstage.
[Доказательства](../research/client455-tutorial-spatial.md). M6/M6F/M7/M9 открыты.

Участок058: QBI scheduler/refresh/flags/shared timer и правила сообщений/
ожиданий восстановлены, standalone native с recording host прошёл. Actual
UI/Avatar host и41остальной селектор открыты. Далее059 — Position/Move/Creation,
затем остальные процессоры, board/briefing и joint Tutorial/fourstage.
[Доказательства](../research/client455-tutorial-runtime.md). M6/M6F/M7/M9 открыты.

Участок057: восстановлен SCP reader47селекторов; самостоятельная C++ библиотека
прошла99реальных сценариев, побайтовую и семантическую сверку. Старый reader28
типов не подходит; новое исполнение команд пока открыто. Далее058 — состояния
заданий/CQBI processors и панель обучения, затем Avatar/scene/fourstage.
[Доказательства](../research/client455-tutorial-scripts.md). M6/M6F/M7/M9 открыты.

Участок056: ordinary CAniCamera loader1.2/1.3, FOV scale и playback455
перенесены;4realCAM/synthetic1.3/actualD3Dprojection/release проверены.
FullPE собрана, existingCreate=1. Далее057 — Tutorial scene/Avatar/UI/local
handlers/fourstage; fullcamera math/FOVconsumer ещё открыты.
[Доказательства](../research/client455-camera.md). M6/M6F/M7/M9 открыты.

Участок055: обычный CGameProgress получил next DWORD и целевой порядок
Input/exit/Frame/Render/reset. Настоящие методы и counters проверены, новая
полная сборка проходит existingCreate. Фабрика4stages/Avatar/Tutorial ещё
открыты; следующий056 продолжает их зависимости и интеграцию.
[Доказательства](../research/client455-progress-base.md). M6/M6F/M7/M9 открыты.

Аудит054 уточнил обязательную работу M6: в455 четыре stage classes, включая
Tutorial, а старая база использует три и modulo-переход. Восстановить stage/
Avatar/Tutorial совместно, затем LoginUI/world transitions. Tutorial входит
в M6F/M9; графика M8 по-прежнему отдельно. Runtime в054 не менялся.
[Доказательства](../research/client455-progress.md).

Последний участок M6 — account053: восстановлены gate seed и account wire
пакеты84/342/88, ответы50/24 и world records72/capacity300. Обычные методы
send/receive/dispatch и GUI pending прошли компонентную проверку; полная PE
собралась и сохранила запуск до existingCreate=1. Аутентификация/fullUI/мир ещё
открыты. Далее054 — country/ini/mode providers, остальные handlers и loginUI.
[Доказательства](../research/client455-account.md). M6/M6F/M7/M9 открыты.

Предыдущий участок M6 — connection052: Connect/events-only wait до engine,
строгие тайм-ауты/задержка callback и102-entry receipt budget восстановлены.
Обычный CCR WinMain прошёл реальное TCP-соединение и существующий Create.
Это не аутентификация. Успех полного Russian/European bootstrap ещё открыт;
подтверждённые endpoint0/1 не перенаправляются искусственно.
Далее053 — gatecrypto request/reply, packet state/35handlers и полный вход/UI.
[Доказательства](../research/client455-connection.md). M6/M6F/M7/M9 открыты.

Последний участок M6 — network-codec051: в обычных CNetProcess отправке/приёме
работают восстановленные AES192-CBC, формат пакетов и буферы20КБ/1МБ. Создаются
два сетевых процесса, вместимость — шесть. Независимый Windows AES и настоящие
потребители подтвердили байты/фрагментацию/переход через конец буфера.
Далее052 — порядок сетевых событий, Connect wait до движка, затем остальные
пакеты и полный интерфейс входа. [Доказательства](../research/client455-network-codec.md).
M6/M6F/M7/M9 открыты.

Последний участок M6 — bootstrap050: FG/USEFG, country instance policy и
per-process Connect state/raw error contract подключены. ActualNetworkCreate
перенесён передengine;existingCreate вернул1. Закрытый TCPпорт и независимый
WinSock oracle выявили подтверждённый по455 порядок,теряющий10061послеclose;
connectedfalse. Full455transport/35handlers/framing/crypto/auth ещёоткрыты.
Следом051 — эти клиентские контракты,затем Connect wait/pump доengine иfullUI.
[Доказательства](../research/client455-bootstrap.md);M6/M6F/M7/M9 открыты.

Новейший участок M6 — launcher049: sourceCCR93/argvпрофили иcountrycheck
подключены кWinMain передlanguage;старыйпозднийread удалён. Полянастоящего
CNetworkMgr проверены offline;собственный existingCreate вернул1,затемstop
доfilters/game-loop. Full455bootstrap/connect/auth/UIещёоткрыты. Следом050 —
FG_CB/instance policy иclientnetwork Create/Connect/state/packet contracts.
[Доказательства](../research/client455-launcher.md);M6/M6F/M7/M9 открыты.

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

1. M6/082: ambient/event audio иостальные RVP magic/trace/screen/timer/collision/shadow providers; advancedparticle/entitymath/globalChef lifecycle/material-lightreset; CGP_Tutorial Load/Create/cameraintro/frame/input иrealAvatar/
   localhandlers/feedback/board47QBI/fourstagefactory. BSPbackend/owner/reload074
   проверены натрёхкартах;полныеILevel/Empty/INS/игровоймир ещёOPEN.
2. Полный интерфейс входа,аутентификация ипереход вигровой мир. Учитывать
   screen/window lifecycle,capture,currentstage guard,device-reset/resources,
   otherlayers/IME/basevirtualsize/wrappers,не объявляя весьGUI соответствующим455.
3. Завершить остальные M6 области и реальные сценарии приёмки, включая полные
   Character/animation/effect/shader/lighting/lifecycle и численные разрывы.
   Ранее открытые gaps сохраняются в client-acceptance.md и feature registry.
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
