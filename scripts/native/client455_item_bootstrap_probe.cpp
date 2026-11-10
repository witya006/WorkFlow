#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "datatable/citemdatamgr.h"
#include "item/citemdata.h"
#include "input/imeedit.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "mainapp.h"
#include "client455_item_bootstrap.h"
#include "client455_nation_paths.h"
#include <cstdio>
#include <cstring>
#include <memory>
#include <stdexcept>

extern CMainApp g_MainApp;
template<class Tag,typename Tag::Type Member>struct MemberAccess{friend typename Tag::Type access(Tag){return Member;}};
struct NetworkMember{using Type=CNetworkMgr CMainApp::*;friend Type access(NetworkMember);};
template struct MemberAccess<NetworkMember,&CMainApp::m_cNetworkMgr>;
static void require(bool value,const char* text){if(!value)throw std::runtime_error(text);}
class Crc {
    unsigned value=0xffffffff;
public:
    void add(const void* data,std::size_t size){
        static unsigned table[256];static bool initialized=false;
        if(!initialized){for(unsigned i=0;i<256;++i){unsigned n=i;for(unsigned bit=0;bit<8;++bit)n=(n>>1)^((n&1)?0xedb88320:0);table[i]=n;}initialized=true;}
        const auto* p=static_cast<const unsigned char*>(data);for(std::size_t i=0;i<size;++i)value=table[(value^p[i])&255]^(value>>8);
    }
    void word(unsigned n){add(&n,4);}
    unsigned get()const{return value^0xffffffff;}
};
static unsigned crc(const void* data,std::size_t size){Crc c;c.add(data,size);return c.get();}
static unsigned word(FILE* file){unsigned n=0;require(std::fread(&n,4,1,file)==1,"Expected word");return n;}
static unsigned descriptionCrc(const RF455ItemDataStore& data){
    Crc c;for(const auto& group:data.itemDescriptions()){c.word(unsigned(group.size()));for(const auto& value:group){c.word(value.index);c.word(value.code);c.word(unsigned(value.bytes.size()));c.add(value.bytes.data(),value.bytes.size());}}
    c.word(unsigned(data.dungeonDescriptions().size()));for(const auto& value:data.dungeonDescriptions()){c.word(value.index);c.add(value.name.data(),64);c.word(unsigned(value.bytes.size()));c.add(value.bytes.data(),value.bytes.size());}return c.get();
}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    require(crc("123456789",9)==0xcbf43926,"Independent CRC convention");
    require(RF455_ItemCashPaths("ko-kr",-1).data==".\\DataTable\\ItemCash.edf"&&
        RF455_ItemCashPaths("zh-tw",65535).names==".\\DataTable\\zh-tw\\NDItemCash_65535.edf"&&
        RF455_ItemCashPaths("ru-ru",0).data==".\\DataTable\\ItemCash_0.edf","Exact selector filenames");
    FILE* file=std::fopen("expected.bin","rb");require(file,"Expected file");char magic[4];require(std::fread(magic,1,4,file)==4&&!std::memcmp(magic,"IB42",4),"Expected signature");
    const int selector=static_cast<int>(word(file));unsigned cash[4],set[4],tables[47][3];for(auto& n:cash)n=word(file);for(auto& n:set)n=word(file);for(auto& table:tables)for(auto& n:table)n=word(file);
    const unsigned work=word(file),descriptions=word(file),consumed=word(file),expectedRows=word(file);require(std::fgetc(file)==EOF,"Expected extent");std::fclose(file);
    require(RF455_InitializeNationPaths(),"Actual nation path initialization");
    auto& network=g_MainApp.*access(NetworkMember{});auto* previous=g_pNetworkMgr;g_pNetworkMgr=&network;
    network.m_account455.zoneRequestMode=-1;
    unsigned char reply[12]={};if(selector!=-1){reply[3]=1;reply[4]=static_cast<unsigned char>(selector);reply[5]=static_cast<unsigned char>(unsigned(selector)>>8);}
    require(network.DispatchWorldEntry455(reinterpret_cast<char*>(reply),sizeof(reply))&&network.m_worldEntry455.cashShop==selector,"Actual world reply supplies cash selector");
    CItemDataMgr manager;require(manager.Create()&&manager.LoadBootstrap455(),"Ordinary ItemDataMgr initial bootstrap");
    auto& items=RF455_GameItems();
    require(items.cashLoadResult==bool(cash[0])&&items.cash.count==cash[1]&&items.cash.stride==cash[2]&&crc(items.cash.bytes.data(),items.cash.bytes.size())==cash[3],"Actual cash records/localized DWORD16");
    require(items.setEffectLoadResult==bool(set[0])&&items.setEffect.count==set[1]&&items.setEffect.stride==set[2]&&crc(items.setEffect.bytes.data(),items.setEffect.bytes.size())==set[3],"Actual set-effect records");
    unsigned rows=0,objects=0;
    for(unsigned kind=0;kind<47;++kind){const auto& table=items.data.itemTables()[kind];
        require(table.count==tables[kind][0]&&table.stride==tables[kind][1]&&crc(table.bytes.data(),table.bytes.size())==tables[kind][2],"All actual localized Item47 table bytes");rows+=table.count;
        require(!manager.GetData455(kind,table.count).data,"Typed row boundary");
        if(table.count&&objects<12){const auto span=manager.GetData455(kind,0);require(span.data==table.bytes.data()&&span.size==table.stride,"Ordinary typed borrowed row");
            {CBoardObject object;auto* payload=items.create(0,static_cast<BYTE>(kind),0);require(payload,"Actual typed payload factory");object.SetItem455(payload);
                require(object.GetItemData455()==span.data&&!std::strcmp(object.GetName(),reinterpret_cast<const char*>(span.data+8)),"Real item wrapper name/data");
                {std::unique_ptr<CBoardObject> clone(object.Clone());require(clone&&clone->GetItem455()==payload&&payload->header().references==2,"Actual cloned item retains");}
                require(payload->header().references==1,"Clone release keeps original");}
            require(items.manager.size()==0,"Last owner releases actual payload");++objects;
        }
    }
    require(rows==expectedRows&&rows==76049&&objects==12&&!manager.GetData455(47,0).data,"Item corpus/typed wrappers/bounds");
    Crc directory;directory.add(items.data.itemWorkStarts().data(),47*4);directory.add(items.data.itemWorkCounts().data(),47*4);
    require(directory.get()==work&&descriptionCrc(items.data)==descriptions&&items.data.localizedBytesConsumed()==consumed,"Work directory/descriptions/dungeons complete bytes");
    g_pNetworkMgr=previous;
    FILE* out=std::fopen("result.json","wb");require(out,"Output");
    std::fprintf(out,"{\"status\":\"PASS\",\"selector\":%d,\"cash_loaded\":%s,\"cash_rows\":%u,\"set_effect_rows\":%u,\"item_tables\":47,\"item_rows\":%u,\"actual_typed_wrappers\":%u,\"all_table_description_bytes\":true,\"actual_reply_selector\":true,\"full_bootstrap_or_legacy_consumers\":false}\n",selector,items.cashLoadResult?"true":"false",items.cash.count,items.setEffect.count,rows,objects);std::fclose(out);return 0;
}
int main(){try{return run();}catch(const std::exception& error){std::fprintf(stderr,"Item bootstrap: %s\n",error.what());return 2;}}
