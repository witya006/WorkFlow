# Память проекта

Обновлено 2026-11-09.

127 PARTIAL_COMPONENT,current research/source arithmetic;runtime126 remains current.
Audit: inventory/client455-sky-lighting-reference.json.
Command:scripts/Invoke-Python.ps1 scripts/audit_client455_sky_lighting.py.
Evidence:research/client455-sky-lighting.md. Previous memory/steps:*before127.md.
No runtime source/build changes127. Exact engine/PE hashes below unchanged.

17fullasm/1538instructions/17ranges equalboth455;allpositiveCFGstarts covered.
14newasm/777instructions;8B1F20/8B1640/900B00 reused126/761instructions.
Rawsky-lighting127-reference/session.json;IDA63ea5f70savedclosed/list0.
MCPconfiguredsmoke4970a219closed,66tools. 8B1220unrecognizedfunction→fallback
60998total;EXCLUDED fromselected,onlyexact7byteFLD/RET boundedbytes used.

Criticalframeorder:900CD0computesSunposition fromPREVIOUSorbit/scale/currentfar,
thennewSunstate/night/angles,then8B1640 tint usesPREVIOUSfog,thennewfog.
DoNOTsynchronizeawayone-frame lag. Far forposition is1157C88,notSunrender1400.
GetSunPosition8B1620 consumer8CB460lensflareOPEN. PackedBF734C/BF7350 initial
FFFFFFFF/getters8B1820/8B1830;secondno directxrefs. Avoidunprovedambientlabels.
8B30B0 enabled→CPUcolor modulation /256,alpha preserved;disabledreturnsbase.
DrawMap8E7C40 setsTEXTUREFACTOR=tint beforeBSP;material8C80A0flag8000/global
1157CB8 also consumes. INS/Planet separate. Exposure setter8B1210 called8E77B0:
DWORD stored inthis145,lowBYTE/255 passed. IdentifyactualownAPI beforewiring.

Fogflag2:currentColorD38/dayD58/nightD5C,currentStartD30/dayD48/nightD4C,
currentEndD34/dayD50/nightD54 in1157xxx. R3Xflag4 setsday/current/main/far;
flag8 setsnight;InitCorezeroesboth endpoints. Don'tenable legacyspatialFog2 code.
Withoutflag2:CPU17x17=289samples,gridcenter8,step1290,cappedradius4,height5160.
8B2670 softwareRayleigh/Mie/scattering;notGPUreadback. Normalize/dot(0,-1,0),
exp2negativeLengthBeta/log2,phase reciprocal-sqrt cubed,clamp/scatter*Sun*intensity.
AggregateunsignedRGB/divisor trunc(count*float(exposure*.899999976+.899999976)),
clampchannels255. TargetNOzero-divisor fallback;don'tsilentlyreturnblack/default.

Newclient455_sky_lighting_math.h not yetincludedengine:quartertint/directalpha,
weightedfogfloats/channels (complementkeptx87extended),/256modulation,divisor with
unsignedcountcorrection. Probeec0a5c6b/sky-lighting-math-001:129cases=36Sun45fog
24filter24divisor,PC24/53/64nearest-even,Fractionoracleexactbits/CWrestored,
3zerodivisors exposed. No actualDIV0 executed. OtherRC/FP/NaN/Inf/CRT open.
Next128:wirewholechain+realR3X/script endpoints/exposure/mapGPU-CPUconsumers/
software289point fog. Saveexact126engine/PE/MAP/rsp/reportsbeforeanyruntimeedit.
No broad/nativeworld/GPU reruns127 because runtime unchanged. M6/M9OPEN.

## Текущий ordinary runtime126

126 PARTIAL M6: actual atmosphere prepass/resources and selected Sun scalar update.
Current gate: inventory/client455-sky-atmosphere-checkpoint.json.
Команда: scripts/Invoke-Python.ps1 scripts/checkpoint_client455_sky_atmosphere.py.
Доказательства: research/client455-sky-atmosphere.md.
Полная предыдущая память/шаги: research/project-memory-before126.md и
research/next-steps-before126.md. Gate125 теперь исторический.

## Цель и ограничения

Только CLIENT RF_Online.bin,R3Engine и клиентские ресурсы. M9 УЖЕ определён:
полная приёмка клиента455 без модернизации графики;не повторять старый вопрос Goal.
M0–M4 diagnostic/выбранныйM5 завершены;M6/M6F/M7/M9 OPEN,M8 не нужен.
Build/Create1/компонентные labs не означают полной приёмки.
Серверные исходники только читать:не менять,не собирать,не восстанавливать.
InputEXE никогда не запускать;оригиналы неизменны;копии подwork/.
Локальный Git,безremote/push/publish. Subagents только по явному запросу.
Python:scripts/Invoke-Python.ps1 file.py,не-c/-m. Primary VS2026 MSVC x86.
Native/GPU jobs последовательно,дождаться terminal;timeout не повод для restart.
Перед изменением engine сохранять exactengine/PE/MAP/linkrsp/reports.
159k/широкие unchanged suites не повторять без нового риска.
Пользователю кратко по-русски,обновления не реже60s.

## Текущее доказательство126

16fullasm/2029instructions/19ranges equalbothpinned455x86/base400000.
SelectedVA:900DA0,901900,8B1840,901450,9017F0,901410,9013D0,901BC0,
8B1260,8B1280,8D88D0,900B00,8B19F0,9018B0,8B1640,8B1F20.
Raw artifacts/client455-progress/sky-atmosphere126-reference.json/session.json;
IDA d09e1f5b savedclosed/list0. Full8B1F20 pcode/asm reused125+newCFG.
Critical: cursor/total alone insufficient! Every positive CFG blockstart must occur
inasm. 9018B0 lowerchunk901760..9017EF missed byheadrequest;query901760 gives70
instructions vshead7. 8B1260/1280 tails900C90/900CB0. Audit unionsbody+CFG,
skipszeroexternalblocks. Disasm<=100/page;MCPrawsave20kchunkspertoolcall.

