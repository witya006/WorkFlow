#include "client455_item_payloads.h"
#include <cstdio>
#include <cstring>
#include <new>
#include <stdexcept>

static void check(bool value,const char* text){if(!value)throw std::runtime_error(text);}
static std::vector<unsigned char> read(const char* name){
    FILE* f=std::fopen(name,"rb");check(f!=nullptr,"fixture open");
    check(std::fseek(f,0,SEEK_END)==0,"fixture size");long n=std::ftell(f);check(n>=0,"fixture length");
    std::rewind(f);std::vector<unsigned char> out(static_cast<std::size_t>(n));
    check(std::fread(out.data(),1,out.size(),f)==out.size(),"fixture read");std::fclose(f);return out;
}
struct Oracle {
    std::vector<unsigned char> bytes;std::size_t at=0;
    explicit Oracle(const char* file):bytes(read(file)){}
    const unsigned char* take(std::size_t n){check(n<=bytes.size()-at,"oracle extent");auto p=bytes.data()+at;at+=n;return p;}
    std::uint32_t word(){std::uint32_t n;std::memcpy(&n,take(4),4);return n;}
    std::uint64_t quad(){std::uint64_t n;std::memcpy(&n,take(8),8);return n;}
    void end(){check(at==bytes.size(),"oracle trailing bytes");}
};
template<std::size_t N> static void tables(Oracle& oracle,const std::array<RF455RawItemTable,N>& rows){
    for(const auto& row:rows){
        check(oracle.word()==row.count&&oracle.word()==row.stride,"actual count/stride");
        check(std::memcmp(oracle.take(row.bytes.size()),row.bytes.data(),row.bytes.size())==0,"independent all-row oracle");
    }
}
static void items(const RF455ItemDataStore& data,const char* name){
    Oracle oracle(name);tables(oracle,data.itemTables());
    for(auto value:data.itemWorkStarts())check(oracle.word()==value,"work start");
    for(auto value:data.itemWorkCounts())check(oracle.word()==value,"work count");oracle.end();
}
static void descriptions(const RF455ItemDataStore& data,const char* name){
    Oracle oracle(name);
    for(const auto& group:data.itemDescriptions()){
        check(oracle.word()==group.size(),"description count");
        for(const auto& row:group){
            check(oracle.word()==row.index&&oracle.word()==row.code&&oracle.word()==row.bytes.size(),"description header");
            check(std::memcmp(oracle.take(row.bytes.size()),row.bytes.data(),row.bytes.size())==0,"description bytes");
        }
    }
    check(oracle.word()==data.dungeonDescriptions().size(),"dungeon count");
    for(const auto& row:data.dungeonDescriptions()){
        check(oracle.word()==row.index&&std::memcmp(oracle.take(64),row.name.data(),64)==0&&oracle.word()==row.bytes.size(),"dungeon header");
        check(std::memcmp(oracle.take(row.bytes.size()),row.bytes.data(),row.bytes.size())==0,"dungeon bytes");
    }
    oracle.end();
}
struct Allocator {
    unsigned made=0,freed=0;
    static void* allocate(void* p,std::size_t n){check(n==620,"clone extent");++static_cast<Allocator*>(p)->made;return ::operator new(n);}
    void release(void* p){::operator delete(p);++freed;}
};
int main(){try{
    auto root=read("item.edf"),flat=read("flat.edf"),quest=read("quest.edf"),character=read("character.edf");
    RF455ItemDataStore data;check(data.loadItemEdf(root.data(),root.size(),true),"actual segmented item load");items(data,"base.tables");
    RF455ItemDataStore generic;check(generic.loadItemEdf(flat.data(),flat.size(),false),"generated flat branch");items(generic,"base.tables");
    const char* locales[]={"zh-tw","ko-kr","ru-ru"};
    const unsigned expectedDescriptions[]={68084,63821,52255},expectedDungeons[]={100,100,0};
    const std::size_t expectedConsumed[]={9460191,9972550,9191029};
    for(unsigned i=0;i<3;++i){
        char name[80];std::snprintf(name,sizeof(name),"nd-%s.edf",locales[i]);auto nd=read(name);
        RF455ItemDataStore localized;check(localized.loadItemEdf(root.data(),root.size(),true)&&localized.localizeItemEdf(nd.data(),nd.size()),"actual NDItem profile");
        std::snprintf(name,sizeof(name),"%s.tables",locales[i]);items(localized,name);
        std::snprintf(name,sizeof(name),"%s.descriptions",locales[i]);descriptions(localized,name);
        std::size_t count=0;for(const auto& group:localized.itemDescriptions())count+=group.size();
        check(count==expectedDescriptions[i]&&localized.dungeonDescriptions().size()==expectedDungeons[i]&&localized.localizedBytesConsumed()==expectedConsumed[i],"real ND counts/tail");
    }
    auto matching=read("nd-zh-tw.edf");check(data.localizeItemEdf(matching.data(),matching.size()),"installed Taiwan localization");
    check(data.loadQuestEdf(quest.data(),quest.size())&&data.loadCharacterEdf(character.data(),character.size()),"actual Quest/Character readers");
    Oracle q("quest.tables"),c("character.tables");tables(q,data.questTables());q.end();tables(c,data.characterTables());c.end();
    RF455SourceItemManager manager;Allocator allocator;Oracle cases("cases.bin");
    check(std::memcmp(cases.take(4),"IP89",4)==0,"case magic");const auto count=cases.word();unsigned successful=0,bounded=0;
    for(unsigned i=0;i<count;++i){
        const auto selector=cases.word(),type=cases.word(),index=cases.word(),kind=cases.word(),size=cases.word(),tableIndex=cases.word(),isQuest=cases.word(),status=cases.word();
        const auto* mask=cases.take(size);const auto* expected=cases.take(size);const auto* name=cases.take(64);
        RF455ManagedItem* raw=nullptr;bool outside=false;
        try{raw=manager.createPayload(data,static_cast<std::uint8_t>(selector),static_cast<std::uint8_t>(type),index);}catch(const std::out_of_range&){outside=true;}
        if(status){check(outside&&!raw&&manager.size()==0,"explicit unsupported metadata owner bound");++bounded;continue;}
        check(!outside&&raw&&manager.size()==1,"concrete fresh payload factory");auto* item=dynamic_cast<RF455BasicItem*>(raw);check(item!=nullptr,"basic concrete payload");
        const auto bytes=item->recordBytes();check(bytes.size==size,"record size");
        for(unsigned n=0;n<size;++n)if(mask[n]){
            if(bytes.data[n]!=expected[n]){std::fprintf(stderr,"case %u selector %u type %u row %u byte %u actual %u expected %u\n",i,selector,type,index,n,bytes.data[n],expected[n]);check(false,"independent constructor/create byte oracle");}
        }
        const auto row=isQuest?data.getQuest(index):data.getItem(type,index);
        check(item->tableIndex()==tableIndex&&item->rawData().data==row.data&&item->header().data16==static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(row.data)),"real borrowed record/index");
        check(manager.itemIsKind(&item->header(),static_cast<std::uint8_t>(kind)),"actual manager kind");
        if(isQuest){bool refused=false;try{item->name();}catch(const std::logic_error&){refused=true;}check(refused,"missing Quest sentence provider must be explicit");}
        else check(std::memcmp(item->name(),name,64)==0,"actual localized item name");
        RF455BoardItemRecord origin={};origin.item=&item->header();RF455_RetainItem(*origin.item);
        auto* link=RF455_CloneBoardItemRecord(origin,0x45500010,&allocator,Allocator::allocate);check(link&&link->item->references==2,"shared real payload clone");
        if(i&1){check(RF455_ReleaseBoardItemReference(origin,manager)&&link->item->references==1,"origin releases first");check(RF455_ReleaseBoardItemReference(*link,manager)&&!link->item,"link releases last");}
        else{check(RF455_ReleaseBoardItemReference(*link,manager)&&origin.item->references==1,"link releases first");check(RF455_ReleaseBoardItemReference(origin,manager)&&!origin.item,"origin releases last");}
        check(manager.size()==0,"concrete last-owner erase");allocator.release(link);++successful;
    }
    cases.end();check(successful+bounded==count&&allocator.made==successful&&allocator.freed==successful,"all selected fresh payload lifetimes");
    Oracle levels("levels.bin");check(std::memcmp(levels.take(4),"AL89",4)==0,"level magic");const auto levelCount=levels.word();
    for(unsigned i=0;i<levelCount;++i){const auto kind=levels.word();const auto xp=levels.quad();const auto index=levels.word();const auto row=data.animusLevel(static_cast<std::uint8_t>(kind),xp);
        check(row.data==(index==0xffffffff?nullptr:data.characterTables()[6].get(index).data),"real Animus XP threshold/boundary");}levels.end();
    for(unsigned kind=0;kind<47;++kind){check(!data.getItem(kind,data.itemTables()[kind].count).data,"item index boundary");}
    check(!data.getItem(47,0).data&&!data.getItem(255,0).data&&!data.getItem(256,0).data,"full DWORD type bounds");
    for(unsigned selector: {0,2,3,4})check(!manager.createPayload(data,static_cast<std::uint8_t>(selector),47,0)&&manager.size()==0,"failed fresh factory not registered");
    for(unsigned index: {2895u,0xf0000006u,0xffffffffu})check(!manager.createPayload(data,5,17,index)&&manager.size()==0,"Quest special/ordinary upper bounds");
    bool refused=false;try{manager.createPayload(data,1,1,0);}catch(const std::logic_error&){refused=true;}check(refused&&manager.size()==0,"SF requires real data owner");
    RF455SkillForceData sf;check(sf.loadFiles("base.edf","zh-tw.edf"),"real SF owner");
    auto* skill=manager.createPayload(data,1,1,0,&sf);check(skill&&dynamic_cast<RF455SkillForceItem*>(skill)&&manager.size()==1,"generic factory SF dispatch");
    RF455BoardItemRecord sfOrigin={};sfOrigin.item=&skill->header();RF455_RetainItem(*sfOrigin.item);check(RF455_ReleaseBoardItemReference(sfOrigin,manager)&&manager.size()==0,"generic SF last-owner erase");
    auto unknown=read("unknown.edf"),bad=read("bad-offset.edf");RF455ItemDataStore unknownData,badData,shortData;
    check(unknownData.loadItemEdf(unknown.data(),unknown.size(),true)&&unknownData.itemTables()[0].bytes.empty()&&unknownData.itemTables()[1].bytes==generic.itemTables()[1].bytes,"unknown F12E is skipped");
    check(!badData.loadItemEdf(bad.data(),bad.size(),true)&&!shortData.loadItemEdf(root.data(),288,true),"bounded malformed section/envelope failures");
    refused=false;try{data.loadItemEdf(root.data(),root.size(),true);}catch(const std::logic_error&){refused=true;}check(refused,"unported item reload explicit");
    refused=false;try{data.localizeItemEdf(matching.data(),matching.size());}catch(const std::logic_error&){refused=true;}check(refused,"unported relocalize lifetime explicit");
    FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"result output");
    std::fprintf(out,"{\"status\":\"PASS\",\"real_item_rows\":76049,\"real_item_tables\":47,\"real_quest_frames\":12,\"real_character_frames\":7,\"real_quest_rows\":2895,\"fresh_factory_cases\":%u,\"fresh_payloads\":%u,\"bounded_unsafe_cases\":%u,\"cloned_wrappers\":%u,\"Animus_level_cases\":%u,\"NDItem_locales\":3,\"concrete_primary_manager\":true,\"whole_table_byte_oracles\":true,\"source_SF_dispatch\":true,\"ordinary_game_binding\":false,\"Quest_sentence_expansion\":false,\"full_payload_gameplay\":false,\"full_client\":false}\n",count,successful,bounded,allocator.made,levelCount);
    std::fclose(out);return 0;
}catch(const std::exception& error){std::fprintf(stderr,"Item payloads:%s\n",error.what());return 1;}}
