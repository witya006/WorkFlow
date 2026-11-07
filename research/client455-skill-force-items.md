# Client455 SF items and concrete manager — 088

2026-11-07. **PARTIAL_SOURCE_RUNTIME**, within M6. A source SF payload factory,
five-table data owner and concrete primary manager now cooperate with087
wrapper clone/reference-release kernels on real supplied EDF files. The
manager host is no longer a recording fixture for these SF scenarios.
Ordinary game-global item/board/hover/Linker owners are not yet migrated;
production RF_Online.bin remains086.

## Reference and selected behavior

Both pinned references are x86/base400000:

- behavior SHA-256 `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
- backup SHA-256 `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.

Thirty-five selected function ranges have equal bytes between pins;16 full
assembly exports contain1224 distinct instructions. IDA includes noncontiguous
compiler EH tails in several functions: these are separately pinned with
15-byte windows covering every external instruction. They were not discarded
to force a contiguous-range check. Capturing them does not establish full
exception/unwind equivalence.

| VA | RVA | Confirmed role |
|---|---|---|
| 5FBC80 | 1FBC80 | Load five root SkillForce tables into manager+48..96 |
| 5FB670 | 1FB670 | Root load, localized overlay, count mismatch returns0 |
| 5F0CC0 / 5F0DC0 | 1F0CC0 / 1F0DC0 | Count/stride/raw table and ordinal lookup |
| 462E00 / 462EB0 | 62E00 / 62EB0 | CSFItem constructor/selected initialization |
| 462FD0 | 62FD0 | Fresh SF Create, IDs/subtype/borrowed data/initial level |
| 469AD0 | 69AD0 | Six-way factory; selector1 allocates160-byte SF payload |
| 4697B0 | 697B0 | Create then append successful payload, no deduplication |
| 469720 / 469960 | 69720 / 69960 | Primary cache clear/remove |
| 404CF0 / 404D10 | 4CF0 / 4D10 | Kind BYTE getter/comparison |

RVA/size/SHA-256, raw export hashes and external-tail windows are in
`inventory/client455-skill-force-items-reference.json`. Owned IDA session
cd8baa1a was saved/closed and followed by an empty session list. Original EXEs
were never executed; original files and servers were not modified.

## Actual inputs and installed profile

The target loader uses **root** `DataTable/SkillForce.edf`, followed by
`DataTable/<country>/NDSkillForce.edf` (or its separate W variant). The five
root tables contain:

| File/profile | Counts in table order |
|---|---|
| Root SkillForce.edf | 88,84,504,60,711 |
| zh-tw/NDSkillForce.edf | 88,84,504,60,711 |
| ko-kr/NDSkillForce.edf | 88,84,504,60,640 |
| ru-ru/NDSkillForce.edf | 88,77,504,39,446 |

Root strides are1100/1124/1124/1124/1124; the payload is1624356 bytes and has
1447 rows. Each localized row supplies name32/text512; its second header DWORD
is ignored by5FB670. The target writes name at+112 and text at+524. It returns
failure on the first section-count mismatch **after preserving earlier
section writes**. Thus Korean input fails at zero-based table4, Russian at1.
The source reproduces those failures and prefix mutations.

The original installed R3Engine.ini currently selects `Language=Taiwan`.
The already verified nation mapping gives ID8/folderzh-tw. The successful
source test therefore matches the installed resource profile; it is not a
configuration change. The checkpoint records the selected setting-line hash
and mapping evidence. A separate new early-startup probe runs the exact own
PE with Taiwan: CRT/WinMain, real NDLanguage950/6997 records, local TCP fixture
and sound return1 pass; the own debugger stops before D3D. It does not execute
the new SF factory from an ordinary gameplay owner.
Earlier Korea/Russia GUI probes remain bounded GUI evidence, not end-to-end
acceptance of this installed profile.

All12 supplied `*SkillForce*.edf` candidates are inventoried with SHA-256,
counts and strides. The additional `ko-kr/SkillForce.edf` has different counts
and strides; it is not silently substituted for the root file. Equal counts
are not proof of official version attribution or complete compatibility.
No missing labels were padded or fabricated.

