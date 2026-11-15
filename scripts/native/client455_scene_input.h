#pragma once

#include "client455_character_rfs.h"
#include "r3bsp.h"
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <new>
#include <vector>

bool RF455_ValidateMapR3m455(const RF455ResourceBytes& source, DWORD& materialCount);

// Original client 455 x86, image base 0x400000, SHA-256
// b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b.
// RVA 0x4FDEA0 and 0x4FF280 read loose BSP39 and EBP20 sequentially.
class RF455SceneInput455 {
public:
    explicit RF455SceneInput455(const char* path)
        : cache_(RF455_GetCharacterRfsCache()),
          bytes_(cache_->ReadLooseBytes(path, maxAllocation).bytes)
    {}

    bool validateBsp() const
    {
        _BSP_FILE_HEADER header{};
        return checkBspHeader(header);
    }

    bool validateBspMaterials(DWORD materialCount) const
    {
        return (bspChecked_ || (!position_ && validateBsp())) && materialCount >= bspMaterialsRequired_;
    }

    bool prepareMapMaterials(const char* path)
    {
        constexpr std::uint64_t maxR3mBytes = 64u * 1024u * 1024u;
        const auto source = cache_->ReadLooseBytes(path, maxR3mBytes);
        if (source.status != RF455ResourceReadStatus::Ready || !source.bytes) return false;
        DWORD count = 0;
        if (!RF455_ValidateMapR3m455(source.bytes, count) || !validateBspMaterials(count)) {
            cache_->RemovePayloadBytes(source.bytes);
            return false;
        }
        mapMaterialBytes_ = source.bytes;
        return true;
    }

    bool fitsRetention(std::size_t maxBytes) const
    {
        const auto bspBytes = bytes_ ? bytes_->capacity() : 0;
        const auto materialBytes = mapMaterialBytes_ ? mapMaterialBytes_->capacity() : 0;
        return bspBytes <= maxBytes && materialBytes <= maxBytes - bspBytes;
    }

    const RF455ResourceBytes& mapMaterialBytes() const { return mapMaterialBytes_; }
    bool failed() const { return failed_; }
    const RF455ResourceBytes& resourceBytes() const { return bytes_; }

    void reject(const char* path) const
    {
        if (bytes_) cache_->RemoveLooseBytes(path);
    }

    bool read(void* destination, std::size_t count)
    {
        if (!contains(count) || (count && !destination)) {
            failed_ = true;
            return false;
        }
        if (count) std::memcpy(destination, bytes_->data() + position_, count);
        position_ += count;
        return true;
    }

    bool skip(std::size_t count)
    {
        if (!contains(count)) {
            failed_ = true;
            return false;
        }
        position_ += count;
        return true;
    }

    bool readBsp(_BSP_FILE_HEADER& header)
    {
        return checkBspHeader(header) && skip(sizeof(header));
    }

