# Владельцы предметов и иконок Linker — 096

2026-11-07. M6 PARTIAL; M6/M6F/M7/M9 OPEN.
Current gate: `inventory/client455-linker-owners-checkpoint.json`.
Только клиент; серверные файлы и originals не изменялись, входные EXE не исполнялись.

## Подтверждённый результат

Обычные CLinkBoard.Add/Remove/Clear теперь вызывают перенесённое typed владение.
Add создаёт отдельный CBoardObject clone с общей payload reference, копирует
иконку в банк реального владельца окна, связывает её с clone и регистрирует095.
Remove сначала удаляет регистрацию, очищает иконку локально, затем удаляет clone.
Занятая ячейка отклоняет Add и освобождает попытку клонирования, как выбранный
target path. Оригинальный wrapper и оригинальная иконка не становятся членами
реестра копий автоматически.

RF455LinkerIconSlots — реальное поле существующего m_uiLinkWindow,50 CGUIItem
для5 банков×10 ячеек. Оно не заменяет полный CGUILinkWindow: его Init, layout,
screen scaling, bank buttons, input, overlays и bank selection ещё не подключены.
Обычный legacy draw всё ещё использует8 старых ячеек. Просмотренные кадры096
рисуют выбранные настоящие bound icons напрямую в тестовых позициях; это не
скриншоты полного игрового окна. takeIn реализован для constructor scale1,
размер38×38. При дальнейшем переносе нужен настоящий scale=min(width/1024,1).

Перенесены `scripts/native/client455_linker_owners.{h,cpp}` и
`scripts/client455_linker_owners_port.py`; hooks воспроизводятся prepare script.
Typed paths живут в canonical production facade. Untyped borrowed legacy path
сохранён до согласованной миграции payload-kind/mixed-derived callers.

## Бинарная опора

Оба pins x86, image base0x400000:

| Вход | SHA-256 |
|---|---|
| current | b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b |
| reference-backup | 46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558 |

21 выбранный диапазон равен на обоих pins;1105 asm instructions, включая EH
tails. Полная raw выгрузка: ignored
`artifacts/client455-progress/linker-owners096-reference.json`.
Малый манифест: `inventory/client455-linker-owners-reference.json`.
IDA sessionbb7e4b5e savedclosed;после закрытия list count0.

| RVA | Контракт |
|---|---|
| 0x100570 | Add_ProcessExist всегда false |
| 0x100590 | source ref detach,virtual clone,pack Add,icon bind/register |
| 0x1007e0 | unregister,50 cooldown records cleanup,icon empty,pack delete |
| 0xfa210 | общий Add требует object и payload,проверяет bank,вызывает virtual paths |
| 0xf9940 / 0xf99a0 | pack stores owner / deletes owner |
| 0x268a90 | TakeIn:5×10/null check,SetData,38×scale,refnull |
| 0x268bd0 / 0x267440 | TakeOut / прямой адрес bank-slot icon |
| 0x6b720 / 0x21bdc0 | очистка source icon reference |
| 0x6ee40 | icon context BYTE1360 |
| 0x6b920 / 0x6b970 | physical grade и его обновление |
| 0x64360 / 0x648b0 | SF/Animus callbacks только при ненулевом source-board pointer |
| 0x21aa10 / 0x21bb80 | full target copy/empty;перенесены только выбранные поля |
| 0x100220 | target destruction order;полный shutdown ещё не принят |

Asm подтверждает bank addressing `packs+16*bank`: decompiler500590 скрывает этот
ECX argument. Сравнение только псевдокода здесь было бы недостаточным.

## Проверка и границы

Own-entry с настоящими normal objects и facade проверяет:

- Actual EDF-backed physical item + actual CGUIInventoryBoard original;50
  distinct CBoardObject clones и50 icon owners через настоящий CLinkBoard.Add.
- Payload reference count51, source ref detach, context2,index,38×38,refnull;
  occupied slot releases attempted clone;валидные bounds5×10. До Add всем50
  ячейкам задаются разные позиции;копирование сохраняет позицию получателя
  и совмещает с ней рамку,как завершающий SetPos в target61AA10.
