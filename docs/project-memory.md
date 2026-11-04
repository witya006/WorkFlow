# Память проекта

Обновлено 2026-11-04 после уточнения пользователя: ИСКЛЮЧИТЕЛЬНО КЛИЕНТ.

## Цель и границы

Восстановить исходники и собираемый клиент RF Online 455 на основе старого клиентского
кода, R3Engine и реверса клиента 455. R3Engine/утилиты входят в работу как зависимости
клиента. Серверные проекты, БД и серверная логика вне задачи. Их отсутствие не блокирует
клиентскую работу. Перенос под современный MSVC выполняется сейчас; графика отдельно.
Оригиналы читать.

Уточнение пользователя: конечный результат — исходный код RF_Online.bin с полным
функционалом и поведением эталона 455, а не только собирающийся старый клиент.
Промежуточная сборка/первый формат не закрывают проект. Полноту подтверждать реестром
возможностей, сценариями и расхождениями: client-acceptance.md.
Серверные исходники можно читать как справочник; изменять или собирать их нельзя,
включая копии. Их описание не доказывает поведение клиента 455.

## Подтверждено

- Git локальный. IDA/Hex-Rays/Python/MCP работают. Предыдущая проверка MCP на серверном
  бинарнике была только проверкой инструмента, не этапом восстановления клиента.
- Клиент 455 полностью ещё не исследован. Текущий RF_Online.bin отличается от backup.
- Клиентский DSP: 4 CFG, 359 SOURCE, 180 C++; R3Engine: 6 CFG, 126 SOURCE, 58 C++.
  Все перечисленные входы этих двух проектов имеются; это не подтверждает сборку.
- R3Engine собран: успешная полная сборка и две чистые пересборки, 58 COFF x86
  объектов и R3Engine.lib. SHA-256 в inventory/client-build-result.json, сведения
  в research/client-port-m1.md. M1 завершён по критерию компиляции/архивации.
- DirectX 8.1b SDK извлечён локально; SHA1 совпал с архивом, подпись Microsoft Valid.
  Используется overlay 13 DX8 headers без старых системных Windows headers.
- Одиннадцать рабочих файлов исправлены байтовыми патчами, оригиналы неизменны.
  /Zc:forScope- временно сохраняет VC6 loop scope; в будущем заменить объявлениями.
- Два клиента отличаются 5 байтами в 2 диапазонах. Текущий RF_Online.bin закреплён
  как эталон поведения в config/client-target.json; backup — вторичный материал.
  Число 4.55 в файле само по себе не доказывает происхождение/полноту версии.
- IDA проанализировала backup; собственная сессия 4ffd6991 сохранена/закрыта.
  Детали изменённых участков: research/client-reference.md, binary-comparison.json.
- Нет Character.h, требуемых вариантов Character .lib и ряда сторонних статических .lib.
  Из существующих клиентских ABuse.dll/Adv.dll/PDLL.dll восстановлены три x86 import .lib;
  link/import-name probe прошёл без выполнения DLL. Это не восстановление их реализации.
  В CharacterMR.lib 10 .debug$T секций содержат только LF_TYPESERVER (0x16),
  ссылки на внешний vc60.pdb; полных определений типов внутри них не оказалось.
  Пользователь подтвердил: дополнительных материалов Character нет. Продолжать
  восстановление по имеющейся библиотеке/использованиям, не ждать исходников/SDK.
- Установлена VS 2026 Professional 18.11.3. Проверены MSVC 14.51.36231 (compiler
  19.51.36260.0), Windows SDK 10.0.26100.0, CMake 4.3.1-msvc1, MSBuild 18.11.1.51303.
  Собственная тестовая Win32 программа собрана/запущена как x86. Отчёт msvc-verification.json.
  В песочнице получен FileTracker E_ACCESSDENIED; вне песочницы проверка прошла.
- Исторический аудит охватил 14 проектов. Все 962 исходных файла сохранили SHA-256.
  Серверная часть того отчёта не задаёт текущую область работы.

## Решения

- D01 отозван: выбор LoginServer для первой сборки был ошибкой области задачи.
- D01C: первая цель сборки клиентской зависимости — R3Engine - Win32 RTMovie Release.
  В её CPP-флагах нет RTMOVIE; достижимость Character-зависимости проверить препроцессором.
  Эта конфигурация создаёт R3Engine.lib и не удовлетворяет автоматически клиентскому
  требованию R3EngineMT.lib. Это первый шаг восстановления сборки, не готовый клиент.
