#define main RF455_UnusedTradeOreProbeMain
#include "client455_trade_ore_probe.cpp"
#undef main

#include "gameobject/board/itemboard/citemworkboard.h"
#include "gameobject/board/itemboard/citemupgradeboard.h"
#include "definemessage.h"

namespace {
void verifyCraft(HWND sink)
{
    CItemWorkBoard board;
    board.Create(IBT_ITEM_WORK, 0, 0);
    board.InitWindow(UII_ITEM_WORKING_WINDOW, 0, 0);
    auto& window = static_cast<CGUIItemMakeWindow&>(*board.GetWindow());
    position(window, 329, 0, 228, 395);
    image(window, 14, 0, 0);
    check(window.GetID() == 15 && window.GetMakeGroup() == CGUIItemMakeWindow::None &&
          !window.GetItemListWindow(3), "craft root identity and closed groups");
    for (BYTE i = 0; i < 3; ++i)
        check(!static_cast<CGUIItemListWindow*>(window.GetItemListWindow(i))->IsCreated(), "lazy recipe panels");

    const BYTE tabs[] = {9, 5, 2};
    const unsigned titles[] = {0x3d3, 0x3d4, 0xc2};
    const char* frames[] = {"craft-weapons.bgra", "craft-armor.bgra", "craft-consumables.bgra"};
    window.Show(TRUE);
    for (BYTE group = 0; group < 3; ++group) {
        window.SetMakeGroup(static_cast<CGUIItemMakeWindow::MakeGroup>(group));
        auto& list = static_cast<CGUIItemListWindow&>(*window.GetItemListWindow(group));
        check(list.IsCreated() && list.GetID() == 15 && &child(window, 0) == &list, "actual active recipe owner");
        position(list, 329, 0, 228, 395);
        image(child(list, 0), 14, group + 1, tabs[group]);
        text(static_cast<CGUIText&>(child(window, 2)), RF455_GetNormalLanguagePack()->get(titles[group]));
        const BYTE active = tabs[group] - 1;
        expectMouse(list, child(list, tabs[group]), MOUSE_STROKED, sink, 0x583, 0);
        image(child(list, tabs[group]), 14, group + 1, active);
        auto& pager = static_cast<CGUIContainer&>(child(list, 21 + tabs[group]));
        auto& pageText = static_cast<CGUIText&>(child(pager, 3));
        position(pager, 348, 222, 187, 18);
        text(pageText, "1 / 1");
        auto& first = static_cast<CGUISocket&>(child(list, 1 + tabs[group]));
        auto& last = static_cast<CGUISocket&>(child(list, 20 + tabs[group]));
        position(first, 349, 63, 34, 34);
        position(last, 501, 177, 34, 34);
        for (BYTE slot : {BYTE(0), BYTE(19), BYTE(20), BYTE(99)})
            check(list.TakeInItem(active, slot, 0x30000, slot, 2), "controlled recipe");
        check(!list.TakeInItem(tabs[group], 0, 0x30000, 0, 1) &&
              !list.TakeInItem(active, 100, 0x30000, 0, 1), "recipe tab and slot bounds");
        text(pageText, "1 / 5");
        list.SetPage(1);
        check(first.GetItem() == list.GetItem(active, 20) && first.GetItem()->UsesTypedIcon455(),
              "page index binds the real icon");
        list.SetPage(255);
        text(pageText, "5 / 5");
        check(last.GetItem() == list.GetItem(active, 99), "last page and clamped request");
        expectMouse(list, last, MOUSE_STROKED, sink, 0x500, UI_MOUSE_MSG(active, 99, 0, 0).m_dwData);
        expectMouse(list, last, MOUSE_HOVERED, sink, 0x501, UI_MOUSE_MSG(active, 99, 0, 0).m_dwData);
        window.SelectItem(99);
        image(last, 44, 0, 0);
        window.SetSprite();
        image(last, 44, 0, 0);
        window.SetMaterialStr(0, "Ore", 3, FALSE);
        window.SetMaterialStr(1, "Ore", 5, TRUE);
        auto& line = static_cast<CGUIText&>(child(window, 7));
        check(line.GetString() && std::strncmp(line.GetString(), "Ore   3", 7) == 0 &&
              line.GetFont()->dwColor == 0xffff8b82, "localized material amount and color");
        window.EnableMake(TRUE);
        expectMouse(window, child(window, 12), MOUSE_CLICKED, sink, 0x582, 0);
        list.SetPage(0);
        window.SelectItem(0);
        capture(window, frames[group]);
        check(list.TakeOutItem(active, 99, 0) && !list.GetItem(active, 99), "recipe removal");
        text(pageText, "1 / 2");
    }
    _GetUIScreen()->Remove(&window);
    window.RemoveAll();
}

void verifyUpgrade(HWND sink)
{
    CItemUpgradeBoard board;
    board.Create(IBT_ITEM_UPGRADE, 1, MAX_UIAT_TYPE);
    board.InitWindow(UII_ITEM_UPGRADE_WINDOW, 0, 0);
    check(board.GetMaxSocketNum455(0) == 6 && board.AddPack(0), "upgrade board pack");
    auto& window = static_cast<CGUIItemUpgradeWindow&>(*board.GetWindow());
    position(window, 329, 0, 228, 395);
    check(window.GetID() == 16, "upgrade window ID");
    image(window, 15, 0, 0);
    auto& restore = child(window, 0);
    auto& upgrade = child(window, 9);
    image(restore, 1, 1, 7);
    image(upgrade, 1, 1, 7);
    position(child(window, 3), 411, 134, 64, 64);
    position(child(window, 4), 427, 53, 32, 32);
    check(window.TakeInItem(0, 0, 0x30000, 1, 1) && window.TakeInItem(0, 1, 0x30000, 3, 1) &&
          !window.TakeInItem(0, 6, 0x30000, 3, 1), "upgrade icons and bounds");
    check(window.GetItem(0, 0)->UsesTypedIcon455(), "ordinary upgrade icon");
    window.EnableUpgrade(TRUE);
    window.Show(TRUE);
    image(restore, 1, 1, 4);
    image(upgrade, 1, 1, 4);
    expectMouse(window, restore, MOUSE_CLICKED, sink, 0x4309, 0);
    expectMouse(window, upgrade, MOUSE_CLICKED, sink, 0x584, 0);
    capture(window, "upgrade-items.bgra");
    check(window.TakeOutItem(0, 0) && window.TakeOutItem(0, 1) && !window.GetItem(0, 0), "upgrade item return");
    image(restore, 1, 1, 7);
    image(upgrade, 1, 1, 7);
    _GetUIScreen()->Remove(&window);
    window.RemoveAll();
}
}

int main()
{
    return runWindowProbe("ItemWork455", [](HWND sink) { verifyCraft(sink); verifyUpgrade(sink); },
                          "{\"status\":\"PASS\",\"recipe_groups\":3,\"tabs\":[9,5,2],\"recipe_slot_capacity\":100,"
                          "\"upgrade_slots\":6,\"window_messages\":14,\"GPU_frames\":4,"
                          "\"ordinary_recipe_provider\":false,\"transactions_tested\":false}\n");
}
