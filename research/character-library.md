# Character SDK: состояние исследования

Файл CharacterMR.lib (две идентичные копии в исходном комплекте), SHA-256
483715b927690fc69607682a093dff53635911870456f5849c9f52741702b8a8.
10 COFF x86 объектов. Для релокируемого архива image RVA неприменим.

В архиве присутствуют .debug$S и .debug$T. Проверка содержимого .debug$T показала
по одному LF_TYPESERVER (leaf 0x16, CodeView signature 2) на объект. Это ссылки
на внешний vc60.pdb исходного разработчика, а не полные определения структур
в самом архиве. Пути типа D:/RFOnline/ChracterLib/.../vc60.pdb — отладочные строки,
а не доказательство наличия таких файлов на этой машине.

Проверено scripts/inspect_coff_types.py; отчёт inventory/character-codeview.json.
Целевой поиск Character.h/vc60.pdb/Character-архивов с --hidden --no-ignore под
RFOnlineTrash, D:/MEGA и Downloads дополнительных материалов не нашёл.
Пользователь ответил: дополнительных материалов нет. Продолжать восстановление
контракта по библиотеке и её использованию, не ожидать внешнего SDK.

RF_Client/BaseHeader.h:29 безусловно включает Character.h. Типы нужны большому
числу исходников клиента; простое исключение include или пустая заглушка не решает
восстановление контракта. В M4 требуется найти совместимые материалы либо восстановить
интерфейс и реализацию по символам/использованиям/дизассемблированию.

Совместимость CharacterMR с современным CRT/MSVC не доказана; старый клиент требует
другие имена вариантов. Переименование библиотеки не производится.

## Начало восстановления контрактов M4

Из индекса публичных символов извлечены и деманглированы 224 не-STL контракта:
inventory/character-public-contracts.json, scripts/recover_character_contracts.py.
Они дают сигнатуры методов, но не размеры/поля классов. На их основании автоматически
генерировать Character.h пока нельзя.

10 COFF объектов извлечены в work/character-reverse без изменения содержимого.
Хеш каждого объекта в inventory/character-codeview.json. member_06.obj содержит
ChInterface.cpp по строке .file. Он проанализирован в IDA; сессия e76a265d сохранена
и закрыта. Архитектура x86; база IDA 0, смещения ниже — адреса COFF-анализа,
не runtime RVA загруженного клиентского PE.

Подтверждённые инструкции/наблюдения:

- InitCharacter: адреса 0x8/0xA записывают device в this+0 и this+408 (0x198).
- GetMeshData(char*): вызов GetCharacter по адресу 0x9A0 использует this+112 (0x70);
  далее LoadRealData получает this+408 как TextureManager*.
- GetAlpha: по адресу 0xD66 возвращается float из CHARACTEROBJECT*+772 (0x304).

Полные декомпиляции в artifacts/character-interface-{0,1,2}.json, вне Git.
Размеры классов, наследование и соответствующие именованные поля этим ещё не
доказаны. Для восстановления нужны остальные методы, inline-использования в клиенте,
конструкторы/деструкторы и проверка ABI. Заголовок-заглушка не создавался.

Дополнительно начат анализ поставленного клиента 455: найдены связанные render-функции,
восстановлены две GPU-декларации вершин. Это отдельная версия контракта D3D9; она не
подставляется в старую D3D8 библиотеку. См. character-455-recovery.md.

## Выгрузка тел функций и проверка полей — первый проход

2026-11-04: scripts/export_character_analysis.py выгрузил через IDA MCP 207 тел
публичных функций из 10 рабочих COFF объектов. Это количество определений по объектам,
включая повторные inline-определения, а не число уникальных методов SDK. Неопределённые
внешние символы отфильтрованы по COFF, чтобы не принять extern за реализацию.
Сводка inventory/character-analysis-export.json; полные тела только в ignored
artifacts/character-analysis/. Все созданные сессии закрываются в finally.
Последний повтор использовал кеш, поэтому sessions_closed в его сводке пуст.

scripts/recover_character_layouts.py проверяет 21 операнд реальных x86 инструкций
по именованным COFF функциям и создаёт частичные memory views в
work/recovered/character-legacy/memory_views.hpp. MSVC x86 /W4 /WX подтвердил размеры
и смещения через static_assert; тестовая программа не выполнялась.
Манифест inventory/character-legacy-layouts.json содержит SHA-256 библиотеки/объектов/
функций, номер секции, смещение от начала функции и абсолютное файловое смещение
инструкции. Runtime RVA для релокируемого COFF не существует.

| Старый контракт | Подтверждённое значение | Основание |
|---|---|---|
| CHARACTEROBJECT | выделение 776 байт (0x308) | LoadMeshData, push 308h перед operator new |
| ObjectMesh | шаг массива 1072 байта (0x430) | SetAlpha, учёт памяти конструктора; согласуется с InitVertex |
| ChAnimation | выделение 280 байт (0x118) | AddAnimation, push 118h перед operator new |
| CHARACTEROBJECT loaded | DWORD +260 | LoadRealData читает флаг, после загрузки пишет 1 |
| CHARACTEROBJECT count / mesh pointer | +528 / +532 | SetAlpha, согласуется с обходом IsHaveEffect |
| CHARACTEROBJECT alpha / material | +772 / +692 | GetAlpha/SetAlpha и SetMaterial |
| ObjectMesh alpha | +952 | SetAlpha |
| ObjectMesh effect-active | +888, +904, +920; дополнительное +936 | IsHaveEffect, 3 слота с шагом 16 |
| CObjectManager begin/end/capacity | +4 / +8 / +12 | GetCharacter(unsigned long), AddCharacter |
| CObjectManager next ID | +16 | AddCharacter присваивает объекту и увеличивает счётчик |

