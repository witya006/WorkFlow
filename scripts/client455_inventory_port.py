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
        return raw,True
    if relative!=root+'.cpp':return raw,False
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
