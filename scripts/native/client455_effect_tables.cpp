#include "client455_effect_tables.h"
#include "client455_character_rfs.h"
#include <cerrno>
#include <cctype>
#include <cstdlib>
#include <new>

namespace {
constexpr std::uint64_t effectTableMaxBytes = 2u * 1024u * 1024u;

bool readEffectTable(const char* path, std::string& text, RF455EffectTableRead& report)
{
    const auto original = RF455_GetCharacterRfsCache()->ReadLooseBytes(path, effectTableMaxBytes);
    if (original.status == RF455ResourceReadStatus::Unavailable) return false;
    if (original.status != RF455ResourceReadStatus::Ready || !original.bytes) {
        report.status = RF_EFFECT_TABLE_FORMAT;
        return false;
    }
    try {
        if (!original.bytes->empty())
            text.assign(reinterpret_cast<const char*>(original.bytes->data()), original.bytes->size());
    } catch (const std::bad_alloc&) {
        report.status = RF_EFFECT_TABLE_FORMAT;
        return false;
    }
    report.status = RF_EFFECT_TABLE_OK;
    return true;
}

struct EffectNumberInput {
    const char* next;
    const char* end;

    bool hasInput() {
        while (next < end && std::isspace(static_cast<unsigned char>(*next))) ++next;
        return next < end;
    }

    bool decimal(int& value) {
        if (!hasInput()) return false;
        char* after;
        errno = 0;
        const long parsed = std::strtol(next, &after, 10);
        if (after == next || errno == ERANGE) return false;
        next = after;
        value = static_cast<int>(parsed);
        return true;
    }

    bool hex(unsigned& value) {
        if (!hasInput()) return false;
        char* after;
        errno = 0;
        const unsigned long parsed = std::strtoul(next, &after, 16);
        if (after == next || errno == ERANGE) return false;
        next = after;
        value = static_cast<unsigned>(parsed);
        return true;
    }
};
}

void RF455_ConstructEffectPatterns(RF455EffectPatterns* table){
    table->present.fill(0);for(auto& row:table->values)row.fill(0);table->known.fill(RF455_EFFECT_ALL_KNOWN);
}
RF455EffectTableRead RF455_ReadEffectPatterns(RF455EffectPatterns* table,const char* path){
    RF455EffectTableRead report={RF_EFFECT_TABLE_MISSING,0,0,0,0};
    std::string text;
    if (!readEffectTable(path, text, report)) return report;
    EffectNumberInput input{text.c_str(), text.c_str() + text.size()};
    int id=0,values[9]={};std::uint64_t known=0;
    // 925710 scans whitespace,not lines. It makes at most2299 attempts and
    // leaves existing rows intact on reload/missing files.
    for(unsigned attempt=1;attempt<2300;++attempt){
        if (!input.hasInput()) break;
        if (!input.decimal(id)) { report.status=RF_EFFECT_TABLE_FORMAT; break; }
        int count = 1;
        while (count < 10 && input.decimal(values[count-1])) ++count;
        ++report.scanned;report.partial+=count!=10;
        for(int n=0;n<count-1;++n)known|=std::uint64_t(1)<<n;
        const auto index=static_cast<unsigned>(id);if(index>=2300)continue;
        report.duplicates+=table->present[index]!=0;table->present[index]=1;
        table->values[index].fill(0);for(unsigned n=0;n<9;++n)table->values[index][n]=static_cast<unsigned>(values[n]);
        table->known[index]=known;++report.stored;
    }
    return report;
}
RF455EffectTableRead RF455_ReadEffectItems(RF455EffectItems* table,const char* path){
    RF455EffectTableRead report={RF_EFFECT_TABLE_MISSING,0,0,0,0};
    std::string text;
    if (!readEffectTable(path, text, report)) return report;
    EffectNumberInput input{text.c_str(), text.c_str() + text.size()};
    unsigned id=0;int patterns[6]={};
    while (input.hasInput()) {
        if (!input.hex(id)) { report.status=RF_EFFECT_TABLE_FORMAT; break; }
        int count = 1;
        while (count < 7 && input.decimal(patterns[count-1])) ++count;
        ++report.scanned;report.partial+=count!=7;
        std::array<unsigned,6> row;for(unsigned i=0;i<6;++i)row[i]=static_cast<unsigned>(patterns[i]);
        const bool inserted=table->entries.emplace(id,row).second;report.stored+=inserted;report.duplicates+=!inserted;
    }
    return report;
}
RF455EffectSelection RF455_SelectItemEffect(const RF455EffectPatterns* patterns,const RF455EffectItems* items,unsigned item,unsigned grade,unsigned group){
    if(grade>=36)return {RF_EFFECT_QUERY_OK,0};
    const auto found=items->entries.find(item);if(found==items->entries.end())return {RF_EFFECT_QUERY_OK,0};
    if(group>=6)return {RF_EFFECT_QUERY_GROUP,0};
    const unsigned id=found->second[group];if(id>=2300)return {RF_EFFECT_QUERY_PATTERN,0};
    if(!(patterns->known[id]&(std::uint64_t(1)<<grade)))return {RF_EFFECT_QUERY_UNDEFINED,0};
    // 927B80 reads values directly: present[] is not consulted.
    return {RF_EFFECT_QUERY_OK,patterns->values[id][grade]};
}
