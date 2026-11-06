# Client455 scrollbar EX/Var — участок066

2026-11-06. Scope: distinct source contracts in ordinary GUI provider and
full-object verification. Production minimap455 integration and full parent input
remain OPEN. No input EXE executed or server source modified.

References: x86/base `0x400000`;
current SHA256 `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
backup `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
37 function ranges and two primary-vtable regions agree byte-for-byte between
pins.13 full instruction dumps retained. All addresses below are RVA.
Owned IDA sessions `68442489` and `ef4ffb43` saved/closed.

## Recovered EX contracts

- Constructor `23A2C0`:base scrollbar plus ordinary CGUIButton at target+968;
  mouse/motion observers assigned,button added even when total0.
- Size `23A570` and amount `23A750`:same asymmetric arrow layout,plain thumb
  dimensions and independent minimum. Auto length is remainingExtent-total with
  minimum field;there is no composite6×18 clamp. Negative available minimum is
  retained. Total0 removes observers,keeps child.
- Track `23B050` and UpdateBar `23AA60`:own plain thumb size,wrapped signed32
  current×track followed by division.
- Input `23AAE0` and motion `23AE40` call **base** snap `23A1A0`,which reads
  inherited composite size. This is intentionally different from positioning.
  EX has no MOUSE_PRESSED arrow-repeat branch. Grab does not press composite caps.
  Track/drag retains post-update direction comparison;release aligns using own
  track when amount unchanged.
- Alpha `23A3C0`:plain button,arrows,unused composite and self.
- Primary vtable `6DB02C` points to inherited Draw `2394A0`. GUIObject ctor
  `225C70` sets show0. Therefore visible EX paints children but its hidden unused
  composite can make Draw return FALSE. Probe initially expected TRUE;expectation
  corrected after inspecting constructor and Draw,without normalizing source.

## Recovered Var contracts

- Constructor `23B0C0`,initializer `23B2B0`,vtable `6DB0FC`:virtual+24 is
  SetSprite `23B310`,**not RemoveAll**. Two inherited arrow children remain.
- Three objects at+968/+1064/+1204,with middle CGUIObjectEx;two image metadata
  sets per object. Common action15 frames0/1/2 and pressed3/4/5.
- Sprite setter `23B440` intentionally does nothing.
- Size `23B630`:outer size remains raw;separate skin size clamps6×18. Cap width
  uses skin width,height comes from valid requested resource,otherwise0. Does
  not call SetAmount/reflow or recompute cached middle extent.
- Virtual total/current/amount `23B6E0/23B720/23B760`:clamp amounts,addthree skins
  and base composite,place composite at origin,resize to preferredHeight-total
  plus cap heights with composite minimum. Does not UpdateBar. Cached middle
  extent is preferredHeight-total including zero and negatives. Total0 removes
  four children and self mouse observer,but does not clear cached extent.
- Track `23BA90` subtracts cap dimensions and cached middle extent. Snap
  `23BB20` has same x87/F32/ftol2/modulo/half rules as ordinary scrollbar.
- Input `23BC40`:vertical track subtracts **full** thumb height;thumb press
  changes three skins and grab;release/click changes skins only. Horizontal
  track path reads an uninitialized local;source refuses that path explicitly.
- Motion `23BED0`:vertical free position,clamp,commit/event then restore free
  position. It does not gain a generic horizontal implementation.
- Draw `23B460`:zero extent returns FALSE before drawing children;negative
  extent skips row loop. Row loop uses **common action2** frame1/4 despite cap
  metadata action15. Crop row2 repeats per pixel. Middle/bottom positions then
  update and ordinary container draws. UV helper `2269A0` stores width ratio as
  float before final UV;source preserves that spill.

## Real callers and resource limitation

EX constructor has a real caller in CGUIMiniMapWindow constructor `305160`;
its Init `3059E0` calls helper `3B2C60`,moves scrollbar y+15,sets80/80,assigns
scroll observer and adds it. Those owner/helper/input bindings are not yet ported.
There are no direct Var constructor xrefs in this IDB. Indirect construction or
other uses are not excluded by that observation.

Selected Ko/Ru common.spr has15 actions and44 frames in action2. Target loader
`4CFB90` requires **actions<16**,already established in048 and rechecked066.
Consequently ordinary loading cannot provide Var action15 at all. Do not alter
the target guard merely to make an unused/default skin work.

The first owned fixture16actions correctly terminated via engine Error/exit1.
Corrected fixture has15actions,keeps cap action15 unavailable (height0),and gives
action2 frame1/4 distinguishable row2 colors. This verifies missing-cap behavior
and row rendering;it is not a replacement game asset or evidence of actual Var
usage in gameplay. Real common arrow data is used for EX capture.

## Source and verification

Tracked `scripts/native/client455_gui_scrollbar.{h,cpp}` now contain EX/Var.
Base state is protected and SetSize virtual for source dispatch. Existing base
amount methods remain static calls;EX must not silently gain different snapping.
Legacy0.7 parent/show adapter remains;full455 parent input/focus is OPEN.

`probe_client455_scrollbar_variants.py` links actual ordinary client object set;
queued events go through CGUIObject event queue and real IScrollObserver.
Clock replay is restored to default after tests. No methods are force-retained
in production:until real455 owner is ported,unused variant code can be stripped.

Own probe SHA256
`7d9b518cd492543317be036979821e12ee1e48a2556dbe81175235dc5c58f396`,
both Ko/Ru natural exit0. Three640×480 GPU readbacks:

| Scenario | Changed pixels | SHA256 |
|---|---:|---|
| EX real arrows/plain thumb | 282 | f82459ba48608252bafdceff29aceaf31d8573aa16e93bf4d78264e79bddbe59 |
| Var normal row2 | 420 | f234ab14b4196253acdec1fdd87c4ac73f76d60f626b913d095f29e2f903e92e |
| Var pressed row2 | 420 | 577ce46ee4f8a6f583a946197ffab9268c2f31b2abf6f3bcdfbaf650883343f4 |

All three frames agree between locale profiles. Pre-final148e5bba previews were
visually inspected;final7d9b518c frames have identical hashes. Pixel oracle
requires green/cyan row2,not gray remaining rows.

Production RF_Online.bin SHA256
`b24f1f0967de631da59f427df4c73908cf057621385238f88166e2f40b59db95`,
x86/base400000/entry14E290,2029568bytes,182client/20kernel/26facade TU,0unresolved.
Generator idempotent. Ordinary scrollbar,textboard,textmetrics,font,modal and
tutorial-board regressions passed. Exact own WinMain passed TCP fixture/engine/
D3D/Character/existingCreate1;stopped before game loop. This is not auth or world
acceptance. Scoped checkpoints remain PARTIAL.

Evidence: `inventory/client455-scrollbar-variants-{reference,native,checkpoint}.json`;
raw ignored `artifacts/client455-tutorial/scrollbar-*066.json`;
lab `work/m9/7d9b518c/variants-{ko-kr,ru-ru}-001`.

Next067:actual minimap owner/helper3B2C60 and parent input;then production rich
callers/message sizing/fullbriefing/actual Tutorial/fourstage. Other private ABI,
all skins/alpha/clipping/lifecycle/OOM/FP/unsafe domains and full gameplay remain
open. M6/M6F/M7/M9 OPEN;M8 graphics modernization outside this goal.
