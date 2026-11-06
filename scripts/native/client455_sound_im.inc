//Pinned455 immediate-wave table. RVP uses this process-wide owner, not PlayWave's cache.
#include "client455_sound_im.h"
#include <cstring>
struct RF455ImmediateWave {
    DWORD flag;
    HSAMPLE handle;
    U32* memory;
    DWORD loopCount;
    WORD sample2D,used;
};
static_assert(sizeof(RF455ImmediateWave)==20,"455 immediate wave record");
static RF455ImmediateWave* stIM_WaveList=nullptr;
static int stIM_MaxWaveNum=0,stIM_WaveNum=0;

static RF455ImmediateWave* immediate(unsigned id){
    //Out-of-range IDs are outside the accepted original unchecked domain.
    return stIM_WaveList&&id&&id<=unsigned(stIM_WaveNum)?stIM_WaveList+id-1:nullptr;
}
static BOOL loadImmediateMP3(char* name,DWORD loop,HSAMPLE* handle,U32** memory){
    if(!stIsInit||!GetR3State()->mMusicOn)return TRUE;
    *memory=static_cast<U32*>(AIL_file_read(name,FILE_READ_WITH_SIZE));
    if(!*memory){Warning(name,"<- File not found\n");return FALSE;}
    *handle=AIL_allocate_sample_handle(stDigital);
    if(*handle){AIL_init_sample(*handle);if(AIL_set_named_sample_file(*handle,name,*memory+1,**memory,-1)){
        //The target passes the raw load flag as the actual Miles loop count.
        AIL_set_sample_loop_count(*handle,loop);return TRUE;
    }}
    AIL_mem_free_lock(*memory);*memory=nullptr;Warning(AIL_last_error(),"");return FALSE;
}
DWORD IM_LoadWave(char* name,DWORD flag){
    if(!stIsInit)return 0;
    if(!stIM_MaxWaveNum){stIM_MaxWaveNum=128;stIM_WaveList=static_cast<RF455ImmediateWave*>(Dmalloc(20*stIM_MaxWaveNum));std::memset(stIM_WaveList,0,20*stIM_MaxWaveNum);}
    if(!IsExistFile(name))return 0;
    int slot=0;while(slot<stIM_WaveNum&&stIM_WaveList[slot].used)++slot;
    auto& wave=stIM_WaveList[slot];wave.loopCount=flag!=1;
    const char* dot=std::strrchr(name,'.');const char* extension=dot?dot+1:name+1;
    if(!_stricmp(extension,"MP3")){loadImmediateMP3(name,flag,&wave.handle,&wave.memory);wave.sample2D=1;}
    else wave.sample2D=0; //The measured non-MP3 branch does not load a handle.
    wave.used=1;
    if(slot==stIM_WaveNum&&++stIM_WaveNum>=stIM_MaxWaveNum){
        stIM_WaveList=static_cast<RF455ImmediateWave*>(ReAlloc(stIM_WaveList,20*stIM_MaxWaveNum,20*(stIM_MaxWaveNum+32)));
        std::memset(stIM_WaveList+stIM_MaxWaveNum,0,20*32);stIM_MaxWaveNum+=32;
    }
    return slot+1;
}
void IM_ReleaseWave(DWORD id){
    if(!stIsInit)return;auto* wave=immediate(id);if(!wave)return;
    if(wave->handle){if(wave->sample2D)AIL_release_sample_handle(wave->handle);else AIL_release_3D_sample_handle(reinterpret_cast<H3DSAMPLE>(wave->handle));wave->handle=nullptr;}
    if(wave->memory){AIL_mem_free_lock(wave->memory);wave->memory=nullptr;}
    //used remains set: a released record is not recycled by the original search.
}
void IM_ReleaseAllWaves(){
    if(!stIsInit)return;for(int i=0;i<stIM_WaveNum;++i)IM_ReleaseWave(i+1);stIM_WaveNum=0;
    if(stIM_WaveList){Dfree(stIM_WaveList);stIM_WaveList=nullptr;stIM_MaxWaveNum=0;}
}
void IM_SetWaveVolumeAndPan(DWORD id,float volume,float pan){
    (void)pan;if(!stIsInit)return;auto* wave=immediate(id);if(!wave||!wave->handle)return;
    if(wave->sample2D)AIL_set_sample_volume_pan(wave->handle,volume,.5f);
    else AIL_set_3D_sample_volume(reinterpret_cast<H3DSAMPLE>(wave->handle),volume);
}
void IM_PlayWave(DWORD id,float volume,float pan){
    (void)pan;if(!stIsInit||!GetR3State()->mSoundOn)return;auto* wave=immediate(id);if(!wave||!wave->handle)return;
    IM_SetWaveVolumeAndPan(id,float(double(volume)*stGlobalWavVolume),.5f);
    if(wave->sample2D)AIL_start_sample(wave->handle);else AIL_start_3D_sample(reinterpret_cast<H3DSAMPLE>(wave->handle));
}
void IM_SetLoopCntWave(DWORD id,DWORD count){
    if(!stIsInit||!GetR3State()->mSoundOn)return;auto* wave=immediate(id);if(!wave||(!wave->handle&&wave->sample2D)||wave->loopCount==count)return;
    wave->loopCount=count;if(wave->sample2D)AIL_set_sample_loop_count(wave->handle,count);
}
void IM_StopWave(DWORD id){
    if(!stIsInit)return;auto* wave=immediate(id);if(!wave||!wave->handle)return;
    if(wave->sample2D)AIL_stop_sample(wave->handle);
    else {auto handle=reinterpret_cast<H3DSAMPLE>(wave->handle);AIL_stop_3D_sample(handle);AIL_end_3D_sample(handle);AIL_release_3D_sample_handle(handle);wave->handle=nullptr;
        if(wave->memory){AIL_mem_free_lock(wave->memory);wave->memory=nullptr;}}
}
RF455IMWaveView RF455_GetIMWaveView(unsigned id){
    const auto* wave=immediate(id);if(!wave)return {unsigned(stIM_WaveNum),unsigned(stIM_MaxWaveNum),0,0,0,nullptr,nullptr};
    return {unsigned(stIM_WaveNum),unsigned(stIM_MaxWaveNum),wave->loopCount,wave->sample2D,wave->used,wave->handle,wave->memory};
}
