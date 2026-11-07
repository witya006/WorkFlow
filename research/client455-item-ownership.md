# Client455 item ownership foundation — 087

2026-11-07. **PARTIAL_SOURCE_FOUNDATION**, within M6. Selected copy/clone and
reference-release source now builds as `RF455ItemOwnership.lib`. It passes
standalone and full-client-object probes with a **recording manager host**.
It is not yet bound to ordinary Linker, item factories or the real item
destructors. Production RF_Online.bin and its086 acceptance remain unchanged.

## Confirmed reference and source gap

Both pinned references are x86/base400000:

- behavior SHA-256 `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
- backup SHA-256 `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.

Twenty-four selected function ranges have equal bytes between pins. Complete
assembly for14 functions contains579 distinct instructions. The audit decodes
eight literal x86 constructor stores from the pinned bytes into an independent
whole-record oracle; no input code or input EXE is executed. Per-function
RVA/size/SHA-256 is in `inventory/client455-item-ownership-reference.json`.

| VA | RVA | Confirmed role |
|---|---|---|
| 45FC80 | 5FC80 | CItem base header initialization |
| 405E70 | 5E70 | CItem header copy constructor |
| 465FD0 | 65FD0 | Increment BYTE reference field20 |
| 4661C0 | 661C0 | Decrement BYTE reference field20 |
| 4661F0 | 661F0 | Read reference BYTE |
| 46B090 | 6B090 | Release underlying item from CItemObject |
| 46B140 / 46EBE0 | 6B140 / 6EBE0 | Primary-manager list-empty guard |
| 469960 / 46A040 | 69960 / 6A040 | Primary/Gesture manager removal boundaries |
| 46B570 | 6B570 | Allocate620-byte clone, retain underlying item |
| 46B5E0 | 6B5E0 | CBoardObject copy constructor |
| 405D30 / 405100 / 405DD0 | 5D30 / 5100 / 5DD0 | CItemObject/CResObject/CObject parent copies |

The target CBoardObject is a CItemObject/CResObject wrapper; the source's
legacy CBoardObject derives directly from CObject and mixes payload state into
CBoardItem/CSFItem/CAnimusItem. Copying a legacy derived object does not create
the target's independently owned wrapper over a shared CItem. The target
parent copies also shallow-copy opaque resource fields. Their complete
resource clear/destruction must be restored before treating raw wrappers as
ordinary gameplay objects.

## Selected source contract

`scripts/native/client455_item_ownership.{h,cpp}` defines x86 **data records**
for the92-byte CItem header and620-byte board wrapper, with static checks for
pointer584/icon596/flag616. These are not callable C++ vtables. The dispatch
word is an opaque owner-supplied token, and the fixtures replace the original
vtable word with a controlled token. Other unnamed fields remain unnamed;
their copy behavior is confirmed without inventing gameplay meanings.

Initialization writes fields4/8 toFFFFFFFF, kind12/data16/ref20/flag21/field88
to zero, and the dispatch word. It does **not** zero bytes22..85 or padding.
Copy writes the selected members and64 bytes22..85, retaining destination
padding13..15/86..87. Wrapper copying retains destination padding5..7,
593..595 and617..619, while copying the known constructor-written ranges.
Clone allocates620 bytes, copies the wrapper, then increments the same
underlying item's BYTE counter. A null allocation does not increment it.
Clones have separate wrapper state and share mutable underlying payload.

Release is not ordinary shared_ptr semantics:

1. Query the **primary** manager at VA C0C020 (RVA80C020). Its list begins+4;
   the tested empty field is+12, VA C0C02C.
2. If that cache is empty, return without decrementing or clearing the wrapper
   pointer. This guard applies even to a Gesture item in its separate manager.
3. For a nonnull item, decrement its BYTE counter with wraparound.
4. Target46B090 explicitly uses MOVSX on AL. A zero or negative **signed**
   result invokes the item's virtual kind6 predicate and the selected manager
   removal: Gesture manager C0BFF4/RVA80BFF4, otherwise primary C0C020.
5. Clear the wrapper pointer even when the manager lookup does not find the
   item. A positive remaining count skips the predicate/removal, then still
   clears the pointer.

Thus decrement0 yields255 and selects removal; decrement128 yields127 and
retains the item. Removing this quirk or normalizing the counter would differ
from455. The source release helper requires a production host for the actual
cache-empty query, virtual predicate and removals. No no-op production host is
installed. Its boolean result describes whether pointer clearing was reached;
it does not claim target EAX return-value equivalence.

## Verification and limits

Three whole-record comparisons cover initialized92 bytes, copied92 bytes and
copied620 bytes with nonzero destination sentinels. The constructor fixture
comes from decoded C6/C7 stores; the copy fixtures use manually reviewed full
constructor assembly. The allocator fixture verifies the620-byte request,
allocation failure and independent wrapper/shared item behavior.

Twelve lifetime scenarios include origin/link release, final owner, primary
empty guard with a live Gesture cache, separate Gesture removal, all seven
chosen reference boundaries0/1/2/127/128/129/255, null underlying pointer,
manager miss and allocation failure. Actual derived item destructors and
factory/database loading are not exercised. The recording host owns its
header fixtures and records callback order/counter state.

The same exact separately compiled library links into a standalone own EXE
and an own entry linked with the full current client object/library set.
Both exit0 with identical reports. The initial combined test translation unit
allowed the compiler to inline away API boundaries; the checkpoint caught the
missing symbols. Only test packaging changed: the full-object entry now links
the exact library, and the checkpoint verifies its providers in both MAPs.

Raw MCP/session/oracle files are ignored under `artifacts/client455-progress/`
and `work/client-reference/item-ownership455/`. Session65f54fa4 was saved and
closed; subsequent IDA list0. No server files or originals were changed.

```powershell
.\scripts\Invoke-Python.ps1 scripts/audit_client455_item_ownership.py
.\scripts\Invoke-Python.ps1 scripts/probe_client455_item_ownership.py
.\scripts\Invoke-Python.ps1 scripts/checkpoint_client455_item_ownership.py
```

Production stays SHA-256
`82625b3ef5c237900146f65531a701a3451d3dbec292a65eef2ed5ece83df6f8`,
with current086 gate `inventory/client455-hotbar-checkpoint.json`. It was not
relinked. Unchanged GPU/startup/159k suites were not rerun or declared fresh087.

## Next integration — 088

Restore the concrete derived payload factories/managers and their real
virtual predicates, CItemObject/CResObject lifecycle and typed wrapper/board/
hover consumers. Bind these kernels to actual ordinary owners, then finish
Linker clone/removal/use/input/cooldowns/download and5x10 CGUILinkWindow.
The087 data records are not permission to reinterpret legacy classes as620-byte
wrappers. Oldbelt callers,36 missing registry classes, full item/DB/trade
protocols, actual Tutorial/fourstage/Login/auth/gameplay and all previous gaps
remain mandatory. M6/M6F/M7/M9 remain OPEN.
