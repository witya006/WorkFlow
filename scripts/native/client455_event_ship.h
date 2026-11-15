#ifndef RF455_EVENT_SHIP_H
#define RF455_EVENT_SHIP_H

#include "client455_edf_input.h"
#include "client455_language.h"
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <new>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

struct RF455EventShipRow {
    const unsigned char* data = nullptr;
    std::size_t size = 0;
};

struct RF455EventShipText {
    std::string text;
    std::uint32_t value;
};

class RF455EventShipCatalog {
public:
    // Borrowed rows and strings remain valid until replacement or Clear().
    bool HasBase() const { return baseLoaded; }
    bool HasLocalization() const { return localized; }
    std::size_t Schedule8Count() const { return state.schedule8.size(); }
    std::size_t Port80Count(std::size_t table) const
    {
        return table < state.ports80.size() ? state.ports80[table].size() : 0;
    }
    std::size_t Schedule16Count(std::size_t table) const
    {
        return table < state.schedule16.size() ? state.schedule16[table].size() : 0;
    }
    std::size_t Locale20Count() const { return state.locale20.size(); }
    std::size_t TextCount() const { return state.texts.size(); }

    RF455EventShipRow Schedule8(std::size_t row) const { return Get(state.schedule8, row); }
    // 0x3C9980 selects these tables by race and rows by transport selector.
    RF455EventShipRow Port80(std::size_t table, std::size_t row) const
    {
        return table < state.ports80.size() ? Get(state.ports80[table], row) : RF455EventShipRow{};
    }
    // The 0x1FDFC0 family uses race and reads hour/minute at +4/+5.
    RF455EventShipRow Schedule16(std::size_t table, std::size_t row) const
    {
        return table < state.schedule16.size() ? Get(state.schedule16[table], row) : RF455EventShipRow{};
    }
    RF455EventShipRow Locale20(std::size_t row) const { return Get(state.locale20, row); }
    const RF455EventShipText* Text(std::size_t row) const
    {
        return row < state.texts.size() ? &state.texts[row] : nullptr;
    }

    bool Load(const char* base, const char* local)
    {
        // Pinned 455 x86 RVA 0x1FD8C0 loads sequential EDF tables.
        State next;
        if (!ReadEdf(base, [&](Cursor& cursor) { return ReadBase(cursor, next); }))
            return false;

        Locale overlay;
        if (!ReadEdf(local, [&](Cursor& cursor) { return ReadLocale(cursor, next, overlay); })) {
            if (!baseLoaded) {
                state = std::move(next);
                baseLoaded = true;
            }
            return false;
        }

        for (std::size_t table = 0; table < next.ports80.size(); ++table) {
            for (std::size_t row = 0; row < next.ports80[table].size(); ++row)
                std::memcpy(next.ports80[table][row].data() + 4, overlay.names[table][row].data(), 64);
        }
        next.locale20 = std::move(overlay.rows20);
        next.texts = std::move(overlay.texts);
        state = std::move(next);
        baseLoaded = localized = true;
        return true;
    }

    void Clear()
    {
        state = State{};
        baseLoaded = localized = false;
    }

private:
    template<std::size_t Size>
    using Rows = std::vector<std::array<unsigned char, Size>>;

    struct State {
        Rows<8> schedule8;
        std::array<Rows<80>, 3> ports80;
        std::array<Rows<16>, 3> schedule16;
        Rows<20> locale20;
        std::vector<RF455EventShipText> texts;
    };
    struct Locale {
        std::array<Rows<64>, 3> names;
        Rows<20> rows20;
        std::vector<RF455EventShipText> texts;
    };

    struct Cursor {
        const std::vector<unsigned char>& plain;
        std::size_t offset = 0;

        std::size_t Remaining() const { return plain.size() - offset; }

        const unsigned char* Take(std::size_t size)
        {
            if (size > Remaining()) return nullptr;
            const auto* first = plain.data() + offset;
            offset += size;
            return first;
        }

        bool Word(std::uint32_t& out)
        {
            const auto* bytes = Take(sizeof(out));
            if (!bytes) return false;
            out = static_cast<std::uint32_t>(bytes[0]) |
                  (static_cast<std::uint32_t>(bytes[1]) << 8) |
                  (static_cast<std::uint32_t>(bytes[2]) << 16) |
                  (static_cast<std::uint32_t>(bytes[3]) << 24);
            return true;
        }

        bool Table(std::uint32_t stride, std::uint32_t& count, const unsigned char*& rows)
        {
            std::uint32_t actualStride;
            if (!Word(count) || !Word(actualStride) || actualStride != stride ||
                count > Remaining() / stride) return false;
            rows = Take(static_cast<std::size_t>(count) * stride);
            return true;
        }

        template<std::size_t Size>
        bool ReadRows(Rows<Size>& out)
        {
            std::uint32_t count;
            const unsigned char* bytes;
            if (!Table(Size, count, bytes)) return false;
            out.resize(count);
            for (std::size_t i = 0; i < count; ++i)
                std::memcpy(out[i].data(), bytes + i * Size, Size);
            return true;
        }
    };

    State state;
    bool baseLoaded = false;
    bool localized = false;

    template<std::size_t Size>
    static RF455EventShipRow Get(const Rows<Size>& rows, std::size_t row)
    {
        return row < rows.size() ? RF455EventShipRow{rows[row].data(), Size} : RF455EventShipRow{};
    }

    template<class Consumer>
    static bool ReadEdf(const char* path, Consumer consume)
    {
        try {
            return RF455_ReadEdfInput(path, [&](const unsigned char* raw, std::size_t size) {
                std::vector<unsigned char> plain;
                if (!RF455_DecodeEdf(raw, size, plain)) return false;
                Cursor cursor{plain};
                return consume(cursor);
            });
        } catch (const std::bad_alloc&) {
            return false;
        } catch (const std::length_error&) {
            return false;
        }
    }

    static bool ReadBase(Cursor& cursor, State& next)
    {
        if (!cursor.ReadRows(next.schedule8)) return false;
        for (auto& table : next.ports80) {
            if (!cursor.ReadRows(table)) return false;
            for (const auto& row : table)
                if (!std::memchr(row.data() + 4, 0, 64)) return false;
        }
        for (auto& table : next.schedule16)
            if (!cursor.ReadRows(table)) return false;
        return cursor.Remaining() == 0;
    }

    static bool ReadLocale(Cursor& cursor, const State& base, Locale& next)
    {
        for (std::size_t table = 0; table < next.names.size(); ++table) {
            auto& names = next.names[table];
            if (!cursor.ReadRows(names) || names.size() != base.ports80[table].size()) return false;
            for (const auto& name : names)
                if (!std::memchr(name.data(), 0, name.size())) return false;
        }
        if (!cursor.ReadRows(next.rows20)) return false;

        std::uint32_t count;
        if (!cursor.Word(count) || !count || count > cursor.Remaining() / 9) return false;
        next.texts.reserve(count);
        for (std::uint32_t i = 0; i < count; ++i) {
            std::uint32_t length, value;
            if (!cursor.Word(length) || !length) return false;
            const auto* text = cursor.Take(length);
            if (!text || text[length - 1] != 0 || !cursor.Word(value)) return false;
            next.texts.push_back({std::string(reinterpret_cast<const char*>(text), length - 1), value});
        }
        return cursor.Remaining() == 0;
    }
};

#endif
