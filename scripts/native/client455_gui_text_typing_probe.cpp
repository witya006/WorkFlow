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
#include "client455_gui_text_typing_board.h"
#include "client455_font.h"
#include "client455_language.h"
#include "client455_nation_paths.h"
#include <cstdio>
#include <cstring>
#include <mbctype.h>
#include <stdexcept>
#include <string>
#include <vector>
extern CMainApp g_MainApp;
static DWORD tick=0;static unsigned queries=0;
static DWORD clockTick(){++queries;return tick;}
static char* text(const char* value){return const_cast<char*>(value);}
static void check(bool value,const char* reason){if(!value)throw std::runtime_error(reason);}
static void cursor(const CGUITextTypingBoard& board,WORD fragment,WORD offset,bool done){
    static unsigned step=0;++step;
    if(board.GetTypingFragment455()!=fragment||board.GetTypingOffset455()!=offset||bool(board.IsTypingFinished455())!=done)
        std::fprintf(stderr,"cursor step%u time%u got%u/%u/%d expected%u/%u/%d\n",step,unsigned(tick),unsigned(board.GetTypingFragment455()),unsigned(board.GetTypingOffset455()),int(board.IsTypingFinished455()),unsigned(fragment),unsigned(offset),int(done));
    check(board.GetTypingFragment455()==fragment&&board.GetTypingOffset455()==offset&&bool(board.IsTypingFinished455())==done,"assembly-derived cursor trace");
}
static void update(CGUITextTypingBoard& board,DWORD time){tick=time;board.Update();}
static void reset(CGUITextTypingBoard& board,const char* value){board.Clear();board.SetSize(400,200);board.SetPos(20,20);board.Show(TRUE);board.InsertText(text(value));board.SetTypingInterval455(80);}
static unsigned capture(CGUITextBoard& board,const char* filename){
    auto* device=GetD3dDevice();check(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET,0xff102030,1,0)),"clear");check(SUCCEEDED(device->BeginScene()),"begin");check(board.Draw()!=0,"draw");check(SUCCEEDED(device->EndScene()),"end");
    IDirect3DSurface9* target=nullptr;IDirect3DSurface9* memory=nullptr;check(SUCCEEDED(device->GetRenderTarget(0,&target)),"target");D3DSURFACE_DESC desc={};target->GetDesc(&desc);check(SUCCEEDED(device->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&memory,nullptr)),"surface");check(SUCCEEDED(device->GetRenderTargetData(target,memory)),"readback");D3DLOCKED_RECT lock={};check(SUCCEEDED(memory->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"lock");
    D3DVIEWPORT9 view={};device->GetViewport(&view);check(view.Width==640&&view.Height==480,"viewport");FILE* out=std::fopen(filename,"wb");check(out!=nullptr,"frame");unsigned pixels=0;
    for(unsigned y=view.Y;y<view.Y+view.Height;++y){auto* row=reinterpret_cast<const DWORD*>(static_cast<const BYTE*>(lock.pBits)+y*lock.Pitch)+view.X;std::fwrite(row,4,view.Width,out);for(unsigned x=0;x<view.Width;++x)pixels+=(row[x]&0xffffff)!=0x102030;}
    std::fclose(out);memory->UnlockRect();memory->Release();target->Release();return pixels;
}
static std::string encode(const wchar_t* value,unsigned cp){const int count=WideCharToMultiByte(cp,0,value,-1,nullptr,0,nullptr,nullptr);check(count>0,"encode");std::vector<char> result(count);check(WideCharToMultiByte(cp,0,value,-1,result.data(),count,nullptr,nullptr)>0,"encode bytes");return result.data();}
struct Child:CGUIObject {unsigned draws=0,updates=0;BOOL Draw()override{++draws;return TRUE;}void Update()override{++updates;}};
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"language");InitR3Engine();GetR3State()->mScreenXsize=640;GetR3State()->mScreenYsize=480;GetR3State()->mbFullScreen=FALSE;ForceFullScreen();check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"D3D init");
    const auto previous=RF455_SetTextTypingClock(clockTick);CGUITextTypingBoard board;
    cursor(board,0xffff,0xffff,false);check(!board.IsTypingRunning455(),"constructor state");
    reset(board,"ABC");tick=1000;check(board.StartTyping455(0,0,250),"start");check(board.GetTypingStartTime455()==1250,"delay");
    update(board,1249);cursor(board,0xffff,0xffff,false);update(board,1250);cursor(board,0xffff,0xffff,false);update(board,1329);cursor(board,0xffff,0xffff,false);
    update(board,1330);cursor(board,0,0,false);check(capture(board,"typing-first-ascii.bgra")==0,"strict start<cursor suppresses first single ASCII byte");
    update(board,1410);cursor(board,0,1,false);const unsigned partial=capture(board,"typing-partial.bgra");check(partial>0,"partial text");
    CGUITextBoard expected;expected.SetPos(20,20);expected.SetSize(400,200);expected.Show(TRUE);expected.InsertText(text("AB"));check(capture(expected,"typing-expected-partial.bgra")==partial,"plain prefix pixel count");
    update(board,1490);cursor(board,0,2,true);const unsigned complete=capture(board,"typing-complete.bgra");check(complete>partial&&board.GetTypingPreviousTime455()==1410,"completion retains previous tick");
    const unsigned before=queries;update(board,9000);check(queries==before,"finished update does not query clock");
    reset(board,"A  B");tick=100;board.StartTyping455(0,0);update(board,100);update(board,180);cursor(board,0,0,false);update(board,260);cursor(board,0,3,true);
    reset(board,"A");board.InsertText(text("BC"));tick=100;board.StartTyping455(0,0);update(board,100);update(board,180);cursor(board,0,0,false);update(board,260);cursor(board,1,0,false);update(board,340);cursor(board,1,1,true);
    reset(board," ");board.InsertText(text("BC"));tick=100;board.StartTyping455(0,0);update(board,100);update(board,180);cursor(board,1,1,true);update(board,260);cursor(board,1,1,true);
    reset(board,"AB\nCD");check(board.GetTotalLineNum()==2,"two lines");tick=100;board.StartTyping455(1,1);update(board,100);update(board,180);cursor(board,0,2,false);update(board,260);cursor(board,0,3,false);update(board,340);cursor(board,0,4,true);
    auto* pack=RF455_GetNormalLanguagePack();const unsigned cp=pack->codepage;const auto localized=encode(cp==949?L"\uac00X":L"\u041fX",cp);
    reset(board,localized.c_str());check(_setmbcp(cp==949?1251:949)==0,"opposite ambient CRT");tick=100;board.StartTyping455(0,0);update(board,100);update(board,180);cursor(board,0,cp==949?1:0,false);const unsigned localizedPixels=capture(board,"typing-localized.bgra");check(cp==949?localizedPixels>0:localizedPixels==0,"resource classifier controls first visible glyph");update(board,260);cursor(board,0,cp==949?2:1,true);check(_setmbcp(_MB_CP_ANSI)==0,"restore ANSI CRT");
    reset(board,"ABC");tick=0;board.StartTyping455(0,0);update(board,0);update(board,80);cursor(board,0xffff,0xffff,false);update(board,160);cursor(board,0,0,false);
    reset(board,"ABC");tick=0xfffffff0;board.StartTyping455(0,0,32);check(board.GetTypingStartTime455()==16,"DWORD delayed start wrap");update(board,0xfffffff0);check(board.GetTypingPreviousTime455()==0xfffffff0,"absolute start comparison before wrap");update(board,16);cursor(board,0xffff,0xffff,false);update(board,80);cursor(board,0,0,false);
    reset(board,"ABC");board.SetTypingInterval455(0);tick=100;board.StartTyping455(0,0);update(board,100);update(board,100);cursor(board,0,2,true);
    CGUITextBoard* polymorphic=&board;polymorphic->Clear();cursor(board,0xffff,0xffff,true);check(board.IsTypingRunning455()&&board.GetTypingPreviousTime455()==100,"Clear resets cursor but retains flags/timer");
    reset(board,"ABC");tick=100;board.StartTyping455(0,0);const unsigned invalidQueries=queries;check(!board.StartTyping455(1,0)&&!board.StartTyping455(0,1)&&queries==invalidQueries,"invalid range leaves timer alone");
    bool refused=false;try{board.StartTyping455(-1,0);}catch(const std::invalid_argument&){refused=true;}check(refused,"negative marker domain explicit");
    Child child;board.Add(&child);board.Show(FALSE);const unsigned hiddenQueries=queries;update(board,100);check(queries==hiddenQueries&&!board.Draw()&&child.draws==0,"hidden update/draw gate");board.Show(TRUE);board.InActive();update(board,100);update(board,180);cursor(board,0,0,false);check(!child.updates,"typing Update does not update children");
    board.SetARGB(0xffff0000);check(capture(board,"typing-no-self-fill.bgra")==0&&child.draws==1,"container children drawn without self fill");board.Remove(&child);board.SetARGB(0xffffffff);
    board.Clear();FONT_INFO red,green;red.dwColor=0xffff0000;green.dwColor=0xff00ff00;board.InsertText(text("A"),&red);board.InsertText(text("BC"),&green);board.FinishTyping455();check(board.IsTypingFinished455(),"force finish");const unsigned colored=capture(board,"typing-colored.bgra");check(colored>0,"colored fragments");
    RF455_SetTextTypingClock(previous);R3ReleaseTextTexture();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();
    FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"output");std::fprintf(out,"{\"status\":\"PASS\",\"codepage\":%u,\"delay_interval_cursor_trace\":true,\"spaces_and_fragment_boundary\":true,\"newline_page_range\":true,\"resource_DBCS_not_CRT\":true,\"zero_and_DWORD_wrap\":true,\"virtual_Clear_retained_flags\":true,\"hidden_and_children\":true,\"negative_domain_refused\":true,\"partial_pixels\":%u,\"complete_pixels\":%u,\"colored_pixels\":%u,\"localized_first_pixels\":%u,\"clock_queries\":%u,\"production_briefing\":false,\"full_Tutorial\":false}\n",cp,partial,complete,colored,localizedPixels,queries);std::fclose(out);return 0;
}
static LONG filter(EXCEPTION_POINTERS* info){return info->ExceptionRecord->ExceptionCode==0xe06d7363?EXCEPTION_CONTINUE_SEARCH:EXCEPTION_EXECUTE_HANDLER;}
static int guarded(){__try{return run();}__except(filter(GetExceptionInformation())){return 99;}}
int main(){try{return guarded();}catch(const std::exception& error){std::fprintf(stderr,"Typing: %s\n",error.what());return 1;}}
