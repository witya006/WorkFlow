#pragma once
#include <cstddef>
#include <cstdint>

// Only the observed legacy vertex/UV records are defined here. These are not
// the 455 vertex or the still-incomplete ObjectData/CHARACTEROBJECT layouts.
class CHARACTERVERTEX {
public:
    float position[3];
    float firstBoneWeight;
    float normal[3];
    float uv[2];
};
struct EXPTVERTEX {
    float position[3];
    std::uint32_t unknown_12;
    float normal[3];
};
struct tagTEXCOORDFLOAT {float u,v;};
static_assert(sizeof(CHARACTERVERTEX)==36,"Legacy vertex stride");
static_assert(offsetof(CHARACTERVERTEX,normal)==16,"Legacy normal offset");
static_assert(offsetof(CHARACTERVERTEX,uv)==28,"Legacy UV offset");
static_assert(sizeof(EXPTVERTEX)==28,"Exported vertex stride");
static_assert(sizeof(tagTEXCOORDFLOAT)==8,"Legacy by-value UV ABI");