## Source component

`client455_skill_force_items.{h,cpp}` implements:

- owned root tables and ordinal lookup, reusing the previously verified EDF
  decoder from the current facade library;
- localized name/text overlays with target prefix-write/count-failure order;
- fresh SF160 record initialization and Create for subtypes0/1/2/3/5;
- borrowed raw table/name/index views, without converting them into legacy
  SF_DATA structs with a different layout;
- source-owned primary/auxiliary caches and concrete ownership-host methods;
- SF creation, registration, removal and clear, including duplicate requests
  producing separate payloads.

Subtype→root-table mapping is1→0,0→1,2→2,3→3,5→4, from the five query helpers
and their assembly offsets48/60/72/84/96. Type0 has serial/field8 equal to the
requested ordinal. Types1/5 OR both withF0000000. Types2/3 OR only the serial,
leave field8 unmasked and start level1. These are not masked24-bit IDs.
GetDTIndex reads the first DWORD of the borrowed row, as the target does;
it does not substitute the requested ordinal.

SF icon-board pointer108 starts null. The selected fresh factory path does
not call a live board. Its complete callbacks/recreate/gameplay methods remain
required. The source record's dispatch word is an owner token, never a
callable vtable address from the reference binary. It is not a complete
private C++ ABI.

## Verification

`RF455SkillForceItems.lib` contains the real SF source and087 ownership code.
The exact same separately compiled library is linked into a standalone EXE
and an own entry with the full current client object/library set. Both use
the existing source EDF decoder; no copied alternative decoder was added.

All1447 real rows create source payloads with independently checked subtype,
IDs/level, raw-row pointers, table index and32 name bytes. Each creates an owned
620-byte wrapper clone and releases origin/link in alternating orders through
the **concrete manager**. The final owner erases the actual payload/cache
entry. All1447 wrapper allocations are freed. Duplicate creation, invalid
subtypes and ordinal boundaries also pass. This is not a process-wide heap
or full-game resource accounting claim.

The five localized tables are compared byte-for-byte with an independent
Python oracle. Separate real Korean and Russian files verify failure and all
partial-write bytes. A short envelope is an explicit bounded failure;
unsafe target malformed/OOM domains are not declared equivalent.

```powershell
.\scripts\Invoke-Python.ps1 scripts/audit_client455_skill_force_items.py
.\scripts\Invoke-Python.ps1 scripts/probe_client455_skill_force_items.py
.\scripts\Invoke-Python.ps1 scripts/checkpoint_client455_skill_force_items.py
```

Production remains SHA-256
`82625b3ef5c237900146f65531a701a3451d3dbec292a65eef2ed5ece83df6f8`.
Its current gate is still `inventory/client455-hotbar-checkpoint.json`.
No production relink or unchanged GPU/Korea-startup/159k suite rerun was needed.
The new Taiwan early-startup scenario adds primary-profile coverage.

## Continuation — 089

Restore the other five payload factories (physical/Animus/Unit/UnitParts/Quest)
and their actual data readers/metadata, then real game-global manager and
CItemObject/CResObject/board/hover bindings. Root Item.edf does not begin with
a simple sequence of47 count/stride tables; the exploratory framing attempt
failed and is not a production parser. Inspect the target Item loader before
assuming offsets. Quest has additional sections beyond its first table.
Cached unported helpers/constructors are in ignored
`artifacts/client455-progress/skill-force088-followup.json`; validate new body
ranges before implementation.

The earlier four SF manager tables/XP/mastery, live UI/cooldown/recreate,
reload leaks/old pointer lifetime, ordinary Linker/5x10view/input/download,
oldbelt consumers,36 missing registry classes, full item/DB/trade protocols,
actual Tutorial/fourstage/Login/auth/gameplay and previous acceptance gaps
remain mandatory. Reload is explicitly rejected by the source owner until
the target lifetime is restored. M6/M6F/M7/M9 remain OPEN.
