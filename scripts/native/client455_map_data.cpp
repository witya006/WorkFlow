#include "client455_map_data.h"
#include "client455_character_rfs.h"
#include "client455_language.h"
#include <cstdio>
#include <cstring>
#include <mbstring.h>
#include <new>
#include <stdexcept>
#include <utility>

namespace {
struct Cursor {
    const unsigned char* data;
    std::size_t size, at = 0;

    const unsigned char* take(std::size_t n)
    {
        if (n > size - at) throw std::runtime_error("Short 455 map stream");
        const auto* bytes = data + at;
        at += n;
        return bytes;
    }

    void read(void* out, std::size_t n)
    {
        if (n) std::memcpy(out, take(n), n);
    }

    const unsigned char* text(std::size_t n)
    {
        const auto* bytes = take(n);
        if (n && !std::memchr(bytes, 0, n))
            throw std::runtime_error("Unterminated 455 map text");
        return bytes;
    }

    template <std::size_t N>
    void text(char (&out)[N])
    {
        std::memcpy(out, text(N), N);
    }

    std::uint32_t u32()
    {
        std::uint32_t value;
        read(&value, sizeof(value));
        return value;
    }

    std::vector<unsigned char> bytes(std::size_t n)
    {
        const auto* start = take(n);
        return {start, start + n};
    }

