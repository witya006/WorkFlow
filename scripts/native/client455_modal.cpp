#include "client455_modal.h"
#include "client455_font.h"
#include "client455_language.h"
#include "userinterface/spritemgr.h"
#include "userinterface/guicontroller/guibutton.h"
#include "userinterface/gamewindow/guichatwindow.h"
#include "userinterface/guicontroller/guiscrollbar.h"

extern CSpriteMgr* g_pUiSpriteMgr;
extern CGUIChatWindow* g_pUiChatWindow;

void RF455_ConfigureModalButton(CGUIButton& button, bool closeButton) {
    auto* sprite = g_pUiSpriteMgr ? g_pUiSpriteMgr->GetSprite(SP_ID_COMMON) : nullptr;
    if (!sprite) {button.SetSpriteInfoEx(nullptr); return;}
    const unsigned action = closeButton ? 0 : 1;
    const unsigned count = closeButton ? 3 : 4;
    if (action >= sprite->GetMaxActions() || sprite->GetMaxFrames(action) < count) {
        button.SetSpriteInfoEx(nullptr);
        return;
    }
    SPRITE_INFO image = {sprite, static_cast<WORD>(action), 0};
    button.SetSpriteInfoEx(&image);
    image.wFrameNo = 1; button.SetSpriteInfoEx(HOVERED, &image);
    image.wFrameNo = 2; button.SetSpriteInfoEx(PRESSED, &image);
    if (!closeButton) {image.wFrameNo = 3; button.SetSpriteInfoEx(DISABLED, &image);}
    button.SetSize(sprite->GetSpriteOrgXL(action, 0), sprite->GetSpriteOrgYL(action, 0));
}

void RF455_ConfigureModalCaption(CGUIButtonEx& button, unsigned languageIndex) {
    const char* text = RF455_GetNormalLanguagePack()->get(languageIndex);
    button.SetLabel(const_cast<char*>(text));
    const auto extent = RF455_MeasureLegacyText(text);
    button.SetLabelMetrics455(extent.cx, extent.cy);
    button.SetLabelStyle(0x20);
}

bool RF455_ModalChatInputFocused() {
    auto* object = CGUIObject::GetFocusedObject();
    return object && object->IsFocused455() && g_pUiChatWindow &&
           object == g_pUiChatWindow->GetInputField();
}

void RF455_ConfigureModalScrollbar(CGUIScrollbar& bar) {
    auto* sprite=g_pUiSpriteMgr?g_pUiSpriteMgr->GetSprite(SP_ID_COMMON):nullptr;
    if(!sprite||sprite->GetMaxActions()<=2||sprite->GetMaxFrames(2)<4)return;
    SPRITE_INFO top[2]={{sprite,2,0},{sprite,2,1}},bottom[2]={{sprite,2,2},{sprite,2,3}};
    bar.SetTopArrowSpriteInfo(top);bar.SetBottomArrowSpriteInfo(bottom);
    POINT size={sprite->GetSpriteOrgXL(2,0),sprite->GetSpriteOrgYL(2,0)};
    bar.SetTopArrowSize(size);size={sprite->GetSpriteOrgXL(2,2),sprite->GetSpriteOrgYL(2,2)};
    bar.SetBottomArrowSize(size);size={5,18};bar.SetBarSize(size);
    bar.SetBarSpriteInfo(nullptr);bar.SetBarColor455(0xff70635d);
    bar.SetStyle(CGUIScrollbar::Vertical);
    bar.SetSize(sprite->GetSpriteOrgXL(2,0),bar.GetSizeY()?bar.GetSizeY():30);
}
