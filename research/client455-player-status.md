# Статус персонажа и условие отмены hover — работа102

2026-11-07. PARTIAL. В обычном CPlayer восстановлены отдельный DWORD статуса,
его getter/setter и подтверждённая часть производителя из 64-битных флагов.
Обычный ненулевой CAvatar теперь проходит фактические SetHover/clear/screen и
ReturnHover в Linker. Полная отмена ядерного прицеливания, остальные эффекты
статуса и его сетевые получатели455 ещё не восстановлены. M6/M6F/M7/M9 OPEN.

Текущая проверка: `scripts/Invoke-Python.ps1 scripts/checkpoint_client455_player_status.py`.
Gate101 стал историческим после изменения source/header/link. Его статические
доказательства и сохранённые кадры остаются; прежние32 других GUI кадра в102
не запускались повторно. Свежие6 hover кадров просмотрены и побайтно равны101.

## Подтверждённые факты

Оба455 x86, image base0x400000. Основной SHA-256:
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
второй:
`46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.

Native IDA MCP:17 полных функций/2036 инструкций/17 равных диапазонов обоих
файлов, плюс отдельный равный диапазон диагностической функции159bytes.
RVA: getter0x1e290, comparison0x44850, setter0x4f090,
flags producer0x4dee0, CPlayer constructor0x4a750,
predicate0x12b810, conversion0x12b870, owning constructor0x12ad70,
aiming constructor0x12aaf0, cancel0x12ab50, setter0x12ac00,
effect/sound branch0x12ac40, frame0x12ab90, position0x12ad20,
network wrappers0x1c5910/0x1c5ab0/0x1c5b10.
Diagnostic0x12a890 содержит `Not Nuclear Posion`. RVA/size/SHA каждого
диапазона записаны в `inventory/client455-player-status-reference.json`.
Raw decompilation/assembly и exploration находятся в ignored artifacts.
Owned session100f46bb saved/closed; последующий idb_list вернул0.

Поле CPlayer+17708/0x452c — DWORD. Predicate52B810 возвращаетfalse при null
Avatar, иначе сравнивает его младший BYTE с2/6/10. Это отдельное поле,
а не старый m_byAttackMode или CombatState.

Производитель44DEE0 получает64-битные флаги. Приоритет:

1. bit16 →10.
2. Иначе bit17: первый установленный bit33..40 →2..9. Если ни одного нет,
   сохраняется старое значение, в том числе неизвестное до первого setter.
3. Иначе bit42 →1.
4. Иначе0.

CPlayer constructor44A750 не инициализирует этот DWORD. Собственная реализация
хранит known/code и явно отказывает чтению до первого производителя. Она не
выдаёт придуманное начальное0 за поведение455. Target unsafe/uninitialized
домен этим не принят. Прямой setter сохраняет все32 бита; predicate берёт BYTE.

У global1028AC8 есть inline owner+12: constructor52AAF0 обнуляет effect handle,
pending и три координаты. Cancel52AB50 сначала обнуляет координаты, вызывает
52AC40(0), затем сбрасывает pending. В зависимости от handle вызываются
7D9730(handle,0) и8BD590(277034,1). При начале52AC40(1) используются world cursor,
effect1358041136, sound277034 и запись3 в global1157CEC. Frame52AB90 обновляет
позицию через7D91A0. Hover4FE020 после отмены выводит локализованное сообщениеC1A.
Эти зависимости пока исследованы статически, не заменены успешными заглушками.

Интерпретация цепочки как ядерного прицеливания следует из связанного
контейнера/сетевых обёрток и диагностической функции. Читаемые названия
статусов2/6/10 и точное исходное имя класса ещё неизвестны. Полная семантика
effect/audio API требует отдельной проверки перед переносом владельца.

## Реализация и проверка

`scripts/native/client455_player_status.h` содержит небольшой общий core.
`client455_player_status_port.py` добавляет его в собственный CPlayer header,
API и вызов из обычного SetServerStatusFlag. Сигнатура последнего расширена
до ULONGLONG; прежние DWORD callers компилируются, но их старые структуры
не считаются восстановленными64-битными сетевыми контрактами455. Остальные
побочные действия старого setter сохранены и не приняты как455.

`client455_board_hover.cpp` читает фактический Avatar через новый getter.
False predicate допускает старый подтверждённый hover path. True predicate
явно отказывает до изменения hover: pending/effect/sound/message owner ещё
предстоит восстановить. В том числе не принят true predicate/pending0,
поскольку настоящее состояние владельца пока отсутствует.

Native status probe:58 проверок,8 подтипов,12 DWORD/lowBYTE случаев,
приоритет/сохранение старого значения/unknown refusal, настоящий CAvatar,
обычный SetServerStatusFlag сbit40, фактический CPU hover/screen с bare wrapper,
отказ ядерной ветки без изменения предмета. Сетевой владелец инициализирован
штатным Create/Destroy, без подключения/аутентификации. Первый пробный запуск
без этого владельца упал в legacy SetTextColor, ownRVA34bac; исправлена
инициализация стенда, производственный код ради обхода AV не менялся.

GPU hover probe использует настоящую EDF иконку, фактический Avatar со
статусом0, actual manager/screen/Linker и прежнюю матрицу5 payload kinds.
Nonphysical CPU icons остаются synthetic, Quest names явно отказывают.
6 кадров просмотрены; они побайтно равны сохранённым101. Владельцы,
registry и sprite allocations освобождаются. Большие неизменённые suites,
включая159k/world/audio/atlas/SF, повторно не запускались.

Новая собственная PE:
`5f1f0f770f9dd395bb31ea8044b72ae9eb53b40ece8481cfc39b366674030df1`,
2144768bytes/x86/base400000/entry1587b0/WinMainb7a30/afterCreateb7b9a;
182client/20kernels/57facade/0unresolved. Точная PE прошла прежний Create→1
в офлайн launcher/TCP fixture, остановлена до game loop. Account/hotbar7/
storage3 и normal consumers проходят. Это не полная приёмка bootstrap455.
Engine546a7529…/67objects не менялся,033baseline сохранён. Старый082derived
library snapshot по-прежнему отсутствует; исторические EXE/кадры сохранены.
Original/server без изменений, входные EXE не исполнялись.

## Следующая зависимость103

Восстановить фактический aiming owner: pending/set/clear/position/frame,
подтвердить effect7D9730/7D91A0/7E22F0 и audio8BEE60/8BD590, связать его с
обычным клиентским владельцем и сообщениемC1A. Затем перенести64-битные
получатели флагов и оставшиеся44DEE0 effects; actual Linker handlers и queue,
typed network callers, inventory/equip/SF/Animus/potion cache, Macro/Vending/
fullAdd/bootstrap, Quest и все прежние клиентские gaps остаются обязательными.
