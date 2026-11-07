#pragma once
#include <cstdint>
#include <stdexcept>

// Own semantic state for CPlayer+0x452c, not the target's private class ABI.
// 455's CPlayer constructor does not initialize that DWORD. Keep the unknown
// domain explicit until a confirmed setter/flags producer supplies a value.
struct RF455PlayerStatus {
    std::uint32_t code=0;
    bool known=false;
    void set(std::uint32_t value){code=value;known=true;}
    std::uint32_t get()const{
        if(!known)throw std::logic_error("455 player status is uninitialized before its first producer");
        return code;
    }
    void apply(std::uint64_t flags){
        if(flags&(std::uint64_t(1)<<16)){set(10);return;}
        if(flags&(std::uint64_t(1)<<17)){
            for(unsigned bit=33;bit<=40;++bit)
                if(flags&(std::uint64_t(1)<<bit)){set(bit-31);return;}
            return; // No subtype: 44DEE0 leaves the old DWORD untouched.
        }
        set(flags&(std::uint64_t(1)<<42)?1:0);
    }
};
inline bool RF455_RequiresHoverCancelStatus(std::uint32_t code){
    const auto low=static_cast<std::uint8_t>(code);
    return low==2||low==6||low==10;
}
// Reads the actual source avatar, with the target's null-avatar fast path.
bool RF455_AvatarRequiresHoverCancel();
