//455904B60/904590 and named shader lookup/binding. Same ordinary owner as binary.
#include <cerrno>
#include <cctype>
#include <cmath>
#include <cstdlib>

namespace {
unsigned parameterType455(const char* token){
    static const char* names[]={"n","b","i","f","v","m44","t","timer"};
    for(unsigned i=0;i<8;++i)if(!std::strcmp(token,names[i]))return i;
    return 9;
}

struct SpecialTextProgram455 {
    std::string name;
    std::string profile;
    bool pixel;
};

struct SpecialTextRegistry455 {
    std::vector<SpecialTextProgram455> programs;
    std::vector<RF455SpecialObject> objects;
};

constexpr char specialTextDirectory455[] = ".\\System\\Shader\\";

struct SpecialTextInput455 {
    const char* pos;
    const char* end;

    bool skipSpace()
    {
        const auto* previous = pos;
        while (pos < end && std::isspace(static_cast<unsigned char>(*pos))) ++pos;
        return pos != previous;
    }

    bool text(std::string& value, std::size_t capacity)
    {
        skipSpace();
        const auto* first = pos;
        while (pos < end && !std::isspace(static_cast<unsigned char>(*pos))) ++pos;
        const auto size = static_cast<std::size_t>(pos - first);
        if (!size || size >= capacity) return false;
        value.assign(first, size);
        return true;
    }

    bool integer(int& value)
    {
        static_assert(sizeof(int) == 4 && sizeof(long) == 4, "R3S signed integer");
        skipSpace();
        char* last;
        errno = 0;
        const auto result = std::strtol(pos, &last, 10);
        if (last == pos || errno == ERANGE) return false;
        pos = last;
        value = static_cast<int>(result);
        return true;
    }

