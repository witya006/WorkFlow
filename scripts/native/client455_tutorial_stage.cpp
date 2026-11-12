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
#include "userinterface/guicontroller/guimessagebox.h"
#include "mainapp.h"
#include "client455_briefing_window.h"
#include "client455_fullscreen_effect.h"
#include "client455_nation_paths.h"
#include "client455_protocol_observation.h"
#include "client455_tutorial_intro.h"
#include "client455_tutorial_stage.h"
#include <cstring>
#include <string>

namespace {
constexpr WORD welcomeDialog = 0x6000;
constexpr WORD leaveDialog = 0x6001;

class CGP_Tutorial455 final : public CGameProgress, private RF455TutorialIntroCameraHost,
                              private RF455TutorialBoardHost {
    enum class Phase { Intro, Welcome, Briefing, Leaving, Selecting, Zone, Failed };
    RF455TutorialIntro intro;
    RF455TutorialBoardShared boardState;
    RF455TutorialRuntime runtime;
    RF455TutorialBriefingWindow briefing;
    CTutorialBoard board{runtime, *this, boardState, &briefing};
    RF455TutorialScript script;
    Phase phase = Phase::Intro;
    bool skipIntro = false;
    bool inputBlocked = false;
    bool uiInstalled = false;
    DWORD selectStarted = 0;
    DWORD savedCameraFlags = 0;
    bool savedScreenVisible = true;
    bool savedMouseVisible = true;
    Vector3f cameraPosition{};

    BOOL LoadData() override;
    BOOL UnloadData() override;
    HRESULT FrameMove() override;
    HRESULT Render() override;
    BOOL InputProcess() override;
    void showScreen(bool visible) override { _GetUIScreen()->Show(visible ? TRUE : FALSE); }
    void showMouse(bool visible) override { _GetUIScreen()->GetMouse()->Show(visible ? TRUE : FALSE); }
    void blockStageInput(bool blocked) override { inputBlocked = blocked; }
    void startBoardScript() override;
    void followAvatarCamera() override;
    bool skipTutorial() override { return _GetAvatar()->GetSkipTutorial455() != 0; }
    void setSkipTutorial(std::uint32_t value) override { _GetAvatar()->SetSkipTutorial455(value); }
    std::uint32_t milliseconds() override { return timeGetTime(); }
    void releaseUiCapture() override { _GetUIScreen()->SetCapture455(nullptr); }
    void stageVirtual52() override { phase = Phase::Leaving; }
    void setStageInput(std::uint32_t value) override { inputBlocked = value != 0; }
    void setAvatarStage(std::uint8_t value) override { _GetAvatar()->SetClientStage455(value); }
    void reportProgressRequested() override {
        RF455_ObserveProtocol("tutorial-progress-report-pending", 0, 0, 0);
    }
    void fail(const char* message);
    bool openFirstBriefing();
public:
    ~CGP_Tutorial455() override { Destroy(); }
    BOOL Create() override;
    BOOL Destroy() override;
    HRESULT RestoreDeviceObjects() override;
    HRESULT InvalidateDeviceObjects() override { return S_OK; }
    LRESULT MsgProc(HWND, UINT, WPARAM, LPARAM) override;
    void Dialog(WORD id, DWORD result);
};

BOOL CGP_Tutorial455::LoadData()
{
    static const char* const maps[] = {"Bellato", "Cora", "Accretia"};
    const unsigned race = _GetAvatar()->GetRace() / 2;
    if (race >= 3) return FALSE;
    const std::string map = maps[race];
    std::string path = ".\\Map\\" + map + "\\" + map + ".bsp";
    if (!_GetLand()->LoadLevel(&path[0]) || !_GetLand()->GetLevel()->IsLoadedBsp()) return FALSE;
    m_bIsLoadedData = TRUE;
    return TRUE;
}

BOOL CGP_Tutorial455::UnloadData()
{
    if (m_bIsLoadedData) _GetLand()->UnloadLevel();
    m_bIsLoadedData = FALSE;
    return TRUE;
}

BOOL CGP_Tutorial455::Create()
{
    if (m_bIsCreated) return TRUE;
    if (phase == Phase::Failed || !CGameProgress::Create()) return FALSE;
    auto* screen = _GetUIScreen();
    savedScreenVisible = screen->IsShow() != FALSE;
    savedMouseVisible = screen->GetMouse()->IsShow() != FALSE;
    savedCameraFlags = cameraControlFlags();
    // Login releases its sprite set before this stage is created. Its child
    // windows must be detached before drawing the new scene and dialogs.
    screen->SetCapture455(nullptr);
    screen->RemoveAll();
    if (!LoadData()) {
        fail("Tutorial map could not be loaded.");
        return FALSE;
    }
    static constexpr float spawn[][3] = {{2466, 277, -1129}, {2491, 491, -3978}, {-4295, -296, 165}};
    const auto& start = spawn[_GetAvatar()->GetRace() / 2];
    _GetAvatar()->SetPosition(start[0], start[1], start[2], TRUE, TRUE);
    _GetAvatar()->SetLightColor(ID_INVALID);
    _GetAvatar()->Disable(ROSF_RENDER_ALPHA);
    _GetAvatar()->SetAction(CAI_MOVE_STOP, TRUE);
    _GetCamera()->SetPosition(start[0], start[1], start[2]);
    _GetUISpriteMgr()->LoadSprite(SP_ID_COMMON);
    _GetUISpriteMgr()->LoadSprite(SP_ID_MOUSE);
    board.InitWindow(38, -1, -3);
    uiInstalled = true;
    briefing.window().Close();
    screen->RestoreSprite();
    if (!intro.load(_GetAvatar()->GetRace(), *this)) {
        fail("Tutorial camera could not be loaded.");
        return FALSE;
    }
    fadeIn(0, 2, 1);
    m_bIsCreated = TRUE;
    RF455_ObserveProtocol("tutorial-intro", _GetAvatar()->GetRace(), cameraCount(), 0);
    return TRUE;
}

BOOL CGP_Tutorial455::Destroy()
{
    m_bIsCreated = FALSE;
    if (uiInstalled) {
        releaseUiCapture();
        _CloseDialogBox(nullptr, welcomeDialog);
        _CloseDialogBox(nullptr, leaveDialog);
        _GetUIScreen()->Remove(&briefing.window());
        showScreen(savedScreenVisible);
        showMouse(savedMouseVisible);
        if (GetD3dDevice()) {
            setCameraControlFlags(savedCameraFlags);
            setEngineRenderFlag(0);
            setEngineFloat8CE9D0(0.25f);
        }
        uiInstalled = false;
    }
    UnloadData();
    return TRUE;
}

void CGP_Tutorial455::fail(const char* message)
{
    phase = Phase::Failed;
    RF455_ObserveProtocol("tutorial-failed", 0, 0, 0);
    showScreen(true);
    showMouse(true);
    _GetMainApp()->RequestQuitProgram(3000, const_cast<char*>(message));
}

void CGP_Tutorial455::startBoardScript()
{
    auto* avatar = _GetAvatar();
    const auto row = _GetCharDataMgr()->GetClassData455ByIndex(avatar->GetClassDTIndex(0));
    const unsigned race = avatar->GetRace() / 2;
    if (!row.data || row.size < 16 || race >= 3) {
        fail("Tutorial class could not be identified.");
        return;
    }
    const char type = static_cast<char>(row.data[13]);
    if (type != 'W' && type != 'R' && type != 'F' && type != 'S') {
        fail("Tutorial class could not be identified.");
        return;
    }
    const char file[] = {"bca"[race], char(type + 'a' - 'A'), '.', 's', 'c', 'p', 0};
    const auto path = std::string(RF455_GetClientDataRoot()) + "\\" + file;
    if (!RF455_LoadTutorialScript(path.c_str(), script) || script.quests.empty() ||
        script.quests[0].instructions.empty() || script.quests[0].instructions[0].dataType != 2 ||
        !board.message(2, &script.quests[0].instructions[0].message, 0)) {
        fail("Tutorial script could not be loaded.");
        return;
    }
    phase = Phase::Welcome;
    RF455_ObserveProtocol("tutorial-welcome", race, static_cast<unsigned>(type), 0);
}

bool CGP_Tutorial455::openFirstBriefing()
{
    if (script.quests.size() < 2) return false;
    const auto& commands = script.quests[1].instructions;
    if (commands.size() < 3 || commands[0].selector != 13 || commands[1].selector != 14 ||
        commands[2].dataType != 1) return false;
    Vector3f orbit{};
    std::memcpy(orbit, commands[1].fixed.data() + 8, sizeof(orbit));
    float yaw = 0;
    std::memcpy(&yaw, commands[0].fixed.data() + 12, sizeof(yaw));
    _GetAvatar()->SetRotY(yaw, FALSE);
    _GetCamera()->SetYaw(orbit[0]);
    _GetCamera()->SetPitch(orbit[1]);
    _GetCamera()->SetDistance(orbit[2]);
    return board.message(1, &commands[2].message, 0);
}

void CGP_Tutorial455::followAvatarCamera()
{
    auto* avatar = _GetAvatar();
    Vector3f target{};
    std::memcpy(target, avatar->GetPosition(), sizeof(target));
    _GetCamera()->SetPosition(target);
    _GetCamera()->Render();
    _GetCamera()->GetR3Camera()->GetPos(cameraPosition);
}

HRESULT CGP_Tutorial455::FrameMove()
{
    if (phase != Phase::Failed) {
        intro.frame(*this, skipIntro);
        if (intro.active()) std::memcpy(cameraPosition, position(), sizeof(cameraPosition));
        _GetLand()->GetLevel()->FrameMove();
        if (!intro.active()) {
            _GetAvatar()->FrameMove();
            _GetAvatar()->Animation();
        }
    }
    _GetUIScreen()->Update();
    return S_OK;
}

HRESULT CGP_Tutorial455::Render()
{
    if (!R3BeginScene()) return S_OK;
    R3ClearFrameBuffer();
    _GetLand()->Render(cameraPosition);
    if (intro.active()) FullScreenEffect();
    else if (phase != Phase::Failed) {
        _GetCharIF()->SetState();
        _GetAvatar()->Render();
        _GetCharIF()->UnSetState();
    }
    if (_GetUIScreen()->IsShow()) _GetUIScreen()->Draw();
    DrawFadeScreen();
    R3EndScene();
    RF455_CaptureTutorialFrame455();
    return S_OK;
}

BOOL CGP_Tutorial455::InputProcess()
{
    _GetUIMouseDev()->Update();
    _GetUIScreen()->InputProc();
    auto* network = _GetNetworkMgr();
    if (phase == Phase::Leaving && IsFadeOut()) {
        if (!network->SystemMsg_SelCharRequest_zone(BYTE(RF455_SelectedCharacterSlot()))) {
            fail("Tutorial could not select the character on the server.");
            return TRUE;
        }
        phase = Phase::Selecting;
        selectStarted = timeGetTime();
    } else if (phase == Phase::Selecting) {
        const BYTE result = network->GetResultOfCharacterSelect();
        if (result == CHAR_SELECT_SUCCESS) {
            network->SetResultOfCharacterSelect(CHAR_SELECT_NOT_RECIVED);
            network->Connect(GST_ZONE);
            phase = Phase::Zone;
            selectStarted = timeGetTime();
        } else if (result != CHAR_SELECT_NOT_RECIVED || timeGetTime() - selectStarted >= 15000) {
            fail("The server did not confirm character selection after Tutorial.");
        }
    } else if (phase == Phase::Zone) {
        if (network->IsConnectedToServer(GST_ZONE)) {
            SetNextStage455(GPI_MAIN_GAME);
            RequestStageExit455();
        } else if (timeGetTime() - selectStarted >= 15000) {
            fail("The server did not accept the zone connection after Tutorial.");
        }
    }
    return TRUE;
}

void CGP_Tutorial455::Dialog(WORD id, DWORD result)
{
    if (!m_bIsCreated) return;
    if ((phase == Phase::Welcome && id == welcomeDialog && result == MSG_CANCEL) ||
        (phase == Phase::Briefing && id == leaveDialog && result == MSG_OK)) {
        board.requestFinish(true);
        fadeOut(0, 2, 1);
        RF455_ObserveProtocol("tutorial-leaving", RF455_SelectedCharacterSlot(), 0, 0);
    } else if (phase == Phase::Welcome && id == welcomeDialog && result == MSG_OK) {
        if (!openFirstBriefing()) {
            fail("Tutorial briefing could not be opened.");
            return;
        }
        phase = Phase::Briefing;
        RF455_ObserveProtocol("tutorial-briefing", 1, 0, 0);
    }
}

HRESULT CGP_Tutorial455::RestoreDeviceObjects()
{
    if (uiInstalled) _GetUIScreen()->RestoreSprite();
    return S_OK;
}

LRESULT CGP_Tutorial455::MsgProc(HWND window, UINT message, WPARAM key, LPARAM data)
{
    if (phase == Phase::Intro && message == WM_KEYDOWN && key == VK_ESCAPE && !(data & (1L << 30))) {
        skipIntro = true;
        return 0xffffffff;
    }
    // The modal handles WM_CHAR Escape as Close. Open on release so the
    // character event from the same press cannot close the new dialog.
    if (phase == Phase::Briefing && message == WM_KEYUP && key == VK_ESCAPE &&
        !_IsOpenedDialogBox(nullptr, leaveDialog)) {
        board.openLanguageDialog(444, leaveDialog);
        return 0xffffffff;
    }
    if (!inputBlocked) _GetUIScreen()->MsgProc(window, message, key, data);
    return 0;
}
}

CGameProgress* RF455_CreateTutorialStage() { return new CGP_Tutorial455; }

void RF455_DeliverTutorialDialog(CGameProgress& stage, WORD id, DWORD result)
{
    static_cast<CGP_Tutorial455&>(stage).Dialog(id, result);
}
