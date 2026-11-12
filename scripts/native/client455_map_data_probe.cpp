#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "userinterface/gamewindow/etcwin/guiminimapwindow.h"
#include "client455_nation_paths.h"
#include "client455_map_data.h"
#include <array>
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <vector>

template<class Tag,typename Tag::Type Member>struct MemberAccess{friend typename Tag::Type access(Tag){return Member;}};
struct LevelOwner{using Type=CLevel* CLand::*;friend Type access(LevelOwner);};template struct MemberAccess<LevelOwner,&CLand::m_pLevel>;
static unsigned checks=0;
static void check(bool yes,const char* message){++checks;if(!yes)throw std::runtime_error(message);}
static std::vector<unsigned char> read(const char* name){FILE* f=std::fopen(name,"rb");check(f!=nullptr,"fixture file");std::fseek(f,0,SEEK_END);const auto n=std::ftell(f);check(n>=0,"fixture size");std::rewind(f);std::vector<unsigned char> bytes(n);check(std::fread(bytes.data(),1,bytes.size(),f)==bytes.size(),"fixture read");std::fclose(f);return bytes;}
static std::vector<unsigned char> canonical(const RF455MapData& data,bool labels=true){
    std::vector<unsigned char> result;
    auto put=[&](const void* p,std::size_t n){const auto* bytes=static_cast<const unsigned char*>(p);if(n)result.insert(result.end(),bytes,bytes+n);};
    auto u32=[&](std::uint32_t n){put(&n,4);};
    for(unsigned i=0;i<data.count;++i){const auto& row=data.maps[i];unsigned char raw[588];std::memcpy(raw,&row,588);for(unsigned at:{492,500,508})std::memset(raw+at,0,4);if(!labels)std::memset(raw+36,0,64);put(raw,588);
        for(unsigned j=0;j<row.byPortalNum;++j){unsigned char p[288];std::memcpy(p,row.pPortalInfo+j,288);std::memset(p+240,0,4);if(!labels)std::memset(p+173,0,64);put(p,288);}
        for(unsigned j=0;j<row.byPortalNum;++j){const auto& p=row.pPortalInfo[j];put(p.byLinkedPortal,p.byLinkedPortalNum*8u);}
        put(row.pMineInfo,row.byMineNum*96u);
        for(unsigned j=0;j<row.byAreaNum;++j){auto area=row.pAreaInfo[j];if(!labels)std::memset(area.pName,0,sizeof(area.pName));put(&area,sizeof(area));}
    }
    for(unsigned section=0;section<2;++section){u32(static_cast<std::uint32_t>(data.layers[section].size()));u32(labels?data.localizedLayerCounts[section]:0);
        for(const auto& layer:data.layers[section]){u32(layer.height);u32(layer.width);u32(static_cast<std::uint32_t>(layer.name.size()));put(layer.name.data(),layer.name.size());u32(static_cast<std::uint32_t>(layer.labels.size()));
            for(const auto& label:layer.labels){put(label.fields,16);u32(labels?static_cast<std::uint32_t>(label.text.size()):0);if(labels)put(label.text.data(),label.text.size());}
            u32(static_cast<std::uint32_t>(layer.image.size()));put(layer.image.data(),layer.image.size());}}
    return result;
}
struct Binding {
    CLand& land;CLevel& level;
    ~Binding(){level.mBsp->mNode=nullptr;land.*access(LevelOwner{})=nullptr;g_pUiMinimapWindow=nullptr;}
};
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    auto main=read("main.bin"),nd=read("localized.bin"),oracle=read("canonical.bin"),geometry=read("geometry.bin");
    RF455MapData parsed;check(RF455_ParseMapData(parsed,main.data(),main.size(),nd.data(),nd.size())==RF455MapLoad::Complete,"real two-stream parse");check(canonical(parsed)==oracle,"all110 map/portal/link/mine/area/layer/label/image bytes equal independent reader");
    check(parsed.mainConsumed==main.size()&&parsed.localizedConsumed==nd.size(),"both streams fully consumed");check(parsed.layers[0].size()==103&&parsed.layers[1].size()==7,"both appended layer sections");
    unsigned maxPortals=0,maxMines=0;for(unsigned i=0;i<110;++i){maxPortals=(std::max)(maxPortals,parsed.maps[i].byPortalNum);maxMines=(std::max)(maxMines,parsed.maps[i].byMineNum);}
    check(maxPortals==54&&maxMines==62,"actual arrays exceed legacy50");
    for(std::size_t cut:{std::size_t(0),std::size_t(3),std::size_t(36),std::size_t(426),main.size()-1})check(RF455_ParseMapData(parsed,main.data(),cut,nd.data(),nd.size())==RF455MapLoad::Malformed,"short main stream rejected");
    for(std::size_t cut:{std::size_t(0),std::size_t(3),std::size_t(68),nd.size()-1})check(RF455_ParseMapData(parsed,main.data(),main.size(),nd.data(),cut)==RF455MapLoad::Malformed,"short localized stream rejected");
    auto changed=main;std::uint32_t bad=109;std::memcpy(changed.data(),&bad,4);check(RF455_ParseMapData(parsed,changed.data(),changed.size(),nd.data(),nd.size())==RF455MapLoad::MainCount,"exact110 count gate");
    changed=nd;bad=31;std::memcpy(changed.data(),&bad,4);check(RF455_ParseMapData(parsed,main.data(),main.size(),changed.data(),changed.size())==RF455MapLoad::LocalizedCount,"localized count gate");
    check(canonical(parsed)==oracle,"guarded failed parse preserves owned successful data");
    CLand land;auto& paths=*RF455_GetNormalNationPaths();const auto saved=paths;check(RF455_ReadNationPaths(".\\R3Engine.ini",&paths),"actual nation configuration");
    check(land.LoadData()!=0&&land.MapLoadStatus455()==RF455MapLoad::Complete&&land.GetMaxMapNum()==110,"actual ordinary CLand LoadData");check(canonical(land.MapData455())==oracle,"ordinary owner uses real loader");
    const auto baseGeometry=canonical(parsed,false);
    const char* incompatible[]={"en-gb","en-id","en-ph","ja-jp","ko-kr","pt-br","ru-ru","zh-cn"};
    for(const auto* folder:incompatible){
        std::sprintf(paths.dataRoot,".\\DataTable\\%s",folder);
        check(land.LoadData()!=0&&land.MapLoadStatus455()==RF455MapLoad::BaseOnly&&land.GetMaxMapNum()==110,
              "ordinary owner publishes base with a mismatched locale");
        const auto& base=land.MapData455();
        check(base.localizationStatus==RF455MapLoad::LocalizedCount&&base.localizedConsumed==0&&
              base.localizedCount==(!std::strcmp(folder,"ko-kr")?100u:31u),"actual mismatch retained for diagnosis");
        check(!std::strcmp(base.maps[0].pName_UI,"NeutralB")&&canonical(base,false)==baseGeometry,
              "fallback name and complete base geometry");
    }
    const auto fallback=canonical(land.MapData455());
    RF455MapData optional;
    check(RF455_LoadMapData(optional,"DataTable/Map.edf","missing-ndmap.edf")==RF455MapLoad::BaseOnly&&
          optional.localizationStatus==RF455MapLoad::MissingInput&&canonical(optional)==fallback,
          "missing optional file preserves the same base catalog");
    check(RF455_LoadMapData(optional,"DataTable/Map.edf","truncated-ndmap.edf")==RF455MapLoad::BaseOnly&&
          optional.localizationStatus==RF455MapLoad::Malformed&&canonical(optional)==fallback,
          "malformed localization never publishes partial labels");
    check(RF455_LoadMapData(optional,"truncated-map.edf","DataTable/zh-tw/NDMap.edf")==RF455MapLoad::Malformed&&
          canonical(optional)==fallback,"malformed required catalog preserves previous ownership");
    std::strcpy(paths.dataRoot,".\\DataTable\\zh-tw");check(land.LoadData()!=0&&canonical(land.MapData455())==oracle,"real map data reload");paths=saved;
    CLevel level;CGUIMiniMapWindow window;Binding binding{land,level};land.*access(LevelOwner{})=&level;g_pUiMinimapWindow=&window;
    std::array<_BSP_NODE,2> nodes={};std::size_t at=0;unsigned geometryCases=0;
    static_assert(sizeof(_BSP_NODE)==24,"Actual BSP node stride");
    for(unsigned world=0;world<3;++world){check(geometry.size()-at>=48,"BSP fixture");std::memcpy(nodes.data(),geometry.data()+at,48);at+=48;level.mBsp->mNode=nodes.data();
        const float point[]={(nodes[1].bb_min[0]+nodes[1].bb_max[0])/2.0f,0,(nodes[1].bb_min[2]+nodes[1].bb_max[2])/2.0f};
        for(unsigned i=0;i<110;++i){check(land.ApplyMiniMapGeometry455(static_cast<BYTE>(i)),"ordinary world-to-MiniMap geometry producer");float expected[4];check(geometry.size()-at>=sizeof(expected),"geometry oracle bounds");std::memcpy(expected,geometry.data()+at,sizeof(expected));at+=sizeof(expected);
            for(BYTE j=0;j<3;++j){auto& marker=window.NuclearMarker455(j);check(!std::memcmp(marker.Scale455(),expected,8),"actual map dimensions over signed BSP node1 bounds");marker.SetTargetPosition455(point);check(!std::memcmp(marker.RelativePosition455(),expected+2,8),"actual signed map offsets and world-to-marker projection");}
            ++geometryCases;
        }}
    check(at==geometry.size()&&geometryCases==330,"all110 maps across3 actual BSP bounds");
    window.SetMapIndex(0,109);check(window.GetMiniMapIndex()==109,"legacy8map clamp removed");check(land.ApplyMiniMapGeometry455(109),"selected map109 remains valid");
    land.SetMapIndex(109);check(land.ApplyMiniMapGeometry455(0xff),"default current map selection");check(!land.ApplyMiniMapGeometry455(110),"owned invalid map guard");
    FILE* f=std::fopen("canonical-actual.bin","wb");check(f!=nullptr,"canonical output");const auto bytes=canonical(land.MapData455());check(std::fwrite(bytes.data(),1,bytes.size(),f)==bytes.size(),"canonical write");std::fclose(f);
    f=std::fopen("result.json","wb");check(f!=nullptr,"result output");std::fprintf(f,"{\"status\":\"PASS\",\"checks\":%u,\"maps\":110,\"layers\":[103,7],\"labels\":660,\"image_bytes\":257919,\"ordinary_CLand_LoadData\":true,\"all_canonical_bytes_equal\":true,\"incompatible_locales_with_full_base\":8,\"missing_and_malformed_localization\":true,\"malformed_base_atomic\":true,\"actual_BSP_node_fixtures\":3,\"geometry_cases\":330,\"ordinary_geometry_provider\":true,\"GPU_frames\":0,\"full_BSP_loader\":false,\"full_minimap\":false,\"full_client\":false}\n",checks);std::fclose(f);return 0;
}
int main(){try{return run();}catch(const std::exception& e){std::fprintf(stderr,"map data:%s checks=%u\n",e.what(),checks);return 1;}}
