#pragma once
#ifndef RF455_NUCLEAR_REGISTRY_H
#define RF455_NUCLEAR_REGISTRY_H
#include "client455_nuclear_aiming.h"
#include <cstddef>
#include <map>
#include <memory>

// The observed record really allocates32 bytes. Its DWORD12 has no confirmed
// initializer/producer: leave those bytes untouched and never read them here.
struct RF455NuclearRecord {
    DWORD launch,impact,radar,reserved12;
    float position[3];
    DWORD countdown;
    RF455NuclearRecord()noexcept:launch(0),impact(0),radar(0),position{},countdown(0){}
    RF455NuclearRecord(const RF455NuclearRecord&)=delete;
    RF455NuclearRecord& operator=(const RF455NuclearRecord&)=delete;
};
static_assert(sizeof(RF455NuclearRecord)==32&&offsetof(RF455NuclearRecord,position)==16&&offsetof(RF455NuclearRecord,countdown)==28,"455 observed record32 lanes");

// Shared process clock, not a timer per record or container. Caller order is
// observable: a due first record consumes the tick before later records.
struct RF455NuclearCountdownClock {
    bool initialized=false;
    DWORD last=0;
    template<class Clock,class Emit>void Tick(DWORD& count,Clock clock,Emit emit){
        if(static_cast<LONG>(count)<=0)return;
        if(!initialized){initialized=true;last=clock();}
        const DWORD now=clock();
        if(now-last>=1000){
            last=now;--count;
            if(static_cast<LONG>(count)<0)count=0;
            emit(count+1);
        }
    }
};

// Own modern map implementation; the target's private STL ABI is not reused.
class RF455NuclearContainer {
    std::map<WORD,std::unique_ptr<RF455NuclearRecord>> records;
    RF455NuclearAiming aiming;
    RF455NuclearRecord* FindMutable(BYTE race,BYTE index);
public:
    RF455NuclearContainer()=default;
    ~RF455NuclearContainer();
    RF455NuclearContainer(const RF455NuclearContainer&)=delete;
    RF455NuclearContainer& operator=(const RF455NuclearContainer&)=delete;
    RF455NuclearAiming& Aiming(){return aiming;}
    const RF455NuclearRecord* Find(BYTE race,BYTE index)const;
    const float* Position(BYTE race,BYTE index)const;
    std::size_t Size()const{return records.size();}
    BOOL Add(BYTE race,BYTE index);
    BOOL Remove(BYTE race,BYTE index);
    BOOL ClearAll();
    BOOL ResetRecords();
    BOOL SetPosition(BYTE race,BYTE index,const float*);
    BOOL Launch(BYTE race,BYTE index);
    BOOL Impact(BYTE race,BYTE index);
    BOOL Radar(BYTE race,BYTE index,BOOL on);
    BOOL NotifyRace(BYTE race,BYTE index);
    BOOL SetCountdown(BYTE race,BYTE index,DWORD value);
    void FrameMove();
};
RF455NuclearContainer& RF455_NuclearContainer();
RF455NuclearContainer* RF455_GetNuclearContainer();
void RF455_BindNuclearContainer(RF455NuclearContainer*);
void RF455_UnbindNuclearContainer(RF455NuclearContainer*);
#endif
