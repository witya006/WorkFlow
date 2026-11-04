# Character: полный source InitVertex и найденный MESH08 path

2026-11-05, M6. Восемь legacy функций теперь имеют собственный C++ source:
прежние4parent/blend bindings плюс InitVertex, ConvertVtToD3D, ConvertUV и
DecodeTwoBlendPhysiqueData. Source нужен для удаления бинарных Character consumers
перед переносом455mesh/renderer. Legacy1072byte mesh/36byte vertex не равен455.

## Реализация и проверка

scripts/native/character_mesh_init.cpp восстанавливает полный old load body:
texture path/ID resolution, matrices/bounds/flags/names, exported vertices,
physique weights, triangle expansion/UV, MakeVB failure flag, local/external
parents/blends, publication иBONE classification. Пятый bool, как в SDK body,
не потребляется. Непроверенные unsafe/OOM/exception/locale domains не исправлялись.
Private renderer data alias указывает на прежний ?m_Render@CRender@@0PAV1@A;
новый singleton или assignment не добавлен. private format header задаёт только
подтверждённые36/28/8byte vertex/export/UV records,не полный ObjectData/455layout.

COFF adapter оставляет восемь исходных bodies как независимую comparison group;
внутренние calls этой группы остаются SDK. Остальные callers выбирают source.
Все instruction bytes сохранены. Четыре COFF tests проверяют10объектов,границы,
повреждённые tables инезависимость retained InitVertex. Normal/lab map идва actual
LoadRealData E8 calls(+0x77/+0x11E) подтверждают переход на собственный InitVertex.
Восемь восстановленных публичных symbols происходят из bindings.obj/init.obj source library.

6732сравнения/144cases/12FP modes проходят standalone ив полном клиенте:
0/1/2meshes,0/1/2faces, skinned/unskinned, local/external parents,relative matrices,
UV/weights/bounds/flags/BONE,create/lock errors иrelease. Actual supplied SDK MakeVB
исполняется с test-only COM buffers; captured bytes совпадают с independent SDK
InitVertex. Это CPU comparison,не физическая GPU verification персонажа.
245прежних binding checks также проходят. Dmalloc/capture-buffer balance0;
игровые DLL/сеть/normal WinMain/input EXE не выполнялись.
No-op providers в production не добавлялись; COM doubles существуют только в tests.

## Подтверждённые отличия455

Эталон x86/base0x400000: current SHA
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b,
backup46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
Legacy CharacterMR SHA483715b927690fc69607682a093dff53635911870456f5849c9f52741702b8a8;
COFF runtime RVA неприменим. audit_character_init455.py закрепляет7reference bodies,
normal/UV/magic instructions,2LoadRealData calls и3реальных model samples.

|455функция|VA/RVA|Подтверждено|
|---|---|---|
|Convert vertex|93B020/53B020|x87 load/store;нормали инвертированы и находятся+32/+36/+40|
|Convert UV|93B5F0/53B5F0|u/v находятся+44/+48;v=1-v|
|Decode physique|93AA10/53AA10|64byte stride,3weights иWORD indices вместо legacy single weight|
|Make indexed vertices|93B310/53B310|64byte memcmp/first occurrence,64000limit,shared GPU managers|
|Convert64→36|93B130/53B130|отдельный software branch,полная семантика ещё открыта|
|MESH08 detector|91F250/51F250|сравнивает ровно первые6bytes MESH08;NULL branch особый|
|MESH08 loader|922A00/522A00|отдельный607line body,5803byte mesh идругой data path|

Actual LoadRealData9238F0/RVA5238F0 вызывает detector;923902/RVA523902 вызывает
loader922A00. Нельзя подавать MESH08 в старый unchecked MakeMeshData693 reader.
Sample Shield065 действительно начинается MESH08;legacy693 framing кнему неприменим.
Plain Shield031 иCloak002 проходят bounded693/28/88/compact-skin framing доEOF.
Это framing,не полная спецификация геометрии/материалов/физики.
Copies/hashes вwork/client-reference/character-models иinventory/character-init-reference.json.
Нет вывода оверсии всех ресурсов или полноте их инвентаризации по одному имени.

## Сборки

Normal2451456bytes,entryRVA0x1BC4B0,SHA
a070e9fb4350290fc8877940ae6cfbce417b0cc12b5a12b8a6a82ba5e121d573,
snapshot artifacts/client-first-build/character-init-source;не исполнялся.
Lab4167680bytes,entryRVA0x7EC8,SHA
ce6a1bb826d11f219218d4361f923ba1b11de9b31fe998b65b98696b68104cce.
289modern client/engine/JPEG objects /MT;bindings.obj/init.obj такжеx86/MT.
1443clock/314map-time/703weather/30resource,432command cases/2628checks+20actual input
regressions прошли. Platform01/device2GPUcases/69checks,0warnings/errors,
Dmalloc/COMbalance0,FPU007F. FrameSHA совпадает с предыдущим просмотренным frame.
Это map/weather regression,не Character GPU parity. Historical M5 checkpoint сохранён.
Reports:character-mesh-source{,-link,-runtime}.json,character-init-source-runtime.json,
character-init-source-graphics-runtime.json;raw artifacts/character-mesh-source.
Owned IDAab009b3b/012583e5closed/save.

Следующий critical path: восстановить MESH08 framing/CPU data по922A00 на pinned
real samples,materials/skin/indices/vertices,потом packed455mesh иD3D9buffer/render
consumers. Plain/legacy source unit не заменяет эту цель. M6/M6F/M7/M9 открыты.
