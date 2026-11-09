# Nuclear116 — ordinary receiver, selected item use and stage ownership

**PARTIAL. M6/M6F/M7/M9 OPEN.** Current gate is
`inventory/client455-nuclear-receiver-checkpoint.json`;115 runtime gate is historical.
The ordinary client now registers and dispatches the actual Nuclear group60
processor. This does not accept complete authentication/gameplay, inventory,
world geometry, full stage lifecycle or complete effect/texture ownership.

## Reference evidence and corrected meanings

Both pinned x86455 images/base0x400000 match config/client-target.json.
Primary SHA-256 is b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b.
44 body ranges/42 complete assembly listings/2473 instructions and one separate
Init EH range agree between pins.18 new assembly listings contain1354 instructions;
the112 protocol/110 hover/115 status-mapping evidence is reused after hash checks.
Raw data: artifacts/client455-progress/nuclear116-reference.json and
nuclear116-session.json. Owned IDAe7a74d3f was saved/closed; supervisor count0.
Input EXEs were never executed; no server changes or builds occurred.

Earlier112 prose called the result2 path an inventory opening/nuclear dialog.
That interpretation was incorrect. The current assembly/getter/callback evidence
replaces that interpretation; historical raw evidence remains intact.

| Target RVA | Confirmed behavior |
| --- | --- |
| 0x1c59d0 | Select MiniMap marker at this+0x2dc4+index×540, then70bf30 |
| 0x30bf30 | Show/hide actual marker; already pinned in114, not a separate dialog |
| 0xb950 | Original selected object getter40b950 reads DWORD232 |
| 0x20ec0 / 0x12000 | Null-aware board payload getter, then DWORD584 |
| 0xb200 | Payload serial DWORD4; sender uses low WORD |
| 0x1b350 | Raw race/gender BYTE17804 divided by2 |
| 0x1c630 | Level DWORD17808 |
| 0x70690 | Original storage-board BYTE229, not inventory visibility |
| 0xfd860 | Board selector0..55; index2 maps to board1 |
| 0xfad00 | CObjectBoard UI_UseResult: virtual124, then conditional operation clear |
| 0x75a90 | Actual CInventoryBoard callback from vtable AAC50C+124 |
| 0x757d0 | Category33 nuclear completion callback is empty |
| 0x75e10 / 0x17140 | Player+17848 use record: only DWORD4 becomesFFFFFFFF |
| 0xfe2b0 / 0xfe2f0 | Actual hover pointer244, or nonempty backup252 |
| 0xfe330 / 0xfe020 | Clear operation and common C1A cancellation, even empty cursor |
| 0x145d00 / 0x1496d0 | MainGame Init binds owned pointer188; Destroy deletes it if created |

All addresses in this table are RVAs. Exact full ranges, sizes, hashes, inventory
RTTI/vtable identity and decoded CALL edges are in the reference report. Pseudocode
argument labels/call markers alone were insufficient: assembly established the
member selection, stack arguments and real call instructions.

## Restored ordinary paths

`CNetworkMgr::Create` constructs a real CNetMsgProcessor_Nuclear derived from the
existing base. Ordinary DataAnalysis/AnalysisServerPacket routes group60 to its
virtual callback. All9 payload layouts use the bounded decoder112. Unknown
opcodes retain the target diagnostic and false return. Own short/null boundaries
reject before mutation; target unchecked malformed-input behavior is unaccepted.

| Opcode | Restored ordered operations |
| --- | --- |
| 0 | Blocked: clear aim, hide status-selected marker, CE6; otherwise result branches below |
| 3 | Request off; set local-race position from payload+4/index16; show marker via lookup |
| 4 | Request off; add; foreign race countdown9; notify C15 only above level24 |
| 5 | Request off; launch using index BYTE4, ignoring payload bytes1..3 |
| 6 | Request off; pending0; radar off; hide local-race marker; impact |
| 7 | Request off; packed position update; radar on |
| 8 / 9 | Hide local-race marker then remove; request flag is retained |
| 10 | Count>9 ignores immediately; otherwise ResetRecords then ClearAll; hide/add packed14 rows; copy position only when all3 components are nonzero |

Unblocked result0 preserves CE7/request-off/arm behavior, including repeated CE7
without restarting an already-pending effect. Result1 reads **GetOrgObject**,
not hover/backup. A present payload supplies serial WORD; request becomes true
before the existing base sends group60/opcode1/payload2. No payload sends nothing.
Error results preserve the actual CE8..CF0/16C/CE6 mapping and request-off order.