    bool readExtBsp(_EXT_BSP_FILE_HEADER& header, DWORD bspLeafCount)
    {
        static_assert(sizeof(_EXT_BSP_FILE_HEADER) == 388, "EBP20 header layout");
        _EXT_BSP_FILE_HEADER candidate{};
        if (!peek(candidate) || candidate.version != _R3_EXT_BSP_VERSION) return false;
        // The EBP reader ignores spare table entries and consumes these lumps.
        const Lump lumps[] = {
            {candidate.CFVertex.size, sizeof(Vector3f)}, {candidate.CFLine.size, sizeof(_TOOL_COL_LINE)},
            {candidate.CFLineId.size, sizeof(WORD)}, {candidate.CFLeaf.size, sizeof(_TOOL_COL_LEAF)},
            {candidate.EntityList.size, sizeof(_ENTITY_LIST)}, {candidate.EntityID.size, sizeof(WORD)},
            {candidate.LeafEntityList.size, sizeof(_LEAF_ENTITIES_LIST_INFO)}, {candidate.SoundEntityID.size, sizeof(WORD)},
            {candidate.LeafSoundEntityList.size, sizeof(_LEAF_SOUND_ENTITIES_LIST_INFO)},
            {candidate.MapEntitiesList.size, sizeof(_READ_MAP_ENTITIES_LIST)},
            {candidate.SoundEntityList.size, sizeof(_READ_SOUND_ENTITY_LIST)},
            {candidate.SoundEntitiesList.size, sizeof(_READ_SOUND_ENTITIES_LIST)}
        };
        std::uint64_t extent = sizeof(candidate);
        for (const auto& lump : lumps) {
            if (lump.bytes % lump.stride) return false;
            extent += lump.bytes;
        }
        if (extent > remaining()) return false;
        const auto collisionLeafCount = candidate.CFLeaf.size / sizeof(_TOOL_COL_LEAF);
        if ((collisionLeafCount && collisionLeafCount != bspLeafCount) ||
            (candidate.CFLine.size && !collisionLeafCount)) return false;
        if ((candidate.LeafEntityList.size &&
             candidate.LeafEntityList.size / sizeof(_LEAF_ENTITIES_LIST_INFO) != bspLeafCount) ||
            (candidate.LeafSoundEntityList.size &&
             candidate.LeafSoundEntityList.size / sizeof(_LEAF_SOUND_ENTITIES_LIST_INFO) != bspLeafCount))
            return false;

        const std::uint64_t staticBytes = extent - sizeof(candidate) - candidate.MapEntitiesList.size -
            candidate.SoundEntityList.size - candidate.SoundEntitiesList.size +
            std::uint64_t(candidate.CFVertex.size) +
            std::uint64_t(candidate.CFLine.size / sizeof(_TOOL_COL_LINE)) * sizeof(Vector4f) +
            std::uint64_t(candidate.MapEntitiesList.size / sizeof(_READ_MAP_ENTITIES_LIST)) * sizeof(_MAP_ENTITIES_LIST) +
            std::uint64_t(candidate.SoundEntityList.size / sizeof(_READ_SOUND_ENTITY_LIST)) * sizeof(_SOUND_ENTITY_LIST) +
            std::uint64_t(candidate.SoundEntitiesList.size / sizeof(_READ_SOUND_ENTITIES_LIST)) * sizeof(_SOUND_ENTITIES_LIST);
        const std::uint64_t entities = candidate.EntityList.size / sizeof(_ENTITY_LIST);
        if (!staticBytes || staticBytes > maxAllocation ||
            entities * sizeof(CEntity) > maxAllocation || entities * sizeof(CParticle) > maxAllocation)
            return false;
        if (!validateExtBspReferences(candidate)) return false;

        header = candidate;
        return skip(sizeof(candidate));
    }

private:
    // The old Dmalloc takes int and adds four bytes for its size word.
    static constexpr std::uint32_t maxAllocation = 0x7ffffffbu;
    struct Lump { DWORD bytes; std::size_t stride; };
    RF455CharacterRfsCache* cache_;
    RF455ResourceBytes bytes_;
    RF455ResourceBytes mapMaterialBytes_;
    std::size_t position_ = 0;
    bool failed_ = false;
    // The immutable lease travels with its successful preflight when copied.
    mutable _BSP_FILE_HEADER bspHeader_{};
    mutable DWORD bspMaterialsRequired_ = 0;
    mutable bool bspChecked_ = false;

    std::size_t remaining() const { return bytes_ ? bytes_->size() - position_ : 0; }
    bool contains(std::size_t count) const { return bytes_ && count <= remaining(); }

    template<class Record>
    struct Records {
        const unsigned char* first;
        std::size_t count;

        Record at(std::size_t i) const
        {
            Record value;
            std::memcpy(&value, first + i * sizeof(Record), sizeof(Record));
            return value;
        }

        template<class Predicate>
        bool all(Predicate valid) const
        {
            for (std::size_t i = 0; i < count; ++i)
                if (!valid(at(i))) return false;
            return true;
        }
    };

    template<class Record>
    static Records<Record> records(const unsigned char*& next, std::size_t bytes)
    {
        const auto* first = next;
        next += bytes;
        return {first, bytes / sizeof(Record)};
    }

    static bool indexRange(std::size_t start, std::size_t count, std::size_t total)
    {
        return !count || (start < total && count <= total - start);
    }

