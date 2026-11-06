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
#include "client455_rvp_runtime.h"
#include "client455_rvp_actor.h"
#include "client455_movie_state.h"
#include <client455_normal_renderer_math.h>
#include "RTMovie.h"
#include "r3enginekernel.h"
#include "jmalloc.h"
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <set>
#include <stdexcept>
extern CMainApp g_MainApp;
static unsigned warnings=0;
static void check(bool value,const char* why){if(!value)throw std::runtime_error(why);}
static void phase(const char* text){std::fprintf(stderr,"phase:%s\n",text);std::fflush(stderr);}
static void errorMessage(char* text){std::fprintf(stderr,"engine:%s\n",text);std::fflush(stderr);std::exit(2);}
static void warningMessage(char* text){++warnings;std::fprintf(stderr,"warning:%s\n",text);std::fflush(stderr);}
static unsigned byteHash(const void* bytes,std::size_t length){unsigned value=2166136261u;const auto* at=static_cast<const unsigned char*>(bytes);while(length--)value=(value^*at++)*16777619u;return value;}
static unsigned paletteHash(const RF455RvpActorRuntime& actor){unsigned out=0;for(const auto& part:actor.palette)out^=byteHash(part.bytes.data(),part.count?part.count*64:64);return out;}
static unsigned capture(const char* filename){
    auto* device=GetD3dDevice();IDirect3DSurface9 *surface=nullptr,*copy=nullptr;
    check(SUCCEEDED(device->GetRenderTarget(0,&surface)),"target");D3DSURFACE_DESC desc;surface->GetDesc(&desc);
    check(SUCCEEDED(device->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&copy,nullptr)),"readback surface");
    check(SUCCEEDED(device->GetRenderTargetData(surface,copy)),"readback");D3DLOCKED_RECT lock;
    check(SUCCEEDED(copy->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"readback lock");
    FILE* file=std::fopen(filename,"wb");check(file!=nullptr,"frame file");unsigned pixels=0;
    for(unsigned y=0;y<480;++y){const auto* row=reinterpret_cast<const DWORD*>(static_cast<const unsigned char*>(lock.pBits)+y*lock.Pitch);std::fwrite(row,4,640,file);for(unsigned x=0;x<640;++x)pixels+=(row[x]&0xffffff)!=0x102030;}
    std::fclose(file);copy->UnlockRect();copy->Release();surface->Release();return pixels;
}
static void begin(){auto* device=GetD3dDevice();check(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET|D3DCLEAR_ZBUFFER,0xff102030,1,0)),"clear");check(SUCCEEDED(device->BeginScene()),"begin");}
static void end(){check(SUCCEEDED(GetD3dDevice()->EndScene()),"end");}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    SetErrorMessageProc(errorMessage);SetWarningMessageProc(warningMessage);phase("init");InitR3Engine();phase("engine");
    auto* state=GetR3State();state->mScreenXsize=640;state->mScreenYsize=480;state->mbFullScreen=FALSE;ForceFullScreen();
    std::strcpy(state->MapPath,".\\Map\\");std::strcpy(state->EntityPath,".\\Map\\Entity\\");
    check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"device");R3SetViewPort(0,0,640,480);phase("device");
    unsigned poses=0,draws=0,unique=0,pixels=0,animatedPixels=0,distinctPoses=0,restored=0;int before=0,after=0;
    {
        ChInterface outer;outer.InitCharacter(GetD3dDevice());before=GetDmallocSize();
        CCamera camera;g_pCamera=&camera;std::unique_ptr<CLand> land(new CLand);check(land->Create()!=0,"land");
        R3SetTime(0);RTMoviePause(FALSE);phase("before-world");check(land->LoadLevel(".\\Map\\neutralAS1\\neutralAS1.bsp")!=0,"world");phase("world");
        auto* level=land->GetLevel();auto initial=RF455_RvpView();check(initial.movieLoaded&&initial.actors==12,"ordinary RVP actors");
        std::set<std::uintptr_t> models;auto& renderer=CRender::GetRender();
        check(renderer.native.meshes.end-renderer.native.meshes.begin==12,"bone registrations retain duplicates");
        check(renderer.native.effects.end-renderer.native.effects.begin==1,"owned BODY manager");
        auto* body=*renderer.native.effects.begin;check(body->end-body->begin==12,"mesh registrations retain duplicates");
        for(unsigned i=0;i<12;++i){const auto& actor=*RF455_RvpActorState(i);std::fprintf(stderr,"actor%u bone=%p mesh=%p parts=%u/%u frame=%u\n",i,actor.bone,actor.mesh,actor.bone?actor.bone->m_MaxObj:0,actor.mesh?actor.mesh->m_MaxObj:0,actor.bone?actor.bone->m_OMaxFrame:0);check(actor.bone&&actor.mesh&&actor.bone->m_Load&&actor.mesh->m_MaxObj,"actual BN/MSH");check(actor.animationSelections==2&&actor.bone->m_MaxObj==0&&actor.bone->m_OMaxFrame==0,"stock ships have real empty BN;do not invent animation targets");models.insert(reinterpret_cast<std::uintptr_t>(actor.mesh));}
        unique=static_cast<unsigned>(models.size());check(unique==4,"first-match shared models");
        check(renderer.native.textures.end>renderer.native.textures.begin,"real model textures");
        RF455_SetMovieState(3);RTMovieStartPlay(TRUE);
        FILE* trace=std::fopen("actor-trace.jsonl","wb");check(trace!=nullptr,"trace");
        for(unsigned tick=0;tick<48;++tick){R3SetTime(tick*.25f);R3SetLoopTime(.25f);level->FrameMove();
            begin();RTMovieRender();end();auto view=RF455_RvpView();
            std::fprintf(trace,"{\"tick\":%u,\"seconds\":%.9g,\"visible\":%u,\"poses\":%u,\"draws\":%u,\"frame0\":%.9g,\"palette0\":%u}\n",tick,view.seconds,view.visibleActors,view.poseUpdates,view.actorDraws,RF455_RvpActorState(0)->frame,paletteHash(*RF455_RvpActorState(0)));
            if(tick==4||tick==20||tick==40){char name[80];std::sprintf(name,"actors-only-%02u.bgra",tick);pixels+=capture(name);}
        }
        std::fclose(trace);auto played=RF455_RvpView();poses=played.poseUpdates;draws=played.actorDraws;
        check(poses&&draws&&pixels>100,"actual pose and actor-only GPU geometry");
        begin();level->DrawSkyBoxRender();level->DrawMapRender();level->DrawMapEntitiesRender();end();capture("actors-world.bgra");
        //Controlled two-actor track uses real models/CAM. Reset only one actor
        //to give two different saved poses in one frame,without stock ships.
        RTMovieRelease();R3SetTime(0);RTMovieCreate("actor-reset.rvp",level);check(IsLoadedRTMovie(),"reset fixture");RF455_SetMovieState(0);RTMovieStartPlay(TRUE);
        for(unsigned tick=0;tick<24;++tick){R3SetTime(tick*.25f);R3SetLoopTime(.25f);level->FrameMove();
            const auto& a=*RF455_RvpActorState(0);const auto& b=*RF455_RvpActorState(1);
            std::fprintf(stderr,"reset%u visible=%u/%u parts=%u/%u frame=%.9g/%.9g max=%u hash=%u/%u cursor=%zu\n",tick,a.visible,b.visible,a.bone->m_MaxObj,a.mesh->m_MaxObj,a.frame,b.frame,a.bone->m_OMaxFrame,paletteHash(a),paletteHash(b),RF455_RvpView().cursor);
            if(tick>14&&a.visible&&b.visible&&a.mesh==b.mesh&&a.frame!=b.frame&&paletteHash(a)!=paletteHash(b)){
                ++distinctPoses;RF455_RestoreRvpPalette(a);
                for(unsigned part=0;part<a.mesh->m_MaxObj;++part){const auto& saved=a.palette[part];check(!std::memcmp(a.mesh->m_pMesh[part].bytes+(saved.count?646:4830),saved.bytes.data(),saved.count?saved.count*64:64),"saved palette restored before shared draw");++restored;}
            }
            begin();RTMovieRender();end();if(tick==20)animatedPixels=capture("actors-reset.bgra");
        }
        check(distinctPoses&&restored&&animatedPixels,"distinct per-actor poses for shared mesh and actual isolated GPU pixels");
        const auto suspended=RF455_RvpView();RF455_AddMovieFlags(16);R3SetTime(30);RTMovieFrameMove();begin();RTMovieRender();end();check(RF455_RvpView().poseUpdates==suspended.poseUpdates&&RF455_RvpView().actorDraws==suspended.actorDraws,"flag16 actor gate");RF455_RemoveMovieFlags(16);
        check(land->Destroy()!=0,"destroy");g_pCamera=nullptr;after=GetDmallocSize();check(before==after,"Dmalloc balanced");check(&CRender::GetRender()==&outer,"outer renderer restored");
    }
    RF455_ReleaseNormalCharacterSharedResources();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();
    FILE* output=std::fopen("result.json","wb");check(output!=nullptr,"result");
    std::fprintf(output,"{\"status\":\"PASS\",\"actors\":12,\"unique_models\":%u,\"pose_updates\":%u,\"actor_draws\":%u,\"actor_pixels\":%u,\"isolated_animated_pixels\":%u,\"distinct_pose_ticks\":%u,\"restored_parts\":%u,\"warnings\":%u,\"memory_before\":%d,\"memory_after\":%d,\"full_particle_audio\":false,\"full_Tutorial\":false}\n",unique,poses,draws,pixels,animatedPixels,distinctPoses,restored,warnings,before,after);std::fclose(output);return 0;
}
int main(){try{return run();}catch(const std::exception& error){std::fprintf(stderr,"actor-probe:%s\n",error.what());return 1;}}
