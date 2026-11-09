#include "client455_nuclear_wire.h"
#include <cstdio>
#include <cstring>
#include <stdexcept>

static unsigned checks=0;
static void check(bool value,const char* why){++checks;if(!value)throw std::runtime_error(why);}
static void same(const RF455NuclearWireMessage& value,const RF455NuclearWireMessage& old){
    bool matched=value.opcode==old.opcode&&value.result==old.result&&value.race==old.race&&value.index==old.index&&value.count==old.count&&value.ignoredList==old.ignoredList&&!std::memcmp(value.position.data(),old.position.data(),12);
    for(std::size_t i=0;i<9;++i)matched=matched&&value.entries[i].race==old.entries[i].race&&value.entries[i].index==old.entries[i].index&&!std::memcmp(value.entries[i].position.data(),old.entries[i].position.data(),12);
    check(matched,"failed read leaves all values unchanged");
}
int main(){try{
    unsigned char data[256]={};RF455NuclearWireMessage out;out.opcode=99;out.result=77;out.index=66;out.race=55;out.count=44;out.position={{7,8,9}};const auto original=out;
    const unsigned char opcodes[]={0,3,4,5,6,7,8,9,10};const std::size_t sizes[]={1,17,2,5,2,14,2,2,1};
    for(std::size_t i=0;i<sizeof(opcodes);++i){
        for(std::size_t n=0;n<sizes[i];++n){check(!RF455_ReadNuclearPayload(opcodes[i],data,n,out),"short prefix rejected");same(out,original);}
        check(!RF455_ReadNuclearPayload(opcodes[i],nullptr,256,out),"null rejected");same(out,original);
    }
    for(unsigned op=0;op<256;++op){
        bool known=false;for(auto value:opcodes)known|=op==value;
        if(known)continue;check(!RF455_ReadNuclearPayload(static_cast<unsigned char>(op),data,256,out),"unknown opcode rejected");same(out,original);
    }
    for(unsigned value=0;value<256;++value){data[0]=static_cast<unsigned char>(value);check(RF455_ReadNuclearPayload(0,data,1,out)&&out.result==value&&out.opcode==0,"all result BYTE values preserved");}
    const unsigned bits[3]={0x80000000,0x7fc12345,0x7f800000};std::memset(data,0xcc,sizeof(data));std::memcpy(data+4,bits,12);data[16]=254;
    check(RF455_ReadNuclearPayload(3,data,17,out)&&out.index==254&&!std::memcmp(out.position.data(),bits,12),"opcode3 ignores first DWORD/preserves position bits/index16");
    check(RF455_ReadNuclearPayload(3,data,256,out)&&!std::memcmp(out.position.data(),bits,12),"unused tail accepted");
    data[0]=251;data[1]=252;data[4]=253;
    check(RF455_ReadNuclearPayload(5,data,5,out)&&out.race==251&&out.index==253,"opcode5 index is BYTE4,not bytes1to3");
    for(auto op:std::array<unsigned char,4>{{4,6,8,9}})check(RF455_ReadNuclearPayload(op,data,2,out)&&out.race==251&&out.index==252,"race/index BYTE pairs");
    std::memcpy(data+2,bits,12);check(RF455_ReadNuclearPayload(7,data,14,out)&&out.race==251&&out.index==252&&!std::memcmp(out.position.data(),bits,12),"opcode7 packed position2");
    for(unsigned count=0;count<256;++count){
        std::memset(data,0,sizeof(data));data[0]=static_cast<unsigned char>(count);
        if(count>9){check(RF455_ReadNuclearPayload(10,data,1,out)&&out.count==count&&out.ignoredList,"target oversized count ignores body ratherthan requiring rows");continue;}
        for(unsigned i=0;i<count;++i){auto* row=data+1+14*i;row[0]=static_cast<unsigned char>(i+200);row[1]=static_cast<unsigned char>(255-i);std::memcpy(row+2,bits,12);}
        const std::size_t end=1+14*count;
        for(std::size_t n=1;n<end;++n){const auto before=out;check(!RF455_ReadNuclearPayload(10,data,n,out),"list prefix rejected");same(out,before);}
        check(RF455_ReadNuclearPayload(10,data,end,out)&&out.count==count&&!out.ignoredList,"full list count0to9 accepted");
        for(unsigned i=0;i<count;++i)check(out.entries[i].race==i+200&&out.entries[i].index==255-i&&!std::memcmp(out.entries[i].position.data(),bits,12),"packed14 list rows andfloat bits preserved");
    }
    FILE* f=nullptr;if(fopen_s(&f,"result.json","wb")||!f)throw std::runtime_error("result file");std::fprintf(f,"{\"status\":\"PASS\",\"checks\":%u,\"opcodes\":9,\"all_result_bytes\":256,\"all_list_counts\":256,\"list_max_rows\":9,\"short_prefixes\":true,\"null_and_unknown\":true,\"float_bits_preserved\":true,\"packed14\":true,\"output_unchanged_on_failure\":true,\"normal_receiver_integrated\":false,\"full_client\":false}\n",checks);std::fclose(f);std::printf("PASS:%u targeted nuclear wire checks\n",checks);return 0;
}catch(const std::exception& error){std::fprintf(stderr,"wire:%s checks=%u\n",error.what(),checks);return 1;}}
