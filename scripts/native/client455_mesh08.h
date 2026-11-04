#pragma once
#include <cstddef>
#include <cstdint>

// Own bounded byte views, not the 5803-byte455 ObjectMesh ABI. The caller owns
// the input buffer and record storage, which must outlive every returned view.
#pragma pack(push,4)
struct RF455Mesh08Part {
    const unsigned char* header;
    const unsigned char* vertices;
    const unsigned char* indices;
    const unsigned char* bones;
    std::uint16_t vertexCount,indexCount,boneCount;
};
struct RF455Mesh08View {
    RF455Mesh08Part* parts;
    const unsigned char* trailing;
    std::size_t consumed,trailingBytes;
    std::uint16_t meshCount;
};
#pragma pack(pop)
#if defined(_M_IX86)
static_assert(sizeof(RF455Mesh08Part)==24,"Own mesh08 record-view ABI");
static_assert(sizeof(RF455Mesh08View)==20,"Own mesh08 model-view ABI");
#endif
enum RF455Mesh08Status {
    RF_MESH08_OK=0,RF_MESH08_ARGUMENT=1,RF_MESH08_MAGIC=2,
    RF_MESH08_TRUNCATED=3,RF_MESH08_CAPACITY=4,RF_MESH08_INDEX_LIMIT=5,
    RF_MESH08_OVERFLOW=6
};
extern "C" {
// Result remains unchanged on failure; caller record storage may be partial.
// Length/capacity errors are owned safety behavior, not reference AV parity.
RF455Mesh08Status RF455_DecodeMesh08(const void* bytes,std::size_t size,
    RF455Mesh08Part* records,std::size_t capacity,RF455Mesh08View* result);
RF455Mesh08Status RF455_EncodeMesh08(const RF455Mesh08View* view,void* bytes,
    std::size_t capacity,std::size_t* written);
}
