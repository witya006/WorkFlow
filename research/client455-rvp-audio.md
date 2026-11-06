# RVP immediate audio and timer-rate — 082

2026-11-07. Client only. **PARTIAL**. Full sound/client/M6/M6F/M7/M9 remain open.

## Reference and compiled behavior

The unchanged x86/image-base0x400000 pins are:

- current SHA-256 `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
- backup SHA-256 `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.

18 body ranges match both pins. 1665 actual assembly instructions from17
functions are fully paginated, with unique addresses. The complete770-line
Create pseudocode is saved in two pages, including resource loads and reference
binding. Raw evidence is ignored in `artifacts/client455-progress/audio082-*.json`;
addresses and hashes are in `inventory/client455-rvp-audio-reference.json`.
Owned IDA session `f1d662d0` was saved/closed; `idb_list` returned0. No reference
executable ran.

| VA / RVA | Contract |
|---|---|
| `8D3BC0` / `4D3BC0` | Attenuation: inner quarter distance, linear outer falloff |
| `8D3C70` / `4D3C70` | Pan calculation from current view/inverse and source |
| `8D3DB0` / `4D3DB0` | Positive-volume event sound |
| `8BEEC0` / `4BEEC0` | Immediate-wave registration,20-byte slots |
| `8BDE00` / `4BDE00` | Actual Miles MP3 sample load |
| `8BF070` / `4BF070` | Play, ignoring the caller's third pan argument |
| `8BDA50` / `4BDA50` | Raw volume update, fixed pan0.5 |
| `8BD950` / `4BD950` | Metadata-gated loop-count update |
| `8BD9B0` / `4BD9B0` | Stop, including type-dependent3D cleanup |
| `8BD8B0` / `4BD8B0` | Release all immediate waves |
| `8B3CB0` / `4B3CB0` | Direct float time-scale setter |

Important compiled behavior, rather than inferred intent:

- The record has handle+4,memory+8,loop metadata+12,type WORD+16,occupied WORD+18.
  Initial capacity128 grows32 when count reaches capacity. Individual release
  keeps occupied set, so the released ID is not reused by the loader's search.
- Only MP3 enters the loader. The measured non-MP3 branch sets type0/occupied1
  without loading a handle. All44 stock RVP files contain0 ambient declarations
  and210 wave events referencing two existing WAVs. These registrations cannot
  start sound through this immediate API. This **does not mean ordinary game
  WAV audio is disabled**: the separate PlayWave cache is a different route.
- MP3 load gates on music-on, reads actual file bytes, allocates/initializes a
  Miles sample and passes the raw load flag to the actual Miles loop count.
  Metadata instead stores `flag!=1`. Thus flag1 gives metadata0/actual loop1;
  a later request0 is skipped. Flag0 gives metadata1/actual loop0. The native
  driver confirms these counterintuitive values; they were not silently fixed.
- Play applies global wave volume once. Subsequent volume updates use raw
  attenuation without global scaling and always pan0.5. They and Stop still
  operate with sound disabled; Play and SetLoop are gated by sound-on.
- Ambient updates use the previous actor matrix before flag16/camera work. A
  positive volume latches start; subsequent frames update volume only; leaving
  range clears the latch/stops. Event lookup prefers a CAM dummy, then actor
  fallback intentionally excludes the last actor. Create prepares twice.
- Timer-rate11 is camera-dependent: flag4 consumes/skips it. It calls the real
  existing engine time-scale bridge, rather than recording a requested value.

Correction to081: `8D6900` is the shared FX cache destructor, not acquire.
Create8D69E0 allocates via8D6870 and increments refs at8D6C57. The previous
reference fact/table/feature label is corrected; deferred lifetime behavior
itself remains valid.

## Source integration and verification

The derived `r3sound.cpp` includes `client455_sound_im.inc`, using the actual
existing Miles driver and its DLL. Other PlayWave/music/streaming code is left
outside this bounded restoration. RVP uses the actual immediate API for ambient
and event sound, real dummy/actor matrices, and ReleaseAll during loaded Release.
`client455_rvp_audio.cpp` provides attenuation/pan/event handling. Frame processes
ambient before flag16; timer-rate writes the real engine loop clock.

`probe_client455_rvp_audio.py` stages hashed owned copies of real client assets,
Miles DLL/MP3 codec, two real actors and CAM, a real MP3 from the installed Snd
corpus and an actual stock WAV. The controlled RVP exercises ambient, dummy and
actor event references and timer-rate. No fake audio sink is used.

Final native run `work/m9/59e544a3/rvp-audio-001` passes: actual Miles decoder
clock advances165ms, sample status/loop count/volume/pan checked, disabled music/
sound semantics and occupied-slot retention checked, capacity boundary129,
ordinary RVP2 ambient starts/2 stops/4 event executions, flag16 ordering and real
time-scale0.5. Dmalloc785169 before/after, warnings0, natural exit0. This proves
the selected real API route; it **does not capture output PCM or certify full
audible-output equivalence**. Attenuation/pan coverage is selected finite
boundaries; all x87/nonfinite/singular domains remain open.

An initial probe compile needed a declaration include. The next fixture wrongly
expected timer-rate under no-camera flag4 and without the previous-frame delay.
The fixture was corrected to the measured flow; production behavior was not
changed to make that expectation pass. Working failures remain ignored.

Fresh actor/FX regression:269 stock ticks/185 actor draws/148 particle draws,
6 isolated entity draws/50 pixels;9 different pose ticks/459 restored parts.
Bellato/Cora/Accretia camera/world regressions pass364/330/262 ticks with balanced
release.15 GPU frames/crops were inspected; small captures still do not prove
fine reference-runtime pixel parity. Weather ABI allocation evidence is refreshed.
Unchanged broad159k suites were not repeated.

Final engine:67 objects/12 overlays, SHA-256
`9caa283a6bf8a2fa1c9a05251b6cad451296bb03bda8a1860c22a872e88fe769`;
baseline033 preserved. Exact own RF_Online.bin is x86,2,094,592 bytes, entry RVA
`0x1512B0`, SHA-256
`7489e8c7cc27765d58ff43a6736179ef682ac2fbea72606b65de8981df1c2552`.
It links182 client/20 kernel/40 facade objects,0 unresolved. Complete import-name
provider audit, entry/startup/contracts and actual PE Create=1 pass. Handled
first-chance exceptions remain recorded, without a full failure-parity claim.

## Next integration

Use `scripts/Invoke-Python.ps1` with the audio input/reference audits, derived
engine and normal prepare/build/consumer/link, audio probe, actor and three
camera regressions, startup evidence and review scripts; then
`checkpoint_client455_rvp_audio.py`. Native graphics/Miles and MSBuild use the
documented local sandbox exception. The gate accepts **PASS_BOUNDED/PARTIAL**.
Earlier081/080 checkpoint manifests remain historical.

Next083 prioritizes actual CGP_Tutorial ownership/lifecycle/frame/input and
Avatar/QBI/follow/local feedback/board47, then four-stage/Login transitions. The
three Tutorial RVPs use the already checked camera/fade route, so unused magic/
trace commands need not postpone that integration. Magic/throw/collision/shadow/
trace/screen, advanced particles/global Chef/material-light reset, complete audio
initialization/PlayWave/streaming, failure/FP/scanner domains and full gameplay
remain mandatory M6/M9 work. They are not waived by this scheduling choice.
