//Only reuse GPU readback;the old icon bulk entry is never executed.
#define main RF455_UnusedIconProbeMain160
#include "client455_item_icon_probe.cpp"
#undef main
#include "client455_gui_tab_board.h"
#include "client455_modal.h"
extern CSpriteMgr* g_pUiSpriteMgr;
static int tab160(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"language");
    InitR3Engine();GetR3State()->mScreenXsize=640;GetR3State()->mScreenYsize=480;GetR3State()->mbFullScreen=FALSE;ForceFullScreen();
    check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"device");
    const auto baseline=GetDmallocSize();auto* previous=g_pUiSpriteMgr;g_pUiSpriteMgr=&gSpriteMgr;
    gSpriteMgr.LoadSprite(SP_ID_COMMON);
    {
        CGUITabBoard455 tabs;tabs.SetPos(20,40);tabs.Show(TRUE);tabs.Init455(5,207,18,219,74);
        RF455_ConfigureModalScrollbar(tabs.Scrollbar455());tabs.SetHeaderSprites455({1,5,0},{1,5,1});tabs.SetSize(219,74);
        check(tabs.Count455()==5&&!tabs.Content455(5)&&!tabs.Group455(255),"BYTE sections and bounds");
        CGUIText rows[4];for(unsigned i=0;i<4;++i){rows[i].SetString(const_cast<char*>(RF455_GetNormalLanguagePack()->get(0x443+i)));rows[i].SetPos(4,4+18*i);tabs.Content455(0)->Add(&rows[i]);}
        for(BYTE i=0;i<5;++i){tabs.SetTitle455(i,RF455_GetNormalLanguagePack()->get(0x43f+i),DWORD(-2434860));check(tabs.Header455(i)->GetSizeX()==207&&tabs.Header455(i)->GetSizeY()==18,"actual common header dimensions");}
        tabs.Content455(0)->SetSize(207,96);tabs.Content455(1)->SetSize(207,64);
        tabs.SetOpened455(0,TRUE);tabs.SetOpened455(1,TRUE);
        check(tabs.IsOpened455(0)&&tabs.IsOpened455(1)&&!tabs.IsOpened455(2),"membership is expansion state");
        check(tabs.Header455(0)->GetSpriteInfo()->wFrameNo==1&&tabs.Header455(2)->GetSpriteInfo()->wFrameNo==0,"two real target states");
        check(tabs.Group455(1)->GetPosY()==154&&tabs.Group455(2)->GetPosY()==236&&tabs.Scrollbar455().GetTotalAmount()==176,"actual reflow geometry");
        check(tabs.Group455(0)->GetAddedObjectNum()==3&&tabs.Content455(0)->GetAddedObjectNum()==4,"borrowed real GUI children retained");
        auto draw=[&](){check(tabs.Draw()!=0,"actual clipped tab draw");};capture(draw,"tabs-expanded.bgra");
        tabs.Scrollbar455().SetCurrentAmount(50);_scroll_event event={&tabs.Scrollbar455(),SCROLLED_DOWN};tabs.ScrollEvent(event);
        check(tabs.Group455(0)->GetPosY()==-10&&tabs.Content455(0)->GetPosY()==8,"actual scroll observer moves group tree");
        capture(draw,"tabs-scrolled.bgra");
        tabs.SetSize(219,240);check(tabs.Scrollbar455().GetCurrentAmount()==10&&tabs.Group455(0)->GetPosY()==30,"resize clamps existing scroll amount");
        _mouse_event click={tabs.Header455(0),MOUSE_STROKED,0,0};tabs.MouseEvent(click);
        check(!tabs.IsOpened455(0)&&tabs.Group455(1)->GetPosY()==58&&tabs.Scrollbar455().GetTotalAmount()==0,"collapse reflows and resets exhausted scroll");
        click.id=MOUSE_PRESSED;tabs.MouseEvent(click);check(!tabs.IsOpened455(0),"only stroke toggles");
        click.id=MOUSE_STROKED;tabs.MouseEvent(click);check(tabs.IsOpened455(0),"stroke reopens retained content");
        tabs.SetOpened455(0,FALSE);tabs.SetOpened455(1,FALSE);check(tabs.Scrollbar455().GetThumb455().GetSizeY()>18,"zero total retains previous thumb extent");capture(draw,"tabs-collapsed.bgra");
        gSpriteMgr.UnloadSpriteAll();gSpriteMgr.LoadSprite(SP_ID_COMMON);RF455_ConfigureModalScrollbar(tabs.Scrollbar455());tabs.SetHeaderSprites455({1,5,0},{1,5,1});tabs.SetSize(219,240);
        check(tabs.Scrollbar455().GetThumb455().GetSizeY()==18,"target style0 configuration resets thumb extent");
        capture(draw,"tabs-reloaded.bgra");check(tabs.Content455(0)->GetAddedObjectNum()==4,"skin reload keeps borrowed objects");
        tabs.Clear455();check(!tabs.Count455()&&!tabs.Content455(0),"owned section clear");
        bool refused=false;try{tabs.Reflow455();}catch(const std::domain_error&){refused=true;}check(refused,"empty target dereference domain not accepted");
    }
    GetD3dDevice()->SetTexture(0,nullptr);gSpriteMgr.UnloadSpriteAll();g_pUiSpriteMgr=previous;check(GetDmallocSize()==baseline,"sprite allocator balance");
    R3ReleaseTextTexture();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();FILE* file=std::fopen("result.json","wb");check(file!=nullptr,"report");
    std::fputs("{\"status\":\"PASS\",\"actual_target_header_sprites\":true,\"sections\":5,\"borrowed_text_children\":4,\"real_scroll_observer\":true,\"stroke_toggle\":true,\"resize_clamp\":true,\"skin_reacquisition\":true,\"allocator_balanced\":true,\"GPU_frames\":4,\"ordinary_CharInfo_connected\":false,\"full_client\":false}\n",file);std::fclose(file);return 0;
}
int main(){try{return tab160();}catch(const std::exception& e){std::fprintf(stderr,"Tab160: %s\n",e.what());return 1;}}
