#include "client455_legacy_runtime.h"
#include <cstdarg>
#include <cstdio>
#include <cstring>
#include <string>
#include <cerrno>

namespace {
template<class T>T get(const void* p,unsigned at){T v;std::memcpy(&v,static_cast<const unsigned char*>(p)+at,sizeof(v));return v;}
template<class T>void put(void* p,unsigned at,T v){std::memcpy(static_cast<unsigned char*>(p)+at,&v,sizeof(v));}
bool valid(const RF455LegacyDiagnostics* d){return d && d->write && d->writeWide;}
void message(const RF455LegacyDiagnostics* d,const char* format,...){
    char text[1024];va_list args;va_start(args,format);std::vsnprintf(text,sizeof(text),format,args);va_end(args);d->write(d->context,text);
}
void copyFloat(void* destination,const void* source){
    __asm {mov eax,source
        mov edx,destination
        fld dword ptr[eax]
        fstp dword ptr[edx]}
}
float weightSum(const unsigned char* vertex){
    float sum;
    __asm {mov eax,vertex
        fld dword ptr[eax+16]
        fadd dword ptr[eax+12]
        fadd dword ptr[eax+20]
        fstp sum}
    return sum;
}
bool weightOutOfRange(float sum){
    unsigned result=0;
    __asm {fldz
        fld sum
        fcom st(1)
        fnstsw ax
        test ah,5
        jnp outside
        fld1
        fcomp st(1)
        fnstsw ax
        test ah,5
        jp done
    outside:
        mov result,1
    done:
        fstp st
        fstp st}
    return result!=0;
}
struct Block {
    const RF455MeshMemoryOps* memory;void* pointer=nullptr;
    ~Block(){if(pointer)memory->release(memory->context,pointer);}
};
struct Pending {
    const RF455MeshMemoryOps* memory;RF455MeshStorage* meshes=nullptr;
    ~Pending(){if(meshes)RF455_DeleteMeshStorage(meshes,3,memory);}
};
struct Stream {FILE* file=nullptr;~Stream(){if(file)std::fclose(file);}};
bool namesValid(RF455MeshStorage* meshes,int count){
    if(count>0 && !meshes)return false;
    for(int n=0;n<count;++n)if(!std::memchr(meshes[n].bytes,0,256))return false;
    return true;
}
void grow(std::vector<unsigned char>& bytes,unsigned count){if(bytes.size()<64u*count)bytes.resize(64u*count,0);}
bool readBlob(FILE* file,unsigned size,const RF455MeshMemoryOps* memory,Block& result){
    result.pointer=memory->allocate(memory->context,size);
    if(!result.pointer)return false;
    if(size && std::fread(result.pointer,1,size,file)!=size){memory->release(memory->context,result.pointer);result.pointer=nullptr;return false;}
    return true;
}
}

