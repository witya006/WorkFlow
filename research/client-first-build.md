# First complete RF_Online source-base build

2026-11-04. The selected diagnostic client target compiled, linked and then rebuilt
with --clean-first successfully. No unresolved symbols or forced link. This is the
build result within M4, not full 455 functionality, a launched game or M9 acceptance.

## Artifact and repeatability

work/client-build/build-character-diagnostic/Release/RF_Online.bin:
2,436,608 bytes, PE32 x86 Windows GUI, image base 0x400000, entry RVA 0x1BA9E0.
Clean SHA-256:
0b4c768fc4f52b26035c48cf900f67553392407d0372e23bb528333d2a87cf91.

Both successful outputs, logs and CMakeCache are preserved under ignored
artifacts/client-first-build/initial and /clean. inventory/client-first-build.json
pins their identities. All bytes are identical after excluding only two DWORD
fields: COFF timestamp at file offset 0x168 and debug-directory timestamp at
0x224344. The actual difference consists of two bytes inside each DWORD. .text,
.data, .data1, .fptable, .rsrc and .reloc hashes match directly; .rdata differs only
by that debug timestamp. Raw executable hashes differ; no raw bit-exact claim.
This comparison proves this repeat build, not a portable build from an empty machine.

verify_client_coff.py checked 180 client +58 engine +46 JPEG objects as x86 /MT.
The helper archives have their own native/directive checks. Direct provider discovery
found all 13 imports: Miles, Win32 APIs, D3D8/DInput8, ABuse, Adv and PDLL. Providers
were read, not loaded; recursive dependencies, actual DLL startup and loader search
directories remain runtime work. The built client has not been executed.

## Why two obsolete link references disappeared

No CheckFiles/SendLog dummy functions were defined, _DEVELOPER_ was not enabled,
and /FORCE is absent. The legacy bodies are preserved in disabled reference branches.
Three separately named options select evidenced portions of 455 behavior, rather
than pretending to have found unavailable original inline implementations:

- RF_CLIENT_455_DRAW_ARGUMENTS: explicit object scale and zero scroll at two sites.
- RF_CLIENT_455_EFFECT_LOG: real reconstructed append/rotation implementation.
- RF_CLIENT_455_LOBBY_TRANSITION: the connection-success edge enters lobby loading.

Defaults are OFF in generated CMake; the diagnostic driver explicitly selects ON.
This is not a successful build of every pure legacy branch/configuration. The
compiler-only ledger and behavior ledger remain distinct. A validated overlay chain
handles cgp_login.cpp, which has both an implicit-int compiler patch and a selected
behavior branch. Repeated patch scripts preserve bytes/timestamps and other ledger
entries. Original source inputs are not edited.

verify_client_draw455.py checks actual compiled object references for all selected
branches and parses the project's compiler/link fields to reject _DEVELOPER_ or
/FORCE. Full draw references are present, the old shortened call is absent,
effectutil calls the reconstructed logger, and the obsolete CheckFiles/SendLog
references are absent only in the selected build. No invented missing-symbol return.

## Effect logging

455 VA 0x7DF200 opens rt+ (wt fallback), measures length before the append, writes
the text, closes, truncates at >10,000,000 or sets a pending flag at >5,000,000.
The nearby clear routine 0x7DF1B0 clears that flag and truncates when set. No xrefs
or absolute pointer to this routine were found; its lifecycle remains unproven.
The owned clear implementation is explicit and has no invented atexit registration.

build_client455_effect_log.py verifies thresholds, signed branches, strings, flag
stores and every direct stdio call in both pinned x86 PEs. Own source resides in
scripts/native/client455_effect_log.*. 14 isolated cases /66 checks passed: strict
boundaries, prior-size semantics, repeated writes, explicit clear, sticky flag,
creation, missing directory, read-only file, CRLF append and ordinary process exit.
Only own fixture files are changed. Null buffers, >2GB/ftell failures, concurrency
and failed truncate-open behavior remain unverified. The implementation retains
the reference's unchecked fclose(fopen(...)) at the truncate sites.

## Connection success to lobby

455 LoadData 0x53F7A0 calls connection-state getter 0x539B90 at 0x53FDC0. A successful
result branches through 0x53FDC9 straight to 0x53FE2B, which pushes lobby.BSP and
calls 0x7C8600 at 0x53FE36, followed by lobby.cam at 0x53FE45. The legacy CheckFiles
block has no corresponding operation on THIS edge. This finding does not assert
that 455 lacks integrity/resource verification elsewhere or that the entire login
sequence is restored. Other network/UI/timeouts remain M6 work.

apply_client_lobby455.py checks the actual edge, loader call and strings in BOTH
pinned PEs before selecting the branch. It preserves the original CheckFiles
block outside that selection. The normal connection/error logic and _DEVELOPER_
setting were not disabled to obtain the build.

Binary identities: current behavior reference SHA-256
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
backup SHA-256 46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
Both x86/base 0x400000; RVA=VA-0x400000. Instruction-level manifests:
inventory/client455-effect-log.json and client-behavior-patches.json.
Owned static IDA session 21aa2688 was closed. No input game EXE/DLL was executed.

## Remaining work

The output still uses a diagnostic reconstructed Character interface and adapted
binary SDK, /Od compatibility flags and explicitly deferred legacy default libraries.
Exact original constructors/layout extents, complete runtime ABI, optimized release,
D3D9 reference rendering, 455 effect-map/36-grade behavior, full source coverage and
all gameplay/UI/network acceptance remain open. See client-acceptance.md.

Next: M5 real selected data loading/use. Helper-only SPT already has real samples
and a Python oracle; identify its actual 455 loader before claiming equivalent
client behavior. A standalone parser is not the full runtime integration result.
