#include "client455_resource_io.h"
#include <utility>
#include <climits>
#include <cstring>
#include <memory>

// Client 455 x86 RVA 0x50B1C0. Wire header=144, layer=46; runtime record=526.
// Cache the encoded file. Texture numbers depend on the current texture table.
static_assert(sizeof(_R3MATERIAL)==526 && sizeof(_ONE_LAYER)==54, "455 R3M runtime layout");
static bool RF455_CanRebaseR3m(const _R3MATERIAL* materials, long long lowBase, long long highBase)
{
    const auto fits = [=](LONG slot) {
        return static_cast<long long>(slot) + lowBase >= LONG_MIN &&
            static_cast<long long>(slot) + highBase <= LONG_MAX;
    };
    for (int i = 0; i < materials[0].m_iMatNum; ++i) {
        const auto& material = materials[i];
        if (material.m_iDetailSurface != -1 && !fits(material.m_iDetailSurface)) return false;
        for (DWORD j = 0; j < material.m_dwLayerNum; ++j)
            if (!fits(material.m_Layer[j].m_iSurface)) return false;
    }
    return true;
}

static void RF455_RebaseR3m(_R3MATERIAL* materials, long long base)
{
    for (int i = 0; i < materials[0].m_iMatNum; ++i) {
        auto& material = materials[i];
        if (material.m_iDetailSurface != -1)
            material.m_iDetailSurface = static_cast<LONG>(material.m_iDetailSurface + base);
        for (DWORD j = 0; j < material.m_dwLayerNum; ++j) {
            auto& slot = material.m_Layer[j].m_iSurface;
            slot = static_cast<LONG>(slot + base);
        }
        if (material.m_iDetailSurface != -1) material.m_dwFlag |= _MAT_FLAG_NO_LOD_TEXTURE;
    }
}

void RF455_BindMapMaterialTextures(_R3MATERIAL* materials, int anticipatedFirst,
                                  DWORD actualFirst, DWORD textureCount)
{
    if (!materials) return;
    // R3M rebased one-based IDs against the anticipated texture-table tail.
    // A reused R3T reservation can begin earlier in that table.
    const auto bind = [&](LONG id, LONG missing) -> LONG {
        if (id == -1 || !actualFirst || anticipatedFirst <= 0) return missing;
        const auto relative = static_cast<long long>(id) - anticipatedFirst;
        if (relative < 0 || relative >= textureCount) return missing;
        const auto slot = static_cast<long long>(actualFirst) + relative;
        return slot <= 2147483647LL ? static_cast<LONG>(slot) : missing;
    };
    for (int i = 0; i < materials[0].m_iMatNum; ++i) {
        auto& material = materials[i];
        material.m_iDetailSurface = bind(material.m_iDetailSurface, -1);
        for (DWORD layer = 0; layer < material.m_dwLayerNum && layer < _MAX_LAYER_NUM; ++layer) {
            auto& id = material.m_Layer[layer].m_iSurface;
            id = bind(id, 0);
        }
    }
}

using RF455_R3mMaterials = std::unique_ptr<_R3MATERIAL, decltype(&Dfree)>;

enum class RF455_R3mStatus { Ready, Format, Version, Memory };

