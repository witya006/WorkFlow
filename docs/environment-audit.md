# Аудит окружения — 04.11.2026

Дата по Asia/Yakutsk. Машинные отчёты используют UTC. Это снимок состояния,
а не непрерывный мониторинг. Работы выполнены в `E:\RFOnlineTrash\Source\WorkFlow`.

## Итог

Работа исключительно над клиентом и его зависимостями. Серверные сведения ниже —
история проверки инструментов/инвентаризации, не задачи и не блокеры клиента.
Серверные исходники разрешены для чтения как справочник, без изменений и сборки.
Целевой результат — исходники RF_Online.bin с полным функционалом и поведением
закреплённого клиента 455; степень соответствия пока не установлена.

Рабочая область и локальный Git подготовлены. GoMMO MCP работает через stdio.
IDAPython восстановлен на Python 3.11.16; IDA MCP установлен, зарегистрирован в Codex
и проверен через stdio и нативные инструменты чата после перезапуска: 669 функций
и декомпиляция получены на рабочей копии PE x86. Установлен universal-modder:
13 навыков с валидными метаданными и работающий CLI um 0.2.0.
Установлена и проверена Visual Studio Professional 2026 18.11.3: MSVC x86,
Windows SDK и CMake. Основной путь — перенос клиента под современный MSVC;
VC6 остаётся резервным инструментом. DirectX 8.1b SDK проверен и подключён локально;
R3Engine собран под VS 2026 x86 с двумя успешными чистыми пересборками.

Статический аудит сборки завершён: 14 DSP / 14 DSW, 41 конфигурация, 832 SOURCE,
6 отсутствующих записей в CameraExporter/R3MapExp. Все 180 C++ клиента уже компилируются
с диагностическим восстановленным Character.h. Линковку останавливает JpegLibMT.lib;
дальше остаются Character inline/варианты библиотек и CRT.
Область работы уточнена: исключительно клиент. Выбор LoginServer отозван;
первая цель клиентской зависимости — R3Engine RTMovie Release, затем RF_Online. Детали: [build-audit.md](build-audit.md),
этапы: [roadmap.md](roadmap.md), актуальная память: [project-memory.md](project-memory.md).

## Инструменты

| Компонент | Проверка | Результат |
|---|---|---|
| ОС | Environment.OSVersion | Windows NT 10.0.19045; редакция не определялась |
| Git | git --version | 2.53.0.windows.3; работает |
| GitHub Desktop | процесс и путь | запущен, каталог app-3.6.10 |
| IDA Pro | реестр и FileVersion | 9.2; файл 9.2.25.0908 |
| Hex-Rays | IDAPython и реальный MCP-вызов | плагин 9.2.0.250908 работает; декомпиляция функции PE x86 подтверждена |
| IDAPython | реальный запуск скрипта | Python 3.11.16; 669 функций, декомпиляция успешна |
| IDA MCP | initialize, tools/list, idb_open, list_funcs, decompile | установлен ida-pro-mcp 2.0.0, 66 инструментов; основные вызовы прошли |
| GoMMO Studio | initialize и studio_status | 2.0.1, несмотря на папку/README 1.3.0 |
| Python для аудита | прямой запуск | 3.12.14 из комплектного runtime Codex |
| Python для IDA | idapyswitch и запуск внутри IDA | 3.11.16, постоянная установка uv в AppData/Roaming/uv/python |
| Системный Python 3.10 | реестр и проверка файла | запись есть, C:\Program Files\Python310\python.exe отсутствует |
| Python 3.14 | цель launcher и проверка файла | launcher ссылается на отсутствующий pythoncore-3.14-64/python.exe |
| Visual Studio | vswhere и реальная сборка | Professional 2026 18.11.3, установка завершена, перезагрузка не требуется |
| MSVC | VsDevCmd x86 и компиляция | toolset 14.51.36231, compiler 19.51.36260.0; x86 проверен |
| MSBuild / CMake | реальная конфигурация/сборка | 18.11.1.51303 / 4.3.1-msvc1, генератор Visual Studio 18 2026, Win32 |
| Windows SDK | VsDevCmd и Win32 smoke | 10.0.26100.0, заголовки и линковка проверены |
| VC6 / DX8.1 SDK | стандартные каталоги и установленные программы | не обнаружены; переносные установки на других дисках не исключены |

Наличие Visual C++ Redistributable и Visual Studio Installer не означает наличие
компилятора. PATH не менялся. IDAPython явно привязан к найденной установке 3.11.16;
остальные Python-установки не заменялись. MCP изолирован в local/ida-mcp-venv.

