#ifndef RF455_CHARACTER_RFS_H
#define RF455_CHARACTER_RFS_H
#include <cstdint>
#include <cstdio>
#include <map>
#include <list>
#include <memory>
#include <set>
#include <string>
#include <vector>

struct RF455CharacterRfsEntry {std::string archive;std::uint32_t offset,size;};
using RF455ResourceBytes=std::shared_ptr<const std::vector<unsigned char>>;
enum class RF455ResourceReadStatus {Unavailable,Ready,ReadError,MemoryError};
struct RF455ResourceRead {
    RF455ResourceReadStatus status=RF455ResourceReadStatus::Unavailable;
    RF455ResourceBytes bytes;
    std::uint64_t declaredSize=0;
};
struct RF455ResourceCacheStats {
    std::uint64_t hits=0,misses=0,payloadReads=0,bytesRead=0,evictions=0;
    std::size_t retainedBytes=0,entries=0;
};
// Client Character RFS, distinct from the R3Engine RPK resource group. The
// container layout is owned; it is not the old std::map binary ABI.
class RF455CharacterRfsCache {
    std::map<std::string,RF455CharacterRfsEntry> files;
    std::set<std::string> directories;
    struct Payload {RF455ResourceBytes bytes;std::list<std::string>::iterator age;};
    std::map<std::string,Payload> payloads;
    std::list<std::string> recent;
    std::size_t byteBudget=64u*1024u*1024u;
    RF455ResourceCacheStats stats;
    enum class IndexLoad {NotOpened,RejectedPath,Malformed,Loaded};
    IndexLoad loadArchive(const std::string& directory,const std::string& file,bool infoMode,
        std::map<std::string,RF455CharacterRfsEntry>& staged);
    const RF455CharacterRfsEntry* findEntry(const char* path);
    enum class PayloadExtent { ExactSize, ToEnd, ToNextMember };
    RF455ResourceRead readPayload(const std::string& key,const std::string& file,
        std::uint64_t offset,std::uint64_t extent,PayloadExtent extentKind,std::uint64_t maxBytes);
    void erasePayload(std::map<std::string,Payload>::iterator entry) noexcept;
    void evictOldest();
    void retain(const std::string& key,const RF455ResourceBytes& bytes);
public:
    RF455CharacterRfsCache()=default;
    RF455CharacterRfsCache(const RF455CharacterRfsCache&)=delete;
    RF455CharacterRfsCache& operator=(const RF455CharacterRfsCache&)=delete;
    static std::string Normalize(const char* path);
    bool LoadDirectory(const std::string& normalizedDirectory);
    FILE* Open(const char* path,std::uint32_t* declaredSize);
    // Sized readers share immutable payloads, never FILE positions or GPU state.
    // Callers choose fallback: an opened-but-invalid archive is not Unavailable.
    RF455ResourceRead ReadArchiveBytes(const char* path);
    // The caller's size limit also applies to already cached data.
    RF455ResourceRead ReadLooseBytes(const char* path,std::uint64_t maxBytes=0xffffffffu);
    // Release the retained loose bytes after a consumer rejects their format.
    // Other entries and already leased bytes remain valid.
    void RemoveLooseBytes(const char* path) noexcept;
    // Discard exactly the rejected retained payload, regardless of its origin.
    // A stale lease cannot remove replacement bytes from a subsequent read.
    void RemovePayloadBytes(const RF455ResourceBytes& bytes) noexcept;
    // A zero end denotes the final member of an RPK archive.
    RF455ResourceRead ReadRpkMemberBytes(const char* archive,std::uint64_t start,
                                       std::uint64_t end,std::uint64_t maxBytes);
    // Refresh only payloads for this RPK file after its group is replaced.
    // Already issued leases remain valid.
    void RemoveRpkArchiveBytes(const char* path) noexcept;
    // Single-owner thread. Files are immutable within a cache generation.
    // Clear refreshes both indexes and payloads after on-disk resource changes.
    // Evicted/cleared bytes remain alive while callers hold their shared lease.
    // Budget limits retained payload capacity, not leases, scratch or index memory;
    // metadata is additionally capped at 4096 payload entries. Oversize reads are
    // uncached. Zero budget disables retention. Empty payloads are not retained.
    void SetByteBudget(std::size_t bytes);
    std::size_t ByteBudget()const{return byteBudget;}
    RF455ResourceCacheStats Stats()const{return stats;}
    // Does NOT refresh archive indexes; use Clear if archive layout changed.
    void ClearPayloads();
    void ResetStats();
    // Explicit cache reset for owner/test lifecycle; not automatically attached
    // to renderer reset. Reference global cache teardown is not reconstructed.
    void Clear(){ClearPayloads();files.clear();directories.clear();}
    std::size_t FileCount()const{return files.size();}
    std::size_t DirectoryCount()const{return directories.size();}
};
RF455CharacterRfsCache* RF455_SetCharacterRfsCache(RF455CharacterRfsCache* cache);
RF455CharacterRfsCache* RF455_GetCharacterRfsCache();
#endif
