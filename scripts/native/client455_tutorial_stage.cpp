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
#include "client455_option_window.h"
#include "client455_protocol_observation.h"
#include "client455_tutorial_intro.h"
#include "client455_tutorial_spatial.h"
#include "client455_tutorial_stage.h"
#include <cmath>
#include <cstring>
#include <string>

namespace {
constexpr WORD welcomeDialog = 0x6000;
constexpr WORD leaveDialog = 0x6001;
constexpr DWORD settingsQuest = 1;
constexpr DWORD movementQuest = 2;
constexpr DWORD cameraQuest = 3;

class TutorialSettingsCommand;

class CGP_Tutorial455 final : public CGameProgress, private RF455TutorialIntroCameraHost,
                              private RF455TutorialBoardHost, private RF455TutorialDistanceHost,
                              private RF455TutorialOrbitHost {
    friend class TutorialSettingsCommand;
    enum class Phase { Intro, Welcome, Briefing, LessonBoundary, Leaving, Selecting, Zone, Failed };
    RF455TutorialIntro intro;
    RF455TutorialBoardShared boardState;
    RF455TutorialRuntime runtime;
    RF455TutorialBriefingWindow briefing;
    CTutorialBoard board{runtime, *this, boardState, &briefing};
    CGUIOptionWindow options;
    Phase phase = Phase::Intro;
    bool skipIntro = false;
    bool inputBlocked = false;
    bool uiInstalled = false;
    bool optionsInstalled = false;
    bool welcomeAccepted = false;
    bool cursorDispatch = false;
    struct {
        bool active = false;
        bool pressed = false;
        float x = 0, y = 0;
        POINT target{};
        BYTE button = 0;
    } cursor;
    DWORD selectStarted = 0;
    DWORD savedCameraFlags = 0;
    DWORD lastGaitChange = 0;
    bool gaitChanged = false;
    bool pathReady = false;
    bool practiceClick = false;
    float savedCameraHeight = 0;
    BOOL savedCameraInterpolation = TRUE;
    BOOL savedCameraKeyboardRotation = FALSE;
    bool savedScreenVisible = true;
    bool savedMouseVisible = true;
    Vector3f cameraPosition{};
    RF455TutorialVector previousOrbit{};
    struct {
        bool active = false;
        LONG x = 0, y = 0;
        float elevation = 0, azimuth = 0;
    } cameraDrag;

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
    bool boardBusy() override { return board.busy() || _IsOpenedDialogBox(nullptr, leaveDialog); }
    void resetCursorButton() override {}
    void questRefreshed() override { board.questRefreshed(); }
    void scriptCompleted() override;
    void message(std::uint8_t, const RF455TutorialMessage*, std::uint16_t) override;
    RF455TutorialWaitState waitState(std::uint32_t) override;
    float avatarX() override { return _GetAvatar()->GetPosX(); }
    float avatarY() override { return _GetAvatar()->GetPosY(); }
    float avatarZ() override { return _GetAvatar()->GetPosZ(); }
    float avatarYaw() override { return _GetAvatar()->GetRotY(); }
    void createAvatarPath(const RF455TutorialVector&) override;
    void turnAvatarToward(RF455TutorialVector&, bool interpolate, float) override;
    void avatarState(std::uint32_t action, bool checkDuplicate) override;
    void avatarToggle(bool run, bool force) override;
    void setCameraOrbit(const RF455TutorialVector&, bool dirty) override;
    void animateCameraOrbit(const RF455TutorialVector& relative) override;
    RF455TutorialVector cameraOrbit() const;
    void cameraFromMouse();
    void advanceCamera();
    bool movementInputEnabled();
    void moveFromMouse();
    void advanceAvatar();
    void advanceLesson();
    void fail(const char* message);
    void openOptions();
    bool applyOption(UINT message, WPARAM value);
    POINT settingsPoint(DWORD reference);
    void startCursor(POINT target, BYTE button);
    void advanceCursor();
    void cancelCursor();
    void sendCursor(UINT message, WPARAM flags, POINT position);
public:
    ~CGP_Tutorial455() override { Destroy(); }
    BOOL Create() override;
    BOOL Destroy() override;
    HRESULT RestoreDeviceObjects() override;
    HRESULT InvalidateDeviceObjects() override { return S_OK; }
    LRESULT MsgProc(HWND, UINT, WPARAM, LPARAM) override;
    void Dialog(WORD id, DWORD result);
};

template<class Value>
Value commandField(const RF455TutorialInstruction& instruction, std::size_t offset)
{
    Value value;
    std::memcpy(&value, instruction.fixed.data() + offset, sizeof(value));
    return value;
}

class TutorialSettingsCommand final : public RF455TutorialProcessor {
    CGP_Tutorial455& stage;
    const RF455TutorialInstruction command;
    bool start(RF455TutorialHost&, RF455TutorialContext&) override;
    bool update(RF455TutorialHost&, RF455TutorialContext&) override { return !stage.cursor.active; }
    void finish(RF455TutorialHost&, RF455TutorialContext&) override {}
public:
    TutorialSettingsCommand(CGP_Tutorial455& stage, const RF455TutorialInstruction& command)
        : RF455TutorialProcessor(command.dataType, command.id), stage(stage), command(command) {}
};

class TutorialStageFactory final : public RF455TutorialFactory {
    RF455TutorialBasicFactory basic;
    CGP_Tutorial455& stage;
    RF455TutorialDistanceHost& movement;
    RF455TutorialOrbitHost& camera;
public:
    TutorialStageFactory(CGP_Tutorial455& stage, RF455TutorialDistanceHost& movement, RF455TutorialOrbitHost& camera)
        : stage(stage), movement(movement), camera(camera) {}
    std::unique_ptr<RF455TutorialProcessor> create(const RF455TutorialInstruction& command) override;
};

std::unique_ptr<RF455TutorialProcessor> TutorialStageFactory::create(const RF455TutorialInstruction& command)
{
    if (command.selector != command.dataType) return nullptr;
    const auto& data = command.fixed;
    switch (command.selector) {
    case 0: case 1: case 2: case 4:
        return basic.create(command);
    case 5:
        if (data.size() == 12 && (data[6] == 1 ||
            (data[6] == 0 && (commandField<DWORD>(command, 8) == 0 || commandField<DWORD>(command, 8) == 3)) ||
            (data[6] == 2 && commandField<DWORD>(command, 8) == 5)))
            return basic.create(command);
        break;
    case 6: case 7: case 8:
        if (data.size() == 20 && (command.selector != 8 || data[6] <= 1))
            return RF455_CreateTutorialDistanceCommand(command, movement);
        break;
    case 13:
        if (data.size() == 20 && std::isfinite(commandField<float>(command, 12)))
            return std::make_unique<TutorialSettingsCommand>(stage, command);
        break;
    case 14: case 15: case 16:
        if (data.size() == 20 && std::isfinite(commandField<float>(command, 8)) &&
            std::isfinite(commandField<float>(command, 12)) && std::isfinite(commandField<float>(command, 16)))
            return RF455_CreateTutorialOrbitCommand(command, movement, camera);
        break;
    case 19: case 21:
        if (data.size() == 8 && data[6] == 27) return std::make_unique<TutorialSettingsCommand>(stage, command);
        break;
    case 27:
        if (data.size() == 20 && data[14] == 1 && commandField<DWORD>(command, 16) == 0xffffffff &&
            commandField<SHORT>(command, 6) == -1 && commandField<SHORT>(command, 8) == -1)
            return std::make_unique<TutorialSettingsCommand>(stage, command);
        break;
    case 29:
        if (data.size() == 20 && commandField<DWORD>(command, 16) <= 1)
            return std::make_unique<TutorialSettingsCommand>(stage, command);
        break;
    case 32:
        if (data.size() == 20 && data[14] == 0 && data[15] == 27) {
            const DWORD reference = commandField<DWORD>(command, 16);
            if (reference == 0xffffffff || (LOWORD(reference) == 0 && HIWORD(reference) < 3) ||
                (LOWORD(reference) == 1 && HIWORD(reference) < 6) ||
                (LOWORD(reference) == 2 && HIWORD(reference) < 6))
                return std::make_unique<TutorialSettingsCommand>(stage, command);
        }
        break;
    }
    return nullptr;
}

bool TutorialSettingsCommand::start(RF455TutorialHost&, RF455TutorialContext&)
{
    switch (type) {
    case 13: _GetAvatar()->SetRotY(commandField<float>(command, 12), TRUE); break;
    case 19: stage.openOptions(); break;
    case 21:
        stage.options.Close();
        RF455_ObserveProtocol("tutorial-options-closed", 27, 0, 0);
        break;
    case 27: stage.startCursor({-1, -1}, 1); break;
    case 29: stage.inputBlocked = commandField<DWORD>(command, 16) == 0; break;
    case 32: stage.startCursor(stage.settingsPoint(commandField<DWORD>(command, 16)), 0); return true;
    }
    flags |= 4;
    return true;
}

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
    savedCameraHeight = _GetCamera()->GetAddY();
    savedCameraInterpolation = _GetCamera()->IsCameraInterpolation();
    savedCameraKeyboardRotation = _GetCamera()->IsRotatedByKeyboard();
    // Login releases its sprite set before this stage is created. Its child
    // windows must be detached before drawing the new scene and dialogs.
    screen->SetCapture455(nullptr);
    screen->RemoveAll();
    if (!LoadData()) {
        fail("Tutorial map could not be loaded.");
        return FALSE;
    }
    static constexpr float spawn[][3] = {{2466, 277, -1129}, {2491, 491, -3978}, {-4295, -296, 165}};
    auto* avatar = _GetAvatar();
    RF455PlayerMoveRates rates;
    if (!_GetCharDataMgr()->Tables455().playerMoveRates(avatar->GetDTIndex(), rates)) {
        fail("Tutorial player movement data could not be loaded.");
        return FALSE;
    }
    const auto& start = spawn[avatar->GetRace() / 2];
    avatar->SetPosition(start[0], start[1], start[2], TRUE, TRUE);
    avatar->SetSpeed(CMM_MOVE_WALK, CHAR_SPEED_DEFAULT * rates.walk);
    avatar->SetSpeed(CMM_MOVE_RUN, CHAR_SPEED_DEFAULT * rates.run);
    avatar->SetLightColor(ID_INVALID);
    avatar->Disable(ROSF_RENDER_ALPHA);
    avatar->SetAction(CAI_MOVE_STOP, TRUE);
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
        cancelCursor();
        releaseUiCapture();
        _CloseDialogBox(nullptr, welcomeDialog);
        _CloseDialogBox(nullptr, leaveDialog);
        _GetUIScreen()->Remove(&briefing.window());
        if (optionsInstalled) {
            _GetUIScreen()->Remove(&options);
            optionsInstalled = false;
        }
        _GetCamera()->SetAddY(savedCameraHeight);
        _GetCamera()->SetState(CAM_STOP);
        _GetCamera()->SetCameraInterpolation(savedCameraInterpolation);
        _GetCamera()->SetRotatedByKeyboard(savedCameraKeyboardRotation);
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
    RF455TutorialScript script;
    if (!RF455_LoadTutorialScript(path.c_str(), script) || script.quests.size() <= cameraQuest ||
        std::memcmp(script.quests[0].name.data(), "TutorialStart", sizeof("TutorialStart")) ||
        std::memcmp(script.quests[settingsQuest].name.data(), "TutorialBegin", sizeof("TutorialBegin")) ||
        std::memcmp(script.quests[movementQuest].name.data(), "TutorialMove", sizeof("TutorialMove")) ||
        std::memcmp(script.quests[cameraQuest].name.data(), "TutorialCamera", sizeof("TutorialCamera"))) {
        fail("Tutorial script could not be loaded.");
        return;
    }
    // Each later quest is attached once its live providers have been verified.
    script.quests.resize(cameraQuest + 1);
    TutorialStageFactory factory(*this, *this, *this);
    RF455TutorialUnsupported unsupported;
    if (!runtime.prepare(script, factory, &unsupported) || !runtime.refresh(*this)) {
        RF455_ObserveProtocol("tutorial-unsupported", static_cast<DWORD>(unsupported.quest),
                              static_cast<DWORD>(unsupported.instruction), unsupported.selector);
        fail("Tutorial lessons could not be loaded.");
        return;
    }
    phase = Phase::Welcome;
    RF455_ObserveProtocol("tutorial-welcome", race, static_cast<unsigned>(type), 0);
}

