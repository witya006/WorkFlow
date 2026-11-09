# Ядерное прицеливание: настоящий сетевой вход и decoder — работа112

Дополнение113: ниже сохранён результат112. Текущий runtime gate —
`inventory/client455-character-flags-checkpoint.json`;111 historical.
Actual Character guard/selected control producers перенесены в113.
UI owner уточнён: три CGUINuclearBomb внутри существующей MiniMap,
а не отдельный dialog. Их source integration и ordinary receiver ещё открыты.
Подробно: [Character flags113](client455-character-flags.md).

2026-11-09. **PARTIAL_COMPONENT**. Восстановлен C++decoder всех девяти входящих
форматов группы60. Исправлена гипотеза предыдущей очереди: начало CE7 вызывается
ответом сетевого обработчика, а не установленным input callback. Ordinary
receiver/guard/UI/owners ещё не перенесены. Runtime gate111 остаётся текущим.
M6/M6F/M7/M9 открыты; конечная цель полного клиента455 не изменена.

Предыдущий goal turn111 — progress:commit c505cfa подключил реальный общий вывод
и живую отмену hover с83 native checks. Текущий112 добавляет новые source files,
проверяемый decoder и45 binary contracts; это не повтор прежнего аудита.

## Эталон и границы доказательств

Оба x86 PE/base400000:

- primary `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
- secondary `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.

45 function bodies совпали; все45 pseudocode complete. Из них22 имеют полные
assembly listings, **903 инструкции**; не называть остальные23 fullasm.
Процессор подтверждён ctor vptr/PE RTTI и Analysis vtable slot+4, а не только
diagnostic string. Пять E8 edges и Character flag initializer декодированы из PE.
IDA sessiona49d0cbc сохранена/закрыта/list0.
Raw:ignored `artifacts/client455-progress/nuclear112-{reference,session}.json`.
Воспроизведение: `scripts/Invoke-Python.ps1 scripts/audit_client455_nuclear_protocol.py`.
Манифест: `inventory/client455-nuclear-protocol-reference.json`.

Все адреса ниже — **RVA** относительно400000.

## Настоящий вход CE7

`RVA1c5ab0` имеет единственную найденную code xref:из1c5910.
Тот вызывается AnalysisServerPacket1c5800 для **group60/opcode0**.
Ctor1c5730 записывает vtable CNetMsgProcessor_Nuclear, ctor factory161000
выделяет8 bytes и сохраняет объект по this+413996. Это private factory slot,
не основание использовать тот же индекс в legacy массиве processors.
Base ctor17ea30 записывает фактический NetworkMgr pointer.

Receiver opcode0 сначала проверяет Avatar predicate:

```text
action DWORD@592 >>28 ==5 OR (internal DWORD@640 &3)!=0
```

При true:Clear aiming→close nuclear UI→localized CE6 независимо от result.
При false:

| Result BYTE | Target действие |
|---|---|
| 0 | Уже восстановленный CE7/request-clear/start helper1c5ab0 |
| 1 | Получить выбранный board payload;если есть,serial WORD→requestflag1→send group60/opcode1/2bytes |
| 2 | При необходимости открыть inventory,затем nuclear UI с преобразованием Avatar status |
| Прочие | Request flag/time clear и localized error;default CF0 |

Error map:3→CE8,4→CE9,5→CEA,6→CEB,7→CEC,8→16C,9→CED,10→CEE,
11→CEF,12→CE6,остальные→CF0. Нельзя молча считать все ненулевые bytes одной
ошибкой:1/2 имеют другие действия.

**Internal DWORD640 не является полем status17708 и не является входными64-bit
server flags.** Character ctor3a060 обнуляет DWORD640;точная запись у3a1ca
проверена как C7/store32 zero. Source GetActionByCategory имеет ту же форму
high-nibble,но legacy Character поля/все writers internalflags ещё требуют
совместного переноса. Не подставлять false/0 только ради прохождения success case.
Для полной guard ветки нужны actual producers и настоящий nuclear UI close.

## Девять входящих форматов

Заголовок внешнего normal dispatcher остаётся4-byte size/group/opcode.
Таблица относится к payload после него. Минимумы следуют из реальных reads,
а не из длины guessed server struct.

