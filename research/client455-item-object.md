# Item-object091 — ordinary typed shared owners

2026-11-07. **PARTIAL**, M6. Actual ordinary classes now implement
CItemObject592/CBoardObject620 over the common resource base090. They use a
real item manager owned by CMainApp. This is no longer only the087 raw-record
ownership host. Full gameplay, icons, mixed legacy payload consumers and
normal automatic table loading remain OPEN, together with M6F/M7/M9.

## Static reference

Both x86 references have image base0x400000:

| Pin | SHA-256 |
|---|---|
| Current | b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b |
| Backup | 46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558 |

21 function ranges agree;14 complete assembly bodies contain444 actual
instructions. External EH instruction windows are pinned separately.
Raw exports/session cleanup are in ignored
`artifacts/client455-progress/item-object091-*`. IDA157b5ed2 was saved/closed,
followed by session list0. No input EXE was executed.

| RVA | Selected contract |
|---|---|
| 0x6af20 / 0x6af70 | Item resource constructor / destructor |
| 0x6afe0 / 0x6b090 | Clear index / guarded payload release |
| 0x6b010 | Virtual Clear,assign payload,retain,copy name |
| 0x6b1b0 / 0x6b250 | Board wrapper constructor / destructor |
| 0x6b4c0 | Clear item then detach icon |
| 0x6b570 / 0x6b5e0 / 0x5d30 | Clone / board and item copies |
| 0x6bc90 / 0x6b450 | Derived payload setter / index propagation |
| 0x6b2f0 | Nonnull shared-payload identity comparison |
| 0x6b7e0 / 0xb140 | Icon refresh boundaries,not restored by this unit |

## Ordinary implementation

`client455_item_object_port.py` changes owned copies of item headers/source
and MainApp through the existing preparation pipeline. It preserves legacy
encoding/unrelated text. Four new production facade units compile ownership,
SF, basic payloads and the ordinary item objects. The private helper names
`array`/`byte` were renamed to avoid Windows/STD collisions; their algorithms
and real-data oracles are unchanged. The new ordinary TU uses the existing
legacy header definitions and for-scope settings. Initial compilation exposed
those settings and a missing SpriteMgr include; both were fixed in the port.

`RF455ClientItems` owns real Item/Quest/Character/SF tables and the primary
manager. It is declared before ordinary game-object members in CMainApp,so
their destruction precedes its manager/data destruction. `loadFiles` performs
actual EDF/localization loads; normal bootstrap has not yet been connected
to this loader. Its successful call here is a controlled own-entry scenario,
not a claim that normal WinMain loads the new item world.

CItemObject stores a source-typed shared payload pointer at584 and field588.
Constructor sets both to zero. Copy does not retain; Clone retains after
successful copy,as455 does. Clear invalidates only the object index first,
then uses087 release semantics through the actual CMainApp manager. The primary
empty guard runs before dereferencing a potentially retired payload. The
selected signed BYTE/wrap rules are preserved. Its destructor calls the
qualified item Clear before CResObject destruction.

CBoardObject now derives from CItemObject,with using BYTE592,icon596 and
17 constructor-zeroed bytes600..616. Padding is preserved in copy. The typed
payload setter copies name,serial/secondary ID into the resource wrapper;
SetIndex also propagates the serial into the shared payload. Base wrapper
equality uses nonnull payload identity. Its Clear detaches the icon after
item release,without resetting unrelated fields. New/Clone create actual
source-owned polymorphic objects. No input vtable or reinterpretation of
legacy objects is used. The managed payload API is source-owned; equal wrapper
sizes do not establish complete target private C++ ABI.

Legacy mixed classes still expose their old type discriminator through virtual
getters rather than an extra base field. Their Clone paths retain after copy,
and Clear chains through the new base. Their old embedded payload/gameplay
methods are not455 implementations. Binding a new payload to those mixed
derived classes explicitly refuses until their consumers are migrated.

