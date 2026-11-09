# Память проекта

Обновлено 2026-11-09. Root `E:\RFOnlineTrash\Source\WorkFlow`.
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

107 PARTIAL: в CMainApp восстановлен core прицеливания20: pending, отдельная
командная позиция, курсор через настоящий BSP, перемещение6 частей эффекта и
tagged Miles Radar.29 реальных проверок проходят; память785169→785169.
Pending0 разрешает hover при соответствующем статусе; pending1 пока отказывает
до мутации из-за отсутствующего C1A message provider. Игровых command producers
ещё нет; SetPending проверен в full-object lab, но удалён из обычной PE linker.
Новая PEd09eec8d…/entry15adc0/182-20-60/unresolved0/Create1. Status62/magic36/
resources66/audio157/runtime573/account/hotbar7/storage3 проходят;10 GPU frames
просмотрены,6 hover побайтно равны106. Gate107 current,106 historical.
Full nuclear/world/message/device/client acceptance ещё открыты. M6/M6F/M7/M9 OPEN.
[Доказательства](../research/client455-nuclear-aiming.md).

Текущий gate: inventory/client455-nuclear-aiming-checkpoint.json.
Проверка: Invoke-Python.ps1 scripts/checkpoint_client455_nuclear_aiming.py.
IDA7cb76d0f saved/closed/list0;19functions/1670asm/19equalranges/2pickslots.
Raw artifacts/client455-progress/nuclear107-*. Broad writer scan partial (2M cap),
не полное покрытие callers. Core20 является member настоящего MainApp; целый
32byte targetcontainer/list12 ABI ещё не принят. FrameMove/Clear retained в PE,
SetPending без игровых producers удалён linker. Frame hook стоит перед ordinary
effects update,но полный frame order не принят. Отдельная команда SetPosition
не меняется при визуальном движении курсора. Missing cue всё равно включает
звук; Clear с handle0 его не останавливает — target quirk проверен.
Нативный lab: work/m9/a3a3c42f/nuclear-aiming-001;29checks,7warnings(6R3T+
expected missing cue),90 drain ticks,realneutralAS1/Miles,soundmuted,memorybalanced.
PEd09eec8dd10a35dbd2bb07523901e0b66dc250dec611fee7efe231800b749c9d,
2157056bytes,base400000,WinMainb8ed0,afterCreateb9044;Fast2D ready7969.
Engine546a7529…/67 unchanged;033baseline сохранён,старого082snapshot нет.
4 effect-runtime GPU frames (отдельная controlled scene,не BSP lab) и6 hover
просмотрены;hover byteequal106. Большие159k/world/audio/остальные32GUI suites
не повторялись. Gate106 snapshot в artifacts,егоruntimegate historical.
Original/server не менялись,inputEXE не исполнялись. Полные сведения в research.

Исследование108:21 выбранная функция/17fullasm/2284instructions/21equalranges
обеих455;IDAffcaa552 saved/closed/list0. См. research/client455-system-messages.md
и inventory/client455-system-messages-reference.json. Runtime gate остаётся107.
Подтверждено расхождение hook:455 вызывает nuclear Frame в конце Render после
UI Draw (RVA14b059), наша107 — до effects update. Перенести hook без дублирования.
Center owner:pending64/active84/max3,queue/pacing/fade;chat4panes/14categories/
style18/wrapping требуют переноса.108 пока static analysis,не новый runtime.

Далее108 — настоящий localized C1A/CE7 message/notification pipeline и
pending1 hover cancellation. Не подменять пустым legacy _SetSystemMsg(DWORD)
или chat-only выводом. Затем command/response producers, list12/container,
final position commit и остальные input cancels. Target orthographic picking,
menu dummy/unsafe FP и полный shutdown остаются открытыми.
Обязательны world pass placement/dynamic-light compositing,quality option/UI,
blur/advanced axis/parabola/multi/curve/device lifecycle. Затем —64-битные455
receivers/остальные44DEE0 effects,Linker handlers/queue,typed quantity/backups/
network callers,inventory/equip/SF/Animus,potion cache,Macro/Vending/fullAdd/
bootstrap и Quest provider. Все прежние fullGUIItem/tooltip/lifecycle/reset/
privateABI/FPunsafe/OOM/concurrency/shutdown,SF/Quest/36boards/Trunk/protocol/
Tutorial/QBI/fourstage/Login/auth/game gaps обязательны. M9 — финальная приёмка
полного клиента455 без модернизации графики; цель не сужена.

Исторические101–105: research/client455-{board-hover,player-status,tagged-audio,magic,effect-resources}.md;
baselines before106 — artifacts/client455-progress/.

## Исторический результат100

100 PARTIAL: восстановлен значок блокировки предмета по flag21 в обычных
CGUIItem/CBoardObject/CLinkBoard. Реальный sprite52 содержит glyph8×12 на
texture8×16. Проверены копирование, позиция, Empty/Remove и отдельный Draw
при обрезке изображения.256 значений BYTE setter,256 wrapper flags,18 geometry
cases и6 новых просмотренных GPU кадров проходят;35 прежних кадров byte-equal.
Новая PE49882fc3…/entry157aa0/182client-20kernels-56facade/0unresolved/Create1.
Исторический gate — inventory/client455-item-lock-checkpoint.json;099 runtime
исторический. Full drag/use/remove/swap/hover/MsgProc,live callbacks,potion cache,
Macro/Vending/fullAdd/bootstrap ещё обязательны. M6/M6F/M7/M9 открыты.
[Доказательства](../research/client455-item-lock.md).

Source:CItemObject/CBoardObject layout620 unchanged;nonvirtualRefreshLock455
added inclient455_item_object.cpp +board_object.inc. GUIItem hasownCGUIObject
m_lockFrame455;ConfigureLock455/BindLock455/SetLock455 initem_icon.cpp;
item_icon_port copiesdescriptor/rawShow andhideschildctor. LinkerAdd calls
RefreshLock455 beforefinalgrade;flag21 refusal removed,other3 retained.
Real52/0/0 DXT1glyph original8x12/texture8x16 stagedbycopy_item_icon_skins
fromnewref.8ownrunners updated,notlegacyinputs. Targetresize is explicitBind;
globallegacyGUIbase unchanged. Clippedlock normalDraw is intentional455quirk.
Empty andRemove preserveShow;Draw exitswhenimageabsent. Native explicitlyshows
actualinventory/copy/Linkericons;notnormal fullwindow/bootstrap acceptance.
256rawBYTE/256normalizedflag21/18geometry/6newviewedGPU pass;allowners/Dmalloc0.
35 oldGPUframes byte-equal:ready6/timer6/window8/owners3/metadata3/icon9.
Oldreviews inheritedusinghashchain099/098;currentcheckpoint validatesbaselines.
Owners096 now3providerrefusals,plusactualflag21Add;syntheticSF/AnimusCPUicons
remainqualified. Hotbar7/storage3/account/currentPECreate1 pass. No159k/world/
audio/atlas093/2013owner/SF1447/manual095 repeats. Icon092 rerun justifiedclipchange.

NewPE49882fc3ef2ba826495dfbdff675a4ef30fa99dcced4557f50222d11fd306083,
2140160bytes/x86/base400000/entry157aa0/WinMainb7610/afterCreateb777a,
182client/20kernels/56facade/0unresolved. Derivedengine546a7529… unchanged;
baseline033/source preserved. Prior082derivedlib snapshot stillnotretained.
17functions/1610asm/17equalranges,actualItemLock.spr exactroundtrip;IDA5eef459d
savedclosed/list0. inventory/client455-item-lock-reference/native/visual-review/
checkpoint.json;research/client455-item-lock.md. Allclientmilestones stillopen.

Next101:typedhovermanager/screen beforeactualhandlers. Exploratoryraw ignored
hover100-full-exploration.json:180asm4FE020 +decomp dependencies (not fullpin).
Targetmanager hover+244/backup+248/otherbackup+252;nullhover copies620 firstbackup,
clearssecond via4FE5C0(0),deleteshover,screen.RemoveObject. Legacy singleCBoardItem
backup/rawGetHoverItem cast incompatible. Needconstructor/dtor/Copy620/backup/
ClearOperation/ReturnHover/managerstorage IDs audit andreal screen632210/632370,
PickingObjectEvent/cursor/tooltip/center/cancelstate2-6-10chain. No successful
recording/no-op;keepallgame dependencies. Thenactualuse/remove/swap/hover/MsgProc,
livecallbacks/potioncache/Macro/Vending/fullAdd/bootstrap. M6/M6F/M7/M9 OPEN.

## Исторический результат099

099 PARTIAL: обычный CLinkBoard получил50 записей перезарядки, поиск исходного
владельца, запуск таймеров и вспышку готовности. Ready child использует настоящий
лист455,40 клеток128px,34FPS и blend3.132 сценария анимации/48 сетки и6 новых
GPU кадров проходят;20 прежних просмотренных кадров побайтно сохранены.
Новая PE6b30676b…/entry157830/182client-20kernels-56facade/0unresolved/Create1.
Исторический gate: inventory/client455-ready-cooldown-checkpoint.json;098 runtime
исторический. Игровые use/remove/swap/hover,live callbacks,lock,potion cache,
Macro/Vending/fullAdd/bootstrap ещё обязательны. M6/M6F/M7/M9 открыты.
[Доказательства](../research/client455-ready-cooldown.md).

Production099 source:client455_gui_animation.h/.cpp +client455_linker_cooldown.h/.cpp;
port scripts/client455_linker_cooldown_port.py. Prepare182/20/56,0errors/unresolved.
NewPE6b30676b54424e15bdb60e296794b3e9ac9861ba24745e2df0798e5e947a4212,
2139648bytes/x86/base400000/entry157830/WinMainb7580/afterCreateb76ea.
Engine546a7529b51139e856b1a108fcad7849c14b2d00563b7abbfdcc8db10026fa5a;
67objects. Adds nonvirtual GetFrameTexture455 via shared2dsprite455.h,forced
through anicamera455.h AFTER port_std.hpp inallengine/clientTUs. Old033lib/source
preserved;derived082lib was overwritten bybuilder,no separateoldlibsnapshot.
Historical082linkedPE/labs retained;do notclaim082binary unchanged.

Static099 base79functions/5906asm/82equalranges remains historical
STATIC_ONLY_NOT_IMPLEMENTED. Newref ready-cooldown8functions/248asm/12equalranges,
sessionfa7d0341 savedclosed/list0. Currentruntime proof separate:newcheckpoint.
AS99fixture132rows,AG99fixture48rows;actualordinaryBeginDelay/FrameMove/Remove,
globalBoardManager sourcepack/originallookup,actualregisteredclonefanout,
active/attached/hidden,occupiedcache,partialRemove/fullExpiry andpendingerasequirk.
6newGPU viewed;20 previouswindow8/owners3/metadata3/timer6rawframes byte-equal,
oldvisualreview manifests inheritedbycheckpoint,not fresh nativehash reviews.
Hotbar7/storage3/account andfreshenginecontracts/PECreate1 pass. No159k/world/
audio/093atlas/092icon/2013owner/SF1447/095manual repeats.

Ready configuration:atlas1/action13/frame0,original1024x640,texture1024²,
8x5cells128,FPS34,noloop,initialstopped,blend3SRCALPHA/ONE. UV mustwrite raw
m_fSpriteUV;legacy SetSpriteU/V requires sprite andrescales,not applicable.
SinglefinalF32 x87 frameadvance. Childonlywindow.Update,notGUIItem.Update.
SetData resetsreadyplayback;SetPos centers signed;Sizealone doesnotrecenter.
Draw ownD3D quad FVF324/stride28/half-pixel;postalphaFALSE/wrap/ZTRUE verified.
Genericotherblend/clippedDraw explicitlyrefuse;fullprivateABI/numeric/reset/
resource-lifecycle notaccepted. ConfigureReady purestate/lazyactualtextureDraw.

Cache50x20:bank/ptr/start/offset/duration;ctor leaves bank/padding unwritten.
Admission actualIsAddedObject(bankrow) ORactive;occupied notoverwritten,each
matchingfreeentry ownclock,offset-1→0. kind/dataDWORD+4/wrapperindex vsserial+4,
not atlasID72. Remove clears ptr/start;expiry unsignedwrap thenzeroall20.
Ready windowchild queuedafterexpiry;pendingerase returnsnext thenouter++ again,
including explicit modeledsentinel wrap. Completeunsafe/stalepointer/OOM notaccepted.
Nonphysical original(FALSE) uses actualpayloadpointer;equal(TRUE) seriallookup;
physicalboards1/0/5 vselqual1/0,SF3/7,Animus4,kind6board22,kind7board35.
SFforcepack=rawBYTE12category0/1→0,2→1,…5→4,else255;Skillpack=BYTE12;
group=BYTE15,subtype2singlesource. Rawgate114A070 default0/nonzero+SF suppressall.
Livegatewriter/Avatarpotioncache stillOPEN;Potion11 explicitlyrefuses.
Labstages actualglobalsourcepacks manually,not fullCItemBoard.Add/bootstrap.
SFgroup twoCPUicons synthetic,actualpayloads/boardpack;not fullSFUI acceptance.

Next100:actualuse/remove/swap/hover/MsgProc,vtablebank-slot500F80 vslegacynonvirtual
UI_UseRequest;liveSF/Animus/inventory/equipcallbacks,Avatarpotioncache,flag21lock,
Macro35/Vending27/fullAdd/bootstrap. Knownstatic099handlers alreadycached.
Allpriorclientgaps/M6/M6F/M7/M9 OPEN. Progress,notblocked. Fullclient%unknown.

Исторический runtime098 (его gate после099 исторический):

098 PARTIAL. Historicalgate inventory/client455-gui-timer-checkpoint.json.
Typed ordinary CGUIItem owns RF455GuiTimer child;olduntyped timer unchanged.
Source-owned selectedstate28,not private208ABI:duration/start/offset/rawstarted/
double remaining/floatangle. Reset leaves geometry/show/vertices;ctor leavesXY.
Start -1→offset0,other signedoffsets rawDWORD;separate clock forself/everymember,
duplicates/selfmembers restartagain. Update wrapDWORD,signed difference clamped0,
unsigned completion;completion leavesangle. Draw never updates/readsclock.
61AD60 state+3vertices copy;SetData reapplies destinationpos. Empty resets only
ifstarted;stoppednonzero remainder survives. Stop resets self/allmembers always.
TypedCGUISFItem query/SetPos/Size/Draw and actualLinker query use this timer.

Radial Draw target629D70:5 independent sectors45/135/225/315/360,finiteFPTAN
defaultpath;decoded CW027f atRVA72b128 (initial133f hypothesis rejected),double
pi3.141592741012573 atRVA6da958,float radians andtan spills. CPU-selected SSEtan,
FPexceptions/NaN/unmaskednumeric domains stillopen;do notclaim fullCRT equivalence.
Whole timer clip rejects partialrect;label hasseparate16-square scaled test.
Labels strictthresholds:0/60000/3600000 unit3 empty;secondsfloor(ms/1000)+1,
so45000→46;red<10/yellowothers,white minutes/hours. Context0/1/5 vs2/3 vs4
positions/scales;unknown leavesoutputs partial anddraw explicitlyrefuses.
Unclipped image→gradeframe order corrected per61B6B0;clipped grade→image retained.

32equalranges/29functions/2791asm;175state/112label/57rays/171triangles pass.
Native verifiesctorXY/copy/conditionalempty/derivedtyped update,separate clock
fanout duplicate/self andactual2clones query.29GPUframes viewed:timer6/window8/
owners3/metadata3/icon9.11of23previousrawframes changed bygradeorder;12byteequal
(glyph3/metadataempty1/icon8). Stopfanout availableinfullobjectprobe,unusednormalPE.
NewPEd943ef46fdd2dcc700ad051502462fe056e7464eff7dcf7458ddc746f4cc0d21,
2134016bytes/x86/entry156570/WinMainb74a0/afterCreateb760a,182/20/54TU,
0unresolved/engine082same. Hotbar7/storage3/account/ownPEearly/Create1pass.
IDA316a9b70 savedclosed/list0;rawartifacts gui-timer098-reference/session.json.
097runtimegate historical/staticproofs retained;new current098. No unchangedworld/
audio/159k/093atlas/2013owner/1447SF/095manual reruns. Originals/server untouched.
Next099 cooldowncache501C30/actualhandlers thenlivecallbacks/lock/Macro/Vending/
fullAdd/bootstrap;allpriorgaps mandatory,M6/M6F/M7/M9 OPEN. Progress,notblocked.

Исторический результат097:

097 PARTIAL. Current gate inventory/client455-linker-window-checkpoint.json.
ActualCLinkBoard embeds CGUILinkWindow455 (old8slotview no longer actualmember),
constructorbindsowner,InitWindowcallsactualInit/bottomright,bank50C updatesactual
boardactivebank. Window hierarchy attaches real50iconowners096 to5bankcontainers,
mainrow,expand/all/prev-next/pin/select controls and bitmapglyphs. Layoutscale
min(width/1024,1);main481x46,row461x46,icon38,offset24,step44. Preservetruncation
AFTER origin+offset fornegativepositions. Expandedactivebankinmainrow,otherraw
nonzero flags0..4 stackup;cyclechecks4neighbors. Flags rawintnotbool.

Window MouseEvent/PostMessage codes455:drag502,Alt512,Ctrl510,left504,hover501,
Shift-right3327;right noShift/noDrag delegatesrealboardUseRequest. NativeUse
callback RECORDING subclass,notgameplay;fullitemhandlers/typedtimer stillopen.
Registeredobserver verifiedvia actualSendMouseEvent->GUIqueue->MouseEvent.
LegacyCGUISFItemtimer checks cannotcastnewCGUIItem;RF455_LinkerIconDelaying455
explicitlythrowsfortypedtimer untilrealproviderrestored,keepslegacyderivedquery.
No false-success timer. Target50C signedJGE atRVA101beb acceptsnegativeLPARAM
thenstoreslowBYTE;-1->255/-255->1tested. Sourceunsignedguardcorrected. Window
SelectBankBYTE rejects>=5;malformedboardbank subsequentuse notaccepted.

CGUIImageText455 readsrealatlas1/action7/frame3/cell7x9,numbersffcabaa6. Unknown/
out-of-sheetglyph255keepsblankposition;realzh-twframe lacksall19codes. Glyphmap
MOVoperandschecked. ClippedDrawpreservesobservedtargetnonidealUVandpersistentV
usedbynextnormalDraw;doNOT"fix" clippingformula silently. Fullallocator/numeric/
unsafezero-width/privateABI stillopen. Windowuseslocalizedzh-tw/main.spr and
common.spr,notCommonversions. SourcepixelreviewdoesnotexecutereferenceEXE.

51equalranges:36functions/3509asm+14doubles+21byte50Cbranchwindow;integergeometry
and9glyphMOVvaluesdecoded.21layout/1050actualicons/320sparsecycles/48events/
1792glyphs and8GPUframesviewed:5windowstates+normal/clip/afterclip text.16real
inventoryoriginals/50actualadmittedclones;Potion11excludedfromwindowfixturedue
requiredcooldownproviderrefusal096. ActualInitWindow/Draw/banknotifications/
ownerrelease/Dmallocpassed. IDAa69bf228andsecondarymessage session savedclosed/
list0. Rawref linker-window097-reference.json/message-assembly.json inartifacts.

096owners50 and094metadata566/race520/16icons repeated,newfacade;6rawframes
byte-equalpreviousreviews. Baseline096 artifacts/client455-progress/linker-
owners096-before097.json;metadataoriginal094 unchangedbaseline. Hotbar7/storage3/
account/newexactPEearly/Create1pass. PE SHA
9d8b57ad0ebb735aea477d99c9eebff05381d359f3086e7e137f6fbbfb702622,
2121216bytes/x86/entry155690/WinMainb73e0/afterCreateb754a,182/20/53TU,
0unresolved/engine082unchanged. NormalInitc6d50/Layoutc6f90/MouseEventc7570,
ImageTextDrawcfe60/clipcfcc0 retained.096runtimegate historical/staticproofs
retained. No unchangedworld/audio/159k/093atlas/092icon/2013owner/SF1447/095manual
reruns. AllpriorM6/M6F/M7/M9gapsmandatory. Progress,notblocked/notcomplete.

Next098: actualCGUITimer/typedGUIItemtimer state/copy/reset/draw/fanout,
Linkercooldowncache andactualnew455item-use/remove/swap/hoverhandlers. Then
liveSF/Animus source-boardcallbacks,flag21lock/remainingchildren/followers,
Macro35specialtextkind7/Vending27/fullCItemBoard.Add notifications andnormal
tablebootstrap. Coordinatewrapperkind/mixedcasts. Savedexploratorytimerdecomp:
artifacts/client455-progress/linker-timer097-exploration.json.61BC20self+registry
fanout calls61BCB0;41EED0->41EF00readstartedofchild+216.629880clears96/100/104/
108/double112/float120;legacytimerlayout/methods differ,verifybeforeborrowing.
Fullresize/deviceReset/windowlifecycle/privateABI/unsafe/OOM/concurrency still
open;remainingboards/Trunk/protocol/Tutorial/QBI/fourstage/Login/auth/game remain
required. Research research/client455-linker-window.md.

Исторический результат096 (runtime gate historical after097):

096 PARTIAL. Current gate inventory/client455-linker-owners-checkpoint.json.
Actual CLinkBoard.Add/Remove/Clear typedhooks nowclone/own CBoardObject wrappers,
windowmember RF455LinkerIconSlots owns50CGUIItem. Real5banks/10slots storage;
fullCGUILinkWindow Init/layout/scale/controls/input NOTyetwired,ordinarylegacy
draw still8oldslots. Probe drawsselectedactualboundiconsattestpositions,notfullUI.
Source contextBYTE1360 stored2. AddExist typedfalse,target500570;AddNew detaches
originalref,clones,packAdd failuredeletesattempt;successcopyicon38x38/refnull,
wrapperSetIcon/register/physicalgrade. Remove unregisters beforelocalempty then
packdelete. Emptyindex/itemIDFFFFFFFF,num1,refnull,framecolor0;gradeBYTEkept.
Typedsourceearlydestructorcleanup differsfromtargetuntilfullshutdownorder port.
Untypedlegacyborrowedpath remains;kindpredicate/mixedcasts notmigrated.

21equalpinranges/1105asm. Asm500590 confirms packs+16*bank hiddenbydecompiler.
50distinctclones/icons/refs51,occupiedclonecleanup/all50fanout/originalrelease
retains49copies/ordinaryClear-lastowner/destructor/Dmallocpass. ThreeGPUframes
viewed:realinventoryoriginal+twoactualLinkerboundcopies;gray255fanout;Remove4/9
clearslastimage. Freshnullcallbackcases0/1/2pass:SF/AnimusCPUicons deliberately
synthetic;Animus permissivefactory2onrealphysicaltable1,row3848,notcanonical
AnimusUIevidence. Fourexplicitmissingproviderrefusals leave noowner/registration:
flag21lock,potiondata88=11 cooldown,nonnullSFiconBoard,nonnullAnimusstate96.
These providers required,notreplacedbysuccessfulno-op. Scale1admitted;fullscale
min(screenwidth/1024,1) notconnected. SourceGetIteminvalidcoords boundednull,
targetuncheckedpointerarithmetic;unsafe/OOM/concurrency/privateABI notaccepted.

095registry160/094metadata566+520/16icons repeated,newsourcefacade:allnative
results unchanged,6rawframes byte-equal previousreviewed. Baselines095graph:
artifacts/client455-progress/icon-links095-before096.json;metadataoriginal094:
item-metadata094-before095.json. Oldvisualreports retained,096gatecheckslineage.
Hotbar7/storage3/account/newexactPEearly/Create1pass. PE SHA
613a6e973a94659c767feda5c3a422139d970429ae0e3478623a85932b87520a,
2113536bytes/x86/entry153bd0/WinMainb7830/afterCreateb799a,182/20/51TU,
0unresolved/engine082unchanged. NormalAddTypedc6250/RemoveTypedc65a0 nowretained;
registryregisterc96d0/unregisterc9810 nowretainedandactualLinkerbound (095gapclosed).
IDAbb7e4b5esavedclosed/list0;no newinstalls/serverwrites/inputEXEexecution.
095runtimegate historical/staticproofs retained. No unchangedworld/audio/159k/
093atlas/092icon/2013owner/SF1447bulk rerun. M6/M6F/M7/M9OPEN.

Next097: completeactualCGUILinkWindow Init/scale/layout5x10/bankcontrols/selection/
MsgProc andordinarydrawing/input;remainingGUIItemcopy/emptychildren/timer/lock/
cooldown/followers andliveSF/Animusowner callbacks. Macro35specialtextkind7 and
Vending27 mandatorybeforefullCItemBoard.Add thennormaltablebootstrap. Coordinate
wrapperkind/mixedcastmigration. Savedexploratorydecomp (notasm/pincomplete):
artifacts/client455-progress/linker-window096-exploration.json includeswindow
667770/667980/667C70/669410/669570/669190,Macro andcallbacks. Allprevious36boards/
Trunk/protocol/Tutorial/QBI/fourstage/Login/auth/game/M6F/M7/M9gaps mandatory.
Research research/client455-linker-owners.md. Progress,notblocked/notcomplete.

Исторический результат095 (runtime gate historical after096):

095 PARTIAL. Current gate inventory/client455-icon-links-checkpoint.json.
RF455IconLinks actualg_MainApp field beforem_items455/UI,source-owned map/vector,
notfullprivateUIManagerABI. Key=((itemID&0fffffff)<<28)|(index&0fffffff)|
(uint64(BYTEtype)<<60),bits56..59zero/toptypebits truncate. Register appends
duplicates;remove recomputesCURRENTkey,erasesFIRSTpointer,retains emptybucket.
No auto-reindex/destructor unregister;owners mustremove beforeidentitychange/
destruction. Missingkey removefalse;existingkey absentmember/emptybucket target
erase(end())UB explicitlyrefusedbylogic_error,trackedgap. Typed SetNum writes
selfWORD thenregisteredmembers(nullguard);SetUsable rawBYTE,no nullguard.
Unregisteredinitiator canupdate group;registeredcopy cannotupdate unregistered
original. Untypedlegacy setters remainlocal. Not a source-pointer/parentgraph;
actualregistrationcallers Linker6/Macro35,nothover.

22equalpinranges/1154asm/160binaryoperandkeyoracles. ActualMainApp registry tests
duplicates/order/maskedaliases/rawWORD/rawBYTE/remove/currentidentity/2unsafe
refusals/clearedlifetimes pass. ActualEDF-backed CGUIInventoryBoard original+
2explicitlyregisteredCGUIItemcopies/3GPUframesviewed;detachedcopy staysgray255
whileotherswhite2. Allpayloads released,registry cleared,Dmalloc balanced.
094metadata566/race520/16icons repeatedonnewfacade;3rawframes byte-equal to old
reviewed094,baseline artifacts/client455-progress/item-metadata094-before095.json.
094visualreport retained withbaselineprovenance;094runtimegate historical.
Hotbar7/storage3/account/newexactPEearly/Create1pass. PE SHA
e2741f24ead98890bbf59f6b70bb98f4b3388f999d0950c81c3d388123be4a77,
2109440bytes/x86/entry1530e0/WinMainb7730/afterCreateb789a,182/20/50TU,
0unresolved,engine082 unchanged. OrdinaryPE retains SetNum455c8d20/
SetUsable455c8d60/findc8db0;register/unregister unuseduntil realowners migrated.
IDA22f5e8a7savedclosed/list0;configuredprobe passed. No unchangedworld/audio/159k/
093atlas/092icon/2013owner/SF1447bulk rerun. M6/M6F/M7/M9remainOPEN.

