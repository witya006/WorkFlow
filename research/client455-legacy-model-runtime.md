# Source455: legacy MSH/BN runtime

2026-11-05. Завершён выбранный source unit M6: importer93C770/converter93CD60,
vertex/UV/physique/indexing/bone kernels. Полный клиент вызывает его через own lab
entry. Normal dispatcher,ANI,animation/skinning draw/shaders/typedconsumers ещё
открыты. M6/M6F/M7/M9 не закрыты, полного C++/STL/heapABI это не доказывает.

## Основание

Оба RF_Online.bin x86,base0x400000:current
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
backup46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
9bodyranges equalbothpins;RVA/size/SHA —client455-legacy-runtime-reference.json.

| RVA | Bytes | Контракт |
|---|---:|---|
| 0x53B020 | 49 | Vertex28→64,positions/negative normals |
| 0x53B5F0 | 23 | UVu/1-v |
| 0x53AA10 | 704 | Physique indices/3weights/fourth implicit/diagnostics |
| 0x53B130 | 452 | Vertex64→36 |
| 0x53B310 | 731 | First-match memcmp64 dedup/VB+IB |
| 0x53BC40 | 502 | Legacy424physique bone bindings |
| 0x53A9D0 | 51 | Удаление suffix с последней точки |
| 0x53CD60 | 4227 | Converter |
| 0x53C770 | 291 | RFS/loose importer/parser/rawfree/log |

Source client455_legacy_runtime.h/.cpp →RFClient455LegacyRuntime.lib;intermediate
reader/lifetime —RFClient455LegacyModel.lib. Raw artifacts/character-converter455,
owned0d9553e1/08d81b2fclosed/save.578lineconverter ужеcached:250head вcharacter-gpu455/
next-2.json,328tail вcharacter-legacy455/converter-tail.json. Не выгружать заново.
Входные EXE не запускались, installation/server не менялись.

## Подтверждённые детали

File importer не проверяет расширение:RFS→loose→parser→rawfree→безусловный
`ImportMeshorBoneData( %s ) :NULL` даже приуспехе. Missingfile diagnostic включает
errno/strerror. Callbacks различают ANSIlogger иOutputDebugStringW;fullrenderer
owner ещё должен подключить их. Default successful providers нет.

Converter выделяет cookie5803array,изmodel.name4 удаляет suffix споследнейточки,
добавляет.mtg,открываетloosefile. MTG84bytes/face:3records28,первые3float каждой
→vertex52/56/60 черезx87fld/fstp,включаяsNaNquieting. Shortread boundedIOerror —
ownpolicy,неuncheckedreference. Expandedbuffer выделяется даже приfaces0.

Material/header kernels переиспользованы после проверки offsets/flow. Counts5086/
5090=3faces записаны доmatrix calls. D3DX9_36 настоящий,pinned. После local/external
parents,если последнийimport.compactflag24==0:mesh4702=mesh4574*parent4638 длявсех
связанныхмешей. Не заменено flag каждойзаписи. Vertex64positionsx87;normalsFCHS;
initialweights1/0/0,4WORDindices0. Persistent scratch vertices/unique/rawindices/
rebasedindices zero-initial/growwithoutshrink,unwrittenfields retained. Otherglobal
users/threading ещё открыты;sourceowner сериализует этотcontext.

Physique namesunique/firstencounter. Record обнуляет3weights/4indices vertex;
первые3influences пишутweightsx87,четвёртый толькоindex. Sum16+12+20 черезx87
послекаждогоinfluence,FCOM/parity0..1 диагностика иNaN поведение сохранены.
Unsafeindex==vertexCount/negative/influence>4/stackname overflow —ownederrors.

Faces→3*faceCount vertices64+UV+optionalMTG. Mode2+physique+firstinfluenceCount>2:
expandedarray4506 сохраняется,VB/IB не строятся;mesh dtor освобождает4506.
Остальные:memcmpвсех64bytes/firstmatch,mode4unique64upload,mode2convert36. Conversion
loops expandedCount,uploaduniqueCount. У93B130 всеmappedfields DWORDcopies,кроме
weight12x87,дажеscalar remainder. Декомпиляторfloat labels здесь неточны.

