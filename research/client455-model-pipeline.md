# Character455: владение мешами и связанный MESH08 путь

2026-11-05. M6 продвинут; M6/M6F/M7/M9 остаются открытыми. Связаны уже
восстановленные source модули материалов, заголовка, GPU и parent/bone bindings.
Это valid-input MESH08 route и lifetime kernels, не полный Character runtime.

## Эталон

RF_Online.bin x86/base400000: current SHA256
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b,
backup46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
10 полных диапазонов совпали между pins; RVA/размер/SHA в
inventory/client455-models-reference.json. Главные VA/RVA:
920FD0/520FD0 mesh dtor,91C3C0/51C3C0 tables,920F20/520F20 strings,
921480/521480 deleting dtor,87284C/47284C reverse vector iterator,
921960/521960 delete-name,921A50/521A50 delete-ID,921BC0/521BC0 manager clear,
9214E0/5214E0 constructor,922A00/522A00 MESH08loader.
Обе free thunks8745BA/871E91 ведут к одному provider; это не доказательство
совместимости старой кучи с modern /MT. Собственная IDA50804ce1 закрыта/save.
Raw decompiles/instructions/xrefs — artifacts/character-model455; полные loader
иmesh dtor уже были в artifacts/character-mesh-source, повторно не декомпилировались.

## Владение и освобождение

Mesh5803byte dtor вызывает COM Release4486/4490, не обнуляя эти поля. Затем
free+null5095/5099/4506. Таблицы5595 содержат20 пар указателей: освобождение
порядком i,i+20, затем весь168byte диапазон обнуляется. Встроенный объект5163
содержит пять старых basic_string fields. Они очищаются в обратном порядке:
relative132/96/68/32/4. При capacity>=16 освобождается data pointer; после
каждой строки меняются только cap=15,len=0,firstbyte=0. Остальные байты сохраняются,
включая хвост старого heap pointer. Повторный dtor с живыми COM fields небезопасен;
source сохраняет поведение. Test-only COM storage удерживается для проверки этого
факта; реальный COM после Release0 повторно не вызывается.

Массив выделяется как DWORD count +5803*count; constructor идёт вперёд,
destructor — назад. В921480 flags2 выбирает массив, flags1 освобождает память.
Возврат — адрес начала выделения, даже после free; не разыменовывать его.
Для array delete счётчик cookie авторитетен, а не model.count.
Выбранный branch из manager delete/clear требует model+260 иnonnull model+536;
удаляет массив, обнуляет536, сохраняет count532. Затем manager отдельно освобождает
record. Полный vector manager/delete-name/delete-ID ещё не перенесён этим модулем.

Source client455_model_lifecycle.cpp использует обязательные MemoryOps владельца.
Поставляется реальный modern static CRT provider malloc/free; успешных no-op нет.
Память иной кучи должна освобождаться её provider. Применять modern free к
непроверенным binarySDK allocations нельзя. Native тесты оборачивают настоящий
CRT для учёта каждой allocation/free и отдельно вводят null-allocation failures.

## Связанный source route

client455_model_loader.cpp принимает mutable MESH08 buffer, known model prefix
и реальный context: MemoryOps, pinned D3DX9 matrices, TextureManager, sharedVB/IB,
общие accounting records. RF455KnownModelPrefix800bytes — собственный view
известного минимума, не полный ObjectData ABI или его constructor.

Для каждого mesh: material lookup/load, header/scalars/matrices/names, GPU upload,
копия404byte bone records. Затем сброс parent flag, local parent binding, external
binding при model+272, bone resolution с external priority/local fallback.
Bone scratch освобождается перед публикацией; сначала model.meshes536, потом
count532. Model flag796 сохраняется или устанавливается special-name branch.

Повторная загрузка перезаписывает старый array pointer без освобождения, как922A00.
Это не автоматически исправленный reload: владелец должен выбрать тот же caller
policy. Native тест сохраняет обе allocations и освобождает их явно.
Shared textures/GPU pools переживают отдельные модели и освобождаются своим owner.
Пустой meshCount0 также публикует ненулевой pointer после4byte cookie.

