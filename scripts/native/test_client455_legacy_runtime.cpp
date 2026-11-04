#include "client455_legacy_runtime.h"
#include "client455_character_manager.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <float.h>
#include <map>
#include <memory>
#include <string>
#include <vector>

static unsigned checks,loadedFiles,loadedParts,physicalParts,retainedParts,pairedFiles,pairedParts,pairedPhysicalParts;
#define LR_CHECK(x) do{++checks;if(!(x)){std::fprintf(stderr,"legacy runtime check%u line%d\n",checks,__LINE__);return 1;}}while(0)
template<class T>static T lrGet(const void* p,unsigned at){T v;std::memcpy(&v,static_cast<const unsigned char*>(p)+at,sizeof(v));return v;}
template<class T>static void lrPut(void* p,unsigned at,T v){std::memcpy(static_cast<unsigned char*>(p)+at,&v,sizeof(v));}
namespace {
struct Memory {
    RF455MeshMemoryOps real=RF455_CrtMeshMemoryOps();std::map<void*,std::size_t> live;unsigned calls=0,fail=0;bool bad=false;
    ~Memory(){for(const auto& p:live)real.release(real.context,p.first);}
    static void* __cdecl allocate(void* raw,std::size_t n){auto& m=*static_cast<Memory*>(raw);if(++m.calls==m.fail)return nullptr;void* p=m.real.allocate(m.real.context,n);if(p)m.live[p]=n;return p;}
    static void __cdecl release(void* raw,void* p){auto& m=*static_cast<Memory*>(raw);if(p && !m.live.erase(p)){m.bad=true;return;}m.real.release(m.real.context,p);}
    RF455MeshMemoryOps ops(){return {this,allocate,release};}
};
struct Diagnostics {
    std::vector<std::string> text;std::vector<std::wstring> wide;
    static void __cdecl write(void* raw,const char* s){static_cast<Diagnostics*>(raw)->text.push_back(s);}
    static void __cdecl writeWide(void* raw,const wchar_t* s){static_cast<Diagnostics*>(raw)->wide.push_back(s);}
    RF455LegacyDiagnostics ops(){return {this,write,writeWide};}
};
bool read(const std::string& path,std::vector<unsigned char>& b){FILE* f=std::fopen(path.c_str(),"rb");if(!f)return false;std::fseek(f,0,SEEK_END);const long n=std::ftell(f);if(n<0){std::fclose(f);return false;}std::fseek(f,0,SEEK_SET);b.resize(n);const bool ok=!n || std::fread(b.data(),1,n,f)==static_cast<std::size_t>(n);return !std::fclose(f) && ok;}
struct Reader {
    const std::vector<unsigned char>& b;std::size_t at=0;bool ok=true;
    const unsigned char* take(std::size_t n){if(n>b.size()-at){ok=false;return nullptr;}const auto* p=b.data()+at;at+=n;return p;}
    unsigned number(unsigned n=4){auto* p=take(n);unsigned x=0;if(p)for(unsigned i=0;i<n;++i)x|=static_cast<unsigned>(p[i])<<(8*i);return x;}
    std::string string(){const auto n=number(2);auto* p=take(n);return p?std::string(reinterpret_cast<const char*>(p),n):std::string();}
    std::vector<unsigned char> bytes(std::size_t n){auto* p=take(n);return p?std::vector<unsigned char>(p,p+n):std::vector<unsigned char>();}
};
struct Part {
    std::string name,parent;unsigned parentToken=0,missing=0,expandedCount=0,uniqueCount=0,firstInfluences=0;
    std::vector<unsigned> bones;std::vector<unsigned char> header,expanded,unique;std::vector<unsigned short> indices;
};
struct Sample {std::string path;unsigned mtg,lastCompact;std::vector<Part> parts;};
int goldens(const char* path,std::vector<Sample>& samples){
    std::vector<unsigned char> data;LR_CHECK(read(path,data));Reader r={data};LR_CHECK(r.number()==0x3534524c && r.number()==1 && r.number()==17);
    for(unsigned i=0;i<17;++i){Sample s;s.path=r.string();const auto count=r.number();s.mtg=r.number();s.lastCompact=r.number();LR_CHECK(count<1000);s.parts.resize(count);
        for(auto& p:s.parts){p.name=r.string();p.parent=r.string();p.parentToken=r.number();p.header=r.bytes(693);const auto n=r.number();p.missing=r.number();LR_CHECK(n<=50);for(unsigned j=0;j<n;++j)p.bones.push_back(r.number());p.expandedCount=r.number();p.uniqueCount=r.number();p.firstInfluences=r.number();LR_CHECK(p.expandedCount<=64000 && p.uniqueCount<=p.expandedCount);p.expanded=r.bytes(64u*p.expandedCount);p.unique=r.bytes(64u*p.uniqueCount);for(unsigned j=0;j<p.expandedCount;++j)p.indices.push_back(static_cast<unsigned short>(r.number(2)));}
        samples.push_back(std::move(s));
    }
    LR_CHECK(r.ok && r.at==data.size());return 0;
}
// Test-only byte capture uses the real source pool code;physical runs replace
// this device with an actual D3D9 HAL device and validate resource descriptors.
struct Capture;
struct Buffer {void** table;Capture* owner;std::vector<unsigned char> bytes;unsigned released=0;};
struct FakeDevice {void** table;Capture* owner;};
struct Capture {
    void* deviceTable[119]={};void* bufferTable[14]={};FakeDevice device={deviceTable,this};std::vector<std::unique_ptr<Buffer>> buffers;unsigned failCreate=0,failLock=0;
    Capture();IDirect3DDevice9* d3d(){return reinterpret_cast<IDirect3DDevice9*>(&device);}
};
ULONG WINAPI release(Buffer* b){++b->released;return 0;}
HRESULT WINAPI lock(Buffer* b,UINT at,UINT n,void** output,DWORD){if(b->owner->failLock || at>b->bytes.size() || n>b->bytes.size()-at)return E_FAIL;*output=b->bytes.data()+at;return S_OK;}
HRESULT WINAPI unlock(Buffer*){return S_OK;}
HRESULT create(FakeDevice* d,UINT n,void** output){if(d->owner->failCreate)return E_FAIL;std::unique_ptr<Buffer> b(new Buffer);b->table=d->owner->bufferTable;b->owner=d->owner;b->bytes.resize(n);*output=b.get();d->owner->buffers.push_back(std::move(b));return S_OK;}
HRESULT WINAPI vb(FakeDevice* d,UINT n,DWORD,DWORD,D3DPOOL,IDirect3DVertexBuffer9** output,HANDLE*){return create(d,n,reinterpret_cast<void**>(output));}
HRESULT WINAPI ib(FakeDevice* d,UINT n,DWORD,D3DFORMAT,D3DPOOL,IDirect3DIndexBuffer9** output,HANDLE*){return create(d,n,reinterpret_cast<void**>(output));}
Capture::Capture(){deviceTable[26]=reinterpret_cast<void*>(vb);deviceTable[27]=reinterpret_cast<void*>(ib);bufferTable[2]=reinterpret_cast<void*>(release);bufferTable[11]=reinterpret_cast<void*>(lock);bufferTable[12]=reinterpret_cast<void*>(unlock);}
struct Environment {
    RF455TextureManager textures;RF455VertexBufferPool v64,v36;RF455IndexBufferPool indices;RF455MeshAccounting mesh={};RF455BufferAccounting buffers={};RF455LegacyScratch scratch;
    Environment(IDirect3DDevice9* textureDevice,IDirect3DDevice9* poolDevice){RF455_ConstructTextureManager(&textures);RF455_ConstructVertexPool(&v64);RF455_ConstructVertexPool(&v36);RF455_ConstructIndexPool(&indices);textures.device=textureDevice;v64.device=v36.device=indices.device=poolDevice;}
    ~Environment(){RF455_DestroyTextureManager(&textures);RF455_DestroyIndexPool(&indices);RF455_DestroyVertexPool(&v36);RF455_DestroyVertexPool(&v64);}
    RF455LegacyLoadContext context(RF455MeshMemoryOps memory,RF455MeshMatrixOps matrices,RF455LegacyDiagnostics diagnostic,unsigned mode){return {{memory,matrices,&textures,&v64,&indices,&mesh,&buffers},&v36,mode,&scratch,diagnostic};}
};
int primitives(){
    Diagnostics diagnostic;auto ops=diagnostic.ops();unsigned initial=0;LR_CHECK(!_controlfp_s(&initial,0,0));
    for(unsigned pc:{_PC_24,_PC_53,_PC_64})for(unsigned rc:{_RC_NEAR,_RC_DOWN,_RC_UP,_RC_CHOP}){
        unsigned before=0,after=0;LR_CHECK(!_controlfp_s(&before,pc|rc,_MCW_PC|_MCW_RC));unsigned char source[28]={},target[64],expected[64];std::memset(target,0xa5,64);std::memcpy(expected,target,64);
        const unsigned bits[]={0x80000000,0x3f800001,0x7f800123,0x3f800000,0xff800123,0};for(unsigned i=0;i<3;++i){lrPut(source,4*i,bits[i]);lrPut(source,16+4*i,bits[i+3]);}
        const unsigned wanted[]={0x80000000,0x3f800001,0x7fc00123,0xbf800000,0x7fc00123,0x80000000};for(unsigned i=0;i<3;++i){lrPut(expected,4*i,wanted[i]);lrPut(expected,32+4*i,wanted[i+3]);}
        RF455_ConvertLegacyVertex64(target,source);LR_CHECK(!std::memcmp(target,expected,64));const unsigned uv[]={0x7f800123,0x3e800000};RF455_ConvertLegacyUv64(target,uv);LR_CHECK(lrGet<unsigned>(target,44)==0x7fc00123 && lrGet<unsigned>(target,48)==0x3f400000);
        unsigned char vertices[5*64],converted[5*36];for(unsigned i=0;i<5*64;i+=4)lrPut(vertices,i,0x7f800123u);RF455_ConvertLegacyVertices36(vertices,converted,5);
        for(unsigned i=0;i<5;++i)for(unsigned j=0;j<9;++j)LR_CHECK(lrGet<unsigned>(converted,36*i+4*j)==(j==3?0x7fc00123u:0x7f800123u));
        unsigned char physique[424]={};lrPut<unsigned>(physique,4,4);for(unsigned i=0;i<4;++i){std::sprintf(reinterpret_cast<char*>(physique+8+100*i),"bone%u",i);lrPut<unsigned>(physique,408+4*i,0x3e800000);}std::memset(target,0xa5,64);LR_CHECK(RF455_DecodeLegacyWeights(target,1,physique,1,&ops)==RF_LEGACY_RUNTIME_OK);
        for(unsigned i=0;i<3;++i)LR_CHECK(lrGet<unsigned>(target,12+4*i)==0x3e800000);for(unsigned i=0;i<4;++i)LR_CHECK(lrGet<unsigned short>(target,24+2*i)==i);
        LR_CHECK(!_controlfp_s(&after,0,0) && before==after);
    }
    unsigned ignored=0;LR_CHECK(!_controlfp_s(&ignored,initial,_MCW_PC|_MCW_RC));return 0;
}
int bindingEdges(){
    Diagnostics d;auto log=d.ops();RF455LegacyModel imported={};RF455LegacyPart part={};lrPut<unsigned short>(imported.bytes,2,1);lrPut(imported.bytes,4,&part);
    std::vector<RF455MeshStorage> parents(50);for(unsigned i=0;i<50;++i)std::sprintf(reinterpret_cast<char*>(parents[i].bytes),"bone%02u",i);
    for(unsigned count:{30u,31u,50u}){
        std::vector<unsigned char> raw(424*count,0);for(unsigned i=0;i<count;++i){lrPut<unsigned>(raw.data()+424*i,4,1);std::sprintf(reinterpret_cast<char*>(raw.data()+424*i+8),"bone%02u",i);}
        lrPut<unsigned short>(part.bytes,396,static_cast<unsigned short>(count));lrPut(part.bytes,704,raw.data());RF455MeshStorage mesh,expected;std::memset(mesh.bytes,0xa5,5803);std::strcpy(reinterpret_cast<char*>(mesh.bytes),"local");expected=mesh;lrPut(expected.bytes,522,count);
        for(unsigned i=0;i<count;++i)for(unsigned j=0;j<16;++j)lrPut<unsigned>(expected.bytes,646+64*i+4*j,j%5?0:0x3f800000);for(unsigned i=0;i<count;++i)lrPut(expected.bytes,526+4*i,parents.data()+i);
        RF455MeshBindingStats stats={};LR_CHECK(RF455_ResolveLegacyBones(parents.data(),50,&mesh,1,&imported,&log,&stats)==RF_LEGACY_RUNTIME_OK && stats.resolvedNames==count && !stats.missingNames && !std::memcmp(&mesh,&expected,5803));
        if(count>=31)LR_CHECK(lrGet<RF455MeshStorage*>(mesh.bytes,646)==parents.data()+30);
    }
    unsigned char raw[848]={};for(unsigned i=0;i<2;++i){lrPut<unsigned>(raw+424*i,4,1);std::strcpy(reinterpret_cast<char*>(raw+424*i+8),"absent");}lrPut<unsigned short>(part.bytes,396,2);lrPut(part.bytes,704,raw);RF455MeshStorage mesh={};std::strcpy(reinterpret_cast<char*>(mesh.bytes),"local");RF455MeshBindingStats stats={};
    LR_CHECK(RF455_ResolveLegacyBones(parents.data(),50,&mesh,1,&imported,&log,&stats)==RF_LEGACY_RUNTIME_OK && stats.missingNames==2 && stats.resolvedNames==0 && d.wide.size()==2 && d.wide[0]==L"Error: Can't Find Parent!!\n" && d.wide[1]==d.wide[0]);
    std::strcpy(reinterpret_cast<char*>(raw+8),"local");lrPut<unsigned short>(part.bytes,396,1);LR_CHECK(RF455_ResolveLegacyBones(parents.data(),50,&mesh,1,&imported,&log,&stats)==RF_LEGACY_RUNTIME_OK && lrGet<RF455MeshStorage*>(mesh.bytes,526)==&mesh);
    unsigned char vertices[64]={},physique[424]={};lrPut<unsigned>(physique,4,2);std::strcpy(reinterpret_cast<char*>(physique+8),"a");std::strcpy(reinterpret_cast<char*>(physique+108),"b");lrPut<unsigned>(physique,408,0x3fa00000);const auto before=d.text.size();LR_CHECK(RF455_DecodeLegacyWeights(vertices,1,physique,1,&log)==RF_LEGACY_RUNTIME_OK && d.text.size()==before+2 && d.text.back()=="Blend Weight Error: 1.250000");
    lrPut<unsigned>(physique,408,0x7f800123);const auto nanBefore=d.text.size();LR_CHECK(RF455_DecodeLegacyWeights(vertices,1,physique,1,&log)==RF_LEGACY_RUNTIME_OK && lrGet<unsigned>(vertices,12)==0x7fc00123 && d.text.size()==nanBefore);
    lrPut<unsigned>(physique,0,1);LR_CHECK(RF455_DecodeLegacyWeights(vertices,1,physique,1,&log)==RF_LEGACY_RUNTIME_PHYSIQUE);return 0;
}
int indexEdges(RF455MeshMatrixOps matrices){
    Capture capture;Environment env(nullptr,capture.d3d());Memory memory;auto ops=memory.ops();Diagnostics d;auto log=d.ops();auto context=env.context(ops,matrices,log,4);unsigned char raw[3*64]={};raw[64]=1;RF455MeshStorage mesh;RF455_ConstructMeshStorage(&mesh,&env.mesh);unsigned unique=99;
    capture.failCreate=1;LR_CHECK(RF455_IndexLegacyVertices(raw,3,&mesh,&context,&unique)==RF_LEGACY_RUNTIME_OK && unique==2 && lrGet<unsigned>(mesh.bytes,4494)==0xffffffff && lrGet<unsigned>(mesh.bytes,4502)==0xffffffff && d.text.size()==2);capture.failCreate=0;
    // Vertex Create succeeds but its Lock fails;IB muststill be attempted.
    capture.failLock=1;LR_CHECK(RF455_IndexLegacyVertices(raw,3,&mesh,&context,&unique)==RF_LEGACY_RUNTIME_OK && env.v64.buffers[0] && env.indices.buffers[0] && !env.v64.used[0] && !env.indices.used[0]);capture.failLock=0;
    LR_CHECK(RF455_IndexLegacyVertices(raw,3,&mesh,&context,&unique)==RF_LEGACY_RUNTIME_OK && unique==2 && env.scratch.indices[0]==0 && env.scratch.indices[1]==1 && env.scratch.indices[2]==0);
    const auto vo=lrGet<unsigned>(mesh.bytes,4494);LR_CHECK(env.scratch.rebasedIndices[1]==1+(vo%2300000)/64);
    context.rendererMode=2;memory.fail=memory.calls+1;LR_CHECK(RF455_IndexLegacyVertices(raw,3,&mesh,&context,&unique)==RF_LEGACY_RUNTIME_MEMORY && memory.live.empty());memory.fail=0;
    context.rendererMode=9;const auto bytesBefore=env.indices.used[0];LR_CHECK(RF455_IndexLegacyVertices(raw,3,&mesh,&context,&unique)==RF_LEGACY_RUNTIME_OK && env.indices.used[0]==bytesBefore+6 && env.scratch.rebasedIndices==env.scratch.indices);
    const auto messages=d.text.size();LR_CHECK(RF455_IndexLegacyVertices(nullptr,0,&mesh,&context,&unique)==RF_LEGACY_RUNTIME_OK && !unique && d.text.size()==messages);LR_CHECK(RF455_IndexLegacyVertices(raw,64001,&mesh,&context,&unique)==RF_LEGACY_RUNTIME_LIMIT);
    context.rendererMode=4;std::vector<unsigned char> maximum(64*64000,0);LR_CHECK(RF455_IndexLegacyVertices(maximum.data(),64000,&mesh,&context,&unique)==RF_LEGACY_RUNTIME_OK && unique==1 && env.scratch.indices.size()==64000);
    return 0;
}
int comparePart(const Part& p,RF455MeshStorage* mesh,RF455MeshStorage* all,unsigned mode,Environment& env,RF455MeshMatrixOps matrices,bool physical){
    auto* b=mesh->bytes;LR_CHECK(!std::strcmp(reinterpret_cast<char*>(b),p.name.c_str()) && !std::strcmp(reinterpret_cast<char*>(b+256),p.parent.c_str()));
    LR_CHECK(lrGet<RF455MeshStorage*>(b,518)==(p.parentToken?all+p.parentToken-1:nullptr) && b[512]==(p.parentToken?1:0) && lrGet<unsigned>(b,522)==p.bones.size());
    for(unsigned i=0;i<p.bones.size();++i)LR_CHECK(lrGet<RF455MeshStorage*>(b,526+4*i)==all+p.bones[i]-1);
    LR_CHECK(!std::memcmp(b+4574,p.header.data()+200,64) && !std::memcmp(b+4510,p.header.data()+200,64) && !std::memcmp(b+4766,p.header.data()+328,64));
    unsigned char inverse[64];float determinant=0;LR_CHECK(matrices.inverse(inverse,&determinant,p.header.data()+200) && !std::memcmp(b+4638,inverse,64));
    const auto flag=lrGet<unsigned>(b,5567);LR_CHECK(flag==(p.name.rfind("BONE ",0)==0?1u:0u));
    const bool retained=mode==2 && p.expandedCount && p.firstInfluences>2;LR_CHECK(lrGet<unsigned>(b,5090)==p.expandedCount && lrGet<unsigned>(b,5086)==(retained?p.expandedCount:p.uniqueCount));
    if(retained){auto* cpu=lrGet<void*>(b,4506);LR_CHECK(cpu && !std::memcmp(cpu,p.expanded.data(),p.expanded.size()) && lrGet<unsigned>(b,4494)==0xffffffff && lrGet<unsigned>(b,4502)==0xffffffff);++retainedParts;return 0;}
    LR_CHECK(!lrGet<void*>(b,4506));const auto vo=lrGet<unsigned>(b,4494),io=lrGet<unsigned>(b,4502);
    if(!p.expandedCount){LR_CHECK(vo==0xffffffff && io==0xffffffff);return 0;}
    LR_CHECK(vo!=0xffffffff && io!=0xffffffff);auto* vb=(mode==2?env.v36:env.v64).buffers[vo/2300000];auto* ib=env.indices.buffers[io/1000000];LR_CHECK(vb && ib);const unsigned base=(vo%2300000)/(mode==2?36:64);
    if(physical){D3DVERTEXBUFFER_DESC vd={};D3DINDEXBUFFER_DESC id={};LR_CHECK(SUCCEEDED(vb->GetDesc(&vd)) && SUCCEEDED(ib->GetDesc(&id)) && vd.Size==2300000 && vd.FVF==(mode==2?278u:282u) && id.Format==D3DFMT_INDEX16 && id.Size==1000000);++physicalParts;}
    else{auto* captured=reinterpret_cast<Buffer*>(vb);const auto* expected=p.unique.data();std::vector<unsigned char> narrow;
        if(mode==2){narrow.resize(36*p.uniqueCount);const unsigned from[]={0,4,8,12,32,36,40,44,48};for(unsigned n=0;n<p.uniqueCount;++n)for(unsigned i=0;i<9;++i)std::memcpy(narrow.data()+36*n+4*i,p.unique.data()+64*n+from[i],4);expected=narrow.data();}
        LR_CHECK(!std::memcmp(captured->bytes.data()+vo%2300000,expected,(mode==2?36:64)*p.uniqueCount));auto* index=reinterpret_cast<Buffer*>(ib);for(unsigned i=0;i<p.indices.size();++i)LR_CHECK(lrGet<unsigned short>(index->bytes.data(),io%1000000+2*i)==static_cast<unsigned short>(p.indices[i]+base));
    }
    return 0;
}
int modelCases(const char* workspace,const std::vector<Sample>& samples,RF455MeshMatrixOps matrices,Environment& env,bool physical){
    Memory memory;auto ops=memory.ops();Diagnostics diagnostic;auto log=diagnostic.ops();
    for(unsigned mode:{4u,2u})for(const auto& sample:samples){auto context=env.context(ops,matrices,log,mode);RF455LegacyModel* imported=nullptr;const auto path=std::string(workspace)+"/"+sample.path;const auto oldMessages=diagnostic.text.size();
        LR_CHECK(RF455_ImportLegacyFile(path.c_str(),&ops,&log,&imported)==RF_LEGACY_RUNTIME_OK && imported && diagnostic.text.size()==oldMessages+1 && diagnostic.text.back()=="ImportMeshorBoneData( "+path+" ) :NULL");
        RF455CharacterStorage record;RF455_ConstructCharacter(&record);LR_CHECK(path.size()<256);std::strcpy(reinterpret_cast<char*>(record.prefix.bytes+4),path.c_str());std::strcpy(reinterpret_cast<char*>(record.prefix.bytes+276),".\\tex");RF455LegacyLoadStats stats={};
        LR_CHECK(RF455_LoadLegacyModel(imported,nullptr,&record.prefix,&context,&stats)==RF_LEGACY_RUNTIME_OK && stats.publishedMeshes==sample.parts.size());auto* meshes=lrGet<RF455MeshStorage*>(record.prefix.bytes,536);LR_CHECK(meshes && lrGet<unsigned>(record.prefix.bytes,532)==sample.parts.size());
        unsigned retained=0,indexed=0,missing=0,resolved=0;for(unsigned n=0;n<sample.parts.size();++n){const auto& p=sample.parts[n];LR_CHECK(comparePart(p,meshes+n,meshes,mode,env,matrices,physical)==0);retained+=mode==2 && p.expandedCount && p.firstInfluences>2;indexed+=p.expandedCount && !(mode==2 && p.firstInfluences>2);missing+=p.missing;resolved+=static_cast<unsigned>(p.bones.size());
            unsigned char expected[64];std::memcpy(expected,p.header.data()+264,64);if(!sample.lastCompact && p.parentToken)matrices.multiply(expected,meshes[n].bytes+4574,meshes[p.parentToken-1].bytes+4638);LR_CHECK(!std::memcmp(meshes[n].bytes+4702,expected,64));++loadedParts;}
        LR_CHECK(stats.cpuRetainedMeshes==retained && stats.indexedMeshes==indexed && stats.bindings.missingNames==missing && stats.bindings.resolvedNames==resolved);
        lrPut<unsigned>(record.prefix.bytes,260,1);RF455_ReleaseModelMeshArray(&record.prefix,&ops);RF455_DeleteLegacyModel(imported,&ops);LR_CHECK(memory.live.empty() && !memory.bad);++loadedFiles;
    }
    return 0;
}
int pairedRoutes(const char* workspace,const char* golden,RF455MeshMatrixOps matrices,Environment& env,bool physical){
    std::vector<unsigned char> data;LR_CHECK(read(golden,data));Reader g={data};LR_CHECK(g.number()==0x4742384d && g.number()==1 && g.number()==12);Memory memory;auto ops=memory.ops();Diagnostics diagnostic;auto log=diagnostic.ops();auto context=env.context(ops,matrices,log,4);
    for(unsigned sample=0;sample<12;++sample){const auto path=g.string();const auto parentCount=g.number();std::vector<std::string> parentNames;for(unsigned i=0;i<parentCount;++i)parentNames.push_back(g.string());const auto count=g.number();std::vector<int> tokens(count);std::vector<std::vector<int>> bones(count);
        for(unsigned i=0;i<count;++i){g.string();g.string();tokens[i]=static_cast<int>(g.number());const auto n=g.number();for(unsigned j=0;j<n;++j)bones[i].push_back(static_cast<int>(g.number()));g.number();}
        char suffix[100];std::sprintf(suffix,"/work/client-reference/character-legacy-runtime/real_%02u.bn",sample);const auto filename=std::string(workspace)+suffix;RF455LegacyModel* imported=nullptr;LR_CHECK(RF455_ImportLegacyFile(filename.c_str(),&ops,&log,&imported)==RF_LEGACY_RUNTIME_OK);
        RF455CharacterStorage parent,child;RF455_ConstructCharacter(&parent);RF455_ConstructCharacter(&child);std::strcpy(reinterpret_cast<char*>(parent.prefix.bytes+4),filename.c_str());RF455LegacyLoadStats parentStats={};LR_CHECK(RF455_LoadLegacyModel(imported,nullptr,&parent.prefix,&context,&parentStats)==RF_LEGACY_RUNTIME_OK && parentStats.publishedMeshes==parentCount);RF455_DeleteLegacyModel(imported,&ops);lrPut<unsigned>(parent.prefix.bytes,260,1);auto* external=lrGet<RF455MeshStorage*>(parent.prefix.bytes,536);
        for(unsigned i=0;i<parentCount;++i)LR_CHECK(!std::strcmp(reinterpret_cast<char*>(external[i].bytes),parentNames[i].c_str()));
        lrPut(child.prefix.bytes,272,&parent.prefix);std::strcpy(reinterpret_cast<char*>(child.prefix.bytes+276),".\\tex");std::vector<unsigned char> raw;LR_CHECK(read(std::string(workspace)+"/"+path,raw));RF455ModelLoadStats stats={};LR_CHECK(RF455_LoadMesh08Model(raw.data(),raw.size(),&child.prefix,&context.base,&stats)==RF_MODEL_OK && stats.publishedMeshes==count);auto* meshes=lrGet<RF455MeshStorage*>(child.prefix.bytes,536);
        auto token=[&](int n)->RF455MeshStorage*{return n>0?external+n-1:n<0?meshes-n-1:nullptr;};for(unsigned i=0;i<count;++i){LR_CHECK(lrGet<RF455MeshStorage*>(meshes[i].bytes,518)==token(tokens[i]) && lrGet<unsigned>(meshes[i].bytes,522)==bones[i].size());for(unsigned j=0;j<bones[i].size();++j)LR_CHECK(lrGet<RF455MeshStorage*>(meshes[i].bytes,526+4*j)==token(bones[i][j]));if(lrGet<unsigned>(meshes[i].bytes,5090)){LR_CHECK(lrGet<unsigned>(meshes[i].bytes,4494)!=0xffffffff && lrGet<unsigned>(meshes[i].bytes,4502)!=0xffffffff);if(physical)++pairedPhysicalParts;}++pairedParts;}
        lrPut<unsigned>(child.prefix.bytes,260,1);RF455_ReleaseModelMeshArray(&child.prefix,&ops);RF455_ReleaseModelMeshArray(&parent.prefix,&ops);LR_CHECK(memory.live.empty() && !memory.bad);++pairedFiles;
    }
    LR_CHECK(g.ok && g.at==data.size() && pairedFiles==12 && pairedParts==393);return 0;
}
int failureCases(const char* workspace,RF455MeshMatrixOps matrices,Environment& env){
    Memory memory;auto ops=memory.ops();Diagnostics diagnostic;auto log=diagnostic.ops();RF455LegacyModel* imported=nullptr;
    LR_CHECK(RF455_ImportLegacyFile("missing.bin",&ops,&log,&imported)==RF_LEGACY_RUNTIME_IO && !imported && diagnostic.text.back().find("Mesh or Bone Not Found : FileName = missing.bin [")==0);
    LR_CHECK(RF455_ImportLegacyFile(".\\pack\\scene.any",&ops,&log,&imported)==RF_LEGACY_RUNTIME_OK);LR_CHECK(lrGet<unsigned short>(imported->bytes,2)==3);RF455_DeleteLegacyModel(imported,&ops);
    const auto path=std::string(workspace)+"/work/client-reference/character-legacy-runtime/scene_plain.msh";LR_CHECK(RF455_ImportLegacyFile(path.c_str(),&ops,&log,&imported)==RF_LEGACY_RUNTIME_OK);auto context=env.context(ops,matrices,log,2);
    RF455CharacterStorage model;RF455_ConstructCharacter(&model);std::strcpy(reinterpret_cast<char*>(model.prefix.bytes+4),path.c_str());RF455LegacyLoadStats stats={};memory.calls=0;LR_CHECK(RF455_LoadLegacyModel(imported,nullptr,&model.prefix,&context,&stats)==RF_LEGACY_RUNTIME_OK);const auto allocations=memory.calls;lrPut<unsigned>(model.prefix.bytes,260,1);RF455_ReleaseModelMeshArray(&model.prefix,&ops);const auto live=memory.live.size();
    for(unsigned fail=1;fail<=allocations;++fail){RF455_ConstructCharacter(&model);std::strcpy(reinterpret_cast<char*>(model.prefix.bytes+4),path.c_str());lrPut<unsigned>(model.prefix.bytes,536,0x12345678);stats.publishedMeshes=0x9876;memory.calls=0;memory.fail=fail;LR_CHECK(RF455_LoadLegacyModel(imported,nullptr,&model.prefix,&context,&stats)==RF_LEGACY_RUNTIME_MEMORY && lrGet<unsigned>(model.prefix.bytes,536)==0x12345678 && stats.publishedMeshes==0x9876 && memory.live.size()==live && !memory.bad);}
    memory.fail=0;RF455_DeleteLegacyModel(imported,&ops);LR_CHECK(memory.live.empty());
    LR_CHECK(RF455_ImportLegacyFile("broken.msh",&ops,&log,&imported)==RF_LEGACY_RUNTIME_OK);RF455_ConstructCharacter(&model);std::strcpy(reinterpret_cast<char*>(model.prefix.bytes+4),"broken.msh");LR_CHECK(RF455_LoadLegacyModel(imported,nullptr,&model.prefix,&context,&stats)==RF_LEGACY_RUNTIME_IO && !lrGet<void*>(model.prefix.bytes,536));RF455_DeleteLegacyModel(imported,&ops);LR_CHECK(memory.live.empty() && !memory.bad);
    return 0;
}
struct Device {
    HMODULE matrix=nullptr,d3d=nullptr;HWND window=nullptr;IDirect3D9* api=nullptr;IDirect3DDevice9* device=nullptr;
    ~Device(){if(device)device->Release();if(api)api->Release();if(window)DestroyWindow(window);if(d3d)FreeLibrary(d3d);if(matrix)FreeLibrary(matrix);}
};
int run(const char* workspace,const char* golden,const char* pairs,const char* dll,bool physical){
    LR_CHECK(primitives()==0 && bindingEdges()==0);std::vector<Sample> samples;LR_CHECK(goldens(golden,samples)==0);Device d;d.matrix=LoadLibraryA(dll);LR_CHECK(d.matrix);
    RF455MeshMatrixOps matrices={reinterpret_cast<decltype(matrices.inverse)>(GetProcAddress(d.matrix,"D3DXMatrixInverse")),reinterpret_cast<decltype(matrices.multiply)>(GetProcAddress(d.matrix,"D3DXMatrixMultiply"))};LR_CHECK(matrices.inverse && matrices.multiply);
    LR_CHECK(indexEdges(matrices)==0);RF455CharacterTextureApi texture={reinterpret_cast<decltype(texture.memory2D)>(GetProcAddress(d.matrix,"D3DXCreateTextureFromFileInMemoryEx")),reinterpret_cast<decltype(texture.memoryCube)>(GetProcAddress(d.matrix,"D3DXCreateCubeTextureFromFileInMemoryEx")),reinterpret_cast<decltype(texture.file2D)>(GetProcAddress(d.matrix,"D3DXCreateTextureFromFileA"))};LR_CHECK(texture.memory2D && texture.memoryCube && texture.file2D);auto* oldApi=RF455_SetCharacterTextureApi(&texture);RF455CharacterRfsCache cache;auto* oldCache=RF455_SetCharacterRfsCache(&cache);
    if(physical){char system[MAX_PATH];LR_CHECK(GetSystemDirectoryA(system,MAX_PATH));d.d3d=LoadLibraryA((std::string(system)+"\\d3d9.dll").c_str());LR_CHECK(d.d3d);auto create=reinterpret_cast<IDirect3D9* (WINAPI*)(UINT)>(GetProcAddress(d.d3d,"Direct3DCreate9"));LR_CHECK(create);d.api=create(D3D_SDK_VERSION);LR_CHECK(d.api);d.window=CreateWindowExA(0,"STATIC","RF455 owned legacy converter",WS_OVERLAPPEDWINDOW,0,0,64,64,nullptr,nullptr,GetModuleHandleA(nullptr),nullptr);LR_CHECK(d.window);D3DPRESENT_PARAMETERS pp={};pp.BackBufferWidth=pp.BackBufferHeight=64;pp.BackBufferFormat=D3DFMT_X8R8G8B8;pp.SwapEffect=D3DSWAPEFFECT_DISCARD;pp.Windowed=TRUE;pp.hDeviceWindow=d.window;LR_CHECK(SUCCEEDED(d.api->CreateDevice(D3DADAPTER_DEFAULT,D3DDEVTYPE_HAL,d.window,D3DCREATE_SOFTWARE_VERTEXPROCESSING,&pp,&d.device)));}
    Capture capture;
    {Environment env(d.device,physical?d.device:capture.d3d());LR_CHECK(modelCases(workspace,samples,matrices,env,physical)==0 && pairedRoutes(workspace,pairs,matrices,env,physical)==0 && failureCases(workspace,matrices,env)==0);}
    for(const auto& b:capture.buffers)LR_CHECK(b->released==1);RF455_SetCharacterTextureApi(oldApi);RF455_SetCharacterRfsCache(oldCache);
    if(physical){LR_CHECK(d.device->Release()==0);d.device=nullptr;LR_CHECK(d.api->Release()==0);d.api=nullptr;}return 0;
}
}
extern "C" int RF455_RunLegacyRuntimeChecks(const char* workspace,const char* golden,const char* pairs,const char* dll,const char* output,int physical){
    checks=loadedFiles=loadedParts=physicalParts=retainedParts=pairedFiles=pairedParts=pairedPhysicalParts=0;const int result=run(workspace,golden,pairs,dll,physical!=0);FILE* f=std::fopen(output,"wb");if(!f)return 1;std::fprintf(f,"{\"status\":\"%s\",\"checks\":%u,\"model_runs\":%u,\"model_parts\":%u,\"physical_indexed_parts\":%u,\"cpu_retained_parts\":%u,\"paired_files\":%u,\"paired_parts\":%u,\"paired_physical_parts\":%u}\n",result?"FAIL":"PASS",checks,loadedFiles,loadedParts,physicalParts,retainedParts,pairedFiles,pairedParts,pairedPhysicalParts);std::fclose(f);return result;
}
#ifndef RF455_LEGACY_RUNTIME_EMBEDDED
int main(int argc,char** argv){if(argc!=7 || (std::strcmp(argv[1],"--cpu") && std::strcmp(argv[1],"--gpu")))return 2;return RF455_RunLegacyRuntimeChecks(argv[2],argv[3],argv[4],argv[5],argv[6],!std::strcmp(argv[1],"--gpu"));}
#endif
