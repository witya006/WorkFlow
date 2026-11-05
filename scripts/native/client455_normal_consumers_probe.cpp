#include "cresobject.h"
#include "global.h"
#include <cstdio>
#include <cstring>
#include <vector>

#define REQUIRE(value) do{if(!(value)){std::fprintf(stderr,"Normal consumer failure line%d\n",__LINE__);return 1;}}while(0)
static unsigned value(const void* p,unsigned at){unsigned out;std::memcpy(&out,static_cast<const unsigned char*>(p)+at,4);return out;}
int main(int argc,char** argv){
    if(argc!=3)return 2;
    // Normal named fields must address the SAME bytes as the recovered kernels.
    RF455CharacterStorage model;RF455_ConstructCharacter(&model);
    REQUIRE(model.m_Load==0 && model.m_Frame==160 && model.m_Alpha==1);
    model.m_Frame=912;model.m_Transition=1;model.m_TransFrame=25;model.m_TransTime=150;
    REQUIRE(value(&model,672)==912 && value(&model,704)==1 && value(&model,712)==25 && value(&model,716)==150);
    RF455MeshStorage mesh;RF455MeshAccounting accounting={};RF455_ConstructMeshStorage(&mesh,&accounting);
    mesh.m_MatResult._41=17;mesh.m_BefMatResult._42=19;mesh.m_BefMatLocal._43=23;
    float a,b,c;std::memcpy(&a,mesh.bytes+4830+48,4);std::memcpy(&b,mesh.bytes+4894+52,4);std::memcpy(&c,mesh.bytes+4958+56,4);
    REQUIRE(a==17 && b==19 && c==23 && mesh.m_Alpha==1);
    std::FILE* file=std::fopen(argv[1],"rb");REQUIRE(file);std::fseek(file,0,SEEK_END);const long length=std::ftell(file);std::rewind(file);std::vector<unsigned char> raw(length);REQUIRE(std::fread(raw.data(),1,raw.size(),file)==raw.size());std::fclose(file);
    std::vector<RF455AniTrackView> tracks(raw[0]);RF455AniView decoded={};std::size_t failure=0;
    REQUIRE(RF455_DecodeAni(raw.data(),raw.size(),tracks.data(),tracks.size(),&decoded,&failure)==RF_ANIMATION_OK);
    unsigned loaded=0,maxFrame=0;
    {
        ChInterface renderer;g_ifCharIF=&renderer;
        CUnityBoneMgr bones;CUnityMeshMgr models;CUnityAniMgr animations;
        REQUIRE(bones.Create() && models.Create() && animations.Create());
        REQUIRE(!animations.Create());
        auto* animation=animations.AddAni(RLI_MONSTER,argv[1]);REQUIRE(animation && !animation->m_Load);
        REQUIRE(animations.AddAni(RLI_MONSTER,argv[1])==animation);
        // Same ID mutation made by actual CCharResData::LoadAniDataList.
        animation->m_Ident=0x12000042;REQUIRE(value(animation,264)==0x12000042 && !std::strcmp(animation->m_Name,argv[1]));
        auto* metadata=new ANI_EXT_INFO;metadata->nMaxFrameNum=2;metadata->dwEffectFrame[0]=320;metadata->dwEffectFrame[1]=640;
        animation->m_pExtra=metadata;REQUIRE(value(animation,280)==reinterpret_cast<unsigned>(metadata));
        CAnimation control;control.SetAniData(animation);control.LoadData();
        REQUIRE(control.GetAniData()==animation && control.GetMaxEffectFrameNum()==2 && control.GetEffectFrame()==320);
        REQUIRE(animation->m_Load && animation->loadAttempted==1 && animation->maximum==decoded.maxFrame && animation->imported);
        REQUIRE(animations.GetAni(RLI_MONSTER,0x12000042)==animation && !animations.GetAni(RLI_MONSTER,0x12000043));
        auto* imported=animation->imported;control.LoadData();REQUIRE(animation->imported==imported);
        auto* lazy=animations.AddAni(RLI_PLAYER,argv[1]);REQUIRE(lazy && lazy!=animation && !lazy->m_Load);
        REQUIRE(animations.GetAni(RLI_PLAYER,lazy->m_Ident)==lazy && lazy->m_Load && lazy->maximum==decoded.maxFrame && lazy->imported && lazy->imported!=imported);
        char missing[]=".\\missing.ani";auto* failed=animations.AddAni(RLI_FORCE,missing);REQUIRE(failed && !failed->m_Load);
        REQUIRE(animations.GetAni(RLI_FORCE,failed->m_Ident)==failed && !failed->m_Load && failed->loadAttempted==1 && !failed->imported);
        REQUIRE(renderer.IsLoadAnimation(failed) && !failed->m_Load && !renderer.IsLoadAnimation(nullptr));
        REQUIRE(animations.GetAni(RLI_FORCE,failed->m_Ident)==failed && !failed->m_Load && failed->loadAttempted==1 && !failed->imported);
        loaded=2;maxFrame=animation->maximum;
        REQUIRE(animations.Destroy() && !animations.Destroy());REQUIRE(models.Destroy() && bones.Destroy());
        g_ifCharIF=nullptr;
    }
    REQUIRE(!GetModuleHandleA("mss32.dll") && !GetModuleHandleA("ABuse.dll") && !GetModuleHandleA("Adv.dll") && !GetModuleHandleA("PDLL.dll"));
    file=std::fopen(argv[2],"wb");REQUIRE(file);
    std::fprintf(file,"{\"status\":\"PASS\",\"normal_client_modules\":2,\"unity_manager_groups\":3,\"real_ani_loaded\":%u,\"max_frame\":%u,\"named_record_sizes\":[1188,5803,284],\"game_dlls_loaded\":false}\n",loaded,maxFrame);
    std::fclose(file);return 0;
}
