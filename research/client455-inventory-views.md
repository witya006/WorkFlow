# Инвентарь, сумки и экипировка455 — частичная работа165

11.11.2026. `inventory/client455-inventory-checkpoint.json`:
**PARTIAL_KNOWN_FAILURE**. В обычном клиенте после принятого выбора персонажа
вернулся Init инвентаря; следующий отказ — собственный guard старого Belt storage
в ещё не перенесённой схеме MainGame::Create_Board. Мир пока не достигнут.
Окна сумок и экипировки проверены как компоненты; их Init в живом входе ещё
не подтверждён: guard находится раньше обычного создания экипировки.

## Подтверждённые материалы оригинала

Два неизменённых455 x86, image base0x400000:

- основной SHA-256 `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
- второй SHA-256 `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.

`audit_client455_inventory.py` проверяет52 полных функции,4375 инструкций,
458 положительных блоков CFG, все страницы и равные диапазоны обоих BIN.
Raw в ignored `artifacts/client455-progress/inventory165-reference/`.
Основные RVA: Inventory Init2766A0/skins276AC0, pack Init272C90/skins273140,
equipment Init2746A0/skins274CF0; inherited Draw25EA40,
currency name2024F0, currency widgets277990/277A50. Все размеры/хеши/диапазоны
записаны в `inventory/client455-inventory-reference.json`.
Новые границы функций не добавлялись; индекс IDA37871 прежний.
Owned sessions e237c3ec и18a8be40 сохранены/закрыты, последний idb_list:0.

## Что подключено к обычным исходникам

`client455_inventory_port.py` и `native/client455_inventory.inc` заменяют
подтверждённые методы обычных CGUIInventoryWindow/CGUIInventoryBoard/CGUIEquipWindow.
Исходные private layouts оригинального C++ не накладываются на собственную память.

- Инвентарь:228×395,14 дочерних объектов и заимствованное окно экипировки.
  Настоящий inventory6/0/0, общий header1/4/0, help слева/close справа,
  пять кнопок сумок через41pixel. Root alphaD8.
- Сумка:20 иконок, сетка5×4,83 дочерних объекта. Размер после Init228×176,
  маски34×34, центрированная подпись483 и маленький close common0/15..17.
- Экипировка:16 владельцев,67 дочерних объектов, реальные позиции и естественные
  размеры изображений. Пустые отметки alpha70. Два дополнительных слота
  располагаются в(46,4)/(150,4); их предметное назначение не выдумывается.
- Валютные подписи10/11/12 выбираются по encoded race/2; title47B/gold3C7.
  Значения сохраняют signed64, используют уже сверенный x87 money kernel
  и выравниваются относительно более широкой подписи.
- Открытие/закрытие и режим одной сумки, родительская связь экипировки,
  действия pack buttons и help1204. Маски trade/useless используют настоящий
  **sprite44 SocketState.spr**, отдельный от ItemLock.spr.
- Из двух классов удалены старые специальные Draw: их455 vtables наследуют
  обычный65EA40, который возвращает1 и для скрытого окна. Selected/ready objects
  уже находятся в настоящем списке детей; старое повторное рисование исключено.

## Особенности, которые нельзя исправлять произвольным alias

Target677320 сохраняет pressed descriptor inventory/action2/frame11.
Во всех четырёх прочитанных штатных inventory.spr action2 имеет11 кадров0..10.
60B4F0 копирует pressed descriptor, затем разрешает только текущее состояние.
Собственная первая проверка слишком рано требовала кадр11 и останавливала
обычный Init. Исправлен порядок: normal9/10 разрешается сразу, ссылка pressed11
сохраняется. Другой кадр не подставляется. Полная pressed/error ветвь остаётся
непринятой. Common equipment action1 имеет14 изображений, admitted локализованные
наборы —15; использовать случайный ресурс другой локали нельзя.

Public equipment GetItem возвращает null для пустого владельца. Первое ожидание
стенда ошибочно требовало ненулевой указатель; оно исправлено по675270.
Проверка16 реальных владельцев выполняется отдельно через собственный array,
поведение getter не менялось ради теста. После single-mode закрытая вторая
сумка допустима; дополнительно проверен target return1 скрытого Draw.

