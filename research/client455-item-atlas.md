# Item-atlas093 — автоматический выбор изображения

Runtime gate093 исторический после [metadata094](client455-item-icon-metadata.md).
Его static atlas proof сохраняется; неизменённые880/4GPU suites не повторялись.
094 проверяет реальный payload→inventory icon handoff и подключает общий fields
core к ordinaryTakeInItem. Полный CItemBoard.Add ещё открыт. Ниже — результат093.

2026-11-07. **PARTIAL, M6**. В обычный клиент перенесены callbacks выбора
страницы и ячейки для предметов, деталей MAU и обычных спрайтов. Typed CGUIItem
вызывает их из настоящего SetSprite по своим itemID/spriteID/type. Явная
SPRITE_INFO больше не нужна для этого пути. Данные реального payload и игровые
окна ещё должны заполнить эти поля: полная цепочка инвентаря не принята.

## Закреплённый бинарный контракт

Оба файла x86, image base0x400000. SHA-256 current:
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
backup:46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
Совпадают18 диапазонов:17 полных функций/1001 инструкция и две switch tables.
Внешние EH windows закреплены отдельно. Из47 инструкций C6 извлечены значения
таблиц armor10, other30 и семь outer-kind страниц для независимого oracle.
Raw и закрытие IDA4c6c7c2c сохранены в ignored artifacts/client455-progress/
item-atlas093-*. После сохранения/закрытия список сессий пуст. Input EXE не запускался.

| RVA | Назначение |
|---|---|
| 0x3b0620 | ItemSearch: категории, новые страницы, геометрия и границы |
| 0x3b0a40 | UnitPartsSearch: страница детали MAU и номер ячейки |
| 0x3b05e0 | DefaultSearch: два младших байта ID → action/frame |
| 0x3b0570 / 0x3b0400 / 0x3b0490 | Диспетчер callback, unit и sprite lookup |
| 0x3b01a0 / 0x3afcb0 | Регистрация callback после загрузки unit |
| 0x3b0a20 | Количество страниц из первого action |
| 0x21c9f0 / 0x21ca10 | Категория bits16..19 / подтип bits8..15 |
| 0x21af30 / 0x1099c0 | GUIItem.SetSprite и emptyID guard |
| 0x4cfb40 / 0x4cfb60 | Размер ячейки / выбор страницы |
| 0x4d1020 / 0x4d1080 | Реальные размеры страницы |

## Реализованное поведение

В сравнении с0.7 добавлены страницы для новых типов предметов, жестов, макросов
и других иконок. Список other расширен до30 подтипов. Weapon subtypes29..31
выбирают страницу30; consumable13 —34. Для other subtype2 номера1024..2047
переходят с12 на37 с вычитанием1024, от2048 — на39 с вычитанием2048.
Неизвестный outer-kind оставляет page0, но неизвестная физическая категория
возвращает отказ. Эти разные default ветви сохранены.

Геометрия использует signed деление размеров на width и unsigned деление ID.
Номер строки сначала обрезается до WORD и только потом сравнивается с числом
строк. Это допускает некоторые большие ID после переполнения; исправление этого
поведения отдельно от восстановления не выполнялось. Проверены width0,
отрицательные значения/INT_MIN,65535/65536 и реальные размеры трёх атласов.
Частичные записи action/frame при отказе самого callback сохранены. Диспетчер
после отказа обнуляет оба поля; ссылка на настоящий спрайт остаётся. Поэтому
некорректная классификация может рисовать штатную ячейку «Default» из файла455.
Отсутствующий unit оставляет переданный результат без изменений.

CGUIItem.SetSprite в typed домене выбирает target8 либо19 для type5/MAU.
Остальные типы составляют classification как `(type<<28)|(itemID&0x0fffffff)`.
Empty itemID0xffffffff ничего не меняет. После назначения ссылки сохраняется
прежний отображаемый размер. Рамка092 назначает свою sprite-ссылку при Draw;
полный порядок child/timer/lock/common-skin инициализации61AF30 пока не
перенесён; полный GUIItem не объявляется готовым. Старые mixed callers
продолжают пользоваться прежними group IDs. Новый targetcache092 используется
как настоящий владелец атласов; полный target spriteUnit57/его lifecycle открыт.

## Проверка

Из файлов455 скопированы и закреплены Common/item.spr, inventory.spr и
unitparts.spr. Exact round trip проходит; в первых action соответственно40,
4 и7 страниц. Oracle использует реальные размеры страниц и значения таблиц,
полученные из байтов бинарника. Все880 сценариев проходят через raw callbacks
и реальный CSpriteMgr:563 отказа, два подтверждённых переполнения WORD строки.
Два переполнения подсчитаны по исходному полному quotient; первоначальный
слишком широкий счётчик largeID уточнён и целевой probe повторён.

Просмотрены4 GPU кадра:16 автоматически выбранных иконок в32/64 размерах,
отдельная деталь MAU, штатная fallback ячейка и пустой itemID. Сетка включает
оружие/броню, skill/Force/class/Animus/gesture/macro и новые страницы. Это
искусственно заданные itemID/spriteID, без выдачи их за реальные payload owners.
Загрузка трёх атласов, выгрузка и повторная загрузка возвращают Dmalloc к baseline.
Динамического захвата эталонного EXE не было; нет заявления о полном COM/reset/OOM.

Все9 кадров092 повторены и побайтно совпадают с ранее просмотренными:
рамки/alpha128/обрезка/WORD65535/hidden/noimage не изменились. Baseline092
сохранён под work/client-reference/item-atlas455, хеши входят в reference093.
Production owners2013/data575/SF1447,hotbar7/storage3/account также проходят.
Неизменённые world/audio/159k suites не запускались.

Новая собственная RF_Online.bin:

- SHA-256 dbd71f6a2b6252f924ccffbb78b344d8f24006102e108ba64f051deab83d4bf1;
- x86,2108416bytes, entryRVA152d60, WinMain b7670, afterCreate b77da;
-182 client TU/20kernels, ещё одна facade TU,0 unresolved; движок082 неизменён;
- ранний Korea949/localTCP/Miles и точная новая PE/Create1 проходят. First-chance
  события сохранены. Успешный полный login/game loop этим не подтверждён.

Настроенный IDA MCP дополнительно проверен:66 tools, список10 функций,
декомпиляция и закрытие smoke-сессии. Первый отдельный probe завершился с worker
code2 в sandbox; тот же настроенный probe с разрешённым запуском прошёл.
Встроенное MCP соединение работало; переустановка/изменение настроек не требовались.

Текущий gate — inventory/client455-item-atlas-checkpoint.json. Runtime gate092
исторический после новых source/report/link; его static references и visual
baseline сохранены. M6/M6F/M7/M9 открыты.

Далее094: получить и проверить настоящий payload→icon metadata contract,
подключить typed board/hover/Linker owners. Затем normal table bootstrap и
миграция mixed consumers. Полные GUIItem children, Quest sentence expansion,
Linker5x10/input/use/cooldowns/download,36boards/Trunk/item protocol,
Tutorial/QBI/fourstage/Login/auth/gameplay и прежние M6F/M7/M9 gaps обязательны.
Серверы и исходная установка не менялись, публикации нет.
