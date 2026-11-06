# RF Online: исследовательская рабочая область

Цель: восстановить исходный код RF_Online.bin и довести собираемый КЛИЕНТ
до полного функционала и поведения закреплённой версии 455,
используя старые клиентские исходники и R3Engine как базу. Работа исключительно
над клиентом, его движком и необходимыми инструментами ресурсов. Серверные проекты
и серверные базы данных в задачи не входят. Серверные исходники разрешено читать
только как справочный материал, без изменений и сборки. Точная идентичность оригинальным
исходникам не предполагается. Модернизация графики — отдельный этап.

Основная папка: `E:\RFOnlineTrash\Source\WorkFlow`.
Репозиторий локальный; публикация и remote не настроены.

Последний участок M6 — tutorial-board061: восстановлено управление панелью,
выходом и выбором сценария; сообщения2/3 открывают настоящие GUI-диалоги и
проверены на D3D. На кадре обнаружены старые назначения кнопочных спрайтов.
Полный briefing и подключение к игровому Tutorial ещё открыты.
[Доказательства](research/client455-tutorial-board.md).

Предыдущий участок M6 — tutorial-actions060: правила UI/Equip/Cursor/Combat/Item
перенесены; фабрика охватывает47типов и подготавливает99реальных сценариев.
Проверка — recording host. Настоящий UI/Avatar/world и ordinary Tutorial
ещё открыты. [Доказательства](research/client455-tutorial-actions.md).

Предыдущий участок M6 — tutorial-spatial059: перенесены правила Move/Creation/
Position. Factory охватывает0–18; recording-host проверки прошли. Настоящий
мир/Avatar, остальные28 селекторов и неизвестный хвост item packet ещё открыты.
[Доказательства](research/client455-tutorial-spatial.md).

Предыдущий участок M6 — tutorial-runtime058: восстановлены порядок/состояния QBI,
сообщения и ожидания. Собственная библиотека проверена с recording host;
реальный UI/Avatar host и остальные41 селектор ещё открыты.
[Доказательства](research/client455-tutorial-runtime.md).

Предыдущий участок M6 — tutorial-scripts057: восстановлен формат47команд SCP.
Новая C++ библиотека прочитала99реальных сценариев и сохранила все байты;
поля/границы проверены. Исполнение команд и подключение Tutorial ещё впереди.
[Доказательства](research/client455-tutorial-scripts.md).

Предыдущий перенос M6 — camera056: обычный CAniCamera загружает1.2/1.3,
восстановлены FOV scale и playback boundaries455. Реальные камеры обучения/
входа, GPU projection и release проверены; новая PE сохранила existingCreate=1.
Полный Tutorial/fourstage/мир ещё открыты. [Доказательства](research/client455-camera.md).

Предыдущий перенос M6 — progress-base055: восстановлены обычный базовый цикл,
поле next-stage и Title next1. Реальные методы/счётчики проверены; полная
сборка и existingCreate=1 сохранены. Фабрика4stage/Tutorial ещё открыта.
[Доказательства](research/client455-progress-base.md).

Предыдущий аудит M6 — progress054: подтверждены четыре этапа455, включая
CGP_Tutorial; источник mode2 — Avatar stage. Текущая база ещё имеет три этапа
и старые переходы. Следующий перенос охватывает stage/Avatar/Tutorial вместе.
[Доказательства](research/client455-progress.md). Runtime в054 не менялся.

Последний реализованный участок M6 — account053: начальный seed, пакеты входа342байта,
ответы и world records72байта подключены к обычным send/receive/dispatch.
Реальные методы и диалог ожидания проверены на собственных пакетах; полная
сборка и запуск до существующего Create=1 сохранены. Настоящая аутентификация,
полный UI/протокол/мир ещё открыты. [Доказательства](research/client455-account.md).

