# Character flags and actual MiniMap nuclear owner — work113

2026-11-09. CLIENT ONLY. Result **PARTIAL**, M6/M6F/M7/M9 OPEN.
Current gate: `inventory/client455-character-flags-checkpoint.json`.
Reproduce with `scripts/Invoke-Python.ps1 scripts/checkpoint_client455_character_flags.py`.

## Confirmed reference

Both x86 images/base0x400000 are pinned, never executed:

- primary SHA256 `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
- secondary SHA256 `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.

New selected evidence:30 equal function-body ranges,29 complete pseudocode
functions,14 full assembly listings/760 instructions; constructor EH tails are
pinned separately. Target vtables/constructor stores and direct CALL bytes are
checked against both images. Earlier Character constructor/guard and complete
44DEE0 reference from102/112 are reused, not re-decompiled.
Raw evidence: `artifacts/client455-progress/nuclear113-reference.json`;
summary with hashes/RVAs: `inventory/client455-character-flags-reference.json`.

RVA0x3D960 enables bits in Character DWORD+640. Bit1 calls the movement-controller
clock writer RVA0x3D9B0 before the OR, including repeated enable. The real clock
is timeGetTime and its destination is controller+8 through Character+2356.
Clear RVA0x3D9D0 preserves the timestamp; toggle RVA0x3DA70 uses virtual
slots172/176. Actual CPlayer vtable RVA0x6A8DDC and RTTI confirm those writers,
SetAction slot184 and SetWalkMode slot208.

RVA0x3DA40/0x1E5C30 implements **none(mask): `(value&mask)==0`**. This is not
an all-bits predicate. Nuclear guard RVA0x3DB60 tests action highnibble5 OR any
internal bits1/2. Internal flags are distinct from the 64-bit server flags and
from the converted player status DWORD.

Selected 44DEE0 control ordering is restored: flag1 clear when serverbit5 is
absent; corpse flag2 clear/recovery with none(flag1); cached blocked state;
death/control action transitions; permission flags0x20000/0x40000 from inverse
serverbits14/15; mining action0x70000004 only for serverbit11&&!cachedBlocked.
Action callbacks are checked for ordering but full SetAction sideeffects are
not restored by this work.

## Actual source and runtime

`client455_character_flags_port.py` adds an owned state member and typed methods
to actual CCharacter/CPlayer copies. Ordinary IsDeath now uses the recovered
guard; ordinary64bit SetServerStatusFlag calls the selected control producer
before status conversion. Conflicting legacy corpse/mining writers are removed.
The source clock has an explicit unknown state before first bit1 enable.
Source layout is owned and deliberately not the private455 class ABI.

`client455_character_flags.h/.cpp` is the65th normal facade. Complete build:
182 client/20 kernel/65 facade, unresolved0. Own x86 RF_Online.bin SHA256:
`4c81042a5a001d6a99ac33859061ae00ce6a55028da11797f7e3d845bb444393`,
2197504bytes,base0x400000,entryRVA0x1616C0,WinMainRVA0xB9060,
afterCreateRVA0xB91D4. Exact PE reaches Create return1 in the private lab.
Own decoded producer proof verifies the control call precedes the inline
statusbit16 conversion; no nonexistent out-of-line status call is claimed.

New native173 PASS at `work/m9/cbbfcf95/character-flags-001`: actual Avatar,
ordinary IsDeath over8 internal masks/16 action highnibbles, any/none0 and
partial-mask distinctions, clock-before-OR/repeated enable/DWORD clock wrap,
real WinMM timestamp,8 selected target action traces, ordinary64bit status
producer and nonzero BOOL toggle. Action transition traces use the source
kernel callback; a loaded model/action/effect/movement pipeline is not accepted.

Fresh changed-dependency regressions: status62, message83, center69,6 hover GPU
frames, exact own startup/Create1. Fifteen new GPU captures were viewed;
10 center/hover captures equal the pre113 baseline byte for byte. Native runs:

- status: `work/m9/82e752ae/player-status-001`;
- messages: `work/m9/1f581f89/message-output-001`;
- center: `work/m9/86a6aea7/center-messages-001`;
- hover: `work/m9/bf9ece2f/board-hover-001`;
- exact PE: `work/m9/4c81042a/startup001` and `ui-startup001`.

Engine67 SHA256 `546a7529b51139e856b1a108fcad7849c14b2d00563b7abbfdcc8db10026fa5a`
is unchanged. Old111 gate is historical; pre113 reports are saved under
`artifacts/client455-progress/*-before113.json`. Decoder112 and unchanged
chat/world/audio/bulk suites were not rerun. Their evidence remains historical,
not fresh proof against this PE. First failed prep/build attempts and failed
duplicate-header probe are not acceptance runs. Preparation now skips structured
library records when selecting canonical string-path producer reports.

## UI ownership correction for the next work

Earlier references to a separate nuclear dialog were too broad. Actual constructor
RVA0x305160, vptr write0x3051AB and RTTI identify **CGUIMiniMapWindow**. It owns
three540-byte **CGUINuclearBomb** children at+11716. Marker constructor
RVA0x30BBB0/vptr store0x30BBED confirms that identity. Helper RVA0x1C59D0 consumes
ECX MiniMap loaded from the caller's real global; its misleading decompiler
stdcall prototype does not make it a processor member or a standalone window.

Marker show RVA0x30BF30 positions from the actual race/index record before
configuring/showing the children; hide removes label/background/icon children.
Tuple RVA0x30BD80 is spriteID4/main.spr/action5/frame43 with autosize, dark
background0x96000000, then actual imagefont spriteID1/common.spr/action7/frame3,
7x9. Position RVA0x30BFE0 inverts worldZ against bounds.bottom; label uses
`"%2d %2d"`, `(int)(relative/4)+3`; background width is9*cellWidth,height30.
Preserve the position-before-configuration order; first-use zero dimensions
must not be silently repaired. Virtual roles of0x30BE90/0x30BEC0, MiniMap
transform/configuration producers, record lookup/lifecycle and actual drawing
still need remaining evidence. The added reference is not UI source integration.

## Remaining work

Work114: restore the actual three MiniMap marker owners/transforms/record
interface, then wire the already pinned group60 receiver/decoder112/core111.
Use selected board GetOrgObject/GetItem455 and real item serial/send endpoint;
retain result1/2/error/blocked branches rather than leaving no-ops. Receive
result0 starts selection, not an invented input callback.

Full Character SetAction flag writers, movement-controller owner/frame/clock
consumer, all remaining64bit server sideeffects, Nuclear registry32/opcodes/
frame/draw, actual gameplay flow and every client-acceptance gap stay open.
Bit1 clock methods are exercised in the full-object lab; ordinary SetAction
does not yet produce/consume that state. Compilation and Create1 do not close M9.

The initial owned IDA worker7760fad4 expired during the build. Authoritative
idb_list confirmed it absent; same copied IDB was reopened as1f253126 with
longer idle TTL, saved/closed successfully, final list0. No original EXE was
executed and no server files were modified/built.
