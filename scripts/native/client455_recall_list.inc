#include "client455_character_rfs.h"
#include <cctype>
#include <cstdlib>
#include <cstring>

namespace {
bool readRecallToken455(const unsigned char*& next, std::size_t& remaining, char (&out)[256])
{
    while (remaining && std::isspace(*next)) { ++next; --remaining; }
    if (!remaining) return false;
    const auto* start = next;
    while (remaining && *next && !std::isspace(*next)) { ++next; --remaining; }
    const auto size = static_cast<std::size_t>(next - start);
    if (!size || size >= sizeof(out) || (remaining && !*next)) return false;
    std::memcpy(out, start, size);
    out[size] = 0;
    return true;
}
}

// Client 455 x86 RVA 0x3BF9E0 reads three whitespace-delimited fields per row.
void CAnimusEffect::LoadAEffectList(char* filename)
{
    constexpr std::uint64_t maxBytes = 1024u * 1024u;
    const auto source = RF455_GetCharacterRfsCache()->ReadLooseBytes(filename, maxBytes);
    if (source.status != RF455ResourceReadStatus::Ready || !source.bytes) return;
    auto* next = source.bytes->data();
    auto remaining = source.bytes->size();
    char id[256], level[256], path[256];
    while (readRecallToken455(next, remaining, id) &&
           readRecallToken455(next, remaining, level) &&
           readRecallToken455(next, remaining, path)) {
        LoadEffect(std::atoi(id), std::atoi(level), path);
    }
}
