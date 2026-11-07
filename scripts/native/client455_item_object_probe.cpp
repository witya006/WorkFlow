#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "input/imeedit.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "mainapp.h"
#include "client455_item_object.h"
#include <cstdio>
#include <cstring>
#include <memory>
#include <new>
#include <stdexcept>

static void check(bool okay,const char* why){if(!okay)throw std::runtime_error(why);}
static std::vector<unsigned char> read(const char* name){FILE* f=std::fopen(name,"rb");check(f!=nullptr,"fixture open");std::fseek(f,0,SEEK_END);long n=std::ftell(f);check(n>=0,"fixture length");std::rewind(f);std::vector<unsigned char> out(static_cast<std::size_t>(n));check(std::fread(out.data(),1,out.size(),f)==out.size(),"fixture read");std::fclose(f);return out;}
static unsigned word(const unsigned char* p){unsigned v;std::memcpy(&v,p,4);return v;}
static void compare(const void* data,const char* file,bool timestamp){auto expected=read(file);std::vector<unsigned char> actual(static_cast<const unsigned char*>(data),static_cast<const unsigned char*>(data)+620);const unsigned dispatch=0xc0455000,time=0x01020304;std::memcpy(actual.data(),&dispatch,4);if(timestamp)std::memcpy(actual.data()+244,&time,4);check(actual==expected,"independent whole620byte oracle");}
template<class Tag,typename Tag::Type Member>struct Access{friend typename Tag::Type access(Tag){return Member;}};
struct Packs{using Type=CObjectPack* CObjectBoard::*;friend Type access(Packs);};template struct Access<Packs,&CObjectBoard::m_listItemPack>;

