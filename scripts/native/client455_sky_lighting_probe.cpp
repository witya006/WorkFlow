#define RF455_SKY_MATERIAL_NO_MAIN
#include "client455_sky_material_probe.cpp"
#include "client455_sky_atmosphere.h"
#include "client455_sky_lighting.h"
#include "client455_weather_format.h"
#include "r3material.h"
void LoadR3X(char*);

using State128=HRESULT(WINAPI*)(IDirect3DDevice9*,D3DRENDERSTATETYPE,DWORD);
static void** table128;static State128 stateMethod128;static std::vector<DWORD> factors128;
static void patchState128(void* value){DWORD previous,discard;check(VirtualProtect(table128+57,sizeof(void*),PAGE_READWRITE,&previous)!=0,"lab state slot writable");table128[57]=value;check(VirtualProtect(table128+57,sizeof(void*),previous,&discard)!=0,"lab state slot protected");}
static HRESULT WINAPI observeState128(IDirect3DDevice9* d,D3DRENDERSTATETYPE state,DWORD value){patchState128(reinterpret_cast<void*>(stateMethod128));if(state==D3DRS_TEXTUREFACTOR)factors128.push_back(value);const auto result=stateMethod128(d,state,value);patchState128(reinterpret_cast<void*>(observeState128));return result;}
struct StateHook128{StateHook128(IDirect3DDevice9* d){table128=*reinterpret_cast<void***>(d);stateMethod128=reinterpret_cast<State128>(table128[57]);factors128.clear();patchState128(reinterpret_cast<void*>(observeState128));}~StateHook128(){patchState128(reinterpret_cast<void*>(stateMethod128));}};

static void floats128(FILE* out,const float* values,unsigned count){
    std::fputc('[',out);for(unsigned i=0;i<count;++i)std::fprintf(out,"%s%u",i?",":"",bits125(values[i]));std::fputc(']',out);
}
static void endpoint128(FILE* out,const RF455SkyFogEndpoint& value){
    std::fprintf(out,"[%u,%u,%u]",bits125(value.start),bits125(value.end),value.color);
}
static void endpoints128(FILE* out){
    std::fprintf(out,",\"day_fog\":");endpoint128(out,RF455_GetSkyDayFog());
    std::fprintf(out,",\"night_fog\":");endpoint128(out,RF455_GetSkyNightFog());
}
static void state128(FILE* out){
    auto* s=GetR3State();std::fprintf(out,",\"fog\":[%u,%u,%u],\"main\":[%u,%u,%u],\"far\":%u,\"flags\":%u",bits125(s->mFogStart),bits125(s->mFogEnd),s->mFogColor,bits125(s->mMainFogStart),bits125(s->mMainFogEnd),s->mMainFogColor,bits125(s->mFar),s->mEnvironmentSceneFlags);endpoints128(out);
}
static void ownText128(const char* path,const char* text){FILE* file=std::fopen(path,"wb");check(file!=nullptr,"own parser fixture");std::fputs(text,file);std::fclose(file);}
static void parser128(FILE* out){
    phase("text128");CreateDirectoryA("lighting-text",nullptr);ownText128("lighting-text/dummy.mst","");
    const char* cases[]={
        "*FOG_COLOR 18 52 86\n",
        "*FOG_START 12.5\n*FOG_END 1000.5\n*FOG_COLOR 18 52 86\n*FOG_START2 110\n*FOG_END2 6000.25\n*FOG_COLOR2 186 152 118\n*use_fog_fog2\n",
        "*fog_start 900\n*fog_end 10000\n*fog_color 1 2 3\n",
        "*FOG_COLOR2 3 5 7\n*FOG_START2 2.5\n*FOG_END2 200\n*FOG_COLOR 11 13 17\n*FOG_START 4.5\n*FOG_END 400\n"};
    auto* s=GetR3State();for(unsigned i=0;i<4;++i){
        RF455_ResetSkyFogEndpoints();s->mFogStart=s->mFogEnd=s->mMainFogStart=s->mMainFogEnd=0;s->mMainFogColor=0;s->mFar=6000;s->mEnvironmentSceneFlags=0;
        FILE* f=std::fopen("lighting-text/MainMaterial.mst","wb");check(f!=nullptr,"actual text path");std::fputs("*MATERIAL_NUM 1\n{\ndummy 0\n}\n",f);std::fputs(cases[i],f);std::fclose(f);
        char path[]="lighting-text/";check(LoadMainMaterial(path)!=nullptr,"actual public material script loader");
        std::fprintf(out,"{\"kind\":\"text\",\"id\":%u,\"enabled\":%s",i,s->mIsFog?"true":"false");state128(out);std::fprintf(out,"}\n");
    }
    ReleaseMainMaterial();RF455_ResetSkyFogEndpoints();phase("r3x128");
    unsigned index=0;for(DWORD flags:{0u,4u,8u,0u,12u}){
        RF455_ExtMaterial mat={};mat.mFlag=flags;mat.mSceneFlags=2;
        mat.mFogStart=12.5f+index;mat.mFogEnd=1000.5f+index;mat.mFogColor=0xff123456+index;
        mat.mFogStart2=110.f+index;mat.mFogEnd2=6000.25f+index;mat.mFogColor2=0xffba9876+index;
        FILE* f=std::fopen("lighting-input.r3x","wb");check(f!=nullptr,"own R3X");const float version=1.1f;std::fwrite(&version,4,1,f);std::fwrite(&mat,sizeof(mat),1,f);std::fclose(f);
        char path[]="lighting-input.r3x";LoadR3X(path);std::fprintf(out,"{\"kind\":\"r3x\",\"id\":%u,\"input_flags\":%u",index++,flags);state128(out);std::fprintf(out,"}\n");
    }
    const auto day=RF455_GetSkyDayFog(),night=RF455_GetSkyNightFog();const DWORD oldFlags=s->mEnvironmentSceneFlags;const float badVersion=.5f;
    FILE* f=std::fopen("lighting-invalid.r3x","wb");check(f!=nullptr,"bad version fixture");std::fwrite(&badVersion,4,1,f);std::fclose(f);char bad[]="lighting-invalid.r3x";LoadR3X(bad);
    check(!std::memcmp(&day,&RF455_GetSkyDayFog(),sizeof(day))&&!std::memcmp(&night,&RF455_GetSkyNightFog(),sizeof(night))&&s->mEnvironmentSceneFlags==oldFlags,"invalid version preserves endpoints");
}

