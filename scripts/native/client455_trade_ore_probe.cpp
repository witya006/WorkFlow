#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "gameobject/board/shopboard/cplayertradeboard.h"
#include "gameobject/board/itemboard/coreprocboard.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "input/imeedit.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/guicontroller/guiscreen.h"
#include "userinterface/spritemgr.h"
#include "userinterface/uiglobal.h"
#include "mainapp.h"
#include "client455_language.h"
#include "client455_nation_paths.h"
#include <cstdio>
#include <cstring>
#include <stdexcept>

extern CMainApp g_MainApp;
extern CSpriteMgr* g_pUiSpriteMgr;

namespace {
void check(bool value, const char* reason)
{
    if (!value) throw std::runtime_error(reason);
}

CGUIObject& child(CGUIContainer& owner, WORD index)
{
    auto* object = owner.GetAddedObject(index);
    check(object != nullptr, "child index");
    return *object;
}

void image(CGUIObject& object, BYTE id, WORD action, WORD frame)
{
    auto* info = object.GetSpriteInfo();
    check(info->pSprite && info->pSprite == gSpriteMgr.GetTargetSprite455(id) &&
          info->wActionNo == action && info->wFrameNo == frame, "sprite descriptor");
}

void text(CGUIText& object, const char* expected)
{
    check(object.GetString() && expected && std::strcmp(object.GetString(), expected) == 0, "localized or numeric label");
}

void position(CGUIObject& object, LONG x, LONG y, LONG width, LONG height)
{
    check(object.GetPosX() == x && object.GetPosY() == y && object.GetSizeX() == width &&
          object.GetSizeY() == height, "window or control geometry");
}

void capture(CGUIWindow& window, const char* path)
{
    auto* device = GetD3dDevice();
    check(SUCCEEDED(device->Clear(0, nullptr, D3DCLEAR_TARGET, 0xff102030, 1, 0)) &&
          SUCCEEDED(device->BeginScene()), "begin frame");
    check(window.Draw() && SUCCEEDED(device->EndScene()), "window draw");
    IDirect3DSurface9 *target = nullptr, *copy = nullptr;
    check(SUCCEEDED(device->GetRenderTarget(0, &target)), "render target");
    D3DSURFACE_DESC desc = {};
    check(SUCCEEDED(target->GetDesc(&desc)) && desc.Width == 800 && desc.Height == 600, "800x600 canvas");
    check(SUCCEEDED(device->CreateOffscreenPlainSurface(800, 600, desc.Format, D3DPOOL_SYSTEMMEM, &copy, nullptr)) &&
          SUCCEEDED(device->GetRenderTargetData(target, copy)), "GPU readback");
    D3DLOCKED_RECT lock = {};
    check(SUCCEEDED(copy->LockRect(&lock, nullptr, D3DLOCK_READONLY)), "readback lock");
    FILE* out = std::fopen(path, "wb");
    check(out != nullptr, "frame output");
    unsigned visible = 0;
    for (unsigned y = 0; y < 600; ++y) {
        const auto* row = reinterpret_cast<const DWORD*>(static_cast<const BYTE*>(lock.pBits) + y * lock.Pitch);
        check(std::fwrite(row, 4, 800, out) == 800, "frame pixels");
        for (unsigned x = 0; x < 800; ++x) visible += (row[x] & 0xffffff) != 0x102030;
    }
    std::fclose(out);
    copy->UnlockRect();
    copy->Release();
    target->Release();
    check(visible > 40000, "visible window");
}

void expectMouse(CGUIWindow& window, CGUIObject& object, WORD type, HWND sink, UINT msg, LPARAM arg)
{
    _mouse_event event = {};
    event.source = &object;
    event.id = type;
    window.MouseEvent(event);
    MSG posted = {};
    check(PeekMessageA(&posted, sink, msg, msg, PM_REMOVE) && posted.wParam == window.GetID() && posted.lParam == arg,
          "ordinary observer message");
}

void probeTrade(HWND sink)
{
    CPlayerTradeBoard board;
    board.Create(IBT_PLAYER_TRADE, 1, MAX_PLAYER_TRADE_ITEM_NUM);
    check(board.GetMaxPackNum() == 1 && board.GetMaxSocketNum455(0) == 15, "15-slot trade package");
    board.InitWindow(UII_TRADE_WINDOW, 200, 0);
    auto& window = static_cast<CGUITradeWindow&>(*board.GetWindow());
    check(window.GetID() == 23, "trade ID");
    position(window, 329, 0, 228, 571);
    image(window, 16, 0, 0);
    text(static_cast<CGUIText&>(child(window, 1)), RF455_GetNormalLanguagePack()->get(0x404));
    for (unsigned i = 0; i < 15; ++i) {
        const LONG x = 350 + 38 * (i % 5), row = 38 * (i / 5);
        position(child(window, WORD(4 + 4 * i)), x, 338 + row, 34, 34);
        position(child(window, WORD(5 + 4 * i)), x + 1, 339 + row, 32, 32);
        position(child(window, WORD(6 + 4 * i)), x, 62 + row, 34, 34);
        position(child(window, WORD(7 + 4 * i)), x + 1, 63 + row, 32, 32);
    }
    auto& lock = child(window, 67);
    auto& accept = child(window, 68);
    image(lock, 16, 0, 3);
    image(accept, 1, 1, 3);
    position(child(window, 65), 362, 473, 105, 12);
    window.SetEnableSocketNum_Avatar(10);
    window.SetEnableSocketNum_Other(14);
    image(child(window, 44), 44, 1, 0);
    image(child(window, 62), 44, 1, 0);
    check(window.TakeInItem_Avatar(9, 0x30000, 9, 7) && window.GetItem_Avatar(9)->UsesTypedIcon455() &&
          !window.TakeInItem_Avatar(15, 0x30000, 1, 2), "local item and out-of-range slot");
    check(window.TakeInItem_Other(13, 0x30000, 2, 4) && !window.TakeInItem_Other(13, 0x30000, 3, 5),
          "remote slot rejects duplicate");
    window.SetAvatarDalant(123456789012LL);
    window.SetOtherGold(9876543210LL);
    check(window.GetAvatarDalant() == 123456789012LL, "64-bit offered value");
    text(static_cast<CGUIText&>(child(window, 71)), "9,876,543,210");
    window.Show(TRUE);
    capture(window, "trade-offer.bgra");
    expectMouse(window, lock, MOUSE_CLICKED, sink, 0x521, 0);
    window.SetLock_Avatar(TRUE);
    image(lock, 16, 0, 1);
    image(accept, 1, 1, 0);
    expectMouse(window, accept, MOUSE_CLICKED, sink, 0x522, 0);
    window.SetAccept_Other(TRUE);
    image(child(window, 73), 1, 1, 2);
    expectMouse(window, child(window, 2), MOUSE_CLICKED, sink, 0x1201, 1);
    capture(window, "trade-locked.bgra");
    check(window.TakeOutItem_Avatar(9) && !window.GetItem_Avatar(9) && window.TakeOutItem_Other(13),
          "visible item removal");
    _GetUIScreen()->Remove(&window);
    window.RemoveAll();
}

void probeOre()
{
    COreProcBoard board;
    board.Create(IBT_ORE_PROCESSING, 1, MAX_ORE_PROC_SOCKET);
    check(board.GetMaxPackNum() == 1 && board.GetMaxSocketNum455(0) == 40 && board.AddPack(0), "40-slot ore package");
    board.InitWindow(UII_ORE_PROC_WINDOW, 0, 0);
    auto& window = static_cast<CGUIOreProcWindow&>(*board.GetWindow());
    check(window.GetID() == 12, "ore ID");
    position(window, 329, 0, 228, 395);
    image(window, 10, 0, 0);
    text(static_cast<CGUIText&>(child(window, 1)), RF455_GetNormalLanguagePack()->get(0x3b1));
    position(*window.GetOre(), 411, 35, 64, 64);
    for (unsigned i = 0; i < 20; ++i)
        position(child(window, WORD(5 + i)), 349 + 38 * (i % 5), 204 + 38 * (i / 5), 34, 34);
    auto& process = child(window, 26);
    auto& disposal = child(window, 27);
    image(process, 1, 1, 3);
    image(disposal, 1, 1, 3);
    window.Show(TRUE);
    check(window.TakeInInputOre(0x30000, 1, 12), "ore input");
    window.SetProcPrice(9876543210LL);
    text(static_cast<CGUIText&>(child(window, 4)), "9,876,543,210");
    for (BYTE i = 0; i < 21; ++i)
        check(window.TakeInResultOre(i, 0x30000, i, BYTE(i + 1)), "ore result");
    check(!window.TakeInResultOre(40, 0x30000, 0, 1), "ore result bounds");
    text(static_cast<CGUIText&>(child(window, 30)), RF455_GetNormalLanguagePack()->get(0x3be));
    auto& scroll = static_cast<CGUIScrollbar&>(child(window, 32));
    check(scroll.GetTotalAmount() == 35 && scroll.GetCurrentAmount() == 35 &&
          window.GetItem(0, 20) != nullptr, "one scrolled ore row");
    capture(window, "ore-result.bgra");
    window.ClearResultOreSocket();
    check(IS_DISABLED(disposal.GetState()) && window.TakeOutInputOre() &&
          IS_DISABLED(process.GetState()), "ore clears result and input");
    _GetUIScreen()->Remove(&window);
    window.RemoveAll();
}
}

