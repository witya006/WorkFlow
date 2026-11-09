#pragma once
#ifndef RF455_CHARACTER_FLAGS_H
#define RF455_CHARACTER_FLAGS_H
#include <cstdint>
#include <stdexcept>

// Source owner for Character DWORD640. The related movement-controller clock is
// represented explicitly; full movement-controller frame/lifetime remains open.
struct RF455CharacterFlags {
    using Clock=std::uint32_t(*)();
    std::uint32_t value=0,touchedAt=0;
    bool touchedKnown=false;
    bool any(std::uint32_t mask)const{return (value&mask)!=0;}
    bool none(std::uint32_t mask)const{return (value&mask)==0;}
    bool blocked(std::uint32_t action)const{return (action>>28)==5||any(3);}
    void enable(std::uint32_t mask,Clock clock){
        if(mask&1){if(!clock)throw std::logic_error("455 Character flag1 requires the actual clock");touchedAt=clock();touchedKnown=true;}
        value|=mask;
    }
    void disable(std::uint32_t mask){value&=~mask;}
    void toggle(std::uint32_t mask,bool on,Clock clock){if(on)enable(mask,clock);else disable(mask);}
    template<class GetAction,class SetAction>
    bool applyServer(std::uint64_t flags,GetAction action,SetAction change,Clock clock){
        if(!(flags&(std::uint64_t(1)<<5)))disable(1);
        if(!(flags&(std::uint64_t(1)<<19))){
            if(any(2)&&none(1)&&(action()>>28)==5)change(0x10000000, false);
            disable(2);
        }
        const bool wasBlocked=blocked(action());
        if(flags&(std::uint64_t(1)<<5)){
            if(!wasBlocked)change(0x50000001,false);
        }else if(!wasBlocked){
            if(flags&(std::uint64_t(1)<<19)){
                enable(2,clock);
                if((action()>>28)!=5)change(0x50000001,false);
            }else{
                disable(2);
                if((action()>>28)==5)change(0x10000000,false);
            }
        }
        toggle(0x20000,!(flags&(std::uint64_t(1)<<14)),clock);
        toggle(0x40000,!(flags&(std::uint64_t(1)<<15)),clock);
        return wasBlocked;
    }
};
#endif
