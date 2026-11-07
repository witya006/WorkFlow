#include "client455_item_ownership.h"
#include <cstring>
#include <new>
#include <stdexcept>

void RF455_InitializeItemHeader(RF455ItemHeader& item,std::uint32_t dispatch){
    item.dispatch=dispatch;item.serial=0xffffffff;item.field8=0xffffffff;
    item.kind=0;item.data16=0;item.references=0;item.flag21=0;item.field88=0;
}
void RF455_CopyItemHeader(RF455ItemHeader& to,const RF455ItemHeader& from,std::uint32_t dispatch){
    to.dispatch=dispatch;to.serial=from.serial;to.field8=from.field8;to.kind=from.kind;
    to.data16=from.data16;to.references=from.references;to.flag21=from.flag21;
    std::memcpy(to.bytes22,from.bytes22,sizeof(to.bytes22));to.field88=from.field88;
}
void RF455_RetainItem(RF455ItemHeader& item){item.references=std::uint8_t(item.references+1);}
void RF455_DropItemReference(RF455ItemHeader& item){item.references=std::uint8_t(item.references-1);}
bool RF455_ItemReferenceNonpositive(const RF455ItemHeader& item){
    // Target46B090 uses MOVSX AL before the signed comparison,not an unsigned
    // reference count and not a saturating counter.
    return item.references==0 || item.references>=128;
}
void RF455_CopyBoardItemRecord(RF455BoardItemRecord& to,const RF455BoardItemRecord& from,std::uint32_t dispatch){
    // 405DD0 skips CObject padding5..7;405100 copies fields80..583.
    std::memcpy(to.resourceBase,&dispatch,4);to.resourceBase[4]=from.resourceBase[4];
    std::memcpy(to.resourceBase+8,from.resourceBase+8,576);
    to.item=from.item;to.field588=from.field588;to.usingState=from.usingState;to.icon=from.icon;
    to.field600=from.field600;to.field604=from.field604;
    to.field608=from.field608;to.field612=from.field612;to.flag616=from.flag616;
}
RF455BoardItemRecord* RF455_CloneBoardItemRecord(const RF455BoardItemRecord& from,std::uint32_t dispatch,
                                               void* context,RF455ItemRecordAllocate allocate){
    if(!allocate)throw std::invalid_argument("455 board clone needs its actual allocator");
    void* storage=allocate(context,sizeof(RF455BoardItemRecord));
    if(!storage)return nullptr;
    auto* result=new(storage) RF455BoardItemRecord;
    RF455_CopyBoardItemRecord(*result,from,dispatch);
    if(from.item)RF455_RetainItem(*from.item);
    return result;
}
bool RF455_ReleaseBoardItemReference(RF455BoardItemRecord& object,RF455ItemOwnershipHost& host){
    if(host.primaryCacheEmpty() || !object.item)return false;
    auto* item=object.item;RF455_DropItemReference(*item);
    if(RF455_ItemReferenceNonpositive(*item)){
        if(host.itemIsKind(item,6))host.eraseGesture(item);
        else host.erasePrimary(item);
    }
    object.item=nullptr;return true;
}
