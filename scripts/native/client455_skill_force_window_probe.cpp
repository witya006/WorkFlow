#define main RF455_UnusedIconProbeMain
#include "client455_item_icon_probe.cpp"
#undef main

#include "gameobject/board/skillforceboard/cskillboard.h"
#include "gameobject/board/skillforceboard/cforceboard.h"
#include "client455_client_items.h"
#include "client455_tutorial_inventory.h"
#include "client455_tutorial_skills.h"
#include "userinterface/uiglobal.h"
#include <fstream>
#include <iterator>

extern CSpriteMgr* g_pUiSpriteMgr;

template<class Tag, typename Tag::Type Member>
struct ProbeMember { friend typename Tag::Type access(Tag) { return Member; } };
struct QueueCreate { using Type = void(*)(WORD); friend Type access(QueueCreate); };
struct QueueProcess { using Type = void(*)(); friend Type access(QueueProcess); };
struct SendMouse { using Type = void(CGUIObject::*)(WORD); friend Type access(SendMouse); };
template struct ProbeMember<QueueCreate, &CGUIObject::CreateEventQueue>;
template struct ProbeMember<QueueProcess, &CGUIObject::EventProcess>;
template struct ProbeMember<SendMouse, &CGUIObject::SendMouseEvent>;

static void mouse(CGUIObject& object, WORD event)
{
    (object.*access(SendMouse{}))(event);
    access(QueueProcess{})();
}

static CGUIObject& child(CGUIContainer& owner, WORD index)
{
    auto* object = owner.GetAddedObject(index);
    check(object != nullptr, "actual child owner");
    return *object;
}

static void sprite(CGUIObject& object, unsigned id, WORD action, WORD frame)
{
    auto* image = object.GetSpriteInfo();
    check(image->pSprite && image->pSprite == gSpriteMgr.GetTargetSprite455(id) &&
          image->wActionNo == action && image->wFrameNo == frame, "actual sprite frame");
}

static CGUISkillForceBoard& page(CGUISFWindow& window)
{
    for (int i = 0; i < window.GetAddedObjectNum(); ++i) {
        if (auto* current = dynamic_cast<CGUISkillForceBoard*>(&child(window, WORD(i)))) return *current;
    }
    throw std::runtime_error("visible window owns actual TabBoard");
}

static void checkTabs(CGUISFWindow& window, unsigned id, WORD action, const BYTE (&groups)[5], WORD firstFrame)
{
    check(window.GetSizeX() == 228 && window.GetSizeY() == 395 && window.GetAddedObjectNum() == 13,
          "actual root 228x395 and thirteen attached controls");
    for (BYTE i = 0; i < 5; ++i) {
        auto& tab = child(window, WORD(5 + i));
        sprite(tab, id, action, i == 0 ? firstFrame : i);
        mouse(tab, MOUSE_STROKED);
        auto& board = page(window);
        check(window.GetCurBoardTab() == i && board.Count455() == groups[i] && board.IsOpened455(0),
              "observer selects actual group layout and retains first open section");
        check(board.GetSizeX() == 219 && board.GetPosX() == window.GetPosX() + 5, "panel geometry");
        sprite(*board.Header455(0), 1, 5, 1);
    }
    mouse(child(window, 5), MOUSE_STROKED);
}

static _skill_force_info rowInfo(BYTE type, DWORD ordinal)
{
    const auto row = RF455_GameItems().skillForce.get(type, ordinal);
    check(row.data && row.size >= 144, "actual localized EDF record");
    _skill_force_info info = {};
    info.bySFType = type;
    info.dwIndex = type ? ordinal | 0xf0000000 : ordinal;
    info.byStep = 0;
    info.pName = reinterpret_cast<char*>(const_cast<unsigned char*>(row.data + 112));
    std::memcpy(&info.dwItemID, row.data + 4, 4);
    std::memcpy(&info.dwSpriteID, row.data + 8, 4);
    info.byLevel = 3;
    info.fExpByPercent = 42.35f;
    return info;
}

