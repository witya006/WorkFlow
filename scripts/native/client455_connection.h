#pragma once
#include <cstdint>
struct RF455ConnectionWait {
    void* context;
    std::uint32_t (*clock)(void*);
    void (*pump)(void*);
    bool (*connected)(void*);
    void (*sleep)(void*,std::uint32_t);
};
enum class RF455ConnectionOutcome {NotAttempted,Connected,TransportError,Timeout};
struct RF455ConnectionReport {
    RF455ConnectionOutcome outcome=RF455ConnectionOutcome::NotAttempted;
    std::uint32_t timeoutMs=0,waitIterations=0;
    int rawResult=0,detailError=0;
};
std::uint32_t RF455_ReadConnectTimeout();
bool RF455_WaitForConnection(const RF455ConnectionWait&,std::uint32_t timeout,std::uint32_t& iterations);
bool RF455_AcceptDelayElapsed(std::uint32_t now,std::uint32_t connectedAt);
RF455ConnectionReport* RF455_GetConnectionReport();