- Конечная цель сборки — RF_Online, после проверки Character/CRT/прочих библиотек.
- D05: основной путь — сразу VS 2026/MSVC x86, без обязательной установки VC6.
  Старые DSP сохраняются как справочник настроек. DirectX/рендер пока не модернизировать.
- D06: включать _NEW_UI_ и в современной Release сборке. В старом DSP флаг есть только
  в Debug; текущие классы предметов без него исключаются. Контрпроверка global.cpp:
  без флага — ошибки неполных типов, с флагом — успешная компиляция без изменения файла.
- Для клиента строить R3EngineClientMT (/MT, OUTPUT_NAME R3EngineMT), M1 /MD хранить
  отдельно. Не обходить LNK2038 и не переименовывать несовместимые варианты.
- D07: прямая CharacterMR + UCRT несовместима по проверенному FILE EOF доступу.
  Успешный link без адаптации этого ABI не закрывает M4. Старый архив допускается
  только как явная reference library в отдельном diagnostic link, без переименования.
- CharacterMR.lib не переименовывать в CharacterMD/R без проверки символов и ABI.
- Повседневно Sol medium; реверс Sol high; Astra high для трудных локальных вопросов.

## Следующий шаг

Новая активная /Goal (после завершённой ограниченной цели): довести проект до M9.
Пользователь уточнил: M9 — финальная приёмка клиента 455 без модернизации графики.
Критерии docs/client-acceptance.md и M6F/M7, M8 не требуется. Продолжать с M4,
не завершать цель по первой сборке/запуску/частичному участку. Сообщить после приёмки M9.

Предыдущая ограниченная /Goal: завершить движок/закрепление эталона и сообщить при начале
пункта 4 «Получить сборку клиента». Она заменила предыдущий ориентир до M5.
Критерии этой /Goal выполнены: две свежие чистые сборки, совпали runtime sections/
relocations всех 58 x86 объектов; 492 входа целы. Оба исходных бинарника/копии совпали
с закреплёнными хешами; 5 bytes / 2 ranges повторно проверены. Helper-only SPT: 7 тестов,
140 файлов / 97 543 записи повторно прошли. inventory/goal-checkpoint.json,
research/goal-checkpoint.md. Полный клиент и весь проект этим не завершены.

M1 выполнен; бинарный эталон и различия M2 закреплены. M3 выполнен для helper-only
SPT: 140 реальных файлов / 97 543 объекта, побитовое float32 round trip и 7 unit-тестов.
Детали: research/helper-spt-format.md, inventory/helper-spt-verification.json.
M4: диагностическая компиляция всех 180 C++ клиента прошла; RF_Online.bin ещё нет.
Реальный R3EngineMT.lib (/MT) собран отдельно, 58 объектов; вместе с клиентом все 238
объектов проверены как COFF x86 /MT. LNK2038 устранён выбором правильного CRT при сборке,
пути genuine DX8 .lib подключены. JPEG 6b и Miles зависимости уже подключены.
inventory/client-character-diagnostic.json и client-mt-variant.json; research/client-port-m4.md.

В work/recovered/character-legacy/include/Character.h создан диагностический заголовок:
224 исходных публичных контракта, 64 layout assertions, native decorated names 165
адресуемых публичных функций совпали с библиотекой. 30 проверок инструкций подтверждают
числа в отдельном манифесте character-legacy-layouts.json. Это ещё не полный SDK:
конструкторы и часть inline API/default arguments не восстановлены и объявлены без
реализаций, STL/CRT/исключения VC6 не сертифицированы. Никаких пустых реализаций нет.
207 тел функций из 10 объектов кешированы в artifacts/character-analysis; не повторять
массовый реверс. 4 проверки COFF прошли. research/character-library.md.

JPEG 6b: official IJG archive pinned, 46 C /MT, 28 ABI values совпали со старыми
headers; baseline/progressive golden decodes побайтово точны. Miles .lib из комплекта
подключена, 26 реальных импортов есть в 455 mss32.dll; DLL не запускалась. 284 x86 /MT
объекта проверены. Сводки jpeg6b-build.json, miles-link-audit.json, client-mt-variant.json.
Старый item switch уже был недостижим под _NEW_UI_; #else исключает мёртвые ссылки,
живая маршрутизация не менялась. Все 11 патчей сохраняют bytes/кодировки и timestamps
при повторе; генераторы тоже не переписывают идентичные файлы.

Diagnostic link берёт отдельную stdio-adapted копию CharacterMR и адресно откладывает
CharacterR/ziplibm/ZipArchive_STL_M/libci default libs, без /FORCE. Осталось 4 unique
undefined symbols: DrawCharacter short call, SetEffect, CheckFiles и SendLog.
Проверки целостности/логирования не отключались. Парсер LNK исправлен, 3 теста прошли.

