# Страна, корень данных и следующий участок обычного Create — 044

06.11.2026. M6, частичный результат. M6F/M7/M9 открыты.

В обычный WinMain добавлен реальный выбор страны из `[Setup] Language` в
`.\R3Engine.ini`, до инициализации движка. Восстановлены сравнение имени и
построение `.\DataTable\<folder>`. Собственная полная сборка затем прошла
ранний Create: Character создан и привязан к тому же устройству D3D9, что и
приложение. Процесс остановлен перед `_CreateCharDataMgr`, до старых читателей
игровых таблиц. Полный Create, языковой пакет и весь запуск 455 ещё не приняты.

## Эталон и подтверждённые контракты

Только статический анализ собственных копий. Входные EXE не исполнялись.

- Current SHA-256 `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`.
- Backup SHA-256 `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
- Оба x86, image base `0x400000`. Указанные тела совпали в обоих PE.

| Назначение | VA | RVA | Размер |
|---|---|---|---|
| Имя страны → WORD | 7D29C0 | 3D29C0 | 179h |
| Setup/Language, проверка страны | 7D2880 | 3D2880 | DAh |
| Папка/CRT locale/шрифт/кодовая страница | 7CFB10 | 3CFB10 | 571h |
| Возврат корня данных из объекта | 5E5B70 | 1E5B70 | 1Bh |
| Запись параметров шрифта | 8C5A80 | 4C5A80 | 47h |

SHA каждого тела и RVA строк: `inventory/client455-nation-paths-reference.json`.
IDA session `5f01f0d1` закрыта с сохранением; выгрузки в
`artifacts/client455-locale/`. Это не отдельная библиотека с оригинальным ABI:
новый модуль имеет собственные явные типы и интерфейсы.

`7D29C0` использует `_mbscmp`: сравнение чувствительно к регистру. Неизвестное
имя даёт WORD FFFF. `7D2880` читает буфер 128 байт; WORD >11 отвергается.
Число 11 этим mapper не порождается; default языкового selector соответствует
Корее. При неуспешном чтении опубликованное состояние не заменяется.

| ID | Настройка | Папка | CRT locale | Шрифт | Charset |
|---|---|---|---|---|---|
| 0 | Korea | ko-kr | Korean_Korea | B1 BC B8 B2 C3 BC | 129 |
| 1 | Brazil | pt-br | Portuguese_Brazil | Arial | 1 |
| 2 | China | zh-cn | Chinese_China | SimSun | 134 |
| 3 | Europe | en-gb | English_United Kingdom | Arial | 1 |
| 4 | Indonesia | en-id | English_Indonesia | Arial | 1 |
| 5 | Japan | ja-jp | Japanese_Japan | MS Gothic | 128 |
| 6 | Philippines | en-ph | English_Philippines | Tahoma | 1 |
| 7 | Russia | ru-ru | Russian_Russia | Lucida Console | 204 |
| 8 | Taiwan | zh-tw | Chinese_Taiwan | MingLiU | 136 |
| 9 | USA | en-us | English_United Kingdom | Arial | 1 |
| 10 | Thailand | th-th | Thai_Thailand | Tahoma | 222 |

CRT locale/шрифт/charset сейчас сохранены как подтверждённые параметры, **их
применение ещё не восстановлено**. USA действительно использует UK CRT locale.
`setlocale(1,...)` здесь означает LC_COLLATE; не подменять LC_CTYPE. Затем
эталон сравнивает кодовую страницу с ETCAction, сохраняет параметры шрифта
9×12 и загружает NDLanguage. Успех построения пути не доказывает этот процесс.
Номер страны нельзя использовать как индекс старого массива из трёх языков.

## Реальная сборка и запуск

`scripts/prepare_client455_normal.py` переносит изменение только в рабочую
копию mainapp.cpp. Полная сборка: 182 клиентских объекта, 12 facade CPP,
20 canonical kernels; без CharacterMR и без `/FORCE`, 0 unresolved.
Производная библиотека движка 043 и исходная база 033 сохранены.

Собственная `work/client455-port/normal/build/RF_Online.bin`:

- SHA-256 `cb64af10cad3f527af015609f71ca0c7d300cce59aa3c2671bf0155aab384b88`;
- x86/base400000, 1 967 104 байт, entry RVA1496C0;
- WinMain RVA B3CD0, после sound B3CFA, после D3D B3D0D;
- остановка перед CALL `_CreateCharDataMgr`: RVA B33F9.

Адреса остановки теперь извлекаются из **декодированных инструкций текущего
собственного PE** и сверяются с MAP/реальным CALL target. Прежние фиксированные
WinMain+1D/+30 после изменения startup уже неверны. Аудит не запускает EXE.

Лаборатории с точной копией собственного PE и копиями настоящих входов:

- `work/m9/cb64af10/startup001`: CRT/WinMain/engine/Miles, sound return1;
- `work/m9/cb64af10/device-startup001`: ready1/windowed1/render32;
- `work/m9/cb64af10/create-startup001`: обычный Create после land/camera/network
  manager init прошёл `_CreateCharIF`, bone/mesh/animation/bounds managers.

В последнем процессе actual Character device `0x44d5da0` совпал с actual device
приложения; owner `0x439f160`. В trace наблюдался реальный опубликованный
`.\DataTable\ko-kr`. Для Character переданы 12 закреплённых SHO; исключения
shader init не возникли. Это доказательство раннего normal owner lifecycle,
не игрового кадра и не проверки всех результатов отдельных manager Create.

Проверка исходного клиентского networking перед этим запуском: Create вызывает
SetNetSystem/SetProcess, при m_bServer=FALSE не вызывает InitAcceptSocket;
Connect является отдельным последующим методом. Аккаунты/адреса серверов в lab
не задавались, connect/игровой обмен не выполнялись. Серверные проекты не трогались.

Отладчик запускает только собственный child, breakpoint восстанавливает его
исходный байт; EAX/ветвления/результаты production функций не подменяются.
SW_HIDE — запрос для lab, не приёмка поведения показа окна. В конце наблюдён
плановый exit E0434200. Три first-chance события runtime обработал; необработанных
исключений не было. Ни одного процесса или IDA session не оставлено работающим.

## Проверка и продолжение

Независимая fixture построена из строк обоих PE. Native проверка production
модуля покрывает 11 стран, реальные WinAPI profile reads, регистр, неизвестное
имя, отсутствие ключа, усечение длинного ввода и повторное чтение после ошибки.
Короткие ANI/BBX/model/effect/shadow/clock/accounting сценарии прошли с текущими
библиотеками; прежние кадры сохранились, COM/Dmalloc balance0. Неизменённые
большие исторические наборы не повторялись.

Воспроизведение через `scripts/Invoke-Python.ps1`, по порядку:

1. `audit_client455_nation_paths.py`, `probe_client455_nation_paths.py`.
2. `prepare_client455_normal.py`, `build_client455_normal.py`,
   `probe_client455_normal_consumers.py`, `link_client455_normal.py`.
3. `audit_client455_own_entry.py`, `audit_client455_startup.py`,
   `probe_client455_startup_contracts.py`, `probe_client455_startup.py`.
4. `probe_client455_device_startup.py`, затем тот же скрипт с `--create`.
5. `checkpoint_client455_nation_paths.py` и затронутые scoped checkpoints.

План отладчика в device/Create режиме содержит 11 DWORD hex: state-fullscreen
RVA, state-renderbits RVA, mainApp RVA, ready/window/device/windowed offsets,
after-sound RVA, after-D3D RVA, g_ifCharIF RVA, Character-device offset.
Последний offset0 измерен собственным компилятором; не original ABI overlay.

Следующий участок045 — завершить реальный language/data bootstrap перед UI:
ETCAction country factory/провайдер кодовой страницы, CRT/font и NDLanguage
603130 с настоящим EDF reader5EEC00/5EE900/5EEB90. Затем normal data readers/
Create/UI/launcher, порядок client network, BGM, lifecycle/shutdown. Старые
таблицы нельзя признавать совместимыми по имени или насильно продолжать их
чтение; подтверждать формат/потребителей 455. Полнота задаётся
`docs/client-acceptance.md`; этот результат её не заменяет.
