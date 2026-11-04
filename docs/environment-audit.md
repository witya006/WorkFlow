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
с диагностическим восстановленным Character.h. JPEG 6b/Miles подключены.
Получена полная diagnostic RF_Online.bin и успешная чистая пересборка, unresolved нет.
Выбранные 455 ветки имеют отдельные flags/ledger, исходные legacy branches сохранены.
Это не проверка запуска/полного поведения 455. Подробности research/client-first-build.md.
Последующее M5: helper loader455 найден, три отличия перенесены отдельным flag.
Обычная ревизия собрана, отдельный own lab entry полного проекта выполнил загрузку
140 реальных файлов/97 543 записей и CPU transforms/bbox;12 fixtures,2 546 779 checks,
4 import-parser tests. В lab игровые DLL отложены и не загружались. Обычный игровой
запуск/LoadLevel не проверены. Последующее: две x87 math функции восстановлены
с совпадением всех инструкций455, проверены в обоих linked clients и338 native
checks/12FP modes. Повтор140files после выравнивания Release options успешен,
2 546 931checks, FP control0x027F. Weather source перенесён:2слоя,R3X/text config,
load/release/update/draw split,interior/night.65real R3X +4fixtures/703checks,
37actual CPU lifecycle checks,285modern objects /MT. GPU/normal map/clock integration
остаются открыты. research/client455-weather-source.md.
Последующий resource audit:78RPK/3775files,70BSP+93EBP,20weather assets закреплены
с SHA.8parser tests прошли. Выявлены1067неверных size fields RPK и stale offsets
Dungeon00;455 использует offset-only fopen и sequential BSP reads соответственно.
На этом статическом этапе Source VFS/end ещё отсутствовал. Один weather path missing для
трёхTower R3X, directory component не найден во всех162RPK indexes. Игровые EXE/DLL
не запускались; сборки не менялись. research/client455-map-resources.md.
Следующий цикл восстановил RPK source/group/fopen/exists и particle end:18 907native
module checks на3775members/78RPK и30actual full-project archive/SPT/R3X checks.
Обе сборки успешны,286modern x86 /MT objects; selected compiled branches и DDS mask
проверены.703weather checks прошли на новой lab revision. Normal LoadLevel/GPU не
выполнены. MSBuild FileTracker sandbox E_ACCESSDENIED устранён escalation того же
build command. research/client455-resource-io-source.md.
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

## Последующее M5: настоящий GPU и map path

M5 закрыт для первого helper-data участка, gate inventory/client-m5-checkpoint.json.
Own entry полного client project выполнил настоящий D3D8 HAL на RTX2080Ti, загрузку/
отрисовку5RPKentities и5real particle scripts, CLevel::LoadLevel/FrameMove/render/release
для lobby и Platform01.13cases/321checks,0warnings/errors, allocation и COM balance0.
Platform01:23helpers/8interiors и два weather layers15/500; inside/night stop,
outside/night start,outside/day stop проверены настоящим FrameMove. GPU BMP прочитаны
из backbuffer, hashes сохранены, кадры просмотрены. Control words027F→027F→007F;
map/particle/render/helper consumer не изменяют007F. Reference startup state неизвестен.
Sandbox HAL creation дал0x8876086A, тот же EXE вне sandbox прошёл без изменения source.
Game DLL delayed и не загружались; звук/сеть/normal WinMain/input EXE не запускались.
703weather/30resource/23 337targeted helper regressions прошли на final lab SHA
ece2acccb434ef06ee0aba3d35a15778f3bdf87e5b70589221f8f34732aed3ae.
Normal build a761c930... не менялся. IDA reference graphics analysis:3functions/6exact
instruction checks на обоих pinned PE; owned77bfa3a2 закрыта с save.
research/client455-graphics-runtime.md. D3D9/full Character/particles/clock/UI/network
и M6/M6F/M7/M9 открыты; M8 modernization не требуется.

## M6: численный clock455

