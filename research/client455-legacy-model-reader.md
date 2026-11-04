# Промежуточный reader MSH/BN455

2026-11-05. Source client455_legacy_model.h/.cpp восстанавливает выбранный контракт
93C2F0 иlifetime промежуточных objects. Это следующий source unit M6, не полный
BNruntime loader/скелет/анимация. Он пока проверен standalone и не подключён
к normal либо fullclient lab dispatch. Предыдущие клиентские PE этим этапом не менялись.

## Эталон

Оба x86 RF_Online.bin, image base0x400000, закреплены:
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b и
46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
7полныхbodyranges равны в обоих PE. RVA/size/SHA —
inventory/client455-legacy-models-reference.json. Список включает importer/converter
как исследуемые зависимости; их наличие в report не означает source implementation.

| RVA | Bytes | Контракт |
|---|---:|---|
| 0x53C020 | 35 | Constructor part720:zero5pointers,прочее нетронуто |
| 0x51C270 | 134 | Part dtor:free/null696,700,704,716,712 |
| 0x51FB20 | 99 | Import release:reverse720array/cookie,then12/20 |
| 0x53C2F0 | 1136 | Raw legacy reader |
| 0x53C760 | 5 | Raw import thunk |
| 0x53C770 | 291 | File importer, source pending |
| 0x53CD60 | 4227 | Runtime converter, source pending |

Owned IDA926983beclosed/save. Raw artifacts/character-legacy455 содержит ctor/dtors,
critical instruction lists иполный хвост converter93CD60(offset250,328lines).
Вместе с artifacts/character-gpu455/next-2.json теперь есть все578lines converter;
не декомпилировать заново без потребности в отдельных инструкциях.
Parser181lines уже был сохранён вcharacter-manager455/manager-plus-4.json.
Ни reference EXE, ни серверные файлы не исполнялись/менялись.

## Контракт

Input начинается WORD count, magic отсутствует. Каждый record:693byte header,
28*WORD(header392) vertices,88*WORD(header394) faces, затем physique branch.
Header DWORD642 задаёт compact. Count physique —WORD396.

Промежуточный model28: pointers4/12/20 ctor обнуляет, WORD2=count;
DWORD24 перезаписывается compact flag каждой записи (последняя побеждает).
При count0 этот DWORD не записывается. Остальные bytes не инициализируются.
Array имеет DWORD cookie count, затем count*720 records; count0 всё равно
выделяет cookie и публикует ненулевой pointer+4.

Part720: первые693 bytes — raw header, padding693..695 нетронут.
Pointers696/700/704/716/712 ctor=0. Vertices696 иfaces700 выделяются даже при size0.
Plain branch копирует424*physique bytes в704, при physique0 сохраняет null.
Никакого декодирования имён/весов plain branch на этом этапе не делает; даже
influence count5 сохраняется. Count708 остаётся allocator-dependent приplain.

Compact branch читает DWORD namesCount в708. При0 никаких names/compact/expanded
allocations иникаких physique bytes не потребляет, даже при physiqueCount>0.
При namesCount>0:100*names в712;40*physique в716;424*physique в704, включая size0.
Expanded record: первые8bytes копируются изcompact, influence count signed+4.
Положительные influences: dictionary index DWORD+8+4*i;strncpy99 вexpanded+8+100*i,
затем forcedNUL+107+100*i;weight+24+4*i →expanded+408+4*i.
Все unused bytes expanded allocation нетронуты. Negativecount не запускает loop.

Подтверждены signedjle93C5E6/signedjl93C676 иx87fld93C641/fstp93C64E.
Поэтому source copy weight использует x87, включая masked sNaN quieting.
Обычная memcpy здесь не даёт того же результата для signalingNaN.

Dtor part освобождает/null указанные5pointers вфиксированном порядке. Model release
берёт число изcookie, уничтожает parts в обратном порядке,freecookie/null4,
затемfree/null12,20. Model28 освобождается отдельным own Delete wrapper.
Count/flags/остальные bytes release не обнуляет.

## Проверки и границы

Standalone x86/MT, /O2/W4/WX. 4606native checks:

- 12pinned realBN/455records +5synthetic/4records. Сравнены whole720part и28model,
  все allocation sizes/opaque payload bytes,ctor/dtor mutations иorder release.
  Synthetic содержитnonzero geometry/plainphysique/compact names+weights,
  zero dictionary сpositivephysique,emptyphysique сnonzero names,emptymodel.
- Golden получается изранее проверенного независимого Python framing reader
  имоделиcompact expansion поинструкциям. Собственный test allocator заполняет
  blocksA5, чтобы проверять именно сохранение unwritten bytes, а не приписывать
  эталонному allocator фиксированные значения. Реальные heap blocks затем освобождаются.
- 1183prefix truncations сконцомinput упирающимся вPAGE_NOACCESS,output/consumed
  unchanged,0leaks.7failure injection points allocations,cleanup всехconstructed
  parts. Huge dictionary count,influence>4,index-out-of-bounds,arguments,trailing.
- Weight bitspositive1ULP/negativezero/+sNaN/-sNaN в12maskedFPmodes;control unchanged.
  6Python tests oracle/boundaries. Heap0. Входной PE не выполнялся.

Безопасные bounds/influence<=4/index/nullalloc/status/cleanup — собственная адаптация;
unchecked reference способен читать/писать вне границ, аварийно завершаться или
выбрасывать исключения. Полная equivalence этих domains не заявлена. Вunmasked FP
environment,private allocator/STL ABI/exception unwind иподозрительных состоянияx
исходники не сертифицированы.

Файл BN пока только разобран впромежуточные данные. File importer93C770,converter
93CD60,real runtime matrices/parent selection/vertexconversion/material/GPU и
dispatcher9238A0 остаются следующим шагом. Пары по одинаковому basename — fixture
choice, не доказательство runtime selection.

Воспроизведение через scripts/Invoke-Python.ps1:
test_legacy_model_oracle.py; audit_client455_legacy_models.py;
build_client455_legacy_models.py; probe_client455_legacy_models.py.
Reports client455-legacy-models-reference/build/cpu.json. Последний report содержит
SHA source/build/golden/native output иownedEXE path+SHA+entryRVA.
