# Tutorial059: Move, Creation и Position

2026-11-06. Только клиент. Восстановлены правила QBI6–18 поверх диспетчера058;
проверка использует recording spatial host. Реальный мир/Avatar/backend,
остальные28 селекторов и полный Tutorial ещё открыты. Обычная PE не менялась.

455 x86/base400000 SHA-256
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
backup `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
32 function ranges, таблица категорий47байт, начальные счётчики и константы
совпали между pins. Семь функций сохранены с полными инструкциями.
IDA c60c1913/5b89854f/7dedc5cb/cfea0c20 сохранены и закрыты. Входные EXE не запускались.

| RVA | Контракт |
|---|---|
| 27C10/27F00 | Position Start/Update, включая pending default17 |
| 28290/28570/28620 | Move Start/Update/Finish |
| 27F90/28200/28270 | Creation Start/Update/Finish |
| 4B4CA0 | Расстояние по X/Z; Y игнорируется |
| 165410/165A90 | Локальные клиентские получатели monster/item spawn |
| 6A9C44 | Карта47 категорий;38–46 имеют нулевые значения |
| 7CB758/7CB75C | Начальные item WORD3840 и monster DWORD65535 |

## Правила

Position12 устанавливает Avatar position с аргументами1/0;13 передаёт второй
float в поворот Avatar с1/12.0;14 задаёт camera orbit и dirty flag. Эти команды
выставляют bit4 и завершаются без Update.15/16 записывают абсолютные величины
трёх общих cameraRemaining; только15 запрашивает относительное движение камеры.
Они заканчиваются при всех трёх значениях<=1 либо unsigned elapsed>=20000мс.
16 сохраняет cursor button по общему правилу058.17 — подтверждённая default
ветка: Start успешен, Update остаётся false.18 пишет camera float276, при
значении<=0 использует75. Назначение этого поля ещё не принято; не называть FOV.
Orbit включает два угла и дистанцию, не три пространственных угла.

Move6/7 mode0 ставят маркер; только6 создаёт путь через43EEF0/5EE790, вызывает
поворот Avatar к цели через vt84/7CE550 с1/12.0 и задаёт state10000001. Update проверяет X/Z расстояние<=15 и освобождает
маркер с1.0. В этой ветке нет20секундного timeout. Mode1 запоминает unsigned
distance как float;6 вычисляет цель по sin/cos yaw и DWORD(distance+2), включая
переполнение сложения. Порядок чтений X/yaw/Y/Z/yaw сохранён. Окончание —
remainingDistance<=1 либо elapsed>=20000. Mode2 завершает сразу. Type8 вызывает
Avatar4115B0(mode==1,0) и завершает сразу. Прочие mode остаются pending.

Move и Creation выставляют общий context+0 в1; Finish сбрасывает0. В контекст
добавлены remainingDistance(context+8) и cameraRemaining(+12/16/20). Их изменение
настоящими Frame/Avatar процедурами ещё не подключено; проба управляет этими
входами явно. Это не проверка реального движения персонажа по карте.

Creation9 получает шаблон и формирует17байтовый локальный monster packet.
Creation10 использует временный CItem: constructor → clone lookup → локальный
dispatch → destructor. При неудаче lookup destructor всё равно вызывается;
счётчик ID не расходуется. Обе команды получают bit4 даже при отсутствии
шаблона. Счётчики имеют время жизни процесса, независимо от refresh/clear.
Creation11 ждёт пустого контейнера либо20секунд; его фактический provider открыт.

Преобразование координат повторяет вызов x87 __ftol2_sse и использует AX.
Расстояние повторяет x87 X/Z sum, float spill перед _CIsqrt и float результата.
Direction math сохраняет явные float/double spills и pinned6.283185307/360/12.
CRT error/NaN/FP-mode области сверх проверенных конечных примеров остаются
открытыми; текущие CRT helpers не выданы за доказательство всех numeric domains.

## Пакеты и существенное расхождение

Monster17: WORD localIndex, WORD1, DWORD serial, три WORD координат, нулевые
байты14–16. Item known25: BYTE mappedCategory, WORD localIndex, BYTE1,
WORD serial, FF в полях6–17, три WORD координат18/20/22, FF в24. Таблица всех47
категорий сверена целиком с эталоном. Signed координаты восстанавливаются
клиентскими получателями; их низкие WORD сохраняются, без clamp.

**Item handler565A90 дополнительно читает DWORD по+25** и передаёт в46EB70,
который сохраняет его в item DWORD676. Producer427F90 инициализирует только25
байт, оставляя этот хвост стека неопределённым. Он явно учтён как OPEN.
Новая библиотека передаёт host только подтверждённые25байт, не дописывает нули
или выдуманное значение. Пока хвост и настоящий handler не приняты, creation
rules нельзя считать полной приёмкой создания предмета в455.

## Проверка

MSVC x86 собрал RF455TutorialSpatial.lib
`19d337cb7d599e8f51c1caee31925abbaf587b58072439db57931e825c9c120c`.
Собственная PEdb7706b3..., entry RVA9B30, естественный exit0. Проверены:
позиция/повороты/default75/тип17, X/Z triangle/соседняя граница15/игнорирование Y,
getter order, request-only, wrap distance+2, тайм-ауты и быстрые завершения,
lowWORD координат, точные17/25байт, карта47 категорий, lifecycle временного CItem,
неудачный lookup и переполнение обоих serial counters.

В BW/CW/AR factory создаёт946 из1235 процессоров,289 требуют оставшихся типов.
Это выборка создания объектов процессоров, не полнота исполнения или процент
клиента. Подготовка полного сценария останавливается на первом отсутствующем
селекторе>=19; пропусков нет. Native host не создаёт реальные игровые объекты.

Из-за расширения общего context короткая проба058 повторена и прошла:
актуальная PEa95ef0b2..., entry8050, librarydaab7a98... . Большие неизменённые
клиентские suites не запускались. Production PE по-прежнему56905e68... .
Обнаружение20 канонических kernel sources сохранилось; reports library:string.

Доказательства: inventory/client455-tutorial-spatial-{reference,native,checkpoint}.json.
Raw в artifacts/client455-tutorial/spatial-*.json и059-*-asm.json.
Воспроизведение через scripts/Invoke-Python.ps1: audit_client455_tutorial_spatial.py,
probe_client455_tutorial_spatial.py, checkpoint_client455_tutorial_spatial.py.

Далее060: UI19–22, Equip23–26, затем Cursor27–34/Combat35–39/Item40–46;
CTutorialBoard/briefing и реальный Avatar/world host. Сцена, локальные сообщения,
настоящий Tutorial иjoint fourstage обязательны. M6/M6F/M7/M9 открыты.

Дополнение060: recording host вынесен в тестовый template header, spatial
регрессия повторена без изменения правил. Текущие артефакты:c73ed3fe.../entry9B30,
lib42c67412...; исходные артефакты059 выше исторические.
[Следующий участок](client455-tutorial-actions.md).
