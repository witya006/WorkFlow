# Avatar class writers144

Selected class index/name writers now use the real455class table in the ordinary
client. Full class-skill creation,455CharInfo layout, equipment/appearance and
selection are still open. This is a partial client step,not M9 acceptance.

References: x86/base0x400000;primary SHA256
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
secondary46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
14 complete functions/460instructions/76positive CFG blocks match both pins.
Raw:artifacts/client455-progress/avatar-classes144-reference/session.json.
All RVA/region hashes:inventory/client455-avatar-classes-reference.json.

- RVA12050 numeric setter writes one of4 indices without validating it.
- RVA12140 string setter requires an exact-case class-code lookup first.
- Both preserve the class-skill callback callsite when board7 exists. Its full
  production implementation remains unported;accepted native cases use the
  board-absent branch,as in the registered-character Login fixture.
- Slot0,slot1==-1:numeric setter updates only label4;string setter updates label4
  then stored base name/label5. These writers must not be folded together.
- Slot0,slot1!=-1:stored base name/label5 only.
- Slot1:stored base name/label5 from class0,then label4 from class1.
- Slots2/3:indices and callback only,no name changes.
- RVA12580 only copies the stored name if both row and global CharInfo exist;
  RVA12640 updates label4 without changing the Avatar stored name.
- Copy1E5920 zeroes the entire32-byte destination and copies at most31 bytes.
- GetIndex12280,level122C0,initial-class123A0,availability126C0 are confirmed.
- UI setter263370 accepts indices0..22 and forwards to a real text widget.

Source remains ordinary CAvatar members,not a copied private binary object.
The existing CharInfo Level/Guild/Attribute fields have different indices. A
separate23-widget value owner receives455class writes,avoiding corrupting old
fields. Its455layout/rendering and other field writers are explicitly pending;
this unit does not make class labels visible in the old window.

Native verification uses the real compiled Avatar,CharacterDataMgr and text
widgets with Character.edf/NDCharacter for ko,zh,ru. All165 real class indices
and complete localized class-table CRCs match independent Python oracles.
Representative numeric/string/slot1/slots2–3/unknown-index/null/missing-code,
UI-absent retention,31-byte truncation/whole-destination zeroing,23-field bounds
and preservation of legacy Level/Guild/Attribute widgets pass.
The probe exposes protected methods through a derived access-only class;
production headers were not made public for testing.

Affected account/registered receiver suite was also rerun with real class data:
actual1/8 request and encrypted1/9 reply/fragment-wrap apply3 real class indices
to3 actual Avatar objects. UI is absent,so stored names correctly stay empty.
The production registered receiver's decoded CALL reaches the new string setter.
Full real authentication and appearance/selection are not implied by this test.

Own RF_Online.bin SHA256
ea25eea5222039073ddf7e7823219336080ae298fd78afa0e99b38a65584f812,
x86/base400000/entry174FC0/2294784bytes;182client/20kernels/link0/unresolved0.
SetClassName and SetAdvancedClassName455 are inlined in ordinary production
consumers;the gate does not require nonexistent standalone MAP symbols for them.
Engine137 unchanged708c892e60c3bf7457389b40ac24b9a466958c9d232d9efaf497d1ac3232b870.
Fresh ordinary WinMain/Miles/Login frame70/3219ms/640x500 inspected:lobby,
waiting,unopened panels hidden;legacy label remains. This ordinary run did not
execute a successful Login response/bootstrap. No input EXE was executed.

Exact143 runtime/evidence saved in before144(49files). Unaffected143 bulk table
and graphics suites were not repeated. Class probes staged6 asset references/
3.04MB logical,new pool0;account reused existing shared files. IDA01ef697a
saved/closed. M6/M6F/M7/M9 OPEN;estimate25%(20–35%) unchanged.

Next145:real typed equipment/default items and registered-character appearance;
then remaining bootstrap and ordinary selection. Full class-skill callback,
23-field window layout/other UI writers,all client acceptance and unsafe/
concurrent/failure variants remain recorded gaps. No server work.

Reproduce:audit_client455_avatar_classes.py;prepare/build normal;normal-consumer
probe;link;probe_client455_avatar_classes.py;probe_client455_account.py;fresh
startup/own-entry/Login+visual review;checkpoint_client455_avatar_classes.py.
