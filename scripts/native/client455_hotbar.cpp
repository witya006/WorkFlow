#include "client455_hotbar.h"

std::uint32_t RF455_EncodeHotbarReference(std::uint8_t kind,std::uint8_t sfType,
                                        std::uint32_t tableIndex,std::uint32_t serial){
    std::uint32_t tag;
    switch(kind){case 0:tag=4;break;case 1:tag=sfType;break;case 2:tag=3;break;
        case 6:tag=5;break;case 7:tag=6;break;default:return RF455_EMPTY_HOTBAR_REFERENCE;}
    // Target5003C0 ORs without masking the index;58BB90 later writes only WORD.
    return (tag<<24)|(kind==0?serial:tableIndex);
}
std::uint8_t RF455HotbarWindowState::packed()const{
    std::uint32_t value=active;
    for(unsigned i=0;i<5;++i)value|=std::uint32_t(bankFlags[i])<<(7-i);
    return static_cast<std::uint8_t>(value);
}
std::vector<std::uint8_t> RF455HotbarDelta::prepare(const RF455HotbarSnapshot& current,
        std::uint8_t state,bool hoverPresent,std::uint8_t originBoard,std::uint32_t hoverReference){
    std::vector<std::uint8_t> packet{state,0};packet.reserve(202);
    for(unsigned i=0;i<50;++i){
        if(current[i]==previous[i])continue;
        if(hoverPresent&&originBoard==6&&hoverReference==previous[i])continue;
        const auto key=current[i];packet.push_back(static_cast<std::uint8_t>(i));
        packet.push_back(static_cast<std::uint8_t>(key>>24));
        packet.push_back(static_cast<std::uint8_t>(key));
        packet.push_back(static_cast<std::uint8_t>(key>>8));
        ++packet[1];previous[i]=key;
    }
    if(!packet[1]&&state==previousState)return {};
    previousState=state;return packet;
}
