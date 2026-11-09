#pragma once
#include <d3d9.h>

//903B90:128 rows in each table. These are engine shader objects, distinct
//from the Character program manager and its combined shader source files.
struct RF455SpecialProgram {char name[256];IUnknown* program;IUnknown* constants;};
struct RF455SpecialObject {WORD vertex,pixel;BYTE parameters[1960];};
struct RF455SpecialTables {
    RF455SpecialProgram *effects,*vertices,*pixels;
    RF455SpecialObject* objects;
    unsigned effectsCount,vertexCount,pixelCount,objectCount;
};
static_assert(sizeof(RF455SpecialProgram)==264&&sizeof(RF455SpecialObject)==1964,"455 special shader tables");
const RF455SpecialTables& RF455_GetSpecialShaderTables(); //Borrowed,read-only view.
void RF455_ReleaseSpecialShaders();
int RF455_LoadSpecialShaderBinary(); //905220 binary branch,0 on fclose success.
const RF455SpecialObject* RF455_GetSpecialShaderObject(unsigned);
IDirect3DVertexShader9* RF455_GetSpecialVertexShader(unsigned);
IDirect3DPixelShader9* RF455_GetSpecialPixelShader(unsigned);