Предыдущий участок M6 — connection052: настоящий Connect/wait выполняется до
движка. Восстановлены обработка сетевых событий, задержка callback и тайм-ауты.
Korean CCR WinMain через реальное TCP-соединение прошёл engine/D3D/existingCreate;
ошибки проверены отдельно. Это не игровой вход. У argv-профилей остаётся вопрос
endpoint0/1 и недостающих country/handler side effects.
[Доказательства](research/client455-connection.md). M6/M9 открыты.

Предыдущий участок M6 — network-codec051: AES-CBC с отдельными ключами направлений
и формат пакета подключены к обычным отправке/приёму. Восстановлены кольцевые
буферы 20КБ/1МБ и два настроенных сетевых процесса при вместимости шесть.
Байты сверены с Windows AES, реальные методы клиента проверены на фрагментации
и переходе через конец буфера. Полный протокол, вход и UI ещё открыты.
[Доказательства](research/client455-network-codec.md). M6/M9 открыты.

Предыдущий участок M6 — bootstrap050: FG/USEFG, country-specific instance check
и сетевое состояние Connect восстановлены. Настоящий NetworkMgr создаётся
один раз перед движком. Полная собственная PE собирается; прежний Create
возвращает1. На закрытом порту подтверждена особенность455: чтение ошибки
после closesocket теряет10061 и даёт0, connected остаётсяfalse. Полный транспорт,
шифрование, вход и UI ещё открыты. [Доказательства](research/client455-bootstrap.md).
M6/M9 открыты; следующий участок051 — клиентский transport/framing/crypto.

Предыдущий участок M6 — launcher049: восстановлены 93-байтовый launcher-файл
и аргументы Россия/Европа. Обычный WinMain читает их перед языком и движком;
старое позднее чтение удалено. Существующий CMainApp.Create вернул успех.
Проверки проведены на собственных offline-данных; подключение и вход455 ещё
не приняты. [Доказательства](research/client455-launcher.md); M6/M9 открыты.

Предыдущий участок M6 — sprites048: обычный CMainApp.LoadData загружает настоящие
языковые/Common спрайты455; восстановлена загрузка DXT5. Курсор и кнопка
отрисованы, содержимое текстур сверено с файлами. Точная собственная PE прошла
инициализацию UI до чтения launcher-данных. Полные интерфейс/вход/игра ещё
открыты. [Доказательства](research/client455-sprites.md); M6/M9 открыты.

Предыдущий участок M6 — lifecycle047: восстановлен подтверждённый по 455 выход
из UnloadLevel до создания уровня. Три пробы реального глобального CMainApp/
CLand и две GUI-пробы без создания Land завершились естественно с кодом 0.
Полная новая RF_Online.bin собирается; полные Create, ILevel и игровой цикл
ещё открыты. [Доказательства](research/client455-lifecycle.md). M6/M9 открыты.

Предыдущий участок M6 — font046: обычный engine text path использует455GDI/
Unicode backend. Реальный CGUIText нарисовал Hangul/кириллицу из NDLanguage;
метрики/atlas проверены независимым GDI,оба UI probes завершились чисто.
Exact own PE font/D3D/Character startup и прежние кадры сохранились. FullUI/
FT/IME/early-abort/shutdown открыты. research/client455-font.md; M6/M9 открыты.

Предыдущий участок M6 — language045: EDF/NDLanguage reader, indexed lookup и
DBCS boundaries восстановлены. Exact own WinMain загрузил корейский и русский
пакеты с правильными codepages; после корейского сохранился startup Character.
Все9доступных пакетов прошли byte roundtrip;11CRT locale согласованы. Шрифт/
текст/UI и весь Create ещё открыты. research/client455-language.md; M6/M9 открыты.

Предыдущий участок M6 — nationpaths044: выбор страны/корня данных подключён к
обычному WinMain. Новая полная сборка прошла ранний CMainApp::Create до Character
и менеджеров; Character привязан к настоящему устройству приложения. Остановка
до старых игровых таблиц. Полный язык/CRT/font/NDLanguage и Create/UI открыты.
research/client455-nation-paths.md; checkpoint PARTIAL; M6/M9 открыты.