The existing GUIItem lacks the target object-index/inline-caption provider.
Nonnull icons on typed wrappers therefore explicitly refuse; this domain is
not replaced by a successful no-op. Unbound legacy icon setters remain
callable,but the mixed Clear/Create callers still need target lifecycle
migration: Clear now chains through the real base and detaches its icon.
Quest names likewise explicitly refuse at
the existing missing sentence provider. These are remaining implementation
gaps,not accepted target failure behavior.

Ordinary `CLinkBoard::HotbarReference455` now reads shared payload metadata
before legacy mixed-object lookup. Its physical/SF/Animus keys preserve the
confirmed unmasked OR encoding. Full Linker clone/storage/UI/input lifecycle
is still pending; its current legacy Add path must not be called accepted455
ownership merely because this metadata helper now handles real wrappers.

## Runtime evidence

New ordinary RF_Online.bin:

- SHA-256 `7d7ff847b49d28a2d24a203d1a9b863a5ff273e10a82eda9d3d7e7c94ecb3bc0`;
- x86,2104832 bytes,entry RVA0x152070;
- WinMain RVA0xb6fe0,after-Create checkpoint RVA0xb714a;
-182 client/20 canonical kernel/46 facade objects,zero unresolved symbols;
- engine082 unchanged, SHA-256
  `9caa283a6bf8a2fa1c9a05251b6cad451296bb03bda8a1860c22a872e88fe769`.

Three own entries link the actual normal object/library set. MAPs identify
production facade providers rather than a second independently linked item
library. All naturally exit0:

1. Typed owner probe loads real files through CMainApp,creates1447 SF plus566
   other selected payloads,binds/clones actual CBoardObjects and removes them
   in alternating order through the actual CObjectPack implementation.2013
   clones share their payload; the last wrapper removes the concrete manager
   entry. The container is obtained from a real CLinkBoard pack; full Linker
   Add/UI ownership is not tested by bypassing its unfinished methods.
2. The unchanged data probe passes76049 item rows/47 tables,Quest12/Character7,
   three complete NDItem corpora,575 fresh factory cases and99 Animus XP
   boundaries on production providers.
3. The unchanged SF probe passes all1447 SF rows/wrappers and locale failure
   prefix rules on production providers.

Two complete620-byte constructor/copy oracles extend the pinned common-base
oracle,normalize only own dispatch/time and verify unwritten padding. Typed
tests also cover base-vs-derived setter behavior,null identity,retired-pointer
primary-empty guard,seven signed BYTE cases,actual metadata keys,explicit mixed
and icon refusals. Nine Quest name cases refuse with owner cleanup; they are
not counted as restored Quest sentence behavior.

Affected ordinary hotbar7 actual send-ring/AES packets,storage17-class registry
and Avatar/account paths pass. Exact new PE reaches CRT/WinMain/local TCP
fixture/sound/D3D/normal Create=1 with recorded first-chance events and no
unhandled exception. It stops before the game loop. The renderer/map/audio
algorithms are unchanged; their090 evidence is retained as historical for
that link,and unchanged GPU/audio/159k suites were not repeated.

Current ordinary gate: `inventory/client455-item-object-checkpoint.json`.
The090 runtime gate and earlier source runtime checkpoints are historical
after the new link/source-provider reports; their static references remain.

## Next092

Restore the real item icon/caption owner and typed board/hover/Linker consumers,
then connect the new data owners to the verified455 bootstrap order/profile.
Implement normal5x10 view/input/use/cooldown/download and replace obsolete belt
callers. Do not retain the old mixed payload model as the final game runtime.

All existing gaps remain mandatory: full payload copy/mutation/network/UI,
Quest localization/sentence expansion,Gesture/Macro,36 missing board classes,
Trunk/item protocol,Tutorial/QBI/fourstage/Login/auth/gameplay and remaining
resource/renderer behavior. No server file was modified,copied for development
or built. Originals and original configuration remain unchanged.
