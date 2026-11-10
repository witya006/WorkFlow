#pragma once

#include "client455_language.h"
#include "userinterface/spritemgr.h"
#include "userinterface/guicontroller/guibutton.h"
#include "userinterface/guicontroller/guiwindow.h"

#include <stdexcept>

namespace RF455UnitView {
inline SPRITE_INFO Image(BYTE id, WORD action, WORD frame)
{
    auto* sprite = gSpriteMgr.GetTargetSprite455(id);
    if (!sprite || action >= sprite->GetMaxActions() || frame >= sprite->GetMaxFrames(action))
        throw std::runtime_error("455 unit window sprite frame unavailable");
    return {sprite, action, frame};
}

inline void Bind(CGUIObject& object, BYTE id, WORD action, WORD frame)
{
    auto image = Image(id, action, frame);
    object.SetSpriteInfo(&image);
    object.SetSize(image.pSprite->GetSpriteOrgXL(action, frame),
                   image.pSprite->GetSpriteOrgYL(action, frame));
}

inline void Button(CGUIButton& button, BYTE id, WORD action, WORD frame,
                   bool hover, bool disabled)
{
    auto image = Image(id, action, frame);
    button.SetSpriteInfoEx(&image);
    button.SetSize(image.pSprite->GetSpriteOrgXL(action, frame),
                   image.pSprite->GetSpriteOrgYL(action, frame));
    if (hover) {
        image = Image(id, action, ++frame);
        button.SetSpriteInfoEx(HOVERED, &image);
    }
    image = Image(id, action, ++frame);
    button.SetSpriteInfoEx(PRESSED, &image);
    if (disabled) {
        image = Image(id, action, ++frame);
        button.SetSpriteInfoEx(DISABLED, &image);
    }
}

inline char* Text(unsigned index)
{
    auto* pack = RF455_GetNormalLanguagePack();
    if (!pack || pack->records.empty())
        throw std::logic_error("455 unit window language unavailable");
    return const_cast<char*>(pack->get(index));
}

inline void HeaderPosition(CGUIWindow& window, CGUIObject& header,
                           CGUIText& title, CGUIButton& close)
{
    header.SetPos(window.GetPosX() + (window.GetSizeX() - header.GetSizeX()) / 2,
                  window.GetPosY() + 6);
    title.SetPos(header.GetPosX() + (header.GetSizeX() - title.GetSizeX()) / 2,
                 header.GetPosY() + (header.GetSizeY() - title.GetSizeY()) / 2);
    close.SetPos(header.GetPosX() + header.GetSizeX() - close.GetSizeX() - 4,
                 header.GetPosY() + 4);
}
}
