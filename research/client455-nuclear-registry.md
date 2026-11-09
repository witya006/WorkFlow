# Nuclear registry115 — record32, effects and shared countdown

**Исторический этап. Current runtime gate116:** [receiver116](client455-nuclear-receiver.md).
Result2 — original storage board0/actual UI_UseResult(TRUE),а не открытие
инвентаря/отдельного dialog;5C59D0 — marker MiniMap. Registry теперь stage-owned;
ordinary receiver/lookup connected,full world geometry/stage/auth/texture lifecycle OPEN.

Status: **PARTIAL**. M6/M6F/M7/M9 remain OPEN. Current runtime gate:
`inventory/client455-nuclear-registry-checkpoint.json`. Previous114 gate is
historical. This restores a required client subsystem; it does not accept the
ordinary group60 receiver, complete gameplay or full stage lifetime.

## Evidence and reference identity

Both pinned x86 images, image base0x400000, were checked against
`config/client-target.json`. Primary SHA-256:
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`.
The complete secondary SHA is in the generated reference report.
34 complete selected pseudocode bodies and31 full assembly listings cover
1394 instructions;30 assembly listings/1339 instructions were acquired in115.
Three EH tails are hashed separately. Cached112 record bodies and114 lookup
were reused after hash validation, without repeating the protocol audit.

Raw: `artifacts/client455-progress/nuclear115-reference.json` and
`nuclear115-session.json`. Owned IDA session7f76f2ac was saved/closed; the
supervisor returned count0. Input EXEs were never executed. Server files were
not changed or built.

| Target RVA | Confirmed role |
| --- | --- |
| 0x12a680 | Record constructor:32 bytes; DWORD12 untouched |
| 0x12a6d0 | Empty record destructor |
| 0x12a750 | Copy position float3 |
| 0x12a7a0 | C15 race notification |
| 0x12a7e0 | Shared process countdown |
| 0x12a890 / 0x12a930 | Launch / impact |
| 0x12a9d0 | Radar with sound tag2 |
| 0x12aa90 | Reset handles, retaining position/countdown |
| 0x12ad70 / 0x12ae00 | Container constructor / destructor |
| 0x12ae70 | Ordered record update, then aiming update |
| 0x12af00 / 0x12b080 | Add / remove |
| 0x12b1c0 / 0x12b290 | ClearAll / ResetRecords |
| 0x12b3e0 / 0x12b480 | Race/index record lookup / position getter |
| 0x14638c | MainGame init calls container constructor |
| 0x14b059 | Late MainGame render calls container update |

The reference report contains exact body/tail sizes, hashes and decoded direct
CALL edges for both pins. Names from decompilation are descriptions, not proof
of source identity or full equivalence.

## Preserved behavior

The record contains handles at0/4/8, float3 at16 and DWORD countdown at28.
Known fields start zero; DWORD12 is not initialized or read by this port. The
modern map uses the target key `(race<<8)|index`, including unsigned65535.
Duplicate insertion keeps the original record; missing operations return false.
The private old STL container ABI is not reused or accepted.

Remove and ResetRecords set aiming.pending0 **before** missing/empty checks.
Pending0 retains an existing aiming effect/sound, as established in107. RadarOff
disappears a nonzero radar handle before stopping277034/tag2, and stops sound
even when the handle is zero. Reset reverses that order: stop tag2, call radar
disappear0 even for handle0, then zero all three handles. Position/countdown
remain. Launch and impact are detached and continue in the global effect system.
The record destructor is empty; the container destructor performs ClearAll.

Launch/impact at all-zero position emit the exact literal `Not Nuclear Posion`
without starting effects/audio or forcing light. Partial-zero positions are
valid. Radar allows the all-zero position. A position setter does not move an
already-created effect. Actual archived resources:

| Operation | Magic ID | Sound ID | Parameters |
| --- | --- | --- | --- |
| Radar | 1358041136 | 277034 | angle0, persistent, loop1/tag2 |
| Launch | 1358041392 | 277036 | angle90, auto, loop0/tag0 |
| Impact | 1358041648 | 277038 | angle90, auto, loop0/tag0 |

All three starts force dynamic-light setting3, including a missing effect handle.
The scripts are read from actual EffectEntity59.rpk, with manifest mapping and
saved byte hashes. Launch contains1 entity track with Y offset-70; impact has
14 entity tracks and a quake control at2.6s, time5/density150. The native lab
also stages the separate actual archive containing generic dynamic-light entity1,
found by its pinned archive directory rather than an invented filename.

The sound cache retains tag2 while another active tag1 keeps the same wave
cached. A tag2 restart can therefore be suppressed until the entire wave entry
is collected. The probe preserves this accepted backend behavior.

The countdown uses process globals VA0x1012850/0x1012854. It does not reset with
records, maps or containers. Only positive **signed** countdowns read the clock.
Initialization sets the flag before the first timeGetTime, then reads it again.
Unsigned elapsed>=1000 consumes exactly one tick, with no catch-up. C17 receives
the new count+1. Ascending map order means the first eligible record consumes the
tick; later records do not decrement during the same immediate frame. C15 uses
actual language indices0/1/2 for race names, and an empty literal for other races.

## Source and ordinary integration

`scripts/native/client455_nuclear_registry.h/.cpp` implements the source owner;
`scripts/client455_nuclear_registry_port.py` prepares ordinary MainApp/MainGame
copies. Existing aiming access now refers to its member in the container.
MainGame's ordinary late Render invokes record countdown, then cursor aiming;
ordinary MainApp shutdown clears records before the existing aiming Clear.
These direct calls were decoded from the **own linked PE** and byte-checked.

The current MainApp holder remains a temporary bridge. The target creates this
manager inside MainGame initialization and destroys it on stage teardown. Proper
stage ownership/factory/reset is still required. The extra explicit aiming Clear
at own MainApp shutdown is inherited own integration, not a target container
destructor claim. Ordinary receiver/record-creation callers are absent; Launch
and NotifyRace helpers are stripped from the ordinary linked PE. Their execution
is proven only in a lab linked against the complete current object/library set.

## Current validation

Own PE SHA-256:
`52c2a7c55aa7491045306b67a9b541c1cb2cce75f2568d7448337dda9a1a60f4`.
x86/base0x400000,2203648 bytes,entry RVA0x162800,WinMain RVA0xb9380,
after-Create RVA0xb94f4. Build182 client/20 kernel/67 facade objects, unresolved0;
exact own PE reaches existing Create with EAX1. This is not full bootstrap/game
acceptance. Engine67 remains
`546a7529b51139e856b1a108fcad7849c14b2d00563b7abbfdcc8db10026fa5a`.

- Registry native109 checks, actual effect/sound resources and5 GPU frames:
  `work/m9/8159c8c3/nuclear-registry-001`. Signed/clock-wrap/999/1000/no-catchup
  cases use the production kernel with a supplied clock; two real1050ms waits
  additionally prove ordinary process-clock order and persistence across ClearAll.
- Existing aiming29 passes with real BSP/6 children/Miles and its scoped allocation
  balance: `work/m9/675361e3/nuclear-aiming-001`.
- Marker702/6 GPU: `work/m9/6bea5e91/nuclear-minimap-001`; actual Linker header
  compatibility build succeeds. Full Linker runtime was not repeated.
- Ordinary messages83/5 GPU: `work/m9/929aae5f/message-output-001`.
- All16 current frames were viewed;11 marker/message frames exactly match114.
  The nearby blast covers the viewport in this selected scene; no original455
  executable capture or full trajectory comparison is claimed.

The final detached effects naturally drain in321 update ticks; both final frames
have zero remaining effect pixels. **The registry run emits20 R3T release
warnings during teardown.** The legacy R3ReleaseTextureMem warning path is present
in unchanged engine code; complete registry texture ownership/memory balance is
unproven. A vanished effect is not proof of correct texture lifetime. Keep this
as a concrete M6 follow-up, along with full world/camera quake/light compositing.

Early probe attempts exposed incomplete lab archive staging, retained-tag cache
behavior and chat-inserted line breaks. Fixture/assertion corrections resolved
those failures without changing production behavior; failed run console files
remain in ignored work/m9. Successful registry validation is bound to the final
probe/source hashes. Failure unwinding through uncreated legacy stage teardown
also remains outside accepted full-stage lifecycle.

Before115 reports are preserved under artifacts/client455-progress. Git stores
JSON blobs with LF whereas the historical working report hash used CRLF. The
old aiming report's exact CRLF bytes were reconstructed only after confirming
the recorded SHA-256, and saved as `client455-nuclear-aiming-native-historical-before115.json`.
No old-source recoding or original input changes occurred.

## Remaining work

Next116: connect the actual group60 receiver and all9 decoder layouts to real
guard/selection/dialog/send, registry and MiniMap consumers. Restore proper
MainGame container ownership together with stage birth/teardown. Follow up the
concrete R3T teardown warnings and then worldgeometry588 producer, full effect
trajectory/camera/lights/quality/device lifecycle. All earlier acceptance gaps,
including full action/movement/status/input/inventory/auth/gameplay, remain.
No159k, broad world/audio/other GUI suites were rerun as a proxy for completeness.
