# Таблицы паттернов и предметных эффектов 455

2026-11-06, Asia/Yakutsk. Участок M6 номер038. В обычную сборку подключены
EffectPatternList, ItemEffectList, их чтение и IsHaveMeshEffect. Это восстановление
подтверждённых данных и выбора эффекта, не загрузка/применение всего EFF.
Полный линк ещё открыт; M6/M6F/M7/M9 не закрыты.

Эталон x86/base400000, SHA-256 current
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b,
backup46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
Пять диапазонов функций совпадают. SHA/RVA/размеры, начальный образ таблицы,
входные файлы и независимые выборки: inventory/client455-effect-tables-reference.json.
Raw decompile/disasm — ignored artifacts/normal-effects455. IDA3ce41498
закрыта, saved=true. Исходные EXE не исполнялись; серверы не использовались.

| Контракт | VA / RVA |
|---|---|
| Чтение PatternList | 925710 / 525710 |
| Чтение ItemEffectList | 929920 / 529920 |
| IsHaveMeshEffect | 927B80 / 527B80 |
| Поиск unsigned item key | 9276B0 / 5276B0 |
| Уникальная вставка: первая запись остаётся | 929460 / 529460 |

Обычный login53FFA1..53FFE7 подтверждает владельцев: PatternList1189820,
ItemEffectList11897EC, EffectFileList11897FC. Последний ещё не реализован.
Инициализация материалов и прочие таблицы не выданы за пустые успешные объекты.

## Подтверждённое поведение и обнаруженная граница

PatternList —2300 DWORD flags и2300 строк по36 DWORD:340400байт. В обоих
PE весь первоначальный образ диапазона1189820..11DC9D0 нулевой, включая
виртуальный хвост секции. Query не читает flags: только сами значения.

Reader925710 делает максимум2299 попыток. Он читает ID и девять чисел через
fscanf("%d%d%d%d%d%d%d%d%d%d"), пропуская whitespace, а не строки. ID>=2300
пропускается; отрицательный ID превращается в большой unsigned и тоже пропускается.
Дубликат перезаписывает строку. Загрузка/отсутствующий файл не очищают прошлые строки.

При этом reader копирует в строку36 DWORD из stack, хотя записал лишь9.
Остальные27 слов не происходят из файла: это неподтверждённые stack bytes.
Инструкции67строк проверены полностью. Утверждать нулевые или восстановленные
эффекты grades9..35 для загруженной строки нельзя.

Source core client455_effect_tables.{h,cpp} хранит собственную known-bit metadata.
Числа без доказанного значения остаются неизвестными. Query такого значения
возвращает RF_EFFECT_QUERY_UNDEFINED; обычный bool facade явно выбрасывает ошибку,
вместо незаметного false/нулевого effect ID. Это открытая граница восстановления,
а не заявка на соответствие неизвестному содержимому stack. Любой будущий
SetMeshEffect должен пользоваться этим же SelectItemEffect и учитывать status.

ItemEffectList читает hexadecimal ID и шесть decimal pattern selectors.
Скалярные переменные обнуляются один раз перед циклом; неполный последний
record сохраняет предыдущие поля. Уникальная вставка оставляет первую запись
при повторном ID. Reload дополняет map; уже существующие ID не заменяются.
Проверены88 инструкций reader и78 инструкций insert, включая unsigned compare.
Современная std::map — собственное source представление: старые STL узлы/ABI
не используются и не приводятся к ней.

Query игнорирует model pointer. Сначала grade>=36 даёт false, затем отсутствующий
item даёт false. Только после нахождения item выбираются group и pattern row.
Group>=6/pattern>=2300 в исходном коде не проверяются. Наш core возвращает
явную ошибку границ; malformed nonnumeric input также останавливается с ошибкой.
В исходном item parser такой токен способен вызвать бесконечный цикл. Эти
невалидные/OOM/unchecked domains не сертифицированы как эквивалентные.

## Проверка и подключение

На рабочих копиях настоящих CHEF/PatternList.txt и ItemEffectList.txt получены
2246 паттернов и4600 уникальных предметов. Независимый Python oracle проверяет
180 выборок из начала/середины/конца данных: группы0/5, grades0/8/9/35/36.
72 выборки явно достигают неизвестного tail, и native probe подтверждает ошибку,
а не выдаёт их за принятый функционал455. Остальные значения/отсутствие эффекта
совпали с oracle в определённой области.

Целевые примеры проверяют дубликаты, reload/missing file, case-independent hex
числа, границы grade/group/pattern, неполные записи со stale fields, нечисловой
токен и ограничение2299 попыток. Используются именно глобальные normal facade
объекты и методы; MAP подтверждает client455_normal_effect_tables.obj.

182client +6facade +20canonicalCPP собираются x86/MT. Реальный полный линк
теперь LNK1120:15 разных методов/данных вместо20, других ошибок нет.
CharacterMR и принудительное разрешение символов не использовались.
Из-за изменения общего Character455.h повторены короткие consumer/renderer
проверки: реальные ANI/BBX, два прежних цветных кадра, теневая текстура,
COM/Dmalloc0. Большие неизменённые suites не повторялись.

Собственный native PE SHA/entry RVA, fixture/library/source hashes, MAP и вывод:
inventory/client455-effect-tables-native.json. Checkpoint — PARTIAL,
inventory/client455-effect-tables-checkpoint.json. Это не полный normal WinMain.

## Далее

Оставшиеся15 перечислены в normal-link.json: EffectList/FileList и globals,
binary EFF loader/SetPartEffect/SetMeshEffect/InitEffect, model IsHaveEffect,
particleSlots/entitySlot, accounting и Character clock. Renderer context у
setter455 дополнительный; старую четырёхаргументную реализацию нельзя вернуть.

Навигация для следующего шага уже сохранена: login вызывает92CEA0
(EffectFileList),92CD60 (Monster/Unit lists),92B380 (EFF load). SetEffect9298D0
идёт в9293D0, затем9281A0/927040. 927040 публикует effect pointer в mesh5455 и
грузит вторичные texture/cache pointers, но это пока reference, не source port.
91C710 проверяет именно render effect/transparency, а не доказанные particle slots.
Не подставлять старые offsets частиц без проверки настоящего455consumer.

Через Invoke-Python.ps1: audit_client455_effect_tables.py,
prepare_client455_normal.py, build_client455_normal.py,
probe_client455_effect_tables.py, probe_client455_normal_consumers.py,
probe_client455_normal_renderer.py, link_client455_normal.py (ненулевой exit),
checkpoint_client455_effect_tables.py. Текущие normal checkpoints также проходят,
сохраняя открытые границы полного клиента.
