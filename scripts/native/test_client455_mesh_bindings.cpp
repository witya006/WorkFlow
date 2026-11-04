#include "client455_mesh_bindings.h"
#include <cstdio>
#include <cstring>
#include <cstdint>
#include <string>
#include <vector>

static unsigned bindingChecks,bindingFailures,bindingFiles,bindingParts,overlapCases;
#define MB_CHECK(value) do{++bindingChecks;if(!(value)){++bindingFailures;std::fprintf(stderr,"mesh binding check%u line%d\n",bindingChecks,__LINE__);return 1;}}while(0)
template<class T> static T mbRead(const unsigned char* data,unsigned at){T x;std::memcpy(&x,data+at,sizeof(x));return x;}
template<class T> static void mbWrite(unsigned char* data,unsigned at,T x){std::memcpy(data+at,&x,sizeof(x));}
static void mbName(RF455MeshStorage& mesh,unsigned at,const std::string& name){std::memset(mesh.bytes+at,0,256);std::memcpy(mesh.bytes+at,name.data(),name.size());}
static void mbInit(RF455MeshStorage& mesh,const std::string& name,const std::string& parentName="?"){
    std::memset(&mesh,0xa5,sizeof(mesh));mbName(mesh,0,name);mbName(mesh,256,parentName);mbWrite<std::uint32_t>(mesh.bytes,5495,0);
}
static bool mbFile(const std::string& name,std::vector<unsigned char>& bytes){
    FILE* f=std::fopen(name.c_str(),"rb");if(!f)return false;
    if(std::fseek(f,0,SEEK_END)){std::fclose(f);return false;}const long size=std::ftell(f);
    if(size<0 || std::fseek(f,0,SEEK_SET)){std::fclose(f);return false;}
    bytes.resize(static_cast<std::size_t>(size));const bool ok=bytes.empty() || std::fread(bytes.data(),1,bytes.size(),f)==bytes.size();return std::fclose(f)==0 && ok;
}
struct MBReader {
    const std::vector<unsigned char>& bytes;std::size_t at=0;bool ok=true;
    std::uint32_t number(unsigned count=4){if(count>bytes.size()-at){ok=false;return 0;}std::uint32_t x=0;for(unsigned n=0;n<count;++n)x|=static_cast<std::uint32_t>(bytes[at++])<<(8*n);return x;}
    std::string string(){const auto count=number(2);if(count>bytes.size()-at){ok=false;return {}; }const std::string x(reinterpret_cast<const char*>(bytes.data()+at),count);at+=count;return x;}
};
static RF455MeshStorage* mbToken(std::int32_t token,std::vector<RF455MeshStorage>& external,std::vector<RF455MeshStorage>& local){
    return token>0?&external[static_cast<unsigned>(token-1)]:token<0?&local[static_cast<unsigned>(-token-1)]:nullptr;
}
static void mbExpectedBlend(RF455MeshStorage& mesh,const std::vector<RF455MeshStorage*>& selected){
    const auto count=static_cast<std::uint32_t>(selected.size());mbWrite(mesh.bytes,522,count);
    for(unsigned i=0;i<count;++i){std::uint32_t identity[16]={0x3f800000,0,0,0,0,0x3f800000,0,0,0,0,0x3f800000,0,0,0,0,0x3f800000};std::memcpy(mesh.bytes+646+64*i,identity,64);}
    if(count)std::memcpy(mesh.bytes+526,selected.data(),4u*count);
}
static int runMeshBindingChecks(const char* goldenPath,const char* workspace,FILE* output){
    std::vector<unsigned char> bytes;MB_CHECK(mbFile(goldenPath,bytes));MBReader g={bytes};
    MB_CHECK(g.number()==0x4742384d);MB_CHECK(g.number()==1);const unsigned files=g.number();MB_CHECK(files==12);
    for(unsigned file=0;file<files;++file){
        const auto path=g.string();const unsigned externalCount=g.number();MB_CHECK(externalCount>0 && externalCount<1000);
        std::vector<RF455MeshStorage> external(externalCount);for(auto& mesh:external)mbInit(mesh,g.string());
        const unsigned count=g.number();MB_CHECK(count>0 && count<1000);
        std::vector<RF455MeshStorage> meshes(count),expected(count);std::vector<std::int32_t> parents(count);std::vector<std::vector<std::int32_t>> selected(count);unsigned missing=0,resolved=0;
        for(unsigned n=0;n<count;++n){
            const auto name=g.string(),parentName=g.string();MB_CHECK(name.size()<256 && parentName.size()<256);mbInit(meshes[n],name,parentName);
            parents[n]=static_cast<std::int32_t>(g.number());MB_CHECK(parents[n]>=-static_cast<int>(count) && parents[n]<=static_cast<int>(externalCount));
            const unsigned bones=g.number();MB_CHECK(bones<=50);selected[n].resize(bones);
            for(auto& token:selected[n]){token=static_cast<std::int32_t>(g.number());MB_CHECK(token && token>=-static_cast<int>(count) && token<=static_cast<int>(externalCount));}
            missing+=g.number();resolved+=bones;
        }
        MB_CHECK(g.ok);expected=meshes;
        for(unsigned n=0;n<count;++n){
            if(parents[n]){mbWrite(expected[n].bytes,518,mbToken(parents[n],external,meshes));expected[n].bytes[512]=1;if(parents[n]>0)mbWrite<std::uint32_t>(expected[n].bytes,5495,1);}
        }
        RF455_BindMeshParents(meshes.data(),static_cast<int>(count),meshes.data(),static_cast<int>(count));
        RF455_BindMeshParents(external.data(),static_cast<int>(externalCount),meshes.data(),static_cast<int>(count));
        MB_CHECK(!std::memcmp(meshes.data(),expected.data(),count*sizeof(RF455MeshStorage)));
        std::vector<unsigned char> input;MB_CHECK(mbFile(std::string(workspace)+"/"+path,input));
        std::vector<RF455Mesh08Part> parts(count);RF455Mesh08View view={};
        MB_CHECK(RF455_DecodeMesh08(input.data(),input.size(),parts.data(),count,&view)==RF_MESH08_OK && view.meshCount==count);
        RF455MeshBindingStats stats={123,456};MB_CHECK(RF455_ResolveMesh08Bones(external.data(),static_cast<int>(externalCount),meshes.data(),static_cast<int>(count),parts.data(),&stats)==RF_MESH_BIND_OK);
        MB_CHECK(stats.missingNames==missing && stats.resolvedNames==resolved);
        for(unsigned n=0;n<count;++n){
            std::vector<RF455MeshStorage*> pointers;for(auto token:selected[n])pointers.push_back(mbToken(token,external,meshes));
            mbExpectedBlend(expected[n],pointers);MB_CHECK(!std::memcmp(&meshes[n],&expected[n],sizeof(RF455MeshStorage)));++bindingParts;
        }
        ++bindingFiles;
    }
    MB_CHECK(g.ok && g.at==bytes.size());
    RF455MeshStorage external[4],local[3];mbInit(external[0],"A");mbInit(external[1],"A");mbInit(external[2],"a");mbInit(external[3],"B");
    mbInit(local[0],"A","A");mbInit(local[1],"C","A");mbInit(local[2],"X","a");
    MB_CHECK(RF455_FindParentMesh("A",external,4)==&external[0]);MB_CHECK(RF455_FindParentMesh("a",external,4)==&external[2]);MB_CHECK(!RF455_FindParentMesh("b",external,4));
    MB_CHECK(!RF455_FindParentMesh(nullptr,nullptr,-1));MB_CHECK(!RF455_BindMeshParents(nullptr,-1,nullptr,0));
    MB_CHECK(RF455_BindMeshParents(local,3,local,3)==2);MB_CHECK(mbRead<RF455MeshStorage*>(local[1].bytes,518)==&local[0]);MB_CHECK(mbRead<std::uint32_t>(local[1].bytes,5495)==0);
    MB_CHECK(RF455_RematchMeshParents(external,4,local,3)==0);
    mbWrite<std::uint32_t>(local[1].bytes,5495,2);MB_CHECK(RF455_RematchMeshParents(external,4,local,3)==1);MB_CHECK(mbRead<RF455MeshStorage*>(local[1].bytes,518)==&external[0]);
    MB_CHECK(mbRead<std::uint32_t>(local[1].bytes,5495)==1);MB_CHECK(RF455_BindMeshParents(external,4,local,3)==3);
    std::vector<unsigned char> records(3*404,0);const char* queries[]={"A","B","A","missing","C","a","B"};
    mbWrite<std::int32_t>(records.data(),0,4);mbWrite<std::int32_t>(records.data(),404,3);mbWrite<std::int32_t>(records.data(),808,-1);
    for(unsigned i=0;i<7;++i)std::strcpy(reinterpret_cast<char*>(records.data()+404*(i/4)+4+100*(i%4)),queries[i]);
    RF455Mesh08Part part={};part.bones=records.data();part.boneCount=3;RF455MeshBindingStats stats={};
    const auto start=local[0];RF455MeshStorage expected=start;
    mbExpectedBlend(expected,{&external[0],&external[3],&local[1],&external[2]});
    MB_CHECK(RF455_ResolveMesh08Bones(external,4,local,1,&part,&stats)==RF_MESH_BIND_OK);
    // Local fallback searches the supplied local count; make C available below.
    MB_CHECK(stats.resolvedNames==3 && stats.missingNames==2);
    local[0]=start;RF455Mesh08Part parts[3]={part,{},{}};
    MB_CHECK(RF455_ResolveMesh08Bones(external,4,local,3,parts,&stats)==RF_MESH_BIND_OK);MB_CHECK(stats.resolvedNames==4 && stats.missingNames==1);MB_CHECK(!std::memcmp(&local[0],&expected,sizeof(expected)));
    part.boneCount=0;local[0]=start;expected=start;mbExpectedBlend(expected,{});
    MB_CHECK(RF455_ResolveMesh08Bones(nullptr,-1,local,1,&part,&stats)==RF_MESH_BIND_OK);MB_CHECK(!std::memcmp(&local[0],&expected,sizeof(expected)));
    MB_CHECK(RF455_ResolveMesh08Bones(nullptr,0,nullptr,-1,nullptr,&stats)==RF_MESH_BIND_OK && !stats.resolvedNames && !stats.missingNames);
    MB_CHECK(RF455_ResolveMesh08Bones(nullptr,1,local,1,&part,&stats)==RF_MESH_BIND_ARGUMENT);
    part.boneCount=1;mbWrite<std::int32_t>(records.data(),0,5);local[0]=start;stats={123,456};
    MB_CHECK(RF455_ResolveMesh08Bones(external,4,local,1,&part,&stats)==RF_MESH_BIND_RECORD);MB_CHECK(!std::memcmp(&local[0],&start,sizeof(start)) && stats.missingNames==123 && stats.resolvedNames==456);
    mbWrite<std::int32_t>(records.data(),0,1);std::memset(records.data()+4,'a',100);
    MB_CHECK(RF455_ResolveMesh08Bones(external,4,local,1,&part,&stats)==RF_MESH_BIND_RECORD);
    std::memset(local[0].bytes,'a',256);MB_CHECK(RF455_ResolveMesh08Bones(external,4,local,1,&part,&stats)==RF_MESH_BIND_RECORD);
    std::vector<RF455MeshStorage> many(51);records.assign(51*404,0);
    for(unsigned i=0;i<51;++i){char name[20];std::sprintf(name,"bone_%02u",i);mbInit(many[i],name);mbWrite<std::uint32_t>(records.data(),404*i,1);std::strcpy(reinterpret_cast<char*>(records.data()+404*i+4),name);}
    part.bones=records.data();
    for(unsigned count=0;count<=50;++count){
        mbInit(local[0],"local");expected=local[0];std::vector<RF455MeshStorage*> pointers;for(unsigned i=0;i<count;++i)pointers.push_back(&many[i]);
        mbExpectedBlend(expected,pointers);part.boneCount=static_cast<std::uint16_t>(count);
        MB_CHECK(RF455_ResolveMesh08Bones(many.data(),51,local,1,&part,&stats)==RF_MESH_BIND_OK);MB_CHECK(stats.resolvedNames==count && !stats.missingNames);MB_CHECK(!std::memcmp(&local[0],&expected,sizeof(expected)));
        if(count>30)++overlapCases;
    }
    mbInit(local[0],"local");const auto before=local[0];part.boneCount=51;stats={123,456};
    MB_CHECK(RF455_ResolveMesh08Bones(many.data(),51,local,1,&part,&stats)==RF_MESH_BIND_CAPACITY);MB_CHECK(!std::memcmp(&local[0],&before,sizeof(before)) && stats.missingNames==123 && stats.resolvedNames==456);
    std::fprintf(output,"{\"checks\":%u,\"failures\":%u,\"real_pairs\":%u,\"parts\":%u,\"overlap_cases\":%u,\"gpu_used\":false}\n",bindingChecks,bindingFailures,bindingFiles,bindingParts,overlapCases);return 0;
}
#ifndef RF455_MESH_BINDINGS_EMBEDDED
int main(int argc,char** argv){return argc==3?runMeshBindingChecks(argv[1],argv[2],stdout):2;}
#endif
