#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "input/imeedit.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "userinterface/gamewindow/guiinventorywindow.h"
#include "mainapp.h"
#include "gameprogress/cgp_maingame.h"
#include "gameprogress/cgp_login.h"
#include "client455_message_dispatch.h"
#include "client455_icon_links.h"
#include "client455_font.h"
#include "client455_language.h"
#include "client455_nation_paths.h"
#include "client455_player_status.h"
#include "client455_rvp_effects.h"
#include <client455_normal_renderer_math.h>
#include "addcodebyjang/effectcore.h"
#include "addcodebyjang/effectentitylist.h"
#include "RTMovie.h"
#include "mss.h"
#include <cstdio>
#include <cstring>
#include <memory>
#include <stdexcept>
#include <string>
extern CMainApp g_MainApp;
static unsigned checks=0;
static void check(bool value,const char* why){++checks;if(!value)throw std::runtime_error(why);}
static void warning(char* message){std::fprintf(stderr,"warning:%s\n",message);}
static void error(char* message){throw std::runtime_error(message);}
template<class Tag,typename Tag::Type Member>struct MemberAccess{friend typename Tag::Type access(Tag){return Member;}};
struct NetworkMember{using Type=CNetworkMgr CMainApp::*;friend Type access(NetworkMember);};
template struct MemberAccess<NetworkMember,&CMainApp::m_cNetworkMgr>;
struct ProgressMember{using Type=CGameProgress* CMainApp::*;friend Type access(ProgressMember);};
template struct MemberAccess<ProgressMember,&CMainApp::m_pGameProgress>;
struct Scope {
    CMainApp* app=g_pMainApp;CGameProgress* progress=g_MainApp.*access(ProgressMember{});BYTE id=g_MainApp.GetGameProgressID();CGUIChatWindow* chat=g_pUiChatWindow;CAvatar* avatar=g_pAvatar;CGUIScreen* screen=g_pUiScreen;
    Scope(){g_pMainApp=&g_MainApp;g_pUiScreen=&gScreen;check((g_MainApp.*access(NetworkMember{})).Create()!=0,"actual offline network Create");}
    ~Scope(){g_pAvatar=avatar;g_pUiChatWindow=chat;g_MainApp.*access(ProgressMember{})=progress;g_MainApp.SetGameProgressID(id);g_pMainApp=app;g_pUiScreen=screen;(g_MainApp.*access(NetworkMember{})).Destroy();}
    void bind(BYTE value,CGameProgress* object){g_MainApp.SetGameProgressID(value);g_MainApp.*access(ProgressMember{})=object;}
};
static unsigned capture(const char* name,CGUIChatWindow* chat,RF455CenterMessages* center,RF455LoginMessages* login){
    auto* d=GetD3dDevice();check(SUCCEEDED(d->Clear(0,nullptr,D3DCLEAR_TARGET,0xff102030,1,0))&&SUCCEEDED(d->BeginScene()),"begin frame");
    d->SetRenderState(D3DRS_ZENABLE,FALSE);if(chat)for(unsigned i=0;i<4;++i)chat->GetChatBoard455(i)->Draw();if(center)center->Draw();if(login)login->Draw();d->SetRenderState(D3DRS_ZENABLE,TRUE);check(SUCCEEDED(d->EndScene()),"end frame");
    IDirect3DSurface9 *target=nullptr,*copy=nullptr;check(SUCCEEDED(d->GetRenderTarget(0,&target)),"render target");D3DSURFACE_DESC desc={};target->GetDesc(&desc);
    check(SUCCEEDED(d->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&copy,nullptr))&&SUCCEEDED(d->GetRenderTargetData(target,copy)),"readback");
    D3DVIEWPORT9 view={};d->GetViewport(&view);check(view.Width==640&&view.Height==480,"real viewport");D3DLOCKED_RECT lock={};check(SUCCEEDED(copy->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"lock");
    FILE* out=std::fopen(name,"wb");check(out!=nullptr,"capture file");unsigned pixels=0;
    for(unsigned y=view.Y;y<view.Y+480;++y){const auto* line=static_cast<BYTE*>(lock.pBits)+y*lock.Pitch+view.X*4;std::fwrite(line,4,640,out);for(unsigned x=0;x<640;++x){DWORD pixel;std::memcpy(&pixel,line+4*x,4);pixels+=(pixel&0xffffff)!=0x102030;}}
    std::fclose(out);copy->UnlockRect();copy->Release();target->Release();return pixels;
}
static std::string text(CGUITextBoard* board,unsigned at=0){const auto* entry=board->GetFragment455(at);return entry?const_cast<CGUITextInfo*>(entry)->GetText():"";}
static void clear(CGUIChatWindow& chat){for(unsigned i=0;i<4;++i)chat.GetChatBoard455(i)->Clear();}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"actual Korean NDLanguage");InitR3Engine();SetWarningMessageProc(warning);SetErrorMessageProc(error);
    auto* state=GetR3State();state->mScreenXsize=640;state->mScreenYsize=480;state->mbFullScreen=FALSE;ForceFullScreen();check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"D3D/fonts");R3SetViewPort(0,0,640,480);gScreen.SetSize(640,480);
    Scope scope;auto game=std::unique_ptr<CGP_MainGame>(new CGP_MainGame);auto login=std::unique_ptr<CGP_LogIn>(new CGP_LogIn);auto& chat=game->ChatWindow455();auto& center=game->CenterMessages455();chat.InitializeChat455();g_pUiChatWindow=&chat;
    for(unsigned i=0;i<4;++i){auto* board=chat.GetChatBoard455(i);board->SetPos(15+(i%2)*320,25+(i/2)*220);board->SetSize(290,180);board->SetMargin(3,3);board->Show(TRUE);}
    auto& counts=RF455_SystemMessageCounters();counts={};scope.bind(0,nullptr);_SetSystemMsg("title %d",7);check(!counts.main&&!counts.tutorial&&center.Pending().empty(),"ordinary Title suppresses common/center");
    scope.bind(1,nullptr);_SetSystemMsg("null Login");check(!counts.main&&!*login->SystemMessages455().Primary(),"valid null current Login pointer");scope.bind(1,login.get());
    const auto* language=RF455_GetNormalLanguagePack();const char* c1a=language->get(0xc1a);const char* ce7=language->get(0xce7);
    _SetSystemMsg("%s",c1a);check(!std::strcmp(login->SystemMessages455().Primary(),c1a)&&center.Pending().empty()&&!counts.main,"ordinary Login sink actual member");
    const auto pixels1=capture("dispatch-login.bgra",nullptr,nullptr,&login->SystemMessages455());check(pixels1>0,"visible actual Login message");
    for(unsigned n:{0u,1u,254u,255u,256u,600u}){std::string input(n,'X');auto& messages=login->SystemMessages455();messages.SetPrimary(input.c_str());check(std::strlen(messages.Primary())==(n<255?n:255),"primary256 byte boundary");}
    login->SystemMessages455().SetPrimary("primary");login->SystemMessages455().SetSecondary("secondary");login->SystemMessages455().SetSecondary(nullptr);check(!*login->SystemMessages455().Primary()&&!std::strcmp(login->SystemMessages455().Secondary(),"secondary"),"actual null-secondary clears primary only");
    scope.bind(GPI_MAIN_GAME,game.get());check(RF455_CurrentMessageContext().stage==3&&g_MainApp.GetGameProgress455()==game.get(),"ordinary legacy2 maps targetMainGame3");
    _SetSystemMsg("%s",c1a);check(counts.main==1&&!counts.tutorial&&text(chat.GetChatBoard455(0)).find("[1] : ")==0&&!chat.GetChatBoard455(1)->GetFragmentCount455()&&chat.GetChatBoard455(3)->GetFragmentCount455()==1&&center.Active().size()==1&&center.Pending().empty(),"ordinary main routes actual center andpanes0/3");
    center.FrameMoveAt(timeGetTime(),.05f);const auto pixels2=capture("dispatch-main.bgra",&chat,&center,nullptr);check(pixels2>0,"actual main dispatch GPU");clear(chat);center.Clear();
    RF455_DispatchMessage(RF455_CurrentMessageContext(),"tip",9,0);check(counts.main==2&&const_cast<CGUITextInfo*>(chat.GetChatBoard455(0)->GetFragment455(0))->GetFont()->dwColor==game->ChatProfile455().Body(25).color,"category9 selects style25");clear(chat);
    for(BYTE pane=0;pane<4;++pane)chat.SetChatFilterKernel455(13,0,pane);RF455_DispatchMessage(RF455_CurrentMessageContext(),"forced",13,26);for(unsigned i=0;i<4;++i)check(chat.GetChatBoard455(i)->GetFragmentCount455()==1,"nonzero26 overrides default andbypasses filters");
    const auto pixels3=capture("dispatch-forced.bgra",&chat,nullptr,nullptr);check(pixels3>0,"forced actual panels GPU");clear(chat);
    RF455_DispatchMessage({2,nullptr,&chat},"tutorial kernel",255,255);check(counts.tutorial==1&&counts.main==3&&text(chat.GetChatBoard455(0)).find("[1] : ")==0&&chat.GetChatBoard455(3)->GetFragmentCount455()==1,"selected Tutorial routing ignores args anduses separate counter,not actualTutorial instance");clear(chat);
    counts.main=0x7fffffff;RF455_DispatchMessage(RF455_CurrentMessageContext(),"wrap",3,0);check(counts.main==0x80000000&&text(chat.GetChatBoard455(0)).find("[-2147483648] : ")==0,"DWORD sequence signed header");clear(chat);counts.main=0;
    _SetSystemMsg(static_cast<const char*>(nullptr));check(!counts.main&&center.Pending().empty(),"null Format no operation");
    RF455_ShowDoubleMessage("double");check(center.Active().size()==2&&center.Pending().empty()&&counts.main==1,"double wrapper preserves two centers");center.Clear();clear(chat);
    RF455_ShowOrangeMessage("orange");check(center.Active().front().color==0xffffd200,"orange center color");center.Clear();RF455_ShowFriendMessage("friend");check(center.Pending().empty()&&center.Active().empty()&&counts.main==2,"friend common only");clear(chat);
    auto& runtime=RF455_GameItems();check(runtime.loadFiles("item.edf","nd-zh-tw.edf","quest.edf","character.edf","base.edf","zh-tw.edf"),"real EDF item provider");
    RF455_PrepareTaggedAudio(state->SoundPath);check(InitR3SoundSystem(".\\Snd\\WaveList.spt")!=0,"real Miles driver");SetGlobalWavVolume(0);auto& audio=g_MainApp.TaggedAudio455();check(audio.Open(".\\Snd\\WaveList.spt",state->SoundPath),"actual radar provider/listener");
    unsigned drain=0;
    {
        ChInterface renderer;renderer.InitCharacter(GetD3dDevice());CCamera camera;g_pCamera=&camera;std::unique_ptr<CLand> land(new CLand);check(land->Create()&&land->LoadLevel(".\\Map\\neutralAS1\\neutralAS1.bsp"),"real neutralAS1 BSP");
        D3DXVECTOR3 eye(0,120,-220),focus(0,0,0),up(0,1,0);D3DXMatrixLookAtLH(&state->mMatView,&eye,&focus,&up);D3DXMatrixInverse(&state->mInvMatView,nullptr,&state->mMatView);D3DXMatrixPerspectiveFovLH(&state->mMatProj,D3DX_PI/3,640.f/480,1,30000);D3DXMatrixMultiply(&state->mMatViewProj,&state->mMatView,&state->mMatProj);gMouse.x=320;gMouse.y=240;
        CreateEffectsList(".\\Effect\\EffectEntityList.spt");CreateMagicSptList(".\\Effect\\MagicSptList.spt");CAvatar avatar;g_pAvatar=&avatar;avatar.SetStatusCode455(2);auto* manager=_GetGBM();manager->SetRequestProcessState(TRUE);state->mSoundOn=TRUE;
        const auto before=counts.main;RF455_BeginNuclearSelection();auto& aim=RF455_NuclearAiming();const auto handle=aim.effectHandle;auto wave=audio.Inspect(277034);
        check(!manager->IsRequestProcess()&&aim.pending&&handle&&counts.main==before+1&&center.Active().back().text[0]&&text(chat.GetChatBoard455(0)).find(ce7)!=std::string::npos,"actual CE7/requestclear/start chain");check(wave.sample&&AIL_3D_sample_status(static_cast<H3DSAMPLE>(wave.sample))==SMP_PLAYING,"real Miles radar playing");
        RF455_BeginNuclearSelection();check(aim.effectHandle==handle&&counts.main==before+2&&audio.Inspect(277034).sample==wave.sample,"repeat emits CE7 without restarting effect/audio");R3SetLoopTime(.05f);for(unsigned i=0;i<16;++i){R3SetTime(i*.05f);FrameMoveAllEffectsList();}check(GetEffectListCnt()==6,"six real effect children");
        FILE* sample=std::fopen("metadata-samples.bin","rb");check(sample!=nullptr,"real metadata sample");char magic[4];unsigned n,row[3];check(std::fread(magic,1,4,sample)==4&&!std::memcmp(magic,"MS94",4)&&std::fread(&n,4,1,sample)==1&&std::fread(row,4,3,sample)==3,"selected real item row");std::fclose(sample);
        CGUIInventoryBoard inventory;CBoardObject source;source.SetItem455(runtime.create(row[0],row[1],row[2]));check(inventory.TakeInItem455(0,&source,0)&&source.GetIcon()->UsesTypedIcon455(),"real item and actual typed inventory icon");
        float command[3]={7,8,9};aim.SetPosition(command);clear(chat);center.Clear();const auto cancelBefore=counts.main;
        auto* hovered=manager->SetHoverObject(&source);check(hovered&&hovered!=&source&&hovered->GetItem455()==source.GetItem455(),"ordinary typed hover succeeds with actual Avatar/pending1");
        float zeros[3]={};check(!aim.pending&&!aim.effectHandle&&!std::memcmp(aim.position,zeros,12)&&AIL_3D_sample_status(static_cast<H3DSAMPLE>(wave.sample))==SMP_DONE,"actual C1A cancellation clears position/effect/pending andstops radar");
        check(counts.main==cancelBefore+1&&center.Active().size()==1&&center.Pending().empty()&&!std::strcmp(center.Active().front().text,c1a)&&text(chat.GetChatBoard455(0)).find(c1a)!=std::string::npos,"actual C1A goes through center andactual chat");
        center.FrameMoveAt(timeGetTime(),.05f);const auto pixels4=capture("dispatch-cancel.bgra",&chat,&center,nullptr);check(pixels4>0,"cancel message GPU");manager->SetHoverObject(nullptr);manager->ClearHoverBackups455();g_pAvatar=scope.avatar;
        while((GetEffectListCnt()||GetMagicListCnt())&&drain<300){++drain;FrameMoveAllEffectsList();}check(!GetEffectListCnt()&&!GetMagicListCnt()&&drain<300,"cancelled effects drain");audio.Collect();DestroyEffectsList();DestroyMagicSptList();check(land->Destroy()!=0,"world teardown");RTMovieRelease();g_pCamera=nullptr;
        clear(chat);center.Clear();const auto pixels5=capture("dispatch-cleared.bgra",&chat,&center,nullptr);check(!pixels5,"actual messages clear after cancellation");
        FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"result");std::fprintf(out,"{\"status\":\"PASS\",\"checks\":%u,\"actual_MainApp_context\":true,\"ordinary_formatted_entry\":true,\"actual_Login_member\":true,\"actual_four_chat_panes\":true,\"Tutorial_kernel_only\":true,\"signed_counter\":true,\"live_Avatar_typed_item_hover_cancel\":true,\"real_BSP_effect6_Miles\":true,\"real_C1A_CE7_dispatch\":true,\"repeat_CE7_retains_effect\":true,\"cancelled_effects_drain\":%u,\"GPU_frames\":5,\"pixels\":[%u,%u,%u,%u,%u],\"CE7_game_action_registration\":false,\"full_Login_auth_flow\":false,\"full_Tutorial\":false,\"full_client\":false}\n",checks,drain,pixels1,pixels2,pixels3,pixels4,pixels5);std::fclose(out);
    }
    audio.Close();ReleaseR3SoundSystem();gSpriteMgr.UnloadTargetSprites455();RF455_ReleaseNormalCharacterSharedResources();scope.bind(0,nullptr);g_pUiChatWindow=nullptr;login.reset();game.reset();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();return 0;
}
static LONG filter(EXCEPTION_POINTERS* p){if(p->ExceptionRecord->ExceptionCode==0xe06d7363)return EXCEPTION_CONTINUE_SEARCH;std::fprintf(stderr,"exception=%08lx ownRVA=%08lx checks=%u\n",p->ExceptionRecord->ExceptionCode,DWORD(p->ExceptionRecord->ExceptionAddress)-DWORD(GetModuleHandleA(nullptr)),checks);return EXCEPTION_EXECUTE_HANDLER;}
static int guarded(){__try{return run();}__except(filter(GetExceptionInformation())){return 99;}}
int main(){try{return guarded();}catch(const std::exception& e){std::fprintf(stderr,"dispatch:%s checks=%u\n",e.what(),checks);return 1;}}
