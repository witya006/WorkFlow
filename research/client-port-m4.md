# M4: клиент скомпилирован, линковка не завершена

2026-11-04. Только рабочие копии клиента/R3Engine; оригиналы и серверы не изменялись.
Это снимок первого полного compile. Продолжение с восстановленными JPEG/Miles,
полным списком link gaps и native проверкой несовместимости CRT —
[client-dependencies-m4.md](client-dependencies-m4.md).

## Подтверждено

- Все 180 C++ единиц RF_Online скомпилированы MSVC 2026 x86.
- Заново собран R3EngineClientMT: 58 C++, /MT, результат R3EngineMT.lib.
  Сборка M1 /MD хранится отдельно; архив не переименован из /MD варианта.
- У всех 238 объектов проверены COFF machine 0x14c и /DEFAULTLIB:LIBCMT.
- Genuine x86 библиотеки DX8 подключены, LNK2038 устранён корректным выбором CRT.
- Последняя линковка: exit 1, LNK1104 JpegLibMT.lib. RF_Online.bin нет, M4 не завершён.

Отчёты: inventory/client-character-diagnostic.json, client-mt-variant.json.
R3EngineMT.lib SHA-256: 227ce192bd5fe28b7dfbffaf0ee9b9525c3646fc4be692a1bda17f55db28d7f2.
Подробные хеши объектов и журналы — ignored artifacts/client-character-diagnostic/.

## Что изменилось

Диагностический Character.h генерируется scripts/prepare_character_header.py в
work/recovered/character-legacy/include. Проверены 56 layout assertions и decorated
names 165 адресуемых публичных функций. 30 операндов независимо сверены с инструкциями.
Это не завершённый SDK: конструкторы, часть inline API и короткие перегрузки объявлены
без реализаций. Исходные default arguments не выдуманы. Эти пробелы останутся link
errors до восстановления поведения. Внутренний layout API-only классов неизвестен;
создавать их экземпляры нельзя. research/character-library.md.

В современной Release включён _NEW_UI_ (D06). Старый DSP содержит флаг только в Debug,
но текущие классы предметов в item/citemdata.h полностью исключаются без него.
Контрпроверка global.cpp: ошибки неполных типов без флага, compile exit 0 с ним,
без изменения самого файла. Это не доказательство соответствия UI клиента 455.

Четыре новых байтовых патча сохраняют прежний implicit int: MAX_PUSH_OUT_COUNT,
LIMIT_DEAD_TIME, EQUIP_ITEM_REQ_TIME, endwav. Всего в ledger 10 рабочих файлов;
оригиналы/кодировки сохранены. Значения и алгоритмы этих патчей не изменены.

Отдельный diagnostic forced header предоставляет неквалифицированные имена STL
и существующий R3Engine DXUtil.h; Winsock2 включается до Windows.h. Он не является
частью восстановленного ABI Character. /Od и /MP4 ускоряют проход; итоговую Release
сборку и две чистые пересборки ещё предстоит выполнить.

## Повтор

1. scripts/Invoke-Python.ps1 scripts/apply_client_port_patches.py
2. scripts/Invoke-Python.ps1 scripts/prepare_client_build.py
3. scripts/Invoke-Python.ps1 scripts/prepare_character_header.py
4. scripts/Invoke-Python.ps1 scripts/check_character_header.py
5. scripts/probe_client_character_build.ps1
6. scripts/Invoke-Python.ps1 scripts/verify_client_coff.py

Шаг 5 пока ожидаемо возвращает 1. Preflight требует успешный global.cpp и совпадение
хешей Character.h/shim до полного прохода. Диагностическая папка build-character-diagnostic
отделена от M1 build-vs2026. 180 объектов отдельно проверены как настоящие COFF x86 /MT.

## Осталось

В jpeglib.h указан JPEG_LIB_VERSION 62 (6b), а jpegfile.cpp действительно вызывает
jpeg_*. Подготовить настоящую JPEG /MT, затем проверять zip/Character link diagnostics.
Официальный архив IJG: https://www.ijg.org/files/ — jpegsrc.v6b.tar.gz / jpegsr6b.zip.
На момент записи исходники оттуда ещё не загружены и не собраны.

В старом CLevel::GetFrustumNormalPlane найден самовызов (C4717); в core.cpp есть
одноимённая глобальная функция. Это не исправлялось: проверить вызовы/поведение по 455.
