#include "Character.h"
#include <cstring>
#include <stdexcept>

namespace {
template<class T>T get(const void* p,unsigned n){T value;std::memcpy(&value,static_cast<const unsigned char*>(p)+n,sizeof(value));return value;}
template<class T>void put(void* p,unsigned n,T value){std::memcpy(static_cast<unsigned char*>(p)+n,&value,sizeof(value));}
void accepted(const RF455EffectRead& r){if(r.status!=RF_EFFECT_OK && r.status!=RF_EFFECT_MISSING)throw std::runtime_error("455 EFF input outside confirmed bounded format");}
void selected(CHARACTEROBJECT* model,const RF455EffectFileEntry& entry,int grade){if(model && model->m_MaxObj)RF455_ApplyEffectFile(&RF455_NormalEffects(),&CRender::GetRender().native,model,entry.file.c_str(),grade);}
}
EffectList g_EFFMonList,g_EFFNPCList,g_EFFUnitList,g_EFFKitList;
EffectFileList g_EffectFileList;
void EffectList::LoadEffectFileList(char* file){lastRead=RF455_LoadEffectFileTable(&native,&RF455_NormalEffects(),file,false);accepted(lastRead);}
void EffectFileList::LoadEffectFileList(char* file){lastRead=RF455_LoadEffectFileTable(&native,&RF455_NormalEffects(),file,true);accepted(lastRead);}
void EffectList::SetEffect(CHARACTEROBJECT* model,DWORD id){const auto found=native.entries.find(id);if(found!=native.entries.end())selected(model,found->second,36);}
void EffectObjectManager::LoadEffect(char* file){accepted(RF455_LoadEffects(&RF455_NormalEffects(),file));}
int EffectObjectManager::SetPartEffect(CHARACTEROBJECT* model,char* file,int grade){if(!model || !model->m_MaxObj)return 0;return RF455_ApplyEffectFile(&RF455_NormalEffects(),&CRender::GetRender().native,model,file,grade);}
void SetMeshEffect(CHARACTEROBJECT* model,unsigned long item,unsigned long grade,unsigned long group){
    const auto result=RF455_SelectItemEffect(&g_PatternList.native,&g_EffectItemList.native,item,grade,group);
    if(result.status==RF_EFFECT_QUERY_UNDEFINED)throw std::runtime_error("455 effect grade depends on uninitialized original pattern stack");
    if(result.status!=RF_EFFECT_QUERY_OK)throw std::out_of_range("455 effect selector outside confirmed table");
    if(!result.effect)return;const auto found=g_EffectFileList.native.entries.find(result.effect);if(found!=g_EffectFileList.native.entries.end())selected(model,found->second,found->second.mode?static_cast<int>(grade):36);
}
void RF455MeshStorage::InitEffect(){put<unsigned>(bytes,5567,0);put<float>(bytes,5131,1);put<void*>(bytes,5115,nullptr);put<void*>(bytes,5119,nullptr);put<unsigned>(bytes,5123,0xffffffffu);put<unsigned>(bytes,5127,0xffffffffu);}
void CRender::InitEffect(CHARACTEROBJECT* model){for(unsigned i=0;i<model->m_MaxObj;++i){auto* mesh=model->m_pMesh+i;mesh->InitEffect();RF455_ApplyInlineEffect(&native,mesh,36);}}
CharacterEffectSlot* RF455MeshStorage::particleSlots(){auto* data=get<unsigned char*>(bytes,5455);return data?reinterpret_cast<CharacterEffectSlot*>(data+208):nullptr;}
CharacterEffectSlot& RF455MeshStorage::entitySlot(){auto* data=get<unsigned char*>(bytes,5455);if(!data)throw std::logic_error("455 mesh has no current effect data");return *reinterpret_cast<CharacterEffectSlot*>(data+256);}
int RF455MeshStorage::IsHaveEffect(){auto* data=get<unsigned char*>(bytes,5455);if(!data)return 0;for(unsigned i=0;i<3;++i)if(get<unsigned>(data,220+16*i))return 1;return get<unsigned>(data,268)!=0;}
int RF455CharacterStorage::IsHaveEffect(){for(unsigned i=0;i<m_MaxObj;++i)if(m_pMesh[i].IsHaveEffect())return 1;return 0;}
