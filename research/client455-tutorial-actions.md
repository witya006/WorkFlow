# Tutorial060: UI, экипировка, курсор, бой и предметы

2026-11-06. Только клиент. Перенесены правила QBI19–46 и добавлена фабрика,
составляющая все47 семейств процессоров. Native использует recording host;
настоящие UI/Avatar/world providers и обычный Tutorial ещё не подключены.
Подготовка всех сценариев не является их игровым исполнением. M6/M6F/M7/M9 открыты.

455 x86/base400000 SHA-256
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
backup `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
50 диапазонов функций, equipment map16 и два virtual bindings совпали между pins.
11 основных функций сохранены с полными инструкциями. IDA758bbebc сохранена и
закрыта. Оригинальные EXE не запускались. WinProc7D2260 сохранён только отрывком;
вся его семантика этой работой не принята.

| RVA | Участок |
|---|---|
| 28640/28A10 | UI open/close и ожидание состояния |
| 28CB0/28E10 | Экипировка и ожидания слотов |
| 28F10/29330 | Курсор, экранные точки и завершение перемещения |
| 29380/29440/29600 | Боевые условия и сброс feedback |
| 29660/29C60 | Создание/использование/link предметов |
| 6A9C74 | Equipment map:16байт, последний элемент46 |
| 1588A0 | Tutorial virtual60: сохранить DWORD enabled в owner+64 |
| 2233C0 | Mouse virtual48: ShowCursor при нужном флаге, затем base Show |

## UI и экипировка

UI19 открывает,21 закрывает и выставляет bit4.20/22 только ждут открытого/
закрытого состояния, без timeout. ID0/63/64 здесь обращаются к board0,
5→7,6→3,11→17. Для board0 выбирается page0; для7/3 после открытия выполняются
tab update(0,0,1) и select0 на одном window instance. Для25 открытие идёт через
поиск предмета477D10 и use4FAA70; при отсутствии выводится NDLanguage284.
27 открывается напрямую,25/27 закрываются через соответствующее special window.
Неизвестный ID в команде открытия/закрытия просто заканчивается, в ожидании
остаётся pending — это подтверждённые ветки оригинала.

Equip23 ищет подходящий предмет по equipment map в временном620-byte board
object и запрашивает экипировку из найденного pack/slot. Временный объект
уничтожается до завершения команды. Slot255 ничего не ищет.25 снимает указанный
слот; для12 затем снимает13.24/26 блокируются при ненулевом4FE2B0 и ждут
наличия/отсутствия экипировки. Для26/slot12 проверяются оба12 и13 по порядку.
Wait255 остаётся pending. Индексы16–254 для23 за пределами доказанной таблицы
не подменяются данными: factory отказывает в этой небезопасной области.

## Курсор

Данные cursor содержат origin shorts(+6/+8), target shorts(+10/+12), button
BYTE(+14), window BYTE(+15), DWORD value(+16).27/31 выбирают origin приFFFFFFFF
либо точки left/right/center/top/bottom по value0–4. Нечётные размеры экрана
усекаются, без округления. Неизвестное value даёт0/0 по original default.

28/32 вызывают default427020 или element4272B0. Их результат — **два DWORD X/Y**,
а не прямоугольник. В QBI сохраняются младшие WORD, затем используются как
signed16. Важно: mapping63 внутри point helper относится к board1, хотя UI19
открывает board0 для63. Не нормализовать эти разные контракты одним mapping.

При провале helper оригинал может читать неинициализированные локальные
координаты. Host явно сообщает initialized; неизвестные значения не выдумываются,
Start возвращает false. Это ограниченная область с известным расхождением,
не принятая за эквивалентность455. Если host знает записанные координаты даже
при false result, сохраняется bit4 и дальнейший порядок оригинала.

Для положительных27/28 выполняется SetCursorPos, при offset-mode добавляются
origin окна и21 по Y; логические координаты сохраняются без origin. Отрицательные
значения передаются5578F0.31/32 ждут точного совпадения с logical cursor.
29 сохраняет исходный DWORD input enabled,30 передаёт исходный BOOL в Mouse Show.
33 проецирует первый world object; при отсутствии/провале заканчивается, при
успехе передаёт движение.33/34 не завершаются собственным Update: их внешние
frame/input writers ещё надо проверить и подключить.

## Бой и предметы

35 передаёт411320(attackType==1),37 передаёт420B70(attackType!=0); обе ставят
bit4.36 ждёт lock target и точный type, затем wildcard, race faction либо
monster template index. При отсутствующем monster template оригинал принимает
условие, что сохранено. Для других совпавших типов дополнительного index filter нет.

38 сравнивает тип feedback, затем wildcard/тип4 либо code найденного skill.
Отсутствующий skill также принимается. Finish очищает attackType/skillIndex/
оба target feedback.39 ставит собственный attackType255 и сравнивает unsigned
context.state52 с threshold. Это доказывает использование owner+52 как значения
прогресса, но его настоящие writers/игровой смысл ещё не приняты. Для всех Combat
Start/Finish общий operationActive устанавливается1/0. Доступ к типизированным
параметрам реализован через RF455_GetTutorialCombatParameters, без raw overlay.

40/41 используют временный CItem, resolve/create, count200 для stackable либо
default value45FE90→item96. Serial берётся из того же process WORD, что в059.
Затем временный board object получает item и serial, ищется пустой inventory
slot и вызывается insert.41 всегда category18, после insert использует предмет
и закрывает board3 только если он был закрыт перед операцией. Порядок destructor
board→clone сохранён; при failed lookup serial не расходуется.

43/45 добавляют ссылку в board6 из board7/3 при наличии объекта и отсутствии
такой ссылки: target pack/slot255/255, select=false.42 ждёт item field112.
44/46 ждут link и при qualifier!=255 дополнительно проверяют identity конкретного
hotbar slot BYTE(qualifier-1), включая wrap0→255. Эти ожидания не имеют timeout.

## Проверка и границы

RF455TutorialActions.lib SHA-256
`71c8d6505c07a939689ddf4007ee857d37fa515634800901f5930c723d022403`.
Собственная x86 PEac630491..., entry RVA13F80, natural exit0. Проверены вызовы,
mapping, short-circuit/flags, оба equipment slots, cursor arguments/lowWORD/
chrome21, lock/race/skill/counter predicates, missing templates, lifetime и
insert/use/link order. Equipment map16 отдельно сверена со всеми байтами455.

Все99 реальных файлов и39864 записей успешно подготовлены с фабрикой0–46.
Отдельный независимый47selector fixture тоже подготовлен. Это проверка parser/
конструкторов/наличия обработчиков; исходные сценарии целиком не проигрывались.
Recording host не является реализацией UI, инвентаря, персонажа или мира.

Общий recording spatial fixture вынесен в native/testing/, без включения в
производственные заголовки. Короткая регрессия059 повторена и прошла: текущая
PEc73ed3fe.../entry9B30, lib42c67412... . Production RF_Online.bin по-прежнему
56905e68... . Большие прежние наборы проверок не запускались; canonical20kernels
discovery сохранилось. Серверы не читались и не изменялись.

Открыты concrete host/CTutorialBoard/briefing, реальный frame/input/feedback,
item tail+25 из059, имя camera276 и остальные numeric/error domains. Полная
обычная Tutorial/fourstage/client455 приёмка ещё обязательна.

Доказательства: inventory/client455-tutorial-actions-{reference,native,checkpoint}.json.
Raw: artifacts/client455-tutorial/actions-*.json и060-*-asm.json. Воспроизведение
через scripts/Invoke-Python.ps1: audit_client455_tutorial_actions.py →
probe_client455_tutorial_actions.py → checkpoint_client455_tutorial_actions.py.

Далее061: настоящий CTutorialBoard/CGUIBriefingWindow и message0–4 providers,
далее связи с Avatar/world/frame и ordinary Tutorial/fourstage. Наличие всех
фабрик не позволяет закрыть M6F или M9.