void CGP_Tutorial455::message(std::uint8_t type, const RF455TutorialMessage* content, std::uint16_t reference)
{
    if (!board.message(type, content, reference)) {
        fail("Tutorial briefing could not be opened.");
        return;
    }
    if (type <= 1) {
        phase = Phase::Briefing;
        const auto* quest = runtime.get();
        RF455_ObserveProtocol("tutorial-briefing", runtime.currentQuest,
                              quest ? static_cast<DWORD>(quest->next) : 0, type == 0 ? 1 : 0);
    }
}

void CGP_Tutorial455::scriptCompleted()
{
    phase = Phase::LessonBoundary;
    inputBlocked = false;
    RF455_ObserveProtocol("tutorial-camera-complete", runtime.currentQuest, 0, 0);
}

RF455TutorialVector CGP_Tutorial455::cameraOrbit() const
{
    auto* camera = _GetCamera();
    return {{camera->GetYaw(), camera->GetPitch(), camera->GetDistance()}};
}

void CGP_Tutorial455::setCameraOrbit(const RF455TutorialVector& orbit, bool dirty)
{
    auto* camera = _GetCamera();
    camera->SetYaw(orbit[0]);
    camera->SetPitch(orbit[1]);
    camera->SetDistance(orbit[2]);
    if (dirty) cameraDrag.active = false;
}