Native CRT probe: Character EffectList loader читает FILE+12 &0x10; modern EOF даёт
flags=0x2049 и старый тест false. Classic msvcrt даёт 0x19 и true. Это подтверждённая
несовместимость, не просто риск. Classic x86 DLL hash/metadata проверены с SysWOW64.
Тест использовал только собственную fixture/EXE, не игровой код. vc6-stdio-probe.json.
Адаптер 8 stream API создан: source scripts/native/character_legacy_stdio.*, 1828 native
проверок на собственных fixtures и 3 теста COFF прошли. Только undefined имена в 10 копиях
объектов перенаправлены, инструкции/релокации и оригинал сохранены. Diagnostic link
использует отдельный CharacterMR-stdio.lib + adapter lib. CObjectManager constructor
восстановлен по inlined stores member_06.obj; native harness прошёл 1296 проверок
реальных старых SDK операций на unloaded objects (259 добавлений). Test-only _Xlen/_Xran
aliases теперь удалены и из тестов; modern STL fixture types не используются.
AnimationManager: собственный empty-vector constructor + реальный Init (+16=0,+20=1).
Оригинальный inline ctor не найден, undocumented singleton assignment не добавлялся.
1806 дополнительных проверок real SDK регистрации/поиска/удаления по ID/destruction,
всего 3102. DeleteAnimation(name) имеет предполагаемую UAF по decompile, не проверен.
Header: 64 layout assertions, 165 signatures по-прежнему совпадают.
Два реальных загрузчика Pattern/Item прошли 49 native проверок valid fixtures с
classic FILE adapter. По обоим pinned PE проверены push0/call targets для mesh-effect
defaults; corresponding function names — structural inference, не символы из PDB.
_Xlen/_Xran: собственные /MT typed throws с теми же messages/classes, что в Microsoft
signed x86 msvcp60.dll SHA8d024f35...98dd139; provider не dependency клиентской сборки.
770 сравнений type/message/ref catch/rethrow/512 guard destructions прошли.
Manager/parser тесты повторно прошли с реальной exception library без aliases.
Историческая libci и полное exception unwinding Character ещё не проверены.
research/character-effects-and-exceptions.md, character-managers.md;
inventory/character-{effect-defaults,effect-loaders,exceptions,managers}.json.
Последнее: SetTexPath/SetMipMap восстановлены по 455 (null source, strncpy255 без
форсированного tail NUL; raw DWORD detail). Legacy offsets path272, manager mip156
проверены по consumers; 455 offsets другие. 18 ABI byte checks прошли, character-setters.json.
Texture/mesh/render/interface ctors: собственные empty states + реальные Init SDK.
CRender bridge связывает m_Render=this для старых effect consumers; original inline
binding/полный sizeof не доказаны, Texture/Animation static pointers не менялись.
8 constructions/destructions и 136 part allocations проверены настоящими SDK методами;
оба setters вызываются на constructed objects. Всего 3630 native checks (528 renderer).
research/character-setters-and-construction.md; 4 link gaps. Дальше DrawCharacter
source calls: найден 455 CResObject::Render 0x7CD2A0, явные scale=this+240 и scroll=0.
Проверить CNpc по RTTI/vtable, не угадывать default1.0; изменения поведения вести отдельно
от compiler patches. 455 EffectList setter 0x9298D0 map-based, legacy массивы отличны.
CheckFiles/SendLog сохраняются. Все raw findings сохранены, IDA session 2e6f4605 закрыта.
Полной runtime ABI
проверки ещё нет. research/character-stdio-adapter.md; character-stdio-adapter.json.
Все собственные IDA-сессии закрыты. Серверы не менялись.
В 455 подтверждён D3D9, восстановлены 2 GPU layouts; это не CPU ABI старой D3D8 библиотеки.
Дополнительных материалов у пользователя нет. M5 ещё не начат; новая /Goal заканчивается
финальной приёмкой M9 без модернизации графики.
Полный хеш-манифест ресурсов и атрибуция версии ещё открыты.

## Неизвестное

Полный Character SDK/inline/default arguments, сторонние .lib и runtime ABI;
покрытие поведения 455. Известна рекурсия CLevel::GetFrustumNormalPlane в старом коде,
не исправлялась; проверить относительно 455. Серверные вопросы в задачи не входят.

## Обновление

После этапа обновлять статус и следующий шаг. Доказательства в inventory/research,
крупные результаты в work/artifacts. Не хранить здесь логи, секреты и декомпиляции.
