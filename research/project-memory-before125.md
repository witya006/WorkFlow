# Память проекта

Обновлено 2026-11-09.

124 PARTIAL M6: восстановлены sky fade state/x87/color/alpha в ordinaryr3util.
Current gate: inventory/client455-sky-fade-checkpoint.json.
Команда: scripts/Invoke-Python.ps1 scripts/checkpoint_client455_sky_fade.py.
Доказательства: research/client455-sky-fade.md.
Предыдущая память и шаги: research/project-memory-before124.md и next-steps-before124.md.

## Цель и ограничения

Только клиент RF_Online.bin, R3Engine и нужные клиентские ресурсы/инструменты.
M9 УЖЕ определён: финальная приёмка полного клиента455 без модернизации графики.
Не повторять устаревший вопрос из текста Goal. M0–M4 diagnostic и выбранныйM5
завершены;M6/M6F/M7/M9 OPEN,M8 не нужен. Build/Create1/lab не означают приёмку.

Серверные файлы только читать как reference:не менять,не собирать,не восстанавливать.
Оригиналы неизменны;работать подwork/. Входные EXE никогда не запускать.
Локальный Git,безremote/push/publish. Subagents только по явному запросу.
Python только scripts/Invoke-Python.ps1 file.py,без-c/-m.
Primary VS2026 x86;VC6 fallback. Native/GPU jobs последовательно,дождаться terminal.
Перед rebuild сохранять exact engine/PE/reports. Ignored файл не backup.
Не повторять159k/старые broad suites без причины. Пользователю — коротко по-русски.

## Текущие доказательства124

4 полные функции/282instructions equalbothpins: SetFadeSky8B58A0,
DrawFadeSKy8B5900,GetColorToColorAlpha8B5780,SetFadeFactor8B49B0.
Read-only literals/calls/ranges checked;rawsky-fade124-reference/session.json.
OwnedIDA7f86f1ac savedclosed/list0. ВходныеEXE не запускались.

Engine9e1b9c677ee4d9fe62f01e3186a3a481489950d3afccd02e1c83561febf7fb9f;
67/15derived,толькоr3util.obj payloadchanged,66byteequal.
Headers/182client/20kernel неизменны,normalrelink послеfreshANI2/BBX smoke.
PE38ba1441b77774edd02da237c83e99dac5a62181c1c99e756f156c498e8f0047,
2227200bytes,x86/base400000/entry167A00;WinMainB98B0/afterCreateB9A24,unresolved0.
Previous123exact engine/PE/reports *before124* сохранены.

work/m9/d42443cf/sky-fade-001:90actualstateframes(60active/30idle)+27sharedhelper
cases;PC24/53/64 nearest/even,integertruncationCWrestore,exactstate/fog/quad.
Independent rational oracle rounds targetoperations/spills. 8oldSSEfog differences;
alpha27cases noold/newdifference,не выдумывать её. 5realBellatoskyGPUviewed:
base/middle/covered/return/done;coveredRGB96/64/32,donebyteequalbase,warnings0.
InitialCW127(PC24). Earlyframealpha0 stilldraws/fog;nextcallidle returnsTRUE.
Lab prototype missing corrected;alpha-difference assumption removed afterevidence;
verifier-only fixes reusedsuccessfulnative (--verify-existing),productionnotweakened.

work/m9/dbc48543/world-frame-001:76queue/16clock±1/rayhit/16FXlightframes/
3ValidateDeviceS_OK,5GPUviewedandbyteequal123,6existingwarnings.
ExactPEstartup sound1/window/device/existingCreate1/contractsPASS;handledfirstchance
40080201/E06D7363/406D1388 recorded. Maps2692/projection12/sky123/bulk historical,
not rerun because onlyr3util changed.10GPUviewedtotal124;no livejobs/IDAsessions.

Next125:materialflags4/8/10h/20h requireactualdayprofile/enable/owners.
Exploratorypcode8B1240 returns1154DF4;nightweight+20=1154E08 from8B1F20.
ExistingRF455_AdvanceDayClock restores ONLY256byteprefix,notlightingtail.
BF7344/getter8B12B0 gates8B1840 specialprepass/sun/lensflare/scattering.
Theseexploratorynewfunctions notfullasmpinproofyet. Verifywriters/ordering,
restore actualstate andconsumers;donotfakefractionprovider/no-op prepass.
Fullsky/unloadedcleanup/texturedfadeGPU/allRC/NaN/lostreset andclientgapsOPEN.
Currentgoalturnclassifiedprogress;prioratlasexplanationconversationonly.

