# RVP actors: resources, animation and saved poses — 080

2026-11-07. M6 continues; M6F/M7/M9 remain open.

The ordinary CLevel → RTMovie path now loads normal actors through the source
Character implementation, selects animations, binds camera dummies, calculates
visibility and poses, restores each actor's snapshot before drawing, applies
materials/EFF and flushes transparency. The separate particle/entity pass and
shared-effect lifetime are still required. Magic, collision, shadow, ambient
and event audio, trace, screen and timer-rate providers remain explicit refusals.

## Reference

The pinned x86 binaries have base `0x400000`:

- Current SHA-256: `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`.
- Backup SHA-256: `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.

Sixteen full function ranges match between pins. Actual IDA pages contain all
1,051 assembly instructions. Owned session `f9d34033` was saved and closed.
Raw `artifacts/client455-progress/rvp-actor080-{initial,extra,flow}.json` and
[the audit](../inventory/client455-rvp-actor-reference.json) preserve evidence.
The existing078/079 caller evidence supplies full Create, FrameMove and Render.

| Contract | Reference RVA |
|---|---|
| Actor load and bounds | `0x4D4020` |
| Animation selection | `0x4D41E0` |
| Fade setters | `0x4D4310`, `0x4D4460` |
| Visibility | `0x4D3F10` |
| Save/restore palette | `0x4D4700`, `0x4D47F0` |
| OneTimeScene | `0x4D5F10` |
| Bone registration/lookup | `0x531480`, `0x531600` |
| Mesh registration/lookup | `0x5313F0`, `0x531560` |
| BODY manager | `0x5320F0` |
| Model bounds | `0x531B60` |
| Light/material setup | `0x4B52F0` |
| Cache reset, still open | `0x4CE5D0` |

Confirmed behavior preserved:

- Bone registry is renderer offset4264, despite its old own field name `meshes`.
  Mesh records belong to BODY. Registration appends duplicates; exact name lookup
  returns the first match. Several actors therefore share one model record.
- Load sets the renderer texture directory. BBX fallback uses real model bounds
  and then swaps Y/Z. The legacy fixed ±10 fallback is removed.
- Animation selection resets both frame values, clamps its index and leaves
  `nowAction` unchanged. OneTimeScene and final Prepare retain repeated setup.
- FrameMove publishes the bone frame before wrap; only the actor frame resets
  to160 for that tick. The matrix is dummy × scale. Automatic camera now publishes
  the frustum before actor culling, as the reference caller does.
- Each actor saves/restores its own pose around shared-model updates. Original
  counts start at2400 and matrix slots at2680, stride256, maximum70 mesh parts.
- Render retains ambient divisor412, reversed light direction, material biases,
  actual EFF application and the existing transparency pass.
- Fade setters have track callers. Function RVA `0x4D4340` has no xrefs and is
  absent from ordinary FrameMove/Render. No extra fade tick was introduced.

## Executed evidence

The unchanged neutralAS1 RVP is loaded by the real CLand/CLevel with its BSP/CAM.
Twelve actor records resolve to four shared models. Their 2-byte BN resources
are valid empty skeletons; the ANI files do not supply missing bone targets.
Registration, first-match sharing and two initial animation selections are checked.

The stock48-tick trace records70 visible pose updates and70 draws. Actor-only
captures contain391 non-background pixels in total. Ships are small at the
actual camera distance; these frames cannot establish detailed visual parity.

A separate controlled two-actor RVP uses pinned real model/skeleton/ANI inputs
from `client455-draw-reference.json` and the original neutralAS1 CAM/Dummy01.
One actor resets at frame75. The stock RVP and original assets remain unchanged.
The shared model has51 meshes/56 bones and maximum frame4320. Nine ticks have
different per-actor poses;459 parts pass exact palette restoration. The isolated
GPU capture contains14 non-background pixels, so matrix evidence is stronger
than visible detail. This fixture is not presented as a stock455 scenario.

Final run: `work/m9/c224c1d5/rvp-actor-001`, exit0, warnings0, Dmalloc270592
before/after, flag16 suspension and outer renderer restoration verified.
Five actor and six camera regression frames were inspected, including explicitly
enlarged pixel crops. Fresh Bellato/Cora/Accretia camera regressions pass:
10/9/8 selections and364/330/262 ticks, matching events and balanced release.
Unchanged broad GUI/kernel and Tutorial intro suites were not repeated; older
reports remain historical, without a fresh comprehensive acceptance claim.

New ordinary PE: x86,2,082,304 bytes, entry RVA `0x150DC0`, SHA-256
`a03ae596d5942d800d1fdce350330791226d59cfde67f17a404b0a57d0c51ddb`.
It links182 client/20 kernel/38 facade objects with zero unresolved symbols.
The exact PE passes the existing client Create checkpoint with return1.
Startup contracts and entry/import audits are fresh. First-chance `0x40080201`
and C++ exceptions remain recorded; full failure parity is unaccepted.

Two initial native GPU runs timed out at InitR3Engine inside the managed sandbox.
The same probe outside it initializes immediately. Subsequent diagnostic failures
corrected the expectation of nonempty stock BN and moved controlled actors onto
a visible real dummy. Working directories remain preserved. Only the final
successful run supplies acceptance. MSBuild required the known FileTracker
sandbox exception. No input EXE was executed and no server file was modified.

## Reproduction and gaps

Use `scripts/Invoke-Python.ps1` for audit/preparation/build/consumer/link scripts,
then `probe_client455_rvp_actor.py` and the three `probe_client455_rvp_runtime.py`
race options. Native graphics require desktop access outside the sandbox.
Refresh startup/entry/contracts and exact PE `--after-create` evidence. Inspect
both RVP contact sheets before marking their review scripts `--reviewed`.
`checkpoint_client455_rvp_actor.py` validates the bounded result as **PARTIAL**.

Next081: real particle/entity DrawEffectMat and shared-effect Create/Release,
reference counts and deferred lifetime; then remaining RVP audio/commands and
actual Tutorial/Avatar/QBI/four-stage/Login integration. Collision/shadow need
their455 contracts. Palettes with more than70 parts or more than4 matrices per
slot are rejected; original overflow/fatal policy is outside accepted coverage.
Scanner078, numeric/locale/failure079 and all other acceptance gaps remain.
M9 still requires complete gameplay and [all client criteria](../docs/client-acceptance.md).
