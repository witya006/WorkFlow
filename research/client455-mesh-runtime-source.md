# Создание и заголовок меша 455, запросы материалов

2026-11-05, M6. Восстановлены три исходные CPU-функции: конечное состояние
конструктора меша, применение заголовка MESH08 с производными матрицами и порядок
запросов текстур. Они проверены отдельно и в own entry полного клиентского проекта.
Физический TextureManager, shared GPU buffers, полный loader и нормальный запуск
пока не используют этот новый путь.

## Бинарное основание

Эталоны x86/base0x400000: current SHA
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b,
backup46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
Пять тел совпадают в обоих PE: constructor9214E0/RVA5214E0 (450bytes),
overwritten subobject constructor920E40/520E40 (222), loader922A00/522A00 (3739),
texture lookup934120/534120 (324), texture load934A20/534A20 (829).
Последние два пока служат справочником backend, не объявлены исходно восстановленными.

Матрицы в этом пути вызывает d3dx9_36.dll через thunks854130/454130 и85412A/45412A.
Их IAT slots сверены с импортируемыми именами D3DXMatrixInverse/Multiply. DLL возле
эталона побайтово равна установленной C:/Windows/SysWOW64/d3dx9_36.dll:
SHA c12f0ab0338eb5031d3d04beaf7208ac848f7e037d21ff963d2af90221cbe935,
x86,3734536bytes,version9.19.949.2111. Authenticode: Valid,Microsoft Corporation.
Own probe загружает именно этот абсолютный системный путь, входной EXE не исполняется.
Публичные DLL export-entry RVA:Inverse1654A1,Multiply164F24;preferred DLL image base
400000. Это отдельный модуль; внутренний CPU dispatch ещё не картирован.
inventory/client455-d3dx9-provider.json фиксирует SHA/x86/RVA инаблюдаемый результат.

## Состояние и численные особенности

Constructor сначала вызывает subobject initialization без выделений, затем
перезаписывает все5803bytes нулями. Исходник сохраняет конечный результат: четыре
поля1.0, девять полей-1, остальные0; cumulative constructor count/byte counter
увеличиваются с DWORD wraparound. Это восстановление final state/counters,
не всего C++ класса, его owning methods или деструктора.

Header-derived CPU fields закреплены инструкциями и golden:

| Вход | Runtime mesh | Действие |
|---|---|---|
| DWORD598 | float5339 | x87 FILD signed, при отрицательном +2^32, FSTP |
| float602/606/610 |5459/5463/5467| x87 copy |
| float614/618/622 |5471/5475/5479| x87 copy |
| byte634/639 | DWORD5359/5143 | zero extend |
|16bytes646|5579| raw copy |
| matrix200 |4510,4574| raw copy |
| matrix264 |4702| raw copy |
| matrix328 |4766| raw copy |
| inverse(matrix328)*matrix200 |5022| D3DX9;потом translation row5070/74/78=+0 |
| inverse(matrix200) |4638| D3DX9 |
| name/parent100-byte fields |0/256| CRT basename+extension,case сохраняется |

Self pointer5455 задаётся на собственный subobject+5163. Перенесены поля5363/5115,
vertex/index counts5086/5090 и восемь точных special-name веток5575/5571/model+796.
Несовпадение имени не очищает ранее заданные special flags.

Закреплённая D3DX9_36 на текущем CPU даёт наблюдаемое отклонение1ULP.
Для diagonal(2,2,2,1) прямой вызов экспорта вернул inverse diagonal bits
3EFFFFFF/3EFFFFFF/3EFFFFFF/3F7FFFFF, а не математические0.5/0.5/0.5/1.
Synthetic composition с diagonal(3,4,5,1) даёт bits
3FBFFFFF/3FFFFFFF/401FFFFF/3F7FFFFF. Это отдельно проверено прямым вызовом DLL,
затем точным byte comparison исходного пути. Не заменять математически идеальными
константами/собственным inverse. Это наблюдение текущего provider/CPU dispatch,
не доказательство одинакового результата на всех CPU. Reciprocal approximation —
предположение о причине отклонения; инструкции внутренней реализации DLL не исследованы.