void CGP_Tutorial455::animateCameraOrbit(const RF455TutorialVector& relative)
{
    Vector3f change = {relative[0], relative[1], relative[2]};
    _GetCamera()->SetRotate(change);
}

void CGP_Tutorial455::cameraFromMouse()
{
    if (runtime.currentQuest != cameraQuest || phase != Phase::Briefing) return;
    auto* mouse = _GetUIMouseDev();
    const LONG wheel = mouse->GetZ();
    gMouse.z = 0;
    const bool allowed = !inputBlocked && !boardBusy() && g_dwGUIInputID == NONE_INPUT_ID &&
        GetForegroundWindow() == _GetUIScreen()->GetHWND();
    auto* camera = _GetCamera();
    if (allowed && mouse->IsPressed(R_BUTTON)) {
        const LONG x = mouse->GetX(), y = mouse->GetY();
        auto* screen = _GetUIScreen();
        if (!cameraDrag.active) {
            cameraDrag = {true, x, y, camera->GetYaw(), camera->GetPitch()};
        } else if (x != cameraDrag.x || y != cameraDrag.y) {
            const float elevation = cameraDrag.elevation + (y - cameraDrag.y) *
                (static_cast<float>(screen->GetSizeX()) / 1024.0f) * 0.2f;
            camera->SetYaw(std::fmax(-89.0f, std::fmin(89.0f, elevation)));
            if (x <= 40 || x >= screen->GetSizeX() - 40) {
                cameraDrag.x = x;
                cameraDrag.azimuth = camera->GetPitch();
                camera->SetPitch(cameraDrag.azimuth + (x <= 40 ? 3.0f : -3.0f));
            } else {
                camera->SetPitch(cameraDrag.azimuth + (cameraDrag.x - x) *
                    (static_cast<float>(screen->GetSizeY()) / 768.0f) * 0.15f);
            }
        }
    } else cameraDrag.active = false;
    if (allowed && wheel) {
        static constexpr float maximum[] = {250, 250, 275, 275, 290};
        const auto race = _GetAvatar()->GetRace();
        if (race < _countof(maximum))
            camera->SetDistance(std::fmax(10.0f, std::fmin(maximum[race], camera->GetDistance() - wheel * 0.07f)));
    }
}

