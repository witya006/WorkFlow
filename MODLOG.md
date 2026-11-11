2026-11-11 — Initial download 179, PARTIAL_MAP_LOADED_AVATAR_EQUIPMENT_FAILURE.
Restored the store list map gate. Decoded 60 records and loaded the real
NeutralB BSP. Avatar creation hit a legacy weapon consumer before `3/1`.
[Evidence and remaining work](research/client455-store-download.md)

2026-11-11 — Initial download 178, PARTIAL_WAITING_FOR_GUILD_AND_WORLD_INITIALIZATION.
Decoded character macro and announcement data and received guild list `27/112`.
Located the MainGame gate before the target start-position request.
[Evidence and remaining work](research/client455-macro-download.md)

2026-11-11 — Initial download 177, PARTIAL_WAITING_FOR_MACRO_AND_LINKER_OWNERS.
Applied Linker bank settings. Two saved references remain unresolved.
Received macro `3/50` and patriarch shout `13/105` in the ordinary client.
[Evidence and remaining work](research/client455-linker-download.md)

2026-11-11 — Initial download 176, PARTIAL_WAITING_FOR_LINKER_AND_ITEM_OWNERS.
Applied supported mastery fields and resolved seven quest catalog records.
The live client handled empty unit and miner lists and received `3/45`.
Linker application, the quest journal, item owners and world entry remain open.
[Evidence and remaining work](research/client455-mastery-quests.md)

2026-11-11 — Initial download 175, PARTIAL_WAITING_FOR_MASTERY_AND_ITEM_OWNERS.
The ordinary client applies supported base fields for map 0, parses 21
inventory records and 82 Force records, and receives the 322-byte mastery reply.
The legacy item providers apply zero of those records. Build 0280bf77… x86.
Both pins agree on eight full functions and 2,162 instructions. Address coverage
2,658, full listings 855, partial bindings 299. World entry remains open.
[Evidence and remaining work](research/client455-initial-download.md)

2026-11-11 — Target windows and dungeon counter 174, PARTIAL_WAITING_FOR_BASE_DECODER.
The ordinary client sends 3/3 after accepted selection and receives the
431-byte 3/4 reply. Four Taiwan frames pass with the 455 target skins.
Build c85bd40d… x86. Both pins agree on 20 bodies and 1,563 instructions.
Address coverage 2,650, full listings 847, partial bindings 293.
Base decoding, inventory request and world entry remain open.
[Evidence and remaining work](research/client455-target-windows.md)

2026-11-11 — Party window 173, PARTIAL_KNOWN_FAILURE.
The ordinary party initializer returns after accepted character selection.
The next fault is selected-mob info window 18 at own RVA 130A9F.
Two Taiwan frames and five messages pass on controlled data, with 11
remote members and eight status slots per side. Base request opcode is
corrected to 3/3, its live send and the 3/4 decoder remain open.
Build 59122c67… x86. Both pins agree on 25 bodies and 4,354 instructions.
Address coverage 2,630, full listings 827, partial bindings 276.
Live party operations and world entry remain open.
[Evidence and remaining work](research/client455-party-window.md)

2026-11-11 — Currency exchange, mining, promotion and Linker 172, PARTIAL_KNOWN_FAILURE.
Ordinary selection passes windows 13, 11 and 36 and attaches the single
Linker. The next fault occurs in party window 19 at own RVA 13088F. Three
Taiwan frames, eight messages, both currency directions and the 8/17-byte
packet boundary pass on controlled inputs. Build 917f69fb… x86. Both pins
agree on 45 bodies and 4,081 instructions. Address coverage 2,605, full
listings 802, partial bindings 255. Live transactions and world entry remain open.
[Evidence and remaining work](research/client455-service-windows.md)

2026-11-11 — Crafting and upgrade windows 171, PARTIAL_KNOWN_FAILURE.
Window 15 uses three recipe groups, 9/5/2 tabs and 20 visible cells.
Window 16 uses six upgrade slots. Four Taiwan frames, 14 window messages
and merchant paging regression pass. Live selection returns from both
initializers and reaches the exchange window skin fault at own RVA 130FFF.
Build c9aeaf27… x86. Both pins checked for 24 bodies and 2,897 instructions.
Address coverage 2,562, complete listings 758, partial bindings 217.
Recipe data, transactions and world entry remain open.
[Evidence and remaining work](research/client455-item-work.md)

2026-11-11 — Player exchange and ore processing 170, PARTIAL_KNOWN_FAILURE.
Trade uses window 23 and 15 slots per side. Ore uses window 12, a 40-slot
package and 20 visible results. Controlled offers, three messages, ore
scrolling and three Taiwan frames pass. Live selection reaches the old
ItemMakeWindow skin fault at own RVA 13066F after both initializers return.
Build ad434f01… x86, no unresolved symbols. Both pins checked for 21 bodies
and 2,929 instructions. Address coverage 2,538, complete listings 734,
partial bindings 197. Transactions and world entry remain open.
[Evidence and remaining work](research/client455-trade-ore.md)

2026-11-11 — NPC merchant window 169, PARTIAL_KNOWN_FAILURE.
Board 9 starts with 200 slots and window 7. Stock Taiwan skins and paging
over 21 controlled rows per mode passed, with three reviewed frames. Live
selection returns from the merchant initializer and reaches the legacy player
trade skin crash at own RVA 12FF6F. Build 7d348e69… x86, entry 183430,
no unresolved symbols. Both pins checked for 16 bodies and 1,989 instructions.
Address coverage 2,517, complete listings 713, partial bindings 178.
[Evidence and remaining work](research/client455-shop-window.md)

2026-11-11 — Skill and Force windows 168, PARTIAL_KNOWN_FAILURE.
Ordinary Skill and Force initializers use five tabs each and the recovered
TabBoard. Three viewed frames, four stock localized EDF rows, three race cases
and the help HWND message passed in the component. Automatic population and
gameplay remain open. Live selection reaches the legacy ShopWindow skin crash
at own RVA 12F8BF. Build 83b60d77… x86, entry 182D80, no unresolved symbols.
24 full functions and 2,518 instructions checked in both pins. Address coverage
2,501 (+22), full listings 697 (+24), partial bindings 166. World and M9 open.
[Evidence and remaining work](research/client455-skill-force-window.md)

2026-11-11 — UnitTuning and UnitStorehouse 167, PARTIAL_KNOWN_FAILURE.
Ordinary 455 client now activates tuning 8 × 200 and storehouse 1 × 4 with
windows 34 and 35. Stock Taiwanese assets, three HWND messages and three GPU
frames verified. Live selection passes both initializers and reaches the old
SkillWindow skin failure at own RVA 1305EF. Build 23332d3f… x86, entry 183A80,
182 client / 67 engine / 20 shared modules, no unresolved symbols. The world
and M9 remain open. Both pins checked for 16 functions and 3,815 instructions.
Address coverage 2,479 (+16), full listings 673 (+16), partial bindings 148.
[Evidence and remaining work](research/client455-unit-windows.md)

2026-11-11 — MainGame Linker startup166, PARTIAL_KNOWN_FAILURE.
Actual ordinary startup now creates Linker6/five banks/ten slots/window3,
activates0..4 and opens it. No obsolete separate Belt exists at this location;
other legacy consumers retain their guards. Native7d430eab:50admitted clone
owners/16real originals,actual window3 HWND-to-manager-to-bank4 route and8viewed
GPUframes PASS. Shared staging38assets/79608818linkedbytes/0newpoolbytes.
Own fe40637c…/x86/entry183720/2369024bytes,182/67/20/build-link0. Live choice
accepted;Linker startup returned,next old UnitTuning.Init/SetSprite fails at
ownGetSpriteXL13028F. World/fullfactory/M9OPEN. Complete6ASM/CFG/3032instructions
bothpins;analysis2463(+2)/657(+6),IDA37871unchanged;137partialbindingsunchanged.
Corrected old084factory undercount:53regex identities omitted explicit-this
CBlackListBoard12bytes/slot30. All54allocation sites now checked;17sourceclasses,
37missing owners,semantics of existing17not accepted. IDAa06985c9/5c316b5a
saved/closed/list0;ownjobsdone/handoffremoved;server/originalsunchanged.
research/client455-board-startup.md;inventory/client455-board-startup-checkpoint.json.

2026-11-11 — Inventory views165, PARTIAL_KNOWN_FAILURE.
11.11.2026. Частичная165: подключены настоящие виды инвентаря, сумок20slots и
экипировки16slots. Native459bd43c:3расы/Taiwan/4просмотренных кадра,64bitmoney,
маски/состояния/reload и6маршрутов событий проходят. Final own96afbd62…/x86/
entry182C50/2364928bytes;182client/67engine/20kernels,build/link0.
Live выбор принят, обычный Inventory.Init вернулся. Следом срабатывает собственный
RF455_RejectRemovedLegacyBelt в старом Create_Board. Сумки/equipment Init в живом
пути пока не доказаны;мир не достигнут. Дальше настоящая455фабрика/порядок board
создания,не возврат удалённого старого storage. Potion/hotbar остаются в M9.
52fullfunctions/4375instructions обоих pins. Анализ2461(+42)/651(+45) из37871;
25новых выборочных partialbindings,24standalone,всего137в9реестрах. Это не
готовность. M6/M6F/M7/M9OPEN,0/12,ориентир25%(20–35%) прежний.
Staging32assets/16010369linkedbytes/0newpoolbytes. IDA18a8be40closed/list0,
nativejobsdone/privatehandoff removed,server/originals без изменений.
Gate inventory/client455-inventory-checkpoint.json:PARTIAL_KNOWN_FAILURE.
Доказательства/полный остаток:research/client455-inventory-views.md.

