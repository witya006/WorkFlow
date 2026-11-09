#define main unusedWorldEntrySky123
#include "client455_world_probe.cpp"
#undef main
static int runSky123(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);InitR3Engine();SetWarningMessageProc(warningMessage);SetErrorMessageProc(errorMessage);auto* s=GetR3State();s->mScreenXsize=640;s->mScreenYsize=480;s->mbFullScreen=FALSE;ForceFullScreen();std::strcpy(s->MapPath,".\\Map\\");std::strcpy(s->EntityPath,".\\Map\\Entity\\");check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"device");
    unsigned pixels=0;{
        CCamera camera;g_pCamera=&camera;CLand land;check(land.Create()!=0,"land");char path[]=".\\Map\\bellato\\bellato.bsp";check(land.LoadLevel(path)!=0,"real Bellato");auto& level=*land.GetLevel();check(level.mSkyBox->IsLoaded455(),"actual Bellato sky loaded");s->mFov=.6f;s->mAsfectRatio=640.f/480;s->mFar=6000;s->mNear=17;R3SetTime(.5f);R3SetLoopTime(1.f/30);
        auto frame=[&](const char* name,float x,BOOL ortho,float nearPlane){
            s->mNear=nearPlane;s->mOrthographic=ortho;s->mOrthographicScale=5;D3DXVECTOR3 eye(x,477,-1429),at(x,477,-1129),up(0,1,0);D3DXMATRIX view;D3DXMatrixLookAtLH(&view,&eye,&at,&up);float position[]={eye.x,eye.y,eye.z};level.SetCameraPos(position);level.SetViewMatrix(&view);D3DXMatrixInverse(&s->mInvMatView,nullptr,&s->mMatView);D3DXMatrixPerspectiveFovLH(&s->mMatProj,s->mFov,s->mAsfectRatio,nearPlane,s->mFar);D3DXMatrixMultiply(&s->mMatViewProj,&s->mMatView,&s->mMatProj);level.FrameMove();auto* d=GetD3dDevice();check(SUCCEEDED(d->Clear(0,nullptr,D3DCLEAR_TARGET|D3DCLEAR_ZBUFFER,0xff102030,1,0))&&SUCCEEDED(d->BeginScene()),"begin");level.DrawSkyBoxRender();check(SUCCEEDED(d->EndScene()),"end");return capture(name);
        };
        pixels=frame("sky-base.bgra",2466,FALSE,17);check(pixels>100,"visible actual sky");check(frame("sky-translated.bgra",3466,FALSE,17)==pixels,"sky translation count");check(frame("sky-near3000.bgra",2466,FALSE,3000)==pixels,"temporary sky near2 count");check(frame("sky-ortho.bgra",2466,TRUE,17)==pixels,"sky always perspective count");level.mSkyBox->ReleaseSkyBox();check(!level.mSkyBox->IsLoaded455(),"actual sky release");check(frame("sky-unloaded.bgra",2466,FALSE,17)==0,"unloaded sky leaves clear control");land.Destroy();g_pCamera=nullptr;
    }
    g_MainApp.ReleaseR3D3D();ReleaseR3Engine();FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"result");std::fprintf(out,"{\"status\":\"PASS\",\"GPU_frames\":5,\"visible_sky_pixels\":%u,\"actual_Bellato_sky\":true,\"warnings\":%u,\"full_client\":false}\n",pixels,warnings);std::fclose(out);return 0;
}
int main(){try{return runSky123();}catch(const std::exception& e){std::fprintf(stderr,"sky-world123:%s\n",e.what());return 1;}}
