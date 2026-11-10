#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "item/citemmgr.h"
#include "input/imeedit.h"
#include "baseheader.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "mainapp.h"
#include "client455_premium_state.h"
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <memory>

static void require(bool value,const char* message){if(!value)throw std::runtime_error(message);}
static DWORD bits(float value){DWORD word;std::memcpy(&word,&value,4);return word;}
static float scalar(DWORD word){float value;std::memcpy(&value,&word,4);return value;}
static void put(unsigned char* data,unsigned offset,float value){std::memcpy(data+offset,&value,4);}
struct NetworkAccess final: CNetworkMgr {using CNetworkMgr::AnalysisServerPacket;};
static bool dispatch(NetworkAccess& network,unsigned char* bytes,unsigned size){
    _MSG_HEADER header{};header.m_wSize=static_cast<WORD>(size+4);header.m_byType[0]=57;header.m_byType[1]=12;
    return network.AnalysisServerPacket(&header,reinterpret_cast<char*>(bytes));
}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    std::unique_ptr<NetworkAccess> networkOwner(new NetworkAccess);
    std::unique_ptr<CAvatar> avatarOwner(new CAvatar);
    auto& network=*networkOwner;auto& avatar=*avatarOwner;auto* previous=g_pAvatar;
    struct Restore{CAvatar* previous;~Restore(){g_pAvatar=previous;}}restore{previous};g_pAvatar=&avatar;
    require(network.PremiumState455()==0,"Actual network constructor state");
    network.SetPremiumState455(0x12345678);require(network.PremiumState455()==0x12345678,"FullDWORD state getters/setter");
    auto& benefits=avatar.PremiumBenefits455();bool unknown=false;
    try{benefits.combatBonuses();}catch(const std::logic_error&){unknown=true;}require(unknown,"Unproduced Avatar bonuses unknown");
    unknown=false;try{benefits.rate(0,2);}catch(const std::logic_error&){unknown=true;}require(unknown,"Unwritten columns unknown");
    unsigned char packet[61]{};packet[0]=1;
    const float wire[14]={1.25f,-.5f,2.25f,-2.f,3.25f,-3.f,4.25f,-4.f,5.25f,-5.f,6.25f,-6.f,7.25f,-7.25f};
    std::memcpy(packet+1,wire,sizeof(wire));
    for(unsigned size:{0u,1u,56u})require(!dispatch(network,packet,size)&&network.PremiumState455()==0x12345678,"Truncated active branch leaves state unchanged");
    require(!dispatch(network,nullptr,57),"Null input rejected");
    require(dispatch(network,packet,57)&&network.PremiumState455()==1,"Actual dispatcher activates Premium");
    const float expected[6][2]={{2.25f,0},{3.25f,0},{4.25f,0},{5.25f,0},{6.25f,0},{1.25f,0}};
    for(unsigned family=0;family<6;++family)for(unsigned column=0;column<2;++column)
        require(bits(benefits.rate(family,column))==bits(expected[family][column]),"Independent packet order/clamp oracle");
    require(benefits.selectedMask()==0xffff&&benefits.combatBonuses()[0]==7.25f&&benefits.combatBonuses()[1]==-7.25f,"Actual Avatar raw bonuses/mask");
    benefits.setColumn(2,77,{11,12,13,14,15,16});
    packet[0]=2;put(packet,9,scalar(0x7fc01234));put(packet,17,scalar(0x80000000));
    put(packet,49,scalar(0x7fc05678));put(packet,53,scalar(0xff800000));
    require(dispatch(network,packet,61)&&network.PremiumState455()==1,"Status2 andunused trailingbytes");
    require(bits(benefits.rate(0,0))==0x7fc01234&&bits(benefits.rate(1,0))==0x80000000,"ASM unordered/negativezero rates retained");
    require(bits(benefits.combatBonuses()[0])==0x7fc05678&&bits(benefits.combatBonuses()[1])==0xff800000,"Raw bonus floats notclamped");
    require(benefits.rate(5,2)==16&&benefits.selectedMask()==0xffff,"Packet leaves othercolumns untouched andupdatesmask");
    packet[0]=0;require(!dispatch(network,packet,48)&&network.PremiumState455()==1,"Disabled branch bounds only48ratebytes");
    require(dispatch(network,packet,49)&&network.PremiumState455()==0,"Disabled branch needs49bytes,not57");
    require(bits(benefits.combatBonuses()[0])==0&&bits(benefits.combatBonuses()[1])==0,"Disabled bonuses positivezero");
    require(bits(benefits.rate(0,0))==0x7fc01234,"Disabled packet stillupdates benefit columns");
    for(unsigned char status:{static_cast<unsigned char>(3),static_cast<unsigned char>(255)}){
        packet[0]=status;require(dispatch(network,packet,1)&&network.PremiumState455()==0,"Ignoredstatus consumesonlyonebyte");
    }
    g_pAvatar=nullptr;packet[0]=1;require(!dispatch(network,packet,57)&&network.PremiumState455()==0,"UnboundownAvatar explicitfailure;unsafe targetdomain notaccepted");
    FILE* out=std::fopen("result.json","wb");require(out,"Result output");
    std::fputs("{\"status\":\"PASS\",\"ordinary_network_dispatch\":true,\"actual_Avatar_owner\":true,\"enabled_payload_bytes\":57,\"disabled_payload_bytes\":49,\"ignored_payload_bytes\":1,\"states_checked\":5,\"benefit_cells\":12,\"other_columns_preserved\":true,\"raw_DWORD_state\":true,\"malformed_state_unchanged\":true,\"NaN_and_negativezero_rate_oracles\":true,\"raw_bonus_float_oracles\":true,\"premium_UI_connected\":false,\"post_update_condition_refresh_connected\":false,\"full_handler\":false,\"full_client\":false}\n",out);
    std::fclose(out);return 0;
}
int main(){try{return run();}catch(const std::exception& e){std::fprintf(stderr,"Premium state:%s\n",e.what());return 2;}}