void CGP_Tutorial455::advanceCamera()
{
    _GetCamera()->Rotate();
    const auto* quest = runtime.get();
    const auto* command = quest ? quest->current : nullptr;
    if (!command || (command->type != 15 && command->type != 16) || (command->flags & 2)) return;
    const auto orbit = cameraOrbit();
    auto& remaining = runtime.context.cameraRemaining;
    const auto reached = [&] { return remaining[0] <= 1 && remaining[1] <= 1 && remaining[2] <= 1; };
    const bool previouslyReached = reached();
    for (unsigned i = 0; i < orbit.size(); ++i)
        if (remaining[i] > 0) remaining[i] -= std::fabs(orbit[i] - previousOrbit[i]);
    previousOrbit = orbit;
    if (!previouslyReached && reached())
        RF455_ObserveProtocol("tutorial-camera-reached", command->id, command->type, 0);
}

RF455TutorialWaitState CGP_Tutorial455::waitState(std::uint32_t)
{
    RF455TutorialWaitState result;
    result.avatarByte614 = _GetAvatar()->GetWalkMode();
    return result;
}

void CGP_Tutorial455::createAvatarPath(const RF455TutorialVector& target)
{
    Vector3f position = {target[0], target[1], target[2]};
    auto* avatar = _GetAvatar();
    avatar->CreatePath(position);
    pathReady = avatar->GetTotalPathNo() > 0;
}

