# Память проекта

Обновлено 2026-11-04. Основной root: E:\RFOnlineTrash\Source\WorkFlow.

## Цель и границы

Только клиент: поддерживаемые исходники RF_Online.bin с полным функционалом и
поведением закреплённого 455. /Goal — M9: финальная приёмка без модернизации графики.
M8 не требуется. Компиляция, запуск и частичный участок не закрывают цель;
критерии docs/client-acceptance.md. Степень соответствия сейчас неизвестна.
Серверные файлы разрешено только читать как справочник. Не изменять/копировать для
разработки/собирать серверы, БД или GoMMO server logic. Оригиналы читать, работать в work/.
Не запускать входные EXE. Субагенты — только по прямому запросу пользователя.

## Текущее состояние

- M1: R3Engine.lib под VS 2026 x86, две чистые пересборки; отдельный /MT R3EngineMT.lib.
- M2: бинарный эталон закреплён, 5 bytes / 2 ranges различий с backup исследованы.
- M3: helper-only SPT, 140 файлов / 97 543 записи, float32 round trip и 7 tests.
- M4: ПЕРВАЯ ПОЛНАЯ ДИАГНОСТИЧЕСКАЯ СБОРКА RF_Online.bin И CLEAN REBUILD УСПЕШНЫ.
  Это старая исходная база с отдельными подтверждёнными 455 ветками, /Od, NDEBUG,
  recovered Character header и адаптированной CharacterMR. Pure legacy branches OFF
  не объявлены восстановленными; canonical optimized Release и весь runtime ещё открыты.
  Не выдавать сборочный результат за полноту клиента или завершение M9.
- M5 В РАБОТЕ: loader455 найден, три отличия перенесены. Full-project own lab entry
  загрузил 140 реальных файлов/97 543 записи, использовал ненулевые координаты/bbox;
  12 fixtures/2 546 779 checks и 4 import-parser tests прошли. Обычный LoadLevel,
  BSP consumer и x87 parity ещё не проверены; M5 пока не закрыт.

## Артефакт первой сборки

Первая историческая версия (snapshot artifacts/client-first-build/clean), 2 436 608 bytes,
x86 Windows GUI, base 0x400000, entry RVA 0x1BA9E0. Clean SHA-256:
0b4c768fc4f52b26035c48cf900f67553392407d0372e23bb528333d2a87cf91.
Снимки initial/clean в ignored artifacts/client-first-build. Различаются только
COFF timestamp и timestamp debug directory; после исключения этих двух DWORD
все остальные байты равны. Не заявлять raw bit-exact EXE. Все 284 modern COFF x86 /MT.
13 direct DLL providers найдены; recursive loader/runtime не проверены. EXE не запускался.
inventory/client-first-build.json, client-character-diagnostic.json, client-mt-variant.json.

Текущая обычная ревизия с helper455: work/client-build/build-character-diagnostic/
Release/RF_Online.bin, 2 436 608 bytes, entry RVA0x1BAA10, SHA256
cf6cd16e348453dfeb478cfa06947acdb3749332ca102cc78991f43f8f120f1d.
Snapshot helper455 сохранён отдельно. Обычный EXE не запускался, 284 objects /MT проверены.
Own lab EXE SHA7f5d7be0679cce3c92eff3f6ec176c99b444c67758805731f415cb6493df0b5a,
entry RVA0x9ADE, находится work/client-helper-lab/RF_Online.bin. Только этот вариант
исполнялся с --rf-helper-probe. Game DLLs delayed и GetModuleHandle подтвердил отсутствие
их загрузки; normal GPU/network/startup/teardown не выполнялись.

## Эталон и инструменты

config/paths.json: legacy_source, client_455, server_bundle — reference inputs.
Current RF_Online.bin SHA b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b.
Backup SHA 46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
Оба x86/base 0x400000; config/client-target.json. Показанное 4.55 само не доказывает
официальную атрибуцию. Полный resource manifest ещё не готов; samples M3 хешированы.
VS2026 Professional18.11.3, MSVC14.51.36231/v145, WinSDK10.0.26100, CMake4.3.1-msvc1.
VC6 не обязателен. Python через scripts/Invoke-Python.ps1. Git локальный, без remote/push.
IDA9.2/HexRays/IDAPython3.11/native ida_mcp работают; owned sessions закрыты.
GoMMO stdio audit работает; это не разрешение Install/publish/server work.
13 Universal Modder skills и um0.2 установлены. Документы docs/ida-mcp.md/universal-modder.md.

## Сборка и источники доказательств