Next096: actualLinker/MacroAdd-Remove clone/ownership/registration,coordinate
typedwrapperkind andmixedcallers. Then Vending27/fullCItemBoard.Add mandatory
notifications/cooldowns,normaltablebootstrap,fullLinker5x10/use/input/download.
Do not claim testedcopies asrealLinker UI or add successfulno-op providers.
DedicatedSF/Quest/fullGUIItemchildren/remainingboards/Trunk/protocol/Tutorial/
QBI/fourstage/Login/auth/game andpreviousgaps mandatory. Progress,notblocked/
notcomplete. Research research/client455-icon-links.md.

Исторический результат094 (runtime gate historical after095):

094 PARTIAL. Current gate inventory/client455-item-icon-metadata-checkpoint.json.
RF455BasicIconMetadata actualBasic0/2/3/4: Data72classification/76sprite,
NormalBYTE92quantity/others1,gradeData152 onlyequipmentkind1..10,requiredlevel
kind88-dependent. ReadbasicSF/Quest explicitlythrows; no inventedcommonvtbl.
rawMetadata accessor preserves existing table-owner extent,not just rowstride.
Racepredicate uses mask0ff00000 (already present inlegacy too,not a difference),
user0..4/5..10/default andBYTElevel-required255 rules. Source arrays/data untouched.
CGUIInventoryBoard.TakeInItemFields455 is called by ORDINARY existingTakeInItem
withactualAvatar race;normalMAPretains it atRVA c8ae0. Sharedcore sets typed0/
cell64,ID/sprite/quantity,stickyrequiredFF,autoSprite/display32,usable/trademark.
TakeInItem455(rawpayloadwrapper,caller race) reads metadata, rejectsquantity0/
wrongkind/null/slots20+, bindsgrade/index. InvalidID succeedswindow butGetItem
null detachesicon. Raw core quantity0 allowed;parent handoff rejects0,as455.
FullCItemBoard.Add is NOT connected;basicreader+handoff strippedfromnormalPE as
unused,while own-entry invokes sameproductionfacade. Do notforce-retain code
or mistake this actualwindow handoff for full inventory/event acceptance.

28equalranges/22functions/1138asm/15decodedreads/vtables;IDA4f540aafsavedclosed/
list0,configuredMCPprobe66tools/10functions/decomp/closepassed. 566realbasic
metadata/9Questrefusals+SFrefusal/520race-levelcases,16realpayload-ownerclones/
actualCObjectPack/actualCGUIInventoryBoard icons pass. ThreeGPUframes viewed:
real non-placeholder data,quantity255+grade11 update,clear. Inputstagedfiles
unchanged;copieddata memory edits restored;allpayload ownersfreed,Dmallocbaseline.
Initialprobe incorrectly assumedfirstsampleequipment;selectedequipment byreal
kind88. Sampleslaterimproved to nonzero/non-first rows for meaningfulimages.
NewPE85a909e356f40f713d2f785fca2a973c920034f15bf5926c2149ba8374de9685,
2108416bytes/x86/entry152d60/WinMainb7540/afterCreateb76aa,182/20/49TU,
0unresolved;engine082unchanged. Freshhotbar7/storage3/account/earlyKorea949/
localTCP/Miles/exactPECreate1passed;firstchanceeventsretained,nogameloopacceptance.
World/audio/159k/093atlas/092icon/2013owner/1447SFbulk unchanged,notrerun.
Runtime093gate historical;staticproofs retained. M6/M6F/M7/M9remainOPEN.

Next095: fullCItemBoard.Add/realownership and sharediconstate contracts. Target
479320 has mandatoryLinker6/Macro35/Vending27 notifications and cooldown/grade/
quantity propagation;sourcefactory35/27 notaccepted. Coordinate globalwrapper
IsEqualItemType (stilllegacytag) with mixedcallers,neverstatic_cast typedbase to
oldCSFItem/CBoardItem. Restore missingactualclientproviders ratherthan successful
no-ops. Then ordinarytablebootstrap,fullLinker5x10/use/input/download,dedicated
SF/Quest,GUIItemchildren/followers,remainingboards/Trunk/protocol/Tutorial/QBI/
fourstage/Login/auth/game. No serverwrites/inputEXEexecution/publication. Progress,
notblocked/notcomplete. Research research/client455-item-icon-metadata.md.

Исторический результат093 (runtime gate historical after094):

093 PARTIAL. Current gate inventory/client455-item-atlas-checkpoint.json.
Normal typedCGUIItem.SetSprite routesItem8/UnitParts19 bytype5,uses own
itemID/spriteID/type andpreservesdisplayedsize;emptyFFFFFFFF earlyreturn.
Actual targetcallbacks7B0620/7B0A40/7B05E0 implemented in production facade.
New other30 map;weaponext29..31->page30/consume13->34/otherext2>1023rebase to
page37(-1024)or39(-2048). Unknownouterkinddefaultpage0,unknownphysicalkind
fails. Geometry uses signed dimensions/width, unsignedIDdivision,WORDrowtruncate
BEFORE signedheightcompare;rawpartialwrites retained,manager failure resets
action/frame0 while retainingactualsprite. Missingunit leavesoutputunchanged.
Width0/negative/INTMIN/65535/65536 tested;no unsafe input EXE execution.

18equalpinranges/1001asm/2switchtables/47C6decodedbyte stores;realitem40pages/
unitparts7/inventory sprite roundtrip,880oraclecases/563failures/2actualWORDrow
wraps pass. FourGPUframes viewed:16syntheticmetadataautomaticicons32/64,
unitparts,stockDefaultfallback,emptyID. This is NOTrealpayloadmetadata binding.
Nine092frames reproducedbyte-equal to savedpreviousvisualbaseline; Dmalloc
load/unload/reloadbalanced. FullGUIItem61AF30children/timers/lock/commoninit and
privateABI/fulltargetUnit57lifecycle remainopen;known55filenamecache reused.
NewPE dbd71f6a2b6252f924ccffbb78b344d8f24006102e108ba64f051deab83d4bf1,
2108416bytes/x86/entry152d60/WinMainb7670/afterCreateb77da,182client/20kernels,
oneextra facadeTU,0unresolved. Engine082 unchanged. Freshowners2013/data575/
SF1447/hotbar7/storage3/account/earlyKorea949/localTCP/Miles/exactPECreate1 pass.
Firstchanceevents recorded,game loopnotaccepted. Worlds/audio/159k notrerun.
IDA4c6c7c2csavedclosed/list0. Configured MCPprobe66tools/10functions/decomp/close
passes withescalatedexecution after sandboxworkercode2;nativeconnectorworked,
noinstallation/config changes. Runtime092gate historical;staticrefs andviewed
framebaseline retained. M6/M6F/M7/M9OPEN;goalprogress/notblocked/notcomplete.

Next094: actual payload->icon metadata/getters and typedboard/hover/Linker owners,
then normal tablebootstrap order/profile andmixedconsumers. Do NOTmistake
syntheticSetItemID/SpriteID GPU samples for actual inventory integration. Full
GUIItemchildren/Questnames/Linker5x10/input/use/cooldown/download/oldbelt/36boards/
Trunk/itemprotocol/Tutorial/QBI/fourstage/Login/auth/game and priorgaps mandatory.
Research research/client455-item-atlas.md;all source edits underwork/canonical
trackedpatches;original/server inputs unchanged,localGitonly.

Исторический результат092 (runtimegate historical after093):

092 PARTIAL. Current gate inventory/client455-item-icon-checkpoint.json.
Ordinary CBoardObject.SetIcon/Refresh/SetIndex now update actual typed CGUIItem
index and grade-frame color. Correction: targetGUIItem1240 is a CGUIObject grade
BORDER, not caption/text; prior091 wording was a hypothesis, now disproved.
Typed core Draw:cell64, preservealpha white/666666 tint, targetinventory6/action3/
frame2(width<64)or3(width>=64), mainimage then selected WORDquantity. Quantity>1
types0/2/7 unclipped but0/7 clipped;zero onlytype0; hidden0/noimage1 skipsframe.
Separate real CSpriteMgr targetID0..54 cache uses existing localized/Common
paths and CSprite load/release; legacyIDs retained for oldcallers. Only6/8draw
accepted. Missing assets remain explicit;fullspriteUnit targetmanager57 notclaimed.
Selectedsource-owned metadata/frame is NOT completeprivateGUIItemABI. Base
CGUIObject.SetSize remainsnonvirtual;typedCGUIItem pointer paths only. CGUISFItem
and other old mixed Create/consumers are not thereby migrated. SetData copies
new selectedfields;fulltarget copy/update/shake/timers/overlays/hover notaccepted.

22equalpinranges/1740asm/RTTI/jumptable/EHwindows;256gradeoracle decodedfrom
binary MOV EAX immediates. RealCommoninventory4actions/33frames,item1/40 passed
roundtrip. IDAaa30c75csavedclosed/list0. Native256grades/120quantity/8signedwidth/
POINTgeometry/actualwrapperbind-clone-rebind-clear/copy pass. NineactualGPUframes
viewed at32/64sizes, tintalpha128, clipping, quantity65535, hidden/noimage;Dmalloc
load-unload-reload balanced. GPU usesexplicitSPRITE_INFO,NOTautomaticatlasfactory.
NewPE e540395b8f05fce56b9b7eec8e46ee1b555cbd18f9ad41fd692b54c74de45308,
2107392bytes/x86/entry152a30/WinMainb7630/afterCreateb779a;182client/20kernels,
oneextra facadeTU,0unresolved,engine082unchanged. Freshowners2013/data575/SF1447/
hotbar7/storage3/account and exactPEearlyKorea949/localTCP/Miles/Create1 pass.
Firstchanceevents retained;nogame loop acceptance. Worlds/audio/159k unchanged
suites notrerun. Old091runtimegate historical;its staticrefs/byteoracles retained.
See research/client455-item-icon.md. AllM6/M6F/M7/M9remainOPEN,percentageunknown.

Next093: actual spriteUnit/classification→atlas callbacks7B0570/7B0400 and typed
board/hover/Linker consumers;then normal data bootstrap order/profile,mixed
payload migration. FullGUI/Questnames/5x10/input/use/cooldowns/download/oldbelt/
36boards/Trunk/protocol/Tutorial/QBI/fourstage/Login/auth/game remainmandatory.
No server/original input writes. Goalprogress,notblocked/notcomplete.

Исторический результат091 (runtime gate historical after092):

091 PARTIAL. Previous ordinary gate:
inventory/client455-item-object-checkpoint.json. Commit090 was progress;
091 now moves actual ordinary classes to shared ownership, not only raw kernels.

CItemObject derives from real CResObject584, has RF455ManagedItem* at584 and
field588, size592. CBoardObject derives from it, size620: using BYTE592,
icon596,17 ctor-zeroed bytes600..616. Copy preserves padding593..595/617..619,
does not retain; Clone retains after copy. CItemObject destructor calls qualified
Clear before CRes destructor. Clear first invalidates object index, then uses
087 release with actual CMainApp manager; test primary-empty before dereferencing
retired payload. Setter calls virtual Clear→assign→retain→name. Board setter adds
serial/secondary ID; SetIndex updates shared serial. Base identity requires same
nonnull payload. Equal sizes do not prove target private CItem ABI: managed
payload is a source-typed API with its own polymorphic object/record storage.

RF455ClientItems (data/SF/manager) declared BEFORE other CMainApp game members,
so those destruct before manager/data. loadFiles really reads Item/NDItem/Quest/
Character/SF, verified with actual stagedfiles; NOT yet called by normal bootstrap.
Do not claim automatic gameplay loading or full game-global shutdown acceptance.
Four backends now compile into normal production facade (46 TUs total).
New facade TU needs _NEW_UI_, matching engine/client definitions,/Zc:forScope-
and SpriteMgr include. Initial117 then1 compile errors were port context issues,
fixed. Internal payload helper names array/byte renamed to avoid Windows/STD
collisions; algorithms unchanged. RF455ManagedItem now has virtual const name().

Legacy CBoardItem/CSFItem/Animus/UnitParts/Unit retain compatibility tags through
virtual getters, no extra base tag field. Clones retain after copy; Clear chains
new base. Their old embedded payloads/methods are NOT final455 runtime.
Binding a new payload to a mixed derived wrapper explicitly throws.
Typed nonnull icon/caption provider also throws: legacyGUIItem lacks target
index/inline caption. Unbound legacy icon setters still callable, but Clear now
detaches icon; mixed Create/callers require migration. Quest name still throws
for missing sentence provider; nine cases verify refusal plus owner cleanup.
Do not paper over any of these missing providers with success/no-op.

HotbarReference455 handles owned physical/SF/Animus before legacy RTTI path,
preserving unmasked OR. Full ordinary Linker Add/remove/view/input/cooldowns/
download and hover remain unported/legacy borrowed paths. Tests use actual
CObjectPack from a CLinkBoard container, not its incomplete Add/UI integration.

21equalpinranges/444actualasm/14bodies/EH windows;raw item-object091-reference/
session under artifacts/client455-progress. IDA157b5ed2 savedclosed/list0.
Two whole620byte constructor/copy oracles extend unchanged090 base oracle.
Actual CMainApp data manager + typed wrappers:1447SF +566other owners=2013
clones/alternating production pack Remove/dtor/last-owner erase pass. Seven
signedBYTE cases/primary-empty retired pointer/base-vs-board setter/independent
hotbar keys/mixed+icon refusal tested. Data575/76049rows/3locales/99XP and SF1447
probes pass on PRODUCTION facade, not a separately linked item.lib. All3 exit0.
Old087–089 separate-library runners are historical; don't rerun them as current
production evidence or claim their providers survived the canonical integration.

NewPE SHA7d7ff847b49d28a2d24a203d1a9b863a5ff273e10a82eda9d3d7e7c94ecb3bc0,
2104832bytes/x86/entry152070/WinMainB6FE0/afterCreateB714A,
182client/20kernel/46facade/0unresolved. Engine9caa283a… unchanged082.
Fresh normalconsumers/hotbar7packets/storage3runs/Avataraccount and exactPEearly
Korea949/localTCP/sound/D3D/Create1 pass. First-chance events recorded; no game
loop acceptance. Unchanged GPU/maps/audio/159k suites not rerun;090 visual
evidence historical for that link.090 runtimegate now historical after new
normal reports; its static base evidence/oracles retained.

Next092: real item icon/caption source owner, typed board/hover/Linker consumers;
then normal data bootstrap order/profile and mixed payload consumers. Finish
5x10GUI/input/use/cooldowns/download/oldbelt/Tutorial. All full resource/payload/
Quest/Gesture/Macro/36boards/Trunk/protocol/Tutorial/QBI/fourstage/Login/auth/game/
M6F/M7/M9 gaps mandatory. Server files/originals untouched. Goal remains active.

Предыдущий перенос090 (runtime gate historical):

090 PARTIAL/currentordinarygateinventory/client455-resource-object-checkpoint.json.
Обнаружена общаяобязательнаязависимость itemwrappers:legacyCObject48/CRes472,
target80/584. Теперь actualordinarybases80/584: name64 (globalMAX_NAME32 не
менятьдляпротокола),ctor clearsonlyfirst32namebytes/оставляетtail32;SetName
clear/copy64/nullpreserve;CObjectcopy сохраняетpadding5..7/копируетname64.
VirtualClear invalidatesindexonly. CRes addsconstructor timestamp244/state84@500,
removesunusedblinktimes8/reordersfields:flags116/animation140/scale240/created244/
interp248/material288/light356/alpha468/blink472/hide476/text480/receive484/
effects492/state500. Profileuses existingRF455_InitializeSecondaryState,
sourceCAnimation100helperunchanged. CRescopybase+rawresourcebytes80..583;
newownC++vtables,неcallabletargetaddresses. Fullresource methods/privateABI open.

Enable/Disable effectguard: (flags&0x21000)||!(flags&2),неoldflags&~2.
Enable additionally resetsreceipt whenserver-out10000;Disable doesnot. Existing
DeleteEffectIDactualprovider clearsbothIDs aftercallbacks. RenderName passes
name directly,obsolete32byte sprintfbufferremoved;fullmetrics stillunported.
Generatedcopiesonly via scripts/client455_resource_object_port.py+prepare.

23equalpinranges/765actualasm/14bodies/21decodedC6C7stores/7floatconstants/EH
windows pinned;rawres-object090-reference-complete/session underartifacts.
IDA65c60c5dsavedclosed/list0. Twofull584byteoracles/28namedoffsets/160flags
(20retain/140clear/48receiptreset)/actualtimeGetTime/name/null/baseClear/dtorpass.
Commonprobe liveMagiccacheempty:невыдаватьзаfullpopulatedFXacceptance.

NewordinaryPEdc6f2c6293c91cab28b8b4689f9261a8d3d82039162ab309944c26df1087034e,
2093568bytes/x86/base400000/entry1500e0/WinMainB5B40/afterCreateB5CAA,
182client/20kernel/42facade/0unresolved. Engine9caa283a… unchanged082.
Freshnormalconsumers/hotbar7actualpackets/storage3runs/Avataraccount passed.
Actor12/269ticks/185draws/148particle/6entity/9viewedGPU and3worlds/6viewedGPU/
reload/collision/memorybalancepassed. Firstworld35aad37f/world-bellato-001 failed
beforeload:oldrunner omitted requiredCharacter.sho;copy_character_shaders now
stagesverifiedinputs andall3passed,noadditionalproductionfix. NewexactPEearly
Korea949/localTCP/sound1/D3D/normalCreate1passed;firstchanceeventsrecorded,
normalgame loopnotreached. No159k/audio suitesrerun.

089sourcepayloads UNCHANGED butnative4runs regenerated againstnewdependency/
fullobjectset:575factories/99XP/3NDItem andSF1447pass. 086/088/089runtimegates
historical afternewnormal/reporthashes;staticreferencesvalid,current090gate
includesrenewed089native. Do notrunoldhardcoded086gates ascurrentacceptance.

Далее091: actualCItemObject/CBoardObject typedsource lifecycle/realgame-global
manager,board/hoverowners;связать087–089сordinarypath,thenLinker5x10/input/use/
cooldown/download/oldbelt/Tutorial. LegacyCBoardObjectstillmixedmodel,не620wrapper.
Cacheartifacts/client455-progress/res-object090-future-item-owners.json:
46AF20ctor/46AF70dtor/46AFE0Clear/46B010setter/46B1B0boardctor/46B4C0Clear/
46B570clone/46BC90setter. Somequeriesinterior→verifycanonicalrangesbeforeport.
SetItemvirtualClear→retain→name;derivedsettersetsindex/serverindex/iconrefresh;
dtorCItemObjectcallsitsClearthenCResdtor. Preserve087primarycacheguard/signedBYTE.
Allfullresource/payload/Queststrings/Gesture/Macro/36boards/Trunk/protocol/
Tutorial/QBI/fourstage/Login/auth/game/M6F/M7/M9 gapsmandatory. Serveruntouched.

Предыдущий source-runtime089 (currentregressionrenewed090):

089 PARTIAL_SOURCE_RUNTIME: client455_item_payloads.h/cpp даёт Item47/Quest12/
Character7 owners/readers и freshNormal0/Animus2/Unit3/UnitParts4/Quest5 payloads.
RF455SourceItemManager.createPayload selector1 делегируетrealSF088;прочие
selectors вне2..5 defaultNormal0 (неGesture). Primary concrete/087clone-release.
Wholebyteoracles76049items/3NDItemprofiles иQuest12/Character7;575selected
factory-clone-lifetimes/99AnimusXP boundaries проходят standalone/fullobject.
Та же новаяRF455ItemPayloads.lib проходит unchangedSF1447probe в обоих режимах;
4naturalexit0/buildwarnings0/MAPprovidersverified. Обычный игровой binding нет.

RootItem —48sections Htag/Ibytes/Ioffset10bytes: F100..F12D→0..45,F12F→46,
F130→47workstarts+47workcounts,F12E unmappedskip;next=offset+bytes+10.
InstalledTaiwan virtualslot160→82C490 returns1→segmented. Flatbranch — generated
fixture изactualtables,неотдельныйoriginal. NDnames skip44/45 безчтенияcount;
copymin(localcount,basecount)64bytes@row8,extras skip/shorttail unchanged.
Zh-twkind27=32vs31 корректноskip,ko/ru shortcounts НЕошибка как вSF.
Descriptions/dungeons:zh-tw68084/100,ko63821/100,ru52255/0и11185ignoredtail.
Questframe7=2895x424;F0000000..2→count-9..-7,F0000003..5→count-3..-1.
Characterframe6=648x95;AnimusXP scans81perBYTEtype. FreshClear data16null→
type255→actualnull;неplaceholder. Metadata можетчитать beyondstride только
внутриactualtableowner;внеегоexplicitout_of_range,неfailureparity.
Freshsizes200/136/192/100/116,dispatchopaquetoken/unwrittenbytespreserved.
Questname()explicitthrows:target468450→6057B0/605A70 sentenceexpansion ещёнет.

50equalpinranges/1796actualasm/19bodies,noncontiguousEH15bytewindows included.
Rawitem-payloads089-reference-complete/session.json underartifacts/client455-progress.
IDA877755f1savedclosed/list0. Gateinventory/client455-item-payloads-checkpoint.json.
088runtimegate historical:sharedSFheader changed,newlibSFregression принят089;
static088reference valid. Production086PE82625b3e…/normal-link/hotbargate current,
неизменённые GPU/startup/159k suites неповторялись. M6/M6F/M7/M9OPEN.

Далее090: realgame-globalmanager/CItemObject/CResObject lifecycle/typedboard-
hover owners,потом ordinaryLinker5x10/input/use/cooldown/download/oldbelt/Tutorial.
НеreinterpretcastlegacyCBoardObject (неCResObject) в455wrapper. Fullpayload
copy/mutation/network/UI,Gesture/Macro,Questlocalizedsentenceprovider/other
Characterconsumers/reloadduplicateoldowner/OOM/unwind/unsafe/privateABI ивсе
прежниеgaps обязательны. Процентвсегоклиента невычислен:реестр неполный.
Все вводыоригиналыimmutable,серверныефайлы untouched.

Предыдущая source-основа088 (runtimegate historical,regression обновлён089):

088 PARTIAL_SOURCE_RUNTIME: client455_skill_force_items.h/cpp — realSF160
factory selector1,5ownedtables иconcreteRF455SourceItemManager;087clone/release
теперь проверен на настоящихSFpayloads,неrecordinghost.1447rows/1447wrappers,
same.libstandalone/fullobject,wholelocalizedtablebyteoracles/alternating
origin-linkrelease/last-owner erase/duplicatefactoryrequests/guardfailurespassed.
Dispatchword остаётсяowner token,неcallabletargetvtbl/полныйprivateC++ABI.
Ordinarygame-global SF/Linkerowners ещёнеподключены;Production086/егоgate current.

TargetrootSkillForce.edf — именноDataTable/SkillForce.edf;5tables сmanager+48
до+96. Counts88/84/504/60/711,strides1100/1124/1124/1124/1124,1447rows.
Subtype1→table0,0→1,2→2,3→3,5→4. FreshSFtype0 serial/field8=ordinal;
1/5 bothORF0000000;2/3 serialORF0000000,field8raw,level1. GetDTIndex=firstDWORD
borrowedrow,неordinal. Clear fresh counters only;iconBoard108null.
Locale5FB670 ignores2ndheaderDWORD,writesname32@112/text512@524,наcountmismatch
returns0 сохраняяprefixwrites. Ko fails table4(640vs711),Ru table1(77vs84).
Zh-tw counts matchallfive. OriginalR3Engine.ini УЖЕ Language=Taiwan;mapping8/
zh-tw verified. Не менятьконфиг/оригиналы и не padlabels. Countmatchневлечёт
fullversion/localeproof. Ko-kr/SkillForce.edf другойlayout/counts,неfallback.

35equalpinranges/1224fullasm,noncontiguousEHtailinstructionwindows15bytes
тожеpinned (невыкидывать поheadsize!). Rawskill-force088-reference/session/followup
вartifacts/client455-progress;IDAcd8baa1asavedclosed/list0.
Gate inventory/client455-skill-force-items-checkpoint.json. New exactPEearlyTaiwan
startup passed CRT/WinMain/950/
6997NDLanguage/localTCP/sound1,стопдоD3D;SFgameownerэтимнезапущен.
OldGPU/Korea-startup/159k suites неповторялись;PE82625b3e…/normal-link unchanged.

Очередь088 поfreshfactories/Item/Questframing выполнена089 bounded;game-global/
CItemObject/CResObject/typedboard-hover/Linker/Tutorial ещёOPEN. Cachedfuturectors/
helpers вskill-force088-followup.json;передновымпортомпроверятьranges.
SFearlier4XP/mastery tables/liveicon/recreate/
reloadleakpointerlifetime/unsafeOOMunwind ивсепрежниеgapsOPEN. M6/M6F/M7/M9OPEN.

Предыдущая source-основа:

087 PARTIAL_SOURCE_FOUNDATION: scripts/native/client455_item_ownership.h/cpp
дают rawdata92/620 copy/clone/BYTEretain/drop/selectedrelease. Это records,
dispatchwords — opaque tokens,неcallabletargetvtables/полный C++ABI.
TargetCItem ctor45FC80 не пишет bytes22..85/padding13..15/86..87;copy405E70
сохраняет destinationpadding. Wrappercopy46B5E0 иparents сохраняют padding5..7,
593..595/617..619;resourcefields покаopaque. Targetwrapper inherits
CItemObject→CResObject→CObject,legacyCBoardObject толькоCObject:неreinterpretcast.

Release46B090 сначалаquery PRIMARYcache C0C020 (list+4,count+12);еслиempty,
неdrop инеnull wrapperpointer,дажеGesture. ИначеBYTE--wrap;MOVSXAL signed<=0
вызываетvirtualIsKind6,primary469960 илиgesture46A040/cacheC0BFF4;затемnull
pointer,дажеcachemiss. Clone46B570 alloc620/copy+retain толькоприallocation.
Семантикуglobalcacheempty не переименовывать вshutdownflag/обычныйshared_ptr.

24equalpinranges/579fullasm/8rawdecodedctorstores;raw item-ownership087-reference
и-session вartifacts/client455-progress,IDA65f54fa4savedclosed/list0. Sameexact
library standalone/fullobject probes exit0:3whole-recordoracle/12lifetimecases/
7BYTEboundaries. Hostrecording;actualderivedfactory/predicates/destructors и
ordinaryLinker binding OPEN. Fullprobe links same.lib through pragma;initial
combinedTU inlinedawayAPIs,checkpoint caught;onlyprobe packaging changed.
Gateclient455-item-ownership-checkpoint.json, research/client455-item-ownership.md.
Production086/normal-link/его hotbar gate currentunchanged;GPU/startup/159k
suites не повторялись. Далее088 realfactories/managers/CItemObject/CResObject/
typedboard-hover owners,затем5x10view/input/cooldown/download/oldbelt/Tutorial.
Cachedfactory469AD0/4697B0/469720 и дополнительные helpers сохранены в ignored
artifacts/client455-progress/item-ownership087-followup.json;передпортомновых
тел проверитьranges/pins,не считатьвсеcachedhelpers accepted087.
M6/M6F/M7/M9OPEN;087неordinaryruntimeacceptance.

Последний перенос в обычный клиент:

086 PARTIAL/currentgateclient455-hotbar-checkpoint.json. OrdinaryCLinkBoard
снимает5x10 keys из sourceobjects и отправляет delta group13/op17 через actual
networkowner/sendring/AES. Encodertags4/SFtype/3;Gesture5/Macro6 пока pureonly.
Wire2+4n,max202,fullDWORDcache/WORDwireindex;ORindex безмаски. Drag сorigin6
подавляет oldkey;кэш обновляется до send,включаяfailure. Statepacked activeOR
rawbankflags<<(7-bank),неboolnormalize. Windowmetadata Init0/flags1;realbank
widgets/events не перенесены. FrameMove unsignednow-last>5000,clockupdate после
вызова независимо отрезультата. Fullcooldown/deferredicons ещё не перенесены.

Native7actualpackets/storage3runs/account/exactPE/Create1 passed;hotbar probe
не запускает listener/workers/auth. SourceSF/Animus tables controlledfixture,
неfullDBloading.45equalpinranges/640fullasm;rawhotbar086-{reference,asm,session}
вartifacts/client455-progress. IDA811039d6 savedclosed/list0. CurrentPE
82625b3ef5c237900146f65531a701a3451d3dbec292a65eef2ed5ece83df6f8,
2091008bytes/entry14FD60/WinMainB57D0/afterCreateB593A;182client/20kernel/42facade,
0unresolved. Engine9caa283a…unchanged082/contractsreused. Oldactor/money/maps/audio
GPU/159k suites не повторялись.085/083 gates historical постарой normal-link.

TargetLinker500590 clones620bytewrapper/retainsunderlyingitem;oldsource borrowed
objects/EmptyAll и8-slotCGUIForceBeltWindow неэквивалентны. Очередь после086: общийitem/
wrapper ownership+5x10CGUILinkWindow, input/use/cooldown/download,oldbelt callers;
затемactualTutorial. OldMainGame.Create_Board/BeltList getter всёещёthrows;
36factoryclasses includingTrunk/fullitemprotocol/GUI/Tutorial/game ивсе прежние
gaps обязательны. M6/M6F/M7/M9OPEN;процентнеизмерен. research/client455-hotbar.md.

Предыдущий результат085 (исторический gate по normal-link):

085 PARTIAL/currentgateclient455-storage-checkpoint.json. Source canonical
storage IDs0Inv/1Equip/2Embellish/3Force/4Animus/5Trunk/6Linker;capacity56,
POS_NUM7/STORAGE_NUM6. Старый BELT=255 — INVALID migration marker,неwireID.
CBoardManager.Create больше не создаётCBeltBoard;17same-named target classes
занимают correct455 slots. _GetBeltBoard явноthrow logic_error до миграцииcaller.
ФизическийReturnItem guard4FEF50 (RVAFEF50) принимает0/1/5;real4FEF90callee.
Два legacytrade lookup helpers ограниченыInventory/Equip после удаленияbelt;
это не новаяtrade455реализация. GetBoard2aliases1;GetObject2неalias,какtarget.

ВАЖНО: oldMainGame.Create_Board иBeltListdownload ещё вызывают старыйgetter,
теперьявноотказывают. Ихнельзя считать working455 илиacceptedTutorial. 36target
classes,включаяTrunk5,отсутствуют. Packet/DBlayouts/hotbar/fullreturn effects/
trade/GUI/всеостальныеcommonproviders остаютсяOPEN;старыйпояс не заменятьForce.
Падениеcount18→17 — удалениеobsoleteкласса,непроцентрегресса/готовности.

Reference:10additionalequalpinranges/25actualfullasmguard,53vptrRTTI084revalidated.
Rawstorage085-reference/session.json вartifacts/client455-progress;selected
queuepseudocode only,queue не реализована. IDA64b119a2 savedclosed/list0.
Nativework/m9/a7723312/storage-001/002/003:exit0/identical17classes/18publiclookups,
256BYTEdomain,Force6x20/Animus1x10/Inventory5x20/Equip1x16 basepacks,retiredgetter
throws;полныеSF/UI/object insertion/network transferнеприняты. Перваяprobecompile
потребовалаmissingheaders;изменёнтолькоtestfixture,productionнеподгонялся.

CurrentPE SHA89924a1c95d2b3f2e0a09f2e19cc223e00f1454bac866d79cf19ae3a8d00a031,
2084864bytes/entry14F490/182client-20kernel-41facade/0unresolved. Freshconsumer
ANI/BBX,account/Avatarstage/logintransform иexactPEearlyTCP/sound/D3D/Create1.
WinMainB53B0/afterCreateB551A. Firstchanceexceptionsrecorded,неfailureparity.
Engine9caa283a… unchanged082/startupcontracts reused. Actor/money/maps/audioGPU
и159k suites не повторялись. Gates083/084 historical for old normal link.
Research/client455-storage.md и checkpoint хранятsourcehashes/retiredcallerlist.

Очередь после085: настоящий455Linker/hotbar и миграцияoldbeltconsumers,commonUI/board/
Avatar owners;затемQBI/follow/localhandlers/actualTutoriallifecycle/fourstage/Login.
Trunk/остальные36factoryclasses иfullitemprotocol обязательныM9,неwaived.
M6/M6F/M7/M9OPEN;процентнеизмерен. Не объявлять fullstorage восстановленным.

Предыдущий результат:

084 — AUDIT_OPEN, runtime083 не менялся. Настоящий Tutorial Create5586D0
вызывает общий UI5467D0/boards5477C0/Avatar5488F0. Точное подключение требует
другой общей фабрики:455 Create4FB920 allocates53 objects/limit56,source18/limit19.
GetBoard4FD860 public2→equipment1;physical2/23/30 в этомCreate не назначены.
17same-named source registry classes не дают parity.36 target names отсутствуют
в текущей фабрике, не утверждать отсутствие всех их исходников/поведения.

КРИТИЧНО: Force455id3/source4;Animus455id4/source5. Старый sourceid3 — CBeltBoard,
нет same-named target factory class. Targetslot5 — CTrunkBoard,slot19 CJournalBoard.
Не передавать QBI board3 напрямую в oldGetBoard. Не менять только enumчисла:
появится collision сbelt; перенести storage/protocol consumers/factory вместе.
CQuestBriefingBoard ctor49B550 registry20 и dedicatedCTutorialBoard4A5AE0 —
разные RTTI/vptr/lifecycle, хотя InitWindow обоих38. QBI47 — отдельное число.
CommonAvatar требует nameplate/charinfo/equipment/4gauge consumers, не толькоmoney.

92equalpinranges;1514actual fullasm4funcs (1388/27/44/55);53primary vptr stores
decoded/RTTIconfirmedbothpins. Все выбранные pseudocodeполные;rawtutorial084-*.json
и reusedtutorial083-initial.json вartifacts/client455-progress. IDA14d8cac3
savedclosed/list0. Inventoryclient455-tutorial-integration.json хранит все53IDs,
class/ctorRVA/allocation/vptr/RTTI/sha,source comparisons и пять mandatoryhost
interfaces. Research/client455-tutorial-integration.md описывает границы.

Native actualsource factory probe: embeddedrealCMainApp.CNetworkMgr Create до
boards;8stagedruns exit0/identical18objects/alias2/rangeguard. ProbePE
1e7484980582af6a430f820a263fca529a8cc09d71312a2ee8f5b40df8495e22.
Source sizeofMainGame65984/Avatar19280/Tutorialsemantic32/briefing2736 — неABIparity.
Ошибки fixture:безnetworkowner getterECX0;затем localnetwork stackoverflow.
Обе исправлены вprobe;не считать багом production startup. Старые GPU/159k suites
не повторялись;source083 normalPE иengine082 unchanged,oldmoneygatecurrent.

Очередь после084: реальная migration storage/board contracts/factory, общие UI/Avatar
owners/gauges/nameplate/processor dependencies;затем concreteQBI/follow/handlers
и actualTutorial lifecycle/fourstage/Login. Не заменять host recordings/IDonly.
Полный реестр остальных gameplay/GUI/Character/audio/FX/IME/numeric gaps обязателен;
M6/M6F/M7/M9OPEN,процентнеизмерен. Эта итерация дала новое доказательство разрывов,
не новый работающий Tutorial и не принятую подсистему.

Предыдущий результат:

083: actual Avatar → inventory currency fields/API теперь signed64; значения
выше32бит не теряются. Форматирование группами3 и wider-title x−10−amountWidth,
rowY перенесены. Для negative target использует FILD→double→fabs→truncation:
сохранены rounding выше2^53 и INT64_MIN double-minus при masked invalid.
Форматтер inline в естественно удержанном RF455_GetMoneyText; force-retain нет.
Полные currency network/trade/shop/exchange всё ещё содержат DWORD/float gaps.

21 диапазон обоих pins равен;382 actual asm/10 money functions. Raw money083/
tutorial083 в artifacts/client455-progress. IDA b55212f6 saved/closed/list0.
Korea/Russia native work/m9/5b4651a6/money-{ko-kr,ru-ru}-001:92cases each,
4roundingmodes,3GPUframes each,3416/3796pixels;6кропов просмотрены. Freshaccount
с actual stage/skip/Create gate/login transform PASS, без authentication.
Freshactor work/m9/05a1955b/rvp-actor-001:269ticks/185draws/148particle/6entity,
9distinctpose ticks/459parts,0warnings,Dmalloc270592balanced;9кадров просмотрены.
Полный inventory Init/other controls и reference-runtime pixel parity не приняты.

Current PE SHA8b51618359be41530f1558a47440111196c93b441d2a597edc5b1233ffa2f6ec,
2095104bytes/entryRVA151490/182client-20kernel-41facade/0unresolved. Freshearly
TCP/sound и exactPE/D3D/existingCreate1;WinMainB73B0,afterCreateB751A.
Engine9caa283a6bf8a2fa1c9a05251b6cad451296bb03bda8a1860c22a872e88fe769
не менялся;startup contracts082 reuse. Три карты/Miles082 не повторялись,
159k suites тоже. Gateclient455-money-checkpoint.json PARTIAL/current;
old082gatehistorical. Research/client455-money.md содержит пределы доказательств.

Очередь после083: настоящий CGP_Tutorial со shared UI/board/Avatar preparation5488F0
(Create5586D0 не вызывает statshelper5588C0), concrete QBI/follow/localhandlers/
feedback/frame/input/Destroy иfourstage/Login. Нового полного владельца083нет.
CORRECTION: CTutorialBoard InitWindow ID38. «47» означает QBI selectors, не
подтверждённый board-manager slot. Прежний shorthand board47 не использовать.
Остальные RVP/advancedFX/globalChef/fullMiles/GUI/Character/IME/game gaps остаются.
Общий процент не измерен; реестр неполный, M0–M5 не процент функционала455.
M6/M6F/M7/M9 OPEN.

Предыдущий результат:

082: ordinaryRVP immediate audio иtimer_rate подключены креальномуMiles/clock.
20-byteIMrecords,128+32growth,occupiedнеочищаетсяindividualrelease;sourceoverlay
r3sound.cpp используетactualexistingdigitaldriver. MP3 musicgate/rawloopflag/
metadata mismatch/globalvolumeonlyonPlay/fixedpan0.5 verified. Ambientиспользует
предыдущуюматрицудоflag16;start/update/stoplatch работаетприpaused/gatedtracks.
WaveпредпочитаетCAMdummy,actorfallbackисключаетпоследнего;Prepareдвойной. Timer11
camera-dependent:flag4 consumes/skips;ExtractдоPlayвидитпредыдущийframe.

В44stockRVP:0ambient/210events/2existingWAV. TARGET8BEEC0 non-MP3branch НЕсоздаёт
handle,такчтоRVPWAVчерез8BF070непроигрывается. Не заменять“исправленным”WAVloader;
это не утверждениеобобычномPlayWave/всёмзвукеигры. RealMP3fixtureдляпроверкиbackend
изSnd. Nativework/m9/59e544a3/rvp-audio-001:exit0/warn0/decoder165ms,129boundary,
2ambientstarts/2stops/4events,actualtimeScale.5,Dmalloc785169balance. Никакого
fakeaudiosink;PCMoutputнеписался,fullaudibleparityнеутверждать.

IDA f1d662d0savedclosed/list0;18equalranges/1665actualasm/770Createpseudolines.
CORRECTION081:8D6900 — cache destructor,8D6870 ctor;Create8D69E0increment8D6C57.
Referencefact/researchtable/registrylabelисправлены. Runtime lifetimeнеизменён.
Engine9caa283a6bf8a2fa1c9a05251b6cad451296bb03bda8a1860c22a872e88fe769,
67objects/12overlays/baseline033preserved. PE7489e8c7cc27765d58ff43a6736179ef682ac2fbea72606b65de8981df1c2552,
entry1512B0/2094592bytes/182-20-40TU/0unresolved;freshstartup/contracts/exactCreate1.
Freshactor269ticks/185draws/148particle/6entity;3maps364/330/262ticks,15GPUviews.
Old081/080gateshistorical;currentgateclient455-rvp-audio-checkpoint.json PARTIAL.

Очередь после082 — actualCGP_Tutorial lifecycle/frame/input/Avatar/QBI/follow/localhandlers/
feedback/CTutorialBoard иfourstage/Login. ТриTutorialRVP используют уже проверенныеcamera/
fade;неоткладыватьинтеграциюрадиunusedmagic/trace. Magic/throw/collision/shadow/trace/
screen,advancedFX/globalChef/materiallight,fullMilesinit/PlayWave/streaming/audio
failure иFP/scanner/fullgame остаютсяобязательнымиM6/M9,приоритетнеотмена.
Подробности research/client455-rvp-audio.md. M6/M6F/M7/M9 OPEN.

Предыдущий результат:

081: настоящий отдельный RVP particle/entity DrawEffectMat и sharedFX
Create/refcount/deferred Release подключены к обычному клиенту. EFF-кэш отдельно
от прочих владельцев;17ChefRPK разрешают283/300particle и61/64entity definitions,
все5RVP294–298 доступны. Cache lazy-load/clones6/cycle%6, Loop до публикации
rotation/createpos; falseLoop завершает весь model pass. Entity inverseYZ и
scroll timer сохраняются. Первый Release1->0 удерживает cache; следующий0
удаляет даже без level. Полные advancedFX/численная эквивалентность ещё OPEN.

Owned CParticle1148->1296/CEntity208->212; ctor1296byte oracle PASS.
Реальная регрессия Cora обнаружила heap corruption0xc0000374 при LoadLevel:
отдельный weather helper выделял старые размеры. Исправлено /FI particle455.h
только для него; actual old/new operator-new args1148/208->1296/212 подтверждены
по RVA E69BF/E6AC2 в own probe. Final3maps passed364/330/262ticks,0warnings и
Dmallocbalance. Не повторять ошибку: 58engine TU плюс weather используют owned
декларации; прочие8independent helpers не получают legacy camera namespace.

StockneutralAS1:269ticks до конца/12actors/4models/185draws/148particle draws,
one loadedrecipe. Отдельный actualENTITY1:6draws/50pixels. Старый animation
regression9distinctticks/459parts сохраняется.15GPUframes просмотрены; мелкие
изображения/счётчик particle draws не доказывают isolatedparticle/finepixel parity.
Final actor run work/m9/a81c4cb8/rvp-actor-001, exit0/warn0/Dmalloc270592balance.
Engine14af5e53fd4f639d5afa42e81d38ccb041bd14706d55bfa1b1c4c51763bd5c22,
67objects/11overlays/baseline033preserved. PE0165bf169fb462a9111cd93201963d97f8a9d0e18ea8cdd9f0c600503c34440f,
entry151000/2089984bytes/182-20-39TU/0unresolved;freshstartup/entry/contracts/
exactCreate1passed. IDA2710bd78savedclosed/list0;18equalranges/2960actualasm.
Gate inventory/client455-rvp-effects-checkpoint.json PARTIAL, старые gates historical.

Открыты advancedtrace/curve/light/distort/azirang/combine/special kernels,
полныйCEntity/particle455math/render,process-ownedChef group/context/lifetime,
dense-cache/failure/constructorunwind,Render8CE5D0material/lightreset и все прежние
разрывы. Source adapter explicit-refuses selectedadvancedSPT; не выдавать legacy
basic за полный455. Далее082 — ambient/event audio/Miles contracts и другие
RVP providers, затем actualTutorial/Avatar/QBI/follow/localhandlers/fourstage/Login.
Большие неизменённые159k suites не повторялись. На запрос общей оценки не давать
выдуманный процент: M0–M5 закрыты, M6 частичный; полного входа/мира/игры ещё нет.
M6/M6F/M7/M9 OPEN. Подробности research/client455-rvp-effects.md.

Предыдущий результат:

080: обычный RVP вызывает восстановленные загрузку Character, выбор ANI,
dummy×scale, culling, сохранение/восстановление отдельных поз, material/EFF,
настоящую отрисовку модели и transparency. Новые source APIs находятся в
client455_normal_rvp.cpp: bone registry4264, BODY owned managers; регистрация
сохраняет дубликаты, поиск возвращает первый exact match. Bounds fallback —
реальные mesh bounds с Y/Z swap. Bone frame публикуется перед wrap; actor frame
сбрасывается160 отдельно. Counts2400, palette slots2680/stride256/max70parts;
count>4 — явный отказ вне принятого домена. SetFrustumNormalPlane добавлен после
automatic camera. Fade setters связаны с tracks, но8D4340 имеет0xrefs и НЕ
вызывается обычным455 Frame/Render. Предыдущая заметка о Render fade tick ошибочна.

IDA f9d34033 saved/closed;16ranges equalpins/1051actualfullasm. Raw080initial/
extra/flow и reference audit сохранены. Stock neutralAS1 имеет12actors/4models,
VALID2-byte emptyBN; нельзя придумывать отсутствующие animation targets.
Stock48ticks/70poses/70draws/391pixels. Controlled2actors: pinned real draw model,
51meshes/56bones/max4320,actualDummy01/reset75;9distinctticks/459restoredparts/
14isolatedpixels. Малые изображения не доказывают fine pixel parity.
Final probe work/m9/c224c1d5/rvp-actor-001:exit0/warn0/Dmalloc270592 beforeafter,
flag16/outerrenderer restored.5actor+6camera frames reviewed. Fresh RVP3maps:
10/9/8selections,364/330/262ticks; exact new PE/Create1 и contracts прошли.
PEa03ae596d5942d800d1fdce350330791226d59cfde67f17a404b0a57d0c51ddb,
entry150DC0,size2082304,182/20/38TU/0unresolved; engine079 unchanged.
Firstchance40080201/e06d recorded, полная failure parity открыта.

Sandbox native GPU InitR3Engine зависает до сцены;2timeouts сохранены. Такой же
probe вне sandbox работает. MSBuild FileTracker также требует escalation.
Не перезапускать живой процесс по timeout наблюдения; здесь subprocess timeout
подтвердил его завершение перед следующими диагностическими запусками.
Loaded actor scenes показывают explicit limitation: отдельный particle/entity
pass/sharedFX lifetime ещё OPEN. Magic/collision/shadow/ambientwav/trace/screen/
timer-rate остаются Create refusals. Gate080 PARTIAL; older079/GUI/kernel
reports historical, неизменённые широкие suites не повторялись.
Далее081 — real particle/entity draw и sharedFX Create/Release/deferred lifetime,
затем audio/restRVP, actualTutorial/Avatar/QBI/follow/fourstage/Login/game.
M6/M6F/M7/M9 OPEN. Подробности research/client455-rvp-actor.md.

Предыдущий результат:

079: ordinary RVP camera/timeline теперь НЕ compiled stub. Production CLevel
вызывает новые entry wrappers→client455_rvp_runtime.cpp вnormalfacade. 3worlds
27camera events/26fade-in/29fade-out=82commands; ticks364/330/262,0warnings,
exit0/Dmalloc270592 balance. Floatclock pause/flag16/finish/camera-only/actor
explicitrefusal/reload/nestedrenderer restored passed. Intro realRVPassert,
26cuts/357-325-258ticks и29GPU; display8/GPU6,FSE18,46reviewedframes total.
ВАЖНО: исправлены неверные подписи078:8D5510=Render(call8E7C40),8D8340=Release
(call8E7730). Raw ranges быливерны. New20ranges equalpins,fullasm531Frame+23Start+
14SetNowFloat+114Release. IDA6a789f6fsavedclosed. Raw rvp-runtime079.json/*ranges.
Owned anicamera455.h addsfloat SetNowFrame; fieldsunchanged. /FI only58legacy
engineTU +normal/facade/probes, НЕ9independentkernels (less collision). 67objects/
9overlays/base033preserved. Floatsetter EXACT now-seconds-playStart/30;double-start
offset preserved,notcorrected. Pausemarksplayfalse;resumeStartFALSE. Releasekeeps
loaded/play/pause scalars. FailedCAM-only ownerdetaches safely:failuregapexplicit.
ChInterface secondowner real;ownfacade restores previousactive renderer onnested
destroy;arbitraryout-of-order lifecycle remainsOPEN. RealSHOinputs nowcopied.
RVPno-camera resetsFOV/FSE duringLevel.FrameMove,changesintroGPU;noinventedflag16
tohideinteraction. OrdinaryTutorialowner/order stillOPEN;stage/QBI/followrecordings.
PE83c1793bc8a6b2bb9e1fde2b42b986132f12c077ecaa4f42f75ad0c41037c117,
entry150b20/2071552bytes/182-20-36TU/0unresolved/exactCreate1/freshcontracts.
Engined85c86784516872f8818c92d556bdf63a9dffaf6da559499cb3b3fddd772c347.
080: actualRVP actors/Character/animations/effects/ambient+eventaudio/swordtrace/
screen/timerrate providers,currentlyexplicitCreate refusal. FullCreate/Release
effectcache/deferredparticles andRender8CE5D0reset2caches stillOPEN;pausedautoCAM
undefinedmatrix refused. Quake/blurcodeported,butRVPspecificscenario nottested;
stocktests camera/fadeonly. Scanner078/numericunsafe+allpriorgaps remainOPEN.
ThenrealCGP_Tutorial/Avatar/QBI/follow/localhandlers/fourstage/Login jointly.
Latestgate checkpoint_client455_rvp_runtime.py;details research/client455-rvp-runtime.md.
Oldgateshistorical;bigunchangedsuites notrerun. AllM6/M6F/M7/M9OPEN.

Предыдущий результат:

078: новая RVP load-model library, НЕ ordinary player. 15ranges equalpins,
Create770lines in644+126 pages, fullasm1722 instructions in12pages +curve85.
Raw artifacts/client455-progress/rvp078-paged.json. Большой одиночный disasm
заявлял1722, но реально вернул10строк; отвергнут/заменён полными страницами.
IDAa265e239savedclosed. client455_rvp.h/.cpp: objects/properties/prepare/track,
12kinds/floatbits/order/flags/totalframe, cursor interpolation4D4D80. Все44real
RVP=615actor-records/1569commands; native+Python namedfields match;2fixtures
all12/throw/scanner/malformed/interpolation passed. Latestwork/m9/9cf0f09d/rvp-001.
77 unique resource refs,34missing exactpath. Не считать
их игровым блокером безпроверкиtargetfailure. PATROL_B.* есть подChef,неподставлять
автоматически. Tutorial RVP Bellato29/Cora28/Acc25,actors0 у всех трёх.
RTMrecords20600,tracks56(kind48/frame52). Target fscanf%s не пропускает comments;
unknown/underscore tokens ignored individually; DOS EOF1a; prefixatoi; color/2.
Throw dummy-vs-actor determines extra attachment token; needs camera name context.
IR symbol bindings/resource handles/effect/audio sideeffects ещё не восстановлены;
independent-if keyword-argument fallthrough/numericunsafe domains notcertified.
Ordinary RF_Online.bin/engine/source hashes остаются077; новая library только
в ownprobe. BigGUI/GPU не повторялись, Create1 reused077,не fresh078.
079: actual RVP camera/dummy bindings +Character/effects/audio/resource failures,
Create/Release/Prepare/Start/Pause/Extract/FrameMove/Render, then CGP_Tutorial/
Avatar/QBI/follow/fourstage. Flag16 gate FrameMove требует jointintro integration:
не включать legacyplayer вслепую поверх отдельной probe camera. Allgaps/M9OPEN.
Details research/client455-rvp.md, checkpoint_client455_rvp.py.

Предыдущий результат:

077: movie-state/display/defaultFOV восстановлены. 8D4C30 — положительные
RTMovie flags wide1/logo2/no-camera4, не общий camera-control. Полный request
11641C4 отдельно; getter читает internal11641B4, setter сохраняет верхние биты.
Raw Add/Remove не меняют wide/logo/projection. DrawFadeScreen рисует полосы
до fade-zero return; logo после полос. Default/current FOV отдельные, init и
MainApp.LoadData=0.6; SetDefaultFov читает default, не current animated FOV.
Clear455 не меняет wide viewport. Derived engine67TU/9overlays, baseline033
сохранён; library18086e42c69b69913c289dffc33c332055f5c4a720533aac63153bb344604125.
13ranges/4fullasm equalpins, IDA70b16df7closed/listempty. Flags8/GPU6,
intro3worlds26cameras/357-325-258ticks/Dmalloc270592, fullscreen18, reviewed40
passed. CameraHost movie flags реальные; stage/QBI/follow остаются recordings.
PEb377d2ac419ff52f5ad61ca22d78231fb90e64aa822dd3206958bc6dee69c082,
entry1508a0/2043904bytes/182-20-34TU/0unresolved/exactCreate1/freshcontracts.
ВАЖНО: RTMOVIE player compiled OUT. Собственный RTMovieFrameMove RVAcefe0,
bytes558bec5dc3… = empty body. StateAPI восстановлен вне featureguard, но
проигрыватель НЕ восстановлен. Bellato .rvp [Object] существует. Следующий078:
настоящий RVP track/actor/audio и CGP_Tutorial owner/Avatar/QBI/follow/fourstage;
не включать слепо старый define и не выдавать callbacks за игровых providers.
Direct InitR3D3D fixture stateScreenY500 vs viewport480: проверка явно задаёт
640×480, wrapper не исправлен. %fov command7E3B10 unported. Legacy0.7 inverted
RTMovie request API отдельно от positive455, его callers ещё не сертифицированы.
Все прежние gaps/M6/M6F/M7/M9 OPEN. Детали research/client455-movie-state.md;
checkpoint_client455_movie_state.py. Старые gates исторические, большие
неизменённые suites не повторялись. Число проверок не процент полноты.

Предыдущий результат:

076: restoredordinaryFullscreen motion branch (existingenginefunction,notnew
replacementrenderer). stFullScreenEffectState==target1163FB0,real==FB4,old==FB8;
stMain==1163FE8,stBlur==1163FC0. 8CED70SetState copiesDWORD/resetsoldonlyif0.
8CE9D0densityrawfloat/defaultBF7850=.25;Tutorial .15/.25 nowrealbackendcallbacks.
IMPORTANT8CE9F0motion:modechange mainopaque→CLEAR CURRENTBLUR;eachframe mainalpha
trunc(density*255)→CLEAR CURRENTBLUR→mainopaque. Preservecounterintuitivefinalpass;
doNOTimplementusualtemporalaccumulation. AsmECXFC0 onClear8DA470 confirmsowner.
11ranges/defaultequalpins,4fullasm;rawfullscreen076.json includesinit/end/Begin
asm plusengine/Avatar5488F0/5588C0decomp. IDAf1ac7cc2savedclosed.
Newseventhengineoverlayr3d3d8.cpp: motion.inc,densityAPI,Beginactualreturn,
stTexSize512independentoldlowvidmem. Other455targets/water/bloom/shadow/reset
stillunaccepted;doNOTcallfullInit/graphicscomplete. Base033unchanged,67TU/7overlays,
lib2df1e50eafb559452c4c610815e3c9534cc6eb0d1f5186e0c876cd7ab3576592.
GPU18patternframes(5viewed) passedrealBegin/FSE/End,default/.0/.15/.25/1,fullmode
80000005,red→blue→green nohistory,UI/actualtarget/depth/viewport/Zrestored,
vidmem0/2actual512targets,Release/Beginfalse/Init/success. Numericdrawonlyfinite0..1.
IntroHostmode/densitycallactualbasebackend;cameraControls/stage/QBI/followstill
recordingfixtures. Realintro3maps9/9/8cuts and357/325/258ticks,343/310/244matrices,
skip/reload/counters/Dmalloc270592beforeafter,warn0/exit0;29newviewsreviewed.
PE4553f4016e40d2803bee9a91661961206ef00b59f2ac395c564dcd311dc6f204,entry150860,
2043904bytes,182client20kernel34facade/0unresolved/exactCreate1,freshstartupcontracts.
Runtimechanged so075timestampreuseinapplicable;oldgateshistorical/current076gate
PARTIAL. 40080201unknown. FullStage/QBI/cameraControls/postprocess/M6F/M7/M9OPEN.
Next077 remaining8D4C30consumers andrealCGP_Tutorialowner lifecycle/input/board/
Avatar/localfeedback/fourstagejointintegration. 5488F0normalAvatarCreate differs
from5588C0Tutorialstats99/inventoryhandling;doNOTsubstituteoneforother. Legacy2->3
bridge remains untilactualTutorial2/Main3/Logintransitions. Noopprovidersforbidden.
Details research/client455-fullscreen-effect.md.

075: Tutorial intro branch5590B0 andLoad5594D0 sequence source restored.
RF455TutorialIntro +realRF455TutorialIntroCameraHost (CAniCamera/R3SetCameraMatrix/
fade) normalfacadecompiled butordinaryfactoryunused;NO force-retention/fullstage
claim. Stage/QBI/follow/newenginecontrol callbacks mandatory abstract;probe
explicitrecordings,notproductionproviders. RealAvatar onlyrace/stage,nofullactor.
15ranges/3tablesequalpins,4fullasm,rawintro075.json;IDAb92074d1savedclosed.
Tables generatedfrompins+realCAMcounts9/9/8. Labelunused;ordinalselect matters.
signed32(end-70) threshold,pendingonce,waitIsFading(notIsFadeOut),fadeout2/in3;
activeordinalcount foronetick thenfinish. SkipatendsetsFFFF/deferredfinish.
Loadretainscounters;onlyInitresets. Endout0/in5/unblock/screen/mouse/script/clear/
engine/follow orderchecked. Three actualworld/camera/nativeprocesses exit0/warn0,
29viewedframes(26cuts+3initial),357/325/258ticks drivenR3SetTime/.25loop (nofullwait).
343/310/244matrixapplications;Dmalloc270592beforeafterall. Notpixel455parity or
fullfaderenderer/cameraMatrix/COM/GPU/heapproof. Resources workcopies unchanged.
Firstfailure blankGPU:cameraTUcompiledwithoutRF_CLIENT_455_WEATHER;fixedperfile
ENGINE_DEFINITIONS matchingrealengine. Requiredbygate;donotgloballyalterfacades.
PE516664365726f782f256c87337ba0d14f349ee2e7556fa48205a53619220a44c,entry150790/
2043392bytes/182client20kernel34facade/0unresolved/exactCreate1. Runtimeequal074
aftertwoDWORDtimestamps304/1874448mask;unchangedGUI/kernelnotrerun/historical.
40080201unknown;newgatePARTIAL. FullCGP_Tutorial/Avatar/QBI/newenginecontrols/
factory/M6/M6F/M7/M9 OPEN. Next076 realstageowner withworld+intro+boardproviders,
newengineconsumers8CED70/8CE9D0/8D4C30,thenfourstage/nextDWORD jointly. Legacy2->3
bridge remainsuntilactualTutorial2/Main3/Logintransitions;nevercarryitontoTutorial.
FullILevel/Empty/INS/Character/render/gameplay/auth/IME/lifecycle/failuresgapsstay.
Details research/client455-tutorial-intro.md.

074: realBSP worlds loaded/rendered throughordinaryCLand. ExistingBSP39/EBP20
geometry loaderworked;no rewrite. Newland_load.inc deletesoldlevel/newCLevel/
globalgLevel/camera.Create;indexedload usesit. .ins explicitFALSE/missingprovider.
Derivedengine6thoverlaylevel.cpp:destructorReleaseLevel beforeSky/BSPdelete.
InitialCreate remainslegacyCLevel,fullILevel/Empty/INS NOTported. Base033preserved.
10ranges/vtableprefix48 equalpins,6completeasm;IDA60286d36savedclosed. Rawworld074
inartifacts/client455-progress includesfullLoad pages/owner/release/camera.
Bellato98020verts/85661faces/5455leaf/666mats/1187entities;Cora108443/126980/
8649/477/147;Acc102817/60866/4345/912/0. IndependentMapFilecounts match.
Realspawncollision true/heights277.230469/491.476562/-296.876953,leaf1597/4902/3733.
3load→frame→GPU→reload→frame→GPU→Destroy processesexit0,warnings0;6viewedframes.
Dmallocbefore=after270592;loaded=reloaded10583464/14343055/9627794. NotallCOM/heap
lifetimes orfullphysicsproof. Stage maps/camera0views only,notfullintro/pixel455.
Inputs actualcopieswork/world455-inputs;runhardlinksONLYworkcopies,notoriginals;
hashesunchangedafter. Eachrun .map copiedimmutable. Fixture fixes:Windowspaths,
relativeRPKprefix,CLandheap(stackoverflow0xC00000FD),notgeometrysubstitutions.
PEfd8b038dcbc0890caf4b728c487dd15448dbcb551a6ed38a804ba7002c8b5c21,entry150790,
2043392bytes/182client20kernel32facade/0unresolved/exactCreate1. Engine67TU/6overlays
c00d9d4da762dbf226bff5a8110034026159758b41738c4435c30438aa79568c. Prep4E7428C9…
idempotent. Freshstartupcontracts/account/Avatar/MainApp/KoRuWindowPASS;otherold
GUI/kernelreports historical. 40080201unknown. NewworldgatePARTIAL;M6/M6F/M7/M9OPEN.
Next075 actualCGP_Tutorial Load/Create/cameraintrosegments/frame/input +realAvatar/
localhandlers/board47QBI/fourstage jointly,using provenBSPbackend;don'tre-auditall
mapcontainers. FullILevel/Empty/INS/indexedextras/alpha/effects/shaders/lighting/
audio/deviceReset/Avatar/gameplay/auth/IME/failuresgaps remainmandatory.
Details research/client455-world.md.

Участок073: CAvatar получил source stageBYTE/skipDWORD default0. Targetfields
20165/20168;set/get безнормализации,requested2->3ifskip. Real predicate вcavatar.obj
используетсяaccount342. MainApp GameMainLoop теперьвозвращает0приCreatefailure;
послеуспехапишетAvatarstage. Factory покаlegacy3/modulo:bridgelegacyMain2->455
Main3 обязателен,удалитьсовместноsfourstage. Stage2login skipsmask regardlessskip;
SendNetMessage localbranch stage2+skip0 теперьactual:knownignoredincl21TRUE/noRing,
1/17directtransport сохраняетcodec. Handler4:1/19/31,all5,7:2/5/9/11/13,
13:2/21/26,17:4 покаEXPLICITFALSE/log,НЕaccepted. Group5unknownможетfeedback,
необобщатьignored. Реальныйheartbeatbyteuninitializedещёнепридуман.
Correction072:45FBD0/C0BD64 isSCREENsingleton,notcurrentstage.636C80calledfrom
62FB40Screenctor,4F5E40readsHWND340. SourcePostUI LPARAMguard implemented/nulltested.
34ranges/2vtable64/15fullasm equalpins;IDAb3b8653dsavedclosed. Raw*073вartifacts/
client455-progress. ConfiguredIDAprobe66tools/list10/decompile/closePASSoutside
sandbox;insideworkerexit2. Nativeconnectionworked,noinstalls.
ActualAvatar+MainApp+accountinmemorychecksPASS;stageisvirtualfixture,notTutorial.
KoRuwindow/boardPASS,22GPUhashesequalreviewed687b88c explicitlyreused;othersGUI
historicalunchanged. PE3d1f8c323584e2a21a3e9c8b284d355f898ffcb5528f942385b333b682148970,
entry150550/2042880bytes/182client20kernel32facade/0unresolved/exactCreate1.
PrepC250DB70…idempotent.40080201unknown.M6/M6F/M7/M9OPEN,newgatePARTIAL.
FullTutorialmethods5586D0/558AE0/558B80/5590B0/5594D0/559670/559750/559810/
5598C0 read/saved;actualclassnotcreated. Next074: realworldowner/ILevel/BSP39
forrace-selectedbellato/cora/accretia maps +cameraintro,thenlocalhandlers/real
Avatar/world/frame/input/feedbackhost/board47QBI/fourstage jointmigration.
6realBSP/CAMfilesavailable/pinned;BSP39,CAM1.2. No server changes. Allpriorgapsstay.
Details research/client455-avatar-stage.md.

Участок072: actual source CGUIBriefingWindow/RF455TutorialBriefingWindow готов
для real stage owner. Pages BYTE/80ms/firstdelay250/continuefinish-next-close,
ND445/1059/106,6lineautosize,caps462/611,outline,portrait134/128,keyframe140,
real21/31..33resources. Portraitrole0or2/3/15,raceBYTE/2,128cells8idle/16talk,
FPS10,random%5+10periods/oneperiodtalk;actualwindow Updatecell2/UV0.5 checked.
Avatar race API explicit:realcurrentAvatar provider ещёнет. Screencapture field
target+480E0:membership check onlySet,shown overridesinput/ID andMsg routing;
Remove/Close retainspointer,release before destruction. Msg no queuedrain.
32ranges/vtable212 equalpins,19listedfullasm+2captureasm,IDA18f99dcdsavedclosed.
Ko/Ru3pages/realmouse→queue→NextClose/22frames contact sheets viewed. Russian
ND1059 beyond45pxbutton:pixelparity notproven. ActualCTutorialBoardprobe uses
realwindow/key/capture now;Avatar/stage stillrecordingfixture,productionwindow
instance notregistered. No force-retention. Facade31TU/182client/20kernel,
0unresolved;PEbd50df91f63d2e5a3e844cd6fafe9b960a8bcd3479f8f9c4c2c3b2bc3d5710f7,
entry150350/2041856bytes/exactCreate1. Nativeprobe d0692d3d…/entryE7930.
Freshgui-input/modal/minimapKoRuPASS;olderGUIreports historical,notretagged.
Runtime changed:071timestamp-onlyreuse isNOTcurrent. No largeunchangedsuites.
40080201unknown;ownresource reset/globalmanager/currentstage45FBD0/basewindow/
virtualSetSize/IME/layers/unsafe domains stillOPEN. NewwindowgatePARTIAL.
Next073: actualAvatar/world/frame/input/localfeedback +Tutorial/fourstage,then
fullauth/login/world/gameplay. AllpreviousCharacter/render/lifecyclegaps stay.
M6/M6F/M7/M9OPEN. Details research/client455-briefing-window.md.

Briefing-controls071: new client455_briefing_controls.{h,cpp} supplies frame,
keywidget and sourceanimationbridge;legacyCGUIObjectAni notgloballymigrated.
Maincaps common4:3/4=462x32,9:6/7=611x32,2capchildren;body+verticalborders then
basefill/image+children. Alpha preservesRGB. Colorsmustconfigured:preInit
targetfieldsunspecified/sourcezero notparity. Key21 Common/tutorial.spr,
plus12x12,ND1058,rowsmax2/retainsoriginalcountconditions. Mouse0..4 andkeys
17/18/32/65/70/73/77/79/83/87/90/112.255 preservesstate/size;otherunsupported
resetanimationbutretainsize. Heightsusestale omitteddimensions;pluspositions
two5gaps,butwidthcountsone. NewanimationbridgefloatFPS/x87advance;BYTEgrid0->1,
Org/gridcellsize,UVcell(orforcedextent)/tex. SetSheetdoesn'tsetUVuntilUpdate/
SetFrame;preUpdatecompressedmousesheetsfixture intentional. Loopoverflow0+
paused+stamp,dropsremainder;pauseunsignedelapsed>interval,resumeUpdate noadvance;
nonlooplast/finished. Mode0/unrotatedonlyverified;fulloldAni/unsafe domainsOPEN.

Important070correction:60CAC0 calls2262E0,baseDrawincludesownfill/image. Old
children-onlyclaimwrong. Typing.Draw nowCGUIContainer.Draw,80000redpixelstest;
frame ownfillaftermanualrectanglesbeforecaps. NativeUVtestfirstcaughtdouble
ratio viaoldSetSpriteU/V;fixed directUVassignment. Typing ref19ranges/9asm.
TargetA63A0 asm confirms633360 ECXscreen pointer:1captureswindow,0releases,
setter rejectsnot-added. Fullinput/removal/lifetimecapture consumersOPEN.

29ranges/3vtablesequalpins/8fullasm,IDAs e0103d83/38abac4esavedclosed. Ko/Ru
controls/typingnaturalexit0.20frames/12uniqueviews,8othersbyteequalprofiles;
typedredfillviewed/countverified. Controlsprobe85a2312e56faffd07cc26a2aa2bdf56546fe28b5cee4de57185e1e3225d571c3,
entryE48D0;typing676c939a6ddb6b296f179cacb7a32448ad0ff3524aaaa631ee90907a3a31bab3.
Productionfea692b941be17117b80a697c2af1a09317905bb8ce6fe9ceee7917b594c6cc9,
entry150290,2041856bytes/182client20kernel30facade/0unresolved/exactCreate1.
Unusednewclassesstrippednaturally. WholeownPEruntimebyteequal070 aftermasking
ONLYCOFF/debugtimestamps296/1873360;audit_controls_production.py evidence.
7oldGUI native manifestsunmodified/exactsameas6173adf/recordedsourcesunchanged,
reusedexplicitlyinnewtypinggate;44oldGPUhashesstill069equal. No unchangedlarge
suites rerun. Fresh currenttyping+controls gatesPARTIAL;otheroldergatesremain
historical,not falselyretaggedfresh. PrepE22CE37B…idempotent/engine056same.
Next072 actualCGUIBriefingWindow/outline/portrait/page/events/screencapture/
RF455TutorialBriefingView,thenAvatar/world/Tutorial/fourstage. M6/M6F/M7/M9OPEN.
research/client455-briefing-controls.md andbriefing-analysis.md containdetails.

Предыдущий участок070:

Text-typing070: CGUITextTypingBoard source added(h/cpp),normalfacade29TU.
No production window instance yet;stripunusedallowed,no forceinclude. Actual
full-object native usesfacade methods. State intervalWORD100/running0/finished0/
start0/previous0/first,last0/cursorFFFF. Start target6475A0 signedrangecheck then
WORDstores,clock+delay;negativeacceptedtargetrange explicitrefusal. Update647690
shown/running/notfinished;absoluteDWORD start+loop checks,unsignedelapsed,
previous0sentinel,spaces skippreviousincrement. BoundaryusesOLDfragmentStr
atnewOffset:leadingfragmentspace canrevealBC inone tick. Resource language
601F50/7B2450 DBCS,notambientCRT;firstglyphlead adds1,subsequent2/1 advances.
Donewhen cursor>endmarker/sameoffset>=end. FinaltickretainspreviousTime.
Clear647BD0 cursorFFFF+baseclear,retainsflags/timers;sourceClear nowvirtual.
Draw647940 ownfill/image+children (corrected071),nochildUpdate;strictstart<cursor then
inclusivepartialhelper645150. FirstASCIIcursor0 invisible,firstDBCS cursor1
visible. SharedDrawLineTo455 extracted;smallfull-lineadapter inlines. Existing
TextBoardgate nowchecksactualendpointprovider,notforce-retained oldsymbol.

18ranges/1vtableequalpins,8completeasm;IDA37b9a025savedclosed. Ko/Ru42clockqueries,
nativeexit0;14frames saved/8viewed,typedAB byteequalplainAB.44existingGPUframes
equalcommit7115112checked in newgate. Ownprobe feb7b853ad6cb27e99249f83f74cb9b11ec4657fe3c325df805cd985cb49460e,
entryE4A60. Production8f009924c882d5c87c2f6872c3c99b07ff98a9085bd6ca9643bf13832d6f0b4c,
entry150290/2041856bytes/182client20kernel29facade/0unresolved/existingCreate1.
Prep idempotentF7A4826F…;engine056same. AffectedGUI passed,10gatesPARTIAL.
Firstchance40080201stillunknown;fullauth/world/gameplayOPEN. Next071 actual
CGUIBriefingBoard/key/portrait/frame/window,RF455TutorialBriefingView;thenactual
Avatar/world/Tutorial/fourstage. Fullstaticmap+raw references in
research/client455-briefing-analysis.md;behaviordetailsclient455-text-typing.md.
M6/M6F/M7/M9OPEN;negative/missingmarker/WORDoverflow/foreign/OOM domains notparity.

Предыдущий участок069:

Message-sizing069: ordinary CGUIMessagebox.SetMsg now takes explicit formatted
bool(defaultFALSE),basefontFFE3E0D9,Clear→plain/markup→ResizeToText before reading
dimensions. Null pointer no-op. Target701870 scroll branch reads natural size,
so300/250 caps are fallback ONLY;positive requestedsize is overwritten. No
unconditional scrollbar removal;overflow Add→bar.SetSize→board.AddScrollbar.
Minimum200x100,margins30/30 or60/45+barWidth/buttonHeight. Target701630 is
SetSize(width,height),notRECT SetBound;source keeps typed SetSize→SetBound
bridge. GlobalGUIObject.SetSize stillnonvirtual:mandatorygap. Wrapper700720
forwards runtime formatted/allowClose;constructor/errorwrapper passplain0.
Source create-info bFormatted455 isconvenience,notoriginal455ABI. Emptylist
243D30 readsuninitialized newline local:sourceSetMsg explicitlyrefuseszero
fragments;not equivalence. Allwrapperguards/OOM/invalidgeometry remainOPEN.

21ranges equalpins/15fullasm,IDAb852f877 savedclosed. Ko/Ru12groups GDIoracle+
realmodalcontrols/richwrapper,GPU10frames allviewed;nativeexit0. Ownprobe
1a1b3022…/entryE6B20. Productionc22502faf1a98ed229ed62d341f4609ab5ca55f31c33bd26cdc2b7bc5aa83340,
entry150290,2041856bytes,182/20/28TU,0unresolved/existingCreate1. TextBoard
InsertFormatted455/ResizeToText retainedbyactualSetMsg,notforceinclude;
SetSizeadapterinline/SetBoundretained. IdempotentprepEF02C4A3…. Engine056same.
AffectedGUI/Tutorial/font/metrics/scroll/input passed,9gatesPARTIAL. No unchanged
largeparticle/runtime rerun. Firstchance40080201 stillcauseunknown.
Next070 actualCGUIBriefingWindow rich/resources/events/state,thenactualAvatar/
world/Tutorial/fourstage. M6/M6F/M7/M9OPEN. research/client455-message-sizing.md.

Предыдущий участок068:

GUI-input068: new client455_gui_input.{h,cpp},object/container/queue.inc and
generator overlays actual GUIObject/Container/EventProc/MouseDev. Base input
626B90:extra inputflagDWORD88 default1 (notActive52),double7/right8,300inclusive
DWORDwrap. IfsameLast==this clockqueryforcompare then alwaysnewstampquery;first
differentowner skipscomparequery. Double clearslastowner;rightstroke setsright
pointerandclearslastowner evenifleft suppressesevent;right-held suppresseshover/
move. Source captures modalglobal102CF4C:6277D0 alwayscallsoldvirtual100 before
assignsame/null;outsideleftstroke callsoldcallback andconsumeswithoutunderlying
stroke. Caller63DEB0 isdropdown,notinputfield;API CloseMouseModal455 defaultnoop
as504CF0. Fullpopup implementation stillOPEN.

Msg627370:focuspredicate then WM_KEYDOWN/WM_CHAR,Ctrl17/Alt18 highbitfilter,
allbytekeys;229 mapsENTIREarithmetic high16 viafixedQWERTY scans16–25/30–38/
44–50,elseFF. Not MapVirtualKey,notmask8bits. Queue62AE80dedups source/id/keyBYTE,
ignoreshandler/value. Eventrecord36,bytekey10,DWORDvalue32. Focus70–79 generic
IFocusObserver455,80–89 source/id/value,>=90ignored;old50/60windowroutesretained.
Source namedinterfaces areownedsemanticAPIs,notoriginalprivateABI/identities.

Focus6275C0:alreadyfocused returns1;oldpointerdifferent sends71 BEFOREtesting
newenableFocus/show/active/disabled. Failedcandidate leavesoldpointer despite
blur. Success updatespointer,70. Kill627650 onlywhenIsFocused predicate true;
hidden/inactive pointer canpersist untilvalidkill/destructor. InActive/Disable
focus kills beforeflagchange. Basepredicateignoresdisabled state,soalready
disabledfocusedobject stillqueueskeys. Containerdefaultdisablefocus confirmed
60BDE0→60D0A0;sourceSetFocus nowdelegatesbase afterexplicitEnableFocus.

ContainerAdd60BFA0:nonnull/notduplicate→Show(parent)→pushbackmainlist96.
60C040 pushfront,noimplicitparentobserver. 60D3D0/60D650 arelistinsert and
60DE40/60E010 arefind,NOTbubbling. Input60C850 reverse-main-list;parentinputflag
doesn'tblockchild. Remove60C480:null0,nonnull1 evennonmember,kill eligiblefocus,
removefrom3targetlists;doesNOTclearhover/pressed refs toalivechild. RemoveAll
60C4F0focus-only then3clears. Sourcecurrentlymainlistonly;other2/renderlayers
andlegacyindexedcompatAPI remainOPEN. Mouse7AF900 sameleft/rightpriority plus
middlekey3 (bit2);drag/move rules unchanged.

Important065correction:ordinary638EE0 bindscomposite484 only,639590 registersself
only,627070 onlydirectobserver;defaultarrowsUNBOUND. Removedownedarrowadapter,
updatedoldreferencegap. EX63A750 explicit4regs retained. Removedredundantmanual
Show bridges nowgenericAddinherits. NativeactualInput verifiesordinaryamount10
unchangedonarrow vsEX10→9. Neverinventtargetbugfix. Actualcaller-specific arrow
registration stillrequiresproof.

34ranges/1vtableprefix equalpins,15completeasm;IDA6eadfaf3 savedclosed/idb_list0.
Rawartifacts/client455-tutorial/gui-*068. OwnPEd424f606ec491232aba552e53311e96f79ca76802b636d15120316a62c6a4082,
x86entryE4480,Ko/Ru naturalexit0. Double300/301/wrap/querycount,right/modalguard,
Addshow/duplicates/front/Removealive refs,focusordering/stalepredicate,CtrAlt/
key229/differentqueuedkeys/value/focus70/middle/ordinaryvsEX checked. Native
firstcompile hitbaseheader '#define parent(this)' fixturelocalname;renamedholder.
Tutorial-board061fixture expectedCtorhiddenAFTERscreen.Add;Add455inheritedshow
correctlymadeitvisible. FixtureexplicitShow(FALSE) afterAdd,productionunchanged.
EightboundedgatesPARTIAL;allaffectedscrollbar/variants/minimap/textboard/metrics/
font/modal/tutorialboardpassed. FortyGPUframehashes equalpriorviewedframes.
NormalPEde76223c075a2af2d164f6486e8ceed49d34ebf28153bc7c12a85c4e187be60a,
2036736bytes/x86/base400000/entry14F4A0,182/20/28TU,0unresolved/existingCreate1.
OwnstartupTCPfixture/engine/D3D/Character/Create passed,stopbeforeloop. Oneextra
firstchance40080201 inKernelBase logged;causeunknown,notfaultparityacceptance.
Generatoridempotent,canonical20/engineunchanged,allownedsessionsclosed/probes
stopped,noreferenceEXE/serverchanges/largeunchangedsuites. Next069 production
message sizing/rich callers/fullbriefing,thenactualTutorial/Avatar/world/fourstage.
Inputfield/IME/popup/value80consumers,other2lists/layers,indexedcompat,cross-thread/
OOM/destructorregistry/downstream7/8 actions andallpriorM6F/M7/M9 remainOPEN.

## Предыдущий результат — minimap-opacity067

Minimap-opacity067: new client455_minimap_opacity.{h,cpp},owner.inc +generator
overlays normal CGUIMiniMapWindow header/body. Adds actual EX/IScrollObserver,
known mapped frame/map CGUIContainers and gridbackground. Target7B2C60 wraps
genericalignment7B2B80;it is NOT scrollbar skinhelper. Actualskin7B5450 styles0/1
commonaction8:style0background12,thumb13/14,bottom15/16,top17/18;style1background6,
thumb7directSPI (not statearray),top8/9,bottom10/11. Widthaddsarrowwidths,auto0,
horizontal1. Realcommon gives194×13/button10 and192×15/button8.
Init7059E0 centersEX relativeframe,theny+15,SetAmount80/80,observerandAdd. Main
sprite5:0 frame400×18 and5:32 grid400×400 restored;avatar5:1 andclosecommon0.
Source frameSkin ownCSprite bridgeslegacy id4inventory vs455id4main collision;
lazyverifiedmainpath load,no global ID4 replacement. OwnspriteRelease in dtor.
Other455controls/mapgeneration/assetmanager lifecycle stillOPEN.

Scroll709E10: BYTE(signed32wrap255*(current+20)/100),then independent5558E0 zoom
gate evenforeignsource. Alpha7099E0 appliesmapped title/frame/map/avatar/position/
close and populated marker/tooltip lists,preservesRGB;EXalpha propagation.
Backgroundalpha:alpha==100 ? truncate(alpha*.8) : truncate(alpha*.6). Extra0.7
object/tooltipcontainers not assigned alpha withouttargetproof. Remaining455
groups absent fromlegacyowner OPEN. Gate fields:eligible(alpha==100),suppression,
ack. Ifnotsuppressed returneligible;elseifack clearsboth thenreturns0 thiscall.
Positive555940 actualAvatar/world zoomconsumer explicitlythrows;notrestored,
nevercallit a successful camera operation. Scroll0..80 cannotproducealpha100.
Draw7099A0=container.Draw then dialogs;legacyFFmapgate/outline removed. This
letsactualownerDraw test beforemapproducer;NO fullminimap/gameplay acceptance.

17functionranges+2vtables equalpins,10completeasm. IDA7b53e450/b947042c savedclosed;
idb_list0. Rawartifacts/client455-tutorial/minimap-*067. RealKo fallbackCommon
mainDXT1,Ru localizedmainARGB21;inputpaths preserved inlab,not forcedlocalized.
OwnPE c8d0f03ba214073f0d7f0e77972b5d4796b0dd983dbaff307f8aa7070e09f96e,
x86entryE4380,Ko/Ru naturalexit0. All81queuedamounts,RGB/list alpha,bg100special,
gateack/foreignsource,style0/1,literal/edge/negativeodd alignment verified.
Real MouseDev.Update→window.InputProc→EX→EventProcess→owner:arrow80→79/alpha252,
track→17/94,dragendpoint→78/249 duebase162vsvisible158,release snapsowntrack154.
Buttons muted fixtureonly (unrelated audio nottested). Firststatefixture used
PRESSED alone;corrected to HOVERED|PRESSED as actualInputProc does. No production
button-state behavior altered. Grid frames24133/167218/167200Ko and21148/167236/
167200Ru pixels viewedall6. Graypartialalpha is oldnull-map-sprite rectangle
fallback;gridfrommain5:32,NOterrain/MapID56data. FullrenderparityOPEN.
NormalPE0def3dce864ffe438eddf73abd84e17929121d2abb06f19921c8d37f9ef26e37,
x86/base400000/entry14EFF0/2033664bytes,182/20/27TU,0unresolved/existingCreate1.
Productionmap contains ownerScrollEvent/SetAlpha,EXSetAmount andnewfacadeprovider;
EX is now retained byrealowner,Var canremainstripped. Sourcegenerator idempotent;
oldignored064crt_multibyte.obj removed;CMake27sources/27objects,LIB/LIST andmap
haveNO customadapter (standard__acrt_multibyte symbols arelibucrt,notthatfile).
engineunchanged,canonical20kernels. Affectedscrollbar/variants/textboard/metrics/
font/modal/tutorial-board andexactWinMain/TCPfixture/engine/D3D/Character/Create1
passed,stopbeforeloop. Sevenboundedgates PARTIAL. NoinputEXE/serverchanges.
Next068 GUIObject/Container input/show/focus/parentwiring;Add60BFA0→60D3D0 and
SendMouse*/InputProc. Cached065baseSetAmount hasonlyoneobserverregister(self),
EXhasfour;don'tassumefullpipelineorhelpermeaning. Thenrich/message sizing/
briefing/actualTutorial/fourstage. Fullminimap/camera/allotherM6F/M7/M9 OPEN.