2026-11-11 — Options164, PARTIAL_KNOWN_FAILURE.
11.11.2026. Частичная164: окно настроек455 подключено к обычному клиенту.
Три звуковых и шесть графических регуляторов, радио/переключатели, настоящие
skins/подписи/сообщения проверены; четыре GPU-кадра просмотрены. Исправлено
чтение неизвестного статуса при очистке hover без активного прицеливания;
начальное значение статуса не выдумывается. Точный chat script добавлен в стенд.
Own6b5e61e6…/x86/entry182C50/2364928bytes,182client/67engine/20kernels,
build/link0. Live002: выбор принят, весь обычный Create_UI включая чат вернулся;
следующий отказ — старый CGUIInventoryWindow при создании предметных панелей,
ownRVA12F78F/GetSpriteXL. Мир ещё не достигнут, полный UI455 не принят.
Gate inventory/client455-option-checkpoint.json: PARTIAL_KNOWN_FAILURE.
53полных функции/5879инструкций сверены по обоим pins. Усечённая CFG-выгрузка
заменена полной, verifier проверяет фактическое число блоков. Функции2419(+44)
адресных/606(+47) полных из37871;21новая выборочная partialbinding,112в8реестрах.
Это охват анализа, не готовность. M6/M6F/M7/M9OPEN,0/12,ориентир25%(20–35%).
Before165:165files/6858255private+4295738sharedbytes;клиент не клонировался.
IDA76ab68ba saved/closed/list0,nativejobsdone,privatehandoff removed.
Сервер и оригиналы не менялись. Доказательства: research/client455-options.md.

2026-11-11 — MobControl163 PARTIAL_KNOWN_FAILURE. Actual ordinary16children/
threecommands,real skins,signed HP/FP,stepEXP,resource/name policy restored.
Shared GUI move manager now455 reset/reuse,zero timestamp/duration,float-rounded
sine/exact endpoint,waves/acceleration. Native10c89a6e/four inspected GPUframes/
threeactualHWNDmessages/controlled movement replay PASS.34fullfunctions/3119
instructions bothpins;countryvirtual53 checkedall11tables/bothpins. FullAnimus/
equipmentresourceproducer/tooltippolicy remainopen. Own ae592e21…/x86/entry1821E0/
2362368bytes/build-link0,live choice accepted;MobControlInit returned,next old
Option.SetSprite/Init fatalown12ED3F. Caller/vtable/source corroborated,not unwind.
2375(+28)address/559(+30)full evidence,22newpartialbindings/91selective total,
not full-restoration count. Before163135files preserved;nativepool30assets/
17904385linkedbytes/0newbytes. IDAe410717fclosed/list0,no server/original changes.
World/M6F/M7/M9OPEN,0/12,coarse25%(20–35%) unchanged. research/client455-mob-control.md.

2026-11-11 — Recall162 PARTIAL_KNOWN_FAILURE. Actual window/rows now integrated
into ordinary CGUIRecallWindow: real skins,40byte records,DWORD HP/FP,EXP,state,
scroll/resize and target stale content height. Native a5e7bd7a eight controlled
records/five inspected GPU frames PASS; full Animus producers/settings/link open.
39fullfunctions/3039instructions bothpins; five previously unindexed setter heads
defined in owned IDB only,37865→37870. Positive-SP pseudocode not trusted.
Own e929b1ec…/x86/entry181DA0/2360320bytes/build-link0. Live002 selection accepted,
RecallInit returned; next actual oldMobControl numeric sprite failure own12E81F.
Stack candidates corroborated caller/vtable/source,not unwind. Stack read boundary
bug fixed in diagnostic helper and live repeated; credentials/rawstack not saved.
2347(+37)address/529(+39)full evidence;25newpartial bindings/69selective total,
not full-restoration count. Before162124files preserved,shared nativepool34assets/
81615873linkedbytes/0newbytes. IDAbac5c81dclosed/list0,nooriginal/servercode edits.
World/M6F/M7/M9OPEN,0/12,coarse25%(20–35%) unchanged. research/client455-recall.md.

2026-11-11 — CharInfo161 PARTIAL_KNOWN_FAILURE. Actual ordinary window now uses
three455pages(5/2/4sections),23value owners,real skins/race/mastery/resist/layout.
Nativedb389785/3races/6GPUframes/input/resize PASS;final six images inspected.
Header natural-height correction replaces earlier33923840/161a997c geometry;
only highlight has1x4sheet.60referencefunctions/6095instructions bothpins. Own3ebd9a7d…/x86/
entry181DA0/2360320bytes/build-link0;live selection accepted,CharInfo Init returned.
Next actual failure oldRecall.SetSprite/Init,own12E8FF/GetSpriteXL;world/M9OPEN.
2310(+48)address/490(+51)full function evidence;18newpartialbindings,14prior
TabBoardbindings now connected ordinary owner path,not14newtargetfunctions.
Firsta51live hadno1/14;owned-window background activation-message/delayedEnter
driver fixed observation without OSfocus/globalkeys. Missingproviders remain
explicit. Before161113files saved;IDAa2513525closed/list0,nooriginal/servercode edits.

2026-11-11 — TabBoard160 PARTIAL_COMPONENT_ONLY. Actual expandable-section
source,17functions/1318instructions both455pins. Five-section native example,
real skins/NDLanguage/scroll/reflow/resize/RAII/four GPUframes pass. Style0
thumb reset differs from zero-amount retention;wrong initial reload equality
oracle rejected and corrected from target evidence. Finalnative a7aba19d.
Normal7354a931… builds/links,component object inlibrary,butnotretained inordinary
PE/CharInfo. Runtime sections equal159except verified linker debugtimestamp
RVA210254. No repeated live run;last ordinary failure remainsCharInfo159.
Function2262(+16)/complete439(+17);14partialcomponent bindings,notfullclient.
Before160104files preserved;no server/original changes,IDA5f9b1aa3closed/list0.

2026-11-11 — HUD159 PARTIAL_KNOWN_FAILURE. Actualmain/common/EtcUI4-bar
upperpanel/17children/level/charinfovalues restored. Native7ca856c6/GPU3frames/
threshold7/reload pass. Ownafb30309… live selectionaccepted,priorGaugecrash
passed;nextlegacyCharInfo.SetSprite/Init fatal12C53F. World/M9OPEN.
19referencefunctions/1406instructions bothpins;2246/422functionevidence.

2026-11-11 — Selection158 PARTIAL_KNOWN_FAILURE. FullASM/CFG6+3/689instructions
both455pins,x86/base400000. 1/14oneBYTE/1/15reply22 (WORDresult,serial32,money64)
andtyped6default/11worn Avatar transfer/skip flag restored. Actual addressed
Enter viaownchild HWND/PID accepted byserver;MainGame::Create_UI reached,then
legacy gauge skin fatal own12C8AF. Nativewire/4wallet/defaultretain/PRNG and
3priorPNG pass;world/M9 remainopen. OwnDF69C7EF…/entry17FCD0;before158=157/69files.
Functionevidence2231(+6)/complete403(+7);4sourcebindings,notfullequivalence.
Server/originals unchanged,privatehandoffremoved. IDAb44716bd saved/closed/list0.

2026-11-11 — Actor lighting157 PARTIAL. Target primaryb1b5…/secondary4652…,
x86/base400000,full ASM/CFG208instructions atRVA3CE7A0/04D230/3CEA00.
Actual actor mapcolor/material/negated direction/ambient/specular restored;
12real lobby/gear/GPU cases and3priorPNG pass. Own88dc3d11… live frame370/8000ms
returnedwithout unhandled;viewed comparison shows character no longer nearlyblack.
NoBSP undefined color,legacy blink producers,fullUI/selection/world/M9 open.
3sourcebindings distinguish ordinary retained lighting from probe-only setter.
Function evidence2,225(+3),complete CFG396(+3),not full equivalence count.
Game/server/originals untouched;privatehandoff removed;engine library unchanged.

2026-11-11 — Function-evidence baseline, not restored-function count. Primary
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b/x86/base400000:
IDA37,865; 2,222 unique owners with pinned code evidence, 393 with complete
assembly/CFG, 158 reports. Deduped ranges;5 unresolved queries excluded.
Implementation/equivalence totals remain unclassified; no false ready percent.
docs/function-coverage.md and inventory/client455-function-coverage.json retain
per-RVA evidence; history records future deltas. Targeted audit self-check PASS.
Own156 unchanged; lighting157 remains next. Owned IDA saved/closed/list0.

2026-11-10 — Equipment frame153 PARTIAL. Restored CMesh/CEquip Animation,
FrameMove/end transitions,dummy/always/motion-effect follow andequipment-position
WAV. Virtual120(kind2) isfalse forboth currentwrappers;byte4=2 isnotground.
Ordinary6Avatar defaults nowderivedCEquip. Real ANI end→loop,actor10/Spine17,
Miles,dummy/copy/missingmagic and21controlledbranches pass;6renderPNG equal150.
Own3296a413…/182client/67engine/20kernels/link0;Create/Login/account3Avatar pass.
Fullordinary12-slot player/providers/condition/UI/particles/selection/world/M9open.
Before153 preservesexact152;storageauditunchanged16:34,newfinalpool0,no deletions.
Two fixture expectation errors andrender-report baselinepath fixed,documented.
[Evidence](research/client455-equipment-frame.md). Estimate25%(20–35%)unchanged.

