#include "client455_chat_profile.h"
#include "client455_character_rfs.h"
#include "client455_chat_reference_tables.h"
#include "client455_language.h"
#include <algorithm>
#include <cerrno>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <mbstring.h>
#include <stdexcept>
#include <string>
#include <vector>
#undef min
#undef max

namespace {
RF455ChatProfile* owner=nullptr;
std::vector<std::string> tokenize(const std::string& input){
    std::vector<std::string> tokens;std::size_t at=0;
    // Target skips either UTF16 BOM, but still lexes individual bytes. It does
    // not decode UTF16; interleaved NULs keep those style markers unmatched.
    if(input.size()>2&&((BYTE(input[0])==0xff&&BYTE(input[1])==0xfe)||(BYTE(input[0])==0xfe&&BYTE(input[1])==0xff)))at=2;
    while(at<input.size()){
        if(static_cast<unsigned char>(input[at])<=32){++at;continue;}
        if(input.compare(at,2,"//")==0){const auto end=input.find('\n',at);at=end==std::string::npos?input.size():end+1;continue;}
        if(input[at]=='"'){
            const auto end=input.find('"',++at);if(end==std::string::npos)break; // target drops unfinished EOF token
            tokens.push_back(input.substr(at,end-at));at=end+1;
        }else{
            const auto begin=at;while(at<input.size()&&static_cast<unsigned char>(input[at])>32&&input.compare(at,2,"//")!=0)++at;
            tokens.push_back(input.substr(begin,at-begin));
        }
        if(tokens.size()>65535)throw std::logic_error("455 chat oversized script domain");
    }
    return tokens;
}
bool number(const std::string& token,int& out){
    if(token.empty())return false;char* end=nullptr;errno=0;const auto value=std::strtoll(token.c_str(),&end,10);
    if(errno||*end||value<std::numeric_limits<int>::min()||value>std::numeric_limits<int>::max())return false;
    out=static_cast<int>(value);return true;
}
void setFont(RF455ChatFont& font,DWORD color){font.color=color;font.size=12;font.style=32;font.scale=1;}
}
RF455ChatProfile* RF455_GetChatProfile(){return owner;}
RF455ChatProfile::RF455ChatProfile(){owner=this;}
RF455ChatProfile::~RF455ChatProfile(){Release();owner=nullptr;}
void RF455ChatProfile::Release(){for(auto& value:header)value=RF455ChatFont{};for(auto& value:body)value=RF455ChatFont{};for(auto& value:prefixes)value=RF455ChatPrefix{};ready=false;scriptRecords=fallbackRecords=0;}
void RF455ChatProfile::prefix(unsigned index,const char* text){
    auto& value=prefixes[index];value=RF455ChatPrefix{};if(!text)return;
    const auto bytes=std::strlen(text);if(bytes>65535)throw std::logic_error("455 chat overflowing prefix WORD/string domain");
    value.length=static_cast<WORD>(bytes);
    if(value.length>15){value.length=15;_mbsnbcpy(reinterpret_cast<unsigned char*>(value.text),reinterpret_cast<const unsigned char*>(text),15);}
    else std::strcpy(value.text,text);
}
void RF455ChatProfile::fallback(unsigned index,unsigned nation){
    int color=-1;unsigned language=0;
    switch(index){
    case 2:color=-22928;break;
    case 3:case 4:color=-1573887;language=0x84f;break;
    case 5:case 6:color=-6443185;language=0x850;break;
    case 7:case 8:color=-15672048;language=0x851;break;
    case 9:case 29:color=-16581383;break;
    case 10:case 11:color=-26573;language=0x852;break;
    case 12:case 13:color=-4161281;language=0x853;break;
    case 14:color=-43834;language=0x854;break;
    case 15:color=-43834;language=0x855;break;
    case 16:color=-43834;language=0x856;break;
    case 17:case 18:color=-15750559;language=0x857;break;
    case 19:color=nation==2?-65536:-12128;break;
    case 20:color=-6771798;break;
    case 21:color=-43834;break;
    case 22:color=-16777216;break;
    case 23:color=-15672048;language=0x878;break;
    case 24:color=-10734858;language=0x9ff;break;
    case 25:color=-6160555;break;
    case 26:color=-256;break;
    case 27:color=-6638337;break;
    case 28:color=-13159;break;
    case 30:color=-16746241;break;
    case 31:case 32:color=-10734858;language=0x850;break;
    case 33:color=-809729;break;
    case 34:color=-16729656;break;
    case 35:color=-26573;break;
    }
    setFont(header[index],static_cast<DWORD>(color));
    if(index==13)setFont(header[index],static_cast<DWORD>(color)); // target writes header twice
    else setFont(body[index],static_cast<DWORD>(color));
    prefix(index,language?RF455_GetNormalLanguagePack()->get(language):nullptr);
}
bool RF455ChatProfile::Load(unsigned nation,const char* explicitPath){
    if(ready)return true; // existing process provider is retained in the target
    if(nation>=11)throw std::logic_error("455 chat country domain");
    constexpr std::size_t maxBytes = 4u * 1024u * 1024u;
    const char* path = explicitPath ? explicitPath : RF455_CHAT_PATHS[nation];
    auto* cache = RF455_GetCharacterRfsCache();
    const auto source = cache->ReadLooseBytes(path, maxBytes);
    if (source.declaredSize > maxBytes) {
        cache->RemoveLooseBytes(path);
        throw std::logic_error("455 chat script size domain");
    }
    if (source.status != RF455ResourceReadStatus::Ready || !source.bytes) return false;
    if (source.bytes->empty()) {
        cache->RemoveLooseBytes(path);
        return false;
    }
    try {
        const std::string input(reinterpret_cast<const char*>(source.bytes->data()), source.bytes->size());
        const auto tokens = tokenize(input);
        if (tokens.empty()) {
            cache->RemoveLooseBytes(path);
            return false;
        }
        Release();
        for(unsigned index=0;index<36;++index){
            const auto found=std::find(tokens.begin(),tokens.end(),RF455_CHAT_TAGS[index]);bool parsed=false;
            if(found!=tokens.end()){
                const auto at=static_cast<std::size_t>(found-tokens.begin());int channels[4];
                if(at+5<tokens.size()&&number(tokens[at+1],channels[0])&&number(tokens[at+2],channels[1])&&number(tokens[at+3],channels[2])&&number(tokens[at+4],channels[3])){
                    for(auto& channel:channels)channel=std::max(0,std::min(255,channel));
                    const DWORD color=DWORD(channels[2])|(DWORD(channels[1])<<8)|(DWORD(channels[0])<<16)|(DWORD(channels[3])<<24);
                    setFont(header[index],color);setFont(body[index],color);prefix(index,tokens[at+5].c_str());parsed=true;
                }
            }
            if(parsed)++scriptRecords;else{fallback(index,nation);++fallbackRecords;}
        }
    } catch (const std::logic_error&) {
        cache->RemoveLooseBytes(path);
        throw;
    }
    ready=true;return true;
}
