#include "client455_character_rfs.h"
#include <direct.h>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <limits>
#include <new>
#include <stdexcept>
#include <cctype>
#include <utility>

namespace {
using FileOwner=std::unique_ptr<FILE,decltype(&std::fclose)>;
RF455CharacterRfsCache defaultCache;
RF455CharacterRfsCache* activeCache=&defaultCache;
std::uint32_t number(const unsigned char* bytes){std::uint32_t x;std::memcpy(&x,bytes,4);return x;}
void upper(std::string& value){if(!value.empty())_strupr(&value[0]);}
// Never split an overlong token into a second apparent archive filename.
// Return 0 at EOF, 1 for a complete name, -1 for a consumed invalid token.
int archiveName(FILE* stream,char (&name)[256]){
    int c;do{c=std::fgetc(stream);}while(c!=EOF && std::isspace(static_cast<unsigned char>(c)));
    if(c==EOF)return 0;
    unsigned length=0;bool invalid=false;
    do{
        if(!c)invalid=true;
        if(length<255)name[length++]=static_cast<char>(c);else invalid=true;
        c=std::fgetc(stream);
    }while(c!=EOF && !std::isspace(static_cast<unsigned char>(c)));
    name[length]=0;return invalid || std::ferror(stream)?-1:1;
}
void normalizeAbsoluteFile(char* path){
    for(auto* c=path;*c;++c)if(*c=='/')*c='\\';
    _strupr(path);
}
// Unlike the original RFS key function, loose paths retain every component.
std::string absoluteFile(const char* path){
    if(!path || !*path)return {};
    char* full=_fullpath(nullptr,path,0);if(!full)return {};
    normalizeAbsoluteFile(full);
    std::string result;
    try{result=full;}catch(...){std::free(full);throw;}
    std::free(full);return result;
}
}
RF455CharacterRfsCache* RF455_SetCharacterRfsCache(RF455CharacterRfsCache* cache){auto* previous=activeCache;activeCache=cache?cache:&defaultCache;return previous;}
RF455CharacterRfsCache* RF455_GetCharacterRfsCache(){return activeCache;}
std::string RF455CharacterRfsCache::Normalize(const char* path){
    if(!path || std::strlen(path)>=256)return {};
    char cwd[260];if(!_getcwd(cwd,sizeof(cwd)))return {};
    std::string input(path);for(auto& c:input)if(c=='/')c='\\';
    const auto slash=input.find('\\');std::string output;
    if(slash!=std::string::npos && input.find(':')!=std::string::npos)output=input;
    else output=std::string(cwd)+"\\"+(slash==std::string::npos?input:input.substr(slash+1));
    if(output.size()>=256)return {};upper(output);return output;
}
RF455CharacterRfsCache::IndexLoad RF455CharacterRfsCache::loadArchive(const std::string& directory,const std::string& file,bool infoMode,
    std::map<std::string,RF455CharacterRfsEntry>& staged){
    if(directory.size()>=256 || file.size()>=256-directory.size())return IndexLoad::RejectedPath;
    const std::string archive=directory+file;FileOwner stream(std::fopen(archive.c_str(),"rb"),&std::fclose);if(!stream)return IndexLoad::NotOpened;
    unsigned char word[4];if(std::fread(word,1,4,stream.get())!=4)return IndexLoad::Malformed;const auto count=number(word);
    // Owned malformed-input bounds. Reference trusts its count and reads into
    // stack buffers without checking; valid-entry lookup/declared extents match.
    const long start=std::ftell(stream.get());if(_fseeki64(stream.get(),0,SEEK_END))return IndexLoad::Malformed;const auto length=_ftelli64(stream.get());
    if(length<4 || static_cast<std::uint64_t>(count)>static_cast<std::uint64_t>(length-4)/64 || std::fseek(stream.get(),start,SEEK_SET))return IndexLoad::Malformed;
    std::map<std::string,RF455CharacterRfsEntry> archiveEntries;
    for(std::uint32_t n=0;n<count;++n){
        unsigned char raw[64];if(std::fread(raw,1,64,stream.get())!=64 || !std::memchr(raw,0,56))return IndexLoad::Malformed;
        const std::string name(reinterpret_cast<const char*>(raw));
        if(directory.size()+name.size()>=256 || directory.size()+(infoMode?archive.size():file.size())>=256)continue;
        std::string key=directory+name;upper(key);
        // std::map insert in937840 leaves the first existing value intact.
        archiveEntries.insert({key,{archive,number(raw+56),number(raw+60)}});
    }
    if(std::fclose(stream.release()))return IndexLoad::Malformed;
    // No partial archive publication after structural failure. Directory staging
    // also rolls back the whole scan if any insertion throws.
    for(auto& entry:archiveEntries)staged.emplace(entry.first,std::move(entry.second));
    return IndexLoad::Loaded;
}
bool RF455CharacterRfsCache::LoadDirectory(const std::string& directory){
    if(directory.size()+sizeof("RFSINFO.DAT")>256)return false;
    const auto marked=directories.insert(directory);if(!marked.second)return true; // negative caching too
    std::vector<decltype(files)::iterator> inserted;
    try{
        std::map<std::string,RF455CharacterRfsEntry> staged;
        const std::string info=directory+"RFSINFO.DAT";FileOwner stream(std::fopen(info.c_str(),"rb"),&std::fclose);bool success=true;
        if(stream){
            char name[256];int token;
            while((token=archiveName(stream.get(),name))!=0){
                if(token<0){success=false;continue;}
                if(loadArchive(directory,name,true,staged)!=IndexLoad::Loaded)success=false;
            }
            if(std::ferror(stream.get()))success=false;
            if(std::fclose(stream.release()))success=false;
        }else{
            for(unsigned n=0;n<1024;++n){const std::string name="DATA"+std::to_string(n)+".RFS";
                const auto loaded=loadArchive(directory,name,false,staged);
                if(loaded==IndexLoad::NotOpened)break;
                if(loaded==IndexLoad::RejectedPath){success=false;break;}
                if(loaded==IndexLoad::Malformed)success=false;
            }
        }
        inserted.reserve(staged.size());
        for(auto& entry:staged){const auto result=files.emplace(entry.first,std::move(entry.second));if(result.second)inserted.push_back(result.first);}
        return success;
    }catch(...){
        for(const auto entry:inserted)files.erase(entry);
        directories.erase(marked.first);throw;
    }
}
const RF455CharacterRfsEntry* RF455CharacterRfsCache::findEntry(const char* path){
    const std::string key=Normalize(path);if(key.empty())return nullptr;
    auto entry=files.find(key);
    if(entry==files.end()){
        const auto slash=key.rfind('\\');if(slash==std::string::npos)return nullptr;
        LoadDirectory(key.substr(0,slash+1));entry=files.find(key);
    }
    return entry==files.end()?nullptr:&entry->second;
}
FILE* RF455CharacterRfsCache::Open(const char* path,std::uint32_t* declaredSize){
    if(!declaredSize)return nullptr;const auto* entry=findEntry(path);if(!entry)return nullptr;
    FILE* stream=std::fopen(entry->archive.c_str(),"rb");if(!stream)return nullptr;
    // Reference ignores seek failure and returns an unbounded FILE*, not a
    // substream clamped to the declared member size.
    std::fseek(stream,static_cast<long>(entry->offset),SEEK_SET);
    *declaredSize=entry->size;return stream;
}