## Предыдущий результат — scrollbar-variants066

Scrollbar-variants066: CGUIScrollbar base state protected,SetSize virtual for
455derived dispatch;existing static amount methods retained. New EX plainbutton
added at ctor even total0;SetAmount0 removes observers but not child. Auto sizing
has NO composite6x18 clamp,negative available minimum preserved. UpdateBar uses
own plain button track63B050;Mouse/drag directly call BASE63A1A0 reading inherited
composite size. No MOUSE_PRESSED repeat. Alpha on self/arrows/plain/basecomposite.
Inherited Draw paints children then returnsFALSE when hidden unused composite
Draw fails.625C70 show=0/6394A0 AND confirmed. Source label Draw outcome tested,
not normalized toTRUE. Real owner CGUIMiniMapWindow ctor705160/Init7059E0.
Its helper7B2C60,SetAmount80/80,posY+15,observer and ordinary source owner OPEN.

Var: initializer virtual+24 is SetSprite63B310,NOT RemoveAll (vtableADB0FC);
two base arrows remain. Caps common action15 frames0/1/2,pressed3/4/5. Row draw
explicit common action2 frame1/4 and row2. Own source uses CSprite pointer adapter.
SetSize keeps raw outer width/height,separate skin min6x18,cap heights from valid
requested resource (invalid→0),NO amount/reflow. SetAmount adds3skins+basecomposite,
sets origin and thumbheight=preferredHeight-total+caps with composite minimum;
middleExtent=preferredHeight-total including0/negative;NO UpdateBar. Total0
removes4children,retains extent. Draw0extent skips all;negative loop none then
container.Draw. Vertical trackclick subtracts FULL thumbheight;drag commits then
freepixel;release switches modes only. Horizontal tracklocal uninitialized:
explicit throw,never inventvalue. Var ctor hasNO direct xrefs in IDB;indirectuse
not excluded. Fullclient completeness still requires all known behavior.

Target sprite loader8CFB90 actions<16 already proved048;therefore action15 cannot
be supplied through ordinary loader. Ko/Ru selectedcommon15actions,action2=44.
First fixture16actions correctly hit engineError/exit1;fixture changed to15 and
tests preserve missingcap height0,not productionguard. Other early fixture
assumption DrawTRUE corrected:EX hiddenbasecomposite returnsFALSE after painting.
Shared UV width ratio now floatspill before finalUV,as6269A0. FullFPdomain OPEN.
37ranges+2vtables equalpins,13fullasm;IDA68442489/ef4ffb43 closed/save.
Raw artifacts/client455-tutorial/scrollbar-*066;research/client455-scrollbar-variants.md.
OwnPE7d9b518cd492543317be036979821e12ee1e48a2556dbe81175235dc5c58f396,
Ko/Ru naturalexit0,3GPUframes hashes equal:282/420/420pixels. Three earlier
148e5bba frames viewed;latest7d9b518c frame hashes identical. EX realarrows/plain
thumb;Var owned15action fixture action2 row2 green/cyan;missingcap intentional.
NormalPEb24f1f0967de631da59f427df4c73908cf057621385238f88166e2f40b59db95,
x86/base400000/entry14E290/2029568bytes,182/20/26TU,0unresolved/existingCreate1.
All affected scrollbar/textboard/metrics/font/modal/tutorial-board probes passed;
sixscopedcheckpointsPARTIAL;generator idempotent,canonical20kernels unchanged.
Variants may be stripped from production until real455 minimap owner is ported;
no forced retention. Next067 helper7B2C60/minimap and parentinput;thenrich/message
sizing/briefing/actualTutorial/fourstage. No inputEXE/serverchanges/largeunchanged
suites. All owned sessions closed,probes stopped. M6/M6F/M7/M9 remainOPEN.

## Предыдущий результат — scrollbar065

Scrollbar065: new native/client455_gui_scrollbar.{h,cpp} replace normal header/
body. Ordinary classesCGUIScrollbar+CGUIScrollbarButton (container+3imageobjects),
NOT simplelegacyCGUIButton. Defaultthumb6×18,minwidth6/minheight18;autoTRUE,
minimum20. Auto length=parentExtent-arrowSizes-total thenmin;too-short canleave
negative/zero track. Minsetter capsminimum toavailable excludingarrows;growing
parentdoesnotrestoreoldrequestedmin. Trackrecomputed fromcurrentdimensions;
UpdateBar signed32current*track WRAPS beforeidiv. SetTotal/Current bothSetAmount.
Zero total removesThumb onlyifchildcount==3. SourceDraw=container&&thumb again.
Modalhelper7B4E30requested5×18 nowphysically6×18;062's5waslegacy/requested size.

Calc63A1A0: inttotal/distance double spills,x87 divide/multiply,floatspill;
__ftol2_sse872B70 SSE2 uses32bitCVTTSD2SI,NOT int64. Preservemodulo/halfcompare
andNaNsmall-range upperendpoint. Nativevalidsnap/NaN/INT32overflow/productwrap
passed. NonSSE2 fallback/allFP/unmasked/unsafe domains stillOPEN.
Mouse: strokedtime+eventtime2queries;repeat thresholdquery+newstepquery+eventtime,
DWORD wrap and multiplication. Postupdate comparisoncanemitDOWN31forupward
track/drag. Dragkeepsfreepixelposition;release realignsnoevent ifsnapunchanged.
Nativeclock replaysetter restoresdefaulttimeGetTime. Actualqueue dispatch used.
Ownedarrowobserver/showadapter bridges0.7lackof455parent bubbling/inheritance;
notclaimtargetprivatewiring. GetMinSize/SetScrollSpeed wrappersawaitfullcallerproof.

Compositeframes44/47top,45/48middle,46/49bottom/common action2. Row2 repeated
perpixel;middleUV useswidth/orig/texture ratio as6269A0. RealKo/Rucommon action2
only44frames0..43. Target8CFF90clampsmissing44..49 to43;actualnativepreserves,
realnormal/pressedimagesIDENTICAL. Doesnotproveassetversion orruntimeuseof
defaultskin (flagdefault0). SourceSetSegmented sizesuseSetAction/Frame clamp
beforeGetSpriteOrg;doNOT queryout-of-range frame directly.
OwnsyntheticSPR has50frames/colorcaps/middleonlyrow2green/cyan,otherrowsgray.
Point-samplingfixture actualGPU row2pixeloracle andpressedRGBdifferencepassed.
FiveframesKo/Ruhashesequal,representativesallviewed:478/279/279/478/478pixels.

23functionranges+2vtableprefixes+double2 equalbothpins;15fullasm. OwnedIDA
bfcf8ee1/9775776a closed/save. Raw artifacts/client455-tutorial/scrollbar-*065.
Core/ranges/asm/support/ftol/containerdraw/spriteorder/frameclamp primaryproof;
more/helpers alsoincludeunportedEX/Var decomp for066. NoinputEXE/serverchanges.
OwnPE05e4466e3f8100129a1f40045cdf082d185a73c06b3ac752f9ac9550478fec9a,
entryE4020,naturalexit0Ko/Ru. NativeprivateEventQueue create/process viafriend
accessfixture;noexposureinproduction. SourceCPPfirstMASM 'length' reservedname
renamedscrollLength;probeprivatequeue compilefixedwithfixtureaccess.
Productiond38d74e09a7b11801abec69ff90804ee89c6c5fa12818a1f55311b61414229a8,
x86/base400000/entry14E350/2030080bytes,182client20kernel26facade,0unresolved.
NormalCUnity/CAnimationPASS;engineunchanged;generatoridempotent. CurrentTextBoard/
metrics/font/modal/tutorial-board probesPASS;exactPE WinMain/TCPfixture/engine/
D3D/Character/existingCreate1,stopbeforeloop,noauth/gameclaim. ScopedgatesPARTIAL.
Next066 EX/Var +parentinput/callers;thenmessage sizing/rich/fullbriefing/actual
Tutorial/fourstage. Resource/skin/alpha/clipping/lifecycle/FP/unsafe andfullM9OPEN.
Reportsinventory/client455-scrollbar-{reference,native,checkpoint}.json;
research/client455-scrollbar.md. M6/M6F/M7/M9OPEN.No largeunchangedsuites.

## Предыдущий перенос — text-board064

Text-board064: replaced normal guitextboard.{h,cpp} through generator from new
native/client455_gui_text_board.{h,cpp}. Separate owned TextInfo fragments and
WORD fragment/offset line markers,limit1000/base/view0. Pixel metrics063/layout
append reconstructs lastline;fullreflow only on actualwidthchange. Margin-only
does NOT reflow;unfittable glyph may remain raw without anyline. Newline markers
point at newline byte:leading/trailing newline quirks preserved. Retention
frees wholeoldfragments only when nextmarker advances fragment;zero limitkeeps1.
Rebase atbase+fragment>=FFFF subtracts first absolute marker andresetsbase0.
Actual65536insertions/limit1 reachedrebase native;not65536independentchecks.

FONT_INFO16:BYTE size0/style0/colorFFFFFFFF/float scale1. TextInfo28 cachesWORD
length at8/font at12;Clear freesstring butretainslength. SetFont(nullptr)no-op.
Source refuseslength>FFFF insteadof reproducing target mallocWORD/strcpyoverflow.
Both ordinary CGUIText/boarddraw passscale1;fullother scale/FTconsumers OPEN.
New formatted/extent methods sourceavailable/fullobject tested butSTRIPPED in
production untilrealrich callers port. Legacy messagebox.SetMsg stillbyte-size.
DoNOT forceinclude symbols or reinterpret plainInsertText asmarkup tohidegap.

Markup font/close prefix case-insensitive,attrkeys case-sensitive;stickycolor/
styleflags,colorprecedence andadjacent '>' in %stoken preserved. Reject32token
overflow/nonadvancing malformed grammar explicitly. Helper7B1F40 capacity BYTE
proven0FB64510;256->0 retainsdest. Boardmarkup/finaldraw share256byte scratch;
otheroriginal102DAB0users OPEN. Copy followsambientCRT,notresourceCP.
TargetCRT889853 _setmbcp(-3);_getmbcp returns0forSBCS too. InstalledUCRT source
alreadyinitializesANSI. Incorrect earlyadapter assumption wasrejected;files
removed,noproductionadapter. Nativeexplicit949/1251copy tests restore_MB_CP_ANSI,
notambiguousgetmbcp0. ThisPC ACP1251/ambientgetter0;fullCRT thread/localegapsOPEN.

Scrollbar SetTotal/SetCurrent nowboth SetAmount toclamp/update. TextBoardrange/
view/auto-bottom/observer tested. Fullthumb/inputgeometry/timing/variants legacy.
49ranges+primary/observervtables equalbothpins,17completeasm;owned958042ee,
aabab7c3/06c03ace closed/save. Raw artifacts/client455-tutorial/textboard-*064
and064-643890-asm;reference/native/checkpoint reports client455-text-board-*.
FinalownPE256cbbe73ad1de562bf8b7e8a39b23aa9681917c944d275ed678444af285bbfc,
entryE4610,naturalexit0Korea/Russia. ActualGUI/GDIoracle predefined markers/
DBCS/boundaries/cache/retention/rebase/tags/scroll/GPU4frames passed/viewed.
Ko204/575/271,Ru160/620/304coloredpixels(colors/markup/bottom),highlightalsoseen.
Tutorial061fixture movedfromprivate m_listText topublicfragment API;now compares
rawND441/444 WITHnewlines,modal2/3regression PASS. Rich/stageproviders stillfixtures.
Production3a209cdc328c7fb20313233ba3f58745685344c0521bbe69c071e020a2e71485,
x86/base400000/entry14DD30/2028032bytes,182client20kernel26facade,0unresolved.
Smallcopyhelperinlined intoDrawLine;explicitentry inownprobe. Requirednormal
CUnity/CAnimationpassed;engineunchanged. Currentmetrics/font/modal/tutorial
probesPASS;exactPE WinMain/TCPfixture/engine/D3D/Character/existingCreate1,stop
beforeloop. Noauth/fullgameclaim. Next065fullscrollbar;thenproduction message
sizing/richcallers/fullbriefing/actualTutorial/fourstage. M6/M6F/M7/M9OPEN.
Researchclient455-text-board.md; noinputEXE/server/original changes.

## Предыдущий перенос — text-metrics063

Text-metrics063: normal CGUIText.SetString calls source-owned byte-width
geometry; 80000000 intermediate8*cells/16 overwritten by ordinary size unless
40000000 sets final16*WORD(width/12)/32. SetFont only copies,no recalc.
New native/client455_text_metrics.{h,cpp},gui_text_size.inc,gui_text_metrics.cpp.
GDI measure uses GetTextExtentPoint32A, fit uses GetTextExtentExPointA then
language isLead(fit-1) decrement. Exact raw byte prefix may cut DBCS;FFFF full,
zero/null width0. Default height measures EMPTY AA8DD4 once,retains across reload.
GDI zero-cy fallback is cellHeight. Full FreeType/Unicode route remainsOPEN.
Target FONT_INFO16 has float scale1.0 at+12,NOT link identifier;typed scale/draw
stillOPEN. LegacyTextBoard2000byte-count algorithm not accepted as455.

Initial ownPE19821d65 pre-main C0000005/ownRVA5F034 read10: legacy globalGUI
SetString ran before RF455GdiFont construction. Trace work/m9/19821d65/text-
metrics-ko-kr-001/metric-debug.jsonl. Fixed by owned pending geometry queue:
register backend PODcallback,flush after successful real font creation,
ForgetGuiText in normal destructor removes destroyedpending;registryAlive guards
late global teardown. This is0.7port adaptation,NOT target lifecycle claim.
Native global EarlyText+temporary deletion+real sizes/clean exit checked.

15ranges/emptyliteral equalbothpins,5completeasm; IDAe13a414e closed/save.
Raw artifacts/client455-tutorial/{textboard-initial063,textboard-metrics063,
text-metrics-reference063,063-*-asm}.json. Reports inventory/client455-text-
metrics-{reference,native,checkpoint}.json;research/client455-text-metrics.md.
Native fixture source UTF8 literals initially mojibake under legacy cl source
codepage;fixed universal Unicode escapes+roundtrip. Final PNGs viewed,correct
Hangul/Russian. Current ownPEf7cd59ce7a634a6c3765ea3cef46e5cb3904d202a3e25336e511cfc99f3bef51,
entryE2780,naturalexit0. Korea50prefix/260fit,Russia48/276oracle cases;
actualCGUIText/highflags/noSetFontrecalc/NULL/DBCS/cache reload allpassed.
Viewport640×480,271/304pixels;counts are localassertions,NOT completeness.
Production71bc4b210a88d6f66693d321e8b3b5099d8b04818b9ad6ad4ac4367ba19e8fc4,
x86/base400000/entry14D7C0/2025984bytes,182client20kernel26facade,0unresolved.
Normal width/defaultheight/geometry providers linked;fit helper only used in
fullobject probe untilTextBoard caller port. RequiredCUnity/CAnimation passed.
Generator manifest/preparation idempotent. Engine archive unchanged.
Currentaffectedfont/modalKoRu probes PASS;exactnewPE WinMain/TCPfixture/engine/
D3D/Character/existingCreate1 passed,stopbeforeloop,noauth/gameclaim.
Next064 fullTextBoard fragment/line cache/markup/wrap/retention/margins/scroll
and shared scrollbar;thenfullbriefing/actualTutorial/fourstage. FullFreeType/
16byte scale,olditemtail25/camera276/cursor/numeric/errors retainedOPEN.
No largeunchangedsuites/server/inputEXEexecution. M6/M6F/M7/M9OPEN.

## Предыдущий перенос — modal062

Modal062: ordinary CGUIMessagebox/CGUIDialogBox modified via prepare_normal,
not separate fake dialog. New native client455_modal.{h,cpp},modal_init.inc,
dialog_input.inc. Bothbuttons commonID1/action1/frames0normal1hover2press3disabled;
realko/ruframes67×21;closeaction0frames0/1/2(24×14). CaptionsND106/107,style32,
GDI measuredcentering via RF455_MeasureLegacyText +ownedbuttonmetricsAPI.
CGUIButtonEx disabledcaptionFF797979 beforehover/normal confirmed60BC70;
newownedfielddefault;allnormalheaders/objects rebuilt consistently.
FrameRGB222628/defaultalphaD8,outline6A6E72,width1/inset2;SetAlpha preservesRGB.
Fullbodybounds,buttonmarginsright/bottom7,gap7. Scrollarrows action2frames0/1,2/3
(12×8);thumb5×18/color70635D;shared scrollbar layout/input stilllegacy/OPEN.
Open resetsOKcaption106/enablesOK only;Cancelcustomlabelretained.
Target65C270 constructor closeflagDWORD83=0: owneddefaultFALSE,notTRUE!
Wrappers explicitlysetallowclose; createinfo bAllowClose455 defaultsTRUE;
pooled reusedwindow flagreset. Enter1,Esc3 iffallowclose(else return0,noevent).
YNstyle3 only&&!focusedchat. IsFocused455=enableFocus/show/active/staticidentity
proven627570. Legacyprimarychatinput wired via g_pUiChatWindow->GetInputField;
fullMainGame455provider identity stillOPEN. Mouseobserverbindings+results1/2/3
checked; nested dialogs dispatchbeforeparent.
43functionranges/3vtables equalbothpins,8fullasm;IDA124615b8/14980562closed/save.
Raw artifacts/client455-tutorial/modal-*062.json,062-*-asm. Reports inventory/
client455-modal-*,research/client455-modal.md. Own modal PE d3ca9b9bc5781e4e75c9460d54ea52c93f514a0d9a71f33d5f8d621611442615,
entryE3700,naturalexit0 forKorea/Russia. ActualGUI/GPUviewport640×480,
normal/hover/disabledframes saved;normal20000changedpixels;Korean/RussianPNG
viewed(oldwrongicon gone,labels readable). Text-board/render metricsFull455
NOTaccepted: sharedwrapping/markup/sizing/scroll,FreeType/ANSI/Framewindow/
lifecycle/wrappervariants remainOPEN. SourceGDI helper uses existingGDIroute;
affectedfont046probeKo/RuGDIoracle/atlas/wideframe regression passed.
Production normal nowa5b1da0b344c898c6b71079b64742ee08852e62eaaf7e206e55815540615d994,
base400000/entry14D300/x86/2023936bytes,182client20kernel24facade,0unresolved.
RequiredCUnity/CAnimationconsumerprobe passed beforelink. Ownstartup audit/
decoded entry refreshed;exactnewPE TCPfixture→WinMain/engine/D3D/Character/
existingCreate1, debuggerstopatB460A beforeloop;notauth/fullgame. Handledfirstchance
exceptions retainedintrace;no fullstartup equivalence claim.
No blanket159k suites. Canonical20kernels discovery/checkpoint PARTIAL.
Next063 ordinary text-board/scrollbar455 (markup/wrapping/metrics/sizing/input),
thenfullCGUIBriefingWindow,actualAvatar/world/frame/feedback/localhandlers/
Tutorial/fourstage. Olditemtail25/camera276/cursor/numeric/errors retained.
Historical061frame/report usedoldGUI;062fixesitsbuttonmapping. M6/M6F/M7/M9OPEN.

## Предыдущий перенос — tutorial-board061

Tutorial-board061: new native/client455_tutorial_board.{h,cpp}, source-owned
CTutorialBoard derives actual CBaseBoard. Ordinary WinMain/Tutorial NOT wired;
own full-object harness only. UI/stage providers explicit, missing rich/key
provider returnsfalse; no empty fake CGUIBriefingWindow. Header's briefing
interface is required future dependency. Initial safe own flags ready1/close0/
busy0 match target InitWindow; constructor's raw uninitialized domain not claimed.
Target window38; first relevantMsg two clock reads, shared unsigned elapsed
strictly>60000 reports. Foreignwindow returns beforeclock. Report56BAE0 sends
group1/op17 with uninitialized1byte payload: host notification only, NOpacket.
Frame decrements shared signedpositive cooldown evenSkip; hiddenwindow input3.
quitRequested &&cooldown0&&!busy&&currentQuest!=0→ND441/ID6003/style3,clearquit,
busy1,cooldown5.1403result1forcefinish,thenbusy0;canceljustbusy0.
Finish incomplete&&ready1&&!force→ND444/ID6001/style3,ready0. Second call,
completedorforce→captureNULL,skip1,stagevt52,input1,unload,Avatarstage3 in order.
1400/1402 setinput0 regardlessresult.1201 closeBlocked blocks; baseclose also
requires nonzeroLPARAM,1202toggle. Message0/1 changes close-block only after
successful realviewcall. Message2/3 uses concrete existing CGUIMessagebox:
_mbsnbcpy serialized lengths,IDs6000/6002,styles3/4,alphaB0,durationFFFFFFFF.
Own1023byte bound rejects unsafe overflow; embeddedNUL/DBCS949 pair/lead checked.
Key FFFF hides;low17→{high,255},{17,high},otherwise{low,high}. Actual key imagesOPEN.
startScript race/2 b/c/a,classw/r/f/s,unload-before-read,ordinal0/sharedrefresh;
3realbw/cr/as prepared,failedloadclears,skipretains. NativeActionsFactory requires
ActionsHost, so shared test fixture060 extracted to native/testing/actions_host.
060rule sources unchanged, shortregression exit0; current lib8671a846…,
PEb17c811d…/entry13F80. Generic own_probe builder unchanged after local experiment.
061 ownPEed4fbf9de21341e7b9a5751cc1fb3c7181e82dc54ab5e318c144dccfd4bd78f4,
entryEBD30,naturalexit0. RealclientGUI objects/text and D3Ddraw; stage/Avatar/
rich-view are TEST fixtures. Actual viewport640×480/17694changed pixels exported;
backbuffer640×500 has extra20rows, excluded from comparison (avoids falsepositives).
PNG viewed: legacy button sprite mappings visibly wrong; modal rendering/font/
layout/input455 NOTaccepted. Rich/paged/portrait/key-image panel stillOPEN.
32functionranges+vtable+selectionstrings equalbothpins;9completeasm;
IDA774fd3f4closed/save. Rawboard-*.json,061-*-asm underartifacts/client455-tutorial.
Reports inventory/client455-tutorial-board-*, research/client455-tutorial-board.md.
Checkpoint PARTIAL, canonical20kernels discovery passed. Production056 SHA56905e68…
unchanged. Next062 actualmodal455 buttons/data/text/input then sharedGUI/full
briefing, actual Avatar/world/frame/input/feedback/localhandlers/joint4stage.
Olditemtail25/camera276/failedUIpoint/equip/numeric/error gaps retained.
M6/M6F/M7/M9 OPEN. No server changes/inputEXE execution.

## Предыдущий перенос — tutorial-actions060

Tutorial-actions060: client455_tutorial_actions.{h,cpp};ActionsHost abstract
extendsSpatialHost;Factory composes0–46. Native recordinghost,NOTrealUI/world.
UI19open21closeforcebit4;20/22waitnotimeout. UI0/63/64→board0,5→7,6→3,11→17;
inventorypage0;skill/forcewindowupdateTab(0,0,1)thenselect0samewindow.25openfinditem
Land4289E0+36→477D10/use4FAA70,missingND284;27directshow;25/27directclose.
Equipmap16AA9C74={5,1,2,6,4,8,7,3,9,9,10,10,11,11,11,46};slot25523skip;
invalid16..25423factoryrefused.25slot12then13;24/26waitnot4FE2B0;26slot12bothempty.
Cursor data6/8originshort,10/12targetshort,14button,15window,16DWORDvalue.
27/31originFFFFFFFF orscreen0..4;28/32default427020/element4272B0 returnDWORDX/Y,
NOTrect;lowWORDsigned targets. UIpoint63 mapsboard1 unlikeUIopen63→0;keepseparate.
Failedhelper canleaveuninitializedcoords;Hostpoint.initialized mustexplicit,
Startfalseifunknown(gap),knownfalse-result retainsforcebit4/continuation.
27/28positiveSetCursorPos offsetorigin+Y21 thenlogicalcoords,negative→5578F0;
31/32exactlogicalcompletion.29stageinputDWORDvt60Tutorial5588A0→owner64;
30mouseShowBOOLvt486233C0(+systemShowCursorwhenconfigured).33missing/projfail
immediate,successmotionandUpdatefalse;34defaultmotion/Updatefalse;externalwritersOPEN.
Combat35mode(kind==1),37flag24308(kind!=0),forcebit4.36trace+locktargettype,
wildcardindex/racefaction/monsterlocalindex;missingmonsterDTaccepts.38feedback
type thenwildcard/type4/skillcode;missingSkillaccepts;Finishclearsctxattack/skill/
targetpair.39privatekind255,ctx.state52unsignedthreshold;counterwritersmeaningOPEN.
AllCombatoperationActive1/0;RF455_GetTutorialCombatParameters typedreadonlyview.
Item40/41tempClone→resolve/create→stackcount200OR45FE90value→item96→serialshared
WORD→tempBoard620 attachitem+serial→emptyInventory/insert.41category18/use then
closeboard3onlyifpreviouslyclosed. Boarddtorbeforeclonedtor;failedlookupnoID.
43/45board7/3 objectifnotlinked→finditemslot→board6link(target255,255,select0).
42underlyingitemfield112wait;44/46link+optionalidentityslotBYTE(q-1),0wrap255.
50functionranges/equip16/2vtablebindings equalbothpins;11completeasm;ID758bbebc
closed/save. Raw artifacts/client455-tutorial/actions-*.json,060-*-asm.
WinProc7D2260decompileexcerptonly,NOTfullacceptance. Ownlib71c8d650.../
PEac630491.../entry13F80 naturalexit0.99files/39864processors prepared +synthetic47,
NOTfullruntime. Recording spatialfixture extracted template native/testing/;
059shortregressionPEc73ed3fe.../entry9B30/lib42c67412...passed. Rules059unchanged.
NormalPE56905e68/182client20kernel23facade unchanged;no broadunchanged suites.
Research/client455-tutorial-actions.md +inventory/client455-tutorial-actions-*.
Next061 actual CTutorialBoard/CGUIBriefingWindow/message0–4 providers,then
Avatar/world/frame/input/feedback/localmessages/joint4stage. Remaining real
host/backend/helper/data-view bindings mandatory,plusfailedUIpoint/equipdomain/
itemtail25/camera276/numeric/error gaps. M6/M6F/M7/M9OPEN.Noserver/inputEXEexecution.