2026-11-10 — Equipment providers146 PARTIAL_COMPONENT. Actual ANI selection,
fallback/frame state,pose calls,fade andmounting height source restored.
24completefunctions/2220instructions/373CFG equalpins;65realcases/48ANI/
12models,64realposecalls/1expectedinnerfailure/20ownerlifts pass. Zero-maximum
ANI preserved. Affectedcontroller/clone rebuiltpass;ordinary145PEunchanged.
Itemeffects/typedconditions/ordinaryappearance remainopen. Firstpool+53MB,
repeat0. IDAclosed/list0,nooriginalEXE/serveractivity.
[Evidence](research/client455-equipment-providers.md). M6/M6F/M7/M9OPEN.

2026-11-10 — Player equipment146 PARTIAL_COMPONENT.13typedslots/controller
andselected normal-item clone restored;32fullfunctions/1640instructions/225CFG
match bothpins. Real Item/Resource/model/texture/controller executions,aliases,
wrapper sharing andcloneconsumer lifetime pass. Own145ordinaryPE unchanged.
Required production animation/condition/effect callbacks remain open;probe
recorders are explicitly notgameplay.4539BD/453A80 stores equipmentowner588,
notPlayer.SetPrevAction. No originalEXE/server changes;IDAclosed/list0,newpool0.
[Evidence](research/client455-player-equipment.md).M6/M6F/M7/M9OPEN.

2026-11-10 — Assessment and equipment145 PARTIAL. Final ownPE1a355372…:
18fullfunctions/630instructions/60CFG match both pins;typed equipment resources
and6ordinary Avatar default slots connected.32real models/33GPU textures/
30actual default creations/teardown verified;affected account andordinary Login
frame70/3235ms pass. FullPlayerProc/appearance/selection remainopen.
See research/client455-equipment.md. Assessment25%(20–35%),0/12fullaccepted;
coarse scope unchanged. Roadmap compacted around A–E connectedclient scenarios;
fulloldroadmap/queue archived. No referenceEXE/server changes or oldasset deletion.

# RF Online client reconstruction journal

2026-11-10 — Initial item bootstrap142 PARTIAL. Ordinary Login now invokes real
ItemDataMgr cash/set/Item47+ND path. Four newfullfunctions/257instructions/27CFG
and11country vslot160=true pinnedboth;existing Item588asm reused. Cash selector
uses fullDWORD decimal suffix;ND DWORD16 overlay/base retained oncount mismatch.
Production CALL/JMP cash->set->Item order decoded. Six real ko/zh/ru/default/zh1/
zh10/ko1 cases pass full47tables/76049rows/descriptions/work arrays and12actual
typed wrappers each. Russia cashND count mismatch andmissing koND_1 continue
Item loading. Legacy ITEM_DATA/derived items/Avatar equipment not migrated;
GetData455 accessor probe-only. New PEf0114c80 ordinary Login frame70/3234ms
viewed,no fatal;wide unchanged suites not rerun. Pool+509445bytes/adopt46.2MB.
Before142 snapshot49 preserved. Next143 character tables/classes/appearance.
25%(20–35%),M6/M6F/M7/M9 OPEN. [Evidence](research/client455-item-bootstrap.md).

2026-11-10 — Resource catalog141 PARTIAL. Ordinary Resource.edf nine groups/
260-328-244 rows and84-byte event owner confirmed. Added target player bone
missing/shape checks and bounded preflight;fixed own missing-return accessor.
7fullfunc/934instructions/108CFG including EH tails equalboth455. Actual manager
registers1267bones/10483meshes/18872ANI;missing NPC parent20483 explains1skip.
Five real player BN+one archivedANI loaded,full rows match independent fingerprints.
1120checked unresolved references503BN/592BBX/25ANI remain;not full asset inventory.
Shared suffixes BN/BBX/ANI/MSH/RFS,firstpool+53.1MB/repeats0. Own PEb3f769a9
ordinary Login frame70/3219ms viewed,no fatal.140account snapshot49 preserved;
unchanged account suite not rerun. Next142 remaining bootstrap/item/class data.
25%(20–35%),M6/M6F/M7/M9 OPEN. [Evidence](research/client455-resource-catalog.md).

2026-11-10 — Registered characters140 PARTIAL. Ordinary request1/8 and reply1/9
use fixed506-byte payload/three164-byte records;real Avatar name/race/level/
64bit money-time/tutorial writer restored.9fullfunc/623instructions/72CFG equal
both pins. Actual encrypted/ring fragment-wrap receiver and three Avatar pass.
Missing probe Character shaders resolved by staging real inputs via shared pool,
27assets/newpool0. Own PEa3002fc4 build/link/unresolved0;fresh ordinary Login
frame70/3203ms viewed. Full table bootstrap/classes/appearance/selection remain
open. Assessment stays25%(20–35%);142overlapping records are not completion.
Next141 real bootstrap and ordinary selection. M6/M6F/M7/M9 OPEN.
[Evidence](research/client455-registered-characters.md),[assessment](docs/roadmap.md).

2026-11-10 — Scene resources137,shared asset staging and functional baseline.
Ordinary restore/release owns5targets andPerbMap;capture helper added,full
Fraction/BBoShasi/particle callers remain open. Current ownPE42213f08/engine
708c892e/unresolved0/fresh existingCreate1;actual resource/copy/fullscreen checks
and5reviewed views pass. Shared inputs reuse owned copies;originals independent,
configs/exes private. Old directories were not deleted. Planning estimate25%
(20–35%) over12weighted systems;next anchors Title/Login→selection→world→gameplay.
Initial138 Title/movie evidence is explicitly AUDIT_OPEN. M6/M6F/M7/M9 OPEN.
[Evidence](research/client455-scene-capture.md),[assessment](docs/roadmap.md).

2026-11-10 — Material layout133. Seven runtime54 layers/material526 restored;
binary read46 prefix retained. Extra floats are specular flickering scale/speed,
text flags800001/800002;shader/light DWORD packing and2048guard restored.
5fullasm/1438instructions/5ranges equalboth455 plusguardcontext. Actual adjacent
binary/text records exact1052bytes each,7layers,3badversions close file handles.
Sharedheaderchanged/full182-20rebuild/ANI-BBX/unresolved0/Create1PASS.
Enginefa88420d/42payload17timestamp8same;PEb9002c4c/entry16CC90.
34freshraw+PNG pixelsbyteequal132;no newvisualinspection/unchangedbulks.
Specialmaterialshader8C9230 consumer/fullpipeline,all7GPUlayers/CRT/clientOPEN.
[Evidence](research/client455-material-layout.md).

2026-11-10 — Map entity owner132. Ordinary EBP record Flag72 bit40 is copied
to successful CEntity+104 before RestoreTexMem;failed/particle branch unchanged.
5fullasm/1665instructions/5ranges equalboth455;1025unchanged instructions reused130.
93physicalEBP/3700rows/1584lit/82shader is inputinventory,not unique assets/completed maps.
Two actualNeutralB loads:21flagged rows,20available owners,knownmissingtrade_bel.
Ordinary visibility queue supplies alpha;4newGPUviewed/fixed-LitGrass realBSP routes.
30fresholdpixels byteequal131/72directiondraws/Create1PASS;unchanged240CPU retained.
Engineb710d6c8/1BSPpayload66same/headersstable;PEeed1a216/entry16C9C0/unresolved0.
Next133:runtime materials extra8/capacity/shader lifecycle.Otherwriters/fullclientOPEN.
[Evidence](research/client455-entity-owner.md).

2026-11-10 — Light direction131. Ordinary CEntity uses existing exact455 affine
inverse/transform and136-byte normalizer body with selected finite sqrt CW policy.
Corrected130:Vector3fTransform was already exactx87,not legacy arithmetic.
10fullasm/411instructions/11ranges equalboth455;3linked bodies verified except
epsilon/CALL relocations.240CPU/12PC-RC modes and72actual indexed LitGrass draws
match independent rational oracle.30freshraw+PNG contents byteequal130;explicit
review reuse. Engine9f334789/1payload66same/sharedheadersstable;PEd1738f4e/
entry16C9B0/unresolved0/ANI-BBX/existingCreate1PASS. Full CRT matherr/errno/status
flags and invalid affine caller output remainOPEN. Next:actualflag40 producers,
runtime material fields/capacity and remaining client acceptance.M6/M9OPEN.
[Evidence](research/client455-light-direction.md).

2026-11-10 — Lighting consumers130. Normal36 geometry and actual entity fixed/
Grass/LitGrass consumers plus capability-gated bump pre/after restored.
17fullasm/3450instructions/18ranges equalboth455.5328selectedPC24 normals bitexact;
5actual draw paths/pinned220-300byte shaders/8material cases PASS.5newGPUviewed,
25oldpixel contents reused with byte equality proof. Full182/20/existingCreate1
PASS. Engine6751765f/40payload19timestamp8same;PE52c25310/entry16C930/unresolved0.
Both fixed/shader flag40 use MODULATE;fixed cleanup preserves LIGHTING and
DIFFUSESOURCE,clears COLORVERTEX and enables SPECULAR. Actual GPU states verified.
Exact lit inverse/normalizer,flag40 producers,material extra fields/layer capacity
and full lighting/world/M9 remain OPEN. No unchanged bulk suites.
[Evidence](research/client455-lighting-consumers.md).