Собственный x86 clock module восстановил8scalar functions и256byte clock prefix
из0x8B1F20/RVA0x4B1F20.773instruction bytes совпали в обоих pinned PE после
проверки absolute operands/constants.1275checks/12FP modes прошли standalone и
в полном lab клиенте. Normal retained2used routines/prefix,lab9; linked code,
constants и .CRT$XCU initializer KERNEL32.GetTickCount проверены в обоих EXE.
Обычный RF_Online.bin2440704bytes/entryRVA0x1BBAA0,SHA
f5f945160fe45255b9cea935cb3e27946a0a5ab531a18b1279abbd41164e18e5,не запускался.
Lab SHA bb441c5c3e393f98a298355b794e14bbb95d1efdd790c36e1356080d64c44e9b:
703weather/30resource regression checks и2real GPU cases/59checks на Platform01
прошли. Helper/interior/night states прежние,FP007F,release balance0;game DLLs отсутствуют.
287normal modern x86 /MT objects проверены; дополнительный61-й engine object —clock.
Уточнение:0x7E3E55 это console %time; настоящий clock map caller0x7C8B60.
Cached time/packet origin/CLand/console и full lighting ещё открыты.
research/client455-clock-source.md; inventory/client455-clock*.json/client455-time-callers.json.
M6/M6F/M7/M9 открыты. Historical M5 evidence сохранён отдельно и проверен --saved.

## M6: client map message8/5 → CLand time

Восстановлен selected source path client packet8/5,CLand timestamp/receipt tick cache
и successful map-load clock hook. Source overlays трёх client files,21behavior files
total; own MapTimeState16bytes не применяется как binary455layout. Критический130byte
numeric fragment0x7C8DC4/RVA0x3C8DC4 совпал с обоими pinned PE.314component/full-client
checks/12FP modes/UTC+JST; actual linked helper/CLand/packet object references проверены.
Own GPU entry выполнил реальный CNetMsgProcessor_Map8/5,CLand Create/LoadLevel(char*)
и public post-load hook, Platform01 FrameMove/render/CLand Destroy/UnloadLevel.
Synthetic timestamp43200 при UTC0 дал fractions0.5/0.5,mapDay1 для synthetic mapIndex12.
Это не full byte-index UI/camera/effects path и не root network/socket verification.
2GPUcases/66checks,0errors/warnings,allocation/COM balance0; FPU007F,frame просмотрен.
1275clock/703weather/30resource regressions и288modern x86 /MT checks прошли.
Normal2448896bytes,entryRVA0x1BBDF0,SHA
a1b9dd5d7e45313ef414d90dff198717e66bc5d58e5ed95bcb72fba601cf456a,не исполнялся.
Lab SHA ad3a17d3d54372c4a05962ae0088b3f44d3d96b438f0873e94c06317cae5f441.
Localtime32 old-CRT timezone/DST/invalid/Init domains,opaque fields/other consumers,
full CLand/console/lighting и M6/M6F/M7/M9 открыты. Owned IDA92d1827c закрыта/save.
research/client455-map-time-source.md; inventory/client455-map-time*.json.

## M6: local clock commands и actual input