## Предыдущий перенос — tutorial-spatial059

Tutorial-spatial059: new client455_tutorial_spatial.{h,cpp}, SpatialHost pure
interface+factory composition0–18. RecordingHost native;NOTrealworld/Avatar.
Move6/7 mode0marker,only6createpath43EEF0→facevt84(1/12)→state10000001. Update XZdistance<=15
releasesmarker1,NOtimeout. Mode1 remainingDistance=float(unsignedamount),only6
targetsin/cos(yaw*6.283185307/360)*DWORD(amount+2)+position;getterorderX/yaw/Y/Z/yaw.
Mode1remaining<=1OR unsignedelapsed>=20000;mode2forcefinish;type8toggle(mode==1,0).
Position12setpos1/0;13yawvalue[1],1/12;14orbit+dirty;15/16absremaining3,only15
relativecameraaction;allremaining<=1OR20000ms.17Starttrue/Updatefalse default,
18setcameraFloat276(value<=0?75:value),fieldname/providerUNCONFIRMED,notFOV.
Orbitangles+distance,notXYZEuler. Contextfields added operationActive(target+0),
remainingDistance(+8),cameraRemaining(+12/16/20). Realframe decrement notwired.
Move/Creationstartoperation1/Finish0. Creation9 monster17packet,10knownitem25,
11waitcontaineremptyOR20000. ProcessglobalIDsinitialitemWORD3840/monsterDWORD65535,
wrapnaturally;failedlookupdoesnotconsume. TemporaryCItem begin→lookup→dispatch→
end,includingfailedlookup,RAIIscope;both9/10forcefinish evenlookupfalse.
IMPORTANT producer427F90onlyinitializes25itembytes;receiver565A90readsDWORD+25
→46EB70storesitemDWORD676. Tailuninitialized/meaningOPEN;don'tinventzeros;
Host.localItemSpawnKnown25 receivesonlyknownbytes,notactualfullhandler.
Itemmap47pinnedAA9C44,38..46zero;resolver600030rejects>=47. MonsterIndexlowWORD,
coord __ftol2_sse lowAX,marker1358954291. XZx87sum/floatspill/_CIsqrt;direction
float/double spills retained. CRT/error/NaN/allFP domains notfullycertified.
Nativeallmethods/flags/remaining/timeouts/wrap/triangle/nextafter15/Yignore,
getterorder/known17+25/map47/clone lifetime/failedlookup/IDwrap passedexit0.
3BW/CW/AR1235records,946factorycreate/289open; fullpreparestopsfirst>=19.
Ownlib19d337cb.../PEdb7706b3.../entry9B30;058regressionlibdaab7a98.../
PEa95ef0b2.../entry8050passedaftercontextchange. Production56905e68 unchanged;
no broad unchanged suites rerun,canonical20kernels discovery preserved.
32ranges,data/counters/constants/character vtslots equalbothpins,7completeasm.
43EEF0 doesnotcopyposition:decompiler hidespaththis for5EE790;pathcalls worldvt188.
vt84=43D560→7CE550 facesfromcurrent,target via8B4E40→scalarvt88=43D530→7CE360.
OwnedIDA c60c1913/5b89854f/7dedc5cb/cfea0c20 closed/save.
Raw artifacts/client455-tutorial/spatial-*.json,059-*-asm.
Research/client455-tutorial-spatial.md + inventory/client455-tutorial-spatial-*.
Next060 UI19–22/Equip23–26 thenCursor27–34/Combat35–39/Item40–46,board/briefing/
realworldAvatar/localhandlers/joint4stage. Itemtail andframe/providers mandatory
beforefullTutorial acceptance. M6/M6F/M7/M9OPEN.No server/inputEXE execution.

## Предыдущий перенос — tutorial-runtime058

Tutorial-runtime058: own source QBI scheduler/basic message0–4/wait5 в
client455_tutorial_runtime.{h,cpp}. Standalone, НЕ ordinary Tutorial/realhost.
RF455TutorialHost чисто абстрактный; native recording host не реализация UI.
Factory остальных41selectors возвращаетnullptr;prepare атомарно отказывает,
не пропускает команды.3realBW/CW/AR=1235records,728supported/507open ввыборке.
42functionranges+10vtables equalbothpins;7completeasmfunctions. OwnedIDA
f84ad03d closed/save. Source-owned liba758e02c...;PE9618bd36.../entry8100,
naturalexit0. NormalPE56905e68.../182client20kernel23facade unchanged.
Scheduler: atmost1newBegin/tick;current begun&&!done blocksnext;tick begun
unfinished prefix, lastrecorddone+iteratorend decidescompletion, notallrecords.
BaseBegin resetscursor excepttype16 BEFORE Start; failedStart stopsbeforeclock/
state reset. Success captures timeGetTime, sharedstartTime, input11,state52=0,
flags|1. Bit4 skipUpdate andfinish;donebit2 setbeforeFinish. Both Message/Wait
Finish verifiedempty equalbytes. Refresh429F70 resetsidFFFFFFFF,countWORD0,
flags/iterator/current, preserveslist andprocessorprivate fields;explicit
GetQBI(index) thennull bycount0,defaultFFFF returnscurrent. Explicitquestrefresh
doesn'tselectcurrentordinal. Completioncallback mayclear runtime;noaccessafter.
Wait0 inputBYTE vsfullDWORD,consumes→11;Wait1 unsignedelapsed>=value,wrap;
Wait2 values4..10 exact board17 fields1892/1896,AvatarBYTE614/612,DWORD24308.
Gameplay names/providers unknown; don't guess. Owner52meaning/othercontext,
OOM/arbitrarycallback invalidation/rawreload domains open. fixedMessage4 with
datatype0..3 foreignpointer execution rejected,not claimedasequivalence.
Native checkedqueue/gates/retry/refresh/private retention/onebegin/last-only,
sharedtimerlaterreset/separateclockreads/equality/wrap,conditions,unloadcallback.
Fix057/058 reports: library MUSTstring+library_sha256,notnestedobject;otherwise
prepare.kernel_sources crashesonunhashabledict. Metadata writers/checkpoints
updated;short057+058probes refreshed;canonical20kernels discovery passed.
Parser057code unchanged;itscurrentlib5edb0780.../PEb55131f6.../entryBB30.
Research/client455-tutorial-runtime.md +inventory/client455-tutorial-runtime-*.
Raw artifacts/client455-tutorial/runtime-reference.json,runtime-vtables.json,
058-*-asm.json, scheduler/processor decompile. Next059 restCQBI Position/Move/
Creation first,thenUI/Equip/Cursor/Combat/Item,board/briefing,realAvatar/scene/
localhandlers/joint4stage. M6/M6F/M7/M9OPEN.No server/inputEXE execution.

## Предыдущий перенос — tutorial-scripts057

Tutorial-scripts057: самостоятельный source-owned SCP reader/writer47selectors.
Не подключён к ordinary Tutorial/Avatar и не заменяет его исполнение. Legacy
QUEST_INFO28types имеет другую нумерацию; не отправлять в него новые записи.
Новые scripts/native/client455_tutorial_script.{h,cpp} хранят typed common/message
fields и raw fixed payload/padding; не overlay target processor objects.
Селектор и сохранённый dataType раздельные; fixed ID WORDoffset2, rich IDpacked.
Всего99race/classfiles/9folders:812quests/39864instructions/36818strings/
1471548textbytes.37real selectors; отсутствующие17/18/22/28/30/31/33/34/43/45
synthetic. Decode→encode realbytes и independentPython semantic serialization
совпали.47selectorfixture1069prefixes отвергнуты атомарно; zero/trailer,
unknown/count/encodingbounds,semantic edits/maxWORDstring прошли. Nativeexit0.
Generic DataTable/ko-kr/Tutorial.scp несовместим с reader:offset1215/request8365/
size4742; происхождение неизвестно, targetboardformatter не генерирует егоимя.
Audit хранит отдельную запись, native отвергает без изменения документа.
19functionranges/10processor RTTI/prefixes b/c/a,suffixes w/r/f/s equalbothpins.
Target RVA2AD30 loader,2A340 recordreader,1F1050 string,A5EC0 boardselection.
OwnedIDA c257ee18,b0309dad closed/save. Rawignored artifacts/client455-tutorial/
scripts-reference.json, qbi-asm.json(full700instructions),script-selection.json,
methods-full.json; initial reference.json export has some truncated functions,
use methods-full for saved complete Frame/Input/camera-sequence/board functions.
Standalone lib4522a59b...; nativePEc3243ee3.../entryBB30. NormalPE/libraries056
unchanged; no broad unchanged native suites rerun. Current SCP gatePARTIAL.
Research/client455-tutorial-scripts.md and inventory/client455-tutorial-scripts-*
contain evidence. Next058: scheduler/quest-state/CQBI processors, board/briefing,
then Avatar/scene/client-localmessages andjoint4stage. All commands must be
implemented before acceptance; wire parsing alone is not working Tutorial.
M6/M6F/M7/M9OPEN. No server/inputEXE execution.

## Предыдущий перенос — camera056

Camera056: ordinary CAniCamera::LoadAniCamera/Play now455,basederivedengine
5thoverlay anicamera.cpp;noheaderABI mix,classsize56/ownedprivate80camera
record plus typedFOVdocument registry;targetprivatecamera88. Engine033source/
libraryunchanged. Newparser supports1.2 and1.3FOV20bytekeys,node349 wire100+
tracks16/20,dummyname/parent64. SourcecurrentHeaderusesparentmacro;newdocfield
mustbe parentName. Registrycontainer processlifetime toavoidCRTdestructororder;
Release erasesdoc;originaldestructorstill empty,explicitRelease required.
Actual4realCAM versions1.2:bellato9,cora9,accretia8,lobby24=50cameras,89nodes,
42dummies. Synthetic1.3 adds1camera/1node/FOVkeys. Nativefullobjectprobe
roundtripallbytes/typedmembermaterialization/actualD3Dprojection/FOV*.788/
reverse/loop/stop/releaseDmallocbalance naturalexit0. Malformed/truncation/
size_t-to-intx86allocationbounds checked;atomicfailure differsunsafeoriginal.
Playback4D1DC0:forward>=end/30;flag0restart setsseconds=float(startFrame),
reverse<=0(notend/30);flag0setsend/30+clockreset,nonzeroflag0;terminalfalse.
Pause clock0reads exceptlooprestart;normalrestartmay2reads. Asm verified.
FOVhelper4D1FC0 interpolationatseconds*30/value0*.788,beforefirstselectslast.
SeparateFOVAPItested,buttargetengineconsumer8D5FF0 notyetported;DON'T insert
perframeFOVupdateunconditionallyinPlay. LegacyGetAniMatrix/dummy numeric
domains/cycles remainopen. Fullcamera/Tutorial/fourstage/Avatar notaccepted.

FullownPE56905e68ce0746c5367db5e08cdda8ee948a26196091d11d4777c6c116a697cf,
x86/base400000/entry14ACA0/2022912bytes,182client/20kernel/23facade,0unresolved.
Derivedengine91bdf0c7f76b24c353aef8b3195fc48626e01f2040b1a5c1ccf0bf7c1ed7eb01,
67units/5overlays;baseline033unchanged. ExactownTCP→engine/D3D/Character/
existingCreate1passed;Russia remainsbeforeConnect.12ranges equalbothpins,
ownedIDAc449e061 closed/save. Rawignoredartifacts/client455-camera/reference.json
andplayback-branches.json;research/client455-camera.md;camera-{reference,native,
checkpoint}.json. Next057 Tutorial scene/Avatar/UI/localhandlers/fourstage;
M6/M6F/M7/M9 OPEN. No server/inputEXE execution.
Все22 scoped checkpoints завершились0/PARTIAL на текущей сборке; короткие
зависимые native probes обновлены, прежние большие unchanged suites не запускались.
Для отчётов пользователю: техническая основа и отдельные подсистемы восстановлены,
но сквозной игровой сценарий455 ещё не принят. Полный объём поведения не измерен;
число assertions, файлов и закрытых подготовительных этапов не переводить в процент.

## Предыдущий перенос — progress-base055

Progress-base055: normal CGameProgress now24bytesx86:vt/fourBOOL/nextDWORD.
Explicit SetNextStage455/GetNextStage455/RequestStageExit455;Init retainsnext.
Ownconstructor defaultFFFFFFFF differsfrom targetuninitializeddomain,explicitgap.
BaseMainLoop now Input→ifexitreturn1→FrameMove→Render→realparticlecountreset→0.
IgnoresBOOLactive (owned API retained);virtualreturnsignored. Frameexit still
renders/resets,observedafter nextInput. Title constructorSetNext1. Current
MainAppfactory remains3/modulo;newnextfield NOT wiredtoactualtransitionsyet.
Don'tmap legacyMainGame2 to targetTutorial2;fullfactory/Avatar/Tutorial joint
migration remainsmandatory. ActualTitle lifecycle/input remainslegacy.

Nativefullobjectprobe verified5next values/Initretention,baseCreate/Destroy,
realvirtualorder/inactiveRendering/input/already/frameexit andactual existing
particlecounts0/31/1023;naturalexit0. Currentparticles fixed1024,targetvector
CHPARTICLEstride7836/count7832;dynamicowner notported,notfullparticleparity.
FullownPE5302f71a07bb7b895971dc18e43ae676d2901aeaf7fa737d79d9d0c86144d8b5,
x86/base400000/entry14A750/2012160bytes,182client/20kernel/22facade,0unresolved.
Engine879f9b75 unchanged. Exactownstartup TCP→engine/D3D/Character/existingCreate1
passed;Russia remainsbeforeConnect. No fullgame-loop/authentication acceptance.
18function ranges equalbothpins;ownedIDA3bc31778 closed/save=true. Rawignored
artifacts/client455-progress-base/reference.json plus tutorial-input-tail.json.
SevenTutorialmethods pinned/read:Create5586D0,Destroy558AE0,Frame558B80,
Load5594D0,Unload559750,device559810,input5598C0. Race cameras/startcoordinates
andmanyWorld/UI/Avatar dependencies visible;notimplemented. Useinstructionsfor
decompilerlocals/this,do notreuseguessedarray bounds. research/client455-progress-base.md,
inventory/client455-progress-base-{reference,checkpoint}.json andprogress-native.json.
Next056 Tutorial/world/UI/Avatar/localhandlers→full4stage/explicittransition;
M6/M6F/M7/M9OPEN. CompleteTutorial includedinM9;noserverwork.
Все21scoped checkpoints наcurrent evidence завершились0/PARTIAL;короткие
зависимые native probes обновлены,большие unchanged historicalsuites не
повторялись. Ownednativeпроцессовнет;Gitworkingtreeпослеcommitдолженбытьчистым.

## Предыдущий аудит — progress054

Progress054 — static reverse, runtime не менялся. 28function ranges и4primary
vtable/COL/type descriptor совпали в обоих455pins; имена подтвержденыPE RTTI.
Stage0 CGP_Title ctor557B60/vtAB0E14;1 CGP_LogIn53B860/AB0014;
2 CGP_Tutorial5584D0/AB0F9C;3 CGP_MainGame5454E0/AB0324. Tutorial derivesMainGame.
7D1C30: requested2→3 if AvatarDWORD20168 nonzero,otherwiseTutorial. 7D1370:
после successfulstageCreate записывает AvatarBYTE20165 через4A6160,затем
вызываетMainLoop;следующий stage читаетDWORDstage+20 (7D1470),неmodulo.
Title задаётnext1 через53F6B0. Режим2 в41E130/562E80/562BE0=Tutorial,
НЕ replay;не использовать старый GPI_MAIN_GAME2 как targetTutorial2.
562BE0: stage2 && Avatar20168==0→564520 clienttutorial dispatcher;остальные
путиactualtransport. Fulltutorialhandlers иAvatarstate ещёоткрыты.
Старая normal база MAX_GAME_PROGRESS3/GPI_MAIN_GAME2/modulo, Tutorialfactory
отсутствует. Jointstage migration обязательна,неподменятьучебныйрежиммиром.

5F0EB0..5F0FD1 определён вownedIDB;INI MASTER_SERVERreader имеет0IDAxrefs,
0E8/E9rawcandidates и0absoluteaddressbytes в обоихpins. Computedcalls UNKNOWN.
Не добавлять его вWinMain на основе одного setter! Previousreplay/mandatory
INIprovider hypotheses сняты. Source serverType0 сохраняется,неclaimfull.
Networkstate436232 writers42DCA0:164470 делает2→3/7→8 поsocketinfoflag48;
1643C0 делает3→4/53B430;остальныеwriterslogin/world. Fullstate migrationopen.
research/client455-progress.md,inventory/client455-progress-reference.json,
scripts/audit_client455_progress.py;rawignoredartifacts/client455-progress/.
Owned3915694c closed/save=true. No inputEXE/servermodified;no nativerebuild,
ownPEa12b10f7.../entry14A980 из053неизменён. M6/M6F/M7/M9OPEN.
Next055: stagefoundation/explicitnext/Avatar/Tutorial/localhandlers,then
targetLoginUI/Create/worldtransitions. FullTutorial входитвM6F/M9scope.

## Предыдущий реализованный результат — account053

Account053: group21/op12 на accept endpoint0; op13 даёт BYTE+1/WORD+3,
не новые AESkeys. Join84/PushClose88=ID51/PW33[/zero4]; login342, Taiwan8
ticket257@85, transform BYTE(byte+delta)^LOWBYTE(mask), затем overwrite84
serverType436024. Loginreply50: result/account, clearPW33 кромеresult5.
Worldreply header3/dataSize, signextendedcount; typed records72/capacity300,
signedvalue/name64/status1/pad3. Boundedcount0..127/names1..64; validatebefore
mutation, retainname bytesafter declaredspan. SelectLE16/storedindex,reply24
setsendpoint1IP/port/keys16. Ordinary dispatcher uses decodedframe length.
Pending/tick,F100/ND305/style5: show active0!=2 OR436232==4;close active0!=2
ORmode!=-1. Mode initial=-1;allwritersnotyetported. New normal packer supports
mode2skip as explicit argument;runtime bridge/provider stillopen. SERVER_TYPE
setter5F0FE0 confirmedfrom MASTER_SERVER ini default0;invocation remainsopen.

OwnPEa12b10f729e561f075ba67ea36b575bee9f8110434449ec40b7d161f2ae10ad1,
x86/base400000/entry14A980/2012672bytes,182client/20kernel/22facade,0unresolved.
Engine879f9b75 unchanged. Fullobject native fixture actualsend/ring/fragmented
wrapreceive/dispatch/UIpending/zonepredicates naturalexit0. NoTCP/auth in that
fixture;separate realTCP052/codec051 regressions passed. ExactownWinMain still
reaches D3D/Character/existingCreate1 then controlledstopbeforeloop. Russia
stillbeforeConnect;don'tremap endpoint0→1 withoutproof.
26functions/11selectors equalbothpins;ownedIDAf2469475 closed/save=true.
research/client455-account.md;inventory/client455-account-{reference,native,
checkpoint}.json. Raw ignoredartifacts/client455-account/reference-final.json.
M6/M6F/M7/M9 OPEN. Next054 providers/35handlers→fullloginUI/remainingprotocols.
Все20scoped checkpoint scripts на текущих evidence завершились0/PARTIAL;
короткие зависимые native/regression probes обновлены, большие неизменённые
исторические math/kernel suites не повторялись. Native процессов не осталось.

## Предыдущий результат — connection052

Connection052: обычный WinMain вызывает actual CMainApp::ConnectNetwork455 до
InitR3Engine. Endpoint1/process0, global ./DataTable/ClientSystem.ini Network/
ConnectTime default90sec*1000DWORDwrap. Slot284 FALSE во всех11профилях.
Raw!=0→ND6BE/MessageBox/false. Raw0→clock before events-only PumpEvents455,
connected1 before unsigned elapsed>budget, затем Sleep4; timeout→WSAerror/
NDBFA/ShowWindow hide/MessageBox/false. Бюджет после blocking Connect, не до.
_Receipt теперь максимум102accept/102close/102ready, включая failed accepts;
callback только elapsed>1000 (было legacy>=1000). Pump не разбирает пакеты и
не вызывает UserLoop. В broader OnLoop остаются ещё legacy/gaps.

Реальные native success/raw-error/timeout/Russian argv cases проверены;
getpeername подтверждает собственный TCP-port. Fake clocks — только unit
границы/rollover; production использует настоящее время/сеть. Helper закрывает
реальные error dialogs через hook собственного потока+timer, текст сверяется
с NDLanguage. API/ветки/возвраты в production не подменяются. Три процесса exit0.
TCPfixture временный loopback/zeroRFresponses, все sockets/threads закрыты.

IMPORTANT: reference Russia argv setsendpoint0, initialConnect readsendpoint1,
gettersraw, Initzeros. У own текущего source endpoint1 пуст→timeout. Это НЕ
доказательство полного targetcountry failure:35handler ctors/countryproviders
ещё не все восстановлены, возможные side effects UNKNOWN. Не remap0→1 ради
успеха теста. Exact Russian WinMain останавливается передConnect (не Miles).
Language/launcher gates учитывают эту честную границу; native case проверяет
текущий настоящий timeout. Korean CCR trace проходит TCP→engine/Miles/D3D/
existingCreate=1. Noauth/gameplay acceptance.

OwnPE0733cce1ed6e77e2d70646ddc281129629d029421888cda6adff2f01a433a53a,
x86/base400000/entry14a3f0/2012160bytes;182client/20kernel/21facade,0unresolved.
Engine879f9b75 unchanged. BeforeConnectownRVA B4435→B38E0, after B443A;
afterSound B4458, D3D B4468, existingCreate EAX1 at B447A (callB4475→B3AC0).
15functions+11vtables equalbothpins; IDAbed1c136 closed/save=true.
research/client455-connection.md; audit/probe/checkpoint_client455_connection.py.
Raw artifacts/client455-connection/reference.json. M6/M6F/M7/M9 OPEN.
HistoricalNext053: gatecrypto569CD0/569D30 downstream packet state, full35handlers/
wire layouts/countryproviders, затем fulllogin/UI/game tables/gameplay.

## Предыдущий результат — network-codec051

Network-codec051: AES192-CBC с разными ключами отправки/приёма подключён к
normal CNetProcess::LoadSendMsg/_PopRecvMsg. Plain header LE16length/group/op;
encrypted outer LE16length/BYTEpad/ciphertext. IV0 на каждый пакет, zero-padding
без PKCS; aligned packet без дополнительного блока. Receive consumes wireSize,
а dispatch получает inner header. Group21 выключает process0cipher, другие
группы включают; это действие настоящего CNetworkMgr::SendNetMessage проверено.
33code/7data ranges equalbothpins. Default schedules208bytes (rounds12) verified
standard expansion; inverse schedule converted and verified, directional keys
DIFFERENT. Generated private header underwork/network455; SHA in reference,
sourceAES production, CNG только test oracle. Ключи в Git не добавлены.

Два configuredprocesses, capacity6. _NET_BUFFER80bytes, dynamic main+extra,
borrowed shared scratch, receive20000/send1000000. Реальный sender/receiver
проверен с фрагментацией и wrap, native exit0. Старые12gamehandlers остаются;
queued route/full236config semantics/send filters/throttle/internal security/
threads/Close остаются OPEN. Target source slots2 configpointer Src+472 plus
selector writes228/232 = stackoverwrite; ownsource это не воспроизводит.

OwnPE71e644eb7948f54dcee7528ef69cefc59403d23cc49bfd656c77730abda5d405,
x86/base400000/entry149ef0/2008576bytes;182client/20kernel/20facade,0unresolved.
Engine879f9b75 unchanged. Korean/Russian WinMain startup и existingCreateEAX1
atownRVA B40D8 (callB40D3→B3730), controlledstop beforegame-loop.
IDA4c89c7ab closed/save=true; artifacts/client455-network-codec/reference.json
иaes-block-tails.json. Audit/probe/checkpoint_client455_network_codec.py;
research/client455-network-codec.md. M6/M6F/M7/M9 OPEN.
Next052: event/accept sequencing и настоящий preengineConnect wait/pump;
затем gatecrypto request/response569CD0/569D30, fullprotocol/UI/login.

## Предыдущий результат — bootstrap050

Bootstrap050: FG/USEFG nSize4→atol rawint иcountry instance policy восстановлены.
WinMain Nation→Launcher→Language→FG→actualNetworkCreate→Instance→Engine/Miles.
LateNetworkCreate удалён изexistingCreate:actualearlydebugstringровноодинраз.
Instancebypass2/3/7/8;Japan5неbypass. basenameuppercase13RF_ONLINE.BIN,Toolhelp
count>1reject,Global\\_R_F_is_execute_ existingreject;targetnullmutexaccepted.
Handle сохраняетсядовыхода;ownCRTзакрывает. FGpurposebeyondstoredintUNKNOWN.

Connect562350/RVA162350:activeBYTE6/connectedDWORD4,rawint0success,-1existing;
errorclearsrequestedconnected/preservesactive. Endpoint2/logout directcallback
alwaysprocess0;normalbridgepublishesnewactivebeforeactualcallback. Legacy
BOOLConnectтеперьобёрткаraw==0;source normalCreate/transportещё12handlers/
oneprocess,455Create35handlers/twoconfigs/capacity6. GateAccept569CD0crypto,
queuedtransport236config/framing/cipher/CloseиprotocolещёOPEN. WireID/PW13 vs
state50/32unchangedgap. FullConnectToServer7D1150wait/pumpbeforeengineNOTwired.

IMPORTANT:455VA8B0505closesocket→8B050BWSAGetLastError. IndependentrealWinSock
oracleandactualownTCPclosedport:10061beforeclose,0afterclose,connectedfalse.
Неисправлятьпорядоккакобычныйbug:этоtargetquirk,неуспешное соединение/auth.
Actualinvalidprocess5returns10022;real logoutendpoint1callbacknosend passes.
NativeownhelperRF_Online.bin/secondownchild/name/process/mutex/FG/state all
naturalexit0. Нетслушающегосервиса/эмулятора,оригинальныеEXEнеисполнялись.

28ranges+11countryvtablesequalbothpins. IDAd716d7fa/8102ad50closed/save=true.
Rawartifacts/client455-bootstrap/{reference,network-decompilation,tcp-assembly}.json;
audit/probe/checkpoint_client455_bootstrap.py;research/client455-bootstrap.md.
OwnPE3b93b0ebab349dd0b2d41d970918d4933176eb33431ec547cb7a61db1439d738,
x86/base400000/entry149010/2004992bytes;182client/20kernel/19facade,0unresolved.
Derivedengine879f9b75...unchanged. ActualKorea/RussiaearlybootstrapandD3D;
existingCreateEAX1atownRVA B3F88,callB3F83→B35E0;controlledstopbeforegame-loop.
17scopedgatesPASS/PARTIAL,oldlargehistorical suitesnotrerun.M6/M6F/M7/M9OPEN.
Next051:client455transport/config/Accept/framing/cipher;thenpreenginewait,
targetCreate/video/BGM/fullUI/login/tables;FT/ANSI/IME/ILevel/world/shutdown.

