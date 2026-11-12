#include "client455_tutorial_board.h"
#include "client455_language.h"
#include "userinterface/guicontroller/guiscreen.h"
#include "userinterface/guicontroller/guimessagebox.h"
#include <mbstring.h>
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <string>

extern CGUIScreen* g_pUiScreen;

RF455TutorialKeyGuide RF455_TutorialKeyGuide(std::uint16_t reference) {
    RF455TutorialKeyGuide guide;
    if (reference == 0xffff) return guide;
    guide.visible = true;
    const auto first = static_cast<std::uint8_t>(reference);
    const auto second = static_cast<std::uint8_t>(reference >> 8);
    if (first == 17) {
        guide.count = 2;
        guide.rows[0] = {{second, 255}};
        guide.rows[1] = {{first, second}};
    } else {
        guide.count = 1;
        guide.rows[0] = {{first, second}};
    }
    return guide;
}

bool RF455_JoinTutorialModalText(const RF455TutorialMessage& message,
                                std::array<unsigned char, 1024>& output) {
    if (message.texts.size() > 255) return false;
    std::size_t total = 0;
    for (const auto& text : message.texts) {
        if (text.bytes.size() > 65535 || text.bytes.size() > 1023 - total) return false;
        total += text.bytes.size();
    }
    std::array<unsigned char, 1024> joined{};
    std::size_t at = 0;
    for (const auto& text : message.texts) {
        // 40B1D0 is _mbsnbcpy, not memcpy/strcat. An embedded NUL pads this
        // segment; the next segment starts at its serialized byte length.
        auto source = text.bytes;
        source.push_back(0);
        _mbsnbcpy(joined.data() + at, source.data(), text.bytes.size());
        at += text.bytes.size();
    }
    joined[at] = 0;
    output = joined;
    return true;
}

CTutorialBoard::CTutorialBoard(RF455TutorialRuntime& runtime, RF455TutorialBoardHost& host,
                               RF455TutorialBoardShared& shared, RF455TutorialBriefingView* briefing)
    : m_runtime(runtime), m_host(host), m_shared(shared), m_briefing(briefing) {}

void CTutorialBoard::InitWindow(DWORD id, int x, int y) {
    if (!m_briefing) throw std::logic_error("455 CGUIBriefingWindow provider is missing");
    m_uiWindow = &m_briefing->window();
    m_briefing->setAutoSize(false);
    m_uiWindow->Init();
    m_uiWindow->SetID(id);
    // Target CBaseBoard supports -3=far edge,-2=origin,-1=center independently.
    // Screen integer sizes are the supported normal-port screen domain here.
    auto* screen = g_pUiScreen;
    if (!screen) throw std::logic_error("455 Tutorial requires a UI screen");
    auto align = [](int position, int extent, int size) {
        if (position == -3) return extent - size;
        if (position == -2) return 0;
        if (position == -1) return (extent - size) / 2;
        return position;
    };
    m_uiWindow->SetPos(align(x, screen->GetSizeX(), m_uiWindow->GetSizeX()),
                       align(y, screen->GetSizeY(), m_uiWindow->GetSizeY()));
    screen->Add(m_uiWindow);
    m_ready = true;
    m_closeBlocked = m_busy = false;
}

void CTutorialBoard::openModal(const char* text, std::uint16_t id, std::uint16_t style) {
    if (!g_pUiScreen) throw std::logic_error("455 Tutorial modal requires a UI screen");
    _msgbox_create_info create;
    create.pMsg = const_cast<char*>(text);
    create.dwRGBA = 0xb0ffffff;
    create.wUserDefinedID = id;
    create.wDlgStyle = style;
    create.wDurationTime = 0xffffffff;
    create.bScrollable = FALSE;
    _GUIMessageBox(&create);
}

void CTutorialBoard::openLanguageDialog(std::uint32_t languageIndex, std::uint16_t id) {
    const auto* pack = RF455_GetNormalLanguagePack();
    if (!pack || languageIndex >= pack->records.size())
        throw std::logic_error("455 Tutorial NDLanguage provider is missing");
    openModal(pack->get(languageIndex), id, 3);
}

