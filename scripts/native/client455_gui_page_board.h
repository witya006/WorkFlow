#pragma once

#include "client455_unit_view_skin.h"
#include <algorithm>
#include <cstdio>

// Shared page board constructed by the merchant and crafting panels in 455.
class RF455GuiPageBoard : public CGUIContainer {
    CGUIButtonEx m_previous, m_next;
    CGUIObject m_background;
    CGUIText m_label;
    WORD m_count = 0;
    WORD m_current = 0;

public:
    void SetSprite() override
    {
        using namespace RF455UnitView;
        Button(m_previous, 1, 6, 1, false, true);
        Button(m_next, 1, 6, 4, false, true);
        Bind(m_background, 1, 6, 0);
    }

    void Initialize(LONG x, LONG y, IMouseObserver* observer)
    {
        SetSprite();
        SetPos(x, y);
        SetSize(m_previous.GetSizeX() + m_background.GetSizeX() + m_next.GetSizeX(), m_background.GetSizeY());
        m_previous.SetPos(x, y);
        m_background.SetPos(x + m_previous.GetSizeX(), y);
        m_next.SetPos(m_background.GetPosX() + m_background.GetSizeX(), y);
        m_previous.SetLabel(RF455UnitView::Text(0x3c4));
        m_next.SetLabel(RF455UnitView::Text(0x3c5));
        m_previous.AddMouseEventHandler(observer);
        m_next.AddMouseEventHandler(observer);
        Add(&m_previous);
        Add(&m_next);
        Add(&m_background);
        Add(&m_label);
        m_label.GetFont()->dwColor = 0xffe8e8e8;
        SetPage(0);
    }

    WORD Current() const { return m_current; }
    WORD Count() const { return m_count; }
    CGUIButton& Previous() { return m_previous; }
    CGUIButton& Next() { return m_next; }

    void SetCount(WORD count)
    {
        m_count = count;
        SetPage(m_current);
    }

    void SetPage(WORD requested)
    {
        m_current = m_count ? (std::min)(requested, WORD(m_count - 1)) : 0;
        char label[24] = {};
        std::snprintf(label, sizeof(label), "%u / %u", unsigned(m_count ? m_current + 1 : 0), unsigned(m_count));
        m_label.SetString(label);
        m_label.SetPos(m_background.GetPosX() + (m_background.GetSizeX() - m_label.GetSizeX()) / 2,
                       m_background.GetPosY() + (m_background.GetSizeY() - m_label.GetSizeY()) / 2);
        if (m_current) m_previous.Enable();
        else m_previous.Disable();
        if (m_count && m_current + 1 < m_count) m_next.Enable();
        else m_next.Disable();
    }
};
