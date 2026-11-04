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
GPU state. research/client455-mesh08-format.md. Остальные subsystems/chat/calendar/lighting открыты.
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