## GoMMO MCP: подтверждено

- У запущенного приложения найден локальный instance descriptor.
- В момент проверки адрес: `http://127.0.0.1:64359/mcp`, версия 2.0.1.
- Порт динамический. Токен из descriptor не копировался в рабочую область.
- Использован официальный stdio bridge: `gommostudio.exe -mcp`.
- Успешны `initialize`, `notifications/initialized`, `tools/list`, `studio_status`.
- Сервер объявил 663 инструмента. Это проверка обнаружения, а не испытание каждого.
- `studio_status` показал пустой список документов; клиент и проект не открывались.
- Изменения ассетов, Install, запуск сервера и публикация не выполнялись.
- Схемы и результат: `inventory/gommo-mcp.json`.

В нативном наборе инструментов текущего чата GoMMO не зарегистрирован.
Доступ через наш stdio-клиент уже подтверждён. Пример для последующего подключения
Codex сохранён в `config/codex-mcp.example.toml`; глобальная регистрация GoMMO не добавлялась.

## IDA и MCP: восстановлено после первоначального аудита

На момент начала аудита процесса IDA и слушающего MCP-сервера IDA не было.
До восстановления в пользовательском config.toml Codex не было регистрации
IDA/GoMMO; mcp.json LM Studio не содержал настроенных серверов.

Проверены:

- `C:\Program Files\IDA Professional 9.2\plugins`;
- `C:\Users\Admin\AppData\Roaming\Hex-Rays\IDA Pro`;
- `C:\Users\Admin\AppData\Roaming\Hex-Rays\IDA Pro\mcp\instances` — пусто;
- стандартные `.idapro` и `AppData\Roaming\IDA Pro` — отсутствуют;
- несколько обычных мест расположения `ida-pro-mcp` — не найдены.

Повторный поиск также охватил Downloads, Documents, uv/tools и RFOnlineTrash.
Рабочая старая установка IDA MCP не обнаружена; в найденном Python пакет
ida-pro-mcp отсутствовал. Поэтому выполнена новая установка совместимой реализации.

Скрипт `scripts/probe_ida.py` копирует старый `LoginServerSR.exe` в `work/ida-smoke/`
и запускает только статический анализ через idat.exe. Сам серверный EXE не запускается.
В песочнице IDA завершилась с кодом 2 без диагностического лога. Повтор вне песочницы
завершился с кодом 1 и дал диагностический лог:

```text
failed to load Python runtime: skipping IDAPython plugin
Hex-Rays Decompiler plugin has been loaded (v9.2.0.250908)
.../scripts/ida_smoke.py: unknown file extension
```

Это исторический результат первого аудита. При восстановлении idapyswitch обнаружил
рабочую установку `C:\Users\Admin\AppData\Roaming\uv\python\cpython-3.11.16-windows-x86_64-none`.
После явной привязки к её python311.dll скрипт IDAPython завершился с кодом 0,
получил 669 функций и выполнил декомпиляцию. Переустановка Python не понадобилась.

Установлены:

- ida-pro-mcp 2.0.0, commit `c133c3853faa111a9b00ee615c013b720d0c4acd`;
- зависимости idapro 0.0.12 и tomli-w 1.2.0 в `local/ida-mcp-venv`;
- GUI-плагин в `%APPDATA%\Hex-Rays\IDA Pro\plugins`;
- stdio supervisor в секции `[mcp_servers.ida_mcp]` пользовательского Codex config.

Последняя проверка использовала команду непосредственно из зарегистрированного
Codex config. Успешны initialize, tools/list (66 инструментов), idb_open,
server_health, list_funcs (все 669 функций), decompile и idb_close с сохранением базы.
Пример: `sub_401E60`, VA `0x401E60`, RVA `0x1E60`, image base `0x400000`.
SHA-256 входа: `9874cbada393244db1d02c1549eb02434f6d376e7cea33fc97e8424bfb1cc7a2`.
Пакет сообщает версию 2.0.0, MCP serverInfo — 1.0.0; обе версии зафиксированы.

Отчёты: `inventory/ida-runtime.json`, `inventory/ida-mcp-tools.json`,
`inventory/ida-mcp-verification.json`. `pip check` не выявил конфликтов зависимостей.
Команда `codex mcp list --json` подтверждает `ida_mcp: enabled=true`.
Рабочая база: `work/ida-mcp-smoke/LoginServerSR.exe.i64`.
Запуск проверял статический анализ; серверный EXE не исполнялся.

