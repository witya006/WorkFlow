#define main oldAccountEntry158
#include "client455_account_probe.cpp"
#undef main
#include "client455_selection.h"
struct SelectionDispatch158{using Type=bool(CNetworkMgr::*)(char*,std::size_t);friend Type access(SelectionDispatch158);};template struct MemberAccess<SelectionDispatch158,&CNetworkMgr::DispatchSelectedCharacter455>;

static int selected158(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    REQUIRE(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData());InitR3Engine();
    CAvatar avatar;std::unique_ptr<CAvatar[]> dummy(new CAvatar[3]);auto* previousAvatar=g_pAvatar;auto* previousDummy=g_pAvatarDummy;g_pAvatar=&avatar;g_pAvatarDummy=dummy.get();
    auto& network=g_MainApp.*access(NetworkMember{});auto& process=network.m_Process[0];
    _NET_BUFFER send,receive;std::vector<char> sendScratch(65536),receiveScratch(65536);
    REQUIRE(send.Configure(65536,65536,sendScratch.data())&&receive.Configure(65536,65536,receiveScratch.data()));
    process.*access(SendBuffer{})=&send;process.*access(ReceiveBuffer{})=&receive;process.*access(Owner{})=&network;process.m_nIndex=0;process.m_Type.m_wSocketMaxNum=1;process.m_codec455.initializeDefault(true);process.m_NetSocket.GetSocket(0)->m_bAccept=true;
    (network.*access(Active{}))[0]=2;network.m_account455.zoneRequestMode=-1;avatar.SetClientStage455(3);avatar.SetSkipTutorial455(1);
    REQUIRE(RF455_SelectedCharacterSlot()==0);
    BYTE reply[22]={0,1,0x78,0x56,0x34,0x12};const std::int64_t wantedDalant=0x123456789abll,wantedGold=-0x23456789abll;
    std::memcpy(reply+6,&wantedDalant,8);std::memcpy(reply+14,&wantedGold,8);
    RF455CharacterSelection parsed;parsed.serial=77;
    for(unsigned size:{0u,1u,21u})REQUIRE(!RF455_ReadCharacterSelection(reply,size,parsed)&&parsed.serial==77);
    REQUIRE(!RF455_ReadCharacterSelection(nullptr,22,parsed)&&parsed.serial==77);
    REQUIRE(RF455_ReadCharacterSelection(reply,22,parsed)&&parsed.result==256&&parsed.serial==0x12345678&&parsed.dalant==wantedDalant&&parsed.gold==wantedGold);
    unsigned routes=0;
    for(DWORD skip:{0u,1u,2u,0xffffffffu}){
        avatar.SetSkipTutorial455(skip);avatar.SetDalant(17);avatar.SetGold(19);dummy[0].SetDalant(23);dummy[0].SetGold(29);
        REQUIRE(network.SystemMsg_SelCharRequest_zone(0)&&network.IsSendRequestMsg());
        const auto outgoing=take(send);RF455NetworkCodec peer;peer.initializeDefault(true);peer.receiveKey=process.m_codec455.sendKey;peer.sendKey=process.m_codec455.receiveKey;
        BYTE plain[128]={};std::size_t produced=0;REQUIRE(peer.decode(outgoing.data(),outgoing.size(),plain,sizeof(plain),produced));
        REQUIRE(produced==5&&plain[2]==1&&plain[3]==14&&plain[4]==0);
        REQUIRE(!(network.*access(SelectionDispatch158{}))(reinterpret_cast<char*>(reply),21)&&network.IsSendRequestMsg()&&avatar.GetDalant()==17&&dummy[0].GetDalant()==23);
        BYTE wire[128];std::size_t bytes=0;REQUIRE(peer.encode(0x0f01,reply,22,wire,sizeof(wire),bytes));
        push(receive,wire,2);(process.*access(Pop{}))(0);REQUIRE(network.IsSendRequestMsg());
        push(receive,wire+2,bytes-2);(process.*access(Pop{}))(0);
        REQUIRE(!network.IsSendRequestMsg()&&network.GetResultOfCharacterSelect()==0&&network.GetAvatarIndex()==0x12345678);
        auto* selected=skip==1?&avatar:&dummy[0];auto* other=skip==1?&dummy[0]:&avatar;
        REQUIRE(selected->GetDalant()==wantedDalant&&selected->GetGold()==wantedGold);
        REQUIRE(other->GetDalant()==(skip==1?23:17)&&other->GetGold()==(skip==1?29:19));++routes;
    }
    process.*access(SendBuffer{})=nullptr;process.*access(ReceiveBuffer{})=nullptr;process.*access(Owner{})=nullptr;g_pAvatar=previousAvatar;g_pAvatarDummy=previousDummy;ReleaseR3Engine();
    FILE* result=std::fopen("result.json","wb");REQUIRE(result);std::fprintf(result,"{\"status\":\"PASS\",\"actual_selected_wire\":true,\"actual_encrypted_fragmented_dispatch\":true,\"actual_wallet_routes\":%u,\"WORD_result_to_BYTE\":true,\"full_client\":false}\n",routes);std::fclose(result);return 0;
}
int main(){try{return selected158();}catch(const std::exception& error){std::fprintf(stderr,"Selection158:%s\n",error.what());return 2;}}
