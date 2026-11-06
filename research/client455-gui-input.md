# Client455 base GUI input — участок068

2026-11-07. Base mouse/key/focus/queue and main-list container contracts in ordinary
source providers. FullGUI/IME/other layers/gameplay remain OPEN. No reference EXE
executed,no server source modified.

Pins:x86/base400000,currentSHA256
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`,
backup `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
34ranges/onebase-vtableprefix equal;15complete instruction dumps retained.
IDA6eadfaf3 saved/closed,idb_list0. Addresses below are RVA.

## Mouse and modal state

Input `226B90` has a separate DWORD inputflag at target+88,default1,apart from
Active+52. Existing detected object prevents another selection. Show/bounds are
inclusive through `227440`. Previous hover/pressed state routes to live objects.
Parent `20C850` traverses main list backwards before calling base input.

Event7 is double stroke,**right stroke is8**. Double threshold is300ms inclusive
with DWORD wrap. Only same last object queries clock for comparison;then every
accepted left stroke queries again for timestamp. Double clears last object;
right stroke also clears it and records a separate right-pressed pointer. Right
held suppresses ordinary hover/move branch. Disabled mouse sends only5/6.
Tooltip clears on6/1/8,not7. Source replay providers restore timeGetTime/GetKeyState.

Modal pointer at VA `0x102CF4C` is set by `2277D0`:always call previous object's virtual
offset100 before assigning new pointer,including same/null replacement. Base
callback is the empty `104CF0`;source API calls it CloseMouseModal455. Outside
left stroke calls callback and consumes the stroke without activating underlying
object. Caller23DEB0 expands/removes a dropdown;do not misidentify it as inputfield.
Popup class/private ownership/full callers remain unported.

## Keyboard,focus and queue

MessageProc `227370` returns0 unless focused predicate true. Handles WM_KEYDOWN
and WM_CHAR only,with Ctrl17/Alt18 highbit filtering and all byte keys. Key229
uses `2271E0`'s fixed QWERTY table:

| Full arithmetic high16 scan | Bytes |
|---|---|
| 16–25 | QWERTYUIOP |
| 30–38 | ASDFGHJKL |
| 44–50 | ZXCVBNM |
| Other,including repeat/extended bits | FF |

It does not mask to scan byte or use current keyboard-layout MapVirtualKey.
Modifier queries short circuit in Ctrl/Alt order. Predicate ignores disabled
state,so a disabled-but-already-focused object still forwards base key messages.

Focus `2275C0` returns early for alreadyfocused,otherwise emits old blur71 before
checking new eligibility. Invalid new candidate can leave old focus pointer while
emitting blur. Success sets pointer and70. Predicate `227570` requires enablefocus,
show,active and matching pointer. Kill `227650` acts only when predicate is true;
hidden/inactive stale pointer can persist. DisableFocus/InActive kill before flag
change. Destructor clears matching global references without focus callback.
Other private destructor registry at22ACB0/3B4840 remains OPEN.

Queue `22AE80` dedups by source,id,**BYTEkey**,ignoring handler/value. Record is
36bytes,bytekey+10,DWORDvalue+32. `22AF90` retains mouse/motion/key/scroll/select/
dialog/window routes,adds generic focus70–79 and value80–89;>=90ignored. Source
named focus/value interfaces preserve payloads,not original private C++ symbols.
Full concrete observers and reentrant/OOM/invalid-pointer domains remain open.

## Container and scrollbar correction

Container ctor20BDE0 disables focus;Add20BFA0 rejects null/duplicates,propagates
Show then appends main list at96.20C040 prepends.20D3D0/20D650 are list insertion
and20DE40/20E010 are find helpers,**not parent observer propagation**.
Target also owns lists108/120;their APIs/render use are not yet ported.

Remove20C480 returns0 fornull,1 fornonnull even nonmember,kills eligible focus,
removes from target'sthree lists. It retains mouse references to still-live
objects. RemoveAll20C4F0 kills eligible focus in main list then clears allthree.
Source currently implements main list;indexed compatibility API remains separate.

This corrects065:ordinary238EE0 binds composite thumb only,239590 registers self
only,227070 emits solely to direct observer. There is no automatic base arrow
binding. Removed the owned arrow adapter instead of making original behavior
friendlier. EX23A750 hasfour explicit registrations and retains them. Any actual
ordinary caller-specific arrow registration must be established separately.
Redundant manual Show bridges removed now genericAdd inherits visibility.

Mouse device `3AF900` retains left/right priority and adds middle key3(bit2).
Existing drag/move behavior agrees with target helpers.

## Implementation and verification

New `client455_gui_input.{h,cpp}` and object/container/queue inc files are applied
by generator to actual GUIObject/Container/EventProc/MouseDev. Public source APIs
avoid private-memory overlays. All182client units rebuilt;28facade units now.

Own probe SHA256
`d424f606ec491232aba552e53311e96f79ca76802b636d15120316a62c6a4082`,
x86/entryE4480,Ko/Ru naturalexit0. Tests use real MouseDev,GUIObject/Container,
queue and observer interfaces. Cover300/301/wrap/clockcount,right8/modal callbacks,
inputflags,visibility/duplicates/front/Removealive refs,focus order/predicates,
Ctrl/Alt/229,keydedup,focus/value payloads,middle and ordinary-unbound versus
EX-bound actual mouse path. No world/input-text provider stand-in is treated as
fullGUI completion.

Fixture issues corrected:baseheader defines `parent (this)`,so local renamed
holder. Tutorial-board061 fixture's initial-hidden assumption was invalid after
screen.Add455 inherits visibility;hide explicitly afterAdd to test hidden branch.
Production Add was not rolled back. Other preAdd-hidden legacy callers still
require comparison with target.

Production SHA256
`de76223c075a2af2d164f6486e8ceed49d34ebf28153bc7c12a85c4e187be60a`,
x86/base400000/entry14F4A0,2036736bytes,182client/20kernel/28facade,0unresolved.
Normal production map retains ordinary input/key/focus/queue/Add/Remove providers.
Generator idempotent;engine/canonical20kernels unchanged.

Affected scrollbar/EX-Var/minimap/textboard/metrics/font/modal/tutorial-board
probes passed.40GPU readback hashes agree with prior visually inspected frames;
no visual changes claimed. Exact own WinMain/TCPfixture/engine/D3D/Character/
existingCreate1 passed,stopped before game loop. Trace also records extra
firstchance40080201 viaKernelBase,cause unknown;no full failure-equivalence claim.
Eight scoped gates PARTIAL;no unchanged large runtime/particle suite rerun.

Evidence: `inventory/client455-gui-input-{reference,native,checkpoint}.json`;
raw ignored `artifacts/client455-tutorial/gui-*068.json`;
labs `work/m9/d424f606/input-{ko-kr,ru-ru}-001`.

Next069:production message sizing/rich callers,then actual fullbriefing and
Tutorial/Avatar/world/fourstage. Remaining two lists/layers,private destructor,
popup/GUIInput/IME/focus/value consumers and downstream7/8game actions remain
mandatory M6F/M9 gaps. Fullminimap/camera/auth/gameplay still OPEN;M8 separate.
