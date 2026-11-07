//405100: every resource byte80..583 is copied,including inline100-byte
//animation control/padding and the84-byte secondary state. CObject's copy
//constructor handles its own members and preserves destination padding5..7.
CResObject::CResObject(const CResObject& source):CObject(source){
    std::memcpy(m_vecPos,source.m_vecPos,sizeof(CResObject)-sizeof(CObject));
}
static_assert(sizeof(CResObject)==584,"455 resource base size");
