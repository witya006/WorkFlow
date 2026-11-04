# Character455: RFS, DDS и физический texture backend

2026-11-05. Только клиент. M6 продвинут, M6F/M7/M9 открыты.
Это исходный backend для уже восстановленного material-request kernel;
normal model-loader и полный Character renderer ещё не подключены.

## Эталон и доказательства

Два RF_Online.bin x86/base400000 закреплены SHA256:
current b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b,
backup46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
24 диапазона функций совпали побайтно. Точные размеры/RVA/SHA в
inventory/client455-texture-reference.json. Основные VA/RVA:
manager ctor5DFC40/1DFC40,Init933580/533580,lookup934120/534120,
Add934A20/534A20,file provider933DE0/533DE0,DDS933800/533800,
mip9336C0/5336C0,repair933740/533740,XOR9337B0/5337B0,
normalize935090/535090,RFSindex9379E0/5379E0,open9382B0/5382B0.
DeleteID9345C0/5345C0 разобран инструкциями в диапазоне[9345C0,934627);
decompile этой функции не удался. Одна IDA session6117161d истекла;
последующая a2f02f23 для bounds закрыта/save. RawJSON в artifacts/character-texture455.
Входные EXE не исполнялись.

Реальные texture imports ведут в d3dx9_36.dll, включая Memory2D/MemoryCube/FileA.
SysWOW64 DLL равна клиентской: x86, SHA
c12f0ab0338eb5031d3d04beaf7208ac848f7e037d21ff963d2af90221cbe935,
версия9.19.949.2111, ранее проверенная Microsoft AuthenticodeValid.
Export-entry RVA и import/IAT RVA записаны в reference report.
Character128byte XOR key RVA7F83F0 равен engine7F7F00, SHA
ab9397fdafc4f574dc5ae5ced0a8676232e13a118d41dd2837542316ab6246e4.

## Восстановленное поведение

Manager имеет известные поля в288bytes, Entry272bytes. Device и texture getters
borrowed, без AddRef. Init сбрасывает scalar state, не очищая vector. Clear
освобождает entries/COM, сохраняет capacity,nextID,estimatedBytes; глобальные
счётчики cumulative. Destructor не обнуляет last-manager pointer.
Source opaque+4 и полный private STL/allocator ABI не сертифицированы.

Lookup uppercases ASCII, требует точку и сканирует vector по порядку: первый
exact либо basename.RFT. Add проверяет исходное полное имя до выделения basename,
поэтому path-query может создать второй одинаковый basename. DeleteByName
использует только exact, без alias; DeleteByID удаляет все совпадения.
Рост capacity1,2,3,4,6,9,13,19,28,42,63 проверен на50real COM textures.

Load order: custom original; custom RFC(oneMip); custom RFT; D3DXFileA original;
custom RFT повторно; FileA RFC; FileA RFT. Flags8 берётся только из первого custom
вызова. RFC задаёт Levels1 и colorKeyFFFFFFFF; обычный DDS — Levels0/colorKey0.
Успех добавляет4*width*height в cumulative accounting; удаление не вычитает.

Character RFS отличается от R3Engine RPK: DWORDcount и64byte records
(56rawName,DWORD absoluteOffset,DWORD declaredSize). Первое duplicate имя побеждает.
Directory cache заполняется до открытия, включая отрицательный результат.
RFSINFO.DAT — whitespace list; даже пустой файл подавляет fallback. Без него
DATA0..1023, остановка на первом отсутствующем. Info-mode guard дважды считает
directory length. Normalize заменяет slash, uppercase и при relative path
отбрасывает первый компонент; '.\\tex\\X' и 'tex\\X' имеют разный результат.
Open возвращает обычный FILE*, без ограничения чтения extent; fseek failure
игнорируется. Собственный Clear cache явно управляется владельцем, не выдуман
как автоматическая часть device reset.

DDS header128 читается plain или XOR один раз. Mip skip использует raw
pitch/linear-size и сохраняет quirks break при width/height<=4; bytes могут
прибавиться без уменьшения mip count. maxWidth/Height<256 отключает skip.
Pixel-format repairs перенесены по инструкциям. FILE закрывается после GPU call;
missing/zero-length не меняют caller cubeFlag.

