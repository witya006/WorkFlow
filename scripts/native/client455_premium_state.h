#pragma once
#include <array>
#include <bitset>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <stdexcept>

//40BB50 writes six four-column families;the57/12 packet writes columns0/1.
//Other columns and constructor-unwritten bonus floats stay explicitly unknown.
class RF455PremiumBenefits {
    std::array<std::array<float,4>,6> rates{};
    std::bitset<24> knownRates;
    std::array<float,2> bonuses{};
    std::uint16_t mask=0;
    bool maskKnown=false,bonusesKnown=false;
public:
    void setColumn(std::uint16_t column,std::uint16_t value,const std::array<float,6>& values){
        if(column>=4)throw std::out_of_range("455 premium benefit column");
        mask=value;maskKnown=true;
        for(unsigned family=0;family<6;++family){
            //40BB50:testAH,5/JP keeps unordered(NaN) and -0;only less selects0.
            rates[family][column]=values[family]<0.0f?0.0f:values[family];
            knownRates.set(family*4+column);
        }
    }
    float rate(unsigned family,unsigned column)const{
        if(family>=6||column>=4)throw std::out_of_range("455 premium benefit cell");
        if(!knownRates.test(family*4+column))throw std::logic_error("455 premium benefit has no producer");
        return rates[family][column];
    }
    std::uint16_t selectedMask()const{if(!maskKnown)throw std::logic_error("455 premium mask has no producer");return mask;}
    //40BCB0 does not clamp these two combat bonus floats.
    void setCombatBonuses(float attack,float defence){bonuses={attack,defence};bonusesKnown=true;}
    const std::array<float,2>& combatBonuses()const{if(!bonusesKnown)throw std::logic_error("455 premium combat bonuses have no producer");return bonuses;}
};

struct RF455PremiumUpdate {
    std::uint8_t status;
    std::array<std::array<float,2>,6> rates;
    std::array<float,2> combatBonuses;
};
constexpr std::size_t RF455PremiumUpdateBytes=57;
constexpr std::size_t RF455PremiumRatesBytes=49;
//Validate all bytes used by the selected branch before committing state.
//Statuses>2 consume only the status byte and have no state/UI side effects.
inline bool RF455_ReadPremiumUpdate(const void* source,std::size_t bytes,RF455PremiumUpdate& output){
    if(!source||bytes<1)return false;
    const auto* data=static_cast<const unsigned char*>(source);RF455PremiumUpdate value;
    value.status=data[0];
    if(value.status<=2){
        if(bytes<(value.status?RF455PremiumUpdateBytes:RF455PremiumRatesBytes))return false;
        constexpr unsigned offsets[6]={9,17,25,33,41,1};
        for(unsigned family=0;family<6;++family)for(unsigned column=0;column<2;++column)
            std::memcpy(&value.rates[family][column],data+offsets[family]+4*column,4);
        if(value.status)std::memcpy(value.combatBonuses.data(),data+49,8);
        else value.combatBonuses={0.0f,0.0f};
    }
    //Copy only initialized members in the ignored branch.
    output.status=value.status;
    if(value.status<=2){output.rates=value.rates;output.combatBonuses=value.combatBonuses;}
    return true;
}
inline void RF455_ApplyPremiumBenefits(const RF455PremiumUpdate& value,RF455PremiumBenefits& target){
    if(value.status>2)return;
    for(unsigned column=0;column<2;++column){std::array<float,6> rates;
        for(unsigned family=0;family<6;++family)rates[family]=value.rates[family][column];
        target.setColumn(static_cast<std::uint16_t>(column),0xffff,rates);
    }
    if(value.status)target.setCombatBonuses(value.combatBonuses[0],value.combatBonuses[1]);
    else target.setCombatBonuses(0.0f,0.0f);
}