int main(){try{
    check(sizeof(CItemObject)==592&&sizeof(CBoardObject)==620,"actual typed class sizes");
    alignas(CBoardObject) unsigned char storage[620],sourceStorage[620],copyStorage[620];std::memset(storage,0xa5,620);
    auto* placed=new(storage) CBoardObject;compare(placed,"board-constructed.bin",true);placed->~CBoardObject();
    auto* source=new(sourceStorage) CBoardObject;auto pattern=read("board-copy-source.bin");std::memcpy(sourceStorage+4,pattern.data()+4,616);
    std::memset(copyStorage,0xcc,620);auto* copy=new(copyStorage) CBoardObject(*source);compare(copy,"board-copied.bin",false);
    source->SetEffectID(0,0);source->SetEffectID(1,0);copy->SetEffectID(0,0);copy->SetEffectID(1,0);copy->~CBoardObject();source->~CBoardObject();
    auto& runtime=RF455_GameItems();check(runtime.manager.size()==0&&runtime.loadFiles("item.edf","nd-zh-tw.edf","quest.edf","character.edf","base.edf","zh-tw.edf"),"actual CMainApp game-global manager/data load");
    CLinkBoard container;container.Create(6,1,2);check(container.AddPack(0),"actual board creates pack");auto& pack=(container.*access(Packs{}))[0];
    unsigned owned=0,sfCount=0,physicalCount=0,questRefused=0;
    auto exercise=[&](RF455ManagedItem* payload){
        check(payload&&runtime.manager.size()==1,"real registered factory payload");
        std::unique_ptr<CBoardObject> origin(new CBoardObject);origin->SetItem455(payload);check(origin->GetItem455()==payload&&payload->header().references==1,"actual binding retains");
        check(origin->GetIndex()==payload->header().serial&&origin->GetServerIndex()==payload->header().field8&&std::strcmp(origin->GetName(),payload->name())==0&&origin->GetItemData455()==reinterpret_cast<const void*>(payload->header().data16),"real resource fields/name/data");
        origin->SetUsingState(255);auto* duplicate=origin->Clone();check(duplicate&&duplicate->GetItem455()==payload&&payload->header().references==2&&duplicate->IsUsing()==255&&origin->IsEqual(duplicate),"actual typed clone shares item");
        unsigned reference=0xffffffff;
        if(payload->header().kind==0)reference=0x04000000|origin->GetServerIndex();
        else if(auto* sf=dynamic_cast<RF455SkillForceItem*>(payload))reference=(unsigned(sf->record().subtype)<<24)|sf->tableIndex();
        else if(payload->header().kind==2)reference=0x03000000|static_cast<RF455BasicItem*>(payload)->tableIndex();
        check(CLinkBoard::HotbarReference455(origin.get())==reference&&CLinkBoard::HotbarReference455(duplicate)==reference,"independent ordinary typed hotbar key");
        check(pack.Add(0,origin.get())&&pack.Add(1,duplicate),"actual source pack insertion");origin.release();
        if(owned&1){check(pack.Remove(0)&&runtime.manager.size()==1&&duplicate->GetItem455()->header().references==1,"origin removal retains clone");check(pack.Remove(1)&&runtime.manager.size()==0,"clone last-owner removal");}
        else{auto* survivor=pack.GetObject(0);check(pack.Remove(1)&&runtime.manager.size()==1&&survivor->GetItem455()->header().references==1,"clone removal retains origin");check(pack.Remove(0)&&runtime.manager.size()==0,"origin last-owner removal");}
        ++owned;
    };
    const unsigned types[]={1,0,2,3,5};
    for(unsigned frame=0;frame<5;++frame)for(unsigned i=0;i<runtime.skillForce.records()[frame].count;++i){exercise(runtime.create(1,static_cast<BYTE>(types[frame]),i));++sfCount;}
    auto cases=read("cases.bin");check(std::memcmp(cases.data(),"IP89",4)==0,"factory oracle");std::size_t at=8;
    for(unsigned i=0;i<word(cases.data()+4);++i){check(at+32<=cases.size(),"factory header bounds");const auto* row=cases.data()+at;const unsigned selector=word(row),type=word(row+4),index=word(row+8),size=word(row+16),quest=word(row+24),unsafe=word(row+28);at+=32+2*size+64;check(at<=cases.size()&&!unsafe,"factory case extent/domain");
        auto* payload=runtime.create(static_cast<BYTE>(selector),static_cast<BYTE>(type),index);
        if(quest){bool refused=false;{CBoardObject object;try{object.SetItem455(payload);}catch(const std::logic_error&){refused=true;}}check(refused&&runtime.manager.size()==0,"unrestored Quest sentence provider explicit and no owner leak");++questRefused;}
        else{exercise(payload);++physicalCount;}
    }
    check(at==cases.size()&&sfCount==1447&&physicalCount==566&&questRefused==9&&owned==2013,"all selected actual owners");
    {auto* payload=runtime.create(1,1,0);CItemObject base;base.SetItem455(payload);check(base.IsEmpty()&&payload->header().references==1,"base setter does not copy board ID");base.Clear();check(!base.GetItem455()&&runtime.manager.size()==0,"base clear");}
    {auto* payload=runtime.create(1,1,0);CBoardObject object;object.SetItem455(payload);const auto* retired=object.GetItem455();runtime.manager.clear();object.Clear();check(object.IsEmpty()&&object.GetItem455()==retired,"primary-empty guard precedes retired payload dereference");}
    for(unsigned prior: {0u,1u,2u,127u,128u,129u,255u}){
        auto* payload=runtime.create(1,1,0);CBoardObject object;object.SetItem455(payload);payload->header().references=static_cast<BYTE>(prior);const auto next=static_cast<BYTE>(prior-1);const bool removed=!next||next>=128;
        object.Clear();check(!object.GetItem455()&&runtime.manager.size()==(removed?0:1),"actual signed BYTE boundary/manager removal");if(!removed)check(payload->header().references==next,"actual wrapped reference counter");runtime.manager.clear();
    }
    {CBoardObject one,two;check(!one.IsEqual(&two)&&!one.IsEqual(static_cast<CBoardObject*>(nullptr)),"null payload identity is never equal");}
    {auto* payload=runtime.create(1,1,0);CSFItem legacy;bool refused=false;try{legacy.SetItem455(payload);}catch(const std::logic_error&){refused=true;}check(refused&&!legacy.GetItem455()&&payload->header().references==0,"unported mixed consumer binding explicit");runtime.manager.erasePrimary(&payload->header());}
    {auto* payload=runtime.create(1,1,0);CBoardObject object;object.SetItem455(payload);CGUIItem icon;bool refused=false;try{object.SetIcon(&icon);}catch(const std::logic_error&){refused=true;}check(refused,"missing real icon provider explicit");object.SetIcon(nullptr);}
    check(runtime.manager.size()==0,"all ordinary owners released");
    FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"result");std::fprintf(out,"{\"status\":\"PASS\",\"CItemObject_size\":592,\"CBoardObject_size\":620,\"whole_record_oracles\":2,\"real_SF_owners\":%u,\"real_other_owners\":%u,\"cloned_wrappers\":%u,\"Quest_name_refusals\":%u,\"actual_game_global_manager\":true,\"actual_source_pack_removal\":true,\"primary_empty_retired_guard\":true,\"signed_BYTE_cases\":7,\"ordinary_hotbar_metadata\":true,\"icon_provider\":false,\"normal_bootstrap_load\":false,\"full_Linker_ownership\":false,\"full_client\":false}\n",sfCount,physicalCount,owned,questRefused);std::fclose(out);return 0;
}catch(const std::exception& e){std::fprintf(stderr,"Item object:%s\n",e.what());return 1;}}
