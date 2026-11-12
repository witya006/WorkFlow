#include "client455_character_tables.h"
#include "client455_language.h"
#include "client455_nation_paths.h"
#include <cmath>
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <utility>

namespace {
bool readFile(const char* name,std::vector<unsigned char>& raw){
    FILE* file=std::fopen(name,"rb");if(!file)return false;bool ok=!std::fseek(file,0,SEEK_END);long length=ok?std::ftell(file):-1;
    ok=ok&&length>=0&&!std::fseek(file,0,SEEK_SET);
    if(ok){raw.resize(static_cast<std::size_t>(length));ok=raw.empty()||std::fread(raw.data(),1,raw.size(),file)==raw.size();}
    std::fclose(file);return ok;
}
bool readPlain(const char* name,std::vector<unsigned char>& plain){std::vector<unsigned char> raw;return readFile(name,raw)&&RF455_DecodeEdf(raw.data(),raw.size(),plain);}
struct Cursor {
    const std::vector<unsigned char>& data;std::size_t at=0;
    bool read(void* out,std::size_t size){if(size>data.size()-at)return false;if(size)std::memcpy(out,data.data()+at,size);at+=size;return true;}
    bool word(std::uint32_t& n){return read(&n,4);}
};
}
bool RF455CharacterTables::loadPlayerFile(){
    if(playerLoaded)throw std::logic_error("455 PlayerCharacter reload lifetime remains unported");
    std::vector<unsigned char> plain;if(!readPlain(".\\DataTable\\PlayerCharacter.edf",plain))return false;Cursor c{plain};RF455RawItemTable next;
    if(!c.word(next.count)||!c.word(next.stride))return false;
    if(next.count&&next.stride){if(next.count>(plain.size()-c.at)/next.stride)return false;
        const auto bytes=std::size_t(next.count)*next.stride;next.bytes.assign(plain.data()+c.at,plain.data()+c.at+bytes);}
    players=std::move(next);playerLoaded=true;return players.count&&players.stride;
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
    if(storeNamesLoaded)throw std::logic_error("455 Store relocalization lifetime remains unported");
    const auto* nation=RF455_GetNormalNationPaths();if(!nation->configured)return false;const auto paths=RF455_StoreTablePaths(nation->folder,selector,wide);
    std::vector<unsigned char> plain;
    if(!storeBaseLoaded){
        if(!readPlain(paths.data.c_str(),plain))return false;Cursor c{plain};RF455RawItemTable next;std::uint32_t ignored=0;
        if(!c.word(next.count)||!c.word(ignored))return false;next.stride=2076;
        if(next.count>(plain.size()-c.at)/next.stride)return false;
        next.bytes.assign(plain.data()+c.at,plain.data()+c.at+std::size_t(next.count)*next.stride);
        stores=std::move(next);storeDescriptions.resize(stores.count);storeBaseLoaded=true;
    }
    if(!readPlain(paths.names.c_str(),plain))return false;Cursor c{plain};std::uint32_t count=0;if(!c.word(count)||count!=stores.count)return false;
    for(std::uint32_t i=0;i<count;++i){std::uint32_t ignored=0,bytes=0;auto* row=stores.bytes.data()+std::size_t(i)*2076;
        if(!c.word(ignored)||!c.read(row+17,64)||!c.read(row+81,64)||!c.word(bytes)||bytes>plain.size()-c.at)return false;
        storeDescriptions[i].assign(plain.data()+c.at,plain.data()+c.at+bytes);c.at+=bytes;
    }
    storeNamesLoaded=true;return true;
}
bool RF455CharacterTables::loadCharacterFiles(RF455ItemDataStore& data,bool wide){
    const auto* nation=RF455_GetNormalNationPaths();if(!nation->configured)return false;
    std::vector<unsigned char> raw;
    if(!readFile(".\\DataTable\\Character.edf",raw)||!data.loadCharacterEdf(raw.data(),raw.size()))return false;
    const std::string names=std::string(nation->dataRoot)+"\\NDCharacter"+(wide?"W":"")+".edf";
    return readFile(names.c_str(),raw)&&data.localizeCharacterEdf(raw.data(),raw.size(),RF455_CountryCodePage(nation->nation));
}
