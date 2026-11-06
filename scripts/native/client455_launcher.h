#pragma once
#include <cstddef>
#include <cstdint>

enum class RF455LauncherKind{CcrFile,ArgumentVector};
struct RF455LauncherConnection{
    RF455LauncherKind kind=RF455LauncherKind::CcrFile;
    unsigned endpoint=1;
    std::uint32_t address=0,account=0,keys[4]={},personalReference=0,premium=0,modeValue=0;
    std::uint16_t port=0,worldIndex=0,nation=0xffff;
    char identifier[51]={},password[33]={};
    bool accepted=false,hasAccountFields=false,hasPassword=false,personal=false;
    bool opened=false,readSucceeded=false;unsigned bytesRead=0;
};
void RF455_CopyLauncherText(char*,const char*,std::size_t);
bool RF455_DecodeCcrLauncher(const void*,std::size_t,unsigned,RF455LauncherConnection&);
bool RF455_LoadCcrLauncher(const char*,unsigned,RF455LauncherConnection&);
bool RF455_LoadArgumentLauncher(int,const char*const*,RF455LauncherConnection&);
bool RF455_InitializeLauncher();
const RF455LauncherConnection*RF455_GetLauncherConnection();
