# Character: recovered manager construction and native verification

2026-11-04, M4, client dependency only. This is not evidence of 455 parity.

## CObjectManager

The supplied x86 CharacterMR member_06.obj has SHA-256
`37119bd6f28b6ea184cec9e0d78ab831c8d18fcbc207b8e7750147cf68fc20be`.
In `?AddPartToMM@ChInterface@@QAEXPAD@Z`, function-relative offsets
0x40/0x43/0x46/0x49 store zero at object offsets 4/8/12/16 following allocation
of 148 bytes. These initialize the empty legacy vector and ID counter.
`scripts/build_character_managers.py` checks the object digest and instructions.
This is relocatable COFF evidence: RVA is not applicable.

The authored constructor initializes these fields and defines the previously opaque
allocator/padding and name bytes as zero. Empty name/opaque padding equality with
the unavailable original constructor is not established. The name is not an
algorithmic substitute for the observed container state.

The own x86 /MT harness links the adapted supplied SDK and invokes its real
AddCharacter, GetCharacter, GetID, DeleteCharacter, Clear and destructor routines.
It adds 259 unloaded objects across growth, deletion and reuse, with 1296 passing
checks. Clear retains the increasing ID counter. The harness uses a fixed array
for expected pointers, avoiding modern STL instantiations with the old SDK's
COMDAT names. No input game executable is launched.

Missing _Xlen/_Xran have test-only aliases to an immediate failure routine.
Those aliases are absent from the delivered manager library and client build.
Thus exception paths remain unresolved in production, rather than passing silently.
File loading, loaded mesh destruction, rendering and exceptions are outside this
test. Source and output hashes: inventory/character-managers.json.

## AnimationManager

The original inline constructor remains unavailable. The owned reconstruction
establishes the empty vector consumed by the supplied algorithms, then calls
their real Init. This is an invariant-based reconstruction, not an assertion
that the original constructor was recovered byte for byte. No unsupported
assignment to the static m_AManager is added.

The x86 member_05.obj SHA-256 is
`0fe402dab6108538997fc86f30d0f9f048929a30d7ac429847b779b019036328`.
`?Init@AnimationManager@@QAEHXZ` at file offset 0x6112 is exactly
`c7411000000000c7411401000000c3`: writes +16=0, +20=1 and returns.
It does not define the int result advertised by its symbol; the constructor
discards that result. No return-value behavior is inferred.

1806 further native checks use the real SDK AddAnimation, GetAnimationData,
GetAnimationID, DeleteAnimation2 and destructor. 257 records force repeated
container growth; name case conversion, duplicate rejection, IDs and deletion
are checked. File data is not loaded. DeleteAnimation(name) is excluded: its
cached decompilation suggests deleting objects before comparing their names;
instruction verification and equivalence with 455 remain open.

The combined harness passes 3102 checks. The header has 61 layout assertions
and still matches 165 addressable public decorated names. These checks do not
prove compatibility of loaded animation data, exceptions or the 455 implementation.

After connecting these constructors, all 180 client C++ units remain compiled and
the diagnostic link has 11 unique unresolved symbols, down from 13. The full
RF_Online.bin is not built. inventory/client-character-diagnostic.json.
