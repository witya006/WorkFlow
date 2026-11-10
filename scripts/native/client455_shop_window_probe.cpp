#define main RF455_UnusedIconProbeMain
#include "client455_item_icon_probe.cpp"
#undef main

#include "gameobject/board/shopboard/cshoptradeboard.h"
#include "userinterface/uiglobal.h"

extern CSpriteMgr* g_pUiSpriteMgr;

namespace {
CGUIObject& child(CGUIContainer& owner, WORD index)
{
    auto* object = owner.GetAddedObject(index);
    check(object != nullptr, "shop child index");
    return *object;
}

void image(CGUIObject& object, BYTE id, WORD action, WORD frame)
{
    auto* info = object.GetSpriteInfo();
    check(info->pSprite == gSpriteMgr.GetTargetSprite455(id) && info->wActionNo == action &&
          info->wFrameNo == frame, "shop sprite descriptor");
}

void label(CGUIText& text, const char* expected)
{
    check(text.GetString() && expected && std::strcmp(text.GetString(), expected) == 0, "shop label");
}

void probeShop()
{
    CShopTradeBoard board;
    board.Create(IBT_SHOP, 1, 200);
    check(board.GetMaxPackNum() == 1 && board.GetMaxSocketNum455(0) == 200 && board.AddPack(0),
          "ordinary shop pack");
    board.InitWindow(UII_SHOP_WINDOW, 200, 0);
    auto& shop = static_cast<CGUIShopWindow&>(*board.GetWindow());
    check(shop.GetID() == 7 && shop.GetPosX() == 169 && shop.GetPosY() == 0 &&
          shop.GetSizeX() == 228 && shop.GetSizeY() == 453, "shop root geometry and ID");
    image(shop, 9, 0, 0);
    image(child(shop, 0), 1, 4, 0);
    label(static_cast<CGUIText&>(child(shop, 1)), RF455_GetNormalLanguagePack()->get(0x3c6));
    auto& pager = static_cast<CGUIContainer&>(child(shop, 2));
    check(pager.GetPosX() == 189 && pager.GetPosY() == 223 &&
          pager.GetSizeX() == 187 && pager.GetSizeY() == 18, "pager geometry");
    auto& previous = child(pager, 0);
    auto& next = child(pager, 1);
    auto& pageLabel = static_cast<CGUIText&>(child(pager, 3));
    image(previous, 1, 6, 3);
    image(next, 1, 6, 6);
    label(pageLabel, "0 / 0");
    for (unsigned i = 0; i < 20; ++i) {
        auto& slot = static_cast<CGUISocket&>(child(shop, WORD(14 + i)));
        check(slot.IsEmpty() && slot.GetPosX() == 190 + 38 * LONG(i % 5) &&
              slot.GetPosY() == 64 + 38 * LONG(i / 5) && slot.GetSizeX() == 34 && slot.GetSizeY() == 34,
              "shop grid");
    }
    shop.SetShopType(CGUIShopWindow::Weapon);
    shop.SetTradeMode(CGUIShopWindow::Buy_Mode);
    auto& buy = child(shop, 35);
    auto& sell = child(shop, 36);
    image(buy, 9, 0, 1);
    image(sell, 9, 0, 2);
    check(buy.GetPosX() == 186 && sell.GetPosX() == 288 && buy.GetPosY() == 31 &&
          buy.GetSizeX() == 92 && buy.GetSizeY() == 22, "shop tabs");

    shop.SetDalant(123456789012LL);
    shop.SetGold(-12345678901LL);
    shop.SetPvp455(4294967295UL);
    shop.SetPoints455(98765);
    label(static_cast<CGUIText&>(child(shop, 4)), "123,456,789,012");
    label(static_cast<CGUIText&>(child(shop, 5)), "-12,345,678,901");
    label(static_cast<CGUIText&>(child(shop, 6)), "4,294,967,295");
    label(static_cast<CGUIText&>(child(shop, 7)), "98,765");

    shop.Show(TRUE);
    auto draw = [&] { check(shop.Draw(), "shop frame"); };
    check(capture(draw, "shop-empty.bgra") > 20000, "visible empty shop");
    for (DWORD i = 0; i < 21; ++i) {
        UI_SHOP_ITEM item = {i, 0x00030000, i, i + 1, 1};
        check(shop.TakeInBuyItem(&item), "buy row from controlled metadata");
    }
    auto& first = static_cast<CGUISocket&>(child(shop, 14));
    auto& second = static_cast<CGUISocket&>(child(shop, 15));
    check(first.GetItem() == shop.GetBuyableItem(0) && !second.IsEmpty(), "first purchase page");
    label(pageLabel, "1 / 2");
    image(next, 1, 6, 4);
    shop.SetCurrentShopBoard(255);
    check(shop.GetCurPageNo() == 1 && first.GetItem() == shop.GetBuyableItem(20) &&
          first.GetItem()->UsesTypedIcon455() && first.GetItem()->GetSpriteInfo()->pSprite &&
          second.IsEmpty(), "last purchase page clamps with one atlas item");
    label(pageLabel, "2 / 2");
    image(previous, 1, 6, 1);
    image(next, 1, 6, 6);
    check(capture(draw, "shop-buy-last.bgra") > 20000, "visible purchase page");
    check(shop.TakeOutBuyItem(20) && !shop.TakeOutBuyItem(20) && shop.GetCurPageNo() == 0 &&
          first.GetItem() == shop.GetBuyableItem(0), "safe purchase page shrink");
    label(pageLabel, "1 / 1");

    shop.SetTradeMode(CGUIShopWindow::Sell_Mode);
    label(pageLabel, "0 / 0");
    image(buy, 9, 0, 2);
    image(sell, 9, 0, 1);
    for (DWORD i = 0; i < 21; ++i) shop.TakeInTradeItem(100 + i, 0x00030000, i, BYTE(i + 1));
    label(pageLabel, "1 / 2");
    shop.SetCurrentShopBoard(1);
    check(first.GetItem() == shop.GetTradeItemByIndex(120) && second.IsEmpty(), "last sell page");
    check(capture(draw, "shop-sell-last.bgra") > 20000, "visible sell page");
    shop.SetTradeMode(CGUIShopWindow::Repair_Mode);
    label(pageLabel, "2 / 2");
    shop.TakeOutTradeItem(120);
    label(pageLabel, "1 / 1");
    shop.ClearTradeItemList();
    label(pageLabel, "0 / 0");
    check(first.IsEmpty(), "clear detaches borrowed icon");
    _GetUIScreen()->Remove(&shop);
    shop.RemoveAll();
}
}