2026-11-10 — Weather owner129. Packed script producers→ordinary virtual CLevel
owner→fog exposure connected. Corrected earlier126/128 case-sensitive claim:
90A5ED uppercase before FOG/ENV,90ACEC lowercase before weather/scene flags.
6fullasm/1546instructions/7ranges including99-byte ctorEHtail equalboth455.
90scriptcases/5fogaggregates/25GPUviewed/20oldframesstable/full182-20/Create1PASS.
Engine9b366d8f/49payload10timestamp8same;PEd678c71b/entry16BAB0/unresolved0.
NeutralB thin geometry strips remain an explicit visual gap;material8000/CPU
consumers/INS/Planet/full lighting/world/M9 OPEN. No unchanged bulk suites.
[Evidence](research/client455-weather-owner.md).

2026-11-10 — Ordinary lighting128. Selected lighting chain/bothfog branches
and real endpoint loaders connected to ordinary frame;previousFog/orbit order
preserved.867CPUcolors/3aggregates exactselectedPC24;27Mie3precision/4scripts/
5valid1invalidR3X/5+3frames/29BSPsubmissions PASS.20GPUviewed,15regressionframes
byteequal126. Engine df47c24a/3changed63same/headersunchanged;PE052f7387/
entry16B900/unresolved0/ANI-BBX/startupCreate1PASS. Actual exposure/game tint
consumers and full lighting/CRT/FP/M9 remainOPEN.
[Evidence](research/client455-sky-lighting-runtime.md).

2026-11-09 — Lighting127 source component.17fullasm/1538instructions equalboth455,
CFGcomplete;previous-Sun/previous-fog frameorder,flag2 endpoint interpolation and
289point softwarefog contracts confirmed.129exact source math cases pass in
PC24/53/64 nearest-even. Not yet ordinary integration;runtime126 unchanged.
MCP66tools/ownedIDAsessionssavedclosed. Full lighting/M9OPEN.
[Evidence](research/client455-sky-lighting.md).

2026-11-09 — Atmosphere126. Actual prepass/resources/Sun scalar update integrated
in ordinary client.16fullasm/2029instructions/19ranges equal both455;positiveCFG
coverage includes lowerchunks missed byheadquery.16prepass branches/72Sun boundary
cases/full4225vertex8192triangle buffers/shader612byteequal;20GPUviewed.
Material/fade/world/Create1PASS,world-fadebyteequal125. Engine744733c2/5payload
changed/62byteequal/headersunchanged;PE4dd76810/entry16A440/unresolved0.
Full lighting/fog/FP-CRT/reset andM9OPEN. Originalmissingtrade_bel warningretained.
[Evidence](research/client455-sky-atmosphere.md).

2026-11-09 — Sky material125. Ordinary sky2 selection/legacyfallback,
actual night-weight slice and flags4/8/10h/20h restored.8fullasm/1696instructions
equalboth455;60profile/3frame/36material+directunloaded cases,26actualdraws/
10zeroskips.5realneutralBsky2+5fade+5worldGPUviewed;fade/worldbyteequal124.
OwnlabvtablecloneAVfixed inobserveronly. NeutralBoriginaltrade_bel missing/1warning.
Enginea11b2823/onlylevel+skyboxchanged/65byteequal;PEf6185924/entry167ED0/
unresolved0/ANI-BBX/startupCreate1PASS. Sun/atmosphere/fullM9OPEN.
[Evidence](research/client455-sky-material.md).

2026-11-09 — Sky fade124. Restored x87 sky fade state, color interpolation
and alpha packing in ordinary engine r3util;4fullasm/282instructions equal both455.
90actual frames+27helper cases/3precision modes/exactstate-fog-quad;8demonstrated
legacySSE fog differences.5realBellato fadeGPU+5worldGPU viewed,world byteequal123.
Onlyr3util.obj changed/66membersbyteequal. Engine9e1b9c67/PE38ba1441/entry167A00/
unresolved0;freshANI-BBX/startup/Create1PASS. Materials/dayprofile/specialprepass
and fullsky/M9OPEN. [Evidence](research/client455-sky-fade.md).

2026-11-09 — Sky projection123. Restored ordinary CLevel slot17 wrapper:near2,
loadedguard/fade,world perspective/ortho restore/frustum;real InitCore flag0/scale5.
6fullasm/1435instructions equalboth455,IDAsavedclosed/list0.12cases/24actualbinds,
5realBellatoskyGPU/translation-near3000-ortho byteequal/clearRGB exact;5worldlight
GPU byteequal122/maps2692/330/ANI-BBX/Create1. Engine67/15derivede826ee1a,
full182client20kernel rebuild/PE182ecac6/unresolved0. Ownobserver vptr issue
and unusedX-byte oracle corrected;production workaround absent. Fullsky/fade/M9OPEN.
[research/client455-sky-projection.md](research/client455-sky-projection.md).

2026-11-09 — BSP leaf122. Restored inverse-affine GetLeafNum using supplied
inverse,source455 math and targetleaf0 fallback.13fullasm/971instructions
equalboth455;instance/INS/Planet owners separated,INS normal reader returns0
without claiming fullbranch acceptance.140finitecases/1680exactXYZbytes;
Bellato76queue/16clock/5viewedGPU byteequal121/maps2692/Create1.
Engine2fa70824 onlybsp.obj changed,66byteequal;headers/clientbuild unchanged.
PEb0b13a09/unresolved0,IDAsavedclosed/list0. Fullrenderer/M9 OPEN.
[research/client455-bsp-leaf.md](research/client455-bsp-leaf.md).

2026-11-09 — BSP light geometry121. Restored selected regular/magic guards,
leaf128/256,face5000/saturation3000,batches3000/2001,owned world/inverse and
explicit D3D9 declaration with ordinary create/release.12fullasm/1725instructions
equalboth455,7new/712;IDAsavedclosed/list0.33smallfixtures/1580880vertexbytes,
Bellato76queue/16OSclock/5viewedGPU byteequal120,maps2692/330/ANI-BBX/Create1.
Engine67/14derived12534d28;PE933c276a/182client20kernel/unresolved0.
Exact120engine/PE preserved;sharedheader causes wider COFF payload/relocation
changes,no single-object claim. Placed transform owners/fullrenderer/M9 OPEN.
[research/client455-light-geometry.md](research/client455-light-geometry.md).

2026-11-09 — World frame120. Corrected119wrong class assignment:ordinary
CLevel ctor/vtable/owner prove current-view8E7850;previous-view8EB7F0 is INS.
119previous-view acceptance retracted.26fullasm/2772instructions+2vtables equal
both455;2IDAsavedclosed/list0.76light queue ops/16realOSclock±1/Bellato visible
magic+regular+archivedFX light/exactclearcontrol;10GPUviewed/maps2692/Create1.
Engine67onlylevel.obj changed,66byteequal;ownPE0806b113. Known target geometry
guards/batches/worldmatrix differences remain unported;full renderer/M9 OPEN.
[research/client455-world-frame.md](research/client455-world-frame.md).


2026-11-09 — Camera quake119. Ported interpolation/sway/distance decay and
map previous-view publish order;successful map load stops sway.18fullasm/2600
instructions equalboth455,IDAsavedclosed/list0. CPU142events/2921exactscalars;
real archived impact545frames/onset79/151active/26160exactscalars/CLevel→D3Dview.
5GPUviewed/maps2692/330/Create1. Engine67onlyr3util+level changed,65byteequal.
OwnPE406b400e/182-20-70/unresolved0;exact118engine/PE retained. Fullworld/timer/
control/Empty/INS/FP/CRT/allclient/M9 acceptance open.
[research/client455-quake.md](research/client455-quake.md).


2026-11-09 — Texture lifetime118. Matched target R3T shared-counter/release
behavior and preserved20warnings. Fixed Warning CP949 label and no-callback
return.18fullasm/999instructions+55tail;IDAsavedclosed/list0. Actual109+649,
21owners/24calls/4shared/20FX+132world COM releases/lastpins0/trackedDmalloc0;
5GPUviewed,map2692/330/Create1. Engine67dce960bd:onlyjerror code changed,
65membersbyteequal,r3text timestamp-only. Oldengine/PE snapshots retained.
Full device/texture/world/gameplay/M9 acceptance remains open.
[research/client455-texture-lifetime.md](research/client455-texture-lifetime.md).


2026-11-09 — Map data117. Ordinary CLand loads real Map/NDMap110 and both
appended sections:660 labels/257919 image bytes. Dynamic588/288/96/84 owners;
actual maxima54portals/62mines. Real BSP bounds/map geometry reach ordinary
MiniMap;old8map tables/clamp removed.12equalbody/12fullasm/1850instructions,
2IDAsavedclosed/list0. Native2692/330geometry cases/whole canonical equality;
8incompatible locales refused,only suppliedzh-tw110 accepted. OwnPEfd8b5070/
182-20-70/unresolved0/Create1;engine unchanged. No new GPU/fullworld/bulk run.
Full mapUI/layer consumers/world/texture lifetime/M9 remain open.
[research/client455-map-data.md](research/client455-map-data.md).


