#include "client455_resource_io.h"
#include <cstdlib>
#include <cstring>
#include <io.h>
#include <limits>
#include <memory>

namespace {
template <typename OpenMember>
bool visitResourceMembers(char* path, OpenMember open)
{
    auto* activeGroup = RF455_GetResourceGroup();
    if (RF455_GetResourceArchiveEnabled() && activeGroup) {
        _strlwr(path);
        if (activeGroup->archives && strlen(path) > activeGroup->prefixLength) {
            const char* member = path + activeGroup->prefixLength;
            for (DWORD i = 0; i < activeGroup->count; ++i) {
                const auto& archive = activeGroup->archives[i];
                const LONG offset = archive.LookupOffset(0, member);
                if (offset < 0) continue;
                const auto begin = std::uint64_t(archive.payloadBase) + offset;
                // The serialized declared size can be stale. The next
                // distinct member start is the bounded reader's upper limit.
                if (open(archive.filename, begin, archive.NextMemberOffset(offset))) return true;
            }
        }
    }
    return false;
}
}

RF455ResourceRead RF455_ReadResourceBytes(char* path,std::uint64_t maxBytes,bool* fromArchive) {
    if (fromArchive) *fromArchive = false;
    if (!path || !*path) return {};
    auto* cache = RF455_GetCharacterRfsCache();
    RF455ResourceRead result;
    if (visitResourceMembers(path, [&](const char* archive, std::uint64_t begin, std::uint64_t end) {
        result = cache->ReadRpkMemberBytes(archive, begin, end, maxBytes);
        return result.status != RF455ResourceReadStatus::Unavailable;
    })) {
        if (fromArchive) *fromArchive = true;
        return result;
    }
    return cache->ReadLooseBytes(path, maxBytes);
}

FILE* RF455_OpenResourceTextStream455(char* path, std::uint64_t& archiveBytes)
{
    archiveBytes = (std::numeric_limits<std::uint64_t>::max)();
    if (!path || !*path) return nullptr;
    FILE* result = nullptr;
    if (visitResourceMembers(path, [&](const char* archive, std::uint64_t begin, std::uint64_t end) {
        std::unique_ptr<FILE, decltype(&std::fclose)> stream(std::fopen(archive, "rb"), std::fclose);
        if (!stream) return false;
        const auto length = _filelengthi64(_fileno(stream.get()));
        if (length < 0 || begin > static_cast<std::uint64_t>(length) ||
            (end && (end <= begin || end > static_cast<std::uint64_t>(length))) ||
            _fseeki64(stream.get(), static_cast<__int64>(begin), SEEK_SET)) return true;
        archiveBytes = (end ? end : static_cast<std::uint64_t>(length)) - begin;
        result = stream.release();
        return true;
    })) return result;
    return std::fopen(path, "rt");
}
