# Typed equipment and default Avatar resources145

Creation/resource/payload binding now uses source-owned RF455EquipmentObject
and real455Item data. Six typed Avatar default slots are connected to the
ordinary registered-character receiver. Full CPlayerProc equipment,appearance,
animation/fade/draw and ordinary selection are still open.

References:x86/base0x400000;primarySHA256
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
secondary46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
18fullfunctions/630instructions/60positiveCFG blocks match both pins.
RTTI confirms CEquipObject,vtableAA8F64/Create140→46DB70.
Raw:artifacts/client455-progress/equipment145-reference/session.json.
RVA/region hashes:inventory/client455-equipment-reference.json.

## Recovered path

- Default setter RVA19DA0 accepts parts0..5,clears a prior nonempty wrapper,
  creates resources,creates a kind0 payload,and overwrites payload serial/field8
  with wrapper index/server index before attaching. These IDs omit the part tag.
- Getter1A000 checks wrapper index,not payload presence;the typed receiver
  separately checks the payload before reading its table index.
- CEquipObject Create6DB70 maps type9→46;core6BF60 strips the upper race nibble
  from the table index,reads meshDWORD72,sets index/serverF0000000|index/name.
- Race14 selects resource group6;race15 retains the raw mesh. Other races
  replace bits20..23 only for category0/8,user!=10,and meshpart!=7.
  Types8/46 force resource group5 even after the race14 branch.
- SetBone6D810 obtains the loaded mesh and bounding box;SetMesh6D860 makes
  original/current mesh pointers equal. GetMesh1E0A90 returns null after failed
  loading,unlike the older public getter that can retain an unloaded record.
  Both the load return value and loaded flag must succeed.
- Payload binding6C190 restores index/server index after the existing typed
  CItemObject clear/retain/name path. Resource pointers survive that clear.
- Resource.edf group0 player meshes are registered in manager5 alongside item
  meshes. This deliberate fold explains why equipment requests group5.

This class represents the selected behavior with own fields;it is not a claim
to reconstruct all644private bytes of CEquipObject. Known constructor race/type/
enable fields are represented;complete random/effect/fade state remains open.
Legacy ITEM_DATA/CEquipItem structures are not cast onto455rows. The old public
GetDefaultItem,UnsetDefaultItem and pointer-copy overload remain legacy;the
ordinary455receiver now explicitly uses GetDefaultItem455.

## Real execution

The actual full-object client probe loads the normal Item47+ND and Resource
catalog with the real Character/D3D9 owners.32 real model records load:
six standard parts for each of5 races,plus a weapon and shield. Geometry part
counts and original/current/bone mesh aliases match independently parsed files.
51 branch plans exercise race14/15,category0/8,user10,shieldpart7 andtype9alias.
30 ordinary Avatar.SetDefaultItem calls,slot bounds/replacement/failed lookup,
borrowed resources,source copy retain/release and final payload-count0 pass.
A real type6/index32 row requests mesh00A10320,absent from the catalog:metadata
creation succeeds with null mesh/bone pointers,matching the selected target path.

33 real material texture entries have live GPU surfaces with nonzero dimensions.
Exporter paths such as D:\... are stripped by the proven material loader;
Resource.edf supplies the actual texture directory. All33 requested DDS names
resolve through real RFT files. They are not unresolved required assets.
Complete texture appearance/animated draws are not claimed by this unit.

First staging1685refs/166.1MBlogical,+57,508,702newpoolbytes;repeats add0.
Those are owned shared assets,not links to the original installation. RFSINFO
files are small private copies. No full client-directory copy was made.

Own PE SHA2561a3553721149f8638812d636e2dfa3053d75b58a58c6310df72478050ab5670d,
x86/base400000/entry175F50/2299904bytes;182client/20kernels/link0/unresolved0.
Engine137 unchanged708c892e60c3bf7457389b40ac24b9a466958c9d232d9efaf497d1ac3232b870.
Production receiver's decoded CALL reaches the new default setter.
The affected account/registered suite passes on this PE;its fixture does not
load Item tables,so it is not proof of rendered equipped characters.
Fresh ordinary WinMain/Miles/Login frame70/3235ms/640x500 inspected:lobby and
waiting,unopened panels hidden,legacy label still present. No fatal exception.
This ordinary frame does not execute successful Login-response bootstrap.

Exact144 is preserved in before145(50files). Wider unchanged143/144 suites
were not rerun. IDA7dd394bb saved/closed. No reference EXE execution/server changes.

## Next146

Restore real CPlayerProc equipment create/get/remove and its thirteen slots,
then rematch/weapon/shield/state callbacks and typed render/animation consumers.
Only then accept full registered-character appearance and ordinary selection.
Raw145 includes diagnostic pcode for453030/453760/453550/4536C0/453730,
452FE0/453280 and Avatar4198D0/4199D0;their complete ASM/CFG/port is still needed.
Remaining class-skill/CharInfo/legacy-default APIs,bootstrap,world/gameplay,
failure/concurrency and full client-acceptance remain gaps. M6/M6F/M7/M9 OPEN.

Reproduce:audit_client455_equipment.py;prepare/build normal;normal-consumer
probe;link;probe_client455_equipment.py;affected account;fresh startup/own-entry/
Login frame+visual review;checkpoint_client455_equipment.py.
