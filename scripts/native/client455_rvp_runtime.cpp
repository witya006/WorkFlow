#include "Character.h"
#include "client455_rvp_runtime.h"
#include "client455_rvp.h"
#include "client455_rvp_actor.h"
#include "client455_rvp_effects.h"
#include "client455_rvp_audio.h"
#include "client455_loop_clock.h"
#include "r3sound.h"
#include "client455_camera.h"
#include "client455_movie_state.h"
#include "client455_fullscreen_effect.h"
#include "RTMovie.h"
#include "r3move.h"
#include "commonutil.h"
#include <algorithm>
#include <cstring>
#include <memory>
#include <string>
#include <stdexcept>
#include <utility>

namespace {
struct WaveBinding {unsigned id=0,dummy=0xffffffffu,actor=0xffffffffu;};
struct Movie {
    CLevel* level=nullptr;
    bool loaded=false,playing=false,paused=false;
    RF455RvpDocument data;
    std::unique_ptr<ChInterface> renderer;
    std::unique_ptr<AnimationManager> animations;
    RF455CharacterManager* body=nullptr;
    RF455RvpEffects* effects=nullptr;
    std::vector<RF455RvpActorRuntime> actors;
    std::vector<WaveBinding> waves;
    std::size_t cursor=0;
    unsigned cameras=0,fadeIns=0,fadeOuts=0;
    unsigned waveEvents=0,ambientStarts=0,ambientStops=0;
    float blur=0;
    std::string limitation;
    CAniCamera* camera(){return level?&level->mAutoAniCam:nullptr;}
};
Movie& movie(){static Movie value;return value;}
std::string lower(std::string text){for(auto& c:text)if(c>='A'&&c<='Z')c=char(c-'A'+'a');return text;}
bool ready(Movie& value){return value.camera()&&value.camera()->IsLoadedAniCamera();}
void extract(Movie& value,float frame) {
    while(value.cursor<value.data.tracks.size()) {
        const auto& track=value.data.tracks[value.cursor];
        if(track.frame==-1||frame<track.frame)break;
        //8D4EF5 consumes skipped camera-dependent events permanently.
        if(!(RF455_GetMovieState()&4)||std::uint8_t(track.kind)>=0x80) {
            switch(track.kind) {
            case RF455RvpKind::Camera:
                value.camera()->SetPrePlayCamera(track.value,static_cast<DWORD>(frame),0xffffffffu,1);++value.cameras;break;
            case RF455RvpKind::FadeIn:
                SetFadeIn(0,float(double(track.value)/30),1);++value.fadeIns;break;
            case RF455RvpKind::FadeOut:
                SetFadeOut(0,float(double(track.value)/30),1);++value.fadeOuts;break;
            case RF455RvpKind::Quake:R3EnvironmentQuake(track.first,track.second);break;
            case RF455RvpKind::Blur:value.blur=track.first;break;
            case RF455RvpKind::TimerRate:RF455_SetEngineLoopTimeScale(track.first);break;
            case RF455RvpKind::Wave: {
                const auto& wave=value.waves.at(value.cursor);float matrix[4][4];
                if(wave.actor==0xffffffffu)value.camera()->GetDummyMatrix(matrix,wave.dummy,value.camera()->GetNowFrame());
                else std::memcpy(matrix,value.actors.at(wave.actor).matrix,sizeof(matrix));
                RF455_PlayRvpWave(wave.id,matrix[3],track.first);++value.waveEvents;break;
            }
            case RF455RvpKind::Animation:
                RF455_RvpActorAnimation(value.actors.at(track.actor),value.data.actors.at(track.actor),*value.renderer,*value.animations,track.value);break;
            case RF455RvpKind::CharacterFadeIn: {
                auto& actor=value.actors.at(track.actor);const float seconds=float(double(track.value)/30);actor.fadeDuration=float(double(seconds)+double(.0001f));actor.fadeStart=R3GetTime();break;
            }
            case RF455RvpKind::CharacterFadeOut: {
                auto& actor=value.actors.at(track.actor);const float seconds=float(double(track.value)/30);actor.fadeDuration=float(-double(seconds)-double(.0001f));actor.fadeStart=R3GetTime();actor.fadeAmount=.0001f;break;
            }
            default:throw std::logic_error("RVP unbound operation reached execution");
            }
        }
        ++value.cursor;
    }
    if(value.blur!=0) {
        float interpolated;
        if(RF455_RvpInterpolate(value.data,value.cursor,RF455RvpKind::Blur,frame,interpolated))value.blur=interpolated;
    }
}
void prepare(Movie& value) {
    value.cursor=0;value.camera()->SetPrePlayCamera(0,0xffffffffu,0xffffffffu,0);
    extract(value,0);float matrix[4][4];value.camera()->PlayAniCamera(matrix,1,FALSE);
}
}

