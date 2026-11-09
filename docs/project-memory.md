# Память проекта

Обновлено 2026-11-10. **137 PARTIAL M6**.
Текущая проверка: inventory/client455-scene-capture-checkpoint.json.
Команда: scripts/Invoke-Python.ps1 scripts/checkpoint_client455_scene_capture.py.
Доказательства: research/client455-scene-capture.md.
Предыдущая подробная память: research/project-memory-before137.md.
Предыдущий завершённый участок136,commit f32bc32.137 — progress.

## Цель и границы

CLIENT ONLY: поддерживаемые исходники и собственный RF_Online.bin с полным
функционалом и поведением закреплённого455. M9 определён: финальная приёмка
без модернизации графики. Устаревшую формулировку goal про неопределённыйM9/M4
не использовать. M0–M4/selectedM5 достигнуты; M6/M6F/M7/M9 OPEN,M8 не нужен.
Server только читать reference; не изменять/собирать/восстанавливать даже копии.
Originals immutable; input EXEs никогда не выполнять; работа только под work/.
LocalGit,no push/remote/publication. Subagents запрещены без прямой просьбы.

## Оценка и рабочий приоритет

По прямой просьбе пользователя дана инженерная оценка: около25%,диапазон20–35%,
остаток около75%. Это планирование по12системам,не процент функций/байтов/тестов.
Фиксированные веса100%,weighted18.95–33.55%; полных принятых областей0/12.
Script scripts/assess_client455_progress.py; inventory/client455-progress-assessment.json.
После обновления registry139исторических/пересекающихся записей;не знаменатель
готовности. Full Login→selection→world→gameplay ещё не принят.
Приоритет A: ordinaryTitle/Login; B: clientauth/selection; C: world/avatar/
control/movement; D: combat/items/chat/NPC/quests/social; E: fullM6F/M7/M9.
CRT/FP/failure gaps не отменены,но не подменяют связанный видимый сценарий.
Остаток2–4объёма закрытого поведения — не прогноз календарных дней.

## Завершённое137

Обычные InitFullScreenEffect/ReleaseFullScreenEffect владеют5targets:
screen size+Z,512²+Z,512²безZ,512²+Z,256²безZ;PerbMap load/release.
Capture-current helper портирован,но ordinary game caller ещё не подключён.
Full Fraction/particle/BBoShasi routing иdraw owners НЕ перенесены.
Primary b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
secondary46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558;
x86/base400000.12fullfunc/1855instructions/13equalranges,включая8инструкций
lower chunk8CD830. All positive CFG starts covered;<=100asm/page.
Raw artifacts/client455-progress/refraction137-reference/session.json.
IDA b4737bcb saved/closed/list0. Exact136snapshot47files:before137/manifest.json.
Engine708c892e60c3bf7457389b40ac24b9a466958c9d232d9efaf497d1ac3232b870;
PE42213f081aceb9f1630add0c9d4a77deab330f1ca43936a85fee4c97c5c7cf89,
2267648bytes/entry16F1C0/unresolved0.67engine/onlyr3d3d8.obj payload changed.
Shared headers unchanged;182client/20kernels не rebuild137.
Fresh own WinMain/Miles1/window/D3D/existingCreate1/contracts/providers PASS.
Native work/m9/21083b2f/fullscreen-effect-001:5targets/8configs/3resize cases/
2captures/18fullscreen frames/5GPUviews inspected/warnings0.
Missing PerbMap loose file confirmed;positive32x16DDS is synthetic fixture only.
Capture8CE020 retains surface reference/ignores HRESULTs;lab compensates it
separately. Не claim balanced productioncapture. Initialwrapper640x500 before
viewport640x480;realReset/lost/failures remain open.8CE2A0 is Fraction,notPlazma.
8CE0A0 unowned stack lanes remain;never invent defaults.
Material/world/Bellato135–136 результаты historical,не fresh137 regressions.

## Следующий138: обычный стартовый сценарий

research/client455-title-initial.md;raw title138-initial/session.json.
20diagnostic pcode functions плюс2small instruction contexts;не fullASM/CFG/
secondary range acceptance. IDA9bfd18c8 saved/closed/list0. Native jobs нет.
Current source factory3legacy stages/modulo;455factory4/explicit next.
Legacy Title почти пуст. TargetCreate157CE0 allocates32-byte movie owner,
читаетlocale CcrLogo.dat иAVI,используетDirectShow/CTextureRenderer376.
Title fields послеbase24:movie24,escape28,flag32,ARGB36,field40.
В primary FrameMove157F80 безусловно пишетexit1 иjump epilogue:не включать
недостижимую длинную video/fade ветку,но Create/Render этим не отменяются.
Реальные ko-kr/ru-ru CcrLogo.dat иccrinc.AVI878592bytes существуют.
Следующее действие: actual ordinary Title→Login/first Login LoadData/UI,
проверить стандартную SDK movie dependency перед реверсом всех COM baseclasses.
Не заявлять видимые455экраны или полную4stagefactory уже готовыми.

## Место и проверки

scripts/client455_asset_staging.py подключён к runtime_inputs,generic runner,
earlystartup,device/existingCreate иfullscreen. Pool work/shared-runtime-inputs
adopts SHA-verified ownedcopies;never hardlinks originals. Configs/exes private.
5boundary/fileidentity cases PASS. Latest earlystartup newpool208896bytes;
existingCreate36assets/newpool0;fullscreen11assets/newpool0. Ничего старого
не удалялось. Storage audit snapshot150.95GiBlogical/42.29GiBunique:
m9=134.19/26.20GiB,oldgraphics12.39GiB,sourceport0.42GiB.
НаWindows DirEntry.stat даёт zero inode/link fields;дляhardlinks os.stat(path).
До очистки построить reachability current/historical evidence;не удалять inputs
по одному возрасту. Остальные крупные stagers переводить по мере использования.

Python: scripts/Invoke-Python.ps1 file.py,не-c/-m. VS2026MSVCx86.
Native/GPU jobs последовательно;timeout не termination,опросить тотжеhandle.
MCP JSON<=20kchunks;ASM<=100/page плюс все positiveCFG/tails;save/close ownIDA.
rg--files перед неизвестными именами,безshellpathglobs наWindows.
Не повторять159k unchanged suites. Targeted checks после изменений;обновлять
актуальные evidence/docs. Legacy originals иserver files не изменять.
