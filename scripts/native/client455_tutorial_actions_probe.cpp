#include "client455_tutorial_actions.h"
#include "testing/client455_tutorial_recording_host.h"
#include <cstdio>
#include <algorithm>
#include <cstring>
#include <fstream>
#include <map>
#include <stdexcept>

static void check(bool value,const char* reason){if(!value)throw std::runtime_error(reason);}
using BaseHost=RF455TutorialRecordingSpatialHost<RF455TutorialActionsHost>;
struct Host final : BaseHost {
    std::map<unsigned,bool> boards,special;
    bool ui25Found=true,equipFound=true,busy=false,offsetCursor=true,freeSlot=true,stackable=true,memberSlot=true,linked=false;
    std::array<bool,256> equipment{};
    RF455TutorialSlot candidate{2,3};
    RF455TutorialPoint cursorPointNow{},systemPoint{},motionPoint{},origin{100,200};
    RF455TutorialPointResult uiPoint{true,true,{500,600}};
    RF455TutorialProjection projection{1,12.9f,20.9f};
    RF455TutorialObject projectionObject=600,lockTarget=900,foundObject=701,innerItem=501,hotbar=801;
    std::uint32_t lockType=1,lockIndex=0x12345,inputEnabled=0,defaultValue=17,countValue=0,itemValue=0;
    std::uint32_t skillCode=88,ready112=0,identity=1234,hotbarIdentity=1234;
    std::uint16_t serial=0;
    std::uint8_t race=3,lastMapped=0,lastHotbarSlot=0,lastCategory=0;
    std::int32_t mouseValue=0;
    unsigned notices=0,equipQueries=0,busyQueries=0,motions=0,systems=0,skillQueries=0,traceItems=0,traceLocks=0;
    bool skillFound=true;
    bool pointDefault=false;
    std::uint8_t pointWindow=0;
    std::uint32_t pointElement=0;
    void event(const std::string& value){calls.push_back(value);}
    void openBoard(unsigned b,bool value) override {check(value,"open arg");boards[b]=true;event("open"+std::to_string(b));}
    void closeBoard(unsigned b,bool value) override {check(value,"close arg");boards[b]=false;event("close"+std::to_string(b));}
    bool boardOpen(unsigned b) override {event("is-open"+std::to_string(b));return boards[b];}
    void selectInventoryPage(std::uint8_t page,bool value) override {check(page==0&&value,"inventory page");event("inventory-page");}
    RF455TutorialObject boardWindow(unsigned b) override {event("window"+std::to_string(b));return 1000+b;}
    void updateSkillTab(RF455TutorialObject w,std::uint8_t page,std::uint8_t item,bool value) override {
        check((w==1007||w==1003)&&!page&&!item&&value,"skill tab args");event("tab-update");
    }
    void selectSkillTab(RF455TutorialObject w,std::uint8_t page) override {check((w==1007||w==1003)&&!page,"select tab");event("tab-select");}
    bool findUi25Item(RF455TutorialSlot& out) override {out=candidate;event("find-ui25");return ui25Found;}
    void useInventoryItem(RF455TutorialSlot p) override {check(p.pack==2&&p.slot==3,"use slot");boards[3]=true;event("use");}
    void localizedNotice(unsigned index) override {check(index==284,"notice index");++notices;event("notice284");}
    void showSpecialWindow(unsigned id) override {special[id]=true;event("special-open");}
    void closeSpecialWindow(unsigned id) override {special[id]=false;event("special-close");}
    bool specialWindowOpen(unsigned id) override {return special[id];}
    RF455TutorialObject beginBoardObject() override {event("board-construct");return 800;}
    void endBoardObject(RF455TutorialObject value) override {check(value==800,"board temporary");event("board-destruct");}
    bool findEquipCandidate(RF455TutorialObject value,std::uint8_t category,RF455TutorialSlot& out) override {
        check(value==800,"equip temporary");lastMapped=category;out=candidate;event("equip-find");return equipFound;
    }
    void equipFromInventory(RF455TutorialSlot p) override {check(p.pack==2&&p.slot==3,"equip slot");event("equip");}
    void unequipSlot(std::uint8_t slot) override {equipment[slot]=false;event("unequip"+std::to_string(slot));}
    bool boardTransactionBusy() override {++busyQueries;return busy;}
    bool equipmentSlotPresent(std::uint8_t slot) override {++equipQueries;return equipment[slot];}
    void setGameInputEnabled(std::uint32_t value) override {inputEnabled=value;}
    void showMouse(std::int32_t value) override {mouseValue=value;}
    std::array<float,2> screenSize() override {return {{1025,769}};}
    RF455TutorialPointResult cursorPoint(std::uint8_t window,bool defaultPoint,std::uint32_t element) override {
        pointWindow=window;pointDefault=defaultPoint;pointElement=element;return uiPoint;
    }
    RF455TutorialObject firstProjectionObject() override {return projectionObject;}
    RF455TutorialVector objectPosition(RF455TutorialObject object) override {check(object==600,"project object");return {{1,2,3}};}
    RF455TutorialProjection projectCursorPoint(const RF455TutorialVector&) override {return projection;}
    bool cursorUsesWindowOrigin() override {return offsetCursor;}
    RF455TutorialPoint windowOrigin() override {return origin;}
    void setSystemCursor(RF455TutorialPoint point) override {systemPoint=point;++systems;}
    void setLogicalCursor(RF455TutorialPoint point) override {cursorPointNow=point;}
    RF455TutorialPoint logicalCursor() override {return cursorPointNow;}
    void startCursorMotion(RF455TutorialPoint point,std::uint8_t) override {motionPoint=point;++motions;}
    void setCombatMode(bool value) override {toggle=value;}
    void setCombatFlag24308(bool value) override {toggle=value;}
    void traceLockOnWait() override {++traceLocks;}
    RF455TutorialObject currentLockTarget() override {return lockTarget;}
    std::uint32_t targetType(RF455TutorialObject value) override {check(value==900,"lock target");return lockType;}
    std::uint8_t targetPlayerRace(RF455TutorialObject) override {return race;}
    std::uint32_t targetLocalIndex(RF455TutorialObject) override {return lockIndex;}
    bool attackSkillCode(std::uint8_t,std::uint32_t,std::uint32_t& out) override {++skillQueries;out=skillCode;return skillFound;}
    bool resolveItem(std::uint8_t category,std::uint32_t index,bool clone,std::uint32_t& out) override {
        lastCategory=category;return BaseHost::resolveItem(category,index,clone,out);
    }
    RF455TutorialObject createItem(std::uint32_t zero,std::uint8_t category,std::uint32_t local) override {
        check(!zero&&category==lastCategory&&local==0x12345&&cloneActive,"create item args");event("create-item");return 501;
    }
    bool itemStackable(RF455TutorialObject) override {event("stackable");return stackable;}
    void setItemCount(RF455TutorialObject,std::uint32_t value) override {countValue=value;event("set-count");}
    std::uint32_t itemDefaultValue(RF455TutorialObject) override {event("default-value");return defaultValue;}
    void setItemValue(RF455TutorialObject,std::uint32_t value) override {itemValue=value;event("set-value");}
    void setItemSerial(RF455TutorialObject,std::uint16_t value) override {serial=value;event("set-serial");}
    std::uint32_t itemSerial(RF455TutorialObject) override {event("get-serial");return serial;}
    void attachBoardItem(RF455TutorialObject temporary,RF455TutorialObject item) override {check(temporary==800&&item==501,"attach item");event("attach-item");}
    void setBoardSerial(RF455TutorialObject temporary,std::uint32_t value) override {check(temporary==800&&value==serial,"board serial");event("board-serial");}
    bool findEmptyInventorySlot(RF455TutorialSlot& out) override {out=candidate;event("empty-slot");return freeSlot;}
    void insertInventory(RF455TutorialSlot p,RF455TutorialObject temporary) override {
        check(p.pack==2&&p.slot==3&&temporary==800&&cloneActive,"insert args/lifetime");event("insert");
    }
    RF455TutorialObject boardFindIndex(unsigned b,std::uint32_t index) override {check((b==3||b==7)&&index==77,"find board index");return foundObject;}
    RF455TutorialObject boardItem(RF455TutorialObject object) override {check(object!=0,"nonnull board object");return innerItem;}
    bool linkBoardContains(RF455TutorialObject object) override {return object!=0&&linked;}
    bool findBoardItemSlot(unsigned b,RF455TutorialObject item,RF455TutorialSlot& out) override {
        check((b==3||b==7)&&item==501,"find item position");out=candidate;return memberSlot;
    }
    void addHotbarLink(unsigned b,RF455TutorialSlot p,std::uint8_t pack,std::uint8_t slot,bool select) override {
        check((b==3||b==7)&&p.pack==2&&p.slot==3&&pack==255&&slot==255&&!select,"hotbar request args");event("link"+std::to_string(b));
    }
    std::uint32_t itemField112(RF455TutorialObject item) override {check(item==501,"item ready");return ready112;}
    RF455TutorialObject hotbarObject(std::uint8_t pack,std::uint8_t slot) override {check(!pack,"hotbar pack");lastHotbarSlot=slot;return hotbar;}
    std::uint32_t boardIdentity(RF455TutorialObject object) override {check(object!=0,"identity target");return identity;}
    bool boardIdentityEquals(RF455TutorialObject object,std::uint32_t value) override {check(object==801,"hotbar identity");return hotbarIdentity==value;}
    void traceItemStart() override {++traceItems;event("item-start");}
};