Result2 checks original storage board0. It calls the real source inventory
UI_UseResult(TRUE), then shows the status-selected MiniMap marker. The selected
category33 typed inventory callback is restored: its nuclear-specific body is
empty, then the selected player-use DWORD4 is reset. It does **not** consume the
item or clear a620-byte wrapper. Other typed inventory-use categories remain
explicitly unsupported here and require their full implementations.

The base use-result now clears operation only when hover/backup is absent.
A retained backup therefore preserves the original operation and aiming state.
Without a backup, common SetHoverObject cancellation emits C1A and clears aiming
even when there is no object on the cursor. The former typed-wrapper-only hook
missed that valid empty-cursor path; ordinary SetHoverObject now calls the common
confirmed cancellation before dispatching to either existing source path.

## Ownership and scope limits

MainGame owns a unique_ptr registry allocated/bound by Init, and releases it from
Destroy at the legacy manager teardown boundary. Its deleting destructor also
releases an uncreated own stage. MainApp's previous static holder is removed;
compatibility accessors now return the bound stage's registry/aiming member.
Ordinary late Render continues to update ordered records and then aiming.
These edges and the actual Nuclear vtable slot4 were decoded from the own PE.
Launch/impact/notification/lookup/marker/decoder consumers are now retained there.

Full stage lifetime is **not** accepted: target early Destroy skips cleanup when
uncreated and its global registry pointer remains dangling after normal deletion.
Own uncreated cleanup/unbinding explicitly avoids that unsafe domain; it is not
evidence of target leak/invalid-pointer equivalence. Complete stage factories,
Create/auth/reset/reentry/world teardown still require acceptance. The full
player-use record and its other writers are also open; only its confirmed clear
lane is owned here, with an explicit unknown-before-producer state.

## Current validation

Own PE SHA-256:
`c67a3154fc99f21044d186393a1d66ac83ace1a06a6f412d1352483e1ef5cdda`.
x86/base400000,2211840 bytes,entry RVA164370. Build182 client/20 kernel/69 facade,
unresolved0; exact own PE reaches existing Create with EAX1. Complete game startup
is still unaccepted. Engine67 remains
546a7529b51139e856b1a108fcad7849c14b2d00563b7abbfdcc8db10026fa5a.

- Receiver101: work/m9/db12263f/nuclear-receiver-001. A CNG AES192 packet enters
  the actual receive ring and decrypts/dispatches to the normal processor. The
  low-WORD serial's6-byte plaintext becomes a19-byte encrypted send frame equal
  to independent Windows CNG. A different real backup payload does not change
  the original serial. Empty/nonempty backup completion, blocked/error/repeated
  results and all9 opcode contracts are exercised with actual Avatar, EDF item,
  inventory board/socket, MiniMap, BSP, archived effects and Miles providers.
- Registry109: work/m9/440c1dd3/nuclear-registry-001. Shared timer and clearing
  behavior remain, including the two real1050ms waits and clock survival.
- Aiming30: work/m9/fd28f6f7/nuclear-aiming-001. The former standalone fixture
  now constructs the real offline network provider/MainGame owner; world/effect
  scope still balances785169 bytes before/after. Missing-effect sound quirk kept.
- Marker702/6GPU: work/m9/2142407c/nuclear-minimap-001. Linker header compatibility
  compiles; full Linker runtime was not repeated.
- Messages83/5GPU: work/m9/7d269cfc/message-output-001.

All20 current GPU frames were viewed;11 marker/message frames exactly match115.
Receiver messages are delivered in a batch; its direct center draw shows overlap
at initial positions without normal frame layout updates. C1A is readable in chat;
this lab does not accept complete frame/layout behavior. Effects ultimately drain
and the final receiver image has no remaining effect/UI pixels. No original455
executable capture or complete world trajectory/quake/compositing comparison exists.

Both nuclear labs retain20 R3T release warnings on teardown. Full texture lifetime
and registry memory balance remain unproven. Broad159k/world/audio/other GUI suites
were not rerun. Exact115 working-report bytes were archived before source changes.
Early lab failures (missing board provider, encrypted-vs-plain send expectation,
and the old aiming fixture's missing network provider) remain in work/m9; current
reports bind only successful final source/probe hashes.

## Next

117: restore real worldgeometry588 loader/producer7C9240 and ordinary MiniMap
geometry, which is still a supplied lab input. Investigate the20 R3T release
warnings using actual455 texture ownership before changing or suppressing them.
Continue full stage/input/action/inventory/auth/protocol/world acceptance as in
docs/client-acceptance.md; this selected integration does not complete M9.
