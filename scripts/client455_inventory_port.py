"""Connect the recovered inventory/pack/equipment view owners, retaining explicit gameplay gaps."""

def port_inventory(raw,relative,section,native):
    root='userinterface/gamewindow/guiinventorywindow'
    if relative==root+'.h':
        raw=b'#include "client455_briefing_controls.h"\r\n'+raw
        old=b'#define\tTOTAL_EQUIP_ITEM\t14'
        if raw.count(old)!=1:raise ValueError('Inventory equipment view capacity')
        raw=raw.replace(old,b'#define\tTOTAL_EQUIP_ITEM\t16')
        old=b'CGUIObjectAni\t\t\tm_uiAniTitleBar;'
        if raw.count(old)!=1:raise ValueError('Inventory common header owner')
        raw=raw.replace(old,b'RF455GuiAnimatedImage\tm_uiAniTitleBar;')
        for anchor,method in (
            (b'CGUIItem *\tGetItem( WORD pi_wSocketIndex );',
             b'bool SlotCenter455(BYTE slot, POINT& point) const;'),
            (b'CGUIItem *\tGetItem( BYTE pi_byPackIndex, BYTE pi_bySocketIndex );',
             b'bool SlotCenter455(BYTE slot, POINT& point) const;\r\n\tvoid HighlightEquipSlot455(BYTE slot);'),
        ):
            if raw.count(anchor) not in (1,2):raise ValueError('Inventory slot geometry anchors')
            raw=raw.replace(anchor,anchor+b'\r\n\t'+method,1)
        return raw,True
    if relative!=root+'.cpp':return raw,False
    equip_match=b'CGUIEquipWindow::IsEquipableItem( EquipItemBoard pi_eItemBoard, DWORD pi_dwItemID )'
    start=raw.index(b'{',raw.index(equip_match))+1
    raw=raw[:start]+b'\n\tif (static_cast<unsigned>(pi_eItemBoard) >= 14) return FALSE;'+raw[start:]
    bag_mouse=b'CGUIInventoryBoard::MouseEvent( _mouse_event & event )'
    first,last=section(raw,bag_mouse,bag_mouse)
    mouse=raw[first:last]
    source=b'\t\tif( m_bySelectedSocketIndex == NONE_SOCKET_INDEX )'
    pos=mouse.index(source)
    after=mouse.index(b'\t\t// add',pos)
    mouse=mouse[:pos]+b'''\t\tBYTE slot = 0;
\t\twhile (slot < TOTAL_INVENTORY && event.source != &m_uiTradeItemMark[slot]) ++slot;
\t\tif (slot == TOTAL_INVENTORY) return;
\t\tm_bySelectedSocketIndex = slot;

'''+mouse[after:]
    pos=mouse.index(b'\t\t\tfor( int i = 0; i < TOTAL_INVENTORY; ++i )')
    after=mouse.index(b'\t\t\tif( IsEmpty(',pos)
    mouse=mouse[:pos]+mouse[after:]
    mouse=mouse.replace(b'\t\t\tif( event.source != &m_uiTradeItemMark[m_bySelectedSocketIndex] )\r\n\t\t\t\treturn;\r\n',b'')
    mouse=mouse.replace(b' || event.source != &m_uiTradeItemMark[m_bySelectedSocketIndex]',b'')
    raw=raw[:first]+mouse+raw[last:]
    methods={
        'CGUIInventoryWindow':['Init','SetSprite','SetEquipWindow','SetOpenOnlyOnePack','SetPackState','SetOwnDalant','SetOwnGold','MouseEvent','PickingObjectEvent','Open','Close','OpenDockingPack'],
        'CGUIInventoryBoard':['Init','SetSprite','SetTradeItem','SetUselessSocket','SetUselessItem'],
        'CGUIEquipWindow':['Init','SetSprite','SetTradeItem','SetUselessSocket','SetEmpty','Open','Close'],
    }
    for klass,names in methods.items():
        for name in names:
            sig=(klass+'::'+name+'(').encode();first,last=section(raw,sig,sig)
            start=raw.rfind(b'void',0,first)
            if raw[start:first].strip()!=b'void':raise ValueError('Inventory function boundary '+klass+'::'+name)
            raw=raw[:start]+b'// Recovered455 view method below.\n'+raw[last:]
    sig=b'CGUIInventoryWindow::AddPack(';first,last=section(raw,sig,sig);start=raw.rfind(b'BOOL',0,first)
    if raw[start:first].strip()!=b'BOOL':raise ValueError('Inventory AddPack boundary')
    raw=raw[:start]+b'// Recovered455 AddPack below.\n'+raw[last:]
    for klass in ['CGUIInventoryBoard','CGUIEquipWindow']:
        sig=(klass+'::Draw(').encode();first,last=section(raw,sig,sig);start=raw.rfind(b'BOOL',0,first)
        if raw[start:first].strip()!=b'BOOL':raise ValueError('Inventory inherited Draw boundary '+klass)
        raw=raw[:start]+b'//455 inherits the ordinary window draw route.\n'+raw[last:]
    raw=b'#include "client455_language.h"\n#include "client455_nation_paths.h"\n#include "client455_text_metrics.h"\n#include <stdexcept>\n'+raw
    return raw+b'\n'+(native/'client455_inventory.inc').read_bytes(),True