Названия полей в views описательные; неизвестные области остаются массивами байт.
Это не Character.h, не полноценные классы и не доказательство CPU layout клиента 455.
Размер CObjectManager целиком, ChInterface, встроенные контейнеры, конструкторы и
правила владения ещё не установлены. В клиентскую сборку эти views не подключены.
Современную std::vector нельзя автоматически подставлять в старый контракт менеджера.

Четыре проверки scripts/test_character_coff.py прошли: определения против extern,
границы повреждённых таблиц, все 10 реальных объектов/границы тел, отказ при неверной
инструкции или усечённом операнде. Декомпиляция использована для навигации;
числа таблицы дополнительно сверены с инструкциями.

## Отдельная проба линковки старой библиотеки

scripts/probe_character_link.py компилирует собственную DLL /NOENTRY с одним вызовом
GetAlpha по восстановленной публичной сигнатуре. DLL не загружается и не выполняется.
С явными современными CRT/Win32/D3DX8 библиотеками остаются два unresolved символа:
std::_Xlen и std::_Xran. inventory/character-link-probe.json; журнал ignored.

/NODEFAULTLIB:libci.lib применён только в диагностическом эксперименте; он исключает
отсутствующую старую default library, но не подавляет unresolved errors. В production
такое решение не перенесено. Пустые реализации или /FORCE не добавлялись. Даже успешная
линковка не докажет совместимость VC6/современных контейнеров, CRT и исключений.

Следующий результат M4: установить оставшиеся размеры/встроенные поля и конструкторы
по этим локальным выгрузкам, сопоставить все прямые обращения клиентского кода,
проверить ABI, затем подключить восстановленный заголовок и продолжить полный compile.
Не повторять массовую декомпиляцию без изменения входных хешей.

## Текущее состояние: диагностический Character.h

Число проверок операндов расширено до 30. Подтверждены выделение CObjectManager 148 байт,
имя +20 с порогом длины 128, встроенные менеджеры CRender +112/+260/+408/+568,
последний DWORD TextureManager +156. Это согласуется с TextureManager размером 160.
MAXPARTICLE=3 и MAX_PATTERN_SIZE=9 проверены по циклам/сравнениям. Точные символы,
хеши и смещения — inventory/character-legacy-layouts.json.

scripts/prepare_character_header.py генерирует Character.h в ignored work/.
scripts/check_character_header.py проверил 64 layout assertions и decorated names 165
адресуемых публичных функций. Данные, непубличные методы и конструкторы/деструкторы
этим адресным тестом не проверяются. Права доступа сохранены: MSVC кодирует их в имени.
CHMEMORYINFO описан как семь DWORD: texture size/count, vertex size/count, animation
size, object count/size — по обновлениям счётчиков и использованию в клиенте.
GetRender возвращает ссылку на известный m_Render; вызов с точкой есть в cbasenpc.cpp.

Все 180 C++ клиента скомпилированы с этим заголовком. Это не готовый SDK: при первоначальной
компиляции конструкторы и inline API только объявлялись. Конструкторы и SetMipMap/SetTexPath
впоследствии реконструированы; GetShadow, EffectList::SetEffect и часть коротких перегрузок
ещё без реализаций. Пустые реализации не добавлялись.
Внутренний layout API-only классов не установлен; не создавать их экземпляры.
CRender/ChInterface размером 776 в реконструкции покрывают наблюдаемые поля, но точный
sizeof оригинального ChInterface сверх этого диапазона ещё не доказан.
Современные std::vector не подставлены вместо старого хранения. STL/CRT/исключения
VC6 и передачи STL объектов требуют отдельной проверки. Компиляция этого не доказывает.
JPEG/Miles зависимости уже подключены. Diagnostic link оставляет 4 уникальных
символов, полный список — inventory/client-character-diagnostic.json.
Native тест подтвердил несовместимость прямого FILE EOF доступа CharacterMR с UCRT;
Classic CRT adapter уже реализован и проверен на собственных fixtures и двух
настоящих Pattern/Item загрузчиках (49 checks). CObjectManager и AnimationManager construction подключены,
3102 native проверки реальных SDK операций на unloaded records прошли; пределы и
AnimationManager invariant reconstruction — research/character-managers.md.
Effect defaults и настоящие exception helpers восстановлены; 770 сравнений с classic
exports прошли. SDK не готов. Текущие доказательства и границы —
research/character-effects-and-exceptions.md; исходные зависимости — client-dependencies-m4.md.
Последующее восстановление setters/empty render construction: 18 ABI checks,
3630 combined native checks, включая 8 instances/136 part managers. Конструкторы
reconstructed, exact original inline/sizeof не доказан. Актуальные границы и следующий
DrawCharacter/SetEffect анализ — research/character-setters-and-construction.md.
