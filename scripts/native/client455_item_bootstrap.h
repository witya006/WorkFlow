#pragma once
#include <cstdint>
#include <string>

struct RF455CashPaths {std::string data,names;};
inline RF455CashPaths RF455_ItemCashPaths(const char* folder,std::int32_t selector){
    const std::string suffix=selector==-1?"":"_"+std::to_string(selector);
    return {".\\DataTable\\ItemCash"+suffix+".edf",
            ".\\DataTable\\"+std::string(folder)+"\\NDItemCash"+suffix+".edf"};
}
