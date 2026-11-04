#include "client455_legacy_model.h"
#include <windows.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <float.h>
#include <map>
#include <string>
#include <vector>

static unsigned checks,files,parts,guardedPrefixes,allocationFailures;
#define LG_CHECK(x) do{++checks;if(!(x)){std::fprintf(stderr,"legacy import check%u line%d\n",checks,__LINE__);return 1;}}while(0)
template<class T>static T lgGet(const void* p,unsigned at){T v;std::memcpy(&v,static_cast<const unsigned char*>(p)+at,sizeof(v));return v;}
template<class T>static void lgPut(void* p,unsigned at,T v){std::memcpy(static_cast<unsigned char*>(p)+at,&v,sizeof(v));}
namespace {
const unsigned offsets[]={696,700,704,716,712};
struct Memory {
    std::map<void*,std::size_t> live;std::map<void*,unsigned> tags;std::vector<unsigned> freed;unsigned calls=0,fail=0;bool bad=false;
    ~Memory(){for(const auto& p:live)std::free(p.first);}
    static void* __cdecl allocate(void* raw,std::size_t size){auto& m=*static_cast<Memory*>(raw);if(++m.calls==m.fail)return nullptr;void* p=std::malloc(size);if(p){m.live[p]=size;std::memset(p,0xa5,size);}return p;}
    static void __cdecl release(void* raw,void* p){auto& m=*static_cast<Memory*>(raw);if(p && !m.live.erase(p)){m.bad=true;return;}m.freed.push_back(m.tags[p]);m.tags.erase(p);std::free(p);}
    void* block(std::size_t n,unsigned tag){void* p=allocate(this,n);if(p)tags[p]=tag;return p;}
    RF455MeshMemoryOps ops(){return {this,allocate,release};}
};
bool read(const std::string& path,std::vector<unsigned char>& b){FILE* f=std::fopen(path.c_str(),"rb");if(!f)return false;std::fseek(f,0,SEEK_END);const long n=std::ftell(f);if(n<0){std::fclose(f);return false;}std::fseek(f,0,SEEK_SET);b.resize(n);const bool ok=!n || std::fread(b.data(),1,n,f)==static_cast<std::size_t>(n);return !std::fclose(f) && ok;}
struct Reader {
    const std::vector<unsigned char>& bytes;std::size_t at=0;bool ok=true;
    const unsigned char* take(std::size_t n){if(n>bytes.size()-at){ok=false;return nullptr;}auto* p=bytes.data()+at;at+=n;return p;}
    unsigned number(unsigned n=4){const auto* p=take(n);if(!p)return 0;unsigned x=0;for(unsigned i=0;i<n;++i)x|=static_cast<unsigned>(p[i])<<(8*i);return x;}
    std::string string(){const auto n=number(2);const auto* p=take(n);return p?std::string(reinterpret_cast<const char*>(p),n):std::string();}
};
int lifetime(){
    Memory memory;auto ops=memory.ops();RF455LegacyPart part,expected;std::memset(&part,0xa5,sizeof(part));expected=part;for(unsigned offset:offsets)lgPut<void*>(expected.bytes,offset,nullptr);
    RF455_ConstructLegacyPart(&part);LG_CHECK(!std::memcmp(&part,&expected,sizeof(part)));for(unsigned n=0;n<5;++n)lgPut(part.bytes,offsets[n],memory.block(n+1,10+n));
    RF455_DestroyLegacyPart(&part,&ops);LG_CHECK(!std::memcmp(&part,&expected,sizeof(part)) && memory.live.empty() && !memory.bad && memory.freed==std::vector<unsigned>({10,11,12,13,14}));
    RF455_DestroyLegacyPart(&part,&ops);LG_CHECK(memory.freed.size()==5);
    RF455LegacyModel model,expectedModel;std::memset(&model,0xa5,sizeof(model));expectedModel=model;for(unsigned at:{4u,12u,20u})lgPut<void*>(expectedModel.bytes,at,nullptr);
    auto* cookie=static_cast<unsigned char*>(memory.block(4+1440,100));LG_CHECK(cookie);lgPut(cookie,0,2u);auto* array=reinterpret_cast<RF455LegacyPart*>(cookie+4);
    for(unsigned i=0;i<2;++i){RF455_ConstructLegacyPart(array+i);for(unsigned n=0;n<5;++n)lgPut(array[i].bytes,offsets[n],memory.block(n+1,20+10*i+n));}
    lgPut(model.bytes,4,array);lgPut(model.bytes,12,memory.block(3,101));lgPut(model.bytes,20,memory.block(4,102));memory.freed.clear();RF455_ReleaseLegacyModel(&model,&ops);
    LG_CHECK(!std::memcmp(&model,&expectedModel,sizeof(model)) && memory.live.empty() && !memory.bad && memory.freed==std::vector<unsigned>({30,31,32,33,34,20,21,22,23,24,100,101,102}));return 0;
}
int samples(const char* workspace,const char* golden,std::vector<unsigned char>& compactInput){
    std::vector<unsigned char> bytes;LG_CHECK(read(golden,bytes));Reader reader={bytes};LG_CHECK(reader.number()==0x4e42474c && reader.number()==1 && reader.number()==17);
    for(unsigned sample=0;sample<17;++sample){const auto path=reader.string();const auto length=reader.number();const auto* expectedHeader=reader.take(28);LG_CHECK(expectedHeader);std::vector<unsigned char> input;LG_CHECK(read(std::string(workspace)+"/"+path,input) && input.size()==length);
        if(path.find("/compact.bin")!=std::string::npos)compactInput=input;
        Memory memory;auto ops=memory.ops();RF455LegacyModel* model=nullptr;std::size_t consumed=0;
        LG_CHECK(RF455_ReadLegacyModel(input.data(),input.size(),&ops,&model,&consumed)==RF_LEGACY_OK && consumed==input.size() && model);
        RF455LegacyModel expected;std::memcpy(expected.bytes,expectedHeader,28);auto* array=lgGet<RF455LegacyPart*>(model->bytes,4);lgPut(expected.bytes,4,array);const auto count=lgGet<unsigned short>(expected.bytes,2);
        LG_CHECK(array && lgGet<unsigned>(reinterpret_cast<unsigned char*>(array)-4,0)==count && !std::memcmp(model,&expected,sizeof(expected)));
        for(unsigned i=0;i<count;++i){const auto* expectedRecord=reader.take(720);LG_CHECK(expectedRecord);RF455LegacyPart record;std::memcpy(record.bytes,expectedRecord,720);
            for(unsigned offset:offsets){const auto size=reader.number();void* p=lgGet<void*>(array[i].bytes,offset);
                if(size==0xffffffff){LG_CHECK(!p);continue;}const auto* payload=reader.take(size);LG_CHECK(reader.ok && p && memory.live.count(p)==1 && memory.live[p]==size && (!size || !std::memcmp(p,payload,size)));lgPut(record.bytes,offset,p);
            }
            LG_CHECK(!std::memcmp(array+i,&record,sizeof(record)));++parts;
        }
        RF455_DeleteLegacyModel(model,&ops);LG_CHECK(memory.live.empty() && !memory.bad);++files;
    }
    LG_CHECK(reader.ok && reader.at==bytes.size() && files==17 && parts==459 && !compactInput.empty());return 0;
}
int errors(const std::vector<unsigned char>& input){
    Memory memory;auto ops=memory.ops();RF455LegacyModel* output=reinterpret_cast<RF455LegacyModel*>(0x1234);std::size_t consumed=0x5678;
    SYSTEM_INFO info={};GetSystemInfo(&info);LG_CHECK(input.size()<info.dwPageSize);auto* page=static_cast<unsigned char*>(VirtualAlloc(nullptr,2*info.dwPageSize,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE));LG_CHECK(page);DWORD old=0;LG_CHECK(VirtualProtect(page+info.dwPageSize,info.dwPageSize,PAGE_NOACCESS,&old));
    for(std::size_t size=0;size<input.size();++size){auto* prefix=page+info.dwPageSize-size;if(size)std::memcpy(prefix,input.data(),size);
        LG_CHECK(RF455_ReadLegacyModel(prefix,size,&ops,&output,&consumed)==RF_LEGACY_FORMAT && output==reinterpret_cast<RF455LegacyModel*>(0x1234) && consumed==0x5678 && memory.live.empty() && !memory.bad);++guardedPrefixes;
    }
    LG_CHECK(VirtualFree(page,0,MEM_RELEASE));memory.calls=0;output=nullptr;LG_CHECK(RF455_ReadLegacyModel(input.data(),input.size(),&ops,&output,&consumed)==RF_LEGACY_OK);const auto allocations=memory.calls;RF455_DeleteLegacyModel(output,&ops);
    for(unsigned fail=1;fail<=allocations;++fail){memory.calls=0;memory.fail=fail;output=reinterpret_cast<RF455LegacyModel*>(0x1234);consumed=0x5678;LG_CHECK(RF455_ReadLegacyModel(input.data(),input.size(),&ops,&output,&consumed)==RF_LEGACY_MEMORY && output==reinterpret_cast<RF455LegacyModel*>(0x1234) && consumed==0x5678 && memory.live.empty() && !memory.bad);++allocationFailures;}
    memory.fail=0;auto bad=input;const unsigned compactOffset=2+693+28+176+4+200;lgPut(bad.data(),compactOffset+4,5u);LG_CHECK(RF455_ReadLegacyModel(bad.data(),bad.size(),&ops,&output,&consumed)==RF_LEGACY_INFLUENCES && memory.live.empty());bad=input;lgPut(bad.data(),compactOffset+8,2u);LG_CHECK(RF455_ReadLegacyModel(bad.data(),bad.size(),&ops,&output,&consumed)==RF_LEGACY_NAME_INDEX && memory.live.empty());
    bad=input;lgPut<unsigned>(bad.data(),2+693+28+176,0xffffffff);LG_CHECK(RF455_ReadLegacyModel(bad.data(),bad.size(),&ops,&output,&consumed)==RF_LEGACY_FORMAT && memory.live.empty());
    LG_CHECK(RF455_ReadLegacyModel(nullptr,1,&ops,&output,&consumed)==RF_LEGACY_ARGUMENT && RF455_ReadLegacyModel(input.data(),input.size(),&ops,nullptr,&consumed)==RF_LEGACY_ARGUMENT);
    bad=input;bad.push_back(17);bad.push_back(19);output=nullptr;LG_CHECK(RF455_ReadLegacyModel(bad.data(),bad.size(),&ops,&output,&consumed)==RF_LEGACY_OK && consumed==input.size());RF455_DeleteLegacyModel(output,&ops);LG_CHECK(memory.live.empty() && !memory.bad);return 0;
}
int weights(const std::vector<unsigned char>& input){
    unsigned initial=0;LG_CHECK(!_controlfp_s(&initial,0,0));
    for(unsigned precision:{_PC_24,_PC_53,_PC_64})for(unsigned rounding:{_RC_NEAR,_RC_DOWN,_RC_UP,_RC_CHOP}){
        unsigned before=0,after=0;LG_CHECK(!_controlfp_s(&before,precision|rounding,_MCW_PC|_MCW_RC));Memory memory;auto ops=memory.ops();RF455LegacyModel* model=nullptr;std::size_t consumed=0;
        LG_CHECK(RF455_ReadLegacyModel(input.data(),input.size(),&ops,&model,&consumed)==RF_LEGACY_OK);auto* p=lgGet<RF455LegacyPart*>(model->bytes,4);auto* expanded=lgGet<unsigned char*>(p->bytes,704);
        const unsigned expected[]={0x3f800001,0x80000000,0x7fc00123,0xffc00001};for(unsigned i=0;i<4;++i)LG_CHECK(lgGet<unsigned>(expanded,408+4*i)==expected[i]);LG_CHECK(!_controlfp_s(&after,0,0) && before==after);RF455_DeleteLegacyModel(model,&ops);LG_CHECK(memory.live.empty());
    }
    unsigned ignored=0;LG_CHECK(!_controlfp_s(&ignored,initial,_MCW_PC|_MCW_RC));return 0;
}
int run(const char* workspace,const char* golden){std::vector<unsigned char> compact;LG_CHECK(lifetime()==0 && samples(workspace,golden,compact)==0 && errors(compact)==0 && weights(compact)==0);return 0;}
}
int main(int argc,char** argv){if(argc!=4)return 2;const int result=run(argv[1],argv[2]);FILE* f=std::fopen(argv[3],"wb");if(!f)return 1;std::fprintf(f,"{\"status\":\"%s\",\"checks\":%u,\"files\":%u,\"parts\":%u,\"guarded_prefixes\":%u,\"allocation_failures\":%u}\n",result?"FAIL":"PASS",checks,files,parts,guardedPrefixes,allocationFailures);std::fclose(f);return result;}
