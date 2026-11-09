#pragma once
#include <array>
#include <cstddef>
#include <cstdint>
#include <memory>
#include <vector>

// Source-owned records. These offsets are the x86 455 loader's actual stores.
// Names retained for legacy client consumers; untraced fields stay opaque.
struct RF455MineInfo {
    std::uint32_t byMapIndex=0,byIndex=0;
    float vecMin[3]={},vecMax[3]={},transform[16]={};
};
struct PORTAL_INFO:RF455MineInfo {
    std::uint32_t byPortalType=0,bIsMovable=0;
    std::uint8_t byUsableRace[5]={};
    char pName[64]={},pDesc[64]={};
    std::uint8_t byLinkedPortalNum=0,padding238[2]={};
    std::uint32_t (*byLinkedPortal)[2]=nullptr;
    std::uint8_t fields244[28]={};
    std::uint32_t bIsUsable=0;
    std::uint8_t fields276[12]={};
    ~PORTAL_INFO(){delete[] byLinkedPortal;}
};
using RF455PortalInfo=PORTAL_INFO;
struct RF455MapAreaInfo {
    std::uint32_t dwIndex=0;
    struct {std::int32_t left=0,top=0,right=0,bottom=0;} recArea;
    char pName[64]={};
};
struct RF455MapInfo {
    std::uint32_t byIndex=0;
    char pName[32]={},pName_UI[64]={},pFileName[128]={},pMinimapFileName[128]={};
    std::uint16_t wMinimapAngle=0;
    std::uint8_t fields358[128]={},padding486[2]={};
    std::uint32_t byPortalNum=0;
    RF455PortalInfo* pPortalInfo=nullptr;
    std::uint32_t byMineNum=0;
    RF455MineInfo* pMineInfo=nullptr;
    std::uint32_t byAreaNum=0;
    RF455MapAreaInfo* pAreaInfo=nullptr;
    float fields512[10]={};
    std::int32_t miniMapWidth=0,miniMapHeight=0,miniMapX=0,miniMapY=0;
    std::uint32_t fields568[5]={};
    ~RF455MapInfo(){delete[] pPortalInfo;delete[] pMineInfo;delete[] pAreaInfo;}
};
struct RF455MapLabel {std::uint32_t fields[4]={};std::vector<unsigned char> text;};
struct RF455MapLayer {
    std::uint32_t height=0,width=0;
    std::vector<unsigned char> name,image;
    std::vector<RF455MapLabel> labels;
};
struct RF455MapData {
    std::unique_ptr<RF455MapInfo[]> maps;
    std::uint32_t count=0,localizedCount=0;
    std::array<std::vector<RF455MapLayer>,2> layers;
    std::array<std::uint32_t,2> localizedLayerCounts={};
    std::size_t mainConsumed=0,localizedConsumed=0;
};
enum class RF455MapLoad {Complete,MissingInput,MainCount,LocalizedCount,Malformed};
RF455MapLoad RF455_ParseMapData(RF455MapData&,const void*,std::size_t,const void*,std::size_t);
RF455MapLoad RF455_LoadMapData(RF455MapData&,const char* mainFile,const char* localizedFile);

#if defined(_M_IX86)
static_assert(sizeof(RF455MineInfo)==96&&sizeof(RF455PortalInfo)==288&&sizeof(RF455MapAreaInfo)==84&&sizeof(RF455MapInfo)==588,"455 map records");
static_assert(offsetof(RF455MapInfo,pPortalInfo)==492&&offsetof(RF455MapInfo,miniMapWidth)==552&&offsetof(RF455MapInfo,miniMapX)==560,"455 map lanes");
#endif
