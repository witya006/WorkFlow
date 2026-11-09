#define RF455_SKY_MATERIAL_NO_MAIN
#include "client455_sky_material_probe.cpp"
#include "client455_weather_parameters.h"
#include "client455_sky_atmosphere.h"
#include "client455_sky_lighting.h"
#include <cstddef>

static_assert(offsetof(D3DCAPS9,TextureOpCaps)==144,"455 caps input offset");
static_assert(D3DTEXOPCAPS_BUMPENVMAP==(1u<<21),"4551157CB8 capability");

static void text129(const char* text){
    FILE* f=std::fopen("weather-text/MainMaterial.mst","wb");check(f!=nullptr,"own material script");
    std::fputs("*MATERIAL_NUM 1\n{\ndummy 0\n}\n",f);std::fputs(text,f);std::fclose(f);
    char path[]="weather-text/";check(LoadMainMaterial(path)!=nullptr,"actual public material loader");
}
__declspec(noinline) static void send129(CLevel* owner,DWORD value){owner->SetWeatherColor455(value);}
struct Override129: CLevel{
    unsigned calls=0;
    void SetWeatherColor455(DWORD value)override{++calls;CLevel::SetWeatherColor455(value);}
};
static void floats129(FILE* out,const float* p,unsigned n){
    std::fputc('[',out);for(unsigned i=0;i<n;++i)std::fprintf(out,"%s%u",i?",":"",bits125(p[i]));std::fputc(']',out);
}
static unsigned scripts129(FILE* out){
    CreateDirectoryA("weather-text",nullptr);FILE* empty=std::fopen("weather-text/dummy.mst","wb");check(empty!=nullptr,"own empty material");std::fclose(empty);
    const char* tags[]={"*WeAtHeR","*HaZe","*SpEcIaL_WeAtHeR"};
    const char* values[]={"0.5","1.25","-0.1","0.00392156862745098","0.5019607843137255","2","not_a_number","-1","1.1","0.9999999999999999"};
    const auto saved=cw125();unsigned count=0;
    for(unsigned pc:{0u,2u,3u}){
        const unsigned short cw=(saved&~0xf00u)|(pc<<8);setCW125(cw);
        for(unsigned tag=0;tag<3;++tag)for(const char* value:values){
            RF455_MaterialWeather=0xa5332211u;char script[256];std::sprintf(script,"%s %s\n",tags[tag],value);text129(script);
            check(cw125()==cw,"weather conversion restores CW");
            std::fprintf(out,"{\"kind\":\"packed\",\"tag\":%u,\"value\":\"%s\",\"seed\":%u,\"cw\":%u,\"packed\":%u}\n",tag,value,0xa5332211u,cw,RF455_GetMaterialWeather());++count;
        }
    }
    setCW125(saved);auto* s=GetR3State();s->mEnvironmentSceneFlags=0;RF455_ResetSkyFogEndpoints();
    text129("*nO_sUn\n*NO_SKY_COLOR\n*UsE_FoG_fOg2\n*environment2 MiXeD.r3e\n*fog_start 900\n*FoG_EnD 10000\n*fog_color 1 2 3\n");
    check(s->mEnvironmentSceneFlags==7&&!std::strcmp(s->mEnvEntityNames[1],"MiXeD.r3e"),"case-folded tags preserve copied environment filename");
    const auto& day=RF455_GetSkyDayFog();
    std::fprintf(out,"{\"kind\":\"casefold\",\"flags\":%u,\"environment\":\"%s\",\"day_fog\":[%u,%u,%u],\"far\":%u}\n",s->mEnvironmentSceneFlags,s->mEnvEntityNames[1],bits125(day.start),bits125(day.end),day.color,bits125(s->mFar));
    RF455_MaterialWeather=0;text129("*WEATHER 0.5\n*HAZE 0.25\n*SPECIAL_WEATHER 0.75\n");
    check(RF455_GetMaterialWeather()==0x00bf3f7fu,"canonical script packed weather");ReleaseMainMaterial();return count;
}
static int run129(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);InitR3Engine();SetWarningMessageProc(warningMessage);SetErrorMessageProc(errorMessage);
    check(RF455_GetMaterialWeather()==0,"packed weather BSS default");
    auto* s=GetR3State();s->mScreenXsize=640;s->mScreenYsize=480;s->mbFullScreen=FALSE;ForceFullScreen();std::strcpy(s->MapPath,".\\Map\\");std::strcpy(s->EntityPath,".\\Map\\Entity\\");
    check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"actual device129");auto* d=GetD3dDevice();
    FILE* out=std::fopen("weather-owner.jsonl","wb");check(out!=nullptr,"weather trace");std::setvbuf(out,nullptr,_IONBF,0);const unsigned cases=scripts129(out);
    const auto provider=RF455_ClockTickSource;RF455_ClockTickSource=now125;tick125=0;
    {
        //CLevel destruction releases global map resources. Keep the second
        //owner alive until the loaded land has finished,as in the real owner chain.
        Override129 other;CCamera camera;g_pCamera=&camera;CLand land;check(land.Create()!=0,"actual land129");char path[]=".\\Map\\neutralB\\neutralB.bsp";check(land.LoadLevel(path)!=0,"actual ordinary map load129");auto& level=*land.GetLevel();
        check(level.GetWeatherColor455()==0x00bf3f7fu&&RF455_GetMaterialWeather()==0x00bf3f7fu,"map load applies retained material weather through level owner");
        std::fprintf(out,"{\"kind\":\"map_owner\",\"packed\":%u,\"owned\":%u,\"exposure\":%u,\"cw\":%u}\n",RF455_GetMaterialWeather(),level.GetWeatherColor455(),bits125(RF455_GetSkyFogExposure()),cw125());
        send129(&other,0x123456c0u);check(other.calls==1&&other.GetWeatherColor455()==0x123456c0u&&level.GetWeatherColor455()==0x00bf3f7fu,"virtual owner dispatch and separate retained DWORDs");
        std::fprintf(out,"{\"kind\":\"other_owner\",\"calls\":%u,\"owned\":%u,\"first\":%u,\"exposure\":%u,\"cw\":%u}\n",other.calls,other.GetWeatherColor455(),level.GetWeatherColor455(),bits125(RF455_GetSkyFogExposure()),cw125());
        send129(&level,level.GetWeatherColor455());
        CAniCamera mapCamera;char cameraPath[]=".\\Map\\neutralB\\neutralB.cam";mapCamera.LoadAniCamera(cameraPath);check(mapCamera.IsLoadedAniCamera(),"actual camera129");mapCamera.SetPrePlayCamera(0,_CAM_PLAY_FULL_FRAME,_CAM_PLAY_FULL_FRAME,_CAM_FLAG_FINAL_STOP);
        float view[4][4];check(mapCamera.PlayAniCamera(view,1,TRUE),"actual camera frame129");D3DXMATRIX inverse;D3DXMatrixInverse(&inverse,nullptr,reinterpret_cast<D3DXMATRIX*>(view));float position[]={inverse._41,inverse._42,inverse._43};
        s->mFov=.6f;s->mAsfectRatio=4.f/3;s->mNear=17;s->mFar=6000;s->mEnvironmentSceneFlags=0;
        const unsigned hours[]={0,6,12,18,20};const DWORD colors[]={0x01020300u,0xaabbcc40u,0x11223380u,0x556677c0u,0x8899aaffu};
        const char* names[]={"weather-midnight.bgra","weather-dawn.bgra","weather-noon.bgra","weather-dusk.bgra","weather-night.bgra"};
        for(unsigned i=0;i<5;++i){
            send129(&level,colors[i]);RF455_SetSkyDayEnabled(1);RF455_SetDayTime(hours[i],0,0);R3SetTime(.5f);R3SetLoopTime(1.f/30);
            level.SetCameraPos(position);level.SetViewMatrix(reinterpret_cast<D3DXMATRIX*>(view));level.FrameMove();
            check(level.GetWeatherColor455()==colors[i]&&RF455_GetMaterialWeather()==0x00bf3f7fu,"frame retains owner without changing script producer");
            check(SUCCEEDED(d->Clear(0,nullptr,D3DCLEAR_TARGET|D3DCLEAR_ZBUFFER,0xff102030,1,0))&&SUCCEEDED(d->BeginScene()),"weather frame begin");level.DrawSkyBoxRender();
            unsigned draws=0;{Hook125 hook(d);samples125.clear();level.DrawMapRender();draws=unsigned(samples125.size());}check(SUCCEEDED(d->EndScene())&&draws>0,"ordinary BSP weather submissions");capture(names[i]);
            float light[4],params[17];RF455_GetSkySunColor(light);RF455_GetSkyScatterParameters(params);
            std::fprintf(out,"{\"kind\":\"frame\",\"id\":%u,\"cw\":%u,\"day\":%u,\"owned\":%u,\"exposure\":%u,\"sample_count\":%u,\"divisor\":%u,\"fog\":%u,\"intensity\":%u,\"draws\":%u,\"sun_color\":",i,cw125(),bits125(RF455_GetDayFraction()),level.GetWeatherColor455(),bits125(RF455_GetSkyFogExposure()),RF455_GetSkyFogSampleCount(),RF455_GetSkyFogSampleDivisor(),s->mFogColor,bits125(RF455_GetSunValues().intensity),draws);floats129(out,light,4);std::fprintf(out,",\"params\":");floats129(out,params,17);std::fprintf(out,"}\n");
        }
        land.Destroy();g_pCamera=nullptr;
    }
    RF455_ClockTickSource=provider;std::fclose(out);g_MainApp.ReleaseR3D3D();ReleaseR3Engine();FILE* result=std::fopen("result.json","wb");check(result!=nullptr,"result129");
    std::fprintf(result,"{\"status\":\"PASS\",\"packed_cases\":%u,\"frames\":5,\"warnings\":%u,\"ordinary_map_weather\":true,\"full_lighting\":false}\n",cases,warnings);std::fclose(result);return 0;
}
int main(){try{return run129();}catch(const std::exception& e){std::fprintf(stderr,"weather129:%s\n",e.what());return 1;}}
