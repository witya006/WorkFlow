"""Connect typed455default equipment without casting legacy ITEM_DATA."""
def port_equipment(raw,relative,section):
    def once(old,new):
        nonlocal raw
        if raw.count(old)!=1:raise ValueError('Equipment anchor '+relative+':'+repr(old))
        raw=raw.replace(old,new)
    if relative=='character/avatar/cavatar.h':
        raw=b'#include "client455_equipment_object.h"\n'+raw
        once(b'CEquipItem\t\tm_pDefaultItem[MAX_DEFAULT_PART];',b'RF455EquipmentObject m_defaultItems455[6];\n\tCEquipItem\t\tm_pDefaultItem[MAX_DEFAULT_PART];')
        once(b'CEquipItem*\tGetDefaultItem( BYTE pi_byPartType );',b'''CEquipItem*\tGetDefaultItem( BYTE pi_byPartType );
    RF455EquipmentObject* GetDefaultItem455(BYTE part){return part<6&&!m_defaultItems455[part].IsEmpty()?&m_defaultItems455[part]:NULL;}''')
        return raw,True
    if relative=='character/avatar/cavatar_etc.cpp':
        first,last=section(raw,b'CAvatar::SetDefaultItem( BYTE pi_byPartType, DWORD pi_dwDTIndex )',b'CAvatar::SetDefaultItem( BYTE pi_byPartType, DWORD pi_dwDTIndex )')
        raw=raw[:first]+b'''CAvatar::SetDefaultItem( BYTE pi_byPartType, DWORD pi_dwDTIndex ){
        if(pi_byPartType>=6)return FALSE;
        auto& object=m_defaultItems455[pi_byPartType];if(!object.IsEmpty())object.Clear();
        if(!object.Create455(pi_byPartType,pi_dwDTIndex))return FALSE;
        auto* item=RF455_GameItems().create(0,pi_byPartType,pi_dwDTIndex);if(!item)return FALSE;
        item->header().serial=object.GetIndex();item->header().field8=object.GetServerIndex();
        object.SetItem455(item);return TRUE;
    }'''+raw[last:]
        return raw,True
    return raw,False
