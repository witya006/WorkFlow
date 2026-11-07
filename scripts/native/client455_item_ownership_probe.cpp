#include "client455_item_ownership.h"
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <list>
#include <stdexcept>
#include <string>
#include <vector>

static void require(bool value,const char* text){if(!value)throw std::runtime_error(text);}
static std::vector<unsigned char> read(const char* name){
    FILE* f=std::fopen(name,"rb");require(f!=nullptr,"fixture open");
    std::vector<unsigned char> bytes;int c;
    while((c=std::fgetc(f))!=EOF)bytes.push_back(static_cast<unsigned char>(c));
    std::fclose(f);return bytes;
}
template<class T>static void equals(const T& record,const char* fixture){
    auto expected=read(fixture);
    require(expected.size()==sizeof(record)&&std::memcmp(&record,expected.data(),sizeof(record))==0,"whole-record oracle");
}
struct Allocator {
    bool fail=false;unsigned calls=0;std::size_t bytes=0;
    static void* allocate(void* context,std::size_t bytes){
        auto& a=*static_cast<Allocator*>(context);++a.calls;a.bytes=bytes;
        if(a.fail)return nullptr;
        void* memory=std::malloc(bytes);require(memory!=nullptr,"own fixture allocation");
        std::memset(memory,0xdd,bytes);return memory;
    }
};
// Recording host for the required manager/virtual-predicate boundary. These
// are owned header fixtures,not the complete target derived item factories.
struct Host final:RF455ItemOwnershipHost {
    std::list<RF455ItemHeader*> primary,gestures;
    std::vector<std::string> events;
    unsigned primaryErases=0,gestureErases=0,destroyed=0;
    std::vector<unsigned> referencesAtErase;
    ~Host(){for(auto* p:primary)delete p;for(auto* p:gestures)delete p;}
    RF455ItemHeader* make(unsigned kind,unsigned count,bool gesture=false){
        auto* p=new RF455ItemHeader;std::memset(p,0xa5,sizeof(*p));
        RF455_InitializeItemHeader(*p,0x12340000+kind);p->kind=static_cast<std::uint8_t>(kind);
        p->references=static_cast<std::uint8_t>(count);(gesture?gestures:primary).push_back(p);return p;
    }
    bool primaryCacheEmpty()override{events.push_back("empty");return primary.empty();}
    bool itemIsKind(RF455ItemHeader* p,std::uint8_t kind)override{
        events.push_back("kind"+std::to_string(unsigned(kind)));return p->kind==kind;
    }
    void erase(std::list<RF455ItemHeader*>& list,RF455ItemHeader* p){
        auto at=std::find(list.begin(),list.end(),p);if(at==list.end())return;
        referencesAtErase.push_back(p->references);delete *at;*at=nullptr;list.erase(at);++destroyed;
    }
    void erasePrimary(RF455ItemHeader* p)override{events.push_back("primary");++primaryErases;erase(primary,p);}
    void eraseGesture(RF455ItemHeader* p)override{events.push_back("gesture");++gestureErases;erase(gestures,p);}
};

