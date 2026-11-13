#include <cstdio>
#include <cstring>

#include "client455_money.h"

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
