#include "client455_shaders.h"
#include "client455_enhanced_lighting.h"
#include "client455_shader_key.h"
#if defined(RF_CLIENT_455_CACHED_CHARACTER_SHADER)
#include "client455_character_rfs.h"
#endif
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <limits>
#include <new>
#include <stdexcept>
#include <utility>

namespace {
template<class T>void release(T*& value){if(value){value->Release();value=nullptr;}}
void releaseProgram(RF455ShaderProgram& program){
    release(program.vertex);release(program.pixel);
    release(program.vertexConstants);release(program.pixelConstants);
}
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
constexpr const char* characterShaderFiles[]={
    ".\\System\\shader\\sh_basic.shr", ".\\System\\shader\\sh_normal.shr",
    ".\\System\\shader\\sh_norm_spec.shr", ".\\System\\shader\\sh_shadow.shr",
    ".\\System\\shader\\sh_basic_Bump.shr", ".\\System\\shader\\sh_basic_BumpEffect.shr",
    ".\\System\\shader\\sh_basic_Scroll.shr", ".\\System\\shader\\sh_basic_DScroll.shr",
    ".\\System\\shader\\sh_basic_EnvScroll.shr", ".\\System\\shader\\sh_basic_GradeEffect.shr",
    ".\\System\\shader\\sh_basic_GradeEnvEffect.shr", ".\\System\\shader\\sh_basic_alpha.shr",
};

template<class Shader, class Create>
HRESULT compileReplacementStage(const RF455ShaderApi& api, const std::string& source,
    const char* profile, IUnknown*& constants, Shader*& shader, Create create)
{
    RF455D3DXBuffer* code = nullptr;
    RF455D3DXBuffer* errors = nullptr;
    HRESULT result = api.compile(source.c_str(),static_cast<UINT>(source.size()),nullptr,nullptr,
        "main",profile,0x8008,&code,&errors,&constants);
    if (result == S_OK) {
        const auto* bytecode = code ? static_cast<const DWORD*>(code->GetBufferPointer()) : nullptr;
        result = bytecode ? create(bytecode,&shader) : E_FAIL;
        if (SUCCEEDED(result) && !shader) result = E_FAIL;
    } else if (SUCCEEDED(result)) result = E_FAIL;
    release(code);
    release(errors);
    return result;
}
}
extern "C" void RF455_ConstructShaderManager(RF455ShaderManager* manager){std::memset(manager,0,sizeof(*manager));}
extern "C" void RF455_ReleaseShaderManager(RF455ShaderManager* manager){
    RF455_ReleaseEnhancedActorLighting(manager);
    for(unsigned i=0;i<manager->count;++i)releaseProgram(manager->programs[i]);
    for(unsigned i=0;i<manager->declarationCount;++i)release(manager->declarations[i]);
    std::free(manager->programs);manager->programs=nullptr;manager->capacity=manager->count=0;
    std::free(manager->declarations);manager->declarations=nullptr;manager->declarationCapacity=manager->declarationCount=0;
}
namespace {
int parseShaderSources(char* data,RF455ShaderSources* output)
{
    char* vertex = std::strstr(data,"[vertex shader]");
    char* pixel = std::strstr(data,"[pixel shader]");
    RF455ShaderSources result;
    if (vertex) {
        *vertex = 0; vertex += 15;
        while (*vertex == 13 || *vertex == 10) ++vertex;
        result.hasVertex = true;
        for (auto* p = data; p < vertex; ++p) if (*p == 10) ++result.vertexLine;
    }
    if (pixel) {
        *pixel = 0; pixel += 14;
        while (*pixel == 13 || *pixel == 10) ++pixel;
        result.hasPixel = true;
        for (auto* p = data; p < pixel; ++p) if (*p == 10) ++result.pixelLine;
    }
    if (vertex) result.vertex = vertex;
    if (pixel) result.pixel = pixel;
    *output = std::move(result);
    return 1;
}
}

