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
#include "client455_center_messages.h"
#include "client455_font.h"
#include "client455_language.h"
#include "client455_nation_paths.h"
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <memory>
#include <mbstring.h>
#include <mbctype.h>
#include <locale.h>
#include <stdexcept>
#include <string>
#include <vector>
extern CMainApp g_MainApp;
static unsigned checks=0;
static void check(bool value,const char* why){++checks;if(!value)throw std::runtime_error(why);}
template<class Tag,typename Tag::Type Member>struct MemberAccess{friend typename Tag::Type access(Tag){return Member;}};
struct NetworkMember{using Type=CNetworkMgr CMainApp::*;friend Type access(NetworkMember);};
template struct MemberAccess<NetworkMember,&CMainApp::m_cNetworkMgr>;
struct NetworkScope{CNetworkMgr& network=g_MainApp.*access(NetworkMember{});NetworkScope(){check(network.Create()!=0,"actual offline network owner initialization");}~NetworkScope(){network.Destroy();}};
static bool closeFloat(float a,float b){return std::fabs(a-b)<.0001f;}
static unsigned capture(RF455CenterMessages& messages,const char* name){
    auto* d=GetD3dDevice();check(SUCCEEDED(d->Clear(0,nullptr,D3DCLEAR_TARGET,0xff102030,1,0))&&SUCCEEDED(d->BeginScene()),"scene begin");
    messages.Draw();DWORD z=0;d->GetRenderState(D3DRS_ZENABLE,&z);check(z==D3DZB_TRUE,"actual draw restores depth on");check(SUCCEEDED(d->EndScene()),"scene end");
    IDirect3DSurface9 *target=nullptr,*copy=nullptr;check(SUCCEEDED(d->GetRenderTarget(0,&target)),"render target");D3DSURFACE_DESC desc={};target->GetDesc(&desc);
    check(SUCCEEDED(d->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&copy,nullptr))&&SUCCEEDED(d->GetRenderTargetData(target,copy)),"readback");
    D3DVIEWPORT9 viewport={};d->GetViewport(&viewport);check(viewport.Width==640&&viewport.Height==480&&viewport.X+640<=desc.Width&&viewport.Y+480<=desc.Height,"actual client viewport");
    D3DLOCKED_RECT lock={};check(SUCCEEDED(copy->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"readback lock");FILE* file=std::fopen(name,"wb");check(file!=nullptr,"frame file");unsigned pixels=0;
    for(unsigned y=viewport.Y;y<viewport.Y+480;++y){auto* row=static_cast<unsigned char*>(lock.pBits)+y*lock.Pitch+viewport.X*4;std::fwrite(row,4,640,file);for(unsigned x=0;x<640;++x){DWORD color;std::memcpy(&color,row+x*4,4);pixels+=(color&0xffffff)!=0x102030;}}
    std::fclose(file);copy->UnlockRect();copy->Release();target->Release();return pixels;
}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"actual language");InitR3Engine();auto* state=GetR3State();state->mScreenXsize=640;state->mScreenYsize=480;state->mbFullScreen=FALSE;ForceFullScreen();
    check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"actual text device");R3SetViewPort(0,0,640,480);
    const auto font=RF455_GetFontSnapshotFlags(0x80000010);LOGFONTA lf={};check(font.font&&GetObjectA(font.font,sizeof(lf),&lf)==sizeof(lf),"actual medium font");
    HDC dc=CreateCompatibleDC(nullptr);auto old=SelectObject(dc,font.font);check(lf.lfHeight==-MulDiv(16,GetDeviceCaps(dc,LOGPIXELSY),72),"target16point selection");SIZE expected={};GetTextExtentPoint32A(dc,"WWii",4,&expected);
    const auto actual=RF455_MeasureTextAnsiFlags("WWii",0x80000010);check(expected.cx==actual.cx&&expected.cy==actual.cy,"independent medium GDI metrics");SelectObject(dc,old);DeleteDC(dc);
    NetworkScope network;check(!RF455_GetCenterMessages(),"stage owner absent before construction");std::unique_ptr<CGP_MainGame> stage(new CGP_MainGame);auto& messages=stage->CenterMessages455();
    check(RF455_GetCenterMessages()==&messages&&messages.Active().empty()&&messages.Pending().empty(),"actual MainGame constructor owns center messages");
    messages.Add("WWii",0xffcc1f00);auto first=messages.Active().front();check(sizeof(first)==84&&first.alpha==0&&first.scale==1&&closeFloat(first.y,float(200+expected.cy))&&closeFloat(first.x,float((640.0-expected.cx)/2)),"record84 initial geometry");
    messages.FrameMoveAt(first.time+100,.1f);const auto& moved=messages.Active().front();check(closeFloat(moved.alpha,.45f)&&closeFloat(moved.y,float((200.0-first.y)*.45+first.y))&&(moved.color>>24)==114,"ordinary fade and movement kernel");
    R3SetLoopTime(.1f);messages.FrameMove();check(messages.Active().front().alpha>.45f&&messages.Active().front().alpha<1,"ordinary FrameMove uses live time and engine loop delta");
    messages.Clear();for(const char* s:{"one","two","three","four"})messages.Add(s,0xffcc1f00);
    check(messages.Active().size()==3&&!std::strcmp(messages.Active().front().text,"two")&&!std::strcmp(messages.Active().back().text,"four"),"capacity3 removes oldest");
    messages.FrameMoveAt(messages.Active().back().time+100,.1f);check(closeFloat(messages.Active().back().scale,1)&&closeFloat(messages.Active().front().scale,.91f)&&messages.Active().back().alpha>messages.Active().front().alpha,"newest-to-oldest ranks");
    messages.Clear();char dbcs[8]={};const auto cp=RF455_GetFontSettings().codepage;check(WideCharToMultiByte(cp,0,L"\uac00",1,dbcs,8,nullptr,nullptr)==2,"actual Korean DBCS");std::string text(58,'A');text.append(dbcs,2);text+='Z';
    const int ambientMbcp=_getmbcp();check(_setmbcp(0)==0,"explicit SBCS oracle mode");messages.Add(text.c_str(),0xffffffff);
    check(messages.Pending().size()==2&&std::strlen(messages.Pending().front().text)==59&&std::strlen(messages.Pending().back().text)==2,"ambient SBCS copy may split Korean bytes");
    messages.Clear();check(_setmbcp(949)==0,"explicit DBCS oracle mode");messages.Add(text.c_str(),0xffffffff);
    check(messages.Pending().size()==2&&messages.Active().empty()&&std::strlen(messages.Pending().front().text)==58&&std::strlen(messages.Pending().back().text)==3,"59byte split keeps DBCS together");
    messages.FrameMoveAt(timeGetTime()+100,0);check(messages.Active().size()==1&&messages.Pending().size()==1,"empty active promotes exactly one chunk");const auto stamp=messages.Active().back().time;
    messages.FrameMoveAt(stamp+500,0);check(messages.Pending().size()==1,"500ms strict boundary retains queue");messages.FrameMoveAt(stamp+501,0);check(messages.Pending().empty()&&messages.Active().size()==2,"501ms promotes next chunk");
    check(_setmbcp(ambientMbcp)==0&&_getmbcp()==ambientMbcp,"restore actual ambient CRT mode");
    messages.Clear();std::string flood(59*6+1,'X');messages.Add(flood.c_str(),0xffffffff);messages.FrameMoveAt(timeGetTime()+100,0);check(messages.Pending().size()==6,"flood first promotion");
    messages.FrameMoveAt(messages.Active().back().time+100,0);check(messages.Pending().size()==5&&messages.Active().size()==2,"queue greater5 bypasses500ms but promotes once");
    messages.Clear();messages.Add("boundary",0xffffffff);const auto boundary=messages.Active().front().time;messages.FrameMoveAt(boundary+3600,0);check(messages.Active().size()==1,"3600ms strict removal boundary");messages.FrameMoveAt(boundary+3601,0);check(messages.Active().empty(),"3601ms removes zero-alpha oldest");
    for(const char* s:{"one","two","three"})messages.Add(s,0xffffffff);const auto expired=messages.Active().back().time+3601;messages.FrameMoveAt(expired,0);check(messages.Active().size()==2,"at most one expired row removed per frame");messages.FrameMoveAt(expired,0);messages.FrameMoveAt(expired,0);check(messages.Active().empty(),"all expired rows eventually removed");
    messages.Add("wrap",0xffffffff);messages.FrameMoveAt(messages.Active().front().time-1,0);check(messages.Active().empty(),"DWORD elapsed subtraction preserved");
    messages.Add("overshoot",0xffffffff);messages.FrameMoveAt(messages.Active().front().time+100,1);check(closeFloat(messages.Active().front().alpha,4.5f)&&(messages.Active().front().color>>24)==123,"factor and alpha are not clamped");
    messages.Clear();const auto* pack=RF455_GetNormalLanguagePack();const auto* c1a=pack->get(0xc1a);const auto* ce7=pack->get(0xce7);check(c1a&&ce7&&std::strlen(c1a)&&std::strlen(ce7),"actual C1A and CE7 records");
    messages.Add(c1a,0xffcc1f00);auto now=timeGetTime()+100;for(unsigned i=0;i<10;++i)messages.FrameMoveAt(now+i*50,.05f);const auto pixels1=capture(messages,"center-c1a.bgra");check(pixels1>10,"actual localized C1A drawn");
    messages.Add(ce7,0xffcc1f00);for(unsigned i=0;i<10;++i)messages.FrameMoveAt(now+600+i*50,.05f);const auto pixels2=capture(messages,"center-queued.bgra");check(pixels2>10,"actual localized queue drawn");
    for(unsigned i=0;i<3;++i)messages.FrameMoveAt(now+7000,.1f);const auto pixels3=capture(messages,"center-fading.bgra");check(pixels3>0,"actual fade still visible");
    unsigned drain=0;while((!messages.Active().empty()||!messages.Pending().empty())&&drain<80){messages.FrameMoveAt(now+7000,.1f);++drain;}const auto pixels4=capture(messages,"center-cleared.bgra");std::fprintf(stderr,"fade:active=%u pending=%u ticks=%u pixels=%u/%u/%u/%u\n",unsigned(messages.Active().size()),unsigned(messages.Pending().size()),drain,pixels1,pixels2,pixels3,pixels4);check(messages.Active().empty()&&messages.Pending().empty()&&pixels4==0,"ordinary fade drains and clears GPU frame");
    stage.reset();check(!RF455_GetCenterMessages(),"actual MainGame member destructor unbinds owner");
    g_MainApp.ReleaseR3D3D();ReleaseR3Engine();FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"result");
    std::fprintf(out,"{\"status\":\"PASS\",\"checks\":%u,\"actual_MainGame_owner\":true,\"record_bytes\":84,\"chunk_bytes\":64,\"active_capacity\":3,\"real_language_C1A_CE7\":true,\"real_medium_GDI_oracle\":true,\"DBCS_boundary\":true,\"queue500ms_and_flood\":true,\"fade3600ms_and_single_eviction\":true,\"unsigned_elapsed\":true,\"unclamped_factor\":true,\"GPU_frames\":4,\"pixels\":[%u,%u,%u,%u],\"fade_drain_ticks\":%u,\"owner_unbound\":true,\"all_center_records_released\":true,\"legacy_uncreated_MainGame_allocations_gap\":true,\"full_stage_teardown\":false,\"full_C1A_dispatch\":false,\"live_hover_cancel\":false,\"full_chat\":false,\"full_world_frame_order\":false,\"full_client\":false}\n",checks,pixels1,pixels2,pixels3,pixels4,drain);std::fclose(out);return 0;
}
static LONG filter(EXCEPTION_POINTERS* p){if(p->ExceptionRecord->ExceptionCode==0xe06d7363)return EXCEPTION_CONTINUE_SEARCH;std::fprintf(stderr,"exception=%08lx ownRVA=%08lx checks=%u\n",p->ExceptionRecord->ExceptionCode,DWORD(p->ExceptionRecord->ExceptionAddress)-DWORD(GetModuleHandleA(nullptr)),checks);return EXCEPTION_EXECUTE_HANDLER;}
static int guarded(){__try{return run();}__except(filter(GetExceptionInformation())){return 99;}}
int main(){try{return guarded();}catch(const std::exception& e){std::fprintf(stderr,"center messages:%s\n",e.what());return 1;}}