static void put(std::vector<std::uint8_t>& b,std::size_t at,std::uint32_t value,unsigned bytes=4) {
    for(unsigned i=0;i<bytes;++i)b[at+i]=std::uint8_t(value>>(8*i));
}
static RF455TutorialInstruction command(unsigned type,unsigned qualifier=0,std::uint32_t value=77) {
    RF455TutorialInstruction op;op.selector=op.dataType=std::uint8_t(type);
    op.fixed.resize(type<=22?8:(type<=26||type>=40?12:20));op.fixed[6]=std::uint8_t(qualifier);
    if(op.fixed.size()>=12)put(op.fixed,8,value);
    return op;
}
static RF455TutorialInstruction cursor(unsigned type,std::uint32_t value=0xffffffff) {
    auto op=command(type);put(op.fixed,6,10,2);put(op.fixed,8,20,2);put(op.fixed,10,30,2);put(op.fixed,12,40,2);
    op.fixed[14]=255;op.fixed[15]=5;put(op.fixed,16,value);return op;
}
static RF455TutorialInstruction combat(unsigned type,unsigned attack=1,std::uint32_t skill=88,
                                      std::uint32_t filter=1,std::uint32_t index=77) {
    auto op=command(type,attack,skill);put(op.fixed,12,filter);put(op.fixed,16,index);return op;
}
static void immediate(RF455TutorialActionsFactory& f,Host& h,RF455TutorialContext& c,const RF455TutorialInstruction& op) {
    auto p=f.create(op);check(bool(p)&&p->begin(h,c),"immediate begin");p->tick(h,c);check(p->flags==7,"immediate flags");
}

