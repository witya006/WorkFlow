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
#include "client455_option_window.h"
#include "client455_language.h"
#include "client455_nation_paths.h"
#include "client455_font.h"
#include <wrl/client.h>
#include <cstdio>
#include <stdexcept>
#include <vector>
#include <utility>
#include <limits>
#include <cmath>

extern CMainApp g_MainApp;
template<class Tag,typename Tag::Type Value> struct SettingsMember {friend typename Tag::Type member(Tag){return Value;}};
struct InputTag{using Type=CInputMgr CMainApp::*;friend Type member(InputTag);};
template struct SettingsMember<InputTag,&CMainApp::m_cInputMgr>;
struct QueueTag{using Type=void(*)(WORD);friend Type member(QueueTag);};
template struct SettingsMember<QueueTag,&CGUIObject::CreateEventQueue>;
struct QueueProcessTag{using Type=void(*)();friend Type member(QueueProcessTag);};
template struct SettingsMember<QueueProcessTag,&CGUIObject::EventProcess>;

static std::vector<std::pair<UINT,WPARAM>> messages;
static LRESULT CALLBACK probeWindow(HWND hwnd,UINT message,WPARAM value,LPARAM other){
    if(message>=0x600&&message<=0x62f){messages.emplace_back(message,value);return 0;}
    return DefWindowProcW(hwnd,message,value,other);
}
static void check(bool condition,const char* message){if(!condition)throw std::runtime_error(message);}
static void click(CGUIOptionWindow& window,CGUIObject& object){_mouse_event event={};event.source=&object;event.id=MOUSE_CLICKED;window.MouseEvent(event);}
static unsigned actionCalls[2]={};
static bool actionsBlocked=false;
static void logoutAction(){++actionCalls[0];}
static void quitAction(){++actionCalls[1];}
static bool blockActions(){return actionsBlocked;}
static void actionMouseFrame(CGUIScreen& screen,LONG x,LONG y,DWORD buttons){
    gMouse.x=x;gMouse.y=y;gMouse.z=0;gMouse.button=buttons;
    gMouseDev.Update();screen.InputProc();
}
static void checkActionButtons(CGUIOptionWindow& window,CGUIScreen& screen){
    RF455OptionActions actions;actions.logout=logoutAction;actions.quit=quitAction;actions.blocked=blockActions;
    window.SetActions455(actions);window.Update();
    auto& logout=window.Action455(0);auto& quit=window.Action455(1);auto& close=window.Close455();
    check(window.IsAddedObject(&logout)&&window.IsAddedObject(&quit)&&
          !window.Page455(CGUIOptionWindow::GamePage).IsAddedObject(&logout),"actions belong to settings header");
    check(logout.GetPosY()==quit.GetPosY()&&quit.GetPosY()==close.GetPosY()&&
          logout.GetPosX()+logout.GetSizeX()<quit.GetPosX()&&
          quit.GetPosX()+quit.GetSizeX()<close.GetPosX(),"header actions are adjacent and distinct");
    for(unsigned page=0;page<CGUIOptionWindow::PageCount;++page){
        click(window,window.Tab455(page));
        for(unsigned index=0;index<2;++index){
            auto& button=window.Action455(index);
            const LONG x=button.GetPosX()+button.GetSizeX()/2,y=button.GetPosY()+button.GetSizeY()/2;
            actionMouseFrame(screen,x,y,0);
            check(window.SelectedPage455()==page&&button.IsShow()&&
                  CGUIObject::GetMouseDetectedObject()==&button,"header action hit target on every tab");
        }
    }
    for(unsigned index=0;index<2;++index){
        auto& button=window.Action455(index);
        const LONG x=button.GetPosX()+button.GetSizeX()/2,y=button.GetPosY()+button.GetSizeY()/2;
        actionMouseFrame(screen,x,y,0);actionMouseFrame(screen,x,y,_LEFT_BUTTON_DOWN);actionMouseFrame(screen,x,y,0);
        check(actionCalls[index]==1&&actionCalls[1-index]==(index?1u:0u),"one callback per real mouse click");
    }
    actionsBlocked=true;
    click(window,logout);click(window,quit);
    check(actionCalls[0]==1&&actionCalls[1]==1,"blocked actions do not dispatch");
    actionsBlocked=false;window.SetLogoutRestricted455(TRUE);window.Update();
    check((logout.GetState()&DISABLED)&&(quit.GetState()&DISABLED),"restricted actions disabled");
    click(window,logout);click(window,quit);
    check(actionCalls[0]==1&&actionCalls[1]==1,"restricted actions do not dispatch");
    window.SetLogoutRestricted455(FALSE);window.SetActions455({});window.Update();
    check((logout.GetState()&DISABLED)&&(quit.GetState()&DISABLED),"missing callbacks disabled");
    click(window,logout);click(window,quit);
    check(actionCalls[0]==1&&actionCalls[1]==1,"missing callbacks do not dispatch");
    window.SetActions455(actions);window.Update();
    check(!(logout.GetState()&DISABLED)&&!(quit.GetState()&DISABLED),"world actions restored");
}
static void checkSeeDistance(CGUIOptionWindow& window){
    auto* manager=g_pCharacterMgr;check(manager!=nullptr,"existing character manager");
    auto* previousOptions=g_pUiOptionWindow;g_pUiOptionWindow=&window;
    const BYTE originalLevel=manager->GetVisualFieldAdjustmentLevel();
    const BOOL originalAuto=manager->IsEnableAutoVisualFieldAdjustment();
    const float originalDistance=manager->GetVisualField();
    check(window.Graphic455(CGUIOptionWindow::SeeDist).GetTotalAmount()==3,"four slider positions");
    manager->EnableAutoVisualFieldAdjustment(FALSE);
    for(BYTE level=1;level<=4;++level){
        window.SetGraphicOption(CGUIOptionWindow::SeeDist,float(level));
        check(window.Graphic455(CGUIOptionWindow::SeeDist).GetCurrentAmount()==level-1&&
              window.GetGraphicOption(CGUIOptionWindow::SeeDist)==float(level),"UI level roundtrip1..4");
        manager->SetVisualFieldAdjustmentLevel(BYTE(window.GetGraphicOption(CGUIOptionWindow::SeeDist)));
        check(manager->GetVisualFieldAdjustmentLevel()==level&&
              manager->GetVisualField()==200.f+50.f*(level-1),"manual distance200..350");
    }
    for(const auto value:{std::pair<BYTE,BYTE>{0,1},{255,4}}){
        manager->SetVisualFieldAdjustmentLevel(value.first);
        check(manager->GetVisualFieldAdjustmentLevel()==value.second&&
              window.GetGraphicOption(CGUIOptionWindow::SeeDist)==float(value.second),"manager clamps boundary input");
        window.SetGraphicOption(CGUIOptionWindow::SeeDist,float(value.first));
        check(window.GetGraphicOption(CGUIOptionWindow::SeeDist)==float(value.second),"UI clamps boundary input");
    }
    for(const auto value:{std::pair<float,float>{150.f,200.f},{450.f,350.f},
                           {std::numeric_limits<float>::quiet_NaN(),350.f},
                           {std::numeric_limits<float>::infinity(),350.f}}){
        manager->SetVisualField(value.first);manager->EnableAutoVisualFieldAdjustment(TRUE);
        check(std::isfinite(manager->GetVisualField())&&manager->GetVisualField()==value.second,"automatic distance clamps immediately");
    }
    manager->SetVisualFieldAdjustmentLevel(2);
    check(manager->GetVisualField()==350.f,"automatic mode retains dynamic distance");
    manager->EnableAutoVisualFieldAdjustment(FALSE);
    check(manager->GetVisualField()==250.f,"disabling auto restores stored manual level");
    manager->SetVisualFieldAdjustmentLevel(originalLevel);manager->EnableAutoVisualFieldAdjustment(originalAuto);
    manager->SetVisualField(originalDistance);g_pUiOptionWindow=previousOptions;
    window.Close();window.Open();
}
static void checkVSync(CGUIOptionWindow& window){
    using Microsoft::WRL::ComPtr;
    ComPtr<IDirect3DSwapChain9> chain;
    check(SUCCEEDED(GetD3dDevice()->GetSwapChain(0,&chain)),"VSync current swap chain");
    D3DPRESENT_PARAMETERS before={},after={};
    check(SUCCEEDED(chain->GetPresentParameters(&before)),"VSync initial present parameters");
    check(!window.RequestedVSync455(),"absent VSync key defaults off");
    window.SetPage455(CGUIOptionWindow::ImagePage);
    check(window.VSync455(0).GetPosY()>=window.Resolution455(0).GetPosY()+window.Resolution455(0).GetSizeY(),
          "VSync controls do not overlap resolution controls");
    click(window,window.VSync455(1));
    check(window.RequestedVSync455()&&GetPrivateProfileIntA("RenderState","VSync",0,".\\R3Engine.ini")==0,
          "VSync enabled draft does not persist");
    click(window,window.CancelButton455());window.Open();
    check(!window.RequestedVSync455()&&GetPrivateProfileIntA("RenderState","VSync",0,".\\R3Engine.ini")==0,
          "VSync cancel restores off");
    click(window,window.VSync455(1));check(window.Apply455(),"apply VSync on");
    check(GetPrivateProfileIntA("RenderState","VSync",0,".\\R3Engine.ini")==1,"VSync on persisted");
    window.Close();window.Open();check(window.RequestedVSync455(),"VSync on survives reopen");
    {CGUIOptionWindow reloaded;reloaded.Init();check(reloaded.RequestedVSync455(),"new settings owner reads persisted VSync on");}
    click(window,window.VSync455(0));click(window,window.CancelButton455());window.Open();
    check(window.RequestedVSync455()&&GetPrivateProfileIntA("RenderState","VSync",0,".\\R3Engine.ini")==1,
          "VSync cancel after apply restores on");
    click(window,window.VSync455(0));check(window.Apply455(),"apply VSync off");
    check(GetPrivateProfileIntA("RenderState","VSync",1,".\\R3Engine.ini")==0,"VSync off persisted");
    {CGUIOptionWindow reloaded;reloaded.Init();check(!reloaded.RequestedVSync455(),"new settings owner reads persisted VSync off");}
    check(SUCCEEDED(chain->GetPresentParameters(&after))&&after.PresentationInterval==before.PresentationInterval&&
          after.BackBufferWidth==before.BackBufferWidth&&after.BackBufferHeight==before.BackBufferHeight,
          "VSync apply preserves live presentation until restart");
}
static void capture(CGUIOptionWindow& window,const char* file){
    auto* device=GetD3dDevice();check(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET,0xff101720,1,0)),"clear");
    check(SUCCEEDED(device->BeginScene()),"begin scene");check(window.Draw()!=FALSE,"draw settings");
    check(SUCCEEDED(device->EndScene()),"end scene");
    IDirect3DSurface9* surface=nullptr;check(SUCCEEDED(device->GetRenderTarget(0,&surface)),"render target");
    D3DSURFACE_DESC desc={};surface->GetDesc(&desc);check(desc.Width==1920&&desc.Height==1080,"Full HD frame");
    using Save=HRESULT(WINAPI*)(const char*,D3DXIMAGE_FILEFORMAT,IDirect3DSurface9*,const PALETTEENTRY*,const RECT*);
    auto library=GetModuleHandleA("d3dx9_36.dll");if(!library)library=LoadLibraryA("d3dx9_36.dll");
    auto save=library?reinterpret_cast<Save>(GetProcAddress(library,"D3DXSaveSurfaceToFileA")):nullptr;
    check(save&&SUCCEEDED(save(file,D3DXIFF_PNG,surface,nullptr,nullptr)),"PNG capture");surface->Release();
}
static int run(){
    using Microsoft::WRL::ComPtr;
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"language");InitR3Engine();
    check(GetR3State()->mScreenXsize==1920&&GetR3State()->mScreenYsize==1080,"configured Full HD");
    WNDCLASSW cls={};cls.lpfnWndProc=probeWindow;cls.hInstance=GetModuleHandleW(nullptr);cls.lpszClassName=L"RF455SettingsProbe";
    check(RegisterClassW(&cls)!=0,"class registration");
    HWND hwnd=CreateWindowExW(0,cls.lpszClassName,cls.lpszClassName,WS_POPUP,0,0,1920,1080,nullptr,nullptr,cls.hInstance,nullptr);
    check(hwnd&&!IsWindowVisible(hwnd),"hidden Full HD window");
    ComPtr<IDirect3D9> api;api.Attach(Direct3DCreate9(D3D_SDK_VERSION));D3DDISPLAYMODE desktop={};
    check(api&&SUCCEEDED(api->GetAdapterDisplayMode(0,&desktop)),"adapter");
    D3DPRESENT_PARAMETERS mode={};mode.BackBufferWidth=1920;mode.BackBufferHeight=1080;mode.BackBufferCount=1;
    mode.BackBufferFormat=desktop.Format;mode.SwapEffect=D3DSWAPEFFECT_DISCARD;mode.Windowed=TRUE;mode.hDeviceWindow=hwnd;
    ComPtr<IDirect3DDevice9> device;
    check(SUCCEEDED(api->CreateDevice(0,D3DDEVTYPE_HAL,hwnd,D3DCREATE_SOFTWARE_VERTEXPROCESSING,&mode,&device)),"hardware device");
    GetR3State()->mIsUsedVertexShader=FALSE;check(SUCCEEDED(D3D_R3InitDevice(device.Get())),"engine binding");
    SetViewPortArea(0,0,1920,1080);check(SUCCEEDED(RF455_LoadTextResources(device.Get(),200000000)),"font");
    member(QueueTag{})(256);g_pUiSpriteMgr=&gSpriteMgr;gSpriteMgr.Init();gSpriteMgr.LoadSprite(SP_ID_COMMON);
    for(unsigned id:{1u,5u}){
        auto* sprite=gSpriteMgr.GetTargetSprite455(id);
        const unsigned action=id==1?8:0;
        std::fprintf(stderr,"Settings atlas %u: actions=%u, action%u frames=%u\n",id,
            sprite?sprite->GetMaxActions():0,action,
            sprite&&sprite->GetMaxActions()>action?sprite->GetMaxFrames(action):0);
    }
    auto* screen=CGUIScreen::GetSingletonPtr();check(screen!=nullptr,"screen");g_pUiScreen=screen;
    g_pUiInputMgr=&(g_MainApp.*member(InputTag{}));screen->SetHWND(hwnd);screen->SetSize(1920,1080);
    // This executable runs in its own staged fixture, never the installed game.
    check(WritePrivateProfileStringA("RenderState","VSync",nullptr,".\\R3Engine.ini")!=FALSE,"clear fixture VSync key");
    {
        CGUIOptionWindow window;window.Init();window.SetPos(600,220);screen->Add(&window);window.Open();
        check(window.GetSizeX()==720&&window.GetSizeY()==560,"settings layout");
        checkSeeDistance(window);
        checkVSync(window);
        checkActionButtons(window,*screen);
        for(unsigned page=0;page<CGUIOptionWindow::PageCount;++page){
            click(window,window.Tab455(page));
            check(window.SelectedPage455()==page,"tab click");
            for(unsigned other=0;other<CGUIOptionWindow::PageCount;++other)
                check(bool(window.IsAddedObject(&window.Page455(other)))==(other==page),"inactive pages detached");
            window.Close();window.Open();
            for(unsigned other=0;other<CGUIOptionWindow::PageCount;++other)
                check(bool(window.IsAddedObject(&window.Page455(other)))==(other==page),"reopen keeps a single page");
            auto& content=window.Page455(page);
            for(unsigned child=0;child<content.GetAddedObjectNum();++child){
                auto* control=content.GetAddedObject(WORD(child));
                check(control->GetPosX()>=window.GetPosX()&&control->GetPosY()>=window.GetPosY()&&
                      control->GetPosX()+control->GetSizeX()<=window.GetPosX()+window.GetSizeX()&&
                      control->GetPosY()+control->GetSizeY()<=window.GetPosY()+window.GetSizeY(),"page child stays inside moved window");
            }
            char file[32];std::sprintf(file,"settings-%u.png",page);capture(window,file);
        }
        const auto before=GetPrivateProfileIntA("RenderState","MSAA",99,".\\R3Engine.ini");
        window.SetPage455(CGUIOptionWindow::HUDPage);click(window,window.Diagnostics455(0));
        check(GetPrivateProfileIntA("HUD","LobbyDiagnostics",1,".\\R3Engine.ini")==1,"diagnostics draft not persisted");
        click(window,window.CancelButton455());window.Open();
        check(window.Apply455()&&GetPrivateProfileIntA("HUD","LobbyDiagnostics",0,".\\R3Engine.ini")==1,"diagnostics cancel restores enabled");
        window.SetPage455(CGUIOptionWindow::HUDPage);click(window,window.Diagnostics455(0));
        check(window.Apply455()&&GetPrivateProfileIntA("HUD","LobbyDiagnostics",1,".\\R3Engine.ini")==0,"diagnostics apply persists hidden");
        click(window,window.Diagnostics455(1));check(window.Apply455(),"restore diagnostic HUD");
        window.SetPage455(CGUIOptionWindow::GraphicsPage);click(window,window.Multisampling455(0));
        check(window.RequestedMultisampling455()==0&&GetPrivateProfileIntA("RenderState","MSAA",99,".\\R3Engine.ini")==before,"draft not persisted");
        click(window,window.CancelButton455());window.Open();check(window.RequestedMultisampling455()==before,"cancel restores saved draft");
        click(window,window.Multisampling455(1));window.SetPage455(CGUIOptionWindow::ImagePage);click(window,window.Resolution455(0));
        window.Sound455(CGUIOptionWindow::BGM).SetCurrentAmount(80);
        window.SetGraphicOption(CGUIOptionWindow::SeeDist,2);messages.clear();
        check(window.Apply455(),"apply settings");
        check(GetPrivateProfileIntA("RenderState","MSAA",99,".\\R3Engine.ini")==2,"MSAA persisted");
        check(GetPrivateProfileIntA("RenderState","ScreenXSize",0,".\\R3Engine.ini")==1280&&
              GetPrivateProfileIntA("RenderState","ScreenYSize",0,".\\R3Engine.ini")==720,"future resolution persisted");
        check(messages.size()==8,"all implemented stage messages");
        check(messages[0].first==WM_OPTION_ADJUST_EFFECT_SOUND&&messages[1].first==WM_OPTION_ADJUST_BGM_SOUND,"volume route");
        check(messages[4].first==WM_OPTION_CHANGE_VF_DIST&&messages[4].second==2&&
              GetPrivateProfileIntA("Performance","VisualFieldAdjustmentLevel",0,".\\DataTable\\GameSetting.ini")==2,"logical distance level persists and dispatches");
        check(messages.back().first==WM_OPTION_TOGGLE_HINT,"HUD route");
        window.Close();window.Open();check(window.RequestedMultisampling455()==2,"apply survives close and reopen");
        D3DVIEWPORT9 actual={};device->GetViewport(&actual);check(actual.Width==1920&&actual.Height==1080,"restart-only resolution leaves current Full HD intact");
        window.Close();screen->Remove(&window);member(QueueProcessTag{})();
    }
    gSpriteMgr.UnloadSpriteAll();RF455_ReleaseTextResources();D3D_R3DeleteDevice();device.Reset();DestroyWindow(hwnd);ReleaseR3Engine();
    FILE* result=std::fopen("result.json","wb");check(result!=nullptr,"result");
    std::fprintf(result,"{\"status\":\"PASS\",\"tabs\":5,\"resolution\":[1920,1080],\"native_widgets\":true,\"action_hit_targets_all_tabs\":true,\"action_blocked_missing_single_dispatch\":true,\"inactive_pages_detached\":true,\"cancel\":true,\"apply_persist_reopen\":true,\"vsync_default_off\":true,\"vsync_draft_cancel_apply_reload\":true,\"vsync_restart_only\":true,\"see_distance_levels1to4\":true,\"manager_boundary_clamp\":true,\"auto_distance_finite_clamp\":true,\"stage_messages\":8,\"live_backend\":false}\n");std::fclose(result);return 0;
}
int main(){try{return run();}catch(const std::exception& error){std::fprintf(stderr,"Settings: %s\n",error.what());return 1;}}
