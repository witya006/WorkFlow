#include <fstream>
#include <sstream>
#include <utility>
#include <vector>

#include "client455_font.h"
#include "client455_language.h"
#include "client455_protocol_observation.h"

namespace {

class LobbyMenu455 final : public CGUIWindow {
public:
    enum class Action { None, Start, Credits, Exit };

    void Install(CGUIScreen& screen, bool returningToCharacters)
    {
        if (!configured_) {
            Add(&panel_);
            panel_.SetMouseInput455(FALSE);
            for (auto& button : buttons_) {
                button.AddMouseEventHandler(this);
                Add(&button);
            }
            configured_ = true;
        }
        action_ = Action::None;
        started_ = returningToCharacters;
        screen.Add(this);
        RestoreSprite();
    }

    void Uninstall(CGUIScreen& screen)
    {
        if (IsShow()) Close();
        screen.Remove(this);
        credits_.clear();
        action_ = Action::None;
    }

    void RestoreSprite() override
    {
        auto* login = _GetUISpriteMgr()->GetSprite(SP_ID_LOGIN);
        auto* common = _GetUISpriteMgr()->GetSprite(SP_ID_COMMON);
        SPRITE_INFO panel = {login, 6, 0};
        panel_.SetSpriteInfo(&panel);

        const unsigned labelIds[] = {0x4ae, 0x4af, 0x4b0};
        for (unsigned i = 0; i < 3; ++i) {
            auto& button = buttons_[i];
            SPRITE_INFO face = {common, 0, 6};
            button.SetSpriteInfoEx(&face);
            face.wFrameNo = 7;
            button.SetSpriteInfoEx(PRESSED, &face);
            face.wFrameNo = 8;
            button.SetSpriteInfoEx(HOVERED, &face);
            const char* label = RF455_GetNormalLanguagePack()->get(labelIds[i]);
            button.SetLabel(const_cast<char*>(label));
            button.SetLabelColor(0xffb3b3b3);
            button.SetLabelHoveredColor(0xffffffff);
            button.SetSize(210, 21);
            const SIZE extent = RF455_MeasureLegacyText(label);
            button.SetLabelMetrics455(extent.cx, extent.cy);
        }
        Layout();
    }

    void Layout()
    {
        constexpr int width = 240;
        constexpr int height = 137;
        const int x = (_GetUIScreen()->GetSizeX() - width) / 2;
        const int y = (_GetUIScreen()->GetSizeY() - height) * 9 / 10;
        SetPos(x, y);
        SetSize(width, height);
        panel_.SetPos(x, y);
        panel_.SetSize(width, height);
        for (unsigned i = 0; i < 3; ++i)
            buttons_[i].SetPos(x + 15, y + 33 + 30 * i);
    }

    void MouseEvent(_mouse_event& event) override
    {
        if (!IsShow() || event.id != MOUSE_CLICKED) return;
        for (unsigned i = 0; i < 3; ++i) {
            if (event.source == &buttons_[i]) {
                const Action choices[] = {Action::Start, Action::Credits, Action::Exit};
                action_ = choices[i];
                return;
            }
        }
    }

    bool KeyDown(WPARAM key)
    {
        if (IsShow() && key == VK_RETURN) {
            action_ = Action::Start;
            return true;
        }
        if (!credits_.empty() && (key == VK_ESCAPE || key == VK_SPACE)) {
            credits_.clear();
            Open();
            RF455_ObserveProtocol("lobby-credits-close", static_cast<unsigned>(key), 0, 0);
            return true;
        }
        return false;
    }

    Action TakeAction()
    {
        const Action action = action_;
        action_ = Action::None;
        return action;
    }

    bool Started() const { return started_; }
    bool ShowingCredits() const { return !credits_.empty(); }

    void Start()
    {
        Close();
        started_ = true;
    }

