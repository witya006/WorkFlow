# Память проекта

Обновлено 2026-11-10.

128 PARTIAL M6: ordinary lighting frame + both fog branches + real endpoint
loaders + map TEXTUREFACTOR bind. Gate inventory/client455-sky-lighting-checkpoint.json.
Command:scripts/Invoke-Python.ps1 scripts/checkpoint_client455_sky_lighting.py.
Evidence:research/client455-sky-lighting-runtime.md. Runtime126/компонент127
теперь исторические;полная память/шаги до128:research/*before128.md.

## Цель и ограничения

Только CLIENT RF_Online.bin/R3Engine/client tools. M9 УЖЕ определён:полная
приёмка клиента455 без модернизации графики. Не повторять старый вопрос Goal.
M0–M4 diagnostic/selectedM5 завершены;M6/M6F/M7/M9 OPEN,M8 не нужен.
Build/Create1/component labs не означают полной приёмки.
Server только читать как reference;не менять/не собирать/не восстанавливать.
InputEXE never execute;originals immutable;copies underwork/. Git local only,
безremote/push/publish. Subagents только по явному запросу.
Python:scripts/Invoke-Python.ps1 file.py,не-c/-m. PrimaryVS2026 MSVC x86.
Native/GPU jobs sequential/дождатьсяterminal;timeout не поводrestart.
Перед runtime edit сохранить exactengine/PE/MAP/linkrsp/reports;ignored!=backup.
Не повторять159k/unchanged broad suites без нового риска. Пользователю краткоRU,
обновление<=60s. MCPasm<=100/page +actual lengths/count/unique +everypositive
CFGblockstart coverage (нижнийchunk901760у9018B0 пропускался приheadquery).
MCPrawsave20kchunkspercall,неодинoversizedJS. OwnedIDAsavedclosed.

## Доказательства128

17fullasm/1538instructions/17ranges +3wholecontextbyte bodies equalboth455.
Primaryb1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
secondary46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558;
x86/base400000. Reused127raw sky-lighting127-reference/session.json,
IDA63ea5f70savedclosed/list0;no newIDA128. Context8C3400sizeAC8/90A4D0size9F6/
90AED0size28B wholebytescompared,NOT fullasmclaim. 8B1220notIDAfunction;
exclude60998fallback disasm count;onlyexact7byteFLD/RET boundedgetter.

New client455_sky_lighting.h/.inc appendedafteratmosphereinc inordinarylevel.cpp.
FrameMove:AdvanceDayClock→UpdateSkyLighting. Innerorder:
previousorbit/scale+CURRENTfar→Sunposition;newSun/Mie/night;packedTint usesOLDfog;
thennewfog. Preserveone-frame lag. PositionfarNOT1400 Sunrenderdistance.
R3Xflag4 day endpoints,flag8 night;absencepreservesprevious. InitCorezeroesthem.
FOG_COLOR-only fillsCURRENT/main5/5000 butNOTdaydistances. Main scriptdispatch
case-sensitive:legacystruprremoved;foghandlerat originalfogblock;lateweather/env
callbackremainslate. Don't addduplicateearlyweathercallback.

Fogflag2weightedendpoints usesextendedx87complement;elseCPU289samples17x17,
center8/step1290/cappedradius4/height5160. Actual4B2670 Rayleigh/Mie arithmetic,
x87floatspills/positiveFSQRT;modernCRTpow/log/SunColor paritystillOPEN.
SampleroracleusesACTUALSunColor input,so867exactpackedresults DONOTproveCRT
SunColor equivalence. SoftwaretestsPC24 only;Mie27boundarycasesPC24/53/64.
Unusedreferenceprojection/extinctionFPsideeffects omitted→explicitgap.
Unsignedaggregate/divisor exposure*.899999976+.899999976/clamp255;
NOzero-divisor successfallback. NegativeZ0 mustremain-0 inoracle/geometry.
Mieexact19hfloatboundary.7916666865348816 gives0 betweenneighbor nonzero values;
doNOTsmooth. InitialdayMie0/night.03;indirectwritersopen.

TintBF734C/directBF7350 initialFFFFFFFF. DrawMapRendersetsTEXTUREFACTOR=tint
beforeBSP. Actualmaterial8000/1157CB8 stages andCPUtint consumers not restored.
RF455_ApplySkyTint andSetSkyFogExposureColor retained inMAP, butsymbolretention
DOESNOTproveactualgamecallers. ExposurehelperlowBYTE/255 usedbyrealframe/lab;
targetCLevelDWORDowner atthis145/8E77B0/gameproducers stillOPEN.
GetSunPosition8B1620 consumer8CB460lensflare andlocalfog-volumeacceptance OPEN.

Enginedf47c24a32abef705eb38b34299f0508093357f38af0add0e8b68987824b7c06,
67/18derived;onlylevel/core/r3materialpayloadchanged,63byteequal/0timestamp-only.
Sharedheaders/layoutunchanged;182client20kernel preserved,ANI2/BBXfresh+relink.
PE052f73878f4082c6cab3ad532b08ecb3ec8f250dbd0622a3db83efa5157933ce,
2251264bytes/x86/base400000/entry16B900/WinMainB98B0/afterCreateB9A24/
unresolved0/noCharacterMR/noFORCE. Own-entry/imports/sound1/window/device/
existingCreate1/contractsPASS;handled40080201/E06D7363/406D1388retained.
Exact126engine/PE/MAP/rsp+21reports backedup *before128* beforeedits.

Currentnative work/m9/a92d3696/sky-lighting-001:4actualLoadMainMaterial cases,
5validR3X+1invalidversion;27Mie3precision;5ordinary+3nontrivialfogframes;
867actualCPU samples/3aggregates exact selectedPC24;disabledpreserves;
previousFogTint,previousOrbitPosition;29actualBSPsubmissions/firstTFbind=tint.
Nativewarnings2=1deliberatebadR3X+1originalmissingtrade_bel. Earlierc637cfe4
capturepassed beforeextra3fogframes;finala92d3696 authoritative. Oracle-0Z fix
used --verify-existing;no production workaround. Nativeprototype/far/scope
compile errors corrected. No livejobs remain afterlastpoll.

ActualneutralBcamera pinned109548bytes/SHA4d71c20bdab6507a03904bc77c3d9cac16d062e666c923f71d7370b3030f6044.
R3Xfixtureswere loadedBEFORErealneutralB;absentnight setpreservesfixturevalues.
Don'tmislabel114/6004 asdatafromneutralB. ActualR3Xdaydata independentlychecked.
5lightingGPUviewed. Worldc8b19052/sky-fade120a008a/material5e4340d4:
15GPUviewed/byteequal126. World76queue16clock/6oldwarnings;fade90+27/0warnings;
material60profiles3frames36cases/1missingwarning. Total20GPUviewed.
Old12616prepass/resourcecases historical,not rerun becauseprepass/resources
unchanged. Otherbulksnotrerun. Originaltrade_bel.r3e absent;don'tsubstitute.
Labobservers originalFULLD3Dvtable slots57/82/restoredaroundforward/Get and
pageprotections. NEVERclone119slots(privateD3Dentriesexist). Productionunpatched.

## Следующий участок129

Traceactual8E77B0 CLevel exposureDWORDowner/gamecallers and8B30B0CPUtintcallers;
material8C80A0flag8000/global1157CB8 stages. Packed *weather/*haze/
*special_weather tags90AD04/90AD6A/90ADD3→1157D3C are also nothandled bycurrent
weather callback;traceactualproducer route,not assumed direct exposure writes.
Bindrealowners,not just helper symbols.
Ifclass/sharedlayout changes→full182client/20kernel rebuild asrequired.
Thenlensflare8CB460/localfogvolumes/indirectparams/fullshader/CRT/FP/statusflags.
INS/Planet/fullworld/visibility/alpha/texture/device lost-reset-OOM/stages/auth/
protocol/Character/gameplay/client-acceptance allremainOPEN. Don'tmarkM6/M9done.
Preserve120 ordinaryCURRENTview/INSpreviousview;121BSP/122inverse/123projection/
124fade/125materials/126prepass. Budgetunbounded,goalactive;no pause/block/completion.
