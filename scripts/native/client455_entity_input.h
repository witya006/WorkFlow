#pragma once

#include <windows.h>
#include "entity.h"
#include "r3bsp.h"
#include <cstddef>
#include <cstdint>
#include <cstring>

// Client 455 x86, base 0x400000, SHA-256
// b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b.
// RVA 0x4E0A20 reads the ten sections consecutively and ignores stored offsets.
constexpr std::uint64_t RF455EntityInputMaxBytes = 64u * 1024u * 1024u;

struct RF455EntityInput {
    _ENTITY_FILE_HEADER header{};
    const unsigned char* payload = nullptr;
    std::size_t payloadSize = 0;
};

namespace rf455_entity_input_detail {
template <class Record>
inline Record readRecord(const unsigned char* data, std::size_t index)
{
    Record result{};
    std::memcpy(&result, data + index * sizeof(Record), sizeof(Record));
    return result;
}

inline bool trackFits(DWORD offset, int count, std::size_t stride, DWORD trackSize)
{
    return count >= 0 && offset <= trackSize &&
        static_cast<std::size_t>(count) <= (trackSize - offset) / stride;
}
}

inline bool RF455_ParseEntityInput(const void* bytes, std::size_t length, RF455EntityInput& out)
{
    using rf455_entity_input_detail::readRecord;
    using rf455_entity_input_detail::trackFits;
    constexpr std::size_t miniHeaderSize = 2 * sizeof(DWORD);
    constexpr std::size_t headerSize = miniHeaderSize + sizeof(_ENTITY_FILE_HEADER);
    static_assert(headerSize == 88 && sizeof(_ENTITY_COMP_HEADER) == 38 &&
        sizeof(_READ_ENTITY_FACE) == 6 && sizeof(_READ_ENTITY_M_GROUP) == 22 &&
        sizeof(_READ_ANI_OBJECT) == 88, "R3E113 source layout");

    if (!bytes || length < headerSize || length > RF455EntityInputMaxBytes) return false;
    const auto* encoded = static_cast<const unsigned char*>(bytes);
    // Geometry callers identify the format by version and sections. The
    // second DWORD is read by the original loader but does not select a branch.
    if (readRecord<DWORD>(encoded, 0) != _ENTITY_VERSION) return false;

    RF455EntityInput candidate{};
    candidate.header = readRecord<_ENTITY_FILE_HEADER>(encoded + miniHeaderSize, 0);
    candidate.payload = encoded + headerSize;
    const auto& header = candidate.header;
    if (header.CompHeader.size != sizeof(_ENTITY_COMP_HEADER) ||
        header.CompHeader.size > length - headerSize)
        return false;

    std::size_t vertexStride;
    switch (readRecord<_ENTITY_COMP_HEADER>(candidate.payload, 0).type) {
    case _VERTEX_ARC_TYPE_CHAR: vertexStride = sizeof(Vector3c); break;
    case _VERTEX_ARC_TYPE_SHORT: vertexStride = sizeof(Vector3s); break;
    case _VERTEX_ARC_TYPE_FLOAT: vertexStride = sizeof(Vector3f); break;
    default: return false;
    }

    enum Section {CompHeader, Vertex, VColor, UV, Face, FaceId, VertexId, MatGroup, Object, Track, SectionCount};
    struct SectionSize {DWORD bytes; std::size_t stride;};
    const SectionSize sections[] = {
        {header.CompHeader.size, sizeof(_ENTITY_COMP_HEADER)}, {header.Vertex.size, vertexStride},
        {header.VColor.size, sizeof(DWORD)}, {header.UV.size, sizeof(Vector2s)},
        {header.Face.size, sizeof(_READ_ENTITY_FACE)}, {header.FaceId.size, sizeof(WORD)},
        {header.VertexId.size, sizeof(WORD)}, {header.MatGroup.size, sizeof(_READ_ENTITY_M_GROUP)},
        {header.Object.size, sizeof(_READ_ANI_OBJECT)}, {header.Track.size, 1},
    };
    static_assert(sizeof(sections) / sizeof(sections[0]) == SectionCount, "R3E113 section count");
    const unsigned char* data[SectionCount]{};
    std::size_t counts[SectionCount]{};
    for (std::size_t i = 0; i < SectionCount; ++i) {
        const auto section = sections[i];
        if (section.bytes % section.stride ||
            section.bytes > length - headerSize - candidate.payloadSize)
            return false;
        data[i] = candidate.payload + candidate.payloadSize;
        counts[i] = section.bytes / section.stride;
        candidate.payloadSize += section.bytes;
    }

    for (std::size_t index = 0; index < counts[Object]; ++index) {
        const auto object = readRecord<_READ_ANI_OBJECT>(data[Object], index);
        if (object.frames < 0 ||
            !trackFits(object.pos_offset, object.Pos_cnt, sizeof(_POS_TRACK), header.Track.size) ||
            !trackFits(object.rot_offset, object.Rot_cnt, sizeof(_ROT_TRACK), header.Track.size) ||
            !trackFits(object.scale_offset, object.Scale_cnt, sizeof(_SCALE_TRACK), header.Track.size))
            return false;

        // GetSubObjectMatrix walks parents recursively using a one-based ID.
        // Bound this walk to reject cycles as well as out-of-range parents.
        constexpr unsigned maxParentDepth = 128;
        WORD parent = object.parent;
        for (unsigned depth = 0; parent != 0; ++depth) {
            if (parent > counts[Object] || depth == maxParentDepth) return false;
            parent = readRecord<_READ_ANI_OBJECT>(data[Object], parent - 1).parent;
        }
    }

    // The converter counts expanded vertices in a WORD. Validate every face
    // reached through the material groups, including reused faces.
    constexpr std::size_t maxExpandedVertices = 0xffffu;
    std::size_t expandedVertices = 0;
    for (std::size_t index = 0; index < counts[MatGroup]; ++index) {
        const auto group = readRecord<_READ_ENTITY_M_GROUP>(data[MatGroup], index);
        if (group.object_id > counts[Object] ||
            group.face_start_id > counts[FaceId] ||
            group.face_num > counts[FaceId] - group.face_start_id)
            return false;
        for (std::size_t faceNum = 0; faceNum < group.face_num; ++faceNum) {
            const auto faceId = readRecord<WORD>(data[FaceId], group.face_start_id + faceNum);
            if (faceId >= counts[Face]) return false;
            const auto face = readRecord<_READ_ENTITY_FACE>(data[Face], faceId);
            const std::size_t cornerEnd = std::size_t(face.v_start_id) + face.v_num;
            if (face.v_num < 3 || cornerEnd < face.v_start_id ||
                cornerEnd > counts[VertexId] || cornerEnd > counts[UV] ||
                face.v_num > maxExpandedVertices - expandedVertices)
                return false;
            for (std::size_t corner = face.v_start_id; corner < cornerEnd; ++corner) {
                const auto vertexId = readRecord<WORD>(data[VertexId], corner);
                if (vertexId >= counts[Vertex] || vertexId >= counts[VColor]) return false;
            }
            expandedVertices += face.v_num;
        }
    }

    // Dmalloc accepts a signed int and adds a four-byte allocation header.
    constexpr std::uint64_t maxEngineAllocation = 0x7fffffffu - 4;
    const std::uint64_t engineBytes = std::uint64_t(counts[MatGroup]) * sizeof(_ENTITY_M_GROUP) +
        std::uint64_t(counts[Object]) * sizeof(_ANI_OBJECT) + header.Track.size +
        expandedVertices * sizeof(Vector2f);
    if (engineBytes > maxEngineAllocation ||
        std::uint64_t(counts[Vertex]) * sizeof(Vector3f) > maxEngineAllocation)
        return false;

    out = candidate;
    return true;
}
