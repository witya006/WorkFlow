// Player-to-player trade, target RVA 31FB20..32176D.
#include "client455_money.h"
#include "client455_unit_view_skin.h"
#include <cstring>

namespace {
using namespace RF455UnitView;

void TradeLockArt(CGUIButtonEx& button, BOOL locked, bool interactive)
{
    const WORD frame = locked ? 1 : 3;
    auto image = Image(16, 0, frame);
    button.SetSpriteInfoEx(&image);
    button.SetSize(image.pSprite->GetSpriteOrgXL(0, frame), image.pSprite->GetSpriteOrgYL(0, frame));
    if (interactive) {
        image = Image(16, 0, frame + 1);
        button.SetSpriteInfoEx(PRESSED, &image);
    }
}

void TradeAcceptArt(CGUIButtonEx& button, BOOL accepted, bool interactive)
{
    if (accepted) {
        auto image = Image(1, 1, 2);
        button.SetSpriteInfoEx(&image);
    } else if (interactive) {
        Button(button, 1, 1, 0, true, true);
    } else {
        auto image = Image(1, 1, 0);
        button.SetSpriteInfoEx(&image);
        button.SetSize(image.pSprite->GetSpriteOrgXL(1, 0), image.pSprite->GetSpriteOrgYL(1, 0));
    }
    button.SetARGB(accepted ? 0xffffc3bf : 0xffffffff);
}

void SetTradeInput(CGUIInput& input, __int64 value)
{
    char buffer[32] = {};
    if (value) RF455_FormatMoney(value, buffer);
    input.SetText(buffer);
    input.SetCaretPos(static_cast<WORD>(std::strlen(input.GetText())));
}

void SetTradeValue(CGUIText& field, LONG x, __int64 value)
{
    char buffer[32] = {};
    RF455_FormatMoney(value, buffer);
    field.SetString(buffer);
    field.SetPos(x + 136 - field.GetSizeX(), field.GetPosY());
}

void SetTradeSlots(CGUIObject (&slots)[MAX_TRADE_ITEM_NUM], BYTE enabled)
{
    for (unsigned i = 0; i < MAX_TRADE_ITEM_NUM; ++i) {
        if (i < enabled) {
            slots[i].RemoveSpriteInfo();
            slots[i].SetARGB(0xffffffff);
        } else {
            auto image = Image(44, 1, 0);
            slots[i].SetSpriteInfo(&image);
            slots[i].SetARGB(0xa0ffffff);
        }
    }
}
}

void CGUITradeWindow::SetSprite()
{
    Bind(*this, 16, 0, 0);
    m_uiAniTitleBar.SetImage455(Image(1, 4, 0).pSprite, 4, 0);
    Button(m_uiCloseButton, 1, 0, 0, true, false);
    Button(m_uiHelpButton455, 1, 0, 3, true, false);
    TradeLockArt(m_uiAvatarLockButton, m_avatarLocked455, true);
    TradeLockArt(m_uiOtherLockButton, m_bIsLock_Other, false);
    TradeAcceptArt(m_uiAvatarAcceptButton, m_avatarAccepted455, true);
    TradeAcceptArt(m_uiOtherAcceptButton, m_bIsAccept_Other, true);
    for (unsigned i = 0; i < MAX_TRADE_ITEM_NUM; ++i) {
        for (auto* item : {&m_uiAvatarItem[i], &m_uiOtherItem[i]}) {
            if (!item->IsEmpty()) item->SetSprite();
        }
        for (auto* overlay : {&m_uiAvatarUselessSocket[i], &m_uiOtherUselessSocket[i]}) {
            if (overlay->GetSpriteInfo()->pSprite) {
                auto image = Image(44, 1, 0);
                overlay->SetSpriteInfo(&image);
            }
        }
    }
}

