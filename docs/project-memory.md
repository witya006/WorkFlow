# Память проекта

Обновлено 2026-11-10. **133 PARTIAL M6**.
Gate: inventory/client455-material-layout-checkpoint.json.
Проверка: scripts/Invoke-Python.ps1 scripts/checkpoint_client455_material_layout.py.
Доказательства: research/client455-material-layout.md.
Runtime132 исторический; static owner/math proofs сохранены.
Предыдущая полная память: research/project-memory-before133.md.
Предыдущий goal turn132 — progress, commit a115c03. Текущий133 — progress.

## Цель и правила

CLIENT ONLY: поддерживаемые исходники и свой RF_Online.bin с полным поведением455.
M9 УЖЕ определён:финальная приёмка без модернизации графики. Старый Goal M9/M4 устарел.
M0–M4 diagnostic/selectedM5 завершены;M6/M6F/M7/M9 OPEN,M8 не нужен.
Build/Create1/selected component не закрывают docs/client-acceptance.md.
Server только читать reference;не менять/не собирать/не восстанавливать.
Originals immutable,inputEXE never execute,workcopies,Git local/no push.
Subagents только явно. Python scripts/Invoke-Python.ps1 file.py,не-c/-m.
VS2026 MSVC x86.Native/GPU sequential;timeout не restart,опросить тот же handle.
Перед runtime edits exact engine/PE/MAP/rsp/reports/shared headers backup.
Ignored!=backup.Не повторять159k/unchangedbulks.Updates коротко RU<=60s.
rg --files перед неизвестными именами;не shell path globs.

## Доказательства133

Primary b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
secondary46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
x86/base400000.5fullasm/1438instructions/5ranges equalboth455,fullCFG/pcode.
909400 MatInit40;909500 layer reader763;90A040 material reader316;
90B1C0 binary reader150;8C9230 special shader consumer169.
Additional32-byte2048guard context90A627,pcodepartial90A4D0;not fullasm claim.
Raw/session artifacts/client455-progress/material-layout133-*.json.
Owned session24a6b8ee saved/closed/list0. No live native jobs.
MCP<=100asm/page AND unique/count/done/allpositiveCFGstarts/tails;nofirstpagealias.
LargeJSON<=20k chunks viaNode. All133 raw safely saved273760chars.

Initializer proves7layers,not merely arithmetic. Runtime _ONE_LAYER54/_R3MATERIAL526,
layer starts148+54*i. Base header fields unchanged,name4/flag132/detail136/scale140/
layercount144. New floats layer+46 specularFlickeringScale/+50 Speed.
Target text tokens retain typo specular_flikering_scale/speed;OR800001/800002.
Binary reads46 serialized bytes then advances54,extra floats zero from allocation.
MatInitzero526,each7 layer ARGBffffffff;surface0. Text LoadOneMaterial resets7surfaces
to-1 anddetail-1. Text active LoadOneLayer defaultFlickerAni00ff;unused remain0.

New scripts/client455_material_port.py generates r3material455.h overlay from
unchangedlegacyheader,_MAX_LAYER_NUM7,_MAX_MATERIALS2048 and2floatfields.
No cast332->526. Forceinclude materialheader immediatelyafterport_std before
vertex/particle/core includes in sharedcamera AND particle prefix.
Actual binary loader read46 literal insteadsizeof(runtime54). Versionfailure now
fclose beforeNULL,matching90B1C0. Source legacy had leakedFILE onwrongversion.
Text writers added forspecular/sky flags4/8/10/20(hex)/splat40,shader_object and
light_object. FullDWORD shift/add/OR11000000 preserved,not maskedbyte.
Update old lighting probe staticassert:now526/54/layer1flag216. Old208/332 is historical.

CPUfull-object material run work/m9/edb87690/material-layout-001:
actual LoadSubR3M andLoadSubMaterial,2adjacentrecords each,layer7 boundary,
zero-layer sentinel. Both1052-byte dumps exactlymatch independent expected bytes.
Binaryinput46bytes/layer,noextra fields;runtime extras0. Text7floats/flags anddefaults.
3wrongversions1.2 NULL/warnings3/process handles245->245 PASS.
Fullshader nottested bythis CPU probe;generatedinputs/dumps pinned.
All7 GPU stages,numeric conversions/reload/bad indices/truncation/OOM remainopen.

## Current build

