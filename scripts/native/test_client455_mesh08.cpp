#include "client455_mesh08.h"
#include <windows.h>
#include <cstdio>
#include <cstring>
#include <cstdint>
#include <vector>
#include <string>
#include <limits>

static unsigned checks,failures,files,partsChecked,boundaryCases;
#define M8_CHECK(value) do{++checks;if(!(value)){++failures;std::fprintf(stderr,"mesh08 check%u line%d\n",checks,__LINE__);return 1;}}while(0)
static std::uint32_t fnv(const unsigned char* bytes,std::size_t size){
    std::uint32_t result=2166136261u;for(std::size_t n=0;n<size;++n)result=(result^bytes[n])*16777619u;return result;
}
static void word(std::vector<unsigned char>& data,unsigned value){data.push_back(static_cast<unsigned char>(value));data.push_back(static_cast<unsigned char>(value>>8));}
static void dword(std::vector<unsigned char>& data,std::uint32_t value){for(unsigned n=0;n<4;++n)data.push_back(static_cast<unsigned char>(value>>(8*n)));}
static std::vector<unsigned char> fixture(unsigned vertices=3,unsigned indices=3,unsigned bones=1){
    std::vector<unsigned char> data={'M','E','S','H','0','8',1,0};data.resize(8+693,0);std::memcpy(data.data()+8,"ROOT",4);
    word(data,vertices);for(unsigned n=0;n<vertices*64;++n)data.push_back(static_cast<unsigned char>(n*17+3));
    word(data,indices);for(unsigned n=0;n<indices;++n)word(data,vertices?n%vertices:0);
    word(data,bones);for(unsigned n=0;n<bones;++n){dword(data,2);const auto start=data.size();data.resize(start+400,0);data[start]='A';data[start+100]='B';}
    return data;
}
static bool readFile(const std::string& name,std::vector<unsigned char>& bytes){
    FILE* fp=std::fopen(name.c_str(),"rb");if(!fp)return false;
    if(std::fseek(fp,0,SEEK_END)){std::fclose(fp);return false;}const long length=std::ftell(fp);
    if(length<0 || std::fseek(fp,0,SEEK_SET)){std::fclose(fp);return false;}
    bytes.resize(static_cast<std::size_t>(length));const bool ok=bytes.empty() || std::fread(bytes.data(),1,bytes.size(),fp)==bytes.size();
    return std::fclose(fp)==0 && ok;
}
struct GoldenReader {
    const std::vector<unsigned char>& data;std::size_t at;bool good;
    std::uint32_t number(unsigned count){
        if(count>data.size()-at){good=false;return 0;}std::uint32_t value=0;
        for(unsigned n=0;n<count;++n)value|=static_cast<std::uint32_t>(data[at++])<<(8*n);return value;
    }
    std::string string(unsigned count){
        if(count>data.size()-at){good=false;return {};}
        std::string value(reinterpret_cast<const char*>(data.data()+at),count);at+=count;return value;
    }
};
static int runMesh08Checks(const char* goldenPath,FILE* output){
    std::vector<unsigned char> golden;M8_CHECK(readFile(goldenPath,golden));GoldenReader g={golden,0,true};
    M8_CHECK(g.string(4)=="M8FX");M8_CHECK(g.number(4)==1);const unsigned sampleCount=g.number(4);M8_CHECK(sampleCount>0 && sampleCount<=100);
    const std::string path(goldenPath);const auto slash=path.find_last_of("/\\");const std::string directory=slash==std::string::npos?"":path.substr(0,slash+1);
    for(unsigned file=0;file<sampleCount;++file){
        const unsigned nameLength=g.number(2);M8_CHECK(nameLength<256);const auto name=g.string(nameLength);
        const auto length=g.number(4),count=g.number(2),consumed=g.number(4),fileHash=g.number(4);
        std::vector<unsigned char> data;M8_CHECK(readFile(directory+name,data));M8_CHECK(data.size()==length);M8_CHECK(fnv(data.data(),data.size())==fileHash);
        std::vector<RF455Mesh08Part> storage(count);RF455Mesh08View view={};
        M8_CHECK(RF455_DecodeMesh08(data.data(),data.size(),storage.data(),storage.size(),&view)==RF_MESH08_OK);
        M8_CHECK(view.meshCount==count && view.consumed==consumed && view.trailingBytes==data.size()-consumed);
        for(unsigned n=0;n<count;++n){
            ++partsChecked;std::uint32_t values[11];for(auto& value:values)value=g.number(4);const auto& p=storage[n];
            M8_CHECK(p.header==data.data()+values[0]);M8_CHECK(p.vertices==data.data()+values[1]);M8_CHECK(p.indices==data.data()+values[2]);M8_CHECK(p.bones==data.data()+values[3]);
            M8_CHECK(p.vertexCount==values[4] && p.indexCount==values[5] && p.boneCount==values[6]);
            M8_CHECK(fnv(p.header,693)==values[7]);M8_CHECK(fnv(p.vertices,64u*p.vertexCount)==values[8]);M8_CHECK(fnv(p.indices,2u*p.indexCount)==values[9]);M8_CHECK(fnv(p.bones,404u*p.boneCount)==values[10]);
        }
        std::vector<unsigned char> encoded(data.size());std::size_t written=0;
        M8_CHECK(RF455_EncodeMesh08(&view,encoded.data(),encoded.size(),&written)==RF_MESH08_OK);M8_CHECK(written==data.size() && encoded==data);
        M8_CHECK(RF455_EncodeMesh08(&view,data.data(),data.size(),&written)==RF_MESH08_OK);M8_CHECK(data==encoded);
        ++files;
    }
    M8_CHECK(g.good && g.at==golden.size());
    auto data=fixture();RF455Mesh08Part storage[2];RF455Mesh08View view={};
    M8_CHECK(RF455_DecodeMesh08(data.data(),data.size(),storage,2,&view)==RF_MESH08_OK);
    M8_CHECK(view.consumed==data.size() && storage[0].vertexCount==3 && storage[0].indexCount==3 && storage[0].boneCount==1);
    M8_CHECK(storage[0].vertices==data.data()+703 && storage[0].indices==data.data()+897 && storage[0].bones==data.data()+905);
    std::vector<unsigned char> before(data);std::size_t written=12345;
    M8_CHECK(RF455_EncodeMesh08(&view,data.data(),data.size()-1,&written)==RF_MESH08_CAPACITY);M8_CHECK(data==before && written==12345);
    RF455Mesh08View sentinel;std::memset(&sentinel,0xa5,sizeof(sentinel));const auto unchanged=sentinel;
    M8_CHECK(RF455_DecodeMesh08(nullptr,8,storage,2,&sentinel)==RF_MESH08_ARGUMENT);M8_CHECK(!std::memcmp(&sentinel,&unchanged,sizeof(sentinel)));
    M8_CHECK(RF455_DecodeMesh08(data.data(),data.size(),nullptr,2,&sentinel)==RF_MESH08_CAPACITY);
    M8_CHECK(RF455_DecodeMesh08(data.data(),data.size(),storage,0,&sentinel)==RF_MESH08_CAPACITY);
    before=data;before[0]='m';M8_CHECK(RF455_DecodeMesh08(before.data(),before.size(),storage,2,&sentinel)==RF_MESH08_MAGIC);
    SYSTEM_INFO systemInfo;GetSystemInfo(&systemInfo);const std::size_t page=systemInfo.dwPageSize;M8_CHECK(data.size()<page);
    auto* guarded=static_cast<unsigned char*>(VirtualAlloc(nullptr,2*page,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE));M8_CHECK(guarded!=nullptr);
    DWORD previous=0;M8_CHECK(VirtualProtect(guarded+page,page,PAGE_NOACCESS,&previous)!=FALSE);
    for(std::size_t length=0;length<data.size();++length){
        auto* input=guarded+page-length;if(length)std::memcpy(input,data.data(),length);sentinel=unchanged;
        M8_CHECK(RF455_DecodeMesh08(input,length,storage,2,&sentinel)==RF_MESH08_TRUNCATED);M8_CHECK(!std::memcmp(&sentinel,&unchanged,sizeof(sentinel)));++boundaryCases;
    }
    M8_CHECK(VirtualFree(guarded,0,MEM_RELEASE)!=FALSE);
    auto maximum=fixture(1,64000,0);M8_CHECK(RF455_DecodeMesh08(maximum.data(),maximum.size(),storage,2,&view)==RF_MESH08_OK);M8_CHECK(storage[0].indexCount==64000);
    auto excessive=fixture(1,64001,0);M8_CHECK(RF455_DecodeMesh08(excessive.data(),excessive.size(),storage,2,&sentinel)==RF_MESH08_INDEX_LIMIT);
    auto manyVertices=fixture(65535,0,0);M8_CHECK(RF455_DecodeMesh08(manyVertices.data(),manyVertices.size(),storage,2,&view)==RF_MESH08_OK);M8_CHECK(storage[0].vertexCount==65535);
    std::vector<unsigned char> empty={'M','E','S','H','0','8',0,0,0xff,0,0x80};
    M8_CHECK(RF455_DecodeMesh08(empty.data(),empty.size(),nullptr,0,&view)==RF_MESH08_OK);M8_CHECK(view.meshCount==0 && view.consumed==8 && view.trailingBytes==3);
    std::vector<unsigned char> encoded(empty.size());M8_CHECK(RF455_EncodeMesh08(&view,encoded.data(),encoded.size(),&written)==RF_MESH08_OK);M8_CHECK(encoded==empty);
    view.trailing=reinterpret_cast<const unsigned char*>(1);view.trailingBytes=(std::numeric_limits<std::size_t>::max)()-4;
    M8_CHECK(RF455_EncodeMesh08(&view,nullptr,0,&written)==RF_MESH08_OVERFLOW);
    std::fprintf(output,"{\"checks\":%u,\"failures\":%u,\"real_files\":%u,\"parts\":%u,\"boundary_cases\":%u,\"guard_pages_used\":true,\"gpu_used\":false}\n",checks,failures,files,partsChecked,boundaryCases);
    return failures?1:0;
}
#ifndef RF455_MESH08_EMBEDDED
int main(int argc,char** argv){SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX);if(argc!=2)return 2;return runMesh08Checks(argv[1],stdout);}
#endif
#undef M8_CHECK
