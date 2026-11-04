# Character455: record, manager, cache and raw MSH IO

Дата: 2026-11-05. Завершён выбранный source unit внутри M6. M6/M6F/M7/M9 открыты.
Новый модуль вызывается собственной точкой входа полного клиентского проекта;
обычные игровые consumers пока используют старый Character.

## Доказательства

Оба входных RF_Online.bin — x86, image base0x400000:

- основной b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
- backup 46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.

24body ranges совпали. Размер/RVA/SHA каждого:
inventory/client455-character-manager-reference.json. Ctor444bytes/92instructions
сохранён целиком с адресами/байтами/дизассемблированием в отслеживаемом manifest
client455-character-constructor-instructions.json. Audit проверяет непрерывное
покрытие body и каждый фрагмент против обоих PE.

| RVA | Контракт |
|---|---|
| 0x51C510 / 0x51C450 | Record ctor / material helper |
| 0x1DFE60 / 0x1DFED0 | Manager ctor / cache zero |
| 0x51C7B0 / 0x51C840 | Cache find / put |
| 0x5321B0 / 0x5321F0 | Cache keys |
| 0x520A20 / 0x520A80 / 0x520AD0 | Name / ID / ID-by-name lookup |
| 0x522840 / 0x521D00 | Assign-ID+append / vector growth |
| 0x522240 / 0x521960 / 0x521A50 / 0x521BC0 | Dtor / delete-name / delete-ID / clear |
| 0x531360 | Factory allocation1188/ctor/name/parent/append |
| 0x51F0A0 | Six borrowed texture pointers and alias |
| 0x51F1B0 / 0x5351A0 | Raw MSH reader / extension |
| 0x5383A0 / 0x5367C0 | RFS blob route / declared-size reader |
| 0x5238A0 | Dispatcher: исследован, ещё не реализован |

Raw artifacts/character-manager455; owned c3f13f8bclosed/save. IDB только копия
под work/client-reference, входные EXE не исполнялись. Серверные файлы не требовались.

## Record и manager

Factories931360/9313F0/931480/931ED0 выделяют0x4A4=1188bytes. Storage — prefix800+
tail388. Это подтверждённый allocation size; не все поля/методы/C++ ABI восстановлены.

| Смещение | Подтверждённое поле |
|---|---|
| 0 / 4 | DWORD ID / name256 |
| 260 / 264 | DWORD loaded/ownership / BYTE loading |
| 268 / 272 | Unknown DWORD / external model pointer |
| 276 / 532 / 536 | Texture directory256 / mesh count / mesh array |
| 540 / 604 | Две4x4матрицы |
| 672 / 684 / 696 / 716 | Ctor160 /160 /FFFFFFFF /3000 |
| 720 / 792 / 796 | Material68 / float1 / special flag |
| 1184 | Status, используется FrameMove923A40 |

Ctor zero1188, обе identity matrices, diffuseRGB0.6/ambientRGB0.3/alpha1 и поля
из таблицы. Полное состояние получено bounded interpreter из92instructions и
pinned float constants;91C450 моделируется по отдельно pinned body.9small tests
проверяют ограничения interpreter. Это instruction-derived oracle, не PE execution.

Manager4148: opaque0, vector4/8/12, nextID16, name128+20, cache1000pointers+148.
Ctor сохраняет opaque/name; zero vector/nextID/cache. Первый ID0 валиден; ID по
отсутствующему имени тоже0. Имена case-sensitive/first-match; factory не unique.
Append присваивает nextID++ до vector growth. DWORD wrap, floor1.5x capacity,
минимум size+1, максимум0x3FFFFFFF.

Cache: sum=сумма4байтID, k1=(sum%113) XOR2, k2=((7*sum)%113) XOR2.
Это XOR, не квадрат. Три пробы slot(p)=20*((k1+p)%50)+(k2+p)%20, p0..2.
Lookup проверяет record.ID, затем first vector match. Put — первая пустая,
тот же pointer останавливает поиск; все3заняты → replacement первой.
ID1/256/65536/16777216 коллидируют в65/86/107.

Delete-name/ID удаляют все совпадения с сохранением порядка. Record260 определяет
ownership массива536. Clear сохраняет capacity/nextID/name/cache; dtor освобождает
vector иzero только3егоpointer. Cache ни одним из них не инвалидируется, может
содержать dangling pointers. Это сохранено; тесты проверяют cache bytes и не
разыменовывают freed records. Caller lifecycle ещё требует проверки.

## Raw MSH и refresh

Extension ищет '.' справа; без точки возвращает filename+1. XMSH принимается как
MSH, .MSH тоже. RFS/declared-size read идёт перед loose file, использует прежний
source RFS cache. Zero-size allocation с ненулевым pointer успешна. Собственный
output публикуется только при успехе; bounds/short-read/null allocation policy
отличается от unchecked reference failure domain.