    bool checkBspHeader(_BSP_FILE_HEADER& header) const
    {
        static_assert(sizeof(_BSP_FILE_HEADER) == 684 && sizeof(_BSP_READ_FACE) == 6 &&
            sizeof(_BSP_READ_M_GROUP) == 42, "BSP39 source layout");
        if (!position_ && bspChecked_) {
            header = bspHeader_;
            return true;
        }
        _BSP_FILE_HEADER candidate{};
        if (!peek(candidate) || candidate.version != _R3BSP_VERSION ||
            candidate.Node.size < 2 * sizeof(_BSP_NODE) || !candidate.Leaf.size)
            return false;

        const Lump staticLumps[] = {
            {candidate.CPlanes.size, sizeof(Vector3f)}, {candidate.CFaceId.size, sizeof(DWORD)},
            {candidate.Node.size, sizeof(_BSP_NODE)}, {candidate.Leaf.size, sizeof(_BSP_LEAF)},
            {candidate.MatListInLeaf.size, sizeof(WORD)}, {candidate.Object.size, sizeof(_READ_ANI_OBJECT)},
            {candidate.Track.size, 1}, {candidate.EventObjectID.size, sizeof(WORD)},
        };
        const Lump geometryLumps[] = {
            {candidate.BVertex.size, sizeof(Vector3c)}, {candidate.WVertex.size, sizeof(Vector3s)},
            {candidate.FVertex.size, sizeof(Vector3f)}, {candidate.VertexColor.size, sizeof(DWORD)},
            {candidate.UV.size, sizeof(Vector2f)}, {candidate.LgtUV.size, sizeof(Vector2s)},
            {candidate.Face.size, sizeof(_BSP_READ_FACE)}, {candidate.FaceId.size, sizeof(DWORD)},
            {candidate.VertexId.size, sizeof(DWORD)}, {candidate.ReadMatGroup.size, sizeof(_BSP_READ_M_GROUP)},
        };
        // Exported offsets can be stale. Follow the loader's sequential spans.
        std::uint64_t geometryOffset = sizeof(candidate);
        for (const auto& lump : staticLumps) {
            if (lump.bytes % lump.stride) return false;
            geometryOffset += lump.bytes;
        }
        for (const auto& spare : candidate.ReadSpare) geometryOffset += spare.size;
        std::uint64_t extent = geometryOffset;
        for (const auto& lump : geometryLumps) {
            if (lump.bytes % lump.stride) return false;
            extent += lump.bytes;
        }
        if (extent > remaining()) return false;

        const std::uint64_t objects = candidate.Object.size / sizeof(_READ_ANI_OBJECT);
        if (candidate.EventObjectID.size > objects * sizeof(WORD)) return false;
        const std::uint64_t positions = std::uint64_t(candidate.BVertex.size) / sizeof(Vector3c) +
            candidate.WVertex.size / sizeof(Vector3s) + candidate.FVertex.size / sizeof(Vector3f);
        const std::uint64_t faces = candidate.Face.size / sizeof(_BSP_READ_FACE);
        const std::uint64_t groups = candidate.ReadMatGroup.size / sizeof(_BSP_READ_M_GROUP);
        const std::uint64_t staticBytes = positions * sizeof(Vector3f) + candidate.VertexId.size +
            faces * sizeof(_BSP_C_FACE) + candidate.CPlanes.size + candidate.CFaceId.size +
            candidate.Node.size + candidate.Leaf.size + candidate.MatListInLeaf.size +
            objects * (sizeof(_ANI_OBJECT) + sizeof(WORD)) + candidate.Track.size +
            groups * sizeof(_BSP_MAT_GROUP) + candidate.LgtUV.size + candidate.VertexColor.size;
        if (staticBytes > maxAllocation) return false;

        DWORD materialsRequired = 0;
        try {
            const auto* start = bytes_->data() + position_;
            const auto* staticData = start + sizeof(candidate);
            if (!validateBspObjects(candidate, staticData) ||
                !validateBspTree(candidate, staticData, faces, groups) ||
                !validateBspGeometry(candidate, start + static_cast<std::size_t>(geometryOffset),
                    objects, materialsRequired))
                return false;
        } catch (const std::bad_alloc&) {
            return false;
        }

        if (!position_) {
            bspHeader_ = candidate;
            bspMaterialsRequired_ = materialsRequired;
            bspChecked_ = true;
        }
        header = candidate;
        return true;
    }

