# Character455: source shared GPU buffers

2026-11-05. Source модуль и physical buffer tests выполнены в выбранном domain.
Normal model-loader иполный Character renderer ещё не подключены. M6/M6F/M7/M9 открыты.
inventory/client455-shared-buffers-reference.json хранит SHA256 обоих pinned x86
RF_Online.bin,18полных bodies иcaller fragment сRVA/SHA. Все диапазоны
  побайтно равны между pins. IDA10003798 иb58f27c1 закрыты/save;raw artifacts/character-gpu455.

- VA93DE00/93DE80/93DF20: find/upload/bind36byte vertices.
- VA93DF80/93E000/93E0A0: find/upload/bind64byte vertices.
- VA93E100/93E180/93E220: find/upload/bindINDEX16.
- Общие поля manager:1024COM pointers+0,usedDWORDs+4096,opaqueDWORD+8192,
  borrowed device+8196.8200byte pool подтверждён constructor memset;неполный renderer ABI.
- First-fit1024slots, uint32(used+size)<=capacity. Capacity2300000 дляVB,
  1000000 дляIB. Failure sentinel1025. Lazy managed buffer creation, usage8;
  VB FVF278/282, IB format101. FVF282 не доказывает полный64byte declaration.
- Lock(used,size,out,0); memcpy; Unlock без проверки HRESULT. Затем output=
  capacity*slot+used, used+=size. Lock failure сохраняет output/used, но уже
  созданный COMbuffer и increment global counters остаются.
- Bind делит absoluteOffset наcapacity, выбирает slot, передаёт stream0,
  bufferOffset0,stride36/64 либо SetIndices. Remainder компенсируется caller.
- MESH08 caller923590..92360A пропускает ОБА uploads при indexCount0.
  Иначе vertex64*count, затем WORD index +=((vertexAbsolute%2300000)>>6),
  затем index2*count. Возвраты upload игнорируются. Поля mesh4494/4502
  начинаютсяFFFFFFFF по уже восстановленному constructor; failure propagation
  и partial publication требуют аккуратного переноса полного caller.

Найдены ctor5DFCB0/5DFD40/5DFDD0,size29h:memset всех8200bytes0.
Dtor5DFCE0/5DFD70/5DFE00,size56h:Release nonnullslots0..1023, без обнуления
любых полей ибез вычитания accounting. Source не делает destructor повторяемым.
Owner ctor5DFB70/CDbytes вызывает pools+8928(vertex64),+17128(vertex36),
+25328(indices). SetDevice920590/D6bytes пишет borrowed device вeach pool;
не AddRef. Owner dtor9228A0/157bytes освобождаетIB→VB36→VB64,каждый по порядку
slots;другие shaders/textures/subobjects также имеются иполностью не перенесены.
18full bodies +callerfragment совпали по обоим pins. Binary SHA256:
current b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b,
backup46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
Архитектураx86/base400000,все RVA/SHA в reference report.

Source client455_shared_buffers.cpp/.h содержит ctor/dtor, upload36/64/INDEX16,
bind operations,rebase ивыбранный MESH08GPU caller fragment. Прямые D3D9 COM calls,
без fake/default-success backend. Accounting storage явно передаётся owner и
должно разделяться тремя pools как reference global DWORDs. Это собственные
API adapters;не утверждение о полном C++ ABI/всём renderer constructor/destructor.

158336CPU checks и159173с HAL прошли standalone/full-client,12real files/393parts.
Test-only COM capture проверяет bytes/protocol,first-fit,equal capacity,slot1023,
all1024full,wraparound before unsigned compare,zero-size,Create/Lock failures,
ignored UnlockHRESULT,borroweddevice,non-reset dtor иcumulative counter DWORD wrap.
Mesh08сfailedVB всёравноrebasesотFFFFFFFF ипишетIB;failedIB неоткатываетVB.
117parts имеют indexCount0:обаuploads пропускаются,offsetsFFFFFFFF сохраняются.
Остальные276parts прошли реальные managedVB/IBuploads наHALD3D9;все393parts
учтены какgpu cases. All real index values иvertex bytes проверены capture;
этот byte comparison неявляетсяGPUreadback WRITEONLY buffers.

Четыре synthetic indexed draws:stride36/64,nonzero initial offsets иforced
VB/IBblock1 rollover. До/после кадры RGB совпали;actual GetDesc/GetStreamSource/
GetIndices проверены.64byte путь использует source MESH08 upload/rebase adapter.
Лабораторный POSITIONT/COLOR declaration проверяет передачу данных,не455shaders.
Кадры64x64 просмотрены:cyan/red triangles на фоне132739. SHA:
36=f2eb8fd2335336ae5038018eb3dc6431bbbcec94f7af17eb8120bc2c7657e2cd,
64=b543cfdc7bf9006a0cc45e42fa95e4375f501b556052ac1a6a988bffd690ffed.
Device/D3D9 Release0. Fullclient own entry даёттеже159173checks/framehashes,
Dmalloc balance0,game DLLs отсутствуют. Normal WinMain/input EXE неисполнялись.
RF_CLIENT_455_SHARED_BUFFERS defaultOFF,driver явноON;12ownlab APIs изsource
RFClient455SharedBuffers:shared-buffers.obj. Normal unused APIs stripped.

Ранее полученные scope regressions прошли наактуальномlab:legacy245+6732,
mesh086304,packed4552237,meshCPU14562,clock1443,maptime314,weather703,
resource30,commands432/2628+20actual input,texture8440. Platform01/device
2GPUcases/69checks,0warnings/errors,COM/Dmalloc0;framehashes сохранены.
289normal modern COFF/MT. Snapshot normal character455-shared-buffers,
manifest inventory/client-first-build.json;lab/currentPE hashes/entryRVA в
inventory/client455-shared-buffers-link.json иclient.json.

Команды Python через Invoke-Python.ps1:audit_client455_shared_buffers.py;
build_client455_shared_buffers.py;probe_client455_shared_buffers.py [--gpu];
normal/lab probe_client_character_build.ps1;verify_client455_shared_buffers.py
[--lab];probe_client455_shared_buffers_client.py. MSBuild/HAL требуют стандартную
escalation;никаких новых внешних инструментов/библиотек неустанавливалось.

Открыты renderer reset/device-loss, opaque8192, actual64byte shader declaration,
full OOM/unchecked invalid-state/exception behavior,skin/animation/draw иnormal
model publication. Unsafe overflow checked via test-only captures,не утверждать
проверку всех таких сценариев нареальном драйвере. Следующий unit — owning model
array publication/destructor/failure unwind,затем normal client loader dispatch;
полный skeleton/BN иanimation также необходимы. Новые родные shaders/graphics
style не вводились;восстановление D3D9 входит вM6.
Не повторять декомпиляцию этих девяти functions иполного922A00 без новой причины.
607line922A00 cache:artifacts/character-mesh-source/mesh08-0x922a00.json/.txt.
93DDF0 — чужой14byte accounting helper, не constructor.93DDE0 лежит внутри
большого93CD60, не lifecycle shared manager. Эти ошибочные кандидаты не использовать.

Во время проверки воспроизводимости stdio MCP worker вышел code2 в restricted
контексте. Та же configured command с обычной escalation успешно дала66tools,
client function page10/decompile иclose/save2fa6d05a. Переустановка не потребовалась.
Probe теперь использует отдельную копию455client IDB, без прежнего server smoke
input ибез повторного auto-analysis. Нативные MCP decompile/xrefs/insn calls
также прошли. inventory/ida-mcp-verification.json иdocs/ida-mcp.md обновлены.
