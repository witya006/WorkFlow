#pragma once
#include <cstddef>
// Target IDs are independent of the legacy UI's differently numbered groups.
const char* RF455_SpriteFilename(unsigned targetId);
bool RF455_SelectSpritePath(unsigned targetId,char*output,std::size_t capacity);
