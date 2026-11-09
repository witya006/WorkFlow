# Память проекта

Обновлено2026-11-10. **130 PARTIAL M6**.
Gate inventory/client455-lighting-consumers-checkpoint.json.
Команда scripts/Invoke-Python.ps1 scripts/checkpoint_client455_lighting_consumers.py.
Доказательства research/client455-lighting-consumers.md.129 runtime исторический.
Предыдущая полная память: research/project-memory-before130.md.

## Цель и обязательные правила

CLIENT ONLY: поддерживаемые исходники и свой RF_Online.bin с полным поведением455.
M9 УЖЕ определён:финальная приёмка без модернизации графики. Не повторять вопрос
из старого Goal. M0–M4 diagnostic/selectedM5 завершены;M6/M6F/M7/M9 OPEN,M8 не нужен.
Build/Create1/partial component не закрывают docs/client-acceptance.md.
Server только читать как reference;не менять/не собирать/не восстанавливать.
Originals immutable,inputEXE never execute,copies underwork/,Git local only/no push.
Subagents только по явному запросу. Python scripts/Invoke-Python.ps1 file.py,не-c/-m.
Primary VS2026 MSVC x86. Native/GPU jobs sequential;timeout не restart,дождаться
terminal того же handle. Перед runtime edit exact engine/PE/MAP/rsp/reports backup.
Ignored!=backup. Не повторять159k/unchanged bulk suites без нового риска.
Updates краткоRU<=60s. rg --files перед поиском неизвестного имени;не shell path globs.

## Доказательства130

Primary SHA b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
secondary46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
x86/base400000.17fullasm/3450instructions/18ranges equalboth455,fullCFG/pcode.
Main raw artifacts/client455-progress/lighting-consumers130-reference.json:
16functions/3300instructions. Material-reference.json adds90B1C0/150instructions.
3 owned sessions b02b1824/743cf8cf/eafb9f11 saved/closed/list0; session files pinned.
Transform-context.json has4 contiguous byte contexts/pcode,NOT fullasm proof.
MCP asm<=100/page,counts/unique/done AND everypositive CFGstart including tails.
Shader8DA0C0 headquery71 missedlower8D9F50;queryfromlower gives125 complete.
Keep final125 pages,not duplicate head71. Never alias firstpage.asm.lines and
aggregate (129 collector bug).20k JSON chunks;all130raw now fully saved on disk.

Actual entity path:8E3630 fixedlighting,8E3F10 shaderselection,8E3A00/8E4000 draw,
8FAF70 BSP writesmapcolor andcallsboth. Flag40 priorityover20.8B30B0 map tint
is now used byactual source methods,not just retainedhelper. Daydisabled returns
originalARGB. Fixedlightbuild8B52F0 usesambient divisor412;fixednegateslightdir.
LitGrass usespositive transformed normalized lightdir. Actualshaderfiles original.

New scripts/client455_lighting_port.py createsnormal36 shared r3d3d8455.h:
normal12/color24/UV28/FVF338. CEntity size212 remains. Old source TEX1 had24bytes.
Entity loader accumulatesunitfacenormals bysourcevertexID,then normalizes in-place
for each expandedvertex. Accumulatorpersistsbetweengroupsincludingpriornormalized
values. Exactzero→Y1,noepsilon. SourceGetNormallegacySSE andx87normalizer selected
PC24 finite path verified;allFPmodes/CRT/statusflags NOT accepted.

Materialpre8C7B10/after8C80A0 restored:layer1 flag8000 AND cachedBUMPENVMAP capbit21.
Targetflagfield216 isNOT top-level132. Own logical layer1flag208 because source
record332/layer46/max4; targetruntime526/layer54. Confirmed90B1C0 reads46 serialized
bytes intoeach54 runtime slot. DoNOT cast oldrecordto526 or demandfalseABIassert.
Extra8runtimefields/broaderlayercapacity remainopen;7slots is plausible arithmetic,
notyetconstructorproof. Bumpfactor8C7A60 uses4time reads*time2,not legacy*time3.
Afterbinds current sky tint,finalCOLORARG2=DIFFUSE;topmaterialflag40 specialhandling.

## Current exact build and native evidence

Engine6751765f42dc448ae54f8ee51cdb30a7ca07ba863cf87697cc6dd1149cd1653d,
67objects/21derived;40payload changes/19timestamp-only/8byteequal129.
Sharedheaders changed→full182client/20kernel rebuild PASS. NoCharacterMR/noFORCE.
PE52c253106d9c6f8372f57c7976f026a7f807c5233f1945e23bcc771903ba61a2,
2255872bytes/x86/base400000/entry16C930/WinMainB98B0/afterCreateB9A24/unresolved0.
ANI/BBX actualconsumerprobe now uses sameFIcameraheader asproduction. Own-entry/
imports/sound1/window/device/existingCreate1/contracts PASS. Known firstchance
handled40080201/E06D7363/406D1388 retained;fullbootstrap/gameloop notaccepted.

