// Reuse only GPU readback;the unrelated bulk icon entry is not executed.
#define main RF455_UnusedIconProbeMain161
#include "client455_item_icon_probe.cpp"
#undef main
#include "client455_char_info.h"
#include "userinterface/gamewindow/guicharinfowindow.h"
#include "userinterface/uiglobal.h"
#include "client455_text_metrics.h"
extern CSpriteMgr* g_pUiSpriteMgr;
static float CI161FrameSeconds(){return 0;}
static int charinfo161(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"language");
    InitR3Engine();GetR3State()->mScreenXsize=640;GetR3State()->mScreenYsize=480;GetR3State()->mbFullScreen=FALSE;ForceFullScreen();
    check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"device");
    const auto baseline=GetDmallocSize();auto* previous=g_pUiSpriteMgr;g_pUiSpriteMgr=&gSpriteMgr;gSpriteMgr.LoadSprite(SP_ID_COMMON);
    const auto replay=RF455_SetGuiAnimationReplay({nullptr,CI161FrameSeconds});
    for(BYTE race:{BYTE(0),BYTE(2),BYTE(4)}){
        _SetUIAvatarRace(race);CGUICharInfoWindow window;window.SetPos(20,30);window.Init();window.Show(TRUE);auto& view=window.View455();
        check(window.GetSizeX()==228&&window.GetSizeY()==395&&window.GetAddedObjectNum()==11,"actual ordinary outer window dimensions/child order");
        auto* headerSprite=view.header.GetSpriteInfo()->pSprite;
        check(view.header.GetSizeX()==headerSprite->GetSpriteOrgXL(4,0)&&view.header.GetSizeY()==headerSprite->GetSpriteOrgYL(4,0)&&view.header.GetTotal455()==1,"target header retains full natural image;only highlight has1x4 sheet");
        check(view.highlight.GetTotal455()==4&&view.header.GetPosY()==window.GetPosY()+6&&view.tabs[0].GetPosY()==view.header.GetPosY()+view.header.GetSizeY()+8,"target header/tab vertical geometry");
        check(window.m_uiTitle.GetPosY()==view.header.GetPosY()+(view.header.GetSizeY()-window.m_uiTitle.GetSizeY())/2,"title centered in actual natural header");
        check(view.main.Count455()==5&&view.actions.Count455()==2&&view.equipment.Count455()==4,"actual three page counts");
        check(view.main.Content455(0)->GetAddedObjectNum()==18&&view.main.Content455(1)->GetAddedObjectNum()==28,"all23borrowed text owners");
        check(view.main.Content455(2)->GetAddedObjectNum()==(race==4?44:49)&&view.main.Content455(3)->GetAddedObjectNum()==16&&view.main.Content455(4)->GetAddedObjectNum()==14,"actual race-sensitive mastery/resist/extra composition");
        check(view.main.IsOpened455(0)&&view.main.IsOpened455(1)&&!view.main.IsOpened455(2)&&view.actions.IsOpened455(0)&&view.actions.IsOpened455(1)&&view.equipment.IsOpened455(0),"exact initial expansion defaults");
        check(window.GetWheelScrollObject()==&view.main.Scrollbar455()&&view.selected==0,"ordinary wheel target");
        window.m_uiCloseButton.SoundOn(FALSE);window.m_uiHelpButton.SoundOn(FALSE);window.m_uiCloseButton.SetState(DISABLED);window.m_uiHelpButton.SetState(DISABLED);
        check(window.m_uiCloseButton.GetSpriteInfo()->pSprite&&window.m_uiCloseButton.GetSpriteInfo()->wFrameNo==0&&window.m_uiHelpButton.GetSpriteInfo()->pSprite&&window.m_uiHelpButton.GetSpriteInfo()->wFrameNo==3,"base button descriptor also initializes disabled state");window.m_uiCloseButton.SetState(0);window.m_uiHelpButton.SetState(0);
        for(unsigned i=0;i<23;++i)check(view.main.Content455(i<9?0:1)->IsAddedObject(window.GetInfoValue455(BYTE(i))),"actual455 value widget identity");
        check(std::strcmp(window.GetInfoValue455(1)->GetString(),RF455_GetNormalLanguagePack()->get(6+race/2))==0,"actual NDLanguage race");
        window.SetCharName("Client455");window.SetGuildName("RF");window.SetLevel(55);window.SetHP(1234,5678);window.SetFP(0,0);window.SetSP(0,0);window.SetExp(12.5f);window.SetGenAttackFc(100,250);window.SetForceAttackFc(10,40);window.SetDeffenceFc(111);
        check(std::strcmp(window.GetInfoValue455(0)->GetString(),"Client455")==0&&std::strcmp(window.GetInfoValue455(8)->GetString(),"RF")==0,"legacy name/guild producers address455 owners");
        check(std::strcmp(window.GetInfoValue455(10)->GetString(),"-")==0&&std::strcmp(window.GetInfoValue455(11)->GetString(),"-")==0&&std::strcmp(window.GetInfoValue455(13)->GetString(),"12.500000%") ==0,"actual zero-max and six-decimal writers");
        window.Update();auto draw=[&](){check(window.Draw()!=0,"ordinary CharInfo draw");};if(race==0)capture(draw,"char-info-main.bgra");
        RECT before;window.GetBound(before);RECT shortBounds=before;shortBounds.bottom=shortBounds.top+view.header.GetSizeY()+window.m_uiResizeUnderBar.GetSizeY()+136;window.SetBound(shortBounds);check(window.GetSizeY()==395,"minimum resize rejects request");
        RECT tall=before;tall.bottom+=20;window.SetBound(tall);check(view.main.GetSizeY()==view.actions.GetSizeY()&&view.actions.GetSizeY()==view.equipment.GetSizeY(),"all page viewport bounds resized");window.SetBound(before);
        for(BYTE index:{BYTE(1),BYTE(2),BYTE(0)}){_mouse_event stroke={&view.tabs[index],MOUSE_STROKED,0,0};window.MouseEvent(stroke);check(view.selected==index&&window.GetAddedObjectNum()==11&&window.GetWheelScrollObject()==&view.Page455(index)->Scrollbar455(),"real page input and wheel handoff");check(window.IsAddedObject(view.Page455(index)),"selected real page membership");for(BYTE other=0;other<3;++other)if(other!=index)check(!window.IsAddedObject(view.Page455(other)),"other page removed");if(race==0&&index==1)capture(draw,"char-info-actions.bgra");if(race==0&&index==2)capture(draw,"char-info-equipment.bgra");}
        view.SelectPage455(255);check(view.selected==0,"invalid page ignored");view.SelectPage455(0);check(window.GetAddedObjectNum()==11,"already selected has no duplicate children");
        window.SetTab(0,FALSE);window.SetTab(1,FALSE);window.SetTab(2,TRUE);
        window.SetBattleMastery455(0,99,99);check(std::strcmp(window.m_uiBattlePoint[0].GetString(),"G M")==0,"battle GM equality rule");
        window.SetBattleMastery455(0,99,100);check(std::strcmp(window.m_uiBattlePoint[0].GetString(),"99/100 Pt")==0,"battle maximum remains WORD");
        window.SetMakeMastery455(0,99,100);check(std::strcmp(window.m_uiMakePoint[0].GetString(),"G M")==0,"make GM has different maximum rule");
        window.SetMakeMastery455(0,99,99);check(std::strcmp(window.m_uiMakePoint[0].GetString(),"99/99 Pt")==0,"make max99 keeps fraction");
        for(BYTE i=0;i<6;++i){window.SetBattleMastery455(i,WORD(10+i),99);window.SetBattleMasteryExp(i,0.25f);}
        for(BYTE i=0;i<3;++i){window.SetMakeMastery455(i,WORD(5+i),99);window.SetMakeMasteryExp(i,0.5f);}
        window.SetBattleMasteryExp(0,-1);check(view.battle[0].bar.GetSizeX()==0,"negative exp clamps0");window.SetBattleMasteryExp(0,2);check(view.battle[0].bar.GetSizeX()==view.battle[0].bar.GetSpriteInfo()->pSprite->GetSpriteOrgXL(1,2),"exp clamps1 and restores original bar width");
        if(race==0)capture(draw,"char-info-mastery-race0.bgra");if(race==4)capture(draw,"char-info-mastery-race4.bgra");
        window.SetTab(2,FALSE);window.SetTab(3,TRUE);window.SetResistPoint455(0,-30,-100,100);window.SetResistPoint455(1,30,-100,100);window.SetResistPoint455(2,0,-100,100);window.SetResistPoint455(3,300,-100,100);
        check(std::strcmp(window.m_uiResistPoint[0].GetString(),"-30")==0&&std::strcmp(window.m_uiResistPoint[1].GetString(),"+30")==0,"signed resist text");check(view.resistBar[0].GetPosX()+view.resistBar[0].GetSizeX()==view.resistBack[0].GetPosX()+100&&view.resistBar[1].GetPosX()==view.resistBack[1].GetPosX()+100,"signed resist bars meet center");
        if(race==0)capture(draw,"char-info-resist.bgra");
    }
    RF455_SetGuiAnimationReplay(replay);GetD3dDevice()->SetTexture(0,nullptr);gSpriteMgr.UnloadSpriteAll();g_pUiSpriteMgr=previous;check(GetDmallocSize()==baseline,"sprite allocator balanced");
    R3ReleaseTextTexture();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();FILE* file=std::fopen("result.json","wb");check(file!=nullptr,"report");std::fputs("{\"status\":\"PASS\",\"ordinary_window_methods\":true,\"races\":3,\"pages\":3,\"value_owners\":23,\"GPU_frames\":6,\"full_client\":false,\"dynamic_action_equipment_producers_accepted\":false}\n",file);std::fclose(file);return 0;
}
int main(){try{return charinfo161();}catch(const std::exception& e){std::fprintf(stderr,"CharInfo161: %s\n",e.what());return 1;}}
