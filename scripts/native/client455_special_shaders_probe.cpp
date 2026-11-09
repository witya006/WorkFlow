#define main unusedWorldEntry134
#include "client455_world_probe.cpp"
#undef main
#include "client455_special_shaders.h"
#include <d3dx9.h>
#include <vector>
#include <array>
HRESULT D3D_R3RestoreDevice();
HRESULT D3D_R3InvalidateDevice();
static std::vector<BYTE> bytecode134(IUnknown* p,bool pixel){
    check(p!=nullptr,"real compiled shader134");UINT size=0;
    if(pixel){auto* s=static_cast<IDirect3DPixelShader9*>(p);check(SUCCEEDED(s->GetFunction(nullptr,&size)),"PS size134");std::vector<BYTE> bytes(size);check(SUCCEEDED(s->GetFunction(bytes.data(),&size)),"PS bytes134");return bytes;}
    auto* s=static_cast<IDirect3DVertexShader9*>(p);check(SUCCEEDED(s->GetFunction(nullptr,&size)),"VS size134");std::vector<BYTE> bytes(size);check(SUCCEEDED(s->GetFunction(bytes.data(),&size)),"VS bytes134");return bytes;
}
static int run134(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);InitR3Engine();SetWarningMessageProc(warningMessage);SetErrorMessageProc(errorMessage);
    auto* state=GetR3State();state->mScreenXsize=640;state->mScreenYsize=480;state->mbFullScreen=FALSE;ForceFullScreen();
    check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"ordinary device134");phase("device134");
    const auto& tables=RF455_GetSpecialShaderTables();check(tables.effects&&tables.vertices&&tables.pixels&&tables.objects,"four actual tables134");
    check(tables.effectsCount==0&&tables.vertexCount==2&&tables.pixelCount==2&&tables.objectCount==0,"actual binary counts134");
    std::array<BYTE,1964> zero={};check(!std::memcmp(RF455_GetSpecialShaderObject(0),zero.data(),zero.size()),"real zero-count object0 remains zero134");
    check(RF455_GetSpecialVertexShader(0)==tables.vertices[0].program&&RF455_GetSpecialPixelShader(0)==tables.pixels[0].program,"inclusive <= count getter134");
    check(!RF455_GetSpecialVertexShader(1)&&!RF455_GetSpecialPixelShader(1),"getter rejects index above published0 count134");
    std::array<std::vector<BYTE>,4> original;const char* expected[]={"vFraction.sho","vPlazma.sho","pFraction.sho","pPlazma.sho"};
    FILE* trace=std::fopen("special-shaders.jsonl","wb");check(trace!=nullptr,"trace134");
    for(unsigned i=0;i<4;++i){
        const auto& row=i<2?tables.vertices[i]:tables.pixels[i-2];check(!std::strcmp(row.name,expected[i])&&row.constants,"actual names/constant tables134");original[i]=bytecode134(row.program,i>=2);
        DWORD version=0;std::memcpy(&version,original[i].data(),4);check(version==(i<2?D3DVS_VERSION(2,0):D3DPS_VERSION(2,0)),"actual2.0 shader model134");
        char name[40];std::sprintf(name,"program-%u.bin",i);FILE* file=std::fopen(name,"wb");check(file!=nullptr,"bytecode dump134");std::fwrite(original[i].data(),1,original[i].size(),file);std::fclose(file);
        auto* constants=static_cast<ID3DXConstantTable*>(row.constants);D3DXCONSTANTTABLE_DESC table={};check(SUCCEEDED(constants->GetDesc(&table)),"actual reflection134");
        std::fprintf(trace,"{\"kind\":\"program\",\"id\":%u,\"name\":\"%s\",\"bytes\":%u,\"version\":%u,\"constants\":[",i,row.name,unsigned(original[i].size()),version);
        for(unsigned c=0;c<table.Constants;++c){D3DXCONSTANT_DESC desc={};UINT n=1;check(SUCCEEDED(constants->GetConstantDesc(constants->GetConstant(nullptr,c),&desc,&n))&&n==1,"constant reflection134");std::fprintf(trace,"%s{\"name\":\"%s\",\"register\":%u,\"count\":%u,\"set\":%u}",c?",":"",desc.Name,desc.RegisterIndex,desc.RegisterCount,unsigned(desc.RegisterSet));}
        std::fputs("]}\n",trace);
    }
    const unsigned before=GetDmallocSize();DWORD handlesBefore=0,handlesAfter=0;check(GetProcessHandleCount(GetCurrentProcess(),&handlesBefore)!=0,"handle count134");
    unsigned releases=0;
    for(unsigned iteration=0;iteration<3;++iteration){
        auto* retained=RF455_GetSpecialVertexShader(0);retained->AddRef();check(SUCCEEDED(D3D_R3InvalidateDevice()),"ordinary invalidate134");
        check(!tables.effects&&!tables.vertices&&!tables.pixels&&!tables.objects&&!tables.effectsCount&&!tables.vertexCount&&!tables.pixelCount&&!tables.objectCount,"ordinary invalidation clears all registry owners134");
        check(bytecode134(retained,false)==original[0],"external COM reference remains valid134");retained->Release();++releases;
        check(SUCCEEDED(D3D_R3RestoreDevice()),"ordinary restore134");check(tables.vertexCount==2&&tables.pixelCount==2&&tables.objectCount==0,"restore reads real binary list134");
        for(unsigned i=0;i<4;++i)check(bytecode134(i<2?tables.vertices[i].program:tables.pixels[i-2].program,i>=2)==original[i],"restored actual bytecode stable134");
        check(GetDmallocSize()==before,"same restored allocator ownership134");
    }
    check(GetProcessHandleCount(GetCurrentProcess(),&handlesAfter)!=0&&handlesBefore==handlesAfter,"no loader file handle leak134");std::fclose(trace);phase("reload-done134");
    //Two serialized objects exercise overlapping DWORD reads and the preserved
    //unpublished objectCount;never replace original client inputs.
    check(std::rename("System/shader/init.r3o","System/shader/init.original.r3o")==0,"save staged original134");
    FILE* input=std::fopen("System/shader/init.original.r3o","rb");check(input!=nullptr,"original binary134");std::vector<BYTE> bytes(1424);check(std::fread(bytes.data(),1,bytes.size(),input)==bytes.size(),"actual list bytes134");std::fclose(input);bytes.resize(bytes.size()-4);const DWORD objects=2;const auto* count=reinterpret_cast<const BYTE*>(&objects);bytes.insert(bytes.end(),count,count+4);
    auto add=[&](DWORD value){const auto* p=reinterpret_cast<const BYTE*>(&value);bytes.insert(bytes.end(),p,p+4);};add(0xabcd0001);add(0x43210001);add(1);for(unsigned i=0;i<196;++i)bytes.push_back(BYTE(i));add(0x12340000);add(0x56780000);add(0);
    FILE* fixture=std::fopen("System/shader/init.r3o","wb");check(fixture!=nullptr&&std::fwrite(bytes.data(),1,bytes.size(),fixture)==bytes.size(),"fixture binary134");std::fclose(fixture);
    check(RF455_LoadSpecialShaderBinary()==0,"real loader fixture134");const auto* obj=RF455_GetSpecialShaderObject(0);check(obj->vertex==1&&obj->pixel==1,"DWORD overlap retains two WORD program IDs134");for(unsigned i=0;i<196;++i)check(obj->parameters[i]==BYTE(i),"parameter bytes134");
    const auto* second=RF455_GetSpecialShaderObject(1);check(second->vertex==0&&second->pixel==0&&second->parameters[0]==0x78&&second->parameters[1]==0x56,"second overlapping read persists into parameter0 when count0");
    check(tables.objectCount==0&&RF455_GetSpecialVertexShader(0)==tables.vertices[1].program&&RF455_GetSpecialPixelShader(0)==tables.pixels[1].program,"unpublished count and double-indirection contract134");
    check(std::rename("System/shader/init.r3o","fixture.r3o")==0&&std::rename("System/shader/init.original.r3o","System/shader/init.r3o")==0,"restore staged pinned list134");check(RF455_LoadSpecialShaderBinary()==0,"reload pinned original134");
    g_MainApp.ReleaseR3D3D();check(!tables.objects&&!tables.vertices&&!tables.pixels,"actual final device teardown releases registry134");ReleaseR3Engine();
    FILE* output=std::fopen("result.json","wb");check(output!=nullptr,"result134");std::fprintf(output,"{\"status\":\"PASS\",\"actual_programs\":4,\"restore_cycles\":3,\"retained_COM_checks\":%u,\"overlap_objects\":2,\"overlap_parameter_bytes\":196,\"published_count_remains_zero\":true,\"memory_before\":%u,\"handles_before\":%u,\"handles_after\":%u,\"warnings\":%u,\"full_special_draw\":false}\n",releases,before,handlesBefore,handlesAfter,warnings);std::fclose(output);return 0;
}
int main(){try{return run134();}catch(const std::exception& error){std::fprintf(stderr,"special-shaders134:%s\n",error.what());return 1;}}
