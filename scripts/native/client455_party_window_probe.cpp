#define main RF455_UnusedTradeOreProbeMain
#include "client455_trade_ore_probe.cpp"
#undef main

#include "definemessage.h"
#include "userinterface/gamewindow/group/guipartywindow.h"

namespace {
void assertPosted(HWND sink, UINT id, WPARAM value)
{
    MSG message = {};
    check(PeekMessageA(&message, sink, id, id, PM_REMOVE) && message.wParam == value && message.lParam == 0,
          "party observer message");
}

GROUP_MEMBER_INFO member(DWORD id, BYTE classIcon, const char* name)
{
    GROUP_MEMBER_INFO info;
    info.dwMemberID = id;
    info.byClassIcon455 = classIcon;
    std::snprintf(info.pCharName, sizeof info.pCharName, "%s", name);
    info.wLevel = 51;
    info.fHPRate = 0.5f;
    info.fFPRate = 0.75f;
    info.fSPRate = 0.25f;
    return info;
}

void verifyParty(HWND sink)
{
    static_assert(init_msg == 3 && base_download_request_clzo == 3, "455 base download request");
    CGUIPartyWindow window;
    window.Init();
    window.SetID(UII_PARTY_WINDOW);
    window.SetWindowType(UI_PMT_MEMBER);
    window.Show(TRUE);
    position(window, 0, 0, 248, 60);
    position(child(window, 0), 4, 4, 240, 18);
    image(child(window, 0), 4, 6, 0);
    image(child(window, 2), 4, 6, 17);
    check(IS_DISABLED(child(window, 3).GetState()), "empty party action disabled");
    auto first = member(731, 7, "Alpha");
    auto second = member(732, 255, "Bravo");
    for (unsigned i = 0; i < 8; ++i) {
        first.sfHelp[i].dwItemID = 0x10000 + i;
        first.sfHelp[i].dwSpriteID = i;
    }
    check(window.AddMember(&first) && window.AddMember(&second) && !window.AddMember(&first), "two unique members");
    auto& firstRow = static_cast<CGUIPartyMemberInfo&>(child(window, 5));
    auto& secondRow = static_cast<CGUIPartyMemberInfo&>(child(window, 6));
    position(firstRow, 7, 22, 238, 53);
    position(secondRow, 7, 78, 238, 53);
    image(child(firstRow, 0), 4, 6, 1);
    image(child(firstRow, 2), 20, 0, 2);
    image(child(secondRow, 2), 49, 0, 2);
    text(static_cast<CGUIText&>(child(firstRow, 3)), "Alpha");
    text(static_cast<CGUIText&>(child(firstRow, 4)), "lv51");
    position(child(firstRow, 5), 54, 41, 23, 10);
    position(child(firstRow, 6), 54, 53, 35, 10);
    position(child(firstRow, 7), 54, 65, 11, 10);
    auto& lastEffect = static_cast<CGUIItem&>(child(firstRow, 22));
    check(lastEffect.UsesTypedIcon455() && lastEffect.GetItemID() == 0x10007, "eighth effect is typed");
    window.SetLeader(732);
    position(secondRow, 7, 22, 238, 53);
    image(child(window, 7), 49, 0, 0);
    capture(window, "party-full.bgra", 27000);

    _mouse_event event = {};
    event.id = MOUSE_CLICKED;
    event.source = &child(window, 2);
    window.MouseEvent(event);
    position(window, 0, 0, 176, 139);
    position(secondRow, 7, 22, 168, 33);
    position(firstRow, 7, 57, 168, 33);
    image(child(window, 2), 4, 6, 18);
    check(!lastEffect.IsShow(), "compact hides effects");
    window.Show(FALSE);
    window.Show(TRUE);
    check(!lastEffect.IsShow(), "compact preserved on reopening");
    capture(window, "party-compact.bgra", 15000);

    event.source = &child(window, 3);
    window.MouseEvent(event);
    assertPosted(sink, 0x417, 0);
    window.SetWindowType(UI_PMT_LEADER);
    window.Lock(FALSE);
    window.MouseEvent(event);
    assertPosted(sink, 0x418, 1);
    window.Lock(TRUE);
    window.MouseEvent(event);
    assertPosted(sink, 0x418, 0);
    event.id = MOUSE_STROKED;
    event.source = &child(window, 4);
    window.SetDistribution455(2);
    window.MouseEvent(event);
    assertPosted(sink, 0x41e, 0);
    event.source = &child(firstRow, 1);
    firstRow.MouseEvent(event);
    assertPosted(sink, 0x41f, 731);

    for (unsigned i = 0; i < 9; ++i) {
        auto extra = member(800 + i, 1, "Member");
        check(window.AddMember(&extra), "eleven remote members fit");
    }
    auto extra = member(900, 1, "Overflow");
    check(!window.AddMember(&extra) && IS_DISABLED(child(window, 3).GetState()), "party capacity and disabled lock");
    window.RemoveMember(732);
    check(!IS_DISABLED(child(window, 3).GetState()) && firstRow.GetPosY() == 22 && window.AddMember(&extra),
          "removal compacts rows and restores capacity");
    window.RemoveAllMember();
    check(window.GetAddedObjectNum() == 5 && IS_DISABLED(child(window, 3).GetState()), "all rows removed");
    window.RemoveAll();
}
}

int main()
{
    return runWindowProbe("Party455", verifyParty,
                          "{\"status\":\"PASS\",\"GPU_frames\":2,\"member_capacity\":11,\"effect_slots_per_side\":8,"
                          "\"window_messages\":5,\"both_layouts\":true,\"live_party_operations\":false}\n");
}
