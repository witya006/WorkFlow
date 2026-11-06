# RF Online client reconstruction journal

2026-11-07 — Movie-state077. Positive RTMovie flags/display/defaultFOV source
restored and intro bound to actual engine. Engine67/9overlays, baseline033
preserved. Flags8/GPU6/intro26/fullscreen18/40 reviewed frames/Create1 passed.
PEb377d2ac…; IDA70b16df7 closed. Full RVP player confirmed compiled stub;
RVP/Tutorial/QBI/follow/fourstage/game/M9 remain OPEN. Next078 actual providers.
Details research/client455-movie-state.md.

2026-11-07 — Fullscreen-effect076. Actualmotionbranch/density/Beginreturn,
fixed512targets;11ranges/default/4asm equalpins,IDAf1ac7cc2savedclosed.
Sourceengine67/7overlays,033preserved. GPU18+realintro3maps/26cameras,
34reviewedframes/target-depth-viewport-UI/Dmallocpassed. PE4553f401…/Create1,
freshcontracts. FullStage/QBI/cameraControls/postprocess/M9OPEN;next077.
Details research/client455-fullscreen-effect.md.

2026-11-07 — Tutorial-intro075. Restored455 intro cuts/fade/skip/reload,
15ranges/3tablesequalpins/4asm,IDAb92074d1savedclosed. Real camera/fade/world/
screen/mouse+Avatar race-stage:26cameras/29viewedframes/DmallocbalancePASS.
CameraTU uses matching engine definitions. PE51666436…/exactCreate1,runtime
equal074excepttimestamps. Fullstage/QBI/newenginecontrols/factory/M9OPEN.
Next076;details research/client455-tutorial-intro.md.

2026-11-07 — World074. Real Bellato/Cora/Accretia loaded/rendered throughCLand;
BSP39/EBP20 sourceworked,owner recreation andlevel destructorReleaseported.
10ranges/prefix48/6asm equalpins,IDA60286d36savedclosed. 3worlds/reload/GPU/
collision/Dmallocbalance,6viewedframes,zero warnings. Engine67/6overlays
c00d9d4d…;PEfd8b038d…/entry150790/182-20-32TU/Create1. FullILevel/Empty/INS/
Tutorial/fourstage/M9OPEN. Next075 actualTutorial/cameraintro/Avatar/handlers.
[Evidence](research/client455-world.md).

2026-11-07 — Avatar-stage073. ActualAvatar stage/skip,MainApp Create failure gate,
login stage2 and localTutorial route wired. Knownignored/1-17transport accepted;
missinglocalhandlers explicitlyfail,fullfactory/world/Tutorial stillOPEN.
45FBD0 corrected toSCREENsingleton,PostUIguardimplemented/tested.34ranges/
2vtables/15asm equalpins,IDAb3b8653dsavedclosed. NewPE3d1f8c32…/entry150550,
182/20/32TU/Create1;actualaccount/window/boardPASS,22frames equalreviewed072.
Next074 realworld/BSP39/Tutorialintro andactualhandlers/Avatar/fourstage.M9OPEN.
[Evidence](research/client455-avatar-stage.md).

2026-11-07 — Briefing-window072. Source window/provider/pages/buttons/portraits/
keys and actual Screen capture restored.32ranges/vtable212 equalpins,
19listedfullasm+2captureasm;IDA18f99dcdsavedclosed. CTutorialBoardprobe now uses
real sourceview,Avatar/stage stillrecordingfixture. Ko/Ru22GPUframes viewed,
realmousequeue/portraittimers/cells/affectedGUI passed. PEbd50df91…/entry150350,
182/20/31TU,0unresolved/exactCreate1. Actualstage/Avatar/world/fullwindow
lifecycle andM9 OPEN. Next073 actualTutorial/fourstage integration.
[Evidence](research/client455-briefing-window.md).

2026-11-07 — Briefing-controls071. Restored frame/key/sheetanimation source
controls,realresources/KoRu/GPU20frames/12uniqueviews.29ranges/3vtables equalpins,
8fullasm. Corrected070children-onlyDraw assumption:base2262E0 paintsfill/image;
typing/frame tests nowprovebasefillorder. UVdouble-normalization corrected.
Capture633360 belongsScreen. Productionfea692b9…/entry150290/182-20-30TU,
exactCreate1;runtimeequal070except2timestamps,oldGUIproofreusedexplicitly.
Actualfullwindow/portrait/capture/provider stillOPEN,next072;M9OPEN.
[Evidence](research/client455-briefing-controls.md).

