#pragma once

#include "client455_edf_input.h"
#include "client455_language.h"
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <new>
#include <stdexcept>
#include <tuple>
#include <vector>

namespace rf455_edf_rows {
inline std::uint32_t Word(const unsigned char* bytes)
{
    return std::uint32_t(bytes[0]) | (std::uint32_t(bytes[1]) << 8) |
        (std::uint32_t(bytes[2]) << 16) | (std::uint32_t(bytes[3]) << 24);
}

template<class Row, class Consumer>
bool ReadRows(const char* path, std::vector<Row>& output, Consumer consume)
{
    try {
        return RF455_ReadEdfInput(path, [&](const unsigned char* envelope, std::size_t size) {
            std::vector<unsigned char> plain;
            if (!RF455_DecodeEdf(envelope, size, plain) || plain.size() < 8) return false;
            const std::size_t count = Word(plain.data());
            constexpr auto stride = std::tuple_size<decltype(Row::bytes)>::value;
            static_assert(stride != 0, "EDF row width must be positive");
            const std::size_t body = plain.size() - 8;
            if (Word(plain.data() + 4) != stride || count > body / stride || count * stride != body)
                return false;
            std::vector<Row> next(count);
            for (std::size_t row = 0; row < count; ++row) {
                auto& entry = next[row];
                std::memcpy(entry.bytes.data(), plain.data() + 8 + row * stride, stride);
                if (!consume(entry)) return false;
            }
            output.swap(next);
            return true;
        });
    } catch (const std::bad_alloc&) {
        return false;
    } catch (const std::length_error&) {
        return false;
    }
}
} // namespace rf455_edf_rows