void CGP_Tutorial455::turnAvatarToward(RF455TutorialVector& target, bool interpolate, float)
{
    if (pathReady) _GetAvatar()->SetRotY(_GetAvatar()->GetPosition(), target.data(), interpolate);
}

void CGP_Tutorial455::avatarState(std::uint32_t action, bool checkDuplicate)
{
    if (!pathReady) {
        _GetAvatar()->SetAction(CAI_MOVE_STOP);
        RF455_ObserveProtocol("tutorial-path-rejected", practiceClick, 0, 0);
        return;
    }
    auto* avatar = _GetAvatar();
    avatar->SetAction(action, checkDuplicate);
    RF455_ObserveProtocol(practiceClick ? "tutorial-click-path" : "tutorial-demo-path",
                          avatar->GetWalkMode(), avatar->GetTotalPathNo(), 0);
}

void CGP_Tutorial455::avatarToggle(bool run, bool force)
{
    auto* avatar = _GetAvatar();
    const auto now = milliseconds();
    if (!force && gaitChanged && now - lastGaitChange < 1000) return;
    gaitChanged = true;
    lastGaitChange = now;
    // Tutorial speeds are initialized from the 455 table at stage entry.
    // The legacy player override reads an unrelated 0.7 record pointer.
    avatar->CCharacter::SetWalkMode(run ? CMM_MOVE_RUN : CMM_MOVE_WALK);
    RF455_ObserveProtocol("tutorial-move-gait", avatar->GetWalkMode(), 0, 0);
}

bool CGP_Tutorial455::movementInputEnabled()
{
    return phase == Phase::Briefing && runtime.currentQuest == movementQuest && !inputBlocked && !boardBusy();
}

