// Named views of confirmed fields in the SAME source455 allocation.
// MSVC anonymous unions permit the existing byte kernels and normal consumers
// to share storage. This never overlays a legacy776byte object.
struct RF455CharacterStorage {
    union {
        struct { RF455KnownModelPrefix prefix; unsigned char tail[388]; };
        struct {
            DWORD m_ID; char m_Name[256]; DWORD ownsMeshes,m_Load,opaque268;
            RF455CharacterStorage* legacy_bone; char legacy_texture_path[256];
            DWORD m_MaxObj; RF455MeshStorage* m_pMesh; unsigned char opaque540[132];
            DWORD m_Frame,m_OMaxFrame; unsigned char opaque680[24];
            DWORD m_Transition,m_TransitionStart,m_TransFrame,m_TransTime;
            D3DMATERIAL9 m_Material; DWORD opaque788; float m_Alpha;
            unsigned char opaque796[392];
        };
    };
    int IsHaveEffect(); // Open455contract; no default-success implementation.
};
static_assert(offsetof(RF455CharacterStorage,m_Load)==264 && offsetof(RF455CharacterStorage,m_pMesh)==536,"455 model fields");
static_assert(offsetof(RF455CharacterStorage,m_Frame)==672 && offsetof(RF455CharacterStorage,m_Transition)==704 && offsetof(RF455CharacterStorage,m_Alpha)==792,"455 pose fields");