    void count(std::size_t n, std::size_t stride)
    {
        if (n > (size - at) / stride) throw std::runtime_error("Short 455 map array");
    }
};

RF455MapLoad parseCatalog(RF455MapData& catalog, const void* input, std::size_t size)
{
    if (!input) return RF455MapLoad::MissingInput;
    Cursor src{static_cast<const unsigned char*>(input), size};
    try {
        catalog.count = src.u32();
        // RVA 0x3caae0 requires the 455 base catalog of 110 maps.
        if (catalog.count != 110) return RF455MapLoad::MainCount;
        catalog.maps.reset(new RF455MapInfo[catalog.count]);
        for (std::uint32_t i = 0; i < catalog.count; ++i) {
            auto& row = catalog.maps[i];
            src.read(&row.byIndex, 4);
            src.text(row.pName);
            std::memcpy(row.pName_UI, row.pName, sizeof(row.pName));
            src.text(row.pFileName);

            char sprite[128];
            src.read(sprite, sizeof(sprite));
            const auto* end = static_cast<const char*>(std::memchr(sprite, 0, sizeof(sprite)));
            if (!end || std::size_t(end - sprite) + 25 >= sizeof(row.pMinimapFileName))
                throw std::runtime_error("455 minimap path overflow domain");
            std::sprintf(row.pMinimapFileName, "./SpriteImage/Common/Map/%s", sprite);
            src.read(&row.wMinimapAngle, 2);
            src.text(row.pBspFileName);

            row.byPortalNum = src.u32();
            src.count(row.byPortalNum, 288);
            if (row.byPortalNum) row.pPortalInfo = new RF455PortalInfo[row.byPortalNum];
            for (std::uint32_t j = 0; j < row.byPortalNum; ++j) {
                auto& portal = row.pPortalInfo[j];
                src.read(static_cast<RF455MineInfo*>(&portal), 96);
                src.read(&portal.byPortalType, 8);
                src.read(portal.byUsableRace, 5);
                src.text(portal.pName);
                src.text(portal.pDesc);
                src.read(&portal.byLinkedPortalNum, 1);
                src.read(portal.padding238, 2);
                src.u32(); // Serialized pointer slot is replaced by owned links.
                src.read(&portal.access, sizeof portal.access);
                src.read(&portal.bIsUsable, 4);
                src.read(portal.fields276, 12);
            }
            for (std::uint32_t j = 0; j < row.byPortalNum; ++j) {
                auto& portal = row.pPortalInfo[j];
                src.count(portal.byLinkedPortalNum, 8);
                if (portal.byLinkedPortalNum) {
                    portal.byLinkedPortal = new std::uint32_t[portal.byLinkedPortalNum][2];
                    src.read(portal.byLinkedPortal, portal.byLinkedPortalNum * 8u);
                }
            }

            row.byMineNum = src.u32();
            src.count(row.byMineNum, 96);
            if (row.byMineNum) {
                row.pMineInfo = new RF455MineInfo[row.byMineNum];
                src.read(row.pMineInfo, row.byMineNum * 96u);
            }
            row.byAreaNum = src.u32();
            src.count(row.byAreaNum, 84);
            if (row.byAreaNum) {
                row.pAreaInfo = new RF455MapAreaInfo[row.byAreaNum];
                for (std::uint32_t j = 0; j < row.byAreaNum; ++j) {
                    auto& area = row.pAreaInfo[j];
                    src.read(&area.dwIndex, sizeof(area.dwIndex));
                    src.read(&area.recArea, sizeof(area.recArea));
                    src.text(area.pName);
                }
            }
            src.read(row.fields512, 40);
            src.read(&row.miniMapWidth, 8);
            src.read(&row.miniMapX, 8);
            src.read(row.fields568, 20);
        }

        for (auto& section : catalog.layers) {
            const auto layerCount = src.u32();
            src.count(layerCount, 20);
            section.reserve(layerCount);
            for (std::uint32_t i = 0; i < layerCount; ++i) {
                RF455MapLayer layer;
                layer.height = src.u32();
                layer.width = src.u32();
                const auto nameSize = src.u32();
                if (nameSize > 32) throw std::runtime_error("455 layer name overflow domain");
                layer.name = src.bytes(nameSize);
                const auto labelCount = src.u32();
                src.count(labelCount, 16);
                layer.labels.reserve(labelCount);
                for (std::uint32_t j = 0; j < labelCount; ++j) {
                    RF455MapLabel label;
                    src.read(label.fields, sizeof(label.fields));
                    label.fields[0] |= 0xff000000;
                    layer.labels.push_back(std::move(label));
                }
                layer.image = src.bytes(src.u32());
                section.push_back(std::move(layer));
            }
        }
        catalog.mainConsumed = src.at;
        return RF455MapLoad::Complete;
    } catch (const std::runtime_error&) {
        return RF455MapLoad::Malformed;
    } catch (const std::bad_alloc&) {
        return RF455MapLoad::Malformed;
    } catch (const std::length_error&) {
        return RF455MapLoad::Malformed;
    }
}

RF455MapLoad applyLocalization(RF455MapData& catalog, const void* input, std::size_t size)
{
    if (!input) return RF455MapLoad::MissingInput;
    Cursor nd{static_cast<const unsigned char*>(input), size};

    // Stage the complete overlay before touching any base labels.
    std::vector<std::pair<char*, const unsigned char*>> fixedText;
    std::vector<std::pair<RF455MapLabel*, std::vector<unsigned char>>> layerText;
    std::array<std::uint32_t, 2> layerCounts{};
    try {
        catalog.localizedCount = nd.u32();
        if (catalog.localizedCount != catalog.count) return RF455MapLoad::LocalizedCount;
        for (std::uint32_t i = 0; i < catalog.count; ++i) {
            auto& row = catalog.maps[i];
            fixedText.emplace_back(row.pName_UI, nd.text(64));
            for (std::uint32_t j = 0; j < row.byPortalNum; ++j)
                fixedText.emplace_back(row.pPortalInfo[j].pDesc, nd.text(64));
            for (std::uint32_t j = 0; j < row.byAreaNum; ++j)
                fixedText.emplace_back(row.pAreaInfo[j].pName, nd.text(64));
        }
        for (std::size_t i = 0; i < catalog.layers.size(); ++i) {
            layerCounts[i] = nd.u32();
            for (auto& layer : catalog.layers[i]) {
                for (auto& label : layer.labels) {
                    const auto length = nd.u32();
                    if (length > 64) throw std::runtime_error("455 layer text overflow domain");
                    const auto* bytes = nd.text(length);
                    layerText.emplace_back(&label, std::vector<unsigned char>(bytes, bytes + length));
                }
            }
        }
    } catch (const std::runtime_error&) {
        return RF455MapLoad::Malformed;
    } catch (const std::bad_alloc&) {
        return RF455MapLoad::Malformed;
    } catch (const std::length_error&) {
        return RF455MapLoad::Malformed;
    }

    for (const auto& entry : fixedText) std::memcpy(entry.first, entry.second, 64);
    for (auto& entry : layerText) entry.first->text = std::move(entry.second);
    catalog.localizedLayerCounts = layerCounts;
    catalog.localizedConsumed = nd.at;
    return RF455MapLoad::Complete;
}
}

