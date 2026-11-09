# Sky fade 124: selected state and numeric reconstruction

2026-11-09. PARTIAL M6. Current gate:
`inventory/client455-sky-fade-checkpoint.json`.
M6/M6F/M7/M9 remain OPEN. M9 is the already-defined final acceptance of the
complete455 client without graphics modernization.

## Confirmed reference evidence

Pinned PE32/x86, image base400000:

- primary `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
- secondary `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.

Four complete bodies/pseudocode/full assembly,282 instructions, equal on both
pins. All disassembly pages <=100, actual lengths/counts/totals/unique addresses
checked. Direct calls decoded from PE bytes; referenced numeric literals read
and compared on both inputs. No executable input was launched.

| Function | VA | RVA | Bytes | Instructions |
|---|---|---|---|---|
| SetFadeSky |8B58A0|4B58A0|65|12|
| DrawFadeSKy |8B5900|4B5900|483|143|
| GetColorToColorAlpha |8B5780|4B5780|286|83|
| SetFadeFactor |8B49B0|4B49B0|143|44|

DrawFadeSKy assembly/pcode was reused from123, not downloaded again. Raw:
`artifacts/client455-progress/sky-fade124-reference.json`. Session7f86f1ac was
verified live, then saved/closed, final idb_list count0. Session record alongside
the raw. Other124 exploratory pseudocode is retained, but is not included in the
four-function confirmed/pin-compared evidence count.

## Source change and behavior

`scripts/native/client455_sky_fade_math.h` retains x87 arithmetic order and
explicit float spills; helpers inherit the caller's precision/rounding control.
Integer conversion temporarily selects truncation, uses the reference int64
conversion, then restores the control word. No alpha clamp is added.

`scripts/native/client455_sky_fade.inc` replaces the two sky fade methods in
the derived r3util.cpp. Original globals remain owned by that TU. SetFadeSky
sets duration -0.600100040435791015625, current clock start, input total time,
alpha1e-7 and started0. The positive/negative time branches use the original
epsilon promoted from float to double and float tick spill. Transition to fade-in
uses strict total<0.6f. The last active frame still submits alpha0 and writes fog;
only the following call returnsTRUE without changing state or device.

Shared GetColorToColorAlpha and SetFadeFactor alpha packing use the same numeric
helpers, keeping their existing callers and rectangle/texture rendering route.
Fog interpolation approaches6 and600 and writes actual D3D fog color/start/end.
This does not claim complete Draw2DSprite render-state equivalence.

Engine67/15derived:
`9e1b9c677ee4d9fe62f01e3186a3a481489950d3afccd02e1c83561febf7fb9f`.
Only r3util.obj payload changed;66 members byte-equal,0 timestamp-only.
Headers/layouts and182client/20kernel objects unchanged; the ordinary client was
relinked after fresh real ANI2/BBX consumer smoke. No needless full source rebuild.

Own RF_Online.bin:
`38ba1441b77774edd02da237c83e99dac5a62181c1c99e756f156c498e8f0047`,
2227200bytes, x86/base400000, entry167A00, WinMainB98B0/afterCreateB9A24.
Unresolved0, no CharacterMR/FORCE. Previous exact engine/PE/reports preserved
under `artifacts/client455-progress/*before124*`; old enginee826ee1a and PE182ecac6.
Original input sources,033baseline and server files were not changed.

## Targeted runtime evidence

Own full-object lab: `work/m9/d42443cf/sky-fade-001`.

-90 actual fade frames,60 active/30 idle,27 shared-helper cases.
-24/53/64-bit x87 significand precision, nearest/even; control word preserved.
-Natural long/short duration sequences; fade-in/out tick around1; finished idle;
  reset initialization; finite alpha outside0..1 included for helper packing.
-Independent Python rational oracle rounds every target arithmetic operation to
  the selected x87 precision, then explicit float stores. Actual state bits,
  real GetRenderState fog values and submitted quad colors match exactly.
-Eight fog-value differences from the old float/SSE expression, demonstrating a
  real numeric change. The27 selected alpha pack cases have zero old/new
  differences; no alpha difference is invented or required.
-Five actual Bellato sky GPU readbacks viewed: base, middle, fully covered,
  returning, done. Full coverage has uniform RGB96/64/32, and done is byte-equal
  to base. These are own-engine images; no running455 capture is claimed.
-Warnings0, natural exit0. Native original x87 CW127 (24-bit precision).

Two lab-only corrections before final acceptance: missing public declaration for
GetColorToColorAlpha was supplied in the fixture; an initial oracle expectation
of an alpha difference was replaced with the actually observed fog differences.
The successful native run was reused with --verify-existing after oracle fixes;
no additional native execution was needed. Production code was not weakened to
match those mistakes.

World regression: `work/m9/dbc48543/world-frame-001`,76queue operations/16OS clock
samples ±1/ray hit/16FXlight frames/3ValidateDeviceS_OK. Five GPU readbacks viewed
and byte-equal123. Existing6warnings retained. Maps2692/330,projection12/24 and
other unchanged bulk suites remain historical123 evidence, not newly rerun.
Fresh exact PE startup sound1/window/device/existingCreate1 and startup contract
smoke passed. Handled first-chance40080201/E06D7363/406D1388 are recorded, not
reported as unhandled crashes.

## Open work and exploratory findings for125

The actual sky materials remain different from legacy: flags4/8/10h/20h alter
color/alpha and cleanup masks. The full9157E0 body is already available in123.
Exploratory124 pcode indicates8B1240 returns the profile at1154DF4, night weight
at+20 (1154E08), updated by8B1F20. The implemented clock currently restores only
that function's256-byte clock prefix, explicitly returning before lighting.
The rest includes sun/atmosphere/fog updates. This is not a request to fake a
day-fraction alpha provider: verify the actual enabled state, writers, update
order and finite boundary arithmetic before connecting sky material consumers.

BF7344/getter8B12B0 gates special prepass8B1840. Exploratory xrefs associate its
setter8B12A0 with map owners; full owner classification, byte/pin confirmation,
sun/lensflare/scattering creation/update/render/destruction remain open.
These exploratory functions have pcode, not a new full-assembly proof count.

Full sky/unloaded-state cleanup, all material modes, textured fade branch GPU
states, other rounding modes, NaN/Inf/overflow, lost/reset/recreate/reentry,
all ordinary stage/Character/renderer/gameplay and client-acceptance gaps remain.
Numeric selected acceptance is not full fade/sky/world or final client acceptance.

Previous atlas explanation was conversational only, not goal progress. This
continuation changed authoritative source, PE, evidence, audit and next action;
classification: progress. No live job or owned IDA session remains.