void CGP_Tutorial455::moveFromMouse()
{
    auto* mouse = _GetUIMouseDev();
    if (!movementInputEnabled() || cursorDispatch || g_dwGUIInputID != NONE_INPUT_ID || !mouse->IsStroked(L_BUTTON)) return;
    const auto* quest = runtime.get();
    if (!runtime.context.operationActive || !quest || !quest->current || quest->current->type != 7) return;
    Vector3f point{};
    if (!_GetLevel()->GetPointFromScreenRay(mouse->GetX(), mouse->GetY(), &point)) return;
    RF455TutorialVector target{{point[0], point[1], point[2]}};
    practiceClick = true;
    createAvatarPath(target);
    turnAvatarToward(target, true, 12.0f);
    avatarState(CAI_MOVE_MOVING, true);
    practiceClick = false;
}

void CGP_Tutorial455::advanceAvatar()
{
    auto* avatar = _GetAvatar();
    const RF455TutorialVector before{{avatarX(), avatarY(), avatarZ()}};
    avatar->AdvanceLocalMovement455();
    const auto* quest = runtime.get();
    const auto* command = quest ? quest->current : nullptr;
    if (runtime.context.operationActive && command && (command->type == 6 || command->type == 7)) {
        const float moved = RF455_TutorialDistanceXZ(before, {{avatarX(), avatarY(), avatarZ()}});
        const float previous = runtime.context.remainingDistance;
        runtime.context.remainingDistance -= moved;
        if (previous > 1.0f && runtime.context.remainingDistance <= 1.0f)
            RF455_ObserveProtocol("tutorial-move-distance", command->id, command->type, avatar->GetWalkMode());
    }
    avatar->Animation();
}

void CGP_Tutorial455::advanceLesson()
{
    board.FrameMove();
    advanceCursor();
    if (welcomeAccepted) runtime.context.input = 0;
    const DWORD questIndex = runtime.currentQuest;
    const auto* quest = runtime.get();
    const auto* previous = quest ? quest->current : nullptr;
    const auto step = runtime.step(*this);
    if (step == RF455TutorialStep::QuestAdvanced) {
        welcomeAccepted = false;
        if (questIndex == settingsQuest)
            RF455_ObserveProtocol("tutorial-settings-complete", runtime.currentQuest, 0, 0);
        if (questIndex == movementQuest)
            RF455_ObserveProtocol("tutorial-move-complete", runtime.currentQuest, 0, 0);
    }
    const auto* current = quest ? quest->current : nullptr;
    if (current && current != previous && current->type == 7)
        RF455_ObserveProtocol("tutorial-move-practice", current->id, _GetAvatar()->GetWalkMode(), 0);
    if (current && current != previous && (current->type == 15 || current->type == 16)) {
        previousOrbit = cameraOrbit();
        RF455_ObserveProtocol("tutorial-camera-command", current->id, current->type, 0);
    }
}

void CGP_Tutorial455::openOptions()
{
    auto* screen = _GetUIScreen();
    if (!optionsInstalled) {
        options.Init();
        options.SetID(UII_OPTION_WINDOW);
        options.SetActions455({});
        options.SetLogoutRestricted455(TRUE);
        options.SetPos((screen->GetSizeX() - options.GetSizeX()) / 2, 0);
        options.SetSoundOption(CGUIOptionWindow::Effect_Snd, GetGlobalWavVolume());
        options.SetSoundOption(CGUIOptionWindow::BGM, GetGlobalMusicVolume());
        options.SetGraphicOption(CGUIOptionWindow::Gamma, GetR3State()->mGamma);
        options.SetGraphicOption(CGUIOptionWindow::SeeDist, _GetCharMgr()->GetVisualFieldAdjustmentLevel());
        const int lighting = GetR3State()->mDynamicLight;
        options.SetGraphicOption(CGUIOptionWindow::DynamicLighting, lighting >= 10 ? 3 : lighting / 3);
        const int shadow = GetR3State()->mShadowDetail;
        options.SetGraphicOption(CGUIOptionWindow::Shadow, shadow == -1 ? 3 : shadow == 10 ? 2 : shadow);
        screen->Add(&options);
        optionsInstalled = true;
    }
    options.Open();
    RF455_ObserveProtocol("tutorial-options-open", options.GetSizeX(), options.GetSizeY(), 0);
}

