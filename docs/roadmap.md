# Дорожная карта восстановления клиента RF Online 455

Обновлено 2026-11-05. По прямому указанию пользователя: работа ИСКЛЮЧИТЕЛЬНО НАД КЛИЕНТОМ.
Старые клиентские исходники и R3Engine — база, клиент 455 — объект реверса.
Серверы, БД и серверная логика вне задачи. Прежний серверный план отменён.
Серверные исходники разрешены исключительно для чтения как справочник клиентских
контрактов, без изменений и сборки. Каждый вывод проверяется на клиенте 455.

Конечная цель — исходники RF_Online.bin с полным функционалом и поведением выбранного
455. Этапы ниже — промежуточные результаты. Критерии полноты и начальная матрица:
[client-acceptance.md](client-acceptance.md). Не закрывать проект после сборки/запуска.

## Текущий статус

M1 выполнен: R3Engine.lib, две чистые пересборки, все 58 объектов x86.
M2: бинарный эталон закреплён по SHA-256, различия текущего клиента/backup исследованы.
M3 выполнен для helper-only SPT: 140 файлов, 97 543 объекта, round trip и 7 тестов.
M4: первая полная diagnostic RF_Online.bin из 180 C++ и чистая пересборка успешны.
Это сборочный результат старой базы с выбранными 455 ветками; runtime и canonical
optimized Release не проверены. research/client-first-build.md.
Предыдущая /Goal до начала пункта 4 выполнена (research/goal-checkpoint.md).
Новая активная /Goal — M9: финальная приёмка клиента 455 без модернизации графики.
M8 остаётся отдельным необязательным этапом и не блокирует M9.
Все 180 C++ уже компилируются в диагностической конфигурации с восстановленными
объявлениями Character. Настоящий /MT движок собран отдельно; 238 COFF x86 /MT проверены.
JPEG 6b/Miles подключены; diagnostic link успешен, unresolved symbols нет. CObjectManager
constructor восстановлен, AnimationManager сконструирован через empty state + Init;
реальные SDK операции и empty renderer construction прошли 3630 native проверок.
SetTexPath/SetMipMap восстановлены; 18 дополнительных ABI проверок. Два старых загрузчика прошли
59 проверок с CPU mesh effect application; exception helpers — 770 сравнений с classic exports.
455 draw аргументы подключены отдельным flag/ledger; legacy SetEffect bridge проверен.
455 map/36-grade эффекты ещё не перенесены. Character inline/CRT
ещё не закрыты. research/character-effects-and-exceptions.md.
M5 закрыт для первого выбранного helper-data участка: loader455, две instruction-identical
math функции, RPK доступ и реальное interior/weather использование.140files/97 543records,
2 546 931native/comparison checks,338math checks/12FP modes. Настоящие клиентские
LoadLevel/FrameMove/render/release прошли в own entry на lobby и Platform01;
Platform01:23helpers/8interiors, два weather layers меняют состояния[0,0]→[1,1]→[0,0].
13GPU cases/321checks,703weather,30resource и23 337targeted helper regression checks.
Gate inventory/client-m5-checkpoint.json; research/client-m5-checkpoint.md.
M6 в работе; M6F/M7/M9 открыты.
В M6 восстановлен численный clock:773instruction bytes/8scalar functions+256byte
frame prefix,1275native checks/12FP modes внутри module/полного клиента;287objects /MT.
Actual Platform01 FrameMove/GPU повторно прошёл с новыми clocks (2cases/59checks).
Следом packet8/5,CLand timestamp/tick cache и successful-load hook перенесены:
130byte numeric fragment равен455,314checks/12FP modes/UTC+JST; actual CNetMap/CLand
Platform01 GPU2cases/66checks. Актуальная сборка288objects /MT.
Следом local time/real_time +grade>=1 input перенесены:432cases/2628checks и20actual
CHAT_INFO checks. Clock расширен до10scalar functions+256byte prefix,1037bytes/
1443checks/12FP modes. Commands→actual weather/GPU2cases/69checks;289objects /MT.
Full CLand/transport/calendar/other local commands/chat/lighting domains ещё открыты.
research/client455-clock-source.md.
research/client455-map-time-source.md.
research/client455-time-commands-source.md.
Character:4legacy CPU bindings восстановлены source и подключены normal/lab;
245native checks/4COFFtests,actual InitVertex skinned/unskinned CPU setup/release
и3linked call destinations проверены. Pointer+160 задаётся штатным FindBlendParent;
constructor patch не нужен на подтверждённом пути. Выявлены455mesh5803/vertex64/inline
blends против legacy1072/36/heap иfirst-match vs last-match. Полный Character455
ещё открыт; следующий source unit — InitVertex/vertex conversion и реальные assets.
research/character-mesh-source.md. M6/M6F/M7/M9 не закрыты.
Затем source unit расширен до8functions/full legacy InitVertex:245binding+6732checks/
144cases/12FP modes standalone/full-client,4COFFtests,2actual LoadRealData→source calls.
CPU vertices/triangles/weights/matrices/errors сравниваются с SDK через test-only COM
capture. 455negative normals/vertex64 иотдельный MESH08loader922A00 подтверждены;
Shield065 имеетновый header,old693reader его не читает. Новый приоритет —455MESH08/
CPU data,потом packed layouts/D3D9. research/character-init-source.md. Character455 открыт.
MESH08 framing теперь восстановлен:858real files/12090meshes прошли lossless roundtrip;
6304native checks/12samples/393parts/1309guarded truncations standalone/full-client,
7Python tests. Source dependency доступна, normal model-loader ещё не использует её.
Runtime materials/bones/shared GPU buffers иполный Character455 остаются открытыми.
research/client455-mesh08-format.md. Это завершение формата,не всего loader или M6.
Следом source455parent/bone kernels проверены:2237checks/12real mesh-skeleton pairs/
393meshes/455skeleton records standalone/full-client;20overlap cases31–50. Полный
normal loader иCharacter GPU ещё открыты. research/client455-mesh-bindings-source.md.
Constructor/header/matrices/material-request kernels455 теперь source:14562checks/
12real files/393parts/12FP modes standalone/full-client. Матрицы используютpinned
D3DX9_36 сегоreciprocal quirks;texture provider вtests scripted. Физический
TextureManager/sharedGPU/normal loader ещё открыты. research/client455-mesh-runtime-source.md.
Следом physical Character texture backend восстановлен source ввыбранном domain:
RFS/DDS/lookup/cache/load/delete,actual pinned D3DX9_36+HALD3D9.24body ranges совпали
собоими PE;9Python/333CPU/8440GPU checks standalone/full-client,80DDSprofiles,
68successful texture pairs/137renders,97material parts/59bindings,COM/Dmalloc0.
Normal model-loader ещё legacy;shared buffers/animation/full Character GPU открыты.
research/client455-character-textures.md. Следующий unit93E000/93E180/index rebase/
publication/release,затем normal dispatch. M6/M6F/M7/M9 незакрыты.
Следом sharedGPU sourceunit готов:18pinned bodies,8200byte pools/ctor/Release-only
dtor/first-fit1024/upload36+64+INDEX16/bind/rebase/MESH08GPUfragment.158336CPU/
159173HALchecks standalone/full-client,12files/393parts:276real uploads,
117zero-index skips.4synthetic indexed draws,COM/Dmalloc0. Normal full loader,
owning publication/destructor/unwind,skeleton/skinning/shaders ещё открыты.
research/client455-shared-buffers.md. Следующий unit —owning model lifecycle и
normal dispatch;полныйM6/M6F/M7/M9 не закрыт.
Следом mesh lifetime иconnectedMESH08route source готовы:9953CPU/10021HALchecks,
12files/393parts/276realuploads/59texturebindings,12lifetimecases,ownheap/COM/Dmalloc0.
10bodies equalbothpins. Full-model lab связывает материалы/header/GPU/parents/bones/
publication/release. Normalmanager/filedispatch,полныйmodel ABI,BN/animation/shaders
ещё открыты;known800byte view не заменяетстарыйCHARACTEROBJECT. Next:file/manager
route исогласованныеtypedconsumers. research/client455-model-pipeline.md.
Следом record1188/manager4148/cache/rawMSH/texture refresh восстановлены source:
850CPU/1138HALchecks standalone/fullclient,12models/393parts/276uploads/59pointers.
24bodies equalbothpins;ctor1188byte oracle из92instructions;13APIs linked/called.
Normal dispatcher остаётсяlegacy. Next: BN reader93C2F0/importer93C770/converter93CD60,
dispatcher9238A0/FrameMove923A40, animation иtyped consumers. Current model10021/
Platform01-device69checks прошли,frameSHA сохранены. research/client455-character-manager.md.
Затем intermediate reader93C2F0/part720/model28lifetime source прошли4606standalone
checks/12realBN455records+5synthetic4records,1183guarded prefixes/7allocfailpoints/
12FPmodes/6Python tests. Importer/converter/BNruntime/normal integration ещё впереди.
research/client455-legacy-model-reader.md. Converter теперьcachedвесь578lines.
Затем полныйvalid-input legacyMSH/BN converter/fileIO/weights/indexing/MTG source
подключён:66627capture/14896HALchecks standalone/fullclient,34runs972parts,
832HALindexeduploads/2CPUretained;12realBN→MESH08pairs393parts276uploads.
Fullclient source10APIs verified,heap/COM/Dmalloc0. Normaldispatcher/ANI/animation/
shaders/typedconsumers ещё открыты. Next:ANI93ACD0/dispatcher9238A0/FrameMove923A40.
research/client455-legacy-model-runtime.md. Current manager1138/model10021/graphics69passed.
Очередь M6 уточнена: Character source/ABI перед полным D3D9 port; legacy SDK contract
явно IDirect3DDevice8. Старые InitVertex/loaded mesh/blend kernels уже проверены,
не повторять их исследование. Cached207definitions доступны.
Разница D3D8 базы и D3D9 эталона — обязательное
восстановление M6, а не модернизация M8. Полные particles/clock/Character/UI/network
не сертифицированы; нормальный WinMain и входной455 EXE не запускались.

