# Live launcher route — initial evidence

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
