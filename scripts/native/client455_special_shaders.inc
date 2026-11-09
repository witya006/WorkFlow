//4559036D0..905220 binary shader registry. Included once by r3d3d8.cpp.
#include "client455_special_shaders.h"
#include "client455_shader_key.h"
#include <d3dx9.h>
#include <cstdio>
#include <cstring>

namespace {
RF455SpecialTables special455={};
template<class T>void releaseSpecial455(T*& p){if(p){p->Release();p=nullptr;}}
void specialWarning455(const char* text){Warning(const_cast<char*>(text),const_cast<char*>("Shader"));}
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
char* readSpecial455(const char* path,unsigned* length){
    FILE* f=std::fopen(path,"rb");if(!f)return nullptr;
    std::fseek(f,0,SEEK_END);*length=unsigned(std::ftell(f));std::fseek(f,0,SEEK_SET);
    auto* bytes=static_cast<char*>(Dmalloc(*length+1));std::fread(bytes,*length,1,f);std::fclose(f);
    for(unsigned i=0;i<*length;++i)bytes[i]^=char(RF455_SHADER_KEY[i%137]);
    return bytes; //Compiler receives length;reference does not write a terminator.
}
IUnknown* compileSpecial455(const char* source,unsigned length,const char* profile,IUnknown** constants){
    //Missing source is outside the reference's defined non-null input domain.
    if(!source||!source[0])return nullptr;
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
    }else return nullptr; //Reference leaves code/table stranded for an unknown prefix.
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
const RF455SpecialObject* RF455_GetSpecialShaderObject(unsigned index){return special455.objects+index;}
IDirect3DVertexShader9* RF455_GetSpecialVertexShader(unsigned index){
    return index<=special455.objectCount?static_cast<IDirect3DVertexShader9*>(special455.vertices[special455.objects[index].vertex].program):nullptr;
}
IDirect3DPixelShader9* RF455_GetSpecialPixelShader(unsigned index){
    return index<=special455.objectCount?static_cast<IDirect3DPixelShader9*>(special455.pixels[special455.objects[index].pixel].program):nullptr;
}
int RF455_LoadSpecialShaderBinary(){
    FILE* f=std::fopen("./system/shader/init.r3o","rb");
    if(!f)return RF455_LoadSpecialShaderText();
    initSpecial455();char path[256];int count=0;std::fread(path,256,1,f);std::fread(&count,4,1,f);
    for(int i=0;i<count;++i){
        char name[256];std::fread(name,256,1,f);char* dot=std::strrchr(name,'.');if(dot)*dot=0;std::strcat(name,".sho");char file[256];std::strcpy(file,path);std::strcat(file,name);
        unsigned length=0;char* source=readSpecial455(file,&length);ID3DXEffectPool* pool=nullptr;ID3DXEffect* effect=nullptr;ID3DXBuffer* errors=nullptr;
        if(FAILED(D3DXCreateEffectPool(&pool)))specialWarning455("Effect pool creation failed");
        if(FAILED(D3DXCreateEffect(GetD3dDevice(),source,length,nullptr,nullptr,0x8000,pool,&effect,&errors))){
            if(errors){specialWarning455(static_cast<const char*>(errors->GetBufferPointer()));errors->Release();if(pool)pool->Release();}
            effect=nullptr; //Pool pointer is retained by9036D0,including this failure.
        }
        appendSpecial455(special455.effects,special455.effectsCount,nullptr,effect,pool);if(source)Dfree(source);
    }
    for(unsigned kind=0;kind<2;++kind){
        std::fread(&count,4,1,f);
        for(int i=0;i<count;++i){
            char name[256],profile[32],file[256];std::fread(name,256,1,f);std::fread(profile,32,1,f);
            char* dot=std::strrchr(name,'.');if(dot)*dot=0;std::strcat(name,".sho");std::strcpy(file,path);std::strcat(file,name);
            unsigned length=0;char* source=readSpecial455(file,&length);IUnknown* constants=nullptr;IUnknown* program=compileSpecial455(source,length,profile,&constants);
            if(program)appendSpecial455(kind?special455.pixels:special455.vertices,kind?special455.pixelCount:special455.vertexCount,name,program,constants);
            else specialWarning455(file);
            if(source)Dfree(source);
        }
    }
    std::fread(&count,4,1,f);
    for(int i=0;i<count;++i){
        auto* row=reinterpret_cast<BYTE*>(special455.objects+i);int parameters=0;
        std::fread(row,4,1,f);std::fread(row+2,4,1,f);std::fread(&parameters,4,1,f); //Deliberately overlapping DWORD reads.
        for(int j=0;j<parameters;++j)std::fread(row+4+j*196,196,1,f);
    }
    //905220 does NOT publish count to1175780. Slot0 is valid even for count0.
    return std::fclose(f);
}
#include "client455_special_shader_text.inc"
