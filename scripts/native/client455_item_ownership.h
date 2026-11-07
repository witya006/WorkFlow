#pragma once
#include <cstddef>
#include <cstdint>

// Selected x86 record/data kernels,not callable target vtables or a replacement
// for the complete CItem/CResObject classes. Dispatch words are opaque tokens
// supplied by the owner. No address from the input EXE is invoked.
#pragma pack(push,4)
struct RF455ItemHeader {
    std::uint32_t dispatch,serial,field8;
    std::uint8_t kind,padding13[3];
    std::uint32_t data16;
    std::uint8_t references,flag21,bytes22[64],padding86[2];
    std::uint32_t field88;
};
struct RF455BoardItemRecord {
    std::uint8_t resourceBase[584];
    RF455ItemHeader* item;
    std::uint32_t field588;
    std::uint8_t usingState,padding593[3];
    void* icon;
    std::uint32_t field600,field604,field608,field612;
    std::uint8_t flag616,padding617[3];
};
#pragma pack(pop)
static_assert(sizeof(void*)==4,"455 item records require the client x86 build");
static_assert(sizeof(RF455ItemHeader)==92 && offsetof(RF455ItemHeader,references)==20,"CItem header layout");
static_assert(sizeof(RF455BoardItemRecord)==620 && offsetof(RF455BoardItemRecord,item)==584 &&
              offsetof(RF455BoardItemRecord,icon)==596 && offsetof(RF455BoardItemRecord,flag616)==616,"CBoardObject record layout");

// 45FC80/405E70: unwritten bytes and padding retain their destination values.
void RF455_InitializeItemHeader(RF455ItemHeader&,std::uint32_t dispatch);
void RF455_CopyItemHeader(RF455ItemHeader&,const RF455ItemHeader&,std::uint32_t dispatch);
void RF455_RetainItem(RF455ItemHeader&);
void RF455_DropItemReference(RF455ItemHeader&);
bool RF455_ItemReferenceNonpositive(const RF455ItemHeader&);

// 46B5E0 and its parent copy constructors. This copies opaque resource fields
// as the target does;it does NOT implement their drawing/resource destruction.
void RF455_CopyBoardItemRecord(RF455BoardItemRecord&,const RF455BoardItemRecord&,std::uint32_t dispatch);
using RF455ItemRecordAllocate=void* (*)(void*,std::size_t);
RF455BoardItemRecord* RF455_CloneBoardItemRecord(const RF455BoardItemRecord&,std::uint32_t dispatch,
                                               void* allocatorContext,RF455ItemRecordAllocate);

// Required production providers remain explicit. The selected release routine
// queries the PRIMARY cache even for Gesture items. The host supplies virtual
// IsKind and manager removal;never infer either from an unverified raw layout.
class RF455ItemOwnershipHost {
public:
    virtual ~RF455ItemOwnershipHost()=default;
    virtual bool primaryCacheEmpty()=0;
    virtual bool itemIsKind(RF455ItemHeader*,std::uint8_t)=0;
    virtual void erasePrimary(RF455ItemHeader*)=0;
    virtual void eraseGesture(RF455ItemHeader*)=0;
};
// Returns whether the selected routine reached pointer clearing. Empty cache
// leaves BOTH the wrapper pointer and its reference counter unchanged.
bool RF455_ReleaseBoardItemReference(RF455BoardItemRecord&,RF455ItemOwnershipHost&);