bool CTutorialBoard::message(std::uint8_t type, const RF455TutorialMessage* content,
                             std::uint16_t reference) {
    switch (type) {
    case 0: case 1:
        if (!content || !m_briefing || !m_briefing->showRichMessage(*content, type == 1)) return false;
        m_closeBlocked = type == 0;
        return true;
    case 2: case 3: {
        if (!content) return false;
        std::array<unsigned char, 1024> text;
        if (!RF455_JoinTutorialModalText(*content, text)) return false;
        openModal(reinterpret_cast<const char*>(text.data()), type == 2 ? 0x6000 : MissionDialog,
                  type == 2 ? 3 : 4);
        return true;
    }
    case 4: return m_briefing && m_briefing->showKeyGuide(RF455_TutorialKeyGuide(reference));
    default: return true; // Target Message Start has no action for other dataType.
    }
}

bool CTutorialBoard::startScript(const char* folder, std::uint8_t race,
                                std::uint8_t classIndex, RF455TutorialFactory& factory,
                                RF455TutorialHost& runtimeHost) {
    if (m_host.skipTutorial()) return false;
    if (!folder || race / 2 >= 3 || classIndex >= 4) return false;
    static const char prefixes[] = {'b', 'c', 'a'}, suffixes[] = {'w', 'r', 'f', 's'};
    const std::string path = std::string(folder) + "\\" + prefixes[race / 2] + suffixes[classIndex] + ".scp";
    if (path.size() >= 258) return false; // Unbounded target sprintf domain remains OPEN.
    m_runtime.clear(); // The target unloads before trying the new file.
    RF455TutorialScript script;
    const bool loaded = RF455_LoadTutorialScript(path.c_str(), script) && m_runtime.prepare(script, factory);
    m_runtime.currentQuest = 0;
    if (m_runtime.refresh(runtimeHost)) questRefreshed();
    return loaded;
}

void CTutorialBoard::requestFinish(bool force) {
    if (m_runtime.finished() || !m_ready || force) {
        m_host.releaseUiCapture();
        m_host.setSkipTutorial(1);
        m_host.stageVirtual52();
        m_host.setStageInput(1);
        m_runtime.clear();
        m_host.setAvatarStage(3);
    } else {
        openLanguageDialog(444, 0x6001);
        m_ready = false;
    }
}

void CTutorialBoard::FrameMove() {
    if (m_shared.quitCooldown > 0) --m_shared.quitCooldown;
    if (m_host.skipTutorial()) return;
    if (!m_uiWindow) throw std::logic_error("455 Tutorial frame needs its briefing window");
    if (!m_uiWindow->IsShow()) m_runtime.context.input = 3;
    if (!m_shared.quitCooldown && m_shared.quitRequested && !m_busy && m_runtime.currentQuest) {
        openLanguageDialog(441, 0x6003);
        m_shared.quitRequested = false;
        m_busy = true;
        m_shared.quitCooldown = 5;
    }
}

LRESULT CTutorialBoard::MsgProc(HWND window, UINT message, WPARAM source, LPARAM value) {
    if (source != 38) return 0;
    if (!m_shared.reportClockInitialized) {
        m_shared.reportClockInitialized = true;
        m_shared.reportTime = m_host.milliseconds();
    }
    const auto now = m_host.milliseconds();
    if (std::uint32_t(now - m_shared.reportTime) > 60000) {
        m_host.reportProgressRequested();
        m_shared.reportTime = now;
    }
    if (message == 0x1400 || message == 0x1402) m_runtime.context.input = 0;
    else if (message == 0x1401) requestFinish(false);
    else if (message == 0x1403) {
        if (value == 1) requestFinish(true);
        m_busy = false;
    } else if (message == 0x1201 && m_closeBlocked) return 0;
    // The455 base uses38 as a window ID and toggles for1202. Legacy base
    // uses a different WM_CLOSING value and lacks this ID check.
    if (IsEqualWindow(static_cast<DWORD>(source))) {
        if (message == 0x1201 && value) CloseWindow();
        else if (message == 0x1202) ToggleWindow();
    }
    (void)window;
    return 0;
}