RF455MapLoad RF455_ParseMapData(RF455MapData& out, const void* mainInput, std::size_t mainSize,
                               const void* localizedInput, std::size_t localizedSize)
{
    if (!mainInput || !localizedInput) return RF455MapLoad::MissingInput;
    RF455MapData next;
    const auto base = parseCatalog(next, mainInput, mainSize);
    if (base != RF455MapLoad::Complete) return base;
    const auto text = applyLocalization(next, localizedInput, localizedSize);
    if (text != RF455MapLoad::Complete) return text;
    next.localizationStatus = text;
    out = std::move(next);
    return RF455MapLoad::Complete;
}

RF455MapLoad RF455_LoadMapData(RF455MapData& out, const char* mainFile, const char* localizedFile)
{
    // Client 455 x86 RVA 0x3CAAE0 reads the map catalog and its localized
    // overlay from loose EDF files. Each load owns its decoded map data.
    constexpr std::uint64_t maxBytes = 64u * 1024u * 1024u;
    auto* cache = RF455_GetCharacterRfsCache();
    std::vector<unsigned char> decoded;
    {
        const auto base = cache->ReadLooseBytes(mainFile, maxBytes);
        if (base.status != RF455ResourceReadStatus::Ready || !base.bytes)
            return RF455MapLoad::MissingInput;
        if (!RF455_DecodeEdf(base.bytes->data(), base.bytes->size(), decoded))
            return RF455MapLoad::Malformed;
    }

    RF455MapData next;
    const auto base = parseCatalog(next, decoded.data(), decoded.size());
    if (base != RF455MapLoad::Complete) return base;

    const auto text = cache->ReadLooseBytes(localizedFile, maxBytes);
    if (text.status == RF455ResourceReadStatus::Ready && text.bytes) {
        decoded.clear();
        next.localizationStatus = RF455_DecodeEdf(text.bytes->data(), text.bytes->size(), decoded)
            ? applyLocalization(next, decoded.data(), decoded.size()) : RF455MapLoad::Malformed;
    }
    const bool localized = next.localizationStatus == RF455MapLoad::Complete;
    out = std::move(next);
    return localized ? RF455MapLoad::Complete : RF455MapLoad::BaseOnly;
}

const RF455MapInfo* RF455_FindMapByCode(const RF455MapData& catalog, std::uint32_t code)
{
    if (!catalog.maps) return nullptr;
    // RVA 0x3CA450 matches the stored map code in file order.
    for (std::uint32_t index = 0; index < catalog.count; ++index) {
        const auto& map = catalog.maps[index];
        if (map.byIndex == code) return &map;
    }
    return nullptr;
}

const RF455MapInfo* RF455_FindMapByName(const RF455MapData& catalog, const char* name)
{
    if (!catalog.maps || !name || !*name) return nullptr;
    // RVA 0x3CA360 compares internal names, returning the first match.
    for (std::uint32_t index = 0; index < catalog.count; ++index) {
        const auto& map = catalog.maps[index];
        if (std::memchr(map.pName, 0, sizeof(map.pName)) && _stricmp(map.pName, name) == 0)
            return &map;
    }
    return nullptr;
}

