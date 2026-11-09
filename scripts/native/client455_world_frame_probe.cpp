#define main oldWorldEntry120
#include "client455_world_probe.cpp"
#undef main
#include "addcodebyjang/effectcore.h"
#include "addcodebyjang/effectentitylist.h"
#include "client455_quake.h"
#include "client455_loop_clock.h"
#include "RTMovie.h"
#include <client455_normal_renderer_math.h>
#include <vector>
struct LightFaces120{using Type=_BSP_C_FACE* CBsp::*;friend Type access(LightFaces120);};template struct MemberAccess<LightFaces120,&CBsp::mCFace>;
struct LightFaceIds120{using Type=DWORD* CBsp::*;friend Type access(LightFaceIds120);};template struct MemberAccess<LightFaceIds120,&CBsp::mCFaceId>;

static FILE* log120;
static unsigned bits120(float x){unsigned u;std::memcpy(&u,&x,4);return u;}
static void inspectLight120(CLevel& level,float* point,void* texture){
    float lo[3],hi[3];for(unsigned i=0;i<3;++i){lo[i]=point[i]-2400.f/7;hi[i]=point[i]+2400.f/7;}LONG count=0;SHORT leaves[256];level.mBsp->GetFastLeafListFromBBox(lo,hi,&count,leaves,256);unsigned faces=0,up=0;auto* all=level.mBsp->*access(LightFaces120{});auto* ids=level.mBsp->*access(LightFaceIds120{});
    for(LONG i=0;i<count;++i){const auto& leaf=level.mBsp->mLeaf[leaves[i]];for(unsigned j=0;j<leaf.face_num;++j){const auto& face=all[ids[leaf.face_start_id+j]];++faces;up+=face.Normal[1]>0&&!(face.Attr&_CFACE_WATER);}}
    D3DSURFACE_DESC desc={};check(SUCCEEDED(static_cast<IDirect3DTexture9*>(texture)->GetLevelDesc(0,&desc)),"actual light texture descriptor");using Save=HRESULT(WINAPI*)(const char*,D3DXIMAGE_FILEFORMAT,IDirect3DBaseTexture9*,const PALETTEENTRY*);auto save=reinterpret_cast<Save>(GetProcAddress(GetModuleHandleA("d3dx9_36.dll"),"D3DXSaveTextureToFileA"));check(save&&SUCCEEDED(save("lamp-texture.dds",D3DXIFF_DDS,static_cast<IDirect3DTexture9*>(texture),nullptr)),"preserve actual light texture");FILE* f=std::fopen("light-diagnostic.json","wb");check(f!=nullptr,"light diagnostic");std::fprintf(f,"{\"leaves\":%ld,\"faces\":%u,\"upward\":%u,\"texture_width\":%u,\"texture_height\":%u,\"texture_format\":%u}\n",count,faces,up,desc.Width,desc.Height,unsigned(desc.Format));std::fclose(f);
}
static void floats120(const float* p,unsigned n){std::fputc('[',log120);for(unsigned i=0;i<n;++i)std::fprintf(log120,"%s%u",i?",":"",bits120(p[i]));std::fputc(']',log120);}
static void snapshot120(const char* op,unsigned step,BOOL accepted,const float* input=nullptr,unsigned n=0){
    std::fprintf(log120,"{\"op\":\"%s\",\"step\":%u,\"accepted\":%d,\"limit\":%u,\"input\":",op,step,accepted,GetR3State()->mDynamicLight);floats120(input,n);std::fputs(",\"lights\":[",log120);
    for(unsigned i=0;i<GetDynamicLightNum();++i){float pos[3],diameter,lo[3],hi[3];DWORD color,blend;void* tex;GetDynamicLight(i,pos,&diameter,&color,&tex,&blend);GetDynamicLightBBox(i,&lo,&hi);std::fprintf(log120,"%s{\"color\":%u,\"texture\":%u,\"magic\":%d,\"blend\":%u,\"values\":",i?",":"",color,unsigned(tex),IsMagicLight(i),blend);float p[]={pos[0],pos[1],pos[2],diameter,lo[0],lo[1],lo[2],hi[0],hi[1],hi[2]};floats120(p,10);std::fputc('}',log120);}
    std::fputs("]}\n",log120);
}
static void lightCases120(){
    log120=std::fopen("lights.jsonl","wb");check(log120!=nullptr,"light trace");
    for(unsigned limit:{0u,1u,3u,10u,12u}){
        ClearDynamicLight();GetR3State()->mDynamicLight=limit;snapshot120("clear",0,TRUE);
        for(unsigned i=0;i<13;++i){float p[]={float(i*19)-77,float(i)-4,45-float(i*11)},diameter=i==0?0:i==1?-3.f:float(i*17)+.25f;const auto accepted=InsertDynamicLight(p,diameter,0x813b4c00u+i,reinterpret_cast<void*>(i+1),i%3?7:0,i%4);float input[]={p[0],p[1],p[2],diameter};snapshot120("insert",i,accepted,input,4);}
        GetR3State()->mDynamicLight=1;float p[]={3,5,7};const auto accepted=InsertDynamicLight(p,4,0xfedcba98,reinterpret_cast<void*>(88),-1,9);float input[]={3,5,7,4};snapshot120("shrink",0,accepted,input,4);
    }
    ClearDynamicLight();snapshot120("clear",0,TRUE);std::fclose(log120);
}
static void clockQuake120(){
    log120=std::fopen("clock-quake.jsonl","wb");check(log120!=nullptr,"clock trace");bool positive=false,negative=false;D3DXMatrixIdentity(&GetR3State()->mMatView);
    R3CalculateTime();
    for(unsigned i=0;i<16;++i){Sleep(12);R3CalculateTime();const float dt=R3GetLoopTime();const LONG toggle=R3GetToggle30fps();positive|=toggle>0;negative|=toggle<0;if(!i)R3EnvironmentQuake(.3f,6);float out[3];R3GetQuakeVector(out);std::fprintf(log120,"{\"dt\":%u,\"toggle\":%ld,\"remaining\":%u,\"output\":",bits120(dt),toggle,bits120(RF455_QuakeState().remaining));floats120(out,3);std::fputs("}\n",log120);}
    std::fclose(log120);check(positive&&negative,"actual OS clock produces both quake signs");R3EnvironmentQuake(0,0);
}
static void drawWorld120(CLevel& level,const char* name,bool effects){
    auto* device=GetD3dDevice();check(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET|D3DCLEAR_ZBUFFER,0xff102030,1,0)),"clear");check(SUCCEEDED(device->BeginScene()),"begin");level.DrawSkyBoxRender();std::fprintf(stderr,"frame:%s lights=%u limit=%u\n",name,GetDynamicLightNum(),GetR3State()->mDynamicLight);level.DrawMapRender();
    if(GetDynamicLightNum()){float p[3],diameter;DWORD color,blend,passes=0,cull,zfunc;void* texture;GetDynamicLight(0,p,&diameter,&color,&texture,&blend);SetDynamicLight(p,diameter,color,texture,!IsMagicLight(0),blend);HRESULT bind=RF455_SetFixedVertexFormat(device,D3DFVF_R3VERTEX_TEX0);HRESULT validation=device->ValidateDevice(&passes);device->GetRenderState(D3DRS_CULLMODE,&cull);device->GetRenderState(D3DRS_ZFUNC,&zfunc);std::fprintf(stderr,"light-state bind=%08lx validate=%08lx passes=%u cull=%u zfunc=%u\n",bind,validation,passes,cull,zfunc);UnSetDynamicLight();}
    level.DrawMapEntitiesRender();if(effects)RenderAllEffectsList();check(SUCCEEDED(device->EndScene()),"end");check(capture(name)>100,"actual world capture");
}
static int runFrame120(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);InitR3Engine();SetWarningMessageProc(warningMessage);SetErrorMessageProc(errorMessage);auto* state=GetR3State();state->mScreenXsize=640;state->mScreenYsize=480;state->mbFullScreen=FALSE;ForceFullScreen();check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"device");R3SetViewPort(0,0,640,480);lightCases120();clockQuake120();
    {
        ChInterface renderer;renderer.InitCharacter(GetD3dDevice());CCamera camera;g_pCamera=&camera;std::unique_ptr<CLand> land(new CLand);check(land->Create()&&land->LoadLevel(".\\Map\\bellato\\bellato.bsp"),"real Bellato");auto& level=*land->GetLevel();
        float matrix[4][4];D3DXVECTOR3 eye(2466,477,-1429),focus(2466,277,-1129),up(0,1,0);D3DXMatrixLookAtLH(reinterpret_cast<D3DXMATRIX*>(matrix),&eye,&focus,&up);D3DXMATRIX inverse;D3DXMatrixInverse(&inverse,nullptr,reinterpret_cast<D3DXMATRIX*>(matrix));float position[]={inverse._41,inverse._42,inverse._43};level.SetCameraPos(position);level.SetViewMatrix(reinterpret_cast<D3DXMATRIX*>(matrix));state->mInvMatView=inverse;D3DXMatrixMultiply(&state->mMatViewProj,&state->mMatView,&state->mMatProj);R3SetTime(.5f);R3SetLoopTime(1.f/30);level.FrameMove();check(!GetDynamicLightNum(),"CLevel FrameMove clears queue");drawWorld120(level,"frame-base.bgra",false);
        float point[3]={};bool hit=false;for(int y:{360,420,300,240})if(level.GetPointFromScreenRay(320,y,&point)){hit=true;break;}check(hit,"camera ray hits real world");float floorPoint[3]={2466,277,-1129},height=0;check(level.GetNextYpos(floorPoint,&height),"actual tutorial spawn floor");point[0]=floorPoint[0];point[1]=height+3;point[2]=floorPoint[2];state->mDynamicLight=3;
        ClearDynamicLight();CreateEffectsList(".\\Effect\\EffectEntityList.spt");CreateMagicSptList(".\\Effect\\MagicSptList.spt");auto effect=StartMagicEffect(point,0,1358041136,nullptr,_EF_STATE_ALWAYS_LIVE);check(effect!=0,"archived targeting cue");unsigned populated=0;
        for(unsigned i=0;i<16;++i){R3SetTime(i/30.f);level.SetCameraPos(position);level.SetViewMatrix(reinterpret_cast<D3DXMATRIX*>(matrix));state->mInvMatView=inverse;D3DXMatrixMultiply(&state->mMatViewProj,&state->mMatView,&state->mMatProj);level.FrameMove();check(!GetDynamicLightNum(),"ordinary frame clears previous lights");FrameMoveAllEffectsList();populated+=GetDynamicLightNum()>0;}
        check(populated>0,"actual FX supplies light queue after world preparation");float lampPos[3],lampDiameter;DWORD lampColor,lampBlend;void* lampTexture=nullptr;GetDynamicLight(0,lampPos,&lampDiameter,&lampColor,&lampTexture,&lampBlend);check(lampTexture!=nullptr,"real archived light texture");inspectLight120(level,point,lampTexture);drawWorld120(level,"frame-effects.bgra",true);level.SetCameraPos(position);level.SetViewMatrix(reinterpret_cast<D3DXMATRIX*>(matrix));state->mInvMatView=inverse;D3DXMatrixMultiply(&state->mMatViewProj,&state->mMatView,&state->mMatProj);level.FrameMove();check(InsertDynamicLight(point,2400,0xffe08040,lampTexture,TRUE,_BLEND_BRIGHT),"magic light");drawWorld120(level,"frame-magic.bgra",false);level.SetCameraPos(position);level.SetViewMatrix(reinterpret_cast<D3DXMATRIX*>(matrix));state->mInvMatView=inverse;D3DXMatrixMultiply(&state->mMatViewProj,&state->mMatView,&state->mMatProj);level.FrameMove();check(InsertDynamicLight(point,2400,0xff4080e0,lampTexture,FALSE,_BLEND_BRIGHT),"regular light");drawWorld120(level,"frame-regular.bgra",false);check(SetDisapearTimeMagicEffect(effect,0),"cancel FX");for(unsigned i=0;i<360&&(GetEffectListCnt()||GetMagicListCnt());++i){ClearDynamicLight();FrameMoveAllEffectsList();}check(!GetEffectListCnt()&&!GetMagicListCnt(),"FX drain");level.SetCameraPos(position);level.SetViewMatrix(reinterpret_cast<D3DXMATRIX*>(matrix));state->mInvMatView=inverse;D3DXMatrixMultiply(&state->mMatViewProj,&state->mMatView,&state->mMatProj);level.FrameMove();drawWorld120(level,"frame-cleared.bgra",false);
        log120=std::fopen("world-frame.json","wb");check(log120!=nullptr,"world trace");std::fprintf(log120,"{\"world\":\"bellato\",\"actual_clock\":true,\"positive_and_negative_toggle\":true,\"ray_hit\":true,\"FX_light_frames\":%u,\"light_point\":",populated);floats120(point,3);std::fputs("}\n",log120);std::fclose(log120);DestroyEffectsList();DestroyMagicSptList();check(land->Destroy()!=0,"world release");RTMovieRelease();g_pCamera=nullptr;
    }
    RF455_ReleaseNormalCharacterSharedResources();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();FILE* result=std::fopen("result.json","wb");check(result!=nullptr,"result");std::fprintf(result,"{\"status\":\"PASS\",\"GPU_frames\":5,\"warnings\":%u,\"full_client\":false}\n",warnings);std::fclose(result);return 0;
}
int main(){try{return runFrame120();}catch(const std::exception& e){std::fprintf(stderr,"world-frame120:%s\n",e.what());return 1;}}
