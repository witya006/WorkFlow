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
#include "client455_rvp_effects.h"
#include "client455_rvp_audio.h"
#include "client455_sound_im.h"
#include "client455_loop_clock.h"
#include "client455_movie_state.h"
#include <client455_normal_renderer_math.h>
#include "RTMovie.h"
#include "r3enginekernel.h"
#include "r3sound.h"
#include "jmalloc.h"
#include "mss.h"
#include <cmath>
#include <cstdio>
#include <cstring>
#include <memory>
#include <stdexcept>
extern CMainApp g_MainApp;
static unsigned warnings=0;
static void check(bool ok,const char* message){if(!ok)throw std::runtime_error(message);}
static void phase(const char* text){std::fprintf(stderr,"phase:%s\n",text);std::fflush(stderr);}
static void warning(char* text){++warnings;phase(text);}
static void cameraAt(float x,float y,float z){auto* state=GetR3State();D3DXMatrixIdentity(&state->mMatView);D3DXMatrixIdentity(&state->mInvMatView);state->mInvMatView._41=x;state->mInvMatView._42=y;state->mInvMatView._43=z;}
static HSAMPLE sample(unsigned id){auto view=RF455_GetIMWaveView(id);check(view.handle&&view.memory&&view.sample2D&&view.used,"actual loaded Miles sample");return static_cast<HSAMPLE>(view.handle);}
static void volume(unsigned id,float expected){F32 actual=0,pan=0;AIL_sample_volume_pan(sample(id),&actual,&pan);check(std::abs(actual-expected)<1e-6f&&pan==.5f,"actual Miles volume/center pan");}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);phase("before-engine");InitR3Engine();SetWarningMessageProc(warning);
    auto* state=GetR3State();state->mScreenXsize=640;state->mScreenYsize=480;state->mbFullScreen=FALSE;state->mSoundOn=TRUE;state->mMusicOn=TRUE;ForceFullScreen();
    std::strcpy(state->MapPath,".\\Map\\");std::strcpy(state->EntityPath,".\\Map\\Entity\\");
    check(InitR3SoundSystem(".\\Snd\\WaveList.spt")!=FALSE,"real Miles digital driver");phase("Miles");
    check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"real D3D9 device");R3SetViewPort(0,0,640,480);
    unsigned elapsed=0,starts=0,stops=0,events=0;int before=0,after=0;
    const float savedScale=RF455_GetEngineLoopClockState()->timeScale;
    {
        ChInterface outer;outer.InitCharacter(GetD3dDevice());before=GetDmallocSize();
        cameraAt(0,0,0);float p[3]={0,0,0};check(RF455_RvpVolume(p,200)==1,"inner volume");
        p[0]=50;check(RF455_RvpVolume(p,200)==1&&RF455_RvpPan(p)==1,"inner boundary and right pan");
        p[0]=-125;check(RF455_RvpVolume(p,200)==.5f&&RF455_RvpPan(p)==0,"half attenuation and left pan");
        p[0]=200;check(RF455_RvpVolume(p,200)==0,"outer boundary");p[0]=250;check(RF455_RvpVolume(p,200)<0,"no clamp below zero");
        state->mMusicOn=FALSE;unsigned disabled=IM_LoadWave("loop.mp3",1);check(disabled==1&&!RF455_GetIMWaveView(disabled).handle&&RF455_GetIMWaveView(disabled).sample2D,"music-off reserves MP3 record");
        IM_ReleaseWave(disabled);state->mMusicOn=TRUE;unsigned ambient=IM_LoadWave("loop.mp3",1);check(ambient==2,"released occupied slot is not reused");
        check(RF455_GetIMWaveView(ambient).loopCount==0&&AIL_sample_loop_count(sample(ambient))==1,"raw flag1 actual loop count differs from metadata0");
        IM_SetLoopCntWave(ambient,0);check(AIL_sample_loop_count(sample(ambient))==1,"unchanged metadata skips actual loop update");
        SetGlobalWavVolume(.25f);IM_PlayWave(ambient,.5f,-1);volume(ambient,.125f);
        state->mSoundOn=FALSE;IM_SetLoopCntWave(ambient,7);check(RF455_GetIMWaveView(ambient).loopCount==0,"sound-off loop gate");
        IM_SetWaveVolumeAndPan(ambient,.75f,1);volume(ambient,.75f);IM_StopWave(ambient);check(AIL_sample_status(sample(ambient))==SMP_STOPPED,"stop works with sound disabled");state->mSoundOn=TRUE;
        unsigned event=IM_LoadWave("loop.mp3",0);check(RF455_GetIMWaveView(event).loopCount==1&&AIL_sample_loop_count(sample(event))==0,"raw flag0 event loops in actual Miles");
        IM_PlayWave(event,.5f,1);volume(event,.125f);Sleep(90);S32 total=0,current=0;AIL_sample_ms_position(sample(event),&total,&current);check(total>0&&current>0&&AIL_sample_status(sample(event))==SMP_PLAYING,"real decoder/playback clock advances");elapsed=current;
        unsigned wav=IM_LoadWave("stock.wav",0);check(wav&&RF455_GetIMWaveView(wav).used&&!RF455_GetIMWaveView(wav).sample2D&&!RF455_GetIMWaveView(wav).handle,"455 WAV registration has no sample");IM_PlayWave(wav,1,1);
        IM_ReleaseAllWaves();check(!RF455_GetIMWaveView(0).count&&!RF455_GetIMWaveView(0).capacity,"global release clears table");
        for(unsigned i=1;i<=129;++i){check(IM_LoadWave("stock.wav",0)==i,"monotonic occupied IDs");check(RF455_GetIMWaveView(0).capacity==(i<128?128u:160u),"128/32 capacity boundary");}IM_ReleaseAllWaves();
        check(GetDmallocSize()==before,"immediate-wave Dmalloc release");phase("immediate-API");
        CCamera camera;g_pCamera=&camera;std::unique_ptr<CLand> land(new CLand);check(land->Create()!=0,"land");R3SetTime(0);RTMoviePause(FALSE);check(land->LoadLevel(".\\Map\\neutralAS1\\neutralAS1.bsp")!=0,"world");
        auto* level=land->GetLevel();RTMovieRelease();R3SetTime(0);cameraAt(0,1,0);RTMovieCreate("audio.rvp",level);check(IsLoadedRTMovie()&&RF455_RvpView().actors==2,"real audio RVP loaded");
        check(RF455_GetIMWaveView(0).count==3&&RF455_RvpView().waveEvents==2,"actor/event IDs and double Prepare event");
        const auto& actor=*RF455_RvpActorState(0);check(actor.waveHandle==1&&!actor.wavePlaying,"ambient waiting for first frame");
        RF455_AddMovieFlags(16);const auto frozen=RF455_RvpView();RTMovieFrameMove();check(RF455_RvpView().ambientStarts==1&&RF455_RvpView().cursor==frozen.cursor&&RF455_RvpView().poseUpdates==frozen.poseUpdates,"ambient executes before flag16 gate");
        volume(actor.waveHandle,.25f);RTMovieFrameMove();volume(actor.waveHandle,1); //updates omit global volume
        cameraAt(1000,1,0);RTMovieFrameMove();check(RF455_RvpView().ambientStops==1&&!actor.wavePlaying,"distance stops ambient despite flag16");
        cameraAt(0,1,0);RTMovieFrameMove();check(RF455_RvpView().ambientStarts==2&&actor.wavePlaying,"ambient restarts on reentry");
        //Timer-rate is camera-dependent and is consumed/skipped under flag4.
        //Clear it here; Extract reads the previous camera frame before Play updates it.
        RF455_RemoveMovieFlags(16|4);R3SetTime(.25f);R3SetLoopTime(.25f);RTMovieFrameMove();R3SetTime(.5f);RTMovieFrameMove();
        check(RF455_RvpView().waveEvents==3&&RF455_GetEngineLoopClockState()->timeScale==.5f,"actor-fallback event and real timer_rate setter");
        //Rewind with the listener near the real Dummy01, proving ordinary RVP
        //event execution reaches the loaded Miles sample, without a fake sink.
        float matrix[4][4];const DWORD dummy=level->mAutoAniCam.GetDummyID("Dummy01",FALSE);check(dummy!=0xffffffffu,"actual CAM dummy");level->mAutoAniCam.GetDummyMatrix(matrix,dummy,0);
        cameraAt(matrix[3][0],matrix[3][1]+1,matrix[3][2]);R3SetTime(0);RTMovieStartPlay(TRUE);check(AIL_sample_status(sample(2))==SMP_PLAYING,"ordinary RVP event starts actual Miles sample");
        const auto done=RF455_RvpView();starts=done.ambientStarts;stops=done.ambientStops;events=done.waveEvents;
        check(land->Destroy()!=0,"destroy");RTMovieRelease();g_pCamera=nullptr;check(!RF455_GetIMWaveView(0).count&&!RF455_RvpEffectsState().present,"RVP releases global immediate waves and deferred FX");
        check(&CRender::GetRender()==&outer,"outer renderer restored");after=GetDmallocSize();check(before==after,"world/audio Dmalloc balance");
    }
    RF455_SetEngineLoopTimeScale(savedScale);RF455_ReleaseNormalCharacterSharedResources();g_MainApp.ReleaseR3D3D();ReleaseR3SoundSystem();ReleaseR3Engine();
    FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"result");
    std::fprintf(out,"{\"status\":\"PASS\",\"real_Miles\":true,\"decoder_elapsed_ms\":%u,\"WAV_no_handle\":true,\"MP3_raw_loop_quirk\":true,\"capacity_boundary\":129,\"ambient_starts\":%u,\"ambient_stops\":%u,\"wave_events\":%u,\"ambient_before_flag16\":true,\"timer_rate_actual\":true,\"warnings\":%u,\"memory_before\":%d,\"memory_after\":%d,\"full_audio_parity\":false,\"full_Tutorial\":false}\n",elapsed,starts,stops,events,warnings,before,after);std::fclose(out);return 0;
}
int main(){try{return run();}catch(const std::exception& error){std::fprintf(stderr,"audio-probe:%s\n",error.what());return 1;}}
