# Память проекта

Обновлено 2026-11-06. Root `E:\RFOnlineTrash\Source\WorkFlow`.
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

1. Участок057: Tutorial/world/UI/Avatar/localhandlers/fullfourstage/explicitnext,
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
