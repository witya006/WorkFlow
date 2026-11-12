#define main RF455_UnusedTradeOreProbeMain
#include "client455_trade_ore_probe.cpp"
#undef main

#include "gameobject/board/etcboard/cclasschangeboard.h"
#include "gameobject/board/general/cboard_etc.h"
#include "network/netmsgprocessor/itemtrade/cnetmsgprocessor_itemtrade.h"
#include "client455_linker_window.h"
#include "userinterface/gamewindow/guihotkeyboard.h"
#include "userinterface/gamewindow/guiinventorywindow.h"

extern CGUIInventoryWindow* g_pUiInventWindow;

template<class Tag, typename Tag::Type Member> struct MemberAccess455 {
    friend typename Tag::Type access(Tag) { return Member; }
};
struct QueueCreate455 { using Type = void (*)(WORD); friend Type access(QueueCreate455); };
struct QueueProcess455 { using Type = void (*)(); friend Type access(QueueProcess455); };
template struct MemberAccess455<QueueCreate455, &CGUIObject::CreateEventQueue>;
template struct MemberAccess455<QueueProcess455, &CGUIObject::EventProcess>;

namespace {
void detach(CGUIWindow& window)
{
    _GetUIScreen()->Remove(&window);
    window.RemoveAll();
}

void verifyExchange(HWND sink)
{
    static_assert(trade_msg == 12 && exchange_dalant_for_gold_request_clzo == 10 &&
                  exchange_gold_for_dalant_request_clzo == 11 && exchange_money_result_zocl == 13);
    static_assert(sizeof(_exchange_dalant_for_gold_request_clzo) == 8 &&
                  sizeof(_exchange_gold_for_dalant_request_clzo) == 8 && sizeof(_exchange_money_result_zocl) == 17);
    CNetMsgProcessor_ItemTrade messages;
    _MSG_HEADER header = {sizeof(_MSG_HEADER) + 1, {trade_msg, exchange_money_result_zocl}};
    char malformed[] = {0};
    check(!messages.AnalysisServerPacket(&header, malformed), "short success receipt rejected");

    CGUIInventoryWindow inventory;
    g_pUiInventWindow = &inventory;
    inventory.SetOwnGold(99999998);
    inventory.SetOwnDalant(5000000123LL);
    CExchangeBoard board;
    board.InitWindow(UII_EXCHANGE_WINDOW, 0, 0);
    auto& window = static_cast<CGUIExchangeWindow&>(*board.GetWindow());
    check(window.GetID() == 13, "exchange ID");
    position(window, 329, 0, 228, 419);
    position(child(window, 0), 329, 0, 228, 419);
    image(child(window, 0), 12, 0, 0);
    text(static_cast<CGUIText&>(child(window, 2)), RF455_GetNormalLanguagePack()->get(0x13c2));
    auto& confirm = child(window, 7);
    auto& slider = static_cast<CGUIScrollbarEX&>(child(window, 8));
    position(slider, 347, 353, 192, 15);
    image(slider, 1, 8, 6);
    image(slider.GetButton455(), 1, 8, 7);
    check(slider.GetTotalAmount() == 100000000 && slider.GetCurrentAmount() == 2 &&
          IS_DISABLED(confirm.GetState()), "100 million gold cap and initial button");
    window.Show(TRUE);
    slider.SetCurrentAmount(0);
    slider.SendScrollEvent(SCROLLED_UP);
    access(QueueProcess455{})();
    check(window.GetGold() == 100000000, "purchase reaches gold cap");
    check(window.GetDalant() == 4999998023LL, "purchase charges five percent fee");
    check(!IS_DISABLED(confirm.GetState()), "adjusted quote enables exchange");
    text(static_cast<CGUIText&>(child(window, 16)), "4,999,998,023");
    expectMouse(window, confirm, MOUSE_CLICKED, sink, 0x591, 0);
    expectMouse(window, child(window, 4), MOUSE_CLICKED, sink, 0x1204, 0);
    capture(window, "exchange-buy.bgra");
    slider.SetCurrentAmount(5);
    slider.SendScrollEvent(SCROLLED_DOWN);
    access(QueueProcess455{})();
    check(window.GetGold() == 99999995 && window.GetDalant() == 5000003123LL, "sale at base rate");
    slider.SetCurrentAmount(2);
    slider.SendScrollEvent(SCROLLED_UP);
    access(QueueProcess455{})();
    check(window.GetDalant() == 5000000123LL && IS_DISABLED(confirm.GetState()), "unchanged balances");
    window.SetSprite();
    image(slider.GetBottomArrow455(), 1, 8, 10);
    detach(window);
    g_pUiInventWindow = nullptr;
}

void verifyMining(HWND sink)
{
    CMiningBoard board;
    board.InitWindow(UII_MINING_WINDOW, 0, 0);
    auto& window = static_cast<CGUIMiningWindow&>(*board.GetWindow());
    check(window.GetID() == 11, "mining ID");
    position(window, 0, 0, 148, 69);
    position(child(window, 0), 6, 17, 136, 27);
    image(window, 11, 0, 0);
    image(child(window, 1), 11, 0, 2);
    for (unsigned i = 0; i < 5; ++i) position(child(window, WORD(1 + i)), 9 + 27 * i, 21, 22, 19);
    auto& button = static_cast<CGUIButtonEx&>(child(window, 7));
    image(button, 4, 8, 0);
    check(std::strcmp(button.GetLabel(), RF455_GetNormalLanguagePack()->get(0x39d)) == 0, "move mode label");
    board.SelectOre(4);
    board.SelectOre(5);
    check(!child(window, 1).GetSpriteInfo()->pSprite, "only selected ore retains its mark");
    image(child(window, 5), 11, 0, 2);
    window.SetSprite();
    image(child(window, 5), 11, 0, 2);
    window.Mining_On();
    check(std::strcmp(button.GetLabel(), RF455_GetNormalLanguagePack()->get(0x39c)) == 0, "mine mode label");
    window.Show(TRUE);
    expectMouse(window, child(window, 5), MOUSE_STROKED, sink, 0x586, 4);
    expectMouse(window, button, MOUSE_CLICKED, sink, 0x587, 0);
    capture(window, "mining-ore.bgra", 8000);
    detach(window);
}

void verifyPromotion(HWND sink)
{
    CClassChangeBoard board;
    board.InitWindow(UII_CLASS_CHANGE_WINDOW, 200, 100);
    auto& window = static_cast<CGUIClassChangeWindow&>(*board.GetWindow());
    check(window.GetID() == 36, "promotion ID");
    position(window, 200, 100, 228, 395);
    image(window, 20, 0, 0);
    auto& description = static_cast<CGUITextBoard&>(child(window, 5));
    position(description, 226, 170, 182, 100);
    BYTE classes[] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9};
    DWORD skills[] = {0, 1, 2, 3, 4, 5};
    char className[] = "Promotion sample";
    char body[] = "Class description and equipment.\nAn extra line of text.\n"
                  "Skills and role.\nFourth line.\nFifth line.\nSixth line.\nSeventh line.\nEighth line.";
    window.SetTotalClassNum(10, classes);
    window.SelectClass(9);
    image(child(window, 6), 20, 0, 1);
    position(child(window, 18), 314, 453, 45, 45);
    window.SetClassName(className);
    window.SetDescription(body);
    check(description.GetTotalLineNum() >= 8, "promotion description scrolls");
    char shortDescription[] = "Class description and equipment.\nSkills and role.";
    window.SetDescription(shortDescription);
    window.SetSkillIcon(6, skills);
    auto& sixthSkill = static_cast<CGUIItem&>(child(window, WORD(window.GetAddedObjectNum() - 1)));
    check(sixthSkill.UsesTypedIcon455(), "promotion skill icon type");
    window.Show(TRUE);
    expectMouse(window, child(window, 18), MOUSE_STROKED, sink, 0x500, 9);
    expectMouse(window, child(window, 7), MOUSE_CLICKED, sink, 0x506, 0);
    expectMouse(window, child(window, 8), MOUSE_CLICKED, sink, 0x507, 0);
    expectMouse(window, child(window, 3), MOUSE_CLICKED, sink, 0x1204, 0);
    capture(window, "class-promotion.bgra");
    window.SetTotalClassNum(0, nullptr);
    check(!child(window, 6).GetSpriteInfo()->pSprite, "cleared class selection");
    detach(window);
}

