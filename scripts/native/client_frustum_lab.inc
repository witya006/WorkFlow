#include "client455_frustum.h"
#include "CResObject.h"
#include <string>
extern "C" int RF455_RunFrustumChecks(const char*,const char*,void (*)(const float*,const float*,float (*)[4]));
static void actualFrustumPublisher(const float* view,const float* projection,float output[6][4]){
    std::memcpy(&GetR3State()->mMatView,view,64);std::memcpy(&GetR3State()->mMatProj,projection,64);
    SetCharacterClipping();std::memcpy(output,g_pFrustumPlane,96);
}
class FrustumActorFixture : public CResObject {
public:
    void Setup(BBOX* box,float x,float scale){m_pBBox=box;m_vecPos[0]=x;m_vecPos[1]=m_vecPos[2]=0;m_fScale=scale;m_dwStatusFlag=ROSF_CHECK_Y_POS|ROSF_CLIPPED;}
    bool Clipped()const{return (m_dwStatusFlag&ROSF_CLIPPED)!=0;}
    bool Preserved()const{return (m_dwStatusFlag&~ROSF_CLIPPED)==ROSF_CHECK_Y_POS;}
    ~FrustumActorFixture(){m_pBBox=nullptr;}
};
static int frustumScenarioProbe(){
    const char* output=std::getenv("RF_LAB_HELPER_OUTPUT");const char* golden=std::getenv("RF_FRUSTUM_GOLDEN");if(!output || !golden)return 237;
    const DWORD allocation=GetDmallocSize();const unsigned control=_control87(0,0);float savedView[16],savedProjection[16],savedPlanes[6][4];
    std::memcpy(savedView,&GetR3State()->mMatView,64);std::memcpy(savedProjection,&GetR3State()->mMatProj,64);std::memcpy(savedPlanes,g_pFrustumPlane,96);
    std::string component=std::string(output)+".component.json";unsigned failures=RF455_RunFrustumChecks(golden,component.c_str(),actualFrustumPublisher)?1u:0u,checks=0;
    auto check=[&](bool okay){++checks;if(!okay)++failures;};
    _clearfp();_control87(_MCW_EM|_PC_53|_RC_NEAR,_MCW_EM|_MCW_PC|_MCW_RC);
    const float identity[16]={1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1};float published[6][4];actualFrustumPublisher(identity,identity,published);
    BBOX box={};for(unsigned i=0;i<3;++i){box.pMin[i]=-.25f;box.pMax[i]=.25f;}
    const float positions[]={0,2,1.25f,1.25001f,1.5f,1.50001f,-2,0};
    const float scales[]={1,1,1,1,2,2,1,8};const bool clipped[]={false,true,false,true,false,true,true,false};
    {FrustumActorFixture actor;
        for(unsigned i=0;i<8;++i){actor.Setup(&box,positions[i],scales[i]);check(actor.ProcessClipping()==static_cast<BOOL>(clipped[i]));check(actor.Clipped()==clipped[i]);check(actor.Preserved());}
        actor.Setup(nullptr,0,1);check(actor.ProcessClipping()==FALSE && actor.Clipped() && actor.Preserved());
    }
    std::memcpy(&GetR3State()->mMatView,savedView,64);std::memcpy(&GetR3State()->mMatProj,savedProjection,64);std::memcpy(g_pFrustumPlane,savedPlanes,96);_clearfp();_control87(control,_MCW_EM|_MCW_PC|_MCW_RC);
    check(GetDmallocSize()==allocation);const char* dlls[]={"mss32.dll","ABuse.dll","Adv.dll","PDLL.dll"};for(const auto* name:dlls)check(!GetModuleHandleA(name));
    FILE* file=std::fopen(output,"wb");if(!file)return 238;std::fprintf(file,"{\"status\":\"%s\",\"actor_cases\":9,\"connected_checks\":%u,\"failures\":%u,\"dmalloc_balance\":%ld}\n",failures?"FAIL":"PASS",checks,failures,static_cast<long>(GetDmallocSize()-allocation));std::fclose(file);return failures?239:0;
}
