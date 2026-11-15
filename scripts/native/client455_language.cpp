#include "client455_language.h"
#include "client455_edf_input.h"
#include "client455_nation_paths.h"
#include "client455_font_settings.h"
#include <windows.h>
#include <clocale>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <new>
#include <string>
#include <stdexcept>
#include <utility>

namespace {
RF455LanguagePack normal;
std::uint64_t normalGeneration=0,initializedGeneration=~std::uint64_t(0);
std::string initializedPath;
unsigned initializedCodepage=0;
std::uint32_t u32(const unsigned char*p){std::uint32_t value;std::memcpy(&value,p,4);return value;}
bool loadLanguagePack(RF455LanguagePack& pack, const char* name, unsigned codepage)
{
    try {
        return RF455_ReadEdfInput(name, [&](const void* bytes, std::size_t size) {
            std::vector<unsigned char> plain;
            return RF455_DecodeEdf(bytes, size, plain) &&
                RF455_ParseLanguagePayload(pack, plain.data(), plain.size(), codepage);
        });
    } catch (const std::bad_alloc&) {
        return false;
    } catch (const std::length_error&) {
        return false;
    }
}

bool edfPayloadSize(const void* input, std::size_t size, std::size_t& length)
{
    if (!input || size < 289) return false;
    length = u32(static_cast<const unsigned char*>(input) + 29);
    return length <= size - 289;
}

void decodeEdfPayload(const unsigned char* data, std::size_t n, unsigned char* out)
{
    unsigned char key[256];
    for(unsigned i=0;i<256;++i){const unsigned delta=1u<<((i+1)%8);key[i]=static_cast<unsigned char>(data[33+n+i]+(i%2?delta:0u-delta));}
    for(unsigned i=0;i<128;++i)std::swap(key[i],key[255-i]);
    for(unsigned i=0;i<256;i+=2)std::swap(key[i],key[i+1]);
    for(std::size_t i=0;i<n;++i)out[i]=static_cast<unsigned char>(data[33+i]+(i%2?key[(i+1)%256]:0u-key[(i+1)%256]));
    SecureZeroMemory(key,sizeof(key));
}
}

bool RF455_DecodeEdf(const void* input, std::size_t size, std::vector<unsigned char>& out)
{
    std::size_t length;
    if (!edfPayloadSize(input, size, length)) return false;
    try {
        out.resize(length);
    } catch (const std::bad_alloc&) {
        return false;
    } catch (const std::length_error&) {
        return false;
    }
    decodeEdfPayload(static_cast<const unsigned char*>(input), length, out.data());
    return true;
}

