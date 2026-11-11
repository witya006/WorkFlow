// Item crafting root and three recipe lists from the 455 client.
#include "client455_unit_view_skin.h"
#include <algorithm>
#include <cstdio>
#include <cstring>
#include <string>

namespace {
constexpr BYTE NoRecipe = 0xff;
constexpr BYTE RecipeCapacity = 100;
constexpr BYTE RecipeTabs[] = {9, 5, 2};
constexpr unsigned RecipeTitles[] = {0x3d3, 0x3d4, 0xc2};

void FormatRecipeMaterial(CGUIText& text, const char* item, BYTE count)
{
    const char* format = RF455UnitView::Text(0x3d5);
    char amount[8] = {};
    std::snprintf(amount, sizeof(amount), "%3u", unsigned(count));
    std::string label;
    if (format && std::strcmp(format, "%3d %s") == 0)
        label = std::string(amount) + " " + item;
    else {
        label = std::string(item) + " " + amount;
        if (format && std::strncmp(format, "%s %3d", 6) == 0) label += format + 6;
    }
    text.SetString(&label[0]);
}
}

CGUIItemListWindow::CGUIItemListWindow() = default;
CGUIItemListWindow::~CGUIItemListWindow()
{
    RemoveAll();
}

void CGUIItemListWindow::Create(BYTE group, BYTE tabs, BYTE capacity)
{
    if (m_bIsCreated || group >= 3 || tabs != RecipeTabs[group] || !capacity) return;
    auto tabArt = std::make_unique<CGUIObject[]>(tabs);
    std::vector<std::unique_ptr<CGUIItem[]>> items;
    for (unsigned i = 0; i < tabs; ++i) items.push_back(std::make_unique<CGUIItem[]>(capacity));
    m_lastItem.assign(tabs, 0);
    m_tabs = std::move(tabArt);
    m_items = std::move(items);
    m_group = group;
    m_capacity = capacity;
    Init();
    m_bIsCreated = TRUE;
}

void CGUIItemListWindow::SetSprite()
{
    if (!m_tabs) return;
    using namespace RF455UnitView;
    Bind(m_uiTabBase, 14, WORD(m_group + 1), WORD(m_items.size()));
    for (unsigned i = 0; i < m_items.size(); ++i) {
        auto image = Image(14, WORD(m_group + 1), WORD(i));
        if (i == m_tab) m_tabs[i].SetSpriteInfo(&image);
        for (unsigned n = 0; n < m_capacity; ++n)
            if (!m_items[i][n].IsEmpty()) m_items[i][n].SetSprite();
    }
    m_pages.SetSprite();
    SelectItem(m_selected);
}

void CGUIItemListWindow::Init()
{
    if (!m_tabs) return;
    SetSprite();
    SetSize(228, 395);
    const LONG x = GetPosX(), y = GetPosY();
    m_uiTabBase.SetPos(x + (GetSizeX() - m_uiTabBase.GetSizeX()) / 2, y + 30);
    Add(&m_uiTabBase);
    const LONG tabStart = x + (GetSizeX() - LONG(m_items.size()) * 23) / 2;
    for (unsigned i = 0; i < m_items.size(); ++i) {
        auto& tab = m_tabs[i];
        tab.SetSize(23, 22);
        tab.SetPos(tabStart + 23 * LONG(i), y + 30);
        tab.AddMouseEventHandler(this);
        Add(&tab);
    }
    for (unsigned i = 0; i < TOTAL_ITEM_SOCKET_NUM; ++i) {
        auto& socket = m_uiSocket[i];
        socket.SetSize(34, 34);
        socket.SetPos(x + 20 + 38 * (i % 5), y + 63 + 38 * (i / 5));
        socket.AddMouseEventHandler(this);
        Add(&socket);
    }
    m_pages.Initialize(x + 19, y + 222, this);
    Add(&m_pages);
}

BOOL CGUIItemListWindow::TakeInItem(BYTE tab, BYTE slot, DWORD itemId, DWORD spriteId, BYTE quantity, BYTE)
{
    if (tab >= m_items.size() || slot >= m_capacity) return FALSE;
    auto& item = m_items[tab][slot];
    item.SetIconType455(0);
    item.SetItemID(itemId);
    item.SetSpriteID(spriteId);
    item.SetNum(quantity);
    item.SetSize(32, 32);
    item.SetSprite();
    m_lastItem[tab] = (std::max)(m_lastItem[tab], slot);
    if (tab == m_tab) {
        UpdatePageCount();
        SetPage(0);
    }
    return TRUE;
}