int main()
{
    try {
        SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX | SEM_NOOPENFILEERRORBOX);
        check(RF455_InitializeNationPaths() && RF455_InitializeLanguageData(), "language");
        InitR3Engine();
        GetR3State()->mScreenXsize = 640;
        GetR3State()->mScreenYsize = 480;
        GetR3State()->mbFullScreen = FALSE;
        ForceFullScreen();
        check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr), 0)), "device");
        check(g_MainApp.CreateNetworkMgr455(), "network owner");
        auto* oldScreen = g_pUiScreen;
        g_pUiScreen = CGUIScreen::GetSingletonPtr();
        _GetUIScreen()->SetSize(640, 480);
        g_pUiSpriteMgr = &gSpriteMgr;
        _SetUIAvatarRace(0);
        probeShop();
        g_pUiScreen = oldScreen;
        GetD3dDevice()->SetTexture(0, nullptr);
        gSpriteMgr.UnloadSpriteAll();
        R3ReleaseTextTexture();
        g_MainApp.ReleaseR3D3D();
        ReleaseR3Engine();
        FILE* out = std::fopen("result.json", "wb");
        check(out != nullptr, "result output");
        std::fputs("{\"status\":\"PASS\",\"window_id\":7,\"pack_slots\":200,\"grid_slots\":20,"
                   "\"buy_rows\":21,\"trade_rows\":21,\"GPU_frames\":3,\"real_NPC_inventory\":false,"
                   "\"transaction_tested\":false}\n", out);
        std::fclose(out);
        return 0;
    } catch (const std::exception& error) {
        std::fprintf(stderr, "Shop455: %s\n", error.what());
        return 1;
    }
}
