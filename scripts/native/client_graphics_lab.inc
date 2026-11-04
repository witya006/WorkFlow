// Own hidden-window graphics entry in the full client. No input game startup.
#include "r3enginekernel.h"
#include "r3d3d8.h"
#include "r3d3dtex.h"
#include "r3render.h"
#include "entity.h"
#include "renderparticle.h"
#include "commonutil.h"
#include "jerror.h"
#include "client455_resource_io.h"
#include "level.h"
#if defined(RF_CLIENT_455_MAP_TIME)
#include "Character.h"
#include "global.h"
#include "cland.h"
#include "network/netmsgprocessor/map/cnetmsgprocessor_map.h"
#include <time.h>
#endif

struct GraphicsResult {
    char output[32768];const char* stage;
    unsigned checks,failures,warnings,errors;
    unsigned short fpInitial,fpAfterEngine,fpAfterDevice;
    HRESULT hr;DWORD flags,format;char adapter[512];
    DWORD textureWidth,textureHeight,textureLevels,textureFormat;
    unsigned changedPixels;BOOL entityLoaded,entityDrawn;int entityGroups,entityTextures;
    int allocationBefore,allocationAfter;
    BOOL particleLoaded;unsigned particleCount,particleLive,simulationFrames;
    BOOL levelLoaded;unsigned levelLeaves,levelNodes,levelHelpers,visibleGroups;
    unsigned interiors,weatherCounts[2],weatherStates[3][2],weatherChecks;
    ULONG deviceRefs,d3dRefs;
    unsigned short fpAfterLoad,fpBeforeDraw,fpAfterDraw,weatherFP[3][2];
};
static GraphicsResult graphicsResult={};
static void graphicsString(FILE* fp,const char* s) {
    fputc('"',fp);
    for (const unsigned char* p=(const unsigned char*)s;*p;++p) {
        if (*p=='"' || *p=='\\') { fputc('\\',fp);fputc(*p,fp); }
        else if (*p<32 || *p>126) fprintf(fp,"\\u%04x",(unsigned)*p);
        else fputc(*p,fp);
    }
    fputc('"',fp);
}
static void graphicsReport(const char* stage) {
    graphicsResult.stage=stage;
    FILE* fp=fopen(graphicsResult.output,"wb");if (!fp) ExitProcess(81);
    fprintf(fp,"{\"stage\":");graphicsString(fp,stage);fprintf(fp,",\"adapter\":");graphicsString(fp,graphicsResult.adapter);
    fprintf(fp,",\"checks\":%u,\"failures\":%u,\"warnings\":%u,\"errors\":%u,\"hr\":%u,\"device_flags\":%lu,\"backbuffer_format\":%lu,\"fpu\":[%u,%u,%u],\"texture\":[%lu,%lu,%lu,%lu],\"changed_pixels\":%u,\"entity_loaded\":%d,\"entity_drawn\":%d,\"entity_groups\":%d,\"entity_textures\":%d,\"allocation_before\":%d,\"allocation_after\":%d,\"device_refs_after_release\":%lu,\"d3d_refs_after_release\":%lu}\n",
        graphicsResult.checks,graphicsResult.failures,graphicsResult.warnings,graphicsResult.errors,(unsigned)graphicsResult.hr,
        graphicsResult.flags,graphicsResult.format,graphicsResult.fpInitial,graphicsResult.fpAfterEngine,graphicsResult.fpAfterDevice,
        graphicsResult.textureWidth,graphicsResult.textureHeight,graphicsResult.textureLevels,graphicsResult.textureFormat,
        graphicsResult.changedPixels,graphicsResult.entityLoaded,graphicsResult.entityDrawn,graphicsResult.entityGroups,graphicsResult.entityTextures,
        graphicsResult.allocationBefore,graphicsResult.allocationAfter,graphicsResult.deviceRefs,graphicsResult.d3dRefs);
    fclose(fp);
    FILE* ff=fopen("fpu.json","wb");
    if (ff) { fprintf(ff,"{\"after_load\":%u,\"before_draw\":%u,\"after_draw\":%u,\"weather\":[[%u,%u],[%u,%u],[%u,%u]]}\n",graphicsResult.fpAfterLoad,graphicsResult.fpBeforeDraw,graphicsResult.fpAfterDraw,graphicsResult.weatherFP[0][0],graphicsResult.weatherFP[0][1],graphicsResult.weatherFP[1][0],graphicsResult.weatherFP[1][1],graphicsResult.weatherFP[2][0],graphicsResult.weatherFP[2][1]);fclose(ff); }
    // Keep particle fields in a separate machine-readable companion to avoid
    // changing the earlier graphics record's field meanings.
    if (graphicsResult.particleLoaded) {
        FILE* pf=fopen("particle.json","wb");
        if (pf) { fprintf(pf,"{\"loaded\":%d,\"count\":%u,\"live\":%u,\"frames\":%u}\n",graphicsResult.particleLoaded,graphicsResult.particleCount,graphicsResult.particleLive,graphicsResult.simulationFrames);fclose(pf); }
    }
    if (graphicsResult.levelLoaded) {
        FILE* lf=fopen("level.json","wb");
        if (lf) { fprintf(lf,"{\"loaded\":%d,\"leaves\":%u,\"nodes\":%u,\"helpers\":%u,\"visible_groups\":%u,\"interiors\":%u,\"weather_counts\":[%u,%u],\"weather_states\":[[%u,%u],[%u,%u],[%u,%u]],\"weather_checks\":%u}\n",graphicsResult.levelLoaded,graphicsResult.levelLeaves,graphicsResult.levelNodes,graphicsResult.levelHelpers,graphicsResult.visibleGroups,graphicsResult.interiors,graphicsResult.weatherCounts[0],graphicsResult.weatherCounts[1],graphicsResult.weatherStates[0][0],graphicsResult.weatherStates[0][1],graphicsResult.weatherStates[1][0],graphicsResult.weatherStates[1][1],graphicsResult.weatherStates[2][0],graphicsResult.weatherStates[2][1],graphicsResult.weatherChecks);fclose(lf); }
    }
}
static void graphicsWarning(char*) { ++graphicsResult.warnings; }
static void graphicsError(char*) { ++graphicsResult.errors;graphicsReport("engine-error");ExitProcess(82); }
static bool graphicsHR(HRESULT hr) { graphicsResult.hr=hr;++graphicsResult.checks;if (FAILED(hr)) { ++graphicsResult.failures;return false; }return true; }
static bool graphicsCheck(bool value) { ++graphicsResult.checks;if (!value)++graphicsResult.failures;return value; }
static unsigned short graphicsFP() { unsigned short value;__asm { fnstcw value }return value; }

