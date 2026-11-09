# Память проекта

Обновлено 2026-11-09.

120 PARTIAL: исправлена ошибка119 в привязке метода камеры.
Обычный CLevel подтверждён constructor→vtable→dispatch: B38494/slot27→8E7850,
он использует текущую view. 8EB7F0 относится к INS. Прежний вывод отозван.
26 полных тел/26 asm/2772 инструкции и две vtable равны между двумя455.
На настоящей Bellato проверены76 операций очереди света,16 измерений OS clock
с обоими знаками30fps,обычный/магический свет и архивный эффект. Base и clear
кадры побайтно равны;световые кадры отличаются.10 GPU кадров просмотрены.
Corrected quake142 events/2921 exact scalars;actual impact545 frames/onset79/
151active. Карты2692/330,ANI/BBX и startup/contracts/window/device/Create1 PASS.
Engine67 7c828f77…: изменён только level.obj,66 members byteequal.
Own PE0806b113…/entry167320/182client-20kernel-70facade/unresolved0.
Известные отличия световой геометрии ещё не перенесены;полный renderer и
M6/M6F/M7/M9 OPEN. Следующая121 — эти geometry guards/batches и CBsp world matrix.

## Цель и правила

Только клиент RF_Online.bin, R3Engine и нужные клиентские ресурсы/инструменты.
M9 уже определён пользователем: финальная приёмка полного клиента455 без
модернизации графики. Старое уточнение в тексте Goal не задавать повторно.
M0–M4 diagnostic и выбранный M5 завершены; M6/M6F/M7/M9 открыты, M8 не нужен.
Сборка, Create1 и отдельные labs не означают полную приёмку.

Серверные исходники можно только читать как справочник. Не менять, не собирать,
не восстанавливать серверы/БД. Оригиналы неизменны. Входные EXE не запускать;
работать с копиями под work/. Без remote/push/publish. Subagents только по
явному запросу. Python: scripts/Invoke-Python.ps1 file.py, без -c/-m.
Первый build — R3Engine Win32 RTMovie Release; primary VS2026 x86, VC6 fallback.
Не повторять159k/широкие suites без причины. Ignoring не backup:
сохранять mutable engine/PE до rebuild. Native/GPU jobs запускать последовательно.

## Актуальные доказательства

Gate inventory/client455-world-frame-checkpoint.json, команда:
scripts/Invoke-Python.ps1 scripts/checkpoint_client455_world_frame.py.
Подробности research/client455-world-frame.md. Предыдущая память сохранена:
research/project-memory-before120.md и research/next-steps-before120.md.

Pin455 x86/base400000:
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
secondary46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
Raw world-frame120-reference/session/extra-session.json в artifacts/client455-progress/.
IDA94e4ad3e и b2c3029d saved/closed/list0. GetBBox8B4700..8B4751 определён
в рабочей IDB после проверки байтов. Все26 asm получены страницами<=120,
проверены len(lines)==count,sum==total,unique;MCP может молча усекать большие ответы.
Не верить одному cursor.done и не называть метод по соседству:нужны owner,
constructor,vtable/slot,полный body. Hex-Rays register prototypes/Concurrency
имена в этих функциях могут быть неверными;не переносить как доказанный ABI.
Открывать только копии IDB, session передавать каждому вызову, закрывать owned.

Ошибка119: предыдущая view принадлежит INS8EB7F0(B3872C), не обычному CLevel.
CLand7C8600→new584→8E9F40→vtableB38494:load9=8EA220,frame14=8E7910,
draw18=8E7C40,view27=8E7850(current-view). Исправлены source и oracle.
Старое утверждение119 отозвано в research119 и feature registry.
Остальные quake/sway алгоритмы сохранены. Start/stop sway удерживает старые
цели;period0→.02. Успешный map load выключает sway. Actual gameplay writer7E2AD0
пока не подключён. Нулевое направление,modulo0,allFP/CRT/RNG interleaving открыты.