static void checkTutorialForceTransfers()
{
    std::ifstream input("DataTable/Item.edf", std::ios::binary);
    const std::vector<unsigned char> bytes{std::istreambuf_iterator<char>(input), {}};
    check(RF455_GameItems().data.loadItemEdf(bytes.data(), bytes.size(), true), "stock Item.edf");
    auto* oldScreen = g_pUiScreen;
    g_pUiScreen = CGUIScreen::GetSingletonPtr();
    g_pUiScreen->SetSize(1024, 768);
    for (BYTE race : {BYTE(0), BYTE(2)}) {
        _GetAvatar()->SetRace(race);
        RF455TutorialInventory bag;
        RF455TutorialSkills force;
        bag.initialize();
        force.initialize(true);
        force.show(true);
        bag.show(true);
        POINT point{};
        check(force.isOpen() && force.skillPoint(0x9202, point), "real Force row in panel");
        check(!force.hasBeacon(0x9300), "Force wait needs installed beacon");
        const BYTE demo = bag.grant(18, 0xc50b0003);
        const BYTE practice = bag.grant(18, 0xc00b0001);
        check(bag.beaconForceCode(demo) == 0x9202 && bag.beaconForceCode(practice) == 0x9300, "actual beacon rows");
        bag.handleMessage(WM_BOARD_CHECK_REMOVE_OBJECT, UII_INVENTORY_PACK, UI_MOUSE_MSG(0, demo, 0, 0).m_dwData);
        check(force.handleMessage(WM_BOARD_ADD_OBJECT, UII_FORCE_WINDOW, 0, bag) &&
              force.hasBeacon(0x9202) && bag.beaconForceCode(demo) == ID_INVALID, "GUI transfer installs demo beacon");
        check(force.installBeacon(bag, practice) && force.hasBeacon(0x9300), "QBI42 predicate after installing beacon");
        const BYTE duplicate = bag.grant(18, 0xc00b0001);
        check(!force.installBeacon(bag, duplicate) && bag.beaconForceCode(duplicate) == 0x9300, "duplicate stays in bag");
        force.handleMessage(WM_BOARD_REMOVE_OBJECT, UII_FORCE_WINDOW, 0xf0000028, bag);
        force.handleMessage(WM_BOARD_ADD_OBJECT, UII_INVENTORY_PACK, UI_MOUSE_MSG(0, duplicate, 0, 0).m_dwData, bag);
        check(force.hasBeacon(0x9300), "occupied bag slot rejects drop");
        force.handleMessage(WM_BOARD_ADD_OBJECT, UII_INVENTORY_PACK, UI_MOUSE_MSG(0, practice, 0, 0).m_dwData, bag);
        check(!force.hasBeacon(0x9300) && bag.beaconForceCode(practice) == 0x9300, "GUI return restores the beacon");
        const BYTE grant = bag.grant(18, 0xc50b0001);
        check(force.installBeacon(bag, grant) && force.readyForce(0xf0000018), "QBI41 installs the real Force row");
        force.handleMessage(WM_BOARD_REMOVE_OBJECT, UII_FORCE_WINDOW, 0xf0000018, bag);
        force.handleMessage(WM_BOARD_ADD_OBJECT, 3, UI_MOUSE_MSG(0, 0, 0, 0).m_dwData, bag);
        check(force.matchesShortcut(1, 0x9200) && !force.matchesShortcut(2, 0x9200), "QBI46 rejects wrong slot");
        force.handleMessage(WM_BOARD_REMOVE_OBJECT, UII_FORCE_WINDOW, 0xf0000018, bag);
        force.handleMessage(WM_BOARD_ADD_OBJECT, 3, UI_MOUSE_MSG(0, 1, 0, 0).m_dwData, bag);
        const auto* cast = force.shortcutSkill(0, 1);
        check(cast && cast->tableIndex() == 24 && force.matchesShortcut(2, 0x9200) &&
              !force.matchesShortcut(2, 0x9202), "QBI46 predicate requires row and slot");
        force.shutdown();
        bag.shutdown();
    }
    g_pUiScreen = oldScreen;
}