#if defined(RF_CLIENT_455_MAP_TIME)
static DWORD WINAPI graphicsTimeTick() { return 0x23456789; }
static void graphicsMapTime(CLand* land) {
    const char* env=getenv("TZ");const std::string oldTZ=env?env:"";
    _putenv_s("TZ","UTC0");_tzset();auto provider=RF455_ClockTickSource;
    RF455_ClockTickSource=&graphicsTimeTick;
    char payload[9]={0x7F};const DWORD value=0x11223344,timestamp=43200;
    memcpy(payload+1,&value,4);memcpy(payload+5,&timestamp,4);
    _MSG_HEADER header={};header.m_wSize=13;header.m_byType[0]=8;header.m_byType[1]=5;
    CNetMsgProcessor_Map processor;
    graphicsCheck(processor.AnalysisServerPacket(&header,payload));
    const RF455_MapTimeState& received=land->GetMapTime455();
    graphicsCheck(received.value0==value && received.timestamp==timestamp && received.receiptTick==graphicsTimeTick());
    land->ApplyMapTime455(12);
    graphicsCheck(received.mapDay==1);
    graphicsCheck(RF455_GetDayFraction()==.5f && RF455_GetRealDayFraction()==.5f);
    graphicsCheck(graphicsFP()==0x007F);
    FILE* output=fopen("map-time.json","wb");graphicsCheck(output!=NULL);
    if (output) { fprintf(output,"{\"message\":[8,5],\"value0\":%u,\"timestamp\":%u,\"receipt_tick\":%u,\"map_day\":%u,\"game_fraction\":%.9g,\"real_fraction\":%.9g,\"fpu\":%u,\"client_processor_called\":true,\"land_hook_called\":true}\n",received.value0,received.timestamp,received.receiptTick,received.mapDay,RF455_GetDayFraction(),RF455_GetRealDayFraction(),graphicsFP());fclose(output); }
    RF455_ClockTickSource=provider;_putenv_s("TZ",oldTZ.c_str());_tzset();
}
#endif

