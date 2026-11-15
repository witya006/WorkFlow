"""Attach the recipe catalog to ordinary MainGame board startup."""


def port_item_combine(raw, relative):
    newline = b'\r\n' if b'\r\n' in raw else b'\n'

    def insert_after(data, anchor, addition):
        if data.count(anchor) != 1:
            raise ValueError(f'ItemCombine boundary changed in {relative}: {anchor!r}')
        return data.replace(anchor, anchor + newline + addition)

    if relative == 'mainapp.h':
        raw = insert_after(raw, b'#include "client455_trunk_extension.h"',
                           b'#include "client455_item_combine.h"')
        raw = insert_after(raw, b'\tRF455TrunkExtensionCatalog m_trunkExtension455;',
                           b'\tRF455ItemCombineCatalog m_itemCombine455;')
        raw = insert_after(raw, b'\tRF455TrunkExtensionCatalog& TrunkExtension455() { return m_trunkExtension455; }',
                           b'\tRF455ItemCombineCatalog& ItemCombine455() { return m_itemCombine455; }')
        return raw, True
    if relative == 'mainapp.cpp':
        return insert_after(raw, b'\tm_trunkExtension455.Clear();', b'\tm_itemCombine455.Clear();'), True
    if relative == 'gameprogress/cgp_maingame.cpp':
        anchor = b'\t_GetItemUpgradeBoard()->AddPack( 0 );'
        startup = newline.join((b'\tauto& itemCombine = _GetMainApp()->ItemCombine455();',
                               b'\tif (!itemCombine.RecipeCount())',
                               b'\t\titemCombine.Load("./DataTable/ItemCombine.edf");'))
        raw = insert_after(raw, anchor, startup)
        return raw, True
    return raw, False
