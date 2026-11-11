#pragma once
#include "client455_item_ownership.h"
#include <array>
#include <list>
#include <memory>
#include <vector>
class CGUISkFcUnit;

struct RF455ItemDataSpan {const unsigned char* data=nullptr;std::size_t size=0;};
struct RF455SkillForceTable {
    std::uint32_t count=0,stride=0;
    std::vector<unsigned char> bytes;
    RF455ItemDataSpan get(std::uint32_t)const;
};
class RF455SkillForceData {
    std::array<RF455SkillForceTable,5> tables;
    bool loaded=false;
public:
    // Root SkillForce.edf contains five tables at manager offsets48..96.
    // The earlier four manager tables come from other inputs,not this file.
    bool loadBaseEdf(const void*,std::size_t);
    // Preserve the target's prefix writes on count mismatch;the second header
    // DWORD is ignored. Each row overwrites name32 at112 and text512 at524.
    bool localizeEdf(const void*,std::size_t);
    bool loadFiles(const char* base,const char* localized);
    RF455ItemDataSpan get(std::uint8_t subtype,std::uint32_t index)const;
    bool hasAttackEffect(std::uint8_t subtype, std::uint32_t index) const;
    bool usesMonsterAttackClip(std::uint8_t subtype, std::uint32_t index, std::uint8_t level) const;
    const std::array<RF455SkillForceTable,5>& records()const{return tables;}
};

#pragma pack(push,4)
struct RF455SkillForceRecord {
    RF455ItemHeader item;
    std::uint8_t subtype,padding93[3];
    std::uint32_t successCount;
    std::uint8_t level,flag101,padding102[2];
    float percent;
    void* iconBoard;
    std::uint32_t field112,field116,field120;
    unsigned char bytes124[17],bytes141[17],padding158[2];
};
#pragma pack(pop)
static_assert(sizeof(RF455SkillForceRecord)==160 && offsetof(RF455SkillForceRecord,subtype)==92 &&
              offsetof(RF455SkillForceRecord,iconBoard)==108,"455 SF payload layout");

class RF455ManagedItem {
public:
    virtual ~RF455ManagedItem()=default;
    virtual RF455ItemHeader& header()=0;
    virtual const char* name()const=0;
    bool isKind(std::uint8_t kind){return header().kind==kind;} //404D10
};
class RF455SkillForceItem final:public RF455ManagedItem {
    RF455SkillForceRecord state; // Unwritten bytes retain their own storage.
    RF455ItemDataSpan data;
    friend class RF455SourceItemManager;
    RF455SkillForceItem();
    bool create(const RF455SkillForceData&,std::uint8_t,std::uint32_t);
public:
    RF455ItemHeader& header()override{return state.item;}
    const RF455SkillForceRecord& record()const{return state;}
    std::uint32_t tableIndex()const;
    const char* name()const;
    RF455ItemDataSpan rawData()const{return data;}
    std::uint8_t EffectiveLevel455(bool baseOnly=false)const;
    void SetEquipmentLevel455(std::uint8_t);
    //Only source-created CGUISkFcUnit pointers may be bound here.
    void SetIconBoard455(CGUISkFcUnit* value){state.iconBoard=value;}
};

// Concrete source-owned primary/auxiliary caches. Fresh payload creation is
// implemented by the SF and basic-item modules. Gesture/Macro,live callbacks
// and ordinary game-global binding remain required.
class RF455ItemDataStore;
class RF455SourceItemManager final:public RF455ItemOwnershipHost {
    std::list<std::unique_ptr<RF455ManagedItem>> primary,gestures;
    static bool erase(std::list<std::unique_ptr<RF455ManagedItem>>&,RF455ItemHeader*);
public:
    ~RF455SourceItemManager();
    RF455SkillForceItem* createSkillForce(const RF455SkillForceData&,std::uint8_t,std::uint32_t);
    RF455ManagedItem* createPayload(const RF455ItemDataStore&,std::uint8_t selector,std::uint8_t type,
                                    std::uint32_t index,const RF455SkillForceData* sf=nullptr);
    std::size_t size()const{return primary.size();}
    void clear();
    bool primaryCacheEmpty()override{return primary.empty();}
    bool itemIsKind(RF455ItemHeader*,std::uint8_t)override;
    void erasePrimary(RF455ItemHeader*)override;
    void eraseGesture(RF455ItemHeader*)override;
};
