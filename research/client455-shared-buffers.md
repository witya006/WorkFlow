# Character455: следующий shared GPU source unit

2026-11-05. Пока static research, реализация и physical buffer tests не выполнены.
inventory/client455-shared-buffers-reference.json хранит SHA256 обоих pinned x86
RF_Online.bin, девяти полных bodies и caller fragment с RVA/SHA. Все диапазоны
побайтно равны между pins. IDA10003798 закрыта/save;raw artifacts/character-gpu455.

- VA93DE00/93DE80/93DF20: find/upload/bind36byte vertices.
- VA93DF80/93E000/93E0A0: find/upload/bind64byte vertices.
- VA93E100/93E180/93E220: find/upload/bindINDEX16.
- Общие поля manager:1024COM pointers+0,usedDWORDs+4096,opaqueDWORD+8192,
  borrowed device+8196. Известен минимум8200bytes, не полный owning class ABI.
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

Открыты owner constructor/clear/destructor/reset, opaque8192, actual64byte shader
declaration, wraparound/zero-size/invalid-state/OOM, draw и full publication.
Следующий шаг: выяснить owning lifecycle и восстановить allocator/bind methods;
проверить first-fit/rollover/equal-capacity/1024exhaustion иcreate/Lock/Unlock
failure protocol на test-only capture, затем actual HALD3D9 buffers/draw.
После этого source loader publication/release иnormal client dispatch.
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
