#include "client455_character_tables.h"
#include "client455_event_music.h"
#include "client455_edf_input.h"
#include "client455_language.h"
#include "client455_nation_paths.h"
#include <cmath>
#include <array>
#include <cstring>
#include <stdexcept>
#include <new>
#include <utility>

namespace {
struct Cursor {
    const std::vector<unsigned char>& data;std::size_t at=0;
    bool read(void* out,std::size_t size){if(size>data.size()-at)return false;if(size)std::memcpy(out,data.data()+at,size);at+=size;return true;}
    bool word(std::uint32_t& n){return read(&n,4);}
};
bool storeBase(const std::vector<unsigned char>& plain,RF455RawItemTable& next){
    Cursor c{plain};std::uint32_t ignored=0;
    if(!c.word(next.count)||!c.word(ignored))return false;next.stride=2076;
    if(next.count>(plain.size()-c.at)/next.stride)return false;
    next.bytes.assign(plain.data()+c.at,plain.data()+c.at+std::size_t(next.count)*next.stride);
    return true;
}
using StoreNames=std::vector<std::array<unsigned char,128>>;
bool storeNames(const std::vector<unsigned char>& plain,std::uint32_t expected,StoreNames& names,
                std::vector<std::vector<unsigned char>>& descriptions){
    Cursor c{plain};std::uint32_t count=0;
    if(!c.word(count)||count!=expected||count>(plain.size()-c.at)/136)return false;
    names.resize(count);descriptions.resize(count);
    for(std::uint32_t i=0;i<count;++i){std::uint32_t ignored=0,bytes=0;
        if(!c.word(ignored)||!c.read(names[i].data(),names[i].size())||!c.word(bytes)||bytes>plain.size()-c.at)return false;
        descriptions[i].assign(plain.data()+c.at,plain.data()+c.at+bytes);c.at+=bytes;
    }
    return true;
}
void publishStoreBase(RF455RawItemTable& target,RF455RawItemTable& next){
    if(target.count==next.count&&target.stride==next.stride&&target.bytes.size()==next.bytes.size()){
        if(!next.bytes.empty())std::memcpy(target.bytes.data(),next.bytes.data(),next.bytes.size());
    }else target=std::move(next);
}
RF455StoreTextView storeText455(const unsigned char* bytes, std::size_t size)
{
    if (!bytes || !size) return {};
    const auto* end = static_cast<const unsigned char*>(std::memchr(bytes, 0, size));
    return {reinterpret_cast<const char*>(bytes), end ? static_cast<std::size_t>(end - bytes) : size};
}

struct StoreProductLayout455 {
    std::size_t offset;
    std::size_t stride;
    std::size_t limit;
};

StoreProductLayout455 storeProductLayout455(bool supplemental)
{
    // RVA 0x05CD40 uses separate primary and supplemental descriptor lanes.
    return supplemental ? StoreProductLayout455{1884, 12, 16} : StoreProductLayout455{228, 8, 200};
}
}
bool RF455CharacterTables::loadPlayerFile(){
    if(playerLoaded)return true;
    try{
        return RF455_ReadEdfInput(".\\DataTable\\PlayerCharacter.edf", [&](const unsigned char* raw, std::size_t size) {
            std::vector<unsigned char> plain;
            if (!RF455_DecodeEdf(raw, size, plain)) return false;
            Cursor cursor{plain};
            RF455RawItemTable next;
            if (!cursor.word(next.count) || !cursor.word(next.stride) || !next.count || !next.stride ||
                next.count > (plain.size() - cursor.at) / next.stride) return false;
            const auto bytes = std::size_t(next.count) * next.stride;
            next.bytes.assign(plain.data() + cursor.at, plain.data() + cursor.at + bytes);
            players = std::move(next);
            playerLoaded = true;
            return true;
        });
    }catch(const std::bad_alloc&){return false;}catch(const std::length_error&){return false;}
}
bool RF455CharacterTables::playerMoveRates(std::uint32_t index, RF455PlayerMoveRates& result) const {
    const auto row = players.get(index);
    if (!row.data || row.size < 52) return false;
    RF455PlayerMoveRates rates;
    std::memcpy(&rates.walk, row.data + 44, sizeof(rates.walk));
    std::memcpy(&rates.run, row.data + 48, sizeof(rates.run));
    if (!std::isfinite(rates.walk) || !std::isfinite(rates.run) || rates.walk <= 0 || rates.run <= 0)
        return false;
    result = rates;
    return true;
}
bool RF455CharacterTables::loadStoreFiles(std::int32_t selector,bool wide){
    const auto* nation=RF455_GetNormalNationPaths();if(!nation->configured)return false;
    try{
    auto paths=RF455_StoreTablePaths(nation->folder,selector,wide);const unsigned cp=RF455_CountryCodePage(nation->nation);
    const bool sameKey=storeBaseLoaded&&storeDataPath==paths.data&&storeNamesPath==paths.names&&storeCodepage==cp;
    if(sameKey&&storeNamesLoaded)return true;
    const bool reloadBase=!sameKey;
    std::vector<unsigned char> plain;
    RF455RawItemTable next;std::vector<std::vector<unsigned char>> emptyDescriptions;
    if(reloadBase){
        if (!RF455_ReadEdfInput(paths.data.c_str(), [&](const unsigned char* raw, std::size_t size) {
            return RF455_DecodeEdf(raw, size, plain) && storeBase(plain, next);
        })) return false;
        emptyDescriptions.resize(next.count);
    }
    StoreNames names;std::vector<std::vector<unsigned char>> descriptions;
    const bool localized = RF455_ReadEdfInput(paths.names.c_str(), [&](const unsigned char* raw, std::size_t size) {
        return RF455_DecodeEdf(raw, size, plain) &&
            storeNames(plain, reloadBase ? next.count : stores.count, names, descriptions);
    });
    // A valid replacement base remains usable even without matching NDStore.
    // Same-layout locale changes update it in place, preserving borrowed rows.
    if(reloadBase){
        publishStoreBase(stores,next);storeDescriptions.swap(emptyDescriptions);
        storeDataPath.swap(paths.data);storeNamesPath.swap(paths.names);storeCodepage=cp;
        storeBaseLoaded=true;storeNamesLoaded=false;
    }
    if(!localized)return false;
    for(std::uint32_t i=0;i<stores.count;++i)
        std::memcpy(stores.bytes.data()+std::size_t(i)*2076+17,names[i].data(),names[i].size());
    storeDescriptions.swap(descriptions);storeNamesLoaded=true;return true;
    }catch(const std::bad_alloc&){return false;}catch(const std::length_error&){return false;}
}