bool RF455_DecodeEdf(const void* input, std::size_t size, void* output, std::size_t outputCapacity)
{
    std::size_t length;
    if (!edfPayloadSize(input, size, length) || length > outputCapacity || (length && !output))
        return false;
    decodeEdfPayload(static_cast<const unsigned char*>(input), length, static_cast<unsigned char*>(output));
    return true;
}
bool RF455_ParseLanguagePayload(RF455LanguagePack&pack,const void*input,std::size_t size,unsigned cp){
    if(!input||size<4)return false;const auto*data=static_cast<const unsigned char*>(input);const auto count=u32(data);
    if(!count||count>(size-4)/8)return false;std::size_t at=4;std::vector<RF455LanguageRecord> next;
    // The reference ignores failed reads and can allocate from invalid sizes.
    // Bound those unsafe domains explicitly;do not certify them as equivalence.
    if(count>next.max_size())return false;
    try{
        next.reserve(count);
        for(std::uint32_t i=0;i<count;++i){
            if(size-at<8)return false;RF455LanguageRecord record;record.id=u32(data+at);const auto bytes=u32(data+at+4);at+=8;
            if(!bytes||bytes>size-at||data[at+bytes-1]!=0)return false;
            record.text.assign(data+at,data+at+bytes);at+=bytes;next.push_back(std::move(record));
        }
    }catch(const std::bad_alloc&){return false;}catch(const std::length_error&){return false;}
    pack.records.swap(next);pack.count=count;pack.codepage=cp;
    if(&pack==&normal)++normalGeneration;
    return true;
}
bool RF455_LoadLanguagePack(RF455LanguagePack& pack, const char* name, unsigned codepage)
{
    // An explicit load must observe a file replaced since the previous load.
    RF455_GetCharacterRfsCache()->RemoveLooseBytes(name);
    return loadLanguagePack(pack, name, codepage);
}
const char*RF455LanguagePack::get(std::uint32_t index)const{
    static const char empty[]="";if(index>=count||index>=records.size())return empty;
    return reinterpret_cast<const char*>(records[index].text.data());
}
bool RF455LanguagePack::isLead(const char*text,int index)const{
    if(!text||index<0||static_cast<std::size_t>(index)>=std::strlen(text))return false;
    for(int i=0;i<=index;++i)if(IsDBCSLeadByteEx(codepage,static_cast<BYTE>(text[i]))){if(i==index)return true;++i;}
    return false;
}
bool RF455LanguagePack::isTrail(const char*text,int index)const{
    if(!text||index<0||static_cast<std::size_t>(index)>=std::strlen(text))return false;
    for(int i=0;i<=index;++i)if(IsDBCSLeadByteEx(codepage,static_cast<BYTE>(text[i]))&&++i==index)return true;
    return false;
}
void RF455LanguagePack::release()
{
    std::vector<RF455LanguageRecord>().swap(records);
    if (this == &normal) {
        RF455_GetCharacterRfsCache()->RemoveLooseBytes(initializedPath.c_str());
        ++normalGeneration;
    }
}
unsigned RF455_CountryCodePage(unsigned nation){static const unsigned cp[]={949,1252,936,1252,1252,932,1252,1251,950,1252,874};return cp[nation<11?nation:0];}
RF455LanguagePack* RF455_GetNormalLanguagePack(){return &normal;}
int RF455_InitializeLanguageData(){
    const auto*nation=RF455_GetNormalNationPaths();if(!nation->configured)return 0;const auto&descriptor=RF455_NationDescriptor(nation->nation);
    const unsigned expected=RF455_CountryCodePage(nation->nation);
    char path[300];const int pathLength=std::snprintf(path,sizeof(path),"%s\\NDLanguage.edf",nation->dataRoot);
    if(pathLength<0||static_cast<std::size_t>(pathLength)>=sizeof(path))return 0;
    std::string nextPath,previousLocale;
    const char* previous=std::setlocale(LC_COLLATE,nullptr);if(!previous)return 0;
    // Remember the path resolved at load time for reuse and release.
    const std::unique_ptr<char, decltype(&std::free)> absolute(_fullpath(nullptr,path,0), &std::free);
    if(!absolute)return 0;
    try{nextPath=absolute.get();previousLocale=previous;}
    catch(const std::bad_alloc&){return 0;}
    for(char& c:nextPath)if(c=='/')c='\\';
    const bool samePath=_stricmp(initializedPath.c_str(),nextPath.c_str())==0;
    const bool reusable=initializedGeneration==normalGeneration && samePath &&
        initializedCodepage==expected && normal.codepage==expected && normal.count && normal.records.size()==normal.count;
    RF455LanguagePack candidate;
    // Load failure changes neither font settings nor the process CRT locale.
    if(!reusable){
        if(samePath && initializedCodepage!=expected)
            RF455_GetCharacterRfsCache()->RemoveLooseBytes(nextPath.c_str());
        if(!loadLanguagePack(candidate,nextPath.c_str(),expected))return 0;
    }
    const char*locale=std::setlocale(LC_COLLATE,descriptor.crtLocale);const char*suffix=locale?std::strchr(locale,'.'):nullptr;
    if(!suffix){std::setlocale(LC_COLLATE,previousLocale.c_str());return 0;}
    const unsigned cp=static_cast<unsigned>(std::atol(suffix+1));
    if(cp!=expected){std::setlocale(LC_COLLATE,previousLocale.c_str());char text[256];std::sprintf(text,"Mismatch CodePage between ETCAction(%d) and NationSelect(%d)! %s",expected,cp,descriptor.crtLocale);MessageBoxA(nullptr,text,"RF_ONLINE",0);return 0;}
    // Reuse is effective only after the requested CRT locale passed validation.
    if(!reusable){normal.records.swap(candidate.records);normal.count=candidate.count;normal.codepage=candidate.codepage;++normalGeneration;}
    RF455_SetFontParameters(descriptor.font,9,12,descriptor.charset);RF455_SetFontCodePage(cp);
    initializedPath.swap(nextPath);initializedCodepage=cp;initializedGeneration=normalGeneration;
    char log[96];std::sprintf(log,"RF455 NDLanguage:%u:%u",normal.codepage,normal.count);OutputDebugStringA(log);return 1;
}
