#156: authenticated selection frame,lighting still incorrect

2026-11-10. Own SHA-256
68e02c3dcbf557c5a124e769c0c124884a71b50a367288b56efa3f6039807d55,
x86/base400000/entry17F710/2348032bytes. Gate:
inventory/client455-combat-transition-checkpoint.json PARTIAL.

Pinned44BE00 compares current612/previous613,fetches embedded5200 slots6/7
before mutations,andcalls animation virtual160 thenfade46E220,weapon first.
Mode0 usesanimation2/fade1,mode1 animation1/fade2. The old source's mounted
early return is absent in455. FPS is separately read after each animation,
x87-truncated toint32,andits lowBYTE passed asfade budget;zero becomes60.
The own port usescached typed wrappers andtheactual processor callback;
it doesnot call inherited legacySetAnimation onthe new wrapper.

Full disassembly/CFG for44BE00,46E220 and44BB90:225instructions across3functions,
equal byte regions onboth pins. Whole44BB90 isobserved,not fully ported:
extra action rewrite/savedframes/flags/priorstate fields remain open.
Raw private proof:combat-transition156-reference/session.json.

The next live failure moved fromCPlayer::SetAction tothe old Login dummy
equipment reader. Its active object accesses nowuse typed wrappers/meshes,
andphysical12slots. Login render weapon/shield fade accesses also migrated.
Its legacy scheduling/always-success shell isnot claimed ascomplete455policy.

Following live failures occurred insideDrawWithEffect455. Initially thiswas
misidentified asbasic payload type oroverlay604 producer failure because
different throw branches share one optimized throw site. Extra diagnostics
didnot fire for either condition. Expanded own stack andcomplete surrounding
assembly showed theactual message:grade materials notinitialized.
Temporary class/overlay diagnostics were removed after diagnosis.

Target53BBCD calls7E8ED0 afterLoadData andbefore created=1;53BC1F calls7E8F90
afterbase Destroy,before camera/UnloadData. These callsites matchboth pins.
The existing recoveredCreateEffect/DestroyEffect alreadyload/release grades,
butthe old Login nevercalled them. Its lifecycle nowcalls both. Actual
EffectEntityList.spt/MagicSptList.spt are staged. TheCreate tail isincorrectly
split inIDA andhas apositive-SP diagnostic;fullCreate proof isnot asserted.
Additional diagnostics:combat-transition156-reference/grade-startup-diagnostics.json.

An intermediate run timed out45seconds while traversing missing catalog
resources. Thiswasnot evidence ofa terminal hang. The owned live observation
budget increased to180seconds;regular nonlive observation remains20seconds.
No target success flags,materials orrender branches were forced.

Final live run:work/m9/68e02c3d/login-frame-live-taiwan001. Actual launcher
accepted,key16;game1/1→1/2 result0;1/8→1/9 payload178. Frame364 at8000ms
captured andnextRender returned,unhandled0. Image SHA:
09cbc54d41231924a8da3fee952b4402fb3ef9a1fcd0100e4d7fe0c959a8377f.
Character/equipment arevisible intheselection UI,butthecharacter isnearly
black. User explicitly observed animation andreported wronglighting;the
saved frame agrees. Animation playback isuser evidence,not aclaimed full
automated motion trace. Selection controls/enter-world were not exercised.

Nativework/m9/076242a0/player-owner-001 tests actual mounted/unchanged combat
transitions withreal weapon/shield andFPS lowBYTE/zero budgets. Three previous
assembled render PNGs remain equal155. Controlled camera/light andclone
cleanup limitations areunchanged. All fullclient acceptance requirements remain.

User-reported GameOverlay Store popup:Win10Pro22H2/19045,GameBar packageabsent,
GameDVR_Enabled1. Current-user AppCaptureEnabled andGameDVR_Enabled set0,
old values backedup privately. User confirmed popup disappeared after newrun.
Restore:scripts/Set-GameCapture.ps1 -Restore -BackupPath <saved backup>.
Microsoft reference:https://learn.microsoft.com/en-us/answers/questions/171242/windows-10-behaviour

Next157:trace actual lobby light lookup→CResObject material→CharIF light,
not thecontrolled white fixture. Before157 snapshots exact156,50files.
No original EXEs executed,server files/processes changed,credentials/key/raw
packets persisted orwholeclient copy. Both ownedIDA sessions saved/closed.
M6/M6F/M7/M9 OPEN;25%(20–35%) planning estimate unchanged,0/12full domains.
