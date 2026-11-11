#pragma once
#include "client455_normal_item_copy.h"
#include <array>
#include <cstddef>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <stdexcept>

// Source semantics ofthe two200-byte modifier blocks atcondition16and216.
// This is not an overlay ofthe complete private CHARACTER_CONDITION_INFO ABI.
struct RF455ConditionModifiers {
    std::array<std::int32_t,7> attackDistance{},attackSpeed{};
    std::int32_t integer72=0;
    std::array<float,7> power{},hit{},avoid{};
    float defence=0,defenceWithoutShield=0,moveSpeed=0,visualField=0,consumeFP=0;
    std::uint8_t skillLevel=0,padding[3]{};
    std::array<float,7> flatPower{};
    float flatDefence=0;
    void resetEquipment(){
        *this={};power.fill(1);hit.fill(1);avoid.fill(1);
        defence=defenceWithoutShield=consumeFP=1;
    }
};
static_assert(sizeof(RF455ConditionModifiers)==200,"455 modifier block");
static_assert(offsetof(RF455ConditionModifiers,power)==60&&offsetof(RF455ConditionModifiers,hit)==88&&offsetof(RF455ConditionModifiers,avoid)==116,"455 modifier arrays");
static_assert(offsetof(RF455ConditionModifiers,skillLevel)==164&&offsetof(RF455ConditionModifiers,flatPower)==168,"455 modifier tails");

struct RF455ConditionItem {
    RF455ItemDataSpan metadata{},record{};
    bool valid=false;
    explicit RF455ConditionItem(RF455ManagedItem* item){
        if(!item)return;
        if(auto* normal=dynamic_cast<RF455BasicItem*>(item)){metadata=normal->rawMetadata();record=normal->recordBytes();}
        else if(auto* detached=dynamic_cast<RF455DetachedNormalItem*>(item)){metadata=detached->rawMetadata();record=detached->recordBytes();}
        else throw std::logic_error("455 conditions require a normal item payload");
        if(record.size!=200||item->header().kind!=0)throw std::logic_error("455 normal item condition layout");
        valid=item->header().data16!=0;
    }
    template<class T>T field(std::size_t offset)const{
        if(!valid||!metadata.data||offset>metadata.size||sizeof(T)>metadata.size-offset)throw std::out_of_range("455 condition item metadata extent");
        T value;std::memcpy(&value,metadata.data+offset,sizeof(value));return value;
    }
    std::uint8_t kind()const{return valid?field<std::uint8_t>(88):255;}
    bool equipment()const{const auto k=kind();return k>=1&&k<=10;}
    bool armor()const{const auto k=kind();return (k>=1&&k<=5)||k==7||k==8||k==46;}
    bool upgradable()const{return equipment()&&field<std::uint8_t>(160)!=0;}
    bool armourSetFlag()const{return record.data[113]!=0;} //normal virtual68 ->404EA0
    float upgrade(unsigned index)const{
        const auto offset=144+4*std::size_t(index);
        if(offset>record.size||4>record.size-offset)throw std::out_of_range("455 condition upgrade extent");
        float value;std::memcpy(&value,record.data+offset,4);return value;
    }
    std::uint32_t defence()const{return armor()?field<std::uint32_t>(216):0;}
    std::uint32_t weaponCategory()const{return kind()==6?field<std::uint32_t>(216):0xffffffffu;}
    std::uint32_t delay()const{
        const auto k=kind();return equipment()?field<std::uint32_t>(180):(k==40||k==41)?field<std::uint32_t>(224):k==27?field<std::uint32_t>(232):0;
    }
};

// The integer results arethe low DWORD ofthe target's truncating signed64bit
// conversion. Invalid/out-of-range input yields the integer-indefinite low0.
inline std::uint32_t RF455_ConditionWord(double value){
    if(!std::isfinite(value)||value< -9223372036854775808.0||value>=9223372036854775808.0)return 0;
    return static_cast<std::uint32_t>(static_cast<std::int64_t>(value));
}
inline std::int32_t RF455_ConditionSigned(double value){
    const auto bits=RF455_ConditionWord(value);std::int32_t result;std::memcpy(&result,&bits,4);return result;
}