Bounded parser/header/binding/null-allocation ошибки имеют собственные статусы
и cleanup pending array. Shared texture/buffer side effects не откатываются.
Это отличается от unchecked reference AV/debugbreak/OOM/C++ exception domain;
не объявлять полную failure equivalence. Неконтролируемые std::bad_alloc и
исключения callbacks/full unwind остаются открытыми. Bone vector capacity
резервируется до raw allocations, чтобы push_back не терял новый bone block.

## Проверки

9953CPU/10021HALchecks прошли standalone иphysical версия через own entry полного
клиента.12 lifetime cases: byte-exact5803byte dtor state иordered release trace;
всеflags0..7,reverse array destruction,cookie count,empty/overflow/null allocation,
owned/borrowed array release,count retention. Учитывается настоящая CRT память.
Null-allocation втрёх стадиях оставляет previous publication, очищает pending
allocations; partial model flag796 сохраняется. Truncated input иempty model
проверены как собственные error/empty policies.

12paired real fixtures/393parts прошли весь связанный route. Проверены names,
parent pointers/flags,blend count/pointers/identity matrices,vertex/index counts,
self pointer5455 иpublication/cookie.276nonzero-index parts прошли actual HALD3D9
uploads;117indexCount0 parts сохранилиFFFFFFFF offsets.59texture bindings создаются
actual RFS/DDS/D3DX9 provider. Пары используют заранее выделенные external mesh
names из tooling golden; это не доказательство полного BN loader/матриц скелета.
D3DX9_36 SHA закреплён c12f0ab0338eb5031d3d04beaf7208ac848f7e037d21ff963d2af90221cbe935.
Физической отрисовки455shader/animation/skinning этот тест не выполняет.

В lab5C APIs иCRT provider происходят изRFClient455Models lifecycle/loader objects.
Source/modernCOFF x86/MT. Отдельная D3D9 test TU не смешивает старые D3D8 headers.
Native full-client результат равен component10021checks. Owned heap/COM/Dmalloc
balance0; game DLLs не загружены, normal WinMain ивходные EXE не исполнялись.
RF_CLIENT_455_MODELS defaultOFF,driver явноON;вnormal unused APIs stripped.

Все прежние scoped regression checks прошли наcurrent lab:legacy245+6732,
mesh086304,bindings2237,meshCPU14562,clock1443,maptime314,weather703,resource30,
commands432/2628+20actual input,shared159173,texture8440. Platform01/device69checks,
0warnings/errors,COM/Dmalloc0, прежниеframeSHA сохранены.289normal modernCOFF/MT.
Current PE identities:inventory/client455-models-link.json;normal immutable
snapshot character455-model-pipeline вinventory/client-first-build.json.

## Следующая работа

Normal model manager/file dispatch итипизированные consumers ещё legacy. Нельзя
cast старый CHARACTEROBJECT вknown455prefix: вrecovered legacy header parent
pointer+268,count+528,meshptr+532;455читает+272/+532/+536. Меши1072/36 также
несовместимы с5803/64. Смена layout требует согласованного переноса callers,
renderer/D3D9 иanimation consumers; одной заменой dispatcher это не решается.
Дальше — actual file/manager route иполный455model/character layout, BN/skeleton,
transforms/animation/skinning/declaration/shaders иnormal integration.
Other mesh formats/partial failure/debug logger/reset/device loss/unwind открыты.

Воспроизведение, Python через Invoke-Python.ps1:
audit_client455_models.py;build_client455_models.py;probe_client455_models.py [--gpu];
prepare_client_build.py;probe_client_character_build.ps1 [-HelperLab];
verify_client455_models.py [--lab];probe_client455_models_client.py.
Для HAL/MSBuild стандартная escalation;новыйrun всегда вfresh owned work/m9 cwd.
