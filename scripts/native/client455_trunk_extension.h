#pragma once

#include "client455_edf_rows.h"
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <vector>

struct RF455TrunkExtensionRow {
    std::array<unsigned char, 44> bytes{};

    std::int32_t MoneyCost() const { return SignedWordAt(4); }
    const char* ItemCode() const
    {
        return MoneyCost() > 0 ? nullptr : reinterpret_cast<const char*>(bytes.data() + 8);
    }
    std::int32_t ItemQuantity() const { return SignedWordAt(40); }

private:
    std::int32_t SignedWordAt(std::size_t offset) const
    {
        const auto word = rf455_edf_rows::Word(bytes.data() + offset);
        std::int32_t value;
        std::memcpy(&value, &word, sizeof(value));
        return value;
    }
};

class RF455TrunkExtensionCatalog {
public:
    bool Load(const char* path)
    {
        // 455 x86 RVA 0x84AA0 reads TrunkExted. At 0x85F80 and 0x879F0,
        // the current storehouse stage selects a row by position.
        return rf455_edf_rows::ReadRows(path, rows_, [](const RF455TrunkExtensionRow& row) {
            const auto* code = row.ItemCode();
            return !code || std::memchr(code, 0, 32) != nullptr;
        });
    }

    void Clear() { std::vector<RF455TrunkExtensionRow>().swap(rows_); }
    std::size_t Size() const { return rows_.size(); }

    // Rows remain valid until the next successful load or Clear().
    const RF455TrunkExtensionRow* At(std::size_t stage) const
    {
        return stage < rows_.size() ? &rows_[stage] : nullptr;
    }

private:
    std::vector<RF455TrunkExtensionRow> rows_;
};
