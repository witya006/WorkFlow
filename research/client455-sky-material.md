# Sky materials 125: ordinary sky2 selection and night-weight consumer

2026-11-09. PARTIAL M6. Current gate:
`inventory/client455-sky-material-checkpoint.json`.
M6/M6F/M7/M9 OPEN. M9 remains full client455 acceptance without renderer
modernization; this component is not final sky/atmosphere acceptance.

## Confirmed reference

PE32/x86/base400000. Primary SHA256
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
secondary `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.

Eight complete bodies/pcode/assembly,1696 instructions equal on both pins:

|Role|VA|RVA|Bytes|Instructions|
|---|---|---|---|---|
|Clock and lighting frame|8B1F20|4B1F20|1866|546|
|Ordinary CLevel load|8EA220|4EA220|2342|675|
|Ordinary CLevel frame|8E7910|4E7910|252|70|
|Enable setter|8B12A0|4B12A0|10|3|
|Enable getter|8B12B0|4B12B0|6|2|
|Profile getter|8B1240|4B1240|6|2|
|Profile constructor|900AB0|500AB0|46|15|
|Sky draw|9157E0|5157E0|1279|383|

All actual page lengths/counts/totals/unique addresses checked, max100
instructions. Sky draw reuses complete123 assembly/pcode;8B1F20 pcode reuses124.
Direct call operands, body bytes and referenced readonly numeric literals are
compared on both PEs. The initializer stubA95770 explicitly passes1154DF4 to
900AB0; its pointer is registered atAA8700 in the readonly initializer table.
The constructor sets night field+20 to0. File-backed BF7344 starts1.

Raw `artifacts/client455-progress/sky-material125-reference.json` and session
record alongside it. IDA58629015 saved/closed/list0. A first attempt to decompile
the initializer stub had no IDA function boundary; its actual instructions/call
and table pointer were decoded/read from bytes instead. No input EXE executed.

## Restored source and integration

-`client455_map_sky.inc`: ordinary map load first checks
  MapPath+directory+`\\sky2\\`+mapName+`sky2.r3e`. Existing file sets enabled1
  before LoadSkyBox; absence sets0 and checks the original sky path. Enable
  depends on file existence, not load success. The actual client has20 sky2
  directories; this is not proof that every directory/file naming combination
  is usable by every map owner.
-`client455_sky_day.inc/.h`: own enable/night storage and the exact night-weight
  slice of8B1F20. Ordinary FrameMove calls it immediately after the already
  restored two-clock prefix, before the existing BSP preparation. Disabled mode
  preserves previous night weight; the integer setter preserves its input.
-Dawn/dusk boundaries use the target's actual float-promoted double constants.
  x87 arithmetic order and final float store are retained. Exact dawnEnd
  0.3333333432674407958984375 yields1, while the next float yields0:the original
  discontinuity is preserved rather than smoothed.
-`client455_sky_material.inc`: per-material color mode4/TFACTOR vs5/DIFFUSE,
  sequential flags8/10h/20h alpha overrides, zero-alpha draw skip,
  TFACTOR setup mask1C and post-draw reset mask18. Flag20 alone affects the
  skip decision but does not configure alpha stages. This asymmetry is retained.
-Loaded sky restores actual device VIEW but leaves the caller's translation
  zeroed. Unloaded direct DrawSkyBox sets COLOROP MODULATE and binds the input
  VIEW without modifying its bytes or depth settings. Fog path stays in place.

This restores the actual night-weight value and its real consumers, not an
arbitrary fraction-to-alpha approximation. It deliberately does not present the
remaining atmosphere object fields or missing prepass as implemented.

Engine67/16derived:
`a11b2823ce9afd5be2e576f0d16b75fb20a49e236b260b8776e4dc635e7ee927`.
Only level.obj and skybox.obj payload changed;65 members byte-equal,0timestamp
only. Shared declarations/layouts,182client/20kernel objects unchanged. Real
ANI2/BBX consumer smoke refreshed, then ordinary client relinked.

Own PE `f61859245bea55d93fc2cb28bdf570a7afa4b06142d0bcd81ba6835df18b0b9c`,
2229248bytes/x86/base400000/entry167ED0,WinMainB98B0/afterCreateB9A24,unresolved0.
No CharacterMR/FORCE. Exact124 engine/PE/reports and memory preserved before125.
Original source installation,033baseline and all server files unchanged.

## Selected runtime evidence

`work/m9/22a774bc/sky-material-001`:

-60 finite night-profile cases under x87 precision24/53/64, nearest/even.
  Immediate floats before/at/after each boundary, normal/outside-day inputs,
  disabled-state persistence and setter semantics. Exact float bits match the
  independent rational oracle; control word unchanged.
-Three real ordinary FrameMove profiles use a deterministic clock provider and
  the actual clock code. The night-weight input is the resulting actual fraction.
-36 actual material cases on a real loaded Bellato sky group;12 flag combinations
  across three real frame profiles.26 actual indexed submissions and10alpha-zero
  cases. Actual stage/color/texture-factor/depth values observed at submission;
  asymmetric alpha cleanup and VIEW behavior verified. This does not assert
  complete per-layer animation/alpha-test/shader equivalence.
-Actual Bellato map selects legacy fallback/mode0. Actual neutralB load selects
  sky2/mode1. Five neutralB GPU frames viewed:00:00,06:30,12:00,19:30 and released.
  Four times produce distinct visible sky textures; released control is exact
  RGB16/32/48. Missing atmosphere background remains visibly an open gap.
-Direct unloaded DrawSkyBox method separately verifies COLOROP/view/depth; the
  ordinary wrapper's loaded guard would otherwise skip that branch.
-One warning:neutralB references original missing
  `Map/Entity/e_neutrala/trade_bel/trade_bel.r3e`. Original absence confirmed;
  no replacement is invented. The25 neutralB input files(64224177bytes) are
  copied underwork and pinned alongside existing Bellato/Entity copies.

The first two lab runs faulted executing0x40. The fixture had installed a copied
119-entry public D3D vtable; the implementation also uses private entries.
An own-process debugger recorded first/second-chance AV in the failed lab.
The corrected fixture temporarily replaces only the original DrawIndexedPrimitive
slot, restoring the method around actual forwarding and restoring page protection.
It does not replace the object's full table, attach to another process, or patch
production/client source. Successful43661caf run was followed by22a774bc with
additional direct-unloaded coverage. All failed labs retained.

World `work/m9/9c0ee635/world-frame-001`:76queue operations/16live clock±1/ray hit/
16FXlightframes/3ValidateDeviceS_OK;five viewed frames byte-equal124;6existing
warnings. Fade `work/m9/05075415/sky-fade-001`:90state frames+27helper cases,
three precision modes,exact fog/quad;five viewed frames byte-equal124,warnings0.
Total15 current GPU frames reviewed. Exact PE startup sound1/window/device/
existingCreate1/contracts pass;handled first-chance events retained.
Maps2692/projection12/other unchanged broad suites remain historical, not rerun.

## Next126 and limits

Restore the enabled special atmosphere prepass8B1840 and its actual state/resource
lifecycle. It uses the profile at1154DF4 and a second owner at1154E64, calls
9017F0/900DA0 conditionally, temporarily changes view/projection and clears
shaders/buffers. Check the meaning/writers of1157D40 flags before naming them;
do not assume they are movie flags. Cached124 pcode is exploratory evidence.

Only night weighting from8B1F20's lighting tail is restored. Sun position/matrices,
exposure/scattering coefficients, light colors and day/night fog updates remain
open, as do the prepass shaders/device lifecycle. No no-op prepass was added.
INS/Planet owners remain separate. AllRC/NaN/Inf/invalid data/OOM/lost/reset/
recreate/reentry and full renderer/stage/auth/gameplay acceptance are unproved.

Previous124 goal turn is verified progress(commit156cf28); this125 continuation
changes ordinary source, executable and evidence, also progress. No live native
job or owned IDA session remains. Preserve engine/PE/reports plus map/link response
before subsequent relinks; old reports alone are not full binary backups.