void CGUITradeWindow::Init()
{
    SetSprite();
    const LONG x = GetPosX();
    const LONG y = GetPosY();
    const unsigned race = BYTE(_GetAvatarRace()) / 2;
    auto* moneyName = race < 3 ? Text(10 + race) : nullptr;
    m_uiTitle.SetString(Text(0x404));
    m_uiTitle.GetFont()->dwColor = 0xffc7bdb6;
    m_uiAvatarName.GetFont()->dwColor = 0xffe8e8e8;
    m_uiOtherName.GetFont()->dwColor = 0xffe8e8e8;
    m_uiAvatarDalantStr.SetString(moneyName);
    m_uiOtherDalantStr.SetString(moneyName);
    m_uiAvatarGoldStr.SetString(Text(0x3c7));
    m_uiOtherGoldStr.SetString(Text(0x3c7));
    for (auto* label : {&m_uiAvatarDalantStr, &m_uiAvatarGoldStr, &m_uiOtherDalantStr, &m_uiOtherGoldStr})
        label->GetFont()->dwColor = 0xffc4c4c4;

    HeaderPosition(*this, m_uiAniTitleBar, m_uiTitle, m_uiCloseButton);
    m_uiHelpButton455.SetPos(m_uiAniTitleBar.GetPosX() + 4, m_uiAniTitleBar.GetPosY() + 4);
    Add(&m_uiAniTitleBar);
    Add(&m_uiTitle);
    Add(&m_uiCloseButton);
    Add(&m_uiHelpButton455);
    m_uiCloseButton.AddMouseEventHandler(this);
    m_uiHelpButton455.AddMouseEventHandler(this);
    AddMouseEventHandler(this);

    for (unsigned i = 0; i < MAX_TRADE_ITEM_NUM; ++i) {
        const LONG left = x + 21 + 38 * (i % 5);
        const LONG row = 38 * (i / 5);
        auto place = [&](CGUIObject& background, CGUIItem& item, LONG top) {
            background.SetPos(left, top);
            background.SetSize(34, 34);
            item.SetPos(left + 1, top + 1);
            item.SetSize(32, 32);
            item.AddMouseEventHandler(this);
            Add(&background);
            Add(&item);
        };
        place(m_uiAvatarUselessSocket[i], m_uiAvatarItem[i], y + 338 + row);
        place(m_uiOtherUselessSocket[i], m_uiOtherItem[i], y + 62 + row);
    }
    m_uiAvatarName.SetPos(x + 65, y + 313);
    m_uiAvatarDalantInput.SetPos(x + 33, y + 473);
    m_uiAvatarGoldInput.SetPos(x + 33, y + 502);
    m_uiAvatarLockButton.SetPos(x + 18, y + 538);
    m_uiAvatarAcceptButton.SetPos(x + 143, y + 538);
    m_uiOtherName.SetPos(x + 65, y + 37);
    m_uiOtherDalant.SetPos(x + 150, y + 197);
    m_uiOtherGold.SetPos(x + 150, y + 226);
    m_uiOtherLockButton.SetPos(x + 18, y + 262);
    m_uiOtherAcceptButton.SetPos(x + 142, y + 262);
    m_uiAvatarDalantStr.SetPos(x + 158, y + 473);
    m_uiAvatarGoldStr.SetPos(x + 158, y + 502);
    m_uiOtherDalantStr.SetPos(x + 158, y + 196);
    m_uiOtherGoldStr.SetPos(x + 158, y + 226);

    for (auto* input : {&m_uiAvatarDalantInput, &m_uiAvatarGoldInput}) {
        input->SetSize(105, 12);
        input->SetAlignment(CGUIInput::Right_Alignment);
        input->SetMargin(2, 0);
        input->SetInputType(CGUIInput::Only_Number);
        input->AddMouseEventHandler(this);
        input->AddKeyEventHandler(this);
    }
    for (auto* button : {&m_uiAvatarAcceptButton, &m_uiOtherAcceptButton}) {
        button->SetLabel(Text(0x405));
        button->SetLabelColor(0xffe8e8e8);
        button->SetLabelStyle(R3_HAN_OUTLINE);
    }
    m_uiAvatarLockButton.AddMouseEventHandler(this);
    m_uiAvatarAcceptButton.AddMouseEventHandler(this);
    CGUIObject* fields[] = {
        &m_uiAvatarName, &m_uiAvatarDalantInput, &m_uiAvatarGoldInput, &m_uiAvatarLockButton, &m_uiAvatarAcceptButton,
        &m_uiOtherName, &m_uiOtherDalant, &m_uiOtherGold, &m_uiOtherLockButton, &m_uiOtherAcceptButton,
        &m_uiAvatarDalantStr, &m_uiAvatarGoldStr, &m_uiOtherDalantStr, &m_uiOtherGoldStr,
    };
    for (auto* field : fields) Add(field);
    SetMoveObject(&m_uiAniTitleBar);
    SetMoveObject(&m_uiTitle);
    SetMovable(TRUE);
    DisableFocus();
    SetLock_Avatar(FALSE);
    SetAccept_Avatar(FALSE);
    SetLock_Other(FALSE);
    SetAccept_Other(FALSE);
    m_uiOtherLockButton.Disable();
    m_uiOtherAcceptButton.Disable();
    SetAvatarDalant(0);
    SetAvatarGold(0);
    SetOtherDalant(0);
    SetOtherGold(0);
    SetARGB(0xd8ffffff);
}

void CGUITradeWindow::SetLock_Avatar(BOOL locked)
{
    m_avatarLocked455 = locked;
    TradeLockArt(m_uiAvatarLockButton, locked, true);
    if (locked) {
        m_uiAvatarAcceptButton.Enable();
        m_uiAvatarDalantInput.DisableFocus();
        m_uiAvatarGoldInput.DisableFocus();
    } else {
        m_uiAvatarAcceptButton.Disable();
        m_uiAvatarDalantInput.EnableFocus();
        m_uiAvatarGoldInput.EnableFocus();
    }
}

void CGUITradeWindow::SetAccept_Avatar(BOOL accepted)
{
    m_avatarAccepted455 = accepted;
    TradeAcceptArt(m_uiAvatarAcceptButton, accepted, true);
    if (!accepted) m_uiAvatarAcceptButton.Disable();
}

void CGUITradeWindow::SetLock_Other(BOOL locked)
{
    m_bIsLock_Other = locked;
    TradeLockArt(m_uiOtherLockButton, locked, false);
}

void CGUITradeWindow::SetAccept_Other(BOOL accepted)
{
    m_bIsAccept_Other = accepted;
    TradeAcceptArt(m_uiOtherAcceptButton, accepted, true);
}

void CGUITradeWindow::SetAvatarDalant(__int64 value)
{
    m_dwAvatarDalant = value;
    SetTradeInput(m_uiAvatarDalantInput, value);
}

void CGUITradeWindow::SetAvatarGold(__int64 value)
{
    m_dwAvatarGold = value;
    SetTradeInput(m_uiAvatarGoldInput, value);
}

void CGUITradeWindow::SetOtherDalant(__int64 value) { SetTradeValue(m_uiOtherDalant, GetPosX(), value); }
void CGUITradeWindow::SetOtherGold(__int64 value) { SetTradeValue(m_uiOtherGold, GetPosX(), value); }

void CGUITradeWindow::SetEnableSocketNum_Avatar(BYTE enabled) { SetTradeSlots(m_uiAvatarUselessSocket, enabled); }
void CGUITradeWindow::SetEnableSocketNum_Other(BYTE enabled) { SetTradeSlots(m_uiOtherUselessSocket, enabled); }
