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
#include "client455_chat_profile.h"
#include "client455_font.h"
#include "client455_language.h"
#include "client455_nation_paths.h"
#include "client455_text_metrics.h"
#include <cstdio>
#include <cstring>
#include <fstream>
#include <mbctype.h>
#include <memory>
#include <stdexcept>
#include <string>
extern CMainApp g_MainApp;
static unsigned checks=0,profiles=0,rows=0;
static void check(bool value,const char* why){++checks;if(!value)throw std::runtime_error(why);}
template<class Tag,typename Tag::Type Member>struct MemberAccess{friend typename Tag::Type access(Tag){return Member;}};
struct NetworkMember{using Type=CNetworkMgr CMainApp::*;friend Type access(NetworkMember);};
template struct MemberAccess<NetworkMember,&CMainApp::m_cNetworkMgr>;
struct NetworkScope{CNetworkMgr& network=g_MainApp.*access(NetworkMember{});NetworkScope(){check(network.Create()!=0,"actual offline client network Create");}~NetworkScope(){network.Destroy();}};
static unsigned capture(CGUIChatWindow& window,const char* name){
    auto* d=GetD3dDevice();check(SUCCEEDED(d->Clear(0,nullptr,D3DCLEAR_TARGET,0xff102030,1,0))&&SUCCEEDED(d->BeginScene()),"begin");d->SetRenderState(D3DRS_ZENABLE,FALSE);
    for(unsigned pane=0;pane<4;++pane)window.GetChatBoard455(pane)->Draw();d->SetRenderState(D3DRS_ZENABLE,TRUE);check(SUCCEEDED(d->EndScene()),"end");
    IDirect3DSurface9 *target=nullptr,*copy=nullptr;check(SUCCEEDED(d->GetRenderTarget(0,&target)),"target");D3DSURFACE_DESC desc={};target->GetDesc(&desc);check(SUCCEEDED(d->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&copy,nullptr))&&SUCCEEDED(d->GetRenderTargetData(target,copy)),"readback");
    D3DVIEWPORT9 view={};d->GetViewport(&view);check(view.Width==640&&view.Height==480,"viewport");D3DLOCKED_RECT lock={};check(SUCCEEDED(copy->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"lock");FILE* file=std::fopen(name,"wb");check(file!=nullptr,"frame");unsigned pixels=0;
    for(unsigned y=view.Y;y<view.Y+480;++y){const auto* line=static_cast<BYTE*>(lock.pBits)+y*lock.Pitch+view.X*4;std::fwrite(line,4,640,file);for(unsigned x=0;x<640;++x){DWORD value;std::memcpy(&value,line+x*4,4);pixels+=(value&0xffffff)!=0x102030;}}
    std::fclose(file);copy->UnlockRect();copy->Release();target->Release();return pixels;
}
static void clear(CGUIChatWindow& window){for(unsigned pane=0;pane<4;++pane)window.GetChatBoard455(pane)->Clear();}
static std::string text(CGUITextBoard* board,unsigned index){const auto* entry=board->GetFragment455(index);return entry?const_cast<CGUITextInfo*>(entry)->GetText():"";}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"real language");InitR3Engine();auto* state=GetR3State();state->mScreenXsize=640;state->mScreenYsize=480;state->mbFullScreen=FALSE;ForceFullScreen();check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"actual D3D fonts");R3SetViewPort(0,0,640,480);NetworkScope network;
    check(!RF455_GetChatProfile(),"no stage profile before constructor");std::unique_ptr<CGP_MainGame> stage(new CGP_MainGame);auto& profile=stage->ChatProfile455();auto& window=stage->ChatWindow455();check(RF455_GetChatProfile()==&profile&&!profile.Ready(),"actual stage owns uninitialized profile");
    const int ambient=_getmbcp();check(_setmbcp(0)==0,"SBCS reference oracle mode");
    std::ifstream catalog("oracles.txt");unsigned nation;std::string input,oracle;
    while(catalog>>nation>>input>>oracle){
        profile.Release();check(profile.Load(nation,input.c_str()),"real script override load");std::ifstream expected(oracle);unsigned index,hc,bc,hs,bs,hf,bf,count;std::string hex;unsigned inProfile=0;
        while(expected>>index>>hc>>bc>>hs>>bs>>hf>>bf>>count>>hex){
            unsigned char bytes[16]={};if(hex!="-")for(unsigned i=0;i<hex.size()/2;++i){unsigned value=0;std::sscanf(hex.substr(i*2,2).c_str(),"%2x",&value);bytes[i]=BYTE(value);}
            const auto& h=profile.Header(index);const auto& b=profile.Body(index);const auto& p=profile.Prefix(index);
            check(h.color==hc&&b.color==bc&&h.size==hs&&b.size==bs&&h.style==hf&&b.style==bf&&h.scale==1&&b.scale==1&&p.length==count&&!std::memcmp(p.text,bytes,16),"pinned script/fallback record oracle");++rows;++inProfile;
        }
        check(inProfile==36&&profile.ScriptRecords()+profile.FallbackRecords()==36,"all36 records loaded");++profiles;
    }
    check(profiles==8&&rows==288,"eight actual script inputs");profile.Release();check(profile.Load(2,"partial-profile.txt"),"partial record fixture");
    check(profile.Header(0).color==0xff00ff11&&profile.Prefix(0).length==15&&!std::strcmp(profile.Prefix(0).text,"abcdefghijklmno"),"clamp andprefix15");
    check(profile.Header(13).style==32&&profile.Header(13).size==12&&profile.Body(13).style==0&&profile.Body(13).size==0&&profile.Body(13).color==0xffffffff,"fallback13 preserves doubleheader write");
    check(profile.Header(19).color==0xffff0000&&profile.Header(2).color==0xffffa670,"China19 and incomplete row fallback");profile.Release();check(profile.Load(0,"partial-profile.txt")&&profile.Header(19).color==0xffffd0a0,"othercountry19 fallback");
    profile.Release();check(_setmbcp(949)==0&&profile.Load(0,"dbcs-profile.txt"),"DBCS prefix fixture");check(profile.Prefix(0).length==15&&std::strlen(profile.Prefix(0).text)==14,"stored15 prefix can copy14DBCS bytes");check(_setmbcp(ambient)==0,"restore ambient mode");
    profile.Release();check(!profile.Load(0,"not-present.txt")&&!profile.Ready(),"missing script refusal");window.InitializeChat455();check(profile.Ready()&&profile.ScriptRecords()>0,"actual window initializes actual stage profile");
    {std::ofstream high("high-mask.ini");high<<"[ChatMode]\nAll=1\nParty=2\nGuild=4\nSystem=8\n[DefModeOn]\nAll=2147483648\n";}
    window.InitializeChat455("./high-mask.ini");char highText[32]={};GetPrivateProfileStringA("DefModeOn","All","",highText,sizeof(highText),"./high-mask.ini");check(!std::strcmp(highText,"-2147467265"),"high DWORD settings persist target signed decimal");window.InitializeChat455();
    for(unsigned pane=0;pane<4;++pane){DWORD mask=0;for(unsigned category=0;category<14;++category)if(window.GetChatFilter455(category,pane))mask|=1u<<category;check(mask==(pane?((1u<<pane)|(1u<<5)):0x3fff),"default filter masks with forcedown category");auto* board=window.GetChatBoard455(pane);board->SetPos(15+(pane%2)*320,25+(pane/2)*220);board->SetSize(290,180);board->SetMargin(3,3);board->Show(TRUE);}
    check(GetPrivateProfileIntA("DefModeOn","All",0,"./DataTable/GameSetting.ini")==0x3fff,"ordinary DefModeOn persistence");window.SetChatFilterKernel455(1,0,1);check(window.GetChatFilter455(1,1)==1,"own pane category cannot disable");window.SetChatFilterKernel455(12,2,0);check(window.GetChatFilter455(12,0)==2,"raw DWORD filter retained");
    const char* c1a=RF455_GetNormalLanguagePack()->get(0xc1a);window.InsertText455("[1]",c1a,2,3);
    check(window.GetChatBoard455(0)->GetFragmentCount455()==1&&window.GetChatBoard455(3)->GetFragmentCount455()==1&&!window.GetChatBoard455(1)->GetFragmentCount455()&&!window.GetChatBoard455(2)->GetFragmentCount455(),"actual system category routing0and3");check(text(window.GetChatBoard455(0),0)==std::string("[1] : ")+c1a,"actual formatted C1A text");const auto pixels1=capture(window,"chat-system.bgra");check(pixels1>0,"actual system GPU");
    window.InsertText455("[2]","next",2,3);check(window.GetChatBoard455(0)->GetFragmentCount455()==3&&text(window.GetChatBoard455(0),1)=="\n","existing board gets separator header");
    clear(window);window.InsertText455("Player","Party message",3,1);check(text(window.GetChatBoard455(0),0)==std::string(profile.Prefix(3).text)+" "&&text(window.GetChatBoard455(1),1)=="Player : Party message"&&!window.GetChatBoard455(2)->GetFragmentCount455(),"real marker separate from actual body");const auto pixels2=capture(window,"chat-party.bgra");check(pixels2>0,"actual party GPU");
    clear(window);for(BYTE pane=0;pane<4;++pane)window.SetChatFilterKernel455(13,0,pane);window.InsertChatRaw455("raw filtered",26,13);check(!window.GetChatBoard455(0)->GetFragmentCount455(),"raw method doesnot bypass filters for26");window.InsertText455("Friend","Online",26,13);for(unsigned pane=0;pane<4;++pane)check(window.GetChatBoard455(pane)->GetFragmentCount455()==1,"style26 bypasses all4 filters");const auto pixels3=capture(window,"chat-forced.bgra");check(pixels3>0,"actual forced category GPU");
    clear(window);std::string wrapped="unchanged";auto* first=window.GetChatBoard455(0);const auto oldWidth=first->GetSizeX();check(!window.WrapChat455("abc",oldWidth,1,wrapped)&&wrapped=="unchanged","prefix width failure leaves output unchanged");check(window.WrapChat455("a\nb",0,1,wrapped)&&wrapped=="a\n\nb","explicit newline target doublebreak");
    first->SetSize(RF455_TextWidth("W")+2*first->GetMarginX(),180);check(window.WrapChat455("WW",0,0,wrapped)&&wrapped=="W\nW","exact glyph width wrapping");first->SetSize(1+2*first->GetMarginX(),180);check(window.WrapChat455("WABC",0,1,wrapped)&&wrapped.empty(),"unfittable glyph drops remainder andterminates");first->SetSize(oldWidth,180);
    const std::string message=std::string(c1a)+" alpha beta gamma delta alpha beta gamma delta alpha beta gamma delta";window.InsertText455("Player",message.c_str(),3,1);check(text(first,1).find('\n')!=std::string::npos,"actual wrapping produces newlines");const auto pixels4=capture(window,"chat-wrapped.bgra");check(pixels4>0,"actual wrapped GPU");clear(window);const auto pixels5=capture(window,"chat-cleared.bgra");check(!pixels5,"all four real panes clear");
    stage.reset();check(!RF455_GetChatProfile(),"stage profile registry unbound");g_MainApp.ReleaseR3D3D();ReleaseR3Engine();FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"result");
    std::fprintf(out,"{\"status\":\"PASS\",\"checks\":%u,\"actual_MainGame_profile\":true,\"actual_window_4panes\":true,\"real_script_inputs\":%u,\"profile_records\":%u,\"styles\":36,\"categories\":14,\"prefix_bytes\":18,\"font_bytes\":16,\"fallback13_quirk\":true,\"fallback19_country\":true,\"ambient_prefix_DBCS\":true,\"settings_default_masks\":true,\"DefModeOn_persisted\":true,\"ordinary_typed_Insert\":true,\"real_C1A_direct_input\":true,\"wrap_and_newline_quirks\":true,\"style26_bypass\":true,\"GPU_frames\":5,\"pixels\":[%u,%u,%u,%u,%u],\"all_pane_records_released\":true,\"profile_unbound\":true,\"legacy_uncreated_stage_teardown_gap\":true,\"full_chat_UI\":false,\"legacy_callers_migrated\":false,\"full_C1A_dispatch\":false,\"live_hover_cancel\":false,\"full_client\":false}\n",checks,profiles,rows,pixels1,pixels2,pixels3,pixels4,pixels5);std::fclose(out);return 0;
}
static LONG filter(EXCEPTION_POINTERS* p){if(p->ExceptionRecord->ExceptionCode==0xe06d7363)return EXCEPTION_CONTINUE_SEARCH;std::fprintf(stderr,"exception=%08lx ownRVA=%08lx checks=%u\n",p->ExceptionRecord->ExceptionCode,DWORD(p->ExceptionRecord->ExceptionAddress)-DWORD(GetModuleHandleA(nullptr)),checks);return EXCEPTION_EXECUTE_HANDLER;}
static int guarded(){__try{return run();}__except(filter(GetExceptionInformation())){return 99;}}
int main(){try{return guarded();}catch(const std::exception& e){std::fprintf(stderr,"chat:%s checks=%u\n",e.what(),checks);return 1;}}
