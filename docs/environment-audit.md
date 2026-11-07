# Аудит окружения — 04.11.2026

Дополнение 07.11, tutorial-integration084: установок и изменений runtime нет.
IDA14d8cac3 сохранена/закрыта, список пуст. Проверены92 диапазона обоих pins,
1514 полных asm instructions четырёх функций и primary-vptr/RTTI53 объектов.
Source-only probe создаёт18 досок с настоящим CNetworkMgr; восемь финальных
запусков одинаковы/exit0. Начальные ошибки окружения probe (не создан network
owner, затем большой объект на стеке) исправлены только в проверке.
Подтверждены несовпадающие Force/Animus IDs, отдельные quest/Tutorial владельцы
и новые зависимости общей инициализации. PE083/engine082 не менялись; GPU и
старые большие suites не повторялись. M6/M6F/M7/M9 открыты, аудит AUDIT_OPEN.
[Доказательства](../research/client455-tutorial-integration.md).

Дополнение 07.11, money083: новых установок нет. IDA b55212f6 сохранена и
закрыта, список сессий пуст. 21 диапазон совпадает между закреплёнными x86
бинарниками; сохранены 382 инструкции десяти функций валюты. В собственных
копиях перенесены 64-битные поля/API Avatar и инвентаря; новая PE 8b516183…,
entry RVA 151490, 182/20/41 объектов, без unresolved. Korea/Russia: по 92
проверки в четырёх режимах округления, шесть просмотренных кадров. Account,
actor/FX и точная PE/Create=1 проверены заново; девять actor кадров просмотрены.
Движок 9caa283a… не менялся; проверки трёх карт/Miles из 082 не повторялись.
Полные обучение, вход и игра не приняты. M6/M6F/M7/M9 открыты.
[Доказательства](../research/client455-money.md).

Дополнение07.11, rvp-audio082: новых установок нет. IDAf1d662d0 saved/closed/list0;
18equalranges/1665actualasm/770Create decompilelines. Actual Miles driver/MP3
decoder clock/volume/loop и ordinary RVP ambient/event/timer проверены; WAV immediate
branch в455 подтверждённо не создаёт handle. Nativeexit0/warn0/Dmalloc785169balance.
Engine9caa283a…/67objects/12overlays,PE7489e8c7…/entry1512B0/182-20-40TU/
0unresolved/exactCreate1;3maps/actorFX/15reviewedframespassed. 8D6900 — destructor,
прежняя acquire-подпись081 исправлена. Fullsound/Tutorial/game/M9 OPEN.
[Доказательства](../research/client455-rvp-audio.md).

Дополнение07.11, rvp-effects081: новых установок нет. IDA2710bd78 сохранена/
закрыта;18 ranges совпадают между pins,2960 полных asm instructions сохранены.
Собственные CParticle/CEntity1296/212, полный ctor oracle и базовые RVP FX
проверены:269ticks/148particle/6entitydraws,15просмотренных кадров,3карты и
exactPE/Create1. Исправлена heap corruption Cora: weather helper выделял старые
1148/208 байтов; actual allocation instructions проверены до/после исправления.
Engine14af5e53…/67objects/11overlays,PE0165bf16…/entry151000/182-20-39TU/
0unresolved. Baseline033 сохранена;fullFX/audio/Tutorial/game/M9 OPEN.
[Доказательства](../research/client455-rvp-effects.md).

Дополнение07.11, rvp-actor080: установок нет. IDA f9d34033 сохранена и закрыта;
16 ranges совпадают между pins,1051 asm instructions получены полностью.
Сцена12actors/4models и отдельные позы общей модели прошли проверки:
9ticks/459parts,11просмотренных кадров,3camera regressions и exactPE/Create1.
PEa03ae596…/entry150DC0/182-20-38TU/0unresolved; движок079 не менялся.
MSBuild FileTracker и GPU InitR3Engine требуют запуска вне sandbox; два
первых GPU timeout не считаются успехом. FullFX/audio/Tutorial/M9 остаются OPEN.
[Доказательства](../research/client455-rvp-actor.md).

Дополнение07.11, rvp-runtime079: установокнет. IDA6a789f6fsavedclosed;20ranges
equalpins,full531+23+14+114asm. Engined85c8678…/67objects/9overlays +ownedfloat
cameraheader сохраняет033. OrdinaryRVP3maps/27events/82commands, intro26,
46viewedframes/Dmallocpassed. PE83c1793b…/entry150b20/182-20-36TU/0unresolved/
exactCreate1/freshcontracts. Fullactors/audio/Tutorial/M9OPEN;подписи078исправлены:
8D5510Render/8D8340Release. БольшиеunchangedGUI/kernel suites не повторялись.
[Доказательства](../research/client455-rvp-runtime.md).

Дополнение07.11, rvp078: установок нет. IDAa265e239savedclosed,15ranges equalpins,
полные1722+85asminstructions. Новая x86 source library/probe проверила44RVP
(615actor records/1569commands)+2fixtures/all12kinds/interpolation. Именованные
поля совпали с независимым Python. Exact-path resources:77refs/34missing;
это не подтверждённый blocker. OrdinaryPE/engine/Create evidence остаются077,
runtime player/Tutorial/M9 открыты. [Доказательства](../research/client455-rvp.md).

Дополнение 07.11, movie-state077: новых установок нет. 13 ranges/4 asm equalpins;
IDA70b16df7 закрыта, idb_list пуст. Engine67TU/9overlays/18086e42… сохраняет033.
Flags8/GPU6/intro3worlds26cameras/fullscreen18/40 просмотренных кадров прошли.
PEb377d2ac…/entry1508a0/182-20-34TU/0unresolved/exactCreate1, свежие startup contracts.
Подтверждено: RTMOVIE player отключён при компиляции, state/display API перенесены
вне featureguard. FullRVP/Tutorial/game и M9 открыты; wrapper500/480 и %fov
не исправлены. Большие неизменённые suites не повторялись.
[Доказательства](../research/client455-movie-state.md).

Дополнение07.11,fullscreen-effect076: установокнет.11ranges/default0.25 equalpins,
4fullasm;IDAf1ac7cc2savedclosed. Derivedengine67TU/7overlays/2df1e50e… сохраняет033.
RealFSE GPU18/lowVRAM512/failedBegin/target-depth-viewport-UIpassed;realintro3worlds
26cameras/Dmalloc/34viewedframesPASS. PE4553f401…/entry150860/182-20-34TU/
0unresolved/exactCreate1,freshstartupcontracts. Runtimechanged,075timestampreuse
неприменим;oldGUI/kernelhistorical. Fullpostprocess/stage/QBI/M9OPEN,40080201unknown.
[Доказательства](../research/client455-fullscreen-effect.md).

Дополнение07.11,tutorial-intro075: установокнет.15ranges/3tables equalpins,
4fullasm,IDAb92074d1savedclosed. Realcamera/fade/screen/mouse/world сAvatar
race/stage:26cameras/29viewedGPUframes/skip/reload/DmallocbalancePASS. Исправлен
ENGINE_DEFINITIONS только новойcamera TU для согласованногоengine state layout. PE51666436…
182/20/34TU/0unresolved/exactCreate1;runtime equal074 except2linktimestamps.
Fullstage/QBI/newengine controls/fourstage иM9 OPEN;40080201unknown.
[Доказательства](../research/client455-tutorial-intro.md).

Дополнение07.11,world074:установокнет.10ranges/vtableprefix48/6asm equalpins,
IDA60286d36savedclosed. RealCLand3maps/load/render/reload/release/collision,
6GPUframes иDmallocbalance passed. Engine67TU/6overlays c00d9d4d… сохраняетbase033.
PEfd8b038d…/entry150790/182-20-32TU/0unresolved/exactCreate1;freshstartupcontracts,
account/Avatar/MainApp/KoRuWindowpassed. FullILevel/INS/Tutorial/игра OPEN.
40080201unknown.[Доказательства](../research/client455-world.md).

Дополнение07.11,avatar-stage073: установокнет. ConfiguredIDAprobe внеsandbox
прошёл66tools/list10/decompile/close;внутри sandbox workerexit2. NativeMCP
работал,сессияb3b8653dsavedclosed.34ranges/2vtables/15fullasm equalpins.
ActualAvatar/MainApp/account routing,window/board иexactCreate1PASS;
22кадра равныreviewed072. FinalPE3d1f8c32…/entry150550,182/20/32TU,
0unresolved. FullTutorial/world/handlers/factory ещёOPEN;40080201unknown.
[Доказательства](../research/client455-avatar-stage.md).

Дополнение07.11,briefing-window072: установокнет.32ranges/vtable212 equalpins,
19listedfullasm+2captureasm;IDA18f99dcdsavedclosed. Sourcewindow/provider,
realScreen capture,actualboardrich/key иKo/Ru22GPUframes проверены. Fresh
gui-input/modal/minimap passed. PEbd50df91…/entry150350,182/20/31TU,
0unresolved/exactCreate1. Runtime changed,071timestamp-onlyreuse неприменим;
прочиеoldGUI отчёты оставленыhistorical. ActualTutorial/Avatar/world иполная
приёмкаещёOPEN.40080201unknown.
[Доказательства](../research/client455-briefing-window.md).

Дополнение07.11,briefing-controls071: установокнет.29ranges/3vtablesequalpins,
8fullasm,IDAs e0103d83/38abac4e savedclosed. Frame/key/animation иtyping basefill
Ko/Ru native/GPUpassed,20frames/12uniqueviews. Final PEfea692b9…/entry150290,
182/20/30TU,0unresolved/exactCreate1. Runtime bytes equal070 except2timestamps:
oldGUI evidence reused explicitly,не перезаписано какfresh. Newcontrols/window
instance ещёunused;currenttyping/controls gates PARTIAL. Exception40080201unknown.
[Доказательства](../research/client455-briefing-controls.md).

