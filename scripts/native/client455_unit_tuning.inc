// UnitTuning 455, window Init 32BB90 and SetSprite 32D950.
#include "client455_nation_paths.h"
#include "client455_unit_view_skin.h"
#include <cstdio>

using namespace RF455UnitView;

namespace {
bool CompactUnitStats()
{
    switch (RF455_GetNormalNationPaths()->nation) {
    case 1: case 3: case 4: case 6: case 7: case 9: case 10:
        return true;
    default:
        return false;
    }
}

void UnitMask(CGUIObject& object, WORD action, bool large, bool visible)
{
    const WORD frame = large ? 4 : 0;
    SPRITE_INFO image = visible ? Image(44, action, frame) : SPRITE_INFO{nullptr, action, frame};
    object.SetSpriteInfo(&image);
}
}

void CGUIUnitTuningWindow::SetSprite()
{
    Bind(m_uiUpperBase, 18, 0, 0);
    Bind(m_uiPartsBoard, 18, 0, 1);
    Bind(m_uiBulletBoard, 18, 0, 2);
    Button(m_uiTab[PARTS_TAB], 18, 1, 0, false, true);
    Button(m_uiTab[BULLET_TAB], 18, 1, 3, false, true);
    Button(m_uiPageLeftButton, 18, 1, 6, false, true);
    Button(m_uiPageRightButton, 18, 1, 9, false, true);

    for (BYTE i = 0; i < TOTAL_PARTS_TYPE_NUM; ++i) {
        Bind(m_uiBuyItemTab[i], 18, 2, i);
        Bind(m_uiEmptyPartsFlag[i], 18, 3, i);
        UnitMask(m_uiBuyingPartsFlag[i], 0, true, false);
    }
    for (BYTE i = 0; i < BULLET_TYPE_NUM; ++i) {
        Bind(m_uiEmptyBulletFlag[i], 18, 3, WORD(6 + i));
        UnitMask(m_uiBuyingBulletFlag[i], 0, true, false);
    }
    for (BYTE i = 0; i < BACK_PACK_BULLET_NUM; ++i) {
        Bind(m_uiEmptyBackPackBulletFlag[i], 18, 3, 7);
        UnitMask(m_uiBuyingBackPackBulletFlag[i], 2, false, false);
    }

    m_uiAniTitleBar.SetImage455(Image(1, 4, 0).pSprite, 4, 0);
    Button(m_uiCloseButton, 1, 0, 0, true, false);
    Button(m_uiHelpButton, 1, 0, 3, true, false);
    Button(m_uiRepairButton, 1, 1, 0, true, true);
    Button(m_uiTuningButton, 1, 1, 0, true, true);
    Button(m_uiCancelButton, 1, 1, 0, true, true);
}

