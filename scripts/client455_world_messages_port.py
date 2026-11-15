"""Load the 455 message, transport, and item catalogs during Login."""


def port_world_messages(raw, relative):
    def insert_after(data, anchor, addition):
        if data.count(anchor) != 1:
            raise ValueError('World messages bootstrap boundary: ' + repr(anchor))
        return data.replace(anchor, anchor + nl + addition)

    nl = b'\r\n' if b'\r\n' in raw else b'\n'
    if relative == 'mainapp.h':
        raw = insert_after(raw, b'RF455IconLinks m_iconLinks455;',
                           b'\tRF455WorldMessages m_worldMessages455;' + nl +
                           b'\tRF455EventShipCatalog m_eventShip455;' + nl +
                           b'\tRF455SpecialStoreCatalog m_specialStore455;' + nl +
                           b'\tRF455ItemCollectionCatalog m_itemCollection455;')
        raw = insert_after(raw, b'RF455IconLinks& IconLinks455(){return m_iconLinks455;}',
                           b'\tRF455WorldMessages& WorldMessages455(){return m_worldMessages455;}' + nl +
                           b'\tRF455EventShipCatalog& EventShip455(){return m_eventShip455;}' + nl +
                           b'\tRF455SpecialStoreCatalog& SpecialStore455(){return m_specialStore455;}' + nl +
                           b'\tRF455ItemCollectionCatalog& ItemCollection455(){return m_itemCollection455;}')
        includes = nl.join([b'#include "client455_world_messages.h"', b'#include "client455_event_ship.h"',
                            b'#include "client455_shop_collection.h"', b''])
        return includes + raw, True
    if relative == 'mainapp.cpp':
        return insert_after(raw, b'\tm_cNetworkMgr.Destroy();',
                            nl.join([b'\tm_worldMessages455.Clear();', b'\tm_eventShip455.Clear();',
                                     b'\tm_specialStore455.Clear();', b'\tm_itemCollection455.Clear();'])), True
    if relative == 'gameprogress/cgp_login.cpp':
        tutorial = b"        if (!_GetAvatarDummy(m_Course)->GetSkipTutorial455()) {"
        if raw.count(tutorial) != 1:
            raise ValueError('Quest localization selection boundary')
        raw = raw.replace(tutorial, nl.join([
            b'        RF455_GameItems().selectQuestTextForRace(_GetNetworkMgr()->m_worldEntry455.quest,',
            b'                                                _GetAvatarDummy(m_Course)->GetRace());',
            tutorial,
        ]))
        raw = insert_after(raw, b'_GetCharDataMgr()->LoadData();', nl.join([
            b'                RF455_GameItems().loadQuestFile(_GetNetworkMgr()->m_worldEntry455.quest);',
            b'                const auto* messageNation455 = RF455_GetNormalNationPaths();',
            b'                const std::string messageData455 = messageNation455->dataRoot;',
            b'                _GetMainApp()->EventShip455().Load("./DataTable/EventShip.edf",',
            b'                    messageNation455->configured ? (messageData455 + "/NDEventShip.edf").c_str() : nullptr);',
            b'                auto& messages455 = _GetMainApp()->WorldMessages455();',
            b'                if (messageNation455->configured)',
            b'                    messages455.LoadMonsters((messageData455 + "/NDMsgMonster.edf").c_str());',
        ]))
        raw = insert_after(raw, b'RF455_GameItems().loadItemTimerFile();', nl.join([
            b'                RF455_GameItems().loadItemPremiumFile();',
            b'                if (messageNation455->configured)',
            b'                    messages455.LoadEvents("./DataTable/MsgEvent.edf",',
            b'                        (messageData455 + "/NDMsgEvent.edf").c_str());',
        ]))
        land = b'_GetLand()->LoadData();'
        if raw.count(land) != 1:
            raise ValueError('Shop and collection bootstrap boundary')
        raw = raw.replace(land, nl.join([
            b'_GetMainApp()->SpecialStore455().Load("./DataTable/SpecialStore.edf");',
            b'                _GetMainApp()->ItemCollection455().Load("./DataTable/ItemCollection.edf",',
            b'                    messageNation455->configured ? (messageData455 + "/NDItemCollection.edf").c_str() : nullptr);',
            b'                ' + land,
        ]))
        includes = nl.join([b'#include "client455_nation_paths.h"', b'#include <string>', b''])
        return includes + raw, True
    return raw, False