    bool real(float& value)
    {
        skipSpace();
        char* last;
        errno = 0;
        const auto result = std::strtof(pos, &last);
        if (last == pos || errno == ERANGE || !std::isfinite(result)) return false;
        pos = last;
        value = result;
        return true;
    }
};

bool readSpecialTextObject455(SpecialTextInput455& input, RF455SpecialObject& object)
{
    int first, second;
    if (!input.integer(first) || !input.integer(second)) return false;
    if (first >= 0) {
        object.vertex = static_cast<WORD>(first);
        object.pixel = static_cast<WORD>(second);
    } else {
        std::memcpy(&object, &second, 4);
    }
    if (object.vertex >= 128 || object.pixel >= 128) return false;

    std::string name;
    std::string type;
    std::size_t index = 0;
    while (input.text(name, 128)) {
        if (name == "}") return true;
        if (name == "{") continue;
        if (index == 10 || !input.text(type, 128)) return false;
        auto* destination = object.parameters + index * sizeof(RF455SpecialParameter);
        RF455SpecialParameter row{};
        std::memcpy(&row, destination, sizeof(row));
        // Inactive types keep this slot, and strcpy left the old name tail.
        std::memcpy(row.name, name.c_str(), name.size() + 1);
        row.type = parameterType455(type.c_str());
        if (row.type == 1 || row.type == 2) {
            if (!input.integer(row.integer)) return false;
            ++index;
        } else if (row.type >= 3 && row.type <= 5) {
            const auto values = row.type == 3 ? 1u : row.type == 4 ? 4u : 16u;
            for (unsigned i = 0; i < values; ++i)
                if (!input.real(row.values[i])) return false;
            ++index;
        }
        std::memcpy(destination, &row, sizeof(row));
    }
    return false;
}

// Client 455 x86 RVA 0x504B60. Parse before replacing the live shader tables.
bool parseSpecialText455(const unsigned char* bytes, std::size_t size, SpecialTextRegistry455& out,
                         bool& allocationFailed)
{
    if (!bytes || !size || std::memchr(bytes, 0, size)) return false;
    try {
        const std::string text(reinterpret_cast<const char*>(bytes), size);
        SpecialTextInput455 input{text.c_str(), text.c_str() + text.size()};
        SpecialTextRegistry455 next;
        std::string token;
        std::size_t stages[2]{};
        std::size_t repeatedObjects = 0;
        while (input.pos < input.end) {
            const bool trailingSpace = input.skipSpace();
            if (input.pos == input.end) {
                // The old while(!feof) executes a second [sh_list] after
                // whitespace. Failed scans keep its old count and closing brace.
                constexpr std::size_t maxObjects = 128;
                if (trailingSpace && repeatedObjects) {
                    const auto slots = maxObjects - next.objects.size();
                    next.objects.resize(next.objects.size() + (repeatedObjects < slots ? repeatedObjects : slots));
                }
                break;
            }
            if (!input.text(token, 256)) return false;
            repeatedObjects = 0;
            if (token == "[path]") {
                if (!input.text(token, 256)) return false;
                // A subsequent non-path tag uses the default directory.
            } else if (token == "[fx_list]") {
                int count;
                if (!input.integer(count) || count < 0) return false;
            } else if (token == "[vs_list]" || token == "[ps_list]") {
                const bool pixel = token == "[ps_list]";
                int count;
                if (!input.integer(count) || count < 0 ||
                    static_cast<std::size_t>(count) > 128 - stages[pixel])
                    return false;
                stages[pixel] += static_cast<std::size_t>(count);
                for (int i = 0; i < count; ++i) {
                    SpecialTextProgram455 program{{}, {}, pixel};
                    if (!input.text(program.name, 256) || !input.text(program.profile, 32) ||
                        sizeof(specialTextDirectory455) + program.name.size() > 256)
                        return false;
                    next.programs.push_back(std::move(program));
                }
            } else if (token == "[sh_list]") {
                int count;
                if (!input.integer(count) || count < 0 ||
                    static_cast<std::size_t>(count) > 128 - next.objects.size())
                    return false;
                repeatedObjects = static_cast<std::size_t>(count);
                for (int i = 0; i < count; ++i) {
                    RF455SpecialObject object{};
                    if (!readSpecialTextObject455(input, object)) return false;
                    next.objects.push_back(object);
                }
            }
        }
        out = std::move(next);
        return true;
    } catch (const std::bad_alloc&) {
        allocationFailed = true;
        return false;
    }
}

IUnknown* compileSpecialFile455(const char* file,const char* profile,IUnknown** constants){
    ID3DXBuffer *code=nullptr,*errors=nullptr;ID3DXConstantTable* table=nullptr;
    const HRESULT compiled=D3DXCompileShaderFromFileA(file,nullptr,nullptr,"main",profile,0,&code,&errors,&table);*constants=table;
    if(FAILED(compiled)){
        if(errors)specialWarning455(static_cast<const char*>(errors->GetBufferPointer()));
        releaseSpecial455(errors);
        releaseSpecial455(code);
        releaseSpecial455(*constants);
        return nullptr;
    }
    releaseSpecial455(errors);
    IUnknown* result=nullptr;HRESULT created;
    if(!_strnicmp(profile,"vs",2)){
        IDirect3DVertexShader9* p=nullptr;created=GetD3dDevice()->CreateVertexShader(static_cast<const DWORD*>(code->GetBufferPointer()),&p);result=p;
    }else if(!_strnicmp(profile,"ps",2)){
        IDirect3DPixelShader9* p=nullptr;created=GetD3dDevice()->CreatePixelShader(static_cast<const DWORD*>(code->GetBufferPointer()),&p);result=p;
    }else return code; //904590 returns the buffer for an unrecognized prefix.
    code->Release();
    if(FAILED(created)){specialWarning455("Shader creation failed");releaseSpecial455(result);releaseSpecial455(*constants);return nullptr;}
    return result;
}
RF455SpecialProgram* namedSpecial455(const char* name,bool pixel){
    auto* rows=pixel?special455.pixels:special455.vertices;const unsigned count=pixel?special455.pixelCount:special455.vertexCount;
    for(unsigned i=0;i<count;++i)if(!std::strcmp(rows[i].name,name))return rows+i;
    return nullptr;
}
}
const RF455SpecialParameter* RF455_GetSpecialShaderParameter(unsigned object,unsigned slot)
{
    const auto* record = RF455_GetSpecialShaderObject(object);
    return record && slot < 10 ? reinterpret_cast<const RF455SpecialParameter*>(record->parameters) + slot : nullptr;
}
IUnknown* RF455_GetSpecialShaderConstants(const char* name,bool pixel){auto* row=namedSpecial455(name,pixel);return row?row->constants:nullptr;}
HRESULT RF455_BindSpecialVertexShader(const char* name){
    if(!name){GetD3dDevice()->SetVertexShader(nullptr);return 0;}
    auto* row=namedSpecial455(name,false);return row?GetD3dDevice()->SetVertexShader(static_cast<IDirect3DVertexShader9*>(row->program)):1;
}
HRESULT RF455_BindSpecialPixelShader(const char* name){
    if(!name){GetD3dDevice()->SetPixelShader(nullptr);return 0;}
    auto* row=namedSpecial455(name,true);return row?GetD3dDevice()->SetPixelShader(static_cast<IDirect3DPixelShader9*>(row->program)):1;
}
int RF455_LoadSpecialShaderText()
{
    constexpr std::uint64_t maxBytes = 384u * 1024u;
    constexpr char path[] = ".\\System\\Shader\\Init.r3s";
    auto* cache = RF455_GetCharacterRfsCache();
    const auto source = cache->ReadLooseBytes(path, maxBytes);
    SpecialTextRegistry455 registry;
    const bool ready = source.status == RF455ResourceReadStatus::Ready && source.bytes;
    bool allocationFailed = false;
    if (!ready || !parseSpecialText455(source.bytes->data(), source.bytes->size(), registry, allocationFailed)) {
        if (ready && !allocationFailed) cache->RemoveLooseBytes(path);
        specialWarning455(path);
        return -1;
    }

    initSpecial455();
    for (const auto& entry : registry.programs) {
        char file[256];
        std::memcpy(file, specialTextDirectory455, sizeof(specialTextDirectory455) - 1);
        std::memcpy(file + sizeof(specialTextDirectory455) - 1, entry.name.c_str(), entry.name.size() + 1);
        if (_strnicmp(entry.profile.c_str(), entry.pixel ? "ps" : "vs", 2) != 0) {
            specialWarning455(file);
            continue;
        }
        IUnknown* constants = nullptr;
        IUnknown* program = compileSpecialFile455(file, entry.profile.c_str(), &constants);
        if (program)
            appendSpecial455(entry.pixel ? special455.pixels : special455.vertices,
                entry.pixel ? special455.pixelCount : special455.vertexCount, entry.name.c_str(), program, constants);
        else
            specialWarning455(file);
    }
    if (!registry.objects.empty())
        std::memcpy(special455.objects, registry.objects.data(), registry.objects.size() * sizeof(RF455SpecialObject));
    special455.objectCount = static_cast<unsigned>(registry.objects.size());
    return 0;
}