static void graphicsLevelCamera(CLevel* level,Vector3f camera,Vector3f target) {
    _R3ENGINE_STATE* state=GetR3State();D3DXVECTOR3 eye(camera),at(target),up(0,1,0);
    D3DXMatrixLookAtLH(&state->mMatView,&eye,&at,&up);
    D3DXMatrixInverse(&state->mInvMatView,NULL,&state->mMatView);
    level->SetCameraPos(camera);level->SetViewMatrix(&state->mMatView);
}

static void graphicsLevelWeather(CLevel* level) {
#if defined(RF_CLIENT_455_WEATHER)
    DWORD count=0,indices[1024];level->mDummy.GetDummyList(4,&count,indices);
    graphicsResult.interiors=count;
    CParticle* particles[2]={level->mBsp->GetEnvironmentParticle455(0),level->mBsp->GetEnvironmentParticle455(1)};
    if (!count || !GetR3State()->mEnvIDs[0] || !GetR3State()->mEnvIDs[1]) return;
    if (!graphicsCheck(particles[0] && particles[1])) return;
    for (unsigned i=0;i<2;++i) graphicsResult.weatherCounts[i]=(unsigned)particles[i]->mNum;
    _EXT_DUMMY* dummy=level->mDummy.GetDummy(indices[0]);Vector3f local,inside,outside={30000,30000,30000};
    for (unsigned i=0;i<3;++i) local[i]=(dummy->mBBmin[i]+dummy->mBBmax[i])*0.5f;
    if (!graphicsCheck(level->mDummy.GetWorldFromLocal(&inside,indices[0],local)!=FALSE)) return;
    graphicsCheck(level->mDummy.IsInBBox(indices[0],inside)!=FALSE);
    for (DWORD i=0;i<count;++i) graphicsCheck(level->mDummy.IsInBBox(indices[i],outside)==FALSE);
    for (unsigned scenario=0;scenario<3;++scenario) {
        Vector3f camera,target;
        memcpy(camera,scenario==0?inside:outside,sizeof(camera));memcpy(target,camera,sizeof(target));target[2]+=100;
        graphicsLevelCamera(level,camera,target);
        RF455_SetDayFraction(scenario==2?0.5f:0.0f);R3SetTime(0);R3SetLoopTime(0);
        graphicsResult.weatherFP[scenario][0]=graphicsFP();level->FrameMove();graphicsResult.weatherFP[scenario][1]=graphicsFP();
        for (unsigned layer=0;layer<2;++layer) {
            graphicsResult.weatherStates[scenario][layer]=particles[layer]->GetParticleState();
            graphicsCheck(graphicsResult.weatherStates[scenario][layer]==(scenario==1?1u:0u));
            ++graphicsResult.weatherChecks;
        }
    }
    RF455_SetDayFraction(0);
#endif
}

