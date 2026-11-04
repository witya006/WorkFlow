#include "GameObject/Manager/CCharacterMgr.h"
#include "network/cnetworkmgr.h"
#include "client455_time_commands.h"
namespace TimeCommandsProbe {
#define RF455_TIME_COMMANDS_EMBEDDED
#include "test_client455_time_commands.cpp"
#undef RF455_TIME_COMMANDS_EMBEDDED
}
class CommandFixtureNetwork : public CNetworkMgr {
public:
    void SetFixtureGrade(BYTE value) { m_byAvatarGrade=value; }
};
static int timeCommandsScenarioProbe() {
    const char* output=std::getenv("RF_LAB_HELPER_OUTPUT");if (!output) return 100;
    const char* dlls[]={"mss32.dll","ABuse.dll","Adv.dll","PDLL.dll"};
    for (unsigned i=0;i<4;++i) if (GetModuleHandleA(dlls[i])) return 101;
    FILE* file=std::fopen(output,"wt");if (!file) return 102;
    const int component=TimeCommandsProbe::runTimeCommandChecks(file);
    if (std::fclose(file)) return 103;
    unsigned checks=0,failures=0;
    auto verify=[&](bool value) { ++checks;if (!value) ++failures; };
    const DWORD allocationBefore=GetDmallocSize();
    CNetworkMgr* previousNetwork=g_pNetworkMgr;
    auto provider=RF455_ClockTickSource;RF455_ClockTickSource=&TimeCommandsProbe::testTick;
    CommandFixtureNetwork* network=new CommandFixtureNetwork;
    // Constructor initializes Winsock only; Create/SetNetSystem/Connect are not
    // called and no network process or remote connection is created.
    verify(network->m_dwUseProcessNum==0);g_pNetworkMgr=network;
    CHAT_INFO chat;strcpy(chat.m_pMessageType,"previous-prefix");network->SetFixtureGrade(1);
    TimeCommandsProbe::calls=0;char game[]="%TIME 12";
    verify(chat.SendMessage(game)==TRUE);verify(TimeCommandsProbe::calls==1);
    verify(RF455_GetDayFraction()==.5f);verify(chat.m_pMessageType[0]==0);
    verify(chat.m_byMaxSendMessageNum==1 && chat.m_byCurrentSendMessageNo==0);
    verify(!strcmp(chat.m_listSendMessage[0],"%TIME 12") && !strcmp(game,"%TIME 12"));
    TimeCommandsProbe::calls=0;char real[]="%real_time 6 0";
    verify(chat.SendMessage(real)==TRUE);verify(TimeCommandsProbe::calls==1);
    verify(RF455_GetRealDayFraction()==.25f && RF455_GetDayFraction()==.5f);
    verify(chat.m_byMaxSendMessageNum==2 && chat.m_byCurrentSendMessageNo==1);
    verify(!strcmp(chat.m_listSendMessage[1],real));
    network->SetFixtureGrade(0);TimeCommandsProbe::calls=0;
    const DWORD base=RF455_DayBase;verify(chat.SendMessage(game)==FALSE);
    verify(TimeCommandsProbe::calls==0 && RF455_DayBase==base && RF455_GetDayFraction()==.5f);
    verify(network->m_dwUseProcessNum==0);
    g_pNetworkMgr=previousNetwork;delete network;RF455_ClockTickSource=provider;
    verify(GetDmallocSize()==allocationBefore);
    for (unsigned i=0;i<4;++i) verify(GetModuleHandleA(dlls[i])==NULL);
    const std::string inputReport=std::string(output)+".input.json";
    file=std::fopen(inputReport.c_str(),"wt");if (!file) return 104;
    std::fprintf(file,"{\"checks\":%u,\"failures\":%u,\"actual_chat_send_called\":true,\"grades\":[1,0],\"history_prefix_checked\":true,\"network_processes_created\":0,\"winsock_constructor_only\":true,\"game_dlls_loaded\":false}\n",checks,failures);
    if (std::fclose(file)) return 105;
    return component||failures?106:0;
}
