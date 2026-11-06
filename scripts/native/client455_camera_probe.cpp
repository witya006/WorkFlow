#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "item/citemmgr.h"
#include "input/imeedit.h"
#include "baseheader.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "mainapp.h"
#include "client455_camera.h"
#include "Jmalloc.h"
#include <cstdio>
#include <cstring>
#include <cmath>
#include <vector>
extern CMainApp g_MainApp;
template<class Tag,typename Tag::Type Member>struct MemberAccess{friend typename Tag::Type access(Tag){return Member;}};
#define FIELD(Tag,TypeName,member) struct Tag{using Type=TypeName CAniCamera::*;friend Type access(Tag);};template struct MemberAccess<Tag,&CAniCamera::member>;
FIELD(Cameras,_ANI_CAMERA*,AniCamera)
FIELD(Dummies,_ANI_OBJECT*,mDummy)
FIELD(DummyCount,DWORD,mDummyNum)
FIELD(Now,float,mNowFrame)
FIELD(StartTick,float,mStartTick)
#define REQUIRE(x) do{if(!(x)){std::fprintf(stderr,"Camera failure line%d: %s\n",__LINE__,#x);return 1;}}while(0)
static_assert(sizeof(CAniCamera)==56&&sizeof(_ANI_OBJECT)==349,"Owned camera API and typed animation ABI");
static void bytes(std::vector<BYTE>& out,const void* p,std::size_t size){const auto* b=static_cast<const BYTE*>(p);if(size)out.insert(out.end(),b,b+size);}
static void word(std::vector<BYTE>& out,std::size_t n){DWORD v=static_cast<DWORD>(n);bytes(out,&v,4);}
static void node(std::vector<BYTE>& out,const RF455CameraNode& n){bytes(out,n.matrix,64);bytes(out,n.position,12);bytes(out,n.rotation,16);word(out,n.positions.size());word(out,n.rotations.size());bytes(out,n.positions.data(),n.positions.size()*16);bytes(out,n.rotations.data(),n.rotations.size()*20);}
static std::vector<BYTE> encode(const RF455CameraDocument& doc){
    std::vector<BYTE> out;bytes(out,&doc.version,4);word(out,doc.cameras.size());
    if(!doc.cameras.empty()){
        word(out,doc.start);word(out,doc.end);
        for(const auto& c:doc.cameras){bytes(out,c.name,64);bytes(out,&c.fov,4);bytes(out,&c.distance,4);word(out,c.hierarchy.size());if(doc.version>=1.3f){word(out,c.fovKeys.size());bytes(out,c.fovKeys.data(),c.fovKeys.size()*20);}for(const auto& n:c.hierarchy)node(out,n);}
        word(out,doc.dummies.size());for(const auto& d:doc.dummies){bytes(out,d.name,64);bytes(out,d.parentName,64);node(out,d.node);}
    }
    bytes(out,doc.trailer.data(),doc.trailer.size());return out;
}
static bool equalNode(const _ANI_OBJECT& actual,const RF455CameraNode& expected){
    return !std::memcmp(actual.s_matrix,expected.matrix,64)&&!std::memcmp(actual.pos,expected.position,12)&&!std::memcmp(actual.quat,expected.rotation,16)&&actual.Pos_cnt==expected.positions.size()&&actual.Rot_cnt==expected.rotations.size()&&actual.Scale_cnt==0&&actual.Scale==nullptr&&(!actual.Pos_cnt||!std::memcmp(actual.Pos,expected.positions.data(),actual.Pos_cnt*16))&&(!actual.Rot_cnt||!std::memcmp(actual.Rot,expected.rotations.data(),actual.Rot_cnt*20));
}
struct Clock{float value[2];unsigned calls=0;static float read(void* p){auto& c=*static_cast<Clock*>(p);const unsigned i=c.calls++;return c.value[i<2?i:1];}};
int main(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    Clock c={{3,3.25f}};RF455CameraClock clock={&c,&Clock::read};RF455CameraPlayback s={60,120,1,0,9,10};REQUIRE(!RF455_AdvanceCamera(s,1,false,clock)&&s.nowFrame==4&&s.oldFrame==10&&c.calls==1);
    c.calls=0;s={60,120,0,0,0,0};REQUIRE(!RF455_AdvanceCamera(s,1,false,clock)&&s.nowFrame==60&&s.startTick==3.25f&&c.calls==2);
    c.calls=0;s={120,60,1,0,0,0};REQUIRE(RF455_AdvanceCamera(s,1,false,clock)&&s.nowFrame==1&&c.calls==1);
    c={{5,5.25f}};s={120,60,1,0,0,1};REQUIRE(!RF455_AdvanceCamera(s,1,false,clock)&&s.nowFrame==0&&c.calls==1);
    c.calls=0;s={120,60,0,0,0,1};REQUIRE(!RF455_AdvanceCamera(s,1,false,clock)&&s.nowFrame==2&&s.startTick==5.25f&&c.calls==2);
    c.calls=0;s={60,120,1,0,0,3};REQUIRE(RF455_AdvanceCamera(s,1,true,clock)&&s.nowFrame==3&&c.calls==0);
    s.nowFrame=5;REQUIRE(!RF455_AdvanceCamera(s,1,true,clock)&&s.nowFrame==4&&c.calls==0);
    c.calls=0;s={60,120,0,0,0,5};REQUIRE(!RF455_AdvanceCamera(s,1,true,clock)&&s.nowFrame==60&&c.calls==1);
    RF455CameraDocument synthetic;synthetic.version=1.3f;synthetic.end=90;synthetic.cameras.resize(1);auto& camera=synthetic.cameras[0];std::memset(camera.name,0,64);std::memcpy(camera.name,"fixture",7);camera.fov=1;camera.distance=10;camera.hierarchy.resize(1);auto& n=camera.hierarchy[0];std::memset(n.matrix,0,64);n.matrix[0]=n.matrix[5]=n.matrix[10]=n.matrix[15]=1;std::memset(n.position,0,12);std::memset(n.rotation,0,16);n.rotation[3]=1;camera.fovKeys={RF455CameraFovKey{0,{1,2,3,4}},RF455CameraFovKey{90,{2,3,4,5}}};
    auto valid=encode(synthetic);RF455CameraDocument parsed;REQUIRE(RF455_ParseCamera(valid.data(),valid.size(),parsed)&&encode(parsed)==valid);
    for(std::size_t size=0;size<valid.size();++size)REQUIRE(!RF455_ParseCamera(valid.data(),size,parsed)&&encode(parsed)==valid);
    auto malformed=valid;std::memset(malformed.data()+4,255,4);REQUIRE(!RF455_ParseCamera(malformed.data(),malformed.size(),parsed));
    int marker=0;RF455_StoreCameraDocument(&marker,std::move(parsed));float fov=0;REQUIRE(RF455_CameraFov(&marker,0,1.5f,fov)&&std::fabs(fov-1.182f)<1e-6f);REQUIRE(RF455_CameraFov(&marker,0,-1,fov)&&std::fabs(fov-1.576f)<1e-6f);RF455_ForgetCameraDocument(&marker);REQUIRE(!RF455_GetCameraDocument(&marker));
    FILE* sample=std::fopen("synthetic13.cam","wb");REQUIRE(sample);REQUIRE(std::fwrite(valid.data(),1,valid.size(),sample)==valid.size());std::fclose(sample);
    InitR3Engine();auto* state=GetR3State();state->mScreenXsize=640;state->mScreenYsize=480;state->mbFullScreen=FALSE;ForceFullScreen();REQUIRE(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)));
    unsigned files=0,allCameras=0,allObjects=0,allDummies=0;
    for(const char* name:{"bellato","cora","accretia","lobby","synthetic13"}){
        char path[256];if(!std::strcmp(name,"synthetic13"))std::strcpy(path,"synthetic13.cam");else std::sprintf(path,"Map/%s/%s.cam",name,name);
        RF455CameraDocument doc;REQUIRE(RF455_LoadCameraFile(path,doc));const auto encoded=encode(doc);char output[128];std::sprintf(output,"%s.roundtrip.cam",name);FILE* out=std::fopen(output,"wb");REQUIRE(out);REQUIRE(std::fwrite(encoded.data(),1,encoded.size(),out)==encoded.size());std::fclose(out);
        const int baseline=GetDmallocSize();CAniCamera actual;REQUIRE(!actual.IsLoadedAniCamera());actual.LoadAniCamera(path);REQUIRE(actual.GetCameraNum()==doc.cameras.size()&&actual.GetStartFrame()==doc.start&&actual.GetEndFrame()==doc.end&&RF455_GetCameraDocument(&actual));
        auto* records=actual.*access(Cameras{});for(unsigned i=0;i<doc.cameras.size();++i){const auto& expected=doc.cameras[i];REQUIRE(!std::memcmp(actual.GetCameraName(i),expected.name,64)&&records[i].fov==expected.fov&&records[i].tdist==expected.distance&&records[i].h_num==expected.hierarchy.size());for(unsigned j=0;j<expected.hierarchy.size();++j){REQUIRE(equalNode(records[i].obj[j],expected.hierarchy[j]));++allObjects;}}
        REQUIRE((actual.*access(DummyCount{}))==doc.dummies.size());auto* dummies=actual.*access(Dummies{});for(unsigned i=0;i<doc.dummies.size();++i)REQUIRE(equalNode(dummies[i],doc.dummies[i].node)&&!std::memcmp(dummies[i].ObjectName,doc.dummies[i].name,64)&&!std::memcmp(dummies[i].ParentName,doc.dummies[i].parentName,64));
        actual.LoadAniCamera("missing-owned-fixture.cam");REQUIRE(actual.GetCameraNum()==doc.cameras.size());actual.SetPrePlayCamera(0,_CAM_PLAY_FULL_FRAME,_CAM_PLAY_FULL_FRAME,_CAM_FLAG_FINAL_STOP);
        actual.*access(Now{})=0;float matrix[4][4];REQUIRE(actual.PlayAniCamera(matrix,1,TRUE));for(unsigned i=0;i<16;++i)REQUIRE(std::isfinite((&matrix[0][0])[i]));REQUIRE(std::fabs(state->mFov-doc.cameras[0].fov*0.788f)<1e-6f);
        D3DXMATRIX projection;REQUIRE(SUCCEEDED(GetD3dDevice()->GetTransform(D3DTS_PROJECTION,&projection))&&!std::memcmp(&projection,&state->mMatProj,64));
        actual.*access(Now{})=static_cast<float>(doc.end/30.0+1);REQUIRE(!actual.PlayAniCamera(matrix,1,TRUE)&&actual.GetNowFrame()==static_cast<float>(doc.end/30.0));
        if(!std::strcmp(name,"synthetic13")){
            actual.SetPrePlayCamera(0,90,30,_CAM_FLAG_FINAL_STOP);actual.*access(Now{})=0.5f;
            REQUIRE(actual.PlayAniCamera(matrix,1,TRUE)&&actual.GetNowFrame()==0.5f);
            actual.*access(Now{})=-1;REQUIRE(!actual.PlayAniCamera(matrix,1,TRUE)&&actual.GetNowFrame()==0);
            actual.SetPrePlayCamera(0,30,90,_CAM_FLAG_LOOP);actual.*access(Now{})=4;
            REQUIRE(!actual.PlayAniCamera(matrix,1,TRUE)&&actual.GetNowFrame()==30);
        }
        actual.ReleaseAniCamera();REQUIRE(!actual.IsLoadedAniCamera()&&!RF455_GetCameraDocument(&actual)&&GetDmallocSize()==baseline);actual.ReleaseAniCamera();REQUIRE(GetDmallocSize()==baseline);++files;allCameras+=doc.cameras.size();allDummies+=doc.dummies.size();
    }
    g_MainApp.ReleaseR3D3D();ReleaseR3Engine();FILE* result=std::fopen("result.json","wb");REQUIRE(result);std::fprintf(result,"{\"status\":\"PASS\",\"files\":%u,\"cameras\":%u,\"camera_nodes\":%u,\"dummies\":%u,\"wire_roundtrip\":true,\"actual_camera_materialization\":true,\"actual_play_projection\":true,\"actual_release_balance\":true,\"synthetic13_fov\":true,\"playback_clock_and_boundaries\":true,\"bounded_truncation\":true,\"fullTutorial\":false}\n",files,allCameras,allObjects,allDummies);std::fclose(result);return 0;
}
