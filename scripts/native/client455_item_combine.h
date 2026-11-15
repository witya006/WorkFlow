#pragma once

#include "client455_edf_rows.h"
#include <cstddef>
#include <new>
#include <stdexcept>
#include <vector>

class RF455ItemCombineCatalog {
public:
    static constexpr std::size_t RecipeWidth = 128;
    static constexpr std::size_t IngredientGroupWidth = 1208;

    RF455ItemCombineCatalog() = default;
    RF455ItemCombineCatalog(const RF455ItemCombineCatalog&) = delete;
    RF455ItemCombineCatalog& operator=(const RF455ItemCombineCatalog&) = delete;

    bool Load(const char* path)
    {
        // 455 x86 RVA 0x10ED70 reads two consecutive count/stride blocks.
        // The recipe consumer at 0x10FCA0 resolves a group by row ordinal.
        try {
            return RF455_ReadEdfInput(path, [&](const unsigned char* envelope, std::size_t size) {
                std::vector<unsigned char> decoded;
                if (!RF455_DecodeEdf(envelope, size, decoded)) return false;

                Section recipes, groups;
                std::size_t offset = 0;
                if (!ReadSection(decoded, offset, RecipeWidth, recipes) ||
                    !ReadSection(decoded, offset, IngredientGroupWidth, groups)) return false;

                // The fixed-block reader ignores bytes beyond these sections.
                bytes_.swap(decoded);
                recipes_ = recipes;
                groups_ = groups;
                return true;
            });
        } catch (const std::bad_alloc&) {
            return false;
        } catch (const std::length_error&) {
            return false;
        }
    }

    void Clear()
    {
        std::vector<unsigned char>().swap(bytes_);
        recipes_ = {};
        groups_ = {};
    }

    std::size_t RecipeCount() const { return recipes_.count; }
    std::size_t IngredientGroupCount() const { return groups_.count; }

    // Returns a borrowed row of the corresponding width, valid until the
    // next successful load or Clear(). An out-of-range index returns null.
    const unsigned char* RecipeAt(std::size_t index) const
    {
        return index < recipes_.count ? bytes_.data() + recipes_.offset + index * RecipeWidth : nullptr;
    }

    const unsigned char* IngredientGroupAt(std::size_t index) const
    {
        return index < groups_.count ? bytes_.data() + groups_.offset + index * IngredientGroupWidth : nullptr;
    }

private:
    struct Section {
        std::size_t offset = 0;
        std::size_t count = 0;
    };

    static bool ReadSection(const std::vector<unsigned char>& bytes, std::size_t& offset,
        std::size_t width, Section& section)
    {
        constexpr std::size_t headerSize = 8;
        if (bytes.size() - offset < headerSize) return false;
        const auto* header = bytes.data() + offset;
        const std::size_t count = rf455_edf_rows::Word(header);
        offset += headerSize;
        if (!count || rf455_edf_rows::Word(header + 4) != width ||
            count > (bytes.size() - offset) / width) return false;

        section = {offset, count};
        offset += count * width;
        return true;
    }

    std::vector<unsigned char> bytes_;
    Section recipes_;
    Section groups_;
};