void RF455CharacterRfsCache::erasePayload(std::map<std::string,Payload>::iterator entry) noexcept {
    stats.retainedBytes -= entry->second.bytes->capacity();
    recent.erase(entry->second.age);
    payloads.erase(entry);
    stats.entries = payloads.size();
    ++stats.evictions;
}
void RF455CharacterRfsCache::evictOldest(){
    if(recent.empty())return;
    erasePayload(payloads.find(recent.back()));
}
void RF455CharacterRfsCache::SetByteBudget(std::size_t bytes){
    byteBudget=bytes;while(stats.retainedBytes>byteBudget)evictOldest();
}
void RF455CharacterRfsCache::ClearPayloads(){
    payloads.clear();recent.clear();stats.retainedBytes=0;stats.entries=0;
}
void RF455CharacterRfsCache::ResetStats(){
    const auto retained=stats.retainedBytes,entries=stats.entries;
    stats={};stats.retainedBytes=retained;stats.entries=entries;
}
void RF455CharacterRfsCache::retain(const std::string& key,const RF455ResourceBytes& bytes){
    const auto size=bytes->capacity();if(!size || size>byteBudget)return;
    while(stats.retainedBytes>byteBudget-size || payloads.size()>=4096)evictOldest();
    // A successful read must remain usable even if cache metadata allocation fails.
    try{
        recent.push_front(key);
        try{
            const auto inserted=payloads.emplace(key,Payload{bytes,recent.begin()});
            if(!inserted.second){recent.pop_front();return;}
        }catch(...){recent.pop_front();throw;}
        stats.retainedBytes+=size;stats.entries=payloads.size();
    }catch(const std::bad_alloc&){}
}
RF455ResourceRead RF455CharacterRfsCache::readPayload(const std::string& key,
    const std::string& file,std::uint64_t offset,std::uint64_t extent,PayloadExtent extentKind,std::uint64_t maxBytes){
    RF455ResourceRead result;
    if(extentKind==PayloadExtent::ExactSize)result.declaredSize=extent;
    const auto found=payloads.find(key);
    if(found!=payloads.end()){
        result.declaredSize=found->second.bytes->size();
        if(result.declaredSize>maxBytes){result.status=RF455ResourceReadStatus::ReadError;return result;}
        recent.splice(recent.begin(),recent,found->second.age);++stats.hits;
        result.status=RF455ResourceReadStatus::Ready;result.bytes=found->second.bytes;
        return result;
    }
    ++stats.misses;
    std::unique_ptr<FILE,decltype(&std::fclose)> stream(std::fopen(file.c_str(),"rb"),&std::fclose);
    if(!stream)return result;
    result.status=RF455ResourceReadStatus::ReadError;
    if(_fseeki64(stream.get(),0,SEEK_END))return result;
    const auto measured=_ftelli64(stream.get());if(measured<0)return result;
    const auto length=static_cast<std::uint64_t>(measured);
    if(offset>length)return result;
    std::uint64_t size=extent;
    if(extentKind==PayloadExtent::ToEnd)size=length-offset;
    if(extentKind==PayloadExtent::ToNextMember){
        if(extent<offset || extent>length)return result;
        size=extent-offset;
    }
    result.declaredSize=size;
    // Subtraction avoids offset+size wrap. Legacy Open remains unbounded;
    // this owned sized API rejects malformed extents before allocating.
    if(size>length-offset || size>maxBytes || size>(std::numeric_limits<std::uint32_t>::max)()
        || size>(std::numeric_limits<std::size_t>::max)())return result;
    if(_fseeki64(stream.get(),static_cast<__int64>(offset),SEEK_SET))return result;
    try{
        auto bytes=std::make_shared<std::vector<unsigned char>>(static_cast<std::size_t>(size));
        if(size){
            ++stats.payloadReads;const auto read=std::fread(bytes->data(),1,bytes->size(),stream.get());
            stats.bytesRead+=read;if(read!=bytes->size())return result;
        }
        if(std::fclose(stream.release()))return result;
        result.bytes=bytes;result.status=RF455ResourceReadStatus::Ready;retain(key,result.bytes);
    }catch(const std::bad_alloc&){result.status=RF455ResourceReadStatus::MemoryError;}
    catch(const std::length_error&){result.status=RF455ResourceReadStatus::MemoryError;}
    return result;
}
RF455ResourceRead RF455CharacterRfsCache::ReadArchiveBytes(const char* path){
    try{
        const auto* entry=findEntry(path);if(!entry)return {};
        const auto archive=absoluteFile(entry->archive.c_str());if(archive.empty())return {};
        const auto key="A:"+archive+":"+std::to_string(entry->offset)+":"+std::to_string(entry->size);
        return readPayload(key,archive,entry->offset,entry->size,PayloadExtent::ExactSize,0xffffffffu);
    }catch(const std::bad_alloc&){RF455ResourceRead result;result.status=RF455ResourceReadStatus::MemoryError;return result;}
}
RF455ResourceRead RF455CharacterRfsCache::ReadLooseBytes(const char* path,std::uint64_t maxBytes){
    try{
        const auto file=absoluteFile(path);if(file.empty())return {};
        return readPayload("L:"+file,file,0,0,PayloadExtent::ToEnd,maxBytes);
    }catch(const std::bad_alloc&){RF455ResourceRead result;result.status=RF455ResourceReadStatus::MemoryError;return result;}
}

