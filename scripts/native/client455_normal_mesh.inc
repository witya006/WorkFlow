#pragma pack(push,1)
struct CharacterEffectSlot {float m_X,m_Y,m_Z;DWORD m_ID;};
#pragma pack(pop)
static_assert(sizeof(CharacterEffectSlot)==16,"455 particle/entity slot");
#pragma pack(push,1)
struct RF455MeshStorage {
    union {
        unsigned char bytes[5803];
        struct {
            char m_Name[256],parentName[256];bool m_HaveParent;
            unsigned char opaque513[5];RF455MeshStorage* m_pParent;DWORD m_BlendNum;
            unsigned char opaque526[120];D3DXMATRIX m_pMatBlend[30];
            unsigned char opaque2566[2264];D3DXMATRIX m_MatResult,m_BefMatResult,m_BefMatLocal;
            unsigned char opaque5022[109];float m_Alpha;unsigned char opaque5135[668];
        };
    };
    // Native kernels perform the confirmed constructor writes explicitly.
    // D3DXMATRIX has a nontrivial C++ constructor, so declare this union owner.
    RF455MeshStorage() noexcept {}
    // Views into CURRENT effect5455 (particle208/entity256),not old inline slots.
    CharacterEffectSlot* particleSlots();
    CharacterEffectSlot& entitySlot();
    int IsHaveEffect();
    void InitEffect();
};
#pragma pack(pop)
static_assert(offsetof(RF455MeshStorage,m_pParent)==518 && offsetof(RF455MeshStorage,m_BlendNum)==522,"455 binding fields");
static_assert(offsetof(RF455MeshStorage,m_pMatBlend)==646 && offsetof(RF455MeshStorage,m_MatResult)==4830 && offsetof(RF455MeshStorage,m_BefMatResult)==4894 && offsetof(RF455MeshStorage,m_BefMatLocal)==4958,"455 pose matrices");
