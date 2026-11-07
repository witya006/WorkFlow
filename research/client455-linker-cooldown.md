# Перезарядки и игровые обработчики панели — работа099

Дополнение: выбранная ready-animation/cache часть перенесена и проверена в
[ready-cooldown099](client455-ready-cooldown.md). Текущий runtime gate —
inventory/client455-ready-cooldown-checkpoint.json. Ниже сохранён исторический
статический аудит;его STATIC_ONLY_NOT_IMPLEMENTED manifest не переименован в
runtime proof. Очередь actualhandlers/livecallbacks/fullAdd/bootstrap остаётся.

2026-11-07. Статический аудит перед переносом; код production пока остаётся098.
M6/M6F/M7/M9 OPEN. Нельзя считать этот документ реализацией перезарядок или
приёмкой Linker. Текущий runtime gate — client455-gui-timer-checkpoint.json.

## Что установлено

Оба закреплённых клиента x86,base0x400000. Current SHA-256
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`,
reference-backup SHA-256
`46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
Функции, assembly, vtable entries и внешние instruction windows сохраняются
в ignored artifacts/client455-progress/linker-cooldown099-reference.json;
хеши и актуальная область проверки — inventory/client455-linker-cooldown-reference.json.
79 canonical functions/5906 instructions,82 равных диапазона обеих455,
20class-specific virtual entries. Дополнительные predicates/list helpers —
linker-cooldown099-extra.json. IDA31e85147 сохранена/закрыта,list0;
session evidence linker-cooldown099-session.json.
Исходные EXE не исполняются, серверные файлы не меняются.

| RVA | Установленный контракт |
|---|---|
| 0x101c30 | Регистрация перезарядок и запуск таймеров исходного владельца |
| 0x101750 | FrameMove: истечение записей, постановка/снятие сигнала готовности |
| 0x1019e0 | Проверка присутствия bank row в списке детей корневого окна |
| 0x1007e0 | Удаление копии: очистка object/start в соответствующих записях |
| 0x102190 / 0x102330 | Разные маршруты поиска исходного/равного объекта |
| 0x101a20 | Настоящий MsgProc сraw455 message codes |
| 0x21af30 / 0x21b240 | Настройка и центрирование ready-animation child |
| 0x228bd0 / 0x228ae0 | Update анимации и установка frame/stopped |
| 0x4c6f40 | Blend mode3: SRCALPHA/ONE |

В CLinkBoard есть50 записей по20байт:BYTE bank,4-byte wrapper pointer,start,
offset,duration. Padding и незаписанный bank в конструкторе не считать нулевыми
без доказательства. Для занятой записи повторный запуск не переписывает её.
После совпадения каждая свободная ячейка отдельно читает timeGetTime.
Elapsed offset-1 превращается в0, прочие значения хранятся rawDWORD.

Admission проверяет root-window membership bank row или текущий active bank.
Это не IsShow и не один pin flag. Проверка5019E0 создаёт адрес
window+0x150+bank*0x3bc8 и передаёт его CGUIContainer membership search60C680.
Сопоставление предмета использует virtual kind/code, затем wrapper index
против serial исходного CItem+4. Это отдельные условия, а не только равенство
указателей/GUIItem atlas ID. Raw global gate114A070 по умолчанию0; если gate
ненулевой и input kind1, пропускается вся функция. Более широкое игровое
значение gate пока не названо.

FrameMove использует DWORD(now-start)+offset сunsigned wrap и сравнивает
elapsed>=duration. Запись истекает и очищается независимо от текущего
присутствия банка. Сигнал готовности добавляется только для присутствующего
или active банка. Удаление wrapper обнуляет pointer/start, сохраняя прочие
поля; истечение делает memset20. Pending-animation list имеет собственный
цикл удаления:erase502C50 возвращает уже продвинутый iterator,затем outerloop
5018F8 снова делает increment. Поэтому соседний stopped cue может остаться
до следующего frame. Не заменять это обычным erase-without-increment loop.
End/sentinel/unsafe/OOM/concurrency domains остаются открытыми.

Поиск исходного владельца502190 для physical kind0 проверяет boards1,0,5,
а502330 — только1,0. SF использует3/7,Animus4,kind6 board22,Macro7 board35.
Это реальные455 board contracts, не разрешение восстанавливать серверы.
В0.7 CObjectBoard.UI_UseRequest(bank,slot) nonvirtual. У targetCLinkBoard реальный
bank/slot handler500F80 присутствует вvtable. Нельзя назначать имена старых
protectedhooks новым методам только по offset: структуры этих API различаются.

## Найденная обязательная зависимость

После окончания радиального таймера455 добавляет отдельный ready child,
CGUIItem+1040, в список детей окна. Это не постоянная часть CGUIItem.Draw.
Он использует atlas1/action13/frame0:один лист1024×640 стекстурой1024×1024,
8×5 клеток128×128,FPS34,one-shot,initial stopped,blend3. Его координаты:
iconOrigin+(iconSize-128)/2 соsigned integer division.

Следовательно,UV высоты клетки —128/1024, не1/5. Нельзя перепутать40 ячеек
одного изображения с40 frame entries SPR action. На конце animation Update
фиксирует последний кадр и stopped, затем FrameMove убирает child из окна.
Update берёт восстановленный loopSeconds, а не произвольный wall-clock delta;
paused route имеет строгое elapsed>interval. Assembly и source0.7 показывают
разное поведение старого CGUIObjectAni:просто подставить его нельзя.

У существующего legacy CSprite.DrawSpriteUV нет параметра blend3. Он использует
SRCALPHA/INVSRCALPHA, тогда как target3 требует SRCALPHA/ONE. Подстановка
старого Draw с тем же изображением изменила бы поведение. Для переноса нужен
согласованный source API/overlay, позволяющий готовому target sprite owner
передать свою texture в выбранный mode3 route. Не читать private target ABI
через pointer casts и не вызывать адреса из EXE.

## Следующая работа

1. Восстановить source-owned GUI animation/ready child, его frame/UV/stop/update
   и mode3 draw, подключить к обычному GUIItem и окну. Проверить реальные128px
   клетки,финальный кадр/скрытие/центрирование/состояния D3D.
2. Подключить50 cooldown records к CLinkBoard.BeginDelayAnimation/FrameMove/
   Remove и настоящий поиск исходного владельца. Сохранить raw gate и порядок
   clock calls; проверить current/attached/hidden банки и удаление.
3. Перенести actualuse/remove/swap/hoverhandlers из выбранной vtable/MsgProc,
   liveSF/Animuscallbacks/lock,Macro35/Vending27/fullCItemBoard.Add/bootstrap.
   Все прежние клиентские gaps и критерии client-acceptance.md сохраняются.

Новая сборка/GPU acceptance для099 пока отсутствуют. Production098 не менялась;
её проверки не повторяются без нового изменения. Общий процент не измерен.