RF455RvpRuntimeView RF455_RvpView() {
    auto& value=movie();const bool camera=ready(value);
    unsigned visible=0,poses=0,draws=0;for(const auto& actor:value.actors){visible+=actor.visible;poses+=actor.poseUpdates;draws+=actor.draws;}
    return {value.loaded,camera,value.playing,value.paused,value.data.tracks.size(),value.cursor,
        value.cameras,value.fadeIns,value.fadeOuts,camera?value.camera()->GetNowFrame():0,
        value.blur,value.limitation.c_str(),value.actors.size(),visible,poses,draws,value.waveEvents,value.ambientStarts,value.ambientStops};
}
const RF455RvpActorRuntime* RF455_RvpActorState(std::size_t index){const auto& actors=movie().actors;return index<actors.size()?&actors[index]:nullptr;}
void RF455_RvpCreate(char* path,CLevel* level) {
    auto& value=movie();
    if(value.level&&value.level!=level)throw std::logic_error("RVP previous owner was not released");
    value.level=level;value.loaded=false;value.limitation.clear();
    value.cameras=value.fadeIns=value.fadeOuts=0;value.data={};value.cursor=0;
    value.waves.clear();value.waveEvents=value.ambientStarts=value.ambientStops=0;
    if(!path||!level)return;
    std::string cameraPath(path);const auto dot=cameraPath.find_last_of('.');
    if(dot!=std::string::npos)cameraPath.resize(dot);cameraPath+=".cam";
    value.camera()->LoadAniCamera(&cameraPath[0]);if(!ready(value))return;
    const auto* camera=RF455_GetCameraDocument(value.camera());RF455RvpDocument data;std::string error;
    if(!RF455_LoadRvp(path,data,&error,camera)){value.limitation=error;return;}
    // Mandatory unfinished providers are refused before loaded=true. There is
    // no fake animation/effect/audio callback in this production path.
    if(data.flags&8){value.limitation="RVP screen provider remains open";return;}
    for(const auto& actor:data.actors)if((actor.flags&(2|4|8))||!actor.swordTrace.empty()){
        value.limitation="RVP magic/collision/shadow/trace providers remain open";return;
    }
    RF455RvpDocument bound;bound.flags=data.flags;bound.totalFrame=data.totalFrame;bound.actors=std::move(data.actors);
    std::vector<WaveBinding> waves;
    for(auto track:data.tracks) {WaveBinding wave;
        if(track.kind==RF455RvpKind::Camera) {
            const auto name=track.reference.empty()?std::string():track.reference.substr(1);
            DWORD found=0xffffffffu;
            for(DWORD i=0;i<value.camera()->GetCameraNum();++i) {
                const char* actual=value.camera()->GetCameraName(i);
                if(actual&&lower(actual)==name){found=i;break;}
            }
            if(found==0xffffffffu){Warning("RVP camera not found",&track.reference[0]);continue;}
            track.value=found;
        } else if(track.kind==RF455RvpKind::Wave){
            const auto name=track.reference.empty()?std::string():track.reference.substr(1);
            wave.dummy=value.camera()->GetDummyID(const_cast<char*>(name.c_str()),FALSE);
            if(wave.dummy==0xffffffffu){
                //The original actor fallback intentionally excludes the last actor.
                for(unsigned i=0;i+1<bound.actors.size();++i)if(!(bound.actors[i].flags&2)&&bound.actors[i].name==track.reference){wave.actor=i;break;}
                if(wave.actor==0xffffffffu){Warning("RVP wave target not found",const_cast<char*>(track.reference.c_str()));continue;}
            }
        } else if(track.kind!=RF455RvpKind::TimerRate&&track.kind!=RF455RvpKind::FadeIn&&track.kind!=RF455RvpKind::FadeOut&&
                  track.kind!=RF455RvpKind::Quake&&track.kind!=RF455RvpKind::Blur&&
                  track.kind!=RF455RvpKind::Animation&&track.kind!=RF455RvpKind::CharacterFadeIn&&track.kind!=RF455RvpKind::CharacterFadeOut) {
            value.limitation="RVP Character/effect/audio/timer-rate provider remains open";return;
        }
        bound.tracks.push_back(std::move(track));waves.push_back(wave);
    }
    std::unique_ptr<ChInterface> renderer(new ChInterface);renderer->InitCharacter(GetD3dDevice());
    value.renderer=std::move(renderer);
    value.data=std::move(bound);value.actors.clear();value.actors.resize(value.data.actors.size());
    value.waves=std::move(waves);
    for(unsigned i=0;i<value.actors.size();++i)if(!value.data.actors[i].wave.empty())value.actors[i].waveHandle=IM_LoadWave(const_cast<char*>(value.data.actors[i].wave.c_str()),1);
    for(unsigned i=0;i<value.data.tracks.size();++i)if(value.data.tracks[i].kind==RF455RvpKind::Wave)value.waves[i].id=IM_LoadWave(const_cast<char*>(value.data.tracks[i].resource.c_str()),0);
    value.animations.reset(new AnimationManager);value.body=value.renderer->CreatePart455("BODY");
    value.effects=&RF455_AcquireRvpEffects();
    if(!value.actors.empty()) {
        for(std::size_t i=0;i<value.actors.size();++i) {
            const auto& source=value.data.actors[i];auto& actor=value.actors[i];
            const auto name=source.mapDummy.empty()?std::string():source.mapDummy.substr(1);
            actor.dummy=value.camera()->GetDummyID(const_cast<char*>(name.c_str()),FALSE);
            if(actor.dummy==0xffffffffu){value.limitation="RVP actor dummy binding failed;failure domain unaccepted";value.actors.clear();value.renderer.reset();value.animations.reset();value.body=nullptr;return;}
            RF455_LoadRvpActor(actor,source,*value.renderer,value.body,*value.animations);
        }
        value.limitation="RVP actor/basic FX/immediate audio active;advanced FX and global resource lifetime parity remain open";
    }
    RF455_AddMovieFlags(value.data.flags);
    if(value.data.flags&1)GetR3State()->mWideOn=TRUE;
    if(value.data.flags&2)GetR3State()->mIsDrawLogo=TRUE;
    RF455_AddMovieFlags(4); //Create8D82E6;raw flags do not call SetDefaultFov.
    value.playing=true; //Start(TRUE) sets play BEFORE testing movieLoaded.
    prepare(value);prepare(value); //OneTimeScene then explicit Prepare inCreate.
    value.loaded=true;
}
void RF455_RvpStart(bool beginning) {
    auto& value=movie();if(!ready(value))return;value.playing=true;
    if(value.loaded&&beginning)prepare(value);
}
void RF455_RvpPause(bool paused){movie().paused=paused;}
void RF455_RvpFrameMove() {
    auto& value=movie();if(!ready(value)||!value.loaded)return;
    //Ambient sound uses the previous actor matrix, even while flag16 suspends tracks/camera.
    for(unsigned i=0;i<value.actors.size();++i){auto& actor=value.actors[i];if(!actor.waveHandle)continue;
        const float volume=RF455_RvpVolume(actor.matrix[3],value.data.actors[i].waveDistance),pan=RF455_RvpPan(actor.matrix[3]);
        if(volume>0){if(!actor.wavePlaying){actor.wavePlaying=true;IM_SetLoopCntWave(actor.waveHandle,0);IM_PlayWave(actor.waveHandle,volume,pan);++value.ambientStarts;}
            else IM_SetWaveVolumeAndPan(actor.waveHandle,volume,pan);}
        else if(actor.wavePlaying){actor.wavePlaying=false;IM_StopWave(actor.waveHandle);++value.ambientStops;}
    }
    if(RF455_GetMovieState()&16)return;
    const float frame=float(double(value.camera()->GetNowFrame())*30);
    extract(value,frame);float matrix[4][4];bool playing=false;
    if(value.paused||!value.playing) {
        value.camera()->SetNowFrame(float(double(frame)/30));
        if(!(RF455_GetMovieState()&4)) {
            value.limitation="455 paused automatic-camera uses undefined scratch; domain unaccepted";return;
        }
    } else playing=value.camera()->PlayAniCamera(matrix,1,FALSE)!=FALSE;
    if(RF455_GetMovieState()&4)SetDefaultFov();
    else {
        Vector3f position;R3SetCameraMatrix(position,matrix);value.level->SetCameraPos(position);
        value.level->SetViewMatrix(R3MoveGetViewMatrix());
        SetFrustumNormalPlane();
    }
    if(!playing){RF455_AddMovieFlags(4);value.blur=0;value.playing=false;RF455_SetFullScreenEffectDensity(.25f);}
    for(std::size_t i=0;i<value.actors.size();++i)RF455_RvpActorFrame(value.actors[i],value.data.actors[i],*value.renderer,value.body,*value.camera());
    if(RF455_GetMovieState()&4)value.blur=0;
    if(value.blur!=0){RF455_SetFullScreenEffectDensity(1-value.blur);SetStateFullScreenEffect(0x80000000u);}
    else SetStateFullScreenEffect(0);
}
void RF455_RvpRender() {
    auto& value=movie();if(!ready(value)||!value.level->IsLoadedBsp()||!value.loaded||!value.renderer||(RF455_GetMovieState()&16))return;
    //The empty-list455 path has one unconditional UnSetState, no SetState.
    if(GetR3State()->mIsFog)GetD3dDevice()->SetRenderState(D3DRS_FOGENABLE,TRUE);
    for(std::size_t i=0;i<value.actors.size();++i)RF455_RvpActorDraw(value.actors[i],value.data.actors[i],*value.renderer,value.body,*value.effects,*value.level);
    if(!value.actors.empty()){value.renderer->SetState();value.renderer->FlushTransparency();value.renderer->UnSetState();}
    if(GetR3State()->mIsFog)GetD3dDevice()->SetRenderState(D3DRS_FOGENABLE,FALSE);
    value.renderer->UnSetState();
    for(auto& actor:value.actors)if(actor.visible&&actor.bone&&actor.mesh)value.effects->Draw(actor.mesh,reinterpret_cast<D3DXMATRIX*>(actor.matrix),actor.renderColor);
    if(GetR3State()->mIsFog)GetD3dDevice()->SetRenderState(D3DRS_FOGENABLE,TRUE);
}
void RF455_RvpRelease() {
    RF455_ReleaseRvpEffects();auto& value=movie();if(!value.level)return;
    value.camera()->ReleaseAniCamera();
    //455 Release leaves loaded/play/pause scalars untouched. Detach a camera-only
    // failed-load owner as well so the source-owned pointer cannot outlive it;
    // that failure-domain divergence is tracked, not accepted as full parity.
    value.level=nullptr;
    if(!value.loaded)return;
    value.actors.clear();value.renderer.reset();value.animations.reset();value.body=nullptr;value.effects=nullptr;IM_ReleaseAllWaves();value.waves.clear();value.data={};value.cursor=0;value.blur=0;
    RF455_RemoveMovieFlags(0xffffffffu);
}
