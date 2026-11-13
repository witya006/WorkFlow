#include <cstdio>
#include <cstring>

#include "client455_money.h"
#include "client455_font.h"

namespace {

void SetSelectionText(CGUIText& label, unsigned id, const char* value)
{
    const char* format = RF455_GetNormalLanguagePack()->get(id);
    const char* substitution = std::strstr(format, "%s");
    char text[128];
    if (substitution)
        std::snprintf(text, sizeof(text), "%.*s%s%s", int(substitution - format), format, value, substitution + 2);
    else
        std::snprintf(text, sizeof(text), "%s%s", format, value);
    label.SetString(text);
}

} // namespace

BOOL CGUISelectCharacter::CurrencyLabel::Draw()
{
    if (!IsShow()) return FALSE;
    const char* text = GetString();
    if (!text || maximumWidth_ <= 0) return CGUIText::Draw();
    const LONG width = RF455_MeasureLegacyText(text).cx;
    if (width <= maximumWidth_) return CGUIText::Draw();

    // Fit the complete value inside the fixed 455 panel when the locale's
    // font makes the line wider than its available space.
    const auto* font = GetFont();
    float position[] = {float(m_ptPos.x), float(m_ptPos.y), 0.99f, 1.0f};
    auto* device = GetD3dDevice();
    device->SetRenderState(D3DRS_ZENABLE, FALSE);
    RF455_DrawTextAnsiScaled(position, text, font->dwColor, font->dwStyle | 0x400,
                            float(maximumWidth_) / width);
    device->SetRenderState(D3DRS_ZENABLE, TRUE);
    return TRUE;
}

void CGUISelectCharacter::SetCharInfo_Name(char* name)
{
    SetSelectionText(m_cNameStr, 0x4b7, name);
}

void CGUISelectCharacter::SetCharInfo_Level(char* level)
{
    SetSelectionText(m_cLevelStr, 0x4b8, level);
}

void CGUISelectCharacter::SetCharInfo_Attribute(BYTE attribute)
{
    if (attribute < 4)
        m_cAttributeStr.SetString(const_cast<char*>(RF455_GetNormalLanguagePack()->get(0x4b9 + attribute)));
}

void CGUISelectCharacter::SetCharInfo_Money(__int64 dalant, __int64 gold, BYTE race)
{
    char amount[32]{};
    RF455_FormatMoney(dalant, amount);
    const unsigned raceIndex = race / 2;
    if (raceIndex >= 2) {
        SetSelectionText(m_cDalantStr, 0x505, amount);
    } else {
        const char* currency = RF455_GetNormalLanguagePack()->get(10 + raceIndex);
        char text[128];
        std::snprintf(text, sizeof(text), "%s : %s", currency, amount);
        m_cDalantStr.SetString(text);
    }
    RF455_FormatMoney(gold, amount);
    SetSelectionText(m_cGoldStr, raceIndex >= 2 ? 0x4be : 0x4bf, amount);
}