extern "C" int RF455_ReadShaderSources(const char* input,RF455ShaderSources* output){
    if(!input || !output)return 0;
#if defined(RF_CLIENT_455_CACHED_CHARACTER_SHADER)
    try {
        // Client 455 x86 RVA 0x53A6A0 tries the loose encoded source first.
        std::string cached = input;
        const auto dot = cached.find_last_of('.');
        if (dot != std::string::npos) cached.resize(dot);
        cached += ".sho";
        constexpr std::uint64_t maxBytes = 4u * 1024u * 1024u;
        auto* cache = RF455_GetCharacterRfsCache();
        auto source = cache->ReadLooseBytes(cached.c_str(), maxBytes);
        const bool encoded = source.status != RF455ResourceReadStatus::Unavailable;
        if (!encoded) source = cache->ReadLooseBytes(input, maxBytes);
        if (source.status != RF455ResourceReadStatus::Ready || !source.bytes) return 0;
        const auto length = source.bytes->size();
        std::vector<char> data(length + 1);
        if (length) std::memcpy(data.data(), source.bytes->data(), length);
        if (encoded)
            for (std::size_t i = 0; i < length; ++i) data[i] ^= static_cast<char>(RF455_SHADER_KEY[i % 137]);
        const int parsed = parseShaderSources(data.data(), output);
        if (!output->hasVertex && !output->hasPixel)
            cache->RemoveLooseBytes(encoded ? cached.c_str() : input);
        return parsed;
    } catch (const std::bad_alloc&) {
        return 0;
    } catch (const std::length_error&) {
        return 0;
    }
#else
    std::string cached=input;const auto dot=cached.find_last_of('.');if(dot!=std::string::npos)cached.resize(dot);cached+=".sho";
    FILE* file=std::fopen(cached.c_str(),"rb");const bool encoded=file!=nullptr;
    if(!file)file=std::fopen(input,"rb");if(!file)return 0;
    std::fseek(file,0,SEEK_END);const long length=std::ftell(file);std::fseek(file,0,SEEK_SET);
    if(length<0){std::fclose(file);return 0;}
    std::vector<char> data(static_cast<std::size_t>(length)+1);
    const bool complete=!length || std::fread(data.data(),1,static_cast<std::size_t>(length),file)==static_cast<std::size_t>(length);std::fclose(file);if(!complete)return 0;
    if(encoded)for(unsigned i=0;i<static_cast<unsigned>(length);++i)data[i]^=static_cast<char>(RF455_SHADER_KEY[i%137]);
    data[static_cast<std::size_t>(length)]=0;
    return parseShaderSources(data.data(), output);
#endif
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
    int last=-1;for(const auto* path:characterShaderFiles)last=RF455_LoadShaderProgram(manager,api,path,nullptr,nullptr);return last;
}

HRESULT RF455_InitializeReplacementCharacterShaders(RF455ShaderManager* manager, const RF455ShaderApi* api,
    IDirect3DVertexDeclaration9** declaration64, IDirect3DVertexDeclaration9** declaration36)
{
    if (!manager || !manager->device || manager->programs || manager->declarations || manager->count ||
        manager->capacity || manager->declarationCount || manager->declarationCapacity || !api || !api->compile ||
        !declaration64 || !declaration36 || declaration64 == declaration36 || *declaration64 || *declaration36)
        return E_INVALIDARG;

    auto* device = manager->device;
    struct StagedShaders {
        RF455ShaderManager manager{};
        IDirect3DVertexDeclaration9* declaration64 = nullptr;
        IDirect3DVertexDeclaration9* declaration36 = nullptr;
        ~StagedShaders(){RF455_ReleaseShaderManager(&manager);release(declaration64);release(declaration36);}
    } staged;
    staged.manager.device = device;
    HRESULT result = device->CreateVertexDeclaration(elements64,&staged.declaration64);
    if (FAILED(result) || !staged.declaration64) return FAILED(result) ? result : E_FAIL;
    result = device->CreateVertexDeclaration(elements36,&staged.declaration36);
    if (FAILED(result) || !staged.declaration36) return FAILED(result) ? result : E_FAIL;

    try {
        for (const auto* path : characterShaderFiles) {
            RF455ShaderSources sources;
            if (!RF455_ReadShaderSources(path,&sources) || (!sources.hasVertex && !sources.hasPixel)) return E_FAIL;
            RF455ShaderProgram program{};
            if (sources.hasVertex)
                result = compileReplacementStage(*api,sources.vertex,"vs_2_0",program.vertexConstants,program.vertex,
                    [device](const DWORD* code, IDirect3DVertexShader9** shader){return device->CreateVertexShader(code,shader);});
            if (SUCCEEDED(result) && sources.hasPixel)
                result = compileReplacementStage(*api,sources.pixel,"ps_3_0",program.pixelConstants,program.pixel,
                    [device](const DWORD* code, IDirect3DPixelShader9** shader){return device->CreatePixelShader(code,shader);});
            if (SUCCEEDED(result) && append(&staged.manager,program) < 0) result = E_OUTOFMEMORY;
            if (FAILED(result)) {releaseProgram(program);return result;}
        }
    } catch (const std::bad_alloc&) {
        return E_OUTOFMEMORY;
    } catch (const std::length_error&) {
        return E_OUTOFMEMORY;
    }
    *manager = staged.manager;
    *declaration64 = staged.declaration64;
    *declaration36 = staged.declaration36;
    staged.manager = {};
    staged.declaration64 = staged.declaration36 = nullptr;
    return S_OK;
}

#include "client455_enhanced_lighting.inc"
