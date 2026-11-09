# Память проекта

Обновлено 2026-11-09.

121 PARTIAL M6: выбранные отличия световой геометрии перенесены.
Current gate: inventory/client455-light-geometry-checkpoint.json.
Команда: scripts/Invoke-Python.ps1 scripts/checkpoint_client455_light_geometry.py.
Подробности research/client455-light-geometry.md. Прежние память/следующие шаги:
research/project-memory-before121.md, research/next-steps-before121.md.

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

## Доказательства121

Pin455 x86/base400000:
primary b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
secondary 46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
12equalbodies/12fullasm/1725instructions:7new/712+5cached120/1013.
Raw light-geometry121-reference/session.json в artifacts/client455-progress/.
Owned IDAbec9ad05 saved/closed/list0. Новых открытых сессий/процессов нет.
Каждый MCPanalysis сsession;disasm<=120 иlen/sum/total/unique проверять.
Нельзя верить cursor.done безчисел;он может молча усечь ответ.
Имена decompiler/Concurrency и register prototypes не являются доказательством ABI.

Regular8FE980:skipAttr0x10,leafcap128,valid signed→uint leaf check,facecap5000;
VNum0..2 тоже учитывается,fan triangles,color0/stride16,batch3000.
Magic8FEC90:skipAttr0x30,NormalY>0,Xwidth<=1000 (неY/Z),обаBBoxконца внутриroot1,
zeroBBoxreturn,leaf256,seen saturation2999 с перезаписью последнегоID,batch>=2000
послеwholetriangle→реально2001. Sharedscratch5000,неreentrant.
CBsp target world+372/inverse+436:8FDCA0 копирует64+64байта,неинвертирует.
8F66B0 identity обеих.12xrefcaller candidates;полные2caller8EAF60/8EB040.
SourceCBsp расширенсвоими128байтами,неtargetoffsetoverlay/privateABIclone.
Setterпроверенlab;обычные игровыеtransformowners ещёнеподключены.
Explicit COMdeclaration XYZ FLOAT3@0/colorD3DCOLOR@12/END созданаordinarydevice
иreleaseordinaryteardown;полныйreset/OOM/targetErrorflow не принят.

Engine67/14derived:
12534d28dfeccda98c5e2cdffecc6621ffde7b3a95810501f2a513f01911e810.
OwnPE933c276a79a6dce22677bb9b09aefef07f5b8e062b6f146aff770d878fe85df3,
2226176bytes/x86/base400000/entry167630,WinMainb98b0/afterCreateb9a24;
182client/20kernel/unresolved0,безCharacterMR/FORCE.
Sharedheader требует полнойnormalrebuild! Только consumers probe НЕ пересобирает182TU.
Все67engine+182client+20kernel пересобраны.8archivebyteequal,24timestamp-only,
35otherpayload;19runtime-section/rawrelocation differences. Не говорить«только3
codeobjectschanged» безсимволическойнормализации. Lists inreferenceaudit.
Exact120engine7c828f77…/PE0806b113… сохранены engine-before121.lib/normal-before121.bin.
Baseline033 есть;старый082derivedsnapshot отсутствует — gapсохранён.

Geometry work/m9/cf87be57/light-geometry-001:
33cases/1580880actualvertexbytes exact target-derivedPythonoracle,
allbatches/filters/caps/dups/polygons/root/width/tallY/matrix/declarationPASS.
Capture documented44/83/87slots только OWNlabD3Ddevice,restorevtable.
Неinput455execution. ActualdeclarationGetDeclaration+create/releasePASS.
World work/m9/6047792e/world-frame-001:
76queueops/16OSclock±1/realBellato+archivedFX;5GPUviewed иbyteequal120.
Base==clear;diffclear magic151256/regular146637/FX646571bytes.
ValidateDevice S_OK/1pass/CULL3/ZFUNC4,6warningsсохранены.
Map work/m9/06e31dc3/map-data-001:2692/330/110maps/canonicalPASS.
Fresh normalANI2+BBX,imports/ownentry/startup sound1/contracts/window/device/
existingCreate1PASS. Handledfirst-chanceexceptionsсохранены.
Old CPUquake142/explosion545/texture649/receiver101/aim30/marker702/message83/
Character/159k исторические,неповторены. Current gate120 исторический after121.

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

## Далее122

Начать реальные владельцыworld/inverse иILevel/Empty/INS:ctor/vtable/callers,
обычныйpathианалогичныйsourceowner прежде изменения. Selectedsetterготов,
но fullplacedrender/коллизии/обратнаяматрица ещёнепортированы.
Полныеframe/projection/sky/alpha/shadow/device-reset/recreate/error,
trajectory/quality/blur/advancedFX/independenttextureflag8 OPEN.
MapUI/layerselected/special/reset/sprites/avatar/portal/region/scroll;
Tutorial/Avatar/Create/QBI47/IME/input/fourstages/Login/auth/fullprotocol;
Linker/queue/Macro/Vending/inventory/equip/SF/Animus/Quest/36boards/Trunk;
Character/action/movement/status64 ився docs/client-acceptance.md.
InvalidIDs/NaN/allFP/CRT/concurrency/RNG/OOM невыдаватьзапринятые.
