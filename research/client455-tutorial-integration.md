# Tutorial integration dependencies — 084

2026-11-07. Client only. **AUDIT_OPEN**, not a runtime restoration. The normal
RF_Online.bin and engine remain the verified 083/082 binaries. M6/M6F/M7/M9 are
open. This audit changes the implementation order for the real Tutorial owner;
it does not accept Tutorial, the common gameplay UI or the four-stage factory.

## Evidence

Both pinned x86 binaries have image base `0x400000`:

- current SHA-256 `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
- backup SHA-256 `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.

92 selected function body ranges match. All selected pseudocode is complete,
including the 447-line common board initialization. Four functions have **1514
actual complete assembly instructions**: board factory1388, GetBoard27,
Tutorial constructor44, quest-briefing constructor55. This is not full assembly
coverage of all 92 functions. Constructor primary-vptr writes are independently
decoded from the instruction bytes, and their PE complete-object RTTI is read
and compared on both pins. RTTI names establish selected object identities;
they do not establish equivalent behavior of a same-named legacy class.

Raw evidence is under `artifacts/client455-progress/tutorial084-*.json` with
reused complete entrypoint pseudocode in `tutorial083-initial.json`. The
reproducible inventory is `inventory/client455-tutorial-integration.json`.
Owned IDA session `14d8cac3` was saved/closed; the session list returned zero.
No reference EXE ran and no server source was changed or built.

## Confirmed integration gaps

| Target VA / RVA | Role |
|---|---|
| `5586D0` / `1586D0` | Tutorial Create calls all three common initializers below |
| `5467D0` / `1467D0` | Common gameplay UI creation/publication |
| `5477C0` / `1477C0` | Common gameplay board initialization |
| `5488F0` / `1488F0` | Common Avatar preparation |
| `4FB920` / `FB920` | Actual target board-object factory |
| `4FD860` / `FD860` | Public board lookup: below56, ID2 aliases equipment1 |
| `4A5AE0` / `A5AE0` | Dedicated CTutorialBoard constructor |
| `49B550` / `9B550` | CQuestBriefingBoard constructor, ordinary registry ID20 |

The target factory allocates **53 physical objects**, with public lookup limit56.
Physical slots2/23/30 are not assigned by this Create; public ID2 returns slot1.
This does not establish that no other runtime path can fill a remaining slot.

The actual current source constructs18 objects under19 IDs. Seventeen target
class names also occur in that source registry. The remaining36 names are absent
from this registry, which is **not** a complete source-file absence claim or a
count of entirely absent features. The old CBeltBoard name is not among the
53 constructed target identities. Same-named classes remain behavior-unproven.

Some important IDs:

| Object | 455 public ID | Current source ID |
|---|---:|---:|
| CInventoryBoard | 0 | 0 |
| CEquipBoard | 1, alias2 | 1, alias2 |
| CForceBoard | 3 | 4 |
| CAnimusBoard | 4 | 5 |
| CTrunkBoard | 5 | absent in current registry |
| CLinkBoard | 6 | 6 |
| CSkillBoard | 7 | 7 |
| CJournalBoard | 19 | absent in current registry |
| CQuestBriefingBoard | 20 | absent in current registry |
| CQuestFinishReportBoard | 50 | absent in current registry |

The existing QBI action implementation asks the host for board3 for Force UI.
Forwarding this unchanged to current legacy GetBoard would return **CBeltBoard**.
Animus IDs also differ. A real host therefore needs the actual455 storage/board
contracts and matching owners, not an unchecked numeric passthrough.

CQuestBriefingBoard and dedicated CTutorialBoard are distinct constructor/vptr/
RTTI identities and lifecycles. Both use window ID38. Neither a shared ID nor
the47 QBI selectors justifies merging these owners or using board slot47.

The common Avatar initializer also reaches character-info/nameplate consumers,
equipment state and other gameplay state. Selected stat setters reference a
fourth resource gauge and nameplate updates; the earlier 64-bit money unit did
not cover these dependencies. Do not equate the old Create_Avatar body with455
based on similar names/calls. The inventory records required pure-virtual
declarations separately for the five actual host interfaces; inheritance and
overlap mean their declaration counts are not counts of unique gameplay features.

## Actual source measurement

`probe_client455_tutorial_dependencies.py` builds a full-object probe from the
current normal source. It creates the actual existing CMainApp network member
before CBoardManager, as required by real board constructors, then constructs,
queries and destroys the real source objects. No graphics device, game connection
or authentication is used. Native RTTI and source sizes are recorded rather than
inferred from file names.

Final diagnostic PE SHA-256
`1e7484980582af6a430f820a263fca529a8cc09d71312a2ee8f5b40df8495e22`:
eight independently staged runs exit0 and report identical18-object registries,
the equipment alias and out-of-range null. Source sizeof MainGame65984,
Avatar19280, semantic CTutorialBoard32, briefing2736. These source sizes are not
binary-layout parity or percentages: the port deliberately owns semantic
objects rather than overlaying the reference's complete C++ layout.

Two fixture errors were found and corrected without production changes. The
initial probe omitted the actual network owner, and failed inside its getter
with ECX0 (seven of eight diagnostic runs failed; one pass did not establish
stability). A subsequent local CNetworkMgr exceeded the audit process's stack.
Using the real embedded global member and the proper creation/destruction order
gave the eight successful final runs. Failed console/EXE copies remain ignored
under work/m9. These fixture failures are not evidence of bugs in the ordinary
client startup, which already creates the owner in the appropriate order.

## Next implementation work

1. Recover and port the actual455 storage/board contracts and common factory,
   including the Force/Animus IDs and the role of the old belt. Verify protocol
   consumers together; changing just two numbers risks duplicate board slots.
2. Restore the common UI/board/Avatar providers required by actual Tutorial
   creation: gameplay gauges, character-info/nameplate, briefing/quest owners,
   real processor references and resource/lifecycle behavior.
3. Bind actual QBI actions, follow camera and local handlers to those owners;
   then restore CGP_Tutorial Create/Load/Frame/Input/Destroy and four-stage/Login
   transitions. Keep every remaining registry/gameplay feature required for M9.

The source force/animus mismatch and absent registry classes are implementation
work, not a reason to replace the real host with recordings or mark the mode
complete after an ID-only switch. No overall client completion percentage can
be inferred from this partial registry or the number of assertions.

Reproduce through `scripts/Invoke-Python.ps1` using
`probe_client455_tutorial_dependencies.py`, then
`audit_client455_tutorial_integration.py`. The latter revalidates the exact current
link, staged source evidence, constructor instructions, RTTI and reference pins.