492 копии client/R3Engine под work/client-build/source. 11 byte-preserving compiler
patches: inventory/client-source-patches.json; не менять кодировки. Ещё 6 behavior
files (draw2/logger1/login1/helper2) имеют отдельный ledger client-behavior-patches.json.
Compiler/login overlay chain проверяется; повтор не меняет bytes/timestamps.
CMake flags RF_CLIENT_455_DRAW_ARGUMENTS / EFFECT_LOG / LOBBY_TRANSITION / HELPER_LOADER по умолчанию
OFF, diagnostic driver явно ON. Legacy calls сохранены в OFF branches; заглушек
CheckFiles/SendLog нет. _DEVELOPER_ и /FORCE не включены. Подтверждённые изменения:
- Draw: CNpc 0x45D280/CResObject 0x7CD2A0 передают m_fScale,scroll0.
- Logger 0x7DF200: append с prior length, >10M truncate, >5M flag. 14 cases/66 checks.
  Clear routine 0x7DF1B0 существует, но xrefs/absolute pointer не найдены; lifecycle
  неизвестен. Реальная clear implementation есть, автоматического вызова/atexit нет.
- Login success0x53FDC9 ->0x53FE2B -> lobby load0x53FE36, без старого CheckFiles
  на этом edge. Другие проверки файлов/вся login sequence ещё не исследованы полностью.
research/client-first-build.md и client-draw-and-legacy-effects.md, manifest instruction bytes.

D06: _NEW_UI_ включён, как в original Debug; без него текущие item classes некомплектны.
Dead old item switch исключён #else после уже существовавшего unconditional break.
/NODEFAULTLIB только в диагностике: CharacterR/ziplibm/ZipArchive_STL_M/libci; нет /FORCE.
Не переименовывать CharacterMR в R/MD. Готовый EXE не доказывает их полную ABI.
JPEG6b genuine IJG:46 C /MT,28 ABI values,2 exact golden decodes. Miles26 imports в
455 DLL. Genuine DX8.1b overlay13headers; 455 сам использует D3D9 — renderer gap M6.

## Character: что проверено и что осталось

CharacterMR SHA483715b927690fc69607682a093dff53635911870456f5849c9f52741702b8a8,
10 COFF x86. Дополнительных SDK/PDB у пользователя нет. .debug$T только typeserver refs.
207 function bodies cached artifacts/character-analysis; не повторять массовый reverse.
Header:67 layout assertions,165 public decorated refs; unknown storage остаётся opaque.
Рабочие views legacy776/1072 не подменять 455 GPU/CPU layouts. Exact original ctor/sizeof
и все defaults не доказаны. CRender bridge связывает m_Render, использует real Init;
Texture/Animation static pointers не получают придуманных assignments.
3630 native manager/empty renderer checks (8 instances,136 parts); setters 18 ABI checks.
FILE adapter8API:1828 own checks +3 COFF tests. Old loader FILE+12&0x10 несовместим с UCRT;
classic FILE изолирован, только 8 undefined symbols retargeted; bytes/relocations сохранены.
_Xlen/_Xran — real typed /MT throws,770 comparisons с classic system exports;
old exception layouts/unwind не полностью проверены, test-only aliases удалены.
59 checks actual text/binary effect loaders + CPU effect application к 2meshes.
EffectList bridge bounded500 entries, sentinel9; missing inline/out-of-domain unknown,
455 map/36 grades не перенесены. ObjectMesh ctor не задаёт blend pointer+160, dtor
его освобождает. Synthetic fixture задаёт null ownership; SDK не исправлялся. Проверить
real InitVertex/455 перед изменением production поведения. Source CLevel::GetFrustumNormalPlane
рекурсивен (C4717); сверить 455, не исправлять по одному имени.
Детали/хеши в inventory/character-*.json и research/character-*.md.

## Следующий шаг

M5: найти фактический consumer связи helper owner -> BSP+744, сравнить math contracts
с x87 455 и проверить полный LoadLevel path. Loader VA0x90BBF0/RVA0x50BBF0 подтверждён
на обоих PE, новые flags/нормализация/missing reset перенесены. Старый goto обходил
strlwr последующих имён; прежнее описание M3 уточнено. 23 из 140 samples имеют имя
EXT.spt (48 records); не все они автоматически выбраны картой. Ненулевые native
coordinate probes: max roundtrip error .001953125, interior points все внутри bbox.
Точное x87 rounding/полные error rules не доказаны. research/client-helper455-runtime.md,
inventory/client-features.json. Не повторять неизменённые 140 native tests без причины.
M6/M6F и критерии M9 остаются открыты. Подробные команды — docs/next-steps.md.
