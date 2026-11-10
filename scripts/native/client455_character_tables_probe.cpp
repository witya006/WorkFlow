#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "item/citemdata.h"
#include "input/imeedit.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "mainapp.h"
#include "client455_client_items.h"
#include "client455_character_tables.h"
#include "client455_nation_paths.h"
#include <cstdio>
#include <cstring>
#include <memory>
#include <stdexcept>
#include <string>

extern CMainApp g_MainApp;
template<class Tag,typename Tag::Type Member>struct MemberAccess{friend typename Tag::Type access(Tag){return Member;}};
struct NetworkMember{using Type=CNetworkMgr CMainApp::*;friend Type access(NetworkMember);};
struct MasteryMember{using Type=BYTE CSFBoard::*;friend Type access(MasteryMember);};
struct SFCountMember{using Type=BYTE CSFBoard::*;friend Type access(SFCountMember);};
template struct MemberAccess<NetworkMember,&CMainApp::m_cNetworkMgr>;
template struct MemberAccess<MasteryMember,&CSFBoard::m_byTotalMasteryNum>;
template struct MemberAccess<SFCountMember,&CSFBoard::m_byTotalSFNum>;
static void require(bool value,const char* text){if(!value)throw std::runtime_error(text);}
class Crc {
    unsigned value=0xffffffff;
public:
    void add(const void* data,std::size_t size){
        static unsigned table[256];static bool initialized=false;
        if(!initialized){for(unsigned i=0;i<256;++i){unsigned n=i;for(unsigned b=0;b<8;++b)n=(n>>1)^((n&1)?0xedb88320:0);table[i]=n;}initialized=true;}
        const auto* p=static_cast<const unsigned char*>(data);for(std::size_t i=0;i<size;++i)value=table[(value^p[i])&255]^(value>>8);
    }
    void word(unsigned n){add(&n,4);}unsigned get()const{return value^0xffffffff;}
};
static unsigned crc(const void* data,std::size_t size){Crc c;c.add(data,size);return c.get();}
static unsigned word(FILE* file){unsigned n=0;require(std::fread(&n,4,1,file)==1,"Expected word");return n;}
static unsigned u32(const void* p){unsigned n;std::memcpy(&n,p,4);return n;}
template<class Table>static void checkTable(const Table& row,const unsigned* expected){
    require(row.count==expected[0]&&row.stride==expected[1]&&crc(row.bytes.data(),row.bytes.size())==expected[2],"Complete actual table count/stride/CRC");
}
static void checkBoard(CSFBoard* board,unsigned packs,unsigned mastery){
    require(board&&board->GetMaxPackNum()==packs&&board->*access(MasteryMember{})==mastery&&board->*access(SFCountMember{})==100,"Actual board dimensions");
    for(unsigned i=0;i<packs;++i)require(board->GetMaxSocketNum455(BYTE(i))==20&&board->FindEmptySocket(BYTE(i))==0,"Actual empty allocated pack");
    require(board->GetEmptySocketNum()==packs*20,"Every actual board socket exists");
}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    require(crc("123456789",9)==0xcbf43926,"Independent CRC convention");
    require(RF455_StoreTablePaths("ko-kr",-1,false).data==".\\DataTable\\Store.edf"&&
        RF455_StoreTablePaths("zh-tw",65535,false).data==".\\DataTable\\Store_65535.edf"&&
        RF455_StoreTablePaths("zh-tw",65535,true).names==".\\DataTable\\zh-tw\\NDStoreW.edf","Exact selector and wide filenames");
    FILE* f=std::fopen("expected.bin","rb");require(f,"Expected file");char magic[4];require(std::fread(magic,1,4,f)==4&&!std::memcmp(magic,"CT43",4),"Expected signature");
    const int selector=static_cast<int>(word(f));unsigned statuses[4],expected[14][3];for(auto& n:statuses)n=word(f);for(auto& row:expected)for(auto& n:row)n=word(f);
    const unsigned descriptions=word(f),animus=word(f);require(std::fgetc(f)==EOF,"Expected extent");std::fclose(f);
    require(RF455_InitializeNationPaths(),"Actual nation path initialization");InitR3Engine();
    auto& network=g_MainApp.*access(NetworkMember{});auto* oldNetwork=g_pNetworkMgr;g_pNetworkMgr=&network;network.m_account455.zoneRequestMode=-1;
    unsigned char reply[12]={};if(selector!=-1){reply[6]=1;reply[7]=static_cast<unsigned char>(selector);reply[8]=static_cast<unsigned char>(unsigned(selector)>>8);}
    require(network.DispatchWorldEntry455(reinterpret_cast<char*>(reply),sizeof(reply))&&network.m_worldEntry455.npcShop==selector,"Actual reply supplies NPC selector");
    auto* oldAvatar=g_pAvatar;auto* oldManager=g_pCharDataMgr;unsigned classes=0,wrappers=0;bool actualStatus[4]={};
    {
        std::unique_ptr<CAvatar> avatar(new CAvatar);g_pAvatar=avatar.get();CCharacterDataMgr manager;g_pCharDataMgr=&manager;
        require(manager.Create()&&manager.LoadData(),"Ordinary CCharacterDataMgr load including failed localizations");
        const auto& tables=manager.Tables455();const auto& data=RF455_GameItems().data;auto& items=RF455_GameItems();
        actualStatus[0]=tables.playerResult;actualStatus[1]=tables.skillResult;actualStatus[2]=tables.storeResult;actualStatus[3]=tables.characterResult;
        for(unsigned i=0;i<4;++i)require(actualStatus[i]==bool(statuses[i]),"Actual loader return values");
        checkTable(tables.players,expected[0]);checkTable(tables.stores,expected[1]);
        for(unsigned i=0;i<5;++i)checkTable(items.skillForce.records()[i],expected[2+i]);
        for(unsigned i=0;i<7;++i)checkTable(data.characterTables()[i],expected[7+i]);
        Crc desc;for(const auto& bytes:tables.storeDescriptions){desc.word(unsigned(bytes.size()));desc.add(bytes.data(),bytes.size());}
        require(desc.get()==descriptions&&manager.GetMaxAnimusTypeNum()==animus&&animus==8,"Store owned descriptions and animus group divisor81");
        checkBoard(manager.GetSkillBoard(),7,12);checkBoard(manager.GetForceBoard(),6,24);
        // Every lookup is compared with a separate scan of the CRC-validated
        // rows. Duplicate codes/indices must return their first occurrence.
        const auto& ct=data.characterTables()[0];
        const auto findCode=[&](const char* code){for(unsigned j=0;j<ct.count;++j){auto row=ct.get(j);if(!std::strcmp(reinterpret_cast<const char*>(row.data+12),code))return row.data;}return static_cast<const unsigned char*>(nullptr);};
        const auto findIndex=[&](unsigned index){for(unsigned j=0;j<ct.count;++j){auto row=ct.get(j);if(u32(row.data+4)==index)return row.data;}return static_cast<const unsigned char*>(nullptr);};
        for(unsigned i=0;i<ct.count;++i){auto row=ct.get(i);require(std::memchr(row.data+12,0,32),"Bounded real class code");const char* code=reinterpret_cast<const char*>(row.data+12);
            require(manager.GetClassData455(code).data==findCode(code)&&manager.GetClassData455ByIndex(u32(row.data+4)).data==findIndex(u32(row.data+4)),"Actual class lookup first matching row");
            std::string changed(code);for(auto& c:changed)if(c>='A'&&c<='Z')c=char(c-'A'+'a');
            require(manager.GetClassData455(changed.c_str()).data==findCode(changed.c_str()),"Case-sensitive class code");++classes;
        }
        require(!manager.GetClassData455(nullptr).data&&!manager.GetClassData455("!missing-class!").data&&!manager.GetClassData455ByIndex(0xffffffff).data,"Missing class and null bounds");
        for(unsigned char subtype:{1,0,2,3,5}){
            const auto span=items.skillForce.get(subtype,0);require(span.data,"Actual SF table mapping");
            {CBoardObject object;auto* payload=items.create(1,subtype,0);require(payload,"Actual typed SF payload");object.SetItem455(payload);
                require(object.GetItemData455()==span.data&&!std::strcmp(object.GetName(),reinterpret_cast<const char*>(span.data+112)),"Actual SF wrapper borrowed row/name");
                {std::unique_ptr<CBoardObject> clone(object.Clone());require(clone&&clone->GetItem455()==payload&&payload->header().references==2,"SF clone retains");}
                require(payload->header().references==1,"SF clone release");}
            require(items.manager.size()==0,"SF last owner releases");++wrappers;
        }
        require(manager.GetTotalSkillNum()==0&&manager.GetTotalForceNum()==0,"Do not reinterpret455rows as legacy SF_DATA");
    }
    g_pCharDataMgr=oldManager;g_pAvatar=oldAvatar;g_pNetworkMgr=oldNetwork;
    FILE* out=std::fopen("result.json","wb");require(out,"Output");
    std::fprintf(out,"{\"status\":\"PASS\",\"selector\":%d,\"loader_results\":[%u,%u,%u,%u],\"tables\":14,\"class_rows\":%u,\"typed_sf_wrappers\":%u,\"all_table_bytes\":true,\"store_owned_descriptions\":true,\"actual_reply_selector\":true,\"actual_skill_force_board_dimensions\":true,\"full_class_equipment_selection\":false}\n",selector,unsigned(actualStatus[0]),unsigned(actualStatus[1]),unsigned(actualStatus[2]),unsigned(actualStatus[3]),classes,wrappers);std::fclose(out);return 0;
}
int main(){try{return run();}catch(const std::exception& error){std::fprintf(stderr,"Character tables: %s\n",error.what());return 2;}}
