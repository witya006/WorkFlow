#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "input/imeedit.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "mainapp.h"
#include "gameprogress/cgp_maingame.h"
#include "addcodebyjang/effectcore.h"
#include "addcodebyjang/effectentitylist.h"
#include "client455_nuclear_registry.h"
#include "client455_nuclear_receiver.h"
#include "userinterface/gamewindow/etcwin/guiminimapwindow.h"
#include "client455_message_dispatch.h"
#include "client455_language.h"
#include "client455_nation_paths.h"
#include "client455_rvp_effects.h"
#include <client455_normal_renderer_math.h>
#include "RTMovie.h"
#include "mss.h"
#include <bcrypt.h>
#include <client455_network_defaults.h>
#pragma comment(lib,"bcrypt.lib")
#include <cstdio>
#include <algorithm>
#include <cstring>
#include <memory>
#include <new>
#include <stdexcept>
#include <string>
#include <vector>
extern CMainApp g_MainApp;
static unsigned checks=0,warnings=0;
static void check(bool ok,const char* why){++checks;if(!ok)throw std::runtime_error(why);}
static void phase(const char* name){std::fprintf(stderr,"phase:%s checks=%u\n",name,checks);std::fflush(stderr);}
static std::vector<BYTE> cryptOracle(const BYTE* key,const std::vector<BYTE>& plain){
    BCRYPT_ALG_HANDLE algorithm=nullptr;BCRYPT_KEY_HANDLE handle=nullptr;std::vector<BYTE> out(plain.size());ULONG count=0;BYTE iv[16]={};
    if(BCryptOpenAlgorithmProvider(&algorithm,BCRYPT_AES_ALGORITHM,nullptr,0)<0||BCryptSetProperty(algorithm,BCRYPT_CHAINING_MODE,reinterpret_cast<PUCHAR>(const_cast<wchar_t*>(BCRYPT_CHAIN_MODE_CBC)),sizeof(BCRYPT_CHAIN_MODE_CBC),0)<0||BCryptGenerateSymmetricKey(algorithm,&handle,nullptr,0,const_cast<PUCHAR>(key),24,0)<0)throw std::runtime_error("independent CNG key");
    if(BCryptEncrypt(handle,const_cast<PUCHAR>(plain.data()),static_cast<ULONG>(plain.size()),nullptr,iv,16,out.data(),static_cast<ULONG>(out.size()),&count,0)<0||count!=plain.size())throw std::runtime_error("independent CNG encryption");
    BCryptDestroyKey(handle);BCryptCloseAlgorithmProvider(algorithm,0);return out;
}
static std::vector<BYTE> wireOracle(const BYTE* key,BYTE opcode,const std::vector<BYTE>& body){std::vector<BYTE> plain={BYTE(body.size()+4),0,60,opcode};plain.insert(plain.end(),body.begin(),body.end());const auto size=plain.size();plain.resize((size+15)&~std::size_t(15));auto cipher=cryptOracle(key,plain);cipher.insert(cipher.begin(),{BYTE(cipher.size()+3),BYTE((cipher.size()+3)>>8),BYTE(plain.size()-size)});return cipher;}
static void warning(char* value){++warnings;std::fprintf(stderr,"warning:%s\n",value);}
static void error(char* value){throw std::runtime_error(value);}
static bool same(const float* a,const float* b){return !std::memcmp(a,b,12);}
template<class Tag,typename Tag::Type Member>struct MemberAccess{friend typename Tag::Type access(Tag){return Member;}};
struct NetworkMember{using Type=CNetworkMgr CMainApp::*;friend Type access(NetworkMember);};
template struct MemberAccess<NetworkMember,&CMainApp::m_cNetworkMgr>;
struct ProgressMember{using Type=CGameProgress* CMainApp::*;friend Type access(ProgressMember);};
template struct MemberAccess<ProgressMember,&CMainApp::m_pGameProgress>;
struct Scope {
    CMainApp* app=g_pMainApp;CGameProgress* progress=g_MainApp.*access(ProgressMember{});BYTE id=g_MainApp.GetGameProgressID();CGUIChatWindow* chat=g_pUiChatWindow;CGUIScreen* screen=g_pUiScreen;
    Scope(){g_pMainApp=&g_MainApp;g_pUiScreen=&gScreen;check((g_MainApp.*access(NetworkMember{})).Create()!=0,"actual offline network Create");}
    void bind(CGameProgress* object){g_MainApp.SetGameProgressID(object?GPI_MAIN_GAME:0);g_MainApp.*access(ProgressMember{})=object;}
    ~Scope(){g_pUiChatWindow=chat;g_MainApp.*access(ProgressMember{})=progress;g_MainApp.SetGameProgressID(id);g_pMainApp=app;g_pUiScreen=screen;(g_MainApp.*access(NetworkMember{})).Destroy();}
};
static unsigned capture(const char* name,CGUIChatWindow* chat=nullptr,RF455CenterMessages* center=nullptr){
    auto* d=GetD3dDevice();check(SUCCEEDED(d->Clear(0,nullptr,D3DCLEAR_TARGET|D3DCLEAR_ZBUFFER,0xff102030,1,0))&&SUCCEEDED(d->BeginScene()),"begin frame");
    RenderAllEffectsList();if(_GetMinimapWindow())_GetMinimapWindow()->Draw();d->SetRenderState(D3DRS_ZENABLE,FALSE);if(chat)for(unsigned i=0;i<4;++i)chat->GetChatBoard455(i)->Draw();if(center)center->Draw();d->SetRenderState(D3DRS_ZENABLE,TRUE);check(SUCCEEDED(d->EndScene()),"end frame");
    IDirect3DSurface9 *target=nullptr,*copy=nullptr;check(SUCCEEDED(d->GetRenderTarget(0,&target)),"target");D3DSURFACE_DESC desc={};target->GetDesc(&desc);check(SUCCEEDED(d->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&copy,nullptr))&&SUCCEEDED(d->GetRenderTargetData(target,copy)),"readback");
    D3DVIEWPORT9 view={};d->GetViewport(&view);check(view.Width==640&&view.Height==480,"viewport");D3DLOCKED_RECT lock={};check(SUCCEEDED(copy->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"lock");FILE* out=std::fopen(name,"wb");check(out!=nullptr,"capture");unsigned pixels=0;
    for(unsigned y=view.Y;y<view.Y+480;++y){const BYTE* line=static_cast<BYTE*>(lock.pBits)+y*lock.Pitch+view.X*4;std::fwrite(line,4,640,out);for(unsigned x=0;x<640;++x){DWORD pixel;std::memcpy(&pixel,line+4*x,4);pixels+=(pixel&0xffffff)!=0x102030;}}
    std::fclose(out);copy->UnlockRect();copy->Release();target->Release();return pixels;
}
static bool playing(const RF455TaggedWaveView& wave){return wave.sample&&AIL_3D_sample_status(static_cast<H3DSAMPLE>(wave.sample))==SMP_PLAYING;}
static std::string text(CGUITextBoard* board){std::string value;for(unsigned i=0;i<board->GetFragmentCount455();++i){const auto* entry=board->GetFragment455(i);if(entry)value+=const_cast<CGUITextInfo*>(entry)->GetText();}return value;}
static void messageCheck(CGUIChatWindow& chat,const char* expected,const char* label){auto actual=text(chat.GetChatBoard455(0));actual.erase(std::remove(actual.begin(),actual.end(),'\n'),actual.end());check(actual.find(expected)!=std::string::npos,label);}
static void clear(CGUIChatWindow& chat,RF455CenterMessages& center){for(unsigned i=0;i<4;++i)chat.GetChatBoard455(i)->Clear();center.Clear();}
struct SpriteOwner{using Type=CSpriteMgr CMainApp::*;friend Type access(SpriteOwner);};template struct MemberAccess<SpriteOwner,&CMainApp::m_cSpriteMgr>;
struct Load{using Type=BOOL(CMainApp::*)();friend Type access(Load);};template struct MemberAccess<Load,&CMainApp::LoadData>;
struct Unload{using Type=BOOL(CMainApp::*)();friend Type access(Unload);};template struct MemberAccess<Unload,&CMainApp::UnloadData>;
struct Level{using Type=DWORD CPlayer::*;friend Type access(Level);};template struct MemberAccess<Level,&CPlayer::m_dwLevel>;
struct Packs{using Type=CObjectPack* CObjectBoard::*;friend Type access(Packs);};template struct MemberAccess<Packs,&CObjectBoard::m_listItemPack>;
struct Boards{using Type=CBaseBoard*(CBoardManager::*)[MAX_BOARD_TYPE];friend Type access(Boards);};template struct MemberAccess<Boards,&CBoardManager::m_listBoard>;
struct InventoryScope{CBoardManager& manager;CBaseBoard* old;CInventoryBoard* owned;InventoryScope(CBoardManager& value):manager(value),old((value.*access(Boards{}))[0]),owned(new CInventoryBoard){check(!old,"uncreated lab board slot");(value.*access(Boards{}))[0]=owned;}~InventoryScope(){(manager.*access(Boards{}))[0]=old;delete owned;}};
struct Send{using Type=_NET_BUFFER* CNetProcess::*;friend Type access(Send);};template struct MemberAccess<Send,&CNetProcess::m_pSendBuffer>;
struct Receive{using Type=_NET_BUFFER* CNetProcess::*;friend Type access(Receive);};template struct MemberAccess<Receive,&CNetProcess::m_pRecvBuffer>;
struct NetOwner{using Type=CNetWorking* CNetProcess::*;friend Type access(NetOwner);};template struct MemberAccess<NetOwner,&CNetProcess::m_pNetwork>;
struct Active{using Type=BYTE(CNetworkMgr::*)[6];friend Type access(Active);};template struct MemberAccess<Active,&CNetworkMgr::m_activeServer455>;
struct Pop{using Type=void(CNetProcess::*)(WORD);friend Type access(Pop);};template struct MemberAccess<Pop,&CNetProcess::_PopRecvMsg>;
struct Transport {
    CNetProcess& process;_NET_BUFFER send,receive;std::vector<char> scratch,receiveScratch;
    _NET_BUFFER* oldSend;_NET_BUFFER* oldReceive;CNetWorking* oldOwner;DWORD oldIndex;WORD oldMax;bool oldAccept;BYTE oldActive;CNetworkMgr& network;
    Transport(CNetworkMgr& net):process(net.m_Process[0]),scratch(10000),receiveScratch(10000),network(net){
        oldSend=process.*access(Send{});oldReceive=process.*access(Receive{});oldOwner=process.*access(NetOwner{});oldIndex=process.m_nIndex;oldMax=process.m_Type.m_wSocketMaxNum;oldAccept=process.m_NetSocket.GetSocket(0)->m_bAccept;oldActive=(network.*access(Active{}))[0];
        check(send.Configure(10000,10000,scratch.data())&&receive.Configure(10000,10000,receiveScratch.data()),"actual codec buffer");process.*access(Send{})=&send;process.*access(Receive{})=&receive;process.*access(NetOwner{})=&net;process.m_nIndex=0;process.m_Type.m_wSocketMaxNum=1;process.m_codec455.initializeDefault(true);process.m_NetSocket.GetSocket(0)->m_bAccept=true;(network.*access(Active{}))[0]=0;
    }
    ~Transport(){process.*access(Send{})=oldSend;process.*access(Receive{})=oldReceive;process.*access(NetOwner{})=oldOwner;process.m_nIndex=oldIndex;process.m_Type.m_wSocketMaxNum=oldMax;process.m_NetSocket.GetSocket(0)->m_bAccept=oldAccept;(network.*access(Active{}))[0]=oldActive;}
    std::vector<BYTE> take(){int n=0;bool empty=false;auto* p=send.GetSendPoint(&n,&empty);if(!p||empty)return {};std::vector<BYTE> out(p,p+n);send.AddPopPos(n);return out;}
    void deliver(BYTE opcode,const std::vector<BYTE>& body){const auto incoming=wireOracle(RF455_DefaultReceiveKey,opcode,body);std::memcpy(receive.GetPushPos(),incoming.data(),incoming.size());receive.AddPushPos(static_cast<DWORD>(incoming.size()));(process.*access(Pop{}))(0);check(receive.GetTotalPush()==receive.GetTotalPop(),"real encrypted receive ring consumed");}
};
struct Analyze{using Type=bool(CNetworkMgr::*)(DWORD,DWORD,_MSG_HEADER*,char*);friend Type access(Analyze);};template struct MemberAccess<Analyze,&CNetworkMgr::DataAnalysis>;
static bool packet(CNetworkMgr& network,BYTE opcode,std::vector<BYTE> body){_MSG_HEADER header={};header.m_wSize=static_cast<WORD>(body.size()+4);header.m_byType[0]=60;header.m_byType[1]=opcode;return (network.*access(Analyze{}))(0,0,&header,reinterpret_cast<char*>(body.data()));}
static std::vector<BYTE> point(BYTE race,BYTE index,const float* value){std::vector<BYTE> out(14);out[0]=race;out[1]=index;std::memcpy(out.data()+2,value,12);return out;}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"actual language");InitR3Engine();SetWarningMessageProc(warning);SetErrorMessageProc(error);
    auto* state=GetR3State();state->mScreenXsize=640;state->mScreenYsize=480;state->mbFullScreen=FALSE;ForceFullScreen();check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"D3D/fonts");R3SetViewPort(0,0,640,480);g_pUiSpriteMgr=&(g_MainApp.*access(SpriteOwner{}));check((g_MainApp.*access(Load{}))()!=0,"actual sprite LoadData");
    Scope scope;auto& network=g_MainApp.*access(NetworkMember{});check(dynamic_cast<CNetMsgProcessor_Nuclear*>(network.GetNetMsgProcessor(NMP_NUCLEAR))!=nullptr,"ordinary real Nuclear processor factory");
    auto game=std::unique_ptr<CGP_MainGame>(new CGP_MainGame);scope.bind(game.get());auto& registry=game->Nuclear455();check(RF455_GetNuclearContainer()==&registry&&&g_MainApp.Nuclear455()==&registry,"MainGame owns and binds registry");
    auto& map=game->MiniMap455();auto* oldMap=g_pUiMinimapWindow;g_pUiMinimapWindow=&map;map.SetPos(30,20);map.Init();map.Show(TRUE);RECT bounds={-100,-200,300,600};map.SetMapBound(bounds);map.SetNuclearMapGeometry455(400,400,10,-20);
    auto& chat=game->ChatWindow455();auto& center=game->CenterMessages455();chat.InitializeChat455();g_pUiChatWindow=&chat;for(unsigned i=0;i<4;++i){auto* b=chat.GetChatBoard455(i);b->SetPos(15+(i%2)*320,25+(i/2)*220);b->SetSize(290,180);b->SetMargin(3,3);b->Show(TRUE);}
    auto& items=RF455_GameItems();check(items.loadFiles("item.edf","nd-zh-tw.edf","quest.edf","character.edf","base.edf","zh-tw.edf"),"actual EDF items");
    RF455_PrepareTaggedAudio(state->SoundPath);check(InitR3SoundSystem(".\\Snd\\WaveList.spt")!=0,"Miles");SetGlobalWavVolume(0);auto& audio=g_MainApp.TaggedAudio455();check(audio.Open(".\\Snd\\WaveList.spt",state->SoundPath),"tagged audio");state->mSoundOn=TRUE;
    unsigned pixels[4]={},drain=0;
    {
        ChInterface renderer;renderer.InitCharacter(GetD3dDevice());CCamera camera;g_pCamera=&camera;std::unique_ptr<CLand> land(new CLand);check(land->Create()&&land->LoadLevel(".\\Map\\neutralAS1\\neutralAS1.bsp"),"actual BSP");
        D3DXVECTOR3 eye(0,120,-220),focus(0,0,0),up(0,1,0);D3DXMatrixLookAtLH(&state->mMatView,&eye,&focus,&up);D3DXMatrixInverse(&state->mInvMatView,nullptr,&state->mMatView);D3DXMatrixPerspectiveFovLH(&state->mMatProj,D3DX_PI/3,640.f/480,1,30000);D3DXMatrixMultiply(&state->mMatViewProj,&state->mMatView,&state->mMatProj);GetD3dDevice()->SetTransform(D3DTS_VIEW,&state->mMatView);GetD3dDevice()->SetTransform(D3DTS_PROJECTION,&state->mMatProj);gMouse.x=320;gMouse.y=240;
        CreateEffectsList(".\\Effect\\EffectEntityList.spt");CreateMagicSptList(".\\Effect\\MagicSptList.spt");R3SetLoopTime(1.0/30);CAvatar avatar;auto* oldAvatar=g_pAvatar;g_pAvatar=&avatar;avatar.SetRace(1);avatar.SetStatusCode455(10);avatar.SetClientStage455(3);avatar.*access(Level{})=24;auto* manager=_GetGBM();RF455_SystemMessageCounters()={};
        Transport transport(network);auto* processor=network.GetNetMsgProcessor(NMP_NUCLEAR);_MSG_HEADER invalid={};invalid.m_wSize=3;invalid.m_byType[0]=60;BYTE zero=0;check(!processor->AnalysisServerPacket(&invalid,reinterpret_cast<char*>(&zero)),"short header rejected");invalid.m_wSize=5;invalid.m_byType[0]=59;check(!processor->AnalysisServerPacket(&invalid,reinterpret_cast<char*>(&zero)),"wrong group rejected");check(!packet(network,1,{0})&&!packet(network,2,{0})&&!packet(network,255,{0}),"unknown opcodes rejected");
        for(BYTE opcode:{BYTE(0),BYTE(3),BYTE(4),BYTE(5),BYTE(6),BYTE(7),BYTE(8),BYTE(9),BYTE(10)}){_MSG_HEADER h={};h.m_wSize=4;h.m_byType[0]=60;h.m_byType[1]=opcode;check(!processor->AnalysisServerPacket(&h,nullptr),"null/truncated payload rejected before mutation");}check(!registry.Size(),"malformed packets do not create records");
        float pos[3]={60,10,180},other[3]={80,20,160};manager->SetRequestProcessState(TRUE);auto before=RF455_SystemMessageCounters().main;transport.deliver(4,{0,0});check(!manager->IsRequestProcess()&&registry.Size()==1&&!registry.Find(0,0)->countdown&&RF455_SystemMessageCounters().main==before,"opcode4 actual encrypted receive ring/local race division and level24 no notice");
        avatar.*access(Level{})=25;check(packet(network,4,{1,1})&&registry.Find(1,1)->countdown==9&&RF455_SystemMessageCounters().main==before+1,"opcode4 foreign countdown9 and level25 C15");clear(chat,center);
        std::vector<BYTE> ownPosition(17,0);std::memcpy(ownPosition.data()+4,pos,12);ownPosition[16]=0;check(packet(network,3,ownPosition)&&same(registry.Position(0,0),pos)&&map.NuclearMarker455(0).GetAddedObjectNum()==3,"opcode3 own race real lookup and actual marker display");pixels[0]=capture("receive-marker.bgra");
        manager->SetRequestProcessState(TRUE);check(packet(network,0,{0})&&registry.Aiming().pending&&registry.Aiming().effectHandle&&!manager->IsRequestProcess(),"result0 actual guard CE7 and aiming");auto aimingHandle=registry.Aiming().effectHandle;before=RF455_SystemMessageCounters().main;check(packet(network,0,{0})&&registry.Aiming().effectHandle==aimingHandle&&RF455_SystemMessageCounters().main==before+1,"repeat result0 CE7 without restart");
        avatar.EnableCharacterFlags455(1);manager->SetRequestProcessState(TRUE);check(packet(network,0,{1})&&!registry.Aiming().pending&&!registry.Aiming().effectHandle&&map.NuclearMarker455(0).GetAddedObjectNum()==0&&manager->IsRequestProcess()&&transport.take().empty(),"blocked result clears/hides/CE6 before serial branch and retains request flag");avatar.DisableCharacterFlags455(1);clear(chat,center);
        for(BYTE result:{BYTE(3),BYTE(4),BYTE(5),BYTE(6),BYTE(7),BYTE(8),BYTE(9),BYTE(10),BYTE(11),BYTE(12),BYTE(255)}){manager->SetRequestProcessState(TRUE);before=RF455_SystemMessageCounters().main;check(packet(network,0,{result})&&!manager->IsRequestProcess()&&RF455_SystemMessageCounters().main==before+1,"error result clears request and emits actual localized message");clear(chat,center);}
        manager->SetOrgObject(1,0,0,nullptr);manager->SetRequestProcessState(FALSE);check(packet(network,0,{1})&&!manager->IsRequestProcess()&&transport.take().empty(),"result1 absent original item sends nothing");
        InventoryScope inventoryScope(*manager);auto* inventory=dynamic_cast<CInventoryBoard*>(manager->GetBoard(0));check(inventory!=nullptr,"actual inventory board owner");inventory->CObjectBoard::Create(0,1,1);check(inventory->CObjectBoard::AddPack(0),"actual source object pack");auto* object=new CBoardObject;object->SetItem455(items.create(0,33,0));check(object->GetItem455()!=nullptr,"actual nuclear EDF payload");auto* item=dynamic_cast<RF455BasicItem*>(object->GetItem455());check(item&&item->rawData().size>88&&item->rawData().data[88]==33,"actual type33 uses empty4757D0 branch");item->header().serial=0x1234abcd;
        check((inventory->*access(Packs{}))[0].Add(0,object),"actual inventory socket owns typed nuclear object");manager->SetOrgObject(0,0,0,object);const bool accepted=packet(network,0,{1});const auto sent=transport.take();check(accepted&&manager->IsRequestProcess()&&sent.size()==19&&sent==wireOracle(RF455_DefaultSendKey,1,{0xcd,0xab}),"result1 lowWORD original serial/real AES192 packet19 equals independent CNG");
        CBoardObject backup;backup.SetItem455(items.create(0,0,0));check(backup.GetItem455()!=nullptr,"different real backup payload");backup.GetItem455()->header().serial=0x98766543;manager->SetOperationObject455(&backup);
        check(packet(network,0,{1})&&transport.take()==wireOracle(RF455_DefaultSendKey,1,{0xcd,0xab}),"original serial is sent even with a different nonempty hover backup");
        check(packet(network,0,{0})&&registry.Aiming().pending,"arm while backup retained");before=RF455_SystemMessageCounters().main;
        check(packet(network,0,{2})&&manager->GetOrgObject()==object&&manager->GetOrgBoardType()==0&&registry.Aiming().pending&&RF455_SystemMessageCounters().main==before,"result2 nonempty hover backup preserves original operation/aim and doesnot emit C1A");manager->SetOperationObject455(nullptr);
        check(packet(network,0,{0})&&registry.Aiming().pending,"arm before result2 with empty cursor");before=RF455_SystemMessageCounters().main;
        check(packet(network,0,{2})&&avatar.UsingItem455().field4Known&&avatar.UsingItem455().get()==0xffffffff&&manager->GetOrgBoardType()==255&&map.NuclearMarker455(0).GetAddedObjectNum()==3&&inventory->GetObject(0,0)==object&&object->GetItem455()==item&&!registry.Aiming().pending&&!registry.Aiming().effectHandle&&RF455_SystemMessageCounters().main==before+1,"result2 actual inventory completion clears use lane/operation and C1A even empty cursor before marker;doesnot consume item");pixels[1]=capture("receive-use-result.bgra",&chat,&center);clear(chat,center);
        manager->SetOrgObject(1,0,0,nullptr);check(packet(network,7,point(0,0,pos))&&registry.Find(0,0)->radar&&audio.Inspect(277034).tag==2,"opcode7 position then radar tag2");check(packet(network,5,{0,0x77,0x66,0x55,0})&&registry.Find(0,0)->launch,"opcode5 index comes from byte4");
        check(packet(network,0,{0})&&registry.Aiming().pending,"aim before impact");auto heldAim=registry.Aiming().effectHandle;check(packet(network,6,{0,0})&&!registry.Aiming().pending&&registry.Aiming().effectHandle==heldAim&&!registry.Find(0,0)->radar&&registry.Find(0,0)->impact&&map.NuclearMarker455(0).GetAddedObjectNum()==0,"opcode6 pending0 retains aim effect,stops record radar,hides local marker,starts impact");
        for(unsigned i=1;i<=16;++i){R3SetTime(i/30.0);ClearDynamicLight();FrameMoveAllEffectsList();}pixels[2]=capture("receive-effects.bgra");registry.Aiming().Clear();
        manager->SetRequestProcessState(TRUE);check(packet(network,8,{1,1})&&!registry.Find(1,1)&&manager->IsRequestProcess(),"opcode8 remove does not clear request flag");check(packet(network,9,{0,0})&&!registry.Find(0,0)&&manager->IsRequestProcess(),"opcode9 same removal contract");
        std::vector<BYTE> list={3};for(const auto& row:{point(0,0,pos),point(1,1,other),point(2,2,std::array<float,3>{7,0,9}.data())})list.insert(list.end(),row.begin(),row.end());check(packet(network,10,list)&&registry.Size()==3&&same(registry.Position(0,0),pos)&&same(registry.Position(1,1),other)&&!registry.Position(2,2)[0]&&!registry.Position(2,2)[1]&&!registry.Position(2,2)[2],"opcode10 packed14/all components nonzero position filter");check(packet(network,10,{10})&&registry.Size()==3,"count10 ignored without clearing or reading entries");check(packet(network,10,{0})&&!registry.Size(),"count0 clears all records");
        map.Show(FALSE);clear(chat,center);phase("drain");while((GetEffectListCnt()||GetMagicListCnt())&&drain<1200){++drain;R3SetTime(1+drain/30.0);ClearDynamicLight();FrameMoveAllEffectsList();}check(!GetEffectListCnt()&&!GetMagicListCnt()&&drain<1200,"all actual effects drain");pixels[3]=capture("receive-cleared.bgra");check(!pixels[3],"cleared effect/UI pixels");
        check(packet(network,4,{0,0}),"record before owner release");game->ReleaseNuclear455();check(!RF455_GetNuclearContainer(),"actual stage release unbinds its owned registry");
        {auto next=std::unique_ptr<CGP_MainGame>(new CGP_MainGame);check(RF455_GetNuclearContainer()==&next->Nuclear455()&&!next->Nuclear455().Size(),"next actual MainGame has fresh bound registry");}check(!RF455_GetNuclearContainer(),"uncreated own stage cleanup unbinds;target early-Destroy leak remains unaccepted");
        DestroyEffectsList();DestroyMagicSptList();check(land->Destroy()!=0,"world teardown");RTMovieRelease();g_pCamera=nullptr;g_pAvatar=oldAvatar;
    }
    audio.Close();ReleaseR3SoundSystem();scope.bind(nullptr);g_pUiChatWindow=nullptr;g_pUiMinimapWindow=oldMap;game.reset();(g_MainApp.*access(Unload{}))();gSpriteMgr.UnloadTargetSprites455();RF455_ReleaseNormalCharacterSharedResources();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();
    FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"result");std::fprintf(out,"{\"status\":\"PASS\",\"checks\":%u,\"warnings\":%u,\"ordinary_factory_and_DataAnalysis\":true,\"all_nine_opcodes\":true,\"real_MainGame_registry_owner\":true,\"original_serial_plain6_encrypted19_CNG\":true,\"real_encrypted_receive_ring\":true,\"hover_backup_preserves_operation\":true,\"actual_type33_inventory_use_callback\":true,\"player_use_only_field4_clear\":true,\"actual_registry_lookup_to_MiniMap\":true,\"guard_blocked_errors_repeat\":true,\"real_BSP_effects_Miles\":true,\"GPU_frames\":4,\"pixels\":[%u,%u,%u,%u],\"drain_ticks\":%u,\"full_socket_auth\":false,\"full_inventory_use\":false,\"full_stage_lifecycle\":false,\"full_world_effects\":false,\"full_client\":false}\n",checks,warnings,pixels[0],pixels[1],pixels[2],pixels[3],drain);std::fclose(out);return 0;
}
static LONG filter(EXCEPTION_POINTERS* p){if(p->ExceptionRecord->ExceptionCode==0xe06d7363)return EXCEPTION_CONTINUE_SEARCH;std::fprintf(stderr,"exception=%08lx ownRVA=%08lx checks=%u\n",p->ExceptionRecord->ExceptionCode,DWORD(p->ExceptionRecord->ExceptionAddress)-DWORD(GetModuleHandleA(nullptr)),checks);return EXCEPTION_EXECUTE_HANDLER;}
static int guarded(){__try{return run();}__except(filter(GetExceptionInformation())){return 99;}}
int main(){try{return guarded();}catch(const std::exception& e){std::fprintf(stderr,"registry:%s checks=%u\n",e.what(),checks);return 1;}}