## Этапы

Последующий unit ANI/record/attachment/Character dispatcher source готов:
14513CPU/15181HALchecks standalone/fullclient,27ANI1062tracks/22real switches,
11BN→MESH08pairs794parts/660HALuploads.13sourceC APIs verified;legacy14896/
manager1138/Platform01-device69passed,framesunchanged. Normalruntime покаlegacy;
pose/key evaluator/animationmanager/worker/shaders/typedconsumers ещё открыты.
Gate inventory/client455-animation-checkpoint.json;
research/client455-animation-dispatch.md. ДалееFrameMove923A40.

Основная среда теперь VS 2026 Professional / MSVC x86: собственная Win32 smoke-сборка
прошла. Сразу переносим клиентский код на современный компилятор. VC6 — резерв,
его поиск не является предварительным условием. Графику сохраняем на этом этапе.

| Этап | Результат | Критерий готовности | Модель |
|---|---|---|---|
| M0. Основа | Git, IDA MCP, инвентарь клиентского кода/движка | Выполнено; клиент ещё не собран | Sol medium |
| M1. Перенос и сборка движка | Современный проект R3Engine на основе RTMovie Release | MSVC x86, две чистые сборки R3Engine.lib, проверены COFF machine/символы/CRT | Sol medium/high |
| M2. Эталон клиента 455 | Копии текущего RF_Online.bin/backup, IDB и карта различий | SHA-256, x86, image base/RVA, закреплённый эталон | Sol high |
| M3. Первый формат 455 | Клиентская спецификация и парсер | Реальные файлы, границы и повреждённые входы проверены | Sol high |
| M4. Полная старая клиентская сборка | RF_Online с согласованными Character/движком/CRT и SDK | Компиляция/линковка и повторная чистая сборка успешны | Sol high, Astra точечно |
| M5. Первый участок 455 | Восстановленный клиент загружает и использует выбранные данные 455 | Поведение сверено с клиентом-эталоном, регрессии проходят | Sol high |
| M6. Клиентские подсистемы | Ресурсы, персонаж, мир, UI, анимация, звук, ввод, клиентский протокол по одному | Для каждого участка: реализация и подтверждённое клиентское поведение | Sol high |
| M6F. Полнота клиента 455 | Исходники и воспроизводимая сборка RF_Online.bin с полным функционалом/поведением эталона | Все выявленные возможности и сценарии покрыты, известных расхождений нет, непроверенное явно учтено; критерии client-acceptance.md | Sol high, Astra для спорных участков |
| M7. Закрепление сборки | Зафиксированные версии и автоматизация современной клиентской сборки | Сохранены форматы и поведение, проходят те же проверки | Sol high |
| M8. Графика (отдельно от текущей цели) | Модернизация клиентского рендера | Отдельная спецификация; не требуется для M9 | Отдельная спецификация |
| M9. Финальная приёмка клиента 455 | Поддерживаемые исходники и воспроизводимый RF_Online.bin с функционалом и поведением закреплённого эталона | Выполнены M6F/M7 и все критерии client-acceptance.md; известные расхождения закрыты, непроверенное не выдано за соответствие; модернизация графики не входит | Sol high, Astra точечно |

