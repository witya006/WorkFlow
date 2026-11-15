#if defined(RF_CLIENT_455_CACHED_VERTEX_SHADER)
#include "client455_character_rfs.h"
#include <cstring>
#include <memory>
#include <new>

static HRESULT readShaderCode455(const char* filename, DWORD kind,
                                 std::unique_ptr<DWORD[]>& code, bool& unavailable)
{
    // Client 455 x86 RVA 0x4D8540 reads loose bytecode before creating the
    // declaration and shader. The cache owns only the encoded bytes.
    constexpr std::uint64_t maxBytes = 1024u * 1024u;
    auto* cache = RF455_GetCharacterRfsCache();
    const auto source = cache->ReadLooseBytes(filename, maxBytes);
    unavailable = source.status == RF455ResourceReadStatus::Unavailable;
    if (source.status == RF455ResourceReadStatus::MemoryError) return E_OUTOFMEMORY;
    if (source.status != RF455ResourceReadStatus::Ready || !source.bytes) return E_FAIL;
    const auto invalid = [&]() {
        cache->RemoveLooseBytes(filename);
        return D3DXERR_INVALIDDATA;
    };
    const auto length = source.bytes->size();
    if (length < 2 * sizeof(DWORD) || length % sizeof(DWORD)) return invalid();
    DWORD version, end;
    std::memcpy(&version, source.bytes->data(), sizeof(version));
    std::memcpy(&end, source.bytes->data() + length - sizeof(end), sizeof(end));
    if ((version & 0xffff0000u) != kind || end != D3DSIO_END) return invalid();

    code.reset(new (std::nothrow) DWORD[length / sizeof(DWORD)]);
    if (!code) return E_OUTOFMEMORY;
    std::memcpy(code.get(), source.bytes->data(), length);
    return S_OK;
}

static HRESULT loadCreateShader455(const char* filename, const D3DVERTEXELEMENT9* elements,
                                   RF455R3VertexProgram* program, bool& unavailable)
{
    std::unique_ptr<DWORD[]> code;
    HRESULT hr = readShaderCode455(filename, 0xfffe0000u, code, unavailable);
    if (hr != S_OK) return hr;
    auto* device = GetD3dDevice();
    if (!device || !program) return E_FAIL;
    RF455R3VertexProgram pending;
    hr = device->CreateVertexDeclaration(elements, &pending.declaration);
    if (hr == S_OK) hr = device->CreateVertexShader(code.get(), &pending.shader);
    if (hr != S_OK) {
        RF455_ReleaseR3VertexProgram(pending);
        return hr;
    }
    RF455_ReleaseR3VertexProgram(*program);
    *program = pending;
    return hr;
}

static void releasePixelShader455(IDirect3DPixelShader9*& shader)
{
    if (shader) shader->Release();
    shader = nullptr;
}

static HRESULT loadCreatePixelShader455(const char* filename, IDirect3DPixelShader9*& program)
{
    std::unique_ptr<DWORD[]> code;
    bool unavailable;
    HRESULT hr = readShaderCode455(filename, 0xffff0000u, code, unavailable);
    if (hr != S_OK) return hr;
    auto* device = GetD3dDevice();
    if (!device) return E_FAIL;
    IDirect3DPixelShader9* pending = nullptr;
    hr = device->CreatePixelShader(code.get(), &pending);
    if (hr != S_OK) {
        releasePixelShader455(pending);
        return hr;
    }
    releasePixelShader455(program);
    program = pending;
    return S_OK;
}

HRESULT LoadCreateShader(char* filename,const D3DVERTEXELEMENT9* elements,RF455R3VertexProgram* program)
{
    bool unavailable;
    return loadCreateShader455(filename, elements, program, unavailable);
}
#else
HRESULT LoadCreateShader(char* filename,const D3DVERTEXELEMENT9* elements,RF455R3VertexProgram* program){
    FILE* file=fopen(filename,"rb");if(!file)return E_FAIL;
    fseek(file,0,SEEK_END);long length=ftell(file);fseek(file,0,SEEK_SET);
    if(length<4 || length%4){fclose(file);return D3DXERR_INVALIDDATA;}
    std::vector<DWORD> code(static_cast<unsigned>(length)/4);
    bool complete=fread(code.data(),static_cast<unsigned>(length),1,file)==1;fclose(file);if(!complete)return E_FAIL;
    HRESULT hr=GetD3dDevice()->CreateVertexDeclaration(elements,&program->declaration);
    if(FAILED(hr))return hr;
    hr=GetD3dDevice()->CreateVertexShader(code.data(),&program->shader);
    if(FAILED(hr)){program->declaration->Release();program->declaration=nullptr;}
    return hr;
}
#endif
