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
  12 fixtures/2 546 931 checks и4 import-parser tests прошли. Две x87 math функции
  инструкционно совпали с455 в library и linked PE;338 native checks/12FP modes,
  3 COFF parser tests. Двухслойная погода перенесена: R3X/text config, load/release,
  CPU update отдельно отdraw, helper owner/interior и night.65real R3X +4fixtures /
  703checks,37native lifecycle checks.58real R3X применены реальной LoadR3X без lens/GPU.
  Обычный LoadLevel/FPU initialization не проверены; M5 пока не закрыт.
  Ресурсный аудит:78RPK/3775file entries,70BSP+93EBP,20real weather assets сохранены
  с hashes.8tool tests прошли. Source VFS и particle end handling ещё отсутствуют;
  research/client455-map-resources.md. Исходники/EXE в этом цикле не менялись.

## Артефакт первой сборки

Первая историческая версия (snapshot artifacts/client-first-build/clean), 2 436 608 bytes,
x86 Windows GUI, base 0x400000, entry RVA 0x1BA9E0. Clean SHA-256:
0b4c768fc4f52b26035c48cf900f67553392407d0372e23bb528333d2a87cf91.
Снимки initial/clean в ignored artifacts/client-first-build. Различаются только
COFF timestamp и timestamp debug directory; после исключения этих двух DWORD
все остальные байты равны. Не заявлять raw bit-exact EXE. Все 284 modern COFF x86 /MT.
13 direct DLL providers найдены; recursive loader/runtime не проверены. EXE не запускался.
inventory/client-first-build.json, client-character-diagnostic.json, client-mt-variant.json.

Текущая обычная ревизия:work/client-build/build-character-diagnostic/Release/RF_Online.bin,
2 438 144bytes,entryRVA0x1BAF50,SHA256
45690c220e37be7e34d234ffdd90f11d31703271e1fd12d37567fb6916c67542.
Snapshot weather455-cpu;предыдущие revisions сохранены. Обычный EXE
не запускался,285objects /MT проверены (180client +59engine +46JPEG).
Own lab EXE SHAe9ae5fa895742de2ff49b2b2c7f52c9748e7717d9ff21a623dc7d13bcdf3f361,
entryRVA0x7DBF,work/client-helper-lab/revisions/e9ae5fa895742de2/RF_Online.bin. Этот вариант
исполнялся с --rf-helper-probe /--rf-weather-read /--rf-weather-scenario.
Game DLLs delayed и GetModuleHandle подтвердил отсутствие
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
patches: inventory/client-source-patches.json; не менять кодировки. Ещё16behavior
files (draw2/logger1/login1/helper2/math1/weather9) имеют отдельный ledger client-behavior-patches.json.
Compiler/login overlay chain проверяется; повтор не меняет bytes/timestamps.
CMake flags RF_CLIENT_455_DRAW_ARGUMENTS / EFFECT_LOG / LOBBY_TRANSITION / HELPER_LOADER /
X87_MATH /WEATHER по умолчанию
OFF, diagnostic driver явно ON. Legacy calls сохранены в OFF branches; заглушек
CheckFiles/SendLog нет. _DEVELOPER_ и /FORCE не включены. Подтверждённые изменения:
- Draw: CNpc 0x45D280/CResObject 0x7CD2A0 передают m_fScale,scroll0.
- Logger 0x7DF200: append с prior length, >10M truncate, >5M flag. 14 cases/66 checks.
  Clear routine 0x7DF1B0 существует, но xrefs/absolute pointer не найдены; lifecycle
  неизвестен. Реальная clear implementation есть, автоматического вызова/atexit нет.
- Login success0x53FDC9 ->0x53FE2B -> lobby load0x53FE36, без старого CheckFiles
  на этом edge. Другие проверки файлов/вся login sequence ещё не исследованы полностью.
- Math MatrixInvert0x8BFBC0/RVA0x4BFBC0 и Vector3fTransform0x8C0980/RVA0x4C0980:
  собственный читаемый x87 source совпал со всеми617bytes инструкций обоих PE,
  кроме проверенной DIR32 ссылки на свою равную epsilon constant. Обе функции
  проверены также после линковки, global wrappers действительно на них переходят.
  Caller FPU control сохраняется; game startup FPU state ещё не проверен.
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

M5: следующий шаг — source RPK/group/fopen4550x8E7680 и case-sensitive particle end
перед lowercase (0x8DB650/0x8DB741), native checks на20staged weather assets.
Затем real entity/particle/normal LoadLevel/GPU, clock/client Time/HMS integration
caller4550x7E3E55. Resource format audit уже выполнен; не повторять его вместо переноса.
78MapEntity archives/3775entries,1067declaredSize mismatches: game fopen их игнорирует,
tool uses next-offset/EOF extent и сохраняет metadata.70BSP39+93EBP20 round trips;
Dungeon00 stale offsets overlap, sequential reads/skip end ровно на EOF. Остальные
162containers offsets совпали.5of6weather SPT resolved +5R3E113/5R3M/5R3T.
DDS headers/mask/DXT mip sizes проверены безGPU. Один e_cauldron_boss_tower/spt/
magmadust.spt missing для3Tower R3X; component нет во всех162RPK indexes. Не подменять.
Evidence inventory/client455-map-resources.json, research/client455-map-resources.md;
scripts/rpk455.py/map455.py,8tests. Strict tooling не эмулирует unsafe game parser.
Двухслойная weather source plumbing уже есть под RF_CLIENT_455_WEATHER, own arrays
не подменяются offsets455. Consumer0x8CAD00/RVA0x4CAD00, R3X reader0x90AED0/RVA0x50AED0:
версия1.1 прежняя, payload1032 vslegacy1024, name2+392/id2+520/sceneFlags+524.
65real files размерами1028/1036,7lens толькоreader;4fixtures,37real CPU lifecycle
checks и703total. CAlpha4buffers fixture исправлена после живого CBsp, allocator не менялся.
Clock normalized dayFraction/HMS, mutable initial rate3.0, numeric equivalence/lighting/
client time caller пока не закрыты. Particle455 curves/options, VFS wrapper0x8E7680,
full fog2/lens/scene weather и unsafe failure domain тоже открыты.
Source failure quirks и unchecked short header сохранены, не улучшать по догадке.
Research client455-weather-source.md; новый module scripts/native/client455_weather.cpp.
Math instruction parity выполнена для двух kernels; normal LoadLevel/FPU init пока нет.
23 из140 samples имеют имя EXT.spt (48records), не все автоматически выбраны картой.
Lab FP control0x027F,max roundtrip error .000967025756835938,interior probes внутри.
Новые доказательства research/client455-x87-and-weather.md, inventory/client455-*.json,
client-features.json. Build driver задаёт base/Release flags явно после выявленного
пустого lab cache при первоначальном E_ACCESSDENIED. RF client diagnostic/Od,
engine Release/O2. Не повторять неизменённые140 native tests без причины.
M6/M6F и критерии M9 остаются открыты. Подробные команды — docs/next-steps.md.