    static bool validateBspObjects(const _BSP_FILE_HEADER& header, const unsigned char* staticData)
    {
        static_assert(sizeof(_READ_ANI_OBJECT) == 88 && sizeof(_POS_TRACK) == 16 &&
            sizeof(_ROT_TRACK) == 20 && sizeof(_SCALE_TRACK) == 32, "BSP39 animation layout");
        const auto* next = staticData + header.CPlanes.size + header.CFaceId.size +
            header.Node.size + header.Leaf.size + header.MatListInLeaf.size;
        const auto objects = records<_READ_ANI_OBJECT>(next, header.Object.size);
        if (!objects.count) return true;

        const auto trackFits = [&header](DWORD offset, int count, std::size_t stride) {
            // The exporter leaves arbitrary offsets for tracks with no keys.
            return count == 0 || (count > 0 && offset <= header.Track.size &&
                static_cast<std::size_t>(count) <= (header.Track.size - offset) / stride);
        };
        if (!objects.all([&](const _READ_ANI_OBJECT& object) {
            // GetFloatMod multiplies the duration by 32768 before casting to LONG.
            return object.frames >= 0 && object.frames <= 65535 &&
                trackFits(object.pos_offset, object.Pos_cnt, sizeof(_POS_TRACK)) &&
                trackFits(object.rot_offset, object.Rot_cnt, sizeof(_ROT_TRACK)) &&
                trackFits(object.scale_offset, object.Scale_cnt, sizeof(_SCALE_TRACK));
        })) return false;

        // Object and parent IDs use WORD and are one-based. Cache computed
        // depths so each referenced record is visited at most once.
        constexpr std::size_t maxObjectId = 0xffff;
        constexpr WORD maxDepth = 256;
        constexpr WORD visiting = 0xffff;
        const std::size_t lastId = objects.count < maxObjectId ? objects.count : maxObjectId;
        std::vector<WORD> depths(lastId + 1);
        WORD chain[maxDepth];
        for (std::size_t id = 1; id <= lastId; ++id) {
            WORD current = static_cast<WORD>(id);
            std::size_t length = 0;
            while (current && !depths[current]) {
                if (length == maxDepth) return false;
                depths[current] = visiting;
                chain[length++] = current;
                const WORD parent = objects.at(current - 1).parent;
                // Match the pre-bind repair of out-of-range parent IDs. The
                // last valid object is still available during bind geometry.
                current = parent <= objects.count ? parent : 0;
            }
            WORD depth = depths[current];
            if (depth == visiting || length + depth > maxDepth) return false;
            while (length) depths[chain[--length]] = ++depth;
        }
        return true;
    }