bool RF455CharacterTables::storeNpcAt(std::uint32_t ordinal, RF455StoreNpcView& out) const
{
    const auto row = stores.get(ordinal);
    if (!row.data || row.size < 1868) return false;
    // RVA 0x05CD40 consumes the model, name and transforms; 0x05DA00 uses
    // the race byte. The description is owned separately from the raw row.
    RF455StoreNpcView value;
    value.record = row;
    std::memcpy(&value.index, row.data, sizeof(value.index));
    std::memcpy(&value.model, row.data + 8, sizeof(value.model));
    value.race = row.data[16];
    value.name = storeText455(row.data + 17, 64);
    if (!value.name.size) {
        static constexpr char unknown[] = "Unknown NPC";
        value.name = {unknown, sizeof(unknown) - 1};
    }
    std::memcpy(&value.orientation, row.data + 212, sizeof(value.orientation));
    std::memcpy(&value.scale, row.data + 220, sizeof(value.scale));
    std::memcpy(value.actions.data(), row.data + 1828, value.actions.size() * sizeof(value.actions[0]));
    if (row.size >= 1876)
        std::memcpy(&value.priceMultiplier, row.data + 1872, sizeof(value.priceMultiplier));
    if (row.size >= 1880)
        std::memcpy(&value.upgradeCode, row.data + 1876, sizeof(value.upgradeCode));
    if (ordinal < storeDescriptions.size()) {
        const auto& description = storeDescriptions[ordinal];
        value.description = storeText455(description.data(), description.size());
    }
    out = value;
    return true;
}

bool RF455CharacterTables::storeNpcByIndex(std::uint32_t index, RF455StoreNpcView& out) const
{
    // RVA 0x1FA7C0 selects the first row with this ID.
    for (std::uint32_t ordinal = 0; ordinal < stores.count; ++ordinal) {
        const auto row = stores.get(ordinal);
        if (!row.data || row.size < sizeof(index)) return false;
        std::uint32_t candidate;
        std::memcpy(&candidate, row.data, sizeof(candidate));
        if (candidate == index) return storeNpcAt(ordinal, out);
    }
    return false;
}