Дополнение07.11,text-typing070: установок нет.18ranges/1vtable equalpins,
8fullasm;IDA37b9a025 savedclosed. Typing source compiled normalfacade,исполнен
в full-object probe,ordinarybriefingещё OPEN. NativeKo/Ru/GPU traces passed,
14frames saved/8viewed,44existingGUIhashes equal069. Production8f009924…,
entry150290,182/20/29TU,0unresolved/existingCreate1;10gatesPARTIAL.
[Доказательства](../research/client455-text-typing.md). Exception40080201unknown.

Дополнение07.11,message-sizing069: установок нет.21ranges equalpins,15fullasm;
IDAb852f877 saved/closed. Productionc22502fa…/entry150290,182/20/28TU,
0unresolved/existingCreate1. Ko/Ru12групп real modal/GDI и10viewedGPUframes;
rich/extent production providers retained naturally. Все затронутые GUI passed,
9gatesPARTIAL. Empty fragment extent иglobalvirtualSetSize остаются OPEN.
Firstchance40080201 черезKernelBase повторяется;causeunknown,не полнаяfailures
приёмка. [Доказательства](../research/client455-message-sizing.md).

Дополнение07.11,gui-input068: установок нет.34ranges/1vtable prefix equalpins,
15completeasm,IDA6eadfaf3 savedclosed,idb_list0. Productionde76223c…/entry14F4A0,
182/20/28TU,0unresolved/existingCreate1. Ko/Ru realGUI input/focus/queue и
затронутые GUI probes прошли;40GPUreadback hashes совпали с предыдущими
просмотренными кадрами. Новый trace содержит firstchance40080201 через
KernelBase (причина не установлена),checkpointCreate1 пройден;это не приёмка
всех exception/failure domains. Старые крупные suites не повторялись.
[Доказательства](../research/client455-gui-input.md).

Дополнение06.11,minimap-opacity067: установок нет.17ranges/2vtable regions
совпали между pins,10complete asm;IDA7b53e450/b947042c closed/save,sessioncount0.
Main sprites:Ko fallbackCommon DXT1,Ru localizedARGB;frames5:0=400×18/5:32=400².
Common8style0=194×13/style1=192×15. Production0def3dce…/entry14EFF0,
182/20/27TU,0unresolved/existingCreate1. Ko/Ru real owner/queued mouse/GPU passed;
source EX and opacity facade retained in production. Полный мир/карта OPEN.
Удалён старый ignored client455_crt_multibyte.obj от эксперимента064:27CMake
facade sources/27актуальныхobjects;LIB/LIST и production map не содержат этого
адаптера. Найденные __acrt_multibyte symbols принадлежат обычному libucrt.
[Доказательства](../research/client455-minimap-opacity.md).

Дополнение06.11, scrollbar-variants066: установок нет.37function ranges и2vtable
regions совпали между pins,13complete asm. IDA68442489/ef4ffb43 closed/save.
Productionb24f1f09…/entry14E290,182/20/26TU,0unresolved/existingCreate1;
Ko/Ru EX/Var full-object/queue/GPU и затронутые GUI probes passed. Target
loader8CFB90 требует actions<16;изменять этот предел ради Var action15 нельзя.
Ранний invalid16action fixture завершился через Error;исправлен fixture15actions,
production guard сохранён. [Доказательства](../research/client455-scrollbar-variants.md).

Дополнение06.11, scrollbar065: установок нет.23ranges/2vtable prefixes/divisor
совпали между pins,15complete asm; IDAbfcf8ee1/9775776a closed/save. Новая PE
d38d74e0…/entry14E350,182/20/26TU,0unresolved/existingCreate1. Ko/Ru ordinary
scrollbar/queued input/GPU и затронутые GUI probes passed. Common action2
имеет44frames,defaults44–49 clamp to43;synthetic sprite только для теста.
[Доказательства](../research/client455-scrollbar.md).

Дополнение06.11, text-board064: установок нет.49 диапазонов и2vtable regions
совпали между pins,17полных asm. IDA958042ee/aabab7c3/06c03ace closed/save.
Полная PE3a209cdc…/entry14DD30,182/20/26TU,0unresolved/existingCreate1.
Korea/Russia TextBoard/GPU и затронутые GUI probes прошли. Исходники UCRT SDK
10.0.26100.0 доступны локально: getter0 допустим для SBCS ANSI1251, отдельный
startup adapter не нужен. [Доказательства](../research/client455-text-board.md).

Дополнение06.11, text-metrics063: установок нет.15 диапазонов и empty literal
совпали между pins,5полных asm; IDAe13a414e closed/save.182client/20kernel/
26facade,0unresolved; production71bc4b21…/entry14D7C0. Собственная GDI/CGUIText
проба Korea/Russia exit0, финальные кадры просмотрены. Ранний null-provider
сбой0.7 исправлен ожиданием реального шрифта. Font/modal/existingCreate1
регрессии прошли. [Доказательства](../research/client455-text-metrics.md).

Дополнение06.11, modal062: установок нет.43 диапазона/3vtable совпали между pins,
8полных asm; IDA124615b8/14980562 closed/save.182client/20kernel/24facade,
0unresolved, production PEa5b1da0b…/entry14D300. Modal Korea/Russia own native
exit0, кадры осмотрены; GDI regression passed. Точная PE прошла D3D/Character/
existingCreate=1, stop до игрового цикла. [Доказательства](../research/client455-modal.md).

Дополнение06.11, tutorial-board061: установок нет.32 диапазона и board vtable/
selection strings совпали между pins;9 полных asm. IDA774fd3f4 closed/save.
Собственная x86 PEed4fbf9d…/entryEBD30 завершилась exit0. Настоящие GUI-диалоги
отрисованы на D3D, viewport640×480 проверен отдельно от backbuffer640×500.
Визуально подтверждены старые назначения кнопочных спрайтов — это открытый gap.
Production PE056 не менялась. [Доказательства](../research/client455-tutorial-board.md).

Дополнение06.11,tutorial-actions060: установок нет.50ranges/equip16/virtual
bindings equalbothpins,11completeasm; IDA758bbebc closed/save. Own x86 lib
71c8d650.../PEac630491.../entry13F80 naturalexit0;recordinghost,не actual UI.
99programs/39864records prepare;spatial fixture regression exit0. Production
56905e68... unchanged. [Доказательства](../research/client455-tutorial-actions.md).

Дополнение06.11,tutorial-spatial059: установок нет.32function ranges/47category
bytes/counters/constants equalbothpins,7asm functions complete. IDAc60c1913/
5b89854f/7dedc5cb/cfea0c20 closed/save. Own x86 lib19d337cb.../PEdb7706b3.../entry9B30 exit0;
recording host, не world. Common-context regression058 passed. Production
PE56905e68... unchanged. [Доказательства](../research/client455-tutorial-spatial.md).

Дополнение06.11,tutorial-runtime058: установок нет.42function ranges/10vtables
совпали в pins,7полных asm функций проверены. IDAf84ad03d closed/save.
Own x86 library/native9618bd36.../entry8100, naturalexit0. Recording host,
не actual UI/Avatar. New reports совместимы с discovery20kernels; production
PE56905e68... не менялась. [Доказательства](../research/client455-tutorial-runtime.md).

Дополнение06.11,tutorial-scripts057: новых установок нет.19диапазонов функций,
CQBI RTTI и selector strings совпали между pins. Own x86 SCP library собрана,
99realfiles/47synthetic selectors/semantic fields/bounds проверены, naturalexit0.
IDA c257ee18/b0309dad закрыты/save. Production PE не менялась; Tutorial runtime
не принят. [Доказательства](../research/client455-tutorial-scripts.md).

Дополнение06.11,camera056: установок нет.12ranges equalbothpins;IDAc449e061
closed/save. Derivedengine67units/5overlays91bdf0c7...;033unchanged. FullownPE
56905e68.../entry14ACA0,182client/20kernel/23facade,0unresolved. RealCAM1.2/
synthetic1.3/play/GPUprojection/release nativeexit0;existingCreate=1. Full
Tutorial/fourstage/M9 open. [Доказательства](../research/client455-camera.md).

Дополнение06.11,progress-base055: установок нет.18function ranges equalbothpins,
IDA3bc31778 closed/save=true. Actual CGameProgress/Title/particlecount probe
naturalexit0. Fullx86PE5302f71a.../entry14A750,182client/20kernel/22facade,
0unresolved;existingCreate=1. Fullfourstage/Tutorial/M6F/M9 открыты.
[Доказательства](../research/client455-progress-base.md).

Дополнение06.11,progress054: установок/пересборки нет.28function ranges,
RTTI/vtables четырёх stage classes совпали в455pins; IDA3915694c closed/save.
Mode2=Tutorial подтверждён через Avatar setter/фабрику/RTTI. Raw static scan
не нашёл callers старого INI reader; computed calls остаются неизвестными.
Runtime/source сборки053 не изменены. [Доказательства](../research/client455-progress.md).

Дополнение06.11,account053: новых установок нет.26функций/11country selectors
совпали между455pins; IDAf2469475 closed/save=true. Собственная x86PEa12b10f7...,
entry14A980,182client/20kernel/22facade,0unresolved. Пакеты account/gateseed,
bounded dispatcher и pending dialog проверены реальными методами на owned
in-memory fixture; естественный exit0. Точная PE сохранила existingCreate=1.
Настоящий вход и full455 ещё открыты. [Доказательства](../research/client455-account.md).

Дополнение06.11,connection052: установок нет.15функций/11vtables совпали между
455pins; IDAbed1c136 closed/save=true. Полная собственная x86PE0733cce1...,
entry14a3f0:182client/20kernel/21facade,0unresolved. Настоящие Connect/events/
wait идут до engine; собственная CCR-проба подтверждает TCP-peer и existing
Create=1. Локальная тестовая TCP-точка не отправляет RFпакеты и закрывается
после каждой пробы. Три native режима естественно exit0, включая реальные
диалоги ошибок; hook установлен только на поток собственной проверки.
Russian WinMain trace теперь честно останавливается перед Connect: текущий
argv endpoint1 не заполнен; полный профиль455 ещё не доказан. M6/M9 открыты.
[Доказательства](../research/client455-connection.md).