2026-11-07 — Text-typing070. Restored missing CGUITextTypingBoard dependency:
WORD cursor/interval,delay/absoluteDWORD quirks,resourceDBCS,space/oldfragment
rule,virtualClear retention,partialDraw.18ranges/1vtable equalpins,8fullasm;
Ko/Ru ownnative/GPU passed,14frames saved/8viewed;44sharedGUI frames unchanged.
Normal8f009924…/entry150290,182/20/29TU,existingCreate1. Compiled source only,
ordinary briefing instance notyetconnected. Next071 actualwindow/key/portrait/
frame/provider,thenAvatar/world/Tutorial/fourstage. M9OPEN.
[Evidence](research/client455-text-typing.md).

2026-11-07 — Message-sizing069. Replaced ordinary modal SetMsg with455
plain/rich/basecolor/pixel extent and scroll/layout order. Natural positive
extent bypasses300/250 fallback caps;ordinary wrapper forwards rich/close.
21ranges equalpins/15fullasm;Ko/Ru12groups,10viewedframes,affectedGUI/Create1
passed. Productionc22502fa…/entry150290,182/20/28TU. Emptylist targetUB explicitly
unsupported;globalbasevirtualSetSize/fullwrappers/Briefing/Tutorial remainOPEN.
Next070 actualBriefing,thenAvatar/world/Tutorial/fourstage. M9OPEN.
[Evidence](research/client455-message-sizing.md).

2026-11-07 — GUI-input068. Restored base double7/right8/mouseguard/key/focus/queue
and main-list container contracts,including300ms/wrap/queryorder,bytekeydedup,
focus70/value80 and middlebutton. Corrected065ordinaryarrowadapter:targetleaves
basearrowsunbound,EXexplicitbindingsretained. Add inheritsShow,Removefocus-only;
otherlists/layers/privateGUI/IME remainOPEN. Ko/Ru real-object tests and affected
GUI/Create1 passed;40GPUhashes unchanged. Normalde76223c…/entry14F4A0,182/20/28TU.
Next069 production rich/message sizing/briefing,actualTutorial/fourstage. M9OPEN.
[Evidence](research/client455-gui-input.md).

2026-11-06 — Minimap-opacity067. Ordinary CGUIMiniMapWindow now owns EX and
receives actual queued mouse/scroll events. Recovered style0/1,alignment80/80,
known alpha groups/lists and Draw455;17ranges/2vtables equalpins,10fullasm.
Ko/Ru81amounts/GPU/actual MouseDev path andaffectedGUI/Create1 passed. Main
resource loaded withownedbridge toavoid legacyID4collision. Grid isasset,not
terrain;fullmap/zoom555940/othercontrols/targetinput remainOPEN. NormalPE0def3dce…,
entry14EFF0,182/20/27TU. Next068 parent/input contracts. M9OPEN.
[Evidence](research/client455-minimap-opacity.md).

2026-11-06 — Scrollbar-variants066. Added distinct EX/Var classes to ordinary
source provider;EX base-composite snap versus plain-button positioning,no repeat,
alpha and Var origin/extent/modes/vertical input/row2 verified with real objects.
Var initializer+24=SetSprite,notRemoveAll. Target loader actions<16 retained;
invalid16action fixture corrected to15,Var missing action15 not hidden. EX real
minimap owner identified but not ported. Ko/Ru queued/D3D probes and affected GUI/
existingCreate1 passed;productionb24f1f09…/entry14E290. Next067 minimap helper/
owner,parent input;fullM9 OPEN. [Evidence](research/client455-scrollbar-variants.md).

2026-11-06 — Scrollbar065. Ordinary geometry/linear thumb sizing,x87 snapping/
SSE2int32 conversion,mouse/drag/repeat clocks and queued events ported. Composite
thumb min6x18 and row2 tiling verified. Real common action2 has44frames,so
defaults44–49 clamp to43;real/synthetic GPU paths kept separate. Ko/Ru probes
and affected GUI/Create1 passed;productiond38d74e0…/entry14E350. EX/Var,parent
input/fullbriefing/Tutorial remain OPEN. [Evidence](research/client455-scrollbar.md).

