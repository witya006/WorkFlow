#include "Character.h"
#include <stdexcept>

EffectPatternList g_PatternList;
ItemEffectList g_EffectItemList;
EffectPatternList::EffectPatternList(){RF455_ConstructEffectPatterns(&native);}
void EffectPatternList::LoadEffectPatternList(char* path){
    lastRead=RF455_ReadEffectPatterns(&native,path);
    if(lastRead.status==RF_EFFECT_TABLE_FORMAT)throw std::runtime_error("455 pattern table: nonnumeric token");
}
void ItemEffectList::LoadItemListFile(char* path){
    lastRead=RF455_ReadEffectItems(&native,path);
    if(lastRead.status==RF_EFFECT_TABLE_FORMAT)throw std::runtime_error("455 item effect table: nonnumeric token");
}
bool IsHaveMeshEffect(CHARACTEROBJECT*,unsigned long item,unsigned long grade,unsigned long group){
    const auto selected=RF455_SelectItemEffect(&g_PatternList.native,&g_EffectItemList.native,item,grade,group);
    if(selected.status==RF_EFFECT_QUERY_UNDEFINED)throw std::runtime_error("455 pattern reader did not initialize this grade; original stack data unknown");
    if(selected.status!=RF_EFFECT_QUERY_OK)throw std::out_of_range("455 item effect group/pattern outside confirmed table");
    return selected.effect!=0;
}