112 PARTIAL_COMPONENT: подтверждён настоящий вход начала прицела — client
Nuclear processor,group60/opcode0/result0,а не input callback.45body ranges/
22fullasm/903instructions совпали между двумя455;ctor/vtable/RTTI подтверждены.
Восстановлен C++decoder всех9 payload layouts:2429 коротких native assertions
PASS,включая packed14/count0..255/short/null/float bits. Это отдельный source
component,ordinary receiver ещё не подключён. Runtime111/PE031df367…/engine
неизменены,его suites не повторены. Guard использует action category5 и internal
Character DWORD640&3,а не status17708/serverflags;нужны реальные writers/UI.
Следующая113 — actual network receiver+guard/selection/dialog/record owners.
Component gate:nuclear-wire-checkpoint; runtime gate111 current. M6/M6F/M7/M9 OPEN.
[Доказательства112](research/client455-nuclear-protocol.md).

Последний runtime результат111:

111 PARTIAL: обычный formatter подключён к actual Login и четырём панелям
чата/центру экрана. Обычный typed hover у настоящего Avatar с pending1 теперь
отменяет реальный прицел/звук,обнуляет координаты и выводит C1A до item mutation.
83 целевые проверки с реальным EDF предметом/BSP/6effects/Miles проходят.
Новая PE031df367…/entry161590/182client-20kernel-64facade/unresolved0/Create1.
Свежие center69/status62 и15 просмотренных GPU кадров;10 center/hover побайтно
равны109. InsertText455 теперь удержан обычной PE. CE7 core проверен вlab,
но его game-action registration ещё нет и helper удалён ordinary linker.
Gate111 current,109 historical. Tutorial только routing kernel;полные stages/
Login/auth/chat UI и прочие client-acceptance gaps открыты. Далее113 — actual network receiver/guard для начала прицеливания. M6/M6F/M7/M9 OPEN.
[Доказательства111](research/client455-message-runtime.md).

Историческое исследование110:

Исследование110: общий dispatch и настоящие C1A/CE7/Login цепочки подтверждены
на двух455:22 функции/22fullasm/1254instructions,22bodies+46-byte EH region,
23 decoded calls и RTTI CGP_LogIn. Login пишет256-byte сообщение и рисует его
внизу экрана; Tutorial2 имеет отдельный counter и фиксирует style2/category3.
При отмене C1A идёт после Clear эффекта/звука,до hover mutation. При начале CE7
идёт после request-state clear,до SetPending;повторное начало снова пишет CE7.
Важно:legacy MainGame2→target3 через существующий bridge,не Tutorial2.
Это AUDIT_OPEN:обычный source/runtime ещё не изменён. На момент110 gate109 оставался текущим.
Далее111 — перенести подтверждённую цепочку с actual Login/chat/center и live
hover/effect/Miles,а не повторять аудит. M6/M6F/M7/M9 OPEN.
[Доказательства110](research/client455-message-dispatch.md).

Работа109 — 109 PARTIAL: восстановлены профиль36 стилей и вставка в четыре настоящие панели
чата:14 категорий, настройки, фильтры и перенос строк.385 целевых проверок,
8 реальных файлов/288 записей и5 просмотренных кадров чата проходят.
Сохранены особенности455: fallback13, byte-lexer Taiwan и signed settings masks.
Профиль/init подключены к обычному MainGame; новый InsertText455 пока вызывается
только full-object lab, игровые legacy callers ещё не перенесены.
Свежие center69/6hover/Create1 проходят;10 кадров побайтно равны108.
PE ef33b250…/entry160400/182-20-63/unresolved0. Gate109 historical,108 historical.
Общий C1A/CE7 dispatch, live pending1 hover и полный chat UI открыты.
M6/M6F/M7/M9 OPEN; дальнейший участок110 — общие сообщения и отмена прицела.
[Доказательства109](research/client455-chat.md).

Исторический108:

108 PARTIAL: в настоящем CGP_MainGame восстановлен владелец экранных сообщений:
queue64/active84/max3,59-byte CRT split,pacing500ms,fade3600ms и medium GDI16.
69 проверок и4 просмотренных GPU кадра реальных C1A/CE7 проходят;после fade кадр
пуст. Это прямой Add в actual stage member,не полный C1A/chat dispatch.
Прицел перенесён из early effects update в late Render после UI;порядок
подтверждён вызовами в собственной PE. BSP/Miles29/status62/6hover/Create1
проходят;hover побайтно равен107. PE5ad0b484…/entry15b6d0/182-20-61/unresolved0.
Gate108 historical,107 historical. Full chat/C1A/live pending1 hover,полный teardown
этапа и другие client-acceptance gaps открыты. M6/M6F/M7/M9 OPEN.
[Доказательства](research/client455-system-messages.md).


Исследование108:21selected functions/17fullasm/2284instructions/21equalranges,
native IDAffcaa552 saved/closed/list0. Подтверждены center-message queue64,
active84/max3,update/fade/draw,lifetime и C1A dispatch через4pane chat.
Выявлено конкретное расхождение107: nuclear Frame должен идти в late Render
после UI Draw,а не в early effects update. Исправление и message runtime ещё
открыты; текущий runtime gate107. [Подробности](research/client455-system-messages.md).

Работа107 — 107 PARTIAL: в CMainApp восстановлен core прицеливания20: pending, отдельная
командная позиция, курсор через настоящий BSP, перемещение6 частей эффекта и
tagged Miles Radar.29 реальных проверок проходят; память785169→785169.
Pending0 разрешает hover при соответствующем статусе; pending1 пока отказывает
до мутации из-за отсутствующего C1A message provider. Игровых command producers
ещё нет; SetPending проверен в full-object lab, но удалён из обычной PE linker.
Новая PEd09eec8d…/entry15adc0/182-20-60/unresolved0/Create1. Status62/magic36/
resources66/audio157/runtime573/account/hotbar7/storage3 проходят;10 GPU frames
просмотрены,6 hover побайтно равны106. Gate107 current,106 historical.
Full nuclear/world/message/device/client acceptance ещё открыты. M6/M6F/M7/M9 OPEN.
[Доказательства](research/client455-nuclear-aiming.md).


Работа106 — 106 PARTIAL: настоящий прицел455 обновляется и рисуется через обычный
effectcore в контрольной D3D сцене: вращающийся радар/волна,6 tracks,90 ticks.
После обычной отмены children/master исчезают за62 ticks, кадр очищается.
Восстановлены512 активных эффектов, eviction/release и два render passes.
Просмотрены4 новых кадра эффекта и6 hover кадров; hover byte-equal105.
Предупреждения R3T подтверждены в коде455 и сохранены; память стенда освобождена.
Новая PE12ca86c5…/entry15ab00/182-20-59/unresolved0/Create1. Адресные регрессии
resources66/magic36/status58/audio157/account/hotbar7/storage3 проходят.
Gate106 current,105 historical. Full nuclear owner/world pipeline/device
lifecycle ещё открыты. M6/M6F/M7/M9 OPEN.
[Доказательства](research/client455-effect-runtime.md).

Работа105 — 105 PARTIAL: восстановлен штатный владелец архивов Effect и автоматический
выбор группы при запуске эффекта/первой загрузке entity и particle. Обычный
прицел читает настоящий cue и загружает6 моделей/5 particle recipes/10 clones
с реальными D3D текстурами.66 проверок проходят;6 legacy R3T release warnings
и полный FrameMove/render остаются открытыми. Глобальные texture tables
освобождает отдельный owner: в стенде память возвращается к исходной.
PE015a25c2…/entry15a320,182 client/20 kernel/59 facade,unresolved0/Create1.
Magic36/status58/audio157/account/hotbar7/storage3 и6 просмотренных hover кадров
сохранены; кадры побайтно равны104. Gate105 current,104 historical.
M6/M6F/M7/M9 OPEN. Полное ядерное прицеливание ещё не принято.
[Доказательства](research/client455-effect-resources.md).

Работа104 — 104 PARTIAL: восстановлены формат эффекта на 64 дорожки, parser и временная
выборка CProcessMagic, EffectInfo56 и runtime456. Обычный кэш читает настоящий
скрипт ядерного прицела из RPK: все шесть дорожек проверены побайтно.
36 целевых проверок проходят; status58/audio157/account/hotbar7/storage3 сохранены.
Новая PE0419f2c0…/entry15a1f0: 182 client / 20 kernel / 59 facade, unresolved 0,
прежний Create→1. Шесть просмотренных hover кадров побайтно равны103.
Текущий gate: inventory/client455-magic-checkpoint.json; gate103 исторический.
Полная отрисовка эффекта и отмена прицеливания ещё открыты. M6/M6F/M7/M9 OPEN.
[Доказательства](research/client455-magic.md).

Работа103 — 103 PARTIAL: восстановлена звуковая зависимость ядерного прицеливания —
tagged3D audio с настоящим Miles,30 каналами и кэшем64 записей. CMainApp
открывает provider/listener в обычном Create; точная новая PE проходит Create→1.
157 проверок реального WAV/меток/остановки/LRU проходят. Статус58, account,
hotbar7/storage3 сохранены;6 просмотренных кадров hover побайтно равны102.
Новая PEcf7ac5e0…/entry159670,182client/20kernels/58facade,0unresolved.
Gate: inventory/client455-tagged-audio-checkpoint.json;102 теперь исторический.
Сам эффект и отмена ядерного прицеливания ещё не подключены. M6/M6F/M7/M9 OPEN.
[Доказательства](research/client455-tagged-audio.md).

