#include "client455_map_data.h"
#include "client455_language.h"
#include <windows.h>
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <utility>

namespace {
struct Cursor {
    const unsigned char* data;std::size_t size,at=0;
    void read(void* out,std::size_t n){if(n>size-at)throw std::runtime_error("Short 455 map stream");if(n)std::memcpy(out,data+at,n);at+=n;}
    std::uint32_t u32(){std::uint32_t x;read(&x,4);return x;}
    std::vector<unsigned char> bytes(std::size_t n){if(n>size-at)throw std::runtime_error("Short 455 map bytes");std::vector<unsigned char> x(n);read(x.data(),n);return x;}
    void count(std::size_t n,std::size_t stride){if(n>(size-at)/stride)throw std::runtime_error("Short 455 map array");}
};
bool file(const char* name,std::vector<unsigned char>& out){
    if(!name)return false;HANDLE h=CreateFileA(name,GENERIC_READ,FILE_SHARE_READ,nullptr,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,nullptr);
    if(h==INVALID_HANDLE_VALUE)return false;LARGE_INTEGER size={};bool ok=GetFileSizeEx(h,&size)&&size.QuadPart>=0&&size.QuadPart<0x80000000;
    try{if(ok)out.resize(static_cast<std::size_t>(size.QuadPart));}catch(...){CloseHandle(h);throw;}
    DWORD got=0;if(ok)ok=ReadFile(h,out.data(),static_cast<DWORD>(out.size()),&got,nullptr)&&got==out.size();CloseHandle(h);return ok;
}
}
RF455MapLoad RF455_ParseMapData(RF455MapData& out,const void* mainInput,std::size_t mainSize,const void* localizedInput,std::size_t localizedSize){
    if(!mainInput||!localizedInput)return RF455MapLoad::MissingInput;
    Cursor src{static_cast<const unsigned char*>(mainInput),mainSize},nd{static_cast<const unsigned char*>(localizedInput),localizedSize};
    RF455MapData next;
    try{
        next.count=src.u32();next.localizedCount=nd.u32();
        //7CAAE0: exact 110 check before comparing the two stream counts.
        if(next.count!=110)return RF455MapLoad::MainCount;
        if(next.localizedCount!=next.count)return RF455MapLoad::LocalizedCount;
        next.maps.reset(new RF455MapInfo[next.count]);
        for(std::uint32_t i=0;i<next.count;++i){
            auto& row=next.maps[i];src.read(&row.byIndex,4);src.read(row.pName,32);nd.read(row.pName_UI,64);src.read(row.pFileName,128);
            char sprite[128];src.read(sprite,128);const auto* end=static_cast<const char*>(std::memchr(sprite,0,sizeof(sprite)));
            if(!end||std::size_t(end-sprite)+25>=sizeof(row.pMinimapFileName))throw std::runtime_error("455 minimap path overflow domain");
            std::sprintf(row.pMinimapFileName,"./SpriteImage/Common/Map/%s",sprite);
            src.read(&row.wMinimapAngle,2);src.read(row.fields358,128);
            row.byPortalNum=src.u32();src.count(row.byPortalNum,288);
            if(row.byPortalNum)row.pPortalInfo=new RF455PortalInfo[row.byPortalNum];
            for(std::uint32_t j=0;j<row.byPortalNum;++j){
                auto& p=row.pPortalInfo[j];src.read(static_cast<RF455MineInfo*>(&p),96);src.read(&p.byPortalType,8);
                src.read(p.byUsableRace,5);src.read(p.pName,64);src.read(p.pDesc,64);src.read(&p.byLinkedPortalNum,1);src.read(p.padding238,2);
                src.u32(); // Serialized pointer slot is replaced by the owned link allocation.
                src.read(p.fields244,28);src.read(&p.bIsUsable,4);src.read(p.fields276,12);
            }
            for(std::uint32_t j=0;j<row.byPortalNum;++j){auto& p=row.pPortalInfo[j];nd.read(p.pDesc,64);src.count(p.byLinkedPortalNum,8);
                if(p.byLinkedPortalNum){p.byLinkedPortal=new std::uint32_t[p.byLinkedPortalNum][2];src.read(p.byLinkedPortal,p.byLinkedPortalNum*8u);}}
            row.byMineNum=src.u32();src.count(row.byMineNum,96);if(row.byMineNum){row.pMineInfo=new RF455MineInfo[row.byMineNum];src.read(row.pMineInfo,row.byMineNum*96u);}
            row.byAreaNum=src.u32();src.count(row.byAreaNum,84);if(row.byAreaNum){row.pAreaInfo=new RF455MapAreaInfo[row.byAreaNum];src.read(row.pAreaInfo,row.byAreaNum*84u);}
            for(std::uint32_t j=0;j<row.byAreaNum;++j)nd.read(row.pAreaInfo[j].pName,64);
            src.read(row.fields512,40);src.read(&row.miniMapWidth,8);src.read(&row.miniMapX,8);src.read(row.fields568,20);
        }
        for(unsigned section=0;section<2;++section){
            const auto n=src.u32();next.localizedLayerCounts[section]=nd.u32();src.count(n,20);next.layers[section].reserve(n);
            for(std::uint32_t i=0;i<n;++i){RF455MapLayer layer;layer.height=src.u32();layer.width=src.u32();const auto nameSize=src.u32();
                if(nameSize>32)throw std::runtime_error("455 layer name overflow domain");layer.name=src.bytes(nameSize);
                const auto labels=src.u32();src.count(labels,16);layer.labels.reserve(labels);
                for(std::uint32_t j=0;j<labels;++j){RF455MapLabel label;src.read(label.fields,16);label.fields[0]|=0xff000000;const auto textSize=nd.u32();
                    if(textSize>64)throw std::runtime_error("455 layer text overflow domain");label.text=nd.bytes(textSize);layer.labels.push_back(std::move(label));}
                layer.image=src.bytes(src.u32());next.layers[section].push_back(std::move(layer));
            }
        }
        next.mainConsumed=src.at;next.localizedConsumed=nd.at;out=std::move(next);return RF455MapLoad::Complete;
    }catch(const std::runtime_error&){return RF455MapLoad::Malformed;}
}
RF455MapLoad RF455_LoadMapData(RF455MapData& out,const char* mainFile,const char* localizedFile){
    std::vector<unsigned char> a,b,main,localized;
    if(!file(mainFile,a)||!file(localizedFile,b))return RF455MapLoad::MissingInput;
    if(!RF455_DecodeEdf(a.data(),a.size(),main)||!RF455_DecodeEdf(b.data(),b.size(),localized))return RF455MapLoad::Malformed;
    return RF455_ParseMapData(out,main.data(),main.size(),localized.data(),localized.size());
}