static int runSkillForce(bool tutorialTransfers)
{
    SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX | SEM_NOOPENFILEERRORBOX);
    check(RF455_InitializeNationPaths() && RF455_InitializeLanguageData(), "actual Taiwan language");
    check(RF455_GameItems().skillForce.loadFiles("DataTable/SkillForce.edf", "DataTable/zh-tw/NDSkillForce.edf"),
          "stock SkillForce records");
    InitR3Engine();
    GetR3State()->mScreenXsize = 640;
    GetR3State()->mScreenYsize = 480;
    GetR3State()->mbFullScreen = FALSE;
    ForceFullScreen();
    check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr), 0)), "D3D device");
    check(g_MainApp.CreateNetworkMgr455(), "normal client network manager allocation");
    auto* device = GetD3dDevice();
    IDirect3DSurface9 *oldTarget = nullptr, *oldDepth = nullptr, *canvas = nullptr;
    check(SUCCEEDED(device->GetRenderTarget(0, &oldTarget)), "old target");
    device->GetDepthStencilSurface(&oldDepth);
    D3DSURFACE_DESC desc = {};
    oldTarget->GetDesc(&desc);
    check(SUCCEEDED(device->CreateRenderTarget(640, 480, desc.Format, D3DMULTISAMPLE_NONE, 0, FALSE, &canvas, nullptr)) &&
          SUCCEEDED(device->SetDepthStencilSurface(nullptr)) && SUCCEEDED(device->SetRenderTarget(0, canvas)), "probe canvas");
    D3DVIEWPORT9 viewport = {0, 0, 640, 480, 0, 1};
    device->SetViewport(&viewport);
    access(QueueCreate{})(256);
    auto* oldSprites = g_pUiSpriteMgr;
    g_pUiSpriteMgr = &gSpriteMgr;
    gSpriteMgr.LoadSprite(SP_ID_COMMON);
    auto* screen = CGUIScreen::GetSingletonPtr();
    const HWND oldWindow = screen->GetHWND();
    HWND window = CreateWindowExA(0, "STATIC", "SkillForce455", 0, 0, 0, 0, 0, HWND_MESSAGE, nullptr,
                                  GetModuleHandleA(nullptr), nullptr);
    check(window != nullptr, "message window");
    screen->SetHWND(window);
    auto* oldAvatar = g_pAvatar;
    auto* oldData = g_pCharDataMgr;
    {
        CAvatar avatar;
        CCharacterDataMgr manager;
        g_pAvatar = &avatar;
        g_pCharDataMgr = &manager;
        avatar.SetRace(0);
        CSkillBoard skills;
        skills.Create(7, 7, 20);
        skills.InitWindow(5, 200, 60);
        skills.CreateBoardObject(7, 12, 100);
        check(skills.GetMaxPackNum() == 7 && skills.GetWindow()->GetID() == 5, "ordinary SkillBoard creation");
        for (BYTE i = 0; i < 7; ++i)
            check(skills.GetMaxSocketNum455(i) == 20 && !skills.AddPack(i), "seven active skill packs");
        auto& skill = static_cast<CGUISkillWindow&>(*skills.GetWindow());
        skill.Show(TRUE);
        const BYTE skillGroups[] = {4, 4, 1, 3, 1};
        checkTabs(skill, 45, 1, skillGroups, 0);
        mouse(child(skill, 4), MOUSE_CLICKED);
        MSG message = {};
        check(PeekMessageA(&message, window, 0x1204, 0x1204, PM_REMOVE) && message.wParam == 5 && !message.lParam,
              "skill help HWND route");
        auto sample = rowInfo(0, 0);
        auto second = rowInfo(0, 1);
        check(skill.TakeInItem(0, &sample) && skill.TakeInItem(0, &second), "actual two localized skill rows");
        auto* row = skill.GetIconBoard(0, sample.dwIndex);
        auto* next = skill.GetIconBoard(0, second.dwIndex);
        check(row && next && row->GetSizeX() == 207 && row->GetSizeY() == 44 && row->GetItem()->GetSizeX() == 38 &&
              next->GetPosY() - row->GetPosY() == 44, "actual row, icon and stacking geometry");
        row->SetUnitState(CGUISkFcUnit::Disabled);
        check(row->GetCover()->GetARGB() == 0x80a05050, "disabled row overlay");
        row->SetUnitState(CGUISkFcUnit::Enabled);
        check(capture([&] { check(skill.Draw(), "ordinary skills draw"); }, "skill.bgra") > 2000, "skills rendered");
        mouse(*page(skill).Header455(0), MOUSE_STROKED);
        check(!page(skill).IsOpened455(0), "section observer collapses actual skill rows");
        mouse(*page(skill).Header455(0), MOUSE_STROKED);
        check(page(skill).IsOpened455(0) && skill.TakeOutItem(0, sample.dwIndex) && !skill.GetIconBoard(0, sample.dwIndex),
              "row removal detaches real item");

        const BYTE forceGroups[] = {4, 4, 4, 4, 4};
        for (BYTE race = 0; race <= 4; race += 2) {
            avatar.SetRace(race);
            CForceBoard forces;
            forces.Create(3, 6, 20);
            forces.InitWindow(6, 300, 60);
            forces.CreateBoardObject(6, 24, 100);
            check(forces.GetMaxPackNum() == 6 && forces.GetMaxSocketNum455(5) == 20 && !forces.AddPack(5),
                  "six active force packs");
            if (race == 4) {
                check(!forces.GetWindow(), "Accretia leaves Force window absent");
                continue;
            }
            auto& force = static_cast<CGUIForceWindow&>(*forces.GetWindow());
            check(force.GetID() == 6, "force ID");
            force.Show(TRUE);
            checkTabs(force, 46, 0, forceGroups, race == 2 ? 5 : 0);
            auto forceInfo = rowInfo(1, race == 0 ? 12 : 0);
            check(force.TakeInItem(0, &forceInfo) && force.GetIconBoard(0, forceInfo.dwIndex), "actual localized force row");
            const char* name = race == 0 ? "force-bellato.bgra" : "force-cora.bgra";
            check(capture([&] { check(force.Draw(), "ordinary force draw"); }, name) > 2000, "force rendered");
            check(force.TakeOutItem(0, forceInfo.dwIndex), "remove with full DWORD identity");
            screen->Remove(&force);
        }
        screen->Remove(&skill);
        if (tutorialTransfers) checkTutorialForceTransfers();
        g_pCharDataMgr = oldData;
        g_pAvatar = oldAvatar;
    }
    screen->SetHWND(oldWindow);
    DestroyWindow(window);
    device->SetTexture(0, nullptr);
    gSpriteMgr.UnloadSpriteAll();
    g_pUiSpriteMgr = oldSprites;
    device->SetRenderTarget(0, oldTarget);
    device->SetDepthStencilSurface(oldDepth);
    canvas->Release();
    oldTarget->Release();
    if (oldDepth) oldDepth->Release();
    R3ReleaseTextTexture();
    g_MainApp.ReleaseR3D3D();
    ReleaseR3Engine();
    FILE* report = std::fopen("result.json", "wb");
    check(report != nullptr, "result output");
    std::fprintf(report, "{\"status\":\"PASS\",\"GPU_frames\":3,\"skill_packs\":7,\"force_packs\":6,"
                         "\"slots_per_pack\":20,\"skill_tabs\":5,\"force_tabs\":5,\"force_races\":3,"
                         "\"real_edf_view_rows\":4,\"production_population_complete\":false%s}\n",
                 tutorialTransfers ? ",\"tutorial_force_transfer_races\":2" : "");
    std::fclose(report);
    return 0;
}

int main(int argc, char** argv)
{
    try { return runSkillForce(argc == 2 && !std::strcmp(argv[1], "--tutorial-transfers")); }
    catch (const std::exception& error) {
        std::fprintf(stderr, "SkillForce455: %s\n", error.what());
        return 1;
    }
}
