#include "client455_tagged_audio.h"
#include "client455_equipment_effects.h"
#include "client455_resource_text.h"
#include "r3enginekernel.h"
#include "r3sound.h"
#include "mss.h"
#include <array>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <list>
#include <new>
#include <string>
#include <vector>
#include <stdexcept>
extern HDIGDRIVER stDigital;
void RF455_PrepareTaggedAudio(const char* redist){if(redist)AIL_set_redist_directory(redist);RF455_OpenEquipmentSounds455();}
namespace {
struct Definition {std::uint32_t id;std::string file;unsigned char loop=0;};
struct Wave {
    H3DSAMPLE samples[30]={};std::uint32_t tags[30]={};
    void* data=nullptr;std::uint32_t id=0,kind=0,active=0;
    float relative[3]={},tail[3]={};
};
static_assert(sizeof(Wave)==280,"Selected 455 cache record");
struct Entry {bool used=false;std::uint32_t key=0;Wave wave;void* allocationBase=nullptr;};
struct LockedFree {void operator()(void* pointer)const{if(pointer)AIL_mem_free_lock(pointer);}};
using LockedMemory=std::unique_ptr<void,LockedFree>;
bool definitions(const char* path,std::vector<Definition>& out){
    RF455ResourceText input;
    if(!input.open(path))return false;
    const auto reject = [&] {
        if (input.hasCachedInput()) RF455_GetCharacterRfsCache()->RemoveLooseBytes(path);
        return false;
    };
    char text[256];bool section=false;
    while(input.read(text)){if(!std::strcmp(text,"[WaveList]")){section=true;break;}}
    if(!section)return !input.failed();
    while(input.read(text)){
        if(!_stricmp(text,"loop")){if(!out.empty())out.back().loop=1;continue;}
        long value=std::atol(text);
        if(!value&&text[0]=='0'&&(text[1]=='x'||text[1]=='X'))value=std::strtoul(text+2,nullptr,16);
        if(!value)continue;
        if(!input.read(text)||std::strlen(text)>58)return reject();
        _strlwr(text);Definition row;row.id=std::uint32_t(value);row.file=text;out.push_back(row);
    }
    return !input.failed();
}
}
struct RF455TaggedAudio::State {
    HPROVIDER provider=0;H3DPOBJECT listener=nullptr;std::string providerName;
    std::vector<Definition> files;std::array<Entry,64> entries;std::list<unsigned> order;
    float position[3]={};bool open=false;
    Definition* find(std::uint32_t id){for(auto& row:files)if(row.id==id)return &row;return nullptr;}
    const Entry* lookup(std::uint32_t id)const{for(unsigned slot:order)if(entries[slot].key==id)return &entries[slot];return nullptr;}
    Entry* lookup(std::uint32_t id){return const_cast<Entry*>(static_cast<const State*>(this)->lookup(id));}
    void release(Entry& entry){
        auto& wave=entry.wave;
        for(auto& handle:wave.samples)if(handle){AIL_end_3D_sample(handle);AIL_release_3D_sample_handle(handle);handle=nullptr;}
        if(entry.allocationBase)AIL_mem_free_lock(entry.allocationBase);
        entry.allocationBase=nullptr;wave.data=nullptr;
        wave.kind=wave.active=0;
    }
    struct Pending {State& owner;Entry entry;explicit Pending(State& value):owner(value){}~Pending(){owner.release(entry);}};
    Entry& hit(std::uint32_t id,int& result){
        for(auto it=order.begin();it!=order.end();++it)if(entries[*it].key==id){
            unsigned slot=*it;order.splice(order.begin(),order,it);result=-1;return entries[slot];
        }
        unsigned slot=0;
        if(order.size()==64){slot=order.back();order.splice(order.begin(),order,--order.end());result=0;}
        else {while(entries[slot].used)++slot;order.push_front(slot);entries[slot]=Entry{};result=1;}
        entries[slot].used=true;entries[slot].key=id;return entries[slot];
    }
    bool load(const Definition& file,std::uint32_t loop,Entry& entry){
        auto& wave=entry.wave;
        // Miles returns one owned allocation: DWORD length followed by file bytes.
        LockedMemory input(AIL_file_read(file.file.c_str(),FILE_READ_WITH_SIZE));
        if(!input)return false;
        U32 bytes=0;std::memcpy(&bytes,input.get(),sizeof(bytes));
        if(bytes<12 || bytes>0x7fffffffu)return false;
        const void* payload=static_cast<unsigned char*>(input.get())+sizeof(bytes);
        const S32 type=AIL_file_type(payload,bytes);
        if(type==1){wave.data=const_cast<void*>(payload);entry.allocationBase=input.release();}
        else if(type==2 || type==13){
            void* decoded=nullptr;U32 size=0;S32 success=0;
            if(type==2){AILSOUNDINFO info={};if(!AIL_WAV_info(payload,&info))return false;success=AIL_decompress_ADPCM(&info,&decoded,&size);}
            else success=AIL_decompress_ASI(payload,bytes,file.file.c_str(),&decoded,&size,nullptr);
            LockedMemory output(decoded);
            if(!success || !output || size<12 || size>0x7fffffffu)return false;
            wave.data=output.get();entry.allocationBase=output.release();
        }else return false;
        wave.samples[0]=AIL_allocate_3D_sample_handle(provider);if(!wave.samples[0])return false;
        if(!AIL_set_3D_sample_file(wave.samples[0],wave.data))return false;
        AIL_set_3D_sample_distances(wave.samples[0],150,40);
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
    if(!stDigital||!manifest||!redist)return false;
    std::vector<Definition> files;
    try{if(!definitions(manifest,files))return false;}
    catch(const std::bad_alloc&){return false;}
    catch(const std::logic_error&){return false;}
    AIL_set_redist_directory(redist);
    HPROENUM cursor=HPROENUM_FIRST;HPROVIDER candidate=0,fast=0,creative=0;char* name=nullptr;
    while(AIL_enumerate_3D_providers(&cursor,&candidate,&name)){
        if(name && !_stricmp(name,"Creative Labs EAX 2 (TM)"))creative=candidate;
        if(name && !_stricmp(name,"Miles Fast 2D Positional Audio"))fast=candidate;
    }
    HPROVIDER provider=0;const char* selectedName=nullptr;
    if(creative&&AIL_open_3D_provider(creative)==M3D_NOERR){provider=creative;selectedName="Creative Labs EAX 2 (TM)";}
    else if(fast&&AIL_open_3D_provider(fast)==M3D_NOERR){provider=fast;selectedName="Miles Fast 2D Positional Audio";}
    else return false;
    H3DPOBJECT listener=AIL_open_3D_listener(provider);
    if(!listener){AIL_close_3D_provider(provider);return false;}
    std::string providerName;
    try{providerName=selectedName;}
    catch(const std::bad_alloc&){AIL_close_3D_listener(listener);AIL_close_3D_provider(provider);return false;}
    state->files.swap(files);state->providerName.swap(providerName);state->provider=provider;state->listener=listener;
    AIL_set_3D_position(state->listener,0,0,0);AIL_set_3D_orientation(state->listener,0,0,1,0,1,0);
    AIL_set_3D_room_type(state->provider,0);state->open=true;
    char debug[160];std::sprintf(debug,"RF455 TaggedAudio:ready:%u:%s",unsigned(state->files.size()),state->providerName.c_str());OutputDebugStringA(debug);
    return true;
}
void RF455TaggedAudio::Close(){
    if(state->open){
        for(unsigned slot:state->order)state->release(state->entries[slot]);
        AIL_close_3D_listener(state->listener);AIL_close_3D_provider(state->provider);
    }
    state->order.clear();for(auto& entry:state->entries)entry=Entry{};
    state->files.clear();state->provider=0;state->listener=nullptr;state->open=false;state->providerName.clear();
}
void RF455TaggedAudio::SetListener(const float* position){if(position)std::memcpy(state->position,position,12);}
void RF455TaggedAudio::Collect(){
    if(!state->open)return;
    bool empty=true; // 8BCD60 deliberately does not reset this for each entry.
    for(auto it=state->order.begin();it!=state->order.end();){
        auto& entry=state->entries[*it];auto& wave=entry.wave;
        for(auto& handle:wave.samples)if(handle){
            if(AIL_3D_sample_status(handle)==2&&wave.active){AIL_end_3D_sample(handle);AIL_release_3D_sample_handle(handle);handle=nullptr;}
            else if(handle)empty=false;
        }
        if(wave.data&&empty){if(entry.allocationBase)AIL_mem_free_lock(entry.allocationBase);entry.allocationBase=nullptr;wave.data=nullptr;wave.kind=wave.active=0;entry.used=false;it=state->order.erase(it);}
        else ++it;
    }
}
void RF455TaggedAudio::PlayAtListener(std::uint32_t id,std::uint32_t loop,std::uint32_t tag){Play(id,loop,tag,state->position);}
void RF455TaggedAudio::Play(std::uint32_t id,std::uint32_t loop,std::uint32_t tag,const float* position){
    if(!position||!GetR3State()->mSoundOn||!state->open)return;
    auto* file=state->find(id);if(!file)return;
    Collect();int hit=0;Entry* entry=state->lookup(id);
    State::Pending pending(*state);
    if(!entry){
        if(!IsExistFile(const_cast<char*>(file->file.c_str())))return;
        // Original retags an LRU victim before checking its stale tag. Preserve
        // this suppressed-play case without requiring one additional handle.
        if(tag && state->order.size()==64){
            const auto& victim=state->entries[state->order.back()].wave;
            for(auto existing:victim.tags)if(existing==tag){state->hit(id,hit);return;}
        }
        if(!state->load(*file,loop,pending.entry))return;
    }
    try{entry=&state->hit(id,hit);}catch(const std::bad_alloc&){return;}
    auto& wave=entry->wave;
    if(tag)for(auto existing:wave.tags)if(existing==tag)return;
    unsigned slot=0;
    if(hit!=-1){
        if(hit==0)state->release(*entry);
        // Keep stale tags beyond slot0, as in the measured eviction behavior.
        std::memcpy(pending.entry.wave.tags,wave.tags,sizeof(wave.tags));
        wave=pending.entry.wave;entry->allocationBase=pending.entry.allocationBase;
        pending.entry.wave=Wave{};pending.entry.allocationBase=nullptr;
        file->loop=static_cast<unsigned char>(loop);wave.tags[0]=tag;
    }else{
        if(!wave.data)return;
        bool found=false;
        for(unsigned n=0;n<30;++n)if(!wave.samples[n]||AIL_3D_sample_status(wave.samples[n])==2){slot=n;found=true;break;}
        if(!found)slot=0;
        const H3DSAMPLE candidate=AIL_allocate_3D_sample_handle(state->provider);if(!candidate)return;
        if(!AIL_set_3D_sample_file(candidate,wave.data)){
            AIL_release_3D_sample_handle(candidate);return;
        }
        if(wave.samples[slot])AIL_release_3D_sample_handle(wave.samples[slot]);
        wave.samples[slot]=candidate;
        wave.tags[slot]=tag;
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
    for(unsigned n=0;n<30;++n)if(entry->wave.tags[n]==tag){if(entry->wave.samples[n])AIL_end_3D_sample(entry->wave.samples[n]);return;}
}
RF455TaggedWaveView RF455TaggedAudio::Inspect(std::uint32_t id,unsigned slot)const{
    RF455TaggedWaveView out;out.cacheEntries=unsigned(state->order.size());out.manifestRecords=unsigned(state->files.size());
    const auto* entry=state->lookup(id);if(!entry)return out;if(slot>=30)throw std::out_of_range("455 wave slot");
    out.present=true;out.slots=30;out.sample=entry->wave.samples[slot];out.data=entry->wave.data;out.tag=entry->wave.tags[slot];out.kind=entry->wave.kind;out.active=entry->wave.active;
    out.waveID=entry->wave.id;
    std::memcpy(out.relative,entry->wave.relative,12);return out;
}
