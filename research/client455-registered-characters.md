# 140: список персонажей 455 и настоящие Avatar

2026-11-10. **PARTIAL, M6 открыт.**
Gate: `inventory/client455-registered-characters-checkpoint.json`.
Проверить: `scripts/Invoke-Python.ps1 scripts/checkpoint_client455_registered_characters.py`.
Восстановлены два сообщения и применение записей. Полные загрузка таблиц,
классы, внешний вид и экран выбора ещё не приняты.

## Эталон и доказательства

Обе закреплённые x86 PE имеют base `0x400000`:

- primary SHA-256 `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
- secondary `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.

Собраны полные инструкции и все положительные блоки CFG девяти функций:
623 инструкции / 72 блока. Диапазоны функций совпали в обеих PE.

| RVA | Роль |
|---|---|
| `0x16add0` | Запрос списка |
| `0x16ae40` | Ответ и заполнение Avatar |
| `0x16b490` | Конструктор ответа |
| `0x16b4d0` | Конструктор записи |
| `0x16b4f0` | Инициализация записи |
| `0x16b550` | Инициализация экипировки |
| `0x1c380` | Gold setter |
| `0x1c3d0` | Dalant setter |
| `0x12140` | Class setter; перенос всех его потребителей ещё открыт |

Сверены массив частей `1,2,3,4,5,7,6,8` по RVA `0x6b2e10` и вызов
receiver из core dispatcher по RVA `0x163091`.
Raw: `artifacts/client455-progress/registered140-reference/session.json`.
Отчёт: `inventory/client455-registered-characters-reference.json`.
IDA `2a850a2f` сохранена/закрыта, список сессий пуст. Входные EXE не запускались.

## Восстановленный контракт

Запрос group1/op8, payload пустой. Ответ group1/op9, payload **506 байт**:
result@0, count@1, 12 reserved bytes, три записи по **164 байта**.
Чтение всех трёх записей сохраняется и при count0.

| Смещение внутри записи | Поле |
|---|---|
| 0 | Имя: 17 wire bytes, локально добавляется ограниченный нулевой терминатор |
| 17 | Serial DWORD; имя не занимает 21 байт |
| 21 / 22 | Race / slot |
| 23 / 28 | Class code 5 bytes / level |
| 29 / 37 | Dalant / gold, signed64 |
| 45 | Base shape DWORD |
| 49 / 65 | Equipment 8×signed16 / upgrade 8 bytes |
| 73 | Reserved 83 bytes |
| 156 | Last connection signed64 |

Bounded dispatcher отвергает null, payload короче506 и count>3 до мутации.
Это явное ограничение безопасного декодера; не доказательство поведения target
при повреждённом count. Slot>2 пропускается; повторные slot применяются по порядку.
Level0 превращается в1 и записывает skipTutorial0, прочие уровни — skipTutorial1.
Сохраняются 64-битные деньги/время, default parts, 8 equipment keys, face/hair,
action `0x10000000`, light `0xff808080`.
Выбор последнего slot использует локальный signed64 max0 и строгое сравнение;
count0 не очищает прежние Avatar и выбранный slot.

Обычный incoming1/9 подключён к новому decoder/receiver, а не только к probe.
Source header ответа содержит506 opaque wire bytes, разбор вынесен в отдельный
типизированный компонент. Общий legacy/server CharacterDB не изменялся.
Полная эквивалентность class-tier/appearance/resource/item callbacks не заявляется.

## Исполнение собственной сборки

Account probe: `work/m9/3cd21e07/account-001`.
Реальный AES/кольцевой буфер с разрывом пакета и переходом через конец буфера
передаёт ответ обычному receiver. Проверены три настоящих Avatar: имена, включая
CP949, race/index/level, деньги >32 бит, tutorial flag и последний slot.
Времена специально выбирают slot0 при64-битном сравнении; сравнение младших
32 бит выбрало бы другой slot. Проверены короткие/null/count4/invalid slot/count0.
Это искусственные входные байты, не реальная авторизованная сессия.

Первая попытка остановилась на отсутствии Character shaders в папке probe.
Добавлен staging настоящих шейдеров через общий pool; production инициализация
не отключалась. Итоговый component PASS, ресурсы освобождены.
27 staged assets, новые pool bytes0; установленный клиент не клонировался.

Own RF_Online.bin SHA-256
`a3002fc48427f09cb1cb7c2f57c95696162d1099ce7714e890f1053d1c321607`,
x86/base400000/entry1703F0, 2271744 bytes. 182 client / 20 kernels,
build/link0, unresolved0. Engine137 SHA `708c892e60c3bf7457389b40ac24b9a466958c9d232d9efaf497d1ac3232b870`
не менялся. Широкие неизменённые старые suites не повторялись.

Свежий обычный WinMain→Title→Login: `work/m9/a3002fc4/login-frame001`,
created1/loaded1, frame70/3203ms,640×500, Renderreturn/ownexit observed, no fatal.
PNG `8ed172376020b2512ffec06a09ff174a07809d5fad9e43ac10b5aa9108bfe289`
просмотрен: lobby/окно ожидания, лишних открытых панелей нет. Экран выбора не показан.
Предыдущий139 сохранён: `artifacts/client455-progress/before140/manifest.json`,49files.

## Следующий функциональный стык

При result0/state6 Login вызывает bootstrap RVA `0x1e7be0`.
Его diagnostic pseudocode сохранён в raw; полное ASM/сверка и перенос ещё нужны.
Порядок: ItemCash→ItemSetEffect→Item→Resource→PlayerCharacter/SkillForce/Store/
Character/boards→Quest→EventShip→NDMsgMonster→ItemTimer→country slot296→
NDMsgEvent→EventSound→SpecialStore→ItemCollection→Map→5default effects→
Avatar finalization→registered-character request.
Вызов country slot296 загружает ItemPremium через RVA `0x204530`.
ItemTimer и SpecialStore не подменять
догадками об Exp/Combine. Варианты cash/NPC/quest должны использовать selectors139.
Затем нужны настоящие таблицы, классы/внешний вид и обычный экран выбора.

Общая плановая оценка остаётся25% (20–35%): локальный packet/actor стык
не закрывает целую систему. M6/M6F/M7/M9 OPEN; серверные файлы не изменялись.
