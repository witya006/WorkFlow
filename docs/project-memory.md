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
- M5 ЗАКРЫТ для первого выбранного участка: helper455data и interior/weather consumer.
  Loader455 и617bytes двух math функций сверены с обоими pinned PE;140реальных
  files/97 543records +12fixtures /2 546 931checks сохранены на historical lab revision.
  338math checks/12FP modes; RPK module18 907checks/3775members/78archives.
  Actual LoadLevel/FrameMove/render/release полного проекта через own entry прошли
  на lobby и Platform01.23helpers/8interiors Platform01 управляют двумя real weather
  particles15/500:inside/night[0,0],outside/night[1,1],outside/day[0,0].
  13GPU cases/321checks,0errors/warnings,allocation/COM release balance0.
  FPU initial/engine/device=0x027F/0x027F/0x007F; actual map/render/consumer остаются007F.
  703weather/30resource/23 337targeted helper checks на текущем lab прошли.
  Gate inventory/client-m5-checkpoint.json; research/client455-graphics-runtime.md.
- M6 в работе. Полные particles/clock/Character/UI/network/renderer parity открыты.
  Численный clock уже восстановлен:8scalar functions+256byte frame prefix,773bytes
  совпали с обоими PE;1275checks/12FP modes в component и полном клиенте. Два
  независимых счётчика и actual FrameMove работают; CLand/cache/packet/console
  integration и весь lighting ещё открыты. research/client455-clock-source.md.
  D3D8 legacy против455D3D9 — обязательное восстановление M6, не optional M8.
  Normal WinMain и reference EXE не запускались. M6F/M7/M9 не закрыты.

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
2 440 704bytes,entryRVA0x1BBAA0,SHA256
f5f945160fe45255b9cea935cb3e27946a0a5ab531a18b1279abbd41164e18e5.
Snapshot clock455;предыдущие revisions сохранены. Обычный EXE
не запускался,287objects /MT проверены (180client +61engine +46JPEG).
Own lab EXE SHA bb441c5c3e393f98a298355b794e14bbb95d1efdd790c36e1356080d64c44e9b,
size4085248,entryRVA0x7DD8; snapshot work/client-clock-lab/bb441c5c3e393f98/RF_Online.bin.
Он исполнялся с clock/resource/weather и --rf-graphics-device/level Platform01.
1275clock checks/12FP modes,703weather/30resource,2GPUcases/59checks прошли.
M5 lab ece2accc... и13GPUcases остаются historical evidence; snapshot/evidence в
artifacts/m5-checkpoint/ece2acccb434ef06, gate verify_client_m5.py --saved.
Game DLLs delayed; GetModuleHandle до/после подтвердил отсутствие их загрузки.
Hidden-window640x480 D3D8 HAL/RTX2080Ti, без focus/input; real backbuffer BMP сохранены.
HAL требует разрешённого запуска вне sandbox; та же сборка внутри вернула0x8876086A.
Звук/сеть/normal game startup/teardown не проверены. Исторические lab hashes сохранены.

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
patches: inventory/client-source-patches.json; не менять кодировки. Behavior
files имеют отдельный ledger client-behavior-patches.json. Сейчас18files: исходные16
плюс2новых resource consumers;7resource overlays включают5weather files и2новых.
Compiler/login overlay chain проверяется; повтор не меняет bytes/timestamps.
CMake flags RF_CLIENT_455_DRAW_ARGUMENTS / EFFECT_LOG / LOBBY_TRANSITION / HELPER_LOADER /
X87_MATH /WEATHER /RESOURCE_IO /CLOCK по умолчанию
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
  Caller FPU control сохраняется; own graphics путь измерен0x007F,455startup ещё не установлен.
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

