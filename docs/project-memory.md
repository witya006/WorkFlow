# Память проекта

Обновлено 2026-11-10. **132 PARTIAL M6**.
Gate: inventory/client455-entity-owner-checkpoint.json.
Проверка: scripts/Invoke-Python.ps1 scripts/checkpoint_client455_entity_owner.py.
Доказательства: research/client455-entity-owner.md.
Runtime131 исторический; source/math/static proofs сохраняются.
Предыдущая полная память: research/project-memory-before132.md.
Предыдущий goal turn131 — progress, commit91027ae. Текущий132 — progress.

## Цель и обязательные правила

CLIENT ONLY: поддерживаемые исходники и свой RF_Online.bin с полным поведением455.
M9 УЖЕ определён: финальная приёмка без модернизации графики. Старый Goal про M9/M4
устарел. M0–M4 diagnostic/selectedM5 выполнены; M6/M6F/M7/M9 OPEN, M8 не нужен.
Build/Create1/selected component не закрывают docs/client-acceptance.md.
Server только читать reference; не менять/не собирать/не восстанавливать.
Originals immutable, inputEXE never execute, copies under work/, Git local/no push.
Subagents только по явному запросу. Python scripts/Invoke-Python.ps1 file.py, не -c/-m.
VS2026 MSVC x86. Native/GPU jobs sequential. Timeout не restart: опросить тот же
handle до terminal. Перед runtime edit exact engine/PE/MAP/rsp/reports backup.
Ignored != backup. Не повторять159k/unchanged bulk suites без нового риска.
Короткие RU updates <=60s. rg --files перед неизвестными именами; не shell path globs.

## Подтверждено132

Primary SHA b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
secondary46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
x86/base400000.5fullasm/1665instructions/5ranges equalboth455, completeCFG/pcode.
640new instructions:8FF280 EBP load,8FDE00 streams,8F94A0 LoadEntities,8E08A0
RestoreTexMem.1025instruction8E0A20 LoadEntity body reused from complete130 raw.
Raw/session artifacts/client455-progress/entity-owner132-*.json. Session3022d6f4
saved/closed/list0. No live native jobs. Source original files/server untouched.
MCP <=100asm/page, counts/unique/done AND everypositiveCFGblockstart/tail.
No firstpage.asm.lines/aggregate alias. Large raw JSON via <=20k Node chunks.

Actual producer:84-byte _ENTITY_LIST.Flag offset72 bit40 -> CEntity.mFlag offset104.
8F9690 test byte[ebx+eax+48h],40h (f644034840),8F969D OR[esi+ecx+68h],40h
(834c0e6840). Only after successful nonparticle LoadEntity,before RestoreTexMem.
Disabled shader clears ShaderID74 before deriving option2. All static get option20;
only record bit40 is copied,not all record flags. Failed load retains20/22,not40.
New client455_map_entity_owner.inc is inserted into generated CBsp::LoadEntities.
No header/layout changes.

Physical Map/**/*.ebp inventory:93files/3700rows/1584static lit rows/82lit shader rows.
These include alternate/duplicate maps;not unique assets or accepted gameplay.
All original files SHA pinned;parser reads EBP20/84-byte entries independently.
Actual neutralB:77entries/21lit/15lit shader. Known missing trade_bel atentry76
hasflag40,so20available loadedlit owners per pass. Do not claim21loaded or fixinput.
Native work/m9/76a8740b/entity-owner-001,2actual CLand/CLevel loads with shader1/0.
All154runtime owner rows checked against actual EBP.4actualBSPdraws/4GPUframes viewed:
b_gate entry62/instance3435 and b_tree04 entry1/instance0, fixed/LitGrass.
No manual CEntityflag assignment. Actual shader dump300bytes equalsLitGrass1.
Images are own lab,not reference455pixel comparison. Unknown thin geometry gap stays.

Harness corrections:generic runner now optional expected_frames(default5),owner uses4.
Initial21loaded assertion wrong becauseknownmissinginput;actual20 proven.
Initial directRenderOne before ordinaryqueue hadalpha0. Need SetCameraPos,
SetViewMatrix, inverseview and viewproj from camera fixture, FrameMove,
DrawMapRender/DrawMapEntitiesRender to compute visibility/fade Color. Then clear
and render chosen actualinstance separately. CLevel::SetViewMatrix deliberately
doesnot publish inverseview; ordinary R3Move camera does. Do not change production
or manually set Color/flags to satisfy lab. Queue used,not fully accepted equivalent.

