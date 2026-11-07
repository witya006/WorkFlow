# Item-icon-metadata094 — реальные предметы и владелец иконок

2026-11-07. **PARTIAL, M6**. Восстановлены выбранные поля физических предметов
и передача реального payload в существующий CGUIInventoryBoard. Обычный
TakeInItem окна теперь вызывает общий проверенный код заполнения ячейки.
Полная цепочка CItemBoard.Add, общие уведомления и игровой цикл ещё не приняты.

## Эталон и границы

Два неизменных x86 файла, image base0x400000:

- current SHA-256 b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
- backup SHA-256 46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.

Совпадают28 диапазонов:22 полные функции/1138 инструкций и6 диапазонов vtables.
Окна внешних EH-инструкций также закреплены. Из15 реальных инструкций чтения
извлечены смещения полей; маска пользователя получена из AND EAX immediate.
Quantity vslot64 проверен у CNormalItem, CAnimusItem, CUnitItem и CUnitPartsItem.
У SF/Quest этот слот имеет другое назначение — общего выдуманного getter нет.

Raw выгрузка и закрытие IDA4f540aaf сохранены в ignored artifacts/client455-progress/
item-metadata094-*. После сохранения/закрытия список сессий пуст. Настроенный
MCP probe подтвердил66 tools/10functions/decompilation/close. Input EXE не
исполнялся; серверные исходники и исходная установка не менялись.

| RVA | Подтверждённый контракт |
|---|---|
| 0x16940 / 0x65ea0 | Mesh/classification72 и sprite76 из реального data16 |
| 0x5fde0 / 0x604f0 | Grade152 для equipment kind1..10 |
| 0x5ffc0 / 0xa2e0 | Требуемый уровень по kind88 и отдельным offsets |
| 0x4e80 / 0x5c60 | BYTE quantity92 Normal / постоянная1 остальных basic |
| 0x6b370 / 0x6b920 / 0x6b970 | Делегирование kind и обновление grade оболочки |
| 0x273390 / 0x277480 | Inventory20 sockets, parent5 packs/quantity guard |
| 0x21ca50 / 0x21c9d0 / 0x21cb80 | Race/user byte и required-level predicate |
| 0x79320 | Полный CItemBoard.Add, исследован для карты обязательных связей |

Имя64 и прочие поля из088–091 не переопределялись. Новый public rawMetadata()
возвращает уже существующий span до конца реального владельца таблицы: некоторые
целевые unchecked reads пересекают объявленную строку. За пределами владельца
источник бросает out_of_range; эти опасные домены не объявляются совпадающими.
На выбранных575 случаях новых выходов за владельца не встретилось.

## Что реализовано

RF455_ReadBasicIconMetadata читает classification, изображение, количество,
required level и grade из настоящих RF455BasicItem0/2/3/4. Dedicated SF/Quest
метаданные явно отклоняются. Это не полная интеграция окон Animus/MAU.
RF455_IconUsable455 воспроизводит race/user0..255 и BYTE level/required, включая
значения255. Поле `(itemID & 0x0ff00000)>>20` подтверждено в455 и уже присутствует
в старом коде; это не новое различие версий.

CGUIInventoryBoard.TakeInItemFields455 выполняет обычный core673390:20-ячеечная
граница, target icon0/cell64, ID/sprite/quantity, sticky required-level255,
автоматический SetSprite, displayedsize32, usable tint и сброс trade marker.
Обычный существующий TakeInItem вызывает этот код с текущей расой Avatar.
Общий обработчик реально сохранён в normal PE; это проверено по MAP.

TakeInItem455 принимает настоящую CBoardObject с physical payload0, использует
тот же core, выставляет grade и связывает иконку с индексом оболочки. Раса
передаётся вызывающим контекстом. Quantity0 отклоняется как у parent window;
сам raw core допускает0, как target673390. Invalid itemID сохраняет успешное
заполнение окна, но GetItem возвращаетnull: оболочка получаетnull вместо ссылки
на пустую иконку. Required-level255 сохраняет предыдущее значение, не обнуляется.

Этот source-owned handoff проверен через actual CGUIInventoryBoard и production
CObjectPack/Clone. **Полный CItemBoard.Add ещё не вызывает его в игровом потоке**.
RF455_ReadBasicIconMetadata и сам handoff пока удаляются normal linker как
неиспользуемые; own-entry тест вызывает их из той же production facade.
Сохранённый ordinary core и отдельно проверенный handoff не равны готовому
инвентарю. Принудительное удержание неиспользуемого кода не применялось.

## Проверка

Oracle содержит566 basic случаев и9 Quest отказов, всего575.
Проверено566 actual metadata результатов на реальных Item/NDItem/Quest/Character/
SF данных CMainApp,9 Quest и отдельный SF отказ.520 race/level случаев используют
независимую таблицу разрешённых рас и BYTE границы.

16 непустых строк из разных таблиц становятся реальными payloads, source
CBoardObject, клонами в настоящем pack и иконками настоящего окна. Их ID/sprite
не вводятся вручную. Проверены quantity0/255, sticky required255, grade update,
invalid ID, slots20/255/null/wrongkind, очистка и last-owner release.
Три GPU кадра просмотрены: реальные предметы, изменение одного предмета,
пустое окно. Для обновления менялись только данные в памяти собственных
загруженных копий, затем восстанавливались. Staged files остались неизменны.
Оригиналы и серверы не затрагивались. Sprite Dmalloc вернулся к baseline;
полные COM/reset/OOM этим не доказаны.

Первоначально тест предполагал equipment у первого образца; первая строка была
другой категории. Тест выбирает equipment по реальному kind88. Затем GPU выборка
улучшена: вместо служебных первых строк с Default выбраны реальные ненулевые
изображения. Повторялись затронутые сценарии, не все старые большие suites.

Новая собственная RF_Online.bin: SHA-256
85a909e356f40f713d2f785fca2a973c920034f15bf5926c2149ba8374de9685;
x86,2108416bytes,entryRVA152d60,WinMain b7540,afterCreate b76aa.
182client/20kernels/49facade TU,0unresolved, движок082 неизменён.
Hotbar7 packets/storage3 runs/account и earlyKorea949/localTCP/Miles/exactPECreate1
проходят. First-chance события сохранены; полный login/game loop не проверен.
Неизменённые world/audio/159k,093atlas,092icon,2013owner/1447SF bulk не повторялись.
Их прежние runtime gates исторические для новых link/reports; static proofs
сохраняются. Новый gate inventory/client455-item-icon-metadata-checkpoint.json.

## Следующая интеграция

095: восстановить связи полного CItemBoard.Add и shared icon state. Target
вызывает Linker6, Macro35 и Vending27, переносит cooldown/grade/quantity state.
Macro/Vending providers и полный общий registry пока не приняты. Старые mixed
derived payloads и глобальный IsEqualItemType нельзя просто использовать для
новых base wrappers: предикаты и callers требуют согласованного переноса.
Не заменять обязательные notifications успешными no-op.

Затем ordinary table bootstrap/profile, fullLinker5x10/input/use/cooldowns/
download, dedicated SF/Quest, полные GUIItem children/quantity-usability followers,
остальные36 boards/Trunk/protocol/Tutorial/QBI/fourstage/Login/auth/gameplay.
M6/M6F/M7/M9 остаются открытыми; общей доли готовности эти проверки не задают.
