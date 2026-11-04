# Character: effect defaults, actual loaders and exception helpers

2026-11-04. M4 client dependency reconstruction; not final 455 acceptance.

## Missing effect arguments

The legacy item source CMeshItem::Render_RenderWithEffect has distinctive shared
structure with 455 sub_46C470: timeGetTime delta multiplied by 0.0005, scroll reset
at 1, effect initialization/alpha update, separate unit branch, mesh ID >>20,
race codes 1/3 choosing effect group 5, another group for other races, drawing
and querying remaining mesh effects. This is a strong structural correspondence,
not a recovered symbol name. 455 expands the effect grade table from 9 to 36
and adds a render-context argument to the setter; those differences remain.

The supplied Character SDK exposes four-argument SetMeshEffect/IsHaveMeshEffect,
where the last argument selects one of six pattern indexes in the item table.
Legacy source omits this argument in the corresponding ordinary branch/query.
455 instructions push 0 at VA 0x46C6AD (RVA 0x6C6AD) before the setter call at
0x46C6E4 -> 0x929E70, and at VA 0x46C8C6 (RVA 0x6C8C6) before the query call
at 0x46C8DA -> 0x927B80. The instruction bytes and relative call destinations
are checked in BOTH pinned x86 PEs by recover_character_effect_defaults.py.
Hashes and offsets are in inventory/character-effect-defaults.json.

The diagnostic header now declares default zero on the existing full functions.
It removes the invented shortened overload declarations. No wrapper/stub or
change to legacy client source is necessary. Other shortened APIs remain open.

## Native old-loader check

probe_character_effect_loaders.py builds an own harness linked to the adapted
SDK, real stdio adapter and reconstructed exception support. It calls the real
EffectPatternList::LoadEffectPatternList and ItemEffectList::LoadItemListFile on
two bounded, valid, synthetic CRLF fixtures. Old global objects retain their
own original allocation/layout and static initialization; no modern STL objects
are substituted. Pattern 1 has alternating nonzero/zero grades, pattern 2 is
all zero. Item group 0 chooses pattern 1; group 5 chooses pattern 2.

49 checks verify positive/negative queries, omitted versus explicit group zero,
group-five distinction, grade 9/UINT_MAX rejection, missing ID and an unloaded
object. SetMeshEffect is exercised with empty effect-file flags, so no mesh,
device or texture loading occurs. This tests actual old fgets/FILE-EOF parsing
through the adapter. It does not certify malformed old-parser inputs, effect
binary files, rendering or all original resource files. Report with hashes:
inventory/character-effect-loaders.json. Raw analysis is ignored under artifacts/.

## Real exception helpers

Installed C:/Windows/SysWOW64/msvcp60.dll is Microsoft signed (signature Valid),
x86, SHA-256 8d024f35eead1e0942aad24ecbf86cf72e3237f7c94eebb5a6a3a41f498dd139,
image base 0x10000000. Its exports match the two unresolved SDK helper names.
_Xlen at RVA 0x27010 constructs length_error with "string too long"; _Xran at
RVA 0x27060 constructs out_of_range with "invalid string position". Constructor
calls, message references, throw descriptors and _CxxThrowException calls are
verified as machine bytes by build_character_exceptions.py; all RVAs and hashes
are in inventory/character-exceptions.json.

Authored character_legacy_exceptions.cpp implements those contracts with the
current /MT CRT's exception objects. It does not copy old string or exception
storage into modern objects and does not require shipping/loading msvcp60.dll
in the client. No modern basic_string COMDAT definitions are allowed in this
support object, preventing collisions with the old SDK's template names.

770 native checks compare classic export calls and reconstructed helpers over
64 rounds: exact type/message, logic_error reference catch, nested rethrow,
typed outer reference catch and 512 guard destructions. The trusted installed
system DLL is executed by this own harness; input game EXEs/DLLs are not run.
The loaded provider timestamp/SizeOfImage are checked against the hashed x86
SysWOW64 file, avoiding 32-bit System32 redirection confusion.

This comparison provider preserves the legacy API but is not proven identical
to the absent historical libci linked when CharacterMR was created. Complete
old Character exceptional cleanup and copying old exception layouts remain
unverified. The manager/parser harnesses now link real helpers without test-only
alternatename overrides and still pass 3102 and 49 checks respectively.

## Current M4 boundary

All 180 client C++ units compile. Diagnostic link now has 7 unique unresolved
symbols: ChInterface constructor, short DrawCharacter, SetEffect, SetMipMap,
SetTexPath, CheckFiles and SendLog. RF_Online.bin is not built and M4 stays open.
CheckFiles/SendLog remain enabled and unresolved rather than bypassed.

Further constructor reconnaissance is saved in artifacts/character455-*ctor.json,
character455-construction.json and character455-render-init.json. 455 allocates
0x8440 for its interface and initializes many more fields than the old SDK view.
The 455 construction chain is 0x5DFA80 -> 0x5DFB50 -> 0x5DFB70 -> 0x91C8F0.
These are backup x86 findings, image base 0x400000, SHA-256
46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
Do not copy its sizes/offsets into the old D3D8 class. Old constructors should be
reconstructed from legacy invariants with explicit unknowns, then verified.
