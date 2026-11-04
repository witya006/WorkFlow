# Восстановление Character из клиентских материалов 455

## Источники

Текущий клиент: SHA-256 b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b,
PE x86, base 0x400000. Статический анализ выполнялся на сохранённой базе backup
(SHA-256 46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558).
Два файла отличаются только ранее установленными 5 байтами. Для восстановленной
инициализации дополнительно проверено побайтовое совпадение тела функции в обоих.

В серверных исходниках и headers GoMMO целевой поиск ChInterface, CHARACTEROBJECT,
ObjectMesh, CHARACTERVERTEX, AnimationManager и связанных имён определений не дал.
Это не исключает пользы серверных структур/протокола для других клиентских задач.
Серверные материалы не копировались, не изменялись и не собирались.

## Подтверждённые зацепки в клиенте

RF_Online.bin статически импортирует d3d9.dll/Direct3DCreate9 и d3dx9_36.dll.
Старая CharacterMR.lib использует IDirect3DDevice8. Контракты версий разделяются;
структуры 455 нельзя автоматически подставить в старую библиотеку.

| Функция | VA / RVA | Статическое наблюдение |
|---|---|---|
| sub_91FD40 | 0x91FD40 / 0x51FD40 | D3DXCreateSprite, создание 2 vertex declarations, загрузка shaders |
| sub_92DB60 | 0x92DB60 / 0x52DB60 | ссылка DrawDynamicVertex(ObjectMesh*), доступы по смещениям объекта |
| sub_8C3400 | 0x8C3400 / 0x4C3400 | ссылки на bone_b.bn и SNWG_001.msh; назначение требует дальнейшего анализа |

Это привязки по инструкциям/строковым xrefs, а не доказанные исходные имена всех функций.
Псевдокод sub_92DB60 имеет неоднозначный прототип с большим числом параметров:
он не используется как готовое объявление C++. Смещения 522, 5086 и матрицы
646/710/774/838 пока являются наблюдениями, а не полным определением ObjectMesh.

## Два восстановленных GPU-контракта

В sub_91FD40 восстановлены два массива D3DVERTEXELEMENT9. Смысл чисел сверён с
официальным d3d9types.h установленного Windows SDK. Тип 7 — SHORT4, не UBYTE4.

| Поле потока | Смещение в потоке 64 байта | Тип |
|---|---:|---|
| POSITION0 | 0 | float3 |
| BLENDWEIGHT0 | 12 | float3 |
| BLENDINDICES0 | 24 | signed short4 |
| NORMAL0 | 32 | float3 |
| TEXCOORD0 | 44 | float2 |
| TANGENT0 | 52 | float3 |

Второй поток: POSITION0 float3 @0, BLENDWEIGHT0 float1 @12, NORMAL0 float3 @16,
TEXCOORD0 float2 @28; минимальный размер структуры 36 байт.

Генератор scripts/recover_vertex_layouts.py создал C++ в
work/recovered/character455/vertex_declarations.hpp. Это GPU-структуры и декларации,
не полный CPU-класс CHARACTERVERTEX и не заглушка Character.h.

scripts/check_recovered_vertices.py собрал и запустил собственный x86 probe:
static_assert размеров/смещений и SDK enums прошли, все 96 байт двух деклараций
совпали с восстановленными записями. Исходные arrays получены статическим анализом,
не захватом работающего клиента. Следовательно, это проверка представления данных,
а не доказательство визуального равенства. Отчёт inventory/character455-vertex-layouts.json.

IDA-сессии 395f70ec/af61006e сохранены и закрыты. Полные выгрузки в artifacts/,
не в Git. Клиент и его DLL не выполнялись.

## Импортные библиотеки из существующих DLL

Из копий ABuse.dll/Adv.dll/PDLL.dll построены современные x86 ABuse.lib/Adv.lib/PDLL.lib.
Экспорты: 9 + 9 + 1; имена/ordinal/RVA и хеши DLL/.lib сохранены в
inventory/recovered-import-libraries.json. Генератор scripts/recover_import_libraries.py.

Проверка: собственный probe успешно скомпилирован/слинкован с тремя архивами;
dumpbin подтвердил именованные импорты ABuse_LoadDic, Adv_LoadDic и HookAllApps.
Probe не запускался, DLL не загружались. Поэтому подтверждена связка имён/линкера,
но не сигнатуры всех экспортов и не их runtime-поведение. В .def имена используются
без привязки к ordinal; ordinal исходных DLL сохранены для справки.

## Далее

Устаревшее включение Winable.h заменено на windows.h в рабочей копии protect.cpp.
Выборочный MSBuild ClCompile/SelectedFiles подтвердил прохождение этого include;
дальше файл остановился на Character.h из BaseHeader.h. Это не успешная полная
компиляция protect.cpp и не изменение/отключение его логики. Патч воспроизводится
scripts/apply_client_port_patches.py; локальный лог protect-selected.txt.

Восстановить CPU-классы Character по библиотеке и клиенту: размеры, поля, конструкторы,
деструкторы, inline-код и владение памятью. Связать legacy/455 форматы mesh/bone/animation
через реальные ресурсы. Полный Character.h ещё не получен, M4 не завершён.
