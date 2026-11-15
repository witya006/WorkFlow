//4559036D0..905220 binary shader registry. Included once by r3d3d8.cpp.
#include "client455_special_shaders.h"
#include "client455_shader_key.h"
#include "client455_character_rfs.h"
#include <d3dx9.h>
#include <array>
#include <cstdio>
#include <cstring>
#include <new>
#include <utility>

namespace {
RF455SpecialTables special455={};

struct SpecialBinaryProgram455 {
    std::string name;
    std::string profile;
};

struct SpecialBinaryRegistry455 {
    std::string path;
    std::vector<std::string> effects;
    std::array<std::vector<SpecialBinaryProgram455>, 2> programs;
    std::vector<RF455SpecialObject> objects;
};

struct SpecialBinaryInput455 {
    const unsigned char* next;
    std::size_t remaining;

    const unsigned char* take(std::size_t size)
    {
        if (size > remaining) return nullptr;
        const auto* bytes = next;
        next += size;
        remaining -= size;
        return bytes;
    }

    bool count(std::int32_t& value, std::int32_t limit)
    {
        const auto* bytes = take(sizeof(value));
        if (!bytes) return false;
        std::memcpy(&value, bytes, sizeof(value));
        return value >= 0 && value <= limit;
    }

    bool text(std::size_t size, std::string& value)
    {
        const auto* bytes = take(size);
        if (!bytes) return false;
        const auto* end = static_cast<const unsigned char*>(std::memchr(bytes, 0, size));
        if (!end) return false;
        value.assign(reinterpret_cast<const char*>(bytes), static_cast<std::size_t>(end - bytes));
        return true;
    }
};

bool readSpecialBinaryName455(SpecialBinaryInput455& input, const std::string& path, std::string& name)
{
    if (!input.text(256, name)) return false;
    const auto dot = name.find_last_of('.');
    if (dot != std::string::npos) name.resize(dot);
    name += ".sho";
    return path.size() + name.size() < 256;
}

// Client 455 x86 RVA 0x505220. Validate the complete registry before touching
// the existing tables or attempting to create any GPU objects.
bool parseSpecialBinary455(const unsigned char* data, std::size_t size, SpecialBinaryRegistry455& out,
                           bool& allocationFailed)
{
    if (!data) return false;
    try {
        SpecialBinaryInput455 input{data, size};
        SpecialBinaryRegistry455 next;
        std::int32_t count;
        if (!input.text(256, next.path) || !input.count(count, 128)) return false;
        next.effects.resize(static_cast<std::size_t>(count));
        for (auto& name : next.effects)
            if (!readSpecialBinaryName455(input, next.path, name)) return false;

        for (auto& programs : next.programs) {
            if (!input.count(count, 128)) return false;
            programs.resize(static_cast<std::size_t>(count));
            for (auto& program : programs) {
                if (!readSpecialBinaryName455(input, next.path, program.name) ||
                    !input.text(32, program.profile))
                    return false;
            }
        }

        if (!input.count(count, 128)) return false;
        next.objects.resize(static_cast<std::size_t>(count));
        for (auto& object : next.objects) {
            const auto* words = input.take(8);
            std::int32_t parameters;
            if (!words || !input.count(parameters, 10)) return false;
            auto* row = reinterpret_cast<unsigned char*>(&object);
            std::memcpy(row, words, 4);
            std::memcpy(row + 2, words + 4, 4); // The second DWORD overlaps the first and parameter 0.
            if (object.vertex >= 128 || object.pixel >= 128) return false;
            const auto parameterBytes = static_cast<std::size_t>(parameters) * sizeof(RF455SpecialParameter);
            const auto* serialized = input.take(parameterBytes);
            if (!serialized) return false;
            std::memcpy(object.parameters, serialized, parameterBytes);
        }
        out = std::move(next);
        return true;
    } catch (const std::bad_alloc&) {
        allocationFailed = true;
        return false;
    }
}

void specialBinaryPath455(const std::string& path, const std::string& name, char (&file)[256])
{
    std::memcpy(file, path.data(), path.size());
    std::memcpy(file + path.size(), name.c_str(), name.size() + 1);
}

template<class T>void releaseSpecial455(T*& p){if(p){p->Release();p=nullptr;}}
void specialWarning455(const char* text)
{
    // Warning appends the context and a six-byte suffix into 256 bytes.
    char context[] = "Shader";
    char message[256 - (sizeof(context) - 1) - 6];
    std::strncpy(message, text ? text : "", sizeof(message) - 1);
    message[sizeof(message) - 1] = 0;
    Warning(message, context);
}
void releasePrograms455(RF455SpecialProgram*& rows,unsigned& count){
    for(unsigned i=0;i<count;++i){releaseSpecial455(rows[i].program);releaseSpecial455(rows[i].constants);}
    count=0;if(rows){Dfree(rows);rows=nullptr;}
}
void initSpecial455(){
    auto* state=GetR3State();D3DCAPS9 caps={};GetD3dDevice()->GetDeviceCaps(&caps);
    if(caps.VertexShaderVersion<D3DVS_VERSION(1,1)||caps.PixelShaderVersion<D3DPS_VERSION(1,1)||state->mTextureUnitNum<4||!state->mIsUsedVertexShader)
        specialWarning455("Special shader capabilities below1.1/four textures"); //Warn,then continue.
    RF455_ReleaseSpecialShaders();
    special455.effects=static_cast<RF455SpecialProgram*>(Dmalloc(33792));std::memset(special455.effects,0,33792);
    special455.vertices=static_cast<RF455SpecialProgram*>(Dmalloc(33792));std::memset(special455.vertices,0,33792);
    special455.pixels=static_cast<RF455SpecialProgram*>(Dmalloc(33792));std::memset(special455.pixels,0,33792);
    special455.objects=static_cast<RF455SpecialObject*>(Dmalloc(251392));std::memset(special455.objects,0,251392);
}
char* readSpecial455(const char* path,unsigned* length)
{
    // Client 455 x86 RVA 0x503A70 opens a loose encoded shader and XORs its
    // 137-byte key into fresh compiler input on every creation.
    *length = 0;
    constexpr std::uint64_t maxBytes = 4u * 1024u * 1024u;
    const auto source = RF455_GetCharacterRfsCache()->ReadLooseBytes(path, maxBytes);
    if (source.status != RF455ResourceReadStatus::Ready || !source.bytes) return nullptr;
    const auto size = static_cast<unsigned>(source.bytes->size());
    auto* bytes = static_cast<char*>(Dmalloc(static_cast<int>(size + 1)));
    if (!bytes) return nullptr;
    for (unsigned i = 0; i < size; ++i)
        bytes[i] = static_cast<char>((*source.bytes)[i] ^ RF455_SHADER_KEY[i % 137]);
    bytes[size] = 0;
    *length = size;
    return bytes;
}
IUnknown* compileSpecial455(const char* source,unsigned length,const char* profile,IUnknown** constants){
    //Missing source is outside the reference's defined non-null input domain.
    if(!source||!length||!source[0])return nullptr;
    ID3DXBuffer *code=nullptr,*errors=nullptr;ID3DXConstantTable* table=nullptr;
    const HRESULT compiled=D3DXCompileShader(source,length,nullptr,nullptr,"main",profile,0,&code,&errors,&table);*constants=table;
    if(FAILED(compiled)){
        if(errors){specialWarning455(static_cast<const char*>(errors->GetBufferPointer()));errors->Release();}
        return nullptr;
    }
    IUnknown* program=nullptr;HRESULT created;
    if(!_strnicmp(profile,"vs",2)){
        IDirect3DVertexShader9* p=nullptr;created=GetD3dDevice()->CreateVertexShader(static_cast<const DWORD*>(code->GetBufferPointer()),&p);program=p;
    }else if(!_strnicmp(profile,"ps",2)){
        IDirect3DPixelShader9* p=nullptr;created=GetD3dDevice()->CreatePixelShader(static_cast<const DWORD*>(code->GetBufferPointer()),&p);program=p;
    }else{
        code->Release();
        releaseSpecial455(*constants);
        return nullptr;
    }
    code->Release();
    if(FAILED(created)){releaseSpecial455(program);releaseSpecial455(*constants);return nullptr;}
    return program;
}
void appendSpecial455(RF455SpecialProgram* rows,unsigned& count,const char* name,IUnknown* program,IUnknown* constants){
    if(count>=128){specialWarning455("Special shader table is full");return;}
    auto& row=rows[count++];if(name)std::memcpy(row.name,name,std::strlen(name));row.program=program;row.constants=constants;
}
}
const RF455SpecialTables& RF455_GetSpecialShaderTables(){return special455;}
void RF455_ReleaseSpecialShaders(){
    releasePrograms455(special455.effects,special455.effectsCount);releasePrograms455(special455.vertices,special455.vertexCount);releasePrograms455(special455.pixels,special455.pixelCount);
    special455.objectCount=0;if(special455.objects){Dfree(special455.objects);special455.objects=nullptr;}
}
const RF455SpecialObject* RF455_GetSpecialShaderObject(unsigned index)
{
    return special455.objects && index < 128 ? special455.objects + index : nullptr;
}