## Материалы

Первый непустой путь требует backslash. Lowercase применяется только к basename
в самом входном693-byte header; остальные bytes сохраняются. До первого .dds
вставляются _NOR/_SEQ/_REF. Если .dds отсутствует, три имени остаются равны основному.
Сначала выполняются три auxiliary lookup и primary lookup. Четыре load attempts
выполняются только при primary miss, включая auxiliaries, уже найденные в cache.
После успешного load повторяется lookup соответствующего имени. Missing texture
ID0 не является общей ошибкой загрузчика. При пустом primary auxiliary fields
сохраняются, main ID задаётся0.

Secondary сохраняет case. Его обратный поиск пропускает индекс0: ведущий единственный
backslash остаётся в имени. Пустой secondary всё равно проходит lookup, затем
load выполняется только при непустом имени и miss. Directory — object+276 при
непустом значении, иначе fallback TextureManager+28.

В исходной функции обязательны реальные lookup/load operations от backend;
успешных no-op implementations нет. Scripted provider существует только в tests
и проверяет восемь последовательностей/ID writes/изменение header. Физическая
загрузка текстур и устройство TextureManager ещё не восстановлены этим модулем.

## Проверки и подключение

По сохранённым offsets заново исследованы именно header domains858files/12090meshes,
без повторения framing roundtrip.8659primary paths пустые; остальные3431 имеют
backslash и .dds basename. Нет unterminated/non-ASCII/% strings, нечисловых matrix
или scalar floats, nonaffine matrices либо нулевых binary64 numeric3x3determinants.
Это ограниченная классификация, не полная оценка обусловленности/сингулярности.

14562native checks прошли standalone/full-client:12real files/393parts, полные
5803-byte golden comparisons с двумя отдельно проверяемыми computed ranges,
матричные алгебраические invariants и synthetic exact composition.12FP modes:
uint32 rounding boundaries,negative zero,denormal,inf,quiet/signaling NaNs,
control word/stack balance. Constructor wraparound, восемь special names,
повторное применение flags, name/path/argument errors и два singular cases проверены.
При singular/invalid input собственные ошибки заменяют unchecked reference failures;
OOM/unmasked FP/locale/failure unwind остаются открытыми.

RF_CLIENT_455_MESH_RUNTIME defaultOFF, driver явно ON; source macro только на labfile.
В lab три API происходят из RFClient455MeshRuntime:mesh-runtime.obj/x86/MT и вызываются
actual helper object. В normal unused APIs удалены; normal model-loader не подключён.
Normal2451456bytes,entryRVA1BC4B0,SHA
6f486f1f4ef950d207d9fd9cba9d2e647d7538954185c39adfeec7d5c9316a0b,
snapshot mesh455-header-material;не запускался. Lab4585984bytes,entryRVA828D,SHA
f55fdb172661cbcfdf131aa3d7a0ddba1413b2039151ff866c88f78f2a3c42cb.
Construct/Header/Materials VA6C6250/6C5D20/6C6370,RVA2C6250/2C5D20/2C6370.

Текущие регрессии:mesh08 6304,binding455 2237,legacy245+6732,clock1443,map-time314,
weather703,resource30,time-command432cases/2628checks+20actual input.289modern COFF/MT.
Platform01/device2GPUcases/69checks,0warnings/errors,Dmalloc/COMbalance0,FPU007F;
обаframeSHA равны прежним просмотренным. Это map/weather regression,CharacterGPU открыт.
GameDLLs/normalWinMain/referenceEXE не запускались. Owned IDA716ae4fa закрыта/save.

Evidence: inventory/character-mesh08-headers.json,client455-mesh-runtime*.json,
character-mesh455-runtime-graphics.json. Raw queries/decompiles — artifacts/character-mesh08.

Далее: actual TextureManager934120/934A20 иего provider933DE0;shared vertex/index
allocators93E000/93E180, index rebase((vertexOffset%0x231860)>>6), zero-index branch,
publication/release/unwind иD3D9consumer. Потом normal model dispatch иполные
skeleton/animation/game scenarios. M6/M6F/M7/M9 остаются открытыми.