2026-11-06 — Text-board064. Replaced ordinary board with pixel layout,fragment/
line caches,WORD retention/rebase and draw. FONT_INFO16/TextInfo28 restored;
BYTE-copy and markup quirks verified in full-object probe. Production rich
callers and full scrollbar remain OPEN. Korea/Russia four GPU frames viewed,
affected GUI/tutorial-modal/Create1 passed. Production3a209cdc…/entry14DD30.
CRT getter0/SBCS misunderstanding corrected using installed UCRT source;
redundant experimental adapter removed. [Evidence](research/client455-text-board.md).

2026-11-06 — Text-metrics063. Ported current GDI byte width/DBCS fit/first-height
cache and actual ordinary CGUIText sizing/style fallthrough. Added an owned
deferred geometry adapter for pre-font legacy static constructors; native global
creation/deletion and clean exit checked. Fixed mojibake in the test fixture;
final Korea/Russia PNGs viewed. New production71bc4b21… links and passes existing
Create1; affected font/modal regressions passed. FullTextBoard/scrollbar/FreeType/
16byte font scale/Tutorial remain OPEN. [Evidence](research/client455-text-metrics.md).

2026-11-06 — Modal062. Ordinary CGUIMessagebox/CGUIDialogBox now use confirmed
455button frames/dimensions/captions,outline/colors/margins and keyboard input.
Korea/Russia full-object GUI/D3D probes exit0;mouse observers/results,nested/focus/
pool/Open checked. GDI regression passed;new production PEa5b1da0b… links with
0unresolved and passes existingCreate=1. Fulltext/scrollbar/Tutorial still OPEN.
[Evidence](research/client455-modal.md).

2026-11-06 — Tutorial-board061. Added CTutorialBoard control rules and concrete
modal2/3 bridge into actual client GUI objects. Own x86 full-object harness
rendered viewport640x480, naturalexit0; finish/quit/clock/DBCS/key rows/race-class
selection checked. Captured legacy button sprite mismatch remains OPEN. Rich
window and real stage/Avatar/Tutorial integration remain OPEN; production unchanged.
[Evidence](research/client455-tutorial-board.md).

2026-11-06 — Tutorial-actions060. Recovered QBI19–46 rules and composed all47
processor families. Recording-host native exit0;99real programs/39864records
prepare, without claiming playback. Equip map16, lifetimes, cursor/feedback/
item/link branches verified. Undefined failed UI coordinates remain OPEN.
Shared spatial fixture extracted/tested; production PE unchanged.
[Evidence](research/client455-tutorial-actions.md).

2026-11-06 — Tutorial-spatial059. Restored Move/Creation/Position rules6–18,
shared remaining state and exact known spawn bytes. Recording-host x86 native
exit0; prior scheduler regression passed. Item receiver reads an uninitialized
DWORD+25 beyond producer25bytes; tracked OPEN without invented tail. Real host/
remaining28 selectors/Tutorial still open; production PE unchanged.
[Evidence](research/client455-tutorial-spatial.md).

2026-11-06 — Tutorial-runtime058. Recovered QBI scheduling/refresh/shared state,
message and wait rules. Own x86 library/recording-host tests exit0, including
clock wrap and completion that unloads the runtime. Other41 selectors/real host
remain open; unsupported real programs fail explicitly. Production PE unchanged.
Fixed057/058 library report schema for canonical discovery; verified20kernels.
[Evidence](research/client455-tutorial-runtime.md).

2026-11-06 — Tutorial-scripts057. Restored a source-owned47-selector SCP reader
and writer. All99 race/class files roundtrip losslessly; named fields match an
independent parser. Synthetic missing selectors and bounded failures pass.
Generic ko-kr/Tutorial.scp recorded as incompatible/unselected, not relabelled.
Command execution/board/ordinary Tutorial remain open; production PE unchanged.
[Evidence](research/client455-tutorial-scripts.md).

2026-11-06 — Camera056. Ordinary CAniCamera nowreads1.2/1.3 typedpayloads and
preserves confirmed455playback/FOV quirks. Fourreal1.2CAM plus synthetic1.3
roundtrip/materialize/play/GPUprojection/release pass,naturalexit0. Source033
preserved;newfullPE existingCreate1. FullTutorial/camera-cut/matrixparity open.
[Evidence](research/client455-camera.md).

