// 455 killing counter skin at RVA 321EF0. The panel keeps its 144x126 size.
#include "client455_unit_view_skin.h"

void CGUIKillingCounter::SetSprite()
{
    auto skin = RF455UnitView::Image(17, 0, 0);
    auto gauge = RF455UnitView::Image(17, 0, 1);
    SetSpriteInfo(&skin);
    m_sGaugeSpriteInfo = gauge;
    m_fGaugeUV[0] = static_cast<float>(GetSizeX()) / gauge.pSprite->GetSpriteXL(0, 1);
    m_fGaugeUV[1] = static_cast<float>(GetSizeY()) / gauge.pSprite->GetSpriteYL(0, 1);
}
