# RVP basic particle/entity pass and shared FX lifetime — 081

2026-11-07. Client only. **PARTIAL**, M6/M6F/M7/M9 remain open.

## Reference evidence

The x86/image-base `0x400000` pins are unchanged:

- current: `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
- backup: `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.

All 18 measured function bodies match both pins. All **2960 actual assembly
instructions** are saved, paginated and checked for overlapping/truncated pages.
The addresses and body hashes are in
`inventory/client455-rvp-effects-reference.json`; raw decompilation/assembly is
ignored under `artifacts/client455-progress/particle081-{initial,extra}.json`.
Owned IDA session `2710bd78` was saved and closed; `idb_list` returned zero.
No reference executable was executed.

Key contracts:

| VA / RVA | Measured behavior |
|---|---|
| `90D4C0` / `50D4C0` | Second model particle/entity draw pass |
| `7BD560` / `3BD560` | Lazy particle load and six-instance cloning |
| `8D6900` / `4D6900` | Shared FX creation/reference increment |
| `8D8340` / `4D8340` | Reference decrement and deferred destruction |
| `8DAE60` / `4DAE60` | Particle constructor, 1296 bytes |
| `BF8148` / `7F8148` | Entity Y/Z matrix, pinned 64 bytes |

The scroll multiplier stored as a double is exactly the promoted float
`0.0005000000237487257`, followed by double30. It must not be replaced by the
nearest double0.0005. The timer persists outside the cache lifetime.

## Implemented source and boundaries

`client455_rvp_effects.{h,cpp}` provides a source-owned shared cache, independent
EFF table, real Chef RPK resource reads and lazy particle/entity loads. The
ordinary model draw binds EFF and the separate FX pass runs after geometry and
transparent flush. The model matrix left by the geometry pass is intentionally
not restored per actor during this second pass, matching the measured call flow.

Each particle definition has six actual CParticle instances selected modulo6.
Loop runs before publishing the new rotation/create position. A false Loop
returns from the entire model pass, rather than skipping one slot. White RGB is
ORed into the current color while preserving alpha. Entities load once, restore
textures and use inverseYZ × model × world with the shared scroll value.

Release with a positive reference count decrements and retains the cache. A
later zero-reference release destroys it, including when the level is already
null. The native fixture observes 1→0 retention, reacquisition, nested ownership
and final destruction. CLand unload plus CLevel destruction can supply two
release calls; the camera regression checks that actual route as well.

Owned byte-preserving header/source overlays expand **CParticle1148→1296** and
**CEntity208→212**, and adapt initialization/release/basic SPT fields. Static
assertions check measured offsets. A placement-new probe compares all1296 bytes
against the measured particle constructor: zero fill, gravityY−15, lightID−1.
Original legacy inputs remain unchanged.

This is a bounded adapter: ordinary basic SPT update/entity draw still use legacy
code with measured overlays. Advanced trace/curve/light/distortion/azirang/
combine-scale tokens explicitly refuse loading; special-particle and full
numeric/render equivalence are not accepted. The original process-owned Chef
group is currently indexed by the shared RVP cache; exact global owner/context
and arbitrary failure/unwind semantics remain open. Dense original cache storage
is represented by sparse owned slots, without a claim of byte-identical cache ABI.

## Actual input resolution

The read-only audit indexes **17 Chef RPKs**. It resolves **283/300 particle** and
**61/64 entity** definitions. These counts describe resource resolution only.
All five RVP particle recipes294–298 resolve inside the supplied archives and
have no selected advanced tokens. Missing exact loose paths were therefore not
treated as proof that those RVP assets were absent. Duplicate archive payloads
must match for this tool audit; it does not certify runtime enumeration order.

## Verification and an ABI regression fixed

Final stock neutralAS1 runs to completion:269 ticks,12 actors/4 shared models,
185 actor draws and148 particle draws, one lazily loaded particle recipe. A
separate176-byte test EFF selects actual ENTITY1 from the real INI/RPK corpus:
six entity draws and50 non-background readback pixels. The controlled two-actor
animation regression preserves9 different pose ticks/459 restored mesh parts.
Exit0, warnings0, Dmalloc270592 before/after.

Nine actor/world/entity frames plus six camera frames were inspected, including
enlarged crops. Stock geometry is small and several captures are empty after
the ships leave view. The isolated entity is also small. These captures **do not
establish fine reference-runtime pixel equivalence or isolated particle pixels**.

The first Cora regressions failed with `0xC0000374` during world loading. The
weather helper had remained outside the owned declaration prefix: it allocated
legacy1148/208 bytes while linked constructors required1296/212. Merely checking
the main engine/client declarations would not catch this caller mismatch.
`audit_client455_particle_abi.py` decodes the actual old and fixed OWN executables:
operator-new arguments at RVAs `E69BF`/`E6AC2` change1148/208→1296/212. The failed
working executable and console are retained; evidence is
`inventory/client455-particle-abi-fix.json`. The fix supplies particle/entity
declarations to the weather helper without injecting camera declarations into
the other independent kernels. Final camera/world regressions pass Bellato364,
Cora330 and Accretia262 ticks with balanced release and no warnings.

Final engine:67 objects,11 source overlays, library SHA-256
`14af5e53fd4f639d5afa42e81d38ccb041bd14706d55bfa1b1c4c51763bd5c22`.
Baseline033 library/source hashes are preserved. Final normal RF_Online.bin:
x86,2,089,984 bytes, entry RVA `0x151000`, SHA-256
`0165bf169fb462a9111cd93201963d97f8a9d0e18ea8cdd9f0c600503c34440f`.
It links182 client/20 kernel/39 facade objects with zero unresolved symbols.
Fresh import/entry/startup contracts, actual early WinMain and exact PE
Create=1 pass. Observed handled first-chance exceptions are retained in the
startup trace; complete failure parity is not claimed. Native GPU/MSBuild use
the documented sandbox exception. No server files were modified.

## Reproduction and next work

Run via `scripts/Invoke-Python.ps1`: `audit_client455_rvp_effects.py`,
`audit_client455_particle_inputs.py`, engine build, normal prepare/build/consumer/
link, particle layout probe, actor probe and three RVP camera race regressions.
Refresh startup audit/entry/contracts/early startup and exactPE `--after-create`.
Run `audit_client455_particle_abi.py`, inspect both review sheets and mark reviewed,
then `checkpoint_client455_rvp_effects.py`. It accepts only **PASS_BOUNDED/PARTIAL**.
Historical080 and earlier checkpoint manifests are not fresh081 acceptance.
Unchanged broad159k suites were not repeated.

Next082: remaining RVP providers, beginning with ambient/event audio and its real
Miles ownership; advanced particles/global Chef lifecycle/material-light reset
remain explicit work. Then real CGP_Tutorial/Avatar/QBI/follow/local handlers and
four-stage/Login integration. All earlier scanner/numeric/palette/world/GUI/
IME/auth/gameplay gaps remain mandatory under `docs/client-acceptance.md`.
The incomplete feature registry still cannot yield an honest whole-client
completion percentage. M0–M5 closure does not measure the share of455 behavior.