2026-11-06 — Progress-base055. Ordinary CGameProgress now has explicit next
storage/exit API and recovered Input/exit/Frame/Render/reset order. Actual
base/Title/particle-owner native cases exit0;fullPE still reaches existing
Create=1. Fourstage factory/Avatar/Tutorial remainopen. OwnedIDA3bc31778 saved/
closed;no referenceEXE or server execution.
[Evidence](research/client455-progress-base.md).

2026-11-06 — Progress054. Pinned4stage classes via PE RTTI and28functions.
Avatar mode2 is Tutorial;replay hypothesis rejected. Legacy3stage/modulo
factory is an explicit client gap. Old INI reader has no static callers found;
do notinsert intoWinMain withoutproof. Tutorial is mandatory M6F/M9 scope.
Runtime unchanged;ownedIDA3915694c closed/save=true.
[Evidence](research/client455-progress.md).

2026-11-06 — Account053. Restored gate seed,342byte login and account/world
packet consumers in the ordinary client. Actual sender/ring/dispatcher and
pending dialogs pass owned fixture cases;naturalexit0. Full PE still reaches
existingCreate=1. No authentication or server implementation. Providers/fullUI/
other game protocols remain open. M6/M9 open.
[Evidence](research/client455-account.md).

2026-11-06 — Connection052. Restored events-only pre-engine connection wait,
strict timeout/delayed-accept boundaries and102-entry receipt budgets. Actual
normal WinMain reaches existingCreate through genuine TCP; native real-method
success/raw-error/timeout cases exit0 and verify localized dialogs. No RF
protocol or authentication is simulated. Current argv endpoint0/1 gap remains
open pending full455country/handler side effects. M6/M9 open.
[Evidence](research/client455-connection.md).

2026-11-06 — Network codec051. Recovered directional AES192-CBC packet framing
and dynamic80-byte rings; wired actual normal sender/receiver and two configured
processes with capacity6. Source AES matches independent CNG; real consumers pass
fragmented/wrapped packet tests and natural exit0. ExistingCreate still returns1.
Full transport/events/35handlers/authentication/UI/M9 remain open.
[Evidence](research/client455-network-codec.md).

2026-11-06 — Bootstrap050. Restored FG profile/instance policy, moved actual
network creation before engine and recovered per-process Connect/raw results.
Real full-object tests cover duplicate own processes/mutex, state callbacks and
closed-port TCP. Target closes socket before reading its error: independent
WinSock and own source both lose10061 to0 here,while connected staysfalse.
ExistingCreate stillreturns1. Full455transport/framing/crypto/auth/UI/M9 remain
open. [Evidence](research/client455-bootstrap.md).

2026-11-06 — Launcher049. Reconstructed CCR93file/country andRussia/Europeargc5
profiles,includingbounded50/32fields. ActualWinMain nowloadsmetadata before
language/engine andlatelegacyread isremoved. Realmembernetwork setters pass
offline,ownexistingCreate returns1 thencontrolledstop beforefilters/game loop.
No authentication performed;remainingbootstrap/network/wire/targetCreate/UI
andM9open. [Evidence](research/client455-launcher.md).

2026-11-06 — Sprites048. Recovered55target filenames/localized→Common selection
and455managed texture uploader,including actual requiredDXT5. Ordinary startup
mouse/common consumers nowload real455resources;actualCMainApp.LoadData and
CGUIMouse pass payload/frame/cache/cleanexit checks in Korean/Russian labs.
ExactownPE reaches decodedpre-launcher boundary afterexistingUI initialization.
FullUI/targetbootstrap/Create/login andM9 remainopen.
[Evidence](research/client455-sprites.md).

2026-11-06 — Lifecycle047. Restored the binary-confirmed455null-level FALSE
return before cleanup in ordinary CLand::UnloadLevel. Three normal global
CMainApp/CLand labs and both GUI font labs without artificial Land creation
exit naturally with0. Full normal source PE links with0unresolved and preserves
startup/Character/frames. Full typed ILevel,world/Create/WinMain/shutdown remain
open. [Evidence](research/client455-lifecycle.md).

2026-11-06 — Devicestartup043. Corrected legacy ForceFullScreen behavior to the
actual455color32 write and restored nonzero Create→exit0 policy in a derived
engine, preserving033. Exact own PE reaches window/device ready in configured
windowed mode, then stops before client Create. Target bootstrap order/locale/
launcher/network and full runtime acceptance remain open.
[research/client455-device-startup.md](research/client455-device-startup.md).

