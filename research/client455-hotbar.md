# Client455 Linker delta-save — 086

2026-11-07. **PARTIAL M6**. Ordinary `CLinkBoard::FrameMove` now reaches a
source implementation of the target's periodic hotbar delta upload. Full
Linker ownership, view/input, cooldowns, restore/download and gameplay are open.
This is not a completed hotbar, Tutorial or client455 acceptance.

## Pinned evidence

Static analysis only; neither input EXE was executed. Both are x86 with image
base `0x400000`:

- behavior pin SHA-256 `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
- backup pin SHA-256 `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.

The checkpoint verifies equal bytes for 45 selected function ranges between
these pins. It checks complete selected pseudocode and 640 distinct assembly
instructions across nine functions. Raw MCP output is ignored evidence under
`artifacts/client455-progress/hotbar086-{reference,asm,session}.json`;
per-function RVA, size and SHA-256 are in
`inventory/client455-hotbar-checkpoint.json`. IDA owned session `811039d6` was
saved and closed; the subsequent session list was empty.

| VA | RVA | Confirmed role |
|---|---|---|
| 5003C0 | 1003C0 | Reference key from wrapper/underlying item |
| 58BB90 | 18BB90 | Compare cached keys and send delta |
| 5004E0 | 1004E0 | Pack active bank and five raw bank flags |
| 58BE20 | 18BE20 | Payload size `2 + 4*count`, count guard50 |
| 58A6C0 | 18A6C0 | Item message group13 |
| 57EAC0 | 17EAC0 | Client0/group/op transport wrapper |
| 501750 | 101750 | Full FrameMove, including periodic upload branch |
| 669410 | 269410 | Raw bank-flag setter, also has unported view effects |
| 669190 | 269190 | Active bank setter, also has unported view effects |

## Confirmed contract and implementation

The key encoder recognizes physical, SF, Animus, Gesture and Macro categories.
Tags are respectively4, SF subtype,3,5,6. Unknown/null references encode
`FFFFFFFF`. Target `5003C0` tests the underlying item's physical predicate:
physical items use their serial, the other selected types use their table
index. It ORs the tag with the full index without masking. The source bridge
binds actual `CBoardItem`, `CSFItem` and `CAnimusItem` metadata. Gesture/Macro
owners are absent and remain required; only their pure encoding is implemented.

The delta scans five banks of ten entries, comparing full cached DWORD keys.
A change is suppressed while a hover reference originates from Linker6 and
matches the **old** cached key. Each emitted record is flat slot BYTE,
high/tag BYTE, low index WORD in little endian. Although the cache is32 bits,
the wire index truncates to16 bits. The payload has two header bytes
`[packedWindowState, recordCount]`, and at most202 bytes.

The window byte ORs active bank with each raw DWORD flag shifted by7-bank and
then truncates to BYTE. Flags are not normalized to booleans. Constructor
metadata has active255/flags0; successful legacy view Init now initializes
active0/all flags1, producingF8. This metadata does not implement target bank
widgets, their actions, layout or side effects.

Unchanged keys/state send nothing. Both key and window caches commit **before**
transport, including failed sends. Reset resnapshots keys and resets upload
time, retaining the cached window byte. The periodic branch uses unsigned
`timeGetTime()-last > 5000`, then updates last regardless of send result.
The real ordinary FrameMove contains this branch; target cooldown and
deferred-icon passes remain unported.

Transport uses actual `CNetworkMgr::SendNetMessage`, client0/group13/op17.
Legacy `item_msg` is7; changing that global would relabel unrelated unported
packets, so the confirmed message uses an explicit group13/op17 pair.
`client455_hotbar.{h,cpp}` and the bridge are incorporated by
`prepare_client455_normal.py` into the ordinary source and linked PE.

## Verification

`probe_client455_hotbar.py` builds an own console entry against the current
normal client objects/libraries. No socket listener, network worker,
authentication or game loop is started by this hotbar fixture. It uses the
actual embedded network owner, actual send ring/AES and actual source board
objects. Controlled SF/Animus records are attached by the test; full database
loading is not claimed.

Seven decoded outgoing frames match independently specified bytes:

- initialized stateF8, no item records;
- physical/SF/Animus references at flat slots0/39/49;
- changed bank-stateAA only;
- deletion after drag release, with no packet during drag;
- post-failure changed serial, proving cache commit despite transport failure;
- all50 records,202-byte payload;
- a change sent by actual ordinary FrameMove, with an immediate second call
  sending nothing.

Additional checks cover initial/no-change suppression, snapshot reset,
strict5000/5001 and unsigned wrap, raw negative/nonboolean flag packing, and
pure Gesture/Macro/unknown selectors. Real borrowed source insertion is used
for these checks; that does not prove target clone/refcount ownership.

Affected regression: source storage factory passed three runs (17 registered
classes, Force3/Animus4, public limit56, all256 BYTE lookup codes); actual
account/Avatar stage/login transform passed. New exact PE passed CRT/WinMain,
local TCP acceptance fixture, sound startup, real D3D and existing Create=1.
The debugger stopped it before the game loop. Recorded first-chance exceptions
do not establish failure-domain equivalence.

Current PE: SHA-256
`82625b3ef5c237900146f65531a701a3451d3dbec292a65eef2ed5ece83df6f8`,
2091008 bytes/x86, entry RVA14FD60, WinMainB57D0, afterCreateB593A.
Build:182 client/20 kernel/42 facade translation units; zero unresolved symbols.
Engine `9caa283a6bf8a2fa1c9a05251b6cad451296bb03bda8a1860c22a872e88fe769`
is unchanged082, so existing engine contracts are reused. Actor/money/map/audio
GPU and159k suites were not rerun without a changed dependency.

Reproduction after a current normal build/link:

```powershell
.\scripts\Invoke-Python.ps1 scripts/probe_client455_hotbar.py
.\scripts\Invoke-Python.ps1 scripts/checkpoint_client455_hotbar.py
```

The checkpoint also requires the fresh storage/account/early-startup/UI-startup
reports. Historical085/083 gates refer to their historical links and were not
rewritten to claim new runtime coverage.

## Required continuation

Target Add500590 clones a620-byte wrapper and retains an underlying item;
target Remove5007E0 removes owned clones/icon registrations/cooldown records.
Legacy source uses borrowed `CBoardObject*` and an eight-slot
`CGUIForceBeltWindow`. Its pack destructor policy and SF/Animus classes differ.
Blindly copying/deleting these objects would neither implement455 ownership
nor preserve origin lifetimes. Restore the actual common item/wrapper ownership
and five-bank `CGUILinkWindow` together, then its use/input/cooldown/restore
paths and oldbelt consumers. This is the next087 unit, not waived scope.

Old `MainGame::Create_Board` and old BeltList download still explicitly refuse
the retired belt getter. Trunk5 plus35 other target registry classes, complete
item/DB/trade/return protocols, shared UI/Avatar, real QBI/follow/local handlers,
actual Tutorial/fourstage/Login/auth/gameplay and prior acceptance gaps remain
mandatory. M6/M6F/M7/M9 stay OPEN. Servers and originals were not modified.
