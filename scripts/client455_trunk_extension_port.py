"""Load the common Trunk extension table at ordinary board startup."""


def port_trunk_extension(raw, relative):
    newline = b'\r\n' if b'\r\n' in raw else b'\n'

    def insert_after(data, anchor, addition):
        if data.count(anchor) != 1:
            raise ValueError(f'Trunk extension boundary changed in {relative}: {anchor!r}')
        return data.replace(anchor, anchor + newline + addition)

    if relative == 'mainapp.h':
        raw = insert_after(raw, b'#include "client455_shop_collection.h"',
                           b'#include "client455_trunk_extension.h"')
        raw = insert_after(raw, b'\tRF455ItemCollectionCatalog m_itemCollection455;',
                           b'\tRF455TrunkExtensionCatalog m_trunkExtension455;')
        raw = insert_after(raw, b'\tRF455ItemCollectionCatalog& ItemCollection455(){return m_itemCollection455;}',
                           b'\tRF455TrunkExtensionCatalog& TrunkExtension455() { return m_trunkExtension455; }')
        return raw, True
    if relative == 'mainapp.cpp':
        raw = insert_after(raw, b'\tm_itemCollection455.Clear();', b'\tm_trunkExtension455.Clear();')
        return raw, True
    if relative == 'gameprogress/cgp_maingame.cpp':
        return insert_after(raw, b'\t_GetGBM()->Create();',
                            b'\t_GetMainApp()->TrunkExtension455().Load("./DataTable/TrunkExted.edf");'), True
    return raw, False
