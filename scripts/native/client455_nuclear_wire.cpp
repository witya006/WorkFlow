#include "client455_nuclear_wire.h"
#include <cstring>

bool RF455_ReadNuclearPayload(std::uint8_t opcode,const void* payload,std::size_t bytes,
                            RF455NuclearWireMessage& output){
    const auto* p=static_cast<const std::uint8_t*>(payload);
    if(!p)return false;
    RF455NuclearWireMessage value;value.opcode=opcode;
    switch(opcode){
    case 0:
        if(bytes<1)return false;value.result=p[0];break;
    case 3:
        if(bytes<17)return false;
        std::memcpy(value.position.data(),p+4,12);value.index=p[16];break;
    case 4:case 6:case 8:case 9:
        if(bytes<2)return false;value.race=p[0];value.index=p[1];break;
    case 5:
        if(bytes<5)return false;value.race=p[0];value.index=p[4];break;
    case 7:
        if(bytes<14)return false;
        value.race=p[0];value.index=p[1];std::memcpy(value.position.data(),p+2,12);break;
    case 10:
        if(bytes<1)return false;value.count=p[0];
        if(value.count>9){value.ignoredList=true;break;}
        if(bytes<1+std::size_t(value.count)*14)return false;
        for(std::size_t i=0;i<value.count;++i){
            const auto* row=p+1+14*i;auto& entry=value.entries[i];
            entry.race=row[0];entry.index=row[1];std::memcpy(entry.position.data(),row+2,12);
        }
        break;
    default:return false;
    }
    output=value;return true;
}
