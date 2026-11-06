#include "Character.h"
#include <algorithm>
#include <cfloat>
#include <cstring>
#include <new>
#include <stdexcept>

RF455CharacterManager* ChInterface::CreatePart455(const char* name) {
    if(!name||std::strlen(name)>=128||std::strchr(name,'%'))throw std::invalid_argument("RVP part name");
    const auto ops=RF455_CrtMeshMemoryOps();
    auto* part=static_cast<RF455CharacterManager*>(ops.allocate(ops.context,sizeof(RF455CharacterManager)));
    if(!part)throw std::bad_alloc();RF455_ConstructCharacterManager(part);std::strcpy(part->name,name);
    auto& registry=native.effects;const auto count=registry.begin?registry.end-registry.begin:0;
    const auto capacity=registry.begin?registry.capacity-registry.begin:0;
    if(count==capacity) {
        const auto next=(std::max)(capacity+capacity/2,count+1);
        auto** records=static_cast<RF455CharacterManager**>(ops.allocate(ops.context,next*sizeof(RF455CharacterManager*)));
        if(!records){ops.release(ops.context,part);throw std::bad_alloc();}
        if(count)std::memcpy(records,registry.begin,count*sizeof(*records));
        if(registry.begin)ops.release(ops.context,registry.begin);
        registry.begin=records;registry.end=records+count;registry.capacity=records+next;
    }
    *registry.end++=part;return part;
}
CHARACTEROBJECT* ChInterface::RegisterBone455(const char* name) {
    const auto ops=RF455_CrtMeshMemoryOps();
    //931480/931600 use owner+0x10a8=4264, despite the old own field name meshes.
    return RF455_CreateCharacter(&native.meshes,name,nullptr,&ops);
}
CHARACTEROBJECT* ChInterface::LookupBone455(const char* name) {
    auto* result=RF455_FindCharacterName(&native.meshes,name);
    return result&&LoadRealData(result,&m_TM,false)?result:nullptr;
}
CHARACTEROBJECT* ChInterface::RegisterMesh455(RF455CharacterManager* part,const char* name,CHARACTEROBJECT* root) {
    const auto ops=RF455_CrtMeshMemoryOps();return RF455_CreateCharacter(part,name,root,&ops);
}
CHARACTEROBJECT* ChInterface::LookupMesh455(RF455CharacterManager* part,const char* name) {
    auto* result=RF455_FindCharacterName(part,name);
    return result&&LoadRealData(result,&m_TM,false)?result:nullptr;
}
void ChInterface::ModelBounds455(CHARACTEROBJECT* model,float* low,float* high) {
    for(unsigned axis=0;axis<3;++axis){low[axis]=FLT_MAX;high[axis]=-FLT_MAX;}
    for(unsigned i=0;i<model->m_MaxObj;++i)for(unsigned axis=0;axis<3;++axis) {
        float a,b;std::memcpy(&a,model->m_pMesh[i].bytes+5471+axis*4,4);
        std::memcpy(&b,model->m_pMesh[i].bytes+5459+axis*4,4);
        if(low[axis]>a)low[axis]=a;if(high[axis]<b)high[axis]=b;
    }
}