IDirect3DVertexShader9* RF455_GetSpecialVertexShader(unsigned index)
{
    if (!special455.vertices || index > special455.objectCount) return nullptr;
    const auto* object = RF455_GetSpecialShaderObject(index);
    return object && object->vertex < 128 ?
        static_cast<IDirect3DVertexShader9*>(special455.vertices[object->vertex].program) : nullptr;
}

IDirect3DPixelShader9* RF455_GetSpecialPixelShader(unsigned index)
{
    if (!special455.pixels || index > special455.objectCount) return nullptr;
    const auto* object = RF455_GetSpecialShaderObject(index);
    return object && object->pixel < 128 ?
        static_cast<IDirect3DPixelShader9*>(special455.pixels[object->pixel].program) : nullptr;
}
int RF455_LoadSpecialShaderBinary()
{
    constexpr char registryPath[] = "./system/shader/init.r3o";
    constexpr std::uint64_t maxRegistryBytes = 384u * 1024u;
    auto* cache = RF455_GetCharacterRfsCache();
    const auto input = cache->ReadLooseBytes(registryPath, maxRegistryBytes);
    if (input.status == RF455ResourceReadStatus::Unavailable) return RF455_LoadSpecialShaderText();
    SpecialBinaryRegistry455 registry;
    const bool ready = input.status == RF455ResourceReadStatus::Ready && input.bytes;
    bool allocationFailed = false;
    if (!ready || !parseSpecialBinary455(input.bytes->data(), input.bytes->size(), registry, allocationFailed)) {
        if (ready && !allocationFailed) cache->RemoveLooseBytes(registryPath);
        specialWarning455(registryPath);
        return -1;
    }

    initSpecial455();
    for (const auto& name : registry.effects) {
        char file[256];
        specialBinaryPath455(registry.path, name, file);
        unsigned length=0;char* source=readSpecial455(file,&length);ID3DXEffectPool* pool=nullptr;ID3DXEffect* effect=nullptr;ID3DXBuffer* errors=nullptr;
        if(FAILED(D3DXCreateEffectPool(&pool)))specialWarning455("Effect pool creation failed");
        if(source && length && FAILED(D3DXCreateEffect(GetD3dDevice(),source,length,nullptr,nullptr,0x8000,pool,&effect,&errors))){
            if(errors){
                specialWarning455(static_cast<const char*>(errors->GetBufferPointer()));
                releaseSpecial455(errors);
                releaseSpecial455(pool);
            }
            effect=nullptr;
        }
        appendSpecial455(special455.effects,special455.effectsCount,nullptr,effect,pool);if(source)Dfree(source);
    }
    for (std::size_t kind = 0; kind < registry.programs.size(); ++kind) {
        for (const auto& row : registry.programs[kind]) {
            char file[256];
            specialBinaryPath455(registry.path, row.name, file);
            if (_strnicmp(row.profile.c_str(), kind ? "ps" : "vs", 2)) {
                specialWarning455(file);
                continue;
            }
            unsigned length = 0;
            char* source = readSpecial455(file, &length);
            IUnknown* constants = nullptr;
            IUnknown* program = compileSpecial455(source, length, row.profile.c_str(), &constants);
            if (program) {
                appendSpecial455(kind ? special455.pixels : special455.vertices,
                    kind ? special455.pixelCount : special455.vertexCount, row.name.c_str(), program, constants);
            } else {
                specialWarning455(file);
                releaseSpecial455(constants);
            }
            if (source) Dfree(source);
        }
    }
    if (!registry.objects.empty())
        std::memcpy(special455.objects, registry.objects.data(), registry.objects.size() * sizeof(RF455SpecialObject));
    // 0x505220 leaves the published object count at zero, even after filling slots.
    return 0;
}
#include "client455_special_shader_text.inc"
