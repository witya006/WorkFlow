#pragma once
#include <d3d9.h>

// Source-owned declaration shared by the two BSP light geometry passes.
HRESULT RF455_CreateBspLightDeclaration(IDirect3DDevice9* device);
void RF455_ReleaseBspLightDeclaration();
IDirect3DVertexDeclaration9* RF455_BspLightDeclaration();