Предыдущий участок M6 — devicestartup043: по 455 восстановлены установка32бит
без принудительного fullscreen и строгий результат Create. Производная
библиотека движка сохраняет033; полная PE прошла actual window/D3D init:
ready1/windowed1, устройство ненулевое. Остановка перед CMainApp::Create.
research/client455-device-startup.md; checkpoint PARTIAL; M6/M9 открыты.

Предыдущий участок M6 — startup042: точная собственная RF_Online.bin прошла CRT,
вошла в обычный WinMain, выполнила engine bootstrap и успешный Miles Audio init.
Запуск из отдельного lab остановлен отладчиком перед D3D; окно/Create/сеть и
полный shutdown ещё не приняты. Импорты и реально загруженные providers проверены.
research/client455-startup.md; checkpoint PARTIAL; M6/M9 открыты.

Предыдущий участок M6 — accounting041: общее накопительное хранение счётчиков
Character и чтение их диагностическим экраном подключены. Реальные ANI/модели/
GPU-ресурсы и release проверены. Новая D3D9/Character source ветка полностью
скомпилировалась и слинковалась в RF_Online.bin: 0 missing symbols. Это ещё не
приёмка normal WinMain или поведения всего455. research/client455-normal-accounting.md;
checkpoint PARTIAL; M6/M9 открыты. Далее — normal startup/initialization.

Предыдущий участок M6 — characterclock040: отдельный таймер Character восстановлен
и подключён к обычному _R3CalculateTime. QPC, fallback и независимость от таймера
движка проверены. Полный линк: один g_ChMemoryInfo; следующие задачи — учёт памяти
и полная линковка. research/client455-character-clock.md; M6/M9 открыты.

Предыдущий участок M6 — effects039: загрузка EFF, выбор и применение эффектов,
сброс и ссылки на particle/entity slots подключены к обычной сборке. Эффект
с настоящей DDS проверен на модели через D3D9; прежние кадры сохранились.
Полный линк сократился с 15 до 2 символов: Character accounting и clock.
research/client455-effects.md; checkpoint PARTIAL; M6/M9 открыты.

Предыдущий участок M6 — effecttables038: два readerтаблиц иquery подключены,
реальные таблицы проверены. Неизвестные grades9..35 выявляются явно; весь EFF
ещё не перенесён. Полный линк15символов. research/client455-effect-tables.md;
checkpoint PARTIAL; M6/M9OPEN.

Предыдущий участок M6 — normalshadow037: восстановлены BeginShadow/EndShadow
и теневые render targets. Реальная модель дала силуэт, прежние цветные кадры
совпали. Полный линк ещё20символов; обычный игровой shadow lifecycle открыт.
research/client455-normal-shadow.md; checkpoint PARTIAL; M6/M9OPEN.

Предыдущий участок M6 — normalcontracts036: восстановлены пять методов
reset/parent/eye/texturepath/bounds. Реальная модель после сброса и повторного
назначения анимации/перепривязки рисует прежние два кадра. Полный линк ещё22символа.
research/client455-normal-contracts.md; checkpoint PARTIAL; M6/M9OPEN.

Предыдущий участок M6: обычные CUnity → модели/ANI → поза → CRender → D3D9
отрисовали реальную модель. Два кадра через координаты и явную матрицу совпали;
проверены фильтры видимости, alpha/material и очистка ресурсов. Полный линк ещё
открыт: 27 методов/данных. research/client455-normal-renderer.md;
inventory/client455-normal-renderer-checkpoint.json (PARTIAL). M9 открыт.

