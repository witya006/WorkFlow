# Progress054: четыре этапа455 и источник режима2

2026-11-06. Static reverse клиента; runtime не менялся. M6/M6F/M7/M9 открыты.

455 x86/base400000, SHA-256
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
backup `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
28 function ranges и vtable/COL/type descriptor четырёх классов совпали между
pins. Имена классов проверены по RTTI в самих PE, а не только по IDA labels.
Owned IDA3915694c закрыта/save=true. Входные EXE не запускались.

| Stage ID455 | Класс из RTTI | Constructor RVA | Primary vtable RVA |
|---|---|---|---|
| 0 | CGP_Title | 157B60 | 6B0E14 |
| 1 | CGP_LogIn | 13B860 | 6B0014 |
| 2 | CGP_Tutorial | 1584D0 | 6B0F9C |
| 3 | CGP_MainGame | 1454E0 | 6B0324 |

RVA3D1C30 уничтожает прежний stage и создаёт выбранный. Запрос2 превращается
в3, если Avatar DWORD20168 ненулевой; иначе создаётся настоящий CGP_Tutorial.
Его constructor вызывает CGP_MainGame constructor, затем устанавливает
Tutorial vtables. Это самостоятельный обязательный клиентский режим455.
Более широкая семантика/lifetime DWORD20168 пока не доказаны.

RVA3D1370 после успешного Create stage устанавливает Avatar BYTE20165 равным
текущему stage (setter RVA A6160). Constructor Avatar первоначально пишет0.
Getter RVA1E130 сравнивает это поле с аргументом. Значит ветка2 в login mask
и SendNetMessage относится к **Tutorial**. Прежнее предположение replay не
подтвердилось. Не переносить legacy GPI_MAIN_GAME2 в это условие: в старом
source это основной мир, а в455 основной мир имеет ID3.

RVA162BE0 при существующем Avatar, stage2 и DWORD20168==0 передаёт исходящий
пакет клиентскому Tutorial dispatcher RVA164520. Он обрабатывает группы
1/4/5/7/13/17; большинство остальных сообщений возвращают1 без отправки в
сеть. Специальный group1/op17 идёт в transport. Эти обработчики — часть самого
клиента455, не сервер. Их реализация ещё впереди; нельзя применять эту ветку
к обычному входу и объявлять успешную аутентификацию.

RVA162E80 пропускает login-byte transform при stage2 независимо от DWORD20168.
Packer053 имеет такой explicit аргумент, но runtime Avatar provider пока не
подключён. Требуется совместный перенос Avatar state и четырёх stage classes.

В MainLoop RVA3D1370 следующий stage берётся из DWORD stageObject+20 через
RVA3D1470. Setter RVA13F6B0 задаёт поле явно; Title constructor задаёт1.
Старая собственная база использует `(id+1)%3`, GPI_MAIN_GAME2 и не создаёт
Tutorial. Одной смены константы на3 недостаточно: нужны переходы и Tutorial.
Также normal base MainLoop условно вызывает Render по IsActive, target base
RVA138FF0 вызывает Input/FrameMove/Render без такого аргумента. Полный focus/
render/lifecycle контракт ещё проверять совместно с конкретными stage.

CGP_LogIn vtable связывает LoadData с RVA13F7A0. Там есть старая ветка reconnect
под country slot284. Во всех11 закреплённых профилях этот slot false (052),
поэтому нельзя исполнять её безусловно для исправления argv endpoint0/1.
Полная собственная PE до stage MainLoop пока не принималась.

Поле NetworkMgr436232, использованное053 в pending predicates, имеет setter
RVA2DCA0 и реальные переходы. RVA164470 меняет2→3 или7→8 при установленном
process0/socket0 info flag+48. RVA1643C0 меняет3→4 и вызывает53B430; другие
writers встречаются в login/world/level переходах. Это часть более крупного
автомата, а не произвольная настройка UI. Полный автомат ещё не перенесён.

INI reader VA5F0EB0/RVA1F0EB0 определён в owned IDB по подтверждённым границам
5F0EB0..5F0FD1. Он читает MASTER_SERVER IP/PORT/NAME/TYPE. После определения
функции IDA всё ещё не находит xrefs. Дополнительно по обоим pins проверены
E8/E9 relative candidates в .text и literal absolute address bytes во всём
PE — совпадений0. Computed indirect calls этим не исключены. Следствие:
нет доказанного основания добавлять этот reader в WinMain или считать его
обязательным runtime источником SERVER_TYPE. Сам setter подтверждён в053;
гипотеза обязательного startup вызова снимается с ближайшего плана.

Decompiler INI reader имеет positive-SP warning и неверные import prototypes;
для него используются инструкции. Аналогично часть CGP_LogIn Create имеет
разбитые function boundaries в IDB: не переносить decompiler JUMPOUT как логику.

Изменён только аудит/матрица/план. Рабочая сборка остаётся a12b10f7... из053,
новая пересборка и большие runtime suites не требовались. Reproduce:
`scripts/Invoke-Python.ps1 scripts/audit_client455_progress.py`.
Доказательства: inventory/client455-progress-reference.json; raw в ignored
artifacts/client455-progress/reference.json. Сохранение IDB не меняет PE pin.

Далее055: восстанавливать stage foundation/явный next-stage, Avatar stage и
Tutorial вместе с его клиентскими handlers, затем target Login UI/Create и
world-transition state. Полное обучение включить в обязательную M6F/M9
приёмку. Серверные исходники и логика не изменялись.
