# 142: штатное начало загрузки предметов 455

2026-11-10. **PARTIAL, M6 открыт.**
Gate: `inventory/client455-item-bootstrap-checkpoint.json`.
Проверка: `scripts/Invoke-Python.ps1 scripts/checkpoint_client455_item_bootstrap.py`.
Обычный Login подключён к загрузке ItemCash→ItemSetEffect→Item47/NDItem.
Полный bootstrap,legacy consumers,экипировка и экран выбора ещё открыты.

## Подтверждённые данные

Две закреплённые x86 PE/base400000:
primary SHA `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`,
secondary `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.

| RVA | Роль |
|---|---|
| `0x1f8ec0` | ItemCash paths/selector и локализация DWORD16 |
| `0x2089e0` | ItemSetEffect: одна count/stride таблица |
| `0x4329b0` | Korea profile vslot160: true |
| `0x42c490` | Остальные10 profiles vslot160: true |
| `0x1fee30` | Item47/NDItem; переиспользовано полное588-instruction исследование089 |

Четыре новые полные функции:257 инструкций/27 положительных CFG blocks,включая
все вынесенные chunks. Их regions и11 slots одинаковы в обеих PE.
Raw: `artifacts/client455-progress/item-bootstrap142-reference/session.json`.
Предыдущее Item исследование089/его SHA проверено,его большой suite не повторялся.
IDA b958e3d1 сохранена/закрыта,list0. Входные EXE не запускались.

Все11 профилей используют segmented Item,а не только Taiwan. Selector-1 выбирает
ItemCash.edf/NDItemCash.edf,прочие значения — полный десятичный suffix `%d`.
ASM передаёт полный DWORD selector;декомпилятор ошибочно показывает char.
NDItemCash читает count/ignored stride и заменяет DWORD16 каждой базовой записи.
При несовпадении counts базовая таблица сохраняется,loader возвращает0.
Внешний bootstrap игнорирует cash/set return и продолжает Item loading.

## Реализация и границы

Существующий RF455ItemDataStore подключён к обычному CItemDataMgr::LoadData,
который раньше пытался читать455данные как старые ITEM_DATA/embedded descriptions.
Добавлен LoadBootstrap455 для первых трёх target calls. Обычный Login вызывает
его на прежнем месте получения данных после ответа входа.
Cash/set owned tables живут в CMainApp.Items455 рядом с существующим store.
Typed accessor GetData455 возвращает borrowed span из настоящего owner.

В обычной PE подтверждены transfers cash→set→Item по декодированным CALL/JMP.
Тонкий LoadData inlined в bridge. GetData455 сейчас удержан full-object probe,
но ещё не обычными игровыми consumers. Legacy GetData/derived CBoardItem/
CEquipItem/Avatar default gear **не перенесены**:455raw не кастуется в старые
структуры. Загрузка данных не выдаётся за готовую экипировку или выбор персонажа.
Проверки bad extents и reload guards — собственная ограниченная политика;
полная эквивалентность unsafe inputs/reload lifetime не заявляется.

## Исполнение реальных данных

Full-object probe вызывает настоящий receiver world-entry:ответ12 задаёт cash
selector,затем реальный CItemDataMgr.LoadBootstrap455. Это fixture bytes в памяти,
не успешная авторизация. Каждый случай исполняется в отдельном процессе,без reload.

| Данные | Selector | Cash localization | Item47/ND и typed wrappers |
|---|---:|---|---|
| Korea | -1 | PASS | PASS |
| Taiwan | -1 | PASS | PASS |
| Russia | -1 | count mismatch,base retained | PASS |
| Taiwan | 1 | PASS | PASS |
| Taiwan | 10 | PASS | PASS |
| Korea | 1 | NDItemCash_1 отсутствует,base retained | PASS |

Во всех случаях cash base1000rows,set-effect1373rows,Item47/76049rows.
Независимый Python oracle сравнивает CRC32 всех локализованных таблиц,work directory,
descriptions/dungeons и consumed extent. Это47 полных таблиц,не76049игровых функций.
Для12 выбранных типов созданы настоящие CBoardObject/managed payload,имя/data
привязаны к loaded row;clone удерживает payload,последний owner освобождает его.
Проверены границы typed accessor и полные selector paths вплоть до65535.
Все шесть случаев PASS. Raw outputs/console/exe hashes сохранены в native report.

29 staged asset references/165,101,584 logical bytes через shared pool.
Из уже существующих owned copies принято46,200,039 bytes,новых pool copies
509,445 bytes. Установленный клиент не клонировался;originals без изменений.
Config/expected/own EXEs private. История141 сохранена before142,49files.

## Обычная сборка и следующий участок

Own SHA `f0114c80b2a08bdb313113368c729b4a7cb4b4c0c05cdc193ee368edf627f2d1`,
x86/base400000/entry172C30/2283520bytes.182client/20kernels/build/link0/unresolved0.
Engine137 unchanged. Required normal consumers обновлены;неизменённые широкие
account/resource/graphics suites не повторялись. Их точная предыдущая PE сохранена.
Fresh WinMain/Miles/providers иобычный Login проходят:frame70/3234ms,640×500,
Renderreturn/exit observed,no fatal. PNG276eb78c… просмотрен:lobby/ожидание,
лишние панели скрыты. Обычный success-response bootstrap в этом запуске не проходился.

Следующий143: PlayerCharacter/SkillForce/Store/Character tables и локализация,
class tiers/имена;затем реальные item/Avatar equipment consumers и экран выбора.
Не загружать новые raw records через старые C++ layouts. Все прочие bootstrap
таблицы/квесты/мир/игровые сценарии и требования М9 остаются.
Оценка25%(20–35%),0/12 полностью принятых областей,M6/M6F/M7/M9 OPEN.
