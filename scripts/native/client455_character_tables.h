#pragma once
#include "client455_item_payloads.h"
#include <array>
#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

struct RF455StorePaths {std::string data,names;};
struct RF455PlayerMoveRates { float walk = 0, run = 0; };
struct RF455StoreTextView {
    const char* data = nullptr;
    std::size_t size = 0;
};
struct RF455StoreProduct {
    std::uint8_t kind = 0;
    std::uint32_t itemCode = 0;
};
struct RF455StoreNpcView {
    std::uint32_t index = 0, model = 0;
    std::uint32_t upgradeCode = 0xffffffffu;
    std::uint32_t priceMultiplier = 1;
    std::uint8_t race = 0xff;
    float orientation = 0.0f, scale = 0.0f;
    RF455StoreTextView name, description;
    std::array<std::uint32_t, 10> actions{};

    std::size_t ProductCount(bool supplemental) const;
    bool ProductAt(bool supplemental, std::size_t slot, RF455StoreProduct& out) const;

private:
    friend struct RF455CharacterTables;
    RF455ItemDataSpan record;
};
struct RF455ResolvedStoreProduct {
    std::uint8_t kind;
    std::uint32_t itemIndex;
    std::uint32_t storeSlot;
    bool supplemental;
};
std::vector<RF455ResolvedStoreProduct> RF455_ResolveStoreProducts(const RF455StoreNpcView&,
                                                                const RF455ItemDataStore&);
inline RF455StorePaths RF455_StoreTablePaths(const char* folder,std::int32_t selector,bool wide){
    return {".\\DataTable\\Store"+(selector==-1?std::string():"_"+std::to_string(selector))+".edf",
            ".\\DataTable\\"+std::string(folder)+"\\NDStore"+(wide?"W":"")+".edf"};
}
struct RF455CharacterTables {
    RF455RawItemTable players,stores;
    // The serialized row's pointer lane1868 stays opaque. Its real owned
    // description lives here,not in a cast target/legacy C++ allocation.
    std::vector<std::vector<unsigned char>> storeDescriptions;
    bool playerLoaded=false,storeBaseLoaded=false,storeNamesLoaded=false;
    bool playerResult=false,skillResult=false,storeResult=false,characterResult=false;
    bool loadPlayerFile();
    bool playerMoveRates(std::uint32_t index, RF455PlayerMoveRates& result) const;
    bool loadStoreFiles(std::int32_t selector,bool wide=false);
    // Borrowed text and products are valid until Store publication or owner destruction.
    bool storeNpcAt(std::uint32_t ordinal, RF455StoreNpcView& out) const;
    bool storeNpcByIndex(std::uint32_t index, RF455StoreNpcView& out) const;
    bool loadCharacterFiles(RF455ItemDataStore&,bool wide=false);
private:
    std::string storeDataPath,storeNamesPath;
    unsigned storeCodepage=0;
    const RF455ItemDataStore* characterOwner=nullptr;
    std::string characterNamesPath;
    unsigned characterCodepage=0;
};
