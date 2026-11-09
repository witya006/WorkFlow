# Память проекта

Обновлено 2026-11-09.

122 PARTIAL M6: восстановлен inverse-affine GetLeafNum;полные renderer/M9 OPEN.
Current gate: inventory/client455-bsp-leaf-checkpoint.json.
Команда: scripts/Invoke-Python.ps1 scripts/checkpoint_client455_bsp_leaf.py.
Подробности research/client455-bsp-leaf.md. Прежние память/следующие шаги:
research/project-memory-before122.md, research/next-steps-before122.md.

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

## Доказательства122

Pin455 x86/base400000:
primary b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
secondary 46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
13 equal bodies/13 full asm/971 instructions:11 new/742+2 cached120/229.
Raw bsp-leaf122-reference/session.json в artifacts/client455-progress/.
Owned IDA279e61eb saved/closed/list0. Нет живых процессов/сессий этого участка.
MCP disasm<=100..120;проверять len/count/sum/total/unique,не только cursor.done.
Decompiler register prototypes/Concurrency имена не являются доказательством ABI.

CBsp::GetLeafNum target8FAF00:affine transform world→local через inverse+436,
mTempSearchOk=-1,SearchNode1. 8C0980 не делит наW. SearchNode8FAE20 продолжает
после leaf0,ранний stop только leaf>0. Source использует существующий
Vector3fTransform/source455 math и собственную inverse из121.
Instance ctor8EABF0/RTTI CInstanceNode,276byte nodes,world+84/inverse+148.
Offset8EADC0:coords*30000,localbounds±15000,27nodes уINS.
INS ctor8ECFA0→B3872C/load9=8ED220/draw18=8EC850.
Planet ctor912000→B3A0BC/draw18=913800;RTTI CPlanetLevel,27nodes stride260.
Не путать этих владельцев с ordinary CLevel. Их12settercallers не дают
основания придумывать новый matrix writer вобычной карте.
INS reader8EB5E0 во всех нормальных выходах возвращает0. SuppliedMap.ins/.wld
не найдены. Но sideeffects/Error/ctor/destructor/ILevel/console/fullINS остаются
gaps:source CLand.ins отказ по-прежнему не target parity. Не удалять изM9.
Planet ctor caller8E2500 имеет load/capture команды;полныйconsole/reachability
не приняты. Все эти выводы отделены от реальной реализации GetLeafNum.

Engine67/14derived:
2fa70824eb20d19588c5043b438f12176f49e61065b31e68175da588e80bc1e4.
От121 изменён только bsp.obj,66 members byteequal,все shared overlays прежние.
Normal182client+20kernel objects/build report неизменены;новый engine relink.
Own PEb0b13a09b36ec625202244d3998c4581b702caa508c9cd38a329a0e9c5485af9,
2226176bytes/x86/base400000/entry167600,WinMainb98b0/afterCreateb9a24,
unresolved0,безCharacterMR/FORCE. Exact121 engine12534d28…/PE933c276a…
в engine-before122.lib/normal-before122.bin;reports *-before122.json.
Baseline033 есть;старый082derivedsnapshot отсутствует,этотgap остаётся.

Leaf work/m9/1e5a3366/bsp-leaf-001:
140finite cases/1680exactlocalXYZbytes,allleafIDs,7affinematrices,4topologies,
5points;leaf0 fallback,unrelatedworld/suppliedinverse,independentowner identity.
NoGPU,только ownfullobjectclient. Nonfinite/allFP/unsafe domains не приняты.
World work/m9/52d6745b/world-frame-001:
76queueops/16OSclock±1/rayhit/16archivedFX light frames;5GPU просмотрены,
все byteequal121. Base==clear;magic151256/regular146637/FX646571bytes diff.
3ValidateDevice S_OK/1pass/CULL3/ZFUNC4,6warnings сохранены.
Map work/m9/a3fb1290/map-data-001:2692/330/110maps/canonicalPASS.
Exact new PE ownentry/imports/startup sound1/contracts/window/device/Create1PASS.
Handledfirstchanceexceptions сохранены. Это не fullbootstrap/auth/game.
Oldgeometry33/ANI-BBX/quake/explosion/texture/receiver/Character/159k исторические,
не повторялись. Gate121 исторический after122. Не запускать его какcurrent.
121 lightgeometry/ownedmatrices/declaration implementation сохранена безизменения;
подробные caps/quirks в research/client455-light-geometry.md и memory-before122.

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

## Далее123

Приоритет — ordinary CLevel sky/projection8E7A10:temporary near2 sky,
DrawFadeSky,restoreperspective либоorthographic +frustum refresh.
Legacy wrapper отличается. До новогоstate проверить writers ортографических
flag/scale и существующиеAPIs;не добавлять фиктивные дефолты дляпроходатеста.
Raw122 уже содержит полный47line pcode8E7A10,частичный sky9157E0/85of114,
fullgetter915660,fade8B5900/66lines,frustum8C2A90/64lines;asm этихновыхsky
тел ещёнеполучен. Это поиск,непринятый source/runtime компонент.

Полный ReadyBspRender8FE4B0 по-прежнему не перенесён:local camera,inverse,
cache owners,world-awarefrustum/visibility/alpha/entity cache,ordinarycallers.
GetLeafNum не считать восстановлениемвсейподсистемы. INS/Planet/ILevel gaps
сохранены;не тратить следующийучасток на выдуманныйordinarymatrixwriter.

Полныеprojection/sky/alpha/shadow/device-reset/recreate/error,
trajectory/quality/blur/advancedFX/independenttextureflag8 OPEN.
MapUI/layers/selected/special/reset/sprites/avatar/portal/region/scroll;
Tutorial/Avatar/Create/QBI47/IME/input/fourstages/Login/auth/fullprotocol;
Linker/queue/Macro/Vending/inventory/equip/SF/Animus/Quest/36boards/Trunk;
Character/action/movement/status64 и вся docs/client-acceptance.md.
InvalidIDs/NaN/allFP/CRT/concurrency/RNG/OOM не выдавать за принятые.
