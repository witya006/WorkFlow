#include "network/protocol/pt_zone_client.h"
FIELD(EntryCloseFlag,BOOL,CNetworkMgr,m_bIsRequestClose)
static bool sameEntry(const RF455WorldEntry& a,const RF455WorldEntry& b){
    return a.result==b.result&&a.grade==b.grade&&a.kind==b.kind&&a.responseSeen==b.responseSeen&&a.cashShop==b.cashShop&&a.npcShop==b.npcShop&&a.quest==b.quest;
}
static int worldEntryChecks(CNetworkMgr& network,CNetProcess& process,_NET_BUFFER& send,_NET_BUFFER& receive){
    static_assert(sizeof(_enter_world_request_zone)==58&&sizeof(_enter_world_result_zone)==12,"actual packed protocol declarations");
    BYTE payload[12]={242,255,173,0,0xfe,0xff,7,0xff,0xff,255,0,0};
    RF455WorldEntry unchanged;unchanged.result=19;unchanged.kind=23;unchanged.cashShop=47;
    for(unsigned bytes=0;bytes<12;++bytes){auto state=unchanged;REQUIRE(!RF455_ReadWorldEntry(payload,bytes,state)&&sameEntry(state,unchanged));}
    auto nullState=unchanged;REQUIRE(!RF455_ReadWorldEntry(nullptr,12,nullState)&&sameEntry(nullState,unchanged));
    for(BYTE result:{BYTE(0),BYTE(242),BYTE(255)})for(unsigned flags=0;flags<8;++flags){
        BYTE data[12]={result,255,173,BYTE(flags&1?1:0),0x34,0x12,BYTE(flags&2?7:0),0xff,0xff,BYTE(flags&4?255:0),0,0};
        RF455WorldEntry state;REQUIRE(RF455_ReadWorldEntry(data,sizeof(data),state));
        REQUIRE(state.responseSeen&&state.result==result&&state.grade==255&&state.kind==173);
        REQUIRE(state.cashShop==(flags&1?0x1234:-1)&&state.npcShop==(flags&2?65535:-1)&&state.quest==(flags&4?0:-1));
    }
    REQUIRE(network.GetAccountIndex()==0x12345678);
    for(unsigned i=0;i<4;++i)REQUIRE(network.GetWorldServerKey(BYTE(i))==DWORD(0x04030201u+0x04040404u*i));
    // This component entry bypasses WinMain,which normally publishes this flag.
    const BOOL previousWindowed=g_bIsWindowed;g_bIsWindowed=TRUE;
    network.ReceiveResponseMsg();(network.*access(Active{}))[0]=1;network.*access(EntryCloseFlag{})=FALSE;
    REQUIRE(network.SystemMsg_EnterWorldRequest_zone()&&network.IsSendRequestMsg()&&(network.*access(EntryCloseFlag{})));
    const auto sent=take(send);RF455NetworkCodec peer;peer.initializeDefault(true);
    peer.receiveKey=process.m_codec455.sendKey;peer.sendKey=process.m_codec455.receiveKey;
    BYTE plain[128]={};std::size_t plainBytes=0;REQUIRE(peer.decode(sent.data(),sent.size(),plain,sizeof(plain),plainBytes)&&plainBytes==62);
    // Fixed oracle for fixture account/keys in the windowed target request.
    static const char oracle[]="3e00010178563412a1fb9c0ea5ff9802a9f39406adf7901a00f7ed0100373561333264346136646166663534386663666362343066656138333861306400";
    static_assert(sizeof(oracle)==125,"62 byte plain frame");
    const auto nibble=[](char c){return c<='9'?c-'0':c-'a'+10;};
    for(unsigned i=0;i<62;++i){const BYTE expected=BYTE((nibble(oracle[2*i])<<4)|nibble(oracle[2*i+1]));if(plain[i]!=expected)std::fprintf(stderr,"World entry oracle offset%u actual%02x expected%02x\n",i,unsigned(plain[i]),unsigned(expected));REQUIRE(plain[i]==expected);}
    BYTE fullscreen[58];const std::uint32_t keys[4]={0x04030201,0x08070605,0x0c0b0a09,0x100f0e0d};
    RF455_PackWorldEntry(fullscreen,0x12345678,keys,true);REQUIRE(fullscreen[20]==1);
    fullscreen[20]=0;REQUIRE(!std::memcmp(fullscreen,plain+4,58));
    const auto before=network.m_worldEntry455;const BYTE beforeResult=network.GetResultOfEnterTheWorldServer();
    for(unsigned size=0;size<12;++size)REQUIRE(!network.DispatchWorldEntry455(reinterpret_cast<char*>(payload),size)&&sameEntry(before,network.m_worldEntry455)&&network.GetResultOfEnterTheWorldServer()==beforeResult&&network.IsSendRequestMsg());
    REQUIRE(!network.DispatchWorldEntry455(nullptr,12)&&sameEntry(before,network.m_worldEntry455));
    BYTE wire[64]={};std::size_t wireBytes=0;REQUIRE(peer.encode(0x0201,payload,sizeof(payload),wire,sizeof(wire),wireBytes));
    receive.m_dwPopPnt=receive.m_dwPushPnt=receive.m_capacity-1;receive.m_dwPopRot=receive.m_dwPushRot=0;
    push(receive,wire,2);(process.*access(Pop{}))(0);REQUIRE(network.IsSendRequestMsg()&&sameEntry(before,network.m_worldEntry455));
    push(receive,wire+2,wireBytes-2);(process.*access(Pop{}))(0);
    REQUIRE(!network.IsSendRequestMsg()&&!_IsOpenedDialogBox(nullptr,0xf100));
    REQUIRE(network.GetResultOfEnterTheWorldServer()==242&&network.GetAvatarGrade()==255);
    const auto& state=network.m_worldEntry455;REQUIRE(state.responseSeen&&state.result==242&&state.kind==173&&state.cashShop==-1&&state.npcShop==65535&&state.quest==0);
    payload[0]=0;payload[2]=1;payload[3]=1;network.SendRequestMsg();
    REQUIRE(peer.encode(0x0201,payload,sizeof(payload),wire,sizeof(wire),wireBytes));
    push(receive,wire,wireBytes);(process.*access(Pop{}))(0);
    REQUIRE(network.GetResultOfEnterTheWorldServer()==0&&network.m_worldEntry455.kind==1&&network.m_worldEntry455.cashShop==65534&&!network.IsSendRequestMsg());
    (network.*access(Active{}))[0]=0;g_bIsWindowed=previousWindowed;
    FILE* output=std::fopen("world-entry-result.json","wb");REQUIRE(output);
    std::fputs("{\"status\":\"PASS\",\"ordinary_request_bytes\":58,\"ordinary_response_bytes\":12,\"request_golden_frame\":true,\"fullscreen_flag\":true,\"short_lengths_checked\":12,\"null_rejected\":true,\"result_flag_combinations\":24,\"fragmented_wrapped_encrypted_receiver\":true,\"request_dialog_closed\":true,\"failure_response_selectors_retained\":true,\"authentication_performed\":false,\"bootstrap_or_selection_accepted\":false}\n",output);
    std::fclose(output);return 0;
}
