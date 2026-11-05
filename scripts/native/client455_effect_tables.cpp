#include "client455_effect_tables.h"
#include <cstdio>

void RF455_ConstructEffectPatterns(RF455EffectPatterns* table){
    table->present.fill(0);for(auto& row:table->values)row.fill(0);table->known.fill(RF455_EFFECT_ALL_KNOWN);
}
RF455EffectTableRead RF455_ReadEffectPatterns(RF455EffectPatterns* table,const char* path){
    std::FILE* input=std::fopen(path,"rb");RF455EffectTableRead report={RF_EFFECT_TABLE_MISSING,0,0,0,0};if(!input)return report;
    report.status=RF_EFFECT_TABLE_OK;int id=0,values[9]={};std::uint64_t known=0;
    // 925710 scans whitespace,not lines. It makes at most2299 attempts and
    // leaves existing rows intact on reload/missing files.
    for(unsigned attempt=1;attempt<2300;++attempt){
        const int count=std::fscanf(input,"%d%d%d%d%d%d%d%d%d%d",&id,values,values+1,values+2,values+3,values+4,values+5,values+6,values+7,values+8);
        if(count==EOF)break;
        if(!count){report.status=RF_EFFECT_TABLE_FORMAT;break;} // Own visible malformed-input policy.
        ++report.scanned;report.partial+=count!=10;
        for(int n=0;n<count-1;++n)known|=std::uint64_t(1)<<n;
        const auto index=static_cast<unsigned>(id);if(index>=2300)continue;
        report.duplicates+=table->present[index]!=0;table->present[index]=1;
        table->values[index].fill(0);for(unsigned n=0;n<9;++n)table->values[index][n]=static_cast<unsigned>(values[n]);
        table->known[index]=known;++report.stored;
    }
    std::fclose(input);return report;
}
RF455EffectTableRead RF455_ReadEffectItems(RF455EffectItems* table,const char* path){
    std::FILE* input=std::fopen(path,"rb");RF455EffectTableRead report={RF_EFFECT_TABLE_MISSING,0,0,0,0};if(!input)return report;
    report.status=RF_EFFECT_TABLE_OK;unsigned id=0;int patterns[6]={};
    for(;;){
        const int count=std::fscanf(input,"%x%d%d%d%d%d%d",&id,patterns,patterns+1,patterns+2,patterns+3,patterns+4,patterns+5);
        if(count==EOF)break;
        if(!count){report.status=RF_EFFECT_TABLE_FORMAT;break;} // Reference would not advance: an endless loop.
        ++report.scanned;report.partial+=count!=7;
        std::array<unsigned,6> row;for(unsigned i=0;i<6;++i)row[i]=static_cast<unsigned>(patterns[i]);
        const bool inserted=table->entries.emplace(id,row).second;report.stored+=inserted;report.duplicates+=!inserted;
    }
    std::fclose(input);return report;
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
