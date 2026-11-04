#include "client455_mesh_runtime.h"
#include <cstdlib>
#include <cstring>
#include <string>

namespace {
template<class T> void write(unsigned char* bytes,unsigned at,T value){std::memcpy(bytes+at,&value,sizeof(value));}
bool terminated(const unsigned char* field){return std::memchr(field,0,100)!=nullptr;}
void basenameTo(unsigned char* destination,const unsigned char* source){
    char drive[256],filename[256],extension[256];
    _splitpath(reinterpret_cast<const char*>(source),drive,drive,filename,extension);
    std::strcat(filename,extension);std::strncpy(reinterpret_cast<char*>(destination),filename,255);
}
const float unsignedBias=4294967296.0f;
void copyFloat(unsigned char* output,const unsigned char* input){
    __asm {
        mov eax,input
        mov edx,output
        fld dword ptr[eax]
        fstp dword ptr[edx]
    }
}
void unsignedFloat(unsigned char* output,const unsigned char* input){
    __asm {
        mov eax,input
        mov edx,output
        fild dword ptr[eax]
        cmp dword ptr[eax],0
        jge nonnegative
        fadd unsignedBias
    nonnegative:
        fstp dword ptr[edx]
    }
}
std::string variant(const char* name,const char* suffix){
    std::string result(name);const auto at=result.find(".dds");
    if(at!=std::string::npos)result.insert(at,suffix);return result;
}
}
extern "C" void RF455_ConstructMeshStorage(RF455MeshStorage* mesh,RF455MeshAccounting* accounting){
    // The preceding original subobject initializations allocate nothing and are
    // overwritten by its whole5803-byte memset. Preserve the final state.
    auto* bytes=mesh->bytes;std::memset(bytes,0,5803);
    ++accounting->constructed;accounting->bytesConstructed+=5803;
    for(unsigned at:{5131u,5483u,5487u,5491u})write<std::uint32_t>(bytes,at,0x3f800000u);
    for(unsigned at:{5111u,5123u,5127u,4494u,4502u,5767u,5771u,5775u,5763u})write<std::uint32_t>(bytes,at,0xffffffffu);
}
extern "C" RF455MeshRuntimeStatus RF455_ApplyMesh08Header(RF455MeshStorage* mesh,
    const RF455Mesh08Part* part,const RF455MeshMatrixOps* matrices,std::uint32_t* modelFlag){
    if(!mesh || !part || !part->header || !matrices || !matrices->inverse || !matrices->multiply || !modelFlag)return RF_MESH_RUNTIME_ARGUMENT;
    const auto* head=part->header;if(!terminated(head) || !terminated(head+100))return RF_MESH_RUNTIME_NAME;
    auto* bytes=mesh->bytes;
    write(bytes,5455,bytes+5163);write<std::uint32_t>(bytes,5363,1);write<std::uint32_t>(bytes,5115,0);
    unsignedFloat(bytes+5339,head+598);
    for(unsigned n=0;n<3;++n)copyFloat(bytes+5471+4*n,head+614+4*n);
    for(unsigned n=0;n<3;++n)copyFloat(bytes+5459+4*n,head+602+4*n);
    write<std::uint32_t>(bytes,5359,head[634]);write<std::uint32_t>(bytes,5143,head[639]);
    std::memcpy(bytes+5579,head+646,16);
    std::memcpy(bytes+4766,head+328,64);std::memcpy(bytes+4574,head+200,64);std::memcpy(bytes+4510,head+200,64);
    alignas(16) unsigned char inverse[64];float determinant=0;
    if(!matrices->inverse(inverse,&determinant,bytes+4766))return RF_MESH_RUNTIME_MATRIX;
    matrices->multiply(bytes+5022,inverse,bytes+4574);
    std::memset(bytes+5070,0,12);
    std::memcpy(bytes+4702,head+264,64);
    if(!matrices->inverse(bytes+4638,&determinant,bytes+4574))return RF_MESH_RUNTIME_MATRIX;
    basenameTo(bytes+256,head+100);basenameTo(bytes,head);
    const char* name=reinterpret_cast<const char*>(bytes);
    const char* special[]={"Bip01 Spine1","Bip01 L Thigh","Bip01 R Thigh"};
    for(unsigned n=0;n<3;++n)if(!std::strcmp(name,special[n])){write<std::uint32_t>(bytes,5575,n+1);break;}
    const char* secondary[]={"Bip01 Ponytail L1","Bip01 Ponytail L11","Bip01 L skirt","Bip01 R skirt","Bip01 B skirt"};
    for(const auto* match:secondary)if(!std::strcmp(name,match)){write<std::uint32_t>(bytes,5571,1);*modelFlag=1;break;}
    write<std::uint32_t>(bytes,5086,part->vertexCount);write<std::uint32_t>(bytes,5090,part->indexCount);
    return RF_MESH_RUNTIME_OK;
}
extern "C" RF455MeshRuntimeStatus RF455_LoadMesh08Materials(RF455MeshStorage* mesh,
    unsigned char* head,const char* objectDirectory,const char* fallbackDirectory,const RF455MeshMaterialOps* materials){
    if(!mesh || !head || !objectDirectory || !fallbackDirectory || !materials || !materials->lookup || !materials->load)return RF_MESH_RUNTIME_ARGUMENT;
    if(!terminated(head+398) || !terminated(head+498))return RF_MESH_RUNTIME_NAME;
    char* primary=reinterpret_cast<char*>(head+398);const auto length=std::strlen(primary);
    if(length){char* slash=std::strrchr(primary,'\\');if(!slash)return RF_MESH_RUNTIME_PATH;primary=slash+1;}
    auto* bytes=mesh->bytes;write<std::uint32_t>(bytes,518,0);
    if(*primary){
        _strlwr(primary);
        const std::string variants[]={variant(primary,"_NOR"),variant(primary,"_SEQ"),variant(primary,"_REF")};
        const unsigned destinations[]={5767,5771,5775};
        for(unsigned n=0;n<3;++n)write(bytes,destinations[n],materials->lookup(materials->context,variants[n].c_str()));
        const auto main=materials->lookup(materials->context,primary);write(bytes,5111,main);
        // All four loads are attempted only when the primary lookup missed,
        // even when an auxiliary lookup already returned a nonzero ID.
        if(!main){
            const char* directory=*objectDirectory?objectDirectory:fallbackDirectory;
            if(materials->load(materials->context,directory,primary))write(bytes,5111,materials->lookup(materials->context,primary));
            for(unsigned n=0;n<3;++n)if(materials->load(materials->context,directory,variants[n].c_str()))
                write(bytes,destinations[n],materials->lookup(materials->context,variants[n].c_str()));
        }
    }else write<std::uint32_t>(bytes,5111,0);
    write<std::uint32_t>(bytes,5107,0);
    const char* secondary=reinterpret_cast<const char*>(head+498);unsigned at=static_cast<unsigned>(std::strlen(secondary));
    // Reference deliberately does not inspect index0 of a nonempty secondary
    // path while searching backwards. A leading-only backslash is retained.
    if(at){while(--at)if(secondary[at]=='\\'){++at;break;}}
    secondary+=at;
    const auto second=materials->lookup(materials->context,secondary);write(bytes,5123,second);
    if(!second && *secondary){
        const char* directory=*objectDirectory?objectDirectory:fallbackDirectory;
        if(materials->load(materials->context,directory,secondary))write(bytes,5123,materials->lookup(materials->context,secondary));
    }
    return RF_MESH_RUNTIME_OK;
}