Enginefa88420ddcc370d58758aea65431f530463f3ed855f957f3829e0dc580f2946c.
67units/21derived,42payload changes/17timestamp-only/8byteequal132.
Sharedcamera/particle changed,materialoverlaynew,vertexheader unchanged.
All182client/20kernel rebuilt PASS. Order:
engine -> prepare normal -> build normal -> probe normal consumers -> link.
Initial link refusedstale ANI/BBX proof;afterfreshprobe linkPASS,no secondfullbuild.
Final fclose source change rebuiltengineunit only;header remainedsame.
PEb9002c4c0bc962af89c72bc7f6768f2b8610c8ffcc3ceed3d3ddbcced3a61e0a.
2256384bytes/x86/base400000/entry16CC90/WinMainB98B0/afterCreateB9A24/unresolved0.
NoCharacterMR/FORCE. Ownentry/providers/sound1/window/device/existingCreate1/
contracts PASS. Handled firstchance40080201/E06D7363/406D1388 retained;
fullbootstrap/gameloop notaccepted.

Fresh actualNeutralB77entries/2loads/20availablelit/4BSPdraws PASS;
72LitGrass directions/12FPmodes,5328normalbits,8materialstates,3bumptimes PASS.
Freshworld76queue/16clock/6warnings,material60/36/1missing,fade90+27/0warnings,
lighting867/3aggregates/27Mie/29BSP/2warnings,weather90/5aggregates/1missing PASS.
All34raw+PNG framecontents byteequal reviewed132. Explicitreviewreuse,no newvisual
inspection. Helperreuse now --frames4 forentity-owner;default5 unchangedothers.
Unchanged240CPU mathproof retained;threeexactmathbodies verified innewPE.
Exact132 before133 backups include reports/engine/PE/MAP/rsp/sharedcamera/vertex/
legacy materialheader andtrackedresearchmemory/next backups.
Feature CLIENT455-MATERIAL-LAYOUT-133 current.

## Next134 and remaining

134:ordinary special-material shader owner/dispatch and8C9230 consumer. Source now
stores specular metadata,but special shader pipeline notported. Follow callers,
shader_object/light_object encoded flags,actual shaderfiles andnormalBSPdraw routing.
8C9230 uploads VS0/4/8 matrices,VS15/PS15 sharedvector,light data via8B2EB0;
binds textures for allm_dwLayerNum atstride54. PS18.xy = firstlayer scrollU/V/256;
z extraScale whenflags&800001,w extraSpeed whenflags&800002. MasksareANY bit tests,
not equality toentiremask. CallsGetBumpFactor then overwrites fourthfloatwithR3time
beforePS17 upload. Needs fullowner/loader/caps/failure/reset/OOM/laterstate consumers.
Do not add unconnected helper andclaim productioncompletion.

All7GPU layers/fullspecialmaterials andfullCRT numeric/reload/error semantics OPEN.
Othergame/effect flag40writers,fullvisibility/fade/alpha/camera/world,unusedregister
lanes,INS/Planet/lensflare/localfog/indirectparams/UI/stages/auth/protocol/Character/
gameplay andclient-acceptance matrix OPEN.NeutralB upwardcamera/thin strips remain
unknownfidelitygap,not fixed bystableframes.

132 mapproducer remains:EBP84.Flag72 bit40 -> successfulCEntity+104 beforeRestoreTex.
Failed/particle branches don'tgetOR. NeutralB77/21sourceflagged/15shader/20available,
missingtrade_bel entry76 neverreplace.93EBP/3700rows/1584lit/82shader include
alternates/duplicates,not unique assets/acceptedmaps.
Native camera fixtures mustpublish inverseview andviewproj,thenordinary FrameMove/
DrawMapRender/DrawMapEntitiesRender prepares Color. SetViewMatrix alone doesn't
publishinverseview;R3Move cameraowner does.Don'tmanually setColor/flags toforcepass.

131 exactinverse485/transform132/normalizer136 bodies retainedexcept verified
epsilon/sqrtCALL. CRTtempCW=(callerCW&300)|7f,FSQRTnearest/callerPC,restoreCWthen
floatstorecallerRC.Selectedfinite12PC/RC exact;matherr/errno/precisioncallbacks/
unmasked/NaNInf/statusOPEN. Inverseguard0.001failureignored,targetusesunspecifiedstack;
no fallback. Geometrynormalizer separate,fullGetNormal/decompressorFP stillOPEN.

Preserve128 orbit/foglag,tintOLDfog;fogflag2 endpoints else289grid,nozerodivfallback.
NegativeZ0=-0;exact19hMie discontinuity,R3X4day8night/absentendpointretention.
FOG_COLOR main5/5000notday.129uppercase90A5ED FOG/ENV,lower90ACEC weather/flags.
Packedweather1157D3C BSS0 persistsInitCore/R3X,fullDWORDspill,no byteclamp.
TemporaryCLevel mustoutliveactive map:destructor freesglobalresources.
D3D observers patch originalFULLvtable57/82/83,restoreforward/Get;neverclone119.
Goalactive,M6/M6F/M7/M9OPEN;no completion onpartial.
