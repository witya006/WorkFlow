# Предмет на курсоре и резервные объекты — работа101

2026-11-07. PARTIAL. В обычный клиент перенесены Copy620, владение hover object,
две резервные копии и передача иконки в CGUIScreen. Сборка и выбранные проверки
проходят. Работа с ненулевым Avatar, полная очередь операций и игровые обработчики
не приняты. M6/M6F/M7/M9 остаются открытыми.

Текущий checkpoint: `inventory/client455-board-hover-checkpoint.json`.
Проверка: `scripts/Invoke-Python.ps1 scripts/checkpoint_client455_board_hover.py`.
Предыдущий100 runtime checkpoint теперь исторический; его статические доказательства
и кадры сохраняются. Общего процента восстановления клиента нет.

## Закреплённые факты

Оба455 x86, image base0x400000. SHA-256 основного:
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
второго:
`46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.

23 canonical functions/1156 instructions/23 равных диапазона обеих455:
constructor/destructor/reset manager RVA0xfb560/0xfb6f0/0xfb840;
SetHover0xfe020, GetHover0xfe2b0, operation getter0xfe2f0,
ClearOperation0xfe330, ReturnHover0xfe3b0, operation setter0xfe5c0;
Add forward0xfd660, FrameMove0xfcf90, Copy6200x6b660;
screen Add/Remove0x232210/0x232370; item ID0x21a7d0, quantity flag0x2300e0,
tooltip reset0x234140; avatar predicate0x12b810, getter0x1e290,
pending flag0xfd640, cancel0x12ab50, effect/sound branch0x12ac40,
IsEmpty0x19f00. Sizes и hashes находятся в reference manifest.

Полные assembly/decompilation/ranges:
`artifacts/client455-progress/board-hover101-reference.json` (ignored).
IDA sessionf131119f сохранена и закрыта, sessions count0. Native MCP работал
через зарегистрированный сервер; конфигурация и установки не менялись.

Target manager выделяет два отдельных CBoardObject620, рядом с hover pointer.
Подтверждены смещения: hover+244, previous+248, operation+252. GetHoverObject
возвращает hover, если он есть, иначе непустой **второй** operation backup.
Первый previous backup в этом fallback не участвует. IsEmpty проверяет index
наFFFFFFFF. HaveHoverObject и наличие fallback — разные состояния.

SetHover(null) сначала копирует hover в previous, очищает operation backup,
затем освобождает hover и убирает экранную иконку. Замена hover ненулевым
источником освобождает старый объект и иконку перед Clone/Add; previous
при такой замене не обновляется. Destructor сначала удаляет boards/hover,
потом previous и operation. Constructor обнуляет320-byte target manager,
задаёт только org/tar board IDs=FF и создаёт оба backup; остальные поля
не считать автоматическиFF.

Copy620 очищает destination, копирует все620 байт и удерживает shared payload.
Self-copy наблюдает уже очищенный source; для него дальнейшее копирование
не меняет объект. В собственном коде избегается overlapping memcpy для self.
Смесь с legacy derived payload objects в этот API не принимается.

Screen Add при ненулевой source icon копирует её, включает количество,
заменяет empty itemID на0, показывает и центрирует по текущему размеру,
скрывает mouse и уведомляет root windows через PickingObjectEvent(TRUE).
Затем manager устанавливает размер64 для kinds0/3/4, иначе40. Поэтому конечная
иконка не обязательно остаётся точно центрированной относительно нового размера.
Последний lock setter получает raw flag21, в отличие от normalized wrapper
refresh100. Remove вызывает Empty, скрывает icon, показывает cursor и шлётFALSE.
Обычный manager FrameMove обновляет hover icon до остальных boards.

AddObject использует raw slots, без GetBoard alias2→Equipment1; допускает
IDs0..15,35,36,38,39. После вызова virtual Add он возвращает0 даже при успехе.
ReturnHover использует GetHoverObject, включая operation fallback. Это отличается
от передачи только m_pHoverObject из старого кода.

## Реализация и ограничения

`client455_board_hover.h/.cpp` содержит source-owned state с двумя владельцами
CBoardObject. Его общий класс CBoardManager остаётся собственным C++ типом,
не наложением на private320-byte ABI. Legacy backup временно сохранён для ещё
не перенесённых потребителей; typed backups отдельны. Headers и ordinary
manager/screen consumers подключены через `client455_board_hover_port.py`.
Copy455 реализован в `client455_item_object.cpp` для собственных620-byte wrappers.

Legacy GetHoverItem и GetDeletedHoverItem не приводят typed wrapper к CBoardItem:
они явно отказывают для неподдержанных typed случаев. В частности legacy deleted
getter отказывает во всём typed mode. Эти callers ещё нужно перенести вместе
с fullCItemBoard.Add/network handlers; это не завершённая совместимость.
Прямой Add сейчас подключён к настоящему CLinkBoard. Существующие другие boards
с typed payload требуют их собственных полных providers, а не успешного no-op.

Live Avatar branch намеренно не объявлен готовым. RVA0x12b810 при null Avatar
возвращаетfalse. При ненулевом Avatar он проверяет low BYTE значения, полученного
getter0x1e290 (target field17708), на2/6/10. При дополнительном pending flag
SetHover выполняет cancel/effect/sound/message цепочку. Производители поля,
полный смысл состояний и владельцы этой цепочки ещё требуют восстановления.
Ненулевой Avatar сейчас вызывает явный отказ **до** изменений hover ownership.
Не подставлять legacy IsDeath/CombatState или произвольное поле по догадке.

Add очищает реально существующий source tooltip. Target имеет три tooltip
контекста и дополнительные флаги, которых текущий screen ещё не воспроизводит.
Полный reset этих трёх слоёв, cursor animation/system cursor, GUIItem children,
privateABI/unsafe/OOM/concurrency/shutdown остаются открытыми.

## Проверка

Native probe использует actual CMainApp data/manager, настоящий EDF inventory
owner, ordinary CBoardManager/CGUIScreen и два owned Linker clones:

- Copy620/null/overwrite/self-copy, полное byte comparison и reference counts;
- отдельные previous/operation backups, fallback без hover и приоритет hover;
- replacement order, ClearOperation partial writes, source/backup/destructor cleanup;
- реальные screen visibility/cursor/PickingObjectEvent и очистка source tooltip;
- обычный manager FrameMove обновляет timer один раз, screen Update повторно его
  не обновляет; raw flag21 и центрирование до resize сохранены;
- 256 BYTE IDs, Add false-after-success, raw slot2 против Equipment alias;
- пять действительных payload kinds0..4 и bare wrapper для64/40 и lifetime;
- Quest alias создаётся, но wrapper по-прежнему явно отказывает без sentence
  provider, с освобождением владельца. Это сохранённый known gap;
- пустая typed screen icon получает itemID0; negative half centering проверен.

Nonphysical CPU icons синтетические: они проверяют общую передачу/размер/ссылки,
не полный SF/Animus/Unit UI. PickObserver фиксирует уведомления; реальные
действия ReturnHover/Add выполняют ordinary manager и CLinkBoard, не recording
provider. Source board table лаборатория размещает явно; full factory/bootstrap
этим не принимаются. Native network owner штатно инициализирован offline;
authentication/подключения к игровому серверу нет.

Шесть GPU кадров actual Screen.Draw просмотрены: idle/picked/updated/replaced/
cleared/returned. Видны source icon, предмет на курсоре, timer/lock, возврат
mouse и две настоящие копии в панели. Все owners/registry/Dmalloc очищены.
Это source GPU evidence, не capture оригинального executable.

32 прежних raw кадра (lock6/ready6/timer6/window8/owners3/metadata3) побайтно
сохранены. Их старые reviews связаны через before101 native manifests и
checkpoint100. Не заявлен повторный просмотр одинаковых пикселей. Unchanged
world/audio/159k/atlas093/icon092/2013owner/SF1447/manual095 suites не повторены.
Hotbar7 packets, storage3 и account проходят.

Обычная PE:182 client/20 kernels/57 facade TU,0 unresolved;
SHA `e77ec7e7d33c9ed0f5cff3f44d066ddc64ce86446cd5cd36ba5b7165ff211d8d`,
2144768bytes,x86,base400000,entry0x1586b0,WinMain0xb7940,
afterCreate0xb7aaa. Точная PE проходит existing Create return1 с offline
launcher fixture; остановлена до игрового цикла. Полный455 startup не принят.
Derived engine546a7529… и baseline033/source не менялись. История отсутствующего
snapshot старой082 derived library остаётся как в099.

Original/server files не менялись; input EXE не исполнялись. Новых remote,
публикаций, установок или серверной разработки нет.

## Следом102

Восстановить live Avatar predicate/cancel owners, затем actual UI use/remove/
swap/hover/MsgProc и manager operation queue. Подключить inventory/equip/SF/
Animus providers, typed quantity/backup/network consumers, Avatar potion cache,
Macro35/Vending27/fullCItemBoard.Add и normal table bootstrap. Вернуться к
Quest sentence provider и трём tooltip layers. Все прежние клиентские gaps
и критерии client-acceptance.md сохраняются; не считать эту лабораторию
приёмкой игрового сеанса или всего перетаскивания455.
