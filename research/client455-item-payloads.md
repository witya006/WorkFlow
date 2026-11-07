# Item payloads089 — source readers and fresh factories

Update091: payload/SF/ownership backends now compile into the ordinary production
facade. Their unchanged real-data probes are rerun against those providers by
`probe_client455_item_object.py` and checked by the091 gate. Earlier separate
item-library runtime reports are historical; do not treat them as the current
canonical provider evidence. See `research/client455-item-object.md`.

Update090: the089 runtime checkpoint is historical after the ordinary common
base/dependency rebuild. The unchanged source was rerun in all four modes with
current dependencies; renewed runtime evidence is checked by
`inventory/client455-resource-object-checkpoint.json`. Static089 references
remain applicable. See `research/client455-resource-object.md` for current state.

2026-11-07. CLIENT ONLY. Status: **PARTIAL_SOURCE_RUNTIME**, not an ordinary
game integration or complete item subsystem. M6/M6F/M7/M9 remain OPEN.

The source manager now creates the five other fresh payload categories:
physical/Normal0, Animus2, Unit3, UnitParts4 and Quest5. Selector1 delegates
to the real SF owner from088. Other selector values use Normal0 as the target
factory does; selector6 is not a Gesture constructor in this factory.

## Reference and scope

Both immutable reference copies are x86, image base0x400000:

| Pin | SHA-256 |
|---|---|
| Current | b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b |
| Backup | 46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558 |

Selected50 function ranges match between pins. Exported19 assembly bodies
contain1796 actual instructions; noncontiguous EH instructions are pinned by
additional15-byte windows. These are static findings; reference EXEs were not
executed. Raw exports/session cleanup remain under ignored
`artifacts/client455-progress/item-payloads089-*`.

| RVA | Role |
|---|---|
| 0x1fee30 | Item table/localization outer loader |
| 0x1ffa00 / 0x1ffc10 | Description / dungeon records |
| 0x1fedd0 / 0x2006b0 | Section-tag mapping and registration |
| 0x42c490 / 0x4329b0 | Country Item branch flag, returns1 |
| 0x5fd60 / 0x61bc0 | Base / ordinary item Create |
| 0x5fe90 / 0x693e0 | Durability metadata / split-kind predicates |
| 0x1fc740 / 0x205d90 | Character / Quest table loaders |
| 0x206250 | Quest special-ID lookup |
| 0x1fa940 | Animus XP threshold lookup |

Full named ranges and input hashes are in
`inventory/client455-item-payloads-reference.json`.

## Confirmed formats and rules

The root Item payload is17563928 bytes with48 sections. Each section starts
with packed WORDtag/DWORDbytes/DWORDoffset. TagsF100..F12D map to0..45,
F12F maps46, F130 supplies47 work starts plus47 work counts; F12E is unmapped.
There are76049 rows in47 tables. Sections seek to offset+bytes+10; processed
length advances by bytes+10. Source code uses the existing EDF decoder.
Installed Taiwan profile selects the segmented branch through country vtable
slot160; the flat branch was checked using a generated envelope of the same
actual table bytes, not claimed as a separately supplied original file.

NDItem skips name blocks44/45 entirely. It copies64-byte names at row+8 up to
min(localizedCount,baseCount), skips extra names and leaves unnamed tail rows
unchanged. Unlike SF localization, a lower count is not a count-failure here.
Taiwan kind27 supplies32 names for31 rows. The following47 description groups
have count and repeated index/code/length/bytes records, then a dungeon group
with index/name64/length/bytes. Corpus results:

| Profile | Descriptions | Dungeons | Consumed payload | Ignored tail |
|---|---:|---:|---:|---:|
| zh-tw | 68084 | 100 | 9460191 | 0 |
| ko-kr | 63821 | 100 | 9972550 | 0 |
| ru-ru | 52255 | 0 | 9191029 | 11185 |