static void uiEquip() {
    Host h;RF455TutorialCreationIds ids;RF455TutorialActionsFactory f(h,ids);RF455TutorialContext c;
    for(unsigned id:{0u,63u,64u,5u,6u,11u,25u,27u}) {
        h.calls.clear();immediate(f,h,c,command(19,id));
        const auto first=id==25?"find-ui25":id==27?"special-open":
            "open"+std::to_string(id==5?7:id==6?3:id==11?17:0);
        check(!h.calls.empty()&&h.calls[0]==first,"UI mapping including63/64 inventory");
    }
    h.calls.clear();immediate(f,h,c,command(19,5));
    check(h.calls==std::vector<std::string>({"open7","window7","tab-update","tab-select"}),"UI open/tab order");
    h.ui25Found=false;immediate(f,h,c,command(19,25));check(h.notices==1,"UI25 failure notice");
    auto p=f.create(command(20,5));p->begin(h,c);h.boards[7]=false;p->tick(h,c);check(p->flags==1,"UI open wait pending");
    h.boards[7]=true;p->tick(h,c);check(p->flags==3,"UI open wait done");
    for(unsigned id:{0u,5u,6u,11u,25u,27u})immediate(f,h,c,command(21,id));
    p=f.create(command(22,27));p->begin(h,c);p->tick(h,c);check(p->flags==3,"special close wait");
    p=f.create(command(20,99));p->begin(h,c);const auto clocks=h.clocks;h.now+=100000;p->tick(h,c);
    check(p->flags==1&&h.clocks==clocks,"unknown UI wait has no timeout");
    FILE* map=std::fopen("equip-map.bin","wb");check(map!=nullptr,"map output");
    for(unsigned slot=0;slot!=16;++slot){immediate(f,h,c,command(23,slot));check(std::fputc(h.lastMapped,map)!=EOF,"map byte");}
    check(std::fclose(map)==0,"map close");
    h.calls.clear();h.equipFound=false;immediate(f,h,c,command(23,0));
    check(h.calls==std::vector<std::string>({"board-construct","equip-find","board-destruct"}),"equip failed search lifecycle");
    h.calls.clear();immediate(f,h,c,command(23,255));check(h.calls.empty(),"equip255 no temporary");
    check(!f.create(command(23,16)),"out-of-table equipment domain explicit");
    h.calls.clear();immediate(f,h,c,command(25,12));
    check(h.calls==std::vector<std::string>({"unequip12","unequip13"}),"paired remove order");
    p=f.create(command(24,12));p->begin(h,c);h.busy=true;const auto queries=h.equipQueries;p->tick(h,c);
    check(p->flags==1&&h.equipQueries==queries,"busy blocks equip query");
    h.busy=false;h.equipment[12]=true;p->tick(h,c);check(p->flags==3,"equip wait");
    p=f.create(command(26,12));p->begin(h,c);p->tick(h,c);check(p->flags==1,"pair still occupied");
    h.equipment[12]=false;h.equipment[13]=true;p->tick(h,c);check(p->flags==1,"second pair occupied");
    h.equipment[13]=false;p->tick(h,c);check(p->flags==3,"both pair slots empty");
    p=f.create(command(26,255));p->begin(h,c);const auto busy=h.busyQueries;p->tick(h,c);
    check(p->flags==1&&h.busyQueries==busy,"wait255 remains pending");
}

