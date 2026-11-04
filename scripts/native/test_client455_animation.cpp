#include "client455_animation.h"
#include <cstdio>
#include <cstring>
#include <map>
#include <string>
#include <vector>

static unsigned checks,decodedFiles,decodedTracks,realMatches,modelParts,physicalParts,strandedBlocks;
#define AN_CHECK(x) do{++checks;if(!(x)){std::fprintf(stderr,"animation check%u line%d\n",checks,__LINE__);return 1;}}while(0)
template<class T>static T anGet(const void* p,unsigned at){T v;std::memcpy(&v,static_cast<const unsigned char*>(p)+at,sizeof(v));return v;}
template<class T>static void anPut(void* p,unsigned at,T v){std::memcpy(static_cast<unsigned char*>(p)+at,&v,sizeof(v));}
namespace {
struct Allocation {std::size_t requested;unsigned tag;};
struct Memory {
    RF455AnimationMemoryOps real=RF455_CrtAnimationMemoryOps();std::map<void*,Allocation> live;std::vector<unsigned> freed;unsigned calls=0,fail=0,padding=0,sizeCalls=0;bool bad=false;
    ~Memory(){for(const auto& p:live)real.memory.release(real.memory.context,p.first);}
    static void* __cdecl allocate(void* raw,std::size_t n){auto& m=*static_cast<Memory*>(raw);if(++m.calls==m.fail)return nullptr;void* p=m.real.memory.allocate(m.real.memory.context,n+m.padding);if(p){m.live[p]={n,0};std::memset(p,0xa5,n+m.padding);}return p;}
    static void __cdecl release(void* raw,void* p){auto& m=*static_cast<Memory*>(raw);const auto found=m.live.find(p);if(p && found==m.live.end()){m.bad=true;return;}m.freed.push_back(found==m.live.end()?0:found->second.tag);if(found!=m.live.end())m.live.erase(found);m.real.memory.release(m.real.memory.context,p);}
    static std::size_t __cdecl extent(void* raw,const void* p){auto& m=*static_cast<Memory*>(raw);++m.sizeCalls;if(!m.live.count(const_cast<void*>(p))){m.bad=true;return 0;}return m.real.extent(m.real.memory.context,p);}
    RF455AnimationMemoryOps ops(){return {{this,allocate,release},extent};}
    void* block(unsigned n,unsigned tag){auto* p=allocate(this,n);if(p)live[p].tag=tag;return p;}
};
struct Diagnostics {
    std::vector<std::string> text;std::vector<std::wstring> wide;
    static void __cdecl write(void* p,const char* s){static_cast<Diagnostics*>(p)->text.push_back(s);}
    static void __cdecl writeWide(void* p,const wchar_t* s){static_cast<Diagnostics*>(p)->wide.push_back(s);}
    RF455LegacyDiagnostics ops(){return {this,write,writeWide};}
};
bool read(const std::string& path,std::vector<unsigned char>& b){FILE* f=std::fopen(path.c_str(),"rb");if(!f)return false;std::fseek(f,0,SEEK_END);const long n=std::ftell(f);if(n<0){std::fclose(f);return false;}std::fseek(f,0,SEEK_SET);b.resize(n);const bool ok=!n || std::fread(b.data(),1,n,f)==static_cast<std::size_t>(n);return !std::fclose(f) && ok;}
struct Reader {
    const std::vector<unsigned char>& b;std::size_t at=0;bool ok=true;
    const unsigned char* take(std::size_t n){if(n>b.size()-at){ok=false;return nullptr;}auto* p=b.data()+at;at+=n;return p;}
    unsigned number(unsigned n=4){auto* p=take(n);unsigned x=0;if(p)for(unsigned i=0;i<n;++i)x|=static_cast<unsigned>(p[i])<<(8*i);return x;}
    std::string string(){const auto n=number(2);auto* p=take(n);return p?std::string(reinterpret_cast<const char*>(p),n):std::string();}
    std::vector<unsigned char> bytes(unsigned n){auto* p=take(n);return p?std::vector<unsigned char>(p,p+n):std::vector<unsigned char>();}
};
struct Track {unsigned offset,count[4],keyOffset[4];std::vector<unsigned char> header,keys[4];};
struct Sample {std::string path;unsigned length,count,maximum,consumed,pair;std::vector<Track> tracks;std::vector<unsigned char> raw;};
int goldens(const char* workspace,const char* path,std::vector<Sample>& samples){
    std::vector<unsigned char> data;AN_CHECK(read(path,data));Reader r={data};AN_CHECK(r.number()==0x35344e41 && r.number()==1 && r.number()==27);const unsigned stride[]={20,16,16,8};
    for(unsigned i=0;i<27;++i){Sample s;s.path=r.string();s.length=r.number();s.count=r.number();s.maximum=r.number();s.consumed=r.number();s.pair=r.number();AN_CHECK(s.count<=255 && read(std::string(workspace)+"/"+s.path,s.raw) && s.raw.size()==s.length);s.tracks.resize(s.count);
        for(auto& t:s.tracks){t.offset=r.number();t.header=r.bytes(140);for(unsigned k=0;k<4;++k){t.count[k]=r.number();t.keyOffset[k]=r.number();AN_CHECK(t.count[k]<=65535);t.keys[k]=r.bytes(stride[k]*t.count[k]);}}
        samples.push_back(std::move(s));
    }
    AN_CHECK(r.ok && r.at==data.size());return 0;
}
int codec(const std::vector<Sample>& samples){
    for(const auto& s:samples){std::vector<RF455AniTrackView> tracks(s.count);RF455AniView view={};std::size_t failed=0;AN_CHECK(RF455_DecodeAni(s.raw.data(),s.raw.size(),tracks.data(),tracks.size(),&view,&failed)==RF_ANIMATION_OK && view.trackCount==s.count && view.maxFrame==s.maximum && view.consumed==s.consumed);
        for(unsigned i=0;i<s.count;++i){const auto& t=s.tracks[i];AN_CHECK(tracks[i].header==s.raw.data()+t.offset && !std::memcmp(tracks[i].header,t.header.data(),140));for(unsigned k=0;k<4;++k)AN_CHECK(tracks[i].data.channel[k].count==t.count[k] && tracks[i].data.channel[k].keys==s.raw.data()+t.keyOffset[k] && (t.keys[k].empty() || !std::memcmp(tracks[i].data.channel[k].keys,t.keys[k].data(),t.keys[k].size())));++decodedTracks;}
        ++decodedFiles;
    }
    const auto& raw=samples[22].raw;SYSTEM_INFO info={};GetSystemInfo(&info);AN_CHECK(raw.size()<info.dwPageSize);auto* page=static_cast<unsigned char*>(VirtualAlloc(nullptr,2*info.dwPageSize,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE));AN_CHECK(page);DWORD old=0;AN_CHECK(VirtualProtect(page+info.dwPageSize,info.dwPageSize,PAGE_NOACCESS,&old));std::vector<RF455AniTrackView> tracks(255);
    for(std::size_t n=0;n<raw.size();++n){auto* start=page+info.dwPageSize-n;if(n)std::memcpy(start,raw.data(),n);RF455AniView v={71,72,73};AN_CHECK(RF455_DecodeAni(start,n,tracks.data(),tracks.size(),&v,nullptr)==RF_ANIMATION_FORMAT && v.trackCount==71 && v.maxFrame==72 && v.consumed==73);}
    AN_CHECK(VirtualFree(page,0,MEM_RELEASE));RF455AniView v={};AN_CHECK(RF455_DecodeAni(raw.data(),raw.size(),tracks.data(),2,&v,nullptr)==RF_ANIMATION_CAPACITY);return 0;
}
int recordLifetime(){
    RF455AnimationStorage record,expected;std::memset(&record,0xa5,284);expected=record;expected.bytes[4]=expected.bytes[5]=0;for(unsigned at:{0u,264u,268u,272u,276u,280u})anPut<unsigned>(expected.bytes,at,0);RF455_ConstructAnimation(&record);AN_CHECK(!std::memcmp(&record,&expected,284));
    Memory memory;auto ops=memory.ops().memory;anPut(record.bytes,268,memory.block(13,1));auto* cookie=static_cast<unsigned char*>(memory.block(4+2*32,2));anPut(cookie,0,2u);anPut(record.bytes,272,cookie+4);anPut(record.bytes,280,memory.block(5,3));anPut<unsigned>(record.bytes,0,1);record.bytes[4]=1;anPut<unsigned>(record.bytes,276,37);expected=record;for(unsigned at:{268u,272u,280u})anPut<void*>(expected.bytes,at,nullptr);
    RF455_DestroyAnimation(&record,&ops);AN_CHECK(!std::memcmp(&record,&expected,284) && memory.live.empty() && !memory.bad && memory.freed==std::vector<unsigned>({1,2,3}));RF455_DestroyAnimation(&record,&ops);AN_CHECK(memory.freed.size()==3);return 0;
}
RF455AnimationData expectedData(const Track& track,const unsigned char* raw){RF455AnimationData d={};for(unsigned i=0;i<4;++i)d.channel[i]={track.count[i],raw+track.keyOffset[i]};return d;}
int switches(const std::vector<Sample>& samples){
    Memory memory;auto ops=memory.ops().memory;RF455MeshAccounting account={};RF455CharacterStorage model;RF455_ConstructCharacter(&model);auto* meshes=RF455_AllocateMeshArray(3,&account,&ops);AN_CHECK(meshes);anPut<unsigned>(model.prefix.bytes,260,1);anPut<unsigned>(model.prefix.bytes,532,3);anPut(model.prefix.bytes,536,meshes);for(unsigned i=0;i<3;++i)std::strcpy(reinterpret_cast<char*>(meshes[i].bytes),i==1?"B":"A");
    int last=99;const auto& a=samples[22];AN_CHECK(RF455_AttachAnimation(a.raw.data(),a.raw.size(),&model.prefix,&ops,&last)==RF_ANIMATION_OK && last==1 && anGet<unsigned>(model.prefix.bytes,676)==40 && !anGet<void*>(meshes[2].bytes,5095));auto wanted=expectedData(a.tracks[0],a.raw.data());auto* current=anGet<RF455AnimationData*>(meshes[0].bytes,5095);AN_CHECK(current && !std::memcmp(current,&wanted,32));
    const auto& b=samples[23];AN_CHECK(RF455_AttachAnimation(b.raw.data(),b.raw.size(),&model.prefix,&ops,&last)==RF_ANIMATION_OK && last==0 && anGet<unsigned>(model.prefix.bytes,676)==40);auto previous=expectedData(b.tracks[0],b.raw.data());wanted=expectedData(b.tracks[1],b.raw.data());auto* backup=anGet<RF455AnimationData*>(meshes[0].bytes,5099);current=anGet<RF455AnimationData*>(meshes[0].bytes,5095);AN_CHECK(current && backup && !std::memcmp(current,&wanted,32) && !std::memcmp(backup,&previous,32));
    unsigned char header[140]={};std::strcpy(reinterpret_cast<char*>(header),"A");anPut<unsigned short>(header,102,999);RF455AniTrackView inactive={header,{}};int matched=-9;AN_CHECK(RF455_ApplyAniTrack(&inactive,&model.prefix,&ops,&matched)==RF_ANIMATION_OK && matched==0 && !meshes[0].bytes[5094] && !anGet<void*>(meshes[0].bytes,5095) && anGet<void*>(meshes[0].bytes,5099)==backup && !anGet<unsigned>(meshes[0].bytes,5103) && anGet<unsigned>(model.prefix.bytes,676)==40);
    anPut<unsigned short>(header,100,1);anPut<unsigned short>(header,102,20);inactive.data=wanted;AN_CHECK(RF455_ApplyAniTrack(&inactive,&model.prefix,&ops,&matched)==RF_ANIMATION_OK && anGet<void*>(meshes[0].bytes,5099)==backup);
    memory.fail=memory.calls+1;AN_CHECK(RF455_ApplyAniTrack(&inactive,&model.prefix,&ops,&matched)==RF_ANIMATION_MEMORY && !anGet<void*>(meshes[0].bytes,5099) && anGet<void*>(meshes[0].bytes,5095));memory.fail=memory.calls+2;AN_CHECK(RF455_ApplyAniTrack(&inactive,&model.prefix,&ops,&matched)==RF_ANIMATION_MEMORY && anGet<void*>(meshes[0].bytes,5099) && !anGet<void*>(meshes[0].bytes,5095));memory.fail=0;
    AN_CHECK(RF455_AttachAnimation(nullptr,0,&model.prefix,&ops,&last)==RF_ANIMATION_OK && last==0);RF455_ReleaseModelMeshArray(&model.prefix,&ops);AN_CHECK(memory.live.empty() && !memory.bad);return 0;
}
struct Environment {
    RF455TextureManager textures;RF455VertexBufferPool v64,v36;RF455IndexBufferPool indices;RF455MeshAccounting meshes={};RF455BufferAccounting buffers={};RF455LegacyScratch scratch;
    Environment(IDirect3DDevice9* device){RF455_ConstructTextureManager(&textures);RF455_ConstructVertexPool(&v64);RF455_ConstructVertexPool(&v36);RF455_ConstructIndexPool(&indices);textures.device=v64.device=v36.device=indices.device=device;}
    ~Environment(){RF455_DestroyTextureManager(&textures);RF455_DestroyIndexPool(&indices);RF455_DestroyVertexPool(&v36);RF455_DestroyVertexPool(&v64);}
    RF455CharacterLoadContext context(RF455AnimationMemoryOps memory,RF455MeshMatrixOps matrices,RF455LegacyDiagnostics diagnostic,unsigned* counter){return {{{memory.memory,matrices,&textures,&v64,&indices,&meshes,&buffers},&v36,4,&scratch,diagnostic},{memory,diagnostic,counter}};}
};
int fileCases(const char* workspace,const std::vector<Sample>& samples,RF455MeshMatrixOps matrices,Environment& env){
    Memory memory;memory.padding=16;Diagnostics diagnostic;auto op=memory.ops();auto log=diagnostic.ops();unsigned counter=0xfffffff0;auto context=env.context(op,matrices,log,&counter);RF455AnimationBuffer raw={};
    AN_CHECK(RF455_ReadAnimationFile(".\\pack\\packed.ani",&context.animation,&raw)==RF_ANIMATION_OK && raw.fromRfs && raw.accountedBytes==Memory::extent(&memory,raw.bytes) && raw.accountedBytes>=raw.length+16 && counter==static_cast<unsigned>(0xfffffff0+raw.accountedBytes));Memory::release(&memory,raw.bytes);
    const auto path=std::string(workspace)+"/"+samples[22].path;const auto before=counter;AN_CHECK(RF455_ReadAnimationFile(path.c_str(),&context.animation,&raw)==RF_ANIMATION_OK && !raw.fromRfs && raw.accountedBytes==samples[22].length && counter==before+samples[22].length);Memory::release(&memory,raw.bytes);
    const auto fallback=counter;AN_CHECK(RF455_ReadAnimationFile(".\\pack\\short.ani",&context.animation,&raw)==RF_ANIMATION_OK && !raw.fromRfs && counter==fallback+raw.length);Memory::release(&memory,raw.bytes);
    RF455ImportedResource imported={};AN_CHECK(RF455_ImportCharacterResource("XANI",1,&context.animation,&imported)==RF_ANIMATION_OK && imported.kind==RF_IMPORTED_ANI);RF455_ReleaseImportedResource(&imported,&op.memory);AN_CHECK(RF455_ImportCharacterResource("wrong.ext",0,&context.animation,&imported)==RF_ANIMATION_TYPE);
    RF455AnimationStorage record;RF455_ConstructAnimation(&record);std::strcpy(reinterpret_cast<char*>(record.bytes+5),"missing.ani");AN_CHECK(!RF455_LoadAnimation(&record,0,&context.animation) && record.bytes[4] && !anGet<unsigned>(record.bytes,0) && !anGet<void*>(record.bytes,268));const auto calls=memory.calls,messages=diagnostic.text.size();AN_CHECK(RF455_LoadAnimation(&record,1,&context.animation) && memory.calls==calls && diagnostic.text.size()==messages);
    RF455_ConstructAnimation(&record);std::strcpy(reinterpret_cast<char*>(record.bytes+5),"broken.ani");anPut<unsigned>(record.bytes,276,123);AN_CHECK(!RF455_LoadAnimation(&record,1,&context.animation) && record.bytes[4] && anGet<unsigned>(record.bytes,276)==123 && memory.live.empty());
    RF455_ConstructAnimation(&record);std::strcpy(reinterpret_cast<char*>(record.bytes+5),path.c_str());const auto failedBefore=counter;memory.fail=memory.calls+1;AN_CHECK(!RF455_LoadAnimation(&record,0,&context.animation) && counter==failedBefore+samples[22].length && diagnostic.text.back().find("ReadAnimationData( ")==0 && memory.live.empty());memory.fail=0;
    AN_CHECK(RF455_FindAnimationMax(&record,samples[22].raw.data(),samples[22].raw.size(),&log)==RF_ANIMATION_OK && anGet<unsigned>(record.bytes,276)==65535u);AN_CHECK(RF455_FindAnimationMax(&record,samples[22].raw.data(),4,&log)==RF_ANIMATION_FORMAT && anGet<unsigned>(record.bytes,276)==65535u);
    RF455LegacyModel empty={};AN_CHECK(RF455_ValidateLegacyModel(&empty,&log));
    AN_CHECK(!memory.bad && memory.live.empty());return 0;
}
struct State {const Track* track=nullptr;const unsigned char* raw=nullptr;};
int compareStates(RF455CharacterStorage& model,const Sample& sample,const unsigned char* raw,std::vector<State>& current,std::vector<State>& previous,unsigned& maximum){
    auto* meshes=anGet<RF455MeshStorage*>(model.prefix.bytes,536);const unsigned count=anGet<unsigned>(model.prefix.bytes,532);AN_CHECK(current.size()==count);
    for(const auto& track:sample.tracks){const char* name=reinterpret_cast<const char*>(track.header.data());unsigned index=0;while(index<count && std::strcmp(name,reinterpret_cast<char*>(meshes[index].bytes)))++index;if(index==count)continue;
        if(anGet<unsigned short>(track.header.data(),100)){if(current[index].track)previous[index]=current[index];current[index]={&track,raw};const auto frame=anGet<unsigned short>(track.header.data(),102);if(frame>maximum)maximum=frame;}
        else current[index]={};
    }
    for(unsigned i=0;i<count;++i){auto* b=meshes[i].bytes;AN_CHECK(b[5094]==(current[i].track?1:0));AN_CHECK(anGet<unsigned>(b,5103)==(current[i].track?static_cast<unsigned>(anGet<unsigned short>(current[i].track->header.data(),102)):0u));
        for(unsigned which=0;which<2;++which){const auto& state=which?previous[i]:current[i];auto* actual=anGet<RF455AnimationData*>(b,which?5099:5095);AN_CHECK(static_cast<bool>(actual)==static_cast<bool>(state.track));if(state.track){const auto expected=expectedData(*state.track,state.raw);AN_CHECK(!std::memcmp(actual,&expected,32));}}
    }
    AN_CHECK(anGet<unsigned>(model.prefix.bytes,676)==maximum && anGet<unsigned>(model.prefix.bytes,672)==160);return 0;
}
int realCases(const char* workspace,const std::vector<Sample>& samples,const char* pairsPath,RF455MeshMatrixOps matrices,Environment& env,bool physical){
    std::vector<unsigned char> bytes;AN_CHECK(read(pairsPath,bytes));Reader g={bytes};AN_CHECK(g.number()==0x4742384d && g.number()==1 && g.number()==12);std::vector<std::string> meshPaths;
    for(unsigned i=0;i<12;++i){meshPaths.push_back(g.string());const auto ext=g.number();for(unsigned j=0;j<ext;++j)g.string();const auto n=g.number();for(unsigned j=0;j<n;++j){g.string();g.string();g.number();const auto b=g.number();for(unsigned k=0;k<b;++k)g.number();g.number();}}AN_CHECK(g.ok && g.at==bytes.size());
    Memory memory;auto ops=memory.ops();Diagnostics diagnostic;auto log=diagnostic.ops();unsigned counter=0;auto context=env.context(ops,matrices,log,&counter);
    for(unsigned pair=1;pair<12;++pair){RF455CharacterStorage root,child;RF455_ConstructCharacter(&root);RF455_ConstructCharacter(&child);char relative[100];std::sprintf(relative,"/work/client-reference/character-legacy-runtime/real_%02u.bn",pair);const auto bone=std::string(workspace)+relative;std::strcpy(reinterpret_cast<char*>(root.prefix.bytes+4),bone.c_str());std::strcpy(reinterpret_cast<char*>(root.prefix.bytes+276),".\\tex");const auto mesh=std::string(workspace)+"/"+meshPaths[pair];std::strcpy(reinterpret_cast<char*>(child.prefix.bytes+4),mesh.c_str());std::strcpy(reinterpret_cast<char*>(child.prefix.bytes+276),".\\tex");anPut(child.prefix.bytes,272,&root.prefix);
        const auto before=memory.calls;AN_CHECK(!RF455_LoadCharacter(&child,1,&context) && !child.prefix.bytes[264] && memory.calls==before);
        RF455AnimationStorage records[2];std::vector<State> current,previous;unsigned maximum=0,pose=0;
        for(const auto& sample:samples)if(sample.pair==pair){AN_CHECK(pose<2);auto& animation=records[pose];RF455_ConstructAnimation(&animation);const auto file=std::string(workspace)+"/"+sample.path;std::strcpy(reinterpret_cast<char*>(animation.bytes+5),file.c_str());anPut<unsigned>(root.prefix.bytes,672,33);AN_CHECK(RF455_MatchAnimation(&animation,&root,&context) && anGet<unsigned>(root.prefix.bytes,260)==1 && root.prefix.bytes[264] && anGet<unsigned>(animation.bytes,0)==1 && animation.bytes[4] && anGet<unsigned>(animation.bytes,276)==sample.maximum);
            const unsigned count=anGet<unsigned>(root.prefix.bytes,532);if(!pose){current.resize(count);previous.resize(count);}const auto* data=anGet<const unsigned char*>(animation.bytes,268);AN_CHECK(compareStates(root,sample,data,current,previous,maximum)==0);const auto loadCalls=memory.calls;AN_CHECK(RF455_LoadAnimation(&animation,pose?0:1,&context.animation) && memory.calls==loadCalls);++realMatches;++pose;
        }
        AN_CHECK(pose==2 && RF455_LoadCharacter(&child,0,&context) && anGet<unsigned>(child.prefix.bytes,260)==1 && child.prefix.bytes[264]);const auto calls=memory.calls;AN_CHECK(RF455_LoadCharacter(&child,1,&context) && memory.calls==calls);
        for(auto* model:{&root,&child}){const auto count=anGet<unsigned>(model->prefix.bytes,532);auto* parts=anGet<RF455MeshStorage*>(model->prefix.bytes,536);modelParts+=count;for(unsigned i=0;i<count;++i)if(anGet<unsigned>(parts[i].bytes,5090)){if(physical){AN_CHECK(anGet<unsigned>(parts[i].bytes,4494)!=0xffffffff && anGet<unsigned>(parts[i].bytes,4502)!=0xffffffff);++physicalParts;}}}
        RF455_ReleaseModelMeshArray(&child.prefix,&ops.memory);RF455_ReleaseModelMeshArray(&root.prefix,&ops.memory);for(auto& record:records)RF455_DestroyAnimation(&record,&ops.memory);AN_CHECK(memory.live.empty() && !memory.bad);
    }
    return 0;
}
int dispatchEdges(RF455MeshMatrixOps matrices,Environment& env){
    Memory memory;auto ops=memory.ops();Diagnostics diagnostic;auto log=diagnostic.ops();unsigned counter=0;auto context=env.context(ops,matrices,log,&counter);RF455CharacterStorage parent,model;RF455_ConstructCharacter(&parent);RF455_ConstructCharacter(&model);anPut<unsigned>(parent.prefix.bytes,260,1);anPut(model.prefix.bytes,272,&parent.prefix);std::strcpy(reinterpret_cast<char*>(model.prefix.bytes+4),"missing.msh");AN_CHECK(!RF455_LoadCharacter(&model,0,&context) && !model.prefix.bytes[264] && !anGet<unsigned>(model.prefix.bytes,260));
    RF455_ConstructCharacter(&model);std::strcpy(reinterpret_cast<char*>(model.prefix.bytes+4),"missing.bn");AN_CHECK(!RF455_LoadCharacter(&model,1,&context) && model.prefix.bytes[264]);const auto calls=memory.calls;AN_CHECK(RF455_LoadCharacter(&model,0,&context) && memory.calls==calls && !anGet<unsigned>(model.prefix.bytes,260));
    RF455_ConstructCharacter(&model);std::strcpy(reinterpret_cast<char*>(model.prefix.bytes+4),"oversize.msh");AN_CHECK(!RF455_LoadCharacter(&model,0,&context) && model.prefix.bytes[264] && memory.live.empty());
    RF455_ConstructCharacter(&model);std::strcpy(reinterpret_cast<char*>(model.prefix.bytes+4),"oversize.msh");anPut(model.prefix.bytes,272,&parent.prefix);AN_CHECK(!RF455_LoadCharacter(&model,1,&context) && !model.prefix.bytes[264] && memory.live.size()==1);const auto stranded=*memory.live.begin();AN_CHECK(stranded.second.requested==2+693+88*21334);++strandedBlocks;Memory::release(&memory,stranded.first); // Harness cleanup AFTERobservingthe reference raw leak.
    RF455_ConstructCharacter(&model);std::strcpy(reinterpret_cast<char*>(model.prefix.bytes+4),"empty.bn");RF455AnimationStorage animation;RF455_ConstructAnimation(&animation);std::strcpy(reinterpret_cast<char*>(animation.bytes+5),"missing.ani");anPut<unsigned>(model.prefix.bytes,672,55);AN_CHECK(!RF455_MatchAnimation(&animation,&model,&context) && anGet<unsigned>(model.prefix.bytes,672)==55);AN_CHECK(RF455_MatchAnimation(&animation,&model,&context) && anGet<unsigned>(model.prefix.bytes,672)==160 && !anGet<unsigned>(animation.bytes,0) && !anGet<void*>(animation.bytes,268));RF455_ReleaseModelMeshArray(&model.prefix,&ops.memory);
    RF455_ConstructCharacter(&model);std::strcpy(reinterpret_cast<char*>(model.prefix.bytes+4),"XANI");AN_CHECK(!RF455_LoadCharacter(&model,0,&context) && model.prefix.bytes[264] && !anGet<unsigned>(model.prefix.bytes,260));RF455_ConstructAnimation(&animation);std::strcpy(reinterpret_cast<char*>(animation.bytes+5),"empty.bn");AN_CHECK(!RF455_LoadAnimation(&animation,0,&context.animation) && animation.bytes[4]);AN_CHECK(memory.live.empty() && !memory.bad);return 0;
}
struct Device {HMODULE matrix=nullptr,d3d=nullptr;HWND window=nullptr;IDirect3D9* api=nullptr;IDirect3DDevice9* device=nullptr;~Device(){if(device)device->Release();if(api)api->Release();if(window)DestroyWindow(window);if(d3d)FreeLibrary(d3d);if(matrix)FreeLibrary(matrix);}};
int run(const char* workspace,const char* golden,const char* pairs,const char* dll,bool physical){
    std::vector<Sample> samples;AN_CHECK(goldens(workspace,golden,samples)==0 && codec(samples)==0 && recordLifetime()==0 && switches(samples)==0);Device d;d.matrix=LoadLibraryA(dll);AN_CHECK(d.matrix);RF455MeshMatrixOps matrices={reinterpret_cast<decltype(matrices.inverse)>(GetProcAddress(d.matrix,"D3DXMatrixInverse")),reinterpret_cast<decltype(matrices.multiply)>(GetProcAddress(d.matrix,"D3DXMatrixMultiply"))};AN_CHECK(matrices.inverse && matrices.multiply);
    RF455CharacterTextureApi texture={reinterpret_cast<decltype(texture.memory2D)>(GetProcAddress(d.matrix,"D3DXCreateTextureFromFileInMemoryEx")),reinterpret_cast<decltype(texture.memoryCube)>(GetProcAddress(d.matrix,"D3DXCreateCubeTextureFromFileInMemoryEx")),reinterpret_cast<decltype(texture.file2D)>(GetProcAddress(d.matrix,"D3DXCreateTextureFromFileA"))};AN_CHECK(texture.memory2D && texture.memoryCube && texture.file2D);auto* oldApi=RF455_SetCharacterTextureApi(&texture);RF455CharacterRfsCache cache;auto* oldCache=RF455_SetCharacterRfsCache(&cache);
    if(physical){char system[MAX_PATH];AN_CHECK(GetSystemDirectoryA(system,MAX_PATH));d.d3d=LoadLibraryA((std::string(system)+"\\d3d9.dll").c_str());AN_CHECK(d.d3d);auto create=reinterpret_cast<IDirect3D9* (WINAPI*)(UINT)>(GetProcAddress(d.d3d,"Direct3DCreate9"));AN_CHECK(create);d.api=create(D3D_SDK_VERSION);AN_CHECK(d.api);d.window=CreateWindowExA(0,"STATIC","RF455 owned ANI dispatch",WS_OVERLAPPEDWINDOW,0,0,64,64,nullptr,nullptr,GetModuleHandleA(nullptr),nullptr);AN_CHECK(d.window);D3DPRESENT_PARAMETERS pp={};pp.BackBufferWidth=pp.BackBufferHeight=64;pp.BackBufferFormat=D3DFMT_X8R8G8B8;pp.SwapEffect=D3DSWAPEFFECT_DISCARD;pp.Windowed=TRUE;pp.hDeviceWindow=d.window;AN_CHECK(SUCCEEDED(d.api->CreateDevice(D3DADAPTER_DEFAULT,D3DDEVTYPE_HAL,d.window,D3DCREATE_SOFTWARE_VERTEXPROCESSING,&pp,&d.device)));}
    {Environment env(d.device);AN_CHECK(fileCases(workspace,samples,matrices,env)==0 && realCases(workspace,samples,pairs,matrices,env,physical)==0 && dispatchEdges(matrices,env)==0);}
    RF455_SetCharacterTextureApi(oldApi);RF455_SetCharacterRfsCache(oldCache);if(physical){AN_CHECK(d.device->Release()==0);d.device=nullptr;AN_CHECK(d.api->Release()==0);d.api=nullptr;}return 0;
}
}
extern "C" int RF455_RunAnimationChecks(const char* workspace,const char* golden,const char* pairs,const char* dll,const char* output,int physical){
    checks=decodedFiles=decodedTracks=realMatches=modelParts=physicalParts=strandedBlocks=0;const int result=run(workspace,golden,pairs,dll,physical!=0);FILE* f=std::fopen(output,"wb");if(!f)return 1;std::fprintf(f,"{\"status\":\"%s\",\"checks\":%u,\"ani_files\":%u,\"tracks\":%u,\"real_ani_matches\":%u,\"model_parts\":%u,\"physical_parts\":%u,\"stranded_raw_blocks_observed_and_harness_freed\":%u}\n",result?"FAIL":"PASS",checks,decodedFiles,decodedTracks,realMatches,modelParts,physicalParts,strandedBlocks);std::fclose(f);return result;
}
#ifndef RF455_ANIMATION_EMBEDDED
int main(int argc,char** argv){if(argc!=7 || (std::strcmp(argv[1],"--cpu") && std::strcmp(argv[1],"--gpu")))return 2;return RF455_RunAnimationChecks(argv[2],argv[3],argv[4],argv[5],argv[6],!std::strcmp(argv[1],"--gpu"));}
#endif