static int runWindowProbe(const char* name, void (*exercise)(HWND), const char* result)
{
    try {
        SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX | SEM_NOOPENFILEERRORBOX);
        check(RF455_InitializeNationPaths() && RF455_InitializeLanguageData(), "language");
        InitR3Engine();
        GetR3State()->mScreenXsize = 800;
        GetR3State()->mScreenYsize = 600;
        GetR3State()->mbFullScreen = FALSE;
        ForceFullScreen();
        check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr), 0)), "device");
        check(g_MainApp.CreateNetworkMgr455(), "network owner");
        auto* device = GetD3dDevice();
        IDirect3DSurface9 *oldTarget = nullptr, *oldDepth = nullptr, *canvas = nullptr;
        check(SUCCEEDED(device->GetRenderTarget(0, &oldTarget)), "old canvas");
        device->GetDepthStencilSurface(&oldDepth);
        D3DSURFACE_DESC desc = {};
        oldTarget->GetDesc(&desc);
        check(SUCCEEDED(device->CreateRenderTarget(800, 600, desc.Format, D3DMULTISAMPLE_NONE, 0, FALSE, &canvas, nullptr)) &&
              SUCCEEDED(device->SetDepthStencilSurface(nullptr)) && SUCCEEDED(device->SetRenderTarget(0, canvas)), "owned canvas");
        D3DVIEWPORT9 view = {0, 0, 800, 600, 0, 1};
        check(SUCCEEDED(device->SetViewport(&view)), "canvas viewport");
        g_pUiScreen = CGUIScreen::GetSingletonPtr();
        g_pUiScreen->SetSize(800, 600);
        g_pUiSpriteMgr = &gSpriteMgr;
        _SetUIAvatarRace(0);
        HWND sink = CreateWindowExA(0, "STATIC", name, 0, 0, 0, 0, 0, HWND_MESSAGE, nullptr,
                                    GetModuleHandleA(nullptr), nullptr);
        check(sink != nullptr, "message-only sink");
        g_pUiScreen->SetHWND(sink);
        exercise(sink);
        g_pUiScreen->SetHWND(nullptr);
        DestroyWindow(sink);
        device->SetTexture(0, nullptr);
        gSpriteMgr.UnloadSpriteAll();
        device->SetRenderTarget(0, oldTarget);
        device->SetDepthStencilSurface(oldDepth);
        canvas->Release();
        oldTarget->Release();
        if (oldDepth) oldDepth->Release();
        R3ReleaseTextTexture();
        g_MainApp.ReleaseR3D3D();
        ReleaseR3Engine();
        FILE* out = std::fopen("result.json", "wb");
        check(out != nullptr, "result output");
        std::fputs(result, out);
        std::fclose(out);
        return 0;
    } catch (const std::exception& error) {
        std::fprintf(stderr, "%s: %s\n", name, error.what());
        return 1;
    }
}

int main()
{
    return runWindowProbe("TradeOre455", [](HWND sink) { probeTrade(sink); probeOre(); },
                          "{\"status\":\"PASS\",\"trade_slots_per_side\":15,\"ore_rows\":21,\"ore_capacity\":40,"
                          "\"trade_messages\":3,\"GPU_frames\":3,\"trade_completed\":false,\"ore_processed\":false}\n");
}
