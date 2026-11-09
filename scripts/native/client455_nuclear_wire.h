#pragma once
#include <array>
#include <cstddef>
#include <cstdint>

// Source values, not an overlay of packed packet14 or private map/record32.
struct RF455NuclearWireEntry {
    std::uint8_t race=0,index=0;
    std::array<float,3> position{};
};
struct RF455NuclearWireMessage {
    std::uint8_t opcode=0,result=0,race=0,index=0,count=0;
    std::array<float,3> position{};
    std::array<RF455NuclearWireEntry,9> entries{};
    bool ignoredList=false;
};
// Target handlers assume valid input. This own boundary rejects short/null data,
// leaves output unchanged on failure, and permits unused trailing packet bytes.
bool RF455_ReadNuclearPayload(std::uint8_t opcode,const void* payload,std::size_t bytes,
                            RF455NuclearWireMessage& output);
