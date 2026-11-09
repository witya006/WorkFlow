# Память проекта

Обновлено 2026-11-10. **138 PARTIAL; M6 открыт.**
Текущий gate: inventory/client455-login-checkpoint.json.
Команда: scripts/Invoke-Python.ps1 scripts/checkpoint_client455_login.py.
Доказательства: research/client455-login.md. Предыдущий gate137 historical; snapshot
artifacts/client455-progress/before138/inventory/client455-scene-capture-checkpoint.json.
Предыдущая подробная память: research/project-memory-before137.md.
137 зафиксирован commit f33d025; промежуточный138/оценка — commit8c22e34.

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
После обновления registry140исторических/пересекающихся записей;не знаменатель
готовности. Full Login→selection→world→gameplay ещё не принят.
Приоритет A: ordinaryTitle/Login; B: clientauth/selection; C: world/avatar/
control/movement; D: combat/items/chat/NPC/quests/social; E: fullM6F/M7/M9.
CRT/FP/failure gaps не отменены,но не подменяют связанный видимый сценарий.
Остаток2–4объёма закрытого поведения — не прогноз календарных дней.

## Завершённый частичный138 и следующий139

Root CGUIScreen::Add перенесён: null/no-op, AlwaysTop→AddFront455 иначе Add,
SetParent(this), затем Show(FALSE), в том числе при duplicate registration.
Подтверждение:5fullfunc/221instructions/21positive CFGblocks, все тела равны2pins.
Raw registration-full.json и audit_client455_login_registration.py; ref report
inventory/client455-login-registration-reference.json. GenericContainer.Add не менялся.
Own PE ba23dd6de02e9b050f3651fd522e69f7ed8e2ab3acd977f4aa801bcfe2c7793b,
entry16F640,size2269184;engine137unchanged.182/20 build/link0/unresolved0.
Свежий normal-consumer ANI/BBX/ownWinMain/Miles/providers иordinary Login PASS.
Latest run work/m9/ba23dd6d/login-frame002:frame70/3203ms/640x500,created1/loaded1,
Renderreturnaftercapture иownexit observed,no fatal. PNG0bf6ec51… просмотрен:
real lobby/waitingdialog;перекрывающиеся unopened panels отсутствуют.
Target all10windows/input/auth/factory4/Title ещё OPEN. Готовность остаётся25%.
43shared assets/44.2MBlinked/newpool0;без клонирования всего клиента.
Diagnostic first_* report fields — aliases;правильное имяlogin_render_returned_after_capture.
13file/4.66MB before-root snapshot и47file exact137 snapshot сохранены.
IDA5a0405db/5818692d saved/closed,list0;nativejobs нет.

139: client response→bootstrap→selection. Diagnostic flow-diagnostic.json:
5401D0 initstate6 normal/7logout;53EF80 byte435973;53D0F0 result0/state6→5E7BE0.
Это pcode research,неfullASM/CFG/equality. Следом найти real producer/dispatcher,
перенести client data bootstrap и выбор персонажа;не force UI/auth success.
Create53BB20 brokenfunction/JUMPOUT/ложнаяCRT аннотация,использовать ASM.
Country slot284false во всех11профилях;не force legacyreconnect. Server readonly.

### История ранних наблюдений138 (до исправления root)

Before138 snapshot47files сохранён;137commit f33d025. OrdinarySpriteMgr теперь
legacy7→target3(login),8→2(loading),3→4(main),0/1unchanged. Без null guards
исправлены два реальных nativecrashes изmissing sprite files. В CgpLogin.Render
добавлен opt-in diagnostic PNGcapture послеEndScene;обычныйрежимне рисуетextra.
Debugger следуетреальному WinMain→Title→LoginCreate→Render,затемточкевозврата.
ТекущаяPE9adc8d0d…(current normal-link),engine137неизменён.182/20build/link0.
Actual run work/m9/9adc8d0d/login-frame001:55inputs,real lobby10files+titlelogo,
captureframe70/3203ms/640x500,created1/loaded1,returnaftercapture,no fatal.
PNGviewed:реальнаяlobby/логотип/UI,НОокнаперекрываются;этоНЕfull455LoginUI.
Старыйversionlabel0.738неисправлялсякосметически. Далееtargetvisibility/window
init/layer routing;Titlemovie/fourstage/auth остаютсяOPEN. Data refs/failures:
artifacts/client455-progress/login138-before-sprite-route.json,
login138-after-sprite-route.json,login138-lobby-frame.json.
IDA621d88dc saved/closed;idb_list count0. Raw diagnostic pcode9functions/pages:
artifacts/client455-progress/login138-reference/session.json. Это не fullASM/
secondary acceptance. Root RTTI CGUIScreen TD BD5D1C→COL B808B4→vtable ADAD8C,
slot208→630A60 (RVA230A60),slot40→632430. Root Add вызывает Add/Insert,SetParent,
затем Show(0);genericContainer.Add сам по себе Show(parent) остаётся правильным.
В legacyRoot.Add финального Hide нет: вероятная причина всех открытых окон.
Следом проверить fullASM/CFG и две pins до изменения,не просто скрывать панели.
Нативныхjobпослеlogin-frame001нет. Probe --login-frame --settle-ms3200 --with-lobby.

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

## Исходное исследование Title138 (история)

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
