#include "client455_language.h"
#include "client455_nation_paths.h"
#include "client455_font_settings.h"
#include <windows.h>
#include <clocale>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <new>
#include <utility>

namespace {
RF455LanguagePack normal;
std::uint32_t u32(const unsigned char*p){std::uint32_t value;std::memcpy(&value,p,4);return value;}
bool readFile(const char*name,std::vector<unsigned char>&bytes){
    HANDLE file=CreateFileA(name,GENERIC_READ,FILE_SHARE_READ,nullptr,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,nullptr);
    if(file==INVALID_HANDLE_VALUE)return false;LARGE_INTEGER length={};bool ok=GetFileSizeEx(file,&length)&&length.QuadPart>=0&&length.QuadPart<0x80000000;
    if(ok){try{bytes.resize(static_cast<std::size_t>(length.QuadPart));}catch(const std::bad_alloc&){ok=false;}}
    DWORD got=0;if(ok)ok=ReadFile(file,bytes.data(),static_cast<DWORD>(bytes.size()),&got,nullptr)&&got==bytes.size();CloseHandle(file);return ok;
}
}
bool RF455_DecodeEdf(const void*input,std::size_t size,std::vector<unsigned char>&out){
    if(!input||size<289)return false;const auto*data=static_cast<const unsigned char*>(input);const std::size_t n=u32(data+29);
    if(n>size-289)return false;unsigned char key[256];
    for(unsigned i=0;i<256;++i){const unsigned delta=1u<<((i+1)%8);key[i]=static_cast<unsigned char>(data[33+n+i]+(i%2?delta:0u-delta));}
    for(unsigned i=0;i<128;++i)std::swap(key[i],key[255-i]);
    for(unsigned i=0;i<256;i+=2)std::swap(key[i],key[i+1]);
    try{out.resize(n);}catch(const std::bad_alloc&){SecureZeroMemory(key,sizeof(key));return false;}
    for(std::size_t i=0;i<n;++i)out[i]=static_cast<unsigned char>(data[33+i]+(i%2?key[(i+1)%256]:0u-key[(i+1)%256]));
    SecureZeroMemory(key,sizeof(key));return true;
}
bool RF455_ParseLanguagePayload(RF455LanguagePack&pack,const void*input,std::size_t size,unsigned cp){
    if(!input||size<4)return false;const auto*data=static_cast<const unsigned char*>(input);const auto count=u32(data);pack.count=count;
    if(!count||count>(size-4)/8)return false;std::size_t at=4;std::vector<RF455LanguageRecord> next;
    // The reference ignores failed reads and can allocate from invalid sizes.
    // Bound those unsafe domains explicitly;do not certify them as equivalence.
    if(count>next.max_size())return false;
    try{
        next.reserve(count);
        for(std::uint32_t i=0;i<count;++i){
            if(size-at<8)return false;RF455LanguageRecord record;record.id=u32(data+at);const auto bytes=u32(data+at+4);at+=8;
            if(bytes>size-at)return false;record.text.assign(data+at,data+at+bytes);at+=bytes;next.push_back(std::move(record));
        }
    }catch(const std::bad_alloc&){return false;}
    pack.records=std::move(next);pack.codepage=cp;return true;
}
bool RF455_LoadLanguagePack(RF455LanguagePack&pack,const char*name,unsigned cp){
    std::vector<unsigned char> raw,plain;return readFile(name,raw)&&RF455_DecodeEdf(raw.data(),raw.size(),plain)&&RF455_ParseLanguagePayload(pack,plain.data(),plain.size(),cp);
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
void RF455LanguagePack::release(){std::vector<RF455LanguageRecord>().swap(records);}
unsigned RF455_CountryCodePage(unsigned nation){static const unsigned cp[]={949,1252,936,1252,1252,932,1252,1251,950,1252,874};return cp[nation<11?nation:0];}
RF455LanguagePack* RF455_GetNormalLanguagePack(){return &normal;}
int RF455_InitializeLanguageData(){
    const auto*nation=RF455_GetNormalNationPaths();if(!nation->configured)return 0;const auto&descriptor=RF455_NationDescriptor(nation->nation);
    const char*locale=std::setlocale(LC_COLLATE,descriptor.crtLocale);const char*suffix=locale?std::strchr(locale,'.'):nullptr;
    if(!suffix)return 0;const unsigned cp=static_cast<unsigned>(std::atol(suffix+1));const unsigned expected=RF455_CountryCodePage(nation->nation);
    if(cp!=expected){char text[256];std::sprintf(text,"Mismatch CodePage between ETCAction(%d) and NationSelect(%d)! %s",expected,cp,descriptor.crtLocale);MessageBoxA(nullptr,text,"RF_ONLINE",0);return 0;}
    RF455_SetFontParameters(descriptor.font,9,12,descriptor.charset);RF455_SetFontCodePage(cp);
    char path[300];std::sprintf(path,"%s\\NDLanguage.edf",nation->dataRoot);
    if(!RF455_LoadLanguagePack(normal,path,cp))return 0;
    char log[96];std::sprintf(log,"RF455 NDLanguage:%u:%u",normal.codepage,normal.count);OutputDebugStringA(log);return 1;
}