Предыдущий участок M6: 180 клиентских исходных единиц перенесены на типы 455
в work/client455-port/normal. После выделения CUnity/CAnimation собираются 182
объекта x86/MT. Реальная загрузка ANI через обычные потребители проверена.
Полная линковка открыта: 39 методов/данных; CharacterMR не используется.
inventory/client455-normal-checkpoint.json; research/client455-normal-port.md.
M6/M9 остаются открытыми.

Предыдущий участок M6: реальный R3Engine перенесён на D3D9 в work/client455-port,
67units x86/MT собираются. Device/Platform01 прошли с Grass shader и source
Character owner на одном D3D9 device,8interiors/2weather layers проверены.
Normal180clientTUs/typed Character facade ещё не подключены; базовая сборка
work/client-build сохранена. Gate inventory/client455-engine9-checkpoint.json;
research/client455-engine9-port.md. M6/M9 остаются открытыми.

Предыдущий участок M6: source владелец Character455 — constructor/device binding/
destruction и typed model/draw contexts. Реальная модель с ANI/3textures прошла
через принадлежащие ему managers/pools/shaders отдельно и в полном client lab;
два кадра совпали, allocations/COM освобождены. Normal runtime прежний кроме
timestamps; совместный normal typed Character/D3D9 port ещё открыт. Gate
inventory/client455-renderer-owner-checkpoint.json; research/client455-renderer-owner.md.

Предыдущий участок M6: восстановленный расчёт плоскостей камеры иAABB подключён
к обычным SetCharacterClipping/CResObject::ProcessClipping. Численные/actor cases
и короткая Platform01 регрессия прошли. Normal Character API audit завершён:
ещё39функций старогоSDK. Следом совместный typed model/animation/Character owner/
D3D9 device port. Gate inventory/client455-frustum-checkpoint.json;
research/client455-normal-character-interface.md. M6/M9 остаются открытыми.

Предыдущий участок M6: основной Character draw/эффекты/прозрачность/batch/CPU/shadow
перенесены в source.16targeted сценариев и реальная модель с ANI/3textures прошли
отдельно и внутри client lab; два кадра совпали. Normal typed model/animation/
D3D9engine migration,visibility/CRT/undefined domains ещё открыты. M6/M9 не закрыты.
Gate inventory/client455-character-draw-checkpoint.json;research/client455-character-draw.md.

Предыдущий участок M6: восстановленные draw-state/program/material/palette/shared
submission рисуют реальный BELPHEGORHOLIDAY с ANI и3textures на D3D9 HAL.
46geometry parts/44skinned,2кадра совпали отдельно и в полном client lab.
Полный92E5F0/effects/transparent routing/normal D3D9 ещё открыты; M6/M9 не закрыты.
Gate inventory/client455-draw-checkpoint.json; research/client455-draw.md.

Предыдущий участок M6: source загрузка12штатных SHO, компиляция12VS/3PS и создание
двух Character declarations проверены на настоящем D3D9 HAL отдельно и в полном
client lab. Контрольный треугольник использует original shader; полный Character
draw и normal renderer ещё открыты. Подтверждённые различия old/455 layout требуют
совместного переноса consumers. Большие неизменённые наборы не повторялись.
M6/M6F/M7/M9 не закрыты. Подробности research/client455-shaders.md,
inventory/client455-shaders-checkpoint.json и docs/next-steps.md.

История предшествующих этапов (актуальная очередь выше):

