#pragma once
#include <cstdint>
#include <cstdio>
#include <map>
#include <set>
#include <string>

struct RF455CharacterRfsEntry {std::string archive;std::uint32_t offset,size;};
// Client Character RFS, distinct from the R3Engine RPK resource group. The
// container layout is owned; it is not the old std::map binary ABI.
class RF455CharacterRfsCache {
    std::map<std::string,RF455CharacterRfsEntry> files;
    std::set<std::string> directories;
    bool loadArchive(const std::string& directory,const std::string& file,bool infoMode);
public:
    static std::string Normalize(const char* path);
    bool LoadDirectory(const std::string& normalizedDirectory);
    FILE* Open(const char* path,std::uint32_t* declaredSize);
    // Explicit cache reset for owner/test lifecycle; not automatically attached
    // to renderer reset. Reference global cache teardown is not reconstructed.
    void Clear(){files.clear();directories.clear();}
    std::size_t FileCount()const{return files.size();}
    std::size_t DirectoryCount()const{return directories.size();}
};
RF455CharacterRfsCache* RF455_SetCharacterRfsCache(RF455CharacterRfsCache* cache);
RF455CharacterRfsCache* RF455_GetCharacterRfsCache();