namespace {
template<std::size_t N>
std::size_t mapField(const std::vector<unsigned char>& source, unsigned char (&field)[N])
{
    const std::size_t size = source.size() < N - 1 ? source.size() : N - 1;
    if (size) std::memcpy(field, source.data(), size);
    field[size] = 0;
    return std::strlen(reinterpret_cast<const char*>(field));
}

std::uint32_t mapRunLength(const unsigned char* run)
{
    return 1u + run[0] + (static_cast<std::uint32_t>(run[1]) << 8);
}

const RF455MapLayer* localMapLayer(const RF455MapData& catalog, std::uint32_t index)
{
    if (index == 0xff || !catalog.maps || index >= catalog.count) return nullptr;
    const auto& name = catalog.maps[index].pName;
    return std::memchr(name, 0, sizeof(name)) ?
        RF455_FindMapLayer(catalog, RF455MapLayerSection::Minimap, name) : nullptr;
}

const char* validatedMapLabel(const RF455MapLayer* layer, std::size_t index)
{
    if (!layer || index >= layer->labels.size()) return nullptr;
    const auto& text = layer->labels[index].text;
    if (text.empty() || text.size() > 64 || !text.front() ||
        !std::memchr(text.data(), 0, text.size()))
        return nullptr;
    return reinterpret_cast<const char*>(text.data());
}
}

const RF455MapLayer* RF455_FindMapLayer(const RF455MapData& catalog, RF455MapLayerSection section,
                                      const char* name)
{
    if (!name || !*name) return nullptr;
    const auto index = static_cast<std::size_t>(section);
    if (index >= catalog.layers.size()) return nullptr;

    // RVA 0x3B42D0 compares names in file order using the current CRT codepage.
    for (const auto& layer : catalog.layers[index]) {
        unsigned char candidate[33];
        mapField(layer.name, candidate);
        if (_mbsicmp(candidate, reinterpret_cast<const unsigned char*>(name)) == 0)
            return &layer;
    }
    return nullptr;
}

int RF455_FindMapLayerLabel(const RF455MapLayer& layer, const char* text)
{
    if (!text || !*text) return -1;
    // RVA 0x3B37D0 compares localized text and returns the zero-based ordinal.
    for (std::size_t index = 0; index < layer.labels.size(); ++index) {
        unsigned char candidate[65];
        mapField(layer.labels[index].text, candidate);
        if (_mbsicmp(candidate, reinterpret_cast<const unsigned char*>(text)) == 0)
            return static_cast<int>(index);
    }
    return -1;
}

const char* RF455_FindLocalMapLabel(const RF455MapData& catalog, std::uint32_t mapIndex,
                                   std::uint16_t ordinal)
{
    // RVA 0x3B43D0 / 0x3B3790 indexes the chosen layer's labels directly.
    return validatedMapLabel(localMapLayer(catalog, mapIndex), ordinal);
}

const RF455MapLayer* RF455_FindWorldMapParent(const RF455MapData& catalog, const char* label, int* ordinal)
{
    if (ordinal) *ordinal = -1;
    if (!label || !*label) return nullptr;
    // RVA 0x3B44E0 takes the first world layer containing the localized name.
    for (const auto& layer : catalog.layers[static_cast<std::size_t>(RF455MapLayerSection::World)]) {
        const int index = RF455_FindMapLayerLabel(layer, label);
        if (index >= 0) {
            if (ordinal) *ordinal = index;
            return &layer;
        }
    }
    return nullptr;
}

