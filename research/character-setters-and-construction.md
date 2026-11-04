# Character: texture setters and empty renderer construction

2026-11-04, M4. Full client link is still incomplete; this is not 455 acceptance.

## Texture path

455 sub_607CB0 corresponds structurally to legacy CCharResData::LoadMeshDataList:
328-byte records, bone IDs -1/-2, BBX name substitution, mesh creation, ID assignment
and texture path from record +200. The setter called at VA 0x60809F is 0x608140.
Its instructions guard a null source, push count 255, add +276 to the destination
object and call strncpy at 0x8797A0. It pads shorter strings and deliberately does
not force byte 255 to zero for long strings. Null source leaves the object alone;
a null destination with nonnull source is not a supported input.

The old SDK InitVertex consumes the override at object +272, confirmed by the
instruction at function offset 0x1B7 in member_07.obj. This differs from the 455
offset. The authored method uses the recovered legacy field and the checked 455
copy behavior; it does not substitute the newer CPU layout into the old library.

## Texture detail

455 login data loading sub_53F7A0 calls 0x540110 immediately before Title.mp3.
The wrapper adds +0x20E8 for its embedded TextureManager and calls 0x540140,
which stores the DWORD unchanged at that manager's +0x11C. The old SDK AddTexture
reads its equivalent +156 and passes it to CHR3LoadDDS. The recovered SetMipMap
therefore stores the supplied value in the old manager's +156 field without
inventing clamping or conversion.

build_character_setters.py verifies these machine instructions in BOTH pinned
x86 PEs and checks original COFF object hashes and consumed-field operands.
inventory/character-setters.json contains full hashes, RVAs, file offsets and
native output identities. Source/call-sequence correspondence is an inference;
the stated instruction effects are confirmed directly. Own source is under
scripts/native/character_recovered_setters.cpp.

18 native checks invoke our compiled leaf methods through the x86 method ABI
on guarded storage: null source, lengths 0/1/10/127/128/254/255/256/600, untouched
neighbors and last byte, and DWORD values including UINT_MAX. This probe does not
construct a renderer. Separately, the combined manager test invokes both setters
through a genuinely constructed recovered ChInterface eight times.

## Owned constructor reconstruction

TextureManager establishes an empty legacy vector and uses the SDK's real Init.
CMeshManager establishes its empty vector. CRender constructs all four embedded
managers, defines its opaque storage, then calls the SDK's real Init (light,
device, flags, shadows and file initialization). ChInterface forwards to that
base construction without additional proven fields. No GPU or texture is loaded.

The old effect routines consume CRender::m_Render, and its supplied destructor
clears that pointer. The owned bridge binds it to the constructed object. This
is an explicit reconstruction invariant, not a recovered original inline binding
sequence. Full original sizeof and other unavailable inline side effects remain
unproven. TextureManager::m_TManager and AnimationManager::m_AManager do not receive
invented assignments. The supplied renderer initializers and input bodies are
pinned in inventory/character-managers.json (COFF has no runtime RVA).

The combined native harness now passes 3630 checks, including 528 checks for eight
empty renderer constructions/destructions, embedded state, light defaults, setters,
136 real SDK part-manager allocations, vector growth and lookup. The old destructor
releases these parts. GetObjectManager uppercases a query while AddPartToMM stores
the supplied name verbatim; uppercase fixture names follow that existing domain.
An initial test incorrectly expected a Specular value at the Ambient offset; the
assertion was corrected against the D3DLIGHT8 layout, without changing SDK behavior.

Header: 64 layout assertions and 165 checked public decorated references. All 180
client C++ units compile. Link now has four unresolved symbols: short DrawCharacter,
EffectList::SetEffect, CheckFiles, SendLog. Integrity/logging calls remain intact.

## Next evidence, before further implementation

455 EffectList changed from the old fixed arrays to a map. Candidate setter 0x9298D0
looks up a key, checks loaded state and calls 0x9293D0 with grade 36. Do not paste
the newer map offsets into the old array object. Raw analysis: ignored artifacts/
character455-effect-setter-new-layout*.json.

CResObject RTTI name at 0xBCB114, descriptor 0xBCB10C, complete-object locator
0xB7A630, vtable pointer at 0xAA9378 (methods begin 0xAA937C). Render slot 6 points
to 0x7CD2A0, matching source flags ROSF_RENDER_BONE=1, ROSF_CLIPPED=4096, optional
bone, BBox=16 and state restoration. It calls draw wrapper 0x92FE80 with scale
from 0x40A210 (this+240) and scroll zero. Legacy CResObject::Render/CNpc::Render
omit scale/scroll even though the object has m_fScale. Do not invent missing
defaults merely to link: inspect the NPC call, then make any 455 behavior adaptation
explicit and separate from compiler migration patches. Raw resobject/draw evidence
is saved in artifacts/character455-resobject-*.json and character455-draw-character.json.

The above 455 analysis used backup SHA-256
46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558,
x86, image base 0x400000; RVA=VA-0x400000. Setter instructions are checked also in
the pinned current behavior reference by the reproducible script. Owned IDA
session 2e6f4605 was saved and closed. No input game EXE/DLL was executed.
