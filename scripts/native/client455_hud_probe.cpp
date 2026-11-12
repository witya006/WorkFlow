//Reuse the GPU readback helper only; the old bulk entry is never executed.
#define main RF455_UnusedIconProbeMain159
#include "client455_item_icon_probe.cpp"
#undef main
#include "userinterface/gamewindow/guigaugeexpwindow.h"
#include "userinterface/gamewindow/guicharinfowindow.h"
#include "userinterface/gamewindow/etcwin/guiradarwindow.h"
#include "userinterface/gamewindow/guihotkeyboard.h"
#include "client455_linker_window.h"
#include "gameprogress/cinputprocessmgr.h"
#include "gameobject/manager/ccharactermgr.h"
#include "network/netmsgprocessor/combat/cnetmsgprocessor_combat.h"
#include "network/netmsgprocessor/event/cnetmsgprocessor_event.h"
#include <array>
extern CGUICharInfoWindow* g_pUiCharInfoWindow;

struct HudBoards {
    using Type = CBaseBoard*(CBoardManager::*)[MAX_BOARD_TYPE];
    friend Type access(HudBoards);
};
template<class Tag, typename Tag::Type Member>
struct HudMember { friend typename Tag::Type access(Tag) { return Member; } };
template struct HudMember<HudBoards, &CBoardManager::m_listBoard>;
struct HudLinkerInput : CInputProcessMgr {
    using CInputProcessMgr::ProcessLinkerKeys455;
};

static unsigned checkRadar()
{
    CGUIRadarWindow radar;
    radar.Init();
    radar.SetPos(640 - radar.GetSizeX(), 0);
    radar.Show(TRUE);
    check(radar.GetAddedObjectNum() == 3, "radar composition");
    auto* compass = static_cast<CGUIObjectEx*>(radar.GetAddedObject(0));
    auto* arrow = static_cast<CGUIObjectEx*>(radar.GetAddedObject(1));
    auto* markers = radar.GetAddedObject(2);
    auto* atlas = gSpriteMgr.GetTargetSprite455(4);
    CGUIObject* const layers[] = {&radar, compass, arrow};
    for (WORD frame = 0; frame < _countof(layers); ++frame) {
        const auto* info = layers[frame]->GetSpriteInfo();
        check(info->pSprite == atlas && info->wActionNo == 3 && info->wFrameNo == frame,
              "actual radar layer frames");
    }
    check(radar.GetSizeX() == 146 && radar.GetSizeY() == 163 && radar.GetPosX() == 494,
          "right aligned frame dimensions");
    check(markers->GetPosX() == 525 && markers->GetPosY() == 32 &&
          markers->GetSizeX() == 97 && markers->GetSizeY() == 97, "radar marker board geometry");
    for (auto* layer : {compass, arrow})
        check(layer->GetPosX() == 527 && layer->GetPosY() == 34 &&
              layer->GetSizeX() == 93 && layer->GetSizeY() == 93, "radar layer geometry");

    const auto draw = [&]() { check(radar.Draw() != 0, "ordinary radar draw"); };
    radar.SetCameraRotate(0.0f);
    radar.SetAvatarRotate(0.0f);
    const auto pixels = capture(draw, "radar-north.bgra");
    radar.SetCameraRotate(45.0f);
    radar.SetAvatarRotate(0.0f);
    check(compass->GetRotate() == 45.0f && arrow->GetRotate() == 45.0f, "camera turns both radar layers");
    capture(draw, "radar-camera-turned.bgra");
    radar.SetAvatarRotate(90.0f);
    check(compass->GetRotate() == 45.0f && arrow->GetRotate() == 135.0f, "avatar turns its own radar layer");
    capture(draw, "radar-avatar-turned.bgra");
    return pixels;
}

