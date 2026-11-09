#pragma once
#include <cstddef>
#include <cstdint>
#include <cstring>

// Target56A840/56A960. Values belong to the client bootstrap,not server logic.
struct RF455WorldEntry {
    std::uint8_t result=255,grade=0,kind=0;
    bool responseSeen=false;
    std::int32_t cashShop=-1,npcShop=-1,quest=-1;
};
constexpr std::size_t RF455WorldEntryRequestBytes=58;
constexpr std::size_t RF455WorldEntryResponseBytes=12;

inline void RF455_PackWorldEntry(std::uint8_t (&output)[RF455WorldEntryRequestBytes],
                                std::uint32_t account,const std::uint32_t (&keys)[4],bool fullscreen){
    std::memset(output,0,sizeof(output));
    const auto put=[&](unsigned at,std::uint32_t value){for(unsigned i=0;i<4;++i)output[at+i]=static_cast<std::uint8_t>(value>>(8*i));};
    put(0,account);
    const std::uint32_t mask=(keys[0]+keys[2]-keys[1]-keys[3])*0x12ab34ccu;
    for(unsigned i=0;i<4;++i)put(4+4*i,keys[i]^mask);
    output[20]=fullscreen?1:0;put(21,126455);
    static const char signature[]="75a32d4a6daff548fcfcb40fea838a0d";
    static_assert(sizeof(signature)==33,"455 entry signature includes its terminator");
    std::memcpy(output+25,signature,sizeof(signature));
}

inline bool RF455_ReadWorldEntry(const void* data,std::size_t bytes,RF455WorldEntry& state){
    if(!data||bytes<RF455WorldEntryResponseBytes)return false;
    const auto* p=static_cast<const std::uint8_t*>(data);
    const auto selected=[&](unsigned at)->std::int32_t{return p[at]?std::int32_t(std::uint32_t(p[at+1])|(std::uint32_t(p[at+2])<<8)):-1;};
    RF455WorldEntry next;next.result=p[0];next.grade=p[1];next.kind=p[2];next.responseSeen=true;
    next.cashShop=selected(3);next.npcShop=selected(6);next.quest=selected(9);
    state=next;return true;
}
