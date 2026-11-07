#include "client455_skill_force_items.h"
#include <cstdio>
#include <cstring>
#include <new>
#include <stdexcept>
#include <vector>

static void check(bool value,const char* text){if(!value)throw std::runtime_error(text);}
static std::vector<unsigned char> read(const char* name){
    FILE* f=std::fopen(name,"rb");check(f!=nullptr,"fixture open");
    check(std::fseek(f,0,SEEK_END)==0,"fixture size");long size=std::ftell(f);check(size>=0,"fixture length");
    std::rewind(f);std::vector<unsigned char> out(static_cast<std::size_t>(size));
    check(std::fread(out.data(),1,out.size(),f)==out.size(),"fixture read");std::fclose(f);return out;
}
static std::uint32_t word(const unsigned char* p){std::uint32_t v;std::memcpy(&v,p,4);return v;}
static std::uint32_t number(FILE* f){std::uint32_t n;check(std::fread(&n,4,1,f)==1,"oracle header");return n;}
static void whole(const RF455SkillForceData& data,const char* name){
    FILE* f=std::fopen(name,"rb");check(f!=nullptr,"whole table oracle");
    for(const auto& table:data.records()){
        check(number(f)==table.count&&number(f)==table.stride,"table count/stride");
        std::vector<unsigned char> expected(table.bytes.size());
        check(std::fread(expected.data(),1,expected.size(),f)==expected.size()&&expected==table.bytes,"independent all-row bytes");
    }
    check(std::fgetc(f)==EOF,"whole table oracle end");std::fclose(f);
}
struct Allocator {
    unsigned made=0,freed=0;
    static void* allocate(void* p,std::size_t size){auto& a=*static_cast<Allocator*>(p);check(size==620,"real clone extent");++a.made;return ::operator new(size);}
    void release(void* p){::operator delete(p);++freed;}
};
int main(){try{
    auto raw=read("base.edf"),matching=read("zh-tw.edf"),korea=read("ko-kr.edf"),russia=read("ru-ru.edf");
    RF455SkillForceData data;check(data.loadFiles("base.edf","zh-tw.edf"),"actual matching five-table base/localization");
    whole(data,"zh-tw.golden");
    RF455SkillForceData ko,ru;check(ko.loadBaseEdf(raw.data(),raw.size())&&!ko.localizeEdf(korea.data(),korea.size()),"real Korean count mismatch must fail");
    whole(ko,"ko-kr.golden");
    check(ru.loadBaseEdf(raw.data(),raw.size())&&!ru.localizeEdf(russia.data(),russia.size()),"real Russian count mismatch must fail");
    whole(ru,"ru-ru.golden");
    check(!data.get(4,0).data&&!data.get(255,0).data,"unsupported SF selectors");
    bool rejected=false;try{data.loadBaseEdf(raw.data(),raw.size());}catch(const std::logic_error&){rejected=true;}
    check(rejected,"unported reload lifetime must be explicit");whole(data,"zh-tw.golden");
    // A short envelope is a bounded failure,not failure parity with the target's
    // unchecked read/allocation domains.
    RF455SkillForceData invalid;check(!invalid.loadBaseEdf(raw.data(),288),"short envelope");
    RF455SourceItemManager manager;Allocator allocator;unsigned created=0;
    const unsigned types[]={1,0,2,3,5};
    for(unsigned tableNo=0;tableNo<5;++tableNo){
        const auto& table=data.records()[tableNo];const auto subtype=static_cast<std::uint8_t>(types[tableNo]);
        check(!data.get(subtype,table.count).data,"real lookup upper boundary");
        for(std::uint32_t index=0;index<table.count;++index){
            auto* item=manager.createSkillForce(data,subtype,index);check(item!=nullptr,"real SF factory");++created;
            const auto row=table.get(index);const auto& state=item->record();
            const auto serial=subtype==0?index:index|0xf0000000;
            const auto secondary=(subtype==0||subtype==2||subtype==3)?index:index|0xf0000000;
            check(state.item.serial==serial&&state.item.field8==secondary&&state.item.references==0&&state.item.kind==1&&
                  state.subtype==subtype&&state.level==((subtype==2||subtype==3)?1:0),"independent target ID/level rules");
            check(state.item.data16==static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(row.data))&&
                  item->tableIndex()==word(row.data)&&item->rawData().data==row.data&&
                  std::memcmp(item->name(),row.data+112,32)==0,"borrow real table/index/name");
            check(manager.itemIsKind(&item->header(),1)&&!manager.itemIsKind(&item->header(),0),"actual kind predicate");
            // Owned wrapper records call the real reconstructed manager host;
            // this tests087 with source SF payloads,not a recording callback.
            RF455BoardItemRecord origin={};origin.item=&item->header();RF455_RetainItem(*origin.item);
            auto* link=RF455_CloneBoardItemRecord(origin,0x45500010,&allocator,Allocator::allocate);
            check(link&&link->item==origin.item&&origin.item->references==2,"shared source SF payload");
            if(index&1){
                check(RF455_ReleaseBoardItemReference(origin,manager)&&link->item->references==1&&manager.size()==1,"origin release preserves link");
                check(RF455_ReleaseBoardItemReference(*link,manager)&&!link->item,"last link release");
            }else{
                check(RF455_ReleaseBoardItemReference(*link,manager)&&origin.item->references==1&&manager.size()==1,"link release preserves origin");
                check(RF455_ReleaseBoardItemReference(origin,manager)&&!origin.item,"last origin release");
            }
            check(manager.size()==0,"last owner erased concrete payload/cache entry");allocator.release(link);
        }
        check(!manager.createSkillForce(data,subtype,table.count)&&manager.size()==0,"factory lookup failure must not register");
    }
    check(created==1447&&allocator.made==created&&allocator.freed==created,"all real source payloads/lifetimes");
    auto* one=manager.createSkillForce(data,1,0);auto* two=manager.createSkillForce(data,1,0);
    check(one&&two&&one!=two&&one->header().serial==two->header().serial&&manager.size()==2,"manager does not deduplicate factory requests");
    manager.clear();check(manager.primaryCacheEmpty(),"actual manager clear");
    check(!manager.createSkillForce(data,4,0)&&!manager.createSkillForce(data,255,0)&&manager.size()==0,"unknown fresh SF subtype failure");
    RF455BoardItemRecord empty={};check(!RF455_ReleaseBoardItemReference(empty,manager),"real empty primary guard");
    FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"result");
    std::fprintf(out,"{\"status\":\"PASS\",\"real_tables\":5,\"real_SF_payloads\":%u,\"cloned_wrappers\":%u,"
        "\"concrete_primary_manager\":true,\"recording_host\":false,\"real_table_borrowing\":true,"
        "\"matching_localization\":\"zh-tw\",\"Korea_count_mismatch_table\":4,\"Russia_count_mismatch_table\":1,"
        "\"prefix_localization_writes\":true,\"actual_last_owner_erase\":true,\"duplicate_factory_requests\":true,"
        "\"source_factory_selector\":1,\"all_payload_factories\":false,\"ordinary_Linker_bound\":false,\"actual_Tutorial\":false}\n",created,allocator.made);
    std::fclose(out);return 0;
}catch(const std::exception& error){std::fprintf(stderr,"SkillForce items:%s\n",error.what());return 1;}}
