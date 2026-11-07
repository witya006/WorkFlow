# Canonical storage and board identities — 085

2026-11-07. Client only. **PARTIAL**: the source now uses the measured455
identities for its17 existing target-named board classes. This is not the full
53-object factory, item protocol, hotbar, trade or Tutorial. M6/M6F/M7/M9 are open.

## Evidence and scope

The unchanged x86/image-base `0x400000` pins are:

- current SHA-256 `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
- backup SHA-256 `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.

The53 target constructor/vptr/RTTI identities and the92 matching body ranges
from084 are revalidated in the new checkpoint. Ten additional selected body
ranges match both pins. The physical-item predicate at VA `4FEF50` / RVA `FEF50`
has25 actual complete assembly instructions: it accepts **0,1,5**. Ordinary
ReturnItemToItemBoard (`4FEF90` / `FEF90`) calls it before looking up the board.
GetBoard (`4FD860` / `FD860`) accepts IDs below56 and aliases public2 to1.
GetObject (`4FD8E0` / `FD8E0`) instead uses the physical table below16 without
that alias. The source already retained this latter distinction.

Raw complete pseudocode/guard assembly and session evidence are saved in
`artifacts/client455-progress/storage085-{reference,session}.json`. Selected
transaction-queue pseudocode was retained for later work; the queue was **not**
implemented in this unit. IDA session `64b119a2` was saved/closed; list count0.
No reference EXE ran or server file was modified/built.

## Source changes

`client455_storage.h` defines the canonical logical storage identities and the
physical-item predicate. `prepare_client455_normal.py` derives five changed
legacy source copies without recoding the originals:

- `network/protocol/characterdb.h`: Inventory0, Equipment1, Embellishment2,
  Force3, Animus4, Trunk5, Linker6. Counts remain7 logical positions/6 storage
  entries. This change **does not certify the legacy packet or DB-record layout**.
- `define.h`: board table capacity56. Existing classes occupy their target IDs;
  Trunk and the other35 target classes are still absent from this factory.
- `cboardmanager.cpp/.h`: remove construction of the obsolete separate
  CBeltBoard; the17 remaining actual classes now register at the measured IDs.
  Physical return eligibility uses the real0/1/5 predicate. Old belt access
  raises an explicit reconstruction error instead of returning Force or Trunk.
- `citemboard.cpp`: retire the old belt from two legacy trade lookup guards,
  retaining their inventory/equipment domain. This is not a new455 trade system.

The old belt symbol is an **invalid migration marker255**, not an invented valid
storage/wire ID. It must never acquire a public table slot. The surviving old
`_GetBeltBoard` callers are listed with paths/lines in the checkpoint. In
particular, **the old MainGame Create_Board and old BeltList download are not
accepted455 implementations and now explicitly refuse their obsolete belt
path**. They need actual455 replacements. Potion/hotbar functionality remains
required for M9; absence of the old separate CBeltBoard does not waive it.

This resolves the concrete wrong-object lookup from084:

| Public ID | Previous source | Current source /455 identity |
|---|---|---|
| 3 | CBeltBoard | CForceBoard |
| 4 | CForceBoard | CAnimusBoard |
| 5 | CAnimusBoard | missing source CTrunkBoard |
| 2 | CEquipBoard alias | CEquipBoard alias retained |

Registered class counts decrease18→17 because the obsolete target-absent class
was removed. This is not a client completion metric, and same-named classes
still need full behavior verification.

## Targeted validation

All182 client objects rebuilt successfully,20 kernels/41 facade units linked,
zero unresolved symbols. The engine is unchanged from082:67 objects/12 overlays,
SHA-256 `9caa283a6bf8a2fa1c9a05251b6cad451296bb03bda8a1860c22a872e88fe769`.
The actual CUnity/CAnimation consumer dependency check passes on real ANI/BBX.

`probe_client455_storage.py` links the full actual source object set. It creates
the actual embedded CMainApp network owner before real CBoardManager objects,
as learned in084. Three separately staged runs under
`work/m9/a7723312/storage-{001,002,003}` exit0 with identical results:

- canonical Force/Animus dynamic types and base pack creation (Force6×20,
  Animus1×10, Inventory5×20, Equipment1×16) work in the tested constructor domain;
- all256 BYTE IDs obey the public table boundary, with17 physical registered
  objects/18 non-null public lookups including equipment alias2;
- the independent fixture from target guard accepts0/1/5 only, and real ordinary
  ReturnItem rejects nonphysical codes before dereferencing a deliberately
  invalid item pointer; missing Trunk5 also returns false through its absent owner;
- the retired legacy getter throws, and no old CBeltBoard is constructed.

No full SF item generation, GUI Init/layout, hotbar execution, object insertion,
full ReturnItem side effects, gameplay transfer or item network packet is accepted
by these checks. The probe's initial compile required two missing includes; only
the test harness changed, and the production code was not retuned for a fixture.

Fresh account regression passes real send/ring/receive/dispatch, Avatar stage/
skip, MainApp Create gate and login transform on owned packets. No authentication
is performed. Exact own WinMain passes the loopback TCP fixture and sound; exact
own D3D/window/existing client Create returns1. First-chance exceptions remain
recorded; neither their handling nor Create1 establishes complete failure-domain
parity or a working ordinary MainGame/Tutorial loop.

Current own RF_Online.bin: SHA-256
`89924a1c95d2b3f2e0a09f2e19cc223e00f1454bac866d79cf19ae3a8d00a031`,
2084864 bytes, x86, entry RVA `14F490`. WinMain RVA `B53B0`, after Create `B551A`.
`inventory/client455-storage-checkpoint.json` is the current **PARTIAL** gate.
Older083/084 current-link gates are historical after this source migration.

Unchanged engine contracts are reused explicitly. Actor/money/map/audio GPU
suites and broad159k checks were not rerun or relabeled as fresh085 evidence.

## Remaining implementation

Next086: restore the real455 Linker/hotbar and remaining old belt consumers,
common UI/board preparation, including required missing providers. Trunk and
all36 missing registry classes remain required for complete455 behavior. Then
bind concrete QBI/follow/local handlers and actual Tutorial lifecycle/four-stage/
Login transitions. Item packet layouts, DB download, trade, ownership/lifecycle,
full Avatar/UI/gauges/nameplate, Character/audio/FX/IME/numeric behavior and every
previous acceptance gap remain open. No total percentage is inferred.

Reproduce with `scripts/Invoke-Python.ps1` and `prepare_client455_normal.py`,
`build_client455_normal.py`, the required consumer/link steps, then
`probe_client455_storage.py` and `checkpoint_client455_storage.py`.
