// Class indices/names from455. The board call site is preserved;the full
// CreateClassSkill implementation and455CharInfo layout remain separate gaps.
void CAvatar::RefreshClassNames455(BYTE slot,bool stringSetter){
    if(slot==0){
        if(m_dwClassDTIndex[1]==ID_INVALID){
            SetAdvancedClassName455(m_dwClassDTIndex[0]);
            // Numeric412050 intentionally does not update the base name in
            // this branch;string412140 updates both,in this order.
            if(stringSetter)SetPrimaryClassName455(m_dwClassDTIndex[0]);
        }else SetPrimaryClassName455(m_dwClassDTIndex[0]);
    }else if(slot==1){
        SetPrimaryClassName455(m_dwClassDTIndex[0]);
        SetAdvancedClassName455(m_dwClassDTIndex[1]);
    }
}
void CAvatar::SetPrimaryClassName455(DWORD index){
    const auto row=_GetCharDataMgr()->GetClassData455ByIndex(index);
    if(row.data&&_GetCharInfoWindow())SetClassName(const_cast<char*>(reinterpret_cast<const char*>(row.data+112)));
}
void CAvatar::SetAdvancedClassName455(DWORD index){
    const auto row=_GetCharDataMgr()->GetClassData455ByIndex(index);
    if(row.data&&_GetCharInfoWindow())_GetCharInfoWindow()->SetInfoText455(4,const_cast<char*>(reinterpret_cast<const char*>(row.data+112)));
}
