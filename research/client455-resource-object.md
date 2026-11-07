# Resource-object090 — ordinary common base migration

Update091: this runtime gate is historical after the typed item-wrapper rebuild.
The current ordinary gate is `inventory/client455-item-object-checkpoint.json`.
The common-base static evidence/oracles remain applicable; the620-byte wrapper
oracles extend them. See `research/client455-item-object.md` for current scope.

2026-11-07. **PARTIAL**, within M6. This changes actual ordinary client
classes, not a parallel record-only runtime. M6/M6F/M7/M9 remain OPEN.

Item ownership work exposed a prerequisite: target CItemObject derives from
an80-byte CObject and584-byte CResObject; the ordinary legacy bases were48
and472 bytes. Migrating wrappers before fixing these parents would retain
the wrong object/resource model. This unit restores the selected common
constructor/copy/name/flag/destructor contracts. Real item-wrapper integration
is the immediate next step091, not considered finished here.

## Pinned evidence

Both reference binaries are x86/base0x400000:

| Pin | SHA-256 |
|---|---|
| Current | b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b |
| Backup | 46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558 |

23 selected function ranges agree.14 complete assembly exports contain765
instructions, including separately pinned noncontiguous EH windows. The
audit decodes21 C6/C7 EAX-relative immediate stores and reads seven float
constants from the pinned data sections for independent record oracles.

| RVA | Selected contract |
|---|---|
| 0x3ccb70 / 0x5dd0 | CObject constructor / copy |
| 0x27b0 / 0x27f0 / 0x1e5920 | Index clear / name setter / bounded copy helper |
| 0x3ccfa0 / 0x5100 | CResObject constructor / copy |
| 0x51c490 |84-byte secondary state defaults |
| 0x3cd210 / 0x3cefe0 | Resource destructor / effect-ID clearing |
| 0x3ce5b0 / 0x3ce620 | Enable / Disable effect and receipt rules |
| 0x3cf050 | Receipt flag / timestamp setter |
| 0x3cd390 | Direct name use by RenderName; full metrics still open |

Raw exports, future item-owner discoveries and saved session cleanup are
under ignored `artifacts/client455-progress/res-object090-*`. IDA65c60c5d
was saved/closed; session list is empty. No reference EXE was executed.

## Ordinary source changes

`client455_resource_object_port.py` applies checked byte edits only to owned
source copies through `prepare_client455_normal.py`. Legacy source encodings
and unrelated bytes/comments are preserved.

- CObject has its own64-byte name, without changing global protocol/name
  constants. Its constructor still clears only the first32 name bytes as455
  does. SetName clears/copies within64 bytes, including target truncation and
  null-input behavior. Explicit copy preserves destination padding5..7.
  The actual virtual Clear invalidates only the index.
- CResObject now has the constructor timestamp at244, the84-byte secondary
  state at500 and the target member order; obsolete unused blink timestamps
  are removed. Existing100-byte animation/84-byte initialization helpers are
  reused. Their values agree with the pinned constructor. The purpose of the
  secondary fields beyond selected defaults is not claimed as restored.
- Explicit CResObject copy delegates CObject copy and copies bytes80..583,
  matching the shallow target copy including animation padding and inline
  state. Source-owned vtables remain callable own C++ vtables.
- Enable/Disable now delete effects when clipping/client-out flags are set
  or the render-mesh bit is absent. The legacy expression used flags&~mesh,
  incorrectly clearing effects for other valid flags on visible objects.
  Enable also resets the receipt flag when server-out is present. Disable
  does not perform that extra reset. Actual effect-ID clearing calls the
  existing magic-effect provider, then clears both IDs.
- The name-render caller passes the name directly, removing its obsolete
  32-byte sprintf buffer. This prevents an overflow after64-byte name support;
  it is not acceptance of remaining legacy name placement/metrics behavior.

All derived consumers are rebuilt against the changed common classes. There
is no reinterpret_cast from legacy board classes to target620-byte wrappers.
Ordinary CBoardObject remains the legacy mixed model pending091.

## Verification

The actual normal182 client/20 canonical kernel/42 facade objects build and
link without unresolved symbols. New ordinary RF_Online.bin:

- SHA-256 `dc6f2c6293c91cab28b8b4689f9261a8d3d82039162ab309944c26df1087034e`;
- x86,2093568 bytes,image base0x400000,entry RVA0x1500e0;
- WinMain RVA0xb5b40,after-Create checkpoint RVA0xb5caa;
- unchanged engine SHA-256
  `9caa283a6bf8a2fa1c9a05251b6cad451296bb03bda8a1860c22a872e88fe769`.

The common-object probe links actual ordinary providers. Two complete584-byte
oracles verify constructor and copy with nonzero destination sentinels;
own vtable and real timeGetTime are normalized only for comparison.28 named
offsets agree with the target. Name64/null/truncation, virtual base Clear,
destructor ID clearing and160 flag cases pass.20 preserve effect IDs,140 clear
them;48 reset receipt. This probe calls the real effect-clear provider with
an empty live magic cache; it does not claim a populated magic cache or full
FX behavior from those cases.

Affected regressions passed:

- ordinary hotbar7 real send-ring/AES packets, storage17 registered classes
  and Avatar/account paths;
- RVP12 actors/269 ticks,185 model draws,148 particle draws,6 entity draws,
  deferred release and memory balance;9 GPU frames visually inspected;
- Bellato/Cora/Accretia real land load/render/reload/collision and memory
  balance;6 frames inspected (Cora reload is byte-identical to its first frame);
- unchanged payload089 source575 factories/wrappers and SF1447 on the new
  dependency archive/full-object set;all four own entry executions exit0;
- exact new PE CRT/WinMain/local TCP fixture/sound/D3D/normal Create=1.
  Startup first-chance exceptions are recorded; no unhandled exception was
  accepted. The debugger stops before the game loop, not a gameplay claim.

The first Bellato world run stopped at Character shader initialization:
the old staging script omitted required Character .sho files. The actor probe
already staged them through `copy_character_shaders`. The world runner now
uses that same verified helper. All three maps then passed. This was a
laboratory input correction, with no additional production change.

The current ordinary acceptance gate is
`inventory/client455-resource-object-checkpoint.json`.086 ordinary and088/089
source-runtime checkpoints are historical after the new link/dependency
reports; static binary/data references remain applicable.089 source-runtime
was rerun against the current dependencies and is checked by090. No unchanged
159k suite, renderer kernel suite or audio suite was repeated.

## Next091 and required gaps

Restore actual CItemObject/CBoardObject lifecycle and binding to source item
payload/data managers, then typed board/hover owners and ordinary Linker
clones/5x10view/input/use/cooldowns/download. The new bases are prerequisites,
not proof these owners already exist.

Cached selected owner bodies include46AF20 ctor,46AF70 destructor,46AFE0
Clear,46B010 payload setter,46B1B0 board ctor,46B4C0 Clear,46B570 clone,
46BC90 derived setter. Revalidate canonical ranges before porting cached
queries that originally hit an interior address. Preserve the primary-cache
guard and signed BYTE reference semantics from087.

Full resource methods, name metrics, shader/lighting/advancedFX/reset/OOM/
unwind and actual private-ABI uses remain open. Full payload methods,
Quest localized sentence expansion, Gesture/Macro,36 missing board classes,
Trunk/item protocol, Tutorial/QBI/fourstage/Login/auth/gameplay and all previous
M6F/M7/M9 requirements remain mandatory. No server files were modified,
copied for development or built. Originals/configuration were unchanged.