Source client455_sky_atmosphere.h/.inc included once in derivedlevel;ordinary
FrameMove calls UpdateSunValues afterclock/night;CSkyBox calls actual prepass.
Resources actualScatter.vso612/vsh2647/sunDDS349652 frompinned455inputs.
Sun256x256/9mips/ARGB/pool1format21;not512. Dome65x65/4225vertices/8192tris,
20bytestride/VB84500/IB49152/usage8/poolMANAGED. Sun36bytestride;
BF7878declaration40bytes vsDomeBF78A024bytes. GetFunctionshaderbyteequal612.
OrdinaryD3Drestore createsafterInitFullScreenEffect,invalidate releasesfirst.
Explicitrelease/recreate/missingshader andfinaldevicecallbackrelease checked;
NOT fulllost-reset/OOM/reentry/caps acceptance.

Flags areR3XsceneFlags offset524,notmovie. Texttokenscase-sensitive:
no_sun1/no_sky_color4/use_fog_fog2=2. LoadLevelresetafterfopen/fclose success.
PrepassVIEWtranslation0/near10/far60000/depth-zwrite-alphatest0;restoreexactglobal
anddeviceVIEW/PROJ+recomputeViewProj. Shaderbind/constants evenifflag4suppressesdome.
Flag1suppressesSun. flags5/7 preserveVS;outerbranchclearsVS/PSotherwise.
SunretainsScattershader intoitsdraw;doNOTfixit. Finalhelper preservesVS anduses
oldVB/IBcache;dome bypassescache,so doNOTclaimallbuffersunbound.
GeneralordinarySetVPIPTex1 legacy24/FVF clearVS remains renderergap.

Sun scalar x87helpers:orbit/theta/phi/scale/alpha/intensity,denominatorfloatspills.
72boundaryPC24/53/64 nearest-even cases+5liveFrameMove profiles exactbits via
independentFractionoracle. Coeffs/initialparams selected restored;nightMieBF7354=.03
filebacked/dayMieBSS0,selected transitions. Indirectconsole/filewriters OPEN.
SunColor modernCRT cos/exp/pow;fullCRT/x87transcendental/allFPparity OPEN.
Onlyc0/c4/direction/reflectance constants nativelycompared;notallirradiance/colors.

Engine744733c27378f78731ce68653ca4755e8d2dcb22a53bc6b44741292a21133e55,
67/17derived. Changedpayloads level/skybox/r3d3d8/r3vertexbuffer/client455_weather;
62byteequal/0timestamponly;sharedheaders/layoutunchanged.
OwnPE4dd76810b62a7137004f75e4cbd2490361a0d0180a1682e42cfa766de0626a5c,
2245632bytes/x86/base400000/entry16A440/WinMainB98B0/afterCreateB9A24.
182client/20kernel unchanged,ANI2/BBXfresh+normalrelink/unresolved0/noCharacterMR/
noFORCE. Freshimports/own-entry/sound1/window/device/existingCreate1/contractsPASS.
Handledfirstchance40080201/E06D7363/406D1388retained. InputEXEneverexecuted.
Exact125 engine/PE/MAP/linkrsp andbefore126reports preserved inartifacts.
Buildergenerated-source-hashes ledger recordsownwrites sofailedbuildgenerationcan
resume;unknownexternaldrift stillrefused. Sourcebaseline033unchanged.

Atmospherework/m9/4847c2b2/sky-atmosphere-001:16prepass branches;4dome/8Sun draws,
fullmeshmaxerror0/indexbyteequal/shaderbyteequal;72scalar+5live;5GPUviewed.
Disablednoonbyteequal125sky2-noon. Native1missingtrade_bel warning.
Materialwork/m9/40ad6a14/sky-material-001:60profile/3frame/36material/26draw/
10zeroalpha/unloadedPASS;5GPUviewed. Materialunitcases setflags5;normalframes
include newatmosphere. Worldwork/m9/a841e924/world-frame-001:76queue/16clock,
5GPUviewed/byteequal125/6oldwarnings. Fadework/m9/6ffedb56/sky-fade-001:
90frames+27helper/5GPUviewed/byteequal125/0warnings. Total20GPUviewed.
Original neutralBtrade_bel.r3e absent;doNOTsubstitute. Otherbulks historical.

Labobserver patchesoriginalFULLvtable slots82/83/restoresaroundforward/Get and
pageprotections. DoNOTclone119slots(privateD3Dentriesexist). Productionunpatched.
Failedfixture512/poolassumptions andearliermissingr3math/mainmacro errors corrected;
no productionworkaround. Earlier125 cloneAV trialsretained.

## Следующий участок128

Restore remaining8B1F20 lightingtail:lightcolors/exposureBF734C/BF7350,
day-nightfog/position/lensflare andactualwriters. Reviewalreadycomplete127asm before
newIDAreads;onlyreadadditionalcallees/writers whenneeded. KeepSunColorFP/CRT,
indirectMieparams/fullshaderconstants andfullreset explicitgaps.
INS/Planet/generalrenderer/worldvisibility/texture lifetime/auth/stages/protocol/
Character/gameplay/fullclientacceptance remainOPEN. DoNOTclaimM6/M9 complete.
Preservecorrections120ordinaryCURRENTview/INSpreviousview,skyvslot17;
121BSPguards/batches,122inverseaffineleaf,123projection,124fade,125materials.
