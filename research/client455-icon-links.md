# Общий реестр иконок и обновление состояния — 095

2026-11-07. M6, ограниченный перенос; M6/M6F/M7/M9 остаются OPEN.
Текущий checkpoint: `inventory/client455-icon-links-checkpoint.json`.
Работа только над клиентом; серверные файлы и оригиналы не изменялись.

## Закреплённые входы и доказательства

Оба входа x86, image base `0x400000`, EXE не исполнялись:

| Вход | SHA-256 |
|---|---|
| current | b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b |
| reference-backup | 46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558 |

22 выбранных диапазона совпали между pins. Полная выгрузка выбранных функций:
1154 asm instructions, включая внешние EH tails; raw evidence хранится в ignored
`artifacts/client455-progress/icon-links095-reference.json`. Малый манифест:
`inventory/client455-icon-links-reference.json`. IDA session22f5e8a7 saved/closed,
после закрытия list count0; configured MCP probe также прошёл.

| RVA | Подтверждённая роль |
|---|---|
| 0x3ae520 | регистрация иконки в семантической группе |
| 0x3ae690 | удаление первой записи указателя по текущему ключу |
| 0x3ae780 | поиск группы по текущему ключу |
| 0x21a8c0 | WORD quantity: self, затем зарегистрированные члены |
| 0x21a960 | BYTE usable: self, затем зарегистрированные члены |
| 0x6ba60 / 0x21a9f0 | прямые WORD110 / BYTE117 stores |
| 0x3af6b0 / 0x3aead0 | std::find и vector.erase; нет проверки end() |
| 0x384330 | append без удаления дубликатов |
| 0xf3240 / 0xf3440 | target Macro Add/Remove вызывают регистрацию/удаление |
| 0x100590 / 0x1007e0 | target Linker Add/Remove вызывают регистрацию/удаление |

Ключ восстанавливается по прочитанным binary operands, а не имени класса:

```text
((uint64(itemID & 0x0fffffff) << 28)
 | (objectIndex & 0x0fffffff)
 | (uint64(BYTE(iconType)) << 60)) modulo 2^64
```

Биты56..59 равны0; старшие биты type отбрасываются. Это группировка по данным
предмета, не граф указателей source/parent. Даже незарегистрированный инициатор
может обновить зарегистрированные копии того же ключа. Обратное обновление
незарегистрированного оригинала не происходит.

Регистрация добавляет дубликаты. Удаление убирает первый совпавший указатель,
оставляет пустую группу в map и каждый раз вычисляет текущий ключ. Target не
переносит запись автоматически при изменении ID/type/index. Владелец обязан
удалить регистрацию до смены идентичности и уничтожения объекта.

Количество сохраняется как WORD; usable — сырой BYTE, без bool normalization.
Quantity loop пропускает null, usable loop — нет. Public source API принимает
ссылку и не предлагает nullable registration. В target удаление отсутствующего
члена существующей группы вызывает erase(end()), undefined behavior. Source
явно бросает logic_error в этом домене: это известное расхождение, не доказанное
эквивалентное поведение. OOM/concurrency/полный private UIManager ABI не приняты.

## Реализация и её границы

`scripts/native/client455_icon_links.{h,cpp}` содержит source-owned map/vector и
typed CGUIItem.SetNum455/SetUsable455. Общий владелец — настоящий g_MainApp;
его поле объявлено до владельцев UI/items и уничтожается после них.
`scripts/client455_icon_links_port.py` переносит header hooks без изменения
originals. Untyped legacy setters сохраняют локальное поведение.

Обычная PE действительно содержит SetNum455 RVA0xc8d20, SetUsable455 RVA0xc8d60
и find RVA0xc8db0 из canonical RFClient455Facade. Register/unregister пока unused
в ordinary graph: полные CLinkBoard/CMacroBoard Add/Remove ещё не подключены.
Own-entry probe регистрирует реальные CGUIItem copies явно через production API;
это проверка реестра, не приёмка настоящего Linker/Macro UI. Hover registration
не заявляется. Full CItemBoard.Add также остаётся открытым.

## Проверка

- 160 key cases из binary-decoded masks/shifts, включая BYTE/64-bit truncation.
- Реальный g_MainApp registry: duplicates/order/first-remove, разные ключи,
  masked aliases, unregistered initiator, current-key lookup и retained empty buckets.
- WORD0/1/255/256/65535/65536 и raw usable0/1/2/127/128/255/256/-1.
- Два явных отказа unsafe removal, untyped legacy isolation, полное удаление
  регистраций до destruction. Это выбранный домен, не все возможные lifecycles.
- Actual EDF-backed CBoardObject, actual CGUIInventoryBoard и две actual CGUIItem
  copies: три GPU кадра просмотрены. До изменения все три изображения одинаковы;
  quantity255/usable0 затемняет все; отсоединённая средняя копия сохраняет gray255,
  когда оригинал и другая копия показывают white2. Dmalloc balanced.
- С новой production facade повторён094 metadata/inventory probe:566 metadata,
  520 race-level,16 real icons и все прежние native results прошли; три raw GPU
  кадра byte-equal прежним просмотренным094. Его прежний visual report сохранён,
  связь с baseline проверяет095 checkpoint. Исторический094 runtimegate не
  переписывался как текущий.
- Hotbar7 packets, storage3 runs и account проходят; новая точная own PE проходит
  ранний WinMain и Create return1. Это остановка на начальной загрузке, не вход
  в игру или проверка authentication. Зарегистрированные first-chance exceptions
  остаются в сохранённом отчёте; terminal exception не наблюдался.

Новая PE: SHA-256 `e2741f24ead98890bbf59f6b70bb98f4b3388f999d0950c81c3d388123be4a77`,
x86,2109440 bytes,entry RVA0x1530e0,WinMain0xb7730,afterCreate0xb789a.
182 client /20 kernels /50 facade TU,0 unresolved. Engine082 неизменён:
`9caa283a6bf8a2fa1c9a05251b6cad451296bb03bda8a1860c22a872e88fe769`.

Не повторялись unchanged world/audio/159k/093atlas/092icon/2013owner/1447SF bulk.
Число assertions не означает долю восстановленного клиента.

## Продолжение

096: перенести настоящие Linker/Macro owners и их Add/Remove registration с
корректным clone/refcount и lifecycle. Согласованно исправить typed kind predicate
и смешанные callers. Затем обязательные Vending27 notifications/fullCItemBoard.Add,
normal table bootstrap, Linker5x10/input/use/cooldowns/download. Не заменять
отсутствующие35/27 успешными no-op. Остальные GUIItem children, SF/Quest metadata,
36 boards/Trunk/protocol/Tutorial/QBI/fourstage/Login/auth/game и все прежние
M6F/M7/M9 gaps остаются обязательными.

Повторяемые команды:

```powershell
.\scripts\Invoke-Python.ps1 scripts/audit_client455_icon_links.py
.\scripts\Invoke-Python.ps1 scripts/probe_client455_icon_links.py
.\scripts\Invoke-Python.ps1 scripts/review_client455_icon_links.py
# --record-reviewed только после просмотра кадров
.\scripts\Invoke-Python.ps1 scripts/checkpoint_client455_icon_links.py
```
