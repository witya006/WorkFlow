# Source MESH08 framing и реальный corpus455

2026-11-05, M6. Формат прочитан lossless; собственный C++ decoder/writer собран
как клиентская зависимость и проверен в own entry полного проекта. Это format
module,не полный607line runtime loader. Normal LoadRealData пока не переключён
на новый путь: materials/skin resolution/GPU/publication ещё требуют source.

## Формат и подтверждение

Эталон x86/base0x400000: current SHA
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b,
backup46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
audit_client_mesh08_reference.py проверяет3bodies и12instruction sites в обоих PE.
Detector91F250/RVA51F250,loader922A00/RVA522A00,bone resolver93CB00/RVA53CB00.
Loader starts cursor8;count WORD+6;header advance693;counted payload multipliers
64/2/404 иindex gate64000 подтверждены инструкциями,а не только pseudocode.

File:6bytes MESH08,WORD meshCount,затем meshCount последовательных records.
Относительно начала каждого record:

| Данные | Offset | Размер |
|---|---|---|
| Original mesh metadata |0|693 opaque bytes |
| Vertex count |693|WORD v |
| Vertices |695|64*v |
| Index count |695+64*v|WORD i |
| Indices |697+64*v|2*i |
| Bone record count |697+64*v+2*i|WORD b |
| Bone records |699+64*v+2*i|404*b |

Все count/index fields little endian. В693byte header присутствуют старые count
fields,но framing использует последующие counted arrays. Не подменять одно другим.
404byte record:DWORD influenceCount и4слота имён по100bytes. Resolver собирает
первые уникальные имена,ищет external/local parent meshes изадаёт inline matrices.
Эти runtime effects reader пока не исполняет. Float/NaN bits,порядок индексов,case
имён ивсе unknown header bytes сохраняются. Reader не делает filename lowercase,
GPU rebase илиповторную normal/UV conversion;это другой слой runtime loader.
Reference не проверяетEOF;trailing bytes принимаются/сохраняются. Увсех858samples tail0.

## Corpus

Проверены2708loose .msh/.bn files изустановленного reference tree.858имеютMESH08;
1850other-prefix files не классифицированы этим аудитом. RFS/архивные модели иполный
resource inventory вне данного census.858/858декодируются иbyte-round-trip равен:
515096894bytes,12090meshes,5153052vertices/indices,412222bone records.
Нет framing errors,trailing bytes,index count>64000,out-of-range indices или
influenceCount>4. Равенство суммарных vertex/index counts не принято как правило:
synthetic cases проверяют разные значения,включая65535vertices/0indices.
Полные per-file SHA/offset/count manifests — ignored artifacts/character-mesh08/corpus.json;
сводка иегоSHA — inventory/character-mesh08-corpus.json. Оригиналы только читались.

12representative samples/393parts скопированы вwork/.../mesh08-native:включены
rigid/skinned иlargest mesh/vertex/index/bone samples. В golden.bin фиксированы
offsets/counts иbyte hashes каждого payload. Копии дополнительно проверяютсяSHA256.
Исходный C++ reader сверяет pointer offsets/counts/байты,восстанавливает stream
в новый buffer инаместе.6304native checks и1309guard-page truncation cases прошли
standalone ив полном клиенте.7Python tests включают roundtrip,all truncations,
wrong magic/count,64000/64001indices,opaque NaN/negative zero иunclamped index values.

## Source API и границы

scripts/native/client455_mesh08.h/.cpp — собственные bounded views идвеC API:
RF455_DecodeMesh08/RF455_EncodeMesh08. Views24/20bytes x86,pack4,не455ObjectMesh5803.
Reader не выделяет память;caller владеет bytes/record storage. Result публикуется
только при success;record storage приerror может бытьpartial. Writer проверяет
capacity/overflow до записи. Length/capacity errors — own safety policy,не
воспроизведениеunchecked AV/OOM/debugbreak reference. Это явное ограничение parity.
Модуль x86/MT;source/library/corpus hashes проверяются build driver.
RF_CLIENT_455_MESH08 defaultOFF,driver explicitON. Legacy overlays не менялись.
В normal build нетruntime consumer:linker удаляет unused format APIs. В lab обе
API связаны с RFClient455Mesh08:mesh08.obj ивызываются actual helper object.

Normal2451456bytes,entryRVA0x1BC4B0,SHA
43863bc4334d896a91888f0b132b79d7e85974b519073c2ebad8a4995b89c6af,
snapshot artifacts/client-first-build/mesh08-format;не запускался.
Lab4483072bytes,entryRVA0x8125,SHA
d8edc962d7985e2598cd1ed4080c416e03ff94ae88f2d4875cf3473657d4f1a6.
Lab decoderVA6B0400/RVA2B0400,writer6B0700/RVA2B0700;неинструкционная идентичностьC++.
6304format,6732InitVertex/245bindings,1443clock/314map-time/703weather/30resource,
432command cases/2628checks+20actual input прошли.289modern objects иformat object /MT.
Platform01/device2GPUcases/69checks,0warnings/errors,Dmalloc/COMbalance0,FPU007F,
frameSHA равен прежнему просмотренному. Это regression существующей map/weather
сцены,неMESH08/CharacterGPU acceptance. ИгровыеDLL/referenceEXE/normalWinMain не запускались.
Owned IDAeb76ecefclosed/save;rawqueries вartifacts/character-mesh08.

Далее source runtime model construction:metadata/matrices,material names/texture
loading,first-match local/external parents и404-record bone order;затем shared
GPU upload/index rebase/publication/release иD3D9consumer. Только послеэтого
переключатьactual normal LoadRealData исравниватьреальныеигровые сценарии.
M6/M6F/M7/M9 остаются открытыми;полноту клиента этот модуль не доказывает.