Работа102 — 102 PARTIAL: восстановлены поле статуса персонажа, его вычисление из64-битных
флагов и условие отмены перетаскивания. Настоящий обычный Avatar теперь может
брать, отпускать и возвращать предмет. Прошли58 CPU проверок;6 просмотренных
GPU кадров побайтно совпали с101. Отмена ядерного прицеливания ещё не перенесена:
эта ветка явно отказывает до изменения предмета на курсоре.
Новая PE:5f1f0f77…, entry1587b0;182 клиентских/20 kernel/57 facade модулей,
0 неразрешённых символов; прежний Create вернул1. Account, hotbar7 и storage3
проходят. Текущий gate: inventory/client455-player-status-checkpoint.json.
Gate101 теперь исторический. M6/M6F/M7/M9 остаются открытыми.
[Доказательства](research/client455-player-status.md).

2026-11-07 — Board-hover101. Restored own Copy620 andordinary typedmanager/
screen ownership withtwo backups,operationfallback,replace/clear/return,rawlock/
center-before-resize andone manager timerUpdate. ActualLinkerforward returns0
aftersuccess;rawslot2keptseparatefromGetBoardalias.23functions/1156asm/23equalranges;
IDAf131119f savedclosed/list0.5kinds+bare/256IDs/mixedrefusals/Questnamerefusal/
6newviewedGPU pass;32previousframes byteequal. Offline network owner initialized.
182-20-57/0unresolved/PEe77ec7e7/entry1586b0/Create1/hotbar7/storage3/account pass.
Engine546a unchanged;nooriginal/serverwrites/inputEXEs/newinstalls/remotes.
OnlyactualnullAvatarbranch admitted;livepredicate/cancel/queue/3tooltipcontexts/
gamehandlers/fullAdd/bootstrap remainmandatory. Gate101current,100historical;
M6/M6F/M7/M9OPEN;next102livecancelowners thenhandlers/queue/providers.
[Evidence](research/client455-board-hover.md).

2026-11-07 — Item-lock100 dependency. Restored actualflag21lockchild onordinary
GUIItem/CBoardObject/LinkerAdd:real52/0/0 DXT1 original8x12/texture8x16,rawBYTE
visibility vsnormalizedwrapperflag,position/copy/empty/Remove/unclippedlock in
clippeditemDraw. Targetresize handledbyownBindLock;legacybaseunchanged.
17functions/1610asm/17equalranges;IDA5eef459d savedclosed/list0.256raw/256wrapper/
18geometry/6newviewedGPU pass,35previousreviewedframes byteequal. Three other
providerrefusals retained.182-20-56/0unresolved/newPE49882fc3/entry157aa0/Create1,
hotbar7/storage3/account pass;engine546a unchanged. Gate100current,099historical.
Exploredhovermanagerdualbackup dependency,notimplemented;next101typedhover/
screen thenfullhandlers/livecallbacks/potion/Macro/Vending/fullAdd/bootstrap.
No unchanged159k/world/audio/bulk reruns;nooriginal/serverwrites/inputEXEexecute.
M6/M6F/M7/M9OPEN. [Evidence](research/client455-item-lock.md).

2026-11-07 — Ready-cooldown099 runtime selected. OrdinaryCLinkBoard now has
50records/cacheadmission/expiry/partialremove/originallookup/SFgroupdelay routes;
GUIItem readychild draws real455sheet128px/8x5/FPS34/SRCALPHA-ONE. Sourceowned
state/loop/UV/copy-reset/centering andtargetpendingerasequirk preserved.
132state/48grid/6viewedGPU pass;20previousreviewedframes byteequal. Actualglobal
sourcepack manuallystaged,syntheticSFCpuicons;notfullAdd/bootstrap/game acceptance.
AddedconsistentnonvirtualCSprite texturegetter overlay toderivedengine/client;
old033/source retained,derived082lib replaced,no separateoldsnapshot. Engine546a…,
newPE6b30676b…/entry157830/182-20-56/0unresolved;hotbar7/storage3/account/engine
contracts/Create1 pass. IDAfa7d0341 savedclosed/list0;8additionalfunctions/248asm/
12equalranges beyondstatic09979/5906/82. Newgate099 current;098runtimehistorical.
Fullhandlers/livecallbacks/potion/lock/Macro/Vending/fullAdd/bootstrap/M9OPEN.
No unchangedworld/audio/159k/bulk reruns/serverwrites/inputEXEexecution.
[Evidence](research/client455-ready-cooldown.md).

2026-11-07 — Linker-cooldown099 static audit.79canonicalfunctions/5906asm/
82equalranges/20customvirtualentries pinned onbothclients. Admission=rootrow
membership ORactive,notIsShow. Readychild1040 uses realcommon13:0 sheet1024x640/
texture1024x1024/8x5/128/FPS34/blend3SRCALPHA-ONE;legacyAni/Draw differ.
Foundrequireddependencybeforeactualcache/handlers;erase/outerincrement quirk,
remove partialreset vs expiry fullreset anddistinctlookup routes recorded.
IDA31e85147 savedclosed/list0. Production/gate098 unchanged,noGPU/bulkreruns.
STATIC_ONLY_NOT_IMPLEMENTED;M6/M6F/M7/M9OPEN;next ownreadycue+cache+handlers.
[Evidence](research/client455-linker-cooldown.md).

2026-11-07 — GUI-timer098. ActualtypedCGUIItem now owns state/update/copy/reset/
radialdraw/labels andrealregistry fanout;typedLinker query restored.32equalranges/
29functions/2791asm;175state/112label/57rays/171triangles pass. Clockwrap/signed
remainder/strictthresholds/rawBOOL/partialwrites/duplicates preserved. Decoded
CW027f corrects exploratory133f assumption;CPU-selected SSEtan/FPexceptions open.
Unclippedgradeorder corrected toimage→frame per61B6B0;clippedretained.29GPUframes
viewed,11of23oldframes change/12equal;targeted092rerun justifiedbylayerchange.
NewPEd943ef46/entry156570/182-20-54/0unresolved/Create1,hotbar7/storage3/account
pass. IDA316a9b70 savedclosed/list0. No unchangedworld/audio/159k/bulk reruns.
Gate098current,097runtimehistorical;next099cooldowncache/actualhandlers then
livecallbacks/lock/Macro/Vending/fullAdd/bootstrap. M6/M6F/M7/M9OPEN.
[Evidence](research/client455-gui-timer.md).

2026-11-07 — Linker-window097. ActualCLinkBoard now embeds banked455window,
ordinaryInit/Draw/layout/scale/controls/MouseEvent/PostMessage/bitmap numbers.
51equalranges/36functions/3509asm/14doubles plus signed50C JGEwindow.21layout/
1050icons/320cycles/48events/1792glyphs/realGUIobserverqueue/8viewedGPU pass.
16actualoriginals/50admittedclones;Potion11excludedwhilecooldownrefuses.Use native
recording,notactualgameplay.096owners/094metadata fresh,6rawframes byte-equal;
hotbar7/storage3/account/newPE9d8b57ad/entry155690/182-20-53/Create1pass.
Image-text clipformula andpersistentV preserved;negative50C storeslowBYTE after
signedcomparison,correctedfromunsignedguard. Typedtimer/livecallbacks/fullactions/
lock/Macro/Vending/fullAdd/bootstrap remainopen. IDAa69bf228+message savedclosed/
list0;no newinstalls/serverwrites/inputEXEs or unchangedworld/audio/159k/bulkreruns.
Gate097 current,096runtimehistorical;next098timer/cooldown/actualhandlers.M9OPEN.
[Evidence](research/client455-linker-window.md).

2026-11-07 — Linker-owners096. OrdinaryCLinkBoard Add/Remove/Clear now clone/own
typed wrappers and bankedwindow icons,register/unregister via095.21equalranges/
1105asm;50ownedclones/5x10/originalrelease/lastowner/destructor/3viewedGPU pass.
Freshnullcallbacks0/1/2 tested with syntheticSF-AnimusCPUicons;Animusfactory uses
permittedphysicaltable metadata,notfullAnimusUI. Fourmissingprovider refusals
tested;no successno-ops. FullCGUILinkWindowlayout/input/scale/livecallbacks/lock/
cooldown/Macro/Vending/fullAdd stillopen.095registry/094metadata fresh,6frames
byte-equal;hotbar7/storage3/account/newPE613a6e97/entry153bd0/182-20-51/Create1pass.
Normalregister/unregister nowretained/actualLinkerbound. IDAbb7e4b5e savedclosed/
list0;no newinstalls/originals/serverwrites or unchangedworld/audio/159k/bulk reruns.
Gate096 current,095runtimehistorical;next097 fullwindow/remainingowners then
Macro-Vending/fullAdd/bootstrap. M6/M6F/M7/M9OPEN.
[Evidence](research/client455-linker-owners.md).

2026-11-07 — Icon-links095. ActualMainApp owns semantic icon buckets;production
typed quantity/usable setters update registered copies.22equalranges/1154asm/
160keys;duplicates/first-remove/currentidentity/emptybucket/WORD/rawBYTE pass.
ThreeGPUframes viewed with realinventory original and2explicitlyregisteredcopies;
unregistered copy staysgray255 whileothers become white2;Dmalloc balanced.
094metadata566/race520/16icons passes with3byte-equalpreviousframes. Hotbar7/
storage3/account/newPEe2741f24/entry1530e0/182-20-50/Create1pass. IDA22f5e8a7
savedclosed/list0;configuredMCPpassed. Typedsetters/find retainedinordinaryPE;
register/unregister unused untilactualLinker/MacroAdd-Remove port. Targetunsafe
erase(end()) refusedexplicitly,trackedgap. Gate095current/094runtimehistorical.
No unchangedworld/audio/159k/oldbulk rerun;no originals/serverwrites. Next096
actualowners/registration/fullAdd/Vending27 thenbootstrap;M6/M6F/M7/M9OPEN.
[Evidence](research/client455-icon-links.md).

