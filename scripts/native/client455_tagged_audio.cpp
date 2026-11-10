#include "client455_tagged_audio.h"
#include "client455_equipment_effects.h"
#include "r3enginekernel.h"
#include "r3sound.h"
#include "mss.h"
#include <array>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <list>
#include <string>
#include <vector>
#include <stdexcept>
extern HDIGDRIVER stDigital;
void RF455_PrepareTaggedAudio(const char* redist){AIL_set_redist_directory(redist);RF455_OpenEquipmentSounds455();}
namespace {
struct Definition {std::uint32_t id;std::string file;unsigned char loop=0;};
struct Wave {
    H3DSAMPLE samples[30]={};std::uint32_t tags[30]={};
    void* data=nullptr;std::uint32_t id=0,kind=0,active=0;
    float relative[3]={},tail[3]={};
};
static_assert(sizeof(Wave)==280,"Selected 455 cache record");
struct Entry {bool used=false;std::uint32_t key=0;Wave wave;};
bool definitions(const char* path,std::vector<Definition>& out){
    FILE* f=std::fopen(path,"rt");if(!f)return false;
    struct Close{FILE* f;~Close(){std::fclose(f);}} close{f};
    char text[256];bool section=false;
    while(std::fscanf(f,"%255s",text)==1){if(!std::strcmp(text,"[WaveList]")){section=true;break;}}
    if(!section)return true;
    while(std::fscanf(f,"%255s",text)==1){
        if(!_stricmp(text,"loop")){if(!out.empty())out.back().loop=1;continue;}
        long value=std::atol(text);
        if(!value&&text[0]=='0'&&(text[1]=='x'||text[1]=='X'))value=std::strtoul(text+2,nullptr,16);
        if(!value)continue;
        if(std::fscanf(f,"%255s",text)!=1)return false;
        if(std::strlen(text)>58)throw std::logic_error("455 tagged wave filename outside bounded manifest domain");
        _strlwr(text);Definition row;row.id=std::uint32_t(value);row.file=text;out.push_back(row);
    }
    return true;
}
}
struct RF455TaggedAudio::State {
    HPROVIDER provider=0;H3DPOBJECT listener=nullptr;std::string providerName;
    std::vector<Definition> files;std::array<Entry,64> entries;std::list<unsigned> order;
    float position[3]={};bool open=false;
    Definition* find(std::uint32_t id){for(auto& row:files)if(row.id==id)return &row;return nullptr;}
    const Entry* lookup(std::uint32_t id)const{for(unsigned slot:order)if(entries[slot].key==id)return &entries[slot];return nullptr;}
    Entry* lookup(std::uint32_t id){return const_cast<Entry*>(static_cast<const State*>(this)->lookup(id));}
    void release(Wave& wave){
        for(auto& handle:wave.samples)if(handle){AIL_end_3D_sample(handle);AIL_release_3D_sample_handle(handle);handle=nullptr;}
        if(wave.data){AIL_mem_free_lock(wave.data);wave.data=nullptr;}
        wave.kind=wave.active=0;
    }
    Wave& hit(std::uint32_t id,int& result){
        for(auto it=order.begin();it!=order.end();++it)if(entries[*it].key==id){
            unsigned slot=*it;order.erase(it);order.push_front(slot);result=-1;return entries[slot].wave;
        }
        unsigned slot=0;
        if(order.size()==64){slot=order.back();order.pop_back();result=0;}
        else {while(entries[slot].used)++slot;entries[slot].wave=Wave{};result=1;}
        entries[slot].used=true;entries[slot].key=id;order.push_front(slot);return entries[slot].wave;
    }
    bool load(Definition& file,std::uint32_t loop,Wave& wave){
        wave.samples[0]=AIL_allocate_3D_sample_handle(provider);if(!wave.samples[0])return false;
        S32 bytes=AIL_file_size(file.file.c_str());void* input=AIL_file_read(file.file.c_str(),nullptr);
        if(!input){AIL_release_3D_sample_handle(wave.samples[0]);wave.samples[0]=nullptr;return false;}
        S32 type=AIL_file_type(input,bytes);U32 size=0;
        if(type==1)wave.data=input;
        else if(type==2){AILSOUNDINFO info={};AIL_WAV_info(input,&info);AIL_decompress_ADPCM(&info,&wave.data,&size);AIL_mem_free_lock(input);}
        else if(type==13){AIL_decompress_ASI(input,bytes,file.file.c_str(),&wave.data,&size,nullptr);AIL_mem_free_lock(input);}
        else {AIL_mem_free_lock(input);AIL_release_3D_sample_handle(wave.samples[0]);wave.samples[0]=nullptr;wave.data=nullptr;return false;}
        AIL_set_3D_sample_file(wave.samples[0],wave.data);AIL_set_3D_sample_distances(wave.samples[0],150,40);
        if(loop==1)AIL_set_3D_sample_loop_count(wave.samples[0],0);
        return true;
    }
};
RF455TaggedAudio::RF455TaggedAudio():state(new State){}
RF455TaggedAudio::~RF455TaggedAudio(){Close();}
bool RF455TaggedAudio::IsOpen()const{return state->open;}
const char* RF455TaggedAudio::ProviderName()const{return state->providerName.c_str();}
bool RF455TaggedAudio::Open(const char* manifest,const char* redist){
    if(IsOpen())return true;
    if(!stDigital)return false;
    if(!definitions(manifest,state->files))return false;
    AIL_set_redist_directory(redist);
    HPROENUM cursor=HPROENUM_FIRST;HPROVIDER candidate=0,fast=0,creative=0;char* name=nullptr;
    while(AIL_enumerate_3D_providers(&cursor,&candidate,&name)){
        if(!_stricmp(name,"Creative Labs EAX 2 (TM)"))creative=candidate;
        if(!_stricmp(name,"Miles Fast 2D Positional Audio"))fast=candidate;
    }
    if(creative&&AIL_open_3D_provider(creative)==M3D_NOERR){state->provider=creative;state->providerName="Creative Labs EAX 2 (TM)";}
    else if(fast&&AIL_open_3D_provider(fast)==M3D_NOERR){state->provider=fast;state->providerName="Miles Fast 2D Positional Audio";}
    else return false;
    state->listener=AIL_open_3D_listener(state->provider);
    if(!state->listener){AIL_close_3D_provider(state->provider);state->provider=0;return false;}
    AIL_set_3D_position(state->listener,0,0,0);AIL_set_3D_orientation(state->listener,0,0,1,0,1,0);
    AIL_set_3D_room_type(state->provider,0);state->open=true;
    char debug[160];std::sprintf(debug,"RF455 TaggedAudio:ready:%u:%s",unsigned(state->files.size()),state->providerName.c_str());OutputDebugStringA(debug);
    return true;
}
void RF455TaggedAudio::Close(){
    if(state->open){
        for(unsigned slot:state->order)state->release(state->entries[slot].wave);
        AIL_close_3D_listener(state->listener);AIL_close_3D_provider(state->provider);
    }
    state->order.clear();for(auto& entry:state->entries)entry=Entry{};
    state->files.clear();state->provider=0;state->listener=nullptr;state->open=false;state->providerName.clear();
}
void RF455TaggedAudio::SetListener(const float* position){std::memcpy(state->position,position,12);}
void RF455TaggedAudio::Collect(){
    if(!state->open)return;
    bool empty=true; // 8BCD60 deliberately does not reset this for each entry.
    for(auto it=state->order.begin();it!=state->order.end();){
        auto& entry=state->entries[*it];auto& wave=entry.wave;
        for(auto& handle:wave.samples)if(handle){
            if(AIL_3D_sample_status(handle)==2&&wave.active){AIL_end_3D_sample(handle);AIL_release_3D_sample_handle(handle);handle=nullptr;}
            else if(handle)empty=false;
        }
        if(wave.data&&empty){AIL_mem_free_lock(wave.data);wave.data=nullptr;wave.kind=wave.active=0;entry.used=false;it=state->order.erase(it);}
        else ++it;
    }
}
void RF455TaggedAudio::PlayAtListener(std::uint32_t id,std::uint32_t loop,std::uint32_t tag){Play(id,loop,tag,state->position);}
void RF455TaggedAudio::Play(std::uint32_t id,std::uint32_t loop,std::uint32_t tag,const float* position){
    if(!GetR3State()->mSoundOn||!state->open)return;
    auto* file=state->find(id);if(!file)return;
    Collect();int hit=0;auto& wave=state->hit(id,hit);
    if(tag)for(auto existing:wave.tags)if(existing==tag)return;
    wave.active=0;unsigned slot=0;
    if(hit!=-1){
        if(!IsExistFile(const_cast<char*>(file->file.c_str())))return;
        if(hit==0)state->release(wave);
        file->loop=static_cast<unsigned char>(loop);state->load(*file,loop,wave);wave.tags[0]=tag;
    }else{
        bool found=false;
        for(unsigned n=0;n<30;++n)if(!wave.samples[n]||AIL_3D_sample_status(wave.samples[n])==2){slot=n;found=true;break;}
        if(!found)slot=0;
        if(wave.samples[slot]){AIL_release_3D_sample_handle(wave.samples[slot]);wave.samples[slot]=nullptr;}
        wave.samples[slot]=AIL_allocate_3D_sample_handle(state->provider);if(!wave.samples[slot])return;
        AIL_set_3D_sample_file(wave.samples[slot],wave.data);wave.tags[slot]=tag;
    }
    auto handle=wave.samples[slot];if(!handle)return;
    wave.id=id;wave.kind=1;
    for(unsigned i=0;i<3;++i)wave.relative[i]=position[i]-state->position[i];
    float orientation[3]={-wave.relative[0],-wave.relative[1],-wave.relative[2]};
    const float length=std::sqrt(orientation[0]*orientation[0]+orientation[1]*orientation[1]+orientation[2]*orientation[2]);
    // 51D5D0 also divides a zero vector by zero. Keep its NaN orientation.
    for(auto& value:orientation)value/=length;
    AIL_set_3D_position(handle,wave.relative[0]*.1f,0,wave.relative[2]*.1f);
    AIL_set_3D_orientation(handle,orientation[0],0,orientation[2],0,1,0);
    AIL_set_3D_sample_volume(handle,GetGlobalWavVolume());if(loop==1)AIL_set_3D_sample_loop_count(handle,0);
    wave.active=1;AIL_start_3D_sample(handle);AIL_active_sample_count(stDigital);AIL_set_3D_sample_effects_level(handle,0);
}
void RF455TaggedAudio::Stop(std::uint32_t id,std::uint32_t tag){
    if(!state->open)return;auto* entry=state->lookup(id);if(!entry)return;
    for(unsigned n=0;n<30;++n)if(entry->wave.tags[n]==tag){AIL_end_3D_sample(entry->wave.samples[n]);return;}
}
RF455TaggedWaveView RF455TaggedAudio::Inspect(std::uint32_t id,unsigned slot)const{
    RF455TaggedWaveView out;out.cacheEntries=unsigned(state->order.size());out.manifestRecords=unsigned(state->files.size());
    const auto* entry=state->lookup(id);if(!entry)return out;if(slot>=30)throw std::out_of_range("455 wave slot");
    out.present=true;out.slots=30;out.sample=entry->wave.samples[slot];out.data=entry->wave.data;out.tag=entry->wave.tags[slot];out.kind=entry->wave.kind;out.active=entry->wave.active;
    out.waveID=entry->wave.id;
    std::memcpy(out.relative,entry->wave.relative,12);return out;
}
