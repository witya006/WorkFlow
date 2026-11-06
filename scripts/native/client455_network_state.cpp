#include "client455_network_state.h"
int RF455_AttemptConnect(RF455NetworkState&state,unsigned endpoint,unsigned process,bool logout,
    std::uint32_t address,std::uint16_t port,RF455ConnectTransport transport,RF455ConnectAccepted accepted,void*context){
    if(endpoint>=4||process>=6||(!transport)||(!accepted))return 10022; // bounded ownAPI domain
    const unsigned active=state.active[process];if(active!=255){if(active>=4)return 10022;if(state.connected[active])return -1;}
    if(endpoint==2||logout){state.active[process]=static_cast<std::uint8_t>(endpoint);accepted(context);return 0;}
    const int result=transport(context,process,address,port);
    if(!result)state.active[process]=static_cast<std::uint8_t>(endpoint);else state.connected[endpoint]=0;
    return result;
}