Дополнение06.11,network-codec051: установок нет.33функции/7диапазонов данных
совпали между455pins; AES192 schedules обоих направлений проверены полностью.
IDA4c89c7ab closed/save=true. Собственная библиотека реализует AES; Windows CNG
использован только в проверочной программе. Буферы/формат пакетов подключены
к normal CNetProcess; два процесса, вместимость6. Full PE71e644eb.../entry149ef0,
182client/20kernel/20facade,0unresolved; зависимости движка сохранены. Own
native codec/ring tests naturalexit0; существующий Create вернул1. Full455
transport/handlers/auth/UI/M9 ещё открыты.
[Доказательства](../research/client455-network-codec.md).

Дополнение06.11,bootstrap050: новых установок нет.28диапазонов функций и11
country vtables совпали между455pins; IDA d716d7fa/8102ad50 closed/save=true.
MSVC x86 собрал182client/20kernel/19facade; ownPE3b93b0eb.../entry149010,
0unresolved. ActualNetworkCreate теперь передengine ивыполняетсяодинраз.
Ownnative FG/name/process/mutex/state probes естественно exit0, включая вторую
собственную RF_Online.bin. Реальный закрытый TCPпорт:10061 доclosesocket,
0после — совпадаетсAPIпорядком455;connectedfalse,аутентификации нет. Exactown
Korea/Russia bootstrap/D3D/existingCreate прошли;отладчик остановилдоцикла.
17scoped gates PASS/PARTIAL. Полный455transport/framing/crypto/UI/M9 открыт.
[Доказательства](../research/client455-bootstrap.md).

Дополнение06.11,launcher049: установок нет.19функций и11country vtables
совпали в обоих pinned455PE;IDAf2fdf71d closed/save=true. Modern MSVC x86
собрал182client/20kernel/17facade;full PE a64601c8.../entry148860,0unresolved.
Три own offline launcher-пробы естественно exit0,сеть не создавали. Exact
WinMain Korean/Russian прошёл nation→launcher→language→engine/Miles;обычный
Create вернул1. Остановка на ownRVA B3DB4 до фильтров/игрового цикла. Debugger
передаёт аргументы только из labfixture,не читает реальные account-файлы.
Полный455bootstrap/connect/auth/gameplay ещё открыт.
[Доказательства](../research/client455-launcher.md);M6/M9 открыты.

Дополнение 06.11, sprites048: установок нет. Сессия IDA64d5aa70 работала с
копией эталона, закрыта/save=true.14диапазонов sprite/texture/manager и55имён
совпали в обоих pinnedPE. Производный движок сохраняет033;67units/4CPP overlays,
новый source texture uploader поддерживает реальный DXT5. Две own GUI пробы
с normal CMainApp.LoadData/CGUIMouse естественно exit0,COMrefs сохранены.
Точная ownPE d431094d.../x86/entry148390 дошла до новой проверенной границы
RVA B354A перед CreateFileA(DefaultSet.tmp);остановлена собственным debugger,
launcher-данные не читались. Полный455bootstrap/вход ещё открыты.
[Доказательства](../research/client455-sprites.md);M6/M9 открыты.

Дополнение 06.11, lifecycle047: установок нет. IDA session dae004fd открыла
копию эталона, закрыта с save=true. Девять диапазонов Land/ILevel совпали
в обоих закреплённых PE; null-level branch RVA3C8F3F подтверждён инструкциями.
Новая собственная x86 PE SHA11833d1e... / entry1485A0: 182 объекта клиента,
20 kernel, линковка без unresolved. Три отдельных процесса с реальным
глобальным CMainApp и две GUI-пробы без Land завершились с exit0 без отладчика
и TerminateProcess. Обычные startup/device/Create checkpoints также сохранены,
но эти отдельные запуски остановлены отладчиком. Полный WinMain/shutdown не
принят. [Подробности](../research/client455-lifecycle.md); M6/M9 открыты.

Дополнение06.11,font046: установок нет. Настоящие CreateFontA/ExtTextOutW/
GDI metrics/D3DX36 atlas работают сcountry params;Hangul/кириллица просмотрены
вкадрахреальногоCGUIText. Собственный font probe создаёт Land передвыходом и
завершаетсяexit0;старый early-abort nullLand gap зафиксирован отдельно.
OwnPE88942d08.../x86/entry1485A0 прошла GDI/D3D/Character;lab fontregistration
очищена. Derivedengine67units,033сохранён. IDAa9adfb47 closed/save=true.
Полные FT/text/UI/IME/window sizing/early-abort/shutdown ещё открыты.
research/client455-font.md; M6/M9 открыты.

Дополнение 06.11, language045: новых установок нет. Actual MSVC CRT LC_COLLATE
для11country names дал ожидаемые codepages.9realNDLanguage EDF/bytes/index/DBCS
проверены;en-us/th-th пакеты здесь отсутствуют,не заменять другими. New own PE
SHA1fc267d5.../x86/entry14A920 прошла Korean+Russian language init/Miles и
Korean D3D/Character startup. Debugger повторно использован по SHA. Lab
work/m9/1fc267d5;IDA34ab1c2b closed/save=true;short regressions/кадры прошли.
Полные font/text/UI/Create/launcher/network/shutdown ещё открыты.
research/client455-language.md; M6/M9 открыты.

Дополнение 06.11, nationpaths044: новых установок нет. Полная собственная PE
SHAcb64af10.../x86/entry1496C0 собирается без unresolved. Выбор страны/корня
данных проверен по обоим455PE; штатный Create дошёл до Character и менеджеров
на реальном D3D9. Точный stop до _CreateCharDataMgr, exit наблюдён. Breakpoint
адреса теперь определяются dumpbin по инструкциям текущего PE/MAP; fixed offsets
удалены. Свой debugger/CPU layout обновлены, short regressions/кадры прошли.
IDA5f01f0d1 закрыта/save=true; lab work/m9/cb64af10/create-startup001.
Полные locale/NDLanguage/launcher/UI/network/shutdown впереди.
research/client455-nation-paths.md; M6/M9 открыты.

Дополнение 06.11, devicestartup043: установок нет. Отдельно собрана библиотека
R3Engine455Startup из67units с двумя подтверждёнными правками;033source/lib
сохранены. Full normal PE линкуется, новый SHA51fd3f49..., entry149510.
Реальный WinMain дошёл до window/D3D/device ready1 в оконном режиме32бит;
свой debugger с SW_HIDE запросом остановил процесс до CMainApp::Create,
exit наблюдён. Source snapshots CPU и exactPE traces под work/, короткие
Character/renderer regressions прошли, прежние кадры сохранены. Reference
IDA1c8c37b3 closed/saved=true. Locale/launcher/network/bootstrap order455
ещё не восстановлены. research/client455-device-startup.md; M6/M9 открыты.

Дополнение 06.11, startup042: установок не требовалось. Собственный Win32
debugger собран VS2026 и запускает только точную staged own RF_Online.bin.
Все15 regular/delayed import descriptors имеют x86 providers/нужные exports;
фактически загруженные eager DLLs и Miles совпали по SHA. CRT/WinMain/engine/
Miles startup прошли, sound return1. Отладчик остановил процесс до D3D/window;
exit наблюдён. Три first-chance события обработаны runtime, second-chance нет.
Lab inputs: копии DLL/WaveList и собственный ini, оригиналы не менялись.
CDB не устанавливался; raw trace под work/m9/39062b2c/startup002. Own IDA
2714f558 closed/saved=true. Нормальная graphics/Create/launcher приёмка впереди.
research/client455-startup.md; checkpoint PARTIAL; M6/M9 открыты.

Дополнение 06.11, accounting041: без новых установок. 182 client / 11 facade /
20 canonical kernel CPP x86/MT собираются; новый полный normal RF_Online.bin
успешно линкуется с 0 unresolved и без принудительного разрешения. PE32 x86,
1 966 080 байт, entry RVA149500, SHA/response/MAP — normal-link.json.
Общие counters и actual ANI/multiple owners/mesh lifetime/GPU descriptors
проверены; release/новый renderer не обнуляют cumulative значения. Старые
цветные/effect/shadow кадры сохранились, COM/Dmalloc0. Входные EXE и normal
WinMain не исполнялись; runtime DLLs/обычная инициализация ещё не приняты.
IDA6b33fc0a closed/saved=true. research/client455-normal-accounting.md;
checkpoint PARTIAL; M6/M6F/M7/M9 открыты.

Дополнение 06.11, characterclock040: без новых установок. Отдельный таймер
Character 91EA80 и _R3CalculateTime подключены к современному x86/MT facade.
168 численных случаев/12 режимов FPU, QPC/fallback и независимость engine clock
прошли. 182 client / 10 facade / 20 kernel CPP собираются; полный линк теперь
только g_ChMemoryInfo. Короткие ANI/BBX/model/effect/shadow сценарии прошли,
прежние кадры сохранились, COM/Dmalloc 0. IDA a91e5275 closed/saved=true.
research/client455-character-clock.md; checkpoint PARTIAL; M9 открыт.

Дополнение 06.11, effects039: новых установок нет. 182 клиентских, 8 facade и
20 canonical kernel CPP собираются x86/MT. Загрузка и применение EFF работают
с прежним source TextureManager на D3D9 HAL. Эффект с реальной DDS изменил кадр
модели; прежние цветные кадры и теневой проход сохранились, COM/Dmalloc 0.
Полный линк: только g_ChMemoryInfo и _R3CalculateTime, других ошибок нет.
IDA 4a2e7cac закрыта с запросом save; returned saved=null. Оригинальные EXE
не исполнялись, серверы не менялись. research/client455-effects.md;
inventory/client455-effects-checkpoint.json: PARTIAL, M9 открыт.

Дополнение06.11 effecttables038: без новых установок. Два reader иquery работают
вnormalfacade с source owners. Проверены реальные2246patterns/4600items,
неизвестные stacktail grades9..35 явно выявлены.182client/6facade/20kernelCPP
собираются, полный линк15символов. Короткая renderer/ANI/BBX/shadow регрессия
прошла; больших неизменённых suites нет. IDA3ce41498closed/saved=true.
research/client455-effect-tables.md; checkpoint PARTIAL/M9OPEN.

