# MainGame Linker startup and factory audit — 166

2026-11-11. CLIENT ONLY. Current gate:
`inventory/client455-board-startup-checkpoint.json`, **PARTIAL_KNOWN_FAILURE**.
M6/M6F/M7/M9 remain open; world not entered; 0/12 full domains accepted.

## Reference and measured scope

Both immutable x86/image-base `0x400000` references were checked:

- primary SHA-256 `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
- secondary SHA-256 `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.

Full paginated ASM and positive CFG regions of six functions match both pins:
3,032 instructions, 253 positive blocks. Raw proof is
`artifacts/client455-progress/board166-reference.json`.

| RVA | Measured body |
|---|---|
| `1477C0` | MainGame board startup, including later unfinished branches |
| `FB920` | 54-owner factory and initial window setup |
| `FCF00` | CBlackListBoard constructor, previously omitted from the count |
| `1002B0` | Linker InitWindow and bottom-right positioning |
| `F92F0` | BaseBoard InitWindow and special positioning values |
| `26CB20` | Late hotkey binding with one window owner |

The startup Linker portion at RVA `147832..1478CB` creates board6 with five
banks of ten slots, initializes window3 at (400,500), activates banks0..4 and
opens it with argument1. InitWindow subsequently places the window at the
screen's bottom right. The next board is UnitTuning12; there is no separate
old potion Belt between them. These operands and calls are checked directly
against the complete assembly, not inferred from the old source constants.

The reference factory constructs 54 named owners. The current source still
registers only17 corresponding classes; **37 owners are missing**. This count
does not prove that the17 existing classes have455 behavior. The complete
reference factory also initializes QuestBriefing20, QuestFinishReport50,
QuestReward21, Trunk5 and NpcQuest52 before MainGame inventory initialization.
Those five paths remain absent. Historical084/085's53-owner count was wrong:
its extraction matched53 `if (operator new(...))` forms but missed the54th
allocation assigned to a temporary before an explicit-this constructor call.
Full assembly confirms size12 at RVA `FC4D5`, constructor call `FC4FB` and slot30
store `FC52E`. Constructor `FCF00` writes the CBlackListBoard primary vptr at
`FCF17`; the bytes and RTTI match both pins. The factory allocates54 distinct
slots; only2(alias) and23 have no allocation in this body. This corrects the
inventory rather than adding a newly invented feature.
The audit also records110 direct MainGame
board lookups with their call RVAs; indirect helper accessors remain in the raw
listing. No factory owner or its behavior was replaced by a generic stub.

## Actual source change and validation

`client455_board_startup_port.py` reproducibly connects the ordinary MainGame
to `CLinkBoard::InitializeMainGame455`, compiled from
`native/client455_linker_startup.inc`. The old one-bank/eight-slot setup and
separate Belt initialization at this location are replaced with the measured
sequence. Other old Belt consumers retain their explicit migration guard.
Later old hotkey/global bindings and other board startup are still open.
No whole-function455 equivalence is claimed for MainGame::Create_Board.

Native `work/m9/7d430eab/linker-window-001` passes the actual startup, all50
admitted clone/icon owners from16 real EDF-backed originals, bank layouts,
events and glyph cases. A real window3/bank4 HWND message passes through the
ordinary CBoardManager and updates Linker6's active bank. The fixture borrows
only this actual board into an otherwise empty test registry and restores the
slot afterwards; it does not claim construction of the missing37 owners.
Full item-use gameplay is unaccepted. The existing Potion11 exclusion remains.

Eight GPU frames were inspected. Final frames are byte-identical, including
their previews, to the just-inspected `0c0ccbc4/linker-window-001` set. Owner
release and sprite allocator balance pass. The first run lacked SocketState.spr
after the165 inventory port; adding the real required asset to the old fixture
resolved that fixture failure. No product skin alias or fallback was introduced.
Staging uses38 shared assets/79,608,818 linked bytes/**0 new pool bytes**.

Normal client build/link, real normal ANI/BBX consumers, own entry/import audits
and fresh early Taiwan startup pass:182 client/67 engine/20 kernel units,
zero unresolved symbols. Current own executable:

- SHA-256 `fe40637c9b230f97057786b6c80f44365a9a12dd9373999558bd91b46490273b`;
- x86, base `400000`, entry RVA `183720`, 2,369,024 bytes.

## Actual live boundary

`work/m9/fe40637c/selection-live-taiwan001` authenticated through the existing
launcher contract; selection tx1:14:1/rx1:15:22/result0 was accepted. The
pre-Enter frame was inspected; it is not a world frame. The ordinary Linker
startup returned and the next old CGUIUnitTuningWindow SetSprite/Init failed:
own access violation C0000005 at RVA `13028F`, CSprite::GetSpriteXL+5F.

Bounded own stack candidates include UnitTuning SetSprite `B95F7`, Init `B7AD4`,
BaseBoard InitWindow `12E62` and MainGame Create_Board `26FC8`. They are candidate
scans, **not an unwind**. Corroboration in the exact own PE includes:

- decoded MainGame call `26F8B E8705A0100`, return `26F90`, to the real Linker
  startup at RVA `3CA00`, before the later UnitTuning call;
- actual UnitTuning vtable RVA `1F53D0`, slot `6C` -> Init RVA `B72A0`;
- BaseBoard return `12E62`, prior `FF506C` virtual Init instruction;
- matching source order and inner SetSprite/Init candidates.

Evidence: the new checkpoint, `board166-own-prefix.txt` and `board166-failure.json`.
UnitTuning Init did not finish. Later equipment/pack Init and the complete
factory/world/gameplay chain are not proved. The successful wrapper exit is
not a successful whole-client run.

## Remaining work and accounting

Next: recover the actual UnitTuning window and board initialization, then keep
migrating the complete54-owner factory and MainGame graph, including its five
initial windows, real IDs/dimensions, one-owner hotkey binding and remaining
old Belt consumers. All previous inventory/Animus/options/actor/network and
M6F acceptance gaps remain mandatory; potion/hotbar gameplay is still required.

Analysis now covers2,463 unique functions with address evidence (+2) and657
with full assembly/CFG (+6), from the unchanged IDA index37,871. The137 selected
partial bindings in nine prior registries are unchanged: this startup prefix
does not become one fully reconstructed original function. Engineering estimate
25%(20–35%) is unchanged and is not measured BIN readiness.

Exact before167 snapshot:197 files,7,502,253 private bytes and4,150,820 shared
prior-snapshot bytes, including the current own executable and relevant source
fragments. No complete client or asset tree was duplicated.

IDA sessions `a06985c9` and `5c316b5a` saved/closed, list0. All own native/live jobs terminated;
private handoff removed. Originals/server code and settings unchanged; input
EXEs not executed; credentials and raw authentication packets not persisted.