void RF455CharacterRfsCache::RemoveLooseBytes(const char* path) noexcept {
    try {
        const auto file = absoluteFile(path);
        if (file.empty()) return;
        const auto entry = payloads.find("L:" + file);
        if (entry != payloads.end()) erasePayload(entry);
    } catch (const std::bad_alloc&) {
        // Cache metadata is best effort, including invalidation under OOM.
    } catch (const std::length_error&) {
    }
}

void RF455CharacterRfsCache::RemovePayloadBytes(const RF455ResourceBytes& bytes) noexcept {
    if (!bytes) return;
    // Rejections are uncommon and retention is bounded to 4096 entries.
    // Compare the lease itself instead of rebuilding or allocating a key.
    for (auto entry = payloads.begin(); entry != payloads.end(); ++entry) {
        if (entry->second.bytes != bytes) continue;
        erasePayload(entry);
        return;
    }
}

RF455ResourceRead RF455CharacterRfsCache::ReadRpkMemberBytes(const char* archive,std::uint64_t start,
    std::uint64_t end,std::uint64_t maxBytes){
    try{
        const auto file=absoluteFile(archive);
        if(file.empty())return {};
        const auto key="P:"+file+":"+std::to_string(start)+":"+std::to_string(end);
        return readPayload(key,file,start,end,end?PayloadExtent::ToNextMember:PayloadExtent::ToEnd,maxBytes);
    }catch(const std::bad_alloc&){RF455ResourceRead result;result.status=RF455ResourceReadStatus::MemoryError;return result;}
}

void RF455CharacterRfsCache::RemoveRpkArchiveBytes(const char* path) noexcept {
    if (!path || !*path || payloads.empty()) return;
    char full[_MAX_PATH];
    if (!_fullpath(full, path, sizeof(full))) return;
    normalizeAbsoluteFile(full);
    const auto pathLength = std::strlen(full);
    for (auto entry = payloads.begin(); entry != payloads.end();) {
        const auto& key = entry->first;
        // Read the two offset separators from the end, after any path colon.
        if (key.compare(0, 2, "P:") == 0 &&
            key.rfind(':', key.rfind(':') - 1) == pathLength + 2 &&
            std::memcmp(key.data() + 2, full, pathLength) == 0) {
            erasePayload(entry++);
        } else {
            ++entry;
        }
    }
}