int main(){try{
    RF455ItemHeader initialized;std::memset(&initialized,0xa5,sizeof(initialized));
    RF455_InitializeItemHeader(initialized,0x10203040);equals(initialized,"header-initialized.bin");
    auto input=read("header-source.bin");require(input.size()==92,"item input");
    RF455ItemHeader original,copied;std::memcpy(&original,input.data(),92);std::memset(&copied,0xcc,92);
    RF455_CopyItemHeader(copied,original,0x55667788);equals(copied,"header-copied.bin");
    RF455_RetainItem(initialized);require(initialized.references==1,"retain");
    initialized.references=255;RF455_RetainItem(initialized);require(initialized.references==0,"retain wraps");
    RF455_DropItemReference(initialized);require(initialized.references==255&&RF455_ItemReferenceNonpositive(initialized),"drop wraps/signed query");
    auto boardInput=read("board-source.bin");require(boardInput.size()==620,"board input");
    RF455BoardItemRecord origin,boardCopy;std::memcpy(&origin,boardInput.data(),620);std::memset(&boardCopy,0xdd,620);
    RF455_CopyBoardItemRecord(boardCopy,origin,0x90abcdef);equals(boardCopy,"board-copied.bin");
    Allocator allocator;
    auto* emptyClone=RF455_CloneBoardItemRecord(origin,0x90abcdef,&allocator,Allocator::allocate);
    require(emptyClone&&allocator.calls==1&&allocator.bytes==620&&!emptyClone->item,"clone allocation/null item");
    equals(*emptyClone,"board-copied.bin");std::free(emptyClone);
    unsigned scenarios=0;
    {
        Host host;origin.item=host.make(0,1);origin.item->serial=0x12345678;origin.usingState=0;
        auto* link=RF455_CloneBoardItemRecord(origin,0x90abcdef,&allocator,Allocator::allocate);
        require(link&&link!=&origin&&link->item==origin.item&&origin.item->references==2,"owned wrapper/shared item");
        link->usingState=1;require(origin.usingState==0,"independent wrapper state");
        origin.item->serial=0x87654321;require(link->item->serial==0x87654321,"shared underlying mutation");
        require(RF455_ReleaseBoardItemReference(*link,host)&&!link->item&&origin.item->references==1,"unlink retains origin");
        require(host.events==std::vector<std::string>{"empty"},"positive count skips removal/predicate");
        host.events.clear();require(RF455_ReleaseBoardItemReference(origin,host)&&!origin.item,"last wrapper release");
        require(host.events==std::vector<std::string>({"empty","kind6","primary"})&&host.destroyed==1,"last owner manager route/order");
        std::free(link);++scenarios;
    }
    {
        Host host;RF455BoardItemRecord object={};object.item=host.make(6,1,true);auto* item=object.item;
        require(!RF455_ReleaseBoardItemReference(object,host)&&object.item==item&&item->references==1,"primary cache empty must preserve gesture pointer/count");
        require(host.events==std::vector<std::string>{"empty"},"empty guard before all other effects");
        host.make(0,0);host.events.clear();require(RF455_ReleaseBoardItemReference(object,host)&&!object.item,"gesture release with nonempty primary");
        require(host.events==std::vector<std::string>({"empty","kind6","gesture"})&&host.gestureErases==1&&host.destroyed==1,"gesture auxiliary cache route");++scenarios;
    }
    const unsigned start[]={0,1,2,127,128,129,255};
    const unsigned after[]={255,0,1,126,127,128,254};
    const bool erase[]={true,true,false,false,false,true,true};
    for(unsigned i=0;i<7;++i){
        Host host;RF455BoardItemRecord object={};object.item=host.make(0,start[i]);auto* item=object.item;
        require(RF455_ReleaseBoardItemReference(object,host)&&!object.item,"reference boundary clears wrapper");
        require(bool(host.primaryErases)==erase[i],"independent signed-byte release table");
        if(erase[i])require(host.referencesAtErase==std::vector<unsigned>{after[i]},"counter observed before deletion");
        else require(item->references==after[i]&&host.destroyed==0,"positive reference kept");++scenarios;
    }
    {
        Host host;host.make(0,0);RF455BoardItemRecord object={};
        require(!RF455_ReleaseBoardItemReference(object,host)&&host.events==std::vector<std::string>{"empty"},"null pointer after cache query");++scenarios;
    }
    {
        Host host;host.make(0,0);RF455ItemHeader unregistered={};unregistered.references=1;
        RF455BoardItemRecord object={};object.item=&unregistered;
        require(RF455_ReleaseBoardItemReference(object,host)&&!object.item&&unregistered.references==0&&host.primaryErases==1&&host.destroyed==0,"manager miss still clears wrapper");++scenarios;
    }
    {
        Host host;origin.item=host.make(1,1);allocator.fail=true;
        require(!RF455_CloneBoardItemRecord(origin,1,&allocator,Allocator::allocate)&&origin.item->references==1,"failed allocation must not retain");
        bool rejected=false;try{RF455_CloneBoardItemRecord(origin,1,nullptr,nullptr);}catch(const std::invalid_argument&){rejected=true;}
        require(rejected,"missing own allocator is an explicit boundary");origin.item=nullptr;++scenarios;
    }
    FILE* out=std::fopen("result.json","wb");require(out!=nullptr,"result file");
    std::fprintf(out,"{\"status\":\"PASS\",\"item_record_bytes\":92,\"wrapper_record_bytes\":620,\"whole_record_oracles\":3,"
        "\"lifetime_scenarios\":%u,\"ref_boundary_cases\":7,\"primary_empty_guard\":true,\"signed_byte_release\":true,"
        "\"shared_payload\":true,\"independent_wrapper_state\":true,\"allocation_failure\":true,"
        "\"recording_host\":true,\"ordinary_Linker_bound\":false,\"actual_item_factory\":false,\"real_item_destructors\":false}\n",scenarios);
    std::fclose(out);return 0;
}catch(const std::exception& error){std::fprintf(stderr,"Item ownership:%s\n",error.what());return 1;}}