2026-11-06 — Startup042. Exact own full PE041 passed CRT/normal WinMain/engine
and real Miles startup (return1), then the own debugger stopped it before D3D.
Actual eager/MSS providers matched the static export/hash audit. Original input
EXEs never executed; no production PE changes. Graphics/Create/launcher/locale/
shutdown and full455behavior remain open.
[research/client455-startup.md](research/client455-startup.md).

2026-11-06 — Accounting041. Normal process-wide cumulative counters now connect
real mesh/buffer/ANI producers and existing texture totals to the diagnostic
consumer. Real ANI/two owners, mesh lifetime/wrap and actual GPU descriptors
pass. First full normal source Character/D3D9 RF_Online.bin links with zero
unresolved symbols. Normal WinMain/gameplay acceptance and M9 remain open.
[research/client455-normal-accounting.md](research/client455-normal-accounting.md).

2026-11-06 — Font046. Country params8C5A80 andGDI/Unicode atlas/cache/draw
9067E0/906C10/906DD0/907710 now drive ordinary R3LoadTextTexture/DrawR3Hangul.
ActualCGUIText renders Hangul/Cyrillic fromNDLanguage;GDIoracle/atlas/frame/
cacheeviction andcleanexit pass. Early-abort~CLand nullLevel found andtracked;
fullFT/text/UI/lifecycle remainopen. [research/client455-font.md](research/client455-font.md).

2026-11-06 — Language045. EDF/NDLanguage603130/RVA203130,index query6023B0,
DBCS601F50/601FE0 and11ETCAction codepage kernels recovered.9realEDF roundtrip
and production source reader pass;exact own normal WinMain loads Korean949
andRussian1251. Normal D3D/Character preserved. Actualfont/text/UI/factory/
launcher andfullCreate/M9 remainopen. [research/client455-language.md](research/client455-language.md).

2026-11-06 — Nationpaths044. Country mapper7D29C0/RVA3D29C0 and selector7CFB10/
RVA3CFB10 pinned both455PEs. Eleven case-sensitive country/root choices now
in actual normal WinMain;CRT/font/NDLanguage remain unfinished. Own full PE
cb64af10... passed partial normal Create through Character/managers using
the same real app D3D9 device;stop before old data readers. New decoded own
CALL/MAP checkpoints replace fixed offsets;short regressions/frames pass.
M6/M9 open. [research/client455-nation-paths.md](research/client455-nation-paths.md).

2026-11-06 — Characterclock040. Restored separate91EA80 QPC/fallback millisecond
timer and real normal _R3CalculateTime bridge. Core/bridge Fraction oracle and
provider lifecycle scenarios pass; engine clock remains independent. Full link
now only g_ChMemoryInfo. Partial M6; full actor/gameplay acceptance open.
[research/client455-character-clock.md](research/client455-character-clock.md).

2026-11-06 — Effects039. Recovered EFF parsing, registry/file lists, application,
reset and current particle/entity slot views in the normal facade. Real DDS
upload and effect application changed a real model frame; previous color and
shadow scenarios passed. Full normal link has two remaining symbols. This is
partial M6, not complete particles/gameplay or M9. Addresses, pins, contracts,
verification and gaps: [research/client455-effects.md](research/client455-effects.md).

2026-11-05 — Main Character draw030. Recovered92E5F0 with effect/transparent/
deferred-batch/CPU/shadow routes.16targeted HAL scenarios plus two real animated
frames passed standalone/fullclient; actual material RGB readback verified.
Normal typedrenderer/visibility/CRT andundefined-scratch fidelity still open.
Evidence and next action: [research/client455-character-draw.md](research/client455-character-draw.md).

2026-11-05 — Character draw primitives029. Source state/program/material/skin
palette/shared-buffer submission now draws real BELPHEGORHOLIDAY with its ANI
and three textures on D3D9 HAL, separately and inside full client lab. Two frame
readbacks agree. Detailed addresses, pins, contracts and remaining gaps:
[research/client455-draw.md](research/client455-draw.md).

This is partial M6. Full effect/transparent/batch/CPU/shadow routes and coupled
normal typed model/animation/renderer migration remain open. Earlier session
evidence is indexed in [docs/project-memory.md](docs/project-memory.md).
