#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "item/citemdata.h"
#include "input/imeedit.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "userinterface/gamewindow/guicharinfowindow.h"
#include "mainapp.h"
#include <cstdio>
#include <cstring>
#include <memory>
#include <stdexcept>

static void require(bool value,const char* text){if(!value)throw std::runtime_error(text);}
struct AvatarAccess final:CAvatar {using CAvatar::UI_RefreshCharInfoWindow_WhenDismountUnit;};
static void text(CGUICharInfoWindow& window,BYTE slot,const char* expected){
    auto* widget=window.GetInfoValue455(slot);require(widget&&widget->GetString()&&!std::strcmp(widget->GetString(),expected),"Actual455statwidget text differs");
}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);InitR3Engine();
    std::unique_ptr<CGUICharInfoWindow> window(new CGUICharInfoWindow);auto& ui=*window;
    ui.m_uiCharInfo[CGUICharInfoWindow::Level].SetString("level-sentinel");ui.m_uiCharInfo[CGUICharInfoWindow::Guild].SetString("guild-sentinel");
    ui.SetInfoText455(4,"class-sentinel");
    require(&ui.ValueForLegacySlot455(CGUICharInfoWindow::GenAttPower)==ui.GetInfoValue455(14)&&
        &ui.ValueForLegacySlot455(CGUICharInfoWindow::FcAttPower)==ui.GetInfoValue455(15)&&
        &ui.ValueForLegacySlot455(CGUICharInfoWindow::Deffense)==ui.GetInfoValue455(16),"Ordinary basicrows useactual455owners");
    ui.SetGenAttackFc(70000,90000);text(ui,14,"70000 - 90000");
    ui.SetGenAttackFc(0xffffffff,0x80000000);text(ui,14,"-1 - -2147483648");
    ui.SetForceAttackFc(250000,300000);text(ui,15,"250000 - 300000");
    ui.SetForceAttackFc(0xffffffff,1);text(ui,15,"-1 - 1");
    ui.SetDeffenceFc(80000);text(ui,16,"80000");ui.SetDeffenceFc(0x80000000);text(ui,16,"-2147483648");
    ui.SetHitRate(1.25f);text(ui,17,"1.25");ui.SetHitRate(-2.5f);text(ui,17,"-2.50");ui.SetHitRate(0);text(ui,17,"0.00");
    ui.SetAvoidRate(3.9f);text(ui,18,"3");ui.SetAvoidRate(-3.9f);text(ui,18,"-3");ui.SetAvoidRate(-.9f);text(ui,18,"0");
    ui.SetAvoidRate(70000.f);text(ui,18,"70000");
    require(!std::strcmp(ui.m_uiCharInfo[CGUICharInfoWindow::Level].GetString(),"level-sentinel")&&
        !std::strcmp(ui.m_uiCharInfo[CGUICharInfoWindow::Guild].GetString(),"guild-sentinel"),"LegacyLevel/Guild notaliasedto455fields");text(ui,4,"class-sentinel");
    ui.Init();
    constexpr unsigned stateTab=1; //Private ordinarywindow TAB_STATE definition.
    require(ui.m_uiInfoBoard[stateTab].IsAddedObject(ui.GetInfoValue455(14))&&
        ui.m_uiInfoBoard[stateTab].IsAddedObject(ui.GetInfoValue455(15))&&
        ui.m_uiInfoBoard[stateTab].IsAddedObject(ui.GetInfoValue455(16)),"Actual ordinarywindow childregistration usesnewvaluewidgets");
    std::unique_ptr<AvatarAccess> avatar(new AvatarAccess);auto* previous=g_pUiCharInfoWindow;
    struct Restore{CGUICharInfoWindow* previous;~Restore(){g_pUiCharInfoWindow=previous;}}restore{previous};g_pUiCharInfoWindow=&ui;
    auto* condition=avatar->GetConditionInfo();condition->m_dwTotalStrikingPower[0]=70000;condition->m_dwTotalStrikingPower[1]=90000;
    condition->m_dwTotalForcePower[0]=250000;condition->m_dwTotalForcePower[1]=300000;condition->m_dwTotalDefencePower=80000;
    condition->m_fTotalHitProb=1.25f;condition->m_fAvoidProb[0]=3.9f;
    avatar->UI_RefreshCharInfoWindow_WhenDismountUnit(FALSE);
    text(ui,14,"70000 - 90000");text(ui,15,"250000 - 300000");text(ui,16,"80000");text(ui,17,"1.25");text(ui,18,"3");
    //The caller above is the real current Avatar path,not proof that its
    //legacy metric producers already implement all455getter/mount/buff rules.
    FILE* out=std::fopen("result.json","wb");require(out,"Output");
    std::fputs("{\"status\":\"PASS\",\"actual_window_value_owners\":5,\"full_DWORD_values_preserved\":true,\"float_setters_not_empty\":true,\"actual_basicrow_child_registration\":3,\"legacy_labels_preserved\":true,\"actual_current_Avatar_caller\":true,\"full455_Avatar_metric_producers\":false,\"full455_Avatar_refresh\":false,\"full455_window_layout\":false,\"full_client\":false}\n",out);
    std::fclose(out);return 0;
}
int main(){try{return run();}catch(const std::exception& e){std::fprintf(stderr,"CharInfo values:%s\n",e.what());return 2;}}
