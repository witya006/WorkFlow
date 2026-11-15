#pragma once

#include "client455_briefing_controls.h"
#include "client455_item_icon_metadata.h"
#include "client455_language.h"
#include "client455_modal.h"
#include "2dsprite.h"
#include "userinterface/guicontroller/guibutton.h"
#include "userinterface/guicontroller/guiitem.h"
#include "userinterface/guicontroller/guiscreen.h"
#include "userinterface/guicontroller/guiwindow.h"
#include "userinterface/spritemgr.h"

class CGUIDungeonGatePanel455 final : public CGUIWindow {
public:
    using Action = void (*)(void*);

    ~CGUIDungeonGatePanel455() override
    {
        board_.RemoveAll();
        RemoveAll();
    }

    void Init() override
    {
        if (initialized_) return;
        initialized_ = true;
        SetID(0xd0000000u); // RVA 0x329780 sets the high byte of the window ID.
        SetSize(width_, height_);
        board_.SetColors455(0xff222628, 0xff5a5857);
        board_.SetBorder455(1, 3);
        title_.DisableFocus();
        title_.SetMouseInput455(FALSE);
        title_.GetFont()->dwColor = 0xffe2d7c3;
        icon_.SetIconType455(0);
        icon_.SetSize(iconSize_, iconSize_);
        icon_.ShowGradeFrame455(FALSE);
        icon_.DrawItemNum(FALSE);
        icon_.DisableFocus();
        icon_.SetMouseInput455(FALSE);
        activate_.SetLabelColor(0xffe2d7c3);
        activate_.SetLabelHoveredColor(0xffffdeb1);
        activate_.AddMouseEventHandler(this);
        close_.AddMouseEventHandler(this);
        board_.Add(&title_);
        board_.Add(&icon_);
        board_.Add(&activate_);
        board_.Add(&close_);
        Add(&board_);
        Show(FALSE);
        SetSprite();
    }

    void SetSprite() override
    {
        if (!initialized_) return;
        auto* common = gSpriteMgr.GetTargetSprite455(1);
        if (!common || common->GetMaxActions() <= 4 || common->GetMaxFrames(4) <= 4) common = nullptr;
        board_.SetCaps455(common, TRUE);
        if (!common) {
            board_.GetUpper455().SetSize(0, 0);
            board_.GetLower455().SetSize(0, 0);
        }
        RF455_ConfigureModalButton(activate_);
        if (!activate_.GetSpriteInfo()->pSprite) activate_.SetSize(88, 24);
        RF455_ConfigureModalCaption(activate_, 0x9fe);
        RF455_ConfigureModalButton(close_, true);
        char closeLabel[] = "X";
        if (!close_.GetSpriteInfo()->pSprite) {
            close_.SetSize(20, 20);
        } else {
            closeLabel[0] = '\0';
        }
        close_.SetLabel(closeLabel);
        title_.SetString(const_cast<char*>(RF455_GetNormalLanguagePack()->get(0x9fd)));
        if (!icon_.IsEmpty()) icon_.SetSprite();
        Layout455();
    }

    void Bind455(void* owner, Action confirm, Action close)
    {
        owner_ = owner;
        confirmAction_ = confirm;
        closeAction_ = close;
    }

    void Present455(const RF455BasicIconMetadata& metadata, CGUIWindow& inventory)
    {
        Init();
        inventory_ = &inventory;
        icon_.SetItemID(metadata.itemID);
        icon_.SetSpriteID(metadata.spriteID);
        icon_.SetNum(1);
        icon_.SetSprite();
        SetPending455(false);
        Layout455();
        CGUIWindow::Open();
    }

    void SetPending455(bool pending)
    {
        if (pending) {
            activate_.Disable();
            close_.Disable();
        } else {
            activate_.Enable();
            close_.Enable();
        }
    }

    void Close() override
    {
        if (!IsShow()) return;
        if (closeAction_) closeAction_(owner_);
        else Hide455();
    }

    void Hide455()
    {
        if (IsShow()) CGUIWindow::Close();
        icon_.SetEmpty();
        inventory_ = nullptr;
    }

    void MouseEvent(_mouse_event& event) override
    {
        if (event.id != MOUSE_CLICKED) return;
        if (event.source == &activate_ && confirmAction_) confirmAction_(owner_);
        else if (event.source == &close_) Close();
    }

private:
    class PanelButton : public CGUIButtonEx {
    public:
        BOOL Draw() override
        {
            DrawFallback455();
            return CGUIButtonEx::Draw();
        }
        BOOL Draw(RECT& clipping) override
        {
            DrawFallback455();
            return CGUIButtonEx::Draw(clipping);
        }
    private:
        void DrawFallback455()
        {
            if (!IsShow() || GetSpriteInfo()->pSprite) return;
            const LONG x = GetPosX(), y = GetPosY();
            const LONG right = x + GetSizeX(), bottom = y + GetSizeY();
            Draw2DRectangle(x, y, right, bottom, 0xff645b50);
            Draw2DRectangle(x + 1, y + 1, right - 1, bottom - 1, 0xff272c2e);
        }
    };

    void Layout455()
    {
        const LONG maxX = gScreen.GetSizeX() - width_;
        const LONG maxY = gScreen.GetSizeY() - height_;
        // RVA 0x0F6020 aligns the panel to the inventory with a two-window left offset.
        LONG x = inventory_ ? inventory_->GetPosX() - 2 * width_ - 15 : maxX / 2;
        LONG y = inventory_ ? inventory_->GetPosY() : maxY / 2;
        if (x > maxX) x = maxX;
        if (y > maxY) y = maxY;
        if (x < 0) x = 0;
        if (y < 0) y = 0;
        SetPos(x, y);
        board_.SetPos(x, y);
        board_.SetSize(width_, height_);
        title_.SetPos(x + (width_ - title_.GetSizeX()) / 2, y + 12);
        icon_.SetPos(x + (width_ - iconSize_) / 2, y + (height_ - iconSize_) / 2);
        activate_.SetPos(x + (width_ - activate_.GetSizeX()) / 2, y + 221);
        close_.SetPos(x + width_ - close_.GetSizeX() - 8, y + 8);
    }

    static constexpr LONG width_ = 228;
    static constexpr LONG height_ = 270;
    static constexpr LONG iconSize_ = 66;
    CGUIBriefingBoard board_;
    CGUIText title_;
    CGUIItem icon_;
    PanelButton activate_, close_;
    CGUIWindow* inventory_ = nullptr;
    void* owner_ = nullptr;
    Action confirmAction_ = nullptr, closeAction_ = nullptr;
    bool initialized_ = false;
};