Engine67/13derived:
7c828f7767bfa5a36ce0d8df2f2f133fc91a235284115c49c75e496a289252e9.
От119 изменён только level.obj,66 members побайтно равны. Точные119engine
9ae6ace8…/PE406b400e… сохранены в engine-before120.lib иnormal-before120.bin.
Baseline033 сохранён;старый082derivedsnapshot отсутствует,этот gap открыт.
Own PE0806b113f1da0025c32dae2b327fefd920a2183fad01437e77b900818f75c9dd,
2225664bytes,x86/base400000/entry167320,WinMainb98b0/afterCreateb9a24;
182client/20kernel/70facade/unresolved0,безCharacterMR иFORCE.

World work/m9/6e19ea9b/world-frame-001:76queue operations совпали с target
oracle;16 OS clock samples дают±1 и правильный quake.5 GPU кадров просмотрены:
base==clear;отclear отличаются151256bytes magic,146637 regular,646571FX.
16/16 archived aiming frames наполняют очередь после реального CLevel clear.
ValidateDevice S_OK/onepass/CULL3/ZFUNC4. Реальная texture512 DXT1 alpha255,
36leaf/811face refs/735upward. Изображение текстуры сохранено из устройства.
Fixture camera смотрит на подтверждённый Bellato spawn2466,277,-1129.
Обязательно согласовать view/inverse/viewproj:пропущенный inverse ранее делал
свет невидимым. Это был дефект fixture,не повод менять production свет.
До нового кадра нужен FrameMove:FX меняют WORLD. Default System/dlight.dds
в комплекте нет;target conditional NULL путь сохранён. Используется настоящий
texture аргумент из архивного эффекта,не подмена.6 штатных texture warnings.

Corrected CPU work/m9/11d9e9d7/quake-001:142events/2921exactscalars.
Explosion work/m9/21d0f1cc/quake-effects-001:545frames,onset79,151active,
26160exactscalars,CLevel→D3D;ещё5 GPU просмотрены,20warnings сохранены.
Fresh map work/m9/35ffaa62/map-data-001:2692/330/canonical PASS.
ANI/BBX consumers иexactownstartup/contracts/window/device/existingCreate1 PASS.
Full bootstrap/auth/game не принят;first-chance exceptions были обработаны.
Старые texture649/receiver101/aim30/marker702/message83/Character/159k и broad
suites исторические,не повторены. Их gate не запускать как текущий.

## Далее121 — сначала реальные отличия, затем другие подсистемы

Regular light8FE980:skipAttr0x10,leaf cap128,face cap5000.
Magic8FEC90:skipAttr0x30 иNormalY>0,BBoxwidth<=1000,оба конца внутриroot bounds,
saturation faceindex2999,triangle batch2000. Target использует CBsp worldmatrix
this+372 и explicit D3D9 declaration. Legacy backend ещё отличается.
Исследовать writers этой матрицы, затем переносить source и проверить границы
на реальных/малых fixtures. Видимый пример света не закрывает эти guards/batches.

Полные ILevel/Empty/INS,frame/projection/sky/alpha/shadow/device reset,
trajectory/quality/blur/advancedFX/independenttextureflag8 ещё открыты.
Map UI/layer managers:selected/special/reset/sprites/avatar/portal/region/scroll.
Tutorial/Avatar/Create/QBI47/IME/input/four stages/Login/auth/fullprotocol;
Linker/queue/Macro/Vending/inventory/equip/SF/Animus/Quest/36boards/Trunk;
Character/action/movement/status64. Полная матрица docs/client-acceptance.md.

Сохранять особенности:Nuclearrecord32,unknownDWORD12untouched,unsignedWORDkeys,
Resetdetach launch/impact,один process clock;type33byte1use/group60all9/AES.
Map110+ND110 compatible только suppliedzh-tw,8ND31/100 отклоняются;не подменять.
WarningCP949suffix3c2db0e6b0ed,nocallbackreturn;shared R3T counter не переписывать.
GoMMO audit только initialize/toolslist/studio_status,безInstall/publish.
