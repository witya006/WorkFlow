#include "client455_equipment_conditions.h"
#include <windows.h>
#include <cstdio>
#include <vector>
#include <string>
#include <limits>

static unsigned contracts=0;
static void require(bool value,const char* message){if(!value)throw std::runtime_error(message);++contracts;}
static void checkFloat(float value,float expected,const char* message){require(std::isfinite(value)&&std::abs(value-expected)<0.00001f,message);}
static std::vector<unsigned char> read(const char* path){
    FILE* f=std::fopen(path,"rb");require(f,"Input file");std::fseek(f,0,SEEK_END);const auto length=std::ftell(f);require(length>=0,"Input size");std::rewind(f);std::vector<unsigned char> bytes(static_cast<std::size_t>(length));require(std::fread(bytes.data(),1,bytes.size(),f)==bytes.size(),"Input read");std::fclose(f);return bytes;
}
struct Oracle {
    std::vector<unsigned char> bytes;std::size_t at=0;
    explicit Oracle(const char* path):bytes(read(path)){}
    const unsigned char* take(std::size_t size){require(size<=bytes.size()-at,"Oracle extent");auto* result=bytes.data()+at;at+=size;return result;}
    unsigned word(){unsigned value;std::memcpy(&value,take(4),4);return value;}
    float floating(){float value;std::memcpy(&value,take(4),4);return value;}
    unsigned byte(){return *take(1);}
};
struct Host146:RF455EquipmentConditionHost {
    bool active=true,unit=false,profile=false,bonus=false;unsigned type=15,refreshes=0;
    std::array<float,2> bonuses{};std::array<RF455ManagedItem*,13> slots{};std::vector<unsigned> skills,weakAtRefresh;
    RF455EquipmentConditions* observed=nullptr;
    bool hasActor()const override{return active;}
    std::uint32_t actorType()const override{return type;}
    bool mountedState2()const override{return unit;}
    bool profileByte17796IsOne()const override{return profile;}
    bool globalBonusEnabled()const override{return bonus;}
    std::array<float,2> globalAvatarBonuses()const override{return bonuses;}
    RF455ManagedItem* basePlayerItem(std::uint8_t part)override{part=part==27?11:part==46?9:part;return part<slots.size()?slots[part]:nullptr;}
    void skillLevelChanged(std::uint32_t value)override{skills.push_back(value);}
    void refreshGlobalAvatarInfo()override{++refreshes;if(observed)weakAtRefresh.push_back(observed->total.weakPart);}
};
static RF455BasicItem* item(RF455SourceItemManager& manager,const RF455ItemDataStore& data,unsigned type,unsigned index=0){
    auto* result=dynamic_cast<RF455BasicItem*>(manager.createPayload(data,0,BYTE(type),index));require(result,"Actual normal payload factory");return result;
}
//Controlled owned payload fixtures exercise missing ordinary upgrade producers.
//They never modify original EDFs or present these writes as game integration.
static void upgrade(RF455BasicItem& item,unsigned index,float value){auto data=item.recordBytes();require(data.size==200&&144+4*index+4<=data.size,"Owned fixture upgrade extent");std::memcpy(const_cast<unsigned char*>(data.data)+144+4*index,&value,4);}
static void flag113(RF455BasicItem& item,BYTE value){const auto data=item.recordBytes();const_cast<unsigned char*>(data.data)[113]=value;}
static void frozen(const RF455ItemDataStore& data){
    RF455SourceItemManager manager;Host146 host;host.type=0;RF455EquipmentConditions state;
    checkFloat(state.equipment.power[0],1,"Base rate default1");checkFloat(state.skillForce.power[0],0,"SF block default0");
    state.equipment.skillLevel=127;state.special(8,1.9f,true,host);require(state.equipment.skillLevel==128&&host.skills.back()==128,"Signed skill addition truncates/wraps");
    state.special(8,.9f,true,host);require(state.equipment.skillLevel==129&&host.skills.back()==0xffffff81u,"Skill callback retains prior signed upperbytes");
    state.special(12,2,true,host);checkFloat(state.equipment.moveSpeed,0,"Remote move modifier excluded");host.type=15;state.special(12,2,true,host);checkFloat(state.equipment.moveSpeed,2,"Avatar move modifier included");
    state.special(13,0,false,host);require(state.markWeakPoint==255,"Direct mark modifier ignores value andwraps");
    state.special(20,2.9f,true,host);state.special(20,.9f,false,host);require(state.equipment.attackDistance[5]==1,"Integer modifier truncates eachstep");
    auto* weapon=item(manager,data,6);upgrade(*weapon,0,.5f);upgrade(*weapon,6,.15f);upgrade(*weapon,7,.2f);
    Host146 combined;RF455EquipmentConditions stats;combined.observed=&stats;
    for(unsigned part:{1u,2u,3u,4u,5u,7u,8u})combined.slots[part]=item(manager,data,part);
    combined.slots[6]=weapon;combined.slots[11]=item(manager,data,27);
    stats.skillForce.power[4]=.25f;stats.skillForce.power[3]=.5f;stats.skillForce.hit[4]=.1f;
    stats.equipment.flatPower[4]=3.5f;stats.skillForce.flatPower[4]=1.5f;
    require(stats.apply(weapon,true,combined),"Apply actual fixture normal item");
    require(stats.total.minimumPower==305&&stats.total.maximumPower==608&&stats.total.minimumForce==117&&stats.total.maximumForce==187,"Combined stats/siege-beforeflat conversion goldens");
    require(stats.total.defence==794&&stats.total.attackDelay==280&&stats.total.weakPart==1,"455armour weights/delay/weakpart goldens");checkFloat(stats.total.hit,1.3f,"Combined hit category");checkFloat(stats.equipment.avoid[0],1.15f,"Upgrade avoid propagatesall7categories");
    require(combined.weakAtRefresh.size()==1&&combined.weakAtRefresh[0]==0,"UI refresh precedes weakpart recomputation");
    for(auto row:std::array<std::array<unsigned,3>,3>{{{{1,200,5}},{{2,300,6}},{{3,200,5}}}}){
        Host146 category;category.type=0;category.slots[6]=item(manager,data,6,row[0]);RF455EquipmentConditions value;value.equipment.power[5]=2;value.equipment.power[6]=3;value.equipment.hit[5]=5;value.equipment.hit[6]=6;value.combine(category);
        require(value.total.minimumPower==row[1]&&value.total.hit==float(row[2]),"Actual weapon category routes ranged/launcher");
    }
    Host146 modes;modes.type=0;modes.slots[6]=item(manager,data,6,1);RF455EquipmentConditions mode;mode.extraPower=.25f;mode.mountedPower=2;mode.profilePower=3;
    modes.unit=modes.profile=true;mode.combine(modes);require(mode.total.minimumPower==200&&mode.total.minimumForce==62,"Mounted precedence omits extra physical power,retains force extra");
    modes.unit=false;mode.combine(modes);require(mode.total.minimumPower==325,"Profile multiplier plus extra");modes.profile=false;mode.combine(modes);require(mode.total.minimumPower==125,"Ordinary extra power");
    modes.bonus=true;modes.bonuses={{.5f,-1}};mode.extraPower=0;mode.combine(modes);require(mode.total.minimumPower==150,"Positive global attack bonus");modes.bonuses[0]=-2;mode.combine(modes);require(mode.total.minimumPower==100,"Negative global bonus ignored");
    Host146 armor;armor.type=0;armor.slots[1]=item(manager,data,1);RF455EquipmentConditions armour;
    armor.unit=true;bool refused=false;try{armour.combine(armor);}catch(const std::logic_error&){refused=true;}require(refused,"Unproduced mounteddefence456 staysunknown");
    armour.setMountedDefence(2);armour.combine(armor);require(armour.total.defence==23,"Confirmed mounted defence producer");
    armor.unit=false;armor.profile=true;armour.profileDefence=1.5f;armour.combine(armor);require(armour.total.defence==17,"Profile armour multiplier");
    auto* nonupgradable=item(manager,data,1,1);armor.slots[1]=nonupgradable;armor.profile=false;RF455EquipmentConditions sets;sets.selectedDefenceSet=1;sets.setValue(5,.5f);upgrade(*nonupgradable,1,1.2f);
    require(!RF455ConditionItem(nonupgradable).upgradable(),"Fixture metadata160disabled");sets.combine(armor);require(sets.total.defence==13,"Without runtime byte113 no setimprovement");
    flag113(*nonupgradable,1);sets.combine(armor);require(sets.total.defence==17,"Virtual68byte113 permits setimprovement despite metadata160disabled");
    sets.skillForce.power[0]=.5f;sets.extraPower=.75f;sets.resetEquipment();checkFloat(sets.equipment.power[0],1,"Reset base modifiers");checkFloat(sets.skillForce.power[0],.5f,"Reset preserves SF block");checkFloat(sets.extraPower,.75f,"Reset preserves extra producer");require(sets.selectedDefenceSet==1,"Reset preserves setselector");
    Host146 absent;absent.active=false;RF455EquipmentConditions unbound;require(unbound.apply(weapon,true,absent),"Top item gate doesnot requireactor");checkFloat(unbound.equipment.power[4],1.5f,"Upgrade changes unbound state whilespecial is skipped");require(!absent.refreshes,"No UI forabsentowner");
    Host146 zero;RF455EquipmentConditions zeroState;auto* emptyOption=item(manager,data,9,1);require(zeroState.apply(emptyOption,true,zero)&&zero.skills.empty(),"Zero-valued metadata option skipped beforecallback");
    {
        RF455SourceItemManager owned;auto* original=item(owned,data,6);upgrade(*original,0,.5f);Host146 owner;owner.slots[6]=original;RF455EquipmentConditions value;require(value.apply(original,true,owner),"Clone test apply");
        RF455DetachedNormalItem snapshot(*original);owner.slots[6]=nullptr;owned.clear();require(value.apply(&snapshot,false,owner),"Detached snapshot survives original payload release");checkFloat(value.equipment.power[4],1,"Detached removal reverses special+upgrade");
    }
    require(RF455_ConditionWord(-1.9)==0xffffffff&&RF455_ConditionWord(4294967297.5)==1&&RF455_ConditionWord(std::numeric_limits<double>::quiet_NaN())==0,"Signed64truncation lowDWORD boundaries");
}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    auto fixedBytes=read("fixture.edf");RF455ItemDataStore fixtures;require(fixtures.loadItemEdf(fixedBytes.data(),fixedBytes.size(),false),"Own encrypted fixed fixture load");frozen(fixtures);
    const unsigned frozenContracts=contracts;auto realBytes=read("DataTable/Item.edf");RF455ItemDataStore real;require(real.loadItemEdf(realBytes.data(),realBytes.size(),true),"Actual455Item.edf");RF455SourceItemManager manager;Oracle expected("expected.bin");require(!std::memcmp(expected.take(4),"EC46",4),"Expected signature");const auto cases=expected.word();unsigned accepted=0;
    for(unsigned i=0;i<cases;++i){const auto type=expected.word(),index=expected.word(),accept=expected.word();auto* normal=item(manager,real,type,index);Host146 host;RF455EquipmentConditions value;host.observed=&value;const auto kind=RF455ConditionItem(normal).kind();
        if(kind<=8)host.slots[kind]=normal;else if(kind==46)host.slots[9]=normal;else if(kind==27)host.slots[11]=normal;
        require(value.apply(normal,true,host)==bool(accept),"Actual metadata top gate");accepted+=accept;
        const auto* block=expected.take(200);if(std::memcmp(&value.equipment,block,200)){std::fprintf(stderr,"Modifier mismatch type%u/index%u\n",type,index);throw std::runtime_error("Independent real modifier bytes");}
        require(value.markWeakPoint==expected.byte(),"Actual mark counter");const auto callbacks=expected.word();require(host.skills.size()==callbacks,"Actual skillcallback count");for(unsigned j=0;j<callbacks;++j)require(host.skills[j]==expected.word(),"Actual skillcallback bits");
        const std::array<unsigned,6> totals={{value.total.minimumPower,value.total.maximumPower,value.total.minimumForce,value.total.maximumForce,value.total.defence,value.total.attackDelay}};
        for(auto actual:totals){const auto wanted=expected.word();if(actual!=wanted){std::fprintf(stderr,"Totals mismatch type%u/index%u actual%u expected%u\n",type,index,actual,wanted);throw std::runtime_error("Independent real total");}}
        checkFloat(value.total.hit,expected.floating(),"Actual total hit");require(value.total.weakPart==expected.byte(),"Actual weakpart");require(host.refreshes==accept,"UI refresh onlyforacceptedAvataritem");
    }
    require(expected.at==expected.bytes.size(),"Oracle completely consumed");manager.clear();
    FILE* out=std::fopen("result.json","wb");require(out,"Output");std::fprintf(out,"{\"status\":\"PASS\",\"frozen_contracts\":%u,\"real_item_cases\":%u,\"accepted_items\":%u,\"modifier_bytes_match_independent_oracle\":true,\"totals_match_independent_oracle\":true,\"set_predicate_is_runtime_byte113\":true,\"detached_remove_after_payload_release\":true,\"owner_callbacks_are_recorders\":true,\"ordinary_player_connected\":false,\"full_conditions_or_gameplay\":false}\n",frozenContracts,cases,accepted);std::fclose(out);return 0;
}
int main(){try{return run();}catch(const std::exception& error){std::fprintf(stderr,"Equipment conditions146:%s\n",error.what());return 2;}}
