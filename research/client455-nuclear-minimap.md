# Actual MiniMap nuclear markers — work114

2026-11-09. CLIENT ONLY. **PARTIAL**, M6/M6F/M7/M9 OPEN.
Previous goal turn113 made progress: local commit `6b9d631` restored selected
Character flag owners/guard and identified the actual MiniMap marker owner.
This work adds the real three child owners and confirmed UI behavior to source.
Gate: `inventory/client455-nuclear-minimap-checkpoint.json`.
Reproduce: `scripts/Invoke-Python.ps1 scripts/checkpoint_client455_nuclear_minimap.py`.

## Reference and corrected virtual roles

Pinned x86/base0x400000 images, never executed:

- primary SHA256 `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
- secondary SHA256 `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.

26 selected complete function bodies and pseudocode;24 full assembly listings,
2594 instructions, including19 new listings/2028 instructions. Reused113/112
evidence is recorded separately, not counted as new analysis. Two constructor
EH ranges are pinned separately. Function bytes, vtable slots, constructor
stores/RTTI and decoded direct calls match both images. Details with exact
RVAs/hashes: `inventory/client455-nuclear-minimap-reference.json`.
Raw: `artifacts/client455-progress/nuclear114-{reference,session}.json`.
Owned IDA a0d50694 saved/closed successfully; final list0.
Input supplement6df7d12e also saved/closed/list0. Its two setters contribute
64 of the new instructions; raw evidence is
`artifacts/client455-progress/nuclear114-input-{reference,session}.json`.
Init virtual88 is container mouse input0:
RVA0x20CF90 writes the raw DWORD through0x20D010 and propagates to existing
children. The new marker implements this for its real simple icon/background/
label children. Initial focus is separate; full parent input is still open.

CGUINuclearBomb vtable RVA0x6E4A14 and constructor RVA0x30BBB0 were already
identified113. Slot4/RVA0x30BE90 delegates SetPos to CGUIContainer and moves
existing children by the parent delta. **Slot40/RVA0x30BEC0 is ordinary Draw**,
not clipped Draw or an update callback. It calls container ordinary Draw
RVA0x20CAC0 first; only after success, icon alpha adds5 through a BYTE.
The zero-extended BYTE cannot exceed255, so the apparent >255 branch is dead.
255 becomes4; no elapsed-time factor or clamp is introduced. Empty shown
markers still advance the retained icon alpha; hidden markers do not.
Slot36 remains inherited clipped Draw RVA0x20CB50 and does not pulse alpha.
MiniMap's ordinary Draw slot40/RVA0x3099A0 also delegates to ordinary Draw.

## Owner, geometry and first-display ordering

Actual MiniMap Init RVA0x3059E0 sets position and size400x400 on each of three
markers, sets mouse inputflag0, shows them and adds them to its map container.
The source uses three CGUINuclearBomb455 members in the existing MiniMap,
not a separate window. Ordinary Init, destructor cleanup and SetMapBound
are connected. Owned source layout is not the private540-byte ABI.

SetMapBound RVA0x3067A0 and geometry setter RVA0x306810 each fan out to all3
markers. Marker setters RVA0x30C2D0/0x30C310 recalculate scales using0x30C360.
Only positive signed bound differences recompute scales; invalid bounds retain
previous scales. Geometry includes original map dimensions and independent
offsets. The actual world producer RVA0x3C9240 reads signed-short bounds
at36/40/42/46 through a returned level object's+692 pointer and map
record588-byte stride fields552/556/560/564, then sets
bounds→geometry→selected map. It is not the legacy hardcoded8-map array.
That world producer/record loader remains unported; source geometry is supplied
through a typed API in this lab, without presenting legacy constants as455 data.

Show helper RVA0x30BF30 looks up the record position by actual Avatar race/index.
Lookup RVA0x12B3E0 uses key `(race<<8)|index`; it returns the record position.
The new source UI API consumes that lookup result. The actual registry/race
lookup and ordinary receiver are not yet connected.

