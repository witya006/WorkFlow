// The ordinary 455 exchange board routes signed 64-bit amounts to item trade.
#include "client455_language.h"
#include "client455_money.h"
#include <cstdio>

BOOL CExchangeBoard::ExchangeMoney_Request(BYTE type, __int64 amount)
{
    if (amount <= 0 || _GetGBM()->IsRequestProcess()) return FALSE;
    if (type == IMT_GOLD)
        return _GetAvatar()->GetGold() >= amount && m_pNetMsgProcessor_ItemTrade->ExchangeGoldForDalantRequest_clzo(amount);
    return _GetAvatar()->GetDalant() >= amount && m_pNetMsgProcessor_ItemTrade->ExchangeDalantForGoldRequest_clzo(amount);
}

void CExchangeBoard::ExchangeMoney_Result(__int64 dalant, __int64 gold, BOOL accepted)
{
    if (accepted) {
        _GetAvatar()->SetDalant(dalant);
        _GetAvatar()->SetGold(gold);
        ClearExchange();
    } else {
        auto* pack = RF455_GetNormalLanguagePack();
        if (pack && pack->get(0x198)) _GUIMessageBox(nullptr, const_cast<char*>(pack->get(0x198)), 0xaaffffff);
    }
}

LRESULT CExchangeBoard::MsgProc(HWND window, UINT message, WPARAM id, LPARAM argument)
{
    switch (message) {
    case WM_EXCHANGE_BOARD_EXCHANGE_CHECK: {
        const auto goldGain = m_uiExchangeWindow.GetGold() - _GetAvatar()->GetGold();
        const auto dalantGain = m_uiExchangeWindow.GetDalant() - _GetAvatar()->GetDalant();
        auto* pack = RF455_GetNormalLanguagePack();
        if (!pack || !pack->get(0x19a) || (goldGain <= 0 && dalantGain <= 0)) break;
        char amount[32], description[64], question[256];
        if (goldGain > 0) {
            const char* format = pack->get(0x199);
            if (!format) break;
            RF455_FormatMoney(goldGain, amount);
            std::snprintf(description, sizeof description, format, amount);
        } else {
            RF455_FormatMoney(dalantGain, amount);
            unsigned race = BYTE(_GetAvatarRace()) / 2;
            const char* currency = pack->get(10 + (race < 3 ? race : 0));
            std::snprintf(description, sizeof description, "[%s] %s", amount, currency ? currency : "");
        }
        std::snprintf(question, sizeof question, pack->get(0x19a), description);
        _GUIMessageBox(&m_uiExchangeWindow, question, 0xccffffff, MSGBOX_ID_EXCHANGE, DLG_STYLE_OK_CANCEL);
        break;
    }
    case WM_EXCHANGE_BOARD_EXCHANGE: {
        const auto goldLoss = _GetAvatar()->GetGold() - m_uiExchangeWindow.GetGold();
        const auto dalantLoss = _GetAvatar()->GetDalant() - m_uiExchangeWindow.GetDalant();
        if (goldLoss > 0) ExchangeMoney_Request(IMT_GOLD, goldLoss);
        else if (dalantLoss > 0) ExchangeMoney_Request(IMT_DALANT, dalantLoss);
        break;
    }
    case WM_EXCHANGE_BOARD_CANCEL:
        ClearExchange();
        break;
    case WM_OPEN_WINDOW:
        ClearExchange();
        m_uiExchangeWindow.SetExchangeCommission(_GetAvatar()->GetExchangeCommission());
        break;
    }
    return CBaseBoard::MsgProc(window, message, id, argument);
}