class RF455EquipmentConditionHost {
public:
    virtual ~RF455EquipmentConditionHost()=default;
    virtual bool hasActor()const=0;
    virtual std::uint32_t actorType()const=0;
    virtual bool mountedState2()const=0; //409730,owner byte17820
    virtual bool profileByte17796IsOne()const=0; //407380
    virtual bool globalBonusEnabled()const=0; //442440
    virtual std::array<float,2> globalAvatarBonuses()const=0; //40BCE0
    //44C670 uses the EMBEDDED player processor,not44C630's current processor.
    virtual RF455ManagedItem* basePlayerItem(std::uint8_t)=0;
    virtual void skillLevelChanged(std::uint32_t)=0; //owner virtual252
    virtual void refreshGlobalAvatarInfo()=0; //41A8B0(0),not arbitraryowner UI
};

struct RF455EquipmentConditionTotals {
    std::uint32_t minimumPower=0,maximumPower=0,minimumForce=0,maximumForce=0;
    std::uint32_t defence=0,attackDelay=0;
    float hit=1;
    std::uint8_t weakPart=0;
};

class RF455EquipmentConditions {
    std::array<float,9> setValues;
    std::array<bool,9> setKnown{};
    float mountedDefenceValue;
    bool mountedDefenceKnown=false;
    static float change(float value,float amount,bool add){return static_cast<float>(add?double(value)+amount:double(value)-amount);}
    static void changeInteger(std::int32_t& value,float amount,bool add){value=RF455_ConditionSigned(add?double(value)+amount:double(value)-amount);}
    float setField(unsigned index)const{
        if(index>=168&&index<=176){const auto slot=index-168;if(!setKnown[slot])throw std::logic_error("455 set-effect value has no confirmed producer");return setValues[slot];}
        if(index==177)return extraPower;
        if(index==178)return extraDefence;
        if(index==179)return extra179;
        if(index==180)return extra180;
        throw std::out_of_range("455 set-effect level outside represented storage");
    }
public:
    RF455ConditionModifiers equipment,skillForce;
    RF455EquipmentConditionTotals total;
    std::uint8_t markWeakPoint=0;
    float mountedPower=1,profilePower=1,profileDefence=1;
    std::int32_t selectedAttackSet=0,selectedDefenceSet=0;
    float extraPower=0,extraDefence=0,extra179=0,extra180=0;
    RF455EquipmentConditions(){equipment.resetEquipment();}
    void resetEquipment(){
        equipment.resetEquipment();markWeakPoint=0;mountedPower=profilePower=profileDefence=1;total={};
        //43F6E0 preserves the secondmodifierblock,set levels/set values,
        //extra708..720 andthe uninitialised/preserved mounteddefence456.
    }
    void setMountedDefence(float value){mountedDefenceValue=value;mountedDefenceKnown=true;}
    void setValue(unsigned index,float value){if(index>=setValues.size())throw std::out_of_range("455 set value index");setValues[index]=value;setKnown[index]=true;}
    void special(std::uint8_t code,float amount,bool add,RF455EquipmentConditionHost& host){
        auto& s=equipment;
        switch(code){
        case 2:s.consumeFP=change(s.consumeFP,amount,add);break;
        case 3:for(unsigned i=4;i<7;++i)s.hit[i]=change(s.hit[i],amount,add);break;
        case 4:for(unsigned i=4;i<7;++i)s.avoid[i]=change(s.avoid[i],amount,add);break;
        case 6:for(auto& value:s.power)value=change(value,amount,add);break;
        case 7:case 21:s.defence=change(s.defence,amount,add);break;
        case 8:{const std::int32_t before=s.skillLevel<128?s.skillLevel:int(s.skillLevel)-256;
            s.skillLevel=static_cast<std::uint8_t>(RF455_ConditionWord(add?double(before)+amount:double(before)-amount));
            host.skillLevelChanged((static_cast<std::uint32_t>(before)&0xffffff00u)|s.skillLevel);break;}
        case 12:if(host.actorType()==15)s.moveSpeed=change(s.moveSpeed,amount,add);break;
        case 13:markWeakPoint=static_cast<std::uint8_t>(int(markWeakPoint)+(add?1:-1));break;
        case 15:s.power[3]=change(s.power[3],amount,add);break;
        case 20:changeInteger(s.attackDistance[5],amount,add);break;
        case 24:for(auto& value:s.avoid)value=change(value,amount,add);break;
        case 25:changeInteger(s.integer72,amount,add);break;
        case 26:changeInteger(s.attackDistance[3],amount,add);break;
        case 33:changeInteger(s.attackSpeed[5],amount,add);break;
        case 34:changeInteger(s.attackSpeed[0],amount,add);break;
        case 35:changeInteger(s.attackSpeed[3],amount,add);break;
        case 36:changeInteger(s.attackSpeed[4],amount,add);break;
        default:break;
        }
    }
    void applySpecial(const RF455ConditionItem& item,bool add,RF455EquipmentConditionHost& host){
        if(!host.hasActor())return;
        const bool mount=item.kind()==46;
        const unsigned count=mount?4:item.field<std::uint8_t>(184);
        for(unsigned i=0;i<count;++i){const float value=item.field<float>((mount?184:192)+4*i);
            if(value!=0.0f)special(item.field<std::uint8_t>((mount?177:185)+i),value,add,host);
        }
    }
    void applyUpgrade(const RF455ConditionItem& item,bool add){
        if(!item.upgradable())return;
        if(item.kind()==6)for(auto& value:equipment.power)value=change(value,item.upgrade(0),add);
        for(unsigned i=0;i<7;++i){equipment.avoid[i]=change(equipment.avoid[i],item.upgrade(6),add);equipment.hit[i]=change(equipment.hit[i],item.upgrade(7),add);}
    }
    void combine(RF455EquipmentConditionHost& host){
        if(!host.hasActor())return;
        const auto type=host.actorType();
        if(type==0||type==15){
            total.minimumPower=total.maximumPower=total.minimumForce=total.maximumForce=total.attackDelay=0;
            total.hit=static_cast<float>(double(equipment.hit[4])+skillForce.hit[4]);
            float defenceSum=0,flatPower=0,upgradeDefence=1;
            const bool capturedBonus=host.globalBonusEnabled();std::array<float,2> bonuses{};
            if(capturedBonus)bonuses=host.globalAvatarBonuses();
            static const float weights[]={0,.23f,.22f,.18f,.17f,.20f};
            for(unsigned slot=0;slot<=10;++slot){auto* normal=host.basePlayerItem(static_cast<std::uint8_t>(slot));if(!normal)continue;
                RF455ConditionItem item(normal);const auto kind=item.kind();
                if(item.armor()){
                    const float weight=kind>=1&&kind<=5?weights[kind]:1;
                    float factor=static_cast<float>(double(equipment.defence)+skillForce.defence);
                    if(host.mountedState2()){
                        if(!mountedDefenceKnown)throw std::logic_error("455 mounted defence456 has no producer");
                        factor=static_cast<float>(double(mountedDefenceValue)-1.0+factor);
                    }else if(host.profileByte17796IsOne())factor=static_cast<float>(double(profileDefence)-1.0+factor);
                    if(kind!=7)factor=static_cast<float>(double(equipment.defenceWithoutShield)+skillForce.defenceWithoutShield-1.0+factor);
                    if(host.globalBonusEnabled()){
                        if(!capturedBonus)throw std::logic_error("455 bonus enable changed after uncaptured pointer");
                        if(bonuses[1]>0)factor=static_cast<float>(double(factor)+bonuses[1]);
                    }
                    if(kind!=46)defenceSum=static_cast<float>(double(item.defence())*factor*weight+defenceSum);
                    upgradeDefence=static_cast<float>(double(item.upgrade(1))-1.0+upgradeDefence);
                    if(selectedDefenceSet>0&&item.armourSetFlag()){
                        const float improvement=static_cast<float>(double(setField(unsigned(selectedDefenceSet)+172))-(double(item.upgrade(1))-1.0));
                        if(improvement>0)upgradeDefence=static_cast<float>(double(upgradeDefence)+improvement);
                    }
                    total.attackDelay+=item.delay();
                }else if(kind==6){
                    const auto category=item.weaponCategory();unsigned attack=4;
                    if(category==5||category==6||category==8||category==11)attack=5;else if(category==7)attack=6;
                    float factor=static_cast<float>(double(equipment.power[attack])+skillForce.power[attack]);
                    if(host.mountedState2())factor=static_cast<float>(double(mountedPower)-1.0+factor);
                    else if(host.profileByte17796IsOne())factor=static_cast<float>(double(profilePower)-1.0+factor);
                    if(!host.mountedState2())factor=static_cast<float>(double(factor)+extraPower);
                    if(item.field<std::uint8_t>(152)<3&&selectedAttackSet>0){
                        const float improvement=static_cast<float>(double(setField(unsigned(selectedAttackSet)+167))-item.upgrade(0));
                        if(improvement>0)factor=static_cast<float>(double(factor)+improvement);
                    }
                    if(host.globalBonusEnabled()){
                        if(!capturedBonus)throw std::logic_error("455 bonus enable changed after uncaptured pointer");
                        if(bonuses[0]>0)factor=static_cast<float>(double(factor)+bonuses[0]);
                    }
                    if(factor<0)factor=0;
                    total.minimumPower=RF455_ConditionWord(double(item.field<std::uint32_t>(232))*factor);
                    total.maximumPower=RF455_ConditionWord(double(item.field<std::uint32_t>(236))*factor);
                    const double force=double(equipment.power[3])+skillForce.power[3]+extraPower;
                    if(force>=0){total.minimumForce=RF455_ConditionWord(double(item.field<std::uint32_t>(240))*force);total.maximumForce=RF455_ConditionWord(double(item.field<std::uint32_t>(244))*force);}
                    else total.minimumForce=total.maximumForce=0;
                    flatPower=static_cast<float>(double(equipment.flatPower[attack])+skillForce.flatPower[attack]+flatPower);
                    total.hit=static_cast<float>(double(equipment.hit[attack])+skillForce.hit[attack]);
                }
            }
            if(auto* kit=host.basePlayerItem(27)){
                const float factor=RF455ConditionItem(kit).field<float>(228);
                total.minimumPower=RF455_ConditionWord(double(total.minimumPower)*factor);total.maximumPower=RF455_ConditionWord(double(total.maximumPower)*factor);
            }
            total.minimumPower=RF455_ConditionWord(double(total.minimumPower)+flatPower);total.maximumPower=RF455_ConditionWord(double(total.maximumPower)+flatPower);
            total.minimumForce=RF455_ConditionWord(double(total.minimumForce)+flatPower);total.maximumForce=RF455_ConditionWord(double(total.maximumForce)+flatPower);
            if(defenceSum>=0){const float value=static_cast<float>(((double(upgradeDefence)+extraDefence)*defenceSum+equipment.flatDefence+skillForce.flatDefence)/2.0);total.defence=RF455_ConditionWord(value);}
            else total.defence=0;
        }
        if(type==15)host.refreshGlobalAvatarInfo();
    }
    void findWeakPart(RF455EquipmentConditionHost& host){
        if(!host.hasActor()||(host.actorType()!=0&&host.actorType()!=15))return;
        total.weakPart=1;std::uint32_t minimum=0xffffffffu;
        for(unsigned slot=1;slot<=5;++slot)if(auto* normal=host.basePlayerItem(static_cast<std::uint8_t>(slot))){
            const auto value=RF455ConditionItem(normal).defence();if(value<minimum){minimum=value;total.weakPart=static_cast<std::uint8_t>(slot);}
        }
    }
    bool apply(RF455ManagedItem* normal,bool add,RF455EquipmentConditionHost& host){
        if(!normal)return false;RF455ConditionItem item(normal);const auto kind=item.kind();
        if(!item.equipment()&&kind!=9&&kind!=10&&kind!=27&&kind!=46)return false;
        applySpecial(item,add,host);applyUpgrade(item,add);combine(host);findWeakPart(host);return true;
    }
};