BOOL CGUIItemListWindow::TakeOutItem(BYTE tab, BYTE slot, BYTE quantity, CGUIItem*)
{
    if (tab >= m_items.size() || slot >= m_capacity) return FALSE;
    auto& item = m_items[tab][slot];
    if (quantity && quantity < item.GetNum()) item.SetNum(item.GetNum() - quantity);
    else item.SetEmpty();
    while (m_lastItem[tab] && m_items[tab][m_lastItem[tab]].IsEmpty()) --m_lastItem[tab];
    if (tab == m_tab) {
        if (slot == m_selected && item.IsEmpty()) DeselectItem();
        UpdatePageCount();
        SetPage(BYTE(m_pages.Current()));
    }
    return TRUE;
}

CGUIItem* CGUIItemListWindow::GetItem(BYTE tab, BYTE slot)
{
    if (tab >= m_items.size() || slot >= m_capacity) return nullptr;
    auto& item = m_items[tab][slot];
    return item.IsEmpty() ? nullptr : &item;
}

void CGUIItemListWindow::UpdatePageCount()
{
    m_pages.SetCount(m_tab < m_items.size() ? m_lastItem[m_tab] / TOTAL_ITEM_SOCKET_NUM + 1 : 0);
}

void CGUIItemListWindow::SetTab(BYTE tab)
{
    if (tab >= m_items.size()) return;
    if (m_tab < m_items.size()) {
        m_tabs[m_tab].RemoveSpriteInfo();
        m_tabs[m_tab].Enable();
    }
    m_tab = tab;
    auto image = RF455UnitView::Image(14, WORD(m_group + 1), tab);
    m_tabs[tab].SetSpriteInfo(&image);
    m_tabs[tab].Disable();
    UpdatePageCount();
    PostUIMessage(WM_ITEM_WORK_BOARD_CANCEL, 0);
    SetPage(0);
}

void CGUIItemListWindow::SetPage(BYTE requested)
{
    m_pages.SetPage(requested);
    const unsigned first = m_pages.Current() * TOTAL_ITEM_SOCKET_NUM;
    for (unsigned i = 0; i < TOTAL_ITEM_SOCKET_NUM; ++i) {
        m_uiSocket[i].SetEmpty();
        if (first + i < m_capacity) {
            if (auto* item = GetItem(m_tab, BYTE(first + i))) m_uiSocket[i].SetItem(item);
        }
    }
    SelectItem(m_selected);
}

void CGUIItemListWindow::SelectItem(BYTE index)
{
    DeselectItem();
    if (index >= m_capacity) return;
    m_selected = index;
    if (index / TOTAL_ITEM_SOCKET_NUM == m_pages.Current()) {
        auto image = RF455UnitView::Image(44, 0, 0);
        m_uiSocket[index % TOTAL_ITEM_SOCKET_NUM].SetSpriteInfo(&image);
    }
}

void CGUIItemListWindow::DeselectItem()
{
    m_selected = NoRecipe;
    for (auto& slot : m_uiSocket) slot.RemoveSpriteInfo();
}

void CGUIItemListWindow::MouseEvent(_mouse_event& event)
{
    CGUIWindow::MouseEvent(event);
    if (event.id == MOUSE_CLICKED) {
        if (event.source == &m_pages.Previous() && m_pages.Current()) SetPage(BYTE(m_pages.Current() - 1));
        if (event.source == &m_pages.Next() && m_pages.Current() + 1 < m_pages.Count()) SetPage(BYTE(m_pages.Current() + 1));
        return;
    }
    if (event.id == MOUSE_STROKED) {
        for (unsigned i = 0; i < m_items.size(); ++i) {
            if (event.source != &m_tabs[i]) continue;
            SetTab(BYTE(i));
            return;
        }
    } else if (event.id != MOUSE_HOVERED || gScreen.ExistObject()) {
        return;
    }
    for (unsigned i = 0; i < TOTAL_ITEM_SOCKET_NUM; ++i) {
        if (event.source != &m_uiSocket[i] || m_uiSocket[i].IsEmpty()) continue;
        const BYTE index = BYTE(m_pages.Current() * TOTAL_ITEM_SOCKET_NUM + i);
        PostUIMessage(event.id == MOUSE_STROKED ? WM_BOARD_CLICK_OBJECT : WM_BOARD_HOVER_OBJECT,
                      UI_MOUSE_MSG(m_tab, index, 0, 0));
        return;
    }
}