После перезапуска Codex появились 66 нативных инструментов IDA. Через них проверены
idb_open, server_health, list_funcs (669 функций), decompile (полный код sub_401E60)
и idb_close. Состояние ok, auto_analysis_ready=true, hexrays_ready=true.
Сессия закрыта без сохранения изменений. Доказательства:
`inventory/ida-native-verification.json`. Подробности: `docs/ida-mcp.md`.
GoMMO по-прежнему доступен через stdio-проверку, его глобальная регистрация не менялась.

## Universal Modder: установлен и проверен

Источник: https://github.com/rehan-remade/universal-modder,
commit `9811709d950979f1b5012dddf10b7ec122d7e95e`.
Все 13 навыков установлены skill-installer в `C:\Users\Admin\.codex\skills`.
CLI um 0.2.0 установлен через uv tool install --editable из закреплённой локальной
копии в local/universal-modder-install, вместе с локальной базой знаний.

Все навыки прошли quick_validate.py. Единственная адаптация: `<game>` заменён на
`this game` в description навыка game-recon, поскольку валидатор Codex не принимает
угловые скобки. Тело навыка не изменено; остальные файлы совпадают с источником.

Проверены um --version, --help, поиск базы знаний и um scan RFOnline --json:
проиндексировано 30 311 файлов. Сканер сообщил unknown native engine и признаки
nProtect GameGuard. R3Engine по имени не распознан; RF_Online.bin не перечислен
среди исследованных EXE. ASI loader — эвристика, а не доказательство мод-загрузчика.
Поиск RF Online выдаёт в том числе нерелевантные материалы о Red Faction.

Игра не запускалась, клиент не менялся. Генерация через fal/Sprixen/Voidless,
3D-рендер, управление игрой и видео не проверялись; ffmpeg и Blender в текущем PATH
не обнаружены. Внешние MCP и API-ключи не подключались. Это установка навыков и CLI,
а не полного плагина с fal MCP. Навыки доступны для выбора со следующего сообщения.

См. `docs/universal-modder.md` и `inventory/universal-modder-installation.json`.

## Материалы RF Online

| Каталог | Файлов | Байт | Что зафиксировано |
|---|---:|---:|---|
| Старые исходники | 962 | 17 763 094 | SHA-256 каждого файла |
| Клиент RFOnline | 30 554 | 11 401 335 169 | сводка дерева и хеши выбранных бинарников |
| rf455-v0.4.0 | 216 | 1 129 623 002 | сводка дерева и хеши выбранных бинарников |

В старом комплекте: 329 cpp, 463 h, 14 dsp, 14 dsw. Найденные проекты включают
движок, клиент, служебные серверы и утилиты; полнота игрового ZoneServer не установлена.
Версия «0.7 / 2004» пока является описанием пользователя, а не результатом атрибуции.

`RF_Online.bin` и его backup — PE x86. `gameserver.exe` из пакета 455 — PE x64.