M2/M3 можно вести до получения toolchain. M1 — восстановление сборки зависимости,
не готовый клиент: R3Engine.lib не совпадает по имени с требуемой клиентом R3EngineMT.lib.
Необходимость Character для конкретных веток движка проверить препроцессором.
Для M4 нужны клиентские зависимости B01–B08; инструменты B09–B11 подключать по необходимости.
Серверные B12/B13 из исторического аудита не являются блокерами этого проекта.

Сетевые находки ограничены клиентскими обработчиками/пакетами/состояниями. Наблюдение
ответа существующего внешнего стенда не превращается в задачу разработки сервера.
Сроки уточнять по первому проверенному формату и первой клиентской сборке.

## Ближайшая очередь

1. M6: FrameMove/key evaluator/pose/animation и
   normal typed consumers. Framing/material/texture/sharedGPU/lifetime/MESH08route/
   selected manager/rawIO/ANI/attachment/dispatcher source готовы; normal loader не переключать до согласования
   ABI иconsumers. Полный455D3D9renderer иреальные model scenarios остаются в M6.
2. Восстановить D3D9renderer/shaders/lighting455 вместе с Character consumers.
3. По одному закрывать остальные M6 client subsystems и реальные acceptance scenarios.
4. M6F: завершить реестр возможностей/расхождений и доказательства полноты клиента.
5. M7: закрепить воспроизводимую сборку;M9: финальная приёмка455 без модернизации графики.