void CGUIUnitTuningWindow::Init()
{
    SetSprite();
    SetSize(228, 571);
    m_uiUpperBase.SetSize(228, 300);
    m_uiLowerBase.SetSize(228, 271);
    m_uiActiveTabBoard.SetSize(75, 29);
    m_uiMainFrameKey.SetSize(64, 64);
    for (auto& tab : m_uiBuyItemTab) tab.SetSize(18, 18);
    for (auto& socket : m_uiBuyItemBoard) socket.SetSize(32, 32);

    const bool compact = CompactUnitStats();
    m_uiTitle.SetString(Text(0x40b));
    for (BYTE i = 0; i < 4; ++i) m_uiMainFrameInfoTitle[i].SetString(Text(0x40c + i));
    m_uiWeaponTitle.SetString(Text(0x410));
    m_uiWeaponInfoTitle[0].SetString(compact ? nullptr : Text(0x411));
    m_uiWeaponInfoTitle[1].SetString(Text(0x412));
    m_uiWeaponInfoTitle[2].SetString(Text(0x413));
    m_uiAddWeaponTitle.SetString(Text(0x414));
    for (BYTE i = 0; i < 3; ++i)
        m_uiAddWeaponInfoTitle[i].SetString(m_uiWeaponInfoTitle[i].GetString());
    m_uiTab[PARTS_TAB].SetLabel(Text(0x415));
    m_uiTab[BULLET_TAB].SetLabel(Text(0x416));
    m_uiRepairButton.SetLabel(Text(0x418));
    m_uiTuningButton.SetLabel(Text(0x419));
    m_uiCancelButton.SetLabel(Text(0x35e));

    char currency[256], costLabel[256];
    const unsigned race = BYTE(_GetAvatarRace()) / 2;
    const int currencySize = std::snprintf(currency, sizeof(currency), "       %s", race < 3 ? Text(10 + race) : "");
    if (currencySize < 0 || currencySize >= sizeof(currency))
        throw std::runtime_error("455 unit currency label exceeds 256 bytes");
    const int costSize = std::snprintf(costLabel, sizeof(costLabel), Text(0x417), currency);
    if (costSize < 0 || costSize >= sizeof(costLabel))
        throw std::runtime_error("455 unit cost label exceeds 256 bytes");
    m_uiTuningCostTitle.SetString(costLabel);

    const LONG x = GetPosX(), y = GetPosY();
    HeaderPosition(*this, m_uiAniTitleBar, m_uiTitle, m_uiCloseButton);
    m_uiHelpButton.SetPos(m_uiAniTitleBar.GetPosX() + 4, m_uiAniTitleBar.GetPosY() + 4);
    m_uiUpperBase.SetPos(x, y);
    m_uiMainFrameKey.SetPos(x + 11, y + 66);
    m_uiRepairButton.SetPos(x + 9, y + 138);
    m_uiMainFrameInfoTitle[0].SetPos(x + 9, y + 33);
    m_uiMainFrameInfoTitle[1].SetPos(x + 9, y + 47);
    m_uiMainFrameInfoTitle[2].SetPos(x + (compact ? 115 : 130), y + 33);
    m_uiMainFrameInfoTitle[3].SetPos(x + (compact ? 115 : 130), y + 47);
    m_uiWeaponTitle.SetPos(m_uiMainFrameKey.GetPosX() + m_uiMainFrameKey.GetSizeX() + 20, y + 65);
    m_uiAddWeaponTitle.SetPos(m_uiWeaponTitle.GetPosX(), y + 126);
    for (BYTE i = 0; i < 3; ++i) {
        auto& primary = m_uiWeaponInfoTitle[i];
        auto& secondary = m_uiAddWeaponInfoTitle[i];
        primary.SetPos(x + 83, y + 79 + 16 * i);
        secondary.SetPos(x + 83, y + 140 + 16 * i);
        m_uiWeaponInfo[i].SetPos(primary.GetPosX() + primary.GetSizeX() - 3, primary.GetPosY());
        m_uiAddWeaponInfo[i].SetPos(secondary.GetPosX() + secondary.GetSizeX() - 3, secondary.GetPosY());
    }
    m_uiTab[PARTS_TAB].SetPos(x + 7, y + 188);
    m_uiTab[BULLET_TAB].SetPos(x + 117, y + 188);
    m_uiTab[PARTS_TAB].SetLabelPos(28, 15);
    m_uiTab[BULLET_TAB].SetLabelPos(37, 15);
    for (BYTE i = 0; i < ITEM_BOARD_NUM; ++i) m_uiBuyItemBoard[i].SetPos(x + 22 + 37 * i, y + 262);
    m_uiPageLeftButton.SetPos(x + 8, y + 268);
    m_uiPageRightButton.SetPos(x + 207, y + 268);
    m_uiLowerBase.SetPos(x, y + m_uiUpperBase.GetSizeY());
    m_uiTuningCostTitle.SetPos(x + (GetSizeX() - m_uiTuningCostTitle.GetSizeX()) / 2 + 5, y + 516);
    m_uiTuningCost.SetPos(x + 109, y + 516);
    m_uiTuningButton.SetPos(x + 18, y + 537);
    m_uiCancelButton.SetPos(x + 143, y + 537);

    Add(&m_uiUpperBase);
    Add(&m_uiAniTitleBar);
    Add(&m_uiTitle);
    CGUIObject* observed[] = {&m_uiCloseButton, &m_uiHelpButton, &m_uiMainFrameKey, &m_uiRepairButton};
    for (auto* object : observed) {
        object->AddMouseEventHandler(this);
        Add(object);
    }
    Add(&m_uiWeaponTitle);
    Add(&m_uiAddWeaponTitle);
    for (BYTE i = 0; i < 4; ++i) {
        Add(&m_uiMainFrameInfoTitle[i]);
        Add(&m_uiMainFrameInfo[i]);
        m_uiMainFrameInfoTitle[i].GetFont()->dwColor = HEAD_COLOR;
        m_uiMainFrameInfo[i].GetFont()->dwColor = TEXT_COLOR;
    }
    for (BYTE i = 0; i < 3; ++i) {
        Add(&m_uiWeaponInfoTitle[i]);
        Add(&m_uiWeaponInfo[i]);
        Add(&m_uiAddWeaponInfoTitle[i]);
        Add(&m_uiAddWeaponInfo[i]);
        m_uiWeaponInfoTitle[i].GetFont()->dwColor = HEAD_COLOR;
        m_uiAddWeaponInfoTitle[i].GetFont()->dwColor = HEAD_COLOR;
        m_uiWeaponInfo[i].GetFont()->dwColor = TEXT_COLOR;
        m_uiAddWeaponInfo[i].GetFont()->dwColor = TEXT_COLOR;
    }
    for (auto& tab : m_uiTab) {
        tab.AddMouseEventHandler(this);
        tab.SetLabelStyle(R3_HAN_OUTLINE);
        Add(&tab);
    }
    for (auto& tab : m_uiBuyItemTab) tab.AddMouseEventHandler(this);
    for (auto& socket : m_uiBuyItemBoard) {
        socket.AddMouseEventHandler(this);
        Add(&socket);
    }
    m_uiPageLeftButton.AddMouseEventHandler(this);
    m_uiPageRightButton.AddMouseEventHandler(this);
    Add(&m_uiPageLeftButton);
    Add(&m_uiPageRightButton);
    Add(&m_uiLowerBase);
    m_uiRepairButton.SetLabelStyle(R3_HAN_OUTLINE);
    for (auto* button : {&m_uiTuningButton, &m_uiCancelButton}) {
        button->SetLabelStyle(R3_HAN_OUTLINE);
        button->AddMouseEventHandler(this);
    }
    Add(&m_uiTuningButton);
    Add(&m_uiCancelButton);
    Add(&m_uiTuningCostTitle);
    Add(&m_uiTuningCost);
    InitPartsBoard();
    InitBulletBoard();

    m_uiUpperBase.SetARGB(0xccffffff);
    m_uiPartsBoard.SetARGB(0xccffffff);
    m_uiBulletBoard.SetARGB(0xccffffff);
    m_uiTitle.GetFont()->dwColor = TITLE_COLOR;
    m_uiWeaponTitle.GetFont()->dwColor = SUB_TITLE_COLOR;
    m_uiAddWeaponTitle.GetFont()->dwColor = SUB_TITLE_COLOR;
    m_uiActiveTabName.GetFont()->dwColor = TEXT_COLOR;
    m_uiBackPackBulletTitle.GetFont()->dwColor = TEXT_COLOR;
    m_uiTuningCostTitle.GetFont()->dwColor = HEAD_COLOR;
    m_uiTuningCost.GetFont()->dwColor = 0xffffffff;
    SetMoveObject(&m_uiTitle);
    SetMoveObject(&m_uiAniTitleBar);
    SetMovable(TRUE);
    m_uiMainFrameKey.DrawItemNum(FALSE);

    SetTab(PARTS_TAB);
    for (BYTE i = 0; i < TOTAL_PARTS_TYPE_NUM; ++i) UnEquip_Parts(i);
    for (BYTE i = 0; i < BULLET_TYPE_NUM; ++i) UnEquip_Bullet(i);
    for (BYTE i = 0; i < BACK_PACK_BULLET_NUM; ++i) UnEquip_BackPack_Bullet(i);
    m_uiRepairButton.Disable();
    m_uiTuningButton.Disable();
    m_uiCancelButton.Disable();
    Select_Bullet(0);
    Enable_BackPack_Bullet(0);
    Enable_Shouler_Bullet(FALSE);
}

