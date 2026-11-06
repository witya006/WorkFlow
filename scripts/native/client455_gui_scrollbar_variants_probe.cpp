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
#include "userinterface/guicontroller/guiscrollbar.h"
#include "mainapp.h"
#include "client455_language.h"
#include "client455_nation_paths.h"
#include <cstdio>
#include <stdexcept>
#include <vector>
extern CMainApp g_MainApp;
static void check(bool value,const char* reason){if(!value)throw std::runtime_error(reason);}
template<class Tag,typename Tag::Type Member>struct MemberAccess{friend typename Tag::Type access(Tag){return Member;}};
struct QueueCreate{using Type=void(*)(WORD);friend Type access(QueueCreate);};
struct QueueProcess{using Type=void(*)();friend Type access(QueueProcess);};
template struct MemberAccess<QueueCreate,&CGUIObject::CreateEventQueue>;
template struct MemberAccess<QueueProcess,&CGUIObject::EventProcess>;
static std::vector<DWORD> ticks;static unsigned tickIndex=0;
static DWORD replayClock(){check(tickIndex<ticks.size(),"unexpected clock query");return ticks[tickIndex++];}
static void timeline(std::initializer_list<DWORD> values){ticks=values;tickIndex=0;}
struct Observer:IScrollObserver{
    CGUIScrollbar* owner=nullptr;std::vector<WORD> ids;
    void ScrollEvent(_scroll_event& event){check(event.source==owner,"queued variant source");ids.push_back(event.id);}
    void drain(){access(QueueProcess{})();}void clear(){ids.clear();}
};
static void mouse(CGUIScrollbar& bar,CGUIObject& source,WORD id,LONG x=0,LONG y=0){_mouse_event event={&source,id,x,y};bar.MouseEvent(event);}
static void drag(CGUIScrollbar& bar,CGUIObject& source,LONG x,LONG y){_mouse_motion_event event={&source,MOUSE_DRAG,x,y,0,0};bar.MouseMotionEvent(event);}
static unsigned capture(CGUIObject& bar,const char* file,bool expected=true){
    auto* device=GetD3dDevice();check(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET,0xff102030,1,0))&&SUCCEEDED(device->BeginScene()),"frame begin");check((bar.Draw()!=0)==expected,"variant Draw return");check(SUCCEEDED(device->EndScene()),"frame end");
    IDirect3DSurface9* target=nullptr;IDirect3DSurface9* memory=nullptr;check(SUCCEEDED(device->GetRenderTarget(0,&target)),"target");D3DSURFACE_DESC desc={};target->GetDesc(&desc);check(SUCCEEDED(device->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&memory,nullptr)),"read surface");check(SUCCEEDED(device->GetRenderTargetData(target,memory)),"readback");D3DLOCKED_RECT lock={};check(SUCCEEDED(memory->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"lock");D3DVIEWPORT9 view={};device->GetViewport(&view);check(view.Width==640&&view.Height==480,"viewport");FILE* output=std::fopen(file,"wb");check(output!=nullptr,"frame output");unsigned pixels=0;
    for(unsigned y=view.Y;y<view.Y+view.Height;++y){const auto* row=reinterpret_cast<const DWORD*>(static_cast<const BYTE*>(lock.pBits)+y*lock.Pitch)+view.X;std::fwrite(row,4,view.Width,output);for(unsigned x=0;x<view.Width;++x)pixels+=(row[x]&0xffffff)!=0x102030;}
    std::fclose(output);memory->UnlockRect();memory->Release();target->Release();return pixels;
}
static DWORD pixel(const char* file,int x,int y){FILE* input=std::fopen(file,"rb");check(input!=nullptr,"pixel input");std::fseek(input,(y*640+x)*4,SEEK_SET);DWORD value=0;check(std::fread(&value,4,1,input)==1,"pixel read");std::fclose(input);return value&0xffffff;}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"nation and language");InitR3Engine();GetR3State()->mScreenXsize=640;GetR3State()->mScreenYsize=480;GetR3State()->mbFullScreen=FALSE;ForceFullScreen();check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"D3D init");access(QueueCreate{})(64);
    const auto oldClock=RF455_SetScrollbarClock(replayClock);timeline({});
    CGUIScrollbarEX bar;Observer observer;observer.owner=&bar;bar.AddScrollHandler(&observer);bar.Show(TRUE);
    check(bar.GetAddedObjectNum()==3&&bar.IsAddedObject(&bar.GetButton455())&&!bar.IsAddedObject(&bar.GetThumb455()),"EX constructor adds plain thumb even at zero amount");
    POINT top={12,8},bottom={10,7};bar.SetTopArrowSize(top);bar.SetBottomArrowSize(bottom);bar.GetButton455().SetSize(5,4);bar.SetPos(100,200);bar.SetSize(12,100);bar.SetAmount(25,10);
    check(bar.GetButton455().GetSizeX()==5&&bar.GetButton455().GetSizeY()==60&&bar.GetScrollLength455()==25&&bar.GetButton455().GetPosY()==218,"EX plain linear thumb without minimum6x18");
    check(bar.CGUIScrollbar::GetScrollLength455()==67&&bar.CalculateAmount455(25)==9,"EX snap deliberately uses inherited composite18 instead of visible60");
    bar.SetCurrentAmount(10);timeline({10,11});mouse(bar,bar.GetBottomArrow455(),MOUSE_STROKED);observer.drain();check(bar.GetCurrentAmount()==11&&observer.ids==std::vector<WORD>{31}&&tickIndex==2,"EX arrow event clock order");observer.clear();
    timeline({});mouse(bar,bar.GetBottomArrow455(),MOUSE_PRESSED);observer.drain();check(tickIndex==0&&bar.GetCurrentAmount()==11&&observer.ids.empty(),"EX no repeat handler");
    bar.SetCurrentAmount(20);timeline({12});mouse(bar,bar,MOUSE_STROKED,103,263);observer.drain();check(bar.GetCurrentAmount()==9&&bar.GetButton455().GetPosY()==217&&observer.ids==std::vector<WORD>{31},"EX track uses base snap and post-update DOWN");observer.clear();
    timeline({});mouse(bar,bar.GetButton455(),MOUSE_STROKED,103,220);check(tickIndex==0&&bar.GetThumb455().GetPressed455()==0,"EX grab does not press composite skin");timeline({13});drag(bar,bar.GetButton455(),103,236);observer.drain();check(bar.GetCurrentAmount()==9&&bar.GetButton455().GetPosY()==233&&observer.ids.empty(),"EX free drag uses base67 track");
    timeline({});mouse(bar,bar.GetButton455(),MOUSE_RELEASED,103,236);check(bar.GetButton455().GetPosY()==217&&tickIndex==0,"EX release restores own25 track");
    bar.SetAlpha455(0x7f);check(bar.GetARGB()==0x7fffffff&&bar.GetButton455().GetARGB()==0x7fffffff&&bar.GetThumb455().GetARGB()==0x7fffffff&&bar.GetTopArrow455().GetARGB()==0x7fffffff,"EX alpha propagation including unused composite");bar.SetAlpha455(0xff);
    bar.SetAmount(0,0);check(bar.GetAddedObjectNum()==3&&bar.IsAddedObject(&bar.GetButton455()),"EX zero total keeps child");
    bar.SetAutoThumb455(FALSE);bar.GetButton455().SetSize(3,4);bar.SetSize(100,12);bar.SetStyle(CGUIScrollbar::Horizontal);bar.SetAmount(25,10);check(bar.GetButton455().GetSizeX()==3&&bar.GetButton455().GetSizeY()==4&&bar.GetButton455().GetPosX()==142,"EX horizontal raw size and own track");
    bar.SetAutoThumb455(TRUE);bar.SetSize(20,12);bar.SetMinimumThumb455(1);bar.SetAmount(100,50);check(bar.GetButton455().GetSizeX()==-2,"EX negative available minimum is not composite-clamped");
    CSprite common;common.LoadSprite(const_cast<char*>("common.spr"));bar.GetButton455().SetSize(8,24);bar.GetButton455().SetARGB(0xff806040);bar.SetAutoThumb455(FALSE);bar.SetPos(50,50);bar.SetSize(12,160);bar.SetStyle(CGUIScrollbar::Vertical);bar.SetAmount(100,50);SPRITE_INFO up[2]={{&common,2,0},{&common,2,1}},down[2]={{&common,2,2},{&common,2,3}};bar.SetTopArrowSpriteInfo(up);bar.SetBottomArrowSpriteInfo(down);const unsigned exPixels=capture(bar,"scrollbar-ex.bgra",false);check(exPixels>100,"EX paints children but returns FALSE from its hidden inherited composite");
    CSprite fixture;fixture.LoadSprite(const_cast<char*>("variant-fixture.spr"));CGUIScrollbarVar var;check(var.GetAddedObjectNum()==2&&var.GetMiddleExtent455()==0,"Var keeps base arrows;initializer calls SetSprite rather than RemoveAll");var.SetSkin455(&fixture);var.SetPos(120,60);var.SetSize(6,100);var.Show(TRUE);var.SetAmount(30,10);
    check(fixture.GetMaxActions()==15&&var.GetTopCap455().GetSizeY()==0,"target loader keeps action15 unavailable;resize helper returns0");
    check(var.GetMiddleExtent455()==70&&var.GetThumb455().GetSizeY()==70&&var.GetThumb455().GetPosY()==60&&var.GetAddedObjectNum()==6,"Var amount sets3skins and composite at origin without UpdateBar");check(var.GetScrollLength455()==30&&var.CalculateAmount455(9)==9,"Var independent track and snap");
    var.GetTopCap455().SetSize(40,40);var.SetSize(2,10);check(var.GetSizeX()==2&&var.GetSizeY()==10&&var.GetTopCap455().GetSizeX()==6&&var.GetTopCap455().GetSizeY()==0&&var.GetMiddleExtent455()==70,"Var size keeps raw outer extent and resource cap height without reflow");var.SetSize(6,100);var.SetAmount(30,10);
    Observer varObserver;varObserver.owner=&var;var.AddScrollHandler(&varObserver);timeline({});mouse(var,var.GetThumb455(),MOUSE_STROKED,121,63);check(var.GetPressed455()==1&&var.GetTopCap455().GetSpriteInfo()->wFrameNo==3&&tickIndex==0,"Var pressed mode and vertical grab");timeline({14});drag(var,var.GetThumb455(),121,72);varObserver.drain();check(var.GetCurrentAmount()==9&&var.GetThumb455().GetPosY()==69&&varObserver.ids==std::vector<WORD>{31},"Var vertical drag and post-update event");varObserver.clear();timeline({});mouse(var,var.GetThumb455(),MOUSE_RELEASED,121,72);check(var.GetPressed455()==0&&var.GetThumb455().GetPosY()==69&&tickIndex==0,"Var release switches skin without alignment");
    timeline({});mouse(var,var,MOUSE_STROKED,121,139);varObserver.drain();check(var.GetCurrentAmount()==9&&var.GetThumb455().GetPosY()==69&&varObserver.ids.empty()&&tickIndex==0,"Var track uses full thumb height instead of half");
    SPRITE_INFO ignored={&common,2,0};var.SetSpriteInfo(&ignored);check(var.GetSpriteInfo()->pSprite==nullptr,"Var base sprite setter is no-op");
    auto* device=GetD3dDevice();DWORD minFilter=0,magFilter=0;device->GetSamplerState(0,D3DSAMP_MINFILTER,&minFilter);device->GetSamplerState(0,D3DSAMP_MAGFILTER,&magFilter);device->SetSamplerState(0,D3DSAMP_MINFILTER,D3DTEXF_POINT);device->SetSamplerState(0,D3DSAMP_MAGFILTER,D3DTEXF_POINT);
    const unsigned varPixels=capture(var,"scrollbar-var.bgra");check(pixel("scrollbar-var.bgra",122,85)==0x00ff00,"Var row2 uses common action2 despite cap action15");timeline({});mouse(var,var.GetThumb455(),MOUSE_STROKED,121,72);const unsigned pressedPixels=capture(var,"scrollbar-var-pressed.bgra");check(pixel("scrollbar-var-pressed.bgra",122,85)==0x00ffff,"Var pressed frame4 uses action2 row2");mouse(var,var.GetThumb455(),MOUSE_RELEASED,121,72);
    var.SetAmount(100,99);check(var.GetMiddleExtent455()==0&&var.Draw()==FALSE,"Var zero middle extent skips entire draw");var.SetAmount(101,1);check(var.GetMiddleExtent455()==-1&&var.GetThumb455().GetSizeY()==18,"Var negative middle extent retains composite minimum");var.SetAmount(0,0);check(var.GetAddedObjectNum()==2&&var.GetMiddleExtent455()==-1,"Var zero removes4children but retains middle extent");
    var.SetStyle(CGUIScrollbar::Horizontal);bool refused=false;try{mouse(var,var,MOUSE_STROKED,0,0);}catch(const std::domain_error&){refused=true;}check(refused,"undefined target horizontal track local explicitly refused");
    device->SetSamplerState(0,D3DSAMP_MINFILTER,minFilter);device->SetSamplerState(0,D3DSAMP_MAGFILTER,magFilter);RF455_SetScrollbarClock(oldClock);bar.AddScrollHandler(nullptr);var.AddScrollHandler(nullptr);fixture.ReleaseSprite();common.ReleaseSprite();R3ReleaseTextTexture();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();FILE* output=std::fopen("result.json","wb");check(output!=nullptr,"result");std::fprintf(output,"{\"status\":\"PASS\",\"codepage\":%u,\"EX_geometry\":true,\"EX_base_snap_quirk\":true,\"EX_no_repeat\":true,\"EX_alpha\":true,\"Var_geometry\":true,\"Var_input\":true,\"Var_row2_action2\":true,\"queued_events\":true,\"undefined_horizontal_refused\":true,\"EX_pixels\":%u,\"Var_pixels\":%u,\"Var_pressed_pixels\":%u,\"production_minimap\":false,\"full_parent_input\":false}\n",RF455_GetNormalLanguagePack()->codepage,exPixels,varPixels,pressedPixels);std::fclose(output);return 0;
}
static LONG filter(EXCEPTION_POINTERS* info){return info->ExceptionRecord->ExceptionCode==0xe06d7363?EXCEPTION_CONTINUE_SEARCH:EXCEPTION_EXECUTE_HANDLER;}
static int guarded(){__try{return run();}__except(filter(GetExceptionInformation())){return 99;}}
int main(){try{return guarded();}catch(const std::exception& error){std::fprintf(stderr,"Scrollbar variants: %s\n",error.what());return 1;}}