Подтверждён cube ownership defect: MemoryCube пишет в отдельную local, а функция
возвращает оставшуюся нулевой2D local. Настоящий cube создаётся и теряется.
Source сохраняет это поведение. Только test wrapper захватывает реальный COM
cube и освобождает после проверки; production не подменяет его2D результатом.

## Проверки

Два copied GuardTower RFS:13masked RFT;3loose realDDS;3MESH08models/97parts.
Синтетические BMP/RFC/cube/badDDS, growth50entries, duplicate/empty/negative cache
fixtures. Пины всех inputs в inventory/character-texture-inputs.json.
Это выбранный небольшой корпус, не полный texture/RFS census или доказательство
игрового выбора mesh/skeleton/texture directories.

9Python tests: RFS roundtrip/duplicates/padding/index truncations/name/extent,
DDSshort headers/XOR/format repairs/cube/mip break/overskip. Независимый Python
golden содержит80DDS profiles. NativeCPU333checks. На HALD3D9 source texture
сравнивается с прямым actualD3DX9 вызовом на Python-prepared golden:68successful
pairs, все mip descriptions и byte contents;137render passes, RGB равны.
RFCfallback/1mip/colorKey, missing/empty flag preservation, first-match alias,
path duplicates, growth/Clear/Init/delete/cumulative accounting и cube orphan
проверены на реальных COM. Checker frame имеет четыре точных RGB quadrants;
визуально просмотрен, SHA e5b32219dc16c2243096b12a7de3aaf3dda8039b76e2c5d50059bb860c3cc69c.

Те же8440checks выполнены через собственную точку входа полного RF_Online.bin:
97material parts,59positive texture-ID bindings, Dmalloc balance0,
Device/D3D9 Release0, game DLLs не загружены. D3D9 test TU отделён от старых
D3D8 headers. Это восстановленный source backend без успешных заглушек.
RF_CLIENT_455_TEXTURE defaultOFF, build driver явно ON; lab12C APIs из
RFClient455Texture:texture.obj. В normal unused APIs stripped; обычный loader
по-прежнему legacy. Полный Character GPU не принимается этим тестом.

Lab SHA ed8315fab2308743db54df96940a5fcf4103b5f8d681e3c29d324d0dc323d79b,
entryRVA85B7; snapshot work/t9/ed8315fa/client001/RF_Online.bin.
Normal2451456bytes/entry1BC4B0, snapshot artifacts/client-first-build/character455-textures,
SHA в inventory/client-first-build.json; не запускался.289normal modern COFF/MT.
Все прежние scoped regressions прошли на lab: legacy245+6732,mesh086304,
packed4552237,meshCPU14562,clock1443,maptime314,weather703,resource30,
commands432/2628+20actual input. Platform01/device2GPUcases/69checks,
0warnings/errors,COM/Dmalloc0, прежние frame SHA сохранены.

## Воспроизведение и ограничения

Python через scripts/Invoke-Python.ps1:
audit_client455_texture.py; test_character_texture.py;
audit_character_texture_inputs.py (только при изменении input/golden);
build_client455_texture.py; probe_client455_texture.py [--gpu];
prepare_client_build.py; probe_client_character_build.ps1 [-HelperLab];
verify_client455_texture.py [--lab]; probe_client455_texture_client.py.
Native HAL и MSBuild требуют привычной escalation. Probe каждый раз копирует
fixtures в новый короткий owned cwd work/t9; originals/fixture master неизменны.

Не закрыты malformed/unchecked reads/OOM/nonASCII CRT locale/unsafe percent-format
domains, logger/allocator/private ABI/global cache teardown/reset lifecycle,
полный model/skeleton loader, shared buffers/index rebase/publication/destructor,
skinning/animation/draw и все игровые сценарии. У нового backend есть owned bounds
errors вместо AV, percent strings явно запрещены; это не failure parity.
Static instruction evidence + независимые goldens + real provider подтверждают
выбранный участок, не полное сравнение двух запущенных RF клиентов.
Следующий source unit: shared vertex/index allocators93E000/93E180 и их D3D9
контракт, затем нормальная сборка/публикация модели и owning release/unwind.
