#define main RF455_UnusedTradeOreProbeMain
#include "client455_trade_ore_probe.cpp"
#undef main

#include "definemessage.h"
#include "userinterface/gamewindow/dungeon/guidungeon.h"
#include "userinterface/gamewindow/guiselectedcharmenu.h"
#include "userinterface/gamewindow/guiselectedcharwin.h"
#include <limits>

namespace {
void verifyTargetWindows(HWND sink)
{
    char name[] = "Target";
    CGUISelectedCharWin bar;
    bar.Init();
    bar.Show(TRUE);
    position(bar, 0, 0, 100, 8);
    image(child(bar, 0), 4, 7, 0);
    image(child(bar, 1), 4, 7, 1);
    bar.SetHPRate(0.37f);
    position(child(bar, 2), 0, 0, 37, 8);
    bar.SetAttackState();
    image(child(bar, 1), 4, 7, 2);
    image(child(bar, 2), 4, 7, 2);
    bar.SetSelectState();
    image(child(bar, 2), 4, 7, 1);
    bar.SetCharName(name);
    text(static_cast<CGUIText&>(child(bar, 3)), name);
    capture(bar, "target-overhead.bgra", 700);

    CGUISelectedMobInfoWin panel;
    panel.Init();
    panel.Init();
    panel.SetPos(0, 28);
    panel.Show(TRUE);
    check(panel.GetAddedObjectNum() == 4, "target initialization is idempotent");
    position(panel, 0, 28, 259, 64);
    image(panel, 41, 0, 1);
    panel.SetHP(0.5f);
    panel.SetHP(1.5f);
    panel.SetHP(std::numeric_limits<float>::quiet_NaN());
    panel.SetSprite();
    image(child(panel, 1), 4, 9, 1);
    position(child(panel, 1), 67, 48, 156, 8);
    position(child(panel, 3), 67, 48, 78, 8);
    panel.SetMobName(name);
    panel.SetLevel455(51);
    text(static_cast<CGUIText&>(child(panel, 0)), "51");
    text(static_cast<CGUIText&>(child(panel, 2)), name);
    capture(panel, "target-details.bgra", 10000);

    CGUISelectedCharMenu menu;
    menu.Init();
    menu.SetID(UII_PLAYER_POPUP_MENU);
    menu.Show(TRUE);
    position(menu, 0, 0, 106, 194);
    check(menu.GetAddedObjectNum() == 9, "seven player choices");
    auto* language = RF455_GetNormalLanguagePack();
    check(language && std::strcmp(static_cast<CGUIButtonEx&>(child(menu, 6)).GetLabel(), language->get(0x16b1)) == 0,
          "additional player choice is localized");
    image(child(menu, 2), 4, 8, 0);
    menu.SetPartyMenu(CGUISelectedCharMenu::Join);
    auto& party = static_cast<CGUIButtonEx&>(child(menu, 4));
    check(std::strcmp(party.GetLabel(), language->get(0x48e)) == 0 && !IS_DISABLED(party.GetState()),
          "join state and label");
    expectMouse(menu, party, MOUSE_CLICKED, sink, WM_PARTY_JOIN_OTHER_PARTY, 0);
    menu.Show(TRUE);
    capture(menu, "target-menu.bgra", 14000);
    menu.SetMenuType(CGUISelectedCharMenu::UNIT);
    position(menu, 0, 0, 106, 98);
    check(menu.GetAddedObjectNum() == 5 && IS_DISABLED(child(menu, 4).GetState()), "three unit choices");
    menu.SetMenuType(CGUISelectedCharMenu::GUARD_TOWER);
    position(menu, 0, 0, 106, 50);
    check(menu.GetAddedObjectNum() == 3, "one tower choice");

    CGUIKillingCounter counter;
    counter.Init();
    counter.Show(TRUE);
    position(counter, 0, 0, 144, 126);
    image(counter, 17, 0, 0);
    counter.SetMaxKillingNum(50);
    counter.SetCurrentKillingNum(25);
    capture(counter, "dungeon-counter.bgra", 2000);
    bar.RemoveAll();
    panel.RemoveAll();
    menu.RemoveAll();
}
}

int main()
{
    return runWindowProbe("TargetWindows455", verifyTargetWindows,
                          "{\"status\":\"PASS\",\"GPU_frames\":4,\"player_choices\":7,"
                          "\"unit_choices\":3,\"tower_choices\":1,\"window_messages\":1,\"live_targeting\":false}\n");
}
