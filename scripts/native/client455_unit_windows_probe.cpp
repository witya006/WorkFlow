#define main RF455_UnusedIconProbeMain
#include "client455_item_icon_probe.cpp"
#undef main

#include "gameobject/board/shopboard/cunittuningboard.h"
#include "userinterface/uiglobal.h"
#include "definemessage.h"

extern CSpriteMgr* g_pUiSpriteMgr;

template<class Tag, typename Tag::Type Member>
struct UnitProbeMember { friend typename Tag::Type member(Tag) { return Member; } };
struct CreateQueue { using Type = void(*)(WORD); friend Type member(CreateQueue); };
struct ProcessQueue { using Type = void(*)(); friend Type member(ProcessQueue); };
struct SendMouse { using Type = void(CGUIObject::*)(WORD); friend Type member(SendMouse); };
template struct UnitProbeMember<CreateQueue, &CGUIObject::CreateEventQueue>;
template struct UnitProbeMember<ProcessQueue, &CGUIObject::EventProcess>;
template struct UnitProbeMember<SendMouse, &CGUIObject::SendMouseEvent>;

static void send(CGUIObject& object, WORD event)
{
    (object.*member(SendMouse{}))(event);
    member(ProcessQueue{})();
}

static CGUIObject& child(CGUIContainer& owner, WORD index)
{
    auto* object = owner.GetAddedObject(index);
    check(object != nullptr, "ordinary child owner");
    return *object;
}

static void image(CGUIObject& object, unsigned id, WORD action, WORD frame)
{
    auto* info = object.GetSpriteInfo();
    check(info->pSprite && info->pSprite == gSpriteMgr.GetTargetSprite455(id) &&
          info->wActionNo == action && info->wFrameNo == frame, "actual sprite descriptor");
}

static void captureUnitWindow(CGUIWindow& window, const char* name)
{
    auto* device = GetD3dDevice();
    check(SUCCEEDED(device->Clear(0, nullptr, D3DCLEAR_TARGET, 0xff102030, 1, 0)) &&
          SUCCEEDED(device->BeginScene()), "begin window frame");
    check(window.Draw() && SUCCEEDED(device->EndScene()), "ordinary window draw");

    IDirect3DSurface9 *target = nullptr, *copy = nullptr;
    check(SUCCEEDED(device->GetRenderTarget(0, &target)), "render target");
    D3DSURFACE_DESC desc = {};
    check(SUCCEEDED(target->GetDesc(&desc)) && desc.Width == 800 && desc.Height == 600, "canvas size");
    check(SUCCEEDED(device->CreateOffscreenPlainSurface(800, 600, desc.Format, D3DPOOL_SYSTEMMEM, &copy, nullptr)) &&
          SUCCEEDED(device->GetRenderTargetData(target, copy)), "GPU readback");
    D3DLOCKED_RECT lock = {};
    check(SUCCEEDED(copy->LockRect(&lock, nullptr, D3DLOCK_READONLY)), "readback lock");
    FILE* out = std::fopen(name, "wb");
    check(out != nullptr, "frame output");
    for (unsigned y = 0; y < 600; ++y)
        check(std::fwrite(static_cast<const BYTE*>(lock.pBits) + y * lock.Pitch, 4, 800, out) == 800, "pixels");
    std::fclose(out);
    copy->UnlockRect();
    copy->Release();
    target->Release();
}

static void expectMessage(HWND window, UINT type, WPARAM id, LPARAM value)
{
    MSG message = {};
    check(PeekMessageA(&message, window, type, type, PM_REMOVE) && message.wParam == id && message.lParam == value,
          "ordinary observer HWND message");
}