Refresh mesh5803: IDs5111/5123/5127/5767/5771/5775 → pointers5107/5115/5119/
5791/5795/5799; alias5283=pointer5115. Все прочие bytes сохранены. AddRef нет,
textures принадлежат TextureManager и должны жить дольше модели.

## Проверки

client455_character_manager.h/.cpp → RFClient455CharacterManager.lib, x86/MT,
/W4/WX. RF_CLIENT_455_CHARACTER_MANAGER defaultOFF, driverON. В lab отдельный
D3D9TU.13 C APIs реально вызваны из test TU и происходят из source manager.obj.
Normal APIs unused/stripped; обычный игровой dispatcher не переключался.

850CPU/1138HAL checks, полный клиент даёт идентичные1138:

- Whole1188byte ctor vs instruction oracle/12FPmodes, unchangedFPcontrol;
  whole4148byte manager ctor, opaque/name preservation.
- 50records/vector growth/duplicate names+IDs/firstID0/case/find/cache collisions/
  replacement/ID validation/DWORD wrap/delete-all/order/clear/dtor.
- Реальные /MT allocations, owner/borrower mesh cookie release, отсутствие утечек;
  собственные name/nullallocation failure policies и consumedID при append failure.
- 18rawreads:6IOfixtures+12realMESH08. Одна настоящая модель в собственномRFS,
  остальные loose; все raw bytes сравнены с pinned sources до разбора. Archive
  precedence/shortarchive→loose/empty/no-dot/dot/case/invalid-extension проверены.
- 12paired real models/393parts: factory→rawIO→model pipeline→refresh→delete.
  276HALuploads/59positive texture pointers. Wholemesh5803 refresh сравнение,
  AddRef/Release observations проверяют отсутствие дополнительных refs. Skeleton
  names пока из tooling golden, не полного BN loader.

На текущем lab также model10021checks иPlatform01/device2cases/69checks,
0errors/warnings/ownheap/COM/Dmalloc; прежние frameSHA совпали. Прочие старые
proofs исторические, повторно не запускались. Normal runtime bytes равны предыдущей
ревизии после исключения двух timestamps.289normal modernCOFF x86/MT,
185clientlabTUs. PE identities/size/entryRVA/evidence hashes:
inventory/client455-character-manager-checkpoint.json.

## Границы и продолжение

Dispatcher9238A0 пока исследован. Возвращает1 при loading264 либо loaded260.
MESH08 branch требует external272 иparent.loaded260. После loading=1 ошибка
MESH08 уменьшает loading; часть legacy errors оставляет loading и/или теряет raw.
No-parent branch:ANI→93ACD0,MSH/BN→93C770→93C2F0; sticky loading failures тоже есть.
Эти пути нельзя заменять successful stubs или считать уже реализованными.

Собственные rejects длинных/percent names, bounds/shortloose/nullalloc cleanup
отличаются отunchecked AV/OOM/exception/logger. Точный RFS retry/reindex failures,
полный unwind/privateSTL/heapABI/unsafe stale-cache dereferences не сертифицированы.

Следующее: reader93C2F0/importer93C770,720byte import records/28byte header;
plain424byte physique илиcompact40+100byte names; converter93CD60 для реального BN.
Потом dispatcher/FrameMove923A40/transforms/animation/skinning/declarations/shaders
и normal consumers. Legacy parent/count/mesh268/528/532 против455272/532/536 —
rawcast недопустим.

Cached: manager-plus-4.json — полный181line93C2F0; manager-layout-3.json+
frame-move-tail.json — FrameMove923A40; dispatcher/93C770 втом же artifacts/
character-manager455. Начало converter93CD60 — artifacts/character-gpu455/
next-2.json, первые250из578lines. Последующее исследование добавило остальные328
вartifacts/character-legacy455/converter-tail.json;теперьbodyсохранёнцеликом.
Полные607line922A00/146line93CB00 ранее сохранены
вcharacter-mesh-source. Не повторять закрытый reverse/858file census без новых входов.

Воспроизведение, Python через scripts/Invoke-Python.ps1:
test_character_ctor_oracle.py; audit_client455_character_manager.py;
build_client455_character_manager.py; probe_client455_character_manager.py [--gpu];
prepare_client_build.py; probe_client_character_build.ps1 [-HelperLab];
verify_client455_character_manager.py [--lab]; probe_client455_character_manager_client.py;
checkpoint_client455_character_manager.py. HAL/MSBuild escalation разрешена,
каждый run в fresh work/m9 без игровых DLL около собственногоEXE.
