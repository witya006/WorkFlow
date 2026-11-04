# Привязка родителей и костей 455 в исходном коде

2026-11-05, M6. Восстановлены четыре CPU-функции для packed-меша 455:
поиск родителя по имени, привязка массива, повторная привязка и сбор костей
из записей MESH08. Проверены отдельно и в собственном входе полного клиентского
проекта. Полный загрузчик моделей, конструктор меша и Character GPU ещё открыты.

## Основание

Оба закреплённых эталона — x86, image base 0x400000. SHA-256 current:
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
backup: 46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
Четыре тела и 12 ключевых инструкций совпадают в обоих PE.

| Функция | VA / RVA | Подтверждённое поведение |
|---|---|---|
| FindParent(name) | 93BA40 / 53BA40 | С учётом регистра, первое совпадение |
| FindParent(array) | 93BAB0 / 53BAB0 | Первое совпадение на меш, без очистки при отсутствии |
| RematchParent | 93BB70 / 53BB70 | Обрабатывает только меши с ненулевым полем +5495 |
| MESH08 bone resolver | 93CB00 / 53CB00 | Внешний скелет, затем локальные меши; порядок первого появления |

Родитель записывается в +518, флаг наличия в +512; внешняя привязка задаёт +5495=1.
Bone resolver читает 404-байтовые записи: signed DWORD числа влияний и имена
по 100 байт начиная с +4. Неположительное число пропускает имена. Он исключает
повторы найденных имён; каждое отсутствующее имя снова вызывает диагностический путь.
В исходном модуле эти события учитываются в stats, сам debug logger ещё не подключён.

Результат: count в +522, указатели от +526, identity matrices от +646. Порядок
записей важен: сначала matrices, затем копирование указателей. При count>=31
указатели перекрывают первые байты матриц. Исходник сохраняет эти записи;
это не доказательство безопасной capacity50 или окончательного устройства ObjectMesh.
В собственном API предел50 — явно обозначенная политика защиты от unchecked overflow.

## Реальные пары и проверки

Для прежних 12 MESH08 samples найдены одноимённые файлы Bone/*.bn и закреплены
копии/SHA-256. Их plain framing проверен до EOF; из заголовков извлечены имена.
Это подбор входов для проверки алгоритма. Он не устанавливает, как игра выбирает
скелет, и не воспроизводит загрузку его геометрии, матриц или анимации.

Всего 393 меша и 455 записей скелетов. Все влияния разрешаются; отсутствующих
имён нет, максимум четыре уникальные найденные кости на меш. Python формирует
независимый golden с индексами выбранных родителей и костей, C++ использует
реальные 404-byte payloads. Проверяются все 5803 байта результата каждого меша,
включая сохранение незатронутых полей.

2 237 native checks прошли отдельно и в полном клиентском проекте. Дополнительные
fixtures проверяют регистр, дубли/первое совпадение, external/local fallback,
неудачный поиск без сброса старого состояния, rematch gate, signed negative count,
ошибочные записи и неизменность текущего меша/stats при ошибке. Для каждого count
от 0 до 50 проверен полный результат; 20 случаев count31–50 сохраняют перекрытие.
Count51 возвращает собственную ошибку вместо повторения выхода за границы эталона.
Шесть Python tests отдельно проверяют plain-BN fixture-name extraction: все
усечения минимального образца, count/geometry mismatch, compact/empty input,
trailing bytes, отсутствие NUL и явно отклоняемый не-ASCII domain.

## Подключение и ограничения

Исходники: client455_mesh_bindings.h/.cpp. RF455MeshStorage — только 5803-байтовое
хранилище для известных полей, не восстановленный конструктор/класс Character.
Модуль заимствует decoded views; reference vector ownership/free остаётся задачей
полного loader adapter. Не смешивать с legacy ObjectMesh1072 и его heap matrices.

RF_CLIENT_455_MESH_BINDINGS defaultOFF, diagnostic driver явно ON и проверяет
хеши библиотеки, исходников и отчётов. Определение макроса ограничено lab source,
чтобы добавление этой зависимости не пересобирало все старые единицы без причины.
В lab все четыре API действительно вызываются helper object и происходят из
RFClient455MeshBindings:mesh-bindings.obj, x86 /MT. В normal их пока удаляет linker:
штатный LoadRealData не использует новый путь, старая Character ABI сохранена.

Normal: 2 451 456 bytes, entry RVA 0x1BC4B0, SHA
d52d1e6889e679af1262182088e6f648affd7a0f73d89b23c35c975f310ac30b;
snapshot artifacts/client-first-build/mesh455-bones, не запускался.
Lab: 4 534 784 bytes, entry RVA 0x81D4, SHA
0a1dbe6d2f069b436556e7933648b3ce44ac877a0e808653cc1ed7d93d92b79d.
Find/Bind/Rematch/Resolve VA6BB800/6BB7D0/6BB880/6BB8B0,
RVA2BB800/2BB7D0/2BB880/2BB8B0. Это исходный C++, не byte-identical assembly port.

Регрессии текущего lab: MESH08 6304, legacy bindings245/InitVertex6732,
clock1443/map-time314, weather703/resource30, time-command432cases/2628checks
и20actual input checks прошли. 289 modern client/engine/JPEG COFF проверены x86/MT.
Platform01/device — 2GPU cases/69checks, 0 warnings/errors, Dmalloc/COM balance0,
FPU007F. Оба frame SHA равны прежним просмотренным кадрам. Это map/weather regression;
сам Character GPU не проверялся. GameDLLs/reference EXE/normal WinMain не запускались.

Evidence: inventory/character-mesh08-bone-pairs.json, client455-mesh-bindings*.json,
character-mesh455-bindings-graphics-runtime.json. Raw scoped instruction queries:
artifacts/character-mesh08/bone-binding-insns.json. Owned IDA6f091546 закрыта/save.
При первом lab compile имя test variable parent столкнулось с legacy macro parent;
переменная переименована, после чего обе сборки и проверки проходят.

Дальше: metadata/matrices, материал/texture lookup, общий vertex/index GPU buffer
и rebase, publication/release, D3D9 consumer. Потом actual normal model dispatch
и игровые сценарии. M6/M6F/M7/M9 остаются открытыми.
