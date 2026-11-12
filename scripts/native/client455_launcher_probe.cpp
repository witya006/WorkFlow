#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "item/citemmgr.h"
#include "input/imeedit.h"
#include "baseheader.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "mainapp.h"
#include "client455_launcher.h"
#include "client455_nation_paths.h"
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>
extern CMainApp g_MainApp;
template<class Tag,typename Tag::Type Member>struct MemberAccess{friend typename Tag::Type access(Tag){return Member;}};
struct NetworkMember{using Type=CNetworkMgr CMainApp::*;friend Type access(NetworkMember);};
template struct MemberAccess<NetworkMember,&CMainApp::m_cNetworkMgr>;
#define REQUIRE(x) do{if(!(x)){std::fprintf(stderr,"Launcher failure line%d\n",__LINE__);return 1;}}while(0)
static unsigned checks=0;
int main(int argc, char**){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    REQUIRE(RF455_InitializeNationPaths());RF455LauncherConnection value;
    for(unsigned nation: {0u,1u,2u,4u,5u,6u,8u,9u,10u}){
        char path[80];std::sprintf(path,"ccr-%u.bin",nation);REQUIRE(RF455_LoadCcrLauncher(path,nation,value));
        REQUIRE(value.opened&&value.readSucceeded&&value.bytesRead==93&&value.endpoint==1&&!value.hasPassword&&value.hasAccountFields);
        REQUIRE(value.address==0x0100007f&&value.port==1&&value.account==17&&value.worldIndex==3&&value.premium==0&&value.modeValue==1&&value.personal&&value.nation==nation);
        REQUIRE(!std::strcmp(value.identifier,"fixture-user"));for(unsigned i=0;i<4;++i)REQUIRE(value.keys[i]==0x10203040+i);
        REQUIRE(!RF455_LoadCcrLauncher(path,(nation+1)%11,value));++checks;
    }
    REQUIRE(!RF455_LoadCcrLauncher("missing-file.bin",0,value)&&!value.opened&&!value.readSucceeded&&value.bytesRead==0);
    REQUIRE(RF455_LoadCcrLauncher("extra.bin",0,value)&&value.bytesRead==93&&value.premium==0);
    for(unsigned size:{0u,1u,4u,6u,56u,57u,60u,61u,76u,77u,78u,79u,82u,83u,86u,87u,90u,91u,92u}){char path[80];std::sprintf(path,"short-%u.bin",size);REQUIRE(!RF455_LoadCcrLauncher(path,0,value)&&value.opened&&value.readSucceeded&&value.bytesRead==size);++checks;}
    HANDLE held=CreateFileA("ccr-0.bin",GENERIC_READ,0,nullptr,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,nullptr);REQUIRE(held!=INVALID_HANDLE_VALUE);REQUIRE(!RF455_LoadCcrLauncher("ccr-0.bin",0,value)&&!value.opened);CloseHandle(held);
    const char*args[]={"own-fixture","127.0.0.1","1","fixture-user","fixture-value"};
    REQUIRE(RF455_LoadArgumentLauncher(5,args,value)&&value.endpoint==0&&value.hasPassword&&!value.hasAccountFields&&value.address==0x0100007f&&value.port==1);
    for(int count:{0,1,4,6})REQUIRE(!RF455_LoadArgumentLauncher(count,args,value));
    args[1]="invalid-address";args[2]="-1";REQUIRE(RF455_LoadArgumentLauncher(5,args,value)&&value.address==0xffffffff&&value.port==65535);
    args[2]="65536";REQUIRE(RF455_LoadArgumentLauncher(5,args,value)&&!value.port);args[2]="  +42tail";REQUIRE(RF455_LoadArgumentLauncher(5,args,value)&&value.port==42);
    const std::string longId(80,'i'),longPassword(80,'p');args[3]=longId.c_str();args[4]=longPassword.c_str();REQUIRE(RF455_LoadArgumentLauncher(5,args,value)&&std::strlen(value.identifier)==50&&std::strlen(value.password)==32);
    char preserved[5]="keep";RF455_CopyLauncherText(preserved,nullptr,5);REQUIRE(!std::strcmp(preserved,"keep"));RF455_CopyLauncherText(preserved,"longer",5);REQUIRE(!std::strcmp(preserved,"long"));
    auto&network=g_MainApp.*access(NetworkMember{});network.SetPassword(const_cast<char*>("retained"));
    const bool reject = GetFileAttributesA("reject-handoff") != INVALID_FILE_ATTRIBUTES;
    const bool accepted = g_MainApp.GetDataFromLauncher() != FALSE;
    REQUIRE(accepted == !reject);
    const auto& normal = *RF455_GetLauncherConnection();
    if (accepted) {
        const bool argvLaunch = argc == 5;
        REQUIRE(normal.accepted && normal.endpoint == (argvLaunch ? 0u : 1u));
        REQUIRE(normal.kind == (argvLaunch ? RF455LauncherKind::ArgumentVector : RF455LauncherKind::CcrFile));
        REQUIRE(network.GetServerIP(normal.endpoint)==normal.address&&network.GetServerPort(normal.endpoint)==normal.port&&!std::strcmp(network.GetID(),normal.identifier));
        if(normal.hasAccountFields){REQUIRE(network.GetAccountIndex()==17&&!std::strcmp(network.GetPassword(),"retained"));for(unsigned i=0;i<4;++i)REQUIRE(network.GetWorldServerKey(i)==0x10203040+i);}
        else REQUIRE(!std::strcmp(network.GetPassword(),"fixture-value"));
    } else {
        REQUIRE(!normal.accepted && !network.GetServerPort(0) && !network.GetServerPort(1));
        REQUIRE(!network.GetServerIP(0) && !network.GetServerIP(1) && !std::strcmp(network.GetPassword(), "retained"));
    }
    network.SetID(const_cast<char*>(longId.c_str()));network.SetPassword(const_cast<char*>(longPassword.c_str()));REQUIRE(std::strlen(network.GetID())==50&&std::strlen(network.GetPassword())==32);
    FILE*out=std::fopen("result.json","wb");REQUIRE(out);std::fprintf(out,"{\"status\":\"PASS\",\"ccr_country_profiles\":9,\"truncation_cases\":19,\"file_sharing_missing_extra\":true,\"argument_count_numeric_bounds\":true,\"normal_network_fields\":true,\"identifier50_password32\":true,\"network_created\":false,\"connection_attempted\":false,\"handoff\":\"%s\"}\n",accepted?(normal.endpoint==1?"ccr":"argv"):"rejected");std::fclose(out);return 0;
}
