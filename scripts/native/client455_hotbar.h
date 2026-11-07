#pragma once
#include <array>
#include <cstdint>
#include <vector>

using RF455HotbarSnapshot=std::array<std::uint32_t,50>;
constexpr std::uint32_t RF455_EMPTY_HOTBAR_REFERENCE=0xffffffff;
std::uint32_t RF455_EncodeHotbarReference(std::uint8_t kind,std::uint8_t sfType,
                                        std::uint32_t tableIndex,std::uint32_t serial);

// Upload metadata of CGUILinkWindow5004E0. These fields do not implement its
// missing visual layout,bank controls or input actions.
struct RF455HotbarWindowState {
    std::uint8_t active=255;
    std::array<std::int32_t,5> bankFlags{};
    void initialized(){active=0;bankFlags.fill(1);}
    std::uint8_t packed()const;
};

class RF455HotbarDelta {
    RF455HotbarSnapshot previous;
    std::uint8_t previousState=255;
public:
    RF455HotbarDelta(){previous.fill(RF455_EMPTY_HOTBAR_REFERENCE);}
    void reset(const RF455HotbarSnapshot& snapshot){previous=snapshot;}
    // The target updates caches BEFORE send,including transport failure. A
    // dragged Linker reference suppresses all differences matching its old key.
    std::vector<std::uint8_t> prepare(const RF455HotbarSnapshot&,std::uint8_t state,
                                     bool hoverPresent,std::uint8_t originBoard,
                                     std::uint32_t hoverReference);
};
inline bool RF455_HotbarUploadDue(std::uint32_t now,std::uint32_t last){return now-last>5000;}
