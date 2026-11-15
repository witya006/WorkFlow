#ifndef RF455_ITEM_TEXT_H
#define RF455_ITEM_TEXT_H

#include "client455_item_payloads.h"
#include <cstddef>
#include <cstring>
#include <windows.h>

inline std::size_t RF455_AppendTooltipLines455(const RF455RewardTooltip& text,
                                               unsigned codepage, char (*lines)[64],
                                               std::size_t capacity)
{
    if (!lines || !capacity) return 0;
    std::size_t count = 0;
    for (const auto* part : {&text.name, &text.description}) {
        std::size_t lineSize = 0;
        for (std::size_t i = 0; i < part->size() && count < capacity;) {
            const auto byte = static_cast<unsigned char>((*part)[i]);
            if (byte == '\r' || byte == '\n') {
                if (lineSize) lines[count++][lineSize] = '\0';
                lineSize = 0;
                ++i;
                continue;
            }
            const std::size_t width = IsDBCSLeadByteEx(codepage, byte) ? 2u : 1u;
            if (width > part->size() - i) break;
            if (lineSize + width >= sizeof(lines[0])) {
                lines[count++][lineSize] = '\0';
                lineSize = 0;
                if (count == capacity) break;
            }
            std::memcpy(lines[count] + lineSize, part->data() + i, width);
            lineSize += width;
            i += width;
        }
        if (lineSize && count < capacity) lines[count++][lineSize] = '\0';
    }
    return count;
}

#endif