Indexbase=(vertexAbsolute%2300000)/stride,WORDwrap. IBattempt послеVBfailure.
Unknownmode emitsVDM/base0/stillIB,а не successstub. Legacy424bone names+8 distinct
fromMESH08+4/404. Externalpriority/localfallback/firstmatch;identities beforepointer
copy,overlap31+ сохранён. Missing occurrences повторяютwide `Error: Can't Find Parent!!`
сnewline;UTF16RVA0x73B118 сверена обоимPE. Послеpublication536/count532,uppercase
первогоиз2meshname tokens==BONE ставит5567. Existingarray overwrittenwithoutfree.

## Проверки

66627CPUcapture/14896HAL,physicalfullclient результат идентичен:

- 17files486parts:12realBN,2reallegacyMSH,3synthetic. Mode4+2:34runs972parts,
  832HALindexeduploads/2CPUretained. Whole retainedarrays/matrices/order/parents/
  flags/counts/names/BONE/specials проверены.
- IndependentPython expectedvertices/weights/UV/tangent/dedup/index/binding tokens;
  capture сравниваетalluploadedbytes/WORDindices,HAL проверяетdescriptors/offsets/
  COMlifetime. WRITEONLYbufferreadback не заявлен. RealMTG в14выбранныхrealinputs
  не найден;MTGsyntheticвключаетNaN. OtherFPmodes —nativeprimitive checks.
- 12actualBN→MESH08pairs393parts/276HALuploads. BN теперь импортирован ипреобразован
  source,не толькоnamesизtooling. Parent/blend pointers проверены поgolden.
- 12maskedFPmodes:±0,sNaNquiet/sign,DWORDpreservation,3weights/4indices,sum/NaNlogs,
  unchangedFPcontrol. Bindingoverlap30/31/50,missingnamerepeats/localfallback.
- Create/Lockfailure stillIB,mode2allocfailure,unsupportedmode,0/64000/64001,
  raw/rebasedindices. All7converterallocation failures cleanpendingarray without
  changingpublishedpointer/stats;sharedGPU/cache/scratch notrolledback. Missingfile,
  RFS.any,shortMTG. OwnedCRT/COM0;fullclientDmalloc0,gameDLLs отсутствуют.

10APIs (8runtime+reader/delete) sourcearchive/map иactual COFFcallers подтверждены.
Sourcex86/MT/O2/W4/WX;normal APIs unused/stripped. Currentmanager1138/model10021/
Platform01-device2cases69checks passed,framesunchanged,0warnings/errors.
Normalruntimebytes equalprevious except2timestamps;289modernnormalCOFF,
186clientlabTUs. Identities/size/entryRVA/evidencehashes:
inventory/client455-legacy-runtime-checkpoint.json. Snapshotcharacter455-legacy-models.
Остальные oldproofs исторические,не повторялись без измененийсоответствующихinputs.

## Следующий шаг и ограничения

ANIimporter93ACD0/full dispatcher9238A0,FrameMove923A40,animation/skinning/draw/
declarations/shaders/device-loss/reset/normaltypedconsumers. Нельзяcast legacy
parent/count/mesh268/528/532 в455272/532/536. BNinitialmatrices/binding теперь
проверены;полная pose/animation equivalence ещё нет. Basenamepairing —fixturechoice,
не доказательствоruntimeassetselection. Full loggerowner/locale/nonASCII/unsafeformat/
uncheckedshortread/singularmatrix/debugbreak/OOM/std::bad_alloc/callbackexceptions/
unwind domains открыты. Shared headerkernel rejects singularinput,reference
продолжает послеuncheckedD3DXfailure;этоgap. FullCharacter/M9 не закрыты.

Воспроизведение Python через scripts/Invoke-Python.ps1:
audit_client455_legacy_runtime.py →prepare_client455_legacy_runtime_inputs.py →
build_client455_legacy_runtime.py →probe_client455_legacy_runtime.py [--gpu] →
prepare_client_build.py →probe_client_character_build.ps1 [обычный/-HelperLab] →
verify_client455_legacy_runtime.py [--lab] →probe_client455_legacy_runtime_client.py.
Послеmanager/model/Platform01 regressions:checkpoint_client455_legacy_runtime.py.
HAL/MSBuild escalation разрешена;newruns вfreshwork/m9,безgameDLL околоownEXE.
