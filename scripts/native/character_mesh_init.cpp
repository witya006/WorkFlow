// Own source for the legacy load path, needed to remove binary-only Character
// consumers before migrating its renderer and packed mesh to455.
#include "Character.h"
#include "character_mesh_format.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <new>

// This retained private SDK data symbol is the same renderer pointer used by
// its InitVertex. No new singleton or guessed assignment is introduced.
extern "C" CRender* RFCharacterLegacyRenderer;
#pragma comment(linker,"/alternatename:_RFCharacterLegacyRenderer=?m_Render@CRender@@0PAV1@A")

namespace {
template<class T> T read(const void* base,unsigned offset) {
    T value;std::memcpy(&value,static_cast<const unsigned char*>(base)+offset,sizeof(value));return value;
}
template<class T> void write(void* base,unsigned offset,const T& value) {
    std::memcpy(static_cast<unsigned char*>(base)+offset,&value,sizeof(value));
}
D3DXMATRIX* matrix(ObjectMesh& mesh,unsigned offset) {
    return reinterpret_cast<D3DXMATRIX*>(reinterpret_cast<unsigned char*>(&mesh)+offset);
}
char* meshName(ObjectMesh& mesh,unsigned offset) {return reinterpret_cast<char*>(&mesh)+offset;}
const char overflowMessage[]="\xbd\xba\xc6\xae\xb8\xb5 \xbf\xc0\xb9\xf6\xc7\xc3\xb7\xce\xbf\xec";
void basenameTo(char* destination,const char* source) {
    char drive[256],filename[256],extension[256];
    _splitpath(source,drive,drive,filename,extension);
    std::strcat(filename,extension);std::strcpy(destination,filename);
}
// The first texture's historical backwards scan assumes a backslash in a
// nonempty path. Preserve that domain rather than silently changing resolution.
const char* primaryTexture(const char* path) {
    unsigned length=static_cast<unsigned>(std::strlen(path));
    if (length) {
        if (path[length]!='\\') do {--length;} while(path[length]!='\\');
        ++length;
    }
    return path+length;
}
const char* secondaryTexture(const char* path) {
    unsigned length=static_cast<unsigned>(std::strlen(path));
    if (length) {
        if (path[length]!='\\') {
            while(--length) if(path[length]=='\\') return path+length+1;
            length=~0u;
        }
        ++length;
    }
    return path+length;
}
float complement(float value) {
    float result;
    __asm {
        fld1
        fsub value
        fstp result
    }
    return result;
}
}

__declspec(noinline) void __cdecl ConvertVtToD3D(CHARACTERVERTEX& target,EXPTVERTEX& input) {
    // Legacy is a DWORD copy, including signaling NaN bits. 455 instead uses
    // x87 stores, inverts normals and writes its distinct64byte vertex.
    std::memcpy(target.position,input.position,12);
    std::memcpy(target.normal,input.normal,12);
}
__declspec(naked) void __cdecl ConvertUV(CHARACTERVERTEX&,tagTEXCOORDFLOAT) {
    __asm {
        fld dword ptr [esp+8]
        mov eax,dword ptr [esp+4]
        fstp dword ptr [eax+28]
        fld1
        fsub dword ptr [esp+12]
        fstp dword ptr [eax+32]
        ret
    }
}
__declspec(noinline) void __cdecl DecodeTwoBlendPhysiqueData(CHARACTERVERTEX* vertices,int vertexCount,PHYSIQUE* input,int count) {
    char names[50][256];int nameCount=0;
    const unsigned char* records=reinterpret_cast<const unsigned char*>(input);
    for(int p=0;p<count;++p) {
        const unsigned char* record=records+424*p;
        for(int b=0;b<read<int>(record,4);++b) {
            const char* name=reinterpret_cast<const char*>(record+8+100*b);bool seen=false;
            for(int n=0;n<nameCount;++n) if(!std::strcmp(name,names[n]))seen=true;
            if(!seen) {
                std::strcpy(names[nameCount++],name);
                if(nameCount>50) OutputDebugStringA("Error: Overflow: Phsyque Node more then 3");
            }
        }
    }
    for(int p=0;p<count;++p) {
        const unsigned char* record=records+424*p;const int index=read<int>(record,0);
        // The supplied body writes before its index comparison and accepts
        // index==vertexCount. Unsafe inputs/OOM are not certified by the port.
        vertices[index].firstBoneWeight=1.0f;
        if(vertexCount<index)break;
        const int bones=read<int>(record,4);
        if(bones>3)OutputDebugStringA("Error: Overflow: Phsyque Node more then 3");
        for(int b=0;b<bones;++b) {
            const char* name=reinterpret_cast<const char*>(record+8+100*b);
            for(int n=0;n<nameCount;++n) if(!std::strcmp(name,names[n])) {
                float weight=read<float>(record,408+4*b);
                vertices[index].firstBoneWeight=n?complement(weight):weight;
            }
        }
    }
}

