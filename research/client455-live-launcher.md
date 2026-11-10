# Live login155 — partial integration,2026-11-10

Own PE SHA-256
`da42b501a1ab0c68c9c47a3cf2c51479b43f251623de1d6d6813a4c9d743e4ad`,
x86/base400000/entryRVA17F660/2347520bytes. Gate:
`inventory/client455-live-login-checkpoint.json` PARTIAL. Ordinary Taiwan Login
renders;the live equipped-selection route still has an unhandled exception.
No world entry orfull455client acceptance is claimed.

Actual user-started v0.4.0 exchange,using the dedicated test account:

| Observation | Result |
|---|---|
| Launcher6C/03→6C/04,TCP27831 | accepted;16-byte rf1:key |
| Own game request1/1,payload58 | Sent toTCP27830 through actual codec/transport |
| Reply1/2,payload12 | result0;client enters resource/bootstrap path |
| Request1/8→reply1/9 | Live reply178bytes,one active164-byte record after14-byte header |
| Later reply1/21 | payload1 observed;full behavior remains unverified |
| Live equipped selection | Fails inlegacy equipment getter during SetAction |

First live probe of154 timed out during cold loading at20seconds. A later154
run reached/rendered Login,while missing staged resources produced diagnostics.
Own observer candidate82808278 confirmed the accepted game reply andexposed
the rejected compact178-byte character frame. Candidate353b926b accepted the
short frame,then failed inGetNormalItem during registered equipment. These
are intermediate diagnostics,not accepted complete runtime baselines.

Pinned primarySHA b1b5…/x86/base400000,handler RVA16AE40:
56AE64 pushes1FAh for memcpy;56AEBA reads count byte1 anditerates164-byte
records. That506-byte internal copy is **not proof of a506-byte minimum wire
frame**. The live compatible server sends only active records. The own bounded
adapter validates14+164*count withcount<=3,then zero-pads absent unused slots
before the established internal decoder. It never reads beyond the packet.
Unsafe original overread behavior isnot claimed equivalent. Existing complete
record/actor evidence isunder registered140-reference/session.json.

The positive equipment branch56B2F3 calls462170. Complete462170 disassembly:
16instructions/1CFG block,confirmed equal onboth pinned binaries;it only writes
the incoming BYTE atoffset113(71h),without clamps orcallbacks. A new source
RF455BasicItem setter andtyped GetNormalItem455 replace the old incompatible
CNormalItem access. Private proof:live155-upgrade-reference/session.json.
Native boundaries0/1/2/3records,short active records,fragmented encrypted178,
andactual worn payload byte isolation pass. Three assembled render PNGs match154.

Final live run:work/m9/da42b501/login-frame-live-taiwan001. Registered processing
returns before later1/21;then the captured exception stack includes own RVA10B23
GetEquipItem@CPlayerProc and555FE SetAction@CPlayer,withAvatar/SetCombatMode
callers. Source points toSetAction_SwitchingCombatMode,which still obtains
legacy weapon/shield objects. Next:verify target transition andmigrate real
animation/fade totyped owners. Do not substitute inherited legacySetAnimation.

Ordinary nonlive Login:work/m9/da42b501/login-frame-taiwan001,visually inspected.
Actual primary owner probe:work/m9/ae382ba2/player-owner-001,exit0. Its controlled
camera/material/light andclone cleanup limitations remain unchanged from154.
Shared-pool resource selection retains only observed dependency archives and
textures;485unresolved catalog paths also fail lookup in the original files.
Their blocking relevance remains unestablished;the user reports a working
original world run. No whole client copy orstorage cleanup was performed.

Password/request/reply/account identifier/key were not logged orcommitted.
The93-byte private live handoff wasremoved in finally. Public traces retain
only message kinds/sizes/result flags. Original EXEs were never executed;
server files/processes were not changed. IDA session9079cdac saved/closed,list0.
This evidence concerns client interaction withGoMMO0.4.0;it doesnot make every
GoMMO behavior a pinned455specification. M6/M6F/M7/M9 remainOPEN.

# Live launcher route — initial evidence,historical

2026-11-10. User-started server reference is
`E:/RFOnlineTrash/rf455-v0.4.0`;client `E:/RFOnlineTrash/RFOnline`.
`inventory/client455-live-server.json` records read-only process/port/file evidence.
The original client matches primary pinned SHA b1b5febf…;the user reports actual
world entry. This is a user observation,not an agent-observed original game frame.

Installed launcher andbundle launcher both have SHA-256
`38e326588c37cdff5af4a34dfe3cee1aaa1c7aae3168b0ab8d2f9482b955451f`,
x64/image-base140000000. It is read/copied/analyzed,never executed bythe agent.
Private diagnostics areunder artifacts/client455-progress/live-launcher155-reference/.
They are pseudocode diagnostics,not complete assembly/CFG acceptance proof.

Observed launcher locations: EncodeAuthRequest RVA24C2C0,DecodeAuthReply24C7A0,
DecodeLoginKey24D0E0,FramerWrite24A9C0/Read24A720,ServerClient.Login290660,
v4x handoff Marshal13BE60. The prefix DWORD976316018 is ASCII `rf1:`,not `rf4:`.

- TCP27831:little-endian size includes4-byte RF-style header(category6C/kind).
- Auth request6C/03:three uint16-length UTF8strings(email,account,password),
  then one bool. Email/account selection uses presence of@ afterTrimSpace.
- Auth reply6C/04:bool,uint32account serial,identifier string,message string,
  optional encoded login key string. Login tests the accepted bool;serial0
  mustnotbe invented asan automatic failure. No actual account values are stored.
- rf1:key decodes32hex digits to16bytes. Live test returnedaccepted=true and
  avalid16-byte key. Public reportcontains only flags/sizes/kinds,not secrets.
- TCP27830 is the game endpoint. Own WinMain connected toit andpassed through
  engine/Miles;thisdoesnot prove own account/world-entry gameplay authentication.
- For455 the launcher writes93-byte System/DefaultSet.tmp via v4x Marshal:
  endpoint/IP,identifier,serial,4keyDWORDs,accounttype,personal,premium,nation.
  It doesnot merely supply the two console credential arguments.

Python wire probe has small valid/malformed examples andan actual successful
local exchange. Credentials entered viahidden console input;nonein source,
commandline,Git orreport. Raw authentication packets,key andidentifier were
discarded. Next:marshal the handoff into an isolated own run with cleanup,
observe actual world-entry requests/replies without dumping account data.
Full server protocol compatibility andfull ownRFauthentication remain open.