Final new consumers work/m9/84c65e3f/lighting-consumers-001:8materialstates,
3bumptimes,5realindexedpaths and5GPUframesviewed. Stockbd_grass01.r3e113/5328vertices
normalsallbitexact in observedCW127(PC24 nearest);position inputs fromGPUcapture,
topologyfrompinnedR3E. This DOESNOT prove inheritedpositiondecompressor/CRT.
Resolved resource capture equalsstagedinput. ActualsubmittedGrass1/LitGrass1
GetFunction dumps equaloriginal220/300-bytecode. Shader19.xyz/21/22 used.
Nativewarnings0. CPP includesworld/sky probe helpers;all provenance pinned.

Initial double geometricoracle gavewrongresidualnormal ondouble-sidedoppositefaces.
Corrected float32 order fromreferenceassembly makesall5328 normal bits match;
production wasNOT changedtoappeaseapproximation. DoNOT smooth tinyresidualtozero.
Diagnostic normal-diagnostic.jsonl retained. Earlier ee67/2fb2/e906/47de runs are
intermediate,final84c65e3f authoritative. Initialprobecompileassert526 was wrong;
correct own332-byte layout and confirmedserialized46/runtime54 mapping used.

Freshregressions:world35a588bc(76queue/16clock/6oldwarnings),materialb1d744fd
(60profiles/3frames/36cases/1missing),fade260c59ec(90+27/0warnings),
lightingbed1b5cc(867capturedcolors/3aggregates/27Mie/real loaders/29BSP/2warnings),
weather764f3808(90scripts/5aggregates/1missing). AllPASS.25freshraw+PNGframecontents
byteequal129 and priorreviewnativehashverified. New reuse_client455_visual_review.py
records explicitreuse,not newinspection.30frames visuallyaccounted=5newlyviewed+25
previouslyviewedidentical. No oldbulks rerun. Exact129backups before130 include31
files/sharedheader/engine/PE/MAP/rsp and research/*before130.md. No livejobs remain.

## Exact remaining gaps and next131

Target8BFBC0 affine inverse has0.001guards. Currentlit usesD3DX inverse forselected
affine fixture;guard/determinant/x87 parity notported.8C0980 transform and
51D5D0 normalize→41DB70 wrapper→41DB90 underlying stillneedexactanalysis.
Currentfixtureworldtranslationonly,notproofrotation/nonuniformscale/allFP.
LitGrass target3-register stackoverreads at19/21/22;shaderuses19.xyz and21/22.
Sourceunusedlanes deterministiczero;prove laterconsumers orrestoreeffects beforeM9.
Both fixed/shader flag40 use MODULATE4,others MODULATE2X5. Removed old fixed
unconditional2X override. Actual fixed post=[LIGHTING1,COLORVERTEX0,
DIFFUSESOURCE(flag40?0:1),SPECULAR1,EMISSIVE0] in selected white draw fixtures.
Intermediate e08ec5ae/25826043 runs predate final COLOROP/cleanup corrections;
84c65e3f final and current PE52c25310 are authoritative. Do not restore legacy
post-states or brighter intermediate pixels merely to retain old lab images.
LegacyGrasscaps/failure/lifecycle/reset/OOM andactualgame flag40producers OPEN.

Next131:exactlit transform/normalizer,actualflag40writers/selection,materialruntime
extra fields/capacity andshaderlifecycle. Thenlensflare8CB460/localfog/indirectdaynight
params/fullCRT/FP,INS/Planet/worldvisibility/alpha/textures/stages/auth/protocol/
Character/gameplay/fullclientacceptance. NeutralB upwardcamera/thin geometry strips
persist asunknownvisualfidelity gap;25oldframesunchangeddoesnotcloseit.

Preserve128 previousorbit/currentfar→Sunposition,thennewSun/Mie/night,tintusesOLDfog,
thennewfog. No one-frame lag cleanup. Fogflag2 endpoints else289grid;NOzero-divisor
fallback. NegativeZzero=-0;Mieexact19h boundarydiscontinuity preserved. R3X4day/8night;
absentendpointsetretains previous;FOG_COLOR current/main5/5000 NOTdaydistances.
129corrected tags:uppercase90A5ED beforeFOG/ENV,lower90ACEC beforeweather/flags.
Packedweather1157D3C BSS0 persistsInitCore/R3X;fullDWORD OR spill,no byteclamp.
Knownmissingtrade_bel.r3e notsubstituted. LabCLevel temporaryowner mustoutliveactive
map:destructor freesglobalresources. LabD3D vtable patch originalFULLtable57/82/83,
restorebeforeforward/Get;NEVERclone119entries(private driver entriesexist).
Goalactive;M6/M6F/M7/M9 OPEN. Do not pause/block/complete onpartialprogress.
