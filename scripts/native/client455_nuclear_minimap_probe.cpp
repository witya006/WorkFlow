#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "item/citemmgr.h"
#include "input/imeedit.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "userinterface/gamewindow/etcwin/guiminimapwindow.h"
#include "mainapp.h"
#include <client455_nuclear_minimap.h>
#include <client455_language.h>
#include <client455_nation_paths.h>
#include <array>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <vector>
extern CMainApp g_MainApp;
template<class Tag,typename Tag::Type Member>struct MemberAccess{friend typename Tag::Type access(Tag){return Member;}};
struct SpriteOwner{using Type=CSpriteMgr CMainApp::*;friend Type access(SpriteOwner);};template struct MemberAccess<SpriteOwner,&CMainApp::m_cSpriteMgr>;
struct ScreenOwner{using Type=CGUIScreen CMainApp::*;friend Type access(ScreenOwner);};template struct MemberAccess<ScreenOwner,&CMainApp::m_cScreen>;
struct Load{using Type=BOOL(CMainApp::*)();friend Type access(Load);};template struct MemberAccess<Load,&CMainApp::LoadData>;
struct Unload{using Type=BOOL(CMainApp::*)();friend Type access(Unload);};template struct MemberAccess<Unload,&CMainApp::UnloadData>;
struct Map{using Type=CGUIContainer CGUIMiniMapWindow::*;friend Type access(Map);};template struct MemberAccess<Map,&CGUIMiniMapWindow::m_uiMiniMap>;
static unsigned checks=0;static void check(bool yes,const char* why){++checks;if(!yes)throw std::runtime_error(why);}
static std::vector<DWORD> capture(CGUIMiniMapWindow& window,const char* filename){
    auto* device=GetD3dDevice();check(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET,0xff102030,1,0))&&SUCCEEDED(device->BeginScene()),"capture begin");check(window.Draw()!=0,"actual MiniMap ordinary Draw");check(SUCCEEDED(device->EndScene()),"capture end");
    IDirect3DSurface9 *surface=nullptr,*memory=nullptr;check(SUCCEEDED(device->GetRenderTarget(0,&surface)),"surface");D3DSURFACE_DESC desc={};surface->GetDesc(&desc);check(SUCCEEDED(device->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&memory,nullptr)),"readback allocation");check(SUCCEEDED(device->GetRenderTargetData(surface,memory)),"readback");D3DLOCKED_RECT lock={};check(SUCCEEDED(memory->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"readback lock");D3DVIEWPORT9 view={};device->GetViewport(&view);check(view.Width==640&&view.Height==480,"actual viewport");std::vector<DWORD> image(640*480);
    for(unsigned y=0;y<480;++y)std::memcpy(image.data()+640*y,static_cast<const BYTE*>(lock.pBits)+(y+view.Y)*lock.Pitch+view.X*4,640*4);
    memory->UnlockRect();memory->Release();surface->Release();FILE* file=std::fopen(filename,"wb");check(file!=nullptr,"capture file");std::fwrite(image.data(),4,image.size(),file);std::fclose(file);return image;
}
static bool samePosition(CGUIObject& a,const POINT& p){return a.GetPosX()==p.x&&a.GetPosY()==p.y;}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"language");InitR3Engine();GetR3State()->mScreenXsize=640;GetR3State()->mScreenYsize=480;GetR3State()->mbFullScreen=FALSE;ForceFullScreen();check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"D3D init");g_pUiSpriteMgr=&(g_MainApp.*access(SpriteOwner{}));g_pUiScreen=&(g_MainApp.*access(ScreenOwner{}));check((g_MainApp.*access(Load{}))()!=0,"actual LoadData");
    LONG iconWidth=0,iconHeight=0;unsigned firstChanged=0,warmChanged=0;bool outOfRange=false;
    {
        CGUIMiniMapWindow window;auto& initial=window.NuclearMarker455(0);check(!initial.IsShow()&&!initial.GetAddedObjectNum()&&!initial.Label455().CellWidth455()&&!initial.Icon455().GetSizeX()&&initial.Scale455()[0]==0&&initial.Scale455()[1]==0,"actual constructor state");
        window.SetPos(30,20);window.Init();window.Show(TRUE);auto& map=window.*access(Map{});
        for(BYTE i=0;i<3;++i){auto& marker=window.NuclearMarker455(i);check(map.IsAddedObject(&marker)&&marker.IsShow()&&!marker.GetMouseInput455()&&marker.GetPosX()==map.GetPosX()&&marker.GetPosY()==map.GetPosY()&&marker.GetSizeX()==400&&marker.GetSizeY()==400,"actual3marker roots,position,size,inputflag0,registration");}
        try{window.NuclearMarker455(3);}catch(const std::out_of_range&){outOfRange=true;}check(outOfRange,"owned bound outside target unchecked-index domain");
        RECT bounds={-100,-200,300,600};window.SetMapBound(bounds);window.SetNuclearMapGeometry455(400,400,10,-20);
        for(BYTE i=0;i<3;++i)check(window.NuclearMarker455(i).Scale455()[0]==1&&window.NuclearMarker455(i).Scale455()[1]==0.5f,"ordinary bound and geometry fanout");
        const float point[]={60,999,180};window.SetNuclearMarker455(0,TRUE,point);auto& marker=window.NuclearMarker455(0);auto& icon=marker.Icon455();auto& label=marker.Label455();auto& background=marker.Background455();
        iconWidth=icon.GetSizeX();iconHeight=icon.GetSizeY();check(iconWidth>0&&iconHeight>0&&icon.GetSpriteInfo()->pSprite==gSpriteMgr.GetTargetSprite455(4)&&icon.GetSpriteInfo()->wActionNo==5&&icon.GetSpriteInfo()->wFrameNo==43,"real main5/43 autosize");
        check(marker.RelativePosition455()[0]==170&&marker.RelativePosition455()[1]==190&&icon.GetPosX()==map.GetPosX()+170&&icon.GetPosY()==map.GetPosY()+190,"first position precedes sprite autosize");
        check(background.GetSizeX()==0&&background.GetSizeY()==30&&label.CellWidth455()==7&&label.CellHeight455()==9&&label.GetSizeX()==35,"first background width uses unconfigured cell0;label then configures7x9");
        check(marker.GetAddedObjectNum()==3&&marker.GetAddedObject(0)==&icon&&marker.GetAddedObject(1)==&background&&marker.GetAddedObject(2)==&label,"icon/background/label draw order");check(background.GetARGB()==0x96000000&&(icon.GetARGB()>>24)==255,"real background tint and initial icon alpha");
        marker.SetMouseInput455(7);check(marker.GetMouseInput455()==7&&icon.GetMouseInput455()==7&&background.GetMouseInput455()==7&&label.GetMouseInput455()==7,"typed container input setter propagates rawBOOL to actual children");marker.SetMouseInput455(FALSE);check(!marker.GetMouseInput455()&&!icon.GetMouseInput455()&&!background.GetMouseInput455()&&!label.GetMouseInput455(),"container input0 propagates to existing simple children");
        auto first=capture(window,"nuclear-map-first.bgra");check((icon.GetARGB()>>24)==4,"ordinary Draw changes255to4 after rendering");
        window.SetNuclearMarker455(0,TRUE,point);const float x=170-static_cast<DWORD>(iconWidth)/2u,y=190-static_cast<DWORD>(iconHeight)/2u;
        check(marker.RelativePosition455()[0]==x&&marker.RelativePosition455()[1]==y&&background.GetSizeX()==63&&background.GetSizeY()==30&&marker.GetAddedObjectNum()==3,"repeat uses retained size/7x9 metrics,does not duplicate children");
        check(label.GetPosX()==LONG(double(map.GetPosX())+x+iconWidth+14)&&label.GetPosY()==LONG(double(map.GetPosY())+y-iconHeight+10),"label target offsets");
        auto warm=capture(window,"nuclear-map-warm.bgra");check((icon.GetARGB()>>24)==9&&warm!=first,"second visible draw uses alpha4 then becomes9");
        auto* device=GetD3dDevice();check(SUCCEEDED(device->BeginScene()),"pulse scene");BYTE alpha=9;
        for(unsigned i=0;i<49;++i){check(marker.Draw()!=0,"actual marker pulse Draw");alpha=static_cast<BYTE>(alpha+5);check(icon.GetARGB()>>24==alpha,"natural draw-count alpha pulse");}check(SUCCEEDED(device->EndScene())&&alpha==254,"natural near-opaque phase");
        auto mature=capture(window,"nuclear-map-mature.bgra");check((icon.GetARGB()>>24)==3&&mature!=warm,"mature visible pulse wraps after draw");
        const POINT oldIcon={icon.GetPosX(),icon.GetPosY()};window.SetNuclearMarker455(0,TRUE,nullptr);check(samePosition(icon,oldIcon)&&marker.GetAddedObjectNum()==3&&(icon.GetARGB()>>24)==3,"missing lookup result retains UI and alpha");
        marker.SetPos(marker.GetPosX()+7,marker.GetPosY()-11);check(icon.GetPosX()==oldIcon.x+7&&icon.GetPosY()==oldIcon.y-11,"inherited target SetPos moves current children");marker.SetPos(map.GetPosX(),map.GetPosY());
        RECT invalid={10,20,10,80};marker.SetMapBound455(invalid);check(marker.Scale455()[0]==1&&marker.Scale455()[1]==0.5f,"invalid bounds preserve prior scales");marker.SetMapBound455(bounds);
        window.SetNuclearMarker455(0,FALSE,nullptr);check(!marker.GetAddedObjectNum()&&icon.IsShow()&&label.IsShow(),"hide removes children without resetting show flags or coordinates");
        auto cleared=capture(window,"nuclear-map-cleared.bgra");check((icon.GetARGB()>>24)==8,"shown empty marker still advances icon alpha");auto clearAgain=capture(window,"nuclear-map-clear-again.bgra");check(clearAgain==cleared,"empty markers render no residual pixels");
        const float another[]={100,0,100};window.SetNuclearMarker455(1,TRUE,another);window.SetNuclearMarker455(2,TRUE,point);check(window.NuclearMarker455(1).GetAddedObjectNum()==3&&window.NuclearMarker455(2).GetAddedObjectNum()==3&&!marker.GetAddedObjectNum(),"all three independent real owners");capture(window,"nuclear-map-three-owners.bgra");
        check(SUCCEEDED(device->BeginScene()),"all-byte pulse scene");alpha=static_cast<BYTE>(icon.GetARGB()>>24);const DWORD rgb=icon.GetARGB()&0xffffff;
        for(unsigned i=0;i<256;++i){check(marker.Draw()!=0,"empty marker ordinary draw");alpha=static_cast<BYTE>(alpha+5);check(icon.GetARGB()==(rgb|(DWORD(alpha)<<24)),"all256 alpha states and RGB retention");}
        RECT clip={map.GetPosX(),map.GetPosY(),map.GetPosX()+400,map.GetPosY()+400};const DWORD before=icon.GetARGB();marker.Draw(clip);check(icon.GetARGB()==before,"inherited clipped Draw has no alpha writer");check(SUCCEEDED(device->EndScene()),"all-byte scene end");
        window.Show(FALSE);const DWORD hidden=icon.GetARGB();check(!marker.Draw()&&icon.GetARGB()==hidden,"hidden root refuses drawing before alpha mutation");
        for(std::size_t i=0;i<first.size();++i){firstChanged+=first[i]!=cleared[i];warmChanged+=warm[i]!=cleared[i];}check(firstChanged&&warmChanged,"real marker/font pixels");
    }
    (g_MainApp.*access(Unload{}))();R3ReleaseTextTexture();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();FILE* file=std::fopen("result.json","wb");check(file!=nullptr,"result");std::fprintf(file,"{\"status\":\"PASS\",\"checks\":%u,\"actual_MiniMap_three_owners\":true,\"actual_bound_fanout\":true,\"root_inputflag_and_child_propagation\":true,\"typed_geometry_and_position_API\":true,\"first_position_before_configure\":true,\"real_sprite4_main5_frame43\":true,\"real_imagefont7x9\":true,\"draw_alpha_states\":256,\"alpha_after_ordinary_not_clipped_Draw\":true,\"empty_draw_still_advances_alpha\":true,\"missing_record_retains_UI\":true,\"hide_preserves_child_state\":true,\"icon_size\":[%ld,%ld],\"GPU_frames\":6,\"first_changed_pixels\":%u,\"warm_changed_pixels\":%u,\"registry_race_lookup\":false,\"ordinary_geometry_world_producer\":false,\"normal_receiver\":false,\"full_minimap\":false,\"full_client\":false}\n",checks,iconWidth,iconHeight,firstChanged,warmChanged);std::fclose(file);return 0;
}
int main(){try{return run();}catch(const std::exception& error){std::fprintf(stderr,"Nuclear MiniMap:%s checks=%u\n",error.what(),checks);return 1;}}
