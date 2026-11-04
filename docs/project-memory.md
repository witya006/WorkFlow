# Память проекта

Обновлено 2026-11-05. Основной root: E:\RFOnlineTrash\Source\WorkFlow.

## Цель и границы

Только клиент: поддерживаемые исходники RF_Online.bin с полным функционалом и
поведением закреплённого 455. /Goal — M9: финальная приёмка без модернизации графики.
M8 не требуется. Компиляция, запуск и частичный участок не закрывают цель;
критерии docs/client-acceptance.md. Степень соответствия сейчас неизвестна.
Серверные файлы разрешено только читать как справочник. Не изменять/копировать для
разработки/собирать серверы, БД или GoMMO server logic. Оригиналы читать, работать в work/.
Не запускать входные EXE. Субагенты — только по прямому запросу пользователя.

## Текущее состояние

- Новейший standalone unit: reader93C2F0/part720 ctor+dtor/model28release.
  4606native checks/12realBN455records+5synthetic4records,1183PAGE_NOACCESS prefixes,
  7allocfailpoints,12FPmodes,6Python tests,heap0. Source x86/MT/O2/W4/WX.
  Fullclient/normal import/converter не подключены; текущие клиентские PE ниже
  не менялись. Next: importer93C770 +converter93CD60, затем dispatcher/FrameMove.
  Research client455-legacy-model-reader.md;inventory/client455-legacy-models*.json.
  Owned926983beclosed/save;converter tail328lines saved,вместе спрежними250все578.
- Последний завершённый source unit M6: Character455 record1188/manager4148,
  IDcache/rawMSH/borrowedtexture refresh.850CPU/1138HAL checks, полный lab1138;
  12models/393parts/276uploads/59texture pointers, ownheap/COM/Dmalloc0.
  24bodies equalbothpins; ctor1188byte oracle из92recorded instructions.
  13APIs реально вызваны из fullclient test TU/source archive. MESH08 из собственного
  RFS и11loose моделей совпали по rawbytes с pinned files. Normal dispatcher legacy.
  Current model10021 иPlatform01/device69checks passed; прочие старые proofs
  исторические. Gate inventory/client455-character-manager-checkpoint.json;
  research/client455-character-manager.md. Next: BN93C2F0/93C770 +converter93CD60,
  затем dispatcher9238A0/FrameMove923A40/animation/typed consumers.
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
  703weather/30resource/23 337targeted helper checks прошли на исторической M5 lab revision.
  Gate inventory/client-m5-checkpoint.json; research/client455-graphics-runtime.md.
