#pragma once
#include <d3d9.h>

struct RF455R3VertexProgram {
    IDirect3DVertexDeclaration9* declaration=nullptr;
    IDirect3DVertexShader9* shader=nullptr;
};
inline HRESULT RF455_BindR3VertexProgram(IDirect3DDevice9* device,const RF455R3VertexProgram& program){
    HRESULT hr=device->SetVertexDeclaration(program.declaration);return FAILED(hr)?hr:device->SetVertexShader(program.shader);
}
inline void RF455_ReleaseR3VertexProgram(RF455R3VertexProgram& program){
    if(program.shader)program.shader->Release();if(program.declaration)program.declaration->Release();program={};
}

// Explicit D3D9 operations at migrated legacy callers. Their error/state
// behavior still requires455comparison as part of the full engine port.
inline HRESULT RF455_SetFixedVertexFormat(IDirect3DDevice9* device,DWORD fvf){
    HRESULT hr=device->SetVertexShader(nullptr);return FAILED(hr)?hr:device->SetFVF(fvf);
}
inline HRESULT RF455_SetTargetAndDepth(IDirect3DDevice9* device,IDirect3DSurface9* target,IDirect3DSurface9* depth){
    HRESULT hr=device->SetRenderTarget(0,target);return FAILED(hr)?hr:device->SetDepthStencilSurface(depth);
}