Получена первая полная диагностическая сборка RF_Online.bin и успешная чистая
пересборка. Это старая база с выбранными подтверждёнными участками 455, а не готовый
клиент 455. Результат/границы: research/client-first-build.md.
M5 закрыт для первого выбранного участка: helper SPT455 и его interior/weather consumer.
140 файлов/97 543 записи проверены; две math функции совпадают с инструкциями455.
В own entry полного проекта настоящие LoadLevel/FrameMove/render/release прошли
на lobby и Platform01. На Platform01 загружены23helpers/8interiors; два погодных слоя
правильно меняют состояния внутри/снаружи и ночью/днём.13GPU cases/321checks прошли.
Основание и границы: research/client-m5-checkpoint.md, client455-graphics-runtime.md.
М6 в работе: clocks,packet8/5,CLand time и локальные time/real_time команды восстановлены.
1443clock+314map-time native checks/12FP modes;432command cases/2628checks и20actual
CHAT_INFO input/access/lifecycle checks прошли. Команды также управляют реальными
weather states на GPU. research/client455-time-commands-source.md. Затем восстановлены
8legacy Character functions,включая полный InitVertex:245binding+6732InitVertex checks/
144cases/12FP modes,4COFFtests,2actual LoadRealData→source calls в полном клиенте.
Это CPU comparison с test-only COM capture,не Character GPU acceptance.
research/character-init-source.md. Следом455MESH08/data/layouts перед D3D9 port:
найден отдельный loader для новых моделей. MESH08format module восстановлен:
858real files/12090meshes прошлиlossless roundtrip,6304native checks standalone/
full-client. Normal runtime model-loader ещё не переключён;следом materials/bones/
GPU state. research/client455-mesh08-format.md. Затем восстановлены четыре455CPU
parent/bone bindings:2237checks/12real mesh-skeleton pairs/393meshes standalone/
full-client. Normal loader не подключён; metadata/materials/sharedGPU ещё открыты.
research/client455-mesh-bindings-source.md. Остальные subsystems/chat/calendar/lighting открыты.
Далее sourceconstructor/header matrices/material request flow455 прошли14562checks/
12real files/393parts/12FP modes standalone/full-client. Матрицы используют именно
pinned D3DX9_36;actual TextureManager/sharedGPU/normal loader ещё открыты.
research/client455-mesh-runtime-source.md.
Нормальный WinMain ещё не запускался; D3D8 база ещё не восстановлена до D3D9 эталона.
M9 — полная приёмка455 без модернизации графики — остаётся открытым.

## Структура

- `docs/` — аудит, порядок работы, план следующих этапов.
- `config/` — пути и подготовленные примеры интеграций без секретов.
- `scripts/` — воспроизводимые проверки окружения и материалов.
- `inventory/` — манифест исходников, ключевых бинарников и сводка каталогов.
- `research/` — проверяемые выводы о функциях и форматах.
- `work/` — локальные копии бинарников, исходников и базы IDA; исключены из Git.
- `artifacts/` — большие выгрузки и результаты сборки; исключены из Git.
- `local/` — временные файлы и машинные настройки; исключены из Git.

Начать с `docs/environment-audit.md` и `docs/next-steps.md`.
Актуальная память: `docs/project-memory.md`; дорожная карта: `docs/roadmap.md`.
Критерии полноты клиента: `docs/client-acceptance.md`.
Аудит 14 проектов и первая сборка: `docs/build-audit.md`.
Повтор проверки входов сборки: `scripts/Invoke-Python.ps1 scripts/audit_build.py`.
Повторная инвентаризация: `scripts/Invoke-Python.ps1 scripts/inventory.py`.
Проверка GoMMO MCP: `scripts/Invoke-Python.ps1 scripts/probe_gommo.py`.
Проверка IDA MCP: `scripts/Invoke-Python.ps1 scripts/probe_ida_mcp.py --configured`.
Проверка VS/MSVC x86: `scripts/Invoke-Python.ps1 scripts/probe_msvc.py`.
Основная сборочная среда — VS 2026 Professional; VC6 не является обязательным этапом.
Настройка и использование IDA: `docs/ida-mcp.md`.
Universal Modder: 13 навыков и CLI um, см. `docs/universal-modder.md`.

Оригинальные каталоги перечислены в `config/paths.json`; скрипты аудита читают их,
но ничего в них не изменяют. Рабочие копии клиентского кода и движка подготовлены
в work/client-build с проверкой SHA-256; исходные байты и кодировки сохранены.
Начало переноса: research/client-port-first-build.md.