- M6 в работе. Полные particles/clock/Character/UI/network/renderer parity открыты.
  Первая clock ревизия:8scalar functions+256byte frame prefix,773bytes
  совпали с обоими PE;1275checks/12FP modes в component и полном клиенте. Два
  независимых счётчика и actual FrameMove работают. Следом source packet8/5,
  CLand timestamp/tick cache и successful-load hook перенесены;314native checks/
  12FP modes/UTC+JST. Actual CNetMsgProcessor_Map/CLand и Platform01 прошли GPU
  2cases/66checks.130byte numeric fragment равен455,linked normal/lab проверены.
  Затем time/real_time commands и actual CHAT_INFO grade>=1 hook перенесены:
  432cases/2628checks/12FP modes,20actual input/access/history/lifecycle checks;
  grade1 accepts/grade0 rejects,no connections. Real HMS set/get добавлены:clock
  теперь10scalar functions+256byte prefix,1037bytes equal455,1443checks/12FP modes.
  Commands→actual Platform01 FrameMove/weather/GPU2cases/69checks прошли.
  Full CLand/transport/calendar domain,other local commands/chat/lighting открыты.
  research/client455-clock-source.md и client455-map-time-source.md.
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
2 451 456bytes,entryRVA0x1BC4B0,SHA256
4634f68457ab0251075b8ed110075f13af36332121bcd4346d32de4de8def5f3.
Snapshot character455-manager-io;предыдущие revisions сохранены. Обычный EXE
не запускался,289objects /MT проверены (180client +63engine +46JPEG).
Own lab EXE SHA 9ebef3b540bcf766643bd26bd40527afc91810b8fc0b74807d6914a01542757f,
size4909056,entryRVA0x8733; snapshot work/m9/9ebef3b5/client001/RF_Online.bin.
Current: manager1138/model10021/Platform01-device69checks;185clientlabTUs.
Normal runtime bytes после исключения двух timestamps равны предыдущему snapshot.
Следующие прежние scoped proofs относятся к историческим revisions; их inputs/
source не менялись, повторных запусков на current PE не было:
1443clock/314map-time/703weather/30resource плюс432command cases/2628checks,
20actual CHAT_INFO access/history/lifecycle и2GPUcases/69checks прошли.
Character8source functions подключены,включая полный legacy InitVertex/vertex/physique.
245binding+6732InitVertex checks/144cases/12FP modes standalone/full-client и4COFFtests
прошли;два actual SDK LoadRealData calls доходят до собственного InitVertex.
0-2meshes/0-2faces,matrices/UV/weights/bounds/parents иcreate/lock failure проверены
через actual SDK MakeVB с test-only COM capture;не Character GPU/455acceptance.
research/character-init-source.md;inventory/character-mesh-source*.json,character-init*.json.
MESH08format decoder/writer sourceготов:858real files/515096894bytes/12090meshes/
5153052vertices+indices/412222bone records прошлиlossless tool roundtrip.
6304native checks/12samples/393parts и1309guard-page truncations standalone/fullclient.
7Python tests. Normal fullmodel-loader consumer не реализован,unused APIs stripped;
labдвеAPI linked. research/client455-mesh08-format.md;client455-mesh08*.json.
Четыре packed455parent/bone kernels sourceготовы:2237checks/12real mesh-skeleton
pairs/393meshes/455skeleton records standalone/full-client,20pointer/matrix overlap
cases31–50. Нет missing influences в fixtures,max4unique/mesh. Names изplain BN
выделены tooling,полный skeleton loader/матрицы/анимации иего selection не доказаны.
Normal consumer ещё отсутствует;не смешивать сlegacy1072ABI. Полный loader открыт.
research/client455-mesh-bindings-source.md;inventory/client455-mesh-bindings*.json.
Constructor final state/counters,header fields/matrices/special names иmaterial
request flow sourceготовы:14562checks/12real files/393parts/12FP modes standalone/
full-client. Матрицы используютactual D3DX9_36,texture backend вtests scripted.
Native algebraic invariants +synthetic bitgolden;неполный arbitrary matrix bitproof.
858files/12090headers исследованы поfrozen offsets:8659primary empty,3431DDS/backslash,
0nonfinite/nonaffine/zero numeric3x3det/unterminated/nonASCII/% strings. Это domain
audit,неfull matrix condition proof. НЕ повторять header census без изменения inputs.
Actual TextureManager backend теперь source;sharedGPU/loader/destructor/normaldispatch открыты.
research/client455-mesh-runtime-source.md;inventory/client455-mesh-runtime*.json.
Следующий source unit завершён в выбранном texture domain: Character RFS index/cache,
DDS XOR/mip/repair и288byte TextureManager known fields.24body ranges совпали по
обоим pinned455PE,3imports ведут вactual D3DX9_36. Источники client455_texture.cpp/
client455_character_rfs.cpp,optionRF_CLIENT_455_TEXTURE. Native333CPU/8440GPU checks,
80DDSprofiles,68successful actualD3DX texture pairs/all mip contents,137renders,
3real MESH08models/97parts/59positive material bindings. Реальный cube orphan+null
return сохранён;test wrapper освобождает orphan только после наблюдения.9Python tests.
Полный lab даёт теже8440checks,COM/Dmalloc0,gameDLLs отсутствуют. Все предыдущие
scoped regressions иPlatform01/device69checks прошли;frameSHA сохранены. Normal
loader ещё legacy,новые unused APIs stripped. Не повторять texture reverse/corpus
без новых inputs;не считать full Character GPU/455acceptance. Next:shared buffers
93E000/93E180,index rebase/publication/owning release,затем normal model dispatch.
Raw artifacts/character-texture455,отчёты inventory/client455-texture*.json,
research/client455-character-textures.md. Private allocator/STL ABI,logger/cache
teardown/reset,malformed/OOM/nonASCII/unsafe format-string domains открыты.
SharedGPU unit теперь source:18full bodies+MESH08upload fragment equalbothpins,
8200byte ctors/Release-onlydtors/first-fit1024/VB36+64/INDEX16/rebase/callerfragment.
Native158336CPU/159173HALchecks standalone/full-client,12real files/393parts;
276nonzero-indexparts реально загружены вmanagedGPUbuffers,117zero-indexparts
пропустилиобаuploads. Capture проверяет bytes,slot1023/exhaustion/wrap/failures;
4synthetic indexed draws до/после rollover совпали. COM/Dmalloc0. Normal APIs
unused/stripped;full renderer/skeleton/animation/model publication ещё открыты.
Не повторять9allocator/bindfunctions и6poolctors/dtors. Next:owning model
array/destructor/failure unwind+normal loader dispatch,затем полноценные
transforms/skinning/shaders. Ownerctor5DFB70,+8928VB64/+17128VB36/+25328IB;
SetDevice920590writesborroweddevices. Renderer reset/opaque8192/unsafeOOMopen.
research/client455-shared-buffers.md;inventory/client455-shared-buffers*.json.
Owned10003798 иb58f27c1closed/save. Все прежние scoped regressions +texture8440
иPlatform01/device69checks прошли наcurrentlab;frames сохранены.
Затем source mesh dtor/array lifetime иconnected MESH08route готовы:9953CPU/
10021HALchecks standalone/full-client,12lifetimecases/12files/393parts,
276realGPUuploads/59texturebindings.10bodies equalbothpins. Dtor920FD0→tables
91C3C0 (20interleavedpairs→168zero)→strings920F20(reverse5fields→cap15/len0/first0).
COM4486/4490 не обнуляются;free+null5095/5099/4506. ArraycookieDWORDcount,
reverse destruction,flags2array/1free. Ownedmodel260 guards536release,count532
retained. Default realMTmalloc/free,MemoryOps для соответствующегоowner;oldheapABI
не смешивать. Source loader usesmaterials/header/GPU→parents/bones→scratchfree→
publish536then532. ExistingarrayoverwrittenWITHOUTfree,caller reloadpolicyneeded.
Own bounded/nullalloc cleanup отличаетсяотuncheckedref failures;full unwindopen.
Knownmodelprefix800 —ownminimumview,неfullABI. Legacy CHARACTEROBJECT parent268/
count528/mesh532 отличаетсяот455272/532/536;неcast/flipnormaldispatcherпреждевременно.
Normalmanager/filedispatch/BN/animation/shaders ещё открыты. Next:actualfile/manager
route иполный455model layout/typedconsumers,затемnormal integration. Начатьxref91F250;
920FD0/921480/3managerdelete bodies уже cached/pinned,не повторять reverse.
research/client455-model-pipeline.md;inventory/client455-models*.json.
Owned50804ce1closed/save;allprevious scopedregressions inclshared159173,
texture8440 иPlatform01/device69 прошли,currentframesunchanged. Ownheap/COM/Dmalloc0.
Configured MCP probe переведён наcopied client455IDB;66tools,10functionpage,
decompile/close2fa6d05a проверены. Restricted workercode2 устраняется тойже
escalation,непереустановкой. Серверныйsmoke input больше не используется.
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
files имеют отдельный ledger client-behavior-patches.json. Сейчас22files: прежние21
плюс1actual CHAT_INFO input file;7resource overlays включают5weather files и2новых.
Compiler/login overlay chain проверяется; повтор не меняет bytes/timestamps.
CMake flags RF_CLIENT_455_DRAW_ARGUMENTS / EFFECT_LOG / LOBBY_TRANSITION / HELPER_LOADER /
X87_MATH /WEATHER /RESOURCE_IO /CLOCK /MAP_TIME /TIME_COMMANDS по умолчанию
OFF, diagnostic driver явно ON. Legacy calls сохранены в OFF branches.
MESH08/MESH_BINDINGS/MESH_RUNTIME — отдельные defaultOFF dependencies,driverON;
последние два source macro ограничены labfile. Normal consumers ещё не подключены.
Заглушек CheckFiles/SendLog нет. _DEVELOPER_ и /FORCE не включены. Подтверждённые изменения:
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
его освобождает; реальный InitVertex→FindBlendParent всегда записывает allocation,
включая count0. Проверены skinned/unskinned CPU cases;constructor patch не обоснован.
Восемь legacy CPU functions/full InitVertex восстановлены source,245+6732checks/
4COFFtests;455mesh5803bytes/vertex64/inline matrices отличается от legacy1072/36/heap.
First-match455 vs last-matchlegacy иnegative455normals(+32/+36/+40)/UV(+44/+48) подтверждены.
MESH08gate91F250/51F250 иloader922A00/522A00 найдены,оба тела совпадают в pinned PE.
Shield065sample имеетMESH08;Shield031/Cloak002 проходят old693framing доEOF.
Полный loader/layout/renderer иunwind открыты. Source CLevel::GetFrustumNormalPlane
рекурсивен (C4717); сверить 455, не исправлять по одному имени.
Детали/хеши в inventory/character-*.json и research/character-*.md.