static int probe()
{
    SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX | SEM_NOOPENFILEERRORBOX);
    check(RF455_InitializeNationPaths() && RF455_InitializeLanguageData(), "language");
    InitR3Engine();
    GetR3State()->mScreenXsize = 800;
    GetR3State()->mScreenYsize = 600;
    GetR3State()->mbFullScreen = FALSE;
    ForceFullScreen();
    check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr), 0)), "device");
    check(g_MainApp.CreateNetworkMgr455(), "normal network manager allocation");

    auto* device = GetD3dDevice();
    IDirect3DSurface9 *oldTarget = nullptr, *oldDepth = nullptr, *canvas = nullptr;
    check(SUCCEEDED(device->GetRenderTarget(0, &oldTarget)), "old target");
    device->GetDepthStencilSurface(&oldDepth);
    D3DSURFACE_DESC desc = {};
    oldTarget->GetDesc(&desc);
    check(SUCCEEDED(device->CreateRenderTarget(800, 600, desc.Format, D3DMULTISAMPLE_NONE, 0, FALSE, &canvas, nullptr)) &&
          SUCCEEDED(device->SetDepthStencilSurface(nullptr)) && SUCCEEDED(device->SetRenderTarget(0, canvas)), "owned canvas");
    D3DVIEWPORT9 viewport = {0, 0, 800, 600, 0, 1};
    device->SetViewport(&viewport);

    member(CreateQueue{})(256);
    auto* screen = CGUIScreen::GetSingletonPtr();
    const HWND oldWindow = screen->GetHWND();
    HWND window = CreateWindowExA(0, "STATIC", "UnitWindows455", 0, 0, 0, 0, 0, HWND_MESSAGE,
                                  nullptr, GetModuleHandleA(nullptr), nullptr);
    check(window != nullptr, "message window");
    screen->SetHWND(window);
    auto* oldSprites = g_pUiSpriteMgr;
    g_pUiSpriteMgr = &gSpriteMgr;
    const BYTE oldRace = _GetAvatarRace();
    _SetUIAvatarRace(0);
    {
        CUnitTuningBoard tuningBoard;
        tuningBoard.Create(IBT_UNIT_TUNING, 8, 200);
        tuningBoard.InitWindow(34, 300, 0);
        for (BYTE pack = 0; pack < 8; ++pack) {
            check(tuningBoard.GetMaxSocketNum455(pack) == 200 && tuningBoard.AddPack(pack) &&
                  !tuningBoard.AddPack(pack), "eight active 200-slot tuning packs");
        }
        CUnitStorehouseBoard storeBoard;
        storeBoard.Create(IBT_UNIT_STOREHOUSE, 1, 4);
        check(storeBoard.GetMaxPackNum() == 1 && storeBoard.GetMaxSocketNum455(0) == 4 &&
              storeBoard.AddPack(0) && !storeBoard.AddPack(0), "active four-slot store pack");
        storeBoard.InitWindow(35, 300, 100);

        auto& tuning = static_cast<CGUIUnitTuningWindow&>(*tuningBoard.GetWindow());
        auto& store = static_cast<CGUIUnitStoreWindow&>(*storeBoard.GetWindow());
        check(tuning.GetID() == 34 && tuning.GetPosX() == 300 && tuning.GetPosY() == 0 &&
              tuning.GetSizeX() == 228 && tuning.GetSizeY() == 571, "tuning root geometry and ID");
        check(store.GetID() == 35 && store.GetPosX() == 300 && store.GetPosY() == 100 &&
              store.GetSizeX() == 228 && store.GetSizeY() == 288 && store.GetAddedObjectNum() == 6,
              "store root geometry, ID and six children");
        image(child(tuning, 0), 18, 0, 0);
        auto& title = static_cast<CGUIText&>(child(tuning, 2));
        check(!std::strcmp(title.GetString(), RF455_GetNormalLanguagePack()->get(0x40b)), "tuning label");
        auto& storeTitle = static_cast<CGUIText&>(child(store, 2));
        check(!std::strcmp(storeTitle.GetString(), RF455_GetNormalLanguagePack()->get(0x409)), "store label");
        auto& action = child(store, 5);
        check(IS_DISABLED(action.GetState()), "store action initially disabled");
        auto& list = child(store, 4);
        check(list.GetPosX() == 307 && list.GetPosY() == 131 && list.GetSizeX() == 218 && list.GetSizeY() == 225,
              "store list position and size");

        for (BYTE i = 0; i < CGUIUnitTuningWindow::TOTAL_PARTS_TYPE_NUM; ++i) {
            auto* slot = tuning.GetParts(i);
            check(slot && slot->IsEmpty() && slot->GetSizeX() == 64, "six empty 64px parts");
        }
        for (BYTE i = 0; i < BACK_PACK_BULLET_NUM; ++i) {
            auto* slot = tuning.GetBackPackBullet(i);
            check(slot && slot->IsEmpty() && slot->GetSizeX() == 32 && IS_DISABLED(slot->GetState()),
                  "eight disabled empty backpack ammo slots");
        }
        check(tuning.GetBullet(0)->GetSizeX() == 64 && IS_DISABLED(tuning.GetBullet(1)->GetState()),
              "two large ammo slots, disabled shoulder");
        tuning.Show(TRUE);
        captureUnitWindow(tuning, "unit-parts.bgra");

        send(child(tuning, 4), MOUSE_CLICKED);
        expectMessage(window, 0x1204, 34, 0);
        send(*tuning.GetMainFrameKey(), MOUSE_STROKED);
        expectMessage(window, 0x538, 34, 0);
        send(child(tuning, 30), MOUSE_STROKED);
        send(*tuning.GetBullet(0), MOUSE_STROKED);
        expectMessage(window, 0x504, 34, UI_MOUSE_MSG(1, 0, 1, 1).m_dwData);
        captureUnitWindow(tuning, "unit-ammo.bgra");

        store.Show(TRUE);
        captureUnitWindow(store, "unit-store.bgra");
        screen->Remove(&tuning);
        screen->Remove(&store);
        tuning.RemoveAll();
        store.RemoveAll();
    }
    _SetUIAvatarRace(oldRace);
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
    FILE* out = std::fopen("result.json", "wb");
    check(out != nullptr, "result output");
    std::fprintf(out, "{\"status\":\"PASS\",\"GPU_frames\":3,\"tuning_packs\":8,\"tuning_pack_slots\":200,"
                      "\"store_pack_slots\":4,\"observer_messages\":3,\"store_rows_exercised\":false,\"unit_gameplay\":false}\n");
    std::fclose(out);
    return 0;
}

int main()
{
    try { return probe(); }
    catch (const std::exception& error) {
        std::fprintf(stderr, "UnitWindows455: %s\n", error.what());
        return 1;
    }
}
