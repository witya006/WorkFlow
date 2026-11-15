#pragma once
// Source facade for normal client consumers. Its wrapper classes are OWN APIs,
// not a claim of the original C++ ABI. All record allocations use455layouts.
#include <d3dx9.h>
#include "client455_renderer_owner.h"
#include "client455_animation_manager.h"
#include "client455_pose.h"
#include "client455_effect_tables.h"
#include "client455_effects.h"
using CHARACTEROBJECT=RF455CharacterStorage;
using ObjectMesh=RF455MeshStorage;
using ChAnimation=RF455AnimationStorage;
enum {MAXPARTICLE=3,MAX_PATTERN_SIZE=36};

class CObjectManager {
public:
    RF455CharacterManager native;
    CObjectManager();~CObjectManager();
    CObjectManager(const CObjectManager&)=delete;CObjectManager& operator=(const CObjectManager&)=delete;
    void AddCharacter(CHARACTEROBJECT*);void Clear();
    void DeleteCharacter(unsigned long);void DeleteCharacter(char*);
    CHARACTEROBJECT* GetCharacter(unsigned long);CHARACTEROBJECT* GetCharacter(char*);
    unsigned long GetID(char*);
};
class AnimationManager {
public:
    RF455AnimationManager native;
    AnimationManager();~AnimationManager();
    AnimationManager(const AnimationManager&)=delete;AnimationManager& operator=(const AnimationManager&)=delete;
    bool AddAnimation(char*);void DeleteAnimation2(unsigned long);void DeleteAnimation(char*);
    ChAnimation* GetAnimationData(unsigned long);ChAnimation* GetAnimationData(char*);
    ChAnimation* GetAnimationDataByNoPath(char*);unsigned long GetAnimationID(char*);
    int Init();
};
class TextureManager {
public:
    explicit TextureManager(RF455TextureManager& value):native(&value){}
    RF455TextureManager* native;
};
class CRender {
public:
    CRender();~CRender();
    CRender(const CRender&)=delete;CRender& operator=(const CRender&)=delete;
    RF455CharacterRenderer native;
    TextureManager m_TM;
    void SetMipMap(DWORD);IDirect3DTexture9* GetShadow(DWORD);
    void DrawCharacter(CHARACTEROBJECT*,float*,float);
    void DrawCharacter(CHARACTEROBJECT*,float*,float,float);
    void DrawCharacter(CHARACTEROBJECT*,float*,float,float,float);
    void DrawCharacter(CHARACTEROBJECT*,float*,float,float,float,bool);
    void DrawCharacterMat(CHARACTEROBJECT*,D3DXMATRIX*,float);
    bool CollectShadowGeometry455(const CHARACTEROBJECT*,const float* position,float yaw,float scale,float opacity,
        RF455CharacterShadowSink,void* owner);
    void SetOverlayTextureMatrix455(const D3DXMATRIX&,bool environment);
    void DrawCharacterOverlay455(CHARACTEROBJECT*,float*,float yaw,float scale,float scroll,bool unscaled);
    void DrawCharacterShadow(CHARACTEROBJECT*,float*,float,float);
    void DrawCharacterShadow(CHARACTEROBJECT*,float*,float,float,float);
    bool LoadRealData(CHARACTEROBJECT*,TextureManager*);
    bool LoadRealData(CHARACTEROBJECT*,TextureManager*,bool);
    RF455PoseStatus UpdatePose455(CHARACTEROBJECT*);
    void FrameMove(CHARACTEROBJECT*);void InitEffect(CHARACTEROBJECT*);
    int BeginShadow(unsigned long);void EndShadow();
    void SetLight(D3DLIGHT9);void SetState();void UnSetState();
    void FlushTransparency();
    static CRender& GetRender();
    struct Runtime;
    Runtime* runtime;
};
class ChInterface:public CRender {
public:
    ChInterface();void InitCharacter(IDirect3DDevice9*);
    ChAnimation* AddAnimationData(AnimationManager*,char*);
    bool IsLoadAnimation(ChAnimation*);
    void MatchAnimationToMesh(ChAnimation*,CHARACTEROBJECT*);
    CHARACTEROBJECT* LoadMeshData(CObjectManager*,char*,bool,CHARACTEROBJECT*);
    void SetTexPath(CHARACTEROBJECT*,char*);void SetAlpha(CHARACTEROBJECT*,float);
    float GetAlpha(CHARACTEROBJECT*);void SetMaterial(CHARACTEROBJECT*,D3DMATERIAL9&);
    void AnimationReset(CHARACTEROBJECT*);void RematchParent(CHARACTEROBJECT*,CHARACTEROBJECT*);
    int ImportBoundBox(char*,float*,float*);void SetEyeVec(char*,CHARACTEROBJECT*,D3DXMATRIX);
    // Source APIs for the recovered RVP registry path;not original C++ ABI.
    RF455CharacterManager* CreatePart455(const char*);
    CHARACTEROBJECT* RegisterBone455(const char*);CHARACTEROBJECT* LookupBone455(const char*);
    CHARACTEROBJECT* RegisterMesh455(RF455CharacterManager*,const char*,CHARACTEROBJECT*);
    CHARACTEROBJECT* LookupMesh455(RF455CharacterManager*,const char*);
    void ModelBounds455(CHARACTEROBJECT*,float*,float*);
};
// Own public facade; real shared transparency storage belongs to the Hub.
class AlphaMeshManager {public:void DrawAlpahMesh();};
class EffectList {public:RF455EffectFiles native;RF455EffectRead lastRead={};void LoadEffectFileList(char*);void SetEffect(CHARACTEROBJECT*,DWORD);};
class EffectObjectManager {public:static void LoadEffect(char*);static int SetPartEffect(CHARACTEROBJECT*,char*,int);};
class EffectFileList {public:RF455EffectFiles native;RF455EffectRead lastRead={};void LoadEffectFileList(char*);};
class EffectPatternList {public:
    RF455EffectPatterns native;RF455EffectTableRead lastRead={};
    EffectPatternList();void LoadEffectPatternList(char*);
};
class ItemEffectList {public:
    RF455EffectItems native;RF455EffectTableRead lastRead={};
    void LoadItemListFile(char*);
};
struct CHMEMORYINFO {DWORD m_TextureSize,m_TextureNum,m_VertexSize,m_VetexNum,m_AniSize,m_ObjectNum,m_ObjectSize;};
extern AlphaMeshManager g_AMeshManager;
// Read-only own view of confirmed counters. No private original global overlay.
CHMEMORYINFO RF455_GetCharacterMemoryInfo();
extern EffectList g_EFFMonList,g_EFFNPCList,g_EFFUnitList,g_EFFKitList;
extern EffectFileList g_EffectFileList;
extern ItemEffectList g_EffectItemList;
extern EffectPatternList g_PatternList;
bool IsHaveMeshEffect(CHARACTEROBJECT*,unsigned long,unsigned long,unsigned long=0);
void SetMeshEffect(CHARACTEROBJECT*,unsigned long,unsigned long,unsigned long=0);
extern float stTime,stLoopTime,stRealTime;
void _R3CalculateTime();
int IsBBoxInFrustum(float*,float*,float (*)[4]);
void SetFustumNormalPlane(float (*)[4],D3DXMATRIX&);
static_assert(sizeof(CHARACTEROBJECT)==1188 && sizeof(ObjectMesh)==5803 && sizeof(ChAnimation)==284,"Normal455records");
