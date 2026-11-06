# EDF и NDLanguage в исходниковом клиенте — 045

06.11.2026. M6, частичный результат. Исходниковый клиент теперь реально
загружает NDLanguage до engine startup. Корейский и русский варианты прошли
через обычный WinMain точной собственной полной PE; после корейского пакета
сохранился запуск D3D9/Character. Полные шрифт, текст/UI и M9 не приняты.

## Доказательства из 455

Current SHA-256 `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
backup `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
Оба x86, image base400000. Входные EXE не исполнялись. IDA session34ab1c2b
закрыта с сохранением. Raw pseudocode и цепочки factory/constructor/vtable
сохранены в `artifacts/client455-language/`; summary/RVA/SHA каждого тела —
`inventory/client455-language-reference.json`.

| Назначение | VA | RVA |
|---|---|---|
| Чтение из расшифрованного буфера | 5EE900 | 1EE900 |
| Конструктор EDF owner | 5EEC00 | 1EEC00 |
| LoadFile | 5EEC90 | 1EEC90 |
| Header/size/body/key reads | 5EED90 | 1EED90 |
| Payload transform | 5EEF00 | 1EEF00 |
| Key transform | 5EF000 | 1EF000 |
| NDLanguage initialization | 601EF0 | 201EF0 |
| Lead/trail position | 601F50/601FE0 | 201F50/201FE0 |
| Строка по индексу | 6023B0 | 2023B0 |
| NDLanguage loader | 603130 | 203130 |
| NDLanguage release | 603360 | 203360 |

EDF имеет 29 байт заголовка, DWORD длины payload, payload и 256 байт ключа.
Заголовок читается, но не проверяется как magic/version. Из encoded key для
чётного i вычитается `1<<((i+1)%8)`, для нечётного прибавляется; затем reverse256
и swap соседних байтов. Для payload из чётного байта вычитается
`key[(i+1)%256]`, к нечётному прибавляется. Арифметика modulo256.

NDLanguage payload: DWORD count, затем count записей `{DWORD id,DWORD bytes,
char text[bytes]}`. `6023B0` использует **индекс**, не id. На выходе за count или
при отсутствии owner возвращает пустую строку. Строки в реальных файлах уже
заканчиваются NUL; исходниковый reader не перекодирует и не дописывает их.
`601EF0` записывает codepage после успешной загрузки. `603360` очищает record
pointer, но сохраняет count/codepage. Lead/trail APIs сканируют байты до нужной
позиции с `IsDBCSLeadByteEx` сохранённой кодовой страницы.

Кодовая страница восстановлена через country factory8321E0 → country factory
virtual create(kind1) → ETCAction constructor/vtable → virtual slot76. Перенесён
только подтверждённый codepage kernel; семь полных factory providers не подменены.

| Страна | Codepage | Тело VA |
|---|---|---|
| Korea | 949 | 832970 |
| Brazil | 1252 | 82FBA0 |
| China | 936 | 82C9B0 |
| Europe | 1252 | 831DD0 |
| Indonesia | 1252 | 82D300 |
| Japan | 932 | 82E080 |
| Philippines | 1252 | 82D9B0 |
| Russia | 1251 | 82E730 |
| Taiwan | 950 | 82EDE0 |
| USA | 1252 | 82F4B0 |
| Thailand | 874 | 830920 |

Все slot pointers и18h-byte return bodies сверены в обоих PE. Country metadata
из044 не менялась: USA использует English_United Kingdom. `setlocale(1,...)` —
LC_COLLATE, не LC_CTYPE; не менять `_setmbcp` по предположению.

## Исходники и реальные данные

`scripts/native/client455_language.h/.cpp` — собственный owner с явными API,
не original private C++ ABI overlay. Читает EDF через CreateFileA/FILE_SHARE_READ,
сохраняет исходные байты текста, предоставляет positional get и lead/trail.
Временный decoded key очищается. Release освобождает records и сохраняет
count/codepage. Перед engine WinMain вызывает проверку CRT locale/codepage и
реальную загрузку `<dataRoot>\NDLanguage.edf`; на ошибке возвращается из WinMain
с сообщением LangPack reading failure. Actual font application пока отсутствует.

