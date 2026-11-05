#include "cresobject.h"
#include "global.h"
#include <cstdio>
#include <cstring>
#include <new>
#include <vector>

#define REQUIRE(value) do{if(!(value)){std::fprintf(stderr,"Normal consumer failure line%d\n",__LINE__);return 1;}}while(0)
static unsigned value(const void* p,unsigned at){unsigned out;std::memcpy(&out,static_cast<const unsigned char*>(p)+at,4);return out;}
template<class T>static void put(unsigned char* p,unsigned at,T v){std::memcpy(p+at,&v,sizeof(v));}
static RF455AnimationData* descriptor(unsigned seed,const unsigned char* keys){
    const auto ops=RF455_CrtMeshMemoryOps();auto* out=static_cast<RF455AnimationData*>(ops.allocate(ops.context,32));
    if(!out)throw std::bad_alloc();for(unsigned i=0;i<4;++i)out->channel[i]={seed+i,keys+i};return out;
}
static int modelContracts(ChInterface& renderer){
    const auto memory=RF455_CrtMeshMemoryOps();RF455MeshAccounting accounting={};
    RF455CharacterStorage model;RF455_ConstructCharacter(&model);RF455MeshStorage meshes[3];
    for(auto& mesh:meshes)RF455_ConstructMeshStorage(&mesh,&accounting);
    model.m_pMesh=meshes;model.m_MaxObj=3;unsigned char keys[8]={};
    // Disabled mode frees current but retains previous and model blend fields.
    renderer.AnimationReset(nullptr);REQUIRE(renderer.native.opaque33840==0);
    model.m_Frame=987;model.m_OMaxFrame=4320;model.m_BlendActive=7;model.m_BlendFrame=13;model.m_BlendMax=17;model.m_BlendElapsed=19;
    auto* kept=descriptor(5,keys);put(meshes[0].bytes,5099,kept);
    for(unsigned i=0;i<2;++i){put(meshes[i].bytes,5095,descriptor(30+i,keys));meshes[i].bytes[5094]=1;put<unsigned>(meshes[i].bytes,5103,900);meshes[i].m_Alpha=.3f;}
    renderer.AnimationReset(&model);
    REQUIRE(model.m_Frame==160 && !model.m_OMaxFrame && model.m_BlendActive==7 && model.m_BlendFrame==13 && model.m_BlendMax==17 && model.m_BlendElapsed==19);
    REQUIRE(value(meshes[0].bytes,5099)==reinterpret_cast<unsigned>(kept));
    for(auto& mesh:meshes)REQUIRE(!mesh.bytes[5094] && !value(mesh.bytes,5095) && !value(mesh.bytes,5103) && mesh.m_Alpha==1);
    // Enabled mode replaces owned descriptor, preserves borrowed key pointers.
    RF455AnimationData expected[2];renderer.native.opaque33840=1;model.m_Frame=1234;model.m_OMaxFrame=5555;
    auto* untouched=descriptor(70,keys);put(meshes[2].bytes,5099,untouched);
    for(unsigned i=0;i<2;++i){auto* current=descriptor(50+i,keys);expected[i]=*current;put(meshes[i].bytes,5095,current);}
    renderer.AnimationReset(&model);
    REQUIRE(model.m_Frame==160 && !model.m_OMaxFrame && model.m_BlendActive==1 && model.m_BlendFrame==1234 && model.m_BlendMax==5555 && model.m_BlendElapsed==0);
    for(unsigned i=0;i<2;++i){auto* previous=reinterpret_cast<const RF455AnimationData*>(value(meshes[i].bytes,5099));REQUIRE(previous && !std::memcmp(previous,&expected[i],32) && !value(meshes[i].bytes,5095));}
    REQUIRE(value(meshes[2].bytes,5099)==reinterpret_cast<unsigned>(untouched));
    const unsigned before=value(meshes[0].bytes,5099);model.m_BlendElapsed=21;renderer.AnimationReset(&model);
    REQUIRE(value(meshes[0].bytes,5099)==before && model.m_BlendElapsed==21);renderer.native.opaque33840=0;
    // First exact parent-name match, external marker gating and missing name.
    RF455CharacterStorage skeletonModel;RF455_ConstructCharacter(&skeletonModel);RF455MeshStorage parents[3];
    for(auto& mesh:parents)RF455_ConstructMeshStorage(&mesh,&accounting);
    skeletonModel.m_pMesh=parents;skeletonModel.m_MaxObj=3;std::strcpy(parents[0].m_Name,"root");std::strcpy(parents[1].m_Name,"root");std::strcpy(parents[2].m_Name,"Root");
    for(auto& mesh:meshes)std::strcpy(mesh.parentName,"root");put<unsigned>(meshes[0].bytes,5495,2);put<unsigned>(meshes[1].bytes,5495,0);put<unsigned>(meshes[2].bytes,5495,1);std::strcpy(meshes[2].parentName,"absent");
    auto* sentinel=&parents[2];meshes[1].m_pParent=sentinel;meshes[2].m_pParent=sentinel;
    renderer.RematchParent(nullptr,&model);renderer.RematchParent(&skeletonModel,nullptr);renderer.RematchParent(&skeletonModel,&model);
    REQUIRE(meshes[0].m_pParent==&parents[0] && meshes[0].m_HaveParent && value(meshes[0].bytes,5495)==1);
    REQUIRE(meshes[1].m_pParent==sentinel && !meshes[1].m_HaveParent && meshes[2].m_pParent==sentinel);
    // Eye matrix is copied by value to the first exact match only.
    std::strcpy(meshes[0].m_Name,"Head");std::strcpy(meshes[1].m_Name,"Head");std::strcpy(meshes[2].m_Name,"head");
    D3DXMATRIX matrix;for(unsigned i=0;i<16;++i)reinterpret_cast<float*>(&matrix)[i]=.25f+i;
    renderer.SetEyeVec("Head",&model,matrix);REQUIRE(value(meshes[0].bytes,5499)==1 && !std::memcmp(meshes[0].bytes+5503,&matrix,64));
    REQUIRE(!value(meshes[1].bytes,5499) && !value(meshes[2].bytes,5499));
    unsigned char snapshot[5803];std::memcpy(snapshot,meshes[0].bytes,5803);renderer.SetEyeVec("absent",&model,matrix);REQUIRE(!std::memcmp(snapshot,meshes[0].bytes,5803));
    // Texture path: source guard, padding, exact limit and retained byte255.
    std::memset(model.legacy_texture_path,0x5a,256);renderer.SetTexPath(nullptr,nullptr);renderer.SetTexPath(&model,nullptr);REQUIRE(model.legacy_texture_path[0]==0x5a);
    char shortPath[]=".\\tex";renderer.SetTexPath(&model,shortPath);REQUIRE(!std::strcmp(model.legacy_texture_path,shortPath) && !model.legacy_texture_path[254] && model.legacy_texture_path[255]==0x5a);
    char longPath[300];std::memset(longPath,'a',299);longPath[299]=0;renderer.SetTexPath(&model,longPath);REQUIRE(!std::memcmp(model.legacy_texture_path,longPath,255) && model.legacy_texture_path[255]==0x5a);
    // Real455BBX plus missing/null/short reads. Reader intentionally returns1
    // for opened malformed files and writes only bytes actually read.
    std::FILE* file=std::fopen("real.bbx","rb");REQUIRE(file);unsigned char raw[280];REQUIRE(std::fread(raw,1,280,file)==280);std::fclose(file);
    float first[3]={},second[3]={};char real[]="real.bbx",missing[]="missing.bbx";
    REQUIRE(renderer.ImportBoundBox(real,first,second)==1 && !std::memcmp(first,raw+268,12) && !std::memcmp(second,raw+256,12));
    float saved[3];std::memcpy(saved,first,12);REQUIRE(!renderer.ImportBoundBox(nullptr,first,second) && !renderer.ImportBoundBox(missing,first,second) && !std::memcmp(saved,first,12));
    file=std::fopen("short.bbx","wb");REQUIRE(file);REQUIRE(std::fwrite(raw,1,258,file)==258);std::fclose(file);std::memset(first,0x36,12);std::memset(second,0x5a,12);
    unsigned char expectedFirst[12],expectedSecond[12];std::memset(expectedFirst,0x36,12);std::memset(expectedSecond,0x5a,12);std::memcpy(expectedSecond,raw+256,2);char partial[]="short.bbx";
    REQUIRE(renderer.ImportBoundBox(partial,first,second)==1 && !std::memcmp(first,expectedFirst,12) && !std::memcmp(second,expectedSecond,12));
    for(auto& mesh:meshes)RF455_DestroyMeshStorage(&mesh,&memory);for(auto& mesh:parents)RF455_DestroyMeshStorage(&mesh,&memory);
    RF455CharacterStorage empty;RF455_ConstructCharacter(&empty);empty.m_Frame=99;empty.m_OMaxFrame=100;renderer.AnimationReset(&empty);REQUIRE(empty.m_Frame==160 && !empty.m_OMaxFrame);
    return 0;
}
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
        REQUIRE(modelContracts(renderer)==0);
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
    std::fprintf(file,"{\"status\":\"PASS\",\"normal_client_modules\":2,\"unity_manager_groups\":3,\"real_ani_loaded\":%u,\"max_frame\":%u,\"named_record_sizes\":[1188,5803,284],\"model_contract_groups\":5,\"real_bbx_loaded\":true,\"game_dlls_loaded\":false}\n",loaded,maxFrame);
    std::fclose(file);return 0;
}
