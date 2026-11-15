#include "../../../cland.h"
#include "../../../ccamera.h"
#include "../../../datatable/cresourcedatamgr.h"
#include "../../../baseheader.h"
#include "../../../gameprogress/cgp_maingame.h"
#include "../../../mainapp.h"
#include "../../../userinterface/guicontroller/guimessagebox.h"
#include "client455_language.h"
#include "client455_reward_wire.h"

namespace {
bool submitReward455(const RF455RewardState& state)
{
    std::array<unsigned char, 9> body;
    if (!RF455_MakeRewardSelection(state, body)) return false;
    auto* net = _GetNetworkMgr();
    auto* eventProcessor = net
        ? static_cast<CNetMsgProcessor_Event*>(net->GetNetMsgProcessor(NMP_EVENT))
        : nullptr;
    const int endpoint = net ? net->GetActiveServerID() : GST_NONE;
    if (!eventProcessor || endpoint < 0 || endpoint >= MAX_GAME_SERVER ||
        !net->IsConnectedToServer(static_cast<BYTE>(endpoint))) {
        const auto* text = RF455_GetNormalLanguagePack()->get(0xdedu);
        if (*text) _SetSystemMsg("%s", text);
        return false;
    }
    return eventProcessor->SendNetMessage(33, body.data(), static_cast<int>(body.size())) != FALSE;
}

bool showRewardOffer455(std::size_t packetSize, const char* packetBody)
{
    std::uint32_t ordinal;
    if (packetSize < sizeof(_MSG_HEADER) ||
        !RF455_ReadRewardOfferOrdinal(packetBody, packetSize - sizeof(_MSG_HEADER), ordinal))
        return false;
    auto* game = dynamic_cast<CGP_MainGame*>(_GetMainApp()->GetGameProgress455());
    if (!game || !game->IsCreated()) return false;
    RF455PremiumOffer offer;
    if (!RF455_GameItems().makePremiumOffer(ordinal, offer)) return false;
    auto& window = game->RewardWindow455();
    window.SetSubmit455(submitReward455);
    return window.Present455(ordinal, offer);
}

bool showRewardResult455(std::size_t packetSize, const char* packetBody)
{
    if (!packetBody || packetSize <= sizeof(_MSG_HEADER)) return false;
    // 0x1A7CD0 maps two statuses to different localized message sinks.
    const auto* lang = RF455_GetNormalLanguagePack();
    switch (static_cast<unsigned char>(packetBody[0])) {
    case 0:
        if (const auto* text = lang->get(0xe7au)) {
            if (*text) _SetSystemMsg("%s", text);
        }
        break;
    case 1:
        if (const auto* text = lang->get(0xcccu)) {
            if (*text) _GUIMessageBox(nullptr, const_cast<char*>(text), 0xd0ffffffu, 0,
                                      DLG_STYLE_OK, 0xffffffffu, FALSE, FALSE, TRUE);
        }
        break;
    }
    return true;
}
}
