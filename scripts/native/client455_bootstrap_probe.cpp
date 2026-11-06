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
#include "client455_bootstrap.h"
#include "client455_network_state.h"
#include "client455_nation_paths.h"
#include <cstdio>
#include <cstring>
#include <string>
extern CMainApp g_MainApp;
template<class Tag,typename Tag::Type Member>struct MemberAccess{friend typename Tag::Type access(Tag){return Member;}};
struct NetworkMember{using Type=CNetworkMgr CMainApp::*;friend Type access(NetworkMember);};
template struct MemberAccess<NetworkMember,&CMainApp::m_cNetworkMgr>;
#define REQUIRE(x) do{if(!(x)){std::fprintf(stderr,"Bootstrap failure line%d: %s\n",__LINE__,#x);return 1;}}while(0)
struct TransportFixture{RF455NetworkState*state;int result;unsigned calls=0,accepted=0,process=99;std::uint32_t address=0;std::uint16_t port=0;};
static int transport(void*p,unsigned process,std::uint32_t address,std::uint16_t port){auto&f=*static_cast<TransportFixture*>(p);++f.calls;f.process=process;f.address=address;f.port=port;return f.result;}
static void accepted(void*p){auto&f=*static_cast<TransportFixture*>(p);++f.accepted;if(f.state->active[0]<4)f.state->connected[f.state->active[0]]=1;}
int main(int argc,char**argv){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    if(argc==4&&!std::strcmp(argv[1],"--hold-instance")){
        HANDLE ready=OpenEventA(EVENT_MODIFY_STATE,FALSE,argv[2]),done=OpenEventA(SYNCHRONIZE,FALSE,argv[3]);REQUIRE(ready&&done);SetEvent(ready);
        const DWORD waited=WaitForSingleObject(done,10000);CloseHandle(ready);CloseHandle(done);REQUIRE(waited==WAIT_OBJECT_0);return 0;
    }
    if(argc==2&&!std::strcmp(argv[1],"--wrong-name")){REQUIRE(RF455_CheckSingleInstance()==RF455InstanceResult::WrongFilename);return 0;}
    REQUIRE(RF455_InitializeNationPaths());RF455_LoadBootstrapSettings();REQUIRE(RF455_GetBootstrapSettings()->useFG==0);
    const auto*paths=RF455_GetNormalNationPaths();std::string path=std::string(paths->dataRoot)+"/FG_CB.ini";
    struct Case{const char*text;int value;};for(const auto&c:{Case{"1",1},Case{"1234",123},Case{"-129",-12},Case{"abc",0},Case{" 42",42}}){
        REQUIRE(WritePrivateProfileStringA("SETTING","USEFG",c.text,path.c_str()));RF455_LoadBootstrapSettings();REQUIRE(RF455_GetBootstrapSettings()->useFG==c.value);
    }
    REQUIRE(WritePrivateProfileStringA("SETTING","USEFG",nullptr,path.c_str()));RF455_LoadBootstrapSettings();REQUIRE(RF455_GetBootstrapSettings()->useFG==0);
    for(unsigned nation=0;nation<11;++nation)REQUIRE(RF455_InstancePolicyBypassed(nation)==(nation==2||nation==3||nation==7||nation==8));
    REQUIRE(RF455_ExecutableNameMatches("C:\\owned\\rf_online.bin"));REQUIRE(RF455_ExecutableNameMatches("RF_ONLINE.BIN"));
    for(const char*name:{"RF_Online.exe","xRF_Online.bin","RF_Online.bin.extra","RF_Online","","RF_Online.binx"})REQUIRE(!RF455_ExecutableNameMatches(name));
    REQUIRE(RF455_CountClientProcesses()==1);REQUIRE(RF455_CheckSingleInstance()==RF455InstanceResult::Accepted);
    REQUIRE(RF455_CheckSingleInstance()==RF455InstanceResult::ExistingMutex);
    char readyName[96],doneName[96],module[MAX_PATH],command[1024];std::sprintf(readyName,"Local\\RF455-bootstrap-ready-%lu",GetCurrentProcessId());std::sprintf(doneName,"Local\\RF455-bootstrap-done-%lu",GetCurrentProcessId());
    HANDLE ready=CreateEventA(nullptr,TRUE,FALSE,readyName),done=CreateEventA(nullptr,TRUE,FALSE,doneName);REQUIRE(ready&&done);REQUIRE(GetModuleFileNameA(nullptr,module,sizeof(module)));
    std::sprintf(command,"\"%s\" --hold-instance %s %s",module,readyName,doneName);STARTUPINFOA startup={};startup.cb=sizeof(startup);PROCESS_INFORMATION child={};
    REQUIRE(CreateProcessA(module,command,nullptr,nullptr,FALSE,CREATE_NO_WINDOW,nullptr,nullptr,&startup,&child));REQUIRE(WaitForSingleObject(ready,5000)==WAIT_OBJECT_0);
    const unsigned duplicateCount=RF455_CountClientProcesses();const auto duplicateResult=RF455_CheckSingleInstance();SetEvent(done);REQUIRE(WaitForSingleObject(child.hProcess,5000)==WAIT_OBJECT_0);DWORD childExit=1;REQUIRE(GetExitCodeProcess(child.hProcess,&childExit));
    CloseHandle(child.hThread);CloseHandle(child.hProcess);CloseHandle(ready);CloseHandle(done);REQUIRE(childExit==0&&duplicateCount==2&&duplicateResult==RF455InstanceResult::TooManyProcesses);
    for(unsigned process=0;process<6;++process)for(unsigned endpoint:{0u,1u,3u}){
        RF455NetworkState state;TransportFixture f={&state,0};REQUIRE(RF455_AttemptConnect(state,endpoint,process,false,0x0100007f,4321,transport,accepted,&f)==0);
        REQUIRE(f.calls==1&&!f.accepted&&f.process==process&&f.address==0x0100007f&&f.port==4321&&state.active[process]==endpoint&&!state.connected[endpoint]);
    }
    {RF455NetworkState state;state.active[5]=2;state.connected[1]=1;TransportFixture f={&state,10061};REQUIRE(RF455_AttemptConnect(state,1,5,false,7,8,transport,accepted,&f)==10061);REQUIRE(state.active[5]==2&&!state.connected[1]&&f.calls==1);}
    {RF455NetworkState state;state.active[5]=1;state.connected[1]=1;TransportFixture f={&state,0};REQUIRE(RF455_AttemptConnect(state,0,5,false,7,8,transport,accepted,&f)==-1);REQUIRE(!f.calls&&!f.accepted&&state.active[5]==1);}
    {RF455NetworkState state;state.active[0]=3;TransportFixture f={&state,9};REQUIRE(RF455_AttemptConnect(state,2,5,false,7,8,transport,accepted,&f)==0);REQUIRE(!f.calls&&f.accepted==1&&state.active[5]==2&&state.connected[3]&&!state.connected[2]);}
    {RF455NetworkState state;TransportFixture f={&state,9};REQUIRE(RF455_AttemptConnect(state,1,0,true,7,8,transport,accepted,&f)==0);REQUIRE(!f.calls&&f.accepted==1&&state.connected[1]);}
    {RF455NetworkState state;TransportFixture f={&state,0};REQUIRE(RF455_AttemptConnect(state,4,0,false,7,8,transport,accepted,&f)==WSAEINVAL);REQUIRE(RF455_AttemptConnect(state,0,6,false,7,8,transport,accepted,&f)==WSAEINVAL);REQUIRE(!f.calls&&!f.accepted);}
    auto&network=g_MainApp.*access(NetworkMember{});network.SetServerIP(0,inet_addr("127.0.0.1"));
    REQUIRE(g_MainApp.CreateNetworkMgr455());REQUIRE(g_pNetworkMgr==&network&&network.GetServerIP(0)==inet_addr("127.0.0.1")&&network.GetActiveServerID()==-1);
    // A bound,non-listening socket reserves an owned closed port. No service or
    // server emulator exists. Compare the target's exact API order to an
    // independent WinSock call:closesocket may erase connect's error.
    SOCKET reserved=socket(AF_INET,SOCK_STREAM,IPPROTO_TCP);REQUIRE(reserved!=INVALID_SOCKET);sockaddr_in local={};local.sin_family=AF_INET;local.sin_addr.s_addr=inet_addr("127.0.0.1");
    REQUIRE(bind(reserved,reinterpret_cast<sockaddr*>(&local),sizeof(local))==0);int length=sizeof(local);REQUIRE(getsockname(reserved,reinterpret_cast<sockaddr*>(&local),&length)==0);
    SOCKET oracle=socket(AF_INET,SOCK_STREAM,0);REQUIRE(oracle!=INVALID_SOCKET);REQUIRE(connect(oracle,reinterpret_cast<sockaddr*>(&local),sizeof(local))==SOCKET_ERROR);
    const int beforeClose=WSAGetLastError();REQUIRE(beforeClose==WSAECONNREFUSED);REQUIRE(closesocket(oracle)==0);const int afterClose=WSAGetLastError();
    network.SetServerPort(0,ntohs(local.sin_port));const int error=network.ConnectRaw455(0,0,local.sin_addr.s_addr,ntohs(local.sin_port));REQUIRE(error==afterClose);
    REQUIRE(network.ConnectToServer455(0,0)==afterClose&&!network.IsConnectedToServer(0)&&network.GetActiveServerID()==(afterClose?-1:0));
    REQUIRE(network.CNetWorking::Connect(0,0,local.sin_addr.s_addr,ntohs(local.sin_port))==(afterClose==0));REQUIRE(network.ConnectRaw455(5,0,0,0)==WSAEINVAL);
    REQUIRE(network.ConnectToServer455(0,5)==WSAEINVAL&&!network.IsConnectedToServer(0));closesocket(reserved);
    // Exercise the real455logout direct branch with endpoint1,which sends no
    // packet. This verifies callback/state publication,not authentication.
    g_MainApp.SetRequestLogout(TRUE);REQUIRE(network.ConnectToServer455(1,0)==0&&network.IsConnectedToServer(1)&&network.GetActiveServerID()==1);
    REQUIRE(network.ConnectToServer455(0,0)==-1);g_MainApp.SetRequestLogout(FALSE);
    FILE*out=std::fopen("result.json","wb");REQUIRE(out);std::fprintf(out,"{\"status\":\"PASS\",\"fg_profile_bounds\":true,\"country_policies\":11,\"instance_name_process_mutex\":true,\"core_process_capacity\":6,\"real_network_created\":true,\"tcp_refusal_before_close\":%d,\"tcp_error_after_close\":%d,\"real_raw_tcp_return\":%d,\"real_invalid_process_error\":%d,\"real_logout_callback\":true,\"authentication_performed\":false}\n",beforeClose,afterClose,error,WSAEINVAL);std::fclose(out);return 0;
}