std::size_t RF455StoreNpcView::ProductCount(bool supplemental) const
{
    const auto layout = storeProductLayout455(supplemental);
    if (!record.data || record.size < layout.offset) return 0;
    std::uint32_t count;
    std::memcpy(&count, record.data + layout.offset - sizeof(count), sizeof(count));
    const auto available = (record.size - layout.offset) / layout.stride;
    if (count > layout.limit || count > available) return 0;
    return count;
}

bool RF455StoreNpcView::ProductAt(bool supplemental, std::size_t slot, RF455StoreProduct& out) const
{
    if (slot >= ProductCount(supplemental)) return false;
    const auto layout = storeProductLayout455(supplemental);
    const auto* bytes = record.data + layout.offset + slot * layout.stride;
    RF455StoreProduct value;
    value.kind = bytes[0];
    std::memcpy(&value.itemCode, bytes + 4, sizeof(value.itemCode));
    out = value;
    return true;
}

std::vector<RF455ResolvedStoreProduct> RF455_ResolveStoreProducts(const RF455StoreNpcView& npc,
                                                                const RF455ItemDataStore& items)
{
    std::vector<RF455ResolvedStoreProduct> results;
    results.reserve(npc.ProductCount(true) + npc.ProductCount(false));
    // For these country profiles RVA 0x05CD40 emits the supplemental lane
    // first. RVA 0x200030 selects the first matching item code for the kind.
    for (const bool supplemental : {true, false}) {
        const auto count = npc.ProductCount(supplemental);
        for (std::size_t slot = 0; slot < count; ++slot) {
            RF455StoreProduct product;
            std::uint32_t itemIndex;
            if (!npc.ProductAt(supplemental, slot, product) ||
                !items.findItemByCode(product.kind, product.itemCode, itemIndex))
                continue;
            const auto item = items.getItem(product.kind, itemIndex);
            if (!item.data || item.size < 8) continue;
            std::uint32_t resolvedCode;
            std::memcpy(&resolvedCode, item.data + 4, sizeof(resolvedCode));
            if (resolvedCode != product.itemCode) continue;
            results.push_back({product.kind, itemIndex, static_cast<std::uint32_t>(slot), supplemental});
        }
    }
    return results;
}

bool RF455CharacterTables::loadCharacterFiles(RF455ItemDataStore& data,bool wide){
    const auto* nation=RF455_GetNormalNationPaths();if(!nation->configured)return false;
    try{
    std::string names=std::string(nation->dataRoot)+"\\NDCharacter"+(wide?"W":"")+".edf";
    const unsigned cp=RF455_CountryCodePage(nation->nation);
    if(data.hasCharacterLocalization()){
        // An already localized foreign owner has no trustworthy locale receipt.
        // Changing language in a live Character owner needs a separate lifecycle.
        return characterOwner==&data&&characterNamesPath==names&&characterCodepage==cp;
    }
    if (!data.hasCharacterData() && !RF455_ReadEdfInput(".\\DataTable\\Character.edf",
        [&](const unsigned char* raw, std::size_t size) { return data.loadCharacterEdf(raw, size); }))
        return false;
    if (!RF455_ReadEdfInput(names.c_str(), [&](const unsigned char* raw, std::size_t size) {
        return data.localizeCharacterEdf(raw, size, cp);
    })) return false;
    characterOwner=&data;characterNamesPath.swap(names);characterCodepage=cp;return true;
    }catch(const std::bad_alloc&){return false;}catch(const std::length_error&){return false;}
}

bool RF455_EventMusicMonsterCode(const RF455ItemDataStore& data, std::uint32_t index, std::uint32_t& code)
{
    const auto& monsters = data.characterTables()[2];
    const auto row = monsters.get(index);
    // 455 RVAs 0x05AB60 and 0x05AC00 use the event flag at +72 and code at +4.
    if (!row.data || row.size < 76) return false;
    std::uint32_t eventEnabled;
    std::memcpy(&eventEnabled, row.data + 72, sizeof(eventEnabled));
    if (!eventEnabled) return false;
    std::memcpy(&code, row.data + 4, sizeof(code));
    return true;
}