static bool graphicsCapture(LPDIRECT3DDEVICE8 device) {
    LPDIRECT3DSURFACE8 surface=NULL;D3DLOCKED_RECT locked;
    if (!graphicsHR(device->GetBackBuffer(0,D3DBACKBUFFER_TYPE_MONO,&surface))) return false;
    if (!graphicsHR(surface->LockRect(&locked,NULL,D3DLOCK_READONLY))) { surface->Release();return false; }
    BITMAPFILEHEADER file={};BITMAPINFOHEADER info={};
    file.bfType=0x4d42;file.bfOffBits=sizeof(file)+sizeof(info);file.bfSize=file.bfOffBits+640*480*3;
    info.biSize=sizeof(info);info.biWidth=640;info.biHeight=-480;info.biPlanes=1;info.biBitCount=24;info.biCompression=BI_RGB;
    FILE* fp=fopen("frame.bmp","wb");if (!fp) { surface->UnlockRect();surface->Release();return false; }
    fwrite(&file,sizeof(file),1,fp);fwrite(&info,sizeof(info),1,fp);
    for (int y=0;y<480;++y) {
        const BYTE* row=(BYTE*)locked.pBits+y*locked.Pitch;
        for (int x=0;x<640;++x) {
            if (row[x*4]!=0x30 || row[x*4+1]!=0x20 || row[x*4+2]!=0x10) ++graphicsResult.changedPixels;
            fwrite(row+x*4,3,1,fp);
        }
    }
    fclose(fp);surface->UnlockRect();surface->Release();return true;
}

