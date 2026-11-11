//Reuse the GPU readback helper only; the old bulk entry is never executed.
#define main RF455_UnusedIconProbeMain159
#include "client455_item_icon_probe.cpp"
#undef main
#include "userinterface/gamewindow/guigaugeexpwindow.h"
#include "userinterface/gamewindow/guicharinfowindow.h"
#include "gameobject/manager/ccharactermgr.h"
#include "network/netmsgprocessor/combat/cnetmsgprocessor_combat.h"
#include "network/netmsgprocessor/event/cnetmsgprocessor_event.h"
#include <array>
extern CGUICharInfoWindow* g_pUiCharInfoWindow;

static void checkAvatarHealth(CGUIGaugeExpWindow& panel, CGUICharInfoWindow& info)
{
    ChInterface renderer;
    auto* previousRenderer = g_ifCharIF;
    g_ifCharIF = &renderer;
    struct ResetAnimation {
        ChInterface* previous;
        ~ResetAnimation() {
            _DestroyAnimationMgr();
            g_ifCharIF = previous;
        }
    } resetAnimation{previousRenderer};
    check(_CreateAnimationMgr(), "ordinary animation manager");
    CCharacterMgr manager;
    manager.CreateAvatar();
    auto* avatar = _GetAvatar();
    check(avatar != nullptr, "actual local player");
    constexpr DWORD avatarSerial = 30214, monsterSerial = 30215;
    avatar->SetCharTypeID(CTI_AVATAR);
    avatar->SetIndex(avatarSerial);
    avatar->SetUnitMountState(UMS_DISMOUNT);
    auto* previous = g_pUiGaugeWindow;
    g_pUiGaugeWindow = &panel;
    struct ResetGauge {
        CGUIGaugeExpWindow* previous;
        ~ResetGauge() { g_pUiGaugeWindow = previous; }
    } reset{previous};

    avatar->SetMaxHP(160000);
    avatar->SetHP(160000);
    panel.SetGauge(CGUIGaugeExpWindow::FORCE_BAR, 200, 150);
    panel.SetGauge(CGUIGaugeExpWindow::STAMINA_BAR, 100, 100);
    auto* monster = manager.AddMonster(monsterSerial);
    check(monster != nullptr, "ordinary attacker");
    monster->SetIndex(monsterSerial);
    CNetMsgProcessor_Combat combat;
    constexpr LONG damage = 70000;
    std::array<char, 15> hit{};
    std::memcpy(hit.data(), &monsterSerial, sizeof monsterSerial);
    hit[6] = CTI_PLAYER;
    std::memcpy(hit.data() + 7, &avatarSerial, sizeof avatarSerial);
    std::memcpy(hit.data() + 11, &damage, sizeof damage);
    _MSG_HEADER hitHeader{19, {5, 13}};
    check(combat.AnalysisServerPacket(&hitHeader, hit.data()), "ordinary incoming attack");
    auto* impact = avatar->GetAttackerInfo(monster);
    check(impact != nullptr, "incoming attack record");
    impact->SetEffectFrameNum(1);
    impact->SetDamaged(TRUE);
    avatar->GetCombatState()->ProcessDamage();
    const auto life = CGUIGaugeExpWindow::LIFE_BAR;
    check(impact->GetCurDamagePoint() == damage && avatar->GetHP() == 160000 &&
          panel.GetCurrentGauge(life) == 160000, "impact awaits an authoritative health update");
    _GetEffectInfoList()->Clear();

    CNetMsgProcessor_Event events;
    std::array<char, 5> payload{};
    const auto send = [&](DWORD hp, WORD bytes) {
        std::memcpy(payload.data(), &hp, sizeof hp);
        _MSG_HEADER header{WORD(4 + bytes), {11, 14}};
        return events.AnalysisServerPacket(&header, payload.data());
    };
    check(!send(90000, 3) && !send(90000, 5) && avatar->GetHP() == 160000 &&
          panel.GetCurrentGauge(life) == 160000, "invalid lengths preserve HP and HUD");
    check(send(90000, 4) && avatar->GetHP() == 90000 && panel.GetCurrentGauge(life) == 90000,
          "ordinary event applies all 32 bits to the player and HUD");
    auto* bar = panel.GetAddedObject(2);
    auto* sprite = bar->GetSpriteInfo()->pSprite;
    check(bar->m_ptSize.x == LONG(double(sprite->GetSpriteOrgXL(0, 1)) * 0.5625) &&
          !std::strcmp(info.GetInfoValue455(9)->GetString(), "90000 / 160000"),
          "visible life gauge width and character sheet agree");
    capture([&]() { check(panel.Draw() != 0, "draw updated health gauge"); }, "hud-avatar-health.bgra");

    avatar->SetUnitMountState(UMS_MOUNT);
    check(send(70000, 4) && avatar->GetHP() == 0 && panel.GetCurrentGauge(life) == 0,
          "active unit gauge reads the unit owner");
    avatar->SetUnitMountState(UMS_DISMOUNT);
    check(avatar->GetHP() == 70000, "player HP received while mounted survives dismount");
    check(send(0, 4) && avatar->GetHP() == 0 && panel.GetCurrentGauge(life) == 0,
          "zero current HP reaches the gauge");
}