    static bool validateBspGeometry(const _BSP_FILE_HEADER& header,
        const unsigned char* next, std::size_t objects, DWORD& materialsRequired)
    {
        const std::size_t charPositions = header.BVertex.size / sizeof(Vector3c);
        const std::size_t shortPositions = header.WVertex.size / sizeof(Vector3s);
        const std::size_t floatPositions = header.FVertex.size / sizeof(Vector3f);
        next += header.BVertex.size + header.WVertex.size + header.FVertex.size;
        const auto colors = records<DWORD>(next, header.VertexColor.size);
        const std::size_t uvCount = header.UV.size / sizeof(Vector2f);
        const std::size_t lightUvCount = header.LgtUV.size / sizeof(Vector2s);
        next += header.UV.size + header.LgtUV.size;
        const auto faces = records<_BSP_READ_FACE>(next, header.Face.size);
        const auto faceIds = records<DWORD>(next, header.FaceId.size);
        const auto vertexIds = records<DWORD>(next, header.VertexId.size);
        const auto groups = records<_BSP_READ_M_GROUP>(next, header.ReadMatGroup.size);

        constexpr std::size_t maxPartitionVertices = 0xffff;
        constexpr std::size_t maxExpandedVertices = _MAX_VB_CNT * maxPartitionVertices;
        // Every face consumes at least three output corners. Bound the bitmap
        // from those outputs before allocating scratch tracking for coverage.
        if (groups.count > maxPartitionVertices + 1 || faces.count > vertexIds.count / 3 ||
            faces.count > maxExpandedVertices / 3 || faces.count > faceIds.count)
            return false;

        std::vector<bool> usedFaces(faces.count);
        std::size_t facesSeen = 0, previousGroupEnd = 0;
        std::size_t totalCorners = 0, totalTriangles = 0;
        std::size_t partitionCorners = 0, partitions = 1;
        for (std::size_t i = 0; i < groups.count; ++i) {
            const auto group = groups.at(i);
            if (group.object_id > objects || group.mtl_id < -1 || group.lgt_id < -1 ||
                !group.face_num || group.face_start_id < previousGroupEnd ||
                !indexRange(group.face_start_id, group.face_num, faceIds.count))
                return false;
            previousGroupEnd = std::size_t(group.face_start_id) + group.face_num;
            const auto groupMaterialsRequired = static_cast<DWORD>(group.mtl_id + 1);
            if (groupMaterialsRequired > materialsRequired) materialsRequired = groupMaterialsRequired;

            // CHAR wins over SHORT, with FLOAT as the decoder's default.
            const auto laneSize = (group.attr & _VERTEX_ARC_TYPE_CHAR) ? charPositions :
                (group.attr & _VERTEX_ARC_TYPE_SHORT) ? shortPositions : floatPositions;
            std::size_t groupCorners = 0, groupTriangles = 0;
            for (std::size_t at = group.face_start_id; at < previousGroupEnd; ++at) {
                const auto faceId = faceIds.at(at);
                if (faceId >= faces.count || usedFaces[faceId]) return false;
                usedFaces[faceId] = true;
                ++facesSeen;

                const auto face = faces.at(faceId);
                if (face.v_num < 3 || face.v_num > 8 ||
                    !indexRange(face.v_start_id, face.v_num, vertexIds.count) ||
                    !indexRange(face.v_start_id, face.v_num, uvCount) ||
                    !indexRange(face.v_start_id, face.v_num, lightUvCount) ||
                    face.v_num > maxPartitionVertices - groupCorners)
                    return false;
                const auto cornerEnd = std::size_t(face.v_start_id) + face.v_num;
                for (std::size_t corner = face.v_start_id; corner < cornerEnd; ++corner) {
                    const auto vertexId = vertexIds.at(corner);
                    if (vertexId >= laneSize || (group.lgt_id == -1 && vertexId >= colors.count))
                        return false;
                }
                groupCorners += face.v_num;
                groupTriangles += face.v_num - 2;
            }
            if (groupCorners > maxPartitionVertices - partitionCorners) {
                if (++partitions > _MAX_VB_CNT) return false;
                partitionCorners = 0;
            }
            partitionCorners += groupCorners;
            totalCorners += groupCorners;
            totalTriangles += groupTriangles;
        }
        // Metal materials reserve two UV vectors and three tangent vectors per
        // corner. Use that worst case before the actual materials are loaded.
        constexpr std::size_t cornerScratch = 2 * sizeof(Vector2f) + 3 * sizeof(Vector3f);
        return facesSeen == faces.count && totalCorners <= vertexIds.count &&
            totalCorners <= maxAllocation / cornerScratch &&
            totalTriangles <= maxAllocation / (3 * sizeof(WORD));
    }

    static bool validateBspTree(const _BSP_FILE_HEADER& header, const unsigned char* next,
        std::size_t faceCount, std::size_t groupCount)
    {
        const std::size_t planeCount = header.CPlanes.size / sizeof(Vector3f);
        next += header.CPlanes.size;
        const auto faceIds = records<DWORD>(next, header.CFaceId.size);
        const auto nodes = records<_BSP_NODE>(next, header.Node.size);
        const auto leaves = records<_BSP_LEAF>(next, header.Leaf.size);
        const auto groupIds = records<WORD>(next, header.MatListInLeaf.size);
        if (!faceIds.all([faceCount](DWORD id) { return id < faceCount; }) ||
            !groupIds.all([groupCount](WORD id) { return id < groupCount; }) ||
            !leaves.all([&](const _BSP_LEAF& leaf) {
                return indexRange(leaf.face_start_id, leaf.face_num, faceIds.count) &&
                    indexRange(leaf.m_group_start_id, leaf.m_group_num, groupIds.count);
            }))
            return false;

        // The engine traverses from node 1 recursively. Bound traversal depth
        // and reject revisiting a node to rule out cycles and repeated subtrees.
        constexpr std::size_t maxDepth = 256;
        constexpr std::size_t maxNodeIds = 0x8000;
        struct Pending { SHORT id; std::size_t depth; };
        std::vector<bool> seenNodes(nodes.count < maxNodeIds ? nodes.count : maxNodeIds);
        std::vector<Pending> pending{{1, 1}};
        while (!pending.empty()) {
            const auto current = pending.back();
            pending.pop_back();
            if (!current.id) continue;
            if (current.id < 0) {
                if (static_cast<std::size_t>(-static_cast<int>(current.id) - 1) >= leaves.count) return false;
                continue;
            }

            const auto nodeId = static_cast<std::size_t>(current.id);
            if (nodeId >= seenNodes.size() || current.depth > maxDepth || seenNodes[nodeId]) return false;
            seenNodes[nodeId] = true;
            const auto node = nodes.at(nodeId);
            if (node.f_normal_id >= planeCount) return false;
            pending.push_back({node.front, current.depth + 1});
            pending.push_back({node.back, current.depth + 1});
        }
        return true;
    }

