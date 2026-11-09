#pragma once
#include <cstddef>
#include <cstdint>
#include <cstring>

struct RF455ResourceCatalogSummary {
    std::uint32_t count[9][3]={};
    std::size_t consumed=0;
};
inline bool RF455_CheckResourceCatalog(const void* data,std::size_t bytes,RF455ResourceCatalogSummary& output){
    if(!data)return false;
    const auto* p=static_cast<const unsigned char*>(data);std::size_t at=0;
    RF455ResourceCatalogSummary next;
    const std::size_t stride[3]={260,328,244};
    for(unsigned group=0;group<9;++group)for(unsigned kind=0;kind<3;++kind){
        if(bytes-at<4)return false;
        std::uint32_t count;std::memcpy(&count,p+at,4);at+=4;
        if(count>(bytes-at)/stride[kind])return false;
        for(std::uint32_t i=0;i<count;++i){const auto* row=p+at+i*stride[kind];
            const unsigned path=kind?8:4,file=kind?136:132;
            if(!std::memchr(row+path,0,128)||!std::memchr(row+file,0,64))return false;
            if(kind==0&&!std::memchr(row+196,0,64))return false;
            if(kind==1&&!std::memchr(row+200,0,128))return false;
            // Positive event counts beyond ten overrun target metadata. Keep
            // that unsafe domain outside the bounded source loader.
            if(kind==2&&row[200]>10&&row[200]<128)return false;
        }
        next.count[group][kind]=count;at+=std::size_t(count)*stride[kind];
    }
    next.consumed=at;output=next;return true;
}
inline bool RF455_MissingPlayerBoneFatal(const char* path,bool exists){
    if(exists||!path)return false;
    const char* match=std::strstr(path,"/character/player/bone");
    return match&&match>path; // Target string.find is compared as signed >0.
}
inline bool RF455_PlayerBoneMatches(std::uint32_t id,std::uint32_t count,const char* firstName){
    static const std::uint32_t expected[5]={30,25,29,38,30};
    return count==(id<5?expected[id]:0)&&firstName&&std::strlen(firstName)==5;
}
