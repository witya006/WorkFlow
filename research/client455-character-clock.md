# Отдельный таймер Character 455

2026-11-06, Asia/Yakutsk. Участок M6 номер040. Восстановлен source таймера
Character и подключён настоящий _R3CalculateTime из mainapp. Это отдельное
состояние времени, которое нельзя заменить повторным вызовом engine clock.
Полный normal link теперь имеет один g_ChMemoryInfo. M6/M6F/M7/M9 открыты.

## Эталон и найденные контракты

Оба PE x86, image base0x400000. Current SHA-256:
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b.
Backup SHA-256:
46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
Точные ranges/RVA/SHA, начальные globals и unsigned correction literal:
inventory/client455-character-clock-reference.json. Raw IDA decompile/disasm
сохранены в ignored artifacts/character-clock455. Owned session a91e5275
closed/saved=true. Входные EXE не исполнялись, серверные файлы не менялись.

| Контракт | VA | RVA | Bytes |
|---|---|---|---|
| Character clock | 0x91EA80 | 0x51EA80 | 0x153 |
| Дубликат, найденных xrefs нет | 0x91EBE0 | 0x51EBE0 | 0x153 |
| Main loop calls engine then Character | 0x7D13A2 | 0x3D13A2 | 10 |
| Frame consumer | 0x924700 | 0x524700 | 0x19E |
| Self-timed frame consumer | 0x9248A0 | 0x5248A0 | 0x1A3 |

В main loop7D1370 сначала вызывается8B3CC0 (engine), затем91EA80 (Character),
затем timeGetTime для другого клиентского timestamp. Совпадение legacy caller
R3CalculateTime/R3CalculateTime_Char подтверждено инструкциями455. Метод
9248A0 тоже вызывает91EA80; дубликат91EBE0 и924700/9248A0 не имеют найденных
входящих xrefs в текущей IDB. Это не доказательство недостижимости через все
возможные динамические вызовы.

Избранные globals исходно нулевые в loaded PE image. initialized1189500,
QPF-result11894F8, elapsedFloat1189504, previousQPC1189508, deltaFloat1189518,
oldTick118951C, samples1189520, window1189524, frequency1189528. Между ними
расположены shader COM pointers1189510/14; source state44B — собственный тип,
его нельзя наложить целиком на этот исходный адресный диапазон.

## Поведение и реализация

Первый вызов ставит initialized до QPF и сохраняет его BOOL. При ненулевом
результате сохраняет signed64 frequency и делает первый QPC для previous.
После этого в том же вызове делает второй QPC. Позже QPF не повторяется,
на кадр один QPC. Исходный BOOL QPC игнорируется; автоматических retry нет.

Сначала происходит целочисленное64-bit вычитание и умножение на1000 с wrap,
затем signed FILD числителя/знаменателя, x87 division и float spill delta.
Elapsed складывается с уже сохранённым float delta и тоже сохраняется float.
Значения в миллисекундах, без engine clamp/scale. EAX исходной функции содержит
lowDWORD произведения; публичный legacy _R3CalculateTime имеет void API.

Fallback получает DWORD timeGetTime, увеличивает samples и window на wrapped
разность now-oldTick. Только при unsigned window>200 вычисляет window/samples
в миллисекундах с исходной uint32→x87 коррекцией, сохраняет delta и обнуляет
samples/window. Иначе delta сохраняется от предыдущего вычисления. OldTick
обновляется всегда. Elapsed на fallback вообще не увеличивается; это
подтверждённая особенность455, которую source сохраняет. Начальный oldTick0
также не заменяется более удобной стартовой инициализацией.

client455_character_clock.{h,cpp} содержит собственный state/core,
client455_normal_clock.cpp — process state и callbacks QPF/QPC/timeGetTime,
реальный C++ _R3CalculateTime и доступ для детерминированного теста. Engine
clock продолжает владеть своим отдельным состоянием в commonutil.cpp.
Новый core собирается тем же modern MSVC x86/MT в normal facade.

## Проверка и границы

Независимый Fraction oracle следует инструкциям: wrap64 до signed FILD,
точные integer loads, промежуточная precision/rounding, float spills и
uint32 bias fallback.168 whole-state cases в12PC/RC modes проходят отдельно
через core и настоящий _R3CalculateTime. Проверены backward/high/wrapped
counters, signed product wrap, ровно200 против201, сохранение предыдущего
delta, unsigned samples/window и неизменность control word.

Provider сценарии проверяют один QPF и два QPC при старте, один QPC позже,
fallback без QPC, точную границу окна и отсутствие elapsed accumulation.
QPC callback с false, но записанным output, подтверждает игнорирование BOOL.
Engine loop time после вызова Character bridge не меняется. MAP подтверждает
RFClient455Facade:client455_normal_clock.obj и client455_character_clock.obj;
actual mainapp.obj содержит тот же вызов, а full link больше не сообщает его
как missing. Верификатор проверяет хеши source/libs/PE/MAP/outputs, SHA эталонов
и настоящий caller. Evidence — inventory/client455-character-clock-native.json
и client455-character-clock-checkpoint.json (PARTIAL).

Полные182client /10facade /20kernel CPP собираются. Full normal link:
g_ChMemoryInfo, других ошибок нет; old CharacterMR и /FORCE не используются.
Короткие реальные ANI/BBX, таблицы/EFF, model/color/shadow сценарии прошли на
новых библиотеках. Прежние цветные кадры совпали, эффект по-прежнему меняет
кадр, COM/Dmalloc0. Большие неизменённые suites не повторялись.

Failed QPF/QPC без записанного output оставляет unspecified stack bytes в
эталоне. Source zero seed не объявляется эквивалентом этой области. Нулевые
частоты/overflow-to-zero fallback divisor, nonfinite values, unmasked FP
exceptions и реальные process timer traces не приняты. Новые frame methods
924700/9248A0 здесь только исследованы/закреплены, а не восстановлены как
достижимые normal APIs. Полный actor lifecycle и normal WinMain/UI/network/
gameplay/device-reset остаются открытыми.

## Следующий участок041: учёт памяти

Подтверждены producers texture11895F8/FC (934A20), buffer1189600/04 (93DE00/
93DF80/93E100), raw ANI1189608 (93ACD0), mesh count/bytes118960C/10 (9214E0).
Debug consumer7F26F1..7F2798 использует эти значения как семь полей старого
заголовка. Они cumulative: release не делает их live heap total.
Отдельный ctor9312E0 обнуляет8DWORD, но найденных xrefs нет; связь последнего
слова с этим global ещё не доказана. Не выдавать guessed32-byte ABI за факт.

В source texture accounting уже process global. Normal Runtime mesh/buffer/
ANI counters пока на renderer: перенести их в правильное общее владение и
подключить g_ChMemoryInfo к реальным producers. Проверить multiple owners,
reload/release и DWORD wrap, затем full link и отдельную normal initialization.

Повтор через scripts/Invoke-Python.ps1: audit_client455_character_clock.py,
prepare_client455_normal.py, build_client455_normal.py,
probe_client455_normal_consumers.py, probe_client455_character_clock.py,
link_client455_normal.py (пока ненулевой exit),
checkpoint_client455_character_clock.py. Затронутые короткие регрессии — по
текущим хешам зависимостей, без повторения неизменённого большого набора.
