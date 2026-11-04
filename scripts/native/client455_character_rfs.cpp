#include "client455_character_rfs.h"
#include <direct.h>
#include <cstdlib>
#include <cstring>
#include <vector>

namespace {
RF455CharacterRfsCache defaultCache;
RF455CharacterRfsCache* activeCache=&defaultCache;
std::uint32_t number(const unsigned char* bytes){std::uint32_t x;std::memcpy(&x,bytes,4);return x;}
void upper(std::string& value){if(!value.empty())_strupr(&value[0]);}
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
bool RF455CharacterRfsCache::loadArchive(const std::string& directory,const std::string& file,bool infoMode){
    const std::string archive=directory+file;FILE* stream=std::fopen(archive.c_str(),"rb");if(!stream)return false;
    unsigned char word[4];bool success=std::fread(word,1,4,stream)==4;const auto count=success?number(word):0;
    // Owned malformed-input bounds. Reference trusts its count and reads into
    // stack buffers without checking; valid-entry lookup/declared extents match.
    const long start=std::ftell(stream);if(_fseeki64(stream,0,SEEK_END)){std::fclose(stream);return false;}const auto length=_ftelli64(stream);
    if(length<4 || static_cast<std::uint64_t>(count)>static_cast<std::uint64_t>(length-4)/64 || std::fseek(stream,start,SEEK_SET)){std::fclose(stream);return false;}
    for(std::uint32_t n=0;n<count;++n){
        unsigned char raw[64];if(std::fread(raw,1,64,stream)!=64 || !std::memchr(raw,0,56)){success=false;break;}
        const std::string name(reinterpret_cast<const char*>(raw));
        if(directory.size()+name.size()>=256 || directory.size()+(infoMode?archive.size():file.size())>=256)continue;
        std::string key=directory+name;upper(key);
        // std::map insert in937840 leaves the first existing value intact.
        files.insert({key,{archive,number(raw+56),number(raw+60)}});
    }
    if(std::fclose(stream))success=false;return success;
}
bool RF455CharacterRfsCache::LoadDirectory(const std::string& directory){
    if(!directories.insert(directory).second)return true; // negative caching too
    const std::string info=directory+"RFSINFO.DAT";FILE* stream=std::fopen(info.c_str(),"rb");bool success=true;
    if(stream){
        char name[256];while(std::fscanf(stream,"%255s",name)==1)if(!loadArchive(directory,name,true))success=false;
        if(std::fclose(stream))success=false;
    }else{
        for(unsigned n=0;n<1024;++n){const std::string name="DATA"+std::to_string(n)+".RFS";
            if(!loadArchive(directory,name,false))break;
        }
    }
    return success;
}
FILE* RF455CharacterRfsCache::Open(const char* path,std::uint32_t* declaredSize){
    if(!declaredSize)return nullptr;const std::string key=Normalize(path);if(key.empty())return nullptr;
    auto entry=files.find(key);
    if(entry==files.end()){
        const auto slash=key.rfind('\\');if(slash==std::string::npos)return nullptr;
        LoadDirectory(key.substr(0,slash+1));entry=files.find(key);
    }
    if(entry==files.end())return nullptr;
    FILE* stream=std::fopen(entry->second.archive.c_str(),"rb");if(!stream)return nullptr;
    // Reference ignores seek failure and returns an unbounded FILE*, not a
    // substream clamped to the declared member size.
    std::fseek(stream,static_cast<long>(entry->second.offset),SEEK_SET);
    *declaredSize=entry->second.size;return stream;
}