static int hud159(bool avatarHealth){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"language");
    InitR3Engine();GetR3State()->mScreenXsize=640;GetR3State()->mScreenYsize=480;GetR3State()->mbFullScreen=FALSE;ForceFullScreen();
    check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"device");
    const auto baseline=GetDmallocSize();unsigned pixels=0;
    {
        CGUICharInfoWindow info;auto* previous=g_pUiCharInfoWindow;g_pUiCharInfoWindow=&info;
        struct Reset{CGUICharInfoWindow* prior;~Reset(){g_pUiCharInfoWindow=prior;}} reset{previous};
        CGUIGaugeExpWindow panel;panel.SetPos(20,30);panel.Show(TRUE);panel.Init();
        check(panel.GetAddedObjectNum()==17,"actual455child composition");
        auto bar=[&](unsigned i){return static_cast<CGUIObjectEx*>(panel.GetAddedObject(i==3?13:2+4*i));};
        auto backing=[&](unsigned i){return panel.GetAddedObject(i==3?12:1+4*i);};
        auto value=[&](BYTE slot,const char* text){check(info.GetInfoValue455(slot)&&info.GetInfoValue455(slot)->GetString()&&!std::strcmp(info.GetInfoValue455(slot)->GetString(),text),"actual455CharInfo callback");};
        auto* sprite=gSpriteMgr.GetTargetSprite455(4);check(sprite&&panel.GetSpriteInfo()->pSprite==sprite,"actualmainatlas");
        check(panel.m_ptSize.x==sprite->GetSpriteOrgXL(0,0)&&panel.m_ptSize.y==sprite->GetSpriteOrgYL(0,0),"root natural frame size");
        for(unsigned i=0;i<3;++i){
            check(bar(i)->GetSpriteInfo()->wFrameNo==i+1&&panel.GetAddedObject(4*i)->GetSpriteInfo()->wFrameNo==i+4,"actualbar/iconframes");
            check(backing(i)->m_ptPos.x==107&&backing(i)->m_ptPos.y==46+14*i&&bar(i)->m_ptPos.x==107&&bar(i)->m_ptPos.y==46+14*i,"actual horizontal layout");
            check(bar(i)->m_ptSize.x==sprite->GetSpriteOrgXL(0,i+1),"zero maximum keeps full bar");
        }
        check(bar(3)->m_ptPos.x==35&&bar(3)->m_ptPos.y==42&&bar(3)->GetSpriteInfo()->wFrameNo==7,"fourth full vertical placement");
        check(!panel.GetAddedObject(16)->IsShow()&&panel.GetAddedObject(16)->m_ptPos.x==85,"target notice initially hidden");
        value(9,"0 / 0");value(10,"-");value(11,"-");value(12,"100 / 100");
        panel.SetLevel(42);value(3,"42");check(panel.GetLevel()==42&&panel.GetAddedObject(15)->m_ptPos.x==39&&panel.GetAddedObject(15)->m_ptPos.y==26,"actual level centering");
        auto draw=[&](){check(panel.Draw()!=0,"ordinary gauge Draw");};pixels=capture(draw,"hud-initial.bgra");
        panel.SetGauge(CGUIGaugeExpWindow::LIFE_BAR,1000,250);value(9,"250 / 1000");
        check(bar(0)->m_ptSize.x==LONG(double(sprite->GetSpriteOrgXL(0,1))*.25),"horizontal quarter");
        panel.SetGauge(CGUIGaugeExpWindow::FORCE_BAR,0,1000);value(10,"-");check(panel.GetCurrentGauge(CGUIGaugeExpWindow::FORCE_BAR)==0,"clamp before zero-maximum callback");
        panel.SetGauge(CGUIGaugeExpWindow::STAMINA_BAR,0xffffffff,0x80000000);value(11,"-2147483648 / -1");
        for(unsigned i=0;i<7;++i){
            const DWORD current[]={0,199,200,699,700,1000,1001};const WORD frame[]={9,9,8,8,7,7,7};
            panel.SetGauge(CGUIGaugeExpWindow::FOURTH_BAR455,1000,current[i]);check(bar(3)->GetSpriteInfo()->wFrameNo==frame[i],"exact fourth-color thresholds");
            check(bar(3)->m_ptPos.y+bar(3)->m_ptSize.y==backing(3)->m_ptPos.y+backing(3)->m_ptSize.y,"bottom-anchored vertical bar");
        }
        panel.SetGauge(CGUIGaugeExpWindow::FOURTH_BAR455,1000,100);value(12,"100 / 1000");capture(draw,"hud-changed.bgra");
        const auto children=panel.GetAddedObjectNum();gSpriteMgr.UnloadTargetSprites455();panel.SetSprite();
        panel.SetGauge(CGUIGaugeExpWindow::LIFE_BAR,1000,250);panel.SetGauge(CGUIGaugeExpWindow::FORCE_BAR,0,0);
        panel.SetGauge(CGUIGaugeExpWindow::STAMINA_BAR,0xffffffff,0x80000000);panel.SetGauge(CGUIGaugeExpWindow::FOURTH_BAR455,1000,100);panel.SetLevel(42);
        check(panel.GetAddedObjectNum()==children,"sprite reload does not duplicate children");capture(draw,"hud-reloaded.bgra");
        panel.SetLevel(300);value(3,"44");check(panel.GetLevel()==44,"target BYTE level");
        panel.SetGauge(CGUIGaugeExpWindow::Bar(255),1,1);check(panel.GetAddedObjectNum()==17,"out-of-domain bar ignored");
        if (avatarHealth) checkAvatarHealth(panel, info);
    }
    GetD3dDevice()->SetTexture(0,nullptr);gSpriteMgr.UnloadTargetSprites455();check(GetDmallocSize()==baseline,"sprite allocator balance");
    R3ReleaseTextTexture();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();
    FILE* f=std::fopen("result.json","wb");check(f!=nullptr,"report");
    std::fprintf(f,"{\"status\":\"PASS\",\"actual_HUD_children\":17,\"actual_target_skins\":3,\"fourth_threshold_cases\":7,\"char_info_value_indices\":[3,9,10,11,12],\"sprite_reload\":true,\"GPU_frames\":%d,\"initial_pixels\":%u,\"sprite_allocator_balanced\":true,\"full_MainGame\":false,\"full_client\":false",avatarHealth ? 4 : 3,pixels);
    if (avatarHealth)
        std::fputs(",\"avatar_health\":{\"hp\":[160000,90000,70000,0],\"impact_damage\":70000,\"hp_after_impact\":160000,\"invalid_lengths\":2,\"mounted_player_hp_retained\":true}", f);
    std::fputs("}\n", f);
    std::fclose(f);
    return 0;
}
int main(int argc, char** argv){try{return hud159(argc == 2 && !std::strcmp(argv[1], "--avatar-health"));}catch(const std::exception& e){std::fprintf(stderr,"HUD159: %s\n",e.what());return 1;}}
