#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "input/imeedit.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "mainapp.h"
#include "client455_tagged_audio.h"
#include "mss.h"
#include "jmalloc.h"
#include <cstdio>
#include <cmath>
#include <stdexcept>
extern CMainApp g_MainApp;
static unsigned checks=0;
static void check(bool ok,const char* message){++checks;if(!ok)throw std::runtime_error(message);}
static H3DSAMPLE sample(RF455TaggedAudio& audio,unsigned id,unsigned slot=0){auto view=audio.Inspect(id,slot);check(view.present&&view.sample&&view.data,"actual loaded sample");return static_cast<H3DSAMPLE>(view.sample);}
static void phase(const char* name){std::fprintf(stderr,"phase:%s\n",name);std::fflush(stderr);}
struct AudioScope {
    RF455TaggedAudio& audio=g_MainApp.TaggedAudio455();
    ~AudioScope(){audio.Close();ReleaseR3SoundSystem();ReleaseR3Engine();}
};
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    InitR3Engine();auto* engine=GetR3State();engine->mSoundOn=TRUE;engine->mMusicOn=TRUE;SetGlobalWavVolume(0);
    AudioScope cleanup;
    RF455_PrepareTaggedAudio(engine->SoundPath);
    check(InitR3SoundSystem(".\\Snd\\WaveList.spt")!=0,"actual digital driver");
    auto& audio=g_MainApp.TaggedAudio455();check(!audio.IsOpen(),"actual mainapp owner starts closed");
    check(audio.Open(".\\Snd\\WaveList.spt",engine->SoundPath),"actual provider/listener open");phase(audio.ProviderName());
    unsigned manifest=audio.Inspect(0).manifestRecords;check(manifest>1000,"real full WaveList");
    const float listener[3]={10,20,30},position[3]={20,40,60};audio.SetListener(listener);
    engine->mSoundOn=FALSE;audio.Play(277034,1,1,position);check(!audio.Inspect(277034).present,"sound disabled fastpath");engine->mSoundOn=TRUE;
    audio.Play(0xfefefefe,1,1,position);check(!audio.Inspect(0xfefefefe).present,"missing ID no allocation");
    audio.Play(277034,1,1,position);auto first=sample(audio,277034);
    check(AIL_3D_sample_status(first)==SMP_PLAYING&&AIL_3D_sample_loop_count(first)==0,"real looped radar sound");
    check(AIL_3D_sample_volume(first)==0,"real Miles sample muted for lab");
    float x=0,y=0,z=0;AIL_3D_position(first,&x,&y,&z);check(x==1&&y==0&&z==3,"3D relative XZ times0.1");
    float maximum=0,minimum=0;AIL_3D_sample_distances(first,&maximum,&minimum);check(maximum==150&&minimum==40,"actual first-slot distances");
    auto view=audio.Inspect(277034);check(view.relative[0]==10&&view.relative[1]==20&&view.relative[2]==30,"cache keeps relative Y despite flat rendering");
    audio.Play(277034,1,1,listener);check(audio.Inspect(277034).sample==first&&!audio.Inspect(277034,1).sample&&audio.Inspect(277034).relative[0]==10,"duplicate tag suppresses restart andposition writes");
    audio.PlayAtListener(277034,1,2);auto second=sample(audio,277034,1);check(second!=first&&audio.Inspect(277034,1).tag==2,"same PCM multiple tagged channels");
    AIL_3D_position(second,&x,&y,&z);check(x==0&&y==0&&z==0,"listener-position wrapper");
    audio.Stop(277034,999);check(AIL_3D_sample_status(first)==SMP_PLAYING&&AIL_3D_sample_status(second)==SMP_PLAYING,"unmatched stop preserves channels");
    audio.Stop(277034,1);check(AIL_3D_sample_status(first)==SMP_DONE&&AIL_3D_sample_status(second)==SMP_PLAYING,"stop targets first matching tag");
    audio.Collect();check(!audio.Inspect(277034).sample&&audio.Inspect(277034).tag==1&&audio.Inspect(277034).data,"collect releases done handle but keeps tag alongside active channel");
    audio.Play(277034,1,1,position);check(!audio.Inspect(277034).sample&&audio.Inspect(277034,1).sample==second,"stale tag still suppresses reusing vacant slot");
    audio.Stop(277034,2);audio.Collect();check(!audio.Inspect(277034).present,"all stopped record is recycled");
    audio.PlayAtListener(277034,1,1);check(AIL_3D_sample_status(sample(audio,277034))==SMP_PLAYING,"same tag can play after whole-record recycle");
    audio.Close();check(!audio.IsOpen()&&!audio.Inspect(277034).present,"close releases owner");
    check(audio.Open("fixture.spt",engine->SoundPath),"fixture reopens actual provider");
    for(unsigned tag=1;tag<=30;++tag)audio.PlayAtListener(1000,1,tag);
    for(unsigned slot=0;slot<30;++slot)check(audio.Inspect(1000,slot).tag==slot+1&&AIL_3D_sample_status(sample(audio,1000,slot))==SMP_PLAYING,"30 actual live slots");
    audio.PlayAtListener(1000,1,31);check(audio.Inspect(1000).tag==31&&audio.Inspect(1000,29).tag==30,"full30channels replace slot0");audio.Close();
    check(audio.Open("fixture.spt",engine->SoundPath),"cache pressure provider");
    for(unsigned id=1000;id<1064;++id){audio.PlayAtListener(id,1,1);check(audio.Inspect(id).sample!=nullptr,"real64cache entries");}
    check(audio.Inspect(1000).cacheEntries==64,"64entry boundary");
    audio.PlayAtListener(1000,1,1);audio.PlayAtListener(1064,1,1);
    check(audio.Inspect(1000).present&&!audio.Inspect(1001).present&&audio.Inspect(1064).sample&&audio.Inspect(1064).cacheEntries==64,"LRU hit promotes evenwhen tag suppresses andvictim reused");
    check(audio.Inspect(1064).waveID==1001,"victim stale tag suppresses evennew key before old payload release");
    audio.PlayAtListener(1065,1,999);check(audio.Inspect(1065).waveID==1065&&audio.Inspect(1065).tag==999,"unique tag actually reloads LRU victim");
    audio.Close();check(audio.Inspect(0).cacheEntries==0,"all real samples andPCM released");
    FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"output");
    std::fprintf(out,"{\"status\":\"PASS\",\"checks\":%u,\"manifest_records\":%u,\"real_Miles_provider_listener_samples\":true,\"actual_MainApp_owner\":true,\"real_radar_WAV\":true,\"muted_lab\":true,\"duplicate_and_stale_tags\":true,\"targeted_stop\":true,\"relative_3D_position\":true,\"channels\":30,\"cache_capacity\":64,\"LRU_reuse\":true,\"full_nuclear_aiming\":false,\"full_audio_parity\":false,\"audible_output_capture\":false,\"full_client\":false}\n",checks,manifest);std::fclose(out);return 0;
}
int main(){try{return run();}catch(const std::exception& e){std::fprintf(stderr,"Tagged audio:%s\n",e.what());return 1;}}
