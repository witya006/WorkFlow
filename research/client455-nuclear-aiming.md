# Контроллер ядерного прицеливания455 — работа107

**PARTIAL, M6.** В CMainApp восстановлен20-байтный core прицеливания:
effect handle, pending и независимая командная позиция. Он использует настоящие
gMouse/CLevel/BSP, обычный effectcore и tagged Miles. FrameMove включён перед
FrameMoveAllEffectsList; Clear вызывается перед закрытием tagged audio.
Полный контейнер, игровые команды, сообщения и мировой порядок кадра ещё открыты.
M6/M6F/M7/M9 не закрыты.

## Опора в455

Native IDA MCP session `7cb76d0f` сохранена/закрыта; после закрытия список пуст.
19 полных функций,1670 инструкций,19 равных диапазонов и2 vtable slots двух
закреплённых x86 binaries, image base `0x400000`. SHA-256:

- `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
- `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.

| RVA | Назначение |
| --- | --- |
| `0x12aaf0` / `0x12ab30` | ctor20 / пустой destructor |
| `0x12ab50` / `0x12ab90` | Clear / FrameMove |
| `0x12ac00` / `0x12ac40` / `0x12ad20` | pending / visual state / командная позиция |
| `0x12ad70` / `0x12ae70` | ctor32 и Frame контейнера с list12 и inline core20 |
| `0x3d91a0` / `0x3d8640` | MovePosMagicEffect / MoveMatrixEffect |
| `0x3e22f0` / `0x3e0d10` | null-character StartMagicEffectType / GetCreatePos |
| `0x4bee60` / `0x4b4820` | PlayAtListener / настоящий dynamic-light limit |
| `0x4e7df0` / `0x4ba830` | CLevel screen-ray wrapper / BSP pick |
| `0x0fe020` / `0x0fd640` | hover cancellation / pending getter |
| `0x738504` / `0x6ecb5c` | реальный и dummy pick vtable slots |

Сырой вывод: `artifacts/client455-progress/nuclear107-reference.json`.
Широкий дополнительный поиск writers в этом файле **частичный**: достигнут
лимит2M instructions/адрес9f0852. Он не является доказательством полноты callers.
Диапазоны, размеры, hashes и ограничения: `inventory/client455-nuclear-aiming-reference.json`.

## Сохранённые правила

- SetPending вызывает visual setter только при старом pending0, затем сохраняет
  полный DWORD. Повтор1 не перезапускает эффект/звук; переход1→0 сохраняет их.
- Visual1 сначала гасит прежний handle, запрашивает положение курсора, запускает
  cue1358041136 с null character, всегда играет Radar277034 loop1/tag1 и
  устанавливает настоящий лимит dynamic lights3.
- Другой visual state останавливает звук только при ненулевом effect handle.
  Поэтому отсутствующий cue всё равно включает звук, а Clear с handle0 оставляет
  звук играть. Этот target quirk воспроизведён; стенд очищает его отдельно.
- SetPosition копирует три float последовательно. Cursor FrameMove меняет
  визуальный эффект и не записывает эту командную позицию.
- MovePosMagicEffect вращает локальное смещение каждой дорожки и переносит child;
  master base matrix остаётся прежней, как в455. Принятый живой сценарий yaw0;
  все числовые/небезопасные домены этим стендом не проверены.
- Hover отменяет прицел только при соответствующем статусе аватара **и** pending.
  Pending0 теперь разрешает обычное перетаскивание. Pending1 пока явно отклоняется
  до мутации предмета, поскольку настоящий localized C1A pipeline не перенесён.

## Реальная проверка

`probe_client455_nuclear_aiming.py`: собственный полный набор клиентских объектов,
настоящая neutralAS1.bsp, штатный CLand, реальное BSP-картирование двух положений
курсора, шесть child из архивного cue и настоящий Miles sample Radar_00.wav.
29 целевых проверок проходят. Проверены повтор pending, удержание при pending0,
замена/исчезновение прежнего эффекта, Clear и missing-cue audio quirk.
90 ticks достаточно для исчезновения обоих master/children. Dmalloc
`785169→785169`;7 warnings =6 прежних подтверждённых R3T и ожидаемый missing cue.
Звук приглушён стендом; запись слышимого выхода не производилась.
Run: `work/m9/a3a3c42f/nuclear-aiming-001`.

Новая RF_Online.bin: SHA-256
`d09eec8dd10a35dbd2bb07523901e0b66dc250dec611fee7efe231800b749c9d`,
2157056bytes, x86/base400000,entryRVA15adc0,WinMainRVA b8ed0,
afterCreateRVA b9044.182 client/20 kernel/60 facade,0 unresolved,Create→1.
FrameMove/Clear retained в карте обычной PE; SetPending пока не имеет игрового
producer и удалён linker из конечной PE. Он проверен в полной объектной сборке
стенда; это не доказательство готового пользовательского игрового пути.
Engine `546a7529b51139e856b1a108fcad7849c14b2d00563b7abbfdcc8db10026fa5a`
не менялась.033 baseline сохранён; старого082 derived snapshot по-прежнему нет.

Регрессии: status62 (pending0 с реальным avatar; pending1 refusal с явно
синтетическим битом),magic36/resources66/audio157/effect-runtime573/account/
hotbar7/storage3 прошли. Просмотрены4 новых GPU frames эффекта и6 hover;
последние побайтно равны106. Большие159k/world/audio suites и прочие32 GUI
frames не повторялись. Контрольные4GPU frames относятся к effect-runtime lab,
а не к новому BSP/Miles lab, который не делает GPU captures.

## Оставшиеся требования

108: восстановить настоящий C1A/CE7 message/notification dispatch, lifecycle
владельца сообщений и live pending1 hover. `_SetSystemMsg(DWORD)` в старом source
пустой, а chat-only overload не доказывает полный455 путь; не использовать их
как подмену успешной отмены. Затем command/response producers, list12/container,
final position commit и остальные способы отмены. Нужны полноценный world frame/
render order, dynamic-light compositing, quality UI, blur/advanced FX/device
reset. Target orthographic pick ещё не перенесён; menu dummy/null/uninitialized
domains явно отклоняются. Размещение core внутри CMainApp не доказывает32byte
private ABI всего target container; shutdown/FP/OOM/concurrency остаются открытыми.
Все прежние требования `docs/client-acceptance.md` сохранены.

Текущий gate: `inventory/client455-nuclear-aiming-checkpoint.json`.
106 runtime gate исторический, snapshot сохранён в artifacts.
Воспроизведение: `scripts/Invoke-Python.ps1 scripts/checkpoint_client455_nuclear_aiming.py`.
Original/server files не менялись, входные EXE не исполнялись, публикации нет.