## Предыдущий результат — launcher049

Launcher049:19function ranges+11full296bytecountryETCActionvtables identical
bothpinnedPE. Slot196:9nations8392E0/RVA4392E0 CCRfile;Russia836CB0/RVA436CB0,
Europe83B4F0/RVA43B4F0 argc5. Europe CString temporary onlycopieshostname;
bothargvmethods inet_addr,noDNS,atol→WORD,endpoint0,id50/password32. Invalid
IP/portnumeric notvalidatedbytarget;argc!=5false. Fullproviders stillOPEN.
CCR93byte layout offsets0ip/4port/6id51/57account/61keys16/77worldWORD/
79personalRef/83premium/87modeDWORD/91nationWORD. XOR masks pinnedinstructions;
premium83..86 forced0,targetcallssettersBEFOREnationcomparison. Source own
statekeepsdecodedfields evenfalse;normalbridge commitsacceptedprofilesonly,
soerror-sideeffects notidentical/explicitgap. Missing/short/exclusive-sharing/
extra data checked. Identifier5E5920 truncates50andzeroes51,password32/33;
source boundedstrlen/size0guard differsunsafe/OOM domains. No authsuccessfake.

New client455_launcher.h/.cpp plus bridge.inc inordinaryMainApp.GetDataFromLauncher.
WinMain nowNation→GetDataFromLauncher→Language→Engine;lateCreate readremoved.
Actual memberCNetworkMgr receivesendpoint/id/password(ifargv)/account+keys(ifCCR).
Worldindex/personal/premium/mode preservedinsource455state,consumersstillOPEN.
Normal CNetworkMgr IDstorage51/password33+confirmedboundedsetter,Initsizeof;
oldnetworkwire structs stillmax_id_len12/max_pw_len12/copied13bytes. Auth/wire
NOTaccepted andmustportbeforegameplay. No actualaccounts/credentials read/stored.
DefaultSet.tmp/argv fixtures syntheticloopbackonly,no connection attempted.

MSVCinlinedCreate afterlateblockremoved;explicit__declspec(noinline) nowkeeps
one-timeproductioninitboundary fordiagnostics withoutresult/branchchange.
Ownentryaudit decodesafterCALL Create now;oldliteral-PUSH boundaryremoved.
OwnPE SHAa64601c891cade91395fa285945320c115d15aa7621258391b4571e0112dd64a,
x86/base400000/entry148860/2001408bytes;182client/20kernel/17facade,
0unresolved;derivedengine879f9b75... unchanged. No originals/server changes.
Nativefull-objectlauncher probes Korea/Russia/Europe:allnaturalexit0,realmember
setter/getter checks incl50/32strings;9CCRcountryprofiles,19shortfileboundaries,
sharing/missing/extra/argccount/inet/portcases. NeitherNetworkCreate norconnect.
Labwork/m9/a20f2085. ActualWinMainKorea/Russia eventorderlauncher beforeNDLanguage,
Miles1. Debuggerforwardsonlystagedlauncher-commandline.txt toownchild;itdoesnot
readuserlauncherdata. Existingnativefont/sprite helpers useownentry,notWinMain.

Exact ownPE existingCreate actuallyreturned1 atRVA B3DB4 (CALLB3DAF,targetB3440).
CLIdeviceprobe --after-create replaces --before-launcher;rawmarkerafter_client_create.
Latestlabwork/m9/a64601c8/ui-startup001;device53E4B80==Characterdevice,ownerA6A36F0.
StopE0434200 beforefilter/game-loop/clientconnect;NOTnaturalexit/full455Create.
Rawdecomp/slots/asm artifacts/client455-launcher;IDA f2fdf71d closedsave=true.
Core/GUI/lifecycle/shortmodel/effects/shadow/clock/accounting testsand16scoped
checkpoints PASS/PARTIAL;font/sprite/otherframes unchanged. M6/M6F/M7/M9OPEN.

Next050:targetFG_CB7D0CD0/instance7CF8A0/NetworkCreate7D10A0/Connect7D1150→562350
andactualclientwire/stateflow. Targetnetwork/create/connect happensBEFOREengine;
ownstilllegacybeyondnewlauncher ordering. Nofakeauth/no serverimplementation.
Offlineclientpacketfixtures first;worldindex/personal/premium/mode remaining
consumers,alltargetmanagers/video/fullUI/gameTables/FT/ANSI/IME/ILevel/shutdown
remainrequiredM6. No blockingconditionrequiring userinput now.

## Предыдущий результат — sprites048

Sprites048: target filenames tableBDB6A0/RVA7DB6A0 (55×128),path7B0110/RVA3B0110
uses ./SpriteImage/<nationFolder>/<name>,_access thenCommon evenifbothmissing;
rejectID>=55. New client455_sprites.h/.cpp source module,16normalfacadeCPPs.
Target IDs differ fromlegacy (loading2/login3/item8/unitparts19);onlymouse0/
common1 ordinaryCSpriteMgr startup calls bridged. OtherUI/layout/slots remain
OPEN,doNOTremapoldgroupsbyguessing. Target pathreplacementcache lifecycle not
ported;selectedsame-path cache reuse verified. CCharacterDataMgr creator5E1920
ctor5FA190/Init5FA370 onlyallocation/init,no tableIO atthatCreateboundary.

Recovered GetDDSTexFromBuffer target8F2E70/RVA4F2E70 in new fourth derivedengine
overlay r3d3dtex.cpp via scripts/native/client455_sprite_texture.inc. Supports
DXT1/DXT5/ARGB32/R5G6B5/A1R5G5B5;one managedtexture,contiguouspayloadcopy;
noncompressed secondmanagedtexture+surface TRIANGLE roundtrip andpitch guard.
Decompiler has wrong stack deltas afterimportedcalls;manuallyfollowed actual
ESP to distinguishT1/T2/surfaces in artifacts/client455-sprites/texture-assembly.
Source bounds publishedstDebugSize andchecksfailedHRESULT/cleansresources;
unsafe/error/OOM domains notclaimedidentical. Legacy033source/library preserved.
Derivedengine67units/4CPP overlays SHA879f9b754d229f3570913d9256327e3ddf0231881efc793e68480d1067814cec.
FullownPE SHAd431094dfee0ceb2ba854c8dc71f2eaacdaf08909c0d57f1cffc1b8103b1fa47,
x86/base400000/entry148390/1999360bytes,182client/20kernel/16facade,0unresolved.

Actual normal CMainApp.LoadData/UnloadData invoked through compiler-typed method
pointers in ownfull-object lab;real memberSpriteMgr+Screen pointers published
exactly asCreate does. FullCreate/WinMain notrun inthislab. ActualCGUIMouse and
Commonbutton drawn;all562selected frame textures eachKorea/Russia matchrealSPR
payloadbytes andmetadata across4formats;bothprocesses naturalexit0/deviceRefs
baselinepreserved. SourceSPR reader remainslegacy,notfullanimation/errorcertified.
4realSPR files losslessroundtrip;55binary-derivednames/bounds/fallback tested.
Labs work/m9/315bb2d7/sprites-{ko-kr,ru-ru}001;previewsviewed;backbuffer640×500
vsviewport480 remainsopen. Font/othermodel/effect/shadow frames preserved.

ExactownfullPE separatelypassed all existingclientCreate/UIinit/LoadData/title
allocation tobeforelegacylauncher I/O atownRVA B354A. Ownentryaudit decodesPUSH
ofuniqueDefaultSet.tmp literal andfollowingCreateFileA IATcall;not fixedoffset
or missing(inlined)GetDataFromLauncher symbol. Debugger optional7thargument
labels before_launcher;restorescodebyte,reads Characterdevice,thencontrolled
TerminateProcessE0434200. ThisrunNOTnaturalexit/fullCreate/target455UI acceptance.
Latestlab work/m9/d431094d/ui-startup002;actualdevice51dbf60==Characterdevice,
ownerA614720. Allfontregistrationscleaned. No launcher/accountfile staged/read.
Nativeearly/device/Create/Korea/Russia/font/lifecycle andshortdependentregressions
passed;15scopedcheckpoints PASS/PARTIAL.M6/M6F/M7/M9OPEN. IDA64d5aa70 closed/save.
Detailedresearch/inventory client455-sprites.*,UIrun client455-ui-startup-native.

Next049:targetlauncher/bootstrap7D04E0 contracts/order/errorpaths. Legacy
GetDataFromLauncher does uncheckedDefaultSet.tmp/CreateFile/ReadFile andoldschema;
doNOTcontinueitwithmissinginput orfakeauthsuccess. Pin455nation→launcher→
language→FG_CB→clientnetwork→engine/BGM;ownofflinefixtures first. Then target
managers/video/fullCreate andloginUI. Fullgametables arestillrequiredlater.
OtherUI/FT/ANSI/text/IME/layout/ILevel/world/network/shutdown remainM6queue.

## Предыдущий результат — lifecycle047

Lifecycle047: только подтверждённая ветка null-level UnloadLevel перенесена
в normal/source/cland.cpp генератором prepare_client455_normal.py; исходная
база и engine033 не изменены. Target x86/base400000: ctor7C78E0/Init7C79F0
обнуляет owner, dtor7C7970→Destroy7C82C0→Unload7C8F30, где CMP[owner],0
при null возвращает FALSE до любых cleanup/global writes (RVA3C8F3F).
Девять диапазонов и default ILevel vtable совпали в обоих pinned PE.
Target Create7C7AC0 выделяет8байт wrapper7C7B60; его release slot40=7C7CB0
пустой. Это НЕ старый полный CLevel. Полный owner/world port ещё обязателен;
created-level effects order/global clearing/extra containers не перенесены.

Собственная RF_Online.bin SHA11833d1e9d58d0f352a211bb92d5d84423a6f5a21fb3a721eab82f62bf9d299a,
x86/base400000/entryRVA1485A0,1998336bytes;182client/20kernel/15facade,
0unresolved. Engine d0ef3b09... прежний. Native lifecycle helper линкует полный
normal object set с собственным console entry. Реальный глобальный CMainApp
и его CLand: uncreated, engine-only, created→Destroy→Destroy; все три процесса
естественно exit0, debugger/TerminateProcess не используются. Full WinMain и
full CMainApp::Create не выполнялись. Helper SHA d0e0036d...;lab work/m9/d0e0036d.
В font probe удалена специальная инициализация Land: Korean/Russian CGUIText
по-прежнему дают прежние кадры и оба процесса exit0. Legacy normal created
cleanup — регрессия сохранения текущего поведения, не доказательство455ILevel.
Точная новая fullPE прошла прежние startup/device/partialCreate checkpoints
(в этих отдельных запусках остаётся контролируемая остановка отладчиком).
Короткие consumer/ANI/BBX/effect/shadow/counters/clock сценарии прошли,
14scoped checkpoints PASS/PARTIAL;M6/M6F/M7/M9OPEN. IDAdae004fd closed/save=true.
Research/inventory: client455-lifecycle.*;rawdecomp artifacts/client455-lifecycle/.

Далее048: normal _CreateCharDataMgr/global.cpp и действительные таблицы455,
порядок/формат эталона и продвижение полного Create к интерфейсу входа.
Не обходить неперенесённые readers. Full typed ILevel/world, FT/ANSI/text/IME/
layout, launcher/FG_CB/network/BGM и shutdown остаются обязательной очередьюM6.

## Предыдущий результат — font046

Font046: replaced activelegacyr3texttail with real455GDI/Unicode bridge;
033engine/source preserved,derived67units now3CPPoverlays(kernel,wrapper,text).
LibrarySHA d0ef3b09bf260a5d513ceb7fad6468b5dcda5cfe5ed5108eaab445e746ee2b3a.
Font settings8C5A80 strncpy250 twice into256names;points9/unusedheight12/
charset appliedin languageinit BEFORENDload. New font_settings/module CPPs
inactualnormalfacade15units;182client/20kernel;full link0unresolved.
GDIref9067E0 DIB-3points,CreateFontA selectedcharset/quality0/pitch0,measurew
cell;905920 D3DXformat26managed;Unicodecache905CF0/906C10/906DD0 pixelwidth+
WCHARcapacity/roundrobin/ExtTextOutW/alpha4. Draw906F60/907710 UVclip,6vertices,
FVF324/stride28,shadow2/outline9/bold2,postblendFALSE/stickylinear0x400.
Normal3fonts bymem100/160m,16point1024x128,24point1024x512;auxTahomaorA010.
FT8C5C60/ANSIcache/fulltextAPI/IME/layout stillOPEN;doNOTclaimfontcomplete.
Source-ownRAII/freeunusedinitialstateblocks differsoriginalleak/OOM domains.
Native full-object textprobe:actual CMainAppdevice+CGUIText::Draw on NDLanguage
Korea/Russia. Frames==directwideAPI;independentGDI metrics/atlas pixels equal;
cachehits/eviction/poststate verified. Viewporttextpixels151/179 (notblacktail).
Actualbackbuffer640x500 vsviewportheight480 separatewindow sizinggap.
Probe uses compiler-typed explicit-instantiation memberpointer to callactual
m_cLand.Create beforeexit,nochangedclassdefinition/guessedoffset. FullGameCreate
NOTcalled;oldtablesnotread. Bothprobes exit0;BMPviewed Hangul/Cyrillic readable.
First incomplete-lab exit exposed old~CLand Destroy→UnloadLevel nullLevel AV:
ownRVA7DD9C READnull+158h;raw work/m9/e73bb511/font-ko-kr001/exception.json.
Production early-abort/lifecycle stillOPEN;do nothidebyexitingearly/successstub.
Own PE88942d085c1de3a349c337b51a91a3ca311e9522b112f824fc2105ebfa85289f,
1998336B/x86/base400000/entry1485A0.MainB3D40,soundB3D89,D3DB3D9C,charDataB3469.
work/m9/88942d08 normal startup/device/Create passed;Font:GDI:129:0 inactual
trace. CharacterownerA2F3060/device516afa0==app. controlledexitE0434200 observed.
AdditionalhandledfirstchanceC++exceptions afterD3DX,font init no2ndchance.
System010TTF copies staged;device lab removesitsfontregistration=true after
kill;bothfont/device scripts cleanupownfontpath in finally evenonfailure.
ShortANI/BBX/model/effect/shadow/clock/accounting regressions PASS,oldframes
equal/COM/Dmalloc0.13scoped checkpoints PASS/PARTIAL;M6/M6F/M7/M9OPEN.
IDAa9adfb47 closed/save=true;rawartifacts/client455-font;21bodyranges equalboth
pins in font-reference.json. Detailed research/client455-font.md;current
GUI frames/ownedrunpaths in font-native.json (probe PE hash changes onrelink).
Previous045 wasprogress;046addsactualnormal text source/GUI pixel evidence.
Next047: pin/restoreCLand/CMainAppearly-abort/lifecycle,thenfullCreate/data/UI/
launcher. KeepFT/ANSI/textmetrics/IME requiredM6queue beforeM6F. TargetLandCreate
7C7AC0 alloc8byteCLevelwrappervia7C7B60,notoldfullCLevellayout;needtypedport/
correctownership beforeclaimingdestroy. CMainAppDestroy7D1E70,Create7D18B0 cached
underfontartifacts;many455managercalls alreadylisted there. Noblocker/userinput.

Предыдущий результат — language045:

Language045: EDF29header/DWORDsize/payload/256encodedkey;key alternating-/+
digit1<<((i+1)%8),reverse256,swapadjacent;payload even-key/odd+key[(i+1)%256].
Reference5EEC00/5EEC90/5EED90/5EEF00/5EF000 andND603130/601EF0/6023B0/603360
pinned bothPEs. NDpayload DWORDcount then{DWORDid,DWORDlen,bytes};querybyINDEX,
notid. Validrealstrings alreadyNUL,do not transcode. CP stored afterloadsuccess;
release clearsrecords pointer,count/cp retained. Lead601F50/trail601FE0 scan
IsDBCSLeadByteEx(storedCP). client455_language.h/.cpp own APIs/RAII,notprivateABI.
Bounded malformed/overflow/OOM guards andcleanup onrepeatedsuccessfulload differ
from unsafe original/leak domains;keep gaps explicit.9availableEDF/44095records
pass byte roundtrip/actualproductionreader;Korea6851,Taiwan6997,others4321.
en-us/th-th NDLanguage missing locally,nofallbackcopies. Fixtures work/client-
reference/language455;metadata inventory/client455-language-reference.json.
CountryCP through factory→ETCAction(kind1)→vtable slot76:949,1252,936,1252,1252,
932,1252,1251,950,1252,874. Returnbodies18h andslots pinnedbothPEs;actualCRT
LC_COLLATE names all11 produceexpectedCP. Full7factory/providers NOTrestored.
Main beforeengine nowcalls InitializeNationPaths thenInitializeLanguageData;
actualfont notapplied. Fullfont/text/UI/startup stillOPEN.13facade CPP+182client/
20canonical kernels;link0unresolved. Own PE1fc267d5ebe214dda8cfaa1b3b456f01ddb78848ec8c18899db1a9c411b17bc1,
1998336B/x86/base400000/entry14A920.MainRVA B3D40,soundB3D89,D3DB3D9C,charDataB3469.
ExactPElabs work/m9/1fc267d5:startup001 Korean949/6851;startup-russia001 Russian
1251/4321;device-startup001 realready1/windowed1/render32;create-startup001
owner4696d20/device456e0a0==appdevice,stopBEFOREoldcharDatareader. Controlled
exitE0434200 observed,no2ndchance,nooriginalEXE/serverchanges. Unchangeddebugger
reused bysource/exeSHA;--nation Russia savesseparatereport,doesnotclobberKorea.
ShortANI/BBX/model/effect/shadow/math/clock/accounting regressions passed;
oldframes equal,COM/Dmalloc0.12scoped checkpoints PASS/PARTIAL;M6/M6F/M7/M9OPEN.
IDA34ab1c2b closed/save=true;rawartifacts/client455-language;codepage-chain.json
records factory/ctor/vtable/method IDs forfuturefullproviders. Detailed
research/client455-language.md. Previous goal turn044 wasprogress;this045adds
productionlanguage data andactualownWinMain Korean/Russian evidence.
Next046: actualfont/text provider8C5A80 andBF7718/BF7618/BF7818/BF781C/BF7820
consumers;comparefontctor/privateInit/glyphlayout455 withlegacyCR3Font85byte
name/DEFAULT_CHARSET/fixedheight. Thennormaltextqueryconsumer andrealtext/DBCS
input;notmerelyloadedstrings. ContinuefullCreate/data/UI/launcher/ETCAction/
FG_CB/networkorder/BGM/shutdown. Noblocker requiring userinput currently.

Предыдущий результат — nationpaths044:

Nationpaths044: реальный country mapper7D29C0 case-sensitive _mbscmp,
11names Korea/Brazil/China/Europe/Indonesia/Japan/Philippines/Russia/Taiwan/
USA/Thailand ->0..10;unknownWORDffff. Setup7D2880 читает128bytes Setup/Language
из .\R3Engine.ini и отвергает>11. Имя Russia,неru-ru;неподставлятьcountry7
в old3language arrays. Selector7CFB10/root5E5B70: .\DataTable\<folder>.
Модуль client455_nation_paths.cpp подключён перед InitR3Engine в normal main.
CRT/font/charset пока только metadata; НЕ заявлять полный SelectR3Language.
USA=en-us с English_United Kingdom;Korea font bytesB1BCB8B2C3BC;setlocale(1)
значит LC_COLLATE,неLC_CTYPE. ETCAction/factory/NDLanguage ещё не реализованы.
Country/source CPU fixture из обоихPE;profile/case/invalid/missing/truncation/
reload cases passed.182client/12facade/20kernel CPP,full link0unresolved.
New own PE cb64af10cad3f527af015609f71ca0c7d300cce59aa3c2671bf0155aab384b88,
1967104B/x86/base400000/entry1496C0. Actual CRT/Miles/window/D3D прошли;
normal Create создал Character/bone/mesh/animation/bounds managers, stop BEFORE
_CreateCharDataMgr. Character owner439f160 device44d5da0 == actual app device.
Source country path .\DataTable\ko-kr виден вtrace.12realSHO staged.
Raw work/m9/cb64af10/{startup001,device-startup001,create-startup001}.
Controlled exitE0434200 observed;no2ndchance;SW_HIDE request не show acceptance.
Own debugger plan11DWORD: full/bits/appRVA,ready/window/device/windowed offsets,
soundRVA,d3dRVA,charGlobalRVA,charDeviceOffset(compiler measured0).
Old main+1D/+30 INVALID after newcall. audit_client455_own_entry.py uses
dumpbin decoded CALL+MAP and currentPE SHA; validated_entry required before run.
MainRVA B3CD0,afterSound B3CFA,afterD3D B3D0D,beforeCharData B33F9.
Current engine043 unchanged,033 baseline preserved. Short ANI/BBX/model/effect/
shadow/math/clock/accounting regressions passed;old frames equal,COM/Dmalloc0.
All11scoped checkpoints PASS/PARTIAL;fullclient acceptance stillOPEN.
Reference IDA5f01f0d1 closed/save=true. No original EXE/server changes.
research/client455-nation-paths.md;inventory/client455-nation-paths-checkpoint.json.
Next045: full locale/data bootstrap: factory8321E0,provider8327B0(1) vslot76,
CRT codepage parse/compare,font8C5A80,NDLanguage601EF0/603130 and EDF reader
5EEC00/5EE900/5EEB90. Do not fake success/factories or move filters blindly.
Then normal data consumers/Create/UI/launcher/network order/BGM/fullshutdown.
Previous goal status-only turn was no progress;state revalidated and this
turn changed production source and yielded actual normal Create evidence.
M6/M6F/M7/M9 remain OPEN;no blockers requiring user input currently.

Предыдущий результат — devicestartup043:

Device startup043: target WinMain7D04E0/setup7D2880/wrapper8EDAB0/color8ED5A0
pinned both bins. CRITICAL old ForceFullScreen name misled legacy code:
4558ED5A0 writes DWORD1157CA8=32, NOT fullscreen1157CB0. Restore this body and
Create policy: vcall8EDB72 TEST/JZ, any nonzero exit(0), including S_FALSE.
Derived work/client455-port/startup-engine builds67units from unchanged033
source inputs, replacing only kernel/wrapper CPP copies. Baseline033source/lib
SHA preserved. New archive R3Engine455Startup.lib selected by normal consumer/
full link; old engine archive not mixed. Source generation build_client455_
engine_startup.py; reference/native startup-contracts. CPU test virtualCreate
only: S_OK continues, S_FALSE/E_FAIL exit0 +atexit; color32 keeps full FALSE/TRUE.
Actual PE changed:51fd3f49ab867f7178a548dcd7058276fb4f1ac4983ab5feac808db863df5fd1,
1966080B/x86/base400000/entry149510. Exact own WinMain real device lab passed:
fullscreen0/renderBits32 from config (NO memory/config behavior override),
afterD3D HRESULT0, ready1/windowed1/nonzeroHWND+device. Own debugger SW_HIDE
request, breakpoints only in child memory; stop before CMainApp::Create,
plannedexitE0434200 observed. Raw work/m9/51fd3f49/device-startup002. No UI input.
Own source layout measured by compiler: ready178060/window178136/device178152/
windowed178052; Core full1964/renderBits1956. Not reference ABI overlay.
EarlyCRT/Miles42 rerun on new exactPE; all short native ANI/BBX/color/effect/
shadow/clock/table/accounting regressions passed, priorframes equal/COM0/
Dmalloc0. No unchanged bulk suites. Reference IDA1c8c37b3 closed/saved=true.
Detailed research client455-device-startup.md, inventory device-startup-checkpoint
PARTIAL; all scoped checkpoints retain M6/M6F/M7/M9 OPEN. Previous goal turn
aa6db9f was progress; this turn adds real source corrections+device execution.
Next044 target bootstrap: Setup/Language in .\\R3Engine.ini (AB04F8 string),
mapper7D29C0/setter7D1110, language selection7CFB10, root5E5B50 buildsFG_CB.ini.
Target nation/launcher/network/connect BEFORE engine, then WaveList+BGMList,
device/Create7D18B0. Old normal main lacks these flows; don't claimstartup455
equivalence or fakefilterrootcopies. Recover locale/root/normalCreate on actual
client resources. Wrapper camera adds reset op18 in455 while oldconsole table17
only; this branch remains OPEN, neverwriteOOB. Full Create/UI/launcher/network/
gameplay/device reset/show/fullshutdown remainOPEN; server/originals untouched.

Предыдущий результат:

Startup042: no production code/PE changes. Actual exact RF_Online.bin041 copied
to work/m9/39062b2c/startup002, x86/base400000/entry149500/SHA39062b2c... unchanged.
Native own_client_startup_debugger.cpp built Win32/MT; CREATE_PROCESS_DEBUG_ONLY,
owned handles/20s bound, breakpoints at own WinMain RVA B3CD0 and B3CED after
sound/before D3D. Breakpoints ephemeral in OWN child memory, never input EXEs.
Main reached, engine bootstrap returned, InitR3SoundSystem returned1; actual
Miles DLL loaded from private lab, real WaveList513339bytes opened. Stop before
D3D/window/Create/network stage, plannedexit E0434200 observed, no live process.
3firstchance events40080201/E06D7363/406D1388 handled byruntime (forwarded via
DBG_EXCEPTION_NOT_HANDLED), no secondchance. No playback/full audio acceptance.
Own IDA2714f558 closed/saved=true; raw own WinMain disasm artifacts/client455-startup.
Static audit parses regular+delay descriptors and x86 provider exports:15groups,
delayed MSS32/ABuse/Adv/PDLL. Regular providers SysWOW64, delayed user DLL copies;
actual eager+MSS hashes matched. ABuse/Adv/PDLL not reached/loaded. Copies of real
WaveList/mssmp3.asi and own R3Engine.ini only; no user accounts/configs copied.
Root cryp.dat/advr.dat absent but ko-kr versions exist, paths/hashes in audit.
Do NOT claim dependencies absent altogether; verify455locale policy before
changing paths. Current legacy main ForceFullScreen overrides ini FALSE.
Scripts audit/probe/checkpoint_client455_startup.py; inventory startup-audit/
native/checkpoint PARTIAL; research client455-startup.md. Existing native suites
not rerun because production PE unchanged. Previous goal turn41db2a9 full link
was progress; this turn adds real exactPE execution/provider evidence, no blocker.
Next043: target455startup/config/locale contracts and actualnormal D3D/window/
device callbacks in controlled windowed own lab; do not treat lab override as
target production behavior. Then Create/launcher/data/error/shutdown and full
UI/network/gameplay. Full M6/M6F/M7/M9 OPEN. InputEXEs/server/originals untouched.

Предыдущий результат:

