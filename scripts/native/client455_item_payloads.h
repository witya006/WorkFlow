#pragma once
#include "client455_skill_force_items.h"
#include <memory>
#include <string>

struct RF455RawItemTable {
    std::uint32_t count=0,stride=0;
    std::vector<unsigned char> bytes;
    RF455ItemDataSpan get(std::uint32_t)const;
};
struct RF455ItemDescription {std::uint32_t index=0,code=0;std::vector<unsigned char> bytes;};
struct RF455RewardTooltip {
    std::string name;
    std::string description;
};
struct RF455QuestDescription {std::uint32_t index=0,code=0;std::vector<unsigned char> bytes;};
struct RF455DungeonDescription {std::uint32_t index=0;std::array<unsigned char,64> name;std::vector<unsigned char> bytes;};

class RF455ItemDataStore {
    bool itemLoaded=false,itemLocalized=false,questLocalized=false,characterLoaded=false,characterLocalized=false;
    std::array<RF455RawItemTable,47> items;
    std::array<std::uint32_t,47> workStarts{},workCounts{};
    std::array<std::vector<RF455ItemDescription>,47> descriptions;
    std::vector<RF455DungeonDescription> dungeons;
    std::shared_ptr<std::array<RF455RawItemTable,12>> quests;
    std::vector<RF455QuestDescription> questDescriptions;
    std::array<RF455RawItemTable,7> character;
    std::size_t localizationConsumed=0;
    friend class RF455BasicItem;
public:
    bool loadItemEdf(const void*,std::size_t,bool segmented);
    bool localizeItemEdf(const void*,std::size_t);
    bool hasItemData() const { return itemLoaded; }
    bool hasItemLocalization() const { return itemLocalized; }
    bool loadQuestEdf(const void*,std::size_t);
    bool localizeQuestEdf(const void*,std::size_t);
    void clearQuestData();
    bool hasQuestData() const { return quests != nullptr; }
    bool hasQuestLocalization() const { return questLocalized; }
    const RF455QuestDescription* questDescription(std::uint32_t ordinal) const;
    const char* questGroupName(std::uint32_t ordinal) const;
    bool loadCharacterEdf(const void*,std::size_t);
    bool localizeCharacterEdf(const void*,std::size_t,unsigned codepage);
    bool hasCharacterData() const { return characterLoaded; }
    bool hasCharacterLocalization() const { return characterLocalized; }
    RF455ItemDataSpan classByCode(const char*)const;
    RF455ItemDataSpan classByIndex(std::uint32_t)const;
    RF455ItemDataSpan getItem(std::uint32_t,std::uint32_t)const;
    bool findItemByCode(std::uint8_t kind, std::uint32_t code, std::uint32_t& index) const;
    bool findItemRowByCode(std::uint8_t kind, std::uint32_t code, std::uint32_t& ordinal) const;
    bool makeRewardTooltip(std::uint8_t kind, std::uint32_t ordinal, RF455RewardTooltip& out) const;
    // Metadata helpers use unchecked offsets in the target. Preserve reads
    // crossing a declared row only while they remain in its actual table owner.
    RF455ItemDataSpan getItemExtent(std::uint32_t,std::uint32_t)const;
    RF455ItemDataSpan getQuest(std::uint32_t)const;
    RF455ItemDataSpan animusLevel(std::uint8_t,std::uint64_t)const;
    const std::array<RF455RawItemTable,47>& itemTables()const{return items;}
    const std::array<RF455RawItemTable,12>& questTables()const;
    const std::array<RF455RawItemTable,7>& characterTables()const{return character;}
    const std::array<std::uint32_t,47>& itemWorkStarts()const{return workStarts;}
    const std::array<std::uint32_t,47>& itemWorkCounts()const{return workCounts;}
    const std::array<std::vector<RF455ItemDescription>,47>& itemDescriptions()const{return descriptions;}
    const std::vector<RF455DungeonDescription>& dungeonDescriptions()const{return dungeons;}
    std::size_t localizedBytesConsumed()const{return localizationConsumed;}
};

struct RF455TalicUpgrade {
    std::uint8_t sockets = 0;
    std::uint8_t count = 0;
    std::array<std::uint8_t, 7> ids{};
};

RF455TalicUpgrade RF455_DecodeTalics455(const RF455ItemDataStore&, RF455ItemDataSpan equipment,
                                       std::uint32_t packed);

// Source-owned fresh factory states,not callable private target C++ objects.
// The record has the selected target size200/136/192/100/116;its dispatch word
// is an own token. Live UI/network changes and full gameplay methods are open.
class RF455BasicItem final:public RF455ManagedItem {
    std::unique_ptr<unsigned char[]> state;
    std::size_t stateSize=0;
    std::uint8_t payloadKind;
    RF455ItemDataSpan data;
    RF455ItemDataSpan metadata;
    std::shared_ptr<const std::array<RF455RawItemTable,12>> questLease;
    friend class RF455SourceItemManager;
    explicit RF455BasicItem(std::uint8_t);
    bool create(const RF455ItemDataStore&,std::uint8_t,std::uint32_t);
public:
    RF455ItemHeader& header()override;
    std::uint32_t tableIndex()const;
    const char* name()const;
    RF455ItemDataSpan rawData()const{return data;}
    RF455ItemDataSpan rawMetadata()const{return metadata;}
    RF455ItemDataSpan recordBytes()const{return {state.get(),stateSize};}
    void SetUpgradeLevel455(std::uint8_t);
    void ApplyTalics455(const RF455ItemDataStore&, std::uint32_t packed);
    void SetDownloadValue455(std::uint32_t value, std::uint32_t animusHigh);
    std::uint8_t quantity455() const;
    bool IsStackable455() const;
    std::uint32_t durability455() const;
    void SetDurability455(std::uint32_t value);
    void SetDownloadModifiers455(std::uint8_t kind, std::uint32_t value,
                                 bool timed, std::int64_t secondsRemaining);
};
