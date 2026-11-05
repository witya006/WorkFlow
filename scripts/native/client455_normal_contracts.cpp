#include "Character.h"
#include <cstdio>
#include <cstring>
#include <new>

namespace {
template<class T> T get(const unsigned char* bytes,unsigned offset){
    T value;std::memcpy(&value,bytes+offset,sizeof(value));return value;
}
template<class T> void put(unsigned char* bytes,unsigned offset,T value){
    std::memcpy(bytes+offset,&value,sizeof(value));
}
constexpr unsigned AnimationFlag=5094,CurrentAnimation=5095,PreviousAnimation=5099;
constexpr unsigned AnimationMaximum=5103,MeshAlpha=5131,EyeEnabled=5499,EyeMatrix=5503;
}

// 931FB0. Descriptor copies own only32bytes; all channel key arrays are borrowed
// from the animation manager. Keep the previous descriptor when current is null
// or blending is disabled. Original allocation-failure/AV policy is not claimed.
void ChInterface::AnimationReset(CHARACTEROBJECT* model){
    if(!model)return;
    const auto memory=RF455_CrtMeshMemoryOps();
    for(int i=0;i<static_cast<int>(model->m_MaxObj);++i){
        auto* bytes=model->m_pMesh[i].bytes;
        auto* current=get<RF455AnimationData*>(bytes,CurrentAnimation);
        bytes[AnimationFlag]=0;put<unsigned>(bytes,AnimationMaximum,0);
        if(current && native.opaque33840){
            auto* previous=get<RF455AnimationData*>(bytes,PreviousAnimation);
            if(previous){memory.release(memory.context,previous);put<void*>(bytes,PreviousAnimation,nullptr);}
            previous=static_cast<RF455AnimationData*>(memory.allocate(memory.context,sizeof(RF455AnimationData)));
            if(!previous)throw std::bad_alloc();
            std::memset(previous,0,sizeof(*previous));put(bytes,PreviousAnimation,previous);
            std::memcpy(previous,current,sizeof(*previous));
            model->m_BlendElapsed=0;model->m_BlendFrame=model->m_Frame;
            model->m_BlendMax=model->m_OMaxFrame;model->m_BlendActive=1;
        }
        if(current){memory.release(memory.context,current);put<void*>(bytes,CurrentAnimation,nullptr);}
        put<float>(bytes,MeshAlpha,1);put<void*>(bytes,CurrentAnimation,nullptr);
    }
    model->m_Frame=160;model->m_OMaxFrame=0;
}

// 931A80 delegates to the already recovered93BB70 kernel. Only meshes marked
// as external-parent bindings are rematched; absent names retain their state.
void ChInterface::RematchParent(CHARACTEROBJECT* parent,CHARACTEROBJECT* model){
    if(parent && model)RF455_RematchMeshParents(parent->m_pMesh,static_cast<int>(parent->m_MaxObj),
        model->m_pMesh,static_cast<int>(model->m_MaxObj));
}

// 931AC0 copies the first EXACT name match, including all16 matrix components.
// The matrix is passed by value in the original callsites (72stack bytes).
void ChInterface::SetEyeVec(char* name,CHARACTEROBJECT* model,D3DXMATRIX matrix){
    for(unsigned i=0;i<model->m_MaxObj;++i){
        auto* bytes=model->m_pMesh[i].bytes;
        if(std::strcmp(reinterpret_cast<const char*>(bytes),name))continue;
        std::memcpy(bytes+EyeMatrix,&matrix,64);put<unsigned>(bytes,EyeEnabled,1);break;
    }
}

// 608140 guards only source; the255th path byte is deliberately retained.
void ChInterface::SetTexPath(CHARACTEROBJECT* model,char* source){
    if(source)std::strncpy(model->legacy_texture_path,source,255);
}

// 931810 ->93BF90: skip256name bytes, then read SECOND output before FIRST.
// Existing/truncated files return1 even after short reads, preserving untouched
// output bytes. This API describes the reference reader, not a validating parser.
int ChInterface::ImportBoundBox(char* path,float* first,float* second){
    if(!path)return 0;
    std::FILE* file=std::fopen(path,"rb");if(!file)return 0;
    char name[256];std::fread(name,1,sizeof(name),file);
    std::fread(second,1,12,file);std::fread(first,1,12,file);std::fclose(file);return 1;
}
