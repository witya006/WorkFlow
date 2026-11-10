#pragma once
#include "client455_item_payloads.h"
#include <string>

struct RF455StorePaths {std::string data,names;};
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
    bool loadStoreFiles(std::int32_t selector,bool wide=false);
    bool loadCharacterFiles(RF455ItemDataStore&,bool wide=false);
};
