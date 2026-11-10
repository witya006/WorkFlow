#pragma once
#include "client455_skill_force_items.h"

struct RF455RawItemTable {
    std::uint32_t count=0,stride=0;
    std::vector<unsigned char> bytes;
    RF455ItemDataSpan get(std::uint32_t)const;
};
struct RF455ItemDescription {std::uint32_t index=0,code=0;std::vector<unsigned char> bytes;};
struct RF455DungeonDescription {std::uint32_t index=0;std::array<unsigned char,64> name;std::vector<unsigned char> bytes;};

class RF455ItemDataStore {
    bool itemLoaded=false,itemLocalized=false,questLoaded=false,characterLoaded=false,characterLocalized=false;
    std::array<RF455RawItemTable,47> items;
    std::array<std::uint32_t,47> workStarts{},workCounts{};
    std::array<std::vector<RF455ItemDescription>,47> descriptions;
    std::vector<RF455DungeonDescription> dungeons;
    std::array<RF455RawItemTable,12> quests;
    std::array<RF455RawItemTable,7> character;
    std::size_t localizationConsumed=0;
public:
    bool loadItemEdf(const void*,std::size_t,bool segmented);
    bool localizeItemEdf(const void*,std::size_t);
    bool loadQuestEdf(const void*,std::size_t);
    bool loadCharacterEdf(const void*,std::size_t);
    bool localizeCharacterEdf(const void*,std::size_t,unsigned codepage);
    RF455ItemDataSpan classByCode(const char*)const;
    RF455ItemDataSpan classByIndex(std::uint32_t)const;
    RF455ItemDataSpan getItem(std::uint32_t,std::uint32_t)const;
    // Metadata helpers use unchecked offsets in the target. Preserve reads
    // crossing a declared row only while they remain in its actual table owner.
    RF455ItemDataSpan getItemExtent(std::uint32_t,std::uint32_t)const;
    RF455ItemDataSpan getQuest(std::uint32_t)const;
    RF455ItemDataSpan animusLevel(std::uint8_t,std::uint64_t)const;
    const std::array<RF455RawItemTable,47>& itemTables()const{return items;}
    const std::array<RF455RawItemTable,12>& questTables()const{return quests;}
    const std::array<RF455RawItemTable,7>& characterTables()const{return character;}
    const std::array<std::uint32_t,47>& itemWorkStarts()const{return workStarts;}
    const std::array<std::uint32_t,47>& itemWorkCounts()const{return workCounts;}
    const std::array<std::vector<RF455ItemDescription>,47>& itemDescriptions()const{return descriptions;}
    const std::vector<RF455DungeonDescription>& dungeonDescriptions()const{return dungeons;}
    std::size_t localizedBytesConsumed()const{return localizationConsumed;}
};

// Source-owned fresh factory states,not callable private target C++ objects.
// The record has the selected target size200/136/192/100/116;its dispatch word
// is an own token. Live UI/network changes and full gameplay methods are open.
class RF455BasicItem final:public RF455ManagedItem {
    std::unique_ptr<unsigned char[]> state;
    std::size_t stateSize=0;
    std::uint8_t payloadKind;
    RF455ItemDataSpan data;
    RF455ItemDataSpan metadata;
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
};