    bool validateExtBspReferences(const _EXT_BSP_FILE_HEADER& header) const
    {
        // The consumer reads these lumps sequentially. Their extents and
        // strides have already been verified without using the stored offsets.
        const auto* next = bytes_->data() + position_ + sizeof(header) + header.CFVertex.size;
        const auto lines = records<_TOOL_COL_LINE>(next, header.CFLine.size);
        const auto lineIds = records<WORD>(next, header.CFLineId.size);
        const auto collisionLeaves = records<_TOOL_COL_LEAF>(next, header.CFLeaf.size);
        const auto entities = records<_ENTITY_LIST>(next, header.EntityList.size);
        const auto entityIds = records<WORD>(next, header.EntityID.size);
        const auto entityLeaves = records<_LEAF_ENTITIES_LIST_INFO>(next, header.LeafEntityList.size);
        const auto soundIds = records<WORD>(next, header.SoundEntityID.size);
        const auto soundLeaves = records<_LEAF_SOUND_ENTITIES_LIST_INFO>(next, header.LeafSoundEntityList.size);
        const auto placements = records<_READ_MAP_ENTITIES_LIST>(next, header.MapEntitiesList.size);
        const auto sounds = records<_READ_SOUND_ENTITY_LIST>(next, header.SoundEntityList.size);
        const auto soundPlacements = records<_READ_SOUND_ENTITIES_LIST>(next, header.SoundEntitiesList.size);
        const auto vertices = header.CFVertex.size / sizeof(Vector3f);

        // SetCFNormal and the collision-leaf reader follow these indices.
        return lines.all([&](const _TOOL_COL_LINE& line) {
            return line.start_v < vertices && line.end_v < vertices;
        }) && lineIds.all([&](WORD index) {
            return index < lines.count;
        }) && collisionLeaves.all([&](const _TOOL_COL_LEAF& leaf) {
            return indexRange(leaf.start_id, leaf.line_num, lineIds.count);
        }) && entities.all([](const _ENTITY_LIST& entity) {
            return std::memchr(entity.Name, 0, sizeof(entity.Name)) != nullptr;
        }) && entityIds.all([&](WORD index) {
            return index < placements.count;
        }) && entityLeaves.all([&](const _LEAF_ENTITIES_LIST_INFO& leaf) {
            return indexRange(leaf.start_id, leaf.entities_num, entityIds.count);
        }) && placements.all([&](const _READ_MAP_ENTITIES_LIST& entity) {
            return entity.ID < entities.count;
        }) && sounds.all([](const _READ_SOUND_ENTITY_LIST& sound) {
            return std::memchr(sound.name, 0, sizeof(sound.name)) != nullptr;
        }) && soundIds.all([&](WORD index) {
            return index < soundPlacements.count;
        }) && soundLeaves.all([&](const _LEAF_SOUND_ENTITIES_LIST_INFO& leaf) {
            return indexRange(leaf.start_id, leaf.entities_num, soundIds.count);
        }) && soundPlacements.all([&](const _READ_SOUND_ENTITIES_LIST& sound) {
            return sound.id < sounds.count;
        });
    }

    template<class Header>
    bool peek(Header& header) const
    {
        if (!contains(sizeof(header))) return false;
        std::memcpy(&header, bytes_->data() + position_, sizeof(header));
        return true;
    }
};

inline bool RF455_CanReadBsp455(const char* path)
{
    RF455SceneInput455 input(path);
    if (input.validateBsp()) return true;
    input.reject(path);
    return false;
}