void CGUIItemMakeWindow::SetSprite()
{
    using namespace RF455UnitView;
    Bind(*this, 14, 0, 0);
    m_uiAniTitleBar.SetImage455(Image(1, 4, 0).pSprite, 4, 0);
    Button(m_uiMakeButton, 1, 1, 0, true, true);
    Button(m_uiCloseButton, 1, 0, 0, true, false);
    Button(m_uiHelpButton, 1, 0, 3, true, false);
    for (auto& list : m_uiMakeItemList) list.SetSprite();
}

void CGUIItemMakeWindow::Init()
{
    using namespace RF455UnitView;
    SetSprite();
    const LONG x = GetPosX(), y = GetPosY();
    m_uiMakeButton.SetLabel(Text(0x3d0));
    m_uiMaterialTitle[0].SetString(Text(0x3d1));
    m_uiMaterialTitle[1].SetString(Text(0x3d2));
    m_uiTitle.GetFont()->dwColor = 0xffc7bdb6;
    for (auto& label : m_uiMaterialTitle) label.GetFont()->dwColor = 0xffc3c1be;
    m_uiMakeButton.SetLabelColor(0xffe8e8e8);
    m_uiMakeButton.SetLabelStyle(R3_HAN_OUTLINE);
    m_uiMakeButton.SetPos(x + 80, y + 363);
    m_uiMaterialTitle[0].SetPos(x + 32, y + 261);
    m_uiMaterialTitle[1].SetPos(x + 32, y + 285);
    HeaderPosition(*this, m_uiAniTitleBar, m_uiTitle, m_uiCloseButton);
    m_uiHelpButton.SetPos(m_uiAniTitleBar.GetPosX() + 4, m_uiAniTitleBar.GetPosY() + 4);
    Add(&m_uiAniTitleBar);
    Add(&m_uiTitle);
    Add(&m_uiCloseButton);
    Add(&m_uiHelpButton);
    for (auto& title : m_uiMaterialTitle) Add(&title);
    for (auto& line : m_uiMaterialStr) Add(&line);
    Add(&m_uiMakeButton);
    m_uiMakeButton.AddMouseEventHandler(this);
    m_uiCloseButton.AddMouseEventHandler(this);
    m_uiHelpButton.AddMouseEventHandler(this);
    SetMoveObject(this);
    SetMoveObject(&m_uiAniTitleBar);
    SetMoveObject(&m_uiTitle);
    SetMovable(TRUE);
    EnableMake(FALSE);
    SoundOn(TRUE);
    SetARGB(0xd0ffffff);
}

void CGUIItemMakeWindow::SetMakeGroup(MakeGroup group)
{
    if (group < Weapon || group > Consume) return;
    auto& list = m_uiMakeItemList[group];
    if (!list.IsCreated()) list.Create(BYTE(group), RecipeTabs[group], RecipeCapacity);
    if (m_eCurMakeGroup != None) Remove(&m_uiMakeItemList[m_eCurMakeGroup]);
    m_eCurMakeGroup = group;
    list.SetID(GetID());
    list.SetPos(GetPosX(), GetPosY());
    AddFront455(&list);
    m_uiTitle.SetString(RF455UnitView::Text(RecipeTitles[group]));
    m_uiTitle.SetPos(m_uiAniTitleBar.GetPosX() + (m_uiAniTitleBar.GetSizeX() - m_uiTitle.GetSizeX()) / 2,
                    m_uiAniTitleBar.GetPosY() + (m_uiAniTitleBar.GetSizeY() - m_uiTitle.GetSizeY()) / 2);
}

void CGUIItemMakeWindow::SetMaterialStr(BYTE index, char* item, BYTE count, BOOL available)
{
    if (index >= 5) return;
    auto& label = m_uiMaterialStr[index];
    if (!item) {
        label.SetString(nullptr);
        return;
    }
    FormatRecipeMaterial(label, item, count);
    const LONG y = index ? m_uiMaterialTitle[1].GetPosY() + (index - 1) * (label.GetSizeY() + 2)
                         : m_uiMaterialTitle[0].GetPosY();
    label.SetPos(GetPosX() + 200 - label.GetSizeX(), y);
    label.GetFont()->dwColor = available ? 0xffffffff : 0xffff8b82;
}
