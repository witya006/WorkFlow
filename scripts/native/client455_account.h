#pragma once
#include <cstddef>
#include <cstdint>

struct RF455AccountHandshake {
    std::uint8_t delta=0;
    std::uint16_t mask=0;
    std::uint8_t serverType=0; // Target setter5F0FE0;ini provider is still separate.
    std::uint32_t selectedWorld=0xffffffff;
    std::int32_t zoneRequestMode=-1; // Target436232;writers still require migration.
};
struct RF455WorldInfo {
    union {std::int32_t value;std::int32_t m_bIsOpen;};
    char m_pName[64];
    std::uint8_t status,padding[3];
};
static_assert(sizeof(RF455WorldInfo)==72,"455 world record stride");
constexpr std::size_t RF455WorldCapacity=300;
constexpr std::size_t RF455LoginBytes=342;

bool RF455_ReadAccountSeed(RF455AccountHandshake&,const void*,std::size_t);
void RF455_PackCredentials(std::uint8_t (&)[84],const char*,const char*);
// mode2 bypass is a confirmed target branch;its runtime provider is not ported.
bool RF455_PackLogin(std::uint8_t (&)[RF455LoginBytes],const RF455AccountHandshake&,
                    const char* id,const char* password,bool ticketProfile,
                    const char* ticket,bool mode2=false);
// Validate the whole bounded record stream before changing caller state.
// Retain bytes after each declared name span,as the original does on reload.
bool RF455_ReadWorldList(const void*,std::size_t,RF455WorldInfo*,std::size_t,
                        std::uint8_t& result,std::uint32_t& count);
