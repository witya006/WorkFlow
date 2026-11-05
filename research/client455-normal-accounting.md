# Учёт памяти Character и полная линковка новой ветки

2026-11-06, Asia/Yakutsk. Участок M6 номер041. Реальные cumulative counters
подключены к обычной сборке и её diagnostic consumer. Новая Character/D3D9
source ветка впервые полностью линкуется в RF_Online.bin. Это не приёмка
normal WinMain или полного поведения455; M6/M6F/M7/M9 открыты.

## Эталон и подтверждённые значения

Оба PE x86, image base0x400000. Current SHA-256:
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b.
Backup SHA-256:
46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
Producer/consumer ranges, RVA/длины/SHA и initial image закреплены в
inventory/client455-normal-accounting-reference.json. Raw decompile/xrefs —
ignored artifacts/normal-accounting455. IDA6b33fc0a closed/saved=true.
Входные EXE не исполнялись; серверные файлы не менялись.

| Source поле | Original VA / RVA | Подтверждённый смысл |
|---|---|---|
| m_TextureSize | 0x11895F8 / 0xD895F8 | Cumulative4*width*height при успешном добавлении |
| m_TextureNum | 0x11895FC / 0xD895FC | Количество успешных добавлений текстур |
| m_VertexSize | 0x1189600 / 0xD89600 | Выделенные shared buffer blocks: vertex2300000/index1000000 |
| m_VetexNum | 0x1189604 / 0xD89604 | Количество созданных shared COM buffer blocks |
| m_AniSize | 0x1189608 / 0xD89608 | Raw ANI bytes: RFS_msize, loose file length |
| m_ObjectNum | 0x118960C / 0xD8960C | Количество конструкторов mesh parts |
| m_ObjectSize | 0x1189610 / 0xD89610 | Cumulative mesh bytes,5803 за часть |

Диапазон первых семи DWORD исходно нулевой в loaded PE image обоих эталонов.
Texture producer934A20/RVA534A20, buffer producers93DE00/93DF80/93E100 (RVA
53DE00/53DF80/53E100), mesh ctor9214E0/RVA5214E0, ANI93ACD0/RVA53ACD0.
Diagnostic consumer7F26F1..7F2798/RVA3F26F1 использует те же значения в старом
выводе. Найденные direct xrefs содержат increments/additions в producers;
delete/release их не уменьшают. Это накопленная оценка созданий, а не текущий
физический объём RAM/VRAM. Названия старых public fields сохранены.

Ctor9312E0/RVA5312E0 обнуляет8DWORD, но входящих xrefs в текущей IDB нет.
1189614 также не имеет найденных xrefs. Эти факты не доказывают связь восьмого
слова с CHMEMORYINFO: private32-byte ABI и его последнее поле не придуманы.
Собственный source view содержит только семь подтверждённых значений.

## Подключение к source

Ранее normal Runtime хранил mesh/buffer/ANI counters на renderer, тогда как
эталон использует process globals. Теперь client455_normal_accounting.{h,cpp}
владеет общими группами; настоящий RF455_RendererModelContext и ANI load
получают pointers на них. Создание/удаление renderer не сбрасывает эти группы.
Существующий process-wide TextureManager accounting сохраняет своё владение
и реальные updates; kernel алгоритмы и отдельные старые component archives
этим изменением не переписывались.

RF455_GetCharacterMemoryInfo возвращает актуальный read-only snapshot из этих
источников. Единственный legacy consumer foreffect.cpp теперь получает один
локальный snapshot вместо восьми прямых чтений старого external global.
Преобразование воспроизводится prepare_client455_normal.py на рабочей копии;
исходные bytes/кодировки reference tree сохранены. Это source port API, не
пустая переменная для линкера и не overlay чужого STL/private ABI. Foreffect
object и full MAP подтверждают настоящий вызов и source provider.

## Проверка

