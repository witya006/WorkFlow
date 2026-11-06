#include "client455_tutorial_actions.h"
#include "testing/client455_tutorial_recording_host.h"
#include <cstdio>
#include <algorithm>
#include <cstring>
#include <fstream>
#include <map>
#include <stdexcept>

static void check(bool value,const char* reason){if(!value)throw std::runtime_error(reason);}
#include "testing/client455_tutorial_actions_host.h"
using Host=RF455TutorialRecordingActionsHost;

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
