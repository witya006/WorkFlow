#include "client455_model_loader.h"
#include <cstdio>
#include <cstring>
#include <map>
#include <memory>
#include <string>
#include <vector>

static unsigned checks,lifetimeCases,loadedFiles,loadedParts,physicalParts,textureBindings;
#define MD_CHECK(x) do{++checks;if(!(x)){std::fprintf(stderr,"model check%u line%d\n",checks,__LINE__);return 1;}}while(0)
template<class T>static T mdGet(const void* data,unsigned at){T value;std::memcpy(&value,static_cast<const unsigned char*>(data)+at,sizeof(value));return value;}
template<class T>static void mdPut(void* data,unsigned at,T value){std::memcpy(static_cast<unsigned char*>(data)+at,&value,sizeof(value));}
namespace {
struct Record {std::size_t size;unsigned tag;};
struct Event {char kind;unsigned tag;};
struct Memory {
    RF455MeshMemoryOps real=RF455_CrtMeshMemoryOps();std::map<void*,Record> live;std::vector<Event> events;unsigned calls=0,failCall=0;bool bad=false;
    RF455KnownModelPrefix* observe=nullptr;RF455MeshStorage* expectedPublished=nullptr;
    ~Memory(){for(const auto& item:live)real.release(real.context,item.first);}
    static void* __cdecl allocate(void* raw,std::size_t size){auto& self=*static_cast<Memory*>(raw);if(++self.calls==self.failCall)return nullptr;void* pointer=self.real.allocate(self.real.context,size);if(pointer)self.live.insert({pointer,{size,0}});return pointer;}
    static void __cdecl release(void* raw,void* pointer){auto& self=*static_cast<Memory*>(raw);const auto found=self.live.find(pointer);if(pointer && found==self.live.end()){self.bad=true;return;}
        if(self.observe && mdGet<RF455MeshStorage*>(self.observe->bytes,536)!=self.expectedPublished)self.bad=true;
        self.events.push_back({'F',found==self.live.end()?0:found->second.tag});if(found!=self.live.end())self.live.erase(found);self.real.release(self.real.context,pointer);
    }
    RF455MeshMemoryOps ops(){return {this,allocate,release};}
    void* block(unsigned size,unsigned tag){void* p=allocate(this,size);if(p)live[p].tag=tag;return p;}
};
struct FakeCom {void** table;Memory* memory;unsigned tag,releases=0;};
ULONG WINAPI mdRelease(FakeCom* self){++self->releases;self->memory->events.push_back({'R',self->tag});return 0;}
int lifetime(){
    Memory memory;const auto ops=memory.ops();RF455MeshStorage mesh;std::memset(&mesh,0xa5,sizeof(mesh));void* table[]={nullptr,nullptr,reinterpret_cast<void*>(mdRelease)};FakeCom a={table,&memory,1},b={table,&memory,2};mdPut(mesh.bytes,4486,&a);mdPut(mesh.bytes,4490,&b);
    const unsigned heap[]={5095,5099,4506};std::vector<Event> expected={{'R',1},{'R',2}};
    for(unsigned i=0;i<3;++i){mdPut(mesh.bytes,heap[i],memory.block(32+i,10+i));expected.push_back({'F',10+i});}
    for(unsigned i=0;i<40;++i)mdPut(mesh.bytes,5595+4*i,memory.block(i+1,100+i));
    for(unsigned i=0;i<20;++i){expected.push_back({'F',100+i});expected.push_back({'F',120+i});}
    const unsigned strings[]={4,32,68,96,132};
    for(unsigned i=0;i<5;++i){const unsigned at=5163+strings[i];const bool heapString=i==1 || i==3 || i==4;mdPut<std::uint32_t>(mesh.bytes,at+20,heapString?16+i:15);mdPut<std::uint32_t>(mesh.bytes,at+16,3);if(heapString)mdPut(mesh.bytes,at,memory.block(32,200+i));}
    expected.push_back({'F',204});expected.push_back({'F',203});expected.push_back({'F',201});
    auto golden=mesh;for(auto at:heap)mdPut<void*>(golden.bytes,at,nullptr);std::memset(golden.bytes+5595,0,168);
    for(auto offset:strings){const unsigned at=5163+offset;mdPut<std::uint32_t>(golden.bytes,at+20,15);mdPut<std::uint32_t>(golden.bytes,at+16,0);golden.bytes[at]=0;}
    RF455_DestroyMeshStorage(&mesh,&ops);MD_CHECK(!std::memcmp(&mesh,&golden,sizeof(mesh)));MD_CHECK(memory.live.empty() && !memory.bad && memory.events.size()==expected.size());
    for(unsigned i=0;i<expected.size();++i)MD_CHECK(memory.events[i].kind==expected[i].kind && memory.events[i].tag==expected[i].tag);
    const auto events=memory.events.size();RF455_DestroyMeshStorage(&mesh,&ops);MD_CHECK(a.releases==2 && b.releases==2 && memory.events.size()==events+2 && !std::memcmp(&mesh,&golden,sizeof(mesh)));++lifetimeCases;
    for(unsigned flags=0;flags<8;++flags){Memory m;auto allocator=m.ops();RF455MeshAccounting accounting={};const unsigned count=(flags&2)?3:1;
        auto* array=(flags&2)?RF455_AllocateMeshArray(count,&accounting,&allocator):static_cast<RF455MeshStorage*>(m.block(5803,0));MD_CHECK(array);if(!(flags&2))RF455_ConstructMeshStorage(array,&accounting);
        FakeCom com[3]={{table,&m,0},{table,&m,1},{table,&m,2}};for(unsigned i=0;i<count;++i)mdPut(array[i].bytes,4486,&com[i]);
        auto* base=reinterpret_cast<unsigned char*>(array)-((flags&2)?4:0);if(flags&2)MD_CHECK(mdGet<unsigned>(base,0)==3);
        MD_CHECK(RF455_DeleteMeshStorage(array,flags,&allocator)==base);MD_CHECK(m.events.size()==count+((flags&1)?1:0));
        for(unsigned i=0;i<count;++i)MD_CHECK(m.events[i].kind=='R' && m.events[i].tag==count-i-1);
        if(!(flags&1))Memory::release(&m,base);MD_CHECK(m.live.empty() && !m.bad);++lifetimeCases;
    }
    {
        Memory m;auto allocator=m.ops();RF455MeshAccounting accounting={0xffffffff,0xfffffff0};auto* empty=RF455_AllocateMeshArray(0,&accounting,&allocator);MD_CHECK(empty && mdGet<unsigned>(reinterpret_cast<unsigned char*>(empty)-4,0)==0);MD_CHECK(accounting.constructed==0xffffffff && accounting.bytesConstructed==0xfffffff0);RF455_DeleteMeshStorage(empty,3,&allocator);MD_CHECK(m.live.empty());
        const auto calls=m.calls;MD_CHECK(!RF455_AllocateMeshArray(0xffffffff,&accounting,&allocator) && m.calls==calls);m.failCall=m.calls+1;MD_CHECK(!RF455_AllocateMeshArray(2,&accounting,&allocator) && m.live.empty());++lifetimeCases;
    }
    for(unsigned owns:{0u,1u}){
        Memory m;auto allocator=m.ops();RF455MeshAccounting accounting={};auto* array=RF455_AllocateMeshArray(3,&accounting,&allocator);RF455KnownModelPrefix model={};mdPut(model.bytes,260,owns);mdPut<unsigned>(model.bytes,532,12345);mdPut(model.bytes,536,array);
        RF455_ReleaseModelMeshArray(&model,&allocator);MD_CHECK(mdGet<unsigned>(model.bytes,532)==12345);MD_CHECK(mdGet<RF455MeshStorage*>(model.bytes,536)==(owns?nullptr:array));if(!owns)RF455_DeleteMeshStorage(array,3,&allocator);MD_CHECK(m.live.empty());++lifetimeCases;
    }
    return 0;
}
bool read(const std::string& path,std::vector<unsigned char>& bytes){FILE* file=std::fopen(path.c_str(),"rb");if(!file)return false;std::fseek(file,0,SEEK_END);const long size=std::ftell(file);if(size<0){std::fclose(file);return false;}std::fseek(file,0,SEEK_SET);bytes.resize(static_cast<std::size_t>(size));const bool ok=bytes.empty() || std::fread(bytes.data(),1,bytes.size(),file)==bytes.size();return !std::fclose(file) && ok;}
struct Reader {
    const std::vector<unsigned char>& bytes;std::size_t at=0;bool ok=true;
    unsigned number(unsigned size=4){if(size>bytes.size()-at){ok=false;return 0;}unsigned x=0;for(unsigned i=0;i<size;++i)x|=static_cast<unsigned>(bytes[at++])<<(8*i);return x;}
    std::string string(){const auto n=number(2);if(n>bytes.size()-at){ok=false;return {}; }std::string s(reinterpret_cast<const char*>(bytes.data()+at),n);at+=n;return s;}
};
struct Device {
    HMODULE matrix=nullptr,d3d=nullptr;HWND window=nullptr;IDirect3D9* api=nullptr;IDirect3DDevice9* device=nullptr;
    ~Device(){if(device)device->Release();if(api)api->Release();if(window)DestroyWindow(window);if(d3d)FreeLibrary(d3d);if(matrix)FreeLibrary(matrix);}
};
struct Environment {
    RF455TextureManager textures;RF455VertexBufferPool vertices;RF455IndexBufferPool indices;RF455MeshAccounting meshes={};RF455BufferAccounting buffers={};
    Environment(IDirect3DDevice9* device){RF455_ConstructTextureManager(&textures);RF455_ConstructVertexPool(&vertices);RF455_ConstructIndexPool(&indices);textures.device=vertices.device=indices.device=device;}
    ~Environment(){RF455_DestroyTextureManager(&textures);RF455_DestroyVertexPool(&vertices);RF455_DestroyIndexPool(&indices);}
};
std::vector<unsigned char> synthetic(){
    std::vector<unsigned char> bytes(8+2*(693+6),0);std::memcpy(bytes.data(),"MESH08",6);mdPut<unsigned short>(bytes.data(),6,2);
    for(unsigned n=0;n<2;++n){auto* header=bytes.data()+8+n*(693+6);std::strcpy(reinterpret_cast<char*>(header),n?"other":"Bip01 Ponytail L1");for(unsigned at:{200u,264u,328u})for(unsigned i=0;i<16;++i)mdPut<unsigned>(header,at+4*i,(i%5)?0:0x3f800000);}
    return bytes;
}
int errorAndReload(const RF455MeshMatrixOps& matrices){
    Environment env(nullptr);Memory memory;auto ops=memory.ops();RF455ModelLoadContext context={ops,matrices,&env.textures,&env.vertices,&env.indices,&env.meshes,&env.buffers};
    for(unsigned fail=1;fail<=3;++fail){auto input=synthetic();RF455KnownModelPrefix model={};mdPut<unsigned>(model.bytes,536,0x12345678);mdPut<unsigned>(model.bytes,532,91);RF455ModelLoadStats stats={71,{72,73}};memory.calls=0;memory.failCall=fail;
        MD_CHECK(RF455_LoadMesh08Model(input.data(),input.size(),&model,&context,&stats)==RF_MODEL_MEMORY);MD_CHECK(mdGet<unsigned>(model.bytes,536)==0x12345678 && mdGet<unsigned>(model.bytes,532)==91 && stats.publishedMeshes==71 && memory.live.empty());MD_CHECK(mdGet<unsigned>(model.bytes,796)==(fail>1?1u:0u));
    }
    memory.failCall=0;auto input=synthetic();RF455KnownModelPrefix model={};mdPut<unsigned>(model.bytes,260,1);RF455ModelLoadStats stats={};
    MD_CHECK(RF455_LoadMesh08Model(input.data(),input.size(),&model,&context,&stats)==RF_MODEL_OK && stats.publishedMeshes==2);auto* old=mdGet<RF455MeshStorage*>(model.bytes,536);MD_CHECK(old && mdGet<unsigned>(model.bytes,796)==1 && memory.live.size()==1);
    memory.observe=&model;memory.expectedPublished=old;MD_CHECK(RF455_LoadMesh08Model(input.data(),input.size(),&model,&context,&stats)==RF_MODEL_OK && !memory.bad);memory.observe=nullptr;auto* current=mdGet<RF455MeshStorage*>(model.bytes,536);MD_CHECK(current!=old && memory.live.size()==2);
    RF455_DeleteMeshStorage(old,3,&ops);RF455_ReleaseModelMeshArray(&model,&ops);MD_CHECK(memory.live.empty());
    auto bad=synthetic();bad.pop_back();MD_CHECK(RF455_LoadMesh08Model(bad.data(),bad.size(),&model,&context,&stats)==RF_MODEL_FORMAT && memory.live.empty());
    std::vector<unsigned char> empty={'M','E','S','H','0','8',0,0};MD_CHECK(RF455_LoadMesh08Model(empty.data(),empty.size(),&model,&context,&stats)==RF_MODEL_OK && stats.publishedMeshes==0 && mdGet<RF455MeshStorage*>(model.bytes,536));RF455_ReleaseModelMeshArray(&model,&ops);MD_CHECK(memory.live.empty());return 0;
}
// Real paired models and actual D3D9 entry follow below.
int realModels(const char* workspace,const char* golden,const RF455MeshMatrixOps& matrices,IDirect3DDevice9* device){
    std::vector<unsigned char> data;MD_CHECK(read(golden,data));Reader g={data};MD_CHECK(g.number()==0x4742384d && g.number()==1 && g.number()==12);
    Environment environment(device);Memory memory;auto allocator=memory.ops();RF455ModelLoadContext context={allocator,matrices,&environment.textures,&environment.vertices,&environment.indices,&environment.meshes,&environment.buffers};
    for(unsigned sample=0;sample<12;++sample){const auto path=g.string();const auto externalCount=g.number();MD_CHECK(externalCount>0 && externalCount<1000);
        auto* external=RF455_AllocateMeshArray(externalCount,&environment.meshes,&allocator);MD_CHECK(external);
        for(unsigned i=0;i<externalCount;++i){const auto name=g.string();MD_CHECK(name.size()<256);std::memcpy(external[i].bytes,name.c_str(),name.size()+1);}
        const auto count=g.number();std::vector<std::string> names(count),parentNames(count);std::vector<int> parentTokens(count);std::vector<std::vector<int>> bones(count);unsigned expectedMissing=0,expectedResolved=0;
        for(unsigned i=0;i<count;++i){names[i]=g.string();parentNames[i]=g.string();parentTokens[i]=static_cast<int>(g.number());const auto n=g.number();bones[i].resize(n);for(auto& token:bones[i])token=static_cast<int>(g.number());expectedMissing+=g.number();expectedResolved+=n;}
        RF455KnownModelPrefix parent={},model={};mdPut<unsigned>(parent.bytes,260,1);mdPut(parent.bytes,532,externalCount);mdPut(parent.bytes,536,external);mdPut<unsigned>(model.bytes,260,1);mdPut(model.bytes,272,&parent);std::strcpy(reinterpret_cast<char*>(model.bytes+276),".\\tex");
        std::vector<unsigned char> input;MD_CHECK(read(std::string(workspace)+"/"+path,input));std::vector<RF455Mesh08Part> records(count);RF455Mesh08View view={};MD_CHECK(RF455_DecodeMesh08(input.data(),input.size(),records.data(),records.size(),&view)==RF_MESH08_OK && view.meshCount==count);
        RF455ModelLoadStats stats={};MD_CHECK(RF455_LoadMesh08Model(input.data(),input.size(),&model,&context,&stats)==RF_MODEL_OK);
        auto* meshes=mdGet<RF455MeshStorage*>(model.bytes,536);MD_CHECK(meshes && stats.publishedMeshes==count && mdGet<unsigned>(model.bytes,532)==count && mdGet<unsigned>(reinterpret_cast<unsigned char*>(meshes)-4,0)==count);
        MD_CHECK(stats.bindings.missingNames==expectedMissing && stats.bindings.resolvedNames==expectedResolved && memory.live.size()==2 && !memory.bad);
        auto token=[&](int value)->RF455MeshStorage*{return value>0?external+value-1:value<0?meshes-value-1:nullptr;};
        for(unsigned i=0;i<count;++i){const auto* bytes=meshes[i].bytes;MD_CHECK(!std::strcmp(reinterpret_cast<const char*>(bytes),names[i].c_str()));MD_CHECK(!std::strcmp(reinterpret_cast<const char*>(bytes+256),parentNames[i].c_str()));
            MD_CHECK(mdGet<RF455MeshStorage*>(bytes,518)==token(parentTokens[i]) && bytes[512]==(parentTokens[i]?1:0));MD_CHECK(mdGet<unsigned>(bytes,5495)==(parentTokens[i]>0?1u:0u));MD_CHECK(mdGet<void*>(bytes,5455)==bytes+5163);
            MD_CHECK(mdGet<unsigned>(bytes,5086)==records[i].vertexCount && mdGet<unsigned>(bytes,5090)==records[i].indexCount && mdGet<unsigned>(bytes,522)==bones[i].size());
            for(unsigned j=0;j<bones[i].size();++j){MD_CHECK(mdGet<RF455MeshStorage*>(bytes,526+4*j)==token(bones[i][j]));for(unsigned m=0;m<16;++m)MD_CHECK(mdGet<unsigned>(bytes,646+64*j+4*m)==(m%5?0u:0x3f800000u));}
            const auto vo=mdGet<unsigned>(bytes,4494),io=mdGet<unsigned>(bytes,4502);
            if(device && records[i].indexCount){MD_CHECK(vo!=0xffffffff && io!=0xffffffff);++physicalParts;}else MD_CHECK(vo==0xffffffff && io==0xffffffff);
            const auto texture=mdGet<unsigned>(bytes,5111);if(texture){MD_CHECK(RF455_GetTextureById(&environment.textures,texture));++textureBindings;}
            ++loadedParts;
        }
        RF455_ReleaseModelMeshArray(&model,&allocator);RF455_ReleaseModelMeshArray(&parent,&allocator);MD_CHECK(memory.live.empty() && !memory.bad);++loadedFiles;
    }
    MD_CHECK(g.ok && g.at==data.size() && loadedFiles==12 && loadedParts==393);if(device)MD_CHECK(physicalParts==276 && textureBindings>0);return 0;
}
int run(const char* workspace,const char* golden,const char* dll,bool physical){
    MD_CHECK(lifetime()==0);Device device;device.matrix=LoadLibraryA(dll);MD_CHECK(device.matrix);
    RF455MeshMatrixOps matrices={reinterpret_cast<decltype(matrices.inverse)>(GetProcAddress(device.matrix,"D3DXMatrixInverse")),reinterpret_cast<decltype(matrices.multiply)>(GetProcAddress(device.matrix,"D3DXMatrixMultiply"))};MD_CHECK(matrices.inverse && matrices.multiply);
    RF455CharacterTextureApi textures={reinterpret_cast<decltype(textures.memory2D)>(GetProcAddress(device.matrix,"D3DXCreateTextureFromFileInMemoryEx")),reinterpret_cast<decltype(textures.memoryCube)>(GetProcAddress(device.matrix,"D3DXCreateCubeTextureFromFileInMemoryEx")),reinterpret_cast<decltype(textures.file2D)>(GetProcAddress(device.matrix,"D3DXCreateTextureFromFileA"))};MD_CHECK(textures.memory2D && textures.memoryCube && textures.file2D);
    const auto* previous=RF455_SetCharacterTextureApi(&textures);RF455CharacterRfsCache cache;auto* oldCache=RF455_SetCharacterRfsCache(&cache);
    MD_CHECK(errorAndReload(matrices)==0);
    if(physical){char directory[MAX_PATH];MD_CHECK(GetSystemDirectoryA(directory,MAX_PATH));device.d3d=LoadLibraryA((std::string(directory)+"\\d3d9.dll").c_str());MD_CHECK(device.d3d);
        auto create=reinterpret_cast<IDirect3D9* (WINAPI*)(UINT)>(GetProcAddress(device.d3d,"Direct3DCreate9"));MD_CHECK(create);device.api=create(D3D_SDK_VERSION);MD_CHECK(device.api);
        device.window=CreateWindowExA(0,"STATIC","RF455 owned model pipeline",WS_OVERLAPPEDWINDOW,0,0,64,64,nullptr,nullptr,GetModuleHandleA(nullptr),nullptr);MD_CHECK(device.window);
        D3DPRESENT_PARAMETERS pp={};pp.BackBufferWidth=pp.BackBufferHeight=64;pp.BackBufferFormat=D3DFMT_X8R8G8B8;pp.SwapEffect=D3DSWAPEFFECT_DISCARD;pp.Windowed=TRUE;pp.hDeviceWindow=device.window;
        MD_CHECK(SUCCEEDED(device.api->CreateDevice(D3DADAPTER_DEFAULT,D3DDEVTYPE_HAL,device.window,D3DCREATE_SOFTWARE_VERTEXPROCESSING,&pp,&device.device)));
    }
    MD_CHECK(realModels(workspace,golden,matrices,device.device)==0);if(physical){MD_CHECK(device.device->Release()==0);device.device=nullptr;MD_CHECK(device.api->Release()==0);device.api=nullptr;}
    RF455_SetCharacterTextureApi(previous);RF455_SetCharacterRfsCache(oldCache);return 0;
}
} // namespace
extern "C" int RF455_RunModelChecks(const char* workspace,const char* golden,const char* dll,const char* output,int physical){
    checks=lifetimeCases=loadedFiles=loadedParts=physicalParts=textureBindings=0;const int result=run(workspace,golden,dll,physical!=0);FILE* file=std::fopen(output,"wb");if(!file)return 1;
    std::fprintf(file,"{\"status\":\"%s\",\"checks\":%u,\"lifetime_cases\":%u,\"real_files\":%u,\"model_parts\":%u,\"physical_uploaded_parts\":%u,\"positive_texture_bindings\":%u}\n",result?"FAIL":"PASS",checks,lifetimeCases,loadedFiles,loadedParts,physicalParts,textureBindings);std::fclose(file);return result;
}
#ifndef RF455_MODELS_EMBEDDED
int main(int argc,char** argv){if(argc!=6 || (std::strcmp(argv[1],"--cpu") && std::strcmp(argv[1],"--gpu")))return 2;return RF455_RunModelChecks(argv[2],argv[3],argv[4],argv[5],!std::strcmp(argv[1],"--gpu"));}
#endif
