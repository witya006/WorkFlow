"""Expose actual payload metadata to the existing inventory icon owner."""
def port_item_metadata(raw,relative,section):
    if relative=='userinterface/gamewindow/guiinventorywindow.h':
        anchor=b'\tCGUIInventoryBoard();'
        if raw.count(anchor)!=1:raise ValueError('Inventory metadata API anchor changed')
        raw=b'class CBoardObject;\r\n'+raw.replace(anchor,anchor+b'\r\n\tBOOL TakeInItem455(BYTE slot,CBoardObject* object,BYTE race);\r\n\tBOOL TakeInItemFields455(BYTE,DWORD,DWORD,BYTE,BYTE,BYTE);')
        return raw,True
    if relative=='userinterface/gamewindow/guiinventorywindow.cpp':
        signature=b'CGUIInventoryBoard::TakeInItem( BYTE pi_bySocketIndex, DWORD'
        begin,end=section(raw,signature,signature)
        body=b'CGUIInventoryBoard::TakeInItem(BYTE slot,DWORD itemID,DWORD spriteID,BYTE quantity,BYTE required){return TakeInItemFields455(slot,itemID,spriteID,quantity,required,_GetAvatarRace());}'
        return raw[:begin]+body+raw[end:],True
    return raw,False
