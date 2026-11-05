#pragma once
#include <array>
#include <cstdint>
#include <map>

constexpr unsigned RF455_EFFECT_PATTERN_COUNT=2300,RF455_EFFECT_GRADES=36,RF455_EFFECT_GROUPS=6;
constexpr std::uint64_t RF455_EFFECT_ALL_KNOWN=(std::uint64_t(1)<<36)-1;
struct RF455EffectPatterns {
    std::array<unsigned,2300> present;
    std::array<std::array<unsigned,36>,2300> values;
    // Own evidence metadata,not part of the original340400-byte table.
    // The reader writes9 stack DWORDs but copies36; unknown bytes must never
    // become a silently accepted zero effect ID.
    std::array<std::uint64_t,2300> known;
};
struct RF455EffectItems {std::map<unsigned,std::array<unsigned,6>> entries;};
enum RF455EffectTableStatus {RF_EFFECT_TABLE_OK=0,RF_EFFECT_TABLE_MISSING=1,RF_EFFECT_TABLE_FORMAT=2};
struct RF455EffectTableRead {RF455EffectTableStatus status;unsigned scanned,stored,duplicates,partial;};
enum RF455EffectQueryStatus {RF_EFFECT_QUERY_OK=0,RF_EFFECT_QUERY_GROUP=1,RF_EFFECT_QUERY_PATTERN=2,RF_EFFECT_QUERY_UNDEFINED=3};
struct RF455EffectSelection {RF455EffectQueryStatus status;unsigned effect;};
void RF455_ConstructEffectPatterns(RF455EffectPatterns*);
RF455EffectTableRead RF455_ReadEffectPatterns(RF455EffectPatterns*,const char*);
RF455EffectTableRead RF455_ReadEffectItems(RF455EffectItems*,const char*);
RF455EffectSelection RF455_SelectItemEffect(const RF455EffectPatterns*,const RF455EffectItems*,unsigned item,unsigned grade,unsigned group);
