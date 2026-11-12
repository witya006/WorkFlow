#include "client455_map_data.h"
#include "client455_language.h"
#include <windows.h>
#include <cstdio>
#include <cstring>
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

bool file(const char* name, std::vector<unsigned char>& out)
{
    if (!name) return false;
    HANDLE h = CreateFileA(name, GENERIC_READ, FILE_SHARE_READ, nullptr, OPEN_EXISTING,
                           FILE_ATTRIBUTE_NORMAL, nullptr);
    if (h == INVALID_HANDLE_VALUE) return false;
    LARGE_INTEGER size = {};
    bool ok = GetFileSizeEx(h, &size) && size.QuadPart >= 0 && size.QuadPart < 0x80000000;
    try {
        if (ok) out.resize(static_cast<std::size_t>(size.QuadPart));
    } catch (...) {
        CloseHandle(h);
        throw;
    }
    DWORD got = 0;
    if (ok) ok = ReadFile(h, out.data(), static_cast<DWORD>(out.size()), &got, nullptr) && got == out.size();
    CloseHandle(h);
    return ok;
}

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
            src.read(row.pName, sizeof(row.pName));
            std::memcpy(row.pName_UI, row.pName, sizeof(row.pName));
            src.read(row.pFileName, sizeof(row.pFileName));

            char sprite[128];
            src.read(sprite, sizeof(sprite));
            const auto* end = static_cast<const char*>(std::memchr(sprite, 0, sizeof(sprite)));
            if (!end || std::size_t(end - sprite) + 25 >= sizeof(row.pMinimapFileName))
                throw std::runtime_error("455 minimap path overflow domain");
            std::sprintf(row.pMinimapFileName, "./SpriteImage/Common/Map/%s", sprite);
            src.read(&row.wMinimapAngle, 2);
            src.read(row.fields358, sizeof(row.fields358));

            row.byPortalNum = src.u32();
            src.count(row.byPortalNum, 288);
            if (row.byPortalNum) row.pPortalInfo = new RF455PortalInfo[row.byPortalNum];
            for (std::uint32_t j = 0; j < row.byPortalNum; ++j) {
                auto& portal = row.pPortalInfo[j];
                src.read(static_cast<RF455MineInfo*>(&portal), 96);
                src.read(&portal.byPortalType, 8);
                src.read(portal.byUsableRace, 5);
                src.read(portal.pName, 64);
                src.read(portal.pDesc, 64);
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
                src.read(row.pAreaInfo, row.byAreaNum * 84u);
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
            fixedText.emplace_back(row.pName_UI, nd.take(64));
            for (std::uint32_t j = 0; j < row.byPortalNum; ++j)
                fixedText.emplace_back(row.pPortalInfo[j].pDesc, nd.take(64));
            for (std::uint32_t j = 0; j < row.byAreaNum; ++j)
                fixedText.emplace_back(row.pAreaInfo[j].pName, nd.take(64));
        }
        for (std::size_t i = 0; i < catalog.layers.size(); ++i) {
            layerCounts[i] = nd.u32();
            for (auto& layer : catalog.layers[i]) {
                for (auto& label : layer.labels) {
                    const auto length = nd.u32();
                    if (length > 64) throw std::runtime_error("455 layer text overflow domain");
                    layerText.emplace_back(&label, nd.bytes(length));
                }
            }
        }
    } catch (const std::runtime_error&) {
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
    std::vector<unsigned char> encoded, decoded;
    if (!file(mainFile, encoded)) return RF455MapLoad::MissingInput;
    if (!RF455_DecodeEdf(encoded.data(), encoded.size(), decoded)) return RF455MapLoad::Malformed;

    RF455MapData next;
    const auto base = parseCatalog(next, decoded.data(), decoded.size());
    if (base != RF455MapLoad::Complete) return base;

    if (file(localizedFile, encoded)) {
        decoded.clear();
        next.localizationStatus = RF455_DecodeEdf(encoded.data(), encoded.size(), decoded)
            ? applyLocalization(next, decoded.data(), decoded.size()) : RF455MapLoad::Malformed;
    }
    const bool localized = next.localizationStatus == RF455MapLoad::Complete;
    out = std::move(next);
    return localized ? RF455MapLoad::Complete : RF455MapLoad::BaseOnly;
}