void CGUIUnitTuningWindow::Select_Parts(BYTE index)
{
    if (index >= TOTAL_PARTS_TYPE_NUM) return;
    UnitMask(m_uiSelectedParts, 1, true, true);
    m_uiSelectedParts.SetARGB(0x90ffffff);
    m_uiSelectedParts.SetPos(m_uiTuningParts[index].GetPosX() - 1,
                             m_uiTuningParts[index].GetPosY() - 1);
}

void CGUIUnitTuningWindow::Select_Bullet(BYTE index)
{
    if (index >= BULLET_TYPE_NUM + BACK_PACK_BULLET_NUM) return;
    const bool large = index < BULLET_TYPE_NUM;
    const auto& slot = large ? m_uiTuningBullet[index] : m_uiTuningBackPackBullet[index - BULLET_TYPE_NUM];
    m_uiSelectedBullet.SetSize(large ? 66 : 34, large ? 66 : 34);
    UnitMask(m_uiSelectedBullet, 1, large, true);
    m_uiSelectedBullet.SetARGB(0x90ffffff);
    m_uiSelectedBullet.SetPos(slot.m_ptPos.x - 1, slot.m_ptPos.y - 1);
}

void CGUIUnitTuningWindow::SetPartsBuyingState(BYTE index, BOOL buying)
{
    if (index < TOTAL_PARTS_TYPE_NUM) UnitMask(m_uiBuyingPartsFlag[index], 0, true, buying != FALSE);
}

