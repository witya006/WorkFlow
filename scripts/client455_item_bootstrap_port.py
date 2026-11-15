"""Connect the455item owners to the actual Login bootstrap and ItemDataMgr."""
def port_item_bootstrap(raw,relative,section):
    if relative=='datatable/citemdatamgr.h':
        raw=b'#include "client455_item_payloads.h"\n'+raw
        anchor=b'\tBOOL\t\tLoadData( void );'
        if raw.count(anchor)!=1:raise ValueError('Ordinary item loading API changed')
        return raw.replace(anchor,anchor+b'\n\tBOOL LoadBootstrap455();\n\tRF455ItemDataSpan GetData455(DWORD,DWORD);'),True
    if relative=='datatable/citemdatamgr.cpp':
        anchor=b'#include "CItemDataMgr.h"'
        if raw.count(anchor)!=1:raise ValueError('Ordinary item includes changed')
        raw=raw.replace(anchor,anchor+b'\n#include "client455_client_items.h"\n#include "network/cnetworkmgr.h"')
        signature=b'CItemDataMgr::LoadData( void )';first,last=section(raw,signature,signature)
        raw=raw[:first]+b'CItemDataMgr::LoadData( void ){return RF455_GameItems().loadItemFiles()?TRUE:FALSE;}'+raw[last:]
        raw+=b'''
BOOL CItemDataMgr::LoadBootstrap455(){
    auto& items=RF455_GameItems();
    items.cashLoadResult=items.loadCashFiles(_GetNetworkMgr()->m_worldEntry455.cashShop);
    items.setEffectLoadResult=items.loadSetEffectFile();
    return LoadData();
}
RF455ItemDataSpan CItemDataMgr::GetData455(DWORD kind,DWORD index){return RF455_GameItems().data.getItem(kind,index);}
'''
        return raw,True
    if relative=='gameprogress/cgp_login.cpp':
        anchor=b'_GetItemDataMgr()->LoadData();'
        timer_anchor=b'_GetCharDataMgr()->LoadData();'
        if raw.count(anchor)!=1 or raw.count(timer_anchor)!=1:
            raise ValueError('Ordinary Login item bootstrap boundary changed')
        raw=b'#include "client455_client_items.h"\n'+raw
        raw=raw.replace(anchor,b'_GetItemDataMgr()->LoadBootstrap455();')
        return raw.replace(timer_anchor,timer_anchor+b'\n                RF455_GameItems().loadItemTimerFile();'),True
    if relative=='gameobject/board/itemboard/cinventoryboard.cpp':
        signature=b'CInventoryBoard::UI_PickUpItemRequest( CGroundItem * pi_pGroundItem )'
        first,last=section(raw,signature,signature)
        body=raw[first:last]
        anchor=b'if( pi_pGroundItem->IsSplitable() )'
        if body.count(anchor)!=1:raise ValueError('455 timer pickup stacking boundary changed')
        body=body.replace(anchor,b'''RF455ItemTimer timer455{};
    const bool hasTimer455 = RF455_GameItems().findItemTimer(pi_pGroundItem->GetItemKind(),
        pi_pGroundItem->GetDTCode(), timer455);
    if( pi_pGroundItem->IsSplitable() && !hasTimer455 )''')
        return b'#include "client455_client_items.h"\n'+raw[:first]+body+raw[last:],True
    return raw,False