static unsigned graphicsProbe(unsigned mode) {
    const bool entityMode=mode==1,particleMode=mode==2,levelMode=mode==3;
    DWORD length=GetEnvironmentVariableA("RF_LAB_HELPER_OUTPUT",graphicsResult.output,sizeof(graphicsResult.output));
    if (!length || length>=sizeof(graphicsResult.output)) return 83;
    graphicsResult.fpInitial=graphicsFP();graphicsResult.allocationBefore=GetDmallocSize();
    graphicsReport("starting");SetErrorMessageProc(graphicsError);SetWarningMessageProc(graphicsWarning);
    const char* delayed[]={"mss32.dll","ABuse.dll","Adv.dll","PDLL.dll"};
    for (unsigned i=0;i<4;++i) graphicsCheck(GetModuleHandleA(delayed[i])==NULL);
    InitR3Engine();graphicsResult.fpAfterEngine=graphicsFP();graphicsReport("engine-initialized");
    HINSTANCE instance=GetModuleHandleA(NULL);
    WNDCLASSA cls={};cls.lpfnWndProc=DefWindowProcA;cls.hInstance=instance;cls.lpszClassName="RFClientGraphicsLab455";
    RegisterClassA(&cls);
    HWND window=CreateWindowExA(WS_EX_NOACTIVATE|WS_EX_TOOLWINDOW,cls.lpszClassName,"RF client graphics lab",WS_OVERLAPPEDWINDOW,0,0,640,480,NULL,NULL,instance,NULL);
    if (!graphicsCheck(window!=NULL)) return 84;
    LPDIRECT3D8 d3d=Direct3DCreate8(D3D_SDK_VERSION);
    if (!graphicsCheck(d3d!=NULL)) { graphicsReport("no-d3d8");return 85; }
    D3DADAPTER_IDENTIFIER8 adapter={};d3d->GetAdapterIdentifier(D3DADAPTER_DEFAULT,0,&adapter);strcpy(graphicsResult.adapter,adapter.Description);
    D3DPRESENT_PARAMETERS pp={};pp.Windowed=TRUE;pp.SwapEffect=D3DSWAPEFFECT_DISCARD;pp.hDeviceWindow=window;
    pp.BackBufferWidth=640;pp.BackBufferHeight=480;pp.BackBufferFormat=D3DFMT_X8R8G8B8;
    pp.EnableAutoDepthStencil=TRUE;pp.AutoDepthStencilFormat=D3DFMT_D16;pp.Flags=D3DPRESENTFLAG_LOCKABLE_BACKBUFFER;
    graphicsResult.flags=D3DCREATE_SOFTWARE_VERTEXPROCESSING;graphicsResult.format=pp.BackBufferFormat;
    LPDIRECT3DDEVICE8 device=NULL;
    HRESULT created=d3d->CreateDevice(D3DADAPTER_DEFAULT,D3DDEVTYPE_HAL,window,graphicsResult.flags,&pp,&device);
    graphicsResult.fpAfterDevice=graphicsFP();
    if (!graphicsHR(created)) { graphicsReport("device-failed");d3d->Release();DestroyWindow(window);return 86; }
    graphicsReport("device-created");
    if (!graphicsHR(R3InitDevice(device,640,480))) return 87;
    SetDefaultFlags();
    _R3ENGINE_STATE* state=GetR3State();
    D3DXVECTOR3 eye(0,0,levelMode?-500.0f:-150.0f),target(0,levelMode?-300.0f:0.0f,0),up(0,1,0);
    D3DXMatrixLookAtLH(&state->mMatView,&eye,&target,&up);
    D3DXMatrixInverse(&state->mInvMatView,NULL,&state->mMatView);
    D3DXMatrixPerspectiveFovLH(&state->mMatProj,0.7f,640.0f/480.0f,1.0f,levelMode?6000.0f:1000.0f);
    device->SetTransform(D3DTS_VIEW,&state->mMatView);device->SetTransform(D3DTS_PROJECTION,&state->mMatProj);
    graphicsHR(device->Clear(0,NULL,D3DCLEAR_TARGET|D3DCLEAR_ZBUFFER,0xff102030,1.0f,0));
    RF455_RpkGroup group;CEntity entity;CParticle particle;
    CLevel* level=NULL;
#if defined(RF_CLIENT_455_MAP_TIME)
    CLand* land=NULL;CLand* previousLand=g_pLand;CLevel* previousLevel=g_pLevel;
#endif
    if (levelMode) {
        char input[256];length=GetEnvironmentVariableA("RF_LAB_HELPER_INPUT",input,sizeof(input));
        if (!length || length>=sizeof(input)) return 88;
#if defined(RF_CLIENT_455_MAP_TIME)
        land=new CLand;graphicsCheck(land->Create()!=FALSE);level=land->GetLevel();
        graphicsReport("loading-level");land->LoadLevel(input);
#else
        level=new CLevel;
        graphicsReport("loading-level");level->LoadLevel(input);
#endif
        graphicsResult.fpAfterLoad=graphicsFP();
        graphicsResult.levelLoaded=level->IsLoadedBsp();graphicsCheck(graphicsResult.levelLoaded!=FALSE);
        if (graphicsResult.levelLoaded) {
#if defined(RF_CLIENT_455_MAP_TIME)
            graphicsMapTime(land);
#endif
            graphicsResult.levelLeaves=level->mBsp->mLeafNum;graphicsResult.levelNodes=level->mBsp->mNodeNum;
            graphicsResult.levelHelpers=level->mDummy.GetTotalNum();
            graphicsLevelWeather(level);
            Vector3f camera={eye.x,eye.y,eye.z},point={target.x,target.y,target.z};graphicsLevelCamera(level,camera,point);
            R3SetTime(1.0f/60.0f);R3SetLoopTime(1.0f/60.0f);
            graphicsReport("updating-level");level->FrameMove();
        }
    }
    if (entityMode || particleMode) {
        char input[256];length=GetEnvironmentVariableA("RF_LAB_HELPER_INPUT",input,sizeof(input));
        if (!length || length>=sizeof(input)) return 88;
        group.LoadDirectory(state->EntityPath);RF455_SetResourceGroup(&group);
        graphicsReport(particleMode?"loading-particle":"loading-entity");
        CEntity* loaded=NULL;
        if (entityMode) { graphicsResult.entityLoaded=entity.LoadEntity(input);loaded=graphicsResult.entityLoaded?&entity:NULL; }
        else {
            srand(1);graphicsResult.particleLoaded=particle.LoadParticleSPT(input);
            loaded=graphicsResult.particleLoaded?particle.mEntity:NULL;
            if (graphicsResult.particleLoaded) {
                // CParticle leaves this transform to its owner. Weather update
                // assigns identity before draw; standalone origin uses the same.
                MatrixIdentity(particle.mRotMat);
                particle.InitParticle();particle.SetParticleState(_PARTICLE_STATE_START);
                graphicsResult.particleCount=(unsigned)particle.mNum;
                graphicsReport("simulating-particle");
                for (unsigned i=0;i<240;++i) { R3SetTime((float)i/60.0f);R3SetLoopTime(1.0f/60.0f);particle.RealLoop();++graphicsResult.simulationFrames; }
                for (int i=0;i<particle.mNum;++i) if (particle.mElement[i].mIsLive) ++graphicsResult.particleLive;
                graphicsCheck(graphicsResult.particleLive>0);
            }
        }
        graphicsResult.fpAfterLoad=graphicsFP();graphicsCheck(loaded!=NULL);
        if (loaded) {
            graphicsResult.entityGroups=loaded->mMatGroupNum;graphicsResult.entityTextures=loaded->mTexNum;
            LPDIRECT3DTEXTURE8 texture=R3GetSurface(loaded->mStartTexID);
            if (graphicsCheck(texture!=NULL)) {
                D3DSURFACE_DESC description={};texture->GetLevelDesc(0,&description);
                graphicsResult.textureWidth=description.Width;graphicsResult.textureHeight=description.Height;
                graphicsResult.textureFormat=description.Format;graphicsResult.textureLevels=texture->GetLevelCount();
            }
        }
    }
    graphicsReport("drawing");
    graphicsResult.fpBeforeDraw=graphicsFP();
    if (graphicsHR(device->BeginScene())) {
        if (entityMode && graphicsResult.entityLoaded) {
            float world[4][4];MatrixIdentity(world);
            graphicsResult.entityDrawn=entity.DrawEntity(world,0xffffffff,0);
            graphicsCheck(graphicsResult.entityDrawn!=FALSE);
        }
        if (particleMode && graphicsResult.particleLoaded) {
            float world[4][4];MatrixIdentity(world);
            DrawCParticle(&particle,particle.mEntity,world);
        }
        if (levelMode && graphicsResult.levelLoaded) {
            graphicsReport("rendering-level");level->DrawSkyBoxRender();level->DrawMapRender();
            level->DrawMapEntitiesRender();Vector3f camera={eye.x,eye.y,eye.z};level->DrawMapAlphaRender(camera);
            graphicsResult.visibleGroups=level->mBsp->mNowRenderMatGroupNum;
        }
        graphicsHR(device->EndScene());
    }
    graphicsResult.fpAfterDraw=graphicsFP();
    graphicsCheck(graphicsCapture(device));
    if (entityMode || particleMode || levelMode) graphicsCheck(graphicsResult.changedPixels>0);
    graphicsReport("captured");
    if (entityMode && graphicsResult.entityLoaded) entity.ReleaseEntity();
    if (particleMode && graphicsResult.particleLoaded) { particle.ReleaseParticle();particle.ReleaseEntity(); }
#if defined(RF_CLIENT_455_MAP_TIME)
    if (land) { delete land;g_pLand=previousLand;g_pLevel=previousLevel; }
    else if (level) { level->ReleaseLevel();delete level; }
#else
    if (level) { level->ReleaseLevel();delete level; }
#endif
    RF455_SetResourceGroup(NULL);group.Release();
    R3ReleaseAllTextures();R3ReleasePreTextures();
    R3DeleteDevice();graphicsResult.deviceRefs=device->Release();graphicsResult.d3dRefs=d3d->Release();
    graphicsCheck(graphicsResult.deviceRefs==0 && graphicsResult.d3dRefs==0);DestroyWindow(window);
    ReleaseR3Engine();graphicsResult.allocationAfter=GetDmallocSize();
    graphicsCheck(graphicsResult.allocationBefore==graphicsResult.allocationAfter);
    for (unsigned i=0;i<4;++i) graphicsCheck(GetModuleHandleA(delayed[i])==NULL);
    graphicsReport("complete");SetErrorMessageProc(NULL);SetWarningMessageProc(NULL);
    return graphicsResult.failures?89:0;
}
