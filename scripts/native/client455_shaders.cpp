#include "client455_shaders.h"
#include "client455_enhanced_lighting.h"
#include "client455_shader_key.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <limits>
#include <utility>

namespace {
template<class T>void release(T*& value){if(value){value->Release();value=nullptr;}}
int append(RF455ShaderManager* manager,const RF455ShaderProgram& program){
    if(manager->count>=manager->capacity){
        if(manager->capacity>(std::numeric_limits<unsigned>::max)()/32)return -1;
        const unsigned next=manager->capacity?2*manager->capacity:8;
        void* data=std::realloc(manager->programs,sizeof(program)*next);
        if(!data)return -1; // Own OOM policy outside certified reference domain.
        manager->programs=static_cast<RF455ShaderProgram*>(data);manager->capacity=next;
    }
    manager->programs[manager->count]=program;return static_cast<int>(manager->count++);
}
void failure(RF455ShaderFailure* output,const RF455ShaderProgram& program,RF455D3DXBuffer* code=nullptr,RF455D3DXBuffer* errors=nullptr){
    if(output){output->orphan=program;output->code=code;output->errors=errors;}
}
void diagnostic(RF455ShaderFailure* output,RF455D3DXBuffer* errors){
    if(output && errors)output->diagnostic=static_cast<const char*>(errors->GetBufferPointer());
}
const D3DVERTEXELEMENT9 elements64[]={
    {0,0,D3DDECLTYPE_FLOAT3,0,D3DDECLUSAGE_POSITION,0},
    {0,12,D3DDECLTYPE_FLOAT3,0,D3DDECLUSAGE_BLENDWEIGHT,0},
    {0,24,D3DDECLTYPE_SHORT4,0,D3DDECLUSAGE_BLENDINDICES,0},
    {0,32,D3DDECLTYPE_FLOAT3,0,D3DDECLUSAGE_NORMAL,0},
    {0,44,D3DDECLTYPE_FLOAT2,0,D3DDECLUSAGE_TEXCOORD,0},
    {0,52,D3DDECLTYPE_FLOAT3,0,D3DDECLUSAGE_TANGENT,0},D3DDECL_END()
};
const D3DVERTEXELEMENT9 elements36[]={
    {0,0,D3DDECLTYPE_FLOAT3,0,D3DDECLUSAGE_POSITION,0},
    {0,12,D3DDECLTYPE_FLOAT1,0,D3DDECLUSAGE_BLENDWEIGHT,0},
    {0,16,D3DDECLTYPE_FLOAT3,0,D3DDECLUSAGE_NORMAL,0},
    {0,28,D3DDECLTYPE_FLOAT2,0,D3DDECLUSAGE_TEXCOORD,0},D3DDECL_END()
};
}
extern "C" void RF455_ConstructShaderManager(RF455ShaderManager* manager){std::memset(manager,0,sizeof(*manager));}
extern "C" void RF455_ReleaseShaderManager(RF455ShaderManager* manager){
    RF455_ReleaseEnhancedActorLighting(manager);
    for(unsigned i=0;i<manager->count;++i){auto& p=manager->programs[i];release(p.vertex);release(p.pixel);release(p.vertexConstants);release(p.pixelConstants);}
    for(unsigned i=0;i<manager->declarationCount;++i)release(manager->declarations[i]);
    std::free(manager->programs);manager->programs=nullptr;manager->capacity=manager->count=0;
    std::free(manager->declarations);manager->declarations=nullptr;manager->declarationCapacity=manager->declarationCount=0;
}
extern "C" int RF455_ReadShaderSources(const char* input,RF455ShaderSources* output){
    if(!input || !output)return 0;
    std::string cached=input;const auto dot=cached.find_last_of('.');if(dot!=std::string::npos)cached.resize(dot);cached+=".sho";
    FILE* file=std::fopen(cached.c_str(),"rb");const bool encoded=file!=nullptr;
    if(!file)file=std::fopen(input,"rb");if(!file)return 0;
    std::fseek(file,0,SEEK_END);const long length=std::ftell(file);std::fseek(file,0,SEEK_SET);
    if(length<0){std::fclose(file);return 0;}
    std::vector<char> data(static_cast<std::size_t>(length)+1);
    const bool complete=!length || std::fread(data.data(),1,static_cast<std::size_t>(length),file)==static_cast<std::size_t>(length);std::fclose(file);if(!complete)return 0;
    if(encoded)for(unsigned i=0;i<static_cast<unsigned>(length);++i)data[i]^=static_cast<char>(RF455_SHADER_KEY[i%137]);
    data[static_cast<std::size_t>(length)]=0;
    char* vertex=std::strstr(data.data(),"[vertex shader]");char* pixel=std::strstr(data.data(),"[pixel shader]");
    RF455ShaderSources result;
    if(vertex){*vertex=0;vertex+=15;while(*vertex==13 || *vertex==10)++vertex;result.hasVertex=true;for(auto* p=data.data();p<vertex;++p)if(*p==10)++result.vertexLine;}
    if(pixel){*pixel=0;pixel+=14;while(*pixel==13 || *pixel==10)++pixel;result.hasPixel=true;for(auto* p=data.data();p<pixel;++p)if(*p==10)++result.pixelLine;}
    if(vertex)result.vertex=vertex;if(pixel)result.pixel=pixel;*output=std::move(result);return 1;
}
extern "C" int RF455_CreateShaderProgram(RF455ShaderManager* manager,const RF455ShaderApi* api,const char* vertex,const char* pixel,const char* prefix,RF455ShaderFailure* details){
    if(details)*details=RF455ShaderFailure{};
    if(!manager || !manager->device || !api || !api->compile || (!vertex && !pixel))return -1;
    RF455ShaderProgram program={};RF455D3DXBuffer* code=nullptr;RF455D3DXBuffer* errors=nullptr;
    if(vertex){
        const std::string source=std::string(prefix?prefix:"")+vertex;
        const HRESULT hr=api->compile(source.c_str(),static_cast<UINT>(source.size()),nullptr,nullptr,"main","vs_2_0",0x8008,&code,&errors,&program.vertexConstants);
        if(hr!=S_OK)diagnostic(details,errors);
        else if(!code || FAILED(manager->device->CreateVertexShader(static_cast<const DWORD*>(code->GetBufferPointer()),&program.vertex))){failure(details,program,code,errors);return -1;}
        release(code);release(errors);
        if(!program.vertex){failure(details,program);return -1;}
    }
    if(pixel){
        const std::string source=std::string(prefix?prefix:"")+pixel;
        const HRESULT hr=api->compile(source.c_str(),static_cast<UINT>(source.size()),nullptr,nullptr,"main","ps_3_0",0x8008,&code,&errors,&program.pixelConstants);
        if(hr!=S_OK)diagnostic(details,errors);
        else if(code)manager->device->CreatePixelShader(static_cast<const DWORD*>(code->GetBufferPointer()),&program.pixel); // HRESULT ignored by reference.
        release(code);release(errors);
        if(!program.pixel){failure(details,program);return -1;}
    }
    const int id=append(manager,program);if(id<0)failure(details,program);return id;
}
extern "C" int RF455_LoadShaderProgram(RF455ShaderManager* manager,const RF455ShaderApi* api,const char* filename,const char* prefix,RF455ShaderFailure* failureInfo){
    if(failureInfo)*failureInfo=RF455ShaderFailure{};
    RF455ShaderSources source;if(!RF455_ReadShaderSources(filename,&source))return -1;
    return RF455_CreateShaderProgram(manager,api,source.hasVertex?source.vertex.c_str():nullptr,source.hasPixel?source.pixel.c_str():nullptr,prefix,failureInfo);
}
extern "C" void RF455_ReleaseCharacterDeclarations(IDirect3DVertexDeclaration9** declaration64,IDirect3DVertexDeclaration9** declaration36){release(*declaration64);release(*declaration36);}
extern "C" int RF455_InitializeCharacterShaders(RF455ShaderManager* manager,const RF455ShaderApi* api,IUnknown** sprite,IDirect3DVertexDeclaration9** declaration64,IDirect3DVertexDeclaration9** declaration36){
    if(!manager || !manager->device || !api || !api->compile || !api->sprite || !sprite || !declaration64 || !declaration36)return -1;
    api->sprite(manager->device,sprite); // No release of a previous sprite in91FD40.
    RF455_ReleaseCharacterDeclarations(declaration64,declaration36);
    manager->device->CreateVertexDeclaration(elements64,declaration64);
    manager->device->CreateVertexDeclaration(elements36,declaration36);
    RF455_ReleaseShaderManager(manager);
    const char* names[]={"sh_basic","sh_normal","sh_norm_spec","sh_shadow","sh_basic_Bump","sh_basic_BumpEffect","sh_basic_Scroll","sh_basic_DScroll","sh_basic_EnvScroll","sh_basic_GradeEffect","sh_basic_GradeEnvEffect","sh_basic_alpha"};
    int last=-1;for(const auto* name:names){const std::string path=std::string(".\\System\\shader\\")+name+".shr";last=RF455_LoadShaderProgram(manager,api,path.c_str(),nullptr,nullptr);}return last;
}

#include "client455_enhanced_lighting.inc"