## Исторические доказательства123 (gate заменён124)

Pin455 x86/base400000:
primary b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
secondary46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
6 full bodies/6fullasm/1435instructions +actualvtable/ctor equalbothpins.
Read-onlyfloat/doubleliterals сверены,AAA450=5. Rawsky-projection123-reference/
session.json вartifacts/client455-progress/. IDA5b615f3e saved/closed/list0.
Нет живых процессов/IDA сессий этого участка. MCPdisasm<=100..120,проверить
len/count/sum/total/unique. Cursor.done иdecompiler register ABI не доказательства.

Ordinary CLevel8E9F40→vtableB38494 sky slot17→8E7A10. Slot15 был догадкой,
отвергнут до принятия audit;не повторять. Wrapper:persp(FOV,aspect,near2,far),
SetPROJ;loadedgetter915660→DrawSkybox9157E0;DrawFadeSky8B5900;restorepersp
сconfiguredNear,либоflag!=0 identity→OrthoLH(width/scale,height/scale,-5000,5000)
→frustum8C2A90;последнийSetPROJвобоихрежимах. Perspectiveнеrefreshfrustum.
InitCore8C3400 подтверждёнflag0/scale5.15+15xref,ограниченный regexpstores scan
8B0000..940000 нашёлinit;не исчерпывающаяклассификация/alias/UIwritersproof.
Source-owned core header+8bytes aftermMatProj:BOOLmOrthographic/floatScale,
realInitCore0/5. Skyheader добавил реальный IsLoaded455 безlayoutchange.
Это собственныйstate,неtargetprivateABIoverlay. Другие Character/ray/alpha/
UIorthographicconsumers остаются открытыми.

Engine67/15derived:
e826ee1aaf9bb6b6f1f10a3470c411357f85eacf846b2436e9fa1aac1fe279cd.
Sharedheader изменился:все67engine+182client+20kernel/facade пересобраны.
42COFFpayloadchanged,17timestamp-only,8byteequal;не утверждать42semanticchanges.
OwnPE182ecac65696d4ffdf3d8b7c7029aeb8befb54cf9c056912419e618449a3e26f,
2227200bytes/x86/base400000/entry1679A0,WinMainB98B0/afterCreateB9A24,
182client/20kernel/unresolved0,безCharacterMR/FORCE.
Exact122engine2fa70824…/PEb0b13a09… вengine-before123.lib/normal-before123.bin,
reports*-before123.json. Baseline033 есть;082derivedsnapshotстарыйотсутствует/gap.

Projectionwork/m9/bae558a3/sky-projection-001:
12cases/24actualD3DPROJbinds/unloadedsky,defaults0/5,persp+ortho/frustum,
finaldevice/source matrix exact;closedformmatrix abs2e-6+rel2e-6,
plane abs.002+rel2e-6. Свойlabobserverвозвращает originalvptrна времяреального
SetTransform/GetTransform. ИначеонвызывалAV;productionworkaroundне добавлен.
Не использоватькопию119slots приforwardреальнымD3Dметодамбезoriginalvptr.

Skywork/m9/001219e8/sky-world-001:
actualBellatoIsLoaded=true/307200pixels,5GPUviewed:base/translatedX+1000/
worldNear3000/ortho byteequal,реальныйReleaseSkyBox→uniformclear.
Loaded-vs-clear921600bytes diff,warnings0. ClearBGRA[48,32,16,0].
Unused4thbyte0неFF:ошибочныйoracle исправлен,повторёнтолькоverifier
(--verify-existing),native ужеPASS. Не придумывать alpha дляXbackbuffer.