static RF455_R3mStatus RF455_ParseR3m(const RF455ResourceBytes& source, DWORD& materialCount,
                                    RF455_R3mMaterials* decoded)
{
    if (!source || source->size() < sizeof(float) + sizeof(DWORD)) return RF455_R3mStatus::Format;

    struct Cursor {
        const unsigned char* next;
        std::size_t remaining;

        bool read(void* target, std::size_t bytes) {
            if (bytes > remaining) return false;
            std::memcpy(target, next, bytes);
            next += bytes;
            remaining -= bytes;
            return true;
        }
    } input{source->data(), source->size()};

    float version = 0;
    DWORD count = 0;
    if (!input.read(&version, sizeof(version))) return RF455_R3mStatus::Format;
    if (version != _R3M_VERSION) return RF455_R3mStatus::Version;
    constexpr std::size_t wireRecordSize = 144;
    constexpr std::size_t wireLayerSize = 46;
    if (!input.read(&count, sizeof(count)) || !count ||
        count > (0x7fffffffu - 4u) / sizeof(_R3MATERIAL) ||
        count > input.remaining / wireRecordSize)
        return RF455_R3mStatus::Format;

    RF455_R3mMaterials pending(nullptr, &Dfree);
    if (decoded) {
        const auto bytes = static_cast<int>(count * sizeof(_R3MATERIAL));
        pending.reset(static_cast<_R3MATERIAL*>(Dmalloc(bytes)));
        if (!pending) return RF455_R3mStatus::Memory;
        std::memset(pending.get(), 0, bytes);
        pending.get()[0].m_iMatNum = static_cast<int>(count);
    }
    // Preflight runs the same record reader with one reusable stack record.
    _R3MATERIAL scratch{};
    for (DWORD i = 0; i < count; ++i) {
        auto& record = decoded ? pending.get()[i] : scratch;
        if (!input.read(&record.m_dwLayerNum, sizeof(record.m_dwLayerNum)) ||
            !input.read(&record.m_dwFlag, sizeof(record.m_dwFlag)) ||
            !input.read(&record.m_iDetailSurface, sizeof(record.m_iDetailSurface)) ||
            !input.read(&record.m_fDetailScale, sizeof(record.m_fDetailScale)) ||
            !input.read(record.m_name, sizeof(record.m_name)))
            return RF455_R3mStatus::Format;
        if (record.m_dwLayerNum > _MAX_LAYER_NUM ||
            !std::memchr(record.m_name, 0, sizeof(record.m_name)))
            return RF455_R3mStatus::Format;
        for (DWORD j = 0; j < record.m_dwLayerNum; ++j)
            if (!input.read(&record.m_Layer[j], wireLayerSize)) return RF455_R3mStatus::Format;
    }
    if (decoded) *decoded = std::move(pending);
    materialCount = count;
    return RF455_R3mStatus::Ready;
}

bool RF455_ValidateMapR3m455(const RF455ResourceBytes& source, DWORD& materialCount)
{
    return RF455_ParseR3m(source, materialCount, nullptr) == RF455_R3mStatus::Ready;
}

static RF455_R3mMaterials RF455_PrepareR3m(char* path, const RF455ResourceBytes* prepared = nullptr)
{
    RF455_R3mMaterials pending(nullptr, &Dfree);
    if (!path || !*path) return pending;
    constexpr std::uint64_t maxBytes = 64u * 1024u * 1024u;
    const auto source = prepared ? RF455ResourceRead{} : RF455_ReadResourceBytes(path, maxBytes);
    if (!prepared && source.status == RF455ResourceReadStatus::Unavailable) {
        char name[192];
        strncpy_s(name, sizeof(name), path, _TRUNCATE);
        @@MISSING_WARNING@@
        return pending;
    }
    if (!prepared && source.status != RF455ResourceReadStatus::Ready) return pending;
    const auto& bytes = prepared ? *prepared : source.bytes;
    if (!bytes) return pending;
    DWORD count = 0;
    const auto status = RF455_ParseR3m(bytes, count, &pending);
    if (status == RF455_R3mStatus::Version) {
        char name[192];
        strncpy_s(name, sizeof(name), path, _TRUNCATE);
        @@VERSION_WARNING@@
    }
    if (status == RF455_R3mStatus::Format || status == RF455_R3mStatus::Version)
        RF455_GetCharacterRfsCache()->RemovePayloadBytes(bytes);
    return pending;
}

_R3MATERIAL* LoadIndependenceR3M(char* path)
{
    auto materials = RF455_PrepareR3m(path);
    if (!materials) return NULL;
    const auto base = static_cast<long long>(GetNowR3D3DTexCnt()) - 1;
    if (!RF455_CanRebaseR3m(materials.get(), base, base)) return NULL;
    RF455_RebaseR3m(materials.get(), base);
    return materials.release();
}