- Текущий клиент: `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`.
- Backup: `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
- Backup совпадает с SHA-256 клиента, указанным в README серверного пакета.
- Происхождение различий текущего клиента и backup ещё не установлено.

Манифесты: `inventory/legacy-files.json`, `inventory/reference-binaries.json`,
`inventory/roots.json`. Полный хеш-манифест 11.4 GB ресурсов и резервное копирование
всех игровых данных в этот этап не входили. Базы, конфиги с паролями и игровые
ресурсы не добавлялись в Git.

## Границы проверки

Полная сборка клиента, восстановление протокола,
распаковка клиента и изменение игровых файлов не выполнялись. Статический аудит
входов/зависимостей всех проектов выполнен; пригодность SDK/ABI и фактическая
линковка ещё не подтверждены. Восстановлены
IDAPython и MCP; реальная проверка выполнялась на старом LoginServerSR.exe.
Полный анализ клиента 455 через IDA пока не выполнялся.
Свободно на E: около 1776 GiB на момент проверки.

## Дополнение: аудит собираемости 2026-11-04

- inventory/build-audit.json содержит конфигурации, SOURCE, include-кандидатов,
  библиотеки, RC-ресурсы, SHA-256 проектов/.lib и сравнение серверных деревьев.
- 12 проектов имеют все перечисленные SOURCE; все DSW разрешают DSP.
  Это не означает, что 12 проектов уже собираются.
- Вложенные AccountServer/LoginServer совпадают с внешними по исходникам/проектам;
  различаются только .ncb/.opt/.plg. Канонический каталог — внешний RF_Server.
- 26 .cpp не входят ни в один DSP. Полный ZoneServer-проект и исходная БД не найдены.
  MySQL-схемы GoMMO не считаются подтверждённой заменой исходной серверной БД.
- Уточнение ADO: четыре #import есть в непроектных обёртках; серверные проекты
  используют ODBC (rfnewdatabase.h/cpp). msado15.dll найден на хосте в обоих стандартных
  Program Files-каталогах; совместимость с будущей VM не проверялась.
- cl/msdev/nmake/rc/link не найдены в PATH; поиск cl/msdev/nmake под RFOnlineTrash пуст.
  Windows Kits в проверенном стандартном каталоге не обнаружен.
- Пять тестов сканера прошли. Все 962 исходных файла сохранили прежние SHA-256.
  Оригиналы и конфигурации системы не менялись в этом этапе.

## Проверка VS 2026 после установки

Проверка: `scripts/Invoke-Python.ps1 scripts/probe_msvc.py`.
Отчёт: inventory/msvc-verification.json. Генерируются только собственные smoke.cpp
и CMakeLists.txt в work/msvc-smoke. Скомпилированы windows.h/Win32 API и static_assert
32-битного указателя; линковка/запуск завершились с 0, вывод x86 Win32 OK.
SHA-256 и entry point RVA тестового PE x86 записаны в отчёте.
Сырые журналы в artifacts/msvc-smoke не включены в Git.

В песочнице MSBuild FileTracker завершался с E_ACCESSDENIED; тот же тест вне
песочницы прошёл. Это не неисправность установки. Глобальный PATH не менялся:
используется VsDevCmd с host x64 / target x86. Также найден toolset 14.44.35207,
но он не испытывался. Проверка не охватывает RF-код, старый DirectX и ABI .lib.

Исторические записи выше о ненайденных компиляторах относятся к состоянию до
установки VS. Блокер отсутствия современного компилятора закрыт.

## Начало клиентского переноса

Подготовлены 492 побайтово проверенные копии RF_Client/R3Engine. Современный проект
движка (58 C++/1 RC) успешно сконфигурирован. Первая компиляция завершилась с 1:
12 COFF x86 объектов получены, отсутствуют DirectX 8 headers, есть C2065/C7732 в
двух legacy-файлах. Библиотека ещё не собрана. Инвентарь client-build-inputs.json и
client-build-result.json, подробности research/client-port-first-build.md.
Отсутствие DirectX-заголовков теперь подтверждено компилятором, а не только поиском.

## Документация интеграций

- [GoMMO: stdio bridge и studio_status](https://oldschoolops.com/docs/gommo-studio/automation/ai-assistants/).
- [Codex: настройка MCP](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).
- Локально: `IDA Professional 9.2/README_python3.txt`, справка `idapyswitch`,
  `docs/user-guide/configuration/command-line-switches.html`.

Результаты локальных запусков имеют приоритет над устаревшим названием папки/README.

## M1 и закрепление клиентского эталона

M1 выполнен по compile/archive: 58 COFF x86 объектов, R3Engine.lib, две чистые
пересборки. Дальнейшие CRT/ABI/поведение проверяются отдельно. DirectX 8.1b SDK имеет
действительную подпись Microsoft и архивный хеш; установщик не запускался.
Результаты: inventory/directx81b-sdk.json, client-source-patches.json,
client-build-result.json, research/client-port-m1.md.

Два клиентских файла отличаются 5 байтами; область ветвления и общий double
исследованы в IDA, собственная сессия закрыта с сохранением. Текущий клиент закреплён
эталоном по SHA-256 в config/client-target.json. Версионная константа не считается
доказательством атрибуции. Полный манифест ресурсов ещё не создан.

M4: 207 определений Character кешированы, 30 операндов инструкций проверены.
Диагностический Character.h: 56 layout assertions и 165 публичных decorated names
проверены; все 180 C++ клиента скомпилированы. Конструкторы/inline/STL ABI ещё открыты.
Отдельно собран настоящий /MT R3EngineMT.lib; 180+58 COFF x86 /MT проверены.
LNK2038 устранён корректной сборкой, genuine DX8 .lib подключены. Последняя линковка:
LNK1104 JpegLibMT.lib. RF_Online.bin пока нет. Старый GetAlpha link-only probe ранее
выявил std::_Xlen/_Xran. Input EXE/DLL не запускались. research/client-port-m4.md;
inventory/client-character-diagnostic.json, client-mt-variant.json,
character-header-recovery.json. Четыре проверки COFF прошли.