Дополнение06.11, normalshadow037: новых установок нет. BeginShadow/EndShadow
и512x512targets на прежнем D3D9HAL/pinnedD3DX9_36 работают в собственном проходе.
Реальная модель дала силуэт;3прохода/reuse/COM0/прежние цветные кадры проверены.
Begin возвращает0 на успехе, а настоящие455callers используют BOOLпроверку;
normal shadow lifecycle ещё не принят. Полный линк20символов. IDA63e04581
closed/saved=true. research/client455-normal-shadow.md; checkpoint PARTIAL/M9OPEN.

Дополнение06.11, normalcontracts036: новых установок нет. Пять методов модели
и сброса анимации455 подключены к обычному x86/MT facade. Реальные BBX и модель
после reset/reattach/rematch прошли, прежние два GPUкадра совпали. Сборка182client/
3facade/20kernelCPP успешна; полный линк22метода/данных, M9OPEN. Большие
неизменённые suites не повторялись. IDAb8160cd3closed/saved=true.
research/client455-normal-contracts.md; inventory/client455-normal-contracts-checkpoint.json.

Дополнение 05.11, normal renderer035: новые установки не требовались. Обычные
CUnity/модель/поза/CRender рисуют два кадра на D3D9; координатная и матричная
обёртки дали одинаковые кадры, COM/Dmalloc после явного завершения 0. Макросы
GPU-теста согласованы с engine/client, включая RF_CLIENT_455_WEATHER.
Полный линк пока 27 методов/данных, M9 открыт. IDA1bcd6f24 закрыта, save запрошен,
saved=null. research/client455-normal-renderer.md и соответствующий checkpoint.

Дополнение 05.11, normal port034: без новых установок компилируются 180 исходных
клиентских единиц на D3D9/типах455; после выделения CUnity/CAnimation — 182 объекта
x86/MT. Реальные потребители загружают ANI. Полный линк пока LNK1120:39 символов
методов/данных, CharacterMR не подключён. База/engine033 сохранены, игровые DLL
в тесте не загружались. inventory/client455-normal-checkpoint.json (PARTIAL);
research/client455-normal-port.md. Сессий IDA не открывали.

Дополнение05.11 engine9port033: local Microsoft.DXSDK.D3DX9.29.952.8 headers,
Author/Repository подписи проверены. PackageSHA/files inventory/d3dx9-headers.json.
Никакие_43runtimeDLLs неустановлены; x86importarchive retargeted36 иactualimports
проверены поpinnedDLLexports. НастоящийD3D9R3Engine67units x86/MT,device/Platform01
иsource Characterowner наодномdevice прошли. Originalnormalсборка не менялась.
Gate inventory/client455-engine9-checkpoint.json. CDBexe отсутствует,ошибкаownrun
разобрана через собственныйSEHreport/MAP. Full180client migration ещёоткрыта.

Дополнение05.11: source renderer owner032 использует прежние MSVCx86/MT,
pinnedD3DX9_36 иD3D9HAL. Constructor/caps/destructor иreal model→pose→draw путь
прошли component/fullclient,ownheap/COM/Dmalloc0;новых установок нет.
Lab197TUs,normal293MTobjects/runtime прежний кромеtimestamps. IDA8ad1c657closed/save.
inventory/client455-renderer-owner-checkpoint.json;research/client455-renderer-owner.md.

Дополнение05.11: source scene-frustum использует прежнюю pinned x86 D3DX9_36,
устанавливать ничего не требовалось. Нормальные SetCharacterClipping/CResObject
подключены к source math;72matrix/204AABB/9actor scenarios икороткая Platform01
регрессия прошли. Normal293MTobjects,lab196clientTUs. Named Character API audit
247objects завершён;39oldSDKfunctions ещё вызываются. Native IDA session закрыта/save.
inventory/client455-frustum-checkpoint.json;research/client455-normal-character-interface.md.

Последнее дополнение: основной Character draw/эффекты/deferred paths source
проверены на том же D3D9HAL/pinnedD3DX9_36 отдельно и в полном client lab:
16targeted scenarios/185assertions,2realmodel frames,COM/heap/Dmalloc0. Lab195TUs,
normal291MTobjects/тот же engine archive/runtime прежний кромеtimestamps.
Новых SDK/установок нет. Старый staticCRT sin/cos ещё не сертифицирован.
inventory/client455-character-draw-checkpoint.json;research/client455-character-draw.md.

Предыдущее дополнение: source Character draw primitives проверены на настоящей
анимированной модели с3textures/D3D9HAL/pinnedD3DX9_36. Два кадра совпали отдельно
и внутри client lab; heap/COM/Dmalloc0. Новых установок нет. Lab194clientTUs,
normal291modernCOFF/MT, прежний engine archive; normal renderer ещё D3D8.
inventory/client455-draw-checkpoint.json;research/client455-draw.md.

Предыдущее дополнение: source Character shader bootstrap работает на настоящем
D3D9 HAL и pinnedD3DX9_36:12SHO/12VS+3PS/2declarations,119checks standalone и в
полном client lab. COM counts0, gameDLLs не загружены; normal renderer ещё D3D8.
Новых SDK/установок нет. Lab193clientTUs,normal291MTobjects/runtime прежний.
inventory/client455-shaders-checkpoint.json;research/client455-shaders.md.

Последнее дополнение: source AnimationManager4554028/11APIs проверен standalone
и full-client lab на коллекции/кэше/владении/одном real ANI. Новых установок нет.
Normal291MTobjects/прежний engine archive, lab192clientTUs. Normal runtime равен
предыдущему после исключения timestamps: старые consumers ещё не переключены.
inventory/client455-animation-manager-checkpoint.json;
research/client455-animation-manager.md. Несвязанные большие тесты не повторялись.

Дополнение после timing: source elapsed clock подключён в normal R3EngineMT.
144 состояния/3 provider сценария прошли; actual R3CalculateTime→CResObject
проверен в полном client lab. Platform01/device прошёл, прежние frame SHA.
Normal291modernCOFF x86/MT, lab191clientTUs; новые установки не требовались.
Текущий gate inventory/client455-loop-clock-checkpoint.json;
research/client455-loop-clock.md. Исторические snapshots ниже не обновлялись.

Актуальное дополнение 05.11: восстановленный расчёт кадра и CAnimation ctor
подключены к обычному клиенту через R3EngineMT. Проверены 612 численных случаев,
16 actual CResObject сценариев и короткая Platform01/device регрессия (2 случая).
Normal290modernCOFF x86/MT, lab190clientTUs; установки не менялись. Runtime обычной
сборки намеренно изменён выбранными вызовами, полный Character455/draw ещё открыт.
Gate inventory/client455-animation-timing-checkpoint.json;
research/client455-animation-timing.md. Старые большие runtime suites не повторялись.

05.11 modelpipeline source:connectedMESH08route/lifetime10021HALchecks вcomponent
иполномclientlab,393parts/276realuploads/59texturebindings,ownheap/COM/Dmalloc0.
ТотжеpinnedD3DX9_36/HAL,no new installs;normalgame manager/renderer integration
ещё открыта. research/client455-model-pipeline.md.

Следующее дополнение05.11:source sharedVB36/VB64/INDEX16 работает втомжеHALD3D9;
159173nativechecks standalone/fullclient,12files/393parts/276real uploads,
4syntheticindexed draws,COM/Dmalloc0. Зависимости/установки не менялись.
Full Character shaders/normal loader ещё открыты. research/client455-shared-buffers.md.

Дополнение05.11: physical Character texture source работает с pinned x86
D3DX9_36 иHALD3D9 через отдельную TU внутри полного client lab.8440checks,
68texture pairs/137renders/97material parts,COM/Dmalloc0;новый SDK неустанавливался,
d3d9.h из WindowsSDK10.0.26100.0/shared. Полный client/Character GPU ещё открыт.
research/client455-character-textures.md;inventory/client455-texture*.json.
IDA configured stdio повторно проверен в user context:66tools,страница10client
functions,декомпиляция/close-save. Probe теперь client-only IDB,без server smoke.
Native MCP также работает. Restricted workercode2 исчезает при привычной
escalation;переустановка не нужна. docs/ida-mcp.md.

Дата по Asia/Yakutsk. Машинные отчёты используют UTC. Это снимок состояния,
а не непрерывный мониторинг. Работы выполнены в `E:\RFOnlineTrash\Source\WorkFlow`.

## Итог

Работа исключительно над клиентом и его зависимостями. Серверные сведения ниже —
история проверки инструментов/инвентаризации, не задачи и не блокеры клиента.
Серверные исходники разрешены для чтения как справочник, без изменений и сборки.
Целевой результат — исходники RF_Online.bin с полным функционалом и поведением
закреплённого клиента 455; степень соответствия пока не установлена.

Рабочая область и локальный Git подготовлены. GoMMO MCP работает через stdio.
IDAPython восстановлен на Python 3.11.16; IDA MCP установлен, зарегистрирован в Codex
и проверен через stdio и нативные инструменты чата после перезапуска: 669 функций
и декомпиляция получены на рабочей копии PE x86. Установлен universal-modder:
13 навыков с валидными метаданными и работающий CLI um 0.2.0.
Установлена и проверена Visual Studio Professional 2026 18.11.3: MSVC x86,
Windows SDK и CMake. Основной путь — перенос клиента под современный MSVC;
VC6 остаётся резервным инструментом. DirectX 8.1b SDK проверен и подключён локально;
R3Engine собран под VS 2026 x86 с двумя успешными чистыми пересборками.

