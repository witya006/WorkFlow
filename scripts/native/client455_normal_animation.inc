struct RF455AnimationStorage {
    union {
        unsigned char bytes[284];
        struct {
            DWORD m_Load;unsigned char loadAttempted;char m_Name[256];unsigned char opaque261[3];
            DWORD m_Ident;void* imported;RF455AnimationData* tracks;DWORD maximum;void* m_pExtra;
        };
    };
    bool LoadRealAnimation(bool synchronous);
};
static_assert(offsetof(RF455AnimationStorage,m_Name)==5 && offsetof(RF455AnimationStorage,m_Ident)==264 && offsetof(RF455AnimationStorage,m_pExtra)==280,"455 animation fields");
