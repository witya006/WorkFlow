# M5: точная математика x87 и найденный consumer helpers

## Восстановленная математика

Эталон x86/base0x400000, current SHA-256
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
backup SHA-256 46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
Две функции: affine MatrixInvert VA0x8BFBC0/RVA0x4BFBC0,485bytes;
Vector3fTransform VA0x8C0980/RVA0x4C0980,132bytes.
Исходник scripts/native/client455_x87_math.cpp содержит читаемую x86 assembly,
без blobs, оригинальных EXE/DLL или извлечённого исполняемого буфера.

Все инструкции собранных функций совпадают с обоими pinned PE. Единственное
исключение — абсолютный operand ссылки на float .001: исходный VA0xAB0D60 заменён
на обычную DIR32 relocation к своей RF455_AffineEpsilon, байты константы совпадают.
Это проверяется на COFF и повторно на физическом коде внутри обоих итоговых клиентов.
Прочие bytes не нормализуются. Функции сохраняют порядок x87 операций, промежуточные
float spills, проверочные переходы, NaN/singular quirks и caller control word.
При одинаковой x87 среде и памяти это существенно сильнее сравнения формул с допуском.
Полная эквивалентность клиента из этого не следует.

Native тест только своей реализации:338checks, PC24/53/64 x4 rounding modes.
Проверены inverse/transform/alias position, affine threshold и следующий float,
NaN в affine-last-cell, singular input с masked exceptions, отсутствие изменения
control word/x87 stack TOP. Пример cancellation: binary32 промежуточный расчёт
16777216+1-16777216 даёт0, восстановленный x87 при PC53/nearest даёт1.
Оригинальные игровые EXE не запускались. 3 tests проверяют COFF relocation boundaries.
inventory/client455-x87-math.json, client455-x87-link.json.

RF_CLIENT_455_X87_MATH — отдельная selectable branch, defaultOFF, driverON.
Старые C++ bodies сохранены без перекодировки в work/.../common/r3math.cpp.
Global MatrixInvert/Vector3fTransform действительно вызывают проверенные реализации:
link checker проверяет integer-only wrappers/tail jumps и, при наличии, linker thunk.
Остальные математические функции и старый binary Character SDK этой заменой не закрыты.

## Интеграционная проверка

Обычная RF_Online.bin собрана:2 436 608bytes, entryRVA0x1BA990, SHA-256
8a728fcf95c2ea27989a80faba4680d0ae74febe462dbfbdd03c8f73b4725593.
Immutable snapshot artifacts/client-first-build/math455-release. Обычный EXE не запускался.
284 modern objects x86 /MT, прежние draw/logger/login selections проверены.

Lab SHA-256 cf5110dd3dbbdbbffa21c91fcd46f2c8b0f5f3bc8cfb255bdfb8c4591a165f44,
entryRVA0x7D97, snapshot work/client-helper-lab/revisions/cf5110dd3dbbdbbf/RF_Online.bin.
Все140real files/97 543records и12fixtures повторно проверены уже с точными math
функциями и совпадающими Release options. 2 546 931 native/comparison assertions.
FP control0x027F до/после каждого scenario: PC53,nearest,masked exceptions.
World/local outputs побитно совпали с отдельным binary64 intermediate calculation;
max world->local error .000967025756835938, все interior probe points внутри bbox.
Это intrinsic float rounding результата, не утверждение об исправлении особенностей 455.
Два math тела также совпали с инструкциями эталона в обоих linked PE.

При первом создании lab cache FileTracker отказал в доступе, CMake оставил пустые
общие flags. Это обнаружено и исправлено: driver теперь явно задаёт одинаковые
base flags /DWIN32 /D_WINDOWS /W3 /GR /EHsc и Release /O2 /Ob2 /DNDEBUG.
RF client сохраняет свой diagnostic /Od override; engine имеет Release optimization.
Предыдущие snapshots не переименованы в новые проверки. Compiler flags сохранены в
build reports; native runner отклоняет cache без нужных Release flags.

Игровые DLL не загружаются в lab; обычный GPU/network/LoadLevel startup не проверен.
В частности, реальное изменение FPU control при D3D initialization ещё требует проверки.
Точная инструкция математики не гарантирует одинаковую среду её вызова всей игрой.

## BSP consumer найден

Функция455 VA0x8CAD00/RVA0x4CAD00,935bytes. После LoadLevel связывает helper owner
через BSP+744, weather reader0x8CAD68 получает тот же указатель, GetDummyList(mask4)
вызывается0x8CADA7, bbox query0x8CAFE4. Camera position берётся из inverse-view
translation; это не сдвинутая на forward*50 позиция создания погодных частиц.

Итерации по двум layer pointers BSP+96/+100 подтверждены whole-function analysis.
Для environment type1 содержащий camera helper с flag4 заставляет SetParticleState(0);
вне interiors ранее остановленный particle запускается SetParticleState(1).
Attr0x10000 добавляет stop при строгом .24<getter0x8B1430()<.83. Getter возвращает
float0x1154DEC; смысл времени пока не установлен, не именовать этот интервал днём
без дальнейшего подтверждения. Type2 сохраняет фиксированный world bbox stop rule.
ClearVariable0x8F66B0 и ReleaseEntities0x8F9940 обнуляют owner.
В стеке weather function список1024indices; malformed overflow behavior не проверен.

Эти выводы закреплены на обоих PE: inventory/client455-weather-helper.json,
повтор scripts/audit_client_weather455.py. Raw asm/decomp — artifacts/helper455-*.
Это подтверждённый consumer, не утверждение об отсутствии других consumers.

## Что остаётся

Старая source weather система имеет один particle и не содержит helper binding.
Нельзя просто подставить 455 offsets в старый CBsp: layout другой. Следующий перенос
должен включать два слоя environment config/state/load/release/render и interior query,
с проверкой настоящего 455 parser и всех ссылок. Нормальный LoadLevel path ещё не
проверен, поэтому M5 остаётся в работе. M9 не достигнут; серверы не затрагивались.
