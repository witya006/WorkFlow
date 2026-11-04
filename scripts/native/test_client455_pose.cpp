#include "client455_pose.h"
#include <cstdio>
#include <cstring>
#include <cmath>
#include <float.h>
#include <map>
#include <string>
#include <vector>

static unsigned checks,realPairs,poseUpdates,keyCases,skinParts;
#define PO_CHECK(x) do{++checks;if(!(x)){std::fprintf(stderr,"pose line%d check%u\n",__LINE__,checks);return 1;}}while(0)
template<class T>static T poGet(const void* p,unsigned at){T v;std::memcpy(&v,static_cast<const unsigned char*>(p)+at,sizeof(v));return v;}
template<class T>static void poPut(void* p,unsigned at,T v){std::memcpy(static_cast<unsigned char*>(p)+at,&v,sizeof(v));}
namespace {
void unit(void* p){float m[16]={};m[0]=m[5]=m[10]=m[15]=1;std::memcpy(p,m,64);}
bool file(const std::string& path,std::vector<unsigned char>& bytes){FILE* f=std::fopen(path.c_str(),"rb");if(!f)return false;std::fseek(f,0,SEEK_END);const long n=std::ftell(f);std::rewind(f);if(n<0){std::fclose(f);return false;}bytes.resize(n);const bool ok=!n || std::fread(bytes.data(),1,n,f)==static_cast<std::size_t>(n);std::fclose(f);return ok;}
struct Reader {std::vector<unsigned char> data;std::size_t at=0;bool good=true;
    unsigned number(unsigned n=4){if(at+n>data.size()){good=false;return 0;}unsigned v=0;for(unsigned i=0;i<n;++i)v|=static_cast<unsigned>(data[at++])<<(8*i);return v;}
    std::string text(){const unsigned n=number(2);if(at+n>data.size()){good=false;return {};}std::string s(reinterpret_cast<char*>(data.data()+at),n);at+=n;return s;}
    float real(){const auto u=number();float f;std::memcpy(&f,&u,4);return f;}
};
struct Memory {
    RF455AnimationMemoryOps real=RF455_CrtAnimationMemoryOps();std::map<void*,std::size_t> live;bool bad=false;
    ~Memory(){for(const auto& p:live)real.memory.release(nullptr,p.first);}
    static void* __cdecl allocate(void* c,std::size_t n){auto& m=*static_cast<Memory*>(c);auto* p=m.real.memory.allocate(nullptr,n);if(p)m.live[p]=n;return p;}
    static void __cdecl release(void* c,void* p){auto& m=*static_cast<Memory*>(c);if(p && !m.live.erase(p)){m.bad=true;return;}m.real.memory.release(nullptr,p);}
    static std::size_t __cdecl extent(void* c,const void* p){auto& m=*static_cast<Memory*>(c);if(!m.live.count(const_cast<void*>(p))){m.bad=true;return 0;}return m.real.extent(nullptr,p);}
    RF455AnimationMemoryOps ops(){return {{this,allocate,release},extent};}
};
struct Owners {std::vector<RF455PoseSpan> spans;
    static int __cdecl resolve(void* c,const RF455AnimationData* data,RF455PoseSpan* out){for(const auto& span:static_cast<Owners*>(c)->spans){const auto p=reinterpret_cast<std::uintptr_t>(data->channel[0].keys),base=reinterpret_cast<std::uintptr_t>(span.bytes);if(p>=base && p-base<span.length){*out=span;return 1;}}return 0;}
};
struct Diagnostics {unsigned messages=0;static void __cdecl text(void* c,const char*){++static_cast<Diagnostics*>(c)->messages;}static void __cdecl wide(void* c,const wchar_t*){++static_cast<Diagnostics*>(c)->messages;}RF455LegacyDiagnostics ops(){return {this,text,wide};}};
struct Scene {
    RF455TextureManager textures;RF455VertexBufferPool v64,v36;RF455IndexBufferPool indices;RF455MeshAccounting mesh={};RF455BufferAccounting buffers={};RF455LegacyScratch scratch;
    Scene(){RF455_ConstructTextureManager(&textures);RF455_ConstructVertexPool(&v64);RF455_ConstructVertexPool(&v36);RF455_ConstructIndexPool(&indices);}
    ~Scene(){RF455_DestroyTextureManager(&textures);RF455_DestroyIndexPool(&indices);RF455_DestroyVertexPool(&v36);RF455_DestroyVertexPool(&v64);}
    RF455CharacterLoadContext context(RF455AnimationMemoryOps memory,RF455MeshMatrixOps math,Diagnostics& log,unsigned* bytes){return {{{memory.memory,math,&textures,&v64,&indices,&mesh,&buffers},&v36,4,&scratch,log.ops()},{memory,log.ops(),bytes}};}
};
RF455PoseMath actual;
const void* lastLeft;const void* lastRight;float lastRatio,lastSlerp[4],lastRotation[4];unsigned slerpCalls;
void* __stdcall observeSlerp(void* destination,const void* a,const void* b,float ratio){++slerpCalls;lastLeft=a;lastRight=b;lastRatio=ratio;auto* result=actual.slerp(destination,a,b,ratio);std::memcpy(lastSlerp,destination,16);return result;}
void* __stdcall observeRotation(void* destination,const void* q){std::memcpy(lastRotation,q,16);return actual.rotationQuaternion(destination,q);}
bool bits(float a,float b){return !std::memcmp(&a,&b,4);}
int selectedKeys(Reader& golden,const char* workspace,RF455PoseMath math){
    const unsigned count=golden.number();std::map<std::string,std::vector<unsigned char>> cache;
    for(unsigned n=0;n<count;++n){const auto path=golden.text();const auto offset=golden.number(),channel=golden.number();const auto frameBits=golden.number();int frame;std::memcpy(&frame,&frameBits,4);const auto expectedIndex=golden.number();const float ratio=golden.real();float vector[3];for(auto& f:vector)f=golden.real();auto& raw=cache[path];if(raw.empty())PO_CHECK(file(std::string(workspace)+"/"+path,raw));
        std::vector<RF455AniTrackView> tracks(255);RF455AniView view={};PO_CHECK(RF455_DecodeAni(raw.data(),raw.size(),tracks.data(),tracks.size(),&view,nullptr)==RF_ANIMATION_OK);const RF455AniTrackView* track=nullptr;for(unsigned i=0;i<view.trackCount;++i)if(tracks[i].header==raw.data()+offset)track=tracks.data()+i;PO_CHECK(track && channel<3);const unsigned stride=channel?16:20;RF455PoseSpan owner={raw.data(),raw.size()};RF455PoseKeyPair pair={};PO_CHECK(RF455_SelectPoseKeys(track->data.channel+channel,stride,frame,channel==2,&owner,&pair)==RF_POSE_OK && pair.index==expectedIndex && bits(pair.ratio,ratio));
        RF455MeshStorage mesh;RF455MeshAccounting account={};RF455_ConstructMeshStorage(&mesh,&account);unit(mesh.bytes+4766);unit(mesh.bytes+5022);for(unsigned i=0;i<3;++i){poPut<float>(mesh.bytes,5483+4*i,1);poPut<float>(mesh.bytes,4750+4*i,static_cast<float>(i+3));}float output[16];unit(output);
        if(channel==2){PO_CHECK(RF455_ApplyPoseScale(output,frame,&mesh,&track->data,&owner,&math)==RF_POSE_OK);for(unsigned i=0;i<3;++i)PO_CHECK(bits(output[5*i],vector[i]));}
        else if(channel==1){PO_CHECK(RF455_ApplyPoseTranslation(output,frame,&mesh,&track->data,&owner)==RF_POSE_OK);PO_CHECK(!std::memcmp(output+12,vector,12));}
        else{const auto before=slerpCalls;PO_CHECK(RF455_ApplyPoseRotation(output,frame,&mesh,&track->data,&owner,&math)==RF_POSE_OK && slerpCalls==before+1 && lastLeft==pair.left && lastRight==pair.right && bits(lastRatio,ratio));PO_CHECK(!std::memcmp(lastSlerp,lastRotation,12));unsigned expectedW=poGet<unsigned>(lastSlerp,12)^0x80000000;PO_CHECK(poGet<unsigned>(lastRotation,12)==expectedW && output[12]==3 && output[13]==4 && output[14]==5);}
        ++keyCases;
    }
    return 0;
}
struct VectorKey {float x,y,z;int time;};
int edgeKeys(){
    VectorKey keys[]={{0,0,0,0},{10,0,0,160},{20,0,0,320}};RF455PoseSpan owner={reinterpret_cast<const unsigned char*>(keys),sizeof(keys)};RF455AnimationChannel channel={0xffff0003,owner.bytes};RF455PoseKeyPair pair={};
    for(int linear:{0,1}){PO_CHECK(RF455_SelectPoseKeys(&channel,16,-80,linear,&owner,&pair)==RF_POSE_OK && pair.index==0 && pair.ratio==-.5f);PO_CHECK(RF455_SelectPoseKeys(&channel,16,400,linear,&owner,&pair)==RF_POSE_OK && pair.index==1 && pair.ratio==1.5f);}
    channel.count=1;PO_CHECK(RF455_SelectPoseKeys(&channel,16,80,0,&owner,&pair)==RF_POSE_OK && pair.ratio==.5f);owner.length=16;PO_CHECK(RF455_SelectPoseKeys(&channel,16,80,0,&owner,&pair)==RF_POSE_BOUNDS);owner.length=sizeof(keys);channel.count=2;keys[1].time=0;PO_CHECK(RF455_SelectPoseKeys(&channel,16,80,1,&owner,&pair)==RF_POSE_OK && pair.ratio==0);
    keys[1].time=static_cast<int>(0x80000001u);PO_CHECK(RF455_SelectPoseKeys(&channel,16,1,0,&owner,&pair)==RF_POSE_OK && bits(pair.ratio,static_cast<float>(1.0/2147483649.0)));keys[0].time=0x7fffffff;keys[1].time=static_cast<int>(0x80000000u);PO_CHECK(RF455_SelectPoseKeys(&channel,16,0,0,&owner,&pair)==RF_POSE_OK && bits(pair.ratio,static_cast<float>(-2147483647.0)));
    return 0;
}
RF455AnimationData descriptor(VectorKey* keys){RF455AnimationData data={};data.channel[0].keys=reinterpret_cast<const unsigned char*>(keys);data.channel[1]={3,reinterpret_cast<const unsigned char*>(keys)};return data;}
int analytic(Scene& scene,RF455PoseMath math){
    const unsigned saved=_control87(0,0);const unsigned precision[]={_PC_24,_PC_53,_PC_64},rounding[]={_RC_NEAR,_RC_DOWN,_RC_UP,_RC_CHOP};
    for(unsigned pc:precision)for(unsigned rc:rounding){_clearfp();_control87(_MCW_EM|pc|rc,_MCW_EM|_MCW_PC|_MCW_RC);
        for(unsigned scenario=0;scenario<8;++scenario){Memory memory;auto ops=memory.ops();Diagnostics log;unsigned imported=0;auto load=scene.context(ops,math.matrix,log,&imported);RF455CharacterStorage model;RF455_ConstructCharacter(&model);auto* b=reinterpret_cast<unsigned char*>(&model);poPut<unsigned>(b,260,1);RF455MeshAccounting account={};auto* meshes=RF455_AllocateMeshArray(3,&account,&ops.memory);PO_CHECK(meshes);poPut<unsigned>(b,532,3);poPut(b,536,meshes);poPut<unsigned>(b,672,80);poPut<unsigned>(b,684,160);poPut<unsigned>(b,680,7);poPut<unsigned>(b,688,9);poPut<float>(b,692,scenario==1?-1.0f:scenario==2?100.0f:50.0f);
            VectorKey current[]={{0,0,0,0},{10,0,0,160},{20,0,0,320}},previous[]={{100,0,0,0},{110,0,0,160},{120,0,0,320}};Owners owners;owners.spans={{reinterpret_cast<const unsigned char*>(current),sizeof(current)},{reinterpret_cast<const unsigned char*>(previous),sizeof(previous)}};
            for(unsigned i=0;i<3;++i){auto* m=meshes[i].bytes;std::sprintf(reinterpret_cast<char*>(m),"node%u",i);for(unsigned at:{4574u,4638u,4702u,4766u,4830u,4894u,4958u,5022u})unit(m+at);for(unsigned axis=0;axis<3;++axis)poPut<float>(m,5483+4*axis,1);if(i==1){m[512]=1;poPut(m,518,meshes);poPut<float>(m,4750,10);poPut<float>(m,4878,10);poPut<unsigned>(m,522,1);poPut(m,526,meshes);}else if(scenario<4){auto data=descriptor(current);auto* p=Memory::allocate(&memory,32);std::memcpy(p,&data,32);poPut(m,5095,p);m[5094]=1;if(scenario<3){data=descriptor(previous);p=Memory::allocate(&memory,32);std::memcpy(p,&data,32);poPut(m,5099,p);}}}
            if(scenario==3){poPut<unsigned>(b,704,1);poPut<unsigned>(b,708,1);poPut<unsigned>(b,712,1);poPut<unsigned>(b,716,2);}
            if(scenario==4){poPut<unsigned>(meshes[0].bytes,5499,1);unit(meshes[0].bytes+5503);poPut<float>(meshes[0].bytes,5503,2);poPut<float>(meshes[0].bytes,5551,77);}
            if(scenario==5){poPut<unsigned>(meshes[0].bytes,5571,1);poPut<unsigned>(b,1184,1);}
            if(scenario==6)meshes[0].bytes[5094]=1;
            if(scenario==7){for(unsigned i=0;i<3;++i)poPut<unsigned>(meshes[i].bytes,5575,0);poPut<unsigned>(b,796,1);poPut<unsigned>(meshes[0].bytes,5575,3);}
            RF455PoseScratch scratch={};RF455PoseContext context={&load,math,&scratch,100,&owners,Owners::resolve};const auto result=RF455_UpdateCharacterPose(&model,&context);
            if(scenario!=5 && result!=RF_POSE_OK)std::fprintf(stderr,"analytic scenario%u result%d slots%u/%u/%u\n",scenario,result,poGet<unsigned>(meshes[0].bytes,5575),poGet<unsigned>(meshes[1].bytes,5575),poGet<unsigned>(meshes[2].bytes,5575));
            if(scenario==5)PO_CHECK(result==RF_POSE_SECONDARY && poGet<unsigned>(b,1184)==1);
            else{PO_CHECK(result==RF_POSE_OK && !poGet<unsigned>(b,708) && scratch.initialized==63 && !poGet<unsigned>(b,1184));const float root=scenario==0?57.5f:scenario==3?2.5f:scenario<3?5.0f:0.0f;const float child=scenario==4?20.0f:root+10;
                // Pinned D3DX inverse uses approximate reciprocal even for I.
                // Only this parent-ramp analytic expectation allows 1e-4; the
                // real skin/parent identities below compare all64bytes exactly.
                const float actualChild=poGet<float>(meshes[1].bytes,4878);const bool childOK=scenario==3?std::fabs(actualChild-child)<.0001f:actualChild==child;
                PO_CHECK(poGet<float>(meshes[0].bytes,4878)==root && childOK && poGet<float>(meshes[1].bytes,694)==root);if(scenario==2)PO_CHECK(!poGet<void*>(meshes[0].bytes,5099) && !poGet<void*>(meshes[2].bytes,5099) && !poGet<unsigned>(b,680) && poGet<unsigned>(b,684)==160 && !poGet<unsigned>(b,688));if(scenario==6)PO_CHECK(log.messages==1);}
            if(scenario==7)PO_CHECK(!std::memcmp(b+1120,meshes[0].bytes+4638,64) && !std::memcmp(b+928,meshes[0].bytes+4830,64));
            RF455_ReleaseModelMeshArray(&model.prefix,&ops.memory);PO_CHECK(memory.live.empty() && !memory.bad);
        }
    }
    _clearfp();_control87(saved,_MCW_EM|_MCW_PC|_MCW_RC);
    Memory memory;auto ops=memory.ops();Diagnostics log;unsigned imported=0;auto load=scene.context(ops,math.matrix,log,&imported);Owners owners;RF455PoseScratch scratch={};RF455PoseContext context={&load,math,&scratch,100,&owners,Owners::resolve};RF455CharacterStorage empty;RF455_ConstructCharacter(&empty);poPut<unsigned>(&empty,260,1);poPut<unsigned>(&empty,708,1);poPut<unsigned>(&empty,1184,1);PO_CHECK(RF455_UpdateCharacterPose(nullptr,nullptr)==RF_POSE_OK && RF455_UpdateCharacterPose(&empty,&context)==RF_POSE_OK && !poGet<unsigned>(&empty,708) && !poGet<unsigned>(&empty,1184) && scratch.initialized==63);
    RF455_ConstructCharacter(&empty);std::strcpy(reinterpret_cast<char*>(empty.prefix.bytes+4),"missing_pose_model.bn");poPut<unsigned>(&empty,1184,1);PO_CHECK(RF455_UpdateCharacterPose(&empty,&context)==RF_POSE_LOAD && !poGet<unsigned>(&empty,1184) && memory.live.empty());return 0;
}
int matrices(const RF455CharacterStorage& model,RF455PoseMath math){
    const auto* meshes=poGet<const RF455MeshStorage*>(model.prefix.bytes,536);const unsigned count=poGet<unsigned>(model.prefix.bytes,532);
    for(unsigned i=0;i<count;++i){const auto* m=meshes[i].bytes;for(unsigned k=0;k<16;++k)PO_CHECK(std::isfinite(poGet<float>(m,4830+4*k)));const unsigned n=poGet<unsigned>(m,522);PO_CHECK(n<=50);for(unsigned j=0;j<n;++j){const auto* bone=poGet<const RF455MeshStorage*>(m,526+4*j);PO_CHECK(bone);float first[16],expected[16];PO_CHECK(math.matrix.multiply(first,m+4574,bone->bytes+4638) && math.matrix.multiply(expected,first,bone->bytes+4830));PO_CHECK(!std::memcmp(expected,m+646+64*j,64));++skinParts;}
        if(!m[5094] && !poGet<unsigned>(m,5499)){float expected[16];if(m[512]){const auto* parent=poGet<const RF455MeshStorage*>(m,518);PO_CHECK(parent && math.matrix.multiply(expected,m+4702,parent->bytes+4830));}else std::memcpy(expected,m+4702,64);PO_CHECK(!std::memcmp(expected,m+4830,64));}
    }
    return 0;
}
int realModels(Reader& golden,const char* workspace,Scene& scene,RF455PoseMath math){
    PO_CHECK(golden.number()==11);
    for(unsigned i=0;i<11;++i){const std::string bone=std::string(workspace)+"/"+golden.text(),mesh=std::string(workspace)+"/"+golden.text();std::string ani[2];for(auto& p:ani)p=std::string(workspace)+"/"+golden.text();Memory memory;auto ops=memory.ops();Diagnostics log;unsigned bytes=0;auto load=scene.context(ops,math.matrix,log,&bytes);RF455CharacterStorage root,child;RF455_ConstructCharacter(&root);RF455_ConstructCharacter(&child);std::strcpy(reinterpret_cast<char*>(root.prefix.bytes+4),bone.c_str());std::strcpy(reinterpret_cast<char*>(child.prefix.bytes+4),mesh.c_str());for(auto* p:{&root,&child})std::strcpy(reinterpret_cast<char*>(p->prefix.bytes+276),".\\tex");poPut(child.prefix.bytes,272,&root.prefix);PO_CHECK(RF455_LoadCharacter(&root,0,&load) && RF455_LoadCharacter(&child,0,&load));
        RF455AnimationStorage animations[2];Owners owners;RF455PoseScratch scratch={};RF455PoseContext context={&load,math,&scratch,150,&owners,Owners::resolve};
        for(unsigned pose=0;pose<2;++pose){auto& animation=animations[pose];RF455_ConstructAnimation(&animation);std::strcpy(reinterpret_cast<char*>(animation.bytes+5),ani[pose].c_str());PO_CHECK(RF455_MatchAnimation(&animation,&root,&load));const auto* raw=poGet<const unsigned char*>(animation.bytes,268);owners.spans.push_back({raw,Memory::extent(&memory,raw)});
            for(unsigned phase=0;phase<3;++phase){poPut<unsigned>(root.prefix.bytes,672,160u<<phase);poPut<unsigned>(root.prefix.bytes,684,80);poPut<float>(root.prefix.bytes,692,75.0f*phase);PO_CHECK(RF455_UpdateCharacterPose(&root,&context)==RF_POSE_OK && RF455_UpdateCharacterPose(&child,&context)==RF_POSE_OK);PO_CHECK(matrices(root,math)==0 && matrices(child,math)==0);poseUpdates+=2;}
        }
        RF455_ReleaseModelMeshArray(&child.prefix,&ops.memory);RF455_ReleaseModelMeshArray(&root.prefix,&ops.memory);for(auto& animation:animations)RF455_DestroyAnimation(&animation,&ops.memory);PO_CHECK(memory.live.empty() && !memory.bad);++realPairs;
    }
    PO_CHECK(golden.good && golden.at==golden.data.size());return 0;
}
int run(const char* workspace,const char* goldenPath,const char* dll){
    HMODULE provider=LoadLibraryA(dll);PO_CHECK(provider);actual.matrix={reinterpret_cast<decltype(actual.matrix.inverse)>(GetProcAddress(provider,"D3DXMatrixInverse")),reinterpret_cast<decltype(actual.matrix.multiply)>(GetProcAddress(provider,"D3DXMatrixMultiply"))};actual.slerp=reinterpret_cast<decltype(actual.slerp)>(GetProcAddress(provider,"D3DXQuaternionSlerp"));actual.rotationQuaternion=reinterpret_cast<decltype(actual.rotationQuaternion)>(GetProcAddress(provider,"D3DXMatrixRotationQuaternion"));PO_CHECK(actual.matrix.inverse && actual.matrix.multiply && actual.slerp && actual.rotationQuaternion);RF455PoseMath math={actual.matrix,observeSlerp,observeRotation};
    RF455CharacterTextureApi texture={reinterpret_cast<decltype(texture.memory2D)>(GetProcAddress(provider,"D3DXCreateTextureFromFileInMemoryEx")),reinterpret_cast<decltype(texture.memoryCube)>(GetProcAddress(provider,"D3DXCreateCubeTextureFromFileInMemoryEx")),reinterpret_cast<decltype(texture.file2D)>(GetProcAddress(provider,"D3DXCreateTextureFromFileA"))};auto* oldApi=RF455_SetCharacterTextureApi(&texture);RF455CharacterRfsCache cache;auto* oldCache=RF455_SetCharacterRfsCache(&cache);Reader golden;PO_CHECK(file(goldenPath,golden.data) && golden.number()==0x35345350 && golden.number()==1);
    const unsigned saved=_control87(0,0);_clearfp();_control87(_MCW_EM|_PC_53|_RC_NEAR,_MCW_EM|_MCW_PC|_MCW_RC);PO_CHECK(selectedKeys(golden,workspace,math)==0 && edgeKeys()==0);{Scene scene;PO_CHECK(analytic(scene,math)==0 && realModels(golden,workspace,scene,math)==0);} _clearfp();_control87(saved,_MCW_EM|_MCW_PC|_MCW_RC);RF455_SetCharacterTextureApi(oldApi);RF455_SetCharacterRfsCache(oldCache);PO_CHECK(FreeLibrary(provider));return 0;
}
}
extern "C" int RF455_RunPoseChecks(const char* workspace,const char* golden,const char* dll,const char* output){checks=realPairs=poseUpdates=keyCases=skinParts=slerpCalls=0;const int result=run(workspace,golden,dll);FILE* f=std::fopen(output,"wb");if(!f)return 1;std::fprintf(f,"{\"status\":\"%s\",\"checks\":%u,\"key_cases\":%u,\"real_pairs\":%u,\"pose_updates\":%u,\"skin_matrices\":%u,\"fp_modes\":12}\n",result?"FAIL":"PASS",checks,keyCases,realPairs,poseUpdates,skinParts);std::fclose(f);return result;}
#ifndef RF455_POSE_EMBEDDED
int main(int argc,char** argv){if(argc!=5)return 2;return RF455_RunPoseChecks(argv[1],argv[2],argv[3],argv[4]);}
#endif
