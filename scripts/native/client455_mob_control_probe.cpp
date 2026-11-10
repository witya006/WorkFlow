#define main RF455_UnusedIconProbeMain163
#include "client455_item_icon_probe.cpp"
#undef main
#include "client455_mob_control.h"
#include "userinterface/guicontroller/guiscreen.h"
#include <cmath>
extern CSpriteMgr* g_pUiSpriteMgr;
static void movements163(){
    CGUIObject object;object.SetPos(100,20);auto& moves=g_cMoveObjectMgr;
    moves.AddMoveObject(&object,MOVE_AXIS_X,100,200,200);moves.StartMoveAt455(&object,1000);moves.FrameMoveAt455(1100);check(object.GetPosX()==170&&object.GetPosY()==20,"target sine midpoint rounds the sin result to float");moves.FrameMoveAt455(1200);check(object.GetPosX()==200&&moves.IsFinishedMove(&object),"exact target endpoint");
    moves.AddMoveObject(&object,MOVE_AXIS_Y,200,100,200);moves.StartMoveAt455(&object,1000);moves.FrameMoveAt455(1100);check(object.GetPosY()==129,"reverse Y truncation");moves.FrameMoveAt455(1200);check(object.GetPosY()==100&&moves.IsFinishedMove(&object),"reverse endpoint");
    moves.AddMoveObject(&object,MOVE_AXIS_X,0,100,0);moves.StartMoveAt455(&object,1000);moves.FrameMoveAt455(1000);check(object.GetPosX()==100&&moves.IsFinishedMove(&object),"zero duration is immediate");
    moves.AddMoveObject(&object,MOVE_AXIS_X,0,100,100);moves.StartMoveAt455(&object,0);moves.FrameMoveAt455(2000);check(object.GetPosX()==0&&!moves.IsFinishedMove(&object),"zero start timestamp remains inactive");
    moves.StartMoveAt455(&object,0xfffffff0);moves.FrameMoveAt455(0x18);check(object.GetPosX()==58,"unsigned timestamp wrap");moves.FrameMoveAt455(0x54);check(object.GetPosX()==100&&moves.IsFinishedMove(&object),"wrap endpoint");
    moves.AddMoveObject(&object,MOVE_AXIS_X,100,200,100,1,10);moves.StartMoveAt455(&object,1000);moves.FrameMoveAt455(1100);check(object.GetPosX()==210&&!moves.IsFinishedMove(&object),"first wave overshoot");moves.FrameMoveAt455(1200);check(object.GetPosX()==200&&moves.IsFinishedMove(&object),"wave returns to final position");
    moves.AddMoveObject455(&object,MOVE_AXIS_X,0,100,100,0);moves.StartMoveAt455(&object,1000);moves.FrameMoveAt455(1500);check(object.GetPosX()==50,"constant velocity branch");moves.FrameMoveAt455(2000);check(object.GetPosX()==100&&moves.IsFinishedMove(&object),"constant velocity endpoint");
    moves.AddMoveObject455(&object,MOVE_AXIS_X,0,100,0,200);moves.StartMoveAt455(&object,1000);moves.FrameMoveAt455(1500);check(object.GetPosX()==25,"accelerated movement branch");moves.FrameMoveAt455(2000);check(object.GetPosX()==100&&moves.IsFinishedMove(&object),"acceleration endpoint");moves.RemoveObject(&object);check(moves.IsFinishedMove(&object),"removed record absent");
}
static int mob163(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"language");
    InitR3Engine();GetR3State()->mScreenXsize=640;GetR3State()->mScreenYsize=480;GetR3State()->mbFullScreen=FALSE;ForceFullScreen();check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"device");
    movements163();const auto baseline=GetDmallocSize();auto* previous=g_pUiSpriteMgr;g_pUiSpriteMgr=&gSpriteMgr;gSpriteMgr.LoadSprite(SP_ID_COMMON);
    auto* screen=CGUIScreen::GetSingletonPtr();check(screen!=nullptr,"ordinary UI screen owner");const HWND savedWindow=screen->GetHWND();HWND messageWindow=CreateWindowExA(0,"STATIC","OwnMobControl163",0,0,0,0,0,HWND_MESSAGE,nullptr,GetModuleHandleA(nullptr),nullptr);check(messageWindow!=nullptr,"own message-only window");screen->SetHWND(messageWindow);
    {
        CGUIMobControl window;window.SetID(77);window.SetPos(25,40);window.Init();window.Show(TRUE);auto draw=[&](){check(window.Draw()!=0,"actual window draw");};
        auto* root=window.GetSpriteInfo();check(root->pSprite==gSpriteMgr.GetTargetSprite455(13)&&root->wActionNo==1&&root->wFrameNo==0,"actual summon root");
        check(window.GetAddedObjectNum()==16&&window.CommandContent455().GetAddedObjectNum()==3&&window.CommandViewport455().GetAddedObjectNum()==1,"actual sixteen children and three commands");
        check(window.GetARGB()==0xd8ffffff&&window.HP455().GetPosX()==51&&window.HP455().GetPosY()==57&&window.FP455().GetPosY()==71,"root alpha and HP/FP layout");
        check(window.HP455().GetSpriteInfo()->pSprite==gSpriteMgr.GetTargetSprite455(4)&&window.HP455().GetSizeX()==0&&window.FP455().GetSizeX()==0,"real main bars zero maximum");
        check(window.Level455().GetSizeX()==7&&window.Level455().GetPosX()==37&&window.Level455().GetPosY()==89,"single digit level centered");capture(draw,"mob-initial.bgra");
        char name[]="PREFIX Animus";window.SetMobName(name);check(std::strcmp(window.Name455().GetString(),"Animus")==0,"actual Korean seven-byte prefix policy");
        auto* nation=RF455_GetNormalNationPaths();const auto savedNation=nation->nation;nation->nation=8;window.SetMobName(name);check(std::strcmp(window.Name455().GetString(),name)==0,"non-Korean name policy");nation->nation=savedNation;window.SetMobName(name);
        window.SetLevel(255);check(window.Level455().GetSizeX()==21&&window.Level455().GetPosX()==30,"BYTE level255 centered");window.SetHP(-1,-1);check(window.HP455().GetSizeX()==0&&window.HPText455().GetSizeX()==70,"negative signed HP and max clamp to zero");
        window.SetHP(0x7fffffff,1);check(window.HP455().GetSizeX()==130&&window.HPText455().GetSizeX()==98,"signed maximum and upper ratio clamp");window.SetHP(100000,200000);window.SetFP(50,100);check(window.HP455().GetSizeX()==65&&window.HPText455().GetSizeX()==105&&window.FP455().GetSizeX()==65,"actual signed full-width HP/FP fields");
        window.SetExp(1);check(window.Exp455().GetSizeX()==89&&window.ExpRemainder455().GetSizeX()==89&&window.ExpText455().GetSizeX()==42,"target full EXP steps and float-loop remainder");window.SetExp(0.5f);
        window.SetResource455(0,0);check(!window.Resource455().IsShow()&&window.ResourceIcon455().GetSpriteInfo()->wFrameNo==3,"zero resource changes icon and hides gauge");window.SetResource455(100,100);check(std::strcmp(window.ResourceText455().GetString(),"99% / 100")==0,"resource percentage display caps before integer formatting");
        window.SetResource455(0x7fffffff,0x7fffffff);check(std::strcmp(window.ResourceText455().GetString(),"0% / 2147483647")==0,"target multiply wraps before signed division");window.SetResource455(50,100);check(window.Resource455().IsShow()&&std::strcmp(window.ResourceText455().GetString(),"50% / 50")==0&&window.ResourceIcon455().GetSpriteInfo()->wFrameNo==4,"nonzero resource uses correct icon and producer fields");capture(draw,"mob-values.bgra");
        auto& content=window.CommandContent455();auto& view=window.CommandViewport455();const LONG edge=window.GetPosX()+window.GetSizeX();check(!window.IsCrossed(edge+1,window.GetPosY()+20),"closed panel hit bounds");
        _mouse_event event={};event.source=&window.CommandIcon455();event.id=MOUSE_HOVERED;window.MouseEvent(event);check(window.CommandsOpen455()&&view.IsShow()&&view.GetSizeX()==content.GetSizeX(),"actual hover opens clipped commands");
        g_cMoveObjectMgr.StartMoveAt455(&content,1000);g_cMoveObjectMgr.FrameMoveAt455(1200);check(content.GetPosX()==view.GetPosX()&&window.IsCrossed(edge+1,view.GetPosY()+1),"expanded animation endpoint and hit bounds");capture(draw,"mob-commands.bgra");
        for(unsigned i=0;i<3;++i){event.source=&window.Command455(i);event.id=MOUSE_CLICKED;window.MouseEvent(event);MSG message={};check(PeekMessageA(&message,messageWindow,WM_ANIMUSCONTROL_BOARD_COMMAND,WM_ANIMUSCONTROL_BOARD_COMMAND,PM_REMOVE)&&message.message==0x530&&message.wParam==77&&message.lParam==i,"actual command HWND/message/board ID/index route");if(i<2){event.source=&window.CommandIcon455();event.id=MOUSE_HOVERED;window.MouseEvent(event);}}
        g_cMoveObjectMgr.StartMoveAt455(&content,1000);g_cMoveObjectMgr.FrameMoveAt455(1150);window.Update();check(!window.CommandsOpen455()&&!view.IsShow()&&view.GetSizeX()==0&&view.GetSizeY()==0,"close animation completion collapses and hides viewport");
        window.SetSprite();window.SetHP(0,0);window.SetFP(0,0);window.SetLevel(1);window.SetExp(-1);window.SetResource455(0,0);check(window.Exp455().GetSizeX()==0&&window.ExpRemainder455().GetSizeX()==0,"negative EXP clamps and zero crop");capture(draw,"mob-reset.bgra");
    }
    screen->SetHWND(savedWindow);DestroyWindow(messageWindow);g_cMoveObjectMgr.RemoveAllObject();GetD3dDevice()->SetTexture(0,nullptr);gSpriteMgr.UnloadSpriteAll();g_pUiSpriteMgr=previous;check(GetDmallocSize()==baseline,"sprite allocator balanced");R3ReleaseTextTexture();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();
    FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"report");std::fputs("{\"status\":\"PASS\",\"ordinary_window_methods\":true,\"children\":16,\"commands\":3,\"actual_message_routes\":3,\"GPU_frames\":4,\"controlled_values\":true,\"shared_movement\":true,\"full_Animus_producers_accepted\":false,\"full_client\":false}\n",out);std::fclose(out);return 0;
}
int main(){try{return mob163();}catch(const std::exception& e){std::fprintf(stderr,"MobControl163:%s\n",e.what());return 1;}}
