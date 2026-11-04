# Проверенный адаптер восьми файловых API Character

2026-11-04. Это сохранённый промежуточный результат M4. Последняя редакция /Goal
заканчивается на уведомлении о начале пункта 4; полная сборка клиента остаётся в плане.

Исходный CharacterMR.lib SHA-256:
483715b927690fc69607682a093dff53635911870456f5849c9f52741702b8a8.
Архитектура x86. В релокируемом COFF runtime RVA отсутствует.

scripts/build_character_stdio_adapter.py создаёт отдельный CharacterMR-stdio.lib в
ignored work/. В десяти копиях COFF объектов перенаправляются только undefined symbols
fopen/fclose/fgets/fread/fwrite/fscanf/fseek/ftell. Исходный архив не меняется. Все байты
до таблицы символов (включая инструкции/релокации) и все публичные определения проверены
на неизменность. Меняются записи имён undefined symbols и дополняется string table.
Манифест с хешами каждого оригинала/результата: inventory/character-stdio-adapter.json.

Авторский исходник scripts/native/character_legacy_stdio.cpp реализует реальную работу
через системный x86 msvcrt.dll. Classic FILE представлен отдельным opaque типом;
современные FILE ему не передаются. Provider сохраняется на время жизни процесса.
Для fscanf, у которого в classic DLL нет vfscanf, x86 cdecl trampoline сохраняет стек
аргументов и передаёт управление настоящему fscanf, без имитации форматов.

Собственная программа test_character_legacy_stdio.cpp выполнила 1828 проверок: восемь
API, полный бинарный диапазон, частичные/нулевые чтения, seek/tell, EOF, read-only ошибка,
CRLF/fgets, malformed fscanf и 256 циклов varargs. Отдельно проверено, что modern CRT
продолжает независимо читать тот же бинарный файл. Три теста COFF проверили сохранение
кода, идемпотентность, ошибочные входы и запрет переименования defined symbols.

Адаптер подключён только к diagnostic link с проверкой хешей обоих архивов и provider.
Новых stdio undefined symbols нет; прежние 13 уникальных link gaps сохраняются.
Эти тесты не исполняют старые загрузчики Character и не подтверждают их полную ABI,
контейнеры, конструкторы или исключения. RF_Online.bin не получен. Следующее продолжение
M4 должно проверить сам старый компонент и восстановить оставшиеся методы, сохраняя
CheckFiles/SendLog. Контекст предыдущих зависимостей: client-dependencies-m4.md.

Дополнительное статическое чтение 455 сохранено как гипотеза: backup SHA-256
46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558,
x86, image base 0x400000. Кандидаты transform/draw wrapper VA 0x92FBE0 / RVA 0x52FBE0
(size 0x295) и mesh draw VA 0x92E140 / RVA 0x52E140 (size 0x4A9). Сырые выгрузки в
artifacts/character455-draw-wrapper.json и character455-draw-mesh-candidate.json.
Вторая выгрузка неполная (220/229 строк). Имена/эквивалентность/default arguments не
подтверждены; реализации на этих предположениях не создавались. Собственная IDA-сессия
7c611c3d закрыта с сохранением.