static void cursors() {
    Host h;RF455TutorialCreationIds ids;RF455TutorialActionsFactory f(h,ids);RF455TutorialContext c;
    const RF455TutorialPoint expected[5]={{0,384},{1025,384},{512,384},{512,0},{512,769}};
    for(unsigned mode=0;mode!=5;++mode){
        immediate(f,h,c,cursor(27,mode));check(h.cursorPointNow.x==expected[mode].x&&h.cursorPointNow.y==expected[mode].y,"screen point");
        check(h.systemPoint.x==100+expected[mode].x&&h.systemPoint.y==221+expected[mode].y,"window origin/chrome21");
    }
    auto op=cursor(27);put(op.fixed,6,0xffff,2);const auto systems=h.systems;immediate(f,h,c,op);
    check(h.systems==systems&&h.motionPoint.x==-1&&h.motionPoint.y==20,"negative direct point uses motion");
    auto p=f.create(cursor(31));p->begin(h,c);p->tick(h,c);check(p->flags==1,"cursor waits exact target");
    h.cursorPointNow={10,20};p->tick(h,c);check(p->flags==3,"cursor target equality");
    h.uiPoint={true,true,{70000,-2}};immediate(f,h,c,cursor(28));
    check(h.motionPoint.x==4464&&h.motionPoint.y==-2&&h.pointWindow==5&&h.pointDefault&&h.pointElement==0xffffffff,
          "UI DWORD point/signed lowWORD/default helper arguments");
    h.uiPoint={true,true,{500,600}};p=f.create(cursor(32,42));p->begin(h,c);
    check(!h.pointDefault&&h.pointElement==42&&h.pointWindow==5,"UI element helper arguments");
    h.uiPoint={false,false,{}};p=f.create(cursor(32));const auto clocks=h.clocks;
    check(!p->begin(h,c)&&p->flags==4&&h.clocks==clocks,"uninitialized lookup coordinates not fabricated");
    h.uiPoint={false,true,{500,600}};immediate(f,h,c,cursor(32));
    immediate(f,h,c,cursor(29,0x80000000));check(h.inputEnabled==0x80000000,"input DWORD preserved");
    immediate(f,h,c,cursor(30,0xffffffff));check(h.mouseValue==-1,"mouse BOOL bits preserved");
    h.projectionObject=0;immediate(f,h,c,cursor(33));
    h.projectionObject=600;h.projection.result=0;immediate(f,h,c,cursor(33));
    h.projection.result=1;p=f.create(cursor(33));p->begin(h,c);p->tick(h,c);
    check(p->flags==1&&h.motionPoint.x==12&&h.motionPoint.y==20,"projected33 target and pending default");
    p=f.create(cursor(34));p->begin(h,c);p->tick(h,c);check(p->flags==1&&h.motionPoint.x==30&&h.motionPoint.y==40,"cursor34 default");
}