bool CGP_Tutorial455::applyOption(UINT message, WPARAM value)
{
    switch (message) {
    case WM_OPTION_ADJUST_EFFECT_SOUND: SetGlobalWavVolume(options.GetSoundOption(CGUIOptionWindow::Effect_Snd)); break;
    case WM_OPTION_ADJUST_BGM_SOUND: SetGlobalMusicVolume(options.GetSoundOption(CGUIOptionWindow::BGM)); break;
    case WM_OPTION_ADJUST_GAMMA: SetGamma(0.8f + static_cast<float>(value) / 10); break;
    case WM_OPTION_ADJUST_DYNAMIC_LIGHTING: {
        static constexpr int levels[] = {0, 3, 6, 10};
        if (value < _countof(levels)) GetR3State()->mDynamicLight = levels[value];
        break;
    }
    case WM_OPTION_ADJUST_SHADOW: {
        static constexpr int levels[] = {0, 1, 10, -1};
        if (value < _countof(levels)) GetR3State()->mShadowDetail = levels[value];
        break;
    }
    default: return false;
    }
    RF455_ObserveProtocol("tutorial-option-adjusted", message, static_cast<DWORD>(value), 0);
    return true;
}

POINT CGP_Tutorial455::settingsPoint(DWORD reference)
{
    CGUIObject* object = &options;
    if (reference != 0xffffffff) {
        const unsigned index = HIWORD(reference);
        switch (LOWORD(reference)) {
        case 0: object = &options.Sound455(index); break;
        case 1: object = &options.Graphic455(index); break;
        case 2: object = &options.Etc455(index); break;
        }
    }
    return {object->GetPosX() + object->GetSizeX() / 2, object->GetPosY() + object->GetSizeY() / 2};
}

void CGP_Tutorial455::sendCursor(UINT message, WPARAM flags, POINT position)
{
    const HWND window = _GetUIScreen()->GetHWND();
    cursorDispatch = true;
    SendMessage(window, message, flags, MAKELPARAM(position.x, position.y));
    cursorDispatch = false;
}

void CGP_Tutorial455::startCursor(POINT target, BYTE button)
{
    auto* mouse = _GetUIScreen()->GetMouse();
    const POINT origin{mouse->GetPosX(), mouse->GetPosY()};
    const bool pressed = button == 1 && GetForegroundWindow() == _GetUIScreen()->GetHWND();
    cursor = {true, pressed, static_cast<float>(origin.x), static_cast<float>(origin.y), target, button};
    if (pressed) sendCursor(WM_LBUTTONDOWN, MK_LBUTTON, origin);
}

void CGP_Tutorial455::advanceCursor()
{
    if (!cursor.active || boardBusy()) return;
    const float dx = cursor.target.x - cursor.x;
    const float dy = cursor.target.y - cursor.y;
    const float distance = std::sqrt(dx * dx + dy * dy);
    const auto width = _GetUIScreen()->GetSizeX();
    const float step = R3GetLoopTime() * (width <= 800 ? 300.0f : width <= 1024 ? 350.0f : 400.0f);
    const bool validPoint = cursor.target.x >= 0 && cursor.target.y >= 0;
    const bool reached = !validPoint || distance <= step || distance == 0;
    if (validPoint) {
        cursor.x = reached ? static_cast<float>(cursor.target.x) : cursor.x + dx * step / distance;
        cursor.y = reached ? static_cast<float>(cursor.target.y) : cursor.y + dy * step / distance;
        const POINT point{static_cast<LONG>(cursor.x), static_cast<LONG>(cursor.y)};
        POINT screenPoint = point;
        const HWND window = _GetUIScreen()->GetHWND();
        if (GetForegroundWindow() == window && ClientToScreen(window, &screenPoint)) {
            SetCursorPos(screenPoint.x, screenPoint.y);
            sendCursor(WM_MOUSEMOVE, cursor.button == 1 ? MK_LBUTTON : 0, point);
        }
        _GetUIScreen()->GetMouse()->SetPos(point.x, point.y);
    }
    if (reached) {
        if (validPoint) RF455_ObserveProtocol("tutorial-cursor-arrived", cursor.target.x, cursor.target.y, cursor.button);
        cancelCursor();
    }
}

