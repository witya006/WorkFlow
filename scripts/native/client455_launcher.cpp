#include <winsock2.h>
#include <windows.h>
#include "client455_launcher.h"
#include "client455_nation_paths.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
namespace {
RF455LauncherConnection normal;
std::uint32_t word32(const unsigned char*p){std::uint32_t v;std::memcpy(&v,p,4);return v;}
std::uint16_t word16(const unsigned char*p){std::uint16_t v;std::memcpy(&v,p,2);return v;}
}
void RF455_CopyLauncherText(char*out,const char*text,std::size_t capacity){
    if(!out||!text||!capacity)return;
    std::size_t n=0;while(n+1<capacity&&text[n])++n;
    std::memset(out,0,capacity);std::memcpy(out,text,n);
}
bool RF455_DecodeCcrLauncher(const void*data,std::size_t size,unsigned nation,RF455LauncherConnection&out){
    unsigned char raw[93]={};if(data)std::memcpy(raw,data,size<93?size:93);
    RF455LauncherConnection value;value.endpoint=1;value.hasAccountFields=true;
    value.address=word32(raw)^0xcb9c4b3a;value.port=word16(raw+4)^0x4fb6;
    // The target setter copies at most50bytes into51;bound the read to the
    // record's identifier instead of reproducing an out-of-bounds strlen.
    char identifier[52]={};std::memcpy(identifier,raw+6,51);RF455_CopyLauncherText(value.identifier,identifier,51);
    value.account=word32(raw+57)^0x6e65e0af;
    const std::uint32_t mask[]={0xcfcf22e6,0x5bbcde6f,0xacdf5eda,0xbccd1b37};
    for(unsigned i=0;i<4;++i)value.keys[i]=word32(raw+61+i*4)^mask[i];
    value.worldIndex=word16(raw+77)^0x4b3a;
    value.personalReference=word32(raw+79)^0xc89c183a;
    value.premium=0; // 455 overwrites the serialized83..86 field before use.
    value.modeValue=word32(raw+87)^0xd29c283b;value.nation=word16(raw+91)^0x32d7;
    value.accepted=value.nation==nation;
    if(value.accepted)value.personal=value.personalReference==value.account;
    out=value;return value.accepted;
}
bool RF455_LoadCcrLauncher(const char*path,unsigned nation,RF455LauncherConnection&out){
    unsigned char raw[93]={};DWORD read=0;HANDLE file=CreateFileA(path,GENERIC_READ,0,nullptr,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,nullptr);
    const bool opened=file!=INVALID_HANDLE_VALUE;const bool ok=ReadFile(file,raw,sizeof(raw),&read,nullptr)!=FALSE;
    CloseHandle(file);const bool accepted=RF455_DecodeCcrLauncher(raw,sizeof(raw),nation,out);
    out.opened=opened;out.readSucceeded=ok;out.bytesRead=ok?read:0;return accepted;
}
bool RF455_LoadArgumentLauncher(int argc,const char*const*argv,RF455LauncherConnection&out){
    if(argc!=5||!argv||!argv[1]||!argv[2]||!argv[3]||!argv[4])return false;
    RF455LauncherConnection value;value.kind=RF455LauncherKind::ArgumentVector;value.endpoint=0;
    value.address=inet_addr(argv[1]);value.port=static_cast<std::uint16_t>(std::atol(argv[2]));
    RF455_CopyLauncherText(value.identifier,argv[3],51);RF455_CopyLauncherText(value.password,argv[4],33);
    value.hasPassword=true;value.accepted=true;out=value;return true;
}
const RF455LauncherConnection*RF455_GetLauncherConnection(){return &normal;}
bool RF455_InitializeLauncher(){
    const auto*paths=RF455_GetNormalNationPaths();if(!paths->configured)return false;
    const bool args=paths->nation==3||paths->nation==7;
    const bool ok=args?RF455_LoadArgumentLauncher(__argc,__argv,normal):RF455_LoadCcrLauncher(".\\System\\DefaultSet.tmp",paths->nation,normal);
    if(ok){char message[80];std::sprintf(message,"RF455 Launcher:%s:%u",args?"argv":"ccr",normal.endpoint);OutputDebugStringA(message);}
    return ok;
}