## Следующий шаг

M6: importer93C770 иconverter93CD60 для настоящего BN/skeleton. Source reader93C2F0
иpart/model lifetime уже проверены standalone; не повторять их reverse.
Затем dispatcher9238A0 соsticky flags/failure lifetime, FrameMove923A40, animation/
skinning/455shaders иnormal typed consumers. Selected manager/fileIO/ctor/refresh
уже готовы; НЕ повторять их reverse. Полный455record allocation1188 подтверждён,
semantics tail/полныйC++ABI открыты. Root next-steps теперь содержит краткую очередь.
Cache retain-after-delete сохранён; не разыменовывать freed entries в тестах.
Current24ranges иctorinstructions pinned; ownedc3f13f8bclosed/save. Raw parser181lines
вartifacts/character-manager455/manager-plus-4.json; FrameMove head+tail тамже.
93CD60:первые250lines вartifacts/character-gpu455/next-2.json,остальные328
вartifacts/character-legacy455/converter-tail.json. Весьbodycached.
Подробности research/client455-character-manager.md. ПолныйD3D9 остаётся M6.

Ниже исторические ориентиры уже выполненных шагов, не текущая очередь:
Использовать уже кешированные207definitions/10COFF, не выгружать всё заново.
Legacy source unit теперь8functions/full InitVertex:245binding+6732InitVertex checks.
Не повторять расследование pointer+160: штатный FindBlendParent его задаёт;failure/
unwind до него открыт. MESH08framing/source reader готов,НЕ повторять corpus858audit
без изменения inputs/parser. TextureManager934120/934A20/provider933DE0 иshared GPU
allocators93E000/93E180/index rebase/publication/release уже перенесены в source.
Constructor/header/matrices/material request flow уже sourceготовы (14562checks),
НЕ повторять этот reverse/header census. First-match local/external bindings и93CB00bone
kernel уже sourceготовы,НЕ повторять reverse. 12fixturepairs pinned,ноnormal model
dispatch/полный skeleton loader не подключены;unknown contracts не объявлятьготовыми.
Не подавать MESH08 встарый unchecked MakeMeshData693 reader. Новый raw body607lines
кеширован artifacts/character-mesh-source/mesh08-0x922a00.json/.txt;не выгружать снова.
Gate91F250 сравнивает6bytes MESH08;LoadRealData9238F0/923902 ведут вgate/loader.
Reference93B020 инвертирует normals ииспользует64byte vertex;93B5F0 задаётUV+44/+48.
7bodies/normal/UV/magic instructions/2calls и3samples pinned вcharacter-init-reference.json.
research/character-init-source.md. В455mesh5803/vertex64/inline matrices;
legacy1072/36/heap — иной ABI. MESH08format sourceесть,full runtime loader ещё открыт.
Stream:MESH08+WORDcount,permesh693header+WORDv/64*v+WORDi/2*i+WORDb/404*b.
3bodies/12framing instructions вbothPE;858loose sources/12090parts roundtrip toEOF,
0trailing/limit/out-of-range/influence>4.1850other-prefix loose files не классифицированы;
RFS/archived models не покрыты. C++ views24/20 неподменяют455mesh5803.
Bounds errors — own safety,неAV/OOM/debugbreak parity. Normal consumerнеподключён,
необъявлятьCharacter455готовым. Raw607line922A00 и146line93CB00кешированы;
large disasm вернул10lines приinstruction_count1069:дляfacts использовать scoped
insn_query,неполагатьсятольконаcursor.done. Owned IDAeb76ecefclosed/save.
Следом IDA6f091546closed/save:4bodies/12binding instruction sites сверены вbothPE.
Packed parent pointer518/flag512/rematch5495,blend count522/pointers526/matrices646.
Identity stores ПЕРЕД pointer copy;count>=31 наблюдаемо перекрывает matrix bytes.
Source воспроизводит порядок,own safetycap50 не означаетofficial safe capacity50.
Signed influence<=0 skips;>4/unterminated/>50resolved — ownerror,неAV/OOM parity.
Vector frees/debug logger ещё не подключены. See research/client455-mesh-bindings-source.md.
Fixture plain-BN name extraction:6Python tests/all minimal truncations passed.
Source/kernel inputs не менялись после final component/full-client validation.
Следом IDA716ae4faclosed/save:5runtime bodies совпали вbothPE,matrix thunks854130/
85412A действительно импортируютd3dx9_36. Installed SysWOW64 DLL равнаclient-local,
SHA c12f0ab0338eb5031d3d04beaf7208ac848f7e037d21ff963d2af90221cbe935,
version9.19.949.2111,Microsoft signatureValid.
DLLexport-entry RVAs:Inverse1654A1/Multiply164F24;client455-d3dx9-provider.json.
Не подменять D3DX8 илиидеальнойmath:inverse diag(2,2,2,1) даёт bits3EFFFFFF x3/3F7FFFFF.
Отклонение1ULP доказано;reciprocal approximation — предположение оего причине.
Header6floats иunsigned598 используютx87;unsigned correction constant2^32.
Material callback API требуетbackend;scriptedprovider толькоtest. Primary-miss
запускает4load attempts;empty primary сохраняетaux;secondary leading-only slash
остаётсявимени. Actual texture cache/creation ещё не подключены. Full607line body
НЕ выгружать;новыеtexture934120/934A20/subctor920E40 cachedartifacts/character-mesh08.
SharedGPU:vertex offset4494,index offset4502;WORD index+=((offset%0x231860)>>6),
upload толькоприindexCount>0;затемparent/boneиpublicationobject+532/+536.
Destructor920FD0 cached,owningmethods/vectorfree/logger/unwind открыты.
research/character-library.md,character-effects-and-exceptions.md,character-setters-and-construction.md.
Local time input уже перенесён; подробности research/client455-time-commands-source.md.
Parser7E3B10 имеет один прямой caller4335A0/RVA335A0,size8B3,call4335BD:
он сначала пробует local parser, затем обрабатывает GM/text-command fallback.
Raw artifacts/clock455-analysis/command-caller-0x4335a0.json;body/call проверены в обоих
PE через audit_client_time455.py. Actual copied CHAT_INFO::SendMessage hook добавлен
с grade>=1 после existing history/prefix path;clock-only subset/ASCII domain.
Other local directives/full chat fallback/UI/key events/CRT locale ещё открыты,
не объявлять parser целиком готовым.
Owned IDAdec47527 закрыта/save.
Уточнение:0x7E3E55 — console %time, НЕ network handler; %real_time вызывает0x8B14A0.
Настоящий map caller0x7C8B60 ->game fraction0x8B1440 и real fraction0x8B15D0 уже
source-integrated. Packet8/5 handler580AE0 stores payload DWORD+1/+5 to CLand+32/+36
и receipt GetTickCount+40. Timestamp signed32 проходит через localtime32; struct tm
не передаётся по сети. Full hours/day carry не добавлять: reference их теряет.
Byte0/value0 meanings и остальные field+24 consumers неизвестны. Init обнуляет+32/+36,
оставляет+40/+24 неизменными в исследованном body; native tests требуют valid packet.
Module own16byte state,130byte x87 fragment,314checks/12FP modes/UTC+JST; copied3files
и2actual compiled client object references проверены. Actual CNetMap/CLand GPU path
использовал char* LoadLevel +public post-load hook; полный byte-index UI/camera/effects
path не исполнялся, root CNetworkMgr/socket тоже. Old-CRT timezone/DST/invalid domains
не закрыты. research/client455-map-time-source.md.
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
полные map/calendar/transport/console/lighting области пока открыты. Particle455 curves/options, все прочие VFS consumers,
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
