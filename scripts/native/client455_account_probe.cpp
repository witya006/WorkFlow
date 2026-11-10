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
#include "client455_client_items.h"
#include "client455_character_tables.h"
#include "client455_account.h"
#include "client455_language.h"
#include "client455_nation_paths.h"
#include "client455_avatar_stage.h"
#include <cstdio>
#include <cstring>
#include <vector>
#include <exception>
extern CMainApp g_MainApp;
template<class Tag,typename Tag::Type Member>struct MemberAccess{friend typename Tag::Type access(Tag){return Member;}};
#define FIELD(Tag,TypeName,Class,member) struct Tag{using Type=TypeName Class::*;friend Type access(Tag);};template struct MemberAccess<Tag,&Class::member>;
FIELD(NetworkMember,CNetworkMgr,CMainApp,m_cNetworkMgr)
FIELD(SpriteMember,CSpriteMgr,CMainApp,m_cSpriteMgr)
FIELD(ScreenMember,CGUIScreen,CMainApp,m_cScreen)
FIELD(StageMember,CGameProgress*,CMainApp,m_pGameProgress)
FIELD(StageIdMember,BYTE,CMainApp,m_byGameProgressID)
FIELD(CreatedMember,BOOL,CMainApp,m_bCreatedAllObject)
FIELD(LoadedMember,BOOL,CMainApp,m_bLoadedAllData)
FIELD(ActiveMember,BOOL,CMainApp,m_bIsActive)
FIELD(SendBuffer,_NET_BUFFER*,CNetProcess,m_pSendBuffer)
FIELD(ReceiveBuffer,_NET_BUFFER*,CNetProcess,m_pRecvBuffer)
FIELD(Owner,CNetWorking*,CNetProcess,m_pNetwork)
struct Active{using Type=BYTE(CNetworkMgr::*)[6];friend Type access(Active);};template struct MemberAccess<Active,&CNetworkMgr::m_activeServer455>;
struct Pop{using Type=void(CNetProcess::*)(WORD);friend Type access(Pop);};template struct MemberAccess<Pop,&CNetProcess::_PopRecvMsg>;
struct Accept{using Type=void(CNetworkMgr::*)(DWORD,DWORD,DWORD);friend Type access(Accept);};template struct MemberAccess<Accept,&CNetworkMgr::AcceptClientCheck>;
struct Load{using Type=BOOL(CMainApp::*)();friend Type access(Load);};template struct MemberAccess<Load,&CMainApp::LoadData>;
struct Unload{using Type=BOOL(CMainApp::*)();friend Type access(Unload);};template struct MemberAccess<Unload,&CMainApp::UnloadData>;
#define REQUIRE(x) do{if(!(x)){std::fprintf(stderr,"Account failure line%d: %s\n",__LINE__,#x);return 1;}}while(0)
static std::vector<BYTE> take(_NET_BUFFER& buffer){
    int bytes=0;bool missing=false;const auto* p=buffer.GetSendPoint(&bytes,&missing);
    if(!p||missing)return {};std::vector<BYTE> result(p,p+bytes);buffer.AddPopPos(bytes);return result;
}
static void push(_NET_BUFFER& buffer,const BYTE* p,std::size_t size){
    DWORD left=buffer.m_capacity-buffer.m_dwPushPnt;std::memcpy(buffer.GetPushPos(),p,size);
    if(size>left)std::memcpy(buffer.m_sMainBuffer,buffer.m_sMainBuffer+buffer.m_capacity,size-left);
    buffer.AddPushPos(static_cast<DWORD>(size));
}
static std::vector<BYTE> frame(BYTE opcode,const std::vector<BYTE>& data){
    std::vector<BYTE> result={BYTE((data.size()+4)&255),BYTE((data.size()+4)>>8),21,opcode};result.insert(result.end(),data.begin(),data.end());return result;
}
static std::vector<BYTE> loginOracle(const char* id,const char* pw,const char* ticket,BYTE delta,WORD mask,BYTE serverType,bool tutorial=false){
    std::vector<BYTE> result(342,0);auto text=[&](unsigned offset,unsigned capacity,const char* input){for(unsigned i=0;i+1<capacity&&input[i];++i)result[offset+i]=BYTE(input[i]);};
    if(ticket)text(85,257,ticket);else {text(0,51,id);text(51,33,pw);}
    if(!tutorial)for(auto& byte:result)byte=BYTE((unsigned(byte)+delta)^mask);result[84]=serverType;return frame(3,result);
}
struct StageFixture: CGameProgress {
    unsigned creates=0,loops=0;bool succeed=false;
    BOOL Create()override{++creates;m_bIsCreated=succeed;return succeed;}
    BOOL MainLoop(BOOL)override{++loops;return FALSE;}
    HRESULT RestoreDeviceObjects()override{return S_OK;}
    HRESULT InvalidateDeviceObjects()override{return S_OK;}
    HRESULT FrameMove()override{return S_OK;}HRESULT Render()override{return S_OK;}
    BOOL InputProcess()override{return TRUE;}BOOL LoadData()override{return TRUE;}BOOL UnloadData()override{return TRUE;}
    LRESULT MsgProc(HWND,UINT,WPARAM,LPARAM)override{return 0;}
    void reset(){Init();creates=loops=0;}
};
struct StageBinding {
    CGameProgress* previousStage=g_MainApp.*access(StageMember{});BYTE previousId=g_MainApp.*access(StageIdMember{});
    BOOL previousCreated=g_MainApp.*access(CreatedMember{}),previousLoaded=g_MainApp.*access(LoadedMember{}),previousActive=g_MainApp.*access(ActiveMember{});
    CAvatar* previousAvatar=g_pAvatar;
    StageBinding(CAvatar& avatar,StageFixture& stage){g_pAvatar=&avatar;g_MainApp.*access(StageMember{})=&stage;g_MainApp.*access(CreatedMember{})=TRUE;g_MainApp.*access(LoadedMember{})=TRUE;g_MainApp.*access(ActiveMember{})=FALSE;}
    ~StageBinding(){g_pAvatar=previousAvatar;g_MainApp.*access(StageMember{})=previousStage;g_MainApp.*access(StageIdMember{})=previousId;g_MainApp.*access(CreatedMember{})=previousCreated;g_MainApp.*access(LoadedMember{})=previousLoaded;g_MainApp.*access(ActiveMember{})=previousActive;}
};
#include "client455_world_entry_probe.inc"
#include "client455_registered_characters_probe.inc"
static int avatarStageChecks(CNetworkMgr& network,_NET_BUFFER& send){
    CAvatar avatar;REQUIRE(avatar.GetClientStage455()==0&&avatar.GetSkipTutorial455()==0);
    StageFixture stage;StageBinding binding(avatar,stage);
    for(BYTE value:{BYTE(0),BYTE(1),BYTE(2),BYTE(3),BYTE(127),BYTE(255)}){
        avatar.SetClientStage455(value);REQUIRE(avatar.GetClientStage455()==value&&avatar.IsClientStage455(value));
        for(DWORD skip:{0u,1u,0xffffffffu}){avatar.SetSkipTutorial455(skip);REQUIRE(avatar.GetSkipTutorial455()==skip);
            REQUIRE(avatar.SelectClientStage455(2)==(skip?3:2)&&avatar.SelectClientStage455(3)==3);
            REQUIRE(bool(avatar.HandlesTutorialLocally455())==(value==2&&!skip));
            REQUIRE(RF455_IsTutorialAvatarStage()==(value==2));}
    }
    avatar.SetClientStage455(255);stage.succeed=false;g_MainApp.*access(StageIdMember{})=2;
    REQUIRE(!g_MainApp.GameMainLoop()&&stage.creates==1&&stage.loops==0&&avatar.GetClientStage455()==255);
    stage.succeed=true;REQUIRE(g_MainApp.GameMainLoop()&&stage.creates==2&&stage.loops==1&&avatar.GetClientStage455()==3);
    avatar.SetClientStage455(255);REQUIRE(g_MainApp.GameMainLoop()&&stage.creates==2&&stage.loops==2&&avatar.GetClientStage455()==255);
    for(BYTE id:{BYTE(0),BYTE(1)}){stage.reset();stage.succeed=true;g_MainApp.*access(StageIdMember{})=id;REQUIRE(g_MainApp.GameMainLoop()&&avatar.GetClientStage455()==id);}
    network.SetID("fixture-id");network.SetPassword("fixture-password");
    for(DWORD skip:{0u,1u,0xffffffffu}){avatar.SetSkipTutorial455(skip);
        for(BYTE id:{BYTE(1),BYTE(2),BYTE(3)}){avatar.SetClientStage455(id);
            REQUIRE(network.AccountMsg_LoginAccountRequest_cllo());
            const auto sent=take(send);if(id==2&&!skip)REQUIRE(sent.empty());else REQUIRE(sent==loginOracle("fixture-id","fixture-password",nullptr,network.m_account455.delta,network.m_account455.mask,network.m_account455.serverType,id==2));network.ReceiveResponseMsg();}
    }
    avatar.SetClientStage455(2);avatar.SetSkipTutorial455(0);auto& codec=network.m_Process[0].m_codec455;
    codec.enabled=false;BYTE type[2]={1,17},payload=0x5a;REQUIRE(network.SendNetMessage(0,type,&payload,1)&&take(send)==std::vector<BYTE>({5,0,1,17,0x5a})&&!codec.enabled);
    type[0]=21;type[1]=3;codec.enabled=true;REQUIRE(network.SendNetMessage(0,type,nullptr,0)&&take(send).empty()&&codec.enabled);
    type[0]=4;type[1]=31;REQUIRE(!network.SendNetMessage(0,type,&payload,1)&&take(send).empty()&&codec.enabled);
    return 0;
}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    RF455AccountHandshake seed;BYTE wrap[3]={255,254,255};REQUIRE(RF455_ReadAccountSeed(seed,wrap,3)&&seed.delta==0&&seed.mask==1);
    REQUIRE(!RF455_ReadAccountSeed(seed,wrap,2)&&seed.delta==0&&seed.mask==1);
    RF455WorldInfo records[300];std::memset(records,0xa5,sizeof(records));BYTE result=0x55;std::uint32_t count=777;
    std::vector<BYTE> worlds={2,14,0,2,1,5,'R','F',0,'x','y',7,254,2,'Z',0,9};
    REQUIRE(RF455_ReadWorldList(worlds.data(),worlds.size(),records,300,result,count)&&result==2&&count==2);
    REQUIRE(records[0].value==1&&!std::strcmp(records[0].m_pName,"RF")&&records[0].status==7&&BYTE(records[0].m_pName[5])==0xa5);
    REQUIRE(records[1].value==-2&&!std::strcmp(records[1].m_pName,"Z")&&records[1].status==9&&records[1].padding[2]==0xa5);
    RF455WorldInfo before[300];std::memcpy(before,records,sizeof(records));
    for(std::size_t length=0;length<worlds.size();++length)REQUIRE(!RF455_ReadWorldList(worlds.data(),length,records,300,result,count)&&result==2&&count==2&&!std::memcmp(before,records,sizeof(records)));
    auto bad=worlds;bad[3]=128;REQUIRE(!RF455_ReadWorldList(bad.data(),bad.size(),records,300,result,count));
    bad=worlds;bad[5]=0;REQUIRE(!RF455_ReadWorldList(bad.data(),bad.size(),records,300,result,count));
    bad=worlds;bad[5]=65;REQUIRE(!RF455_ReadWorldList(bad.data(),bad.size(),records,300,result,count));
    auto longest=std::vector<BYTE>{0,68,0,1,3,64};longest.insert(longest.end(),64,'N');longest.back()=0;longest.push_back(4);
    REQUIRE(RF455_ReadWorldList(longest.data(),longest.size(),records,300,result,count)&&std::strlen(records[0].m_pName)==63&&records[0].status==4);
    std::vector<BYTE> maximum={0,0,0,127};for(unsigned i=0;i<127;++i)maximum.insert(maximum.end(),{1,1,0,3});maximum[1]=BYTE(maximum.size()-3);maximum[2]=BYTE((maximum.size()-3)>>8);
    REQUIRE(RF455_ReadWorldList(maximum.data(),maximum.size(),records,300,result,count)&&count==127&&records[126].status==3);
    REQUIRE(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData());
    InitR3Engine();auto* state=GetR3State();state->mScreenXsize=640;state->mScreenYsize=480;state->mbFullScreen=FALSE;ForceFullScreen();REQUIRE(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)));
    g_pUiSpriteMgr=&(g_MainApp.*access(SpriteMember{}));g_pUiScreen=&(g_MainApp.*access(ScreenMember{}));REQUIRE((g_MainApp.*access(Load{}))());
    auto& network=g_MainApp.*access(NetworkMember{});auto& process=network.m_Process[0];
    _NET_BUFFER send,receive;std::vector<char> sendScratch(1000000),receiveScratch(20000);
    REQUIRE(send.Configure(1000000,1000000,sendScratch.data())&&receive.Configure(20000,20000,receiveScratch.data()));
    process.*access(SendBuffer{})=&send;process.*access(ReceiveBuffer{})=&receive;process.*access(Owner{})=&network;process.m_nIndex=0;process.m_Type.m_wSocketMaxNum=1;process.m_codec455.initializeDefault(true);
    // Component boundary only:no listener,no transport worker,no authenticated peer.
    process.m_NetSocket.GetSocket(0)->m_bAccept=true;(network.*access(Active{}))[0]=0;
    (network.*access(Accept{}))(0,0,0);REQUIRE(take(send)==frame(12,{})&&network.IsSendRequestMsg()&&_IsOpenedDialogBox(nullptr,0xf100));
    auto* dialog=g_pUiScreen->GetLastDialogBox();REQUIRE(dialog&&dialog->GetStyleID()==5);
    const auto incoming=frame(13,{0x7f,0x45,0x23});receive.m_dwPopPnt=receive.m_dwPushPnt=receive.m_capacity-1;
    push(receive,incoming.data(),2);(process.*access(Pop{}))(0);REQUIRE(network.IsSendRequestMsg());
    push(receive,incoming.data()+2,incoming.size()-2);(process.*access(Pop{}))(0);
    REQUIRE(network.m_account455.delta==0x80&&network.m_account455.mask==0x2348&&!network.IsSendRequestMsg()&&!_IsOpenedDialogBox(nullptr,0xf100));
    char id[70],pw[50];std::memset(id,'I',sizeof(id));id[69]=0;std::memset(pw,'P',sizeof(pw));pw[49]=0;network.SetID(id);network.SetPassword(pw);network.m_account455.serverType=0xab;
    send.m_dwPopPnt=send.m_dwPushPnt=send.m_capacity-2;send.m_dwPopRot=send.m_dwPushRot=0;
    REQUIRE(network.AccountMsg_LoginAccountRequest_cllo()&&take(send)==loginOracle(id,pw,nullptr,0x80,0x2348,0xab)&&network.IsSendRequestMsg());
    std::vector<BYTE> reply(50,0);reply[0]=5;reply[1]=0x78;reply[2]=0x56;reply[3]=0x34;reply[4]=0x12;
    REQUIRE(!network.DispatchAccount455(4,reinterpret_cast<char*>(reply.data()),49)&&network.IsSendRequestMsg());
    auto answer=frame(4,reply);push(receive,answer.data(),answer.size());(process.*access(Pop{}))(0);
    REQUIRE(network.GetAccountIndex()==0x12345678&&!network.IsSendRequestMsg()&&network.GetResultOfLogin()==5&&std::strlen(network.GetPassword())==32);
    REQUIRE(network.AccountMsg_PushCloseRequest_cllo());const auto close=take(send);REQUIRE(close.size()==92&&close[2]==21&&close[3]==9&&close[4+49]=='I'&&close[4+50]==0&&close[4+51+31]=='P'&&close[4+83]==0&&close[91]==0);
    reply[0]=0;REQUIRE(network.DispatchAccount455(4,reinterpret_cast<char*>(reply.data()),50));for(unsigned i=0;i<33;++i)REQUIRE(network.GetPassword()[i]==0);
    network.SetPassword(pw);REQUIRE(network.AccountMsg_JoinAccountRequest_cllo());const auto join=take(send);REQUIRE(join.size()==88&&join[3]==1&&join[4+83]==0);
    REQUIRE(network.AccountMsg_LoginAccountRequest_cllo()&&take(send)==loginOracle(id,"",nullptr,0x80,0x2348,0xab));
    REQUIRE(network.DispatchAccount455(6,reinterpret_cast<char*>(worlds.data()),worlds.size())&&network.GetWorldServerNum()==2&&network.GetWorldServerInfoList()[1].status==9);
    REQUIRE(network.AccountMsg_WorldListRequest_cllo()&&take(send)==frame(5,{0,0,0,0}));
    REQUIRE(network.AccountMsg_SelectWorldRequest_cllo(0x12345)&&take(send)==frame(7,{0x45,0x23})&&network.m_account455.selectedWorld==0x2345);
    std::vector<BYTE> selected(24,0);selected[0]=3;selected[1]=127;selected[4]=1;selected[5]=0x34;selected[6]=0x12;for(unsigned i=0;i<16;++i)selected[7+i]=BYTE(i+1);
    REQUIRE(!network.DispatchAccount455(8,reinterpret_cast<char*>(selected.data()),23));REQUIRE(network.DispatchAccount455(8,reinterpret_cast<char*>(selected.data()),24)&&network.GetServerIP(1)==0x0100007f&&network.GetServerPort(1)==0x1234);
    for(unsigned i=0;i<4;++i)REQUIRE(network.GetWorldServerKey(BYTE(i))==DWORD(0x04030201u+0x04040404u*i));
    auto* nation=RF455_GetNormalNationPaths();const auto saved=nation->nation;nation->nation=8;
    REQUIRE(!network.AccountMsg_LoginAccountRequest_cllo());REQUIRE(network.AccountMsg_LoginAccountRequest_cllo("fixture-ticket")&&take(send)==loginOracle("","","fixture-ticket",0x80,0x2348,0xab));nation->nation=saved;
    BYTE login[342];REQUIRE(RF455_PackLogin(login,seed,"id","pw",false,nullptr,true)&&login[0]=='i'&&login[51]=='p');
    BYTE status=7;REQUIRE(network.DispatchAccount455(2,reinterpret_cast<char*>(&status),1)&&network.GetResultOfUserRegistration()==7);
    REQUIRE(network.DispatchAccount455(10,reinterpret_cast<char*>(&status),1)&&network.GetResultOfRequestForDisconnectAccount()==7);
    REQUIRE(!network.DispatchAccount455(99,nullptr,0));network.ReceiveResponseMsg();
    (network.*access(Active{}))[0]=2;network.m_account455.zoneRequestMode=-1;network.SendRequestMsg();REQUIRE(network.IsSendRequestMsg()&&!_IsOpenedDialogBox(nullptr,0xf100));network.ReceiveResponseMsg();
    network.m_account455.zoneRequestMode=4;network.SendRequestMsg();REQUIRE(_IsOpenedDialogBox(nullptr,0xf100));network.m_account455.zoneRequestMode=-1;network.ReceiveResponseMsg();REQUIRE(!network.IsSendRequestMsg()&&_IsOpenedDialogBox(nullptr,0xf100));
    network.m_account455.zoneRequestMode=3;network.ReceiveResponseMsg();REQUIRE(!_IsOpenedDialogBox(nullptr,0xf100));(network.*access(Active{}))[0]=0;
    REQUIRE(worldEntryChecks(network,process,send,receive)==0);
    REQUIRE(registeredCharacterChecks(network,process,send,receive)==0);
    REQUIRE(avatarStageChecks(network,send)==0);
    process.*access(SendBuffer{})=nullptr;process.*access(ReceiveBuffer{})=nullptr;process.*access(Owner{})=nullptr;process.m_NetSocket.GetSocket(0)->m_bAccept=false;
    REQUIRE((g_MainApp.*access(Unload{}))());g_pUiSpriteMgr=nullptr;g_pUiScreen=nullptr;R3ReleaseTextTexture();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();
    FILE* out=std::fopen("result.json","wb");REQUIRE(out);std::fputs("{\"status\":\"PASS\",\"actual_gate_accept_request\":true,\"actual_fragment_wrap_seed_dispatch\":true,\"actual_request_dialog_open_close\":true,\"actual_account_send_receive\":true,\"login_bytes\":342,\"world_stride\":72,\"world_capacity\":300,\"bounded_world_reload\":true,\"maximum_valid_signed_count\":127,\"ticket_profile_packet\":true,\"mode2_packer_branch\":true,\"actual_Avatar_stage_skip\":true,\"actual_MainApp_Create_gate\":true,\"legacy_main2_maps_to455_main3\":true,\"actual_login_Tutorial_transform\":true,\"full_fourstage_factory\":false,\"authentication_performed\":false}\n",out);std::fclose(out);return 0;
}
int main(){try{return run();}catch(const std::exception& error){std::fprintf(stderr,"Account exception: %s\n",error.what());return 2;}}