- Original quantity/usable updates доходят до всех50 копий. Обновление из копии
  не меняет незарегистрированный оригинал. Remove4/9 unregisters и сбрасывает
  только удаляемую иконку: index/itemIDFFFFFFFF,quantity1,grade-frame color0.
- Удаление оригинального inventory owner оставляет49 живых копий. Обычный Clear
  удаляет все регистрации и последний payload. Отдельно проверен scoped destructor.
- Три fresh-null source-board callback cases:0/1/2. Иконки этих CPU cases имеют
  явно synthetic metadata. Animus permissive factory2 получает реальную physical
  table1/row3848, как допускает проверенный089 factory;это не доказательство
  канонических Animus data/window contracts. SF использует реальный factory1/1/0.
- Четыре явных отказа без оставшихся clones/registrations: flag21 lock overlay,
  physical classification11 potion cooldown, live SF owner,live Animus owner.
  Эти providers не заменены успешными no-op;они обязательны для полного клиента.
- Три GPU кадра просмотрены: исходный предмет и две реальные копии;серые255
  распространяются на копии;после ordinary Remove последняя иконка исчезает.
  Это selected rendering, не fullwindow/reference executable capture.
- Все payload owners освобождены, Dmalloc balanced;disk inputs неизменны.

При отказах менялись и восстанавливались только копии данных в памяти harness.
Source preflight отказ раньше target side effects — известное ограничение
неперенесённого домена. GetItem invalid bank/slot bounded-null у source, в target
unchecked pointer arithmetic;unsafe domain не принят. Early typed cleanup в
source destructor защищает регистрацию до destruction window;полный target
shutdown order и clearing50 cooldown records ещё не воспроизведены.

С новой facade повторены095 registry и094 metadata probes;все native results
совпали, шесть raw кадров byte-equal предыдущим просмотренным кадрам. Старые
visual reports сохранены и проверяются через baseline provenance096. Прежние
runtime gates не переписываются как текущие. Hotbar7 packets/storage3/account
проходят. Не повторялись unchangedworld/audio/159k/093atlas/092icon/2013owner/
1447SF bulk: новый риск относится к владельцам/UI/startup,они проверены адресно.

Новая обычная PE x86,2113536 bytes,
SHA-256 `613a6e973a94659c767feda5c3a422139d970429ae0e3478623a85932b87520a`,
entry RVA0x153bd0,WinMain0xb7830,afterCreate0xb799a;182client/20kernels/51facade,
0unresolved. AddTypedObject455 RVA0xc6250 и RemoveTypedObject4550xc65a0 живут в
ordinaryPE;register0xc96d0/unregister0xc9810 теперь также retained и используются
actual Linker path. Это устранённое ограничение095.

Exact own PE ранний WinMain/Create return1 прошёл;terminal exception не наблюдался,
first-chance events сохранены. Игровой цикл/authentication этим не проверены.
Engine082 неизменён:
`9caa283a6bf8a2fa1c9a05251b6cad451296bb03bda8a1860c22a872e88fe769`.

## Далее097

Завершить настоящий CGUILinkWindow: Init/scale/layout5×10,bank controls и
selection/MsgProc;включить новые bank icons в ordinary drawing/input. Перенести
остальные SetData/empty child/timer/follower/lock/cooldown states,live SF/Animus
owner callbacks. Macro35 со special-text kind7 и Vending27 обязательны перед
полным CItemBoard.Add notifications;затем normal table bootstrap. Глобальный
wrapper kind и legacy mixed casts переносить согласованно. Все прежние
36boards/Trunk/protocol/Tutorial/QBI/fourstage/Login/auth/game/M6F/M7/M9 gaps
сохраняются. Полное соответствие455 ещё не достигнуто.

Проверка сохранённого результата:

```powershell
.\scripts\Invoke-Python.ps1 scripts/checkpoint_client455_linker_owners.py
```