Статический аудит сборки завершён: 14 DSP / 14 DSW, 41 конфигурация, 832 SOURCE,
6 отсутствующих записей в CameraExporter/R3MapExp. Все 180 C++ клиента уже компилируются
с диагностическим восстановленным Character.h. JPEG 6b/Miles подключены.
Получена полная diagnostic RF_Online.bin и успешная чистая пересборка, unresolved нет.
Выбранные 455 ветки имеют отдельные flags/ledger, исходные legacy branches сохранены.
Это не проверка запуска/полного поведения 455. Подробности research/client-first-build.md.
Последующее M5: helper loader455 найден, три отличия перенесены отдельным flag.
Обычная ревизия собрана, отдельный own lab entry полного проекта выполнил загрузку
140 реальных файлов/97 543 записей и CPU transforms/bbox;12 fixtures,2 546 779 checks,
4 import-parser tests. В lab игровые DLL отложены и не загружались. Обычный игровой
запуск/LoadLevel не проверены. Последующее: две x87 math функции восстановлены
с совпадением всех инструкций455, проверены в обоих linked clients и338 native
checks/12FP modes. Повтор140files после выравнивания Release options успешен,
2 546 931checks, FP control0x027F. Weather source перенесён:2слоя,R3X/text config,
load/release/update/draw split,interior/night.65real R3X +4fixtures/703checks,
37actual CPU lifecycle checks,285modern objects /MT. GPU/normal map/clock integration
остаются открыты. research/client455-weather-source.md.
Последующий resource audit:78RPK/3775files,70BSP+93EBP,20weather assets закреплены
с SHA.8parser tests прошли. Выявлены1067неверных size fields RPK и stale offsets
Dungeon00;455 использует offset-only fopen и sequential BSP reads соответственно.
На этом статическом этапе Source VFS/end ещё отсутствовал. Один weather path missing для
трёхTower R3X, directory component не найден во всех162RPK indexes. Игровые EXE/DLL
не запускались; сборки не менялись. research/client455-map-resources.md.
Следующий цикл восстановил RPK source/group/fopen/exists и particle end:18 907native
module checks на3775members/78RPK и30actual full-project archive/SPT/R3X checks.
Обе сборки успешны,286modern x86 /MT objects; selected compiled branches и DDS mask
проверены.703weather checks прошли на новой lab revision. Normal LoadLevel/GPU не
выполнены. MSBuild FileTracker sandbox E_ACCESSDENIED устранён escalation того же
build command. research/client455-resource-io-source.md.
Область работы уточнена: исключительно клиент. Выбор LoginServer отозван;
первая цель клиентской зависимости — R3Engine RTMovie Release, затем RF_Online. Детали: [build-audit.md](build-audit.md),
этапы: [roadmap.md](roadmap.md), актуальная память: [project-memory.md](project-memory.md).

## Инструменты

| Компонент | Проверка | Результат |
|---|---|---|
| ОС | Environment.OSVersion | Windows NT 10.0.19045; редакция не определялась |
| Git | git --version | 2.53.0.windows.3; работает |
| GitHub Desktop | процесс и путь | запущен, каталог app-3.6.10 |
| IDA Pro | реестр и FileVersion | 9.2; файл 9.2.25.0908 |
| Hex-Rays | IDAPython и реальный MCP-вызов | плагин 9.2.0.250908 работает; декомпиляция функции PE x86 подтверждена |
| IDAPython | реальный запуск скрипта | Python 3.11.16; 669 функций, декомпиляция успешна |
| IDA MCP | initialize, tools/list, idb_open, list_funcs, decompile | установлен ida-pro-mcp 2.0.0, 66 инструментов; основные вызовы прошли |
| GoMMO Studio | initialize и studio_status | 2.0.1, несмотря на папку/README 1.3.0 |
| Python для аудита | прямой запуск | 3.12.14 из комплектного runtime Codex |
| Python для IDA | idapyswitch и запуск внутри IDA | 3.11.16, постоянная установка uv в AppData/Roaming/uv/python |
| Системный Python 3.10 | реестр и проверка файла | запись есть, C:\Program Files\Python310\python.exe отсутствует |
| Python 3.14 | цель launcher и проверка файла | launcher ссылается на отсутствующий pythoncore-3.14-64/python.exe |
| Visual Studio | vswhere и реальная сборка | Professional 2026 18.11.3, установка завершена, перезагрузка не требуется |
| MSVC | VsDevCmd x86 и компиляция | toolset 14.51.36231, compiler 19.51.36260.0; x86 проверен |
| MSBuild / CMake | реальная конфигурация/сборка | 18.11.1.51303 / 4.3.1-msvc1, генератор Visual Studio 18 2026, Win32 |
| Windows SDK | VsDevCmd и Win32 smoke | 10.0.26100.0, заголовки и линковка проверены |
| VC6 / DX8.1 SDK | стандартные каталоги и установленные программы | не обнаружены; переносные установки на других дисках не исключены |

Наличие Visual C++ Redistributable и Visual Studio Installer не означает наличие
компилятора. PATH не менялся. IDAPython явно привязан к найденной установке 3.11.16;
остальные Python-установки не заменялись. MCP изолирован в local/ida-mcp-venv.

## GoMMO MCP: подтверждено

- У запущенного приложения найден локальный instance descriptor.
- В момент проверки адрес: `http://127.0.0.1:64359/mcp`, версия 2.0.1.
- Порт динамический. Токен из descriptor не копировался в рабочую область.
- Использован официальный stdio bridge: `gommostudio.exe -mcp`.
- Успешны `initialize`, `notifications/initialized`, `tools/list`, `studio_status`.
- Сервер объявил 663 инструмента. Это проверка обнаружения, а не испытание каждого.
- `studio_status` показал пустой список документов; клиент и проект не открывались.
- Изменения ассетов, Install, запуск сервера и публикация не выполнялись.
- Схемы и результат: `inventory/gommo-mcp.json`.

В нативном наборе инструментов текущего чата GoMMO не зарегистрирован.
Доступ через наш stdio-клиент уже подтверждён. Пример для последующего подключения
Codex сохранён в `config/codex-mcp.example.toml`; глобальная регистрация GoMMO не добавлялась.

## IDA и MCP: восстановлено после первоначального аудита

На момент начала аудита процесса IDA и слушающего MCP-сервера IDA не было.
До восстановления в пользовательском config.toml Codex не было регистрации
IDA/GoMMO; mcp.json LM Studio не содержал настроенных серверов.

Проверены:

- `C:\Program Files\IDA Professional 9.2\plugins`;
- `C:\Users\Admin\AppData\Roaming\Hex-Rays\IDA Pro`;
- `C:\Users\Admin\AppData\Roaming\Hex-Rays\IDA Pro\mcp\instances` — пусто;
- стандартные `.idapro` и `AppData\Roaming\IDA Pro` — отсутствуют;
- несколько обычных мест расположения `ida-pro-mcp` — не найдены.

Повторный поиск также охватил Downloads, Documents, uv/tools и RFOnlineTrash.
Рабочая старая установка IDA MCP не обнаружена; в найденном Python пакет
ida-pro-mcp отсутствовал. Поэтому выполнена новая установка совместимой реализации.

Скрипт `scripts/probe_ida.py` копирует старый `LoginServerSR.exe` в `work/ida-smoke/`
и запускает только статический анализ через idat.exe. Сам серверный EXE не запускается.
В песочнице IDA завершилась с кодом 2 без диагностического лога. Повтор вне песочницы
завершился с кодом 1 и дал диагностический лог:

```text
failed to load Python runtime: skipping IDAPython plugin
Hex-Rays Decompiler plugin has been loaded (v9.2.0.250908)
.../scripts/ida_smoke.py: unknown file extension
```

Это исторический результат первого аудита. При восстановлении idapyswitch обнаружил
рабочую установку `C:\Users\Admin\AppData\Roaming\uv\python\cpython-3.11.16-windows-x86_64-none`.
После явной привязки к её python311.dll скрипт IDAPython завершился с кодом 0,
получил 669 функций и выполнил декомпиляцию. Переустановка Python не понадобилась.

Установлены:

- ida-pro-mcp 2.0.0, commit `c133c3853faa111a9b00ee615c013b720d0c4acd`;
- зависимости idapro 0.0.12 и tomli-w 1.2.0 в `local/ida-mcp-venv`;
- GUI-плагин в `%APPDATA%\Hex-Rays\IDA Pro\plugins`;
- stdio supervisor в секции `[mcp_servers.ida_mcp]` пользовательского Codex config.

Последняя проверка использовала команду непосредственно из зарегистрированного
Codex config. Успешны initialize, tools/list (66 инструментов), idb_open,
server_health, list_funcs (все 669 функций), decompile и idb_close с сохранением базы.
Пример: `sub_401E60`, VA `0x401E60`, RVA `0x1E60`, image base `0x400000`.
SHA-256 входа: `9874cbada393244db1d02c1549eb02434f6d376e7cea33fc97e8424bfb1cc7a2`.
Пакет сообщает версию 2.0.0, MCP serverInfo — 1.0.0; обе версии зафиксированы.

Отчёты: `inventory/ida-runtime.json`, `inventory/ida-mcp-tools.json`,
`inventory/ida-mcp-verification.json`. `pip check` не выявил конфликтов зависимостей.
Команда `codex mcp list --json` подтверждает `ida_mcp: enabled=true`.
Рабочая база: `work/ida-mcp-smoke/LoginServerSR.exe.i64`.
Запуск проверял статический анализ; серверный EXE не исполнялся.

После перезапуска Codex появились 66 нативных инструментов IDA. Через них проверены
idb_open, server_health, list_funcs (669 функций), decompile (полный код sub_401E60)
и idb_close. Состояние ok, auto_analysis_ready=true, hexrays_ready=true.
Сессия закрыта без сохранения изменений. Доказательства:
`inventory/ida-native-verification.json`. Подробности: `docs/ida-mcp.md`.
GoMMO по-прежнему доступен через stdio-проверку, его глобальная регистрация не менялась.

## Universal Modder: установлен и проверен

Источник: https://github.com/rehan-remade/universal-modder,
commit `9811709d950979f1b5012dddf10b7ec122d7e95e`.
Все 13 навыков установлены skill-installer в `C:\Users\Admin\.codex\skills`.
CLI um 0.2.0 установлен через uv tool install --editable из закреплённой локальной
копии в local/universal-modder-install, вместе с локальной базой знаний.

