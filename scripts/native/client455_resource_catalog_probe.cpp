#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "input/imeedit.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "mainapp.h"
#include "client455_language.h"
#include "client455_nation_paths.h"
#include "client455_resource_catalog.h"
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <map>
#include <string>
#include <vector>

extern CMainApp g_MainApp;
static void require(bool value,const char* message){if(!value)throw std::runtime_error(message);}
static unsigned fingerprint(const void* pointer,std::size_t size){
    auto* p=static_cast<const unsigned char*>(pointer);unsigned value=2166136261;
    for(std::size_t i=0;i<size;++i)value=(value^p[i])*16777619;return value;
}
static unsigned expected[9][3][2];
static void helperCases(){
    require(RF455_PlayerBoneMatches(0,30,"Bip01")&&RF455_PlayerBoneMatches(1,25,"Bip01")&&
        RF455_PlayerBoneMatches(2,29,"Bip01")&&RF455_PlayerBoneMatches(3,38,"Bip01")&&RF455_PlayerBoneMatches(4,30,"Bip01"),"Five player skeleton counts");
    require(!RF455_PlayerBoneMatches(1,30,"Bip01")&&!RF455_PlayerBoneMatches(0,30,"root")&&
        !RF455_PlayerBoneMatches(0,30,nullptr),"Invalid skeleton shape");
    require(RF455_MissingPlayerBoneFatal("./character/player/bone/missing.bn",false)&&
        !RF455_MissingPlayerBoneFatal("/character/player/bone/missing.bn",false)&&
        !RF455_MissingPlayerBoneFatal("./character/player/bone/present.bn",true)&&
        !RF455_MissingPlayerBoneFatal("./Character/Player/Bone/missing.bn",false)&&
        !RF455_MissingPlayerBoneFatal("./character/monster/bone/missing.bn",false),"Exact player missing path predicate");
    RF455ResourceCatalogSummary summary;summary.count[0][0]=77;
    unsigned char empty[108]={};require(RF455_CheckResourceCatalog(empty,sizeof(empty),summary)&&summary.consumed==108,"Empty nine groups");
    summary.count[0][0]=77;require(!RF455_CheckResourceCatalog(empty,107,summary)&&summary.count[0][0]==77,"Truncated count keeps output");
    empty[0]=255;require(!RF455_CheckResourceCatalog(empty,sizeof(empty),summary)&&summary.count[0][0]==77,"Oversize row count");
}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    helperCases();FILE* fixture=std::fopen("expected.bin","rb");require(fixture,"Independent catalog expectations");
    unsigned playerAnimation=0;require(std::fread(expected,1,sizeof(expected),fixture)==sizeof(expected)&&
        std::fread(&playerAnimation,4,1,fixture)==1&&std::fgetc(fixture)==EOF,"Expected extent");std::fclose(fixture);
    require(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"Nation/language");
    InitR3Engine();auto* state=GetR3State();state->mScreenXsize=640;state->mScreenYsize=480;state->mbFullScreen=FALSE;ForceFullScreen();
    require(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"Own D3D");
    require(_CreateCharIF(GetD3dDevice())&&_CreateBoneMgr()&&_CreateMeshMgr()&&_CreateAnimationMgr()&&_CreateBoundBoxMgr(),"Actual resource owners");
    unsigned totals[3]={},registered[3]={},playerLoaded=0;bool realAnimation=false;
    {
        CCharResDataMgr catalog;require(catalog.LoadData(),"Ordinary Resource.edf loader");
        require(!catalog.GetResourceList(9),"Own accessor bound");
        for(unsigned group=0;group<9;++group){auto* list=catalog.GetResourceList(BYTE(group));
            const unsigned counts[3]={list->GetTotalBoneNum(),list->GetTotalMeshNum(),list->GetTotalAniNum()};
            const void* rows[3]={list->GetBoneData(),list->GetMeshData(),list->GetAniData()};
            const unsigned strides[3]={260,328,244};
            for(unsigned kind=0;kind<3;++kind){require(counts[kind]==expected[group][kind][0],"Actual table count");
                require(fingerprint(rows[kind],std::size_t(counts[kind])*strides[kind])==expected[group][kind][1],"All registered catalog row bytes");totals[kind]+=counts[kind];}
            if(counts[0]){auto& owner=_GetBoneMgr()->GetBoneMgr(group)->native;
                require(owner.begin&&unsigned(owner.end-owner.begin)==counts[0],"Each bone keeps its own registration");
                for(unsigned i=0;i<counts[0];++i){auto* row=list->GetBoneDataByOrder(i);char path[256];std::sprintf(path,"%s%s",row->pPathName,row->pFileName);
                    auto* bone=owner.begin[i];require(bone&&bone->m_ID==row->dwID&&!std::strcmp(bone->m_Name,path),"Ordered case-sensitive bone registration");++registered[0];}}
            std::map<std::string,ANI_DATA*> animations;
            for(unsigned i=0;i<counts[2];++i){auto* row=list->GetAniDataByOrder(i);char path[256];std::sprintf(path,"%s%s",row->pPathName,row->pFileName);_strlwr(path);animations[path]=row;}
            for(auto& entry:animations){auto* row=entry.second;
                auto* animation=_GetAniMgr()->GetAniMgr(group)->GetAnimationData(const_cast<char*>(entry.first.c_str()));
                require(animation,"Declared animation registered");auto* extra=static_cast<ANI_EXT_INFO*>(animation->m_pExtra);require(extra,"Actual animation event owner");
                require(animation->m_Ident==row->dwID,"Animation name/last ID");
                require(extra->nAniNumOfSameAction==char(row->dwNum)&&extra->nMaxFrameNum==char(row->dwEffectNum)&&extra->nCurrentFrameNum==0,"Actual animation event header");
                for(int j=0;j<extra->nMaxFrameNum;++j)require(extra->dwEffectFrame[j]==160+160*row->dwEffectFrame[j]&&!extra->bIsInvokedEffect[j],"Actual event tick conversion");++registered[2];
            }
        }
        for(unsigned owner=0;owner<MAX_MESH_MGR;++owner){auto& manager=_GetMeshMgr()->GetMeshMgr(owner)->native;
            if(manager.begin)registered[1]+=unsigned(manager.end-manager.begin);}
        for(unsigned i=0;i<5;++i){auto* bone=_GetBoneMgr()->GetBone(RLI_PLAYER,i);
            require(bone&&bone->m_Load&&bone->m_pMesh&&RF455_PlayerBoneMatches(i,bone->m_MaxObj,bone->m_pMesh[0].m_Name),"Five actual player bones");++playerLoaded;}
        // The independently selected real ANI can reside inside an RFS archive.
        auto* animation=_GetAniMgr()->GetAni(0,playerAnimation);require(animation&&animation->m_Load&&animation->imported&&animation->maximum,"Real player ANI import");realAnimation=true;
    }
    require(_DestroyBoundBoxMgr()&&_DestroyAnimationMgr()&&_DestroyMeshMgr()&&_DestroyBoneMgr()&&_DestroyCharIF(),"Resource owner teardown");
    g_MainApp.ReleaseR3D3D();ReleaseR3Engine();
    FILE* out=std::fopen("result.json","wb");require(out,"Output");
    std::fprintf(out,"{\"status\":\"PASS\",\"groups\":9,\"rows\":[%u,%u,%u],\"registered\":[%u,%u,%u],\"player_bones_loaded\":%u,\"real_player_animation\":%s,\"all_catalog_row_bytes\":true,\"full_bootstrap_or_selection\":false}\n",totals[0],totals[1],totals[2],registered[0],registered[1],registered[2],playerLoaded,realAnimation?"true":"false");std::fclose(out);return 0;
}
int main(){try{return run();}catch(const std::exception& error){std::fprintf(stderr,"Resource catalog: %s\n",error.what());return 2;}}