void verifyLinkerAttachment()
{
    const POINT viewport = g_pUiScreen->m_ptSize;
    g_pUiScreen->SetSize(800, viewport.y);
    CGUIHotKeyBoard keys;
    keys.Init();
    keys.SetPos(7, 500);
    CGUILinkWindow455 link;
    link.SetSize(300, 32);
    g_pUiScreen->Add(&link);
    keys.SetLinkWindow455(&link);
    check(keys.IsAddedObject(&link) && !g_pUiScreen->IsAddedObject(&link), "Linker attached once to hotkey bar");
    position(link, 219, 506, 300, 32);
    keys.SetLinkWindow455(nullptr);
    check(!keys.IsAddedObject(&link), "Linker detaches on owner release");
    g_pUiScreen->SetSize(viewport.x, viewport.y);
}
}

int main()
{
    return runWindowProbe("ServiceWindows455", [](HWND sink) {
        access(QueueCreate455{})(10);
        verifyExchange(sink);
        verifyMining(sink);
        verifyPromotion(sink);
        verifyLinkerAttachment();
    }, "{\"status\":\"PASS\",\"GPU_frames\":3,\"window_messages\":8,\"mining_ore_choices\":5,"
       "\"promotion_class_choices\":10,\"promotion_skill_icons\":6,\"currency_request_bytes\":8,"
       "\"currency_success_receipt_bytes\":17,\"single_linker_attachment\":true,\"live_transactions\":false}\n");
}