bool RF455_WorldMapSpritePath(const RF455MapLayer& layer, char* output, std::size_t capacity)
{
    constexpr char prefix[] = "./SpriteImage/Common/worldmap/";
    constexpr char extension[] = ".spr";
    unsigned char name[33];
    const std::size_t length = mapField(layer.name, name);
    const std::size_t pathBytes = sizeof(prefix) - 1 + length + sizeof(extension);
    if (!output || !length || capacity < pathBytes) return false;

    for (std::size_t i = 0; i < length; ++i) {
        const unsigned char c = name[i];
        if (!(c >= 'a' && c <= 'z') && !(c >= 'A' && c <= 'Z') &&
            !(c >= '0' && c <= '9') && c != '_' && c != '-') return false;
    }

    std::memcpy(output, prefix, sizeof(prefix) - 1);
    std::memcpy(output + sizeof(prefix) - 1, name, length);
    std::memcpy(output + sizeof(prefix) - 1 + length, extension, sizeof(extension));
    return true;
}

bool RF455MapHitMask::load(const RF455MapLayer& layer)
{
    if (layer_ == &layer && !pixels_.empty()) return true;

    constexpr std::size_t maxMaskBytes = 16 * 1024 * 1024;
    if (!layer.width || !layer.height || layer.width > maxMaskBytes / layer.height ||
        layer.image.empty() || layer.image.size() % 3 != 0) return false;
    const std::size_t total = static_cast<std::size_t>(layer.width) * layer.height;

    // RVA 0x3B34F0 expands a little-endian WORD plus one copies of the byte.
    // Validate the entire stream before allocating or changing the active mask.
    std::size_t written = 0;
    for (std::size_t at = 0; at < layer.image.size(); at += 3) {
        const auto count = mapRunLength(layer.image.data() + at);
        if (count > total - written) return false;
        written += count;
    }
    if (written != total) return false;

    std::vector<unsigned char> next;
    try {
        next.resize(total);
    } catch (const std::bad_alloc&) {
        return false;
    }
    written = 0;
    for (std::size_t at = 0; at < layer.image.size(); at += 3) {
        const auto count = mapRunLength(layer.image.data() + at);
        std::memset(next.data() + written, layer.image[at + 2], count);
        written += count;
    }
    pixels_.swap(next);
    width_ = layer.width;
    height_ = layer.height;
    labelCount_ = layer.labels.size();
    layer_ = &layer;
    return true;
}

int RF455MapHitMask::hit(std::uint32_t x, std::uint32_t y) const
{
    if (x >= width_ || y >= height_ || pixels_.empty()) return -1;
    const auto index = pixels_[static_cast<std::size_t>(y) * width_ + x];
    // RVA 0x3B3670 sign-extends the byte before checking the label count.
    return index < 0x80 && index < labelCount_ ? index : -1;
}

void RF455MapHitMask::clear()
{
    layer_ = nullptr;
    width_ = height_ = 0;
    labelCount_ = 0;
    std::vector<unsigned char>().swap(pixels_);
}

bool RF455LocalMapLayer::select(const RF455MapData& catalog, std::uint32_t mapIndex)
{
    // RVA 0x3CA010 reaches the selected map record's internal name (+4).
    const auto* candidate = localMapLayer(catalog, mapIndex);
    if (!candidate || !mask_.load(*candidate)) {
        clear();
        return false;
    }
    layer_ = candidate;
    return true;
}

const char* RF455LocalMapLayer::labelAt(float x, float y) const
{
    if (!layer_ || !(x >= 0.0f && x < 1.0f && y >= 0.0f && y < 1.0f)) return nullptr;
    const auto column = static_cast<std::uint32_t>(static_cast<double>(layer_->width) * x);
    const auto row = static_cast<std::uint32_t>(static_cast<double>(layer_->height) * y);
    const int index = mask_.hit(column, row);
    return index < 0 ? nullptr : labelAt(static_cast<std::size_t>(index));
}

const char* RF455LocalMapLayer::labelAt(std::size_t index) const
{
    return validatedMapLabel(layer_, index);
}

void RF455LocalMapLayer::clear()
{
    layer_ = nullptr;
    mask_.clear();
}
