#include "Character.h"
#include <cstring>
#include <cwchar>
#include <stdexcept>

namespace {
RF455MeshMemoryOps memory(){return RF455_CrtMeshMemoryOps();}
void __cdecl diagnostic(void*,const char* message){OutputDebugStringA(message);}
void __cdecl diagnosticWide(void*,const wchar_t* message){OutputDebugStringW(message);}
// Own deployment adapter. Missing runtime/export throws; original import-failure
// and full CEngineLog semantics are still acceptance gaps.
struct Hub {
    HMODULE module=nullptr;RF455PoseMath pose={};RF455ShaderApi shader={};
    RF455CharacterTextureApi texture={};const RF455CharacterTextureApi* oldTexture=nullptr;
    RF455RendererShared shared={};
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
#undef LOAD
        RF455_ConstructShaderManager(&shared.shaders);oldTexture=RF455_SetCharacterTextureApi(&texture);
    }
    ~Hub(){RF455_ReleaseShaderManager(&shared.shaders);RF455_ReleaseCharacterDeclarations(&shared.declaration64,&shared.declaration36);RF455_SetCharacterTextureApi(oldTexture);if(module)FreeLibrary(module);}
};
Hub& hub(){static Hub value;return value;}
CRender*& activeRenderer(){static CRender* value=nullptr;return value;}
}
struct CRender::Runtime {
    RF455AnimationMemoryOps animationMemory=RF455_CrtAnimationMemoryOps();
    RF455MeshAccounting meshes={};RF455BufferAccounting buffers={};unsigned importedBytes=0;
    RF455LegacyScratch scratch;RF455CharacterLoadContext load;
    explicit Runtime(RF455CharacterRenderer& owner){
        auto& process=hub();RF455LegacyDiagnostics log={nullptr,diagnostic,diagnosticWide};
        const auto base=RF455_RendererModelContext(&owner,&animationMemory.memory,&process.pose.matrix,&meshes,&buffers);
        load={{base,&owner.vertices36,owner.vertexMode,&scratch,log},{animationMemory,log,&importedBytes}};
    }
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
AnimationManager::AnimationManager(){RF455_ConstructAnimationManager(&native);}
AnimationManager::~AnimationManager(){const auto ops=memory();RF455_ReleaseAnimationManager(&native,&ops);}
bool AnimationManager::AddAnimation(char* name){const auto ops=memory();return RF455_RegisterAnimation(&native,name,&ops)!=0;}
void AnimationManager::DeleteAnimation2(unsigned long id){const auto ops=memory();RF455_DeleteAnimationId(&native,id,&ops);}
void AnimationManager::DeleteAnimation(char* name){const auto ops=memory();RF455_DeleteAnimationName(&native,name,&ops);}
ChAnimation* AnimationManager::GetAnimationData(unsigned long id){return RF455_FindAnimationId(&native,id);}
ChAnimation* AnimationManager::GetAnimationData(char* name){return RF455_FindAnimationName(&native,name);}
ChAnimation* AnimationManager::GetAnimationDataByNoPath(char* name){return RF455_FindAnimationSuffix(&native,name);}
unsigned long AnimationManager::GetAnimationID(char* name){return RF455_FindAnimationIdByName(&native,name);}
int AnimationManager::Init(){RF455_ResetAnimationCounters(&native);return 0;}
CRender::CRender():m_TM(native.textures),runtime(nullptr){RF455_ConstructCharacterRenderer(&native);runtime=new Runtime(native);activeRenderer()=this;}
CRender::~CRender(){const auto ops=memory();RF455_DestroyCharacterRenderer(&native,&ops);delete runtime;if(activeRenderer()==this)activeRenderer()=nullptr;}
CRender& CRender::GetRender(){if(!activeRenderer())throw std::runtime_error("455 Character renderer unavailable");return *activeRenderer();}
ChInterface::ChInterface():CRender(){}
void ChInterface::InitCharacter(IDirect3DDevice9* device){
    if(!device)throw std::invalid_argument("455 Character device");auto& process=hub();
    const int result=RF455_SetCharacterRendererDevice(&native,&process.shared,device,&process.shader,nullptr);
    if(result<0)throw std::runtime_error("455 Character shader initialization");
    runtime->load.legacy.rendererMode=native.vertexMode;
}
void CRender::SetMipMap(DWORD value){native.textures.mipSkip=value;}
bool CRender::LoadRealData(CHARACTEROBJECT* record,TextureManager* textures){return LoadRealData(record,textures,false);}
bool CRender::LoadRealData(CHARACTEROBJECT* record,TextureManager* textures,bool synchronous){
    auto context=runtime->load;if(textures)context.legacy.base.textures=textures->native;
    return RF455_LoadCharacter(record,synchronous,&context)!=0;
}
bool RF455AnimationStorage::LoadRealAnimation(bool synchronous){return RF455_LoadAnimation(this,synchronous,&CRender::GetRender().runtime->load.animation)!=0;}
ChAnimation* ChInterface::AddAnimationData(AnimationManager* manager,char* name){const auto ops=memory();return RF455_GetOrRegisterAnimation(&manager->native,name,&ops);}
bool ChInterface::IsLoadAnimation(ChAnimation* record){return record && record->m_Load!=0;}
void ChInterface::MatchAnimationToMesh(ChAnimation* animation,CHARACTEROBJECT* record){
    RF455_MatchAnimation(animation,record,&runtime->load);
}
// Remaining facade methods are intentionally undefined until their455wrappers
// are verified. They are recorded as link blockers, not successful no-ops.