Все навыки прошли quick_validate.py. Единственная адаптация: `<game>` заменён на
`this game` в description навыка game-recon, поскольку валидатор Codex не принимает
угловые скобки. Тело навыка не изменено; остальные файлы совпадают с источником.

Проверены um --version, --help, поиск базы знаний и um scan RFOnline --json:
проиндексировано 30 311 файлов. Сканер сообщил unknown native engine и признаки
nProtect GameGuard. R3Engine по имени не распознан; RF_Online.bin не перечислен
среди исследованных EXE. ASI loader — эвристика, а не доказательство мод-загрузчика.
Поиск RF Online выдаёт в том числе нерелевантные материалы о Red Faction.

Игра не запускалась, клиент не менялся. Генерация через fal/Sprixen/Voidless,
3D-рендер, управление игрой и видео не проверялись; ffmpeg и Blender в текущем PATH
не обнаружены. Внешние MCP и API-ключи не подключались. Это установка навыков и CLI,
а не полного плагина с fal MCP. Навыки доступны для выбора со следующего сообщения.

См. `docs/universal-modder.md` и `inventory/universal-modder-installation.json`.

## Материалы RF Online

| Каталог | Файлов | Байт | Что зафиксировано |
|---|---:|---:|---|
| Старые исходники | 962 | 17 763 094 | SHA-256 каждого файла |
| Клиент RFOnline | 30 554 | 11 401 335 169 | сводка дерева и хеши выбранных бинарников |
| rf455-v0.4.0 | 216 | 1 129 623 002 | сводка дерева и хеши выбранных бинарников |

В старом комплекте: 329 cpp, 463 h, 14 dsp, 14 dsw. Найденные проекты включают
движок, клиент, служебные серверы и утилиты; полнота игрового ZoneServer не установлена.
Версия «0.7 / 2004» пока является описанием пользователя, а не результатом атрибуции.

`RF_Online.bin` и его backup — PE x86. `gameserver.exe` из пакета 455 — PE x64.