## Exact current build and evidence

Engineb710d6c802cc8ead4be3ce171e54789abc6d9f6ca80feb02d52aae4fec677974.
67objects/21derived,1payload R3Engine455Startup.dir\\Release\\bsp.obj changed,
66byteequal131/no timestamp-only. Sharedcamera/vertex/particle/core/level unchanged.
182client/20kernel objects retained,no redundant full rebuild.
PEeed1a216cb7ee90fccad50d883b9e779fea1be46229a6ed5b63d5d72cb3cf227.
2255872bytes/x86/base400000/entry16C9C0/WinMainB98B0/afterCreateB9A24/unresolved0.
No CharacterMR/FORCE. Exact own entry/providers/sound1/window/device/
existingCreate1/contracts and shortANI/BBX PASS. Knownhandled exceptions
40080201/E06D7363/406D1388 retained;fullbootstrap/gameloop notaccepted.
Audit archive names are bsp.obj,not bsp.cpp.obj. Check actual archive member names.

Fresh72LitGrass directions/12FP modes/5entity paths/5328normalbits/8materialstates/
3bumptimes PASS. Previous240CPU math proof unchanged/explicitly retained;three
exactlinked bodies rechecked in newPE. Freshworld76queue/16clock/6oldwarnings,
material60/36/1missing,fade90+27/0warnings,lighting867/3aggregates/27Mie/29BSP/
2warnings,weather90/5aggregates/1missing PASS. All30freshraw+PNG contents
byteequal reviewed131;explicit reviewreuse before132. Four newframes reviewed.
Gate visuallyaccounted34. No159k/unchangedbulks rerun.
Exact131 backups before132 include reports/engine/PE/MAP/rsp/sharedcamera+vertex
headers and research memory/next backups. Feature CLIENT455-MAP-ENTITY-OWNER-132 current.

## Remaining/next133

133:materialruntime526/layer54/extra8/capacity vs source332/layer46/max4.
90B1C0 reads46serialized bytes into54runtime slots. Do not cast source to526.
Broader7slots plausible,needs constructor/reader/writer proof. Restore actual extra
fields and layer limits,then shader caps/failure/reset/OOM and unused register lanes.
Other game/effect flag40 writers,fullvisibility/fade/alpha/camera/world notaccepted.
LitGrass original3-register overreads:shader reads19.xyz/21/22;source unusedlanes
deterministic,complete state-consumer proof OPEN. Geometricdecompressor/GetNormal
fullFP/status remains OPEN. NeutralB upwardcamera/thin strips unknownfidelitygap.
INS/Planet/lensflare/localfog/indirectparams/UI/stages/auth/protocol/Character/
gameplay andall client-acceptance gaps OPEN.

131 light math:existing exact RF455_MatrixInvert/Vector3fTransform reused;
130 called transformlegacy incorrectly.51D5D0 normalizer136bytebody exact except
selectedsqrt CALL. CRT tempCW=(callerCW&0x300)|0x7f; FSQRT nearest/callerPC,
thenrestorecallerCW andfloatstore withcallerRC. Selectedfinite12PC/RC values exact.
Full CRT matherr/errno/precisionerror/unmasked exceptions/NaNInf/status flags OPEN.
Inverseguard0.001 failure ignored bytargetcaller,unspecified stackbytes;no fallback.

Preserve128 previousorbit/currentfar ->Sunposition,newSun/Mie,tintOLDfog,thennewfog.
Fogflag2 endpoints else289grid17x17,nozero-divisor fallback. NegativeZ0=-0;exact19h
Mie discontinuity. R3X4day/8night,absentendpointretention,FOG_COLOR main5/5000notday.
129 uppercase90A5ED FOG/ENV,lower90ACEC weather/scene flags;packedweather1157D3C
BSS0 persistsInitCore/R3X,fullDWORD OR spill,no byteclamp. Missingtrade_bel no substitute.
TemporaryCLevel mustoutliveactive map:destructor freesglobalresources.
D3D observers patch originalFULLvtable57/82/83,restorearoundforward/Get;neverclone119
entries(private driver slots). Goal active,M6/M6F/M7/M9OPEN;no completion onpartial.
