#pragma once
#include <windows.h>
#include <d3d9.h>
#include <string>

struct RF455D3DXBuffer : IUnknown {
    virtual void* STDMETHODCALLTYPE GetBufferPointer()=0;
    virtual DWORD STDMETHODCALLTYPE GetBufferSize()=0;
};
struct RF455ShaderApi {
    HRESULT (WINAPI* compile)(LPCSTR,UINT,const void*,void*,LPCSTR,LPCSTR,DWORD,RF455D3DXBuffer**,RF455D3DXBuffer**,IUnknown**);
    HRESULT (WINAPI* sprite)(IDirect3DDevice9*,IUnknown**);
};
struct RF455ShaderProgram {
    IDirect3DVertexShader9* vertex;
    IDirect3DPixelShader9* pixel;
    IUnknown* vertexConstants;
    IUnknown* pixelConstants;
};
// Known owner prefix only, not a claim about the complete private C++ class.
struct RF455ShaderManager {
    IDirect3DDevice9* device;
    unsigned capacity,count;
    RF455ShaderProgram* programs;
    unsigned declarationCapacity,declarationCount;
    IDirect3DVertexDeclaration9** declarations;
};
static_assert(sizeof(RF455ShaderProgram)==16 && sizeof(RF455ShaderManager)==28,"455 shader resource fields");
struct RF455ShaderSources {
    std::string vertex,pixel;
    bool hasVertex=false,hasPixel=false;
    unsigned vertexLine=0,pixelLine=0;
};
// Original failures can strand resources before publication. Report their
// borrowed addresses; production does not silently repair the reference leaks.
// A test may release them only AFTER observing the failure, as explicit cleanup.
struct RF455ShaderFailure {
    RF455ShaderProgram orphan={};
    RF455D3DXBuffer* code=nullptr;
    RF455D3DXBuffer* errors=nullptr;
    std::string diagnostic;
};
extern "C" {
void RF455_ConstructShaderManager(RF455ShaderManager*);
void RF455_ReleaseShaderManager(RF455ShaderManager*);
int RF455_ReadShaderSources(const char*,RF455ShaderSources*);
int RF455_CreateShaderProgram(RF455ShaderManager*,const RF455ShaderApi*,const char* vertex,const char* pixel,const char* prefix,RF455ShaderFailure*);
int RF455_LoadShaderProgram(RF455ShaderManager*,const RF455ShaderApi*,const char* filename,const char* prefix,RF455ShaderFailure*);
// Own logical owner views; no cast of the old D3D8 renderer or input EXE calls.
int RF455_InitializeCharacterShaders(RF455ShaderManager*,const RF455ShaderApi*,IUnknown** sprite,IDirect3DVertexDeclaration9** declaration64,IDirect3DVertexDeclaration9** declaration36);
void RF455_ReleaseCharacterDeclarations(IDirect3DVertexDeclaration9**,IDirect3DVertexDeclaration9**);
}
// The manager starts empty with a borrowed device. Publish all twelve programs
// and both declarations together, releasing temporary COM resources on failure.
HRESULT RF455_InitializeReplacementCharacterShaders(RF455ShaderManager*, const RF455ShaderApi*,
    IDirect3DVertexDeclaration9**, IDirect3DVertexDeclaration9**);
