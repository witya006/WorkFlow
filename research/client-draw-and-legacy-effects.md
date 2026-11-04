# 455 draw calls and legacy effect-table bridge

2026-11-04. M4 remains incomplete; no RF_Online.bin is produced yet.

## Explicit draw arguments

CNpc RTTI name is at VA 0xBCCA40, descriptor 0xBCCA38, complete-object locator
0xB7B9F4. Its vtable begins 0xAABD84; slot 6 points to Render at 0x45D280.
The body matches the legacy source's render flags, alpha decay, material,
vertex-blending and post-draw alpha restoration, with additional 455 effects.
The call at 0x45D454 -> 0x92FE80 supplies scale from this+240 and scroll 0.
CResObject Render at 0x7CD2A0 uses the same arguments; scale getter 0x40A210
reads this+240 at instruction 0x40A21F. The input sources already have m_fScale.

scripts/apply_client_draw455.py checks these instructions, calls and vtable slots
in BOTH pinned x86 PEs, then adds exact byte-preserving conditional branches in
two working source copies. Their original shorter calls remain when the option
RF_CLIENT_455_DRAW_ARGUMENTS is off. The generated project defaults this option
off; the separate diagnostic driver explicitly enables it. No missing original
default arguments are invented, and compiler-only patches are kept separate.
inventory/client-behavior-patches.json records source/input/output hashes and
binary evidence. prepare_client_build.py validates the separate patch chain.

Both actual client objects reference the existing full five-argument SDK symbol,
and neither references the missing shortened symbol. Verification:
scripts/verify_client_draw455.py and inventory/client-draw-call-verification.json.
The patch script is idempotent and preserves timestamps on an identical rerun.
This proves selected argument contracts/compilation, not GPU output equivalence.

## EffectList layout and bounded bridge

The original x86 member_03.obj SHA-256 is
d939f5e90d6ce4428cd4635c9d2e57b3253c8fbdb17a31d0cefaad45e0d729f2.
Its actual LoadEffectFileList uses DWORD loaded flags and char* names at +2000,
with a loop bound 500. Function offsets 0x49 (cmp 500) and 0xD0 (store at
this+index*4+2000) are checked. The globals' observed placement is consistent
with 4000 bytes; native reads of the loader's output and layout assertions pass.
The header now has 67 layout assertions and the same 165 checked public symbols.

The owned EffectList::SetEffect bridge selects a loaded table entry and delegates
to the actual SDK SetPartEffect with its no-grade sentinel MAX_PATTERN_SIZE=9.
Its input domain is bounded at 500; unknown original inline/out-of-domain behavior
is not claimed restored. The 455 map-based table and 36 grades remain a known
M6 difference. This bridge is a real legacy component implementation, not final
455 effect subsystem coverage.

The own fixture now includes one valid 176-byte legacy effect record, with an
active particle ID 17 and empty texture filters. The actual old text-table and
binary effect loaders run; first SetPartEffect directly, then the reconstructed
table bridge apply that ID to two real SDK-constructed ObjectMesh records.
All 59 checks pass in the ordinary /MT harness with normal allocation and clean
process exit. No GPU or input game EXE/DLL is run. Native test/report:
scripts/probe_character_effect_loaders.py, inventory/character-effect-loaders.json.
The leaf setter report's 18 checks are separate; the client driver requires the
matching positive effect application report before connecting this library.

## Fixture ownership finding

The first positive test applied effects correctly but failed at scope exit with
0xC0000374. A separate, ignored allocator-trace variant mapped the invalid delete
caller to ObjectMesh::~ObjectMesh (+0x50). The original member_09.obj SHA-256 is
46833cbe908304571d46eeb9e07712a2ef17d2edcf9b7b8e06a5ef363d731e61.
Its destructor at file offset 0xC1F4 reads the +160 blend-matrix pointer at function
offset 0x40 and deletes it if nonnull. The supplied constructor leaves that field
untouched. Our synthetic no-blend meshes had not established that ownership state.

The fixture explicitly sets m_pMatBlend=nullptr after construction. The SDK code
was not changed, and the passing result uses the normal allocator, not the trace
override. Actual mesh-loading initialization of this field and 455 correspondence
remain an audit item; do not silently repair the original constructor on this basis.
Raw failure, trace CPP/MAP and analysis are ignored under artifacts/ and work/.

## Remaining two link symbols and next evidence

CheckFiles and SendLog remain enabled in the legacy branch and unresolved in the
current build. Other legacy default libraries are still explicitly deferred in
the diagnostic configuration. Full client/ABI and M9 acceptance are not achieved.

455 EffectLog corresponds to sub_7DF200, using .\\NetLog\\EffectLog.log:
open rt+ with wt fallback; measure ftell/end BEFORE appending; append/close;
truncate immediately when prior measured length >10,000,000; otherwise set flag
0x113E45C when >5,000,000. It has no direct SendLog call. A nearby candidate at
0x7DF1B0 reads/clears the flag and truncates the log, but IDA found no xrefs to
that routine and decompilation reports a stack-analysis warning. Its reachability
and lifecycle are NOT established: do not assume an atexit callback or add one.
Raw code/asm: artifacts/character455-effect-log*.json. This evidence changes the
next task from guessing SendLog to reconstructing the reference logging flow.

All 455 addresses above refer to backup SHA-256
46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558,
x86, base 0x400000, RVA=VA-0x400000. Draw evidence is additionally checked against
the current pinned behavior reference by the script. COFF has no runtime RVA.
Owned IDA sessions dbda4903, 46039b3e, 68782058 were closed.
