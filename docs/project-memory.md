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

1. Восстановить full Character455 draw/mesh submit/state/constants/palette/material
   и shader selection. Bootstrap028 уже готов. Затем связанный normal typedmodel/
   animation/renderer путь, не отдельная подмена manager. Old ChAnimation name4/
   ID260/size280 против4555/264/284; oldmodel776/mesh1072 против1188/5803. Поэтому
   rawcast/shadow legacy records не добавлять. Коллекция027 готова,не реверсить снова.
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