After a successful lookup, **position0x30BFE0 runs before configuration0x30BD80**.
Coordinates use worldX and inverted worldZ, dimensions/offsets/scales, icon
integer half-size and parent position. Label is `"%2d %2d"`, coordinate
`int(relative/4)+3`. Background width is9*imagefont cellWidth,height30.
Show configures real sprite4/main.spr,action5/frame43/autosize24x24, then
background0x96000000, then imagefont1/common.spr/action7/frame3/7x9.
Child draw order is icon→background→label. First position uses previous icon
size0 and font cellWidth0, so the first background width stays0; repeated show
uses retained24x24/7x9 sizes. This visible target quirk is preserved.
Missing record retains UI state. Hide removes label/background/icon, retaining
their coordinates, Show flags and alpha; it does not reset the marker root.

## Source and real native validation

Sources: `client455_nuclear_minimap.h/.cpp`,
`client455_nuclear_minimap_port.py`; image-text header adds read-only cell metrics
and a conventional include guard for physical native/generated header copies.
The earlier actual Linker window source compiles against the final full object
set; its EXE is not run and no extra Linker runtime acceptance is claimed.
Normal build182client/20kernel/66facade, unresolved0. Own PE:

`7f9ba520ddbb801decf11a18502e00dacfffd04434e9eefd985dc8b7992db62b`,
2200064bytes/x86/base0x400000,entryRVA0x161AE0,WinMain0xB92F0,
afterCreate0xB9464. Exact own PE Create returns1 in the private lab.
Own decoded calls prove ordinary Init→marker registration and
SetMapBound→marker setter; own marker virtual Draw is retained. Position/show
and world-geometry helpers remain stripped from ordinary PE until real callers
are restored. They execute in the full-object lab; this distinction is explicit.

Native **702** PASS, `work/m9/6db17744/nuclear-minimap-001`: actual MiniMap3
roots, bounds/geometry fanout, first/repeated positions, true24x24 sprite and
7x9 font, child ordering, missing-record retention, hide state retention,
parent movement, invalid-bound scale retention, hidden early return, every256
alpha states, ordinary-versus-clipped Draw and empty-root alpha advancement.
Six real GPU frames viewed. First/warm output differs from cleared map by566/
2217 pixels. Coordinates/positions are controlled typed inputs; no live wire
capture or reference EXE capture is claimed.

Changed-dependency regressions:

- actual MiniMap opacity/queue81 amounts, Korea+Russia, six GPU captures:
  `work/m9/c9811d8d/opacity-{ko-kr,ru-ru}-001`;
- actual MainGame message/Login/fourpane/Avatar/BSP/6FX/Miles83, five captures:
  `work/m9/ac72af4d/message-output-001`;
- exact own startup/Create1: `work/m9/7f9ba520/{startup001,ui-startup001}`.

All17 new captures viewed; six opacity frames equal67 baseline, five messages
equal113 byte for byte. No unrelated broad GUI/world/audio/159k reruns.
Character173/status62/center69/hover6 remain historical113; decoder2429 historical112;
chat385 historical109 and other earlier proofs remain historical. Engine67
SHA256 `546a7529b51139e856b1a108fcad7849c14b2d00563b7abbfdcc8db10026fa5a`
unchanged;033baseline preserved,082derived snapshot still absent.
Previous reports saved under `artifacts/client455-progress/*-before114.json`.
An initial staging attempt guessed a localized main.spr path and stopped before
execution. Final probe uses the pinned existing resource manifest and actual
Common/main.spr. Only final successful native output is accepted.

## Next115 and preserved gaps

Restore actual nuclear record32/registry ownership, position lookup and effects/
tag2 audio/lifecycle/frame. Existing112 data/functions are already pinned; do
not repeat the full protocol audit. Then wire group60 decoder/ordinary receiver,
real result1 selection serial/send, result2 inventory/UI, blocked/error/other
opcode branches. The aiming20 core and record registry are different owners.
Restore real world geometry producer/map588 records, without replacing them
with legacy hardcoded arrays. All Character action/movement/64bit-status gaps
and every client-acceptance requirement remain mandatory.

This result does not accept full MiniMap/input/world/bootstrap/lifecycle,
record32/private map ABI, unsafe index/OOB/missing sprites/overflow/OOM/FP domains
or complete Nuclear gameplay. Compilation, Create1 and the selected lab do not
complete M6/M6F/M7/M9. Server files were not modified or built.