Accounting041: source normal_accounting.{h,cpp} supplies process-wide mesh/
buffer/rawANI counters, existing texture global remains actual source owner.
Normal Runtime now passes shared pointers, not per-renderer totals. Own
CHMEMORYINFO remains seven-field read view; RF455_GetCharacterMemoryInfo returns
current values. Sole legacy foreffect diagnostic has8reads replaced by one
local snapshot. No dummy global/no private32byte overlay. Seven globals
11895F8..1189610 and all known producers/debugconsumer pinned both455bins;
initial28bytes zero. Ctor9312E0 zeros32 but no found xrefs/association remains
unknown; eighth field not invented. Actual globals count creations/cumulative
estimated bytes, not live memory. Buffers count COM blocks, object count mesh
parts, ANI counts raw import size. Destruction does not subtract.
CPU actualANI70794bytes loaded/cached/released across2normal renderer owners;
mesh ctor/destruction/DWORDwrap/source snapshot checked. GPU realBN+MSH+ANI:
107meshes/620921bytes,2bufferblocks/3300000bytes,4textures/4194304estimatedbytes
(includes newEFFtexture),43298ANIbytes. Verified against loaded model parts,
nonnull pools, actual texture descriptors and looseANI length. Release andnew
renderer keep totals. Old2color/effect/shadow frames unchanged, COM/Dmalloc0.
One test expectation corrected: texture nextId starts1; GPU oracle now counts
actual entries/descriptors, not nextId. Production counters unchanged by fix.
182client/11facade/20kernelCPP compile. FIRST full normal source455/D3D9 link
PASS/0unresolved/noothererrors/noCharacterMR/noFORCE. Own RF_Online.bin1966080B,
x86/base400000/entry149500,SHA39062b2cbf18f5680fd1d59c3d73c22c020770c30e99c9107302cf6678a53a05.
Full link metadata/MAP/response in normal-link.json; common helper validates
success as separate fact, all8scoped checkpoints remain PARTIAL/M9OPEN.
Research client455-normal-accounting.md, reference/native/checkpoint normal-
accounting; raw artifacts/normal-accounting455. IDA6b33fc0a closed/saved=true.
Originals/server/baseline/engine033 untouched; no input EXE or normalWinMain run.
Previous goal turn progress:69914c3 restoredclock; current adds actual ownership
and full link evidence. No blocking/no-progress condition.
Next042: own fullPE imports/delayed DLL/CRT/global/WinMain preflight and isolated
offline startup lab. Main starts engine→Miles sound→D3D init→Create→ABuse/Adv
filters→loop/network OnLoop. Verify actual DLL APIs/config/assets before run;
do not invent successful providers or use original workingdir. PE lacks.rsrc;
engine winmain.rc containsicon, caller necessity stillunproven. Full actor/
particle/shadow/blend/UI/network/gameplay/device-reset acceptance remainsopen.

Предыдущий результат:

Character clock040: client455_character_clock.{h,cpp} +normal_clock.cpp,
facade10CPP. Separate91EA80 milliseconds timer, not engine8B3CC0. Original
main7D13A2/7D13A7 calls both; both pins equal. Initial selected globals zero
in loaded PE image. Own state44B (no raw overlay across shader COM pointers).
First QPF once, successful branch QPC twice first call/once later; original
ignores QPC BOOL. Wrap64 delta*1000, signed FILD numerator/frequency, float delta
spill then elapsed +=delta. No clamp/scale. Fallback DWORD tick/window/count;
only >200 produces average milliseconds, resets count/window, retains delta
otherwise; NO elapsed accumulation on fallback. Quirks preserved, CW unchanged.
168 Fraction/x87 cases/12PC-RC modes passed in core and actual _R3CalculateTime;
provider lifecycle/ignored BOOL with supplied output passed; engine loop state
unchanged. Failure without supplied QPC data uses own zero seed, not certified.
924700/9248A0 are pinned reference consumers only, not newly restored APIs.
182client/10facade/20kernelCPP compile; full link now only g_ChMemoryInfo.
Short ANI/BBX/renderer/effect/table/shadow regressions passed, old frames/COM0/
Dmalloc0. IDAa91e5275 closed/saved=true. Research client455-character-clock.md;
reference/native/checkpoint client455-character-clock. M6/M6F/M7/M9OPEN.
Previous goal turn was progress: effects039 committed dd66565; this turn adds
real clock implementation/evidence, no blocker/no-progress condition.
Next041: actual process accounting. Producers identified texture11895F8/FC,
buffers1189600/04, rawANI1189608, meshctor118960C/10. Debug7F26F1..7F2798
matches seven old fields. Ctor9312E0 zeros8DWORD but no found xrefs: eighth
field association remains unproven, do not claim full32-byte ABI yet. Texture
source is already cumulative process global; normal Runtime mesh/buffer/ANI
currently per-owner, must share and expose real counters. No fake zero global.
Then full normal link/init; full particles/blend/shadow/UI/network/gameplay open.

Предыдущий результат:

Effects039: source client455_effects.{h,cpp}, normal_effects.cpp и pinned factor
constants; facade теперь 8 CPP. EFF read92B380/converter929070/ctor920E40/
apply927040/filter9281A0/file9293D0/reset91C760+91F2B0/particle predicates и
reader/insert lists/Animus4572D0 pinned both bins. Evidence reference/native/
checkpoint client455-effects, research/client455-effects.md; raw artifacts/eff455.
All discovered EFF framing/names parsed:19766 records, lengths176/172. This is
format inventory, not a whole-game functional test. Native12real files/28records
lossless,132factor cases/12FP modes, bounded malformed/reload/filter/cache/slots
cases passed. strlen may cross20byte fields but bounded at176 in own parser.
Modern strings own text; numeric292 supplies confirmed render/particle fields,
not classic STL ABI. Texture cache attempts56/60 sticky; cached ptr branch
does not change mesh texture ID. Empty filter all, named overrides; duplicate
file/filter last wins, file-list ID first wins. Reset→inline5163, current5455,
particles208/224/240/entity256. MAX_PATTERN_SIZE=36 confirmed by Animus caller.
SetMeshEffect uses status-aware selection; grades9..35 unknown stays explicit.
Actual GPU: InitEffect→binary EFF→tables→SetMeshEffect→real DDS upload→model main
D3D9 draw. Grade/mode/cache tested; before/after5814pixels differ; old two color
frames unchanged, shadow silhouette retained, COM/Dmalloc0. Slot/plumbing test
does not restore full particle emitter math/flags/lifecycle.
182client/8facade/20kernel CPP compile. Full link only g_ChMemoryInfo and
_R3CalculateTime, no other errors/old CharacterMR/forced resolution. Normal,
renderer/contracts/shadow/table/effect checkpoints PARTIAL. No unchanged bulk
suites. Owned IDA4a2e7cac closed with save requested, returned saved=null.
Originals/server/baseline untouched. M6/M6F/M7/M9 OPEN.
Next040: verify CHMEMORYINFO old28 vs455ctor32, actual accounting producers and
Character timer bridge; no empty global/no-op or duplicate clock advance.
Then full normal link/init. Shadow/HRESULT caller, blending, CRT, unknown pattern
tail, full particles/gameplay/UI/network/device-reset acceptance remain open.

Предыдущий результат:

Effect tables038: client455_effect_tables.{h,cpp} иnormal_effect_tables.cpp
вfacade(теперь6CPP). Pattern/Item classes globals имеют настоящие source owners;
2loaders+IsHaveMeshEffect подключены. 925710/929920/927B80/9276B0/929460 pinned
both455bins, initialPattern340400bytes zero PE image verified. Pattern=2300flags+
2300*36DWORD; readerattempt1..2299, scanfID+9ints then COPIES36DWORD fromstack.
Loadedrow grades9..35 UNSPECIFIED,notzeroproven. Own knownmask metadata: direct
SelectItemEffect returnsUNDEFINED;bool facade throws forunknown,neverfalsefallback.
FutureSetMeshEffect MUST use same status-aware selection. First9 partialfields
retain priorloopvalues/knownbits; missing/reload no tableclear, patternduplicate
overwrites. ItemhexID+6selectors initially0/partialretain;duplicatefirstwins.
Query ignoresmodel,grade>=36false/missingitemfalse beforegroups;presentflagunused.
Own invalidgroup/pattern/malformederrors differfromunchecked/hangingreference.
Real2246patterns/4600items,180selectedqueries incl72explicitunknown passed; targeted
duplicates/reload/missing/partial/limits/malformed passed. MAP true normalproviders.
182client/6facade/20kernelCPP compile,fullnormal link15unresolved/noothererrors.
Headerchanged:shortrealANI/BBX/colorframes/shadow regressions passed,COM/Dmalloc0;
no bulkunchangedtests. All5normal/tablecheckpoints PARTIAL. M6/M6F/M7/M9OPEN.
Researchclient455-effect-tables.md. OwnedIDA3ce41498closed/saved=true.
Next15 effects/FileList/globals/EFFbinary/apply/slots/modelIsHaveEffect/accounting/
Characterclock. Cached artifacts/normal-effects455:92CEA0/92CD60/9293D0/9281A0,
927040(applytexture/effectpointer5455),91C710(renderpredicate,NOTparticles).
Login53FFA1..53FFE7 exactcaller. EFFload92B380;SetEffect9298D0 usesrendercontext.
Do notreuseold4arg setter/rawparticle offsets. Unknownpattern stacktail alsoopen.
Originals/server/baseline untouched. Shader/HRESULTcaller,blend,CRT gaps remain.

Предыдущий результат:

Normal shadow037: client455_normal_shadow.cpp — четвёртый facadeCPP.
Begin91D330/End91D5C0/helper9335F0 и callers51DBE0/51DE60 pinned both455bins;
inventory/client455-normal-shadow-reference.json. 20lazy textures512x512/1level
с currentRT format/usage/pool. Quad4*24bytes ±30/FFFFFFFF/exactUV, managedVB96,
usage8/FVF322, shared original1189598 bits published before firstVB attempt.
SavedRT/DS owner8920/8924; literal COM order/restoration and retained released
savedpointers. Failed firstLock leaves cached unfilledVB; S_FALSE createTex rejected.
CRITICAL: Begin returns HRESULT from SetDepthNULL. S_OK=0, BOTH actual455callers
use if(result), so skip End on success. Do notreturn1/fix behavior silently.
Own HAL test explicitly Ends andsetsStateBEFOREBegin;not normalcaller acceptance.
Capture protocol/selectedfailures passed. HAL slot0/19/reuse0,descriptor/depth/Z/
viewport restoration,realmodelshadow silhouette512x512(23218RGBpixels) passed;
frame viewed,2previouscolorframes equal035,COM/Dmalloc0. 182client/4facade/20kernel
CPP compile0errors;fullnormal link20unresolved/noothererrors. All4normal checkpoints
PARTIAL;M6/M6F/M7/M9OPEN. Researchclient455-normal-shadow.md.
Next: effects/tables/particle-entityslots/accounting/Characterclock (normal-link.json).
Groundprojection91D630/GetShadow/nonactiveconsumers/reset/fullnormal lifecycle
andBOOLcaller issue stillopen. No oldSDK/noop/fullgame parity claims.
No bulkunchangedtests. OwnedIDA63e04581closed/saved=true. Baseline/server/originals
unchanged. Normal blend enable/duration/elapsed, originalCRT/profiling stillopen.

Предыдущий результат:

Normal contracts036: client455_normal_contracts.cpp подключён третьим CPP
к RFClient455Facade.lib. AnimationReset931FB0, RematchParent931A80,
SetEyeVec931AC0, SetTexPath608140, ImportBoundBox931810→93BF90 восстановлены.
10body/caller ranges equalboth455pins; inventory/client455-normal-contracts-reference.json.
Reset при current && renderer33840 сохраняет descriptor32 вprevious5099 (keys
borrowed), model680=1/684=oldframe/688=oldmax/692=0; always mesh5094/5103=0,
current5095=null/alpha5131=1, model frame160/max0. Disabled/nullcurrent retains
previous. Namedmodel680..692 теперьcanonical fields, size1188 unchanged.
Rematch используетготовый93BB70 только дляexternal5495, firstexactname.
Eye64bytes→5503/flag5499, texturestrncpy255→276 leaveslastbyte.
BBX loose rb:skip256,second12thenfirst12;shortreadreturns1/preservesunwritten.
Fivegroups inclsynthetic enabledreset/retainedprevious/names/pathlimits/realGOLIATH
BBX+malformed passed, actualCUnity/CAnimation twoANI passed. RealBN/MESH08/ANI
reset→reattach→rematch→pose→HAL passed;2frames equal035precanonical,COM/Dmalloc0.
182client+3facade+20canonicalCPP compile0errors. Fullnormal link22unresolved,
noothererrors; actualMAPall5providersclient455_normal_contracts.obj.
All3normal checkpoints PARTIAL. M6/M6F/M7/M9OPEN. Researchclient455-normal-contracts.md.
Remaining22:effects/tables/particle/entityslots/shadowtargets/Characterclock/accounting.
Do notrepeatdonekernels. Normal33840enabling/33844init/blendelapsedadvance/actor
lifecycle stillopen; enabledresettest setsflag explicitly, GPUduration150explicit.
Bad_alloc ownedOOMpolicy,notoriginalfailureparity. OriginalCRT/profiling/fullnormal
WinMain/gameplay/UI/network stillopen. Largeunchangedsuitesnotrerun.
OwnedIDAb8160cd3closed/saved=true. Baseline/engine033/originals/serveruntouched.

Предыдущий результат:

Normal renderer035:
В этой новой ветви 20productionCPP Character пересобираются в RFClient455Kernels.lib
из scripts/native с ЕДИНЫМИ normal/include определениями типов. Линковать только
новуюcanonicallibrary, не старые отдельные component archives. SourceSHA/evidence
из старых отчётов нужны для происхождения, ихbinarylibs для сборки не нужны.
Кадры/результаты до и после canonical rebuild совпали; precanonical report сохранён
в inventory/client455-normal-renderer-precanonical.json. kernel_sources() в prepare
проверяет source SHA, build/checkpoints проверяют20objects/canonical include set.
Source CRender FrameMove/DrawCharacter/DrawCharacterMat/shadow/
SetState/UnSetState/SetLight, CUnity LoadMeshData, SetAlpha/GetAlpha/SetMaterial и
общая transparency queue подключены в work/client455-port/normal.14ranges equal
bothpins и constants: inventory/client455-normal-renderer-reference.json.
IsLoadAnimation исправлен:9316A0 вызывает loader0, а не проверяет load flag;
повтор после missing file может вернуть true при load0==0/attempted4==1 — проверено.
UnSetState=91CBB0 (caller7CD340), не91D320. Model cull934F00 имеет m32 dot spill
до plane.w, в отличие от scene8C2C90.96angles/60boxes/12FPmodes прошли; signed zero
при RC-down учтён. World coordinate matrix изBF8320, degrees/radians double pinned.
182normalobjects+facade собираются. Actual CUnity BN/MESH08/ANI→pose→DrawCharacter/
alpha flush→HAL прошёл:51parts/46geometry,2animated frames equalmatrixwrapper,
ненулевое положение,3visibility cases/alpha/material/light/unsetstate,COM/Dmalloc0.
Кадры просмотрены; source inputs EXE не запускались, gameDLLs отсутствуют.
Native GPU probe должен иметь ENGINE_DEFINITIONS как у engine/client, особенно
RF_CLIENT_455_WEATHER: без него был неверный offset R3 camera state и пустой кадр.
Inventory normal-renderer-math/gpu содержит PE SHA/RVA/run paths/definitions.
Полный normal link LNK1120:27remaining methods/data, без других ошибок/CharacterMR/
forced unresolved. Оба normal checkpoints PARTIAL; M6/M6F/M7/M9 OPEN.
Следом remaining27 из inventory/client455-normal-link.json:effects/slots/reset/
parent/eye/bounds/texturepath/shadowtargets/time/data. Готовые ядра не восстанавливать.
Важно: originalprofiling/staticCRTtrig/failure/FPspecial/batch/ortho/reset/fullscreen/
normalshutdown не приняты. BlendDuration33844 ctor не пишет; test явно150,
normalinit неизвестен. Теперь читается только при existing previous track.
Shared shutdown own adapter проверен после renderer destruction, normal WinMain
ещё не подключён. Originalframeparity не доказана. Baseline/engine033 сохранены.
Research client455-normal-renderer.md; checkpoint_client455_normal_renderer.py.
IDA owned1bcd6f24 closed,save requested/returned saved=null; новых установок нет.

Предыдущий результат:

Normal port034: work/client455-port/normal, все180clientTUs на D3D9/typed455records
1188/5803/284. Named union views подтверждённых полей только в копиях headers,
не legacy ABI casts. CUnity/CAnimation выделены в два productionTU: тела побайтно
равны исходным секциям, из прежних TU удалены.182clientobjects x86/MT плюс
RFClient455Facade.lib собираются. Wrappers — own API, не original C++ ABI.
Реальные CAnimation::LoadData и CUnityAniMgr::GetAni загрузили ANI, проверены
ID/extra/effect frames/repeat/missing. Animation sticky+4 — BYTE loadAttempted,
НЕ DWORD load=4. Model frame672/max676/ramp704-716; mesh final4830/previous4894/
local4958/palette646; animation name5/id264/extra280 основаны на готовых ядрах.
MAP providers, SHA/RVA/run path в inventory/client455-normal-consumers.json.
Полная normal линковка всех182objects: LNK1120,39distinct unresolved methods/data,
без других ошибок/CharacterMR/forced unresolved. Это НЕ прежние39oldSDKfunctions.
inventory/client455-normal-link.json; checkpoint PARTIAL; M6/M6F/M7/M9 OPEN.
Unknown particleSlots/entitySlot остаются link errors. Screenshot readback compile
only, multisample runtime открыт. Hub exceptions/debug log и высокоуровневые
adapters ещё сверять с455. Baseline/engine033 сохранены. Следом normal FrameMove/
DrawCharacter/SetState/UnSetState/camera/light, затем LoadMeshData/setters/reset/
bounds/effects/data. Готовые kernels не восстанавливать повторно. Через Invoke-Python:
prepare_client455_normal.py, build_client455_normal.py, probe_client455_normal_consumers.py,
link_client455_normal.py (ожидается ненулевой exit), checkpoint_client455_normal.py.
research/client455-normal-port.md; inventory/client455-normal-checkpoint.json.
Новых установок/IDA sessions/bulk suites нет.

Предыдущий результат:

Engine9port033: новаякопия work/client455-port,492files/50byte-migrated;
67realengineTUs x86/MT собираются. Никаких aliasesDevice8→9/legacyCharacterMR
в новом probe. HWND/D3D9HAL R3ConfirmDevice→R3InitDevice→Grass shader/declaration,
source455Characterowner наТOMЖЕdevice (12programs/sprite/pools/textures),cleanup
прошли. Platform01:14141leaves/23helpers/8interiors/2weather states[0,0]→[1,1]→[0,0],
12visiblegroups/frameviewed,enginewarnings/errors0,Dmalloc0,COM0.24device/46map
assertions;big неизменённые suites не повторялись. Runtime
work/m9/7a4bbf82/engine900{1,2}/engine9-probe.exe, SHA/RVA вengine9runtime reports.
Gate inventory/client455-engine9-checkpoint.json;research/client455-engine9-port.md.
База work/client-build иnormalRF_Online не менялись в033. Следом реальные180client
consumers: source Character455.h/facade,typed models/animation иnormalgame linkage
с новымengine.39SDKfunctions/150field candidates прежние. Не rawcast/неподключать
CharacterMR для обхода незавершённого порта. Готовые owner/load/ANI/pose/draw/frustum
переиспользовать. M6/M6F/M7/M9 OPEN.
Genuine headers изsigned Microsoft.DXSDK.D3DX9.29.952.8 stagedlocal;package targets
неисполнялись,_43DLLs неустановлены. x86importarchive retarget43→36,allactualimports
проверены противpinned9_36. SDK43inlines/fullABI36 несертифицированы. Fullscreen
enumeration покаX8R8G8B8;allmodes/reset/unwind/state/shader/camera parity ещёоткрыты.
Engine/probe общийENGINE_DEFINITIONS включаетHELPER_LOADER; безнего было0interiors,
это исправлено. LabWindows path backslashes исправлены послеowncrash. Probe CLand
hooks excluded,неproduction stubs. NativeownSEH exception report+MAP доступны;
CDBexe неустановлен (Debuggers/x64 directory alone notproof). IDAсессийнеоткрывали.

Предыдущий результат:

Renderer owner032 source:client455_renderer_owner.{h,cpp},constants.h;33856byte
storage с managers116/4264,texture8424,effects8712,pools8928/17128/25328,caps33532.
Constructor/SetDevice920590/dtor9228A0/2typed context adapters восстановлены.
11ranges equalbothpins.32892written bytes/constructor mask;opaque bytes preserved.
2poison seeds/5caps scenarios/Release order прошли. Shared shaders bootstrap only
when shareddevice null;repeat bind не пересоздаёт их,device borrowed/noAddRef.
Real BN→MESH08/ANI/3textures→pose→main draw использует owner managers/pools/shaders;
46parts/92draws/2frames совпали component/fullclient.169targeted assertions,
ownheap/COM/Dmalloc0. Fullclient previews work/m9/7bcf7ea4/client001/owner-frame-*.bmp
просмотрены. Lab197TUs/5475840B/entry8C60,
SHA7bcf7ea450ba2a5dfd157b0237c728a813e73ab0bea265269cfa60d4dbb9b3f1.
Normal293MTobjects/тот жеengine archive,owner APIs stripped;runtime равенfrustum031
кромеtimestamps.2451968B/entry1BC610,
SHA626d8f8a800294de371684da5a3c71515e3b0217159fa679b938ef0ec13c7fe8,
snapshot character455-renderer-owner. Gate inventory/client455-renderer-owner-checkpoint.json;
research/client455-renderer-owner.md. Native IDA8ad1c657closed/save.
Следом normal typed model/animation/ChInterface facade иengineD3D9 device path.
Использовать готовый source owner/load/pose/draw/frustum,не восстанавливать повторно.
39oldSDKfunctions/150field candidates ещёактуальны. Shader-failurelogger безcallback,
opaque methods/constructorunwind/reset/OOM/CRTtrig/fullgamecamera ещёоткрыты.
M6/M6F/M7/M9 не закрыты. Большие неизменённые runtime suites не повторялись.

Предыдущий результат:

Scene frustum031 подключён к обычным SetCharacterClipping/ProcessClipping.
Source client455_frustum.{h,cpp}/system.cpp:8C2A90/8C2C90,pinnedD3DX9_36,
x87 float spills/finite masked sqrt CW.72matrix/204AABB/12FP modes прошли отдельно
и через actual publisher;9actor cases прошли,Dmalloc0. Device/Platform01: прежние
frame SHA,COM0,warnings/errors0. Normal2451968B/entry1BC610,
SHA198c2dd38f5f0c78bedbea8d70f6712981ef63b042a21cf4fa16db89bbbcc6b4,
snapshot character455-frustum;293modernCOFF/MT (180client+67engine+46JPEG).
Lab196clientTUs; immutable runtime path/hash в client455-frustum-client.json.
Gate inventory/client455-frustum-checkpoint.json;research/client455-frustum.md.
Normal API inventory завершён:139calls/45symbols;131calls/39functions старогоSDK,
8calls/6source managers/setters.150field tokens только лексические кандидаты;
indirect/SDK internal closure не покрыто.23data refs подтверждены,5stTime отsource
multilayer;2object-only refs не включены. RTMOVIE выключен исходными CPP settings,
не включать вслепую. research/client455-normal-character-interface.md.
9238A0 — уже source loader/dispatch, не culling;92FBA0 делает lazy load→main draw.
Следом coupled typed normal model/animation/Character owner иD3D9 device port,
используя готовые loading/pose/draw модули. Fullcamera/actor visibility/CRT special
domains/device lifecycle ещё открыты. Missing math DLL abort отличается отoriginal
mandatory import failure;deployment policy открыт. M6/M6F/M7/M9 не закрыты.
Owned2a568200closed/save. Большие неизменённые runtime suites не повторялись.

Предыдущий результат:

Main Character draw030: scripts/native/client455_character_draw.{h,cpp},core.cpp,
internal.h;8APIs. Main92E5F0/effects92D3E0/transparent930A40/batch930650/CPU92DB60/
shadow930120 source.13ranges/5constant ranges равныобоимpins. Effect signature5args
cdecl(device,stage,type,color,scroll); apparentoverread был ошибкойdecompiler ESP.
16targeted scenarios/185assertions,materialredGPU-pixel,queue ties/NaN/cap1024,
batch200/201st fallback,DWORDrollover/CPUlimit. Real BELPHEGORHOLIDAY46parts/44skinned,
frames160/2160/3DDS теперьрисуется через main route;92submissions,две картинки
равны standalone/fullclient иrelated029. COM/heap/Dmalloc0,no gameDLLs. Preview
work/m9/3a7ddb01/client001/route-frame-{0,1}.bmp просмотрены. Gate
inventory/client455-character-draw-checkpoint.json;research/client455-character-draw.md.
Normal2451456B/entry1BC450/SHA ccee7cc0d7e4254a90cbc64870132b18827a5428d352748f1b77c37b8784dcfd,
snapshot character455-route-final; runtime равен029кромеtimestamps,291MTobjects/engine прежний.
Lab5427200B/entry8C01/SHA3a7ddb01a9fc8aff2b961863df5288f737833811466a5f989162bbd175c60603,
195clientTUs. Related029primitive596checks повторены из-за выделенияrawpool branch;
старыеbigANI/texture/sharedbuffer/Platform01 runtime suites не повторялись.
Следом normalCharacter interface/caller inventory исовместныйtypedmodel/animation/
rendererD3D9 port. Wrapperculling/simple92E140/scene-frustum8C2A90/device lifecycle
ещёоткрыты. Originalbump branch используетпоследний material scratch,первыйbump
можетчитатьundefinedstack; source имеетявныйzero seed. CPUunusedtemps такжеzero
seed. ModernMTsin/cos(double)→float — explicit labprovider,originalCRT bitsнеприняты.
M6/M6F/M7/M9 незакрыты. Никакихlegacy455casts/shadowrecords/manager-onlyswap.
MCP: route-main-all-instructions.json содержит1582actualinstructions;страницы
по120проверены. Старыйdraw-main-insn.json содержитлишь10lines несмотрянаcount982/done:
не использоватькакполнуювыгрузку. Effect240/transparent681/bump42проверены.
Owned96236a02closed/save. Rawroute-*.json ignoredartifacts/character-animation455.

Предыдущий результат (историческая очередь ниже):

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

Текущий шаг099: cooldowncache501C30,actualLinker use/remove/swap/hover,затем
liveSF/Animuscallbacks/lock/Macro35/Vending27/fullAdd/bootstrap. Подробнее в начале
этого файла и docs/next-steps.md. Ниже сохранена историческая очередь066:

1. Участок066: scrollbarEX/Var/parentinput/callers, затем production message sizing/richcallers/full
   briefing и actual Tutorial/world/UI/Avatar/localhandlers/fullfourstage/explicitnext,
   затем targetLoginUI/Create/worldtransitions,seed56BEA0/35handlers/countryproviders. У own argv endpoint1 не заполнен;
   не делать remap без target доказательств. Account053/TCP052/AES051 уже интегрированы,
   успех TCP не означает аутентификацию. Дальше реальный loginUI/game tables.
2. Full236config semantics/standard-queued routes/filters/throttle/backpressure/
   internal security/threads/Close остаются OPEN; target Create/video/BGM/fullUI,
   FT/ANSI/IME/layout/ILevel/world/actions/startup-error/fullshutdown обязательны.
   Не обходить connect/auth успехом. Только client fixtures; серверы не делать.
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

- Initial connection/events/wait: research/client455-connection.md; gate client455-connection-checkpoint.json.

- Network AES/framing/rings: research/client455-network-codec.md; gate client455-network-codec-checkpoint.json.

- Bootstrap/state/instance: research/client455-bootstrap.md, gate client455-bootstrap-checkpoint.json.

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