## Проверки

Own SHA-256 `96afbd6224f01bfc3d7427061a8471429e3e107e6c6b98968868fa3e2f6945cc`,
x86/VS2026,entry RVA182C50,2364928bytes.182client/67engine/20kernels,
build/link0,unresolved0. Consumers/entry/startup audit/earlyTaiwan проходят.

Native final `work/m9/459bd43c/inventory-001`: PASS, четыре PNG800×600,
три расы на настоящем Taiwan profile. Проверены размеры, владельцы, цвета,
signed64 money, две сумки, режим одной, close/open, masks, reload и шесть
маршрутов событий:3GUI переключения и3настоящих help HWND messages.
Все четыре PNG побайтно совпали с уже просмотренными1b222819; финальная
проверка равенства выполнена. Компонент использует собственный offscreen RT,
производственный рендерер не модернизировался.

На reload видны сброшенные маски и естественная высота pack skin395 вместо
размера176, заданного Init. Последующие обновления данных/восстановление состояний
не проверены как полный lifecycle. Кадры показывают контрольные пустые владельцы
и выбранные маски, а не инвентарь с настоящими полученными предметами.
Staging32assets/16010369linkedbytes/0newpoolbytes; полный клиент не клонировался.
Before166:179файлов,7344900 частных bytes+4005559bytes общих с прежним
неизменяемым snapshot. Preserver теперь также сохраняет прямые script/helpers
самого checkpoint; входные ассеты и трассы в snapshot не копируются.

Final live `work/m9/96afbd62/selection-live-taiwan001`:auth/list,
tx1/14/1 → rx1/15/22/result0, просмотренный preEnter кадр.
Inventory Init вернулся; также пройден следующий Linker Init в исходном порядке.
Далее E06D7363 поднят KernelBase.dll, system RVA140B82 — **это не own RVA**.
Own causal candidate28A61 принадлежит RF455_RejectRemovedLegacyBelt.
Проверен direct call26BFD=`E83E1E0000`,return26C02→guard28A40.
Own Inventory vtable1F099C/slot6C→Init89A70; прежний Create_UI call вернулся
раньше guard на последовательном пути. Это corroborated candidate scan,
не stack unwind. Отдельный inspector теперь помечает code/data candidates
и сохраняет точный SHA/architecture собственной PE.

## Готовность и остаток

Учёт:2461(+42 относительно164) адресных функций,651(+45) с полным ASM/CFG
из37871.25 новых выборочных partial bindings,24 с отдельными символами PE;
в девяти последних реестрах137. Это не общий итог восстановленных функций
и не измеренный процент функциональной готовности.
Ориентир25%(20–35%) прежний; полных областей принято0/12, M6/M6F/M7/M9 OPEN.

Открыты полные item receivers/actions/trade/use/equip/pick/tooltip/ready cues,
settings serialization677DD0, highlight3325/3326, дополнительные поля/массивы
455 и полный lifecycle. В UI16 equipment slots, в старом board backend15:
правильное455 соответствие и producer ещё нужны. Setter basefield+332=1
equipment Init пока не имеет восстановленной семантики. Также открыты полный
mouse mask/hittest, pressed11/error domains, locale completeness и прежние
actor/Animus/world/gameplay gaps. Legacy RemovePack и другие не перенесённые
методы не выдаются за эквивалентное455 поведение.

Очередь166: восстановить настоящую455 MainGame/board factory и порядок создания.
Согласно исследованию085 прежний отдельный potion-belt storage отсутствует;
это **не отменяет обязательные для M9 potion/hotbar возможности**. Не возвращать
старый wire storage и не обходить guard. Нужно подключить реальные клиентские
владельцы и связи455, затем продолжать к карте/avatar/control.
Сервер и оригиналы не изменялись, входные EXE не выполнялись, private handoff
удалён. Все native jobs завершены; подробные доказательства в inventory/ и artifacts/.
