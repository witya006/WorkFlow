#pragma once
#include <d3d9.h>

//903B90:128 rows in each table. These are engine shader objects, distinct
//from the Character program manager and its combined shader source files.
struct RF455SpecialProgram {char name[256];IUnknown* program;IUnknown* constants;};
struct RF455SpecialObject {WORD vertex,pixel;BYTE parameters[1960];};
struct RF455SpecialParameter {char name[128];DWORD type;union{int integer;float values[16];};};
static_assert(sizeof(RF455SpecialParameter)==196,"455 shader parameter record");
struct RF455SpecialTables {
    RF455SpecialProgram *effects,*vertices,*pixels;
    RF455SpecialObject* objects;
    unsigned effectsCount,vertexCount,pixelCount,objectCount;
};
static_assert(sizeof(RF455SpecialProgram)==264&&sizeof(RF455SpecialObject)==1964,"455 special shader tables");
const RF455SpecialTables& RF455_GetSpecialShaderTables(); //Borrowed,read-only view.
void RF455_ReleaseSpecialShaders();
int RF455_LoadSpecialShaderBinary(); //905220,binary then904B60 text fallback.
int RF455_LoadSpecialShaderText();
const RF455SpecialParameter* RF455_GetSpecialShaderParameter(unsigned object,unsigned slot);
HRESULT RF455_BindSpecialVertexShader(const char*);
HRESULT RF455_BindSpecialPixelShader(const char*);
IUnknown* RF455_GetSpecialShaderConstants(const char*,bool pixel);
const RF455SpecialObject* RF455_GetSpecialShaderObject(unsigned);
IDirect3DVertexShader9* RF455_GetSpecialVertexShader(unsigned);
IDirect3DPixelShader9* RF455_GetSpecialPixelShader(unsigned);