void CGUIUnitTuningWindow::SetBulletBuyingState(BYTE index, BOOL buying)
{
    if (index >= BULLET_TYPE_NUM || (index == Bullet_Shoulder && IS_DISABLED(m_uiTuningBullet[index].GetState()))) return;
    UnitMask(m_uiBuyingBulletFlag[index], 0, true, buying != FALSE);
    m_uiBuyingBulletFlag[index].SetARGB(buying ? 0xa0ffffff : 0xffffffff);
}

void CGUIUnitTuningWindow::SetBackpackBulletBuyingState(BYTE index, BOOL buying)
{
    if (index >= BACK_PACK_BULLET_NUM) return;
    m_uiBuyingBackPackBulletFlag[index].GetSpriteInfo()->pSprite = buying ? Image(44, 2, 0).pSprite : nullptr;
    if (!buying) m_uiBuyingBackPackBulletFlag[index].SetARGB(0xffffffff);
}

void CGUIUnitTuningWindow::Enable_Shouler_Bullet(BOOL enabled)
{
    auto& flag = m_uiBuyingBulletFlag[Bullet_Shoulder];
    UnitMask(flag, enabled ? 1 : 2, true, !enabled);
    flag.SetARGB(enabled ? 0xffffffff : 0xa0ffffff);
    if (enabled) m_uiTuningBullet[Bullet_Shoulder].Enable();
    else m_uiTuningBullet[Bullet_Shoulder].Disable();
}

void CGUIUnitTuningWindow::Enable_BackPack_Bullet(BYTE enabledCount)
{
    for (BYTE i = 0; i < BACK_PACK_BULLET_NUM; ++i) {
        auto& flag = m_uiBuyingBackPackBulletFlag[i];
        if (i < enabledCount) {
            SPRITE_INFO image = {nullptr, 0, 3};
            flag.SetSpriteInfo(&image);
            flag.SetARGB(0xffffffff);
            m_uiTuningBackPackBullet[i].Enable();
        } else {
            UnitMask(flag, 2, false, true);
            flag.SetARGB(0xa0ffffff);
            m_uiTuningBackPackBullet[i].Disable();
        }
    }
}
