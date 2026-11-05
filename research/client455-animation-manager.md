# AnimationManager 455: коллекция, кэш и владение

2026-11-05. M6, выбранный source участок; normal consumers и M9 ещё открыты.
Серверы и оригиналы не изменялись, входные EXE не исполнялись.

## Эталон

x86, image base0x400000; основной PE SHA-256
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
backup SHA-256
`46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
25 выбранных диапазонов равны обоим pin, точные размеры/хеши —
inventory/client455-animation-manager-reference.json. Основные функции:

| Роль | VA | RVA |
|---|---|---|
| Constructor | 5E1150 | 1E1150 |
| Cache zero4000 | 5E11D0 | 1E11D0 |
| Counter reset | 932480 | 532480 |
| Hash row/column | 9321B0/9321F0 | 5321B0/5321F0 |
| Cache find/insert | 932240/9322D0 | 532240/5322D0 |
| ID by name | 9329B0 | 5329B0 |
| Last-backslash suffix lookup | 932A60 | 532A60 |
| Full name lookup | 932B30 | 532B30 |
| ID lookup | 932BF0 | 532BF0 |
| Delete by name/ID | 932D30/932E20 | 532D30/532E20 |
| Release records/vector | 932F30 | 532F30 |
| Vector growth/push | 933020/933230 | 533020/533230 |
| Register | 933280 | 533280 |
| Interface get-or-register | 931F80 | 531F80 |
| CUnity GetAni, still reference | 5E12C0 | 1E12C0 |

Allocation0xFBC=4028 подтверждена caller5E1090. Поля: self0, allocator padding4,
vector begin8/end12/capacity16, counter20=0, nextId24=1, cache28 из1000 pointers.
Constructor устанавливает self=this, zero vector/cache и counters. Empty allocator
copy5EA9D0 не пишет ни одного байта, поэтому +4 сохраняется. Это отличается от
legacy AnimationManager24; смешивания его heap/STL с новым типом нет.

Register копирует/понижает регистр короткого имени, возвращает false при дубликате,
создаёт record284, присваивает ID264, добавляет указатель и только затем увеличивает
nextId. Файл при регистрации не загружается. Capacity растёт max(size+1,capacity*1.5)
с integer truncation и reference пределом3FFFFFFF. Счётчик ID переполняется DWORD;
counter20 не является размером vector. Reset counters не очищает vector/cache.

Для ID суммируются четыре байта. Row=(sum%113)^2, column=(7*sum%113)^2.
Три ячейки:20*((row+i)%50)+(column+i)%20. На insertion используются первый пустой
slot/совпадающий pointer; при трёх занятых заменяется первый. Проверка ID читает
record264, затем fallback linear scan. IDs1/256/65536/16777216 имеют одинаковую
сумму1 и slots65/86/107; этот collision/replacement проверен отдельно.

Delete освобождает record, сдвигает хвост и продолжает цикл, поэтому удаляет все
совпадения. Кэш не инвалидируется. Release932F30 уничтожает records, освобождает
vector, обнуляет только8/12/16; nextId/self/cache сохраняются, включая freed
pointer bits. Проверки наблюдают их без разыменования после освобождения.
Record destructor освобождает raw268, descriptor cookie272-4, extra280, затем
manager освобождает сам record. Suffix lookup включает последний backslash;
ключ `\walk.ani` отличается от `walk.ani`.

## Source и проверка

scripts/native/client455_animation_manager.{h,cpp}:11C APIs, отдельный собственный
тип4028, проверенный /MT archive RFClient455AnimationManager.lib. Существующие ANI
owner/load APIs используются напрямую. В source нет старого Character SDK cast.
Обычная сборка имеет доступ к библиотеке, но normal CUnity/ChAnimation ещё legacy:
11 APIs вызываются в full-client lab; normal unused APIs удалены линкером.

87 targeted assertions в4группах standalone и в полном client lab: whole4028
constructor с padding sentinel,14registration/growth шагов, lower/duplicates,
name/ID/suffix lookup, cache collisions, duplicate IDs/delete, IDwrap/emptyname,
owner release order, explicit owned name/OOM policy и один real ANI.
ANI из Character/Monster/Ani/ZETSOHOLIDAY_PEACEDAMAGE_01_00.ANI:
27746B/85tracks/max3200, SHA-256
`686be74f8d0e3697848dd640950311ce6453090d3f63969f701f1c69cf1ecde8`.
Он скопирован под короткое собственное имя, загружен existing source loader,
найден по ID и освобождён через manager. Повтор loaded и sticky failure также
проверены. Это не доказательство игрового выбора ресурса/animated draw.
Heap/Dmalloc balance0, игровые DLL не загружены. Графические/clock/texture/bulk
ANI suites не повторялись: их код не менялся, normal runtime byte equality
проверена после исключения timestamps относительно loop-clock-final.

Normal snapshot character455-animation-manager:2451456B/entry RVA1BC450,
SHA `b597d3ef8287197f6de3da1ef4e2ab360fc87ac6b65fb809c3de2e7cf756bbe0`.
Normal291modernCOFF x86/MT; прежний engine archive не изменился.
Lab192clientTUs,5258752B/entry RVA89EF,
SHA `67d3766c98d5bab983baa7003cc0267b42ca909d1b0898a865b37e809157b6cc`.
Actual E8 REL32 callsites и provider/RVA каждого API — в link report.

Gate inventory/client455-animation-manager-checkpoint.json. Raw MCP:
artifacts/character-animation455/manager-*.json; ownedab74ea29/4c43ad92 closed/save.
COFF verifier теперь может учитывать static function symbols при явном
include_static=True; прежний default external-only не менялся.
test_coff_callers.py:4testsPASS на реальных static/external callers и повреждённых
static offset/CALL opcode. Это отдельные небольшие parser проверки.

## Открытые контракты

Два выбранных importer mode9352A0/935320 оба делают синхронную dispatch. Для
worker935450 IDA не вернула xrefs, точного VA в immediate bytes обоих PE нет.
Это не полное доказательство недостижимости через вычисляемый адрес/внешний вход.
Worker остаётся исследовательским пробелом, не установленной зависимостью этих
двух loader routes. Не начинать повторный reverse его известного тела без caller.

Normal CUnityAniMgr/CAniData/actor lifecycle/transition consumers ещё legacy.
У455 CUnity GetAni есть guard IDFFFFFFFF и различающаяся по mode>=2 обработка
неудачной загрузки с UI/localization; это ещё reference, не source implementation.
Перед normal переключением нужен типизированный контракт, не rawcast record284
к old ChAnimation280/manager24 или к старому SDK heap.

Long names>=255, printf-percent names, null/missing-backslash/OOM/exception/unwind
в исходном коде могут быть undefined/unchecked. Own guards и cleanup на failure
не заявлены как их эквивалент. Locale/non-ASCII/private C++ allocator/STL ABI,
full normal Character455/D3D9 draw и M6F/M9 остаются открыты.

Воспроизведение через scripts/Invoke-Python.ps1:
audit_client455_animation_manager.py → build_client455_animation_manager.py →
probe_client455_animation_manager.py → prepare_client_build.py →
probe_client_character_build.ps1 [обычный/-HelperLab] →
verify_client455_animation_manager.py [--lab] →
probe_client455_animation_manager_client.py → audit_client_executable.py
--label NEW_LABEL → checkpoint_client455_animation_manager.py.
