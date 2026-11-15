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
struct RF455PortalAccess {
    std::uint32_t minimumLevel=0xffffffff, field248=0;
    std::uint8_t itemCount=0, itemTables[3]={};
    std::uint32_t itemCodes[3]={};
    std::uint8_t itemQuantities[3]={}, field271=0;
};
static_assert(sizeof(RF455PortalAccess)==28 && offsetof(RF455PortalAccess,itemCodes)==12 &&
              offsetof(RF455PortalAccess,itemQuantities)==24);

struct PORTAL_INFO:RF455MineInfo {
    std::uint32_t byPortalType=0,bIsMovable=0;
    std::uint8_t byUsableRace[5]={};
    char pName[64]={},pDesc[64]={};
    std::uint8_t byLinkedPortalNum=0,padding238[2]={};
    std::uint32_t (*byLinkedPortal)[2]=nullptr;
    RF455PortalAccess access;
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
    char pBspFileName[128]={};
    std::uint8_t padding486[2]={};
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
enum class RF455MapLoad {Complete,MissingInput,MainCount,LocalizedCount,Malformed,BaseOnly};
struct RF455MapData {
    std::unique_ptr<RF455MapInfo[]> maps;
    std::uint32_t count=0,localizedCount=0;
    std::array<std::vector<RF455MapLayer>,2> layers;
    std::array<std::uint32_t,2> localizedLayerCounts={};
    std::size_t mainConsumed=0,localizedConsumed=0;
    RF455MapLoad localizationStatus=RF455MapLoad::MissingInput;
};
RF455MapLoad RF455_ParseMapData(RF455MapData&,const void*,std::size_t,const void*,std::size_t);
// A valid catalog remains usable when the optional localized overlay fails.
RF455MapLoad RF455_LoadMapData(RF455MapData&,const char* mainFile,const char* localizedFile);

const RF455MapInfo* RF455_FindMapByCode(const RF455MapData&, std::uint32_t code);
const RF455MapInfo* RF455_FindMapByName(const RF455MapData&, const char* name);

enum class RF455MapLayerSection { Minimap, World };
const RF455MapLayer* RF455_FindMapLayer(const RF455MapData&, RF455MapLayerSection, const char* name);
int RF455_FindMapLayerLabel(const RF455MapLayer&, const char* text);
const char* RF455_FindLocalMapLabel(const RF455MapData&, std::uint32_t mapIndex, std::uint16_t ordinal);
const RF455MapLayer* RF455_FindWorldMapParent(const RF455MapData&, const char* label, int* ordinal = nullptr);
bool RF455_WorldMapSpritePath(const RF455MapLayer&, char* output, std::size_t capacity);

class RF455MapHitMask {
public:
    // The selected layer is immutable. Clear the mask before replacing its catalog.
    bool load(const RF455MapLayer&);
    int hit(std::uint32_t x, std::uint32_t y) const;
    void clear();

private:
    const RF455MapLayer* layer_ = nullptr;
    std::uint32_t width_ = 0, height_ = 0;
    std::size_t labelCount_ = 0;
    std::vector<unsigned char> pixels_;
};

class RF455LocalMapLayer {
public:
    // Clear before replacing the catalog. Label pointers borrow its storage.
    bool select(const RF455MapData&, std::uint32_t mapIndex);
    const char* labelAt(float x, float y) const;
    const char* labelAt(std::size_t index) const;
    const RF455MapLayer* layer() const { return layer_; }
    void clear();

private:
    const RF455MapLayer* layer_ = nullptr;
    RF455MapHitMask mask_;
};

#if defined(_M_IX86)
static_assert(sizeof(RF455MineInfo)==96&&sizeof(RF455PortalInfo)==288&&sizeof(RF455MapAreaInfo)==84&&sizeof(RF455MapInfo)==588,"455 map records");
static_assert(offsetof(RF455MapInfo,pFileName)==100&&offsetof(RF455MapInfo,pBspFileName)==358,"455 map paths");
static_assert(offsetof(RF455MapInfo,pPortalInfo)==492&&offsetof(RF455MapInfo,miniMapWidth)==552&&offsetof(RF455MapInfo,miniMapX)==560,"455 map lanes");
#endif
