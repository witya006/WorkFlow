# Следующие шаги

Обновлено 2026-11-10. **138 PARTIAL; M6 открыт.**
Gate: inventory/client455-login-checkpoint.json.
Собственная сборка ba23dd6d… проходит обычный WinMain→Title→Login и показывает
реальную lobby/окно ожидания. Root Add теперь скрывает зарегистрированные окна
по455; наложение лишних панелей устранено. Frame70/3203ms просмотрен, no fatal.
Engine137 не изменён, сборка182/20 и link0/unresolved0. Полный Login455 не принят.
Доказательства: research/client455-login.md.
M6/M6F/M7/M9 OPEN. Оценка готовности около25%(20–35%),не новое доказательство
эквивалентности;inventory/client455-progress-assessment.json.

1. **139/A–B: response→bootstrap→selection.** Проверить настоящий клиентский
   обработчик ответа входа и его переход в загрузку данных/выбор персонажа.
   Diagnostic flow: artifacts/client455-progress/login138-reference/flow-diagnostic.json.
   Target init5401D0: обычный state6, logout state7; getter53EF80 читает byte435973,
   consumer53D0F0 при result0/state6 вызывает5E7BE0. Это пока pcode, не fullproof.
   Начать с сетевого producer/dispatcher для этого результата и real client table
   bootstrap, затем экран выбора. Не обходить ожидание и не форсировать успех.
   Серверные исходники/код не менять. Country slot284 во всех11профилях false;
   не включать legacy reconnect безусловно.
   Full Title/movie/factory4/next-stage остаются открыты. Legacy factory3/modulo.
   Create53BB20 имеет разбитую IDB границу и ложную CRT-аннотацию: использовать ASM.
   РеальныйAVI и начальные Title данные есть в research/client455-title-initial.md;
   не включать недостижимый primary FrameMove fade, не переписывать CRT/COM.
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
Before-root snapshot13files/4.66MB: artifacts/client455-progress/login138-before-window-registration/manifest.json.
IDA5a0405db/5818692d saved/closed; idb_list count0. Остальные инварианты вproject-memory/AGENTS.
