#include "client455_item_payloads.h"
#include "client455_language.h"
#include <cstring>
#include <new>
#include <stdexcept>

namespace {
std::uint32_t u32(const unsigned char* p){std::uint32_t v;std::memcpy(&v,p,4);return v;}
std::uint64_t u64(const unsigned char* p){std::uint64_t v;std::memcpy(&v,p,8);return v;}
void put(unsigned char* p,std::size_t at,std::uint32_t v){std::memcpy(p+at,&v,4);}
struct Cursor {
    const unsigned char* data;std::size_t size,at=0;
    bool read(void* out,std::size_t n){if(n>size-at)return false;if(n)std::memcpy(out,data+at,n);at+=n;return true;}
    bool word(std::uint32_t& n){return read(&n,4);}
    bool skip(std::size_t n){if(n>size-at)return false;at+=n;return true;}
    bool table(RF455RawItemTable& table){
        if(!word(table.count)||!word(table.stride))return false;
        if(!table.count||!table.stride)return true; // Target leaves an empty table;caller ignores Load return.
        if(table.count>(size-at)/table.stride)return false;
        const auto n=std::size_t(table.count)*table.stride;
        table.bytes.assign(data+at,data+at+n);at+=n;return true;
    }
};
int tableForTag(unsigned tag){if(tag>=0xf100&&tag<=0xf12d)return int(tag-0xf100);return tag==0xf12f?46:-1;}
bool readWorkArray455(Cursor& c,std::array<std::uint32_t,47>& out){return c.read(out.data(),47*4);}
std::uint32_t field(RF455ItemDataSpan row,std::size_t at){
    if(!row.data||at>row.size||row.size-at<4)throw std::out_of_range("455 item metadata field outside row");
    return u32(row.data+at);
}
unsigned metadataByte455(RF455ItemDataSpan row,std::size_t at){
    if(!row.data||at>=row.size)throw std::out_of_range("455 item metadata byte outside row");return row.data[at];
}
bool equipment(RF455ItemDataSpan row){const auto kind=metadataByte455(row,88);return kind>=1&&kind<=10;}
bool split(RF455ItemDataSpan row){switch(metadataByte455(row,88)){
    case 13:case 16:case 17:case 20:case 22:case 23:case 26:case 30:case 31:case 32:case 34:case 35:return true;
    default:return false;}}
std::uint32_t maxDurability(RF455ItemDataSpan row){
    const auto kind=metadataByte455(row,88);
    if(equipment(row)||kind==27||kind==19)return field(row,168);
    if(kind==15)return field(row,152);
    if(kind==11||kind==33)return field(row,160);
    if(kind==42||kind==43)return field(row,220);
    if(kind==34)return field(row,172);return 0;
}
}
RF455ItemDataSpan RF455RawItemTable::get(std::uint32_t index)const{
    if(index>=count||!stride||bytes.empty())return {};
    return {bytes.data()+std::size_t(stride)*index,stride};
}
bool RF455ItemDataStore::loadItemEdf(const void* raw,std::size_t size,bool segmented){
    if(itemLoaded)throw std::logic_error("455 item reload/duplicate-owner lifetime remains unported");
    std::vector<unsigned char> plain;if(!RF455_DecodeEdf(raw,size,plain))return false;
    std::array<RF455RawItemTable,47> next;std::array<std::uint32_t,47> starts{},counts{};
    Cursor c{plain.data(),plain.size()};
    if(segmented){
        std::size_t processed=0;std::array<bool,47> seen{};bool directory=false;
        while(processed<plain.size()){
            std::uint16_t tag=0;std::uint32_t bytes=0,offset=0;
            if(!c.read(&tag,2)||!c.word(bytes)||!c.word(offset))return false;
            if(bytes>plain.size()-c.at)return false;
            Cursor section{plain.data()+c.at,bytes};const int number=tableForTag(tag);
            if(number>=0){
                if(seen[number])throw std::logic_error("455 duplicate table old-pointer lifetime is not restored");
                if(!section.table(next[number]))return false;seen[number]=true;
            }else if(tag==0xf130){
                if(directory)throw std::logic_error("455 duplicate item directory lifetime is not restored");
                if(!readWorkArray455(section,starts)||!readWorkArray455(section,counts))return false;directory=true;
            }
            const auto end=std::uint64_t(offset)+bytes+10;
            if(end>plain.size()||std::uint64_t(processed)+bytes+10>plain.size())return false;
            c.at=static_cast<std::size_t>(end);processed+=std::size_t(bytes)+10;
        }
    }else{
        for(auto& table:next)if(!c.table(table))return false;
        if(!readWorkArray455(c,starts)||!readWorkArray455(c,counts))return false;
    }
    items=std::move(next);workStarts=starts;workCounts=counts;itemLoaded=true;return true;
}
bool RF455ItemDataStore::localizeItemEdf(const void* raw,std::size_t size){
    if(itemLocalized)throw std::logic_error("455 item relocalization pointer lifetime remains unported");
    if(!itemLoaded)return false;std::vector<unsigned char> plain;if(!RF455_DecodeEdf(raw,size,plain))return false;
    Cursor c{plain.data(),plain.size()};
    for(unsigned kind=0;kind<47;++kind){
        if(kind==44||kind==45)continue;
        std::uint32_t count=0;if(!c.word(count))return false;
        for(std::uint32_t i=0;i<count&&i<items[kind].count;++i){
            if(items[kind].stride<72)return false;
            if(!c.read(items[kind].bytes.data()+std::size_t(i)*items[kind].stride+8,64))return false;
        }
        if(count>items[kind].count){const auto extra=count-items[kind].count;
            if(extra>(c.size-c.at)/64||!c.skip(std::size_t(extra)*64))return false;}
    }
    for(auto& group:descriptions){
        std::uint32_t count=0;if(!c.word(count)||count>(c.size-c.at)/12)return false;
        std::vector<RF455ItemDescription> next;next.reserve(count);
        for(std::uint32_t i=0;i<count;++i){
            RF455ItemDescription value;std::uint32_t n=0;
            if(!c.word(value.index)||!c.word(value.code)||!c.word(n)||n>c.size-c.at)return false;
            value.bytes.assign(c.data+c.at,c.data+c.at+n);c.at+=n;next.push_back(std::move(value));
        }
        group=std::move(next);
    }
    std::uint32_t count=0;if(!c.word(count)||count>(c.size-c.at)/72)return false;
    std::vector<RF455DungeonDescription> next;next.reserve(count);
    for(std::uint32_t i=0;i<count;++i){
        RF455DungeonDescription value;std::uint32_t n=0;
        if(!c.word(value.index)||!c.read(value.name.data(),64)||!c.word(n)||n>c.size-c.at)return false;
        value.bytes.assign(c.data+c.at,c.data+c.at+n);c.at+=n;next.push_back(std::move(value));
    }
    // Zero dungeons makes5FFC10 return0,which its outer caller ignores.
    dungeons=std::move(next);localizationConsumed=c.at;itemLocalized=true;return true;
}
bool RF455ItemDataStore::loadQuestEdf(const void* raw,std::size_t size){
    if(questLoaded)throw std::logic_error("455 Quest reload lifetime remains unported");
    std::vector<unsigned char> plain;if(!RF455_DecodeEdf(raw,size,plain))return false;
    Cursor c{plain.data(),plain.size()};std::array<RF455RawItemTable,12> next;
    for(auto& table:next)if(!c.table(table))return false;
    quests=std::move(next);questLoaded=true;return true;
}
bool RF455ItemDataStore::loadCharacterEdf(const void* raw,std::size_t size){
    if(characterLoaded)throw std::logic_error("455 Character reload lifetime remains unported");
    std::vector<unsigned char> plain;if(!RF455_DecodeEdf(raw,size,plain))return false;
    Cursor c{plain.data(),plain.size()};std::array<RF455RawItemTable,7> next;
    for(auto& table:next)if(!c.table(table))return false;
    character=std::move(next);characterLoaded=true;return true;
}
bool RF455ItemDataStore::localizeCharacterEdf(const void* raw,std::size_t size,unsigned codepage){
    if(characterLocalized)throw std::logic_error("455 Character relocalization lifetime remains unported");
    if(!characterLoaded)return false;
    std::vector<unsigned char> plain;if(!RF455_DecodeEdf(raw,size,plain))return false;Cursor c{plain.data(),plain.size()};
    RF455LanguagePack language;language.codepage=codepage;
    if(plain.size()<8)return false;std::uint32_t declared=0,ignored=0;
    for(unsigned group=0;group<4;++group){c.word(declared);c.word(ignored);
        auto& table=character[group];const unsigned minimum[4]={1532,97,40,44};if(table.count&&table.stride<minimum[group])return false;
        for(std::uint32_t i=0;i<table.count;++i){auto* row=table.bytes.data()+std::size_t(i)*table.stride;
            // 5FC260 ignores failed Read returns. A short read leaves both the
            // destination and the cursor unchanged,including subsequent rows.
            if(group==0){c.read(row+112,32);c.read(row+508,1024);}
            else if(group==1){for(unsigned j=0;j<3;++j)c.read(row+1+32*j,32);}
            else if(group==2){c.read(row+8,32);
                if(row[39]){row[39]=0;if(language.isLead(reinterpret_cast<char*>(row+8),30))row[38]=0;}}
            else c.read(row+12,32);
        }
        if(declared>table.count&&group<3){const std::size_t extra=declared-table.count;
            // The second section deliberately skips32,not96,per extra row.
            const std::size_t width=group==0?1056:32;if(extra>(c.size-c.at)/width||!c.skip(extra*width))return false;}
    }
    characterLocalized=true;return true;
}
RF455ItemDataSpan RF455ItemDataStore::classByCode(const char* code)const{
    if(!code)return {};
    for(std::uint32_t i=0;i<character[0].count;++i){auto row=character[0].get(i);
        if(row.size<44)throw std::out_of_range("455 class code outside row");
        if(std::memchr(row.data+12,0,32)&&!std::strcmp(reinterpret_cast<const char*>(row.data+12),code))return row;}
    return {};
}
RF455ItemDataSpan RF455ItemDataStore::classByIndex(std::uint32_t index)const{
    for(std::uint32_t i=0;i<character[0].count;++i){auto row=character[0].get(i);
        if(row.size<8)throw std::out_of_range("455 class index outside row");if(u32(row.data+4)==index)return row;}
    return {};
}
RF455ItemDataSpan RF455ItemDataStore::getItem(std::uint32_t kind,std::uint32_t index)const{return kind<47?items[kind].get(index):RF455ItemDataSpan{};}
RF455ItemDataSpan RF455ItemDataStore::getItemExtent(std::uint32_t kind,std::uint32_t index)const{
    auto row=getItem(kind,index);if(!row.data)return {};
    return {row.data,items[kind].bytes.size()-std::size_t(index)*items[kind].stride};
}
RF455ItemDataSpan RF455ItemDataStore::getQuest(std::uint32_t index)const{
    if(index>=0xf0000000){const bool first=index<0xf0000003;index=index-(first?0xf0000000:0xf0000003)+quests[7].count-(first?9:3);}
    return quests[7].get(index);
}
RF455ItemDataSpan RF455ItemDataStore::animusLevel(std::uint8_t type,std::uint64_t experience)const{
    const auto start=81u*type;
    for(unsigned i=start;i<start+81;++i){const auto row=character[6].get(i);
        if(row.data){if(row.size<9)throw std::out_of_range("455 Animus experience row too short");if(experience<u64(row.data+1))return row;}}
    return experience?character[6].get(start+80):RF455ItemDataSpan{};
}
RF455BasicItem::RF455BasicItem(std::uint8_t kind):payloadKind(kind){
    stateSize=kind==2?136:kind==3?192:kind==4?100:kind==5?116:200;
    state.reset(new unsigned char[stateSize]);new(state.get()) RF455ItemHeader;
    RF455_InitializeItemHeader(header(),0x45500000|kind);header().kind=kind;auto* p=state.get();
    if(kind==0){
        p[92]=1;for(unsigned n:{96,104,108,188})put(p,n,0);p[112]=p[113]=p[184]=p[192]=0;
        std::memset(p+116,0,28);std::memset(p+144,0,32);put(p,148,0x3f800000);p[157]=255;
    }else if(kind==2){for(unsigned n:{92,96,104,108,112,116,124,128})put(p,n,0);}
    else if(kind==3||kind==4){
        put(p,92,0);put(p,96,0);
        if(kind==3){std::memset(p+100,0,64);p[164]=0;p[165]=p[166]=255;for(unsigned n:{168,172,176,180})put(p,n,0);}
    }else if(kind==5){p[92]=p[93]=255;std::memset(p+96,0,12);put(p,108,0);}
}
RF455ItemHeader& RF455BasicItem::header(){return *reinterpret_cast<RF455ItemHeader*>(state.get());}
void RF455BasicItem::SetUpgradeLevel455(std::uint8_t value){
    if(payloadKind!=0||stateSize!=200)throw std::logic_error("455 upgrade setter requires normal item payload");
    state[113]=value; //462170: one BYTE write at71h,no clamp or callbacks.
}
bool RF455BasicItem::create(const RF455ItemDataStore& source,std::uint8_t type,std::uint32_t index){
    if(payloadKind==2){
        // Fresh464550 calls SetExperience while base data16 is null:virtual
        // GetDTIndex returnsFFFFFFFF,whose BYTE selects group255 in5FA940.
        const auto level=source.animusLevel(255,0);put(state.get(),92,static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(level.data)));
    }
    data=payloadKind==5?source.getQuest(index):source.getItem(type,index);
    metadata=payloadKind==5?data:source.getItemExtent(type,index);
    header().data16=static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(data.data));
    if(payloadKind==5){
        if(!data.data)return false;state[93]=type;header().serial=header().field8=index|0xf0000000;return true;
    }
    header().serial=header().field8=index|(std::uint32_t(type)<<24)|0xf0000000;
    if(!data.data)return false;
    if(payloadKind==3||payloadKind==4)put(state.get(),92,maxDurability(metadata));
    if(payloadKind==0){
        if(!split(metadata)){const auto maximum=maxDurability(metadata);put(state.get(),96,maximum);put(state.get(),104,maximum);put(state.get(),108,0);}
        if(equipment(metadata))state[112]=static_cast<unsigned char>(metadataByte455(metadata,160));
    }
    return true;
}
std::uint32_t RF455BasicItem::tableIndex()const{return data.data?field(data,0):0xffffffff;}
const char* RF455BasicItem::name()const{
    if(!data.data)return nullptr;
    if(payloadKind==5)throw std::logic_error("455 Quest sentence expansion is not restored");
    if(data.size<72)throw std::out_of_range("455 item name outside row");return reinterpret_cast<const char*>(data.data+8);
}
RF455ManagedItem* RF455SourceItemManager::createPayload(const RF455ItemDataStore& data,std::uint8_t selector,std::uint8_t type,std::uint32_t index,const RF455SkillForceData* sf){
    if(selector==1){if(!sf)throw std::logic_error("455 SF factory requires its real data owner");return createSkillForce(*sf,type,index);}
    const auto kind=static_cast<std::uint8_t>(selector>=2&&selector<=5?selector:0);
    auto item=std::unique_ptr<RF455BasicItem>(new RF455BasicItem(kind));
    if(!item->create(data,type,index))return nullptr;
    auto* result=item.get();primary.push_back(std::move(item));return result;
}
