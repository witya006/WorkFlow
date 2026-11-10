# Character tables143: ordinary manager integration

Scope is client only. Selected loaders and lookups are source and connected to
the ordinary CCharacterDataMgr. Full character classes, appearance, skill-board
population, Login bootstrap and selection are still open.

Reference x86/base0x400000:
- Primary SHA256 b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b.
- Secondary SHA256 46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
- 15 full functions,1737 instructions,193 positive CFG blocks including tails;
  selected regions match both pins. RVA/region hashes are in the reference JSON.
- Raw: artifacts/client455-progress/character-tables143-reference/session.json.

Target owners: LoadData RVA1FB330;board creation1FB390;Player1FB4F0;
SF base1FBC80/localization1FB670;Store1FBD90;CharacterND1FC260/base1FC740;
classByCode1FAF70/codecompare1FAFE0/classByIndex1FB020. Helpers count1FA7A0/
33550 and Read1EE900 were inspected to establish short-read semantics.

The normal manager loads PlayerCharacter,SkillForce,Store,Character in that
order. Failed localizations do not prevent the later loaders or board creation.
The exact own production CALLs are decoded and checked by the checkpoint.
Store uses npcShop from the actual12-byte world-entry reply:flag6/WORD7.
Store[-1/default or _selector].edf uses fixed2076-byte records;NDStore[W].edf
does not inherit the selector suffix. Descriptions are owned separately;
serialized pointer lane1868 is opaque,never cast to a legacy/private pointer.

Character.edf has7 tables(counts165,8,1999,36,324,81,648). ND overlays first4:
class name32@112/text1024@508;three names32@1/33/65 in table1;
monster name32@8;table3 name32@12. Last-byte truncation also removes a lead
DBCS byte at position30. Declared extra rows skip1056/32/32 bytes respectively;
the second group deliberately does not skip96 per extra row.

Important target quirk:Read1EE900 on short input leaves destination and cursor
unchanged;CharacterND ignores its return and loops the base count. Real Korean
and Russian inputs therefore yield203/682 ignored read failures. Preserve this
behavior rather than min(counts),repair or resynchronization. Initial too-short
header/unsafe allocations/out-of-range seeks remain outside accepted coverage.

Class lookup is exact-case string@12 or DWORD index@4,first matching row.
The new typed accessor returns source-owned spans;no cast to CPlayerClass.
Skill and force boards really allocate7/6 packs of20 sockets,12/24 masteries,
100 SF entries. Existing legacy SF counts stay0:their SF_DATA consumers and
class-skill population are not migrated by this unit.

Validation:all14 table counts/strides/CRCs and Store description bytes match
independent Python oracles in the full-object normal-client probe. Every165
class row lookup,case sensitivity/missing/null,5 real typed SF wrappers with
clone/refcount/release,and real board dimensions pass in each case.

| Input | Player | SF localization | Store localization | Character |
|---|---|---|---|---|
| ko default |pass|false,prefix retained|pass|pass,203 ignored reads|
| zh default |pass|pass|false,base retained|pass|
| ru default |pass|false,prefix retained|false,base retained|pass,682 ignored reads|
| zh Store_1 |pass|pass|pass|pass|
| ko with changed DBCS name |pass|false|pass|pass,lead-byte trim verified|

The last row is a deliberately modified name fixture,not another stock locale.
There are5 Player records,1595 default/1651 Store_1 records,and SF tables contain
88/84/504/60/711 rows. False localization results are checked,not hidden.

Own PE b41d50ffb5001c04a54dd0f16bd471c2bc0168e4b8757a52eca7a41067e0b4ec,
x86/base400000/entry174CD0,2293248bytes;182client/20kernels/link0/unresolved0.
Engine137 remains708c892e60c3bf7457389b40ac24b9a466958c9d232d9efaf497d1ac3232b870.
Fresh ordinary WinMain/Miles/Login frame70/3219ms/640x500 was inspected:lobby
and waiting dialog,unopened panels hidden;legacy label remains. This run does
not execute a successful Login response bootstrap. Input EXEs never executed.

Only targeted affected evidence was rerun. Exact142 is preserved in before143;
its item/resource/account suites are historical,not freshly accepted on143.
Shared staging35refs/35.2MBlogical,newpool8.51MB/adopt4.57MB;no installed-client
copy and no original hardlinks. IDA5fe0894d saved/closed/list0.

Next144:actual Avatar class setters and names,then equipment/appearance and
remaining bootstrap/selection. Old CharInfo labels4/5 mean different things
from455;do not write455indices into the old14-label window. Other NPC/monster/
player/skill typed consumers,remaining bootstrap tables/lifetimes/unsafe domains
and full client-acceptance remain open. M6/M6F/M7/M9 OPEN;no renderer modernization.
NDW filename forms are checked as helpers only;uninstalled NDW corpora and the
complete country policy selecting wide variants are not accepted by this unit.

Reproduce: audit_client455_character_tables.py;prepare/build normal;
probe_client455_normal_consumers.py;link normal;probe_client455_character_tables.py;
fresh startup/own-entry/Login frame+visual review;checkpoint_client455_character_tables.py.
