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
#include "userinterface/gamewindow/etcwin/guiminimapwindow.h"
#include "mainapp.h"
#include "client455_minimap_opacity.h"
#include "client455_language.h"
#include "client455_nation_paths.h"
#include <cstdio>
#include <stdexcept>
extern CMainApp g_MainApp;
template<class Tag,typename Tag::Type Member>struct MemberAccess{friend typename Tag::Type access(Tag){return Member;}};
#define FIELD(Tag,TypeName,Class,member) struct Tag{using Type=TypeName Class::*;friend Type access(Tag);};template struct MemberAccess<Tag,&Class::member>;
FIELD(SpriteMember,CSpriteMgr,CMainApp,m_cSpriteMgr)
FIELD(ScreenMember,CGUIScreen,CMainApp,m_cScreen)
FIELD(Suppress,BOOL,CGUIMiniMapWindow,m_suppressZoom455)
FIELD(ClearSuppression,BOOL,CGUIMiniMapWindow,m_clearZoomSuppression455)
FIELD(Title,CGUIText,CGUIMiniMapWindow,m_uiTitle)
FIELD(Close,CGUIButton,CGUIMiniMapWindow,m_uiCloseButton)
FIELD(MapObjects,CGUIMiniMapObjList,CGUIMiniMapWindow,m_listMiniMapObject)
FIELD(Tooltips,CGUIMiniMapTooltipList,CGUIMiniMapWindow,m_listTooltipList)
struct QueueCreate{using Type=void(*)(WORD);friend Type access(QueueCreate);};
struct QueueProcess{using Type=void(*)();friend Type access(QueueProcess);};
struct MouseClear{using Type=void(*)();friend Type access(MouseClear);};
struct Load{using Type=BOOL(CMainApp::*)();friend Type access(Load);};
struct Unload{using Type=BOOL(CMainApp::*)();friend Type access(Unload);};
template struct MemberAccess<QueueCreate,&CGUIObject::CreateEventQueue>;
template struct MemberAccess<QueueProcess,&CGUIObject::EventProcess>;
template struct MemberAccess<MouseClear,&CGUIObject::ClearMouseEventBuffer>;
template struct MemberAccess<Load,&CMainApp::LoadData>;
template struct MemberAccess<Unload,&CMainApp::UnloadData>;
static void check(bool condition,const char* why){if(!condition)throw std::runtime_error(why);}
static void frameInput(CGUIMiniMapWindow& window,LONG x,LONG y,bool down){
    gMouse.x=x;gMouse.y=y;gMouse.z=0;gMouse.button=down?_LEFT_BUTTON_DOWN:0;gMouseDev.Update();access(MouseClear{})();check(window.InputProc()!=0,"actual owner InputProc");access(QueueProcess{})();
}
static unsigned capture(CGUIMiniMapWindow& window,const char* filename){
    auto* device=GetD3dDevice();check(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET,0xff102030,1,0))&&SUCCEEDED(device->BeginScene()),"frame begin");
    //This is actual recovered owner Draw;the map producer remains unported.
    check(window.Draw()!=0,"ordinary owner Draw before map selection");check(SUCCEEDED(device->EndScene()),"frame end");
    IDirect3DSurface9* target=nullptr;IDirect3DSurface9* memory=nullptr;check(SUCCEEDED(device->GetRenderTarget(0,&target)),"target");D3DSURFACE_DESC desc={};target->GetDesc(&desc);check(SUCCEEDED(device->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&memory,nullptr)),"read surface");check(SUCCEEDED(device->GetRenderTargetData(target,memory)),"readback");D3DLOCKED_RECT lock={};check(SUCCEEDED(memory->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"lock");D3DVIEWPORT9 view={};device->GetViewport(&view);check(view.Width==640&&view.Height==480,"viewport");FILE* output=std::fopen(filename,"wb");check(output!=nullptr,"frame output");unsigned pixels=0;
    for(unsigned y=view.Y;y<view.Y+view.Height;++y){auto* row=reinterpret_cast<const DWORD*>(static_cast<const BYTE*>(lock.pBits)+y*lock.Pitch)+view.X;std::fwrite(row,4,view.Width,output);for(unsigned x=0;x<view.Width;++x)pixels+=(row[x]&0xffffff)!=0x102030;}
    std::fclose(output);memory->UnlockRect();memory->Release();target->Release();return pixels;
}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"language");InitR3Engine();GetR3State()->mScreenXsize=640;GetR3State()->mScreenYsize=480;GetR3State()->mbFullScreen=FALSE;ForceFullScreen();check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"D3D init");
    g_pUiSpriteMgr=&(g_MainApp.*access(SpriteMember{}));g_pUiScreen=&(g_MainApp.*access(ScreenMember{}));check((g_MainApp.*access(Load{}))()!=0,"actual LoadData");access(QueueCreate{})(128);
    auto* common=gSpriteMgr.GetSprite(SP_ID_COMMON);check(common!=nullptr,"real common");unsigned full=0,half=0,lowest=0;
    {
        CGUIScrollbarEX style;RF455_ConfigureOpacityScrollbar(nullptr,common);RF455_ConfigureOpacityScrollbar(&style,common,0);check(style.GetSizeX()==194&&style.GetSizeY()==13&&style.GetButton455().GetSizeX()==10,"style0 real resource geometry");check(style.GetTopArrow455().GetSpriteInfo()->wFrameNo==17&&style.GetBottomArrow455().GetSpriteInfo()->wFrameNo==15,"style0 arrow order");
        style.GetButton455().SoundOn(FALSE);style.GetButton455().SetState(PRESSED|HOVERED);check(style.GetButton455().GetSpriteInfo()->wFrameNo==14,"style0 pressed frame14");style.GetButton455().SetState(0);
        RF455_ConfigureOpacityScrollbar(&style,common,1);check(style.GetSizeX()==192&&style.GetSizeY()==15&&style.GetButton455().GetSpriteInfo()->wFrameNo==7,"style1 direct image assignment");
        CGUIObject aligned;aligned.SetSize(7,9);POINT origin={10,20},extent={4,2};RF455_AlignGuiObject(aligned,origin,extent,-1,-1);check(aligned.GetPosX()==9&&aligned.GetPosY()==17,"alignment negative odd difference truncates toward0");RF455_AlignGuiObject(aligned,origin,extent,-2,-3);check(aligned.GetPosX()==10&&aligned.GetPosY()==13,"alignment edges");RF455_AlignGuiObject(aligned,origin,extent,-4,99);check(aligned.GetPosX()==-4&&aligned.GetPosY()==99,"alignment literal values");
        CGUIMiniMapWindow window;window.SetPos(30,40);window.Init();window.Show(TRUE);auto& bar=window.GetOpacityScrollbar455();bar.GetTopArrow455().SoundOn(FALSE);bar.GetBottomArrow455().SoundOn(FALSE);bar.GetButton455().SoundOn(FALSE);
        check(bar.GetSizeX()==194&&bar.GetSizeY()==13&&bar.GetPosX()==133&&bar.GetPosY()==57&&bar.GetTotalAmount()==80&&bar.GetCurrentAmount()==80&&window.GetAlpha455()==255,"actual owner centers frame then shifts15 and sets80/80");check(window.IsAddedObject(&bar)&&window.GetMapBackground455().GetSizeX()==400,"ordinary owner stores and adds real EX");
        full=capture(window,"minimap-opacity-full.bgra");check(full>10000,"actual main/common GPU pixels");
        (window.*access(Title{})).SetARGB(0xff123456);(window.*access(Close{})).SetARGB(0xff665544);
        window.AddMiniMapObject(CGUIMiniMapWindow::PartyLeader,41,1,2);window.AddTooltipObject(42,3,4,5,6,const_cast<char*>("opacity"));
        check((window.*access(MapObjects{})).size()==1&&(window.*access(Tooltips{})).size()==1,"actual populated owner lists");
        for(int current=0;current<=80;++current){bar.SetCurrentAmount(current);bar.SendScrollEvent(SCROLLED_UP);access(QueueProcess{})();check(window.GetAlpha455()==static_cast<BYTE>((current+20)*255/100)&&bar.GetARGB()>>24==window.GetAlpha455(),"all81queued owner opacity amounts");}
        bar.SetCurrentAmount(40);bar.SendScrollEvent(SCROLLED_DOWN);access(QueueProcess{})();check(window.GetAlpha455()==153&&window.GetMapBackground455().GetARGB()>>24==91,"background alpha0.6 route");
        check((window.*access(Title{})).GetARGB()==0x99123456&&(window.*access(Close{})).GetARGB()==0x99665544&&(window.*access(MapObjects{})).front()->uiObject.GetARGB()>>24==153&&(window.*access(Tooltips{})).front()->uiObject.GetARGB()>>24==153,"alpha propagates to mapped title/close/populated lists and preservesRGB");half=capture(window,"minimap-opacity-half.bgra");
        bar.SetCurrentAmount(0);bar.SendScrollEvent(SCROLLED_DOWN);access(QueueProcess{})();check(window.GetAlpha455()==51,"minimum20percent");lowest=capture(window,"minimap-opacity-low.bgra");
        bar.SetCurrentAmount(80);bar.SendScrollEvent(SCROLLED_DOWN);access(QueueProcess{})();frameInput(window,bar.GetPosX()+3,bar.GetPosY()+3,true);check(CGUIObject::GetPressedObject()==&bar.GetTopArrow455()&&bar.GetCurrentAmount()==79&&window.GetAlpha455()==252,"mouse device to owner to EX to queued alpha");frameInput(window,bar.GetPosX()+3,bar.GetPosY()+3,false);
        frameInput(window,bar.GetPosX()+53,bar.GetPosY()+3,true);check(bar.GetCurrentAmount()==17&&window.GetAlpha455()==94,"actual parent input track click retains EX base snap");frameInput(window,bar.GetPosX()+53,bar.GetPosY()+3,false);
        const LONG y=bar.GetPosY()+3;frameInput(window,bar.GetButton455().GetPosX()+3,y,true);const LONG end=bar.GetBottomArrow455().GetPosX()-bar.GetButton455().GetSizeX();frameInput(window,end+3,y,true);check(bar.GetCurrentAmount()==78&&bar.GetButton455().GetPosX()==end&&window.GetAlpha455()==249,"actual parent input drag endpoint uses inherited162 track");frameInput(window,end+3,y,false);check(bar.GetCurrentAmount()==78&&bar.GetButton455().GetPosX()==bar.GetTopArrow455().GetPosX()+13+154,"actual release realigns own158 track");
        window.SetAlpha455(100);check(window.GetMapBackground455().GetARGB()>>24==80&&window.TakeCameraZoomGate455(),"special alpha100 background0.8 and eligibility");window.*access(Suppress{})=TRUE;window.*access(ClearSuppression{})=TRUE;check(!window.TakeCameraZoomGate455()&&!(window.*access(Suppress{}))&&window.TakeCameraZoomGate455(),"zoom suppression acknowledgement clears only for next call");
        CGUIObject foreign;_scroll_event event={&foreign,SCROLLED_UP};bool refused=false;try{window.ScrollEvent(event);}catch(const std::domain_error&){refused=true;}check(refused,"unknown camera consumer explicitly refused even for foreign source");window.SetAlpha455(255);window.ScrollEvent(event);check(window.GetAlpha455()==255,"foreign source leaves alpha unchanged");
    }
    (g_MainApp.*access(Unload{}))();R3ReleaseTextTexture();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();FILE* output=std::fopen("result.json","wb");check(output!=nullptr,"result");std::fprintf(output,"{\"status\":\"PASS\",\"codepage\":%u,\"real_owner_EX\":true,\"style0_and1\":true,\"alignment\":true,\"queued_amounts\":81,\"actual_mouse_parent_path\":true,\"drag_release_quirk\":true,\"mapped_alpha_groups\":true,\"zoom_gate_state\":true,\"camera_consumer_refused\":true,\"full_pixels\":%u,\"half_pixels\":%u,\"low_pixels\":%u,\"full_minimap\":false,\"target_parent_input\":false,\"full_Tutorial\":false}\n",RF455_GetNormalLanguagePack()->codepage,full,half,lowest);std::fclose(output);return 0;
}
static LONG filter(EXCEPTION_POINTERS* info){return info->ExceptionRecord->ExceptionCode==0xe06d7363?EXCEPTION_CONTINUE_SEARCH:EXCEPTION_EXECUTE_HANDLER;}
static int guarded(){__try{return run();}__except(filter(GetExceptionInformation())){return 99;}}
int main(){try{return guarded();}catch(const std::exception& error){std::fprintf(stderr,"Minimap opacity: %s\n",error.what());return 1;}}
