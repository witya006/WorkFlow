# Следующие шаги

Обновлено 2026-11-10. **138 в работе; M6 открыт.**
Последний завершённый частичный gate — 137, сохранён в
artifacts/client455-progress/before138/inventory/client455-scene-capture-checkpoint.json.
Текущая собственная сборка 9adc8d0d… дошла через обычный WinMain/Title до
Login и показала реальные lobby/логотип/UI после 3,2с; панели перекрываются.
Это не приёмка Login455. Свежий отчёт: inventory/client455-login-frame-native.json.
M6/M6F/M7/M9 OPEN. Оценка готовности около25%(20–35%),не новое доказательство
эквивалентности;inventory/client455-progress-assessment.json.

1. **138/A: ordinary Title/Login.** Current legacy factory3/modulo против455four/
   explicitnext;Titlelegacy почти пуст. Target читаетCcrLogo.dat исоздаётmovie.
   Начальные данные:research/client455-title-initial.md.20pcode/2contexts ещёне
   fullproof/source. В primaryFrameMove exit/jump безусловны:не включатьdeadfade.
   РеальныйAVI существует. OrdinaryTitle→Login/отрисовка уже наблюдались;
   следующий шаг — регистрация/видимость окон. Target CGUIScreen primary vtable
   VA ADAD8C, Add slot208→630A60: диагностическая декомпиляция заканчивается
   Show(0), в отличие от текущего legacy CGUIScreen::Add. Сначала собрать полные
   ASM/CFG и проверить тела на двух pins, затем переносить семантику. Не скрывать
   окна произвольным списком. Raw: artifacts/client455-progress/login138-reference/.
   Полная Title/four-stage factory/auth/UI цепь ещё открыта;
   использоватьstandardSDKmovie baseclasses при наличии,не переписывать CRT/COM.
2. **B:** clientauth/selection packet/state transitions/errors,безserverwork.
3. **C:** ordinaryworld/avatar/camera/input/movement/collision/animation loop.
4. **D:** target/attack/skills/items/chat,затемfullNPC/quests/social.
5. **E:** remainingfeatures/maps/classes/lifecycle/reset/errors/fidelity,
   M6F/M7/M9 finalsource/build/acceptance. M9 уже определён,не спрашивать снова.

Технический backlog:fullFraction/particleazirang/BBoShasi;per-BSPlight;
positivebinaryFX/caps/failures;worldvisibility/INS/Empty/fullCharacter/UI/protocol.
Все прежние gaps сохранены. Не расширять137 бесконечными микроконтрактами
вместоordinaryfunctionalroute. Числоassertions не прогресс всего клиента.

Asset staging уже общий дляruntimeinputs/generic/early/device/fullscreen;
оригиналы не hardlinked,configs/exes private. Старые151GiBlogical каталоги не
удалены. До очистки — reachability текущих/historical evidence иinputs.
До каждого нового большого scenario использовать shared staging.
Exact137snapshot уже сохранён: artifacts/client455-progress/before138/manifest.json,
47 файлов. Не перезаписывать его новой сборкой. Нативных jobs нет.
IDA621d88dc saved/closed; idb_list count0. Остальные инварианты вproject-memory/AGENTS.