static void combats() {
    Host h;RF455TutorialCreationIds ids;RF455TutorialActionsFactory f(h,ids);RF455TutorialContext c;
    immediate(f,h,c,combat(35,1));check(h.toggle&&!c.operationActive,"combat mode");
    immediate(f,h,c,combat(35,2));check(!h.toggle,"combat mode is equality1");
    immediate(f,h,c,combat(37,2));check(h.toggle,"combat flag is nonzero");
    auto p=f.create(combat(36));p->begin(h,c);h.lockTarget=0;p->tick(h,c);check(p->flags==1&&h.traceLocks==1,"lock null pending/trace");
    h.lockTarget=900;h.lockType=2;p->tick(h,c);check(p->flags==1,"lock type filter");
    h.lockType=1;h.monsterFound=false;p->tick(h,c);check(p->flags==3&&!c.operationActive,"missing monster template accepts lock");
    h.monsterFound=true;h.lockIndex=0;p=f.create(combat(36));p->begin(h,c);p->tick(h,c);check(p->flags==1,"monster index mismatch");
    h.lockIndex=0x12345;p->tick(h,c);check(p->flags==3,"monster index match");
    h.lockType=0;p=f.create(combat(36,1,0,0,258));p->begin(h,c);p->tick(h,c);check(p->flags==3,"player race byte/faction comparison");
    p=f.create(combat(36,1,0,0,0));p->begin(h,c);p->tick(h,c);check(p->flags==1,"player race mismatch");
    h.lockType=2;p=f.create(combat(36,1,0,2,77));p->begin(h,c);p->tick(h,c);check(p->flags==3,"other matched type default");
    p=f.create(combat(38,3,88));p->begin(h,c);c.attackType=2;p->tick(h,c);check(p->flags==1,"attack kind mismatch");
    c.attackType=3;c.skillIndex=77;c.target[0]=123;c.target[1]=456;h.skillFound=false;p->tick(h,c);
    check(p->flags==3&&c.attackType==255&&c.skillIndex==0xffffffff&&c.target[0]==0xffffffff&&c.target[1]==0xffffffff,"missing skill accepts/reset feedback");
    h.skillFound=true;h.skillCode=99;p=f.create(combat(38,3,88));p->begin(h,c);c.attackType=3;p->tick(h,c);check(p->flags==1,"skill code mismatch");
    h.skillCode=88;p->tick(h,c);check(p->flags==3,"skill code match");
    p=f.create(combat(38,4,88));p->begin(h,c);c.attackType=4;const auto queries=h.skillQueries;p->tick(h,c);
    check(p->flags==3&&h.skillQueries==queries,"attack4 bypasses skill lookup");
    p=f.create(combat(39,1,0,3));p->begin(h,c);RF455TutorialCombatParameters parameters;
    check(RF455_GetTutorialCombatParameters(*p,parameters)&&parameters.attackType==255,"counter start mutates own data");
    c.state52=2;p->tick(h,c);check(p->flags==1,"counter before threshold");c.state52=3;p->tick(h,c);check(p->flags==3,"counter equality");
    p=f.create(combat(39,1,0,0x7fffffff));p->begin(h,c);c.state52=0x80000000;p->tick(h,c);check(p->flags==3,"counter comparison unsigned");
}

