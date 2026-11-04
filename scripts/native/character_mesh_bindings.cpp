// Recovered legacy CPU bindings. These preserve the 1072-byte ABI while the
// 455 renderer/5803-byte mesh is reconstructed separately.
#include "Character.h"
#include <cstring>
#include <new>

namespace {
template<class T> T read(const void* base, unsigned offset) {
    T value;std::memcpy(&value,static_cast<const unsigned char*>(base)+offset,sizeof(value));return value;
}
template<class T> void write(void* base,unsigned offset,const T& value) {
    std::memcpy(static_cast<unsigned char*>(base)+offset,&value,sizeof(value));
}
int bindParents(ObjectMesh* parents,int parentCount,ObjectMesh* meshes,int meshCount,bool rematch) {
    int matches=0;
    for (int i=0;i<meshCount;++i) {
        ObjectMesh& mesh=meshes[i];
        if (rematch && !read<DWORD>(&mesh,996)) continue;
        const char* parentName=reinterpret_cast<const char*>(&mesh)+64;
        for (int j=0;j<parentCount;++j) {
            if (std::strcmp(parentName,parents[j].m_Name)) continue;
            mesh.m_pParent=&parents[j];mesh.m_HaveParent=true;
            if (parents!=meshes) write<DWORD>(&mesh,996,1);
            ++matches;
            // The legacy SDK keeps scanning: duplicate names choose the last
            // parent and count every match. 455 stops at its first match.
        }
    }
    return matches;
}
}

ObjectMesh* __cdecl FindParent(char* name,ObjectMesh* meshes,int count) {
    for (int i=0;i<count;++i) if (!std::strcmp(name,meshes[i].m_Name)) return &meshes[i];
    return nullptr;
}
int __cdecl FindParent(ObjectMesh* parents,int parentCount,ObjectMesh* meshes,int meshCount) {
    return bindParents(parents,parentCount,meshes,meshCount,false);
}
int __cdecl RematchParent(ObjectMesh* parents,int parentCount,ObjectMesh* meshes,int meshCount) {
    return bindParents(parents,parentCount,meshes,meshCount,true);
}
void __cdecl FindBlendParent(ObjectMesh* parents,int parentCount,ObjectMesh* meshes,int meshCount,ObjectData* data) {
    if (meshCount<=0) return;
    const unsigned char* records=read<const unsigned char*>(data,4);
    for (int m=0;m<meshCount;++m) {
        const unsigned char* record=records+720*m;
        const unsigned char* physiques=read<const unsigned char*>(record,704);
        const unsigned physiqueCount=read<unsigned short>(record,396);
        ObjectMesh* selected[50];int selectedCount=0;
        for (unsigned p=0;p<physiqueCount;++p) {
            const unsigned char* physique=physiques+424*p;
            const int influenceCount=read<int>(physique,4);
            for (int b=0;b<influenceCount;++b) {
                char* name=reinterpret_cast<char*>(const_cast<unsigned char*>(physique+8+100*b));
                bool duplicate=false;
                for (int n=0;n<selectedCount;++n) if (!std::strcmp(name,selected[n]->m_Name)) duplicate=true;
                if (duplicate) continue;
                ObjectMesh* found=FindParent(name,parents,parentCount);
                if (!found) found=FindParent(name,meshes,meshCount);
                if (found) selected[selectedCount++]=found;
                else OutputDebugStringA("Error: Can't Find Parent!!\n");
            }
        }
        ObjectMesh& mesh=meshes[m];mesh.m_BlendNum=selectedCount;
        // Includes count0: supplied FindBlendParent always stores the result
        // of operator new, which defines the pointer omitted by its constructor.
        mesh.m_pMatBlend=static_cast<D3DXMATRIX*>(::operator new(64u*selectedCount));
        for (int n=0;n<selectedCount;++n) D3DXMatrixIdentity(&mesh.m_pMatBlend[n]);
        if (selectedCount) std::memcpy(reinterpret_cast<unsigned char*>(&mesh)+144,selected,4u*selectedCount);
    }
}
