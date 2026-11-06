#pragma once
#include <cstdint>
struct RF455NetworkState{
    std::uint8_t active[6]={255,255,255,255,255,255};
    std::uint32_t connected[4]={};
};
using RF455ConnectTransport=int(*)(void*,unsigned,std::uint32_t,std::uint16_t);
using RF455ConnectAccepted=void(*)(void*);
// Only the transport/state contract,not authentication or packet acceptance.
int RF455_AttemptConnect(RF455NetworkState&,unsigned endpoint,unsigned process,bool logout,
    std::uint32_t address,std::uint16_t port,RF455ConnectTransport,RF455ConnectAccepted,void*);