Восстановлены time/real_time,grade>=1 input hook в actual CHAT_INFO::SendMessage и
real HMS set/get. Clock10scalar functions+256byte prefix:1037instruction bytes
совпали с обоими PE;1443checks/12FP modes standalone/full-client. Parser432ASCII cases/
2628checks/12FP modes,20actual input/access/history/lifecycle checks прошли:grade1
accepts,grade0 rejects. CNetworkMgr ctor/dtor/WSAStartup выполнены;Create/SetNetSystem/
Connect не вызывались,network processes0,соединений/отправки нет. Game DLLs отсутствуют.
Две команды в own graphics entry управляют actual Platform01 weather FrameMove:
2GPUcases/69checks,0warnings/errors,Dmalloc/COM balance0,FPU007F,23helpers/8interiors.
289modern x86 /MT,314map-time/703weather/30resource regressions прошли.
Normal2450432bytes,entryRVA0x1BC330,SHA
d656498a2465feec8c9b4fb44149f01e38aa8e4288e4cc9e4bb4c555ec490919,не исполнялся.
Lab SHA d19ea1193dbfd546e68eadb3332e145de3d42d83e5429155726c807cfd3a1c24.
Other local directives/full chat/GUI input/locale/calendar/lighting остаются открытыми.
Owned IDA1bf47ee9 закрыта/save;research/client455-time-commands-source.md.
Следующий critical path — Character sources/ABI перед D3D9; current header/import
contract использует IDirect3DDevice8. M6/M6F/M7/M9 не закрыты.

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
Диагностический Character.h: 67 layout assertions и 165 публичных decorated names
проверены; все 180 C++ клиента скомпилированы. Конструкторы/inline/STL ABI ещё открыты.
Отдельно собран настоящий /MT R3EngineMT.lib; 180+58 COFF x86 /MT проверены.
LNK2038 устранён корректной сборкой, genuine DX8 .lib подключены. JPEG 6b /MT прошёл
28 ABI сравнений и 2 точных golden decodes; 26 Miles импортов есть в 455 DLL.
Проверены 284 x86 /MT объекта. Diagnostic link и clean rebuild успешны.
Native собственный тест подтвердил: старый FILE EOF доступ Character не работает с UCRT;
classic CRT прошёл только этот частный тест. На том этапе RF_Online.bin ещё не был
получен; последующая полная сборка описана выше. Input EXE/DLL не запускались.
research/client-dependencies-m4.md и client-port-m4.md;
inventory/client-character-diagnostic.json, client-mt-variant.json,
character-header-recovery.json. Четыре проверки COFF прошли.

Последнее дополнение: адаптер 8 stdio API прошёл 1828 собственных native проверок и
3 теста COFF; инструкции/релокации 10 входных объектов сохранены. Runtime старых
двух Pattern/Item загрузчиков проверен на valid fixtures (49 checks). CObjectManager
constructor восстановлен; AnimationManager
получил empty-vector constructor + реальный Init. 3102 проверки реальных SDK операций
на unloaded records прошли. Реальные _Xlen/_Xran /MT exceptions прошли 770 сравнений
с classic system exports; aliases в тестах удалены. Link gaps в выбранной сборке закрыты.
Полный Character unwind/loaded data/render не проверен. Header: 67 layout assertions.
research/character-effects-and-exceptions.md.
Новое: SetTexPath/SetMipMap и empty renderer construction восстановлены; 18 ABI
byte checks, 8 instances/136 part managers, всего 3630 combined native checks прошли.
Последующее продолжение: 455 DrawCharacter calls под отдельным flag/ledger,
bounded legacy SetEffect bridge и 59 native checks с CPU mesh effect application.
Последующее продолжение: 455 logging и success->lobby edge перенесены отдельными
flags с сохранением legacy bodies. Нет заглушек CheckFiles/SendLog или _DEVELOPER_ bypass.
Native logger 14 cases/66 checks; полная сборка и clean прошли. 455 map/36-grade
effect behavior ещё не перенесён. research/client-first-build.md.
research/client-draw-and-legacy-effects.md.
Конструкторы используют реальные SDK Init, но исходный inline/sizeof не доказан.
research/character-setters-and-construction.md и inventory/character-setters.json.
research/character-managers.md и research/character-stdio-adapter.md.
Для завершения последней /Goal повторно получены две чистые сборки R3Engine x86;
runtime sections/relocations 58 объектов совпали. Хеши исходных PE/копий и 5 различий
повторно проверены, 140 SPT / 97 543 записи прошли round trip. goal-checkpoint.json.
Предыдущая ограниченная цель выполнена уведомлением о начале пункта 4.
Активная новая /Goal — M9, финальная приёмка клиента 455 без модернизации графики.
Полный клиент ещё не готов.
