#pragma once
#include <windows.h>
#include "gameobject/board/common/cboard.h"
#include "client455_tutorial_runtime.h"
#include <array>

class CGUIWindow;

// Source-owned view of 455's two-row keyboard guide. It is not an object overlay.
struct RF455TutorialKeyGuide {
    bool visible = false;
    std::uint8_t count = 0;
    std::array<std::array<std::uint8_t, 2>, 2> rows{{{{255, 255}}, {{255, 255}}}};
};
RF455TutorialKeyGuide RF455_TutorialKeyGuide(std::uint16_t reference);
bool RF455_JoinTutorialModalText(const RF455TutorialMessage&, std::array<unsigned char, 1024>&);

// The original rich window has animated/paged text, portraits and key images.
// Those consumers must be ported; a generic legacy window is not a substitute.
class RF455TutorialBriefingView {
public:
    virtual ~RF455TutorialBriefingView() = default;
    virtual CGUIWindow& window() = 0;
    virtual void setAutoSize(bool) = 0;
    virtual bool showRichMessage(const RF455TutorialMessage&, bool closeAllowed) = 0;
    virtual bool showKeyGuide(const RF455TutorialKeyGuide&) = 0;
};

// Required Avatar/current-stage providers. No production provider is registered
// until the real Tutorial/Avatar lifecycle and local dispatcher are recovered.
class RF455TutorialBoardHost {
public:
    virtual ~RF455TutorialBoardHost() = default;
    virtual bool skipTutorial() = 0;
    virtual void setSkipTutorial(std::uint32_t) = 0;
    virtual std::uint32_t milliseconds() = 0;
    virtual void releaseUiCapture() = 0;
    virtual void stageVirtual52() = 0;
    virtual void setStageInput(std::uint32_t) = 0;
    virtual void setAvatarStage(std::uint8_t) = 0;
    // Target 56BAE0 sends group1/op17 with an uninitialized one-byte payload.
    // This notification does NOT invent that byte or send a network packet.
    virtual void reportProgressRequested() = 0;
};

// These target globals are shared by board instances and survive InitWindow.
struct RF455TutorialBoardShared {
    std::int32_t quitCooldown = 0;
    bool quitRequested = false;
    bool reportClockInitialized = false;
    std::uint32_t reportTime = 0;
};

class CTutorialBoard final : public CBaseBoard {
public:
    static constexpr WORD MissionDialog = 0x6002;
    CTutorialBoard(RF455TutorialRuntime&, RF455TutorialBoardHost&, RF455TutorialBoardShared&,
                  RF455TutorialBriefingView* = nullptr);
    void InitWindow(DWORD id, int x, int y) override;
    void FrameMove() override;
    LRESULT MsgProc(HWND, UINT, WPARAM, LPARAM) override;
    // False means a missing dependency/unsupported unsafe domain, not success.
    bool message(std::uint8_t type, const RF455TutorialMessage*, std::uint16_t reference);
    bool startScript(const char* folder, std::uint8_t race, std::uint8_t classIndex,
                     RF455TutorialFactory&, RF455TutorialHost&);
    void requestFinish(bool force);
    bool ready() const {return m_ready;}
    bool busy() const {return m_busy;}
    bool closeBlocked() const {return m_closeBlocked;}
    void questRefreshed() {m_ready = true;}
    // Actual modal GUI consumer, with the 455 IDs/style/duration/alpha. The
    // inherited legacy message-box rendering/input remains an explicit M6 gap.
    void openLanguageDialog(std::uint32_t languageIndex, std::uint16_t id);
private:
    void openModal(const char*, std::uint16_t id, std::uint16_t style);
    RF455TutorialRuntime& m_runtime;
    RF455TutorialBoardHost& m_host;
    RF455TutorialBoardShared& m_shared;
    RF455TutorialBriefingView* m_briefing;
    bool m_ready = true, m_closeBlocked = false, m_busy = false;
};