## Организация работы и память

Один цикл — одна проверяемая цель: определить входы/критерий готовности, провести
минимальный эксперимент, проверить, записать доказательства, обновить текущий статус.
Непроверенная гипотеза не становится фактом при переходе в новый чат.
Субагенты — только по отдельной просьбе пользователя.

| Файл/каталог | Назначение |
|---|---|
| AGENTS.md | Постоянные правила, границы действий, порядок чтения |
| docs/project-memory.md | Короткое актуальное состояние, решения, следующий шаг |
| docs/environment-audit.md | Подтверждённое окружение и границы проверки |
| docs/build-audit.md | Клиентские зависимости B01–B11 и первая сборка |
| docs/next-steps.md | Ближайшая очередь, обновляемая после этапа |
| docs/roadmap.md | Долгосрочные этапы и критерии перехода |
| docs/client-acceptance.md | Полнота функционала/поведения и проверяемые расхождения |
| inventory/*.json | Воспроизводимые манифесты и сводки |
| research/ | Исследования форматов/подсистем с доказательствами |
| scripts/ | Повторяемые массовые операции и проверки |
| work/, artifacts/ | Копии, IDB, сборки; требуется отдельный backup |

Находка в бинарнике: файл/SHA-256, архитектура, image base, VA/RVA функции,
вход/выход, вызывающие функции, проверка, статус «подтверждено/гипотеза/неизвестно».
Формат данных: хеш образца, смещения/размеры, границы и обработка ошибок.
В Git — небольшие изменения и очищенные сводки, без секретов, БД, игровых бинарников
и сырых логов. Remote/push для этих этапов не нужны.

## Модель и уровень мышления

Это рекомендация для проекта, не гарантия результата на любом участке:

| Работа | Стартовая настройка | Повышение |
|---|---|---|
| Аудит, скрипты, сборка, документация | GPT-6.1 Sol в Codex, medium | high при нескольких взаимодействующих причинах |
| Реверс C++/x86, структуры, пакеты, сравнение версий | GPT-6.1 Sol, high | Astra high при противоречиях после сбора фактов |
| Сложный ABI/неизвестный алгоритм, пересмотр решения | GPT-6 Astra, high | xhigh для конкретного нерешённого вопроса |
| Сводка проверенных данных | GPT-6 Luna, high, либо существующий скрипт | Не поручать окончательные выводы о совместимости |

Codex — рабочая среда с файлами/MCP; GPT — выбранная модель. Для проекта используем
Codex внутри этой папки. Повседневно достаточно начать с Sol medium; на реверсе — high.
Настройки этим документом не изменены; доступность зависит от аккаунта/клиента.

Официальная документация на 2026-11-04 рекомендует Sol для длительной работы при
важности стоимости, Astra для наиболее сложных задач, Luna для узких повторяемых.
Повышение reasoning расходует больше времени/токенов. Конкретные уровни в нашей
таблице — инженерная рекомендация: https://learn.chatgpt.com/docs/models.

Экономия: массовые выгрузки IDA сохранять локально, в контекст давать нужные функции
и различия; не повторять инвентаризацию без изменения входов; не загружать все навыки;
закрывать по одному контракту с проверками. Max/ultra не использовать по умолчанию.
Бюджет и сроки уточнять после M1/M3 по измеренным результатам.
