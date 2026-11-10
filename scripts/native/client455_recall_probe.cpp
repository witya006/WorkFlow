#define main RF455_UnusedIconProbeMain162
#include "client455_item_icon_probe.cpp"
#undef main
#include "client455_recall_window.h"
#include "client455_modal.h"
#include <cmath>
extern CSpriteMgr* g_pUiSpriteMgr;
static int recall162(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"language");
    InitR3Engine();GetR3State()->mScreenXsize=640;GetR3State()->mScreenYsize=480;GetR3State()->mbFullScreen=FALSE;ForceFullScreen();check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"device");
    const auto baseline=GetDmallocSize();auto* previous=g_pUiSpriteMgr;g_pUiSpriteMgr=&gSpriteMgr;gSpriteMgr.LoadSprite(SP_ID_COMMON);
    {
        CGUIRecallWindow window;window.SetPos(20,30);window.Init();window.Show(TRUE);
        auto draw=[&](){check(window.Draw()!=0,"actual window draw");};
        check(window.GetSizeX()==228&&window.GetSizeY()==395&&window.GetAddedObjectNum()==8&&window.Viewport455().GetAddedObjectNum()==1,"actual root and clipped content owners");
        auto& header=window.Header455();auto* image=header.GetSpriteInfo()->pSprite;check(header.GetSizeY()==image->GetSpriteOrgYL(4,0)&&header.GetTotal455()==1,"natural full-height static header");
        check(window.Title455().GetPosY()==header.GetPosY()+(header.GetSizeY()-window.Title455().GetSizeY())/2,"actual centered title");
        check(window.Viewport455().GetPosX()==26&&window.Viewport455().GetPosY()==header.GetPosY()+header.GetSizeY()+12&&window.Viewport455().GetSizeX()==208,"actual viewport geometry");
        check(window.GetWheelScrollObject()==&window.Scrollbar455()&&window.Scrollbar455().GetAdjustmentUnit()==56,"real wheel/row unit");capture(draw,"recall-empty.bgra");
        for(unsigned i=0;i<8;++i){char name[32];std::snprintf(name,sizeof(name),"Summon %u",i+1);_recall_info info={};info.pName=name;info.dwIndex=100+i;info.dwItemID=0x1200+i;info.dwSpriteID=1+i;info.byLevel=BYTE(10+i);info.nCurHP=100000;info.nMaxHP=200000;info.nCurFP=50000;info.nMaxFP=100000;info.fExp=12.5f*float(i);check(window.TakeInItem(&info),"actual typed row insertion");check(!window.TakeInItem(&info),"duplicate index refused");}
        check(window.Count455()==8&&window.Content455().GetAddedObjectNum()==8&&window.Content455().GetSizeY()==448,"eight owned rows");
        auto* first=window.GetRecallUnitByIndex(100);check(first&&first==window.GetRecallUnitByItemID(0x1200)&&first==window.GetRecallUnitByEventObj(first->GetCover()),"actual index/item/cover lookup");
        check(first->GetSizeX()==204&&first->GetSizeY()==56&&first->GetAddedObjectNum()==13&&first->GetItem()->GetSizeX()==38,"455 row geometry/composition");
        check(first->GetItem()->GetIconType()==4&&(first->GetItem()->GetSpriteInfo()->wActionNo>>8)==24,"actual recall icon atlas classification");
        check(first->HPText455().GetSizeX()==17*7&&first->FPText455().GetSizeX()==17*7,"full32bit padded current/max text extent");
        auto* summon=gSpriteMgr.GetTargetSprite455(13);const LONG hpWidth=summon->GetSpriteOrgXL(0,1),fpWidth=summon->GetSpriteOrgXL(0,2),expWidth=summon->GetSpriteOrgXL(0,3);
        std::fprintf(stderr,"455summon natural widths:HP=%ld FP=%ld EXP=%ld\n",hpWidth,fpWidth,expWidth);
        check(first->HP455().GetSizeX()==hpWidth/2&&first->FP455().GetSizeX()==fpWidth/2,"half-width gauges from actual455 sprite descriptors");
        window.SetLevel(100,255);check(std::strcmp(first->Level455().GetString(),"Lv 255")==0,"BYTE level");window.SetHP(100,0,0);check(first->HP455().GetSizeX()==0&&first->HPText455().GetSizeX()==12*7,"zero max is empty bar with real signed numbers");
        window.SetHP(100,-1,1);check(first->HP455().GetSizeX()==hpWidth,"DWORD ratio upper clamp");window.SetHP(100,100000,200000);
        window.SetFP(0x1200,50000,100000,FALSE);check(first->FP455().GetSizeX()==fpWidth/2,"by-item update route");
        auto* other=window.GetRecallUnitByIndex(101);first->GetItem()->SetRefItem(other->GetItem());window.SetItemState(100,CGUIRecallUnit::Linked);check(first->GetItem()->GetRefItem()==other->GetItem()&&first->GetCover()->GetARGB()==0xffffffff,"linked keeps borrowed reference");window.SetItemState(100,CGUIRecallUnit::Disabled);check(!first->GetItem()->GetRefItem()&&first->GetCover()->GetARGB()==0x80a05050,"disabled clears reference andtints cover");
        window.SetItemState(101,CGUIRecallUnit::NoneUnit);window.SetItemState(102,CGUIRecallUnit::Enabled);capture(draw,"recall-populated.bgra");
        const LONG total=448-window.Viewport455().GetSizeY();check(window.Scrollbar455().GetTotalAmount()==total&&total>0,"actual content overflow");window.Scrollbar455().SetCurrentAmount(100);_scroll_event scroll={&window.Scrollbar455(),SCROLLED_DOWN};window.ScrollEvent(scroll);check(window.Content455().GetPosY()==window.Viewport455().GetPosY()-100,"real scroll observer");capture(draw,"recall-scrolled.bgra");
        window.Scrollbar455().SetCurrentAmount(0);window.ScrollEvent(scroll);window.SetItemState(100,CGUIRecallUnit::Enabled);window.SetExp(100,200);check(first->Exp455().GetSizeX()==expWidth*2&&first->ExpText455().GetSizeX()==6*7,"EXP visual ratio uncapped while text caps99.99");
        window.SetExp(100,50);auto* sprite=first->Exp455().GetSpriteInfo()->pSprite;sprite->SetAction(0);sprite->SetFrame(3);const float expected=float(sprite->GetSpriteOrgXL())/sprite->GetSpriteXL()*0.5f;check(std::fabs(first->GetExpRate()-expected)<0.000001f,"legacy GetExpRate returns texture U,not normalized percent");capture(draw,"recall-values.bgra");
        RECT bounds;window.GetBound(bounds);RECT shortBounds=bounds;shortBounds.bottom=shortBounds.top+header.GetSizeY()+window.Resize455().GetSizeY()+136;window.SetBound(shortBounds);check(window.GetSizeY()==395,"minimum bound rejection");RECT larger=bounds;larger.bottom+=50;window.SetBound(larger);check(window.Viewport455().GetSizeY()==window.Resize455().GetPosY()-window.GetPosY()-header.GetSizeY()-12,"actual resized viewport rule");window.SetBound(bounds);
        check(window.TakeOutItem(100)&&!window.GetRecallUnitByIndex(100)&&window.Count455()==7,"owned row removal");check(window.GetRecallUnitByIndex(101)->GetPosY()==window.Content455().GetPosY(),"remaining rows compact");check(window.Content455().GetSizeY()==448,"target deletion keeps stale content height");for(unsigned i=101;i<108;++i)check(window.TakeOutItem(i),"remaining row removal");check(!window.Count455()&&window.Content455().GetSizeY()==448&&window.Scrollbar455().GetTotalAmount()==448-window.Viewport455().GetSizeY(),"empty list preserves target stale height");check(!window.TakeOutItem(999),"absent index ignored");capture(draw,"recall-removed.bgra");
    }
    GetD3dDevice()->SetTexture(0,nullptr);gSpriteMgr.UnloadSpriteAll();g_pUiSpriteMgr=previous;check(GetDmallocSize()==baseline,"sprite allocator balanced");R3ReleaseTextTexture();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"report");std::fputs("{\"status\":\"PASS\",\"ordinary_window_methods\":true,\"rows\":8,\"full_width_HP_FP\":true,\"target_stale_height_retained\":true,\"GPU_frames\":5,\"controlled_row_records\":true,\"full_Animus_producers_accepted\":false,\"full_client\":false}\n",out);std::fclose(out);return 0;
}
int main(){try{return recall162();}catch(const std::exception& e){std::fprintf(stderr,"Recall162:%s\n",e.what());return 1;}}
