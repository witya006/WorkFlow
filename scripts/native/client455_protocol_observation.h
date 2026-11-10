#pragma once
#include <windows.h>
#include <cstdio>

// Opt-in own-client diagnostics. Never pass account data, keys or payloads.
inline void RF455_ObserveProtocol(const char* event,unsigned category,unsigned kind,unsigned bytes){
    char enabled[2]={};
    if(GetEnvironmentVariableA("RF455_OBSERVE_PROTOCOL",enabled,sizeof(enabled))!=1||enabled[0]!='1')return;
    char text[128];
    std::sprintf(text,"RF455 Protocol:%s:%u:%u:%u",event,category,kind,bytes);
    OutputDebugStringA(text);
}