CPU native использует реальную ANI70794байта через normal ChInterface и
AnimationManager в двух последовательно созданных renderer. Новая загрузка
увеличивает общий raw counter, cached load не меняет его, destruction сохраняет.
Настоящий AllocateMeshArray→construct→delete проверяет count/bytes и DWORD wrap
на специально заданных начальных counters. После освобождения totals прежние.
Поля snapshot сопоставляются с настоящими источниками; test-only seeding не
является production reset API.

GPU native загружает реальные BN/MESH08/ANI через обычные CUnity/renderer.
Количество частей сверяется с mesh constructor counter, buffers — с nonnull
реальными pools и штатными block sizes, texture bytes/count — с actual texture
entries и GetLevelDesc, ANI — с loose file length. После effects/shadow:

| Счётчик | Результат |
|---|---|
| Mesh parts / bytes | 107 /620921 |
| Shared buffer blocks / bytes | 2 /3300000 |
| Textures / estimated bytes | 4 /4194304, включая EFF texture |
| Raw ANI bytes | 43298 |

После model/animation/renderer release значения сохраняются; следующий пустой
renderer их не обнуляет. Все COM refs и Dmalloc освобождены. Старые два цветных,
effect и shadow кадры совпали с предыдущими. Первый вариант теста ошибочно
сравнивал количество текстур с nextId, который начинается1; ожидание исправлено
на actual entries/descriptors без изменения production counters.

Evidence: inventory/client455-normal-accounting-native.json,
client455-normal-renderer-gpu.json (accounting artifact с SHA),
client455-normal-accounting-checkpoint.json. Short ANI/BBX/model/effect/table/
clock/shadow регрессии прошли на новых библиотеках. Большие неизменённые suites
не повторялись.

## Результат полной линковки

182client +11facade +20canonical kernel CPP собираются x86/MT. Полный normal
link завершился0, missing symbols0, других ошибок нет. CharacterMR и /FORCE
не используются. Проверены PE32 x86, реальный MAP и точный linker response.

`work/client455-port/normal/build/RF_Online.bin`:1966080байт,
base0x400000, entry RVA0x149500, SHA-256:
39062b2cbf18f5680fd1d59c3d73c22c020770c30e99c9107302cf6678a53a05.
Авторитетные текущие metadata — inventory/client455-normal-link.json.

Общий validator client455_normal_link_evidence.py проверяет успешный PE/MAP/
response/log/build hashes и отделяет успех линковки от приёмки runtime.
Предыдущие scoped checkpoints теперь отражают link PASS, сохраняя общий PARTIAL
и все границы соответствия455. Это первый полный normal source link после
совместного Character/D3D9 port; прежняя M4 diagnostic base остаётся отдельной.

## Продолжение и ограничения

Не приняты original asynchronous races, точное форматирование diagnostic text,
allocator extent/failure policy и private eighth field. Counter tests не
доказывают весь draw/actor/gameplay lifecycle. Полные particles, shadow/HRESULT
callers, blend producers, static CRT, normal device reset/UI/network/gameplay
остаются открытыми. Normal WinMain ещё не выполнялся.

Следующий042 — preflight imports/delayed DLL/CRT/global construction/WinMain
и изолированный offline startup lab с нужными клиентскими ресурсами. Normal
WinMain вызывает engine, затем Miles sound, D3D init, Create и ABuse/Adv
filters. Перед запуском собственного output подтвердить runtime contracts и
конфигурацию; оригинальную установку и входные EXE не использовать как runtime
workingdir. В PE нет.rsrc; обнаружен engine RC с иконкой, обязательность
встраивания проверяется по реальным callers.

Повтор через scripts/Invoke-Python.ps1: audit_client455_normal_accounting.py,
prepare_client455_normal.py, build_client455_normal.py,
probe_client455_normal_consumers.py, probe_client455_normal_accounting.py,
probe_client455_normal_renderer.py, link_client455_normal.py,
checkpoint_client455_normal_accounting.py. Остальные короткие проверки —
когда меняются их зависимости или выявлен конкретный риск.
