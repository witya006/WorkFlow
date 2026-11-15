#ifndef RF455_SHOP_COLLECTION_H
#define RF455_SHOP_COLLECTION_H

#include "client455_edf_rows.h"
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <vector>

struct RF455SpecialStoreProduct {
    std::uint32_t currencyType;
    std::uint32_t price;
    std::uint32_t kind;
    std::uint32_t catalogIndex;
    std::uint32_t field16;
};

struct RF455SpecialStoreRow {
    std::array<unsigned char, 692> bytes;

    std::uint32_t Index() const { return WordAt(0); }
    const char* Code() const { return reinterpret_cast<const char*>(bytes.data() + 4); }
    const char* CodeSuffix() const { return Code() + 2; }
    std::uint32_t MinimumLevel() const { return WordAt(72); }
    std::uint32_t MaximumLevel() const { return WordAt(76); }
    std::uint32_t MinimumRank() const { return WordAt(80); }
    std::uint32_t ProductCount() const { return WordAt(88); }

    bool ProductAt(std::size_t index, RF455SpecialStoreProduct& product) const
    {
        if (index >= ProductCount() || index >= 30) return false;
        const auto base = 92 + index * 20;
        product = {WordAt(base), WordAt(base + 4), WordAt(base + 8), WordAt(base + 12), WordAt(base + 16)};
        return true;
    }

private:
    std::uint32_t WordAt(std::size_t offset) const
    {
        return rf455_edf_rows::Word(bytes.data() + offset);
    }
};

class RF455SpecialStoreCatalog {
public:
    bool Load(const char* path)
    {
        // Pinned 455 x86 RVA 0x208BE0 reads the common SpecialStore EDF.
        return rf455_edf_rows::ReadRows(path, rows, [](const RF455SpecialStoreRow& row) {
            return row.ProductCount() <= 30 && std::memchr(row.bytes.data() + 6, 0, 62);
        });
    }

    void Clear() { std::vector<RF455SpecialStoreRow>().swap(rows); }
    std::size_t Size() const { return rows.size(); }

    // Row pointers remain valid until the next successful load or Clear().
    const RF455SpecialStoreRow* At(std::size_t row) const
    {
        return row < rows.size() ? &rows[row] : nullptr;
    }

    const RF455SpecialStoreRow* Find(const char* codeSuffix) const
    {
        if (!codeSuffix || strnlen_s(codeSuffix, 62) == 62) return nullptr;
        // Pinned RVA 0x208DF0 compares the case-sensitive suffix in row order.
        for (const auto& row : rows)
            if (std::strcmp(codeSuffix, row.CodeSuffix()) == 0) return &row;
        return nullptr;
    }

private:
    std::vector<RF455SpecialStoreRow> rows;
};

struct RF455ItemCollectionRow {
    std::array<unsigned char, 744> bytes;

    std::uint32_t Index() const { return rf455_edf_rows::Word(bytes.data()); }
    std::uint32_t Field36() const { return rf455_edf_rows::Word(bytes.data() + 36); }
    const char* Name() const { return reinterpret_cast<const char*>(bytes.data() + 40); }
};

class RF455ItemCollectionCatalog {
public:
    // A valid initial base remains available when the locale cannot be applied.
    // Subsequent failures preserve the last published catalog.
    bool Load(const char* base, const char* local)
    {
        using rf455_edf_rows::ReadRows;
        // Pinned x86 RVA 0x1FE520 reads the global table, 0x1FE660 overlays names.
        std::vector<RF455ItemCollectionRow> next;
        if (!ReadRows(base, next, [](const RF455ItemCollectionRow& row) {
            return std::memchr(row.Name(), 0, 64) != nullptr;
        })) return false;
        std::vector<LocalizedName> names;
        if (!ReadRows(local, names, [](const LocalizedName& row) {
            return std::memchr(row.bytes.data(), 0, row.bytes.size()) != nullptr;
        })) {
            if (!baseLoaded) {
                rows.swap(next);
                baseLoaded = true;
            }
            return false;
        }

        const auto count = names.size() < next.size() ? names.size() : next.size();
        for (std::size_t row = 0; row < count; ++row)
            std::memcpy(next[row].bytes.data() + 40, names[row].bytes.data(), names[row].bytes.size());
        rows.swap(next);
        baseLoaded = localized = true;
        return true;
    }

    void Clear()
    {
        std::vector<RF455ItemCollectionRow>().swap(rows);
        baseLoaded = localized = false;
    }

    bool HasBase() const { return baseLoaded; }
    bool HasLocalization() const { return localized; }
    std::size_t Size() const { return rows.size(); }

    // Row pointers remain valid until replacement or Clear().
    const RF455ItemCollectionRow* At(std::size_t row) const
    {
        return row < rows.size() ? &rows[row] : nullptr;
    }

private:
    struct LocalizedName { std::array<unsigned char, 64> bytes; };
    std::vector<RF455ItemCollectionRow> rows;
    bool baseLoaded = false;
    bool localized = false;
};

#endif
