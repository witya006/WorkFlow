#include "Character.h"
#include "client455_normal_renderer_math.h"
#include "client455_normal_accounting.h"
#include "client455_secondary.h"
#include "client455_enhanced_lighting.h"
#include <cstring>
#include <cwchar>
#include <stdexcept>
#include <cmath>
#include <algorithm>
#include <vector>
#include <mmsystem.h>

// Actual engine APIs; these exact declarations are in R3Util.h.
void GetViewMatrix(D3DXMATRIX*);
void GetProjectMatrix(D3DXMATRIX*);

namespace {
RF455MeshMemoryOps memory(){return RF455_CrtMeshMemoryOps();}
void __cdecl diagnostic(void*,const char* message){OutputDebugStringA(message);}
void __cdecl diagnosticWide(void*,const wchar_t* message){OutputDebugStringW(message);}
void __cdecl sine(float* out,const float* in){*out=static_cast<float>(std::sin(static_cast<double>(*in)));}
void __cdecl cosine(float* out,const float* in){*out=static_cast<float>(std::cos(static_cast<double>(*in)));}
unsigned WINAPI ticks(){return timeGetTime();}
std::vector<AnimationManager*>& animations(){static std::vector<AnimationManager*> records;return records;}
int __cdecl animationOwner(void*,const RF455AnimationData* data,RF455PoseSpan* span){
    for(auto* manager:animations())for(auto** at=manager->native.begin;at!=manager->native.end;++at){
        const auto* record=*at;if(!record->imported)continue;const auto ops=RF455_CrtAnimationMemoryOps();
        const auto base=reinterpret_cast<std::uintptr_t>(record->imported);const auto extent=ops.extent(ops.memory.context,record->imported);bool matched=true;
        for(unsigned i=0;i<4;++i)if(data->channel[i].keys){const auto address=reinterpret_cast<std::uintptr_t>(data->channel[i].keys);if(address<base || address-base>extent){matched=false;break;}}
        if(matched){*span={static_cast<const unsigned char*>(record->imported),extent};return 1;}
    }return 0;
}
float added(float a,float b){float out;__asm{fld a
    fadd b
    fstp out}return out;}
// Own deployment adapter. Missing runtime/export throws; original import-failure
// and full CEngineLog semantics are still acceptance gaps.
struct Hub {
    HMODULE module=nullptr;RF455PoseMath pose={};RF455ShaderApi shader={};
    RF455CharacterTextureApi texture={};const RF455CharacterTextureApi* oldTexture=nullptr;
    RF455RendererShared shared={};
    RF455NormalTransformApi transforms={};RF455CharacterDrawMath drawing={};
    RF455SecondaryContext secondary={};RF455SecondaryGlobals secondaryGlobals={};
    RF455CharacterDrawGlobals drawGlobals;RF455CharacterTransparency transparent;
    Hub(){
        wchar_t path[MAX_PATH];const UINT count=GetSystemDirectoryW(path,MAX_PATH);
        if(!count || count+16>=MAX_PATH)throw std::runtime_error("455 D3DX system path");
        std::wcscat(path,L"\\d3dx9_36.dll");module=LoadLibraryW(path);
        if(!module)throw std::runtime_error("455 D3DX runtime missing");
#define LOAD(member,name) member=reinterpret_cast<decltype(member)>(GetProcAddress(module,name));if(!member){FreeLibrary(module);module=nullptr;throw std::runtime_error(name);}
        LOAD(pose.matrix.inverse,"D3DXMatrixInverse");LOAD(pose.matrix.multiply,"D3DXMatrixMultiply");
        LOAD(pose.slerp,"D3DXQuaternionSlerp");LOAD(pose.rotationQuaternion,"D3DXMatrixRotationQuaternion");
        LOAD(shader.compile,"D3DXCompileShader");LOAD(shader.sprite,"D3DXCreateSprite");
        LOAD(texture.memory2D,"D3DXCreateTextureFromFileInMemoryEx");LOAD(texture.memoryCube,"D3DXCreateCubeTextureFromFileInMemoryEx");LOAD(texture.file2D,"D3DXCreateTextureFromFileA");
        LOAD(transforms.rotationZ,"D3DXMatrixRotationZ");transforms.matrix=pose.matrix;
        drawing.matrix=pose.matrix;LOAD(drawing.transform3,"D3DXVec3Transform");LOAD(drawing.ortho,"D3DXMatrixOrthoLH");drawing.ticks=ticks;drawing.sineFloat=sine;drawing.cosineFloat=cosine;
        secondary.math.pose=pose;LOAD(secondary.math.rotationX,"D3DXMatrixRotationX");LOAD(secondary.math.rotationY,"D3DXMatrixRotationY");secondary.math.rotationZ=transforms.rotationZ;LOAD(secondary.math.quaternionMatrix,"D3DXQuaternionRotationMatrix");LOAD(secondary.math.quaternionAxis,"D3DXQuaternionRotationAxis");secondary.math.ticks=ticks;secondary.math.sineFloat=sine;secondary.globals=&secondaryGlobals;
#undef LOAD
        RF455_ConstructShaderManager(&shared.shaders);oldTexture=RF455_SetCharacterTextureApi(&texture);
        RF455_ResetCharacterTransparency(&transparent);
    }
    ~Hub(){RF455_ReleaseShaderManager(&shared.shaders);RF455_ReleaseCharacterDeclarations(&shared.declaration64,&shared.declaration36);RF455_SetCharacterTextureApi(oldTexture);if(module)FreeLibrary(module);}
};
Hub& hub(){static Hub value;return value;}
CRender*& activeRenderer(){static CRender* value=nullptr;return value;}
}
struct CRender::Runtime {
    CRender* previousRenderer=nullptr;
    RF455AnimationMemoryOps animationMemory=RF455_CrtAnimationMemoryOps();
    RF455LegacyScratch scratch;RF455CharacterLoadContext load;
    RF455PoseScratch poseScratch={};RF455PoseContext pose={};
    RF455CharacterDrawContext draw={};D3DXMATRIX view,projection;
    explicit Runtime(RF455CharacterRenderer& owner){
        auto& process=hub();RF455LegacyDiagnostics log={nullptr,diagnostic,diagnosticWide};
        auto& accounting=*RF455_GetNormalCharacterAccounting();
        const auto base=RF455_RendererModelContext(&owner,&animationMemory.memory,&process.pose.matrix,&accounting.meshes,&accounting.buffers);
        load={{base,&owner.vertices36,owner.vertexMode,&scratch,log},{animationMemory,log,&accounting.importedAnimationBytes}};
        pose={&load,process.pose,&poseScratch,0,nullptr,animationOwner,&process.secondary};
        draw.math=process.drawing;draw.memory=animationMemory.memory;draw.globals=&process.drawGlobals;draw.transparent=&process.transparent;
        draw.view=reinterpret_cast<const float*>(&view);draw.projection=reinterpret_cast<float*>(&projection);
    }
    void camera(){GetViewMatrix(&view);GetProjectMatrix(&projection);std::memcpy(draw.transparent->sortView,&view,64);}
};
CObjectManager::CObjectManager(){RF455_ConstructCharacterManager(&native);}
CObjectManager::~CObjectManager(){const auto ops=memory();RF455_DestroyCharacterManager(&native,&ops);}
void CObjectManager::AddCharacter(CHARACTEROBJECT* value){const auto ops=memory();if(!RF455_AddCharacter(&native,value,&ops))throw std::bad_alloc();}
void CObjectManager::Clear(){const auto ops=memory();RF455_ClearCharacters(&native,&ops);}
void CObjectManager::DeleteCharacter(unsigned long id){const auto ops=memory();RF455_DeleteCharacterId(&native,id,&ops);}
void CObjectManager::DeleteCharacter(char* name){const auto ops=memory();RF455_DeleteCharacterName(&native,name,&ops);}
CHARACTEROBJECT* CObjectManager::GetCharacter(unsigned long id){return RF455_FindCharacterId(&native,id);}
CHARACTEROBJECT* CObjectManager::GetCharacter(char* name){return RF455_FindCharacterName(&native,name);}
unsigned long CObjectManager::GetID(char* name){return RF455_CharacterId(&native,name);}
AnimationManager::AnimationManager(){RF455_ConstructAnimationManager(&native);animations().push_back(this);}
AnimationManager::~AnimationManager(){auto& list=animations();list.erase(std::remove(list.begin(),list.end(),this),list.end());const auto ops=memory();RF455_ReleaseAnimationManager(&native,&ops);}
bool AnimationManager::AddAnimation(char* name){const auto ops=memory();return RF455_RegisterAnimation(&native,name,&ops)!=0;}
void AnimationManager::DeleteAnimation2(unsigned long id){const auto ops=memory();RF455_DeleteAnimationId(&native,id,&ops);}
void AnimationManager::DeleteAnimation(char* name){const auto ops=memory();RF455_DeleteAnimationName(&native,name,&ops);}
ChAnimation* AnimationManager::GetAnimationData(unsigned long id){return RF455_FindAnimationId(&native,id);}
ChAnimation* AnimationManager::GetAnimationData(char* name){return RF455_FindAnimationName(&native,name);}
ChAnimation* AnimationManager::GetAnimationDataByNoPath(char* name){return RF455_FindAnimationSuffix(&native,name);}
unsigned long AnimationManager::GetAnimationID(char* name){return RF455_FindAnimationIdByName(&native,name);}
int AnimationManager::Init(){RF455_ResetAnimationCounters(&native);return 0;}
CRender::CRender():m_TM(native.textures),runtime(nullptr){RF455_ConstructCharacterRenderer(&native);auto* previous=activeRenderer();runtime=new Runtime(native);runtime->previousRenderer=previous;activeRenderer()=this;}
CRender::~CRender(){const auto ops=memory();RF455_DestroyCharacterRenderer(&native,&ops);auto* previous=runtime->previousRenderer;delete runtime;if(activeRenderer()==this)activeRenderer()=previous;}
CRender& CRender::GetRender(){if(!activeRenderer())throw std::runtime_error("455 Character renderer unavailable");return *activeRenderer();}
ChInterface::ChInterface():CRender(){}
void ChInterface::InitCharacter(IDirect3DDevice9* device){
    if(!device)throw std::invalid_argument("455 Character device");auto& process=hub();
    const int result=RF455_SetCharacterRendererDevice(&native,&process.shared,device,&process.shader,nullptr);
    if(result<0)throw std::runtime_error("455 Character shader initialization");
    RF455_InitializeEnhancedActorLighting(&process.shared.shaders,&process.shader);
    runtime->load.legacy.rendererMode=native.vertexMode;
    RF455_BindRendererDrawContext(&native,&process.shared,&runtime->draw);
}
void CRender::SetMipMap(DWORD value){native.textures.mipSkip=value;}
bool CRender::LoadRealData(CHARACTEROBJECT* record,TextureManager* textures){return LoadRealData(record,textures,false);}
bool CRender::LoadRealData(CHARACTEROBJECT* record,TextureManager* textures,bool synchronous){
    auto context=runtime->load;if(textures)context.legacy.base.textures=textures->native;
    return RF455_LoadCharacter(record,synchronous,&context)!=0;
}
bool RF455AnimationStorage::LoadRealAnimation(bool synchronous){return RF455_LoadAnimation(this,synchronous,&CRender::GetRender().runtime->load.animation)!=0;}
ChAnimation* ChInterface::AddAnimationData(AnimationManager* manager,char* name){const auto ops=memory();return RF455_GetOrRegisterAnimation(&manager->native,name,&ops);}
bool ChInterface::IsLoadAnimation(ChAnimation* record){return record && record->LoadRealAnimation(false);}
void ChInterface::MatchAnimationToMesh(ChAnimation* animation,CHARACTEROBJECT* record){
    RF455_MatchAnimation(animation,record,&runtime->load);
}
CHARACTEROBJECT* ChInterface::LoadMeshData(CObjectManager* manager,char* name,bool,CHARACTEROBJECT* parent){const auto ops=memory();return RF455_CreateCharacter(&manager->native,name,parent,&ops);}
void ChInterface::SetAlpha(CHARACTEROBJECT* record,float alpha){for(unsigned i=0;i<record->m_MaxObj;++i)record->m_pMesh[i].m_Alpha=alpha;record->m_Alpha=alpha;}
float ChInterface::GetAlpha(CHARACTEROBJECT* record){return record->m_Alpha;}
void ChInterface::SetMaterial(CHARACTEROBJECT* record,D3DMATERIAL9& material){if(record)std::memcpy(&record->m_Material,&material,68);}
void CRender::SetLight(D3DLIGHT9 light){RF455_SetEnhancedActorLightingProtected(false);std::memcpy(&native.light,&light,104);if(native.device)native.device->SetVertexShaderConstantF(10,reinterpret_cast<const float*>(&native.light.Direction),1);}
void CRender::SetState(){RF455_BindRendererDrawContext(&native,&hub().shared,&runtime->draw);RF455_SetCharacterDrawState(&runtime->draw.state);}
void CRender::UnSetState(){RF455_BindRendererDrawContext(&native,&hub().shared,&runtime->draw);RF455_UnsetNormalCharacterState(&runtime->draw.state);}
void CRender::FrameMove(CHARACTEROBJECT* record){
    runtime->pose.blendDuration=0;
    if(record && record->m_pMesh)for(unsigned i=0;i<record->m_MaxObj;++i){void* previous;std::memcpy(&previous,record->m_pMesh[i].bytes+5099,4);if(previous){std::memcpy(&runtime->pose.blendDuration,&native.blendDuration,4);break;}}
    const auto status=RF455_UpdateCharacterPose(record,&runtime->pose);if(status!=RF_POSE_OK)throw std::runtime_error("455 Character pose failure");
}
void CRender::DrawCharacter(CHARACTEROBJECT* record,float* pos,float yaw){DrawCharacter(record,pos,yaw,1,0,false);}
bool CRender::CollectShadowGeometry455(const CHARACTEROBJECT* record,const float* pos,float yaw,float scale,float opacity,
    RF455CharacterShadowSink sink,void* owner){
    if(!record||!pos||!runtime||!record->m_Load||record->opaque268)return false;
    // Deliberately no LoadRealData, camera(), ticks, FrameMove or effect setup.
    // Context/palette work is CPU-only; D3D world/VB/constants remain untouched.
    RF455_BindRendererDrawContext(&native,&hub().shared,&runtime->draw);
    float world[16];RF455_BuildNormalCharacterWorld(world,nullptr,pos,yaw,scale,&hub().transforms);
    return RF455_CollectCharacterShadow455(&runtime->draw,record,world,opacity,sink,owner)==RF_CHARACTER_DRAW_OK;
}
void CRender::DrawCharacter(CHARACTEROBJECT* record,float* pos,float yaw,float scale){DrawCharacter(record,pos,yaw,scale,0,false);}
void CRender::DrawCharacter(CHARACTEROBJECT* record,float* pos,float yaw,float scale,float unused){DrawCharacter(record,pos,yaw,scale,unused,false);}
void CRender::DrawCharacter(CHARACTEROBJECT* record,float* pos,float yaw,float scale,float,bool unscaled){
    if(!record || record->opaque268 || !LoadRealData(record,&m_TM,false))return;
    if(native.effects.active){float low[3],high[3];const auto* b=record->m_pMesh[0].bytes;
        for(unsigned i=0;i<3;++i){float value;std::memcpy(&value,b+5471+4*i,4);low[i]=added(value,pos[i]);std::memcpy(&value,b+5459+4*i,4);high[i]=added(value,pos[i]);}
        const auto* planes=reinterpret_cast<const float(*)[4]>(reinterpret_cast<const unsigned char*>(&native)+8736);
        if(!RF455_IsNormalModelBoxVisible(low,high,planes))return;
    }
    float world[16],translation[16];RF455_BuildNormalCharacterWorld(world,unscaled?translation:nullptr,pos,yaw,scale,&hub().transforms);runtime->camera();timeGetTime();
    if(RF455_DrawCharacter455(&runtime->draw,record,world,unscaled?translation:nullptr)!=RF_CHARACTER_DRAW_OK)throw std::runtime_error("455 Character draw failure");
}
void CRender::DrawCharacterMat(CHARACTEROBJECT* record,D3DXMATRIX* world,float){
    if(!record || !LoadRealData(record,&m_TM,false))return;runtime->camera();
    if(RF455_DrawCharacter455(&runtime->draw,record,world,nullptr)!=RF_CHARACTER_DRAW_OK)throw std::runtime_error("455 Character matrix draw failure");
}
void CRender::SetOverlayTextureMatrix455(const D3DXMATRIX& matrix,bool environment){
    RF455_SelectCharacterShader(runtime->draw.shaders,environment?10:9,&runtime->draw.selected);
    native.device->SetVertexShaderConstantF(92,&matrix.m[0][0],4);
}
void CRender::DrawCharacterOverlay455(CHARACTEROBJECT* record,float* position,float yaw,float scale,float,bool unscaled){
    if(!record||record->opaque268||!LoadRealData(record,&m_TM,false))return;
    if(native.effects.active){
        float low[3],high[3];const auto* first=record->m_pMesh[0].bytes;
        for(unsigned i=0;i<3;++i){float value;std::memcpy(&value,first+5471+4*i,4);low[i]=added(value,position[i]);std::memcpy(&value,first+5459+4*i,4);high[i]=added(value,position[i]);}
        const auto* planes=reinterpret_cast<const float(*)[4]>(reinterpret_cast<const unsigned char*>(&native)+8736);
        if(!RF455_IsNormalModelBoxVisible(low,high,planes))return;
    }
    float world[16],translation[16];
    RF455_BuildNormalCharacterWorld(world,unscaled?translation:nullptr,position,yaw,scale,&hub().transforms);runtime->camera();
    if(RF455_DrawCharacterOverlay455(&runtime->draw,record,world)!=RF_CHARACTER_DRAW_OK)throw std::runtime_error("455 Character overlay draw failure");
}
void CRender::DrawCharacterShadow(CHARACTEROBJECT* record,float* pos,float yaw,float alpha){DrawCharacterShadow(record,pos,yaw,alpha,1);}
void CRender::DrawCharacterShadow(CHARACTEROBJECT* record,float*,float yaw,float,float scale){
    if(!record || !LoadRealData(record,&m_TM,false))return;const float zero[3]={};float world[16];RF455_BuildNormalCharacterWorld(world,nullptr,zero,yaw,scale,&hub().transforms);runtime->camera();
    if(RF455_DrawCharacterShadow(&runtime->draw,record,world)!=RF_CHARACTER_DRAW_OK)throw std::runtime_error("455 Character shadow draw failure");
}
void CRender::FlushTransparency(){runtime->camera();if(RF455_FlushCharacterTransparency(&runtime->draw)!=RF_CHARACTER_DRAW_OK)throw std::runtime_error("455 Character transparency failure");}
AlphaMeshManager g_AMeshManager;
void AlphaMeshManager::DrawAlpahMesh(){CRender::GetRender().FlushTransparency();}
extern "C" void RF455_ReleaseNormalCharacterSharedResources(){
    if(activeRenderer())throw std::runtime_error("455 shared resources still have a renderer owner");
    auto& process=hub();RF455_ReleaseShaderManager(&process.shared.shaders);RF455_ReleaseCharacterDeclarations(&process.shared.declaration64,&process.shared.declaration36);process.shared.shaders.device=nullptr;
}
// Remaining facade methods are intentionally undefined until their455wrappers
// are verified. They are recorded as link blockers, not successful no-ops.