Zero dungeon count returns0 in the inner target loader, but the outer caller
ignores that value. Russian trailing bytes are likewise not parsed by this
path. Files and original configuration were not changed.

Root Character has7 tables, last648x95 at manager+36 for Animus XP. Lookup
scans81 rows per BYTE type for the first XP threshold greater than experience,
then uses the last row when nonzero XP has no greater threshold. Fresh Animus
Clear queries type255 before base data assignment; actual data yields null.
This is a real table lookup, not a placeholder returning zero.

Root Quest has12 tables; table7 contains2895x424 records at manager+84.
Special IDsF0000000..2 select count-9..count-7; F0000003..5 select
count-3..count-1. Further invalid IDs fail the table bound.

Fresh payload records preserve confirmed header/field initialization and
target sizes200/136/192/100/116. Header serial/field8 use the target unmasked
OR rules; data16 borrows an actual row. Physical durability/split/equipment
fields and Unit/Parts durability use target metadata offsets. Unwritten bytes
remain unwritten. Metadata may cross a declared stride while staying within
the actual table allocation; reads outside that owner throw an explicit bound
error and are not accepted as target failure parity. No selected real cases
required an out-of-owner read.

Quest name is **not** a plain row string: target RVA0x68450 invokes sentence
expansion through0x2057b0/0x205a70. The source accessor explicitly refuses this
unrestored provider. Quest localization/strings remain required work.

## Source/runtime evidence

`client455_item_payloads.h/cpp` implements source-owned data and fresh records,
and `RF455SourceItemManager::createPayload` registers successful owned payloads.
Dispatch words are opaque owner tokens, not callable target private vtables.
This is not the complete private C++ ABI or full derived gameplay methods.

The independent Python audit stages actual EDF files plus whole-table,
description and masked constructor/Create oracles. The x86/MT library
`RF455ItemPayloads.lib` contains ownership087, SF088 and payload089 sources.
Two own entries each pass standalone and against the normal client object set:

- New payload probe: all76049 item rows, all Quest12/Character7 frames,
  three complete localized table/description corpora,575 selected fresh
  factory cases,575 cloned wrappers with alternating release order through
  the concrete manager,99 Animus XP boundaries, real SF selector dispatch,
  invalid lookups, unknown section skip and bounded malformed inputs.
- Unchanged SF probe:1447 actual SF payloads and wrappers pass using the same
  new library, including localized prefix failure and last-owner erase.

All four executions naturally exit0. MAP files identify the exact source
library and existing EDF decoder provider. There were no compiler warnings in
the new source build. IDA877755f1 was saved/closed; session list is empty.

`inventory/client455-item-payloads-checkpoint.json` is the current bounded
source-runtime gate. The088 runtime gate is historical after the shared header
change; its static reference remains valid and its regression is covered here.

Ordinary production086 remains unchanged:
SHA82625b3ef5c237900146f65531a701a3451d3dbec292a65eef2ed5ece83df6f8,
x86,182 client/20 kernel/42 facade objects,0 unresolved. Its current gate is
`inventory/client455-hotbar-checkpoint.json`. No production relink, GPU suite,
startup or159k suite was repeated for this source-only unit.

## Required next work

1. Real game-global manager and CItemObject/CResObject lifecycle, typed
   board/hover owners; then ordinary Linker ownership and5x10 UI/input/use/
   cooldowns/download, replacing retired belt callers.
2. Full payload copy/mutation/network/UI methods, Gesture/Macro, Quest
   localization/sentence expansion, other Character consumers, reload/duplicate
   old-owner/OOM/unwind/unsafe domains and private ABI where actually required.
3. All prior gaps remain:36 absent board classes/Trunk, full item protocol,
   actual Tutorial/common UI/Avatar/QBI/fourstage/Login/auth/gameplay,
   remaining engine behavior and M6F/M7/M9 acceptance.

This restores another bounded dependency; it does not measure a percentage of
the complete client. No server source was modified, copied for development,
built or restored.
