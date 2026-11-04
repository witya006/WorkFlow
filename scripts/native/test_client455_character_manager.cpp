#include "client455_character_manager.h"
#include <cstdio>
#include <cstring>
#include <map>
#include <string>
#include <vector>
#include <float.h>

static unsigned checks,recordsTested,rawFiles,modelFiles,modelParts,physicalParts,texturePointers;
#define CM_CHECK(x) do{++checks;if(!(x)){std::fprintf(stderr,"character manager check%u line%d\n",checks,__LINE__);return 1;}}while(0)
template<class T>static T cmGet(const void* p,unsigned at){T v;std::memcpy(&v,static_cast<const unsigned char*>(p)+at,sizeof(v));return v;}
template<class T>static void cmPut(void* p,unsigned at,T v){std::memcpy(static_cast<unsigned char*>(p)+at,&v,sizeof(v));}
namespace {
struct Memory {
    RF455MeshMemoryOps real=RF455_CrtMeshMemoryOps();std::map<void*,std::size_t> live;unsigned calls=0,fail=0;bool bad=false;
    ~Memory(){for(const auto& p:live)real.release(real.context,p.first);}
    static void* __cdecl allocate(void* raw,std::size_t n){auto& m=*static_cast<Memory*>(raw);if(++m.calls==m.fail)return nullptr;void* p=m.real.allocate(m.real.context,n);if(p)m.live[p]=n;return p;}
    static void __cdecl release(void* raw,void* p){auto& m=*static_cast<Memory*>(raw);if(p && !m.live.erase(p)){m.bad=true;return;}m.real.release(m.real.context,p);}
    RF455MeshMemoryOps ops(){return {this,allocate,release};}
};
bool read(const std::string& path,std::vector<unsigned char>& b){FILE* f=std::fopen(path.c_str(),"rb");if(!f)return false;std::fseek(f,0,SEEK_END);const long n=std::ftell(f);if(n<0){std::fclose(f);return false;}std::fseek(f,0,SEEK_SET);b.resize(n);const bool ok=!n || std::fread(b.data(),1,n,f)==static_cast<std::size_t>(n);return !std::fclose(f) && ok;}
struct Reader {
    const std::vector<unsigned char>& b;std::size_t at=0;bool ok=true;
    unsigned number(unsigned n=4){if(n>b.size()-at){ok=false;return 0;}unsigned x=0;for(unsigned i=0;i<n;++i)x|=static_cast<unsigned>(b[at++])<<(8*i);return x;}
    std::string string(){const auto n=number(2);if(n>b.size()-at){ok=false;return {}; }std::string s(reinterpret_cast<const char*>(b.data()+at),n);at+=n;return s;}
};
int constructor(const char* file){
    std::vector<unsigned char> golden;CM_CHECK(read(file,golden) && golden.size()==1188);
    unsigned initial=0;CM_CHECK(!_controlfp_s(&initial,0,0));
    for(unsigned precision:{_PC_24,_PC_53,_PC_64})for(unsigned rounding:{_RC_NEAR,_RC_DOWN,_RC_UP,_RC_CHOP}){
        unsigned before=0,after=0;CM_CHECK(!_controlfp_s(&before,precision|rounding,_MCW_PC|_MCW_RC));RF455CharacterStorage record;std::memset(&record,0xa5,sizeof(record));
        RF455_ConstructCharacter(&record);CM_CHECK(!std::memcmp(&record,golden.data(),golden.size()));CM_CHECK(!_controlfp_s(&after,0,0) && before==after);++recordsTested;
    }
    unsigned ignored=0;CM_CHECK(!_controlfp_s(&ignored,initial,_MCW_PC|_MCW_RC));
    RF455CharacterManager manager,expected;std::memset(&manager,0xa5,sizeof(manager));expected=manager;
    expected.begin=expected.end=expected.capacity=nullptr;expected.nextId=0;std::memset(expected.cache,0,sizeof(expected.cache));RF455_ConstructCharacterManager(&manager);CM_CHECK(!std::memcmp(&manager,&expected,sizeof(manager)));return 0;
}
int managerChecks(){
    Memory memory;auto ops=memory.ops();RF455CharacterManager m;std::memset(&m,0xa5,sizeof(m));RF455_ConstructCharacterManager(&m);
    CM_CHECK(!RF455_FindCharacterName(&m,"missing") && !RF455_FindCharacterId(&m,1) && RF455_CharacterId(&m,"missing")==0);
    std::vector<RF455CharacterStorage*> records;unsigned capacity=0;
    for(unsigned i=0;i<50;++i){const auto name=i<3?"same":("Name"+std::to_string(i));auto* p=RF455_CreateCharacter(&m,name.c_str(),nullptr,&ops);CM_CHECK(p && cmGet<unsigned>(p,0)==i && cmGet<void*>(p,272)==nullptr);records.push_back(p);
        if(i==capacity){capacity=capacity+capacity/2;if(capacity<i+1)capacity=i+1;}CM_CHECK(static_cast<unsigned>(m.end-m.begin)==i+1 && static_cast<unsigned>(m.capacity-m.begin)==capacity && m.nextId==i+1);
    }
    CM_CHECK(RF455_FindCharacterName(&m,"same")==records[0] && RF455_CharacterId(&m,"same")==0 && !RF455_FindCharacterName(&m,"Same"));
    for(unsigned i=0;i<50;++i)CM_CHECK(RF455_FindCharacterId(&m,i)==records[i] && RF455_FindCharacterId(&m,i)==records[i]);
    auto* vector=m.begin;auto* endCapacity=m.capacity;const auto next=m.nextId;RF455CharacterStorage* cache[1000];std::memcpy(cache,m.cache,sizeof(cache));
    RF455_DeleteCharacterName(&m,"same",&ops);CM_CHECK(m.end-m.begin==47 && m.begin==vector && m.capacity==endCapacity && m.nextId==next && !std::memcmp(cache,m.cache,sizeof(cache)));
    for(unsigned i=0;i<47;++i)CM_CHECK(m.begin[i]==records[i+3]); // no stale cache dereference after deletion
    cmPut<unsigned>(m.begin[0],0,77);cmPut<unsigned>(m.begin[2],0,77);RF455_DeleteCharacterId(&m,77,&ops);CM_CHECK(m.end-m.begin==45 && m.begin[0]==records[4] && m.begin[1]==records[6]);
    RF455_ClearCharacters(&m,&ops);CM_CHECK(m.end==m.begin && m.capacity==endCapacity && m.nextId==next && !std::memcmp(cache,m.cache,sizeof(cache)) && memory.live.size()==1);
    RF455_DestroyCharacterManager(&m,&ops);CM_CHECK(!m.begin && !m.end && !m.capacity && m.nextId==next && !std::memcmp(cache,m.cache,sizeof(cache)) && m.opaque0==0xa5a5a5a5 && static_cast<unsigned char>(m.name[0])==0xa5 && memory.live.empty() && !memory.bad);
    // Explicit new constructor, rather than an invented automatic cache reset.
    RF455_ConstructCharacterManager(&m);const unsigned ids[]={1,256,65536,16777216};records.clear();
    for(unsigned id:ids){auto* p=static_cast<RF455CharacterStorage*>(Memory::allocate(&memory,1188));CM_CHECK(p);RF455_ConstructCharacter(p);CM_CHECK(RF455_AddCharacter(&m,p,&ops));cmPut(p,0,id);records.push_back(p);CM_CHECK(RF455_FindCharacterId(&m,id)==p);}
    CM_CHECK(m.cache[65]==records[3] && m.cache[86]==records[1] && m.cache[107]==records[2]);CM_CHECK(RF455_FindCharacterId(&m,1)==records[0] && m.cache[65]==records[0]);
    cmPut<unsigned>(records[0],0,2);CM_CHECK(!RF455_FindCharacterId(&m,1) && RF455_FindCharacterId(&m,2)==records[0]);
    m.nextId=0xffffffff;auto* a=RF455_CreateCharacter(&m,"wrap",records[0],&ops);auto* b=RF455_CreateCharacter(&m,"zero",nullptr,&ops);CM_CHECK(a && b && cmGet<unsigned>(a,0)==0xffffffff && cmGet<void*>(a,272)==records[0] && cmGet<unsigned>(b,0)==0 && m.nextId==1 && RF455_FindCharacterId(&m,0)==b);
    RF455_DestroyCharacterManager(&m,&ops);CM_CHECK(memory.live.empty() && !memory.bad);
    RF455_ConstructCharacterManager(&m);const auto calls=memory.calls;std::string longName(256,'a');CM_CHECK(!RF455_CreateCharacter(&m,"%s",nullptr,&ops) && !RF455_CreateCharacter(&m,longName.c_str(),nullptr,&ops) && !RF455_CreateCharacter(&m,nullptr,nullptr,&ops) && memory.calls==calls);
    memory.fail=memory.calls+1;CM_CHECK(!RF455_CreateCharacter(&m,"record-fail",nullptr,&ops) && !m.nextId && memory.live.empty());memory.fail=memory.calls+2;CM_CHECK(!RF455_CreateCharacter(&m,"vector-fail",nullptr,&ops) && m.nextId==1 && !m.begin && memory.live.empty());memory.fail=0;
    // Owned loaded record releases its cookie allocation; borrowed record does not.
    RF455MeshAccounting accounting={};auto* parent=RF455_CreateCharacter(&m,"owner",nullptr,&ops);auto* child=RF455_CreateCharacter(&m,"borrower",parent,&ops);CM_CHECK(parent && child);auto* array=RF455_AllocateMeshArray(2,&accounting,&ops);CM_CHECK(array);cmPut(parent,260,1u);cmPut(parent,532,2u);cmPut(parent,536,array);cmPut(child,532,2u);cmPut(child,536,array);
    RF455_DeleteCharacterName(&m,"borrower",&ops);CM_CHECK(memory.live.count(reinterpret_cast<unsigned char*>(array)-4)==1);RF455_DeleteCharacterId(&m,cmGet<unsigned>(parent,0),&ops);RF455_DestroyCharacterManager(&m,&ops);CM_CHECK(memory.live.empty() && !memory.bad);return 0;
}
int rawChecks(){
    Memory m;auto ops=m.ops();RF455CharacterRfsCache cache;auto* old=RF455_SetCharacterRfsCache(&cache);
    const char* names[]={"XMSH",".MSH","empty.msh",".\\pack\\same.MSH",".\\pack\\short.MSH",".\\pack\\zero.MSH"};
    const char* contents[]={"nodot","dot","","archive-first","loose-after-short",""};
    for(unsigned i=0;i<6;++i){RF455RawModelBuffer out={reinterpret_cast<void*>(0x1234),77};CM_CHECK(RF455_ReadMshFile(names[i],&ops,&out) && out.bytes && out.length==std::strlen(contents[i]) && !std::memcmp(out.bytes,contents[i],out.length));Memory::release(&m,out.bytes);++rawFiles;}
    for(const auto* name:{"","missing.msh","wrong.bin","bad.MSHx"}){RF455RawModelBuffer out={reinterpret_cast<void*>(0x1234),77};CM_CHECK(!RF455_ReadMshFile(name,&ops,&out) && out.bytes==reinterpret_cast<void*>(0x1234) && out.length==77);}
    RF455RawModelBuffer out={};m.fail=m.calls+1;CM_CHECK(!RF455_ReadMshFile("XMSH",&ops,&out) && !out.bytes && m.live.empty());m.fail=0;
    RF455_SetCharacterRfsCache(old);CM_CHECK(m.live.empty() && !m.bad);return 0;
}
struct Device {
    HMODULE matrix=nullptr,d3d=nullptr;HWND window=nullptr;IDirect3D9* api=nullptr;IDirect3DDevice9* device=nullptr;
    ~Device(){if(device)device->Release();if(api)api->Release();if(window)DestroyWindow(window);if(d3d)FreeLibrary(d3d);if(matrix)FreeLibrary(matrix);}
};
struct Environment {
    RF455TextureManager textures;RF455VertexBufferPool vertices;RF455IndexBufferPool indices;RF455MeshAccounting meshes={};RF455BufferAccounting buffers={};
    Environment(IDirect3DDevice9* d){RF455_ConstructTextureManager(&textures);RF455_ConstructVertexPool(&vertices);RF455_ConstructIndexPool(&indices);textures.device=vertices.device=indices.device=d;}
    ~Environment(){RF455_DestroyTextureManager(&textures);RF455_DestroyVertexPool(&vertices);RF455_DestroyIndexPool(&indices);}
};
int models(const char* workspace,const char* file,const RF455MeshMatrixOps& matrices,IDirect3DDevice9* device){
    std::vector<unsigned char> bytes;CM_CHECK(read(file,bytes));Reader g={bytes};CM_CHECK(g.number()==0x4742384d && g.number()==1 && g.number()==12);
    Environment env(device);Memory memory;auto ops=memory.ops();RF455ModelLoadContext ctx={ops,matrices,&env.textures,&env.vertices,&env.indices,&env.meshes,&env.buffers};RF455CharacterManager manager={};RF455_ConstructCharacterManager(&manager);
    for(unsigned sample=0;sample<12;++sample){const auto path=g.string();const auto externalCount=g.number();CM_CHECK(externalCount && externalCount<1000);auto* parent=RF455_CreateCharacter(&manager,"parent",nullptr,&ops);CM_CHECK(parent);
        auto* external=RF455_AllocateMeshArray(externalCount,&env.meshes,&ops);CM_CHECK(external);for(unsigned i=0;i<externalCount;++i){const auto name=g.string();CM_CHECK(name.size()<256);std::memcpy(external[i].bytes,name.c_str(),name.size()+1);}
        cmPut(parent,260,1u);cmPut(parent,532,externalCount);cmPut(parent,536,external);const auto count=g.number();for(unsigned i=0;i<count;++i){g.string();g.string();g.number();const auto n=g.number();for(unsigned j=0;j<n;++j)g.number();g.number();}
        const auto reference=std::string(workspace)+"/"+path;const auto filename=sample?reference:std::string(".\\pack\\model.MSH");auto* child=RF455_CreateCharacter(&manager,filename.c_str(),parent,&ops);CM_CHECK(child && filename.size()<256);std::strcpy(reinterpret_cast<char*>(child->prefix.bytes+276),".\\tex");
        RF455RawModelBuffer input={};CM_CHECK(RF455_ReadMshFile(filename.c_str(),&ops,&input));std::vector<unsigned char> original;CM_CHECK(read(reference,original) && original.size()==input.length && !std::memcmp(original.data(),input.bytes,input.length));++rawFiles;RF455ModelLoadStats stats={};CM_CHECK(RF455_LoadMesh08Model(input.bytes,input.length,&child->prefix,&ctx,&stats)==RF_MODEL_OK && stats.publishedMeshes==count);Memory::release(&memory,input.bytes);
        auto* meshes=cmGet<RF455MeshStorage*>(child,536);std::vector<RF455MeshStorage> expected(meshes,meshes+count);
        const unsigned ids[]={5111,5123,5127,5767,5771,5775},dest[]={5107,5115,5119,5791,5795,5799};std::map<IDirect3DTexture9*,ULONG> refs;
        for(unsigned i=0;i<count;++i){for(unsigned j=0;j<6;++j){auto* texture=RF455_GetTextureById(&env.textures,cmGet<unsigned>(meshes[i].bytes,ids[j]));cmPut(expected[i].bytes,dest[j],texture);if(texture){++texturePointers;if(!refs.count(texture)){const auto n=texture->AddRef();texture->Release();refs[texture]=n;}}}cmPut(expected[i].bytes,5283,cmGet<void*>(expected[i].bytes,5115));}
        RF455_RefreshModelTextures(&child->prefix,&env.textures);CM_CHECK(!std::memcmp(meshes,expected.data(),count*sizeof(*meshes)));
        for(const auto& item:refs){const auto n=item.first->AddRef();item.first->Release();CM_CHECK(n==item.second);}for(unsigned i=0;i<count;++i)if(device && cmGet<unsigned>(meshes[i].bytes,5090)){CM_CHECK(cmGet<unsigned>(meshes[i].bytes,4494)!=0xffffffff && cmGet<unsigned>(meshes[i].bytes,4502)!=0xffffffff);++physicalParts;}
        cmPut(child,260,1u);RF455_DeleteCharacterName(&manager,filename.c_str(),&ops);RF455_DeleteCharacterName(&manager,"parent",&ops);CM_CHECK(manager.end==manager.begin && memory.live.size()==1 && !memory.bad);modelParts+=count;++modelFiles;
    }
    RF455_DestroyCharacterManager(&manager,&ops);CM_CHECK(g.ok && g.at==bytes.size() && memory.live.empty() && !memory.bad && modelFiles==12 && modelParts==393 && (!device || (physicalParts==276 && texturePointers>0)));return 0;
}
int run(const char* workspace,const char* pair,const char* ctor,const char* dll,bool physical){
    CM_CHECK(constructor(ctor)==0 && managerChecks()==0 && rawChecks()==0);Device d;d.matrix=LoadLibraryA(dll);CM_CHECK(d.matrix);
    RF455MeshMatrixOps matrices={reinterpret_cast<decltype(matrices.inverse)>(GetProcAddress(d.matrix,"D3DXMatrixInverse")),reinterpret_cast<decltype(matrices.multiply)>(GetProcAddress(d.matrix,"D3DXMatrixMultiply"))};CM_CHECK(matrices.inverse && matrices.multiply);
    RF455CharacterTextureApi textures={reinterpret_cast<decltype(textures.memory2D)>(GetProcAddress(d.matrix,"D3DXCreateTextureFromFileInMemoryEx")),reinterpret_cast<decltype(textures.memoryCube)>(GetProcAddress(d.matrix,"D3DXCreateCubeTextureFromFileInMemoryEx")),reinterpret_cast<decltype(textures.file2D)>(GetProcAddress(d.matrix,"D3DXCreateTextureFromFileA"))};CM_CHECK(textures.memory2D && textures.memoryCube && textures.file2D);auto* previous=RF455_SetCharacterTextureApi(&textures);RF455CharacterRfsCache cache;auto* old=RF455_SetCharacterRfsCache(&cache);
    if(physical){char directory[MAX_PATH];CM_CHECK(GetSystemDirectoryA(directory,MAX_PATH));d.d3d=LoadLibraryA((std::string(directory)+"\\d3d9.dll").c_str());CM_CHECK(d.d3d);auto create=reinterpret_cast<IDirect3D9* (WINAPI*)(UINT)>(GetProcAddress(d.d3d,"Direct3DCreate9"));CM_CHECK(create);d.api=create(D3D_SDK_VERSION);CM_CHECK(d.api);d.window=CreateWindowExA(0,"STATIC","RF455 owned character manager",WS_OVERLAPPEDWINDOW,0,0,64,64,nullptr,nullptr,GetModuleHandleA(nullptr),nullptr);CM_CHECK(d.window);D3DPRESENT_PARAMETERS pp={};pp.BackBufferWidth=pp.BackBufferHeight=64;pp.BackBufferFormat=D3DFMT_X8R8G8B8;pp.SwapEffect=D3DSWAPEFFECT_DISCARD;pp.Windowed=TRUE;pp.hDeviceWindow=d.window;CM_CHECK(SUCCEEDED(d.api->CreateDevice(D3DADAPTER_DEFAULT,D3DDEVTYPE_HAL,d.window,D3DCREATE_SOFTWARE_VERTEXPROCESSING,&pp,&d.device)));}
    CM_CHECK(models(workspace,pair,matrices,d.device)==0);RF455_SetCharacterRfsCache(old);RF455_SetCharacterTextureApi(previous);if(physical){CM_CHECK(d.device->Release()==0);d.device=nullptr;CM_CHECK(d.api->Release()==0);d.api=nullptr;}return 0;
}
}
extern "C" int RF455_RunCharacterManagerChecks(const char* workspace,const char* pair,const char* ctor,const char* dll,const char* output,int physical){
    checks=recordsTested=rawFiles=modelFiles=modelParts=physicalParts=texturePointers=0;const int result=run(workspace,pair,ctor,dll,physical!=0);FILE* file=std::fopen(output,"wb");if(!file)return 1;
    std::fprintf(file,"{\"status\":\"%s\",\"checks\":%u,\"ctor_fp_modes\":%u,\"raw_files\":%u,\"model_files\":%u,\"model_parts\":%u,\"physical_parts\":%u,\"positive_texture_pointers\":%u}\n",result?"FAIL":"PASS",checks,recordsTested,rawFiles,modelFiles,modelParts,physicalParts,texturePointers);std::fclose(file);return result;
}
#ifndef RF455_CHARACTER_MANAGER_EMBEDDED
int main(int argc,char** argv){if(argc!=7 || (std::strcmp(argv[1],"--cpu") && std::strcmp(argv[1],"--gpu")))return 2;return RF455_RunCharacterManagerChecks(argv[2],argv[3],argv[4],argv[5],argv[6],!std::strcmp(argv[1],"--gpu"));}
#endif
