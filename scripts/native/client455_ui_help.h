#pragma once

#include "client455_edf_input.h"
#include "client455_language.h"
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <new>
#include <stdexcept>
#include <string>
#include <vector>

struct RF455UiHelpFragment {
    std::array<unsigned char, 12> font{};
    std::string text;
};

struct RF455UiHelpPage {
    std::uint32_t id = 0;
    std::uint32_t window = 0;
    std::uint32_t section = 0;
    std::vector<RF455UiHelpFragment> fragments;
};

constexpr unsigned RF455_UI_HELP_GROUPS = 122;
using RF455UiHelpGroups = std::array<std::vector<RF455UiHelpPage>, RF455_UI_HELP_GROUPS>;

namespace rf455_ui_help_detail {
class Reader {
public:
    explicit Reader(const std::vector<unsigned char>& payload)
        : data_(payload.data()), remaining_(payload.size()) {}

    std::size_t remaining() const { return remaining_; }

    bool readGroup(std::vector<RF455UiHelpPage>& pages)
    {
        const auto* size = take(4);
        if (!size) return false;
        const auto count = read32(size);
        if (count > remaining_ / 13) return false;

        pages.resize(count);
        for (auto& page : pages) {
            const auto* header = take(13);
            if (!header || header[12] > remaining_ / 14) return false;
            page.id = read32(header);
            page.window = read32(header + 4);
            page.section = read32(header + 8);
            page.fragments.resize(header[12]);

            for (auto& fragment : page.fragments) {
                const auto* fields = take(14);
                if (!fields) return false;
                const std::size_t length = std::size_t(fields[12]) | (std::size_t(fields[13]) << 8);
                std::memcpy(fragment.font.data(), fields, fragment.font.size());
                if (length) {
                    const auto* text = take(length);
                    if (!text) return false;
                    fragment.text.assign(reinterpret_cast<const char*>(text), length);
                }
            }
        }
        return true;
    }

private:
    const unsigned char* data_;
    std::size_t remaining_;

    const unsigned char* take(std::size_t size)
    {
        if (size > remaining_) return nullptr;
        const auto* start = data_;
        data_ += size;
        remaining_ -= size;
        return start;
    }

    static std::uint32_t read32(const unsigned char* bytes)
    {
        return std::uint32_t(bytes[0]) | (std::uint32_t(bytes[1]) << 8) |
            (std::uint32_t(bytes[2]) << 16) | (std::uint32_t(bytes[3]) << 24);
    }
};

template<class Output, class Parse>
bool load(const char* path, Output& output, Parse parse)
{
    try {
        return RF455_ReadEdfInput(path, [&](const unsigned char* bytes, std::size_t size) {
            std::vector<unsigned char> plain;
            if (!RF455_DecodeEdf(bytes, size, plain)) return false;
            Reader reader(plain);
            Output next;
            if (!parse(reader, next)) return false;
            output.swap(next);
            return true;
        });
    } catch (const std::bad_alloc&) {
        return false;
    } catch (const std::length_error&) {
        return false;
    }
}
} // namespace rf455_ui_help_detail

// 455 x86 RVAs 0x097720 and 0x0999A0. Some shipped files end with fewer
// groups than the owner holds, leaving the unrepresented groups empty.
inline bool RF455_LoadUiHelp(const char* path, RF455UiHelpGroups& groups)
{
    return rf455_ui_help_detail::load(path, groups, [](auto& reader, auto& next) {
        for (auto& group : next) {
            if (!reader.readGroup(group)) return false;
            if (!reader.remaining()) return true;
        }
        return false;
    });
}

// RVA 0x1F0680 consumes just the first, nonempty group.
inline bool RF455_LoadUiHelp(const char* path, std::vector<RF455UiHelpPage>& pages)
{
    return rf455_ui_help_detail::load(path, pages, [](auto& reader, auto& next) {
        return reader.readGroup(next) && !next.empty();
    });
}
