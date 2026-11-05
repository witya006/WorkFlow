#include "client455_animation_manager.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <map>
#include <vector>

static unsigned managerChecks=0;
#define AM_CHECK(condition) do{++managerChecks;if(!(condition)){std::fprintf(stderr,"Animation manager check%u line%d\n",managerChecks,__LINE__);return 1;}}while(0)
template<class T>static T amRead(const void* bytes,unsigned at){T result;std::memcpy(&result,static_cast<const unsigned char*>(bytes)+at,sizeof(result));return result;}
template<class T>static void amWrite(void* bytes,unsigned at,T value){std::memcpy(static_cast<unsigned char*>(bytes)+at,&value,sizeof(value));}
namespace {
struct Memory {
    RF455AnimationMemoryOps real=RF455_CrtAnimationMemoryOps();
    std::map<void*,unsigned> live;
    std::vector<unsigned> freed;
    unsigned calls=0,failAt=0;
    bool bad=false;
    ~Memory(){for(const auto& item:live)real.memory.release(real.memory.context,item.first);}
    static void* __cdecl allocate(void* raw,std::size_t bytes){
        auto& self=*static_cast<Memory*>(raw);if(++self.calls==self.failAt)return nullptr;
        void* result=self.real.memory.allocate(self.real.memory.context,bytes);
        if(result){self.live[result]=0;std::memset(result,0xa5,bytes);}return result;
    }
    static void __cdecl release(void* raw,void* value){
        auto& self=*static_cast<Memory*>(raw);const auto found=self.live.find(value);
        if(found==self.live.end()){self.bad=true;return;}
        self.freed.push_back(found->second);self.live.erase(found);self.real.memory.release(self.real.memory.context,value);
    }
    static std::size_t __cdecl extent(void* raw,const void* value){
        auto& self=*static_cast<Memory*>(raw);if(!self.live.count(const_cast<void*>(value))){self.bad=true;return 0;}
        return self.real.extent(self.real.memory.context,value);
    }
    RF455MeshMemoryOps ops(){return {this,allocate,release};}
    void* tagged(unsigned bytes,unsigned tag){void* result=allocate(this,bytes);if(result)live[result]=tag;return result;}
};
void __cdecl log(void* raw,const char*){++*static_cast<unsigned*>(raw);}
void __cdecl wideLog(void*,const wchar_t*){}
int collection(){
    Memory memory;const auto ops=memory.ops();RF455AnimationManager manager;
    std::memset(&manager,0xa5,sizeof(manager));RF455_ConstructAnimationManager(&manager);
    unsigned char expected[4028];std::memset(expected,0xa5,sizeof(expected));
    amWrite(expected,0,&manager);std::memset(expected+8,0,16);amWrite<unsigned>(expected,24,1);std::memset(expected+28,0,4000);
    AM_CHECK(!std::memcmp(&manager,expected,sizeof(expected)));
    const unsigned capacities[]={1,2,3,4,6,6,9,9,9,13,13,13,13,19};
    RF455AnimationStorage* first=nullptr;
    for(unsigned i=0;i<14;++i){
        char name[64];std::snprintf(name,sizeof(name),"CLIPS\\WALK_%u.ANI",i);
        AM_CHECK(RF455_RegisterAnimation(&manager,name,&ops)==1);
        auto* record=RF455_FindAnimationName(&manager,name);AM_CHECK(record && amRead<unsigned>(record->bytes,264)==i+1);
        AM_CHECK(static_cast<unsigned>(manager.end-manager.begin)==i+1 && static_cast<unsigned>(manager.capacity-manager.begin)==capacities[i]);
        if(!i)first=record;
    }
    AM_CHECK(first && !std::strcmp(reinterpret_cast<const char*>(first->bytes+5),"clips\\walk_0.ani"));
    AM_CHECK(!RF455_RegisterAnimation(&manager,"clips\\walk_0.ani",&ops) && manager.nextId==15);
    AM_CHECK(RF455_GetOrRegisterAnimation(&manager,"Clips\\Walk_0.Ani",&ops)==first);
    AM_CHECK(RF455_FindAnimationIdByName(&manager,"CLIPS\\WALK_0.ANI")==1 && !RF455_FindAnimationIdByName(&manager,"missing"));
    AM_CHECK(RF455_FindAnimationSuffix(&manager,"\\WALK_0.ANI")==first && !RF455_FindAnimationSuffix(&manager,"WALK_0.ANI"));
    AM_CHECK(RF455_FindAnimationId(&manager,1)==first && RF455_FindAnimationId(&manager,999)==nullptr);
    RF455AnimationStorage* savedCache[1000];std::memcpy(savedCache,manager.cache,sizeof(savedCache));
    RF455_DeleteAnimationName(&manager,"CLIPS\\WALK_0.ANI",&ops);
    AM_CHECK(manager.end-manager.begin==13 && !RF455_FindAnimationName(&manager,"clips\\walk_0.ani"));
    AM_CHECK(!std::memcmp(savedCache,manager.cache,sizeof(savedCache))); // No dereference of freed cache values.
    RF455_ReleaseAnimationManager(&manager,&ops);
    AM_CHECK(!manager.begin && !manager.end && !manager.capacity && manager.nextId==15 && !std::memcmp(savedCache,manager.cache,sizeof(savedCache)));
    AM_CHECK(memory.live.empty() && !memory.bad);return 0;
}
int collisions(){
    Memory memory;const auto ops=memory.ops();RF455AnimationManager manager;RF455_ConstructAnimationManager(&manager);
    const unsigned ids[]={1,256,65536,16777216};RF455AnimationStorage* records[4];
    for(unsigned i=0;i<4;++i){char name[32];std::snprintf(name,sizeof(name),"collision%u.ani",i);manager.nextId=ids[i];AM_CHECK(RF455_RegisterAnimation(&manager,name,&ops));records[i]=manager.end[-1];AM_CHECK(RF455_FindAnimationId(&manager,ids[i])==records[i]);}
    // Instruction-derived keys for sum(bytes(id))==1: slots65,86,107.
    AM_CHECK(manager.cache[65]==records[3] && manager.cache[86]==records[1] && manager.cache[107]==records[2]);
    AM_CHECK(RF455_FindAnimationId(&manager,1)==records[0] && manager.cache[65]==records[0]);
    RF455_ResetAnimationCounters(&manager);AM_CHECK(manager.counter==0 && manager.nextId==1 && manager.end-manager.begin==4 && manager.cache[65]==records[0]);
    AM_CHECK(RF455_RegisterAnimation(&manager,"duplicate_id.ani",&ops));
    RF455_DeleteAnimationId(&manager,1,&ops);AM_CHECK(manager.end-manager.begin==3 && !RF455_FindAnimationName(&manager,"collision0.ani") && !RF455_FindAnimationName(&manager,"duplicate_id.ani"));
    RF455_ReleaseAnimationManager(&manager,&ops);AM_CHECK(memory.live.empty() && !memory.bad);return 0;
}
int wrapAndFailures(){
    Memory memory;const auto ops=memory.ops();RF455AnimationManager manager;RF455_ConstructAnimationManager(&manager);
    manager.nextId=0xffffffff;AM_CHECK(RF455_RegisterAnimation(&manager,"last.ani",&ops));AM_CHECK(manager.nextId==0 && amRead<unsigned>(manager.begin[0]->bytes,264)==0xffffffff);
    AM_CHECK(RF455_RegisterAnimation(&manager,"",&ops));AM_CHECK(manager.nextId==1 && RF455_FindAnimationId(&manager,0)==manager.begin[1]);
    RF455_ReleaseAnimationManager(&manager,&ops);
    RF455_ConstructAnimationManager(&manager);const unsigned savedCalls=memory.calls;
    char longName[256];std::memset(longName,'x',255);longName[255]=0;
    AM_CHECK(!RF455_RegisterAnimation(&manager,nullptr,&ops) && !RF455_RegisterAnimation(&manager,"unsafe%s.ani",&ops) && !RF455_RegisterAnimation(&manager,longName,&ops) && memory.calls==savedCalls);
    memory.failAt=memory.calls+1;AM_CHECK(!RF455_RegisterAnimation(&manager,"oom1.ani",&ops) && manager.nextId==1);
    memory.failAt=memory.calls+2;AM_CHECK(!RF455_RegisterAnimation(&manager,"oom2.ani",&ops) && !manager.begin && memory.live.empty());
    memory.failAt=0;AM_CHECK(!RF455_GetOrRegisterAnimation(&manager,nullptr,&ops));RF455_ReleaseAnimationManager(&manager,&ops);
    AM_CHECK(memory.live.empty() && !memory.bad);return 0;
}
int ownersAndFile(unsigned expectedBytes,unsigned expectedMax){
    Memory memory;const auto ops=memory.ops();RF455AnimationManager manager;RF455_ConstructAnimationManager(&manager);
    auto* record=RF455_GetOrRegisterAnimation(&manager,"owned.ani",&ops);AM_CHECK(record);
    void* raw=memory.tagged(32,1);auto* cookie=static_cast<unsigned char*>(memory.tagged(36,2));void* extra=memory.tagged(16,3);AM_CHECK(raw && cookie && extra);
    amWrite(record->bytes,268,raw);amWrite(record->bytes,272,cookie+4);amWrite(record->bytes,280,extra);memory.live[record]=4;memory.freed.clear();
    RF455_DeleteAnimationId(&manager,1,&ops);AM_CHECK(memory.freed==std::vector<unsigned>({1,2,3,4}));
    RF455_ReleaseAnimationManager(&manager,&ops);AM_CHECK(memory.live.empty());RF455_ConstructAnimationManager(&manager);
    record=RF455_GetOrRegisterAnimation(&manager,".\\clips\\real.ani",&ops);AM_CHECK(record);
    unsigned imported=0,logs=0;RF455AnimationContext context={{{&memory,Memory::allocate,Memory::release},Memory::extent},{&logs,log,wideLog},&imported};
    AM_CHECK(RF455_LoadAnimation(record,1,&context));AM_CHECK(amRead<unsigned>(record->bytes,0)==1 && record->bytes[4]==1 && amRead<void*>(record->bytes,268) && amRead<unsigned>(record->bytes,276)==expectedMax && imported==expectedBytes);
    AM_CHECK(RF455_FindAnimationId(&manager,1)==record && RF455_LoadAnimation(record,0,&context) && imported==expectedBytes && !logs);
    auto* missing=RF455_GetOrRegisterAnimation(&manager,".\\clips\\missing.ani",&ops);AM_CHECK(missing && !RF455_LoadAnimation(missing,1,&context) && missing->bytes[4]==1 && !amRead<unsigned>(missing->bytes,0));
    AM_CHECK(RF455_LoadAnimation(missing,1,&context) && !amRead<unsigned>(missing->bytes,0) && !amRead<void*>(missing->bytes,268) && logs==1);
    RF455_ReleaseAnimationManager(&manager,&ops);AM_CHECK(memory.live.empty() && !memory.bad);return 0;
}
}
extern "C" int RF455_RunAnimationManagerChecks(const char* output,unsigned expectedBytes,unsigned expectedMax){
    managerChecks=0;if(collection() || collisions() || wrapAndFailures() || ownersAndFile(expectedBytes,expectedMax))return 229;
    FILE* file=std::fopen(output,"wb");if(!file)return 230;
    std::fprintf(file,"{\"status\":\"PASS\",\"checks\":%u,\"groups\":4,\"real_ani_files\":1,\"owned_heap_balance\":0}\n",managerChecks);std::fclose(file);return 0;
}
#ifndef RF455_ANIMATION_MANAGER_EMBEDDED
int main(int argc,char** argv){return argc==4?RF455_RunAnimationManagerChecks(argv[1],static_cast<unsigned>(std::strtoul(argv[2],nullptr,10)),static_cast<unsigned>(std::strtoul(argv[3],nullptr,10))):231;}
#endif
