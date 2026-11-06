# Startup455: глубина цвета, ошибки Create и настоящее устройство

2026-11-06, Asia/Yakutsk. Участок M6 номер043. Восстановлены два подтверждённых
startup контракта455 и проверена настоящая normal D3D инициализация. Это ещё
не полная startup/gameplay приёмка: M6/M6F/M7/M9 открыты.

## Эталон и найденные отличия

Reference PE x86, base0x400000. Current SHA-256:
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b.
Backup SHA-256:
46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
Входные EXE не исполнялись. Ranges/RVA/длины/SHA обоих эталонов закреплены
в inventory/client455-startup-contracts-reference.json. Raw decompile/disasm
под artifacts/client455-startup, reference IDA1c8c37b3 closed/saved=true.

| Контракт455 | VA / RVA | Размер |
|---|---|---|
| WinMain | 0x7D04E0 /0x3D04E0 | 0x7EC |
| Установка renderBits32 | 0x8ED5A0 /0x4ED5A0 | 11 |
| Device wrapper | 0x8EDAB0 /0x4EDAB0 | 0xF7 |
| Setup/Language reader | 0x7D2880 /0x3D2880 | 0xDA |
| `.\\R3Engine.ini` | 0xAB04F8 /0x6B04F8 | 15 |

Вызов на месте старого ForceFullScreen не устанавливает fullscreen: две
инструкции8ED5A0 записывают render depth DWORD1157CA8=32 и возвращаются.
Fullscreen хранится отдельно в1157CB0 и читается wrapper. Поэтому перенос
старого ForceFullScreen с записью mbFullScreen=TRUE менял подтверждённое
поведение455 и не позволял штатной оконной настройке работать.

Wrapper8EDAB0 вызывает virtual Create, затем делает TEST EAX/JZ. Любой
ненулевой результат вызывает exit(0), включая положительный S_FALSE. Только
ноль продолжает assignment input flag и возвращает0. Legacy wrapper
игнорировал результат Create. Две исправленные области подтверждены
инструкциями; весь wrapper этой работой не объявлен восстановленным.

## Source и сохранение прежней базы

build_client455_engine_startup.py создаёт отдельный проект под
work/client455-port/startup-engine. Он использует67проверенных исходных units
033, заменяя только две рабочие CPP-копии: r3enginekernel и r3d3dwrapper.
Первая сохраняет public имя ForceFullScreen, но реализует подтверждённую
запись32бит без изменения mbFullScreen. Вторая проверяет Create!=S_OK и
вызывает exit(0). Исходники033 и его R3Engine455.lib сохранены по SHA.

Новый архив R3Engine455Startup.lib выбран normal consumers и полной линковкой.
Старый engine archive не примешивается; MAP подтверждает providers двух
исправленных функций. Генерация/базовые и новые source hashes, CMake, library
и build log закреплены в inventory/client455-startup-engine-build.json.

CPU protocol test использует настоящий новый wrapper и test-only subclass,
который возвращает заданный virtual Create результат без окна. S_OK продолжает
вызов и сохраняет flag; S_FALSE иE_FAIL завершаются0, не доходят до следующего
statement и выполняют atexit. Проверка color32 сохраняет исходный fullscreen
FALSE иTRUE. Это протокол вызова/выхода, не подмена actual graphics acceptance.
Тот же compiler измеряет offsets собственной source class для read-only
debugger inspection. Они не накладываются на layout эталона455.

## Реальное окно и D3D

Полная собственная PE:1966080байт, x86/base0x400000/entry RVA0x149510, SHA-256
51fd3f49ab867f7178a548dcd7058276fb4f1ac4983ab5feac808db863df5fd1.
Линковка успешна, unresolved0. Текущий результат в normal-link.json.

Точная копия запускается под собственным debugger из отдельного lab:
work/m9/51fd3f49/device-startup002. К DLL/WaveList/own ini042 добавлены реальные
Grass1.vsh/grass1.vso иSystem/console.jpg. Production mode не переписывается
debugger: код сам оставляет ini fullscreenFALSE и устанавливает32бит.
Debugger передаёт SW_HIDE startup request; видимость/focus/input и вся UI
система этим прогоном не принимаются.

Собственные точки WinMain RVA0xB3CD0, afterSound0xB3CED,
afterD3D0xB3D00. Последняя непосредственно следует за настоящим CALL
InitR3D3D, что повторно проверяется по MAP и rel32 operand. Возвращён
HRESULT0, прочитаны ready1, windowed1, ненулевые HWND иdevice. Следующий
CMainApp::Create ещё не вызывается. Временные breakpoint bytes находятся
только в памяти собственного ребёнка; дисковая PE не меняется.

Наблюдён planned exitE0434200; живого child после проверки нет. Обработанные
first-chance events остались40080201/E06D7363/406D1388; second-chance нет.
Нормальный shutdown этим ранним stop не проверен. Raw trace/plan/inputs —
ignored work/, hashes/markers/state в device-startup-native.json.

Короткие CUnity/ANI/BBX, renderer/color/effect/shadow, clock/table/accounting
сценарии прошли с новым архивом. Предыдущие кадры совпали, COM/Dmalloc0.
Большие неизменённые suites не повторялись. EarlyCRT/Miles42 также проверен
на новом exact output. Checkpoints сохраняют PARTIAL и M9OPEN.

## Новые открытые startup границы

В455 WinMain сначала настраивает nation/language и получает launcher data,
выбирает language, строит путь FG_CB.ini через5E5B50 и создаёт/подключает
клиентскую сеть. Только после этого идут engine, WaveList и отдельный
BGMList.spt, затем device иCreate7D18B0. Legacy normal main не повторяет
этот порядок. Сходный ранний путь не означает полного соответствия startup455.

SetupNation7D2880 читает Setup/Language из `.\\R3Engine.ini`, вызывает
mapper7D29C0/setter7D1110 и отвергает index>11. Эти managers/выборы пока
не перенесены. Root filter файлы не надо выдавать за отсутствующие данные:
кандидаты лежат вko-kr, но правильный locale/root contract ещё впереди.

Camera branch wrapper455 также сбрасывает console index18. Старая таблица
имеет лишь17entries, поэтому прямое добавление такой записи вызвало бы OOB.
Эта ветка не восстановлена; тесты используют обычный mbStartCameraFALSE.
Полный launcher/nation/locale/BGM/Create/UI/network/gameplay, device reset,
fullscreen/show behavior и normal shutdown остаются открытыми.

## Продолжение044 и повтор

Восстановить точный language/nation/data-root контракт, затем normal Create
с настоящими клиентскими ресурсами и launcher expectations. Сетевую часть
восстанавливать как клиентский контракт, без изменения или сборки серверов.

Через scripts/Invoke-Python.ps1: audit_client455_startup_contracts.py,
build_client455_engine_startup.py, probe_client455_startup_contracts.py,
probe_client455_normal_consumers.py, link_client455_normal.py,
audit_client455_startup.py, probe_client455_startup.py,
probe_client455_device_startup.py, checkpoint_client455_device_startup.py.
Затронутые короткие регрессии — по новым библиотекам. Подробные manifests:
startup-contracts-reference/native, startup-engine-build, device-startup-native/
checkpoint вinventory/. Production normal sources/engine033 и originals
проверяются отдельно от новых derived copies.