Worldwork/m9/9ca60b60/world-frame-001:
76queueops/16OSclock±1/rayhit/16FXlightframes,5GPUviewedиbyteequal122.
Base==clear,magic151256/regular146637/FX646571bytesdiff.
3ValidateDeviceS_OK/1pass/CULL3/ZFUNC4,6warningsсохранены.
Mapwork/m9/6a0283fa/map-data-001:2692/330/110maps/canonicalPASS.
FreshnormalANI2/BBX+exactownentry/imports/startupsound1/contracts/window/device/
existingCreate1PASS. Обработанныеfirstchance40080201/E06D7363/406D1388сохранены.
Итого10GPUviewed123. Ground/lightкадрысами поне доказываютвидимоеsky.
OldBSPleaf140/lightgeometry33/quake/explosion/texture/receiver/Character/159k
исторические,неповторены. Gate122historicalafter123. Fullbootstrap/auth/gameOPEN.

Предыдущие компоненты сохранены:121regular/magiclightcaps/batches/ownedmatrices/
explicitdeclaration;122GetLeafNumworld→inverse→SearchNode1,leaf0неearlystop,
affineбезWdivide. Instance/Planetowners отдельные:INSB3872C/ctor8ECFA0,
CInstanceNodenodes276;PlanetB3A0BC/ctor912000/nodes260. INSreader8EB5E0
нормальновсегда0,ноsourceCLand.ins отказ/ILevel/console/sideeffects остаютсяgaps.
Подробности research/client455-bsp-leaf.md иmemory-before123.

## Важные прежние решения

Ошибка119 отозвана120: ordinaryCLevel ctor8E9F40→vtableB38494/slot27→8E7850
CURRENTinputview;INS ctor8ECFA0→B3872C/slot27→8EB7F0 PREVIOUSglobalview.
CLand7C8600 alloc584/call7C8703;ordinaryload9/frame14/draw18 confirmed.
Не возвращать ошибочнуюINSpreviousview вCLevel. Default System/dlight.dds отсутствует;
targetNULLconditional сохранён,worldfixture использует настоящуюtextureизFX.
Контрольнаяcamera Bellatospawn2466,277,-1129:согласоватьview/inverse/viewproj.
До каждогоframe FrameMove/resetWORLD:FXменяютWORLD. Пропускinverse раньшебыл
дефектомfixture,непричинойменятьproductionlight.

Nuclearrecord32,unknownDWORD12untouched,unsignedWORDkeys,Resetdetachlaunch/impact,
одинprocessclock;type33byte1use/group60all9/AES. Statusguard internal640&3.
Map110+ND110 совместимы suppliedzh-tw;8ND31/100reject,неподменятьлокали.
Warning CP949suffix3c2db0e6b0ed,nocallbackreturn;R3Tsharedcounterнепереписывать.
GoMMOaudit толькоinitialize/toolslist/studio_status,безInstall/publish.
Headers normal/include через<...>,неподключать второйскопированный#pragmaonceпуть.
Search сначалаrg --files;неугадыватьимена/пути и не передавать literal*.py вrgWindows.

## Далее124

Полный actual sky material/render-state flow9157E0 и связанныйfade8B5900.
Raw123содержитполныеpcode/asm1435selected,включаяsky/fade/frustum.
СравнитьlegacyCSkyBox/CEntity:flags/animatedmaterials/alpha/fog/viewrestore,
перенести реальные различия ипроверить видимыеactualskyassets.
Wrapper123 не считать полнойприёмкойCSkyBox/entity/fade/orthopipeline.

Затем fullReadyBspRender8FE4B0:local-camera/inverse/cacheowners/world-frustum/
visibility/alpha/entitycache;projection/sky/shadow/device lost/reset/recreate/error.
Не переносить affineпоправку повсюду бездоказательствапространствааргумента.
INS/Planet/ILevel gaps сохранены. Не изобретатьordinarymatrixwriter.

Полныеtrajectory/quality/blur/advancedFX/independenttextureflag8,
MapUI/layers/selected/special/reset/sprites/avatar/portal/region/scroll,
Tutorial/Avatar/Create/QBI47/IME/input/fourstages/Login/auth/fullprotocol,
Linker/queue/Macro/Vending/inventory/equip/SF/Animus/Quest/36boards/Trunk,
Character/action/movement/status64 иdocs/client-acceptance.md OPEN.
AllFP/NaN/scale0/unsafeIDs/CRT/concurrency/RNG/OOM/privateABIневыдаватьзапринятое.
