#include "client455_account.h"
#include <cstring>

namespace {
std::uint16_t le16(const std::uint8_t* p){return std::uint16_t(p[0])|(std::uint16_t(p[1])<<8);}
void copyText(void* destination,const char* source,std::size_t capacity){
    // 5E5920's defined domain:nonnull source,destination and positive capacity.
    std::memset(destination,0,capacity);
    if(!source)return;
    std::size_t length=0;while(length+1<capacity&&source[length])++length;
    std::memcpy(destination,source,length);
}
}
bool RF455_ReadAccountSeed(RF455AccountHandshake& state,const void* input,std::size_t size){
    if(!input||size<3)return false;
    const auto* p=static_cast<const std::uint8_t*>(input);
    state.delta=static_cast<std::uint8_t>(p[0]+1);
    state.mask=static_cast<std::uint16_t>(le16(p+1)+3);return true;
}
void RF455_PackCredentials(std::uint8_t (&output)[84],const char* id,const char* password){
    copyText(output,id,51);copyText(output+51,password,33);
}
bool RF455_PackLogin(std::uint8_t (&output)[RF455LoginBytes],const RF455AccountHandshake& state,
                    const char* id,const char* password,bool ticketProfile,const char* ticket,bool mode2){
    if(ticketProfile&&!ticket)return false; // Target's null-ticket return is undefined.
    std::memset(output,0,sizeof(output));
    if(ticketProfile)copyText(output+85,ticket,257);
    else {copyText(output,id,51);copyText(output+51,password,33);}
    if(!mode2)for(auto& byte:output)byte=static_cast<std::uint8_t>(static_cast<std::uint8_t>(byte+state.delta)^static_cast<std::uint8_t>(state.mask));
    output[84]=state.serverType; // Overwritten AFTER transformation in569EF0.
    return true;
}
bool RF455_ReadWorldList(const void* input,std::size_t size,RF455WorldInfo* records,std::size_t capacity,
                        std::uint8_t& result,std::uint32_t& count){
    if(!input||!records||size<4)return false;
    const auto* p=static_cast<const std::uint8_t*>(input);const std::size_t bytes=le16(p+1);
    if(bytes<1||bytes>4097||bytes>size-3)return false;
    const std::size_t end=3+bytes;const unsigned total=p[3];
    // Target sign-extends this char and then loops unsigned;128+ is unsafe.
    if(total>127||total>capacity)return false;
    std::size_t at=4;
    for(unsigned i=0;i<total;++i){
        if(at>end||end-at<2)return false;
        const unsigned nameBytes=p[at+1];at+=2;
        if(!nameBytes||nameBytes>64||nameBytes>=end-at)return false;
        at+=nameBytes+1;
    }
    at=4;
    for(unsigned i=0;i<total;++i){
        records[i].value=p[at]<128?p[at]:int(p[at])-256;
        const unsigned nameBytes=p[at+1];at+=2;
        copyText(records[i].m_pName,reinterpret_cast<const char*>(p+at),nameBytes);
        at+=nameBytes;records[i].status=p[at++];
    }
    result=p[0];count=total;return true;
}
