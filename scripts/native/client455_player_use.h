#pragma once
#ifndef RF455_PLAYER_USE_H
#define RF455_PLAYER_USE_H
#include <cstdint>
#include <stdexcept>

// Selected lane only:475E10→417140 writes DWORD4 of the CPlayer+17848
// record toFFFFFFFF. No reference decrement, wrapper Clear or full620byte
// item copy occurs. The constructor/other lanes/producers remain unaccepted.
struct RF455PlayerUse {
    std::uint32_t field4=0;
    bool field4Known=false;
    void clear(){field4=0xffffffff;field4Known=true;}
    std::uint32_t get()const{if(!field4Known)throw std::logic_error("455 player use field4 has no confirmed producer");return field4;}
};
#endif
