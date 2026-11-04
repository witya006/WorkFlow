#include "client455_mesh_runtime.h"
#include <windows.h>
#include <cstdio>
#include <cstring>
#include <cmath>
#include <string>
#include <vector>

static unsigned runtimeChecks,runtimeFiles,runtimeParts,materialCases,runtimeModes;
#define RT_CHECK(x) do{++runtimeChecks;if(!(x)){std::fprintf(stderr,"mesh runtime check%u line%d\n",runtimeChecks,__LINE__);return 1;}}while(0)
template<class T>static T rtRead(const void* bytes,unsigned at){T x;std::memcpy(&x,static_cast<const unsigned char*>(bytes)+at,sizeof(x));return x;}
template<class T>static void rtWrite(void* bytes,unsigned at,T x){std::memcpy(static_cast<unsigned char*>(bytes)+at,&x,sizeof(x));}
static unsigned short rtControl(){unsigned short x;__asm {fnstcw x}return x;}
static unsigned short rtStatus(){unsigned short x;__asm {fnstsw x}return x;}
static void rtSetControl(unsigned short x){__asm {fnclex}__asm {fldcw x}}
static bool rtFile(const std::string& name,std::vector<unsigned char>& bytes){
    FILE* f=std::fopen(name.c_str(),"rb");if(!f)return false;if(std::fseek(f,0,SEEK_END)){std::fclose(f);return false;}const long size=std::ftell(f);
    if(size<0 || std::fseek(f,0,SEEK_SET)){std::fclose(f);return false;}bytes.resize(static_cast<std::size_t>(size));const bool ok=bytes.empty() || std::fread(bytes.data(),1,bytes.size(),f)==bytes.size();return std::fclose(f)==0 && ok;
}
struct RTReader {
    const std::vector<unsigned char>& bytes;std::size_t at=0;bool ok=true;
    std::uint32_t number(unsigned size=4){if(size>bytes.size()-at){ok=false;return 0;}std::uint32_t x=0;for(unsigned n=0;n<size;++n)x|=static_cast<std::uint32_t>(bytes[at++])<<(8*n);return x;}
    std::string string(){const auto size=number(2);if(size>bytes.size()-at){ok=false;return {}; }const std::string x(reinterpret_cast<const char*>(bytes.data()+at),size);at+=size;return x;}
    bool copy(void* output,std::size_t size){if(size>bytes.size()-at){ok=false;return false;}std::memcpy(output,bytes.data()+at,size);at+=size;return true;}
};
static void rtIdentity(unsigned char* bytes){std::memset(bytes,0,64);for(unsigned n=0;n<4;++n)rtWrite<std::uint32_t>(bytes,20*n,0x3f800000);}
static std::vector<unsigned char> rtHeader(const char* name="ROOT"){
    std::vector<unsigned char> head(693,0);std::strcpy(reinterpret_cast<char*>(head.data()),name);std::strcpy(reinterpret_cast<char*>(head.data()+100),"PARENT");for(unsigned at:{200u,264u,328u})rtIdentity(head.data()+at);return head;
}
static int rtMatrixInvariants(const RF455MeshStorage& mesh){
    float source[16],inverse[16],bind[16],composite[16];std::memcpy(source,mesh.bytes+4574,64);std::memcpy(inverse,mesh.bytes+4638,64);std::memcpy(bind,mesh.bytes+4766,64);std::memcpy(composite,mesh.bytes+5022,64);
    for(unsigned r=0;r<4;++r)for(unsigned c=0;c<4;++c){double value=0;for(unsigned k=0;k<4;++k)value+=static_cast<double>(source[4*r+k])*inverse[4*k+c];RT_CHECK(std::fabs(value-(r==c?1.:0.))<0.001);}
    for(unsigned r=0;r<3;++r)for(unsigned c=0;c<4;++c){double value=0;for(unsigned k=0;k<4;++k)value+=static_cast<double>(bind[4*r+k])*composite[4*k+c];RT_CHECK(std::fabs(value-source[4*r+c])<0.001*(1.+std::fabs(source[4*r+c])));}
    RT_CHECK(rtRead<std::uint32_t>(mesh.bytes,5070)==0 && rtRead<std::uint32_t>(mesh.bytes,5074)==0 && rtRead<std::uint32_t>(mesh.bytes,5078)==0);return 0;
}
struct RTStep {char kind;const char* name;int result;const char* directory="";};
struct RTScript {std::vector<RTStep> steps;unsigned at=0,errors=0;};
static int rtStep(RTScript* script,char kind,const char* name,const char* directory){
    if(script->at>=script->steps.size()){++script->errors;return 0;}const auto& step=script->steps[script->at++];
    if(step.kind!=kind || std::strcmp(step.name,name) || (kind=='A' && std::strcmp(step.directory,directory))){++script->errors;return 0;}return step.result;
}
static std::int32_t __cdecl rtLookup(void* context,const char* name){return rtStep(static_cast<RTScript*>(context),'L',name,"");}
static int __cdecl rtLoad(void* context,const char* directory,const char* name){return rtStep(static_cast<RTScript*>(context),'A',name,directory);}
static int rtMaterial(const char* first,const char* second,const char* directory,RTScript script,const std::vector<int>& ids){
    auto head=rtHeader();std::strcpy(reinterpret_cast<char*>(head.data()+398),first);std::strcpy(reinterpret_cast<char*>(head.data()+498),second);auto expectedHead=head;
    RF455MeshStorage mesh;std::memset(&mesh,0xa5,sizeof(mesh));auto expected=mesh;
    const unsigned slots[]={5111,5767,5771,5775,5123};for(unsigned n=0;n<5;++n)rtWrite<std::int32_t>(expected.bytes,slots[n],ids[n]);rtWrite<std::uint32_t>(expected.bytes,518,0);rtWrite<std::uint32_t>(expected.bytes,5107,0);
    if(*first){auto* name=reinterpret_cast<char*>(expectedHead.data()+398);const auto* slash=std::strrchr(name,'\\');if(slash){const auto at=slash-name+1;for(std::size_t n=static_cast<std::size_t>(at);n<std::strlen(first);++n)if(name[n]>='A' && name[n]<='Z')name[n]=static_cast<char>(name[n]+('a'-'A'));}}
    RF455MeshMaterialOps ops={&script,rtLookup,rtLoad};RT_CHECK(RF455_LoadMesh08Materials(&mesh,head.data(),directory,"FALLBACK",&ops)==RF_MESH_RUNTIME_OK);
    RT_CHECK(script.at==script.steps.size() && !script.errors);RT_CHECK(!std::memcmp(&mesh,&expected,sizeof(mesh)));RT_CHECK(head==expectedHead);++materialCases;return 0;
}
static int rtMaterials(){
    const int untouched=static_cast<int>(0xa5a5a5a5u);
    RT_CHECK(!rtMaterial("","","OBJ",{{{'L',"",0}}},{0,untouched,untouched,untouched,0}));
    RT_CHECK(!rtMaterial("FOLDER\\Tex.DDS","a\\Second.DDS","OBJ",{{{'L',"tex_NOR.dds",0},{'L',"tex_SEQ.dds",3},{'L',"tex_REF.dds",0},{'L',"tex.dds",9},{'L',"Second.DDS",7}}},{9,0,3,0,7}));
    RT_CHECK(!rtMaterial("FOLDER\\Tex.DDS","","",{{{'L',"tex_NOR.dds",20},{'L',"tex_SEQ.dds",0},{'L',"tex_REF.dds",0},{'L',"tex.dds",0},{'A',"tex.dds",1,"FALLBACK"},{'L',"tex.dds",5},{'A',"tex_NOR.dds",0,"FALLBACK"},{'A',"tex_SEQ.dds",1,"FALLBACK"},{'L',"tex_SEQ.dds",6},{'A',"tex_REF.dds",0,"FALLBACK"},{'L',"",0}}},{5,20,6,0,0}));
    RT_CHECK(!rtMaterial("FOLDER\\T.DDS","Sec.DDS","OBJ",{{{'L',"t_NOR.dds",0},{'L',"t_SEQ.dds",0},{'L',"t_REF.dds",0},{'L',"t.dds",0},{'A',"t.dds",0,"OBJ"},{'A',"t_NOR.dds",1,"OBJ"},{'L',"t_NOR.dds",2},{'A',"t_SEQ.dds",0,"OBJ"},{'A',"t_REF.dds",0,"OBJ"},{'L',"Sec.DDS",0},{'A',"Sec.DDS",1,"OBJ"},{'L',"Sec.DDS",8}}},{0,2,0,0,8}));
    RT_CHECK(!rtMaterial("FOLDER\\T.TGA","","OBJ",{{{'L',"t.tga",0},{'L',"t.tga",0},{'L',"t.tga",0},{'L',"t.tga",0},{'A',"t.tga",0,"OBJ"},{'A',"t.tga",0,"OBJ"},{'A',"t.tga",0,"OBJ"},{'A',"t.tga",0,"OBJ"},{'L',"",0}}},{0,0,0,0,0}));
    RT_CHECK(!rtMaterial("","\\Case.DDS","",{{{'L',"\\Case.DDS",0},{'A',"\\Case.DDS",1,"FALLBACK"},{'L',"\\Case.DDS",11}}},{0,untouched,untouched,untouched,11}));
    RT_CHECK(!rtMaterial("\\T.DDS","dir\\","OBJ",{{{'L',"t_NOR.dds",2},{'L',"t_SEQ.dds",3},{'L',"t_REF.dds",4},{'L',"t.dds",1},{'L',"",0}}},{1,2,3,4,0}));
    RT_CHECK(!rtMaterial("\\","X.DDS","OBJ",{{{'L',"X.DDS",3}}},{0,untouched,untouched,untouched,3}));
    auto head=rtHeader();std::strcpy(reinterpret_cast<char*>(head.data()+398),"NO_SLASH.DDS");RF455MeshStorage mesh;std::memset(&mesh,0xa5,sizeof(mesh));const auto before=mesh;RTScript script;RF455MeshMaterialOps ops={&script,rtLookup,rtLoad};
    RT_CHECK(RF455_LoadMesh08Materials(&mesh,head.data(),"OBJ","FALLBACK",&ops)==RF_MESH_RUNTIME_PATH);RT_CHECK(!std::memcmp(&mesh,&before,sizeof(mesh)) && script.at==0);
    std::memset(head.data()+398,'x',100);RT_CHECK(RF455_LoadMesh08Materials(&mesh,head.data(),"OBJ","FALLBACK",&ops)==RF_MESH_RUNTIME_NAME);RT_CHECK(!std::memcmp(&mesh,&before,sizeof(mesh)));
    RT_CHECK(RF455_LoadMesh08Materials(&mesh,head.data(),"OBJ","FALLBACK",nullptr)==RF_MESH_RUNTIME_ARGUMENT);return 0;
}
static int runMeshRuntimeChecks(const char* goldenPath,const char* workspace,const char* dllPath,FILE* output){
    const unsigned short saved=rtControl();HMODULE module=LoadLibraryA(dllPath);RT_CHECK(module!=nullptr);
    RF455MeshMatrixOps ops={reinterpret_cast<decltype(ops.inverse)>(GetProcAddress(module,"D3DXMatrixInverse")),reinterpret_cast<decltype(ops.multiply)>(GetProcAddress(module,"D3DXMatrixMultiply"))};RT_CHECK(ops.inverse && ops.multiply);
    rtSetControl(0x027f);std::vector<unsigned char> golden;RT_CHECK(rtFile(goldenPath,golden));RTReader g={golden};RT_CHECK(g.number()==0x5248384d && g.number()==2);const unsigned files=g.number();RT_CHECK(files==12);
    RF455MeshStorage baseline;RT_CHECK(g.copy(&baseline,sizeof(baseline)));RF455MeshAccounting accounting={0xffffffffu,0xfffffffeu};RF455MeshStorage mesh;std::memset(&mesh,0xa5,sizeof(mesh));
    RF455_ConstructMeshStorage(&mesh,&accounting);RT_CHECK(!std::memcmp(&mesh,&baseline,sizeof(mesh)));RT_CHECK(accounting.constructed==0 && accounting.bytesConstructed==5801);
    for(unsigned f=0;f<files;++f){
        const auto path=g.string();const unsigned count=g.number();RT_CHECK(count>0 && count<1000);std::vector<unsigned char> data;RT_CHECK(rtFile(std::string(workspace)+"/"+path,data));
        std::vector<RF455Mesh08Part> parts(count);RF455Mesh08View view={};RT_CHECK(RF455_DecodeMesh08(data.data(),data.size(),parts.data(),count,&view)==RF_MESH08_OK && view.meshCount==count);
        std::uint32_t modelFlag=0;
        for(unsigned n=0;n<count;++n){
            const auto expectedFlag=g.number();RF455MeshStorage expected;RT_CHECK(g.copy(&expected,sizeof(expected)));RF455_ConstructMeshStorage(&mesh,&accounting);const auto control=rtControl();const auto top=rtStatus()&0x3800;
            RT_CHECK(RF455_ApplyMesh08Header(&mesh,&parts[n],&ops,&modelFlag)==RF_MESH_RUNTIME_OK);RT_CHECK(modelFlag==expectedFlag);RT_CHECK(rtControl()==control && (rtStatus()&0x3800)==top);
            auto normalized=mesh;rtWrite(expected.bytes,5455,mesh.bytes+5163);std::memset(normalized.bytes+4638,0,64);std::memset(normalized.bytes+5022,0,64);
            RT_CHECK(!std::memcmp(&normalized,&expected,sizeof(mesh)));RT_CHECK(!rtMatrixInvariants(mesh));++runtimeParts;
        }
        ++runtimeFiles;
    }
    RT_CHECK(g.ok && g.at==golden.size());
    auto head=rtHeader();RF455Mesh08Part part={};part.header=head.data();std::uint32_t flag=0;
    const std::uint32_t integers[]={0,1,16777217,0x7fffffffu,0x80000001u,0xffffffffu};
    const std::uint32_t floatBits[][4]={{0,0,0,0},{0x3f800000,0x3f800000,0x3f800000,0x3f800000},{0x4b800000,0x4b800000,0x4b800001,0x4b800000},{0x4f000000,0x4effffff,0x4f000000,0x4effffff},{0x4f000000,0x4f000000,0x4f000001,0x4f000000},{0x4f800000,0x4f7fffff,0x4f800000,0x4f7fffff}};
    const std::uint32_t specialFloat[]={0x80000000,1,0x7f800000,0x7fc12345,0x7fa12345,0xffa12345};
    for(unsigned precision:{0u,0x200u,0x300u})for(unsigned round=0;round<4;++round){
        const auto control=static_cast<unsigned short>(0x7f|precision|(round<<10));rtSetControl(control);
        for(unsigned i=0;i<6;++i){
            rtWrite(head.data(),598,integers[i]);for(unsigned k=0;k<6;++k)rtWrite(head.data(),602+4*k,specialFloat[k]);RF455_ConstructMeshStorage(&mesh,&accounting);
            RT_CHECK(RF455_ApplyMesh08Header(&mesh,&part,&ops,&flag)==RF_MESH_RUNTIME_OK);RT_CHECK(rtRead<std::uint32_t>(mesh.bytes,5339)==floatBits[i][round]);
            for(unsigned k=0;k<6;++k){const unsigned target=k<3?5459+4*k:5471+4*(k-3);const auto expected=specialFloat[k]|(k>=4?0x400000:0);RT_CHECK(rtRead<std::uint32_t>(mesh.bytes,target)==expected);}
            RT_CHECK(rtControl()==control && (rtStatus()&0x3800)==0);
        }
        ++runtimeModes;
    }
    rtSetControl(0x027f);head=rtHeader();part.header=head.data();
    for(unsigned i=0;i<3;++i){rtWrite<float>(head.data(),200+20*i,static_cast<float>(3+i));rtWrite<float>(head.data(),328+20*i,2.f);}rtWrite<float>(head.data(),248,7.f);rtWrite<float>(head.data(),252,11.f);rtWrite<float>(head.data(),256,13.f);
    RF455_ConstructMeshStorage(&mesh,&accounting);RT_CHECK(RF455_ApplyMesh08Header(&mesh,&part,&ops,&flag)==RF_MESH_RUNTIME_OK);
    // Independently call the actual export on a clean aligned scale matrix.
    // This provider uses reciprocal approximation: even inverse(I*2) differs
    // from ideal arithmetic. Pin that observed behavior, not a rounded ideal.
    alignas(16) float providerInput[16]={2,0,0,0,0,2,0,0,0,0,2,0,0,0,0,1},providerInverse[16];float providerDet=0;
    RT_CHECK(ops.inverse(providerInverse,&providerDet,providerInput)!=nullptr);
    for(unsigned n=0;n<3;++n)RT_CHECK(rtRead<std::uint32_t>(providerInverse,20*n)==0x3effffff);
    RT_CHECK(rtRead<std::uint32_t>(providerInverse,60)==0x3f7fffff);
    const std::uint32_t composed[16]={0x3fbfffff,0,0,0,0,0x3fffffff,0,0,0,0,0x401fffff,0,0,0,0,0x3f7fffff};
    RT_CHECK(!std::memcmp(mesh.bytes+5022,composed,64));RT_CHECK(!rtMatrixInvariants(mesh));
    const char* names[]={"Bip01 Spine1","Bip01 L Thigh","Bip01 R Thigh","Bip01 Ponytail L1","Bip01 Ponytail L11","Bip01 L skirt","Bip01 R skirt","Bip01 B skirt"};
    for(unsigned n=0;n<8;++n){head=rtHeader(names[n]);part.header=head.data();flag=0;RF455_ConstructMeshStorage(&mesh,&accounting);RT_CHECK(RF455_ApplyMesh08Header(&mesh,&part,&ops,&flag)==RF_MESH_RUNTIME_OK);RT_CHECK(rtRead<std::uint32_t>(mesh.bytes,5575)==(n<3?n+1:0));RT_CHECK(flag==(n>=3?1u:0u));}
    head=rtHeader("bip01 Spine1");part.header=head.data();RT_CHECK(RF455_ApplyMesh08Header(&mesh,&part,&ops,&flag)==RF_MESH_RUNTIME_OK && flag==1 && rtRead<std::uint32_t>(mesh.bytes,5571)==1);
    const auto before=mesh;std::memset(head.data(),'x',100);RT_CHECK(RF455_ApplyMesh08Header(&mesh,&part,&ops,&flag)==RF_MESH_RUNTIME_NAME);RT_CHECK(!std::memcmp(&mesh,&before,sizeof(mesh)));
    RT_CHECK(RF455_ApplyMesh08Header(&mesh,&part,nullptr,&flag)==RF_MESH_RUNTIME_ARGUMENT);
    head=rtHeader();part.header=head.data();std::memset(head.data()+328,0,64);RT_CHECK(RF455_ApplyMesh08Header(&mesh,&part,&ops,&flag)==RF_MESH_RUNTIME_MATRIX);
    head=rtHeader();part.header=head.data();std::memset(head.data()+200,0,64);RT_CHECK(RF455_ApplyMesh08Header(&mesh,&part,&ops,&flag)==RF_MESH_RUNTIME_MATRIX);
    RT_CHECK(!rtMaterials());RT_CHECK(FreeLibrary(module)!=FALSE);rtSetControl(saved);
    std::fprintf(output,"{\"checks\":%u,\"failures\":0,\"real_files\":%u,\"parts\":%u,\"material_cases\":%u,\"precision_rounding_modes\":%u,\"matrix_provider\":\"d3dx9_36.dll\",\"gpu_used\":false}\n",runtimeChecks,runtimeFiles,runtimeParts,materialCases,runtimeModes);return 0;
}
#ifndef RF455_MESH_RUNTIME_EMBEDDED
int main(int argc,char** argv){return argc==4?runMeshRuntimeChecks(argv[1],argv[2],argv[3],stdout):2;}
#endif