extern "C" void RF455_ConvertLegacyVertex64(void* target,const void* source){
    __asm {mov eax,source
        mov ecx,target
        fld dword ptr[eax]
        fstp dword ptr[ecx]
        fld dword ptr[eax+4]
        fstp dword ptr[ecx+4]
        fld dword ptr[eax+8]
        fstp dword ptr[ecx+8]
        fld dword ptr[eax+16]
        fchs
        fstp dword ptr[ecx+32]
        fld dword ptr[eax+20]
        fchs
        fstp dword ptr[ecx+36]
        fld dword ptr[eax+24]
        fchs
        fstp dword ptr[ecx+40]}
}
extern "C" void RF455_ConvertLegacyUv64(void* target,const void* uv){
    __asm {mov eax,uv
        mov ecx,target
        fld dword ptr[eax]
        fstp dword ptr[ecx+44]
        fld dword ptr[eax+4]
        fld1
        fsubrp st(1),st
        fstp dword ptr[ecx+48]}
}
extern "C" void RF455_ConvertLegacyVertices36(const void* source,void* destination,unsigned count){
    const unsigned fields[]={0,4,8,32,36,40,44,48},targets[]={0,4,8,16,20,24,28,32};
    auto* to=static_cast<unsigned char*>(destination);auto* from=static_cast<const unsigned char*>(source);
    for(unsigned n=0;n<count;++n){
        //93B130 uses MOV for every mapped field except the first weight, even
        // in its scalar remainder. Decompiler float types obscure this detail.
        copyFloat(to+36*n+12,from+64*n+12);
        for(unsigned i=0;i<8;++i)std::memcpy(to+36*n+targets[i],from+64*n+fields[i],4);
    }
}
extern "C" RF455LegacyRuntimeStatus RF455_DecodeLegacyWeights(void* vertices,unsigned vertexCount,
    const void* raw,unsigned count,const RF455LegacyDiagnostics* diagnostics){
    if(!valid(diagnostics) || (vertexCount && !vertices) || (count && !raw))return RF_LEGACY_RUNTIME_ARGUMENT;
    const auto* records=static_cast<const unsigned char*>(raw);const char* names[50];unsigned nameCount=0;
    for(unsigned p=0;p<count;++p){
        const auto* record=records+424*p;const auto influences=get<std::int32_t>(record,4);
        if(influences>4)return RF_LEGACY_RUNTIME_PHYSIQUE;
        for(int b=0;b<influences;++b){
            const auto* name=reinterpret_cast<const char*>(record+8+100*b);
            if(!std::memchr(name,0,100))return RF_LEGACY_RUNTIME_NAMES;
            bool seen=false;for(unsigned n=0;n<nameCount;++n)if(!std::strcmp(name,names[n]))seen=true;
            if(!seen){if(nameCount==50){message(diagnostics,"PHYSIQUE OVERFLOW!!");return RF_LEGACY_RUNTIME_LIMIT;}names[nameCount++]=name;}
        }
    }
    for(unsigned p=0;p<count;++p){
        const auto* record=records+424*p;const auto index=get<std::int32_t>(record,0);
        if(index<0 || static_cast<unsigned>(index)>=vertexCount)return RF_LEGACY_RUNTIME_PHYSIQUE;
        auto* vertex=static_cast<unsigned char*>(vertices)+64*index;std::memset(vertex+12,0,20);
        const auto influences=get<std::int32_t>(record,4);
        for(int b=0;b<influences;++b){
            const auto* name=reinterpret_cast<const char*>(record+8+100*b);
            for(unsigned n=0;n<nameCount;++n)if(!std::strcmp(name,names[n])){
                put<std::uint16_t>(vertex,24+2*b,static_cast<std::uint16_t>(n));
                if(b<3){copyFloat(vertex+12+4*b,record+408+4*b);break;}
            }
            const float sum=weightSum(vertex);
            if(weightOutOfRange(sum))message(diagnostics,"Blend Weight Error: %f",static_cast<double>(sum));
        }
    }
    return RF_LEGACY_RUNTIME_OK;
}
extern "C" RF455LegacyRuntimeStatus RF455_ResolveLegacyBones(RF455MeshStorage* parents,int parentCount,
    RF455MeshStorage* meshes,unsigned meshCount,const RF455LegacyModel* imported,
    const RF455LegacyDiagnostics* diagnostics,RF455MeshBindingStats* stats){
    if(!imported || !stats || !valid(diagnostics) || (meshCount && !meshes))return RF_LEGACY_RUNTIME_ARGUMENT;
    if(!namesValid(parents,parentCount) || !namesValid(meshes,meshCount))return RF_LEGACY_RUNTIME_NAMES;
    if(meshCount!=get<std::uint16_t>(imported->bytes,2))return RF_LEGACY_RUNTIME_FORMAT;
    const auto* parts=get<const RF455LegacyPart*>(imported->bytes,4);RF455MeshBindingStats result={};
    for(unsigned n=0;n<meshCount;++n){
        const auto* part=parts[n].bytes;const auto count=get<std::uint16_t>(part,396);const auto* raw=get<const unsigned char*>(part,704);
        if(count && !raw)return RF_LEGACY_RUNTIME_PHYSIQUE;
        RF455MeshStorage* selected[50];unsigned selectedCount=0;
        for(unsigned p=0;p<count;++p){const auto* record=raw+424*p;const auto influences=get<std::int32_t>(record,4);
            if(influences>4)return RF_LEGACY_RUNTIME_PHYSIQUE;
            for(int b=0;b<influences;++b){const auto* name=reinterpret_cast<const char*>(record+8+100*b);if(!std::memchr(name,0,100))return RF_LEGACY_RUNTIME_NAMES;
                bool seen=false;for(unsigned i=0;i<selectedCount;++i)if(!std::strcmp(name,reinterpret_cast<const char*>(selected[i]->bytes)))seen=true;
                if(seen)continue;auto* found=RF455_FindParentMesh(name,parents,parentCount);if(!found)found=RF455_FindParentMesh(name,meshes,meshCount);
                if(found){if(selectedCount==50)return RF_LEGACY_RUNTIME_LIMIT;selected[selectedCount++]=found;++result.resolvedNames;}
                else{++result.missingNames;diagnostics->writeWide(diagnostics->context,L"Error: Can't Find Parent!!\n");}
            }
        }
        auto* bytes=meshes[n].bytes;put(bytes,522,selectedCount);
        for(unsigned i=0;i<selectedCount;++i)for(unsigned j=0;j<16;++j)put<unsigned>(bytes,646+64*i+4*j,j%5?0u:0x3f800000u);
        if(selectedCount)std::memcpy(bytes+526,selected,4*selectedCount);
    }
    *stats=result;return RF_LEGACY_RUNTIME_OK;
}
extern "C" RF455LegacyRuntimeStatus RF455_IndexLegacyVertices(const void* expanded,unsigned count,
    RF455MeshStorage* mesh,const RF455LegacyLoadContext* context,unsigned* uniqueCount){
    if(!context || !context->scratch || !context->vertices36 || !context->base.vertices || !context->base.indices || !context->base.bufferAccounting || !context->base.memory.allocate || !context->base.memory.release || !valid(&context->diagnostics) || !mesh || !uniqueCount || (count && !expanded))return RF_LEGACY_RUNTIME_ARGUMENT;
    if(count>64000){message(&context->diagnostics,"MakeIndexVertex : %d",count);return RF_LEGACY_RUNTIME_LIMIT;}
    if(!count){*uniqueCount=0;return RF_LEGACY_RUNTIME_OK;}
    auto& scratch=*context->scratch;grow(scratch.unique,count);if(scratch.indices.size()<count)scratch.indices.resize(count);if(scratch.rebasedIndices.size()<count)scratch.rebasedIndices.resize(count);
    unsigned unique=0;const auto* input=static_cast<const unsigned char*>(expanded);
    for(unsigned n=0;n<count;++n){unsigned index=0;while(index<unique && std::memcmp(input+64*n,scratch.unique.data()+64*index,64))++index;
        if(index==unique){std::memcpy(scratch.unique.data()+64*unique,input+64*n,64);++unique;}scratch.indices[n]=static_cast<std::uint16_t>(index);
    }
    unsigned absolute=get<unsigned>(mesh->bytes,4494),base=0;bool uploaded=false;
    if(context->rendererMode==4){uploaded=RF455_UploadVertices64(context->base.vertices,scratch.unique.data(),64*unique,&absolute,context->base.bufferAccounting)!=0;put(mesh->bytes,4494,absolute);base=(absolute%RF455_VERTEX_BLOCK_BYTES)>>6;}
    else if(context->rendererMode==2){Block converted={&context->base.memory};converted.pointer=context->base.memory.allocate(context->base.memory.context,36u*count);if(!converted.pointer)return RF_LEGACY_RUNTIME_MEMORY;
        RF455_ConvertLegacyVertices36(scratch.unique.data(),converted.pointer,count);uploaded=RF455_UploadVertices36(context->vertices36,converted.pointer,36*unique,&absolute,context->base.bufferAccounting)!=0;put(mesh->bytes,4494,absolute);base=(absolute%RF455_VERTEX_BLOCK_BYTES)/36;
    }
    if(!uploaded)message(&context->diagnostics,"VDM:INSERT ERROR : %s",reinterpret_cast<const char*>(mesh->bytes));
    for(unsigned n=0;n<count;++n)scratch.rebasedIndices[n]=static_cast<std::uint16_t>(scratch.indices[n]+base);
    absolute=get<unsigned>(mesh->bytes,4502);if(!RF455_UploadIndices(context->base.indices,scratch.rebasedIndices.data(),2*count,&absolute,context->base.bufferAccounting))message(&context->diagnostics,"IDM:INSERT ERROR : %s",reinterpret_cast<const char*>(mesh->bytes));put(mesh->bytes,4502,absolute);
    *uniqueCount=unique;return RF_LEGACY_RUNTIME_OK;
}
extern "C" RF455LegacyRuntimeStatus RF455_ImportLegacyFile(const char* filename,
    const RF455MeshMemoryOps* memory,const RF455LegacyDiagnostics* diagnostics,RF455LegacyModel** output){
    if(!filename || !memory || !memory->allocate || !memory->release || !valid(diagnostics) || !output)return RF_LEGACY_RUNTIME_ARGUMENT;
    Block raw={memory};unsigned size=0;Stream input;input.file=RF455_GetCharacterRfsCache()->Open(filename,&size);
    if(input.file){readBlob(input.file,size,memory,raw);std::fclose(input.file);input.file=nullptr;}
    if(!raw.pointer){input.file=std::fopen(filename,"rb");if(!input.file){const int error=errno;message(diagnostics,"Mesh or Bone Not Found : FileName = %s [%d]%s",filename,error,std::strerror(error));return RF_LEGACY_RUNTIME_IO;}
        std::fseek(input.file,0,SEEK_END);const long length=std::ftell(input.file);std::fseek(input.file,0,SEEK_SET);if(length<0)return RF_LEGACY_RUNTIME_IO;size=static_cast<unsigned>(length);if(!readBlob(input.file,size,memory,raw))return RF_LEGACY_RUNTIME_IO;std::fclose(input.file);input.file=nullptr;
    }
    RF455LegacyModel* result=nullptr;std::size_t consumed=0;const auto status=RF455_ReadLegacyModel(raw.pointer,size,memory,&result,&consumed);
    memory->release(memory->context,raw.pointer);raw.pointer=nullptr;message(diagnostics,"ImportMeshorBoneData( %s ) :NULL",filename);
    if(status!=RF_LEGACY_OK)return status==RF_LEGACY_MEMORY?RF_LEGACY_RUNTIME_MEMORY:RF_LEGACY_RUNTIME_FORMAT;*output=result;return RF_LEGACY_RUNTIME_OK;
}
extern "C" RF455LegacyRuntimeStatus RF455_LoadLegacyModel(RF455LegacyModel* imported,
    RF455KnownModelPrefix* external,RF455KnownModelPrefix* model,
    const RF455LegacyLoadContext* context,RF455LegacyLoadStats* stats){
    if(!imported || !model || !context || !stats || !context->scratch || !context->vertices36 || !context->base.memory.allocate || !context->base.memory.release || !context->base.textures || !context->base.vertices || !context->base.indices || !context->base.meshAccounting || !context->base.bufferAccounting || !context->base.matrices.inverse || !context->base.matrices.multiply || !valid(&context->diagnostics))return RF_LEGACY_RUNTIME_ARGUMENT;
    if(!std::memchr(model->bytes+4,0,256) || !std::memchr(model->bytes+276,0,256))return RF_LEGACY_RUNTIME_NAMES;
    const unsigned count=get<std::uint16_t>(imported->bytes,2);auto* parts=get<RF455LegacyPart*>(imported->bytes,4);if(count && !parts)return RF_LEGACY_RUNTIME_FORMAT;
    const auto& memory=context->base.memory;Pending pending={&memory};pending.meshes=RF455_AllocateMeshArray(count,context->base.meshAccounting,&memory);if(!pending.meshes)return RF_LEGACY_RUNTIME_MEMORY;
    std::string sidecar(reinterpret_cast<const char*>(model->bytes+4));const auto dot=sidecar.rfind('.');if(dot!=std::string::npos)sidecar.resize(dot);sidecar+=".mtg";Stream mtg;mtg.file=std::fopen(sidecar.c_str(),"rb");
    const auto materials=RF455_TextureMaterialOps(context->base.textures);RF455LegacyLoadStats result={};
    for(unsigned n=0;n<count;++n){auto* part=parts[n].bytes;auto* mesh=pending.meshes+n;const auto vertices=get<std::uint16_t>(part,392),faces=get<std::uint16_t>(part,394),physiques=get<std::uint16_t>(part,396);const unsigned expandedCount=3u*faces;
        if(expandedCount>64000 || vertices>64000){message(&context->diagnostics,"InitVertex : %s : %d",reinterpret_cast<const char*>(part),expandedCount);return RF_LEGACY_RUNTIME_LIMIT;}
        if(RF455_LoadMesh08Materials(mesh,part,reinterpret_cast<const char*>(model->bytes+276),context->base.textures->directory,&materials)!=RF_MESH_RUNTIME_OK)return RF_LEGACY_RUNTIME_HEADER;
        put(mesh->bytes,5086,expandedCount);put(mesh->bytes,5090,expandedCount);Block expanded={&memory};expanded.pointer=memory.allocate(memory.context,64u*expandedCount);if(!expanded.pointer)return RF_LEGACY_RUNTIME_MEMORY;std::memset(expanded.pointer,0,64u*expandedCount);
        RF455Mesh08Part header={};header.header=part;header.vertexCount=header.indexCount=static_cast<std::uint16_t>(expandedCount);auto flag=get<unsigned>(model->bytes,796);const auto status=RF455_ApplyMesh08Header(mesh,&header,&context->base.matrices,&flag);put(model->bytes,796,flag);if(status!=RF_MESH_RUNTIME_OK)return RF_LEGACY_RUNTIME_HEADER;
        auto& scratch=context->scratch->vertices;grow(scratch,vertices);const auto* exports=get<const unsigned char*>(part,696);if(vertices && !exports)return RF_LEGACY_RUNTIME_FORMAT;
        for(unsigned i=0;i<vertices;++i){auto* v=scratch.data()+64*i;RF455_ConvertLegacyVertex64(v,exports+28*i);put<unsigned>(v,12,0x3f800000);std::memset(v+16,0,16);}
        const auto* physique=get<const unsigned char*>(part,704);if(physique){const auto decoded=RF455_DecodeLegacyWeights(scratch.data(),vertices,physique,physiques,&context->diagnostics);if(decoded!=RF_LEGACY_RUNTIME_OK)return decoded;}
        Block tangents={&memory};if(mtg.file){tangents.pointer=memory.allocate(memory.context,84u*faces);if(!tangents.pointer)return RF_LEGACY_RUNTIME_MEMORY;if(faces && std::fread(tangents.pointer,84u*faces,1,mtg.file)!=1)return RF_LEGACY_RUNTIME_IO;}
        const auto* triangles=get<const unsigned char*>(part,700);if(faces && !triangles)return RF_LEGACY_RUNTIME_FORMAT;
        for(unsigned f=0;f<faces;++f)for(unsigned corner=0;corner<3;++corner){const auto index=get<unsigned>(triangles+88*f,4*corner);if(index>=vertices)return RF_LEGACY_RUNTIME_FORMAT;auto* to=static_cast<unsigned char*>(expanded.pointer)+64*(3*f+corner);std::memcpy(to,scratch.data()+64*index,64);
            if(mtg.file)for(unsigned j=0;j<3;++j)copyFloat(to+52+4*j,static_cast<const unsigned char*>(tangents.pointer)+84*f+28*corner+4*j);
            RF455_ConvertLegacyUv64(to,triangles+88*f+48+12*corner);
        }
        if(tangents.pointer){memory.release(memory.context,tangents.pointer);tangents.pointer=nullptr;}
        if(faces){if(physique && context->rendererMode==2){if(!physiques)return RF_LEGACY_RUNTIME_PHYSIQUE;if(get<std::int32_t>(physique,4)>2){put(mesh->bytes,4506,expanded.pointer);expanded.pointer=nullptr;++result.cpuRetainedMeshes;}}
            if(expanded.pointer){unsigned unique=0;const auto indexed=RF455_IndexLegacyVertices(expanded.pointer,expandedCount,mesh,context,&unique);if(indexed!=RF_LEGACY_RUNTIME_OK)return indexed;put(mesh->bytes,5086,unique);++result.indexedMeshes;}
        }
    }
    if(mtg.file){std::fclose(mtg.file);mtg.file=nullptr;}
    for(unsigned n=0;n<count;++n)pending.meshes[n].bytes[512]=0;
    RF455_BindMeshParents(pending.meshes,count,pending.meshes,count);
    RF455MeshStorage* parents=pending.meshes;int parentCount=count;
    if(external){parents=get<RF455MeshStorage*>(external->bytes,536);parentCount=get<int>(external->bytes,532);RF455_BindMeshParents(parents,parentCount,pending.meshes,count);}
    if(count && !get<unsigned>(imported->bytes,24))for(unsigned n=0;n<count;++n){auto* bytes=pending.meshes[n].bytes;auto* parent=get<RF455MeshStorage*>(bytes,518);if(parent)context->base.matrices.multiply(bytes+4702,bytes+4574,parent->bytes+4638);}
    const auto bound=RF455_ResolveLegacyBones(parents,parentCount,pending.meshes,count,imported,&context->diagnostics,&result.bindings);if(bound!=RF_LEGACY_RUNTIME_OK)return bound;
    put(model->bytes,536,pending.meshes);put(model->bytes,532,count);pending.meshes=nullptr;auto* meshes=get<RF455MeshStorage*>(model->bytes,536);
    for(unsigned n=0;n<count;++n){char first[100]={},second[100]={};std::sscanf(reinterpret_cast<const char*>(meshes[n].bytes),"%s%s",first,second);_strupr(first);if(!std::strcmp(first,"BONE"))put<unsigned>(meshes[n].bytes,5567,1);}
    result.publishedMeshes=count;*stats=result;return RF_LEGACY_RUNTIME_OK;
}
