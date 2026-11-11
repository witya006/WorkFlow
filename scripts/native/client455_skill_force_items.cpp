#include "client455_skill_force_items.h"
#include "client455_language.h"
#include <cstdio>
#include <cstring>
#include <stdexcept>

namespace {
std::uint32_t u32(const unsigned char* p){std::uint32_t v;std::memcpy(&v,p,4);return v;}
int tableNumber(std::uint8_t subtype){switch(subtype){case 1:return 0;case 0:return 1;case 2:return 2;case 3:return 3;case 5:return 4;default:return -1;}}
bool read(const char* name,std::vector<unsigned char>& out){
    FILE* file=std::fopen(name,"rb");if(!file)return false;
    bool ok=std::fseek(file,0,SEEK_END)==0;long length=ok?std::ftell(file):-1;
    ok=ok&&length>=0&&std::fseek(file,0,SEEK_SET)==0;
    if(ok){out.resize(static_cast<std::size_t>(length));ok=out.empty()||std::fread(out.data(),1,out.size(),file)==out.size();}
    std::fclose(file);return ok;
}
}
RF455ItemDataSpan RF455SkillForceTable::get(std::uint32_t index)const{
    if(index>=count)return {};
    return {bytes.data()+std::size_t(stride)*index,stride};
}
bool RF455SkillForceData::loadBaseEdf(const void* raw,std::size_t size){
    // Target reload overwrites raw table pointers without freeing old owners.
    // Reject that unported lifetime domain rather than invalidate live items.
    if(loaded)throw std::logic_error("455 SF table reload/old pointer lifetime is not restored");
    std::vector<unsigned char> plain;if(!RF455_DecodeEdf(raw,size,plain))return false;
    std::array<RF455SkillForceTable,5> next;std::size_t at=0;
    for(auto& table:next){
        if(plain.size()-at<8)return false;
        table.count=u32(plain.data()+at);table.stride=u32(plain.data()+at+4);at+=8;
        if(!table.count||table.stride<1036||table.count>(plain.size()-at)/table.stride)return false;
        const auto bytes=std::size_t(table.count)*table.stride;
        table.bytes.assign(plain.data()+at,plain.data()+at+bytes);at+=bytes;
    }
    // The target consumes five tables and does not reject a trailing payload.
    tables=std::move(next);loaded=true;return true;
}
bool RF455SkillForceData::localizeEdf(const void* raw,std::size_t size){
    if(!loaded)return false;
    std::vector<unsigned char> plain;if(!RF455_DecodeEdf(raw,size,plain))return false;
    std::size_t at=0;
    for(auto& table:tables){
        if(plain.size()-at<8)return false;
        const auto count=u32(plain.data()+at);at+=8; // Ignore second DWORD as5FB670.
        if(count!=table.count)return false;
        for(std::uint32_t i=0;i<count;++i){
            auto* row=table.bytes.data()+std::size_t(i)*table.stride;
            // Keep target read order and successful prefix writes. Unsafe short
            // reads are explicitly bounded here,not claimed as failure parity.
            if(plain.size()-at<32)return false;std::memcpy(row+112,plain.data()+at,32);at+=32;
            if(plain.size()-at<512)return false;std::memcpy(row+524,plain.data()+at,512);at+=512;
        }
    }
    return true;
}
bool RF455SkillForceData::loadFiles(const char* base,const char* localized){
    std::vector<unsigned char> body,names;
    if(!read(base,body)||!loadBaseEdf(body.data(),body.size()))return false;
    return read(localized,names)&&localizeEdf(names.data(),names.size());
}
RF455ItemDataSpan RF455SkillForceData::get(std::uint8_t subtype,std::uint32_t index)const{
    const int number=tableNumber(subtype);return number<0?RF455ItemDataSpan{}:tables[number].get(index);
}
namespace {
constexpr unsigned firstEffect = 144;

bool hasAttackCategory(RF455ItemDataSpan row) {
    constexpr unsigned effectStride = 40;
    constexpr unsigned effectCount = 7;
    if (row.size <= firstEffect + (effectCount - 1) * effectStride) return false;

    const auto* effects = row.data + firstEffect;
    for (unsigned i = 0; i < effectCount; ++i) {
        const auto category = effects[i * effectStride];
        if (category == 0 || category == 4) return true;
    }
    return false;
}
}