2026-11-07 — Item-icon-metadata094. Actual Basic metadata and inventory20 core
restored;ordinaryTakeInItem calls productionfields helper.566metadata/520race-level/
9Quest+SFrefusal/16realiconowners/3viewedGPU/clone-clear-Dmalloc pass. Fullpayload
handoff is verifiedown-entry on actualwindow/sourcepack,not fullCItemBoard.Add;
reader/handoff stillnormalunused. Hotbar/storage/account/newPE85a909e3/Create1pass.
28equalranges/1138asm/15decodedreads;IDA4f540aafclosed/list0. Userfield8bits also
existsinlegacy;earlierdifference wording corrected. No unchanged159k/world/audio/
oldbulk rerun. Currentgate094/093runtimehistorical. Next095 actualAdd/sharedicon
state/Linker6-Macro35-Vending27,thenbootstrap. No originals/serverwrites.
[Evidence](research/client455-item-icon-metadata.md).

2026-11-07 — Item-atlas093. Production typedGUIItem.SetSprite now selectsactual
target8/19atlas cells automatically viaItem/UnitParts/Default callbacks.18equal
ranges/1001asm/47decodedC6stores;880cases/563failures/2WORDrowwraps pass. FourGPU
frames viewed/16syntheticmetadataicons,9previous092frames byte-equal;Dmalloc
reloadbalanced. Owners2013/data575/SF1447/hotbar/storage/account/newPEdbd71f6a/
Create1 pass. IDA4c6c7c2cclosed/list0;configuredMCPprobe passed aftersandbox
worker startupfailure;noinstallation/configchanges. Actualpayloadmetadata/full
children/typedgameowners/bootstrap/M9remainOPEN. Currentgate093/092historical.
No unchangedworld/audio/159k rerun,no serverwrites. Next094payload->iconowners.
[Evidence](research/client455-item-atlas.md).

2026-11-07 — Item-icon092. Ordinary typed wrappers now bindGUIItem index and
grade-border color. Corrected priorcaption hypothesis:1240 is spritegradeframe.
CoreDraw uses real455inventory/item sprites;256grades/120quantityboundaries/
8signedwidths/9viewedGPUframes/reloadDmalloc and production2013owners/575payloads/
1447SF pass. Hotbar/storage/account and newPEe540395b…/Create1 pass.22equalranges/
1740asm/RTTI,IDAaa30c75csavedclosed/list0. Core typed metadata is notfullGUIItemABI;
automatic item atlas, optionalwidgets/mixedconsumers/bootstrap/fullgame stillopen.
Currentgate092;091runtimehistorical,staticrefs retained. No unchangedworld/audio/
159k rerun;no serverwrites. Next093 atlascallbacks/typedconsumers thenbootstrap.
[Evidence](research/client455-item-icon.md).

2026-11-07 — Item-object091. Ordinary CItemObject592/CBoardObject620 share actual
payloads through a CMainApp-owned manager.2013 real bind/clone/pack-removal cases,
two620byteoracles/signedBYTE/retired-primary guard/hotbar keys pass. Production
data575/SF1447 entries pass without a second item archive;hotbar/storage/account
and exact newPE7d7ff847…/Create1 pass.21equalranges/444asm,IDA157b5ed2closed.
Initial facade flags/include/name collisions fixed. Icons/mixed callers/normal
table bootstrap remain explicit gaps;next092. Currentgate091;090historical.
No unchangedGPU/audio/159k suites rerun;no server writes.
[Evidence](research/client455-item-object.md).

2026-11-07 — Resource-object090. Ordinary CObject80/CResObject584 ctor/copy/
name64/virtualClear/flags/effectclear replace legacy48/472 base contracts.
23equalranges/765asm/21decodedstores/7floatconstants,IDA65c60c5dsavedclosed.
NewPEdc6f2c62…/entry1500e0/182-20-42/0unresolved/exactCreate1. Two584byteoracles/
160flags,hotbar/storage/account,actorFX/3worlds and renewedpayload575/SF1447 pass;
15GPUframes viewed. Firstworld lab omitted Character.shaders;runnerstaging fixed,
production unchanged bythatfix. Currentgate090;086/088/089runtimegates historical.
No159k/audio reruns/serverwrites. Next091 actualitemwrappers/owners;M9OPEN.
[Evidence](research/client455-resource-object.md).

2026-11-07 — Item-payloads089. Source Item47/76049rows,Quest12/Character7
readers and five fresh factories/actualprimarymanager/087ownership pass575
selected factory-clone-lifetimes,99AnimusXP boundaries,three completeNDItem
byteoracles,standalone/full-object. Same new.lib passes unchangedSF1447probe;
allfour exit0/buildwarnings0.50equalranges/1796asm/IDA877755f1savedclosed.
Ordinary086/gate unchanged;088runtimegate historical after sharedheaderchange,
staticreference valid/new-librarySFregression here. No unchangedGPU/startup/
159k suites repeated. Realgameowners/fullpayloads/Queststrings/Tutorial/M9OPEN.
Next090 CItemObject/CResObject/ordinaryowners. No server writes.
[Evidence](research/client455-item-payloads.md).

2026-11-07 — Skill-force088. Concrete SF selector1 factory/data owner/primary
manager now drive087clone/release on1447actualrows/ownedwrappers;notrecordinghost.
Standalone/fullobject whole-tablebytes/last-owner erase passed.35equalranges/
1224asm pluspinnednoncontiguousEHwindows;IDAcd8baa1aclosed. Rootcountsmatchzh-tw;
originaliniTaiwan. New exactPEearlyTaiwan/950/6997/localTCP/sound1 passed before
D3D. Ko/ru mismatch4/1 andprefixwrites preserved;originals/config unchanged.
Ordinary086/itsgate current;otherpayloadfactories/ordinarybinding/fullgame/M9OPEN.
[Evidence](research/client455-skill-force-items.md).

2026-11-07 — Item-ownership087. Selected source CItem92/boardwrapper620
copy/clone/refcount/release kernels verified:24equalranges/579asm,8decoded
constructor stores/3whole-recordoracles/12lifetimecases/7BYTEboundaries.
Exact same.lib passes standalone/full-object entry;managerhost recording,
actualfactory/predicates/destructors/ordinaryLinker binding stillOPEN.
Primarycache-empty guard and signedBYTEwrap retained. IDA65f54fa4savedclosed.
Production086 and its gate unchanged;GPU/startup/159k suites not rerun.
Next088 concreteowners/resource lifecycle/view. M9OPEN.
[Evidence](research/client455-item-ownership.md).

2026-11-07 — Hotbar086. Ordinary source CLinkBoard now uploads50-key deltas
through actual group13/op17 send ring/AES with target drag/cache-before-failure
and periodic FrameMove semantics.45equalpinranges/640fullasm,IDA811039d6closed.
Seven exactpackets/storage3runs/account/exactnewPE/Create1 passed. PE82625b3e…,
182/20/42TU,engine9caa283a…unchanged082;oldGPU/159k suites not rerun.
FullLinker wrapperownership/5x10view/input/cooldowns/download/oldbelt/Tutorial
remainOPEN. Next087 actualownership+view. [Evidence](research/client455-hotbar.md).

2026-11-07 — Rvp-runtime079. Ordinary CLevel now calls source camera/timeline
player.3maps/27camera events/82commands, pause/flag16/reload/renderer ownership,
intro26/display8/FSE18/46viewedGPU passed. PE83c1793b…/Create1;67engine/9overlays/
ownedfloatcameraheader,033preserved. 20equalranges/full531+23+14+114asm;
IDA6a789f6fclosed. Corrected078labels:8D5510Render/8D8340Release. Actor/effect/
audio/timer providers refused;fullRVP/Tutorial/M9OPEN. Next080. research/client455-rvp-runtime.md.

2026-11-07 — Rvp078. Source-owned RVP objects/12commands/interpolation restored;
44originals/615actor-records/1569commands and2fixtures passed independent/native
named-field checks. 15ranges equalpins, full1722+85asm; IDAa265e239closed.
77resource refs/34missing exactpaths, not established gameplay blockers.
OrdinaryPE077 unchanged; actual player remains stub. Next079 runtime bindings,
Character/effects/audio andTutorial integration. M9OPEN. research/client455-rvp.md.

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

2026-11-10 — ordinary Login138 PARTIAL. Primary455 x86 SHA b1b5febf…,
root registration RVA230A60,RTTI/vtable RVA6DAD8C:AlwaysTop front/append,
SetParent,then Show(FALSE). Fivefullfunc/221instructions/21CFGblocks match
both pins. Recovered root Add removes overlapping unopened Login panels in
ordinary own PEba23dd6d…;real lobby/waiting frame70/3203ms viewed,no fatal.
43shared assets,new pool bytes0. Full Title/Login/auth/selection/world/M9 OPEN.
Evidence: research/client455-login.md;inventory/client455-login-checkpoint.json.

