#include "Character.h"
#include "client455_rvp_runtime.h"
#include "client455_rvp.h"
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
struct Movie {
    CLevel* level=nullptr;
    bool loaded=false,playing=false,paused=false;
    RF455RvpDocument data;
    std::unique_ptr<ChInterface> renderer;
    std::size_t cursor=0;
    unsigned cameras=0,fadeIns=0,fadeOuts=0;
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
    return {value.loaded,camera,value.playing,value.paused,value.data.tracks.size(),value.cursor,
        value.cameras,value.fadeIns,value.fadeOuts,camera?value.camera()->GetNowFrame():0,
        value.blur,value.limitation.c_str()};
}
void RF455_RvpCreate(char* path,CLevel* level) {
    auto& value=movie();
    if(value.level&&value.level!=level)throw std::logic_error("RVP previous owner was not released");
    value.level=level;value.loaded=false;value.limitation.clear();
    value.cameras=value.fadeIns=value.fadeOuts=0;value.data={};value.cursor=0;
    if(!path||!level)return;
    std::string cameraPath(path);const auto dot=cameraPath.find_last_of('.');
    if(dot!=std::string::npos)cameraPath.resize(dot);cameraPath+=".cam";
    value.camera()->LoadAniCamera(&cameraPath[0]);if(!ready(value))return;
    const auto* camera=RF455_GetCameraDocument(value.camera());RF455RvpDocument data;std::string error;
    if(!RF455_LoadRvp(path,data,&error,camera)){value.limitation=error;return;}
    // Mandatory unfinished providers are refused before loaded=true. There is
    // no fake animation/effect/audio callback in this production path.
    if(!data.actors.empty()||(data.flags&8)) {
        value.limitation="RVP actor/effect/audio/screen providers remain open";return;
    }
    RF455RvpDocument bound;bound.flags=data.flags;bound.totalFrame=data.totalFrame;
    for(auto track:data.tracks) {
        if(track.kind==RF455RvpKind::Camera) {
            const auto name=track.reference.empty()?std::string():track.reference.substr(1);
            DWORD found=0xffffffffu;
            for(DWORD i=0;i<value.camera()->GetCameraNum();++i) {
                const char* actual=value.camera()->GetCameraName(i);
                if(actual&&lower(actual)==name){found=i;break;}
            }
            if(found==0xffffffffu){Warning("RVP camera not found",&track.reference[0]);continue;}
            track.value=found;
        } else if(track.kind!=RF455RvpKind::FadeIn&&track.kind!=RF455RvpKind::FadeOut&&
                  track.kind!=RF455RvpKind::Quake&&track.kind!=RF455RvpKind::Blur) {
            value.limitation="RVP Character/effect/audio/timer-rate provider remains open";return;
        }
        bound.tracks.push_back(std::move(track));
    }
    std::unique_ptr<ChInterface> renderer(new ChInterface);renderer->InitCharacter(GetD3dDevice());
    value.renderer=std::move(renderer);
    value.data=std::move(bound);RF455_AddMovieFlags(value.data.flags);
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
    auto& value=movie();if(!ready(value)||!value.loaded||(RF455_GetMovieState()&16))return;
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
    }
    if(!playing){RF455_AddMovieFlags(4);value.blur=0;value.playing=false;RF455_SetFullScreenEffectDensity(.25f);}
    if(RF455_GetMovieState()&4)value.blur=0;
    if(value.blur!=0){RF455_SetFullScreenEffectDensity(1-value.blur);SetStateFullScreenEffect(0x80000000u);}
    else SetStateFullScreenEffect(0);
}
void RF455_RvpRender() {
    auto& value=movie();if(!ready(value)||!value.level->IsLoadedBsp()||!value.loaded||!value.renderer||(RF455_GetMovieState()&16))return;
    //The empty-list455 path has one unconditional UnSetState, no SetState.
    if(GetR3State()->mIsFog)GetD3dDevice()->SetRenderState(D3DRS_FOGENABLE,TRUE);
    if(GetR3State()->mIsFog)GetD3dDevice()->SetRenderState(D3DRS_FOGENABLE,FALSE);
    value.renderer->UnSetState();
    if(GetR3State()->mIsFog)GetD3dDevice()->SetRenderState(D3DRS_FOGENABLE,TRUE);
}
void RF455_RvpRelease() {
    auto& value=movie();if(!value.level)return;
    value.camera()->ReleaseAniCamera();
    //455 Release leaves loaded/play/pause scalars untouched. Detach a camera-only
    // failed-load owner as well so the source-owned pointer cannot outlive it;
    // that failure-domain divergence is tracked, not accepted as full parity.
    value.level=nullptr;
    if(!value.loaded)return;
    value.renderer.reset();value.data={};value.cursor=0;value.blur=0;
    RF455_RemoveMovieFlags(0xffffffffu);
}