    bool OpenCredits()
    {
        std::ifstream file("System/staff.txt", std::ios::binary | std::ios::ate);
        const auto size = file.tellg();
        if (size <= 0 || size > 65536) return false;
        std::string data(static_cast<std::size_t>(size), '\0');
        file.seekg(0);
        if (!file.read(&data[0], static_cast<std::streamsize>(data.size()))) return false;
        if (data.compare(0, 3, "\xef\xbb\xbf") == 0) data.erase(0, 3);

        std::istringstream input(data);
        std::vector<CreditLine> lines;
        std::string text;
        int style = 0;
        const auto append = [&]() {
            if (text.empty()) return true;
            UINT codePage = CP_UTF8;
            const int bytes = static_cast<int>(text.size());
            int length = MultiByteToWideChar(codePage, MB_ERR_INVALID_CHARS, text.data(), bytes, nullptr, 0);
            if (!length) {
                // The shipped staff.txt stores its Chinese lines in GBK.
                codePage = 936;
                length = MultiByteToWideChar(codePage, MB_ERR_INVALID_CHARS, text.data(), bytes, nullptr, 0);
            }
            if (!length) return false;
            std::wstring wide(static_cast<std::size_t>(length), L'\0');
            if (!MultiByteToWideChar(codePage, MB_ERR_INVALID_CHARS, text.data(), bytes, &wide[0], length))
                return false;
            lines.push_back({style, std::move(wide)});
            return true;
        };
        for (std::string token; input >> token;) {
            if (token.front() == '#') {
                if (!append()) return false;
                style = 0;
                text.clear();
                if (token.size() == 1) {
                    lines.push_back({-1, {}});
                } else if (token[1] >= '0' && token[1] <= '3') {
                    style = token[1] - '0';
                    text = token.substr(2);
                    for (auto& c : text) if (c == '_') c = ' ';
                } else {
                    return false;
                }
            } else {
                if (!text.empty()) text += ' ';
                text += token;
            }
            if (text.size() > 63 || lines.size() > 700) return false;
        }
        if (!append() || lines.empty() || lines.size() > 700) return false;

        Close();
        credits_ = std::move(lines);
        MeasureCredits();
        creditsStart_ = R3GetTime();
        return true;
    }

    void DrawCredits()
    {
        if (credits_.empty()) return;
        const int width = _GetUIScreen()->GetSizeX();
        const int height = _GetUIScreen()->GetSizeY();
        float y = height - (R3GetTime() - creditsStart_) * 15.0f;
        const DWORD colors[] = {0xffffffff, 0xffb2c4ea, 0xffeac9c2, 0xff00f89e};
        for (const auto& line : credits_) {
            if (line.style == -1) {
                y += 14;
                continue;
            }
            if (y > -18.0f && y < height) {
                const int center = width / 2;
                const int x = line.style == 0 ? center : line.style == 1 ? center - line.width - 10
                                                                       : center - line.width / 2;
                float pos[] = {static_cast<float>(x), y, 0.0f, 1.0f};
                RF455_DrawText(pos, line.text.c_str(), colors[line.style], CreditFlags(line.style));
            }
            if (line.style != 1) y += line.style == 0 ? 14 : 18;
        }
        if (y < -10.0f) creditsStart_ = R3GetTime();
    }

private:
    struct CreditLine { int style; std::wstring text; LONG width = 0; };

    static DWORD CreditFlags(int style) { return R3_HAN_OUTLINE | (style >= 2 ? 0x80000000 : 0); }

    void MeasureCredits()
    {
        if (credits_.empty()) return;
        const HDC dc = CreateCompatibleDC(nullptr);
        if (!dc) return;
        for (auto& line : credits_) {
            if (line.text.empty()) continue;
            const HFONT font = RF455_GetFontSnapshotFlags(CreditFlags(line.style)).font;
            if (!font) continue;
            const HGDIOBJ previous = SelectObject(dc, font);
            SIZE size{};
            if (GetTextExtentPoint32W(dc, line.text.c_str(), static_cast<int>(line.text.size()), &size))
                line.width = size.cx;
            if (previous) SelectObject(dc, previous);
        }
        DeleteDC(dc);
    }

    CGUIObject panel_;
    CGUIButtonEx buttons_[3];
    bool configured_ = false;
    bool started_ = false;
    Action action_ = Action::None;
    std::vector<CreditLine> credits_;
    float creditsStart_ = 0.0f;
};

LobbyMenu455 lobbyMenu455;

}
