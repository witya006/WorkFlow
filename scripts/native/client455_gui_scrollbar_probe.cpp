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
#include <cstring>
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
struct Observer : IScrollObserver {
    CGUIScrollbar* owner=nullptr;std::vector<WORD> ids;std::vector<LONG> values;std::vector<DWORD> times;
    void ScrollEvent(_scroll_event& event){check(event.source==owner,"actual queued scroll source");ids.push_back(event.id);values.push_back(owner->GetCurrentAmount());times.push_back(owner->GetLastScrollTime455());}
    void drain(){access(QueueProcess{})();}
    void clear(){ids.clear();values.clear();times.clear();}
};
static void mouse(CGUIScrollbar& bar,CGUIObject& source,WORD id,LONG x=0,LONG y=0){_mouse_event event={&source,id,x,y};bar.MouseEvent(event);}
static void drag(CGUIScrollbar& bar,LONG x,LONG y){_mouse_motion_event event={&bar.GetThumb455(),MOUSE_DRAG,x,y,0,0};bar.MouseMotionEvent(event);}
static void shape(CGUIScrollbar& bar,LONG x=100,LONG y=200,LONG width=12,LONG height=100){POINT top={12,8},bottom={10,7};bar.SetTopArrowSize(top);bar.SetBottomArrowSize(bottom);bar.SetPos(x,y);bar.SetSize(width,height);}
static unsigned capture(CGUIScrollbar& bar,const char* file){
    auto* device=GetD3dDevice();check(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET,0xff102030,1,0))&&SUCCEEDED(device->BeginScene()),"frame begin");check(bar.Draw()!=0,"actual scrollbar Draw");check(SUCCEEDED(device->EndScene()),"frame end");
    IDirect3DSurface9* target=nullptr;IDirect3DSurface9* memory=nullptr;check(SUCCEEDED(device->GetRenderTarget(0,&target)),"target");D3DSURFACE_DESC desc={};target->GetDesc(&desc);check(SUCCEEDED(device->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&memory,nullptr)),"read surface");check(SUCCEEDED(device->GetRenderTargetData(target,memory)),"readback");D3DLOCKED_RECT lock={};check(SUCCEEDED(memory->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"lock");D3DVIEWPORT9 view={};device->GetViewport(&view);check(view.Width==640&&view.Height==480,"viewport");FILE* output=std::fopen(file,"wb");check(output!=nullptr,"frame output");unsigned pixels=0;
    for(unsigned y=view.Y;y<view.Y+view.Height;++y){const auto* row=reinterpret_cast<const DWORD*>(static_cast<const BYTE*>(lock.pBits)+y*lock.Pitch)+view.X;std::fwrite(row,4,view.Width,output);for(unsigned x=0;x<view.Width;++x)pixels+=(row[x]&0xffffff)!=0x102030;}
    std::fclose(output);memory->UnlockRect();memory->Release();target->Release();return pixels;
}
static DWORD framePixel(const char* file,int x,int y){FILE* input=std::fopen(file,"rb");check(input!=nullptr,"pixel oracle input");check(std::fseek(input,(y*640+x)*4,SEEK_SET)==0,"pixel oracle seek");DWORD pixel=0;check(std::fread(&pixel,4,1,input)==1,"pixel oracle read");std::fclose(input);return pixel&0xffffff;}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    check(IsProcessorFeaturePresent(PF_XMMI64_INSTRUCTIONS_AVAILABLE)!=0,"supported SSE2 probe host");
    check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"nation and language");InitR3Engine();GetR3State()->mScreenXsize=640;GetR3State()->mScreenYsize=480;GetR3State()->mbFullScreen=FALSE;ForceFullScreen();check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"D3D init");access(QueueCreate{})(64);
    CGUIScrollbar bar;shape(bar);check(bar.GetMinimumThumb455()==20&&bar.GetAddedObjectNum()==2&&bar.GetThumb455().GetSizeX()==6&&bar.GetThumb455().GetSizeY()==18,"constructor defaults and minimum6x18");bar.Show(TRUE);bar.SetAmount(25,10);
    check(bar.GetThumb455().GetSizeY()==60&&bar.GetScrollLength455()==25&&bar.GetThumb455().GetPosX()==103&&bar.GetThumb455().GetPosY()==218,"vertical linear thumb sizing and position");check(bar.GetTopArrow455().GetPosX()==100&&bar.GetBottomArrow455().GetPosX()==100&&bar.GetBottomArrow455().GetPosY()==293,"asymmetric arrow layout");check(bar.GetThumb455().IsShow(),"owned inherited show adapter");
    bar.SetTotalAmount(5);check(bar.GetCurrentAmount()==5&&bar.GetThumb455().GetSizeY()==80,"total setter clamps current and resizes thumb");bar.SetMinimumThumb455(200);check(bar.GetMinimumThumb455()==85,"minimum clamps to track excluding arrows");bar.SetSize(12,1000);check(bar.GetMinimumThumb455()==85,"growing size does not restore previous requested minimum");
    bar.SetAutoThumb455(FALSE);POINT manual={5,18};bar.SetBarSize(manual);bar.SetSize(12,100);bar.SetAmount(80,40);check(bar.GetScrollLength455()==67&&bar.GetThumb455().GetPosY()==241,"manual thumb and signed integer projection");manual.y=28;bar.SetBarSize(manual);check(bar.GetScrollLength455()==57&&bar.GetThumb455().GetPosY()==241,"length is queried dynamically without forced position update");bar.UpdateBar();check(bar.GetThumb455().GetPosY()==236,"explicit update uses new track");
    manual.y=18;bar.SetBarSize(manual);bar.SetAmount(80,0);bar.SetAdjustmentUnit(10);check(bar.CalculateAmount455(0)==0&&bar.CalculateAmount455(4)==0&&bar.CalculateAmount455(5)==10&&bar.CalculateAmount455(33)==40&&bar.CalculateAmount455(67)==80,"pixel-to-amount golden snap boundaries");
    bar.SetMinimumThumb455(20);bar.SetAutoThumb455(TRUE);bar.SetAmount(3,0);bar.SetAdjustmentUnit(10);check(bar.GetScrollLength455()==3&&bar.CalculateAmount455(1)==0&&bar.CalculateAmount455(2)==3,"total below adjustment splits at half");bar.SetMinimumThumb455(85);bar.SetAmount(3,0);check(bar.GetScrollLength455()==0&&bar.CalculateAmount455(0)==3,"target unordered small-range upper-half branch");
    bar.SetAutoThumb455(FALSE);manual.y=18;bar.SetBarSize(manual);bar.SetSize(12,34);bar.SetAmount(0x7fffffff,0);check(bar.GetScrollLength455()==1,"overflow fixture track1");check(!IsProcessorFeaturePresent(PF_XMMI64_INSTRUCTIONS_AVAILABLE)||bar.CalculateAmount455(2)==static_cast<int>(0x80000012u),"target SSE2 int32 overflow conversion and snap");bar.SetSize(12,37);bar.SetAmount(0x40000000,0x40000000);check(bar.GetScrollLength455()==4&&bar.GetThumb455().GetPosY()==208,"UpdateBar signed32 product wraps");
    CGUIScrollbar horizontal;shape(horizontal,10,20,100,12);horizontal.SetStyle(CGUIScrollbar::Horizontal);horizontal.SetAmount(25,10);check(horizontal.GetThumb455().GetSizeX()==53&&horizontal.GetScrollLength455()==25&&horizontal.GetThumb455().GetPosX()==32&&horizontal.GetThumb455().GetPosY()==17,"horizontal first-attach cross-axis centering");check(horizontal.GetTopArrow455().GetPosY()==22&&horizontal.GetBottomArrow455().GetPosX()==100,"horizontal arrows");
    Observer observer;observer.owner=&bar;bar.AddScrollHandler(&observer);shape(bar);bar.SetAutoThumb455(FALSE);bar.SetBarSize(manual);bar.SetSize(12,100);bar.SetAmount(100,40);bar.SetAdjustmentUnit(10);bar.SetArrowAdjustmentUnit(0);const auto priorClock=RF455_SetScrollbarClock(replayClock);
    timeline({1000,1001});mouse(bar,bar.GetTopArrow455(),MOUSE_STROKED);observer.drain();check(bar.GetCurrentAmount()==30&&bar.GetStrokeTime455()==1000&&bar.GetLastScrollTime455()==1001&&tickIndex==2&&observer.ids==std::vector<WORD>{30}&&observer.values[0]==30,"stroke clocks and actual event queue");observer.clear();timeline({1150});mouse(bar,bar.GetTopArrow455(),MOUSE_PRESSED);observer.drain();check(bar.GetCurrentAmount()==30&&tickIndex==1&&observer.ids.empty(),"repeat below150ms");timeline({1151,1152,1153});mouse(bar,bar.GetTopArrow455(),MOUSE_PRESSED);observer.drain();check(bar.GetCurrentAmount()==20&&tickIndex==3&&observer.ids==std::vector<WORD>{30}&&observer.times[0]==1153,"repeat re-queries time and sends after clamp");observer.clear();
    timeline({0xfffffff0});bar.SendScrollEvent(30);observer.drain();observer.clear();timeline({0x86,0x87,0x88});mouse(bar,bar.GetBottomArrow455(),MOUSE_PRESSED);observer.drain();check(bar.GetCurrentAmount()==30&&bar.GetLastScrollTime455()==0x88,"DWORD clock wrap");observer.clear();
    bar.SetArrowAdjustmentUnit(3);timeline({500,501});mouse(bar,bar.GetBottomArrow455(),MOUSE_STROKED);observer.drain();check(bar.GetCurrentAmount()==33&&observer.ids==std::vector<WORD>{31},"arrow override unit");observer.clear();bar.SetArrowAdjustmentUnit(0);
    bar.SetCurrentAmount(80);timeline({600});mouse(bar,bar,MOUSE_STROKED,100,208+18/2+13);observer.drain();check(bar.GetCurrentAmount()==20&&observer.ids==std::vector<WORD>{31},"in-range upward track click sends DOWN after update");observer.clear();
    const auto thumbY=bar.GetThumb455().GetPosY();timeline({});mouse(bar,bar.GetThumb455(),MOUSE_STROKED,103,thumbY+3);check(tickIndex==0&&bar.GetThumb455().GetPressed455()==1,"thumb grab and pressed cap state");timeline({700});drag(bar,103,208+3+15);observer.drain();check(bar.GetCurrentAmount()==20&&bar.GetThumb455().GetPosY()==223&&observer.ids.empty(),"drag keeps free pixel position inside same snapped amount");
    timeline({701});mouse(bar,bar.GetThumb455(),MOUSE_RELEASED,103,226);observer.drain();check(tickIndex==0&&bar.GetThumb455().GetPressed455()==0&&bar.GetThumb455().GetPosY()==221,"release re-aligns without event when amount unchanged");
    timeline({800});mouse(bar,bar.GetThumb455(),MOUSE_STROKED,103,bar.GetThumb455().GetPosY()+2);drag(bar,103,10000);observer.drain();check(bar.GetCurrentAmount()==100&&bar.GetThumb455().GetPosY()==275&&observer.ids==std::vector<WORD>{31},"drag clamps to lower endpoint");observer.clear();timeline({801});drag(bar,103,-100);observer.drain();check(bar.GetCurrentAmount()==0&&bar.GetThumb455().GetPosY()==208&&observer.ids==std::vector<WORD>{31},"drag upper endpoint retains post-update direction quirk");observer.clear();RF455_SetScrollbarClock(priorClock);
    bar.SetAmount(0,0);check(bar.GetAddedObjectNum()==2&&!bar.IsAddedObject(&bar.GetThumb455()),"zero total removes thumb with three children");CGUIObject extra;bar.Add(&extra);bar.SetAmount(100,50);check(bar.GetAddedObjectNum()==4,"extra child fixture");bar.SetAmount(0,0);check(bar.IsAddedObject(&bar.GetThumb455())&&bar.GetAddedObjectNum()==4,"target only removes thumb when count equals3");bar.Remove(&extra);bar.SetAmount(0,0);
    CSprite sprite;sprite.LoadSprite(const_cast<char*>("common.spr"));check(sprite.GetMaxActions()>2&&sprite.GetMaxFrames(2)>=4,"real arrow sprites");
    const unsigned realFrames=sprite.GetMaxFrames(2);sprite.SetAction(2);sprite.SetFrame(49);check(sprite.GetNowFrames(2)==(realFrames>49?49:realFrames-1),"target SetFrame clamps unavailable cap");
    CGUIScrollbar painted;POINT top={sprite.GetSpriteOrgXL(2,0),sprite.GetSpriteOrgYL(2,0)},bottom={sprite.GetSpriteOrgXL(2,2),sprite.GetSpriteOrgYL(2,2)};SPRITE_INFO up[2]={{&sprite,2,0},{&sprite,2,1}},down[2]={{&sprite,2,2},{&sprite,2,3}};
    painted.SetTopArrowSpriteInfo(up);painted.SetBottomArrowSpriteInfo(down);painted.SetTopArrowSize(top);painted.SetBottomArrowSize(bottom);painted.SetPos(50,50);painted.SetBarColor455(0xff70635d);painted.SetSize(top.x,180);painted.SetAmount(100,40);painted.Show(TRUE);const unsigned plain=capture(painted,"scrollbar-plain.bgra");check(plain>100,"real plain scrollbar pixels");
    painted.SetBarColor455(0xffffffff);painted.GetThumb455().SetSegmented455(&sprite);sprite.SetAction(2);sprite.SetFrame(44);check(painted.GetThumb455().GetSegment455(0).GetSizeY()==sprite.GetSpriteOrgYL(),"cap dimensions use clamped frame");
    const unsigned segmented=capture(painted,"scrollbar-segmented.bgra");painted.GetThumb455().SetPressed455(1);const unsigned pressed=capture(painted,"scrollbar-pressed.bgra");check(segmented>100&&pressed>100&&painted.GetThumb455().GetSegment455(0).GetSpriteInfo()->wFrameNo==47&&painted.GetThumb455().GetSegment455(2).GetSpriteInfo()->wFrameNo==49,"requested pressed metadata retained despite frame clamp");
    CSprite fixture;fixture.LoadSprite(const_cast<char*>("thumb-fixture.spr"));check(fixture.GetMaxFrames(2)==50,"owned six-cap fixture");painted.GetThumb455().SetPressed455(0);painted.GetThumb455().SetSegmented455(&fixture);check(painted.GetThumb455().GetSegment455(0).GetSizeY()==6&&painted.GetThumb455().GetSegment455(2).GetSizeY()==6,"complete cap heights match fixed12 split");
    auto* device=GetD3dDevice();DWORD oldMin=0,oldMag=0;device->GetSamplerState(0,D3DSAMP_MINFILTER,&oldMin);device->GetSamplerState(0,D3DSAMP_MAGFILTER,&oldMag);device->SetSamplerState(0,D3DSAMP_MINFILTER,D3DTEXF_POINT);device->SetSamplerState(0,D3DSAMP_MAGFILTER,D3DTEXF_POINT);
    const unsigned synthetic=capture(painted,"scrollbar-synthetic.bgra");const int sampleX=painted.GetThumb455().GetPosX()+2,sampleY=painted.GetThumb455().GetPosY()+11;check(framePixel("scrollbar-synthetic.bgra",sampleX,sampleY)==0x00ff00,"middle copies the original row2 rather than stretching gray rows");
    painted.GetThumb455().SetPressed455(1);const unsigned syntheticPressed=capture(painted,"scrollbar-synthetic-pressed.bgra");check(synthetic>100&&syntheticPressed>100&&framePixel("scrollbar-synthetic-pressed.bgra",sampleX,sampleY)==0x00ffff,"owned pressed row2 GPU output");painted.GetThumb455().SetSegmented455(nullptr);device->SetSamplerState(0,D3DSAMP_MINFILTER,oldMin);device->SetSamplerState(0,D3DSAMP_MAGFILTER,oldMag);
    fixture.ReleaseSprite();sprite.ReleaseSprite();bar.AddScrollHandler(nullptr);R3ReleaseTextTexture();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();FILE* output=std::fopen("result.json","wb");check(output!=nullptr,"result output");
    std::fprintf(output,"{\"status\":\"PASS\",\"codepage\":%u,\"ordinary_scrollbar\":true,\"composite_thumb\":true,\"vertical_horizontal_geometry\":true,\"minimum_and_linear_auto_size\":true,\"x87_snap_and_SSE2_int32\":true,\"DWORD_repeat_clock_and_query_order\":true,\"mouse_drag_release_and_direction_quirk\":true,\"actual_queued_scroll_events\":true,\"child_count_removal_quirk\":true,\"real_action2_frames\":%u,\"plain_pixels\":%u,\"segmented_pixels\":%u,\"pressed_pixels\":%u,\"synthetic_pixels\":%u,\"synthetic_pressed_pixels\":%u,\"full_EX_Var\":false,\"full_parent_bubbling\":false,\"full_briefing\":false,\"full_Tutorial\":false}\n",RF455_GetNormalLanguagePack()->codepage,realFrames,plain,segmented,pressed,synthetic,syntheticPressed);std::fclose(output);return 0;
}
static LONG filter(EXCEPTION_POINTERS* info){return info->ExceptionRecord->ExceptionCode==0xe06d7363?EXCEPTION_CONTINUE_SEARCH:EXCEPTION_EXECUTE_HANDLER;}
static int guarded(){__try{return run();}__except(filter(GetExceptionInformation())){return 99;}}
int main(){try{return guarded();}catch(const std::exception& error){std::fprintf(stderr,"Scrollbar: %s\n",error.what());return 1;}}
