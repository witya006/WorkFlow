#include <sstream>
#include <string>
#include <utility>
#include <vector>

#include "client455_character_rfs.h"
#include "client455_font.h"
#include "client455_fullscreen_effect.h"
#include "client455_language.h"
#include "client455_movie_state.h"
#include "client455_nation_paths.h"
#include "client455_protocol_observation.h"
#include "client455_lobby_visual.inc"

namespace {

enum class LobbyPresentation455 { Waiting, Warmed, Visible, Failed };
LobbyPresentation455 lobbyPresentation455 = LobbyPresentation455::Waiting;
bool lobbyCoverReported455 = false;
unsigned worldHudPreload455 = 0;
bool lobbyTargetPending455 = false;
DWORD lobbyTargetWaitStarted455 = 0;

// Clear the actual swap-chain buffer even after a compositor/target failure.
// This neither begins/ends a scene nor presents; the normal frame owner does so.
bool CoverLobbyBackbuffer455(IDirect3DDevice9* device)
{
    if (!device) return false;
    IDirect3DSurface9 *backbuffer = nullptr, *targets[4] = {}, *depth = nullptr;
    D3DSURFACE_DESC description{};
    D3DVIEWPORT9 viewport{};
    D3DCAPS9 caps{};
    HRESULT hr = device->GetDeviceCaps(&caps);
    if (SUCCEEDED(hr)) hr = device->GetBackBuffer(0, 0, D3DBACKBUFFER_TYPE_MONO, &backbuffer);
    if (SUCCEEDED(hr)) hr = backbuffer->GetDesc(&description);
    if (SUCCEEDED(hr)) hr = device->GetViewport(&viewport);
    const unsigned count = (std::min)(static_cast<unsigned>(caps.NumSimultaneousRTs), 4u);
    for (unsigned i = 0; i < count && SUCCEEDED(hr); ++i) {
        const HRESULT got = device->GetRenderTarget(i, &targets[i]);
        if (FAILED(got) && (i == 0 || got != D3DERR_NOTFOUND)) hr = got;
    }
    if (SUCCEEDED(hr)) {
        const HRESULT got = device->GetDepthStencilSurface(&depth);
        if (FAILED(got) && got != D3DERR_NOTFOUND) hr = got;
    }
    if (SUCCEEDED(hr)) {
        hr = device->SetDepthStencilSurface(nullptr);
        for (unsigned i = 1; i < count && SUCCEEDED(hr); ++i) hr = device->SetRenderTarget(i, nullptr);
        if (SUCCEEDED(hr)) hr = device->SetRenderTarget(0, backbuffer);
        const D3DVIEWPORT9 full = {0, 0, description.Width, description.Height, 0.f, 1.f};
        if (SUCCEEDED(hr)) hr = device->SetViewport(&full);
        if (SUCCEEDED(hr)) hr = device->Clear(0, nullptr, D3DCLEAR_TARGET, 0xff000000, 1.f, 0);
        const auto restore = [&](HRESULT result) { if (FAILED(result) && SUCCEEDED(hr)) hr = result; };
        restore(device->SetRenderTarget(0, targets[0]));
        for (unsigned i = 1; i < count; ++i) restore(device->SetRenderTarget(i, targets[i]));
        restore(device->SetDepthStencilSurface(depth));
        restore(device->SetViewport(&viewport));
    }
    if (depth) depth->Release();
    for (auto* target : targets) if (target) target->Release();
    if (backbuffer) backbuffer->Release();
    return SUCCEEDED(hr);
}

void FailLobbyPresentation455(unsigned resource, HRESULT error = E_FAIL)
{
    if (lobbyPresentation455 == LobbyPresentation455::Failed) return;
    lobbyPresentation455 = LobbyPresentation455::Failed;
    RF455_ObserveProtocol("lobby-content-failed", resource, static_cast<unsigned>(error), 0);
    // The ordinary quit dialog remains drawable over the cover. Do not spin
    // forever waiting for a synchronously rejected file to become ready.
    char message[] = "Lobby resources could not be loaded. Restore the client files and restart.";
    _GetMainApp()->RequestQuitProgram(3000, message);
}

bool AwaitLobbyBackbufferTarget455(unsigned fullscreenEffect)
{
    if (!fullscreenEffect) {
        lobbyTargetPending455 = false;
        return false;
    }
    if (!lobbyTargetPending455) {
        lobbyTargetPending455 = true;
        lobbyTargetWaitStarted455 = timeGetTime();
        RF455_ObserveProtocol("lobby-target-pending", fullscreenEffect, 0, 0);
    }
    // A stuck legacy target is an error, never a reason to reveal an unready
    // frame. This bounds failure handling only; successful loading has no delay.
    if (timeGetTime() - lobbyTargetWaitStarted455 >= 10000)
        FailLobbyPresentation455(4, D3DERR_INVALIDCALL);
    return true;
}

bool LobbyInterfaceReady455(IDirect3DTexture9* logo)
{
    D3DSURFACE_DESC description{};
    if (!logo || FAILED(logo->GetLevelDesc(0, &description)) ||
        !description.Width || !description.Height) return false;
    const struct { WORD id; DWORD action, frame; } required[] = {
        {SP_ID_MOUSE, 0, 0}, {SP_ID_COMMON, 0, 8}, {SP_ID_LOGIN, 6, 0}
    };
    for (const auto& entry : required) {
        const auto* sprite = _GetUISpriteMgr()->GetSprite(entry.id);
        if (!sprite || !sprite->IsLoaded455() || !sprite->HasFrame455(entry.action, entry.frame)) return false;
    }
    return true;
}

IDirect3DTexture9* ReadLobbyLogo455(IDirect3DDevice9* device, const char* path)
{
    if (!device) return nullptr;
    constexpr std::uint64_t maxBytes = 16u * 1024u * 1024u;
    auto* cache = RF455_GetCharacterRfsCache();
    const auto bytes = cache->ReadLooseBytes(path, maxBytes);
    IDirect3DTexture9* texture = nullptr;
    HRESULT loaded = E_FAIL;
    if (bytes.status == RF455ResourceReadStatus::Ready && bytes.bytes) {
        if (!bytes.bytes->empty())
            loaded = D3DXCreateTextureFromFileInMemory(device, bytes.bytes->data(),
                static_cast<UINT>(bytes.bytes->size()), &texture);
        if (FAILED(loaded) || !texture) cache->RemoveLooseBytes(path);
    } else if (bytes.status == RF455ResourceReadStatus::ReadError && bytes.declaredSize > maxBytes) {
        loaded = D3DXCreateTextureFromFileA(device, path, &texture);
    }
    if (SUCCEEDED(loaded)) return texture;
    if (texture) texture->Release();
    return nullptr;
}

void LoadLobbyLogo455(IDirect3DDevice9* device, IDirect3DTexture9*& logo)
{
    const bool china = RF455_GetNormalNationPaths()->nation == RF455_MapNation("China");
    const char* dds = china ? ".\\System\\titlelogocn.dds" : ".\\System\\titlelogo.dds";
    const char* tga = china ? ".\\System\\titlelogocn.tga" : ".\\System\\titlelogo.tga";
    auto* texture = ReadLobbyLogo455(device, dds);
    if (!texture) texture = ReadLobbyLogo455(device, tga);
    if (logo) logo->Release();
    logo = texture;
}

void DrawLobbyLogo455(IDirect3DTexture9* logo)
{
    D3DSURFACE_DESC image{};
    if (!logo || FAILED(logo->GetLevelDesc(0, &image)) || !image.Width || !image.Height) return;

    const auto* screen = GetR3State();
    const auto scaleAt = (std::min)(image.Width, 1600u);
    const int width = screen->mScreenXsize < scaleAt
        ? static_cast<int>(double(image.Width) * screen->mScreenXsize / scaleAt)
        : static_cast<int>(image.Width);
    const int height = static_cast<int>(image.Height) * width / static_cast<int>(image.Width);
    const int x = static_cast<int>((screen->mScreenXsize - double(width)) / 2.0);
    const int y = static_cast<int>(screen->mScreenYsize * 0.43 - height / 2);
    Draw2DTexture(x, y, x + width, y + height, 0xfeffffff, logo);
}

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
        RF455_InstallLobbyVisual(screen);
        RestoreSprite();
    }

    void Uninstall(CGUIScreen& screen)
    {
        if (IsShow()) Close();
        screen.Remove(this);
        RF455_RemoveLobbyVisual(screen);
        ClearCredits();
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
        if(key==VK_F10){RF455_OpenLobbySettings();return true;}
        if(RF455_LobbyOptions() && RF455_LobbyOptions()->IsShow()){
            if(key==VK_ESCAPE)RF455_LobbyOptions()->Close();
            return true;
        }
        if (IsShow() && key == VK_RETURN) {
            action_ = Action::Start;
            return true;
        }
        if (!credits_.empty() && (key == VK_ESCAPE || key == VK_SPACE)) {
            ClearCredits();
            SetFadeOut(0, 0, 1.0f);
            SetFadeIn(0, 1.0f, 1.0f);
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
        constexpr char path[] = "System/staff.txt";
        auto* cache = RF455_GetCharacterRfsCache();
        constexpr std::uint64_t maxBytes = 64u * 1024u;
        const auto source = cache->ReadLooseBytes(path, maxBytes);
        const auto reject = [&]() {
            cache->RemoveLooseBytes(path);
            return false;
        };
        if (source.declaredSize > maxBytes) return reject();
        if (source.status != RF455ResourceReadStatus::Ready || !source.bytes) return false;
        if (source.bytes->empty()) return reject();
        std::string data(reinterpret_cast<const char*>(source.bytes->data()), source.bytes->size());
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
                if (!append()) return reject();
                style = 0;
                text.clear();
                if (token.size() == 1) {
                    lines.push_back({-1, {}});
                } else if (token[1] >= '0' && token[1] <= '3') {
                    style = token[1] - '0';
                    text = token.substr(2);
                    for (auto& c : text) if (c == '_') c = ' ';
                } else {
                    return reject();
                }
            } else {
                if (!text.empty()) text += ' ';
                text += token;
            }
            if (text.size() > 63 || lines.size() > 700) return reject();
        }
        if (!append() || lines.empty() || lines.size() > 700) return reject();

        Close();
        credits_ = std::move(lines);
        MeasureCredits();
        creditsStart_ = R3GetTime();
        SetStateFullScreenEffect(0x80000000u);
        RF455_SetFullScreenEffectDensity(0.15f);
        RF455_SetMovieState(RF455_GetMovieState() | RF455_MOVIE_WIDE);
        return true;
    }

    bool CreditsScrolled() const { return R3GetTime() - creditsStart_ >= 3.0f; }

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

    void ClearCredits()
    {
        if (credits_.empty()) return;
        credits_.clear();
        SetStateFullScreenEffect(0);
        RF455_SetFullScreenEffectDensity(0.25f);
        RF455_SetMovieState(RF455_GetMovieState() & ~RF455_MOVIE_WIDE);
    }

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