static void items() {
    Host h;RF455TutorialCreationIds ids;ids.item=65535;RF455TutorialActionsFactory f(h,ids);RF455TutorialContext c;
    immediate(f,h,c,command(40,5));
    check(h.countValue==200&&ids.item==0&&h.serial==65535&&!h.cloneActive,"item stack/serial wrap");
    check(h.calls==std::vector<std::string>({"item-start","item-construct","item-resolve","create-item","stackable","set-count","set-serial","board-construct","attach-item","get-serial","board-serial","empty-slot","insert","board-destruct","item-destruct"}),"item lifecycle/insert order");
    h.stackable=false;h.calls.clear();immediate(f,h,c,command(40,5));check(h.itemValue==17,"nonstack default value");
    h.itemFound=false;h.calls.clear();const auto serial=ids.item;immediate(f,h,c,command(40,5));
    check(ids.item==serial&&h.calls==std::vector<std::string>({"item-start","item-construct","item-resolve","item-destruct"}),"failed clone lifecycle/no serial");
    h.itemFound=true;h.stackable=true;h.boards[3]=false;immediate(f,h,c,command(41,5));
    check(h.lastCategory==18&&!h.boards[3],"force item fixed category/restores closed UI");
    h.boards[3]=true;immediate(f,h,c,command(41,5));check(h.boards[3],"force preserves already open UI");
    h.freeSlot=false;h.calls.clear();immediate(f,h,c,command(41));
    check(std::find(h.calls.begin(),h.calls.end(),"use")==h.calls.end(),"full inventory no activation");
    auto p=f.create(command(42));p->begin(h,c);h.foundObject=0;p->tick(h,c);check(p->flags==1,"missing board item wait");
    h.foundObject=701;h.innerItem=0;p->tick(h,c);check(p->flags==1,"missing underlying item wait");
    h.innerItem=501;h.ready112=1;p->tick(h,c);check(p->flags==3,"item field112 wait");
    h.calls.clear();immediate(f,h,c,command(43));immediate(f,h,c,command(45));
    check(h.calls==std::vector<std::string>({"item-start","link7","item-start","link3"}),"skill/force link request args");
    h.linked=true;h.calls.clear();immediate(f,h,c,command(43));check(h.calls==std::vector<std::string>({"item-start"}),"existing link not duplicated");
    p=f.create(command(44,255));p->begin(h,c);p->tick(h,c);check(p->flags==3,"any link wait");
    h.hotbarIdentity=9;p=f.create(command(46,1));p->begin(h,c);p->tick(h,c);check(p->flags==1&&h.lastHotbarSlot==0,"hotbar identity mismatch");
    h.hotbarIdentity=1234;p->tick(h,c);check(p->flags==3,"hotbar identity match");
    p=f.create(command(44,0));p->begin(h,c);h.hotbar=0;p->tick(h,c);check(p->flags==1&&h.lastHotbarSlot==255,"qualifier zero wraps byte");
}

int main() {
    try {
        uiEquip();cursors();combats();items();
        Host h;RF455TutorialCreationIds ids;RF455TutorialActionsFactory factory(h,ids);
        std::ifstream list("inputs.txt");check(bool(list),"input list");
        std::string path;unsigned files=0,records=0;
        while(std::getline(list,path)){
            if(!path.empty()&&path.back()=='\r')path.pop_back();if(path.empty())continue;
            RF455TutorialScript data;check(RF455_LoadTutorialScript(path.c_str(),data),"real script");
            RF455TutorialRuntime runtime;RF455TutorialUnsupported gap;
            check(runtime.prepare(data,factory,&gap),"all real commands have processors");++files;
            for(const auto& q:runtime.quests)records+=static_cast<unsigned>(q.processors.size());
        }
        RF455TutorialScript synthetic;check(RF455_LoadTutorialScript("all47.scp",synthetic),"all47 fixture");
        RF455TutorialRuntime runtime;check(runtime.prepare(synthetic,factory),"all47 selectors prepared");
        auto unsupported=command(46);unsupported.selector=47;check(!factory.create(unsupported),"unknown selector refused");
        FILE* out=std::fopen("result.json","w");check(out!=nullptr,"result");
        std::fprintf(out,"{\"status\":\"PASS\",\"ui19to22\":true,\"equip23to26\":true,\"cursor27to34\":true,"
                     "\"combat35to39\":true,\"item40to46\":true,\"lifecycle_and_branch_order\":true,"
                     "\"files_prepared\":%u,\"records_prepared\":%u,\"synthetic47_prepared\":true,"
                     "\"production_host\":false,\"unsafe_cursor_failure_resolved\":false,\"full_Tutorial\":false}\n",files,records);
        check(std::fclose(out)==0,"close result");return 0;
    }catch(const std::exception& error){std::fprintf(stderr,"%s\n",error.what());return 1;}
}
