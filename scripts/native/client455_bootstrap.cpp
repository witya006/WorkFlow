#include "client455_bootstrap.h"
#include "client455_nation_paths.h"
#include "client455_language.h"
#include <windows.h>
#include <tlhelp32.h>
#include <mbstring.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
namespace{
RF455BootstrapSettings settings;
struct InstanceHandles{std::vector<HANDLE>values;~InstanceHandles(){for(auto h:values)CloseHandle(h);}};
InstanceHandles&handles(){static InstanceHandles value;return value;}
}
const RF455BootstrapSettings*RF455_GetBootstrapSettings(){return &settings;}
void RF455_LoadBootstrapSettings(){
    char path[260],value[32]={};std::sprintf(path,"%s/FG_CB.ini",RF455_GetClientDataRoot());
    GetPrivateProfileStringA("SETTING","USEFG","0",value,4,path);
    settings.useFG=std::atol(value);char message[64];std::sprintf(message,"RF455 FG:%ld",static_cast<long>(settings.useFG));OutputDebugStringA(message);
}
bool RF455_InstancePolicyBypassed(unsigned nation){return nation==2||nation==3||nation==7||nation==8;}
bool RF455_ExecutableNameMatches(const char*path){
    if(!path)return false;char drive[4]={},directory[256]={},name[256]={},extension[256]={},file[128]={};
    if(_splitpath_s(path,drive,sizeof(drive),directory,sizeof(directory),name,sizeof(name),extension,sizeof(extension)))return false;
    if(std::strlen(name)+std::strlen(extension)>=sizeof(file))return false;
    std::sprintf(file,"%s%s",name,extension);_mbsupr(reinterpret_cast<unsigned char*>(file));
    return std::strlen(file)==13&&!_mbscmp(reinterpret_cast<unsigned char*>(file),reinterpret_cast<const unsigned char*>("RF_ONLINE.BIN"));
}
unsigned RF455_CountClientProcesses(){
    unsigned count=0;HANDLE snapshot=CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS,0);PROCESSENTRY32 entry={};entry.dwSize=sizeof(entry);
    if(Process32First(snapshot,&entry))do{if(RF455_ExecutableNameMatches(entry.szExeFile))++count;}while(Process32Next(snapshot,&entry));
    if(snapshot!=INVALID_HANDLE_VALUE)CloseHandle(snapshot);return count;
}
RF455InstanceResult RF455_CheckSingleInstance(){
    char path[260]={};if(!GetModuleFileNameA(nullptr,path,sizeof(path))||!RF455_ExecutableNameMatches(path))return RF455InstanceResult::WrongFilename;
    if(RF455_CountClientProcesses()>1)return RF455InstanceResult::TooManyProcesses;
    HANDLE mutex=CreateMutexA(nullptr,TRUE,"Global\\_R_F_is_execute_");
    if(mutex){const bool existed=GetLastError()==ERROR_ALREADY_EXISTS;ReleaseMutex(mutex);handles().values.push_back(mutex);if(existed)return RF455InstanceResult::ExistingMutex;}
    // The target accepts CreateMutex failure,provided name/process checks pass.
    return RF455InstanceResult::Accepted;
}
bool RF455_CheckStartupInstance(){
    if(RF455_InstancePolicyBypassed(RF455_GetNormalNationPaths()->nation)){OutputDebugStringA("RF455 Instance:country-skip");return true;}
    const auto result=RF455_CheckSingleInstance();if(result==RF455InstanceResult::Accepted){OutputDebugStringA("RF455 Instance:accepted");return true;}
    unsigned message=0xbf5,title=0xbf6;if(result==RF455InstanceResult::TooManyProcesses){message=0xbf7;title=0xbf8;}else if(result==RF455InstanceResult::ExistingMutex){message=0xbf9;title=0xbf8;}
    const auto*pack=RF455_GetNormalLanguagePack();MessageBoxA(nullptr,pack->get(message),pack->get(title),0);return false;
}