| Opcode | Минимум | Используемые bytes |
|---|---:|---|
| 0 | 1 | resultBYTE@0 |
| 3 | 17 | float3@4,indexBYTE@16;первый DWORD handler не использует |
| 4 | 2 | raceBYTE@0,indexBYTE@1 |
| 5 | 5 | raceBYTE@0,indexBYTE@4;bytes1..3 не читать как index |
| 6 | 2 | race/index;SetPending(0) сохраняет имеющийся effect handle |
| 7 | 14 | race/index,float3@2 |
| 8 | 2 | race/index,remove |
| 9 | 2 | Отдельный handler с теми же выбранными reads/действиями,что8 |
| 10 | 1+14×count приcount≤9 | countBYTE,packed rows:race,index,float3 |

При count>9 target opcode10 возвращается,не читая rows. Это не malformed
short-list reject. При count≤9 сначала сбрасываются/удаляются старые records,
затем добавляются новые. Position setter вызывается **только если все три
координаты не0**; не заменять условие на «хотя бы одна не0» при переносе owner.
Конкретные UI/record/FX side effects всех handlers сохранены в raw evidence,
но decoder их не исполняет и не выдаётся за готовый receiver.

## Record и UI зависимости

Map key `(race<<8)|index`, record allocation32:

- DWORD effects@0/4/8 обнулены ctor;
- DWORD@12 ctor не инициализирует;не объявлять его начальный0 доказанным;
- position float3@16 обнулена, DWORD@28 обнулён.

Record radar:effect1358041136/tagged radar277034/tag2,отдельно от aiming tag1.
Launch/impact effects:1358041392/1358041648,угол90 и звуки277036/277038.
При zero position они выводят `Not Nuclear Posion`. Private map ABI,record
frame/lifetime/world render и UI пока не приняты; уже работающий aim core20 не
заменяет этот registry/record32.

UI helper30bf30 при открытии находит record для actual Avatar race и index;
при закрытии удаляет три принадлежащих окну controls через virtual method.
Это реальный UI sink,его нельзя заменить bool или журналом.

## Реализация decoder и проверка

Новые source:

- `scripts/native/client455_nuclear_wire.h/.cpp`;
- `scripts/native/test_client455_nuclear_wire.cpp`.

RF455NuclearWireMessage — own value structure,не overlay packed14/private32.
Читает только подтверждённые поля. На short/null/unknown отказывает без изменения
выходных значений,разрешает неиспользуемый tail. Float bytes копируются без
нормализации,включая−0,quietNaN payload и+Inf. Target unsafe short/null behavior
этим не принимается. Реальных live packet captures в этом этапе нет; native
vectors построены по полным target read contracts.

`scripts/probe_client455_nuclear_wire.py`:VS2026/MSVC x86,/W4/WX;проверены COFF
machine и x86 EXE. Создан `work/recovered/client455/nuclear-wire/RF455NuclearWire.lib`.
Final native run `work/m9/95e80a57/nuclear-wire-001`:**2429 assertions PASS**.
Проверены9 opcodes,все256 result values,все256 list counts,все short prefixes
списков0..9,unknown/null,atomically unchanged output и точные float/packed bytes.
Это один короткий машинный прогон,не2429 запросов к ИИ.

Gate component:

```powershell
.\scripts\Invoke-Python.ps1 scripts/checkpoint_client455_nuclear_wire.py
```

Результат `inventory/client455-nuclear-wire-checkpoint.json` — PARTIAL_COMPONENT.
Нормальный RF_Online.bin/engine не менялись; runtime111 по-прежнему текущий:
PE031df3676c9bed977f660d79fe535666af9cb52cfc4e5b1a61b3f04841df831c,
engine546a7529b51139e856b1a108fcad7849c14b2d00563b7abbfdcc8db10026fa5a.
Нет причин повторять его native/GPU/Create1 suites из-за отдельного decoder.
Ни input EXE,ни серверные файлы не исполнялись/не изменялись.

## Далее113

Перенести actual Nuclear receiver и его ownership в ordinary CNetworkMgr/group60,
используя этот decoder. Совместно восстановить internal Character flag producers/
guard,selected-item serial/request/send mapping и настоящий dialog open/close,
затем record32 registry/остальные opcode effects/list/frame. Не добавлять input
callback вместо подтверждённого сетевого ответа. Сначала проверить существующий
base send endpoint mapping,не угадывать его по group number.

Использовать CE7/C1A core111 и decoder112;не повторять их исследование. Обязательны
все branches0/1/2/error/blocked,реальный normal received-frame путь и actor/UI
providers. До этого normal receiver integration остаётся открытой. Все прежние
M6/M6F/M7/M9 и client-acceptance gaps сохраняются.