M6: следующий шаг — cached map time fields/network origin и CLand clock integration.
Уточнение:0x7E3E55 — console %time, НЕ network handler; %real_time вызывает0x8B14A0.
Настоящий map caller0x7C8B60 ->game fraction0x8B1440 и real fraction0x8B15D0.
Численный clock/FPU contract уже source-integrated и instruction-identical; не
повторять его исследование. inventory/client455-clock*.json,client455-time-callers.json.
Actual entity/texture/particle и LoadLevel/GPU уже прошли M5 в own entry.
RPK file/group/fopen/exists и particle end source уже подключены (flag RESOURCE_IO).
18 907native module checks на3775members/78RPK;30actual CParticle/LoadR3X archive
checks в full-project lab,7source ledgers/6compiled objects проверены. RPKFILE/Group
owners276/268, manual release/active pointer; Dmalloc настоящий в engine. Enumeration
порядок, skip-first,last3letters rpk,256limit,prefix-length-only, mutation и unbounded
FILE сохранены. Остальные consumers/groups/unsafe errors/OOM не сертифицированы.
Compile DDS mask128bytes в обоих linked PE равен455; input EXE/DLL не запускались.
Следом полные particles и обязательное D3D9 восстановление. Research client455-resource-io-source.md;
inventory/client455-resource-{io,reference,runtime,link}.json. Commands в next-steps.md.
Повтор MSBuild после sandbox E_ACCESSDENIED с escalation прошёл, cache не удалялся.
Последняя полная140helper проверка остаётся pinned weather revision;703weather checks
повторены на текущем clock lab;23 337targeted helper checks исторического M5 сохранены.
Owned graphics/clock IDA sessions закрыты/save. Resource audit/GPU уже выполнены;
не повторять их без изменения соответствующих входов.
78MapEntity archives/3775entries,1067declaredSize mismatches: game fopen их игнорирует,
tool uses next-offset/EOF extent и сохраняет metadata.70BSP39+93EBP20 round trips;
Dungeon00 stale offsets overlap, sequential reads/skip end ровно на EOF. Остальные
162containers offsets совпали.5of6weather SPT resolved +5R3E113/5R3M/5R3T.
DDS headers/mask/DXT mip sizes проверены, пять real entities затем загружены наGPU.
Один e_cauldron_boss_tower/spt/
magmadust.spt missing для3Tower R3X; component нет во всех162RPK indexes. Не подменять.
Evidence inventory/client455-map-resources.json, research/client455-map-resources.md;
scripts/rpk455.py/map455.py,8tests. Strict tooling не эмулирует unsafe game parser.
Двухслойная weather source plumbing уже есть под RF_CLIENT_455_WEATHER, own arrays
не подменяются offsets455. Consumer0x8CAD00/RVA0x4CAD00, R3X reader0x90AED0/RVA0x50AED0:
версия1.1 прежняя, payload1032 vslegacy1024, name2+392/id2+520/sceneFlags+524.
65real files размерами1028/1036,7lens толькоreader;4fixtures,37real CPU lifecycle
checks и703total. CAlpha4buffers fixture исправлена после живого CBsp, allocator не менялся.
Clock numeric8functions+two-clock prefix закрыт для equal caller FP environment;
map/client input integration/lighting пока открыты. Particle455 curves/options, все прочие VFS consumers,
full fog2/lens/scene weather и unsafe failure domain тоже открыты.
Source failure quirks и unchecked short header сохранены, не улучшать по догадке.
Research client455-weather-source.md; новый module scripts/native/client455_weather.cpp.
Math instruction parity выполнена для двух kernels; own LoadLevel/FPU init проверены,
reference455startup и normal WinMain остаются неизвестны.
23 из140 samples имеют имя EXT.spt (48records), не все автоматически выбраны картой.
Lab FP control0x027F,max roundtrip error .000967025756835938,interior probes внутри.
Новые доказательства research/client455-x87-and-weather.md, inventory/client455-*.json,
client-features.json. Build driver задаёт base/Release flags явно после выявленного
пустого lab cache при первоначальном E_ACCESSDENIED. RF client diagnostic/Od,
engine Release/O2. Не повторять неизменённые140 native tests без причины.
M6/M6F и критерии M9 остаются открыты. Подробные команды — docs/next-steps.md.