void CGP_Tutorial455::cancelCursor()
{
    if (cursor.active && cursor.pressed)
        sendCursor(WM_LBUTTONUP, 0, {static_cast<LONG>(cursor.x), static_cast<LONG>(cursor.y)});
    cursor.active = false;
}

void CGP_Tutorial455::followAvatarCamera()
{
    auto* avatar = _GetAvatar();
    Vector3f target{};
    std::memcpy(target, avatar->GetPosition(), sizeof(target));
    _GetCamera()->SetPosition(target);
    static constexpr float height[] = {11, 11, 13, 13, 16.5f};
    static constexpr float firstPersonHeight[] = {15.5f, 15.5f, 17, 17, 18};
    const auto race = avatar->GetRace();
    if (race < _countof(height))
        _GetCamera()->SetAddY(_GetCamera()->GetCameraMode() == 2 ? firstPersonHeight[race] : height[race]);
    _GetCamera()->Render();
    _GetCamera()->GetR3Camera()->GetPos(cameraPosition);
}

HRESULT CGP_Tutorial455::FrameMove()
{
    if (phase != Phase::Failed) {
        if (runtime.currentQuest == cameraQuest) advanceCamera();
        intro.frame(*this, skipIntro);
        if (intro.active()) std::memcpy(cameraPosition, position(), sizeof(cameraPosition));
        _GetLand()->GetLevel()->FrameMove();
        if (!intro.active()) advanceAvatar();
    }
    if (phase == Phase::Welcome || phase == Phase::Briefing) advanceLesson();
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
    moveFromMouse();
    cameraFromMouse();
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
        ((phase == Phase::Briefing || phase == Phase::LessonBoundary) && id == leaveDialog && result == MSG_OK)) {
        cancelCursor();
        _GetCamera()->SetState(CAM_STOP);
        _GetAvatar()->SetAction(CAI_MOVE_STOP);
        if (optionsInstalled) options.Close();
        board.requestFinish(true);
        fadeOut(0, 2, 1);
        RF455_ObserveProtocol("tutorial-leaving", RF455_SelectedCharacterSlot(), 0, 0);
    } else if (phase == Phase::Welcome && id == welcomeDialog && result == MSG_OK) welcomeAccepted = true;
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
    if ((phase == Phase::Briefing || phase == Phase::LessonBoundary) && message == WM_KEYUP && key == VK_ESCAPE &&
        !_IsOpenedDialogBox(nullptr, leaveDialog)) {
        board.openLanguageDialog(444, leaveDialog);
        return 0xffffffff;
    }
    if (phase == Phase::Briefing && message == 0x1201 && key == 38) {
        board.MsgProc(window, message, key, data);
        return 0xffffffff;
    }
    if (optionsInstalled && phase == Phase::Briefing && applyOption(message, key)) return 0xffffffff;
    if (movementInputEnabled() && message == WM_KEYDOWN && key == 'W' && !(data & (1L << 30))) {
        avatarToggle(_GetAvatar()->GetWalkMode() != CMM_MOVE_RUN, false);
        return 0xffffffff;
    }
    if (!inputBlocked || cursorDispatch || boardBusy()) _GetUIScreen()->MsgProc(window, message, key, data);
    return 0;
}
}

CGameProgress* RF455_CreateTutorialStage() { return new CGP_Tutorial455; }

void RF455_DeliverTutorialDialog(CGameProgress& stage, WORD id, DWORD result)
{
    static_cast<CGP_Tutorial455&>(stage).Dialog(id, result);
}