- Текущий клиент: `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`.
- Backup: `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
- Backup совпадает с SHA-256 клиента, указанным в README серверного пакета.
- Происхождение различий текущего клиента и backup ещё не установлено.

Манифесты: `inventory/legacy-files.json`, `inventory/reference-binaries.json`,
`inventory/roots.json`. Полный хеш-манифест 11.4 GB ресурсов и резервное копирование
всех игровых данных в этот этап не входили. Базы, конфиги с паролями и игровые
ресурсы не добавлялись в Git.

## Границы проверки

Полная сборка клиента, восстановление протокола,
распаковка клиента и изменение игровых файлов не выполнялись. Статический аудит
входов/зависимостей всех проектов выполнен; пригодность SDK/ABI и фактическая
линковка ещё не подтверждены. Восстановлены
IDAPython и MCP; реальная проверка выполнялась на старом LoginServerSR.exe.
Полный анализ клиента 455 через IDA пока не выполнялся.
Свободно на E: около 1776 GiB на момент проверки.

## Дополнение: аудит собираемости 2026-11-04

- inventory/build-audit.json содержит конфигурации, SOURCE, include-кандидатов,
  библиотеки, RC-ресурсы, SHA-256 проектов/.lib и сравнение серверных деревьев.
- 12 проектов имеют все перечисленные SOURCE; все DSW разрешают DSP.
  Это не означает, что 12 проектов уже собираются.
- Вложенные AccountServer/LoginServer совпадают с внешними по исходникам/проектам;
  различаются только .ncb/.opt/.plg. Канонический каталог — внешний RF_Server.
- 26 .cpp не входят ни в один DSP. Полный ZoneServer-проект и исходная БД не найдены.
  MySQL-схемы GoMMO не считаются подтверждённой заменой исходной серверной БД.
- Уточнение ADO: четыре #import есть в непроектных обёртках; серверные проекты
  используют ODBC (rfnewdatabase.h/cpp). msado15.dll найден на хосте в обоих стандартных
  Program Files-каталогах; совместимость с будущей VM не проверялась.
- cl/msdev/nmake/rc/link не найдены в PATH; поиск cl/msdev/nmake под RFOnlineTrash пуст.
  Windows Kits в проверенном стандартном каталоге не обнаружен.
- Пять тестов сканера прошли. Все 962 исходных файла сохранили прежние SHA-256.
  Оригиналы и конфигурации системы не менялись в этом этапе.

## Проверка VS 2026 после установки

Проверка: `scripts/Invoke-Python.ps1 scripts/probe_msvc.py`.
Отчёт: inventory/msvc-verification.json. Генерируются только собственные smoke.cpp
и CMakeLists.txt в work/msvc-smoke. Скомпилированы windows.h/Win32 API и static_assert
32-битного указателя; линковка/запуск завершились с 0, вывод x86 Win32 OK.
SHA-256 и entry point RVA тестового PE x86 записаны в отчёте.
Сырые журналы в artifacts/msvc-smoke не включены в Git.

В песочнице MSBuild FileTracker завершался с E_ACCESSDENIED; тот же тест вне
песочницы прошёл. Это не неисправность установки. Глобальный PATH не менялся:
используется VsDevCmd с host x64 / target x86. Также найден toolset 14.44.35207,
но он не испытывался. Проверка не охватывает RF-код, старый DirectX и ABI .lib.

Исторические записи выше о ненайденных компиляторах относятся к состоянию до
установки VS. Блокер отсутствия современного компилятора закрыт.

## Начало клиентского переноса

Подготовлены 492 побайтово проверенные копии RF_Client/R3Engine. Современный проект
движка (58 C++/1 RC) успешно сконфигурирован. Первая компиляция завершилась с 1:
12 COFF x86 объектов получены, отсутствуют DirectX 8 headers, есть C2065/C7732 в
двух legacy-файлах. Библиотека ещё не собрана. Инвентарь client-build-inputs.json и
client-build-result.json, подробности research/client-port-first-build.md.
Отсутствие DirectX-заголовков теперь подтверждено компилятором, а не только поиском.

## Последующее M5: настоящий GPU и map path

M5 закрыт для первого helper-data участка, gate inventory/client-m5-checkpoint.json.
Own entry полного client project выполнил настоящий D3D8 HAL на RTX2080Ti, загрузку/
отрисовку5RPKentities и5real particle scripts, CLevel::LoadLevel/FrameMove/render/release
для lobby и Platform01.13cases/321checks,0warnings/errors, allocation и COM balance0.
Platform01:23helpers/8interiors и два weather layers15/500; inside/night stop,
outside/night start,outside/day stop проверены настоящим FrameMove. GPU BMP прочитаны
из backbuffer, hashes сохранены, кадры просмотрены. Control words027F→027F→007F;
map/particle/render/helper consumer не изменяют007F. Reference startup state неизвестен.
Sandbox HAL creation дал0x8876086A, тот же EXE вне sandbox прошёл без изменения source.
Game DLL delayed и не загружались; звук/сеть/normal WinMain/input EXE не запускались.
703weather/30resource/23 337targeted helper regressions прошли на final lab SHA
ece2acccb434ef06ee0aba3d35a15778f3bdf87e5b70589221f8f34732aed3ae.
Normal build a761c930... не менялся. IDA reference graphics analysis:3functions/6exact
instruction checks на обоих pinned PE; owned77bfa3a2 закрыта с save.
research/client455-graphics-runtime.md. D3D9/full Character/particles/clock/UI/network
и M6/M6F/M7/M9 открыты; M8 modernization не требуется.

## M6: численный clock455

Собственный x86 clock module восстановил8scalar functions и256byte clock prefix
из0x8B1F20/RVA0x4B1F20.773instruction bytes совпали в обоих pinned PE после
проверки absolute operands/constants.1275checks/12FP modes прошли standalone и
в полном lab клиенте. Normal retained2used routines/prefix,lab9; linked code,
constants и .CRT$XCU initializer KERNEL32.GetTickCount проверены в обоих EXE.
Обычный RF_Online.bin2440704bytes/entryRVA0x1BBAA0,SHA
f5f945160fe45255b9cea935cb3e27946a0a5ab531a18b1279abbd41164e18e5,не запускался.
Lab SHA bb441c5c3e393f98a298355b794e14bbb95d1efdd790c36e1356080d64c44e9b:
703weather/30resource regression checks и2real GPU cases/59checks на Platform01
прошли. Helper/interior/night states прежние,FP007F,release balance0;game DLLs отсутствуют.
287normal modern x86 /MT objects проверены; дополнительный61-й engine object —clock.
Уточнение:0x7E3E55 это console %time; настоящий clock map caller0x7C8B60.
Cached time/packet origin/CLand/console и full lighting ещё открыты.
research/client455-clock-source.md; inventory/client455-clock*.json/client455-time-callers.json.
M6/M6F/M7/M9 открыты. Historical M5 evidence сохранён отдельно и проверен --saved.

## M6: client map message8/5 → CLand time

Восстановлен selected source path client packet8/5,CLand timestamp/receipt tick cache
и successful map-load clock hook. Source overlays трёх client files,21behavior files
total; own MapTimeState16bytes не применяется как binary455layout. Критический130byte
numeric fragment0x7C8DC4/RVA0x3C8DC4 совпал с обоими pinned PE.314component/full-client
checks/12FP modes/UTC+JST; actual linked helper/CLand/packet object references проверены.
Own GPU entry выполнил реальный CNetMsgProcessor_Map8/5,CLand Create/LoadLevel(char*)
и public post-load hook, Platform01 FrameMove/render/CLand Destroy/UnloadLevel.
Synthetic timestamp43200 при UTC0 дал fractions0.5/0.5,mapDay1 для synthetic mapIndex12.
Это не full byte-index UI/camera/effects path и не root network/socket verification.
2GPUcases/66checks,0errors/warnings,allocation/COM balance0; FPU007F,frame просмотрен.
1275clock/703weather/30resource regressions и288modern x86 /MT checks прошли.
Normal2448896bytes,entryRVA0x1BBDF0,SHA
a1b9dd5d7e45313ef414d90dff198717e66bc5d58e5ed95bcb72fba601cf456a,не исполнялся.
Lab SHA ad3a17d3d54372c4a05962ae0088b3f44d3d96b438f0873e94c06317cae5f441.
Localtime32 old-CRT timezone/DST/invalid/Init domains,opaque fields/other consumers,
full CLand/console/lighting и M6/M6F/M7/M9 открыты. Owned IDA92d1827c закрыта/save.
research/client455-map-time-source.md; inventory/client455-map-time*.json.

## M6: local clock commands и actual input

Восстановлены time/real_time,grade>=1 input hook в actual CHAT_INFO::SendMessage и
real HMS set/get. Clock10scalar functions+256byte prefix:1037instruction bytes
совпали с обоими PE;1443checks/12FP modes standalone/full-client. Parser432ASCII cases/
2628checks/12FP modes,20actual input/access/history/lifecycle checks прошли:grade1
accepts,grade0 rejects. CNetworkMgr ctor/dtor/WSAStartup выполнены;Create/SetNetSystem/
Connect не вызывались,network processes0,соединений/отправки нет. Game DLLs отсутствуют.
Две команды в own graphics entry управляют actual Platform01 weather FrameMove:
2GPUcases/69checks,0warnings/errors,Dmalloc/COM balance0,FPU007F,23helpers/8interiors.
289modern x86 /MT,314map-time/703weather/30resource regressions прошли.
Normal2450432bytes,entryRVA0x1BC330,SHA
d656498a2465feec8c9b4fb44149f01e38aa8e4288e4cc9e4bb4c555ec490919,не исполнялся.
Lab SHA d19ea1193dbfd546e68eadb3332e145de3d42d83e5429155726c807cfd3a1c24.
Other local directives/full chat/GUI input/locale/calendar/lighting остаются открытыми.
Owned IDA1bf47ee9 закрыта/save;research/client455-time-commands-source.md.
Следующий critical path — Character sources/ABI перед D3D9; current header/import
contract использует IDirect3DDevice8. M6/M6F/M7/M9 не закрыты.

## M6: первый Character source unit

Четыре legacy CPU mesh bindings восстановлены source и подключены normal/lab.
245checks standalone/full-client и4COFFtests;три actual InitVertex E8 calls доходят
до source. Skinned/unskinned CPU meshes3vertices/0faces загружаются/освобождаются.
Pointer+160 задаёт штатный FindBlendParent,включая count0;constructor patch не сделан.
455mesh5803/vertex64/inline blends отличаются от legacy1072/36/heap;first-match455
противlast-matchlegacy учтён как gap. Full Character455/render/real assets открыты.
Normal2450944bytes,entryRVA0x1BC340,SHA
9cb2329eda37ff61548f7b24fcb70b617b85a151623e867ced71439972e3a794,не исполнялся.
Lab4146176bytes,entryRVA0x7EAA,SHA
d59233bc12b46799bc8cc5311acfeb6dcb09f3e900624eb3b1933d08458b1c46.
289modern client/engine/JPEG x86/MT иown binding archive /MT проверены.
1443clock/314map-time/703weather/30resource,432command cases/2628checks+20actual input,
Platform01/device2GPUcases/69checks прошли.0GPUwarnings/errors,Dmalloc/COMbalance0,
FPU007F,frame просмотрен;это map/weather regression,не CharacterGPU acceptance.
Owned IDAc99d5253closed/save;8reference bodies/11instruction sites в обоих PE.
research/character-mesh-source.md;inventory/character-mesh-source*.json.

## M6: full legacy InitVertex source,2026-11-05

Source Character unit расширен до8functions/full InitVertex/vertex/physique.245binding+
6732InitVertex checks/144cases/12FP modes standalone/full-client,4COFFtests и2actual
LoadRealData→source calls прошли. Actual SDK MakeVB использует test-only COM capture,
physical Character GPU не сертифицирован. Нормальный WinMain не исполнялся.
Normal2451456bytes,entryRVA0x1BC4B0,SHA
a070e9fb4350290fc8877940ae6cfbce417b0cc12b5a12b8a6a82ba5e121d573.
Lab4167680bytes,entryRVA0x7EC8,SHA
ce6a1bb826d11f219218d4361f923ba1b11de9b31fe998b65b98696b68104cce.
289modern COFF +source bindings/init objects x86/MT;clock/map-time/weather/resource/
time-input regressions прошли. Platform01/device2GPUcases/69checks,0warnings/errors,
Dmalloc/COMbalance0,FPU007F;frameSHA равен прежнему просмотренному frame.
455vertex normals инвертированы,64byte layout иMESH08path91F250→922A00 подтверждены.
7bodies/field/magic instructions/2calls в обоих pinned PE;3model samples закреплены.
В этой ревизии MESH08реализация ещё отсутствовала;старая693frame схема не подходит кShield065.
Owned IDAab009b3b/012583e5closed/save;research/character-init-source.md.

## M6: MESH08 format source и реальный corpus, 2026-11-05

В loose model tree прочитано2708files:858MESH08 и1850other-prefix, не включённых в
данный форматный аудит.858/858 прошли точный byte roundtrip:515096894bytes,
12090meshes,5153052vertices/indices,412222bone records. Archive/RFS модели иполный
resource inventory не покрыты. Source C++ bounded reader/writer x86/MT проверен:
6304checks/12real samples/393parts/1309guard-page truncations standalone/full-client;
7Python tests.3reference bodies/12instruction sites сверены в обоих pinned PE.
Материалы, bone resolver иshared GPU state не восстанавливаются форматным модулем;
normal LoadRealData его ещё не вызывает, обе API в normal EXE удалены linker.
Lab decoder/encoderVA6B0400/6B0700, RVA2B0400/2B0700;source,неbyte-identical port.

Normal2451456bytes,entryRVA0x1BC4B0,SHA
43863bc4334d896a91888f0b132b79d7e85974b519073c2ebad8a4995b89c6af;
snapshot mesh08-format,не запускался. Lab4483072bytes,entryRVA0x8125,SHA
d8edc962d7985e2598cd1ed4080c416e03ff94ae88f2d4875cf3473657d4f1a6.
289modern COFF иformat object /MT. Character245+6732checks,clock1443,map-time314,
weather703,resource30,time-command432cases/2628checks+20actual input прошли.
Platform01/device2GPUcases/69checks,0warnings/errors,Dmalloc/COMbalance0,FPU007F;
frameSHA равен прежнему просмотренному. Это map/weather regression,неCharacterGPU.
GameDLLs/referenceEXE/normalWinMain не запускались. Owned IDAeb76ecefclosed/save.
research/client455-mesh08-format.md;inventory/character-mesh08-corpus.json,
inventory/client455-mesh08*.json. M6/M6F/M7/M9 открыты.

## M6: packed455 parent/bone source, 2026-11-05

Четыре455CPU kernels (lookup/parent array/rematch/MESH08bones) восстановлены source.
4bodies/12instruction sites сверены в обоих pinned PE;owned IDA6f091546closed/save.
2237checks/12real mesh-skeleton pairs/393meshes/455skeleton records прошли standalone
иfull-client own entry;вfixtures0missing influences,max4unique/mesh.20cases count31–50
сохраняют подтверждённое перекрытие pointer copy/matrix fields;owncap50 не доказательство
официальной безопасной capacity. Plain BN framing/names проверены tooling;полный
skeleton/model loader,selection/transforms/animation/material/GPU ещё открыты.
Normal используетlegacyCharacterABI,unused455APIs stripped;lab4APIlinked fromsource /MT.

Normal2451456bytes,entryRVA0x1BC4B0,SHA
d52d1e6889e679af1262182088e6f648affd7a0f73d89b23c35c975f310ac30b;
snapshot mesh455-bones,не запускался. Lab4534784bytes,entryRVA0x81D4,SHA
0a1dbe6d2f069b436556e7933648b3ce44ac877a0e808653cc1ed7d93d92b79d.
Regressions:mesh08 6304,legacy245+6732,clock1443,map-time314,weather703,resource30,
time-command432cases/2628checks+20actual input прошли.289modern COFFx86/MT.
Platform01/device2GPUcases/69checks,0warnings/errors,Dmalloc/COMbalance0,FPU007F;
обаframeSHA равны прежним просмотренным кадрам. Это map/weather,неCharacterGPU.
Source macro ограничен labfile,все180old units без причины не пересобираются.
GameDLLs/referenceEXE/normalWinMain не запускались. M6/M6F/M7/M9 не закрыты.
research/client455-mesh-bindings-source.md;inventory/client455-mesh-bindings*.json,
character-mesh08-bone-pairs.json,character-mesh455-bindings-graphics-runtime.json.

## M6: mesh constructor/header/material request source,2026-11-05

3CPU API constructor final state/counters,header scalars/names/matrices/material
request flow восстановлены source.14562checks/12real files/393parts/12FP modes
standalone/full-client прошли. Матрицы вызываютactual D3DX9_36;texture provider
вtests scripted,физическийTextureManager/sharedGPU/normal loader ещё открыты.
Header domain858files/12090meshes:8659empty primary,3431DDS/backslash;0unterminated/
nonASCII/% strings,nonfinite/nonaffine/zero numeric3x3det. Это ограниченнаяклассификация.
5bodies совпали вbothPE;thunks854130/85412A IAT resolveD3DX9_36;ownedIDA716ae4faclosed/save.
SysWOW64 DLL иclient-local DLL byte-equal,SHA
c12f0ab0338eb5031d3d04beaf7208ac848f7e037d21ff963d2af90221cbe935,x86/3734536bytes,
version9.19.949.2111,Microsoft AuthenticodeValid. Direct export подтвердил1ULP offset:
inverse diag(2,2,2,1) bits3EFFFFFF x3/3F7FFFFF. Сохранятьquirk;reciprocal approximation
предполагается какпричина,внутренниеинструкцииDLL не исследованы.

Normal2451456bytes,entryRVA1BC4B0,SHA
6f486f1f4ef950d207d9fd9cba9d2e647d7538954185c39adfeec7d5c9316a0b,
snapshot mesh455-header-material,не запускался. Lab4585984bytes,entryRVA828D,SHA
f55fdb172661cbcfdf131aa3d7a0ddba1413b2039151ff866c88f78f2a3c42cb.
Lab3API fromsource;normal unused APIs stripped.289modern COFF/MT. Regresions:
mesh086304,binding4552237,legacy245+6732,clock1443,map-time314,weather703,resource30,
time-command432cases/2628checks+20actualinput. Platform01/device2GPUcases/69checks,
0warnings/errors,Dmalloc/COMbalance0,FPU007F;обаframeSHA равны просмотренным.
Это map/weather regression;CharacterGPU ещё открыт. GameDLLs/normalWinMain/referenceEXE
не запускались. M6/M6F/M7/M9 не закрыты. research/client455-mesh-runtime-source.md;
inventory/character-mesh08-headers.json,client455-mesh-runtime*.json,
character-mesh455-runtime-graphics.json.

## Документация интеграций

- [GoMMO: stdio bridge и studio_status](https://oldschoolops.com/docs/gommo-studio/automation/ai-assistants/).
- [Codex: настройка MCP](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).
- Локально: `IDA Professional 9.2/README_python3.txt`, справка `idapyswitch`,
  `docs/user-guide/configuration/command-line-switches.html`.

Результаты локальных запусков имеют приоритет над устаревшим названием папки/README.

## M1 и закрепление клиентского эталона

M1 выполнен по compile/archive: 58 COFF x86 объектов, R3Engine.lib, две чистые
пересборки. Дальнейшие CRT/ABI/поведение проверяются отдельно. DirectX 8.1b SDK имеет
действительную подпись Microsoft и архивный хеш; установщик не запускался.
Результаты: inventory/directx81b-sdk.json, client-source-patches.json,
client-build-result.json, research/client-port-m1.md.

Два клиентских файла отличаются 5 байтами; область ветвления и общий double
исследованы в IDA, собственная сессия закрыта с сохранением. Текущий клиент закреплён
эталоном по SHA-256 в config/client-target.json. Версионная константа не считается
доказательством атрибуции. Полный манифест ресурсов ещё не создан.

M4: 207 определений Character кешированы, 30 операндов инструкций проверены.
Диагностический Character.h: 67 layout assertions и 165 публичных decorated names
проверены; все 180 C++ клиента скомпилированы. Конструкторы/inline/STL ABI ещё открыты.
Отдельно собран настоящий /MT R3EngineMT.lib; 180+58 COFF x86 /MT проверены.
LNK2038 устранён корректной сборкой, genuine DX8 .lib подключены. JPEG 6b /MT прошёл
28 ABI сравнений и 2 точных golden decodes; 26 Miles импортов есть в 455 DLL.
Проверены 284 x86 /MT объекта. Diagnostic link и clean rebuild успешны.
Native собственный тест подтвердил: старый FILE EOF доступ Character не работает с UCRT;
classic CRT прошёл только этот частный тест. На том этапе RF_Online.bin ещё не был
получен; последующая полная сборка описана выше. Input EXE/DLL не запускались.
research/client-dependencies-m4.md и client-port-m4.md;
inventory/client-character-diagnostic.json, client-mt-variant.json,
character-header-recovery.json. Четыре проверки COFF прошли.

Последнее дополнение: адаптер 8 stdio API прошёл 1828 собственных native проверок и
3 теста COFF; инструкции/релокации 10 входных объектов сохранены. Runtime старых
двух Pattern/Item загрузчиков проверен на valid fixtures (49 checks). CObjectManager
constructor восстановлен; AnimationManager
получил empty-vector constructor + реальный Init. 3102 проверки реальных SDK операций
на unloaded records прошли. Реальные _Xlen/_Xran /MT exceptions прошли 770 сравнений
с classic system exports; aliases в тестах удалены. Link gaps в выбранной сборке закрыты.
Полный Character unwind/loaded data/render не проверен. Header: 67 layout assertions.
research/character-effects-and-exceptions.md.
Новое: SetTexPath/SetMipMap и empty renderer construction восстановлены; 18 ABI
byte checks, 8 instances/136 part managers, всего 3630 combined native checks прошли.
Последующее продолжение: 455 DrawCharacter calls под отдельным flag/ledger,
bounded legacy SetEffect bridge и 59 native checks с CPU mesh effect application.
Последующее продолжение: 455 logging и success->lobby edge перенесены отдельными
flags с сохранением legacy bodies. Нет заглушек CheckFiles/SendLog или _DEVELOPER_ bypass.
Native logger 14 cases/66 checks; полная сборка и clean прошли. 455 map/36-grade
effect behavior ещё не перенесён. research/client-first-build.md.
research/client-draw-and-legacy-effects.md.
Конструкторы используют реальные SDK Init, но исходный inline/sizeof не доказан.
research/character-setters-and-construction.md и inventory/character-setters.json.
research/character-managers.md и research/character-stdio-adapter.md.
Для завершения последней /Goal повторно получены две чистые сборки R3Engine x86;
runtime sections/relocations 58 объектов совпали. Хеши исходных PE/копий и 5 различий
повторно проверены, 140 SPT / 97 543 записи прошли round trip. goal-checkpoint.json.
Предыдущая ограниченная цель выполнена уведомлением о начале пункта 4.
Активная новая /Goal — M9, финальная приёмка клиента 455 без модернизации графики.
Полный клиент ещё не готов.

Последний клиентский source unit (2026-11-05): Character455 record1188/manager4148,
IDcache/rawMSH/texture refresh.24body ranges equalbothpins; ctor92instructions
вмаленьком trackedmanifest.850CPU/1138HALchecks standalone,1138вполномlab;
12models/393parts/276uploads/59texturepointers,COM/heap/Dmalloc0. Source x86/MT,
/W4/WX.13C APIs происходят изsource archive ивызываются вlab;normal unused/stripped.
Normal сборка289modernCOFF/MT,lab185clientTUs;проверены модели10021 иPlatform01/device69,
прежниеframeSHA равны. PE identities:inventory/client455-character-manager-checkpoint.json.
Normal EXE не запускался;его runtimebytes кромеtimestamps равны предыдущейrevision.
IDAownedc3f13f8bclosed/save. ПолныйBN/dispatcher/animation/D3D9renderer остаются M6.
research/client455-character-manager.md. Изменений исходного installation/server нет.
Следующий standaloneunit: legacyMSH/BN intermediate parser/lifetime source,
4606checks/17samples459records/1183guarded prefixes/7allocation failures/12FPmodes,
6Python tests,heap0.7bodies pinned;importer/converter покаpending. SourceO2/W4/WX
x86/MT. Fullclient PE не менялся;owned IDA926983beclosed/save. Reports
inventory/client455-legacy-models-reference/build/cpu.json;research/client455-legacy-model-reader.md.
Последующийconnectedunit:legacyMSH/BN converter/importer/MTG/weights/indexing/binding,
66627capture/14896HALchecks standalone/fullclient;34runs972parts/832HALuploads,
2CPUretained,12actualBN→MESH08pairs393parts276uploads.9bodies equalbothpins,
10sourceAPIs verified,heap/COM/Dmalloc0. SourceO2/W4/WX/x86/MT;fullclient186labTUs,
289normalmodernCOFF/MT. Current manager1138/model10021/Platform01-device69passed,
frames иnormalruntimebytes (excepttimestamps) сохранены. Всеidentities/evidence:
inventory/client455-legacy-runtime-checkpoint.json;research/client455-legacy-model-runtime.md.
Normaldispatcher/ANI/animation/shaders пока открыты. Owned0d9553e1/08d81b2fclosed/save.
Последующий unit:ANI/rawIO/record284/lifetime/attachment/Character dispatcher.
16bodyranges equalbothpins;14513CPU/15181HALchecks standalone/fullclient,
27ANI1062tracks/6Python tests/22real switches/11BN→MESH08pairs794parts660uploads.
13sourceC API actual caller/archiveproof;sourceO2/W4/WX/x86/MT. Stickyflags иrawleak
проверены (отдельнаяharnesscleanup после наблюдения). COM/Dmalloc0;normal289modernCOFF,
lab187clientTUs. Current legacy14896/manager1138/Platform01-device69passed,
frames/normalruntimebytes кромеtimestamps сохранены. Normalconsumers/pose/shaders/
AnimationManager/asyncworker остаются открытыми. Owned45964631closed/save.
Gate inventory/client455-animation-checkpoint.json;
research/client455-animation-dispatch.md. Original/server inputs без изменений.
Последующий source unit: pose evaluators/основные FrameMove phases,sourceO2/W4/WX/
x86/MT.11realpairs/132updates/2298skin matrices standalone иfullclientownentry,
5sourceC APIs actualcaller/archiveproof,heap/Dmalloc0. CPUonly,безGPUdraw.
Normal180client/289modernCOFF,lab188TUs. Старые runtime suites не повторялись;
normalruntimebytes кромеtimestamps сохранены. Secondary/producer кадров/manager/
worker/normal consumers/shaders открыты. Gateinventory/client455-pose-checkpoint.json;
research/client455-pose-source.md. НовыхIDA sessions нет,оригиналы/серверы не менялись.
Следующийunit:secondary91E270/borrower7CD430,3bodyranges и18doubleconstants pinned.
Source state84/globals28/5effects,O2/W4/WX/x86/MT;36scalarcases/2realCoraBN/6updates
component/fullclientownentry,6APIs sourcecaller. Relatedpose11pairs/132updates
passed;прочиеoldbulk suites не запускались. Heap/Dmalloc0,CPUonly/noD3Ddraw.
Static__CIsin reference поканеsource,mandatorycallback;labmodernMTsin прямоотмечен.
Normal180client/lab189TUs;normalruntimebytes прежниеexcepttimestamps. Owned8115e37c
closed/save. Gateinventory/client455-secondary-checkpoint.json;
research/client455-secondary-motion.md. Оригиналы исерверы без изменений.
