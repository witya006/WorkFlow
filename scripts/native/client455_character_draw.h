#pragma once
#include "client455_draw.h"
#include "client455_character_manager.h"
#include <vector>

// Explicit dependencies of the recovered draw route. Static CRT transcendental
// functions are providers: a modern CRT provider does not prove original bits.
struct RF455CharacterDrawMath {
    RF455MeshMatrixOps matrix;
    void* (__stdcall *transform3)(void*,const void*,const void*);
    void* (__stdcall *ortho)(void*,float,float,float,float);
    unsigned (__stdcall *ticks)();
    void (__cdecl *sineFloat)(float*,const float*);
    void (__cdecl *cosineFloat)(float*,const float*);
};
struct RF455CharacterDrawGlobals {
    float phase=0;unsigned previousTick=0,bumpEpoch=0;
    float dynamicVertices[2048][8]={}; // zero-initialized persistent11DC9E0 scratch.
};
#pragma pack(push,4)
struct RF455TransparentPacket {
    float depth;RF455TransparentPacket* next;unsigned boneCount;
    float palette[30][16];
    IDirect3DBaseTexture9* primary;IDirect3DBaseTexture9* secondary;
    IDirect3DVertexBuffer9* buffer;float alpha;unsigned vertexCount;float frequency;
    float material[17];unsigned special,textureFactor,secondPass,inverted,effect,opaque2044;
    float scroll;RF455MeshStorage* mesh;unsigned part;
};
#pragma pack(pop)
static_assert(sizeof(RF455TransparentPacket)==2060 && offsetof(RF455TransparentPacket,primary)==1932 && offsetof(RF455TransparentPacket,mesh)==2052,"455 transparency record");
struct RF455CharacterTransparency {
    std::vector<RF455TransparentPacket> entries;
    unsigned count=0;RF455TransparentPacket* head=nullptr;
    float sortView[16];
};
struct RF455CharacterDrawContext {
    RF455CharacterDrawState state;
    RF455ShaderManager* shaders;unsigned selected=0xffffffffu;
    RF455VertexBufferPool* vertices36;RF455VertexBufferPool* vertices64;RF455IndexBufferPool* indices;
    RF455CharacterDrawMath math;RF455CharacterDrawGlobals* globals;
    RF455CharacterTransparency* transparent;RF455MeshMemoryOps memory;
    float* projection;const float* view;
    bool useFvf=false;DWORD fvf=0;bool batchEnabled=false;
    bool orthographic=false;float width=0,height=0,orthoScale=1;
    //8C2A90 publishes frustum planes into the scene owner, outside Character.
    // Required when orthographic is enabled; never replaced with a success no-op.
    void* projectionOwner=nullptr;void (__cdecl *publishProjection)(void*,const float*,const float*)=nullptr;
    std::vector<RF455CharacterStorage*> capturedModels;
    // Optional observation immediately before actual submissions, for capture.
    void* observer=nullptr;void (__cdecl *beforeDraw)(void*,const RF455MeshStorage*,unsigned)=nullptr;
};
enum RF455CharacterDrawStatus {RF_CHARACTER_DRAW_OK=0,RF_CHARACTER_DRAW_ARGUMENT=1,RF_CHARACTER_DRAW_LIMIT=2,RF_CHARACTER_DRAW_MEMORY=3};
extern "C" {
void RF455_ResetCharacterTransparency(RF455CharacterTransparency*);
int RF455_QueueCharacterTransparency(RF455CharacterTransparency*,const RF455TransparentPacket*,const RF455MeshMatrixOps*);
void RF455_SetCharacterEffectStage(RF455CharacterDrawContext*,unsigned stage,unsigned effect,DWORD textureFactor,float scroll);
RF455CharacterDrawStatus RF455_DrawCharacter455(RF455CharacterDrawContext*,RF455CharacterStorage*,const void* world,const void* translationWorld);
RF455CharacterDrawStatus RF455_FlushCharacterTransparency(RF455CharacterDrawContext*);
RF455CharacterDrawStatus RF455_FlushCharacterMeshBatch(RF455CharacterDrawContext*,RF455MeshStorage*);
//92DB60, including its unusual Vec3Transform(normal,skin) and FVF restoration.
void RF455_DrawDynamicCharacterMesh(RF455CharacterDrawContext*,const RF455MeshStorage*,const void* world,const float* precomputedPalette);
RF455CharacterDrawStatus RF455_DrawCharacterShadow(RF455CharacterDrawContext*,RF455CharacterStorage*,const void* world);
}
