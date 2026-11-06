#include "client455_connection.h"
#include <windows.h>
namespace { RF455ConnectionReport report; }
RF455ConnectionReport* RF455_GetConnectionReport(){return &report;}
std::uint32_t RF455_ReadConnectTimeout(){
    return static_cast<std::uint32_t>(GetPrivateProfileIntA("Network","ConnectTime",90,"./DataTable/ClientSystem.ini"))*1000u;
}
bool RF455_AcceptDelayElapsed(std::uint32_t now,std::uint32_t connectedAt){return now-connectedAt>1000u;}
bool RF455_WaitForConnection(const RF455ConnectionWait& api,std::uint32_t timeout,std::uint32_t& iterations){
    iterations=0;const auto begin=api.clock(api.context);
    for(;;){
        const auto now=api.clock(api.context);api.pump(api.context);++iterations;
        if(api.connected(api.context))return true;
        if(now-begin>timeout)return false;
        api.sleep(api.context,4);
    }
}
