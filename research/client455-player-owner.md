# Embedded player owner154 — partial integration

2026-11-10. CLIENT ONLY. Own x86 RF_Online.bin:
`31d24ab9481f56218431661815cd58077b59fae7d79ad123dc0c5c8758bd5426`,
entry RVA `17F430`, 2,347,008 bytes. Build182client/67engine/20kernels,
link unresolved0. Gate: `inventory/client455-player-owner-checkpoint.json`.
Full appearance/selection/world/gameplay and M6F/M7/M9 remain OPEN.

## Reference and implemented path

Both x86/image-base400000 pins are unchanged:
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`
and `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
Three new complete body sets contain24functions/1859instructions/91positiveCFG
blocks and match both pins. Earlier controller/render/conditions/frame proof is
reused,not represented as a new full-client test suite.

- CPlayer ctor RVA4A750 establishes embedded/current processor andactor links.
- CPlayerProc Render RVA50330 andAnimation50BD0 now reach the typed12-slot
  source owner from ordinary numeric equipment APIs. Actual actor20x30part
  caches,mesh rematch/ANI/frame,pose restore,grade,position/yaw/scale are used.
- Base skill callback43E600 is genuinely empty. Avatar RVA1A060 reaches real
  skillboard7/490EB0 andits actual packs. SF RVA63740 writes flag101;63780
  wraps BYTE(level+flag101) before clamp7;subtype2 returns1 first.
- Avatar PutOff RVA19BB0 restores default wrappers forparts0..4. Cloak8/Siege46
  returnfalse AFTER removal ifthe special skillpack2slot0/1 ismissing.

Source uses real CPlayer/Avatar/CSkillBoard owners,not recorder callbacks or
casts of old CNormalItem/ITEM_DATA. A CPlayerProc state owns12typed objects;
its condition adapter supplies actual Premium/bonus/avatar andskill routes.
Selected totals are explicitly transferred to old source fields while their
remaining consumers are migrated. Full455UI metrics/layout are not claimed.

## Copy semantics and limits

CPlayerProc member copy RVA4A40 allocates independent12member storage while
base RVA5A40 retains old actor/bone/box links. Player403D70 also retains the
old currentProc pointer. CEquip4042D0/CMesh404F40/CItem405D30 member copy does
not rand orAddRef. This differs from retained queue527E70,which constructs a
wrapper,consumes rand andretains the payload. Source policies now distinguish
these routes;the compile failure C2280 is resolved without a shared owned pointer.

Full Character/Avatar clone lifecycle is NOT accepted. The legacy Character
copy still aliases three separately deleted pointers. The probe observes those
aliases,then detaches only its fixture copy before destruction. Likewise the
populated processor-copy observation compensates payload references only AFTER
observing the target's no-retain copy. These cleanup adaptations are not a
production fix orproof of safe complete clone/destruction behavior.

## Actual execution

Own full-object entry `work/m9/5544e512/player-owner-001` exits0:

- Numeric puton/base putoff reach the actual embedded controller;19draws and
  12,657visible model pixels. Removing the shirt changes3,752pixels;replacement
  restores the exact dressed PNG. Camera andmaterial/light are controlled;
  model transforms come from actual frame/part caches,not identity overrides.
- Actual Avatar removal restores its typed default garment/shared payload.
- A controlled option in owned metadata exercises equipment→Avatar→two actual
  skill packs→typed SF payload→actual icon label;removal reverses it.
- Production cloak modes start actual actor/Spine magic andMiles WAV using the
  equipment position. Missing specialskill slot yields the measured false-after-
  detach outcome. Full populated specialskill unlink remains explicitly unported.
- Payload manager returns0 after owned actor/pack cleanup. Pack insertion was
  used directly;cleanup follows that allocation route,not uninitialised fullUI.

Six existing queue/base/overlay render PNG match153;new render staging pool0.
Final primary entry staged1761asset paths/255,888,337logical bytes from the shared
owned pool;104,982new pool bytes. No whole-client copy ordeletion was performed.

Ordinary Taiwan WinMain/Create/Login pass on exact own31d24ab9. The viewed Login
capture isframe195/3000ms,640x500,lobby/waiting withlegacyBeta0.738. Seven first-
chance exceptions(6C++/1threadname),0unhandled. The prior Korea check stopped at
the real single-instance policy whilethe user had the original client open;
Taiwan's existing target policy allows that coexistence. No policy was bypassed.
Affected account receiver still applies3actual Avatar records;not game auth.

The user started v0.4.0 andconfirmed entering itsworld withthe original client.
Read-only process/port/hash audit confirms that bundle,client primary pin and
matching launcher. Own Taiwan WinMain also establishes actualTCP27830,then
engine/Miles. Launcher-only6C/03→6C/04 test auth accepted andreturned a16-byte
rf1:key. Credentials,key andraw packets are not persisted. Own RF game auth is
still open. GoMMO behavior is separate from the pinned455client specification.

## Next required integration

Use live launcher handoff in an isolated own runtime,then observe actual client
world-entry/registered/bootstrap state. Finish typed registered appearance,
legacy equipment consumers,ordinary actor animation/material/lifecycle,full
UI/selection and remaining bootstrap. Slot9Siege/unit flags,nonzero shared
particles,full shadow/clone/skill-window lifecycles andall original M9 gaps remain.
No reference input EXE was executed orserver source/config changed.