2026-11-10 — world entry139 PARTIAL. Request group1/op1 now58bytes;reply1/2
now12bytes with cashShop/NPCShop/quest selectors.8fullfunc/1372instructions/
225positive CFGblocks equal2pins. Actual ordinary encrypted send67wirebytes
(before35);bounded receiver/fragment wrap/dialog/failure and success fields PASS.
Own PEeb84c16b…,engine137 unchanged,ordinary Login fresh. Bootstrap/selection/
full455/M9 OPEN. research/client455-world-entry.md;world-entry-checkpoint.json.
2026-11-10 /143:normal CharacterDataMgr Player/SF5/Store/Character7+ND,
typed class lookups иactualSFboards проверены;research/client455-character-tables.md.
Ownb41d50ff… ordinaryLogin PASS;fullAvatarclass/equipment/selection/M9 OPEN.
2026-11-10 /144:actual Avatarclassindex/name writers иencryptedregistered
receiver3realclasses проверены. Own ea25eea5…/ordinaryLogin PASS.
Полныеclassskills/UIlayout/equipment/selection/M9 OPEN;research/client455-avatar-classes.md.

2026-11-10 /146: equipment magic/sound ownership andcleanup source verified
against both pinned x86 binaries.22fullfunctions/1489instructions/222CFG;
actual RPK magicqueue andMiles cloak WAV loop/stop pass. Complete attachment
positions/typed conditions/ordinaryCPlayerProc/appearance remainopen.
Fixed mountingheight input:416940/RVA16940 reads metadata meshID@72,not Item
table index;4additional real discriminators pass.69ANI-provider cases/52ANI/
16models/68poses/24height changes;ordinary145PE unchanged.
NTFS1024link limit reached for280byte sharedBBX;bounded owned pool replicas
allow next run withonly280newbytes,no original hardlinks. Fresh storageaudit:
154.86GiB logical/42.85GiB unique file sizes,not exact diskallocation.
IDA1049c6e2saved/closed/list0;native handles terminal;no originalEXE/server work.
Evidence:research/client455-equipment-effects.md anddocs/progress-report.md.

2026-11-10 /146attachment:23fullfunc/1953instructions/223CFG equal2pins,
including2previouslyconfirmedfunctions;17-entryswitchpinned. Sourceplayerpart/
NPC/weapon/damage position providers andactualmagictranslation pass:25realbody
models/25namedpositions/5races/5cloakmagic/archivedAccretiaANI.28frozencoordcases.
RVA3E0720/3E0B90/3E0D10/3E22F0/3F2D60. Type17Spine→Spine1;18default.
Bindingmatchvalue doesnotselect anothercachematrix;worldbboxheight isscaledagain.
Uninitialised targetfailurecoordinates remainexplicitlyundefined/notaccepted.
Ordinary145/engineunchanged;noordinaryappearanceclaim. Newpoolbytes0.
IDA5c1cdbca saved/closed/list0;nativeexit0. Nexttypedconditions→ordinaryintegration.
Evidence:research/client455-equipment-attachment.md;equipment-attachment-checkpoint.json.

2026-11-10 /146conditions:typed equipment special/upgrade/combinedstats/weakpart
source52fullfunctions/2323instructions/357CFG equal2pins;6switch/weight/vtable
regions. Runtimearmoursetpredicate=payload113,notmetadata160. Baseplayerproc
44C670 always usedforstats evenwhencurrentresourceproc44C630 differs.
22realitems/21accepted,independent200bytemodifier+totals anddetachedremoval pass.
CPU path3assetinputs/newpool7953bytes;noGPU/clientcopy. Ownercallbacksremain
recorders untilordinaryintegration. Ordinary145PEunchanged;M6/M9OPEN.
IDA71813681saved/closed/list0;nativeexit0. Research:client455-equipment-conditions.md.

2026-11-10 /148A:grade MST/DDS/shaders9-10/c92/secondarygeometry andarchiveflag restored;21fullfunctions/2863instructions/239CFG equal2pins. Real model RGB contribution verified. Ordinary lifecycleCALLs/Create/Login passed;typed player/mesh renderer/selection/M9 remainopen. Source+evidence:research/client455-grade-overlay.md. IDAc6eeef7e savedclosed/list0.

149,10.11.2026:typed equipmentRender/default+matrix/fade/alpha/overlay604producer andretained posequeue source/native passed;actualmodel7/14/7draws and2659changedRGB. Ordinaryqueueentrypoints+secondarygeometry retained;Create/Login/account3AvatarPASS. Full13slotplayer andnonzero particle registry OPEN. Ownf4e62e48…/entry179630. research/client455-equipment-draw.md. IDA0a6749ce savedclosed/list0;newpool0;server/originals unchanged.

150,10.11.2026:corrected previous13-slot inference:full4501B0/4502B0 construct12 objects;index12 aliasesfollowingstate. Visibility450810/ctor-copyPRNG verified;ordinaryCreate/Login preserved. research/client455-player-visual.md.

151,10.11.2026:resolved442440 as network PremiumDWORD436028 and40BCE0 as Avatarcombatbonuses24712/24716. Ordinary57/12 state producer connected;full8functions/583instructions/64CFG equal2pins. Actual dispatcher/Avatar/boundaries57-49-1/12rates/NaN/-0 tested;Create/Login/account3Avatar pass. PremiumUI/icon481/post-updatecondition refresh andfullplayer stillopen. Ownd1e44bb9…/entry179970. IDAdfba038a savedclosed/list0;newpool0;originals/server unchanged. research/client455-premium-state.md.

152,10.11.2026:restoredordinaryCharInfo fullDWORD/float stat writers14..18 and3actualbasicrow owners;WORD truncation/emptyfloatsetters removed.6fullfunctions/185instructions/9CFG equal2pins. Actualwindow/childregistration/currentAvatarcaller preserve70000/250000;full455metric/refresh/layout stillopen. FreshCreate/Login/account3AvatarPASS. Own579bc166…/entry179A40. IDAe3deb20c savedclosed/list0;smallprobe1DLL/newpool0;originals/server unchanged. research/client455-char-info-values.md.

154,10.11.2026:primary12-slot CPlayerProc typedowner/frame/render andactualAvatar
defaultgarment/SFcallback/cloak/Miles connected. Own31d24ab9…/x86/entry17F430,
182client/67engine/20kernels/build-link0.24completefunctions/1859instructions/
91positiveCFG matchboth455pins. Realcontrolled assembleddraw:19calls/12657pixels;
remove3752changed,replacementexactPNG;6previousqueue/overlayframes equal153.
Membercopy404A40/4042D0 no rand/AddRef,oldactor/currentProc links retained;
queue527E70 differs. FullCharacterclone lifecycleOPEN;fixturecleanup explicitly
compensated legacyaliases/refs,notaproductionfix. OrdinaryTaiwan Create/Login/
account3AvatarPASS,Login195/3000ms/7firstchance/0unhandled. Fullappearance/
selection/UI/particle/Siege/Unit/gameplay/M9OPEN. research/client455-player-owner.md.

Liveclient evidence: user-startedrf455-v0.4.0,RFOnlineBIN matchesprimarypin;
launcher38e32658… matchesbundle. OwnTCP27830→engine/Miles passes. Launcher-only
6C/03→6C/04 acceptsprovidedtestaccount andreturns16byte rf1:key. Credentials,
identifier/key/rawauthpackets notpersisted. Launcherx64base140000000/RVA24C2C0,
24C7A0,24D0E0/13BE60 diagnostics;notcompleteASMproof orpinnedclientbehavior.
OwnRFgame-auth remainsOPEN. No servercode/config changed,noinputEXEexecuted.
research/client455-live-launcher.md;inventory/client455-live-server.json.

2026-11-10 — Live login155 PARTIAL. Own da42b501…/x86/entry17F660,
182client/67engine/20kernels/build-link0. Real launcher accepts testaccount;
game1/1→1/2(result0) accepted;registered1/9 is178bytes. Fixed incorrect506
minimum byvalidating14+164*count andpadding onlyunused slots. Not original
unsafe-overread equivalence. Registered upgrade nowuses realtyped normal
payload;462170 full16instructions/1CFG bothpins proves BYTE113 write only.
Native compact encrypted fragmentation/boundaries andactual worn payload pass;
three assembledPNG equal154;ordinaryTaiwan Login passes. Live selection still
fails atGetEquipItem@CPlayerProc own10B23←CPlayer::SetAction555FE. World notentered.
Gate inventory/client455-live-login-checkpoint.json;next targetcombat-mode
animation/fade migration. M6/M6F/M7/M9OPEN;estimate25%(20–35%),0/12domains.
Only observed archives staged throughsharedpool;noclient-widecopy/deletion.
Password/rawpackets notsaved;private handoff removed. IDA9079cdac saved/closed,
list0. No servermodifications orinputEXEexecution. See research/client455-live-launcher.md.

2026-11-10 — Combat/Login156 PARTIAL. Own68e02c3d…/x86/entry17F710,
build/link0. Target44BE00 weapon/shield transition,mounted behavior andFPS
lowBYTE fade restored;typed Login reads andeffects Create/Destroy connected.
Actual authenticated selection frame364/8000ms returnswithout unhandled
exception;user observed animation andreported nearlyblack character. Next157
maplight/material path. Initial throw diagnosis waswrong;actualcause was
missing grade material initialization,nowfixed. Three native renderPNG equal155.
Before157 exact156/50files;M6/M6F/M7/M9OPEN. GameBar popup fixed viacurrent-user
capture/DVR0 withbackup;userconfirmed. No original/server changes,credentials
orrawpackets saved. research/client455-combat-transition.md.