bool RF455SkillForceData::hasAttackEffect(std::uint8_t subtype, std::uint32_t index) const {
    return hasAttackCategory(get(subtype, index));
}

bool RF455SkillForceData::usesMonsterAttackClip(std::uint8_t subtype, std::uint32_t index,
                                              std::uint8_t level) const {
    const auto row = get(subtype, index);
    if (!hasAttackCategory(row)) return false;
    const auto* effects = row.data + firstEffect;
    const auto effectiveLevel = subtype == 2 ? 1 : level > 7 ? 7 : level;
    return effects[0] == 0xff || effects[effectiveLevel] != 4;
}
RF455SkillForceItem::RF455SkillForceItem(){
    // An owner token,never a callable address from the input binary.
    RF455_InitializeItemHeader(state.item,0x45500001);state.item.kind=1;
    state.subtype=0;state.successCount=0;state.level=0;state.flag101=0;state.percent=0;
    state.iconBoard=nullptr;state.field112=0;state.field116=0;state.field120=0xffffffff;
    std::memset(state.bytes124,0,17);std::memset(state.bytes141,0,17);
}
bool RF455SkillForceItem::create(const RF455SkillForceData& source,std::uint8_t subtype,std::uint32_t index){
    // Fresh factory instance:462F50 clears counters/UI flags;iconBoard is null.
    // Recreate with an existing live icon board is a separate unfinished domain.
    state.successCount=0;state.level=0;state.percent=0;state.field112=0;state.field116=0;
    data=source.get(subtype,index);
    state.item.data16=static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(data.data));
    if(subtype==0){state.item.serial=index;state.item.field8=index;}
    else if(subtype==1||subtype==5){state.item.serial=index|0xf0000000;state.item.field8=index|0xf0000000;}
    else if(subtype==2||subtype==3){state.item.serial=index|0xf0000000;state.item.field8=index;state.level=1;}
    if(!data.data)return false;
    state.subtype=subtype;return true;
}
std::uint32_t RF455SkillForceItem::tableIndex()const{return data.data?u32(data.data):0xffffffff;}
const char* RF455SkillForceItem::name()const{return data.data?reinterpret_cast<const char*>(data.data+112):nullptr;}
std::uint8_t RF455SkillForceItem::EffectiveLevel455(bool baseOnly)const{
    if(state.subtype==2)return 1;
    if(baseOnly)return state.level;
    const auto value=std::uint8_t(state.level+state.flag101);return value>7?7:value;
}
extern void RF455_UpdateSkillIconLevel455(void*,std::uint8_t);
void RF455SkillForceItem::SetEquipmentLevel455(std::uint8_t value){state.flag101=value;if(state.iconBoard)RF455_UpdateSkillIconLevel455(state.iconBoard,EffectiveLevel455());}
RF455SourceItemManager::~RF455SourceItemManager(){clear();}
RF455SkillForceItem* RF455SourceItemManager::createSkillForce(const RF455SkillForceData& data,std::uint8_t subtype,std::uint32_t index){
    auto item=std::unique_ptr<RF455SkillForceItem>(new RF455SkillForceItem);
    if(!item->create(data,subtype,index))return nullptr;
    auto* result=item.get();primary.push_back(std::move(item));return result;
}
bool RF455SourceItemManager::erase(std::list<std::unique_ptr<RF455ManagedItem>>& items,RF455ItemHeader* header){
    for(auto at=items.begin();at!=items.end();++at)if(&(*at)->header()==header){
        at->reset();items.erase(at);return true;
    }
    return false;
}
void RF455SourceItemManager::erasePrimary(RF455ItemHeader* header){erase(primary,header);}
void RF455SourceItemManager::eraseGesture(RF455ItemHeader* header){erase(gestures,header);}
bool RF455SourceItemManager::itemIsKind(RF455ItemHeader* header,std::uint8_t kind){
    // The primary release path owns the payload header.404D10's virtual
    // predicate is the kind BYTE comparison for these confirmed item classes.
    return header&&header->kind==kind;
}
void RF455SourceItemManager::clear(){
    // Target469720 destroys in list order,then clears the list. Retain its
    // visible membership until all destructor calls have finished.
    for(auto& item:primary)item.reset();primary.clear();
    for(auto& item:gestures)item.reset();gestures.clear();
}