static int run128(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);InitR3Engine();SetWarningMessageProc(warningMessage);SetErrorMessageProc(errorMessage);
    auto* s=GetR3State();s->mScreenXsize=640;s->mScreenYsize=480;s->mbFullScreen=FALSE;ForceFullScreen();std::strcpy(s->MapPath,".\\Map\\");std::strcpy(s->EntityPath,".\\Map\\Entity\\");
    check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"actual device128");auto* d=GetD3dDevice();
    FILE* out=std::fopen("lighting.jsonl","wb");check(out!=nullptr,"trace128");std::setvbuf(out,nullptr,_IONBF,0);parser128(out);check(warnings==1,"one expected invalid-version warning");
    RF455_SetSkyDayEnabled(1);const auto originalCW=cw125();unsigned mieCases=0;
    for(unsigned pc:{0u,2u,3u}){const unsigned short cw=(originalCW&~0xf00u)|(pc<<8);setCW125(cw);
        for(float boundary:{.7708333333333334f,.7916666865348816f,.8333333134651184f})for(float day:{std::nextafter(boundary,0.f),boundary,std::nextafter(boundary,1.f)}){
            RF455_DayFraction=day;RF455_UpdateSunValues();float params[17];RF455_GetSkyScatterParameters(params);check(cw125()==cw,"Mie control word");
            std::fprintf(out,"{\"kind\":\"mie\",\"cw\":%u,\"day\":%u,\"value\":%u}\n",cw,bits125(day),bits125(params[4]));++mieCases;
        }
    }setCW125(originalCW);const auto provider=RF455_ClockTickSource;RF455_ClockTickSource=now125;tick125=0;
    {
        CCamera camera;g_pCamera=&camera;CLand land;check(land.Create()!=0,"actual land owner");char map[]=".\\Map\\neutralB\\neutralB.bsp";check(land.LoadLevel(map)!=0,"actual neutralB load");auto& level=*land.GetLevel();check(level.IsLoadedBsp()&&level.mSkyBox->IsLoaded455(),"actual neutralB map/sky2");
        std::fprintf(out,"{\"kind\":\"actual_map\"");state128(out);std::fprintf(out,"}\n");
        s->mFov=.6f;s->mAsfectRatio=4.f/3;s->mNear=17;s->mFar=6000;
        const unsigned hours[]={0,12,18,12,3},minutes[]={0,0,45,0,0};const DWORD flags[]={0,0,0,2,0};
        const char* names[]={"lighting-midnight.bgra","lighting-noon.bgra","lighting-dusk.bgra","lighting-fog2.bgra","lighting-disabled.bgra"};
        unsigned submissions=0;
        for(unsigned i=0;i<5;++i){
            RF455_SetSkyDayEnabled(i==4?0:1);RF455_SetDayTime(hours[i],minutes[i],0);R3SetTime(.5f);R3SetLoopTime(1.f/30);
            D3DXVECTOR3 eye(0,100,0),at(0,100,100),up(0,1,0);D3DXMATRIX view;D3DXMatrixLookAtLH(&view,&eye,&at,&up);float pos[]={eye.x,eye.y,eye.z};level.SetCameraPos(pos);level.SetViewMatrix(&view);
            D3DXMatrixInverse(&s->mInvMatView,nullptr,&s->mMatView);D3DXMatrixPerspectiveFovLH(&s->mMatProj,s->mFov,s->mAsfectRatio,s->mNear,s->mFar);D3DXMatrixMultiply(&s->mMatViewProj,&s->mMatView,&s->mMatProj);
            s->mEnvironmentSceneFlags=flags[i];RF455_SetSkyFogExposureColor(i==2?0xabcdef80:0);
            const auto oldSun=RF455_GetSunValues();const DWORD oldFog=s->mFogColor,oldTint=RF455_GetSkyTintColor(),oldDirect=RF455_GetSkyDirectColor();float oldPosition[3];RF455_GetSkySunPosition(oldPosition);const float previousFar=s->mFar;
            level.FrameMove();float light[4],params[17],position[3];RF455_GetSkySunColor(light);RF455_GetSkyScatterParameters(params);RF455_GetSkySunPosition(position);
            if(i==4)check(oldFog==s->mFogColor&&oldTint==RF455_GetSkyTintColor()&&oldDirect==RF455_GetSkyDirectColor()&&!std::memcmp(position,oldPosition,12),"disabled frame preserves lighting");
            std::fprintf(out,"{\"kind\":\"frame\",\"id\":%u,\"enabled\":%s,\"cw\":%u,\"day\":%u,\"night\":%u,\"old_fog\":%u,\"tint\":%u,\"direct\":%u,\"alpha\":%u,\"intensity\":%u,\"exposure\":%u,\"previous_far\":%u,\"old_sun\":",i,i==4?"false":"true",cw125(),bits125(RF455_GetDayFraction()),bits125(RF455_GetSkyNightWeight()),oldFog,RF455_GetSkyTintColor(),RF455_GetSkyDirectColor(),bits125(RF455_GetSunValues().alpha),bits125(RF455_GetSunValues().intensity),bits125(RF455_GetSkyFogExposure()),bits125(previousFar));floats128(out,&oldSun.theta,6);
            std::fprintf(out,",\"sun_color\":");floats128(out,light,4);std::fprintf(out,",\"params\":");floats128(out,params,17);std::fprintf(out,",\"position\":");floats128(out,position,3);state128(out);std::fprintf(out,",\"sample_count\":%u,\"divisor\":%u}\n",RF455_GetSkyFogSampleCount(),RF455_GetSkyFogSampleDivisor());
            if(i<3)for(int a=0;a<=16;++a)for(int b=0;b<=16;++b){
                const float x=float(a-8),z=float(b-8);const float radius=float(std::sqrt(double(x*x+z*z)));const float height=4-(radius>4?4:radius);float p[]={x*1290,float(double(height)*5160*.25),-z*1290};
                std::fprintf(out,"{\"kind\":\"sample\",\"frame\":%u,\"index\":%u,\"xyz\":",i,a*17+b);floats128(out,p,3);std::fprintf(out,",\"color\":%u}\n",RF455_SampleSkyColor(p));
            }
            check(SUCCEEDED(d->Clear(0,nullptr,D3DCLEAR_TARGET|D3DCLEAR_ZBUFFER,0xff102030,1,0))&&SUCCEEDED(d->BeginScene()),"real frame begin128");level.DrawSkyBoxRender();check(SUCCEEDED(d->EndScene()),"real frame end128");capture(names[i]);
        }
        // Actual map owner must bind the restored tint before its BSP draws.
        const unsigned mixHours[]={0,6,19},mixMinutes[]={0,0,30};
        for(unsigned i=0;i<3;++i){
            RF455_SetSkyDayEnabled(1);s->mEnvironmentSceneFlags=2;
            RF455_SetDayTime(mixHours[i],mixMinutes[i],0);level.FrameMove();
            float params[17];RF455_GetSkyScatterParameters(params);
            std::fprintf(out,"{\"kind\":\"fog_frame\",\"id\":%u,\"cw\":%u,\"day\":%u,\"night\":%u,\"mie\":%u",i,cw125(),bits125(RF455_GetDayFraction()),bits125(RF455_GetSkyNightWeight()),bits125(params[4]));state128(out);std::fprintf(out,"}\n");
        }
        RF455_SetSkyDayEnabled(1);s->mIsFog=FALSE;CAniCamera mapCamera;char cameraPath[]=".\\Map\\neutralB\\neutralB.cam";mapCamera.LoadAniCamera(cameraPath);check(mapCamera.IsLoadedAniCamera(),"actual neutralB camera");mapCamera.SetPrePlayCamera(0,_CAM_PLAY_FULL_FRAME,_CAM_PLAY_FULL_FRAME,_CAM_FLAG_FINAL_STOP);float cameraMatrix[4][4];check(mapCamera.PlayAniCamera(cameraMatrix,1,TRUE),"actual map camera frame");D3DXMATRIX inverse;D3DXMatrixInverse(&inverse,nullptr,reinterpret_cast<D3DXMATRIX*>(cameraMatrix));float pos[]={inverse._41,inverse._42,inverse._43};level.SetCameraPos(pos);level.SetViewMatrix(reinterpret_cast<D3DXMATRIX*>(cameraMatrix));level.FrameMove();
        check(SUCCEEDED(d->BeginScene()),"map begin128");{Hook125 hook(d);StateHook128 stateHook(d);samples125.clear();level.DrawMapRender();submissions=unsigned(samples125.size());check(!factors128.empty()&&factors128.front()==RF455_GetSkyTintColor(),"ordinary map first texture-factor bind");}check(SUCCEEDED(d->EndScene()),"map end128");check(submissions>0,"actual map indexed submissions");
        std::fprintf(out,"{\"kind\":\"map_draw\",\"submissions\":%u,\"tint\":%u,\"first_texture_factor\":%u,\"factor_writes\":%u}\n",submissions,RF455_GetSkyTintColor(),factors128.front(),unsigned(factors128.size()));land.Destroy();g_pCamera=nullptr;
    }
    RF455_ClockTickSource=provider;std::fclose(out);g_MainApp.ReleaseR3D3D();ReleaseR3Engine();FILE* result=std::fopen("result.json","wb");check(result!=nullptr,"result128");std::fprintf(result,"{\"status\":\"PASS\",\"text_cases\":4,\"R3X_cases\":6,\"mie_cases\":%u,\"frames\":5,\"fog_frames\":3,\"software_samples\":867,\"warnings\":%u,\"full_lighting\":false}\n",mieCases,warnings);std::fclose(result);return 0;
}
int main(){try{return run128();}catch(const std::exception& e){std::fprintf(stderr,"failure128:%s\n",e.what());return 1;}}