Проверены все9NDLanguage в предоставленной установке: ko-kr,pt-br,zh-cn,en-gb,
en-id,ja-jp,en-ph,ru-ru,zh-tw;44 095 записей. Korea6851/Taiwan6997, остальные
4321. Не делать вывод о равенстве версий или полного UI покрытия из счётчиков.
en-us/th-th NDLanguage здесь не найдены; не подставлять чужой пакет. Это известная
граница доступных входов для этих языков, не блокер остальных клиентских работ.

Python specification независимо расшифровывает файлы, разбирает записи и
повторно шифрует их в **побайтно равный исходный EDF**. Native production reader
сверяет decoded bytes/records с fixture и восстанавливает равный payload.
IDs/index distinction дополнительно проверен на непоследовательных и повторных
id; DBCS границы сравнивались с независимым Windows CharNextExA. Все11CRT locale
имён на этой машине дали именно ожидаемые codepages. Мелкие повреждённые входы,
нулевой count, отсутствие файла, диапазоны lookup и release также проверены.

Небезопасные исходные negative-size/overflow/OOM/failed-read domains не выданы
за совместимость: source проверяет длины/границы и ограничивает выделение.
Повторная успешная загрузка освобождает прежнее владение через RAII, в отличие
от утечки старого original allocation; исходные dangling-pointer/OOM последствия
такой утечки не сертифицированы. Нулевые длины/нетерминированные записи в реальных
fixtures не найдены; потребители произвольных таких строк ещё не приняты.

## Полная сборка и настоящий WinMain

182 client objects +13facade CPP +20canonical kernels, link0unresolved, без
CharacterMR и без `/FORCE`. Engine043/база033 сохранены. Собственный RF_Online.bin:

- SHA-256 `1fc267d5ebe214dda8cfaa1b3b456f01ddb78848ec8c18899db1a9c411b17bc1`;
- x86/base400000,1 998 336байт,entry RVA14A920;
- WinMain RVA B3D40,afterSound B3D89,afterD3D B3D9C,beforeCharData B3469.

Exact own PE labs под `work/m9/1fc267d5/`:

- `startup001`: `.\DataTable\ko-kr`,NDLanguage:949:6851,Miles return1;
- `startup-russia001`: `.\DataTable\ru-ru`,NDLanguage:1251:4321,Miles return1;
- `device-startup001`: real window/device ready1/windowed1/render32;
- `create-startup001`: Character device456e0a0 равен actual app device,
  owner4696d20;stop перед `_CreateCharDataMgr`.

Принадлежащий отладчик повторно использован по SHA source/EXE; новый вызов
`probe_client455_startup.py --nation Russia` не переписывает корейский отчёт и
не пересобирает неизменённый debugger. Breakpoints получены из текущего own
disassembly/MAP. Плановый exitE0434200 наблюдён, second-chance ошибок нет.
Показ окна/полный shutdown не принимаются из controlled stop. Серверы/аккаунты/
сетевая авторизация не использовались, оригинальные файлы не менялись.

Короткие ANI/BBX/model/effect/shadow/clock/accounting регрессии прошли; прежние
GPU кадры сохранились, COM/Dmalloc0. Неизменённые большие suites не повторялись.
12scoped checkpoints имеютPASS/PARTIAL по своим участкам; M6/M6F/M7/M9 открыты.

Повтор через `scripts/Invoke-Python.ps1`: `audit_client455_language.py`,
`probe_client455_language.py`; обычный prepare/build/consumer/link; own-entry/
startup audit; startup (Korea и `--nation Russia`), device/Create probes;
`checkpoint_client455_language.py` плюс затронутые scoped checkpoints.

Следом046 — настоящий font/text provider:8C5A80 и consumers BF7718/BF7618/
BF7818/BF781C/BF7820,сверить CR3Font constructor/privateInit/glyph layout455
с legacy85byte name/DEFAULT_CHARSET/fixed height. Подключить language queries к
проверенному normal text/UI consumer и проверить реальный текст/DBCS ввод.
Не считать loaded strings отрисованным UI. Затем полный Create/data readers,
launcher/ETCAction policies/FG_CB/network order/BGM и обычный lifecycle.
