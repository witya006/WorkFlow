#pragma once
#include <cstddef>
#include <cstdint>
#include <cstring>

constexpr std::size_t RF455RegisteredCharactersBytes=506;
constexpr std::size_t RF455RegisteredCharacterStride=164;
// The pinned handler copies506bytes from its receive buffer,then uses count
// at offset1. The live compatible server omits unused trailing records. Bound
// the active records before making that internal image;never read past a frame.
inline bool RF455_ExpandRegisteredCharacters(const void* data,std::size_t bytes,std::uint8_t (&image)[RF455RegisteredCharactersBytes]){
    if(!data||bytes<14)return false;
    const auto* p=static_cast<const std::uint8_t*>(data);
    if(p[1]>3||bytes<14+RF455RegisteredCharacterStride*p[1])return false;
    std::memset(image,0,sizeof(image));
    std::memcpy(image,p,bytes<sizeof(image)?bytes:sizeof(image));return true;
}
struct RF455RegisteredCharacter {
    char name[18]={},classCode[6]={}; // Keep wire bytes and a bounded local terminator.
    std::uint32_t serial=0xffffffff,baseShape=0;
    std::uint8_t race=0,slot=255,level=0,upgrade[8]={},reserved[83]={};
    std::int16_t equipment[8]={-1,-1,-1,-1,-1,-1,-1,-1};
    std::int64_t dalant=0,gold=0,lastConnection=0;
};
struct RF455RegisteredCharacters {
    std::uint8_t result=255,count=0,headerReserved[12]={};
    RF455RegisteredCharacter records[3];
};
inline bool RF455_ReadRegisteredCharacters(const void* data,std::size_t bytes,RF455RegisteredCharacters& state){
    if(!data||bytes<RF455RegisteredCharactersBytes)return false;
    const auto* p=static_cast<const std::uint8_t*>(data);if(p[1]>3)return false;
    const auto u32=[](const std::uint8_t* q){std::uint32_t value=0;for(unsigned i=0;i<4;++i)value|=std::uint32_t(q[i])<<(8*i);return value;};
    const auto i64=[](const std::uint8_t* q){std::uint64_t bits=0;for(unsigned i=0;i<8;++i)bits|=std::uint64_t(q[i])<<(8*i);std::int64_t value;std::memcpy(&value,&bits,8);return value;};
    RF455RegisteredCharacters next;next.result=p[0];next.count=p[1];std::memcpy(next.headerReserved,p+2,12);
    for(unsigned i=0;i<3;++i){const auto* q=p+14+i*RF455RegisteredCharacterStride;auto& r=next.records[i];
        std::memcpy(r.name,q,17);r.serial=u32(q+17);r.race=q[21];r.slot=q[22];std::memcpy(r.classCode,q+23,5);r.level=q[28];
        r.dalant=i64(q+29);r.gold=i64(q+37);r.baseShape=u32(q+45);
        for(unsigned j=0;j<8;++j){const std::uint16_t bits=std::uint16_t(q[49+2*j])|(std::uint16_t(q[50+2*j])<<8);std::memcpy(&r.equipment[j],&bits,2);}
        std::memcpy(r.upgrade,q+65,8);std::memcpy(r.reserved,q+73,83);r.lastConnection=i64(q+156);
    }
    state=next;return true;
}