void __cdecl InitVertex(ObjectData* data,CHARACTEROBJECT* skeleton,CHARACTEROBJECT* character,TextureManager* textures,bool) {
    const unsigned count=read<unsigned short>(data,2);
    const unsigned char* records=read<const unsigned char*>(data,4);
    ObjectMesh* meshes=new ObjectMesh[count];
    CRender* renderer=RFCharacterLegacyRenderer;
    for(unsigned m=0;m<count;++m) {
        ObjectMesh& mesh=meshes[m];const unsigned char* record=records+720*m;
        mesh.m_pParent=nullptr;
        const char* first=primaryTexture(reinterpret_cast<const char*>(record)+398);
        DWORD id=0;
        if(*first) {
            id=textures->GetTextureID(first);
            if(!id) {
                const char* path=character->legacy_texture_path[0]?character->legacy_texture_path:reinterpret_cast<const char*>(textures)+28;
                if(textures->AddTexture(path,first))id=textures->GetTextureID(first);
                else OutputDebugStringA("Can't Find Texture\n");
            }
        }
        write<DWORD>(&mesh,776,id);write<DWORD>(&mesh,772,0);
        const char* second=secondaryTexture(reinterpret_cast<const char*>(record)+498);
        id=textures->GetTextureID(second);
        if(!id && *second) {
            const char* path=character->legacy_texture_path[0]?character->legacy_texture_path:reinterpret_cast<const char*>(textures)+28;
            if(textures->AddTexture(path,second))id=textures->GetTextureID(second);
        }
        write<DWORD>(&mesh,784,id);write<DWORD>(&mesh,864,1);write<DWORD>(&mesh,780,0);
        write<DWORD>(&mesh,796,read<DWORD>(record,598));
        for(unsigned n=0;n<3;++n) {
            write<DWORD>(&mesh,972+4*n,read<DWORD>(record,614+4*n));
            write<DWORD>(&mesh,960+4*n,read<DWORD>(record,602+4*n));
            write<unsigned char>(&mesh,948+n,read<unsigned char>(record,631+n));
        }
        write<unsigned char>(&mesh,957,read<unsigned char>(record,634));
        write<unsigned char>(&mesh,956,read<unsigned char>(record,639));
        const unsigned vertexCount=read<unsigned short>(record,392),faceCount=read<unsigned short>(record,394),expandedCount=3*faceCount;
        write<DWORD>(&mesh,752,expandedCount);write<DWORD>(&mesh,756,expandedCount);
        auto* vertices=static_cast<CHARACTERVERTEX*>(::operator new(36*vertexCount));
        auto* expanded=static_cast<CHARACTERVERTEX*>(::operator new(36*expandedCount));
        std::memcpy(matrix(mesh,432),record+328,64);
        std::memcpy(matrix(mesh,240),record+200,64);std::memcpy(matrix(mesh,176),record+200,64);
        D3DXMATRIX inverse;float determinant=0;
        D3DXMatrixInverse(&inverse,&determinant,matrix(mesh,432));
        D3DXMatrixMultiply(matrix(mesh,688),&inverse,matrix(mesh,240));
        write<DWORD>(&mesh,744,0);write<DWORD>(&mesh,740,0);write<DWORD>(&mesh,736,0);
        std::memcpy(matrix(mesh,368),record+264,64);
        D3DXMatrixInverse(matrix(mesh,304),&determinant,matrix(mesh,240));
        basenameTo(meshName(mesh,64),reinterpret_cast<const char*>(record)+100);
        basenameTo(meshName(mesh,0),reinterpret_cast<const char*>(record));
        if(std::strlen(meshName(mesh,0))>=64)MessageBoxA(nullptr,overflowMessage,nullptr,0);
        if(std::strlen(meshName(mesh,64))>=64)MessageBoxA(nullptr,overflowMessage,nullptr,0);
        auto* exports=read<EXPTVERTEX*>(record,696);
        for(unsigned n=0;n<vertexCount;++n) {ConvertVtToD3D(vertices[n],exports[n]);vertices[n].firstBoneWeight=1.0f;}
        PHYSIQUE* physique=read<PHYSIQUE*>(record,704);
        if(physique)DecodeTwoBlendPhysiqueData(vertices,vertexCount,physique,read<unsigned short>(record,396));
        const unsigned char* faces=read<const unsigned char*>(record,700);
        for(unsigned f=0;f<faceCount;++f) {
            const unsigned char* face=faces+88*f;
            for(unsigned corner=0;corner<3;++corner) {
                expanded[3*f+corner]=vertices[read<int>(face,4*corner)];
                tagTEXCOORDFLOAT uv={read<float>(face,48+12*corner),read<float>(face,52+12*corner)};
                ConvertUV(expanded[3*f+corner],uv);
            }
        }
        write<DWORD>(&mesh,172,0);
        if(faceCount && !renderer->MakeVB(reinterpret_cast<IDirect3DVertexBuffer8**>(reinterpret_cast<unsigned char*>(&mesh)+164),expanded,expandedCount))character->unknown_108=1;
        ::operator delete(expanded);::operator delete(vertices);
    }
    for(unsigned m=0;m<count;++m)meshes[m].m_HaveParent=false;
    FindParent(meshes,count,meshes,count);
    if(skeleton)FindParent(skeleton->m_pMesh,skeleton->m_MaxObj,meshes,count);
    for(unsigned m=0;m<count;++m) {
        ObjectMesh& mesh=meshes[m];
        if(!read<DWORD>(data,24) && mesh.m_pParent)D3DXMatrixMultiply(matrix(mesh,368),matrix(mesh,240),matrix(*mesh.m_pParent,304));
    }
    if(skeleton)FindBlendParent(skeleton->m_pMesh,skeleton->m_MaxObj,meshes,count,data);
    else FindBlendParent(meshes,count,meshes,count,data);
    character->m_pMesh=meshes;character->m_MaxObj=count;
    for(unsigned m=0;m<count;++m) {
        char token[100]={},second[100]={};std::sscanf(meshes[m].m_Name,"%s%s",token,second);_strupr(token);
        if(!std::strcmp(token,"BONE"))write<DWORD>(&meshes[m],1068,1);
    }
}
