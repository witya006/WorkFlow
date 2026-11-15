#ifndef RF455_EDF_INPUT_H
#define RF455_EDF_INPUT_H

#include "client455_character_rfs.h"
#include <cstdio>
#include <memory>
#include <vector>

// 455 x86 RVA 0x1EEC90 opens a loose EDF. Small files use an immutable
// byte lease. Unretained large files keep the signed-length stdio path.
// The consumer parses synchronously and owns any data it keeps.
template<class Consumer>
bool RF455_ReadEdfInput(const char* path, Consumer&& consume)
{
    if (!path || !*path) return false;
    auto* cache = RF455_GetCharacterRfsCache();
    constexpr std::size_t maxCachedBytes = 8u * 1024u * 1024u;
    const auto budget = cache->ByteBudget();
    const auto limit = budget < maxCachedBytes ? budget : maxCachedBytes;
    if (limit) {
        const auto source = cache->ReadLooseBytes(path, limit);
        if (source.status == RF455ResourceReadStatus::Ready && source.bytes) {
            try {
                if (consume(source.bytes->data(), source.bytes->size())) return true;
            } catch (...) {
                cache->RemoveLooseBytes(path);
                throw;
            }
            cache->RemoveLooseBytes(path);
            return false;
        }
        if (source.status != RF455ResourceReadStatus::ReadError || source.declaredSize <= limit)
            return false;
    }

    std::unique_ptr<FILE, decltype(&std::fclose)> file(std::fopen(path, "rb"), &std::fclose);
    if (!file || std::fseek(file.get(), 0, SEEK_END)) return false;
    const auto length = std::ftell(file.get());
    if (length < 0 || std::fseek(file.get(), 0, SEEK_SET)) return false;
    std::vector<unsigned char> bytes(static_cast<std::size_t>(length));
    if (!bytes.empty() && std::fread(bytes.data(), 1, bytes.size(), file.get()) != bytes.size())
        return false;
    return consume(bytes.data(), bytes.size());
}

#endif
