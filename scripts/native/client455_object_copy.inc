//405DD0: copy the selected members,retain destination padding5..7.
CObject::CObject(const CObject& source){
    m_byObjectTypeID=source.m_byObjectTypeID;
    m_dwIndex=source.m_dwIndex;m_dwServerIndex=source.m_dwServerIndex;
    std::memcpy(m_pName,source.m_pName,sizeof(m_pName));
}
static_assert(sizeof(CObject)==80,"455 common object includes its64-byte name");
