#include "client455_secondary.h"
#include <cstdio>
#include <cstring>
#include <cmath>
#include <float.h>
#include <map>
#include <string>
#include <vector>

static unsigned checks,cases,humanModels,humanUpdates,clockCalls;
#define SE_CHECK(x) do{++checks;if(!(x)){std::fprintf(stderr,"secondary line%d check%u\n",__LINE__,checks);return 1;}}while(0)
template<class T>static T seGet(const void* p,unsigned at){T v;std::memcpy(&v,static_cast<const unsigned char*>(p)+at,sizeof(v));return v;}
template<class T>static void sePut(void* p,unsigned at,T v){std::memcpy(static_cast<unsigned char*>(p)+at,&v,sizeof(v));}
namespace {
void unit(void* p){float m[16]={};m[0]=m[5]=m[10]=m[15]=1;std::memcpy(p,m,64);}
struct Reader {std::vector<unsigned char> bytes;std::size_t at=0;bool good=true;
    bool open(const char* path){FILE* f=std::fopen(path,"rb");if(!f)return false;std::fseek(f,0,SEEK_END);const long n=std::ftell(f);std::rewind(f);if(n<0){std::fclose(f);return false;}bytes.resize(n);const bool ok=!n || std::fread(bytes.data(),1,n,f)==static_cast<std::size_t>(n);std::fclose(f);return ok;}
    void take(void* out,std::size_t n){if(n>bytes.size()-at){good=false;return;}std::memcpy(out,bytes.data()+at,n);at+=n;}
    unsigned number(unsigned n=4){unsigned v=0;for(unsigned i=0;i<n;++i){unsigned char c=0;take(&c,1);v|=static_cast<unsigned>(c)<<(8*i);}return v;}
    std::string text(){const unsigned n=number(2);std::string s(n,'\0');if(n)take(&s[0],n);return s;}
    float real(){float f=0;take(&f,4);return f;}
};
struct Memory {
    RF455AnimationMemoryOps real=RF455_CrtAnimationMemoryOps();std::map<void*,std::size_t> live;bool bad=false;
    ~Memory(){for(const auto& p:live)real.memory.release(nullptr,p.first);}
    static void* __cdecl allocate(void* c,std::size_t n){auto& m=*static_cast<Memory*>(c);auto* p=m.real.memory.allocate(nullptr,n);if(p)m.live[p]=n;return p;}
    static void __cdecl release(void* c,void* p){auto& m=*static_cast<Memory*>(c);if(p && !m.live.erase(p)){m.bad=true;return;}m.real.memory.release(nullptr,p);}
    static std::size_t __cdecl extent(void* c,const void* p){auto& m=*static_cast<Memory*>(c);if(!m.live.count(const_cast<void*>(p))){m.bad=true;return 0;}return m.real.extent(nullptr,p);}
    RF455AnimationMemoryOps ops(){return {{this,allocate,release},extent};}
};
struct Scene {
    RF455TextureManager textures;RF455VertexBufferPool v64,v36;RF455IndexBufferPool indices;RF455MeshAccounting mesh={};RF455BufferAccounting buffers={};RF455LegacyScratch scratch;
    Scene(){RF455_ConstructTextureManager(&textures);RF455_ConstructVertexPool(&v64);RF455_ConstructVertexPool(&v36);RF455_ConstructIndexPool(&indices);}
    ~Scene(){RF455_DestroyTextureManager(&textures);RF455_DestroyIndexPool(&indices);RF455_DestroyVertexPool(&v36);RF455_DestroyVertexPool(&v64);}
    static void __cdecl diagnostic(void*,const char*){}static void __cdecl wide(void*,const wchar_t*){}
    RF455CharacterLoadContext context(RF455AnimationMemoryOps memory,RF455MeshMatrixOps math,unsigned* bytes){RF455LegacyDiagnostics log={nullptr,diagnostic,wide};return {{{memory.memory,math,&textures,&v64,&indices,&mesh,&buffers},&v36,4,&scratch,log},{memory,log,bytes}};}
};
RF455SecondaryMath actual;unsigned now;struct Angle {char kind;float value;};std::vector<Angle> angles;
unsigned __stdcall tick(){++clockCalls;return now;}
void __cdecl modernSine(float* output,const float* input){*output=static_cast<float>(std::sin(static_cast<double>(*input)));}
void* __stdcall x(void* output,float angle){angles.push_back({'X',angle});return actual.rotationX(output,angle);}
void* __stdcall y(void* output,float angle){angles.push_back({'Y',angle});return actual.rotationY(output,angle);}
void* __stdcall z(void* output,float angle){angles.push_back({'Z',angle});return actual.rotationZ(output,angle);}
void* __stdcall axis(void* output,const void* raw,float angle){const auto* a=static_cast<const float*>(raw);if(a[0]!=0 || std::fabs(a[1])!=.2f || a[2]!=-1)return nullptr;angles.push_back({'A',angle});return actual.quaternionAxis(output,raw,angle);}
void initialize(RF455CharacterStorage& model,RF455MeshStorage& mesh,RF455MeshStorage& parent,bool tilt){
    RF455_ConstructCharacter(&model);RF455MeshAccounting account={};RF455_ConstructMeshStorage(&mesh,&account);RF455_ConstructMeshStorage(&parent,&account);auto* b=reinterpret_cast<unsigned char*>(&model);for(unsigned at=800;at<=1120;at+=64)unit(b+at);if(tilt)for(unsigned at:{864u,928u}){float rotation[16]={};rotation[1]=-1;rotation[4]=1;rotation[10]=rotation[15]=1;std::memcpy(b+at,rotation,64);}
    for(auto* m:{&mesh,&parent})for(unsigned at:{4574u,4638u,4702u,4766u,4830u,4894u,4958u,5022u})unit(m->bytes+at);for(unsigned i=0;i<3;++i){sePut<float>(mesh.bytes,4878+4*i,static_cast<float>(i+1));sePut<float>(parent.bytes,4878+4*i,static_cast<float>(i+7));}sePut(mesh.bytes,518,&parent);
}
bool equal(const void* actualBytes,const void* expected,std::size_t length){if(!std::memcmp(actualBytes,expected,length))return true;for(std::size_t at=0;at<length;at+=4)if(std::memcmp(static_cast<const unsigned char*>(actualBytes)+at,static_cast<const unsigned char*>(expected)+at,4)){std::fprintf(stderr,"scalar offset%u actual%08x expected%08x\n",static_cast<unsigned>(at),seGet<unsigned>(actualBytes,static_cast<unsigned>(at)),seGet<unsigned>(expected,static_cast<unsigned>(at)));break;}return false;}
int scalars(Reader& golden,RF455SecondaryMath math){
    const unsigned count=golden.number();SE_CHECK(count==36);
    for(unsigned i=0;i<count;++i){const auto name=golden.text();now=golden.number();const bool tilt=golden.number()!=0;RF455SecondaryState state,expected;RF455SecondaryGlobals globals,expectedGlobals;golden.take(&state,sizeof(state));golden.take(&globals,sizeof(globals));golden.take(&expected,sizeof(expected));golden.take(&expectedGlobals,sizeof(expectedGlobals));const unsigned n=golden.number();std::vector<Angle> expectedAngles(n);for(auto& a:expectedAngles){a.kind=static_cast<char>(golden.number(1));a.value=golden.real();}
        RF455CharacterStorage model;RF455MeshStorage mesh,parent;initialize(model,mesh,parent,tilt);std::strcpy(reinterpret_cast<char*>(mesh.bytes),name.c_str());sePut(&model,1184,&state);RF455SecondaryContext context={math,&globals};angles.clear();const unsigned before=clockCalls;
        SE_CHECK(RF455_ApplySecondaryMotion(&model,&mesh,&context)==RF_POSE_OK && clockCalls==before+1);if(!equal(&state,&expected,84) || !equal(&globals,&expectedGlobals,28))std::fprintf(stderr,"case%u %s tick%u\n",i,name.c_str(),now);SE_CHECK(equal(&state,&expected,84) && equal(&globals,&expectedGlobals,28));SE_CHECK(angles.size()==expectedAngles.size());for(unsigned j=0;j<n;++j)SE_CHECK(angles[j].kind==expectedAngles[j].kind && !std::memcmp(&angles[j].value,&expectedAngles[j].value,4));
        for(unsigned k=0;k<16;++k)SE_CHECK(std::isfinite(seGet<float>(mesh.bytes,4830+4*k)));if(name=="Bip01 Ponytail L1")SE_CHECK(seGet<float>(mesh.bytes,4878)==1 && seGet<float>(mesh.bytes,4882)==2 && seGet<float>(mesh.bytes,4886)==3);SE_CHECK(seGet<void*>(&model,1184)==&state);++cases;
    }
    RF455CharacterStorage model;RF455MeshStorage mesh,parent;initialize(model,mesh,parent,false);const auto before=clockCalls;SE_CHECK(RF455_ApplySecondaryMotion(&model,&mesh,nullptr)==RF_POSE_OK && clockCalls==before);RF455SecondaryState state={};sePut(&model,1184,&state);SE_CHECK(RF455_ApplySecondaryMotion(&model,&mesh,nullptr)==RF_POSE_SECONDARY && clockCalls==before);return 0;
}
int __cdecl rejectOwner(void*,const RF455AnimationData*,RF455PoseSpan*){return 0;}
int human(Reader& golden,const char* workspace,RF455SecondaryMath math){
    const unsigned count=golden.number();SE_CHECK(count==2);Scene scene;
    for(unsigned i=0;i<count;++i){const auto name=std::string(workspace)+"/"+golden.text();Memory memory;auto ops=memory.ops();unsigned imported=0;auto load=scene.context(ops,math.pose.matrix,&imported);RF455CharacterStorage model;RF455_ConstructCharacter(&model);std::strcpy(reinterpret_cast<char*>(model.prefix.bytes+4),name.c_str());std::strcpy(reinterpret_cast<char*>(model.prefix.bytes+276),".\\tex");SE_CHECK(RF455_LoadCharacter(&model,0,&load));const unsigned parts=seGet<unsigned>(&model,532);auto* meshes=seGet<RF455MeshStorage*>(&model,536);unsigned effects=0;for(unsigned n=0;n<parts;++n)if(seGet<unsigned>(meshes[n].bytes,5571))++effects;SE_CHECK(effects>0 && seGet<unsigned>(&model,796));
        RF455SecondaryState state={};for(unsigned k=0;k<5;++k){state.direction[k]=1;state.maximum[k]=1;}RF455SecondaryGlobals globals={};RF455SecondaryContext secondary={math,&globals};RF455PoseScratch scratch={};RF455PoseContext context={&load,math.pose,&scratch,150,nullptr,rejectOwner,&secondary};
        for(unsigned frame=0;frame<3;++frame){now=100+11*frame;angles.clear();const auto calls=clockCalls;sePut(&model,1184,&state);SE_CHECK(RF455_UpdateCharacterPose(&model,&context)==RF_POSE_OK && !seGet<void*>(&model,1184) && clockCalls==calls+effects && state.lastTick==now);for(unsigned n=0;n<parts;++n)for(unsigned k=0;k<16;++k)SE_CHECK(std::isfinite(seGet<float>(meshes[n].bytes,4830+4*k)));++humanUpdates;}
        RF455_ReleaseModelMeshArray(&model.prefix,&ops.memory);SE_CHECK(memory.live.empty() && !memory.bad);++humanModels;
    }
    SE_CHECK(golden.good && golden.at==golden.bytes.size());return 0;
}
int run(const char* workspace,const char* goldenPath,const char* dll){
    auto module=LoadLibraryA(dll);SE_CHECK(module);actual.pose.matrix={reinterpret_cast<decltype(actual.pose.matrix.inverse)>(GetProcAddress(module,"D3DXMatrixInverse")),reinterpret_cast<decltype(actual.pose.matrix.multiply)>(GetProcAddress(module,"D3DXMatrixMultiply"))};actual.pose.slerp=reinterpret_cast<decltype(actual.pose.slerp)>(GetProcAddress(module,"D3DXQuaternionSlerp"));actual.pose.rotationQuaternion=reinterpret_cast<decltype(actual.pose.rotationQuaternion)>(GetProcAddress(module,"D3DXMatrixRotationQuaternion"));actual.rotationX=reinterpret_cast<decltype(actual.rotationX)>(GetProcAddress(module,"D3DXMatrixRotationX"));actual.rotationY=reinterpret_cast<decltype(actual.rotationY)>(GetProcAddress(module,"D3DXMatrixRotationY"));actual.rotationZ=reinterpret_cast<decltype(actual.rotationZ)>(GetProcAddress(module,"D3DXMatrixRotationZ"));actual.quaternionMatrix=reinterpret_cast<decltype(actual.quaternionMatrix)>(GetProcAddress(module,"D3DXQuaternionRotationMatrix"));actual.quaternionAxis=reinterpret_cast<decltype(actual.quaternionAxis)>(GetProcAddress(module,"D3DXQuaternionRotationAxis"));SE_CHECK(actual.pose.matrix.inverse && actual.pose.matrix.multiply && actual.pose.slerp && actual.pose.rotationQuaternion && actual.rotationX && actual.rotationY && actual.rotationZ && actual.quaternionMatrix && actual.quaternionAxis);auto math=actual;math.rotationX=x;math.rotationY=y;math.rotationZ=z;math.quaternionAxis=axis;math.ticks=tick;math.sineFloat=modernSine;
    RF455CharacterTextureApi texture={reinterpret_cast<decltype(texture.memory2D)>(GetProcAddress(module,"D3DXCreateTextureFromFileInMemoryEx")),reinterpret_cast<decltype(texture.memoryCube)>(GetProcAddress(module,"D3DXCreateCubeTextureFromFileInMemoryEx")),reinterpret_cast<decltype(texture.file2D)>(GetProcAddress(module,"D3DXCreateTextureFromFileA"))};auto* oldApi=RF455_SetCharacterTextureApi(&texture);RF455CharacterRfsCache cache;auto* oldCache=RF455_SetCharacterRfsCache(&cache);const auto saved=_control87(0,0);_clearfp();_control87(_MCW_EM|_PC_53|_RC_NEAR,_MCW_EM|_MCW_PC|_MCW_RC);Reader golden;SE_CHECK(golden.open(goldenPath) && golden.number()==0x35345353 && golden.number()==1);SE_CHECK(scalars(golden,math)==0 && human(golden,workspace,math)==0);_clearfp();_control87(saved,_MCW_EM|_MCW_PC|_MCW_RC);RF455_SetCharacterRfsCache(oldCache);RF455_SetCharacterTextureApi(oldApi);SE_CHECK(FreeLibrary(module));return 0;
}
}
extern "C" int RF455_RunSecondaryChecks(const char* workspace,const char* golden,const char* dll,const char* output){checks=cases=humanModels=humanUpdates=clockCalls=0;const int result=run(workspace,golden,dll);FILE* f=std::fopen(output,"wb");if(!f)return 1;std::fprintf(f,"{\"status\":\"%s\",\"checks\":%u,\"scalar_cases\":%u,\"human_models\":%u,\"human_updates\":%u,\"sine_provider\":\"modern_MT_sin_double_then_float32_not_reference_parity\",\"rendered\":false}\n",result?"FAIL":"PASS",checks,cases,humanModels,humanUpdates);std::fclose(f);return result;}
#ifndef RF455_SECONDARY_EMBEDDED
int main(int argc,char** argv){if(argc!=5)return 2;return RF455_RunSecondaryChecks(argv[1],argv[2],argv[3],argv[4]);}
#endif