static unsigned checkBottomHud()
{
    const POINT previous = gScreen.m_ptSize;
    unsigned pixels = 0;
    for (const auto viewport : {POINT{640, 480}, POINT{1280, 720}}) {
        const bool scaled = viewport.x == 640;
        gScreen.SetSize(viewport.x, viewport.y);
        CGUIHotKeyBoard hud;
        CLinkBoard linker;
        linker.CObjectBoard::Create(IBT_LINK, 5, 10);
        auto& link = linker.LinkerWindow455();
        hud.Init();
        link.Init();
        hud.SetPos(0, viewport.y - hud.GetSizeY());
        gScreen.Add(&link);
        hud.SetLinkWindow455(&link);
        hud.Show(TRUE);

        auto* frame = hud.GetAddedObject(0);
        const auto* info = frame->GetSpriteInfo();
        check(info->pSprite == gSpriteMgr.GetTargetSprite455(4) && info->wActionNo == 11 && info->wFrameNo == 0,
              "actual bottom HUD frame");
        check(frame->GetPosX() == (scaled ? 0 : 128) && frame->GetPosY() == (scaled ? 441 : 657) &&
              frame->GetSizeX() == (scaled ? 640 : 1024) && frame->GetSizeY() == (scaled ? 39 : 63),
              "viewport-specific bottom HUD geometry");
        check(hud.IsAddedObject(&link) && !gScreen.IsAddedObject(&link), "one owner for Linker");
        check(link.GetPosX() == (scaled ? 170 : 400) && link.GetPosY() == (scaled ? 443 : 661),
              "Linker follows the centered background");
        check(link.HotbarState455().active == 0 && link.GetItem(4, 9), "five banks of ten");

        if (scaled) {
            const auto draw = [&]() { check(hud.Draw() != 0, "ordinary bottom HUD draw"); };
            pixels = capture(draw, "bottom-collapsed.bgra");
            auto& registered = (_GetGBM()->*access(HudBoards{}))[IBT_LINK];
            check(!registered, "empty Linker registry slot");
            registered = &linker;
            struct ReleaseRegistration {
                CBaseBoard*& slot;
                ~ReleaseRegistration() { slot = nullptr; }
            } release{registered};
            HudLinkerInput keys;
            link.SetBankFlag455(1, 0);
            link.SetBankFlag455(2, 0);
            gScan[VK_OEM_3] = 1;
            keys.ProcessLinkerKeys455(1000, TRUE);
            check(link.HotbarState455().active == 0 && !gScan[VK_OEM_3], "chat suppresses bank cycling");
            gScan[VK_OEM_3] = 1;
            keys.ProcessLinkerKeys455(1001, FALSE);
            check(link.HotbarState455().active == 3, "keyboard selects next pinned bank");
            keys.ProcessLinkerKeys455(1002, FALSE);
            check(link.HotbarState455().active == 3, "one bank change per key event");
            capture(draw, "bottom-bank4.bgra");
            link.ResetBankFlags455();
            link.SetExpanded455(TRUE);
            check(link.GetSizeY() == 5 * 28, "five expanded rows");
            capture(draw, "bottom-expanded.bgra");
        }
        hud.SetLinkWindow455(nullptr);
        check(!hud.IsAddedObject(&link) && !gScreen.IsAddedObject(&link), "Linker detaches cleanly");
    }
    gScreen.SetSize(previous.x, previous.y);
    return pixels;
}

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

static int hud159(bool avatarHealth, bool radarOnly, bool bottomOnly){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"language");
    InitR3Engine();GetR3State()->mScreenXsize=640;GetR3State()->mScreenYsize=480;GetR3State()->mbFullScreen=FALSE;ForceFullScreen();
    check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"device");
    const auto baseline=GetDmallocSize();unsigned pixels=0;
    if (radarOnly) {
        pixels = checkRadar();
    } else if (bottomOnly) {
        pixels = checkBottomHud();
    } else {
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
    if (radarOnly) {
        std::fprintf(f,"{\"status\":\"PASS\",\"frame\":[146,163],\"layers\":[93,93],\"board\":[97,97],\"GPU_frames\":3,\"initial_pixels\":%u}\n",pixels);
        std::fclose(f);
        return 0;
    }
    if (bottomOnly) {
        std::fprintf(f,"{\"status\":\"PASS\",\"layouts\":[[640,480],[1280,720]],\"banks\":5,\"slots_per_bank\":10,\"single_owner\":true,\"keyboard_next_bank\":[0,3],\"GPU_frames\":3,\"initial_pixels\":%u}\n",pixels);
        std::fclose(f);
        return 0;
    }
    std::fprintf(f,"{\"status\":\"PASS\",\"actual_HUD_children\":17,\"actual_target_skins\":3,\"fourth_threshold_cases\":7,\"char_info_value_indices\":[3,9,10,11,12],\"sprite_reload\":true,\"GPU_frames\":%d,\"initial_pixels\":%u,\"sprite_allocator_balanced\":true,\"full_MainGame\":false,\"full_client\":false",avatarHealth ? 4 : 3,pixels);
    if (avatarHealth)
        std::fputs(",\"avatar_health\":{\"hp\":[160000,90000,70000,0],\"impact_damage\":70000,\"hp_after_impact\":160000,\"invalid_lengths\":2,\"mounted_player_hp_retained\":true}", f);
    std::fputs("}\n", f);
    std::fclose(f);
    return 0;
}
int main(int argc, char** argv){try{return hud159(argc == 2 && !std::strcmp(argv[1], "--avatar-health"), argc == 2 && !std::strcmp(argv[1], "--radar"), argc == 2 && !std::strcmp(argv[1], "--bottom-hud"));}catch(const std::exception& e){std::fprintf(stderr,"HUD159: %s\n",e.what());return 1;}}
