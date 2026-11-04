# Character: исходные CPU bindings и lifecycle меша

M6, 2026-11-04. Восстановлены четыре функции старого Character SDK в читаемом C++:
FindParent по имени, привязка родителей массива, RematchParent и FindBlendParent.
Они подключены к normal/lab RF_Online.bin. Это подготовка полного исходного Character,
а не завершение персонажа455. Остальной SDK, InitVertex и renderer ещё бинарные.

## Доказательства и границы версии

Входной CharacterMR.lib SHA256
483715b927690fc69607682a093dff53635911870456f5849c9f52741702b8a8,
10x86COFF. Использованы сохранённые207definitions без повторного массового reverse.
Для COFF runtime RVA неприменим; inventory/character-mesh-source.json содержит
хеши объектов, symbols, section/relocation offsets. Исходные объекты не изменены.

Эталон455 x86/base0x400000: current SHA
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b,
backup46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
audit_character_mesh455.py закрепляет8bodies и11точных instruction sites в обоих PE.

| Участок455 | VA / RVA | Подтверждённое отличие |
|---|---|---|
| Constructor |9214E0/5214E0|5803bytes/полное memset вместо частичной инициализации1072bytes |
| Destructor |920FD0/520FD0|COM buffers+4486/+4490, heap+5095/+5099/+4506 и два subobjects |
| LoadRealData |9238A0/5238A0|loading gate+264,loaded+260;новые format paths |
| InitVertex |93CD60/53CD60|packed stride5803,64byte vertices,normal/sequence/reflection textures,MTG path |
| FindParent(name) |93BA40/53BA40|case-sensitive,first match,5803stride |
| FindParent(array) |93BAB0/53BAB0|first match;legacy сохраняет последнее и считает каждое совпадение |
| RematchParent |93BB70/53BB70|gate+5495,также first match |
| FindBlendParent |93BC40/53BC40|count+522,parent pointers+526,inline identity writes from+646 |

Реальное полное устройство455mesh пока не восстановлено. Наблюдаемые parent pointer
copies при count>30 перекрывают начало matrix region;50элементов локального массива
не доказывают безопасную capacity50в объекте. Overflow/OOM/invalid inputs открыты.
Не подставлять packed455offsets в legacy ObjectMesh/Character.h.

## Уточнение blend ownership

Старый конструктор не задаёт pointer+160, деструктор его освобождает. Однако штатный
InitVertex вызывает FindBlendParent для каждого созданного меша. Тот всегда записывает
результат operator new(count*64), включая count0, затем задаёт identity matrices и
parent pointers. CPU сценарий реального InitVertex подтвердил эту цепочку для мешей
с одной костью и без костей. Патч конструктора по одному unloaded fixture не обоснован.
Ранние exception/failure до FindBlendParent, повторное выделение и полный unwind открыты.

## Подключение исходников

scripts/native/character_mesh_bindings.cpp сохраняет legacy1072byte ABI и его quirks.
Source restoration отделена от будущего переноса455behavior. Четыре прежних bodies
в рабочем COFF переименованы для независимого сравнения. Добавлены undefined symbols,
и входящие caller relocations перенаправлены на source; calls внутри comparison group
остались прежними. Instruction bytes всех исходных функций сохранены.

coff_source_bindings.py проверяет границы таблиц; четыре tests проверяют все10реальных
объектов, неизменность инструкций, actual InitVertex relocations и повреждённые tables.
В normal/lab map четыре публичных символа происходят из CharacterMeshSource:bindings.obj.
Три actual linked InitVertex E8 calls, включая возможные E9 thunks, доходят до source.
RF_CHARACTER_MESH_SOURCE defaultOFF; диагностический driver явно ON и проверяет хеши
source/archive/header/scripts. Он не включает _DEVELOPER_ или /FORCE.

245native checks проходят standalone и через own entry полного клиента: имена/case,
negative/zero counts, duplicates/last match, rematch gate, missing/local/external bones,
0–4unique blends, identity matrices и destructor ownership. Реальный InitVertex
использует3CPU vertices/0faces, skinned/unskinned, затем реальное освобождение.
Это bounded fixtures; реальные Character assets, triangle upload и GPU ещё не проверены.
Сравнение выполняется с actual supplied SDK, не с переписанным тестовым алгоритмом.

## Сборки и регрессии

Normal x86/base0x400000,2450944bytes,entryRVA0x1BC340,SHA
9cb2329eda37ff61548f7b24fcb70b617b85a151623e867ced71439972e3a794.
Snapshot artifacts/client-first-build/character-mesh-source;normal WinMain не исполнялся.
Lab4146176bytes,entryRVA0x7EAA,SHA
d59233bc12b46799bc8cc5311acfeb6dcb09f3e900624eb3b1933d08458b1c46.
289modern client/engine/JPEG objects x86/MT;own bindings также x86/MT.
1443clock/314map-time/703weather/30resource checks,432command cases/2628checks и20actual
CHAT_INFO input checks прошли. Clock instruction/link proofs сохранены.
Platform01/device2GPUcases/69checks,0warnings/errors,Dmalloc/COMbalance0,FPU007F;
frame просмотрен. Это regression map/weather, не Character GPU verification.
Сетевых соединений/отправки нет; gameDLLs не загружены, input EXEs не запускались.
Historical M5 checkpoint сохранён отдельно и не переименован в новую проверку.

Evidence: inventory/character-mesh-source{,-link,-runtime,-graphics-runtime}.json,
character455-mesh-reference.json;raw artifacts/character-mesh-source.
Owned IDAc99d5253 закрыта/save.

Далее: полный InitVertex/vertex conversion и mesh-data source contract, реальные
Character assets, buffers/material/texture lifecycle, полные455layouts и D3D9renderer.
Source4functions не закрывает M6/M6F/M7/M9; модернизация графики M8 не требуется.
