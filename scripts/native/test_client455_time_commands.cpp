#include "client455_clock.h"
#include "client455_time_commands.h"
#include <stdio.h>
#include <string.h>
#include <string>
#include <errno.h>

static unsigned checks,failures,firstFailure,calls,cases;
static DWORD WINAPI testTick() { ++calls;return 0x80000000u; }
static unsigned short control() { unsigned short v;__asm { fnstcw v } return v; }
static unsigned short top() { unsigned short v;__asm { fnstsw v } return v&0x3800; }
static void setControl(unsigned short v) { __asm fldcw v }
static void check(bool v) { ++checks;if (!v) { ++failures;if (!firstFailure) firstFailure=checks; } }
static void runCase(const std::string& text,unsigned kind,unsigned hours=0,unsigned minutes=0,bool overflow=false) {
    ++cases;calls=0;errno=0;
    RF455_DayRate=3;RF455_DayFraction=.125f;RF455_RealDayFraction=.25f;
    RF455_DayBase=0x11111111;RF455_RealDayBase=0x22222222;
    const unsigned short cw=control(),st=top();const std::string before=text;
    check(RF455_TryClockCommand(text.c_str())==(kind?1:0));
    check(calls==(kind?1u:0u));check(text==before);check(control()==cw && top()==st);
    const DWORD seconds=3600u*hours+60u*minutes;
    if (kind==1) {
        check(RF455_DayBase==0x80000000u-(seconds/3)*1000u);
        check(RF455_RealDayBase==0x22222222 && RF455_RealDayFraction==.25f);
    } else if (kind==2) {
        check(RF455_RealDayBase==0x80000000u-seconds*1000u);
        check(RF455_DayBase==0x11111111 && RF455_DayFraction==.125f);
    } else {
        check(RF455_DayBase==0x11111111 && RF455_RealDayBase==0x22222222);
        check(RF455_DayFraction==.125f && RF455_RealDayFraction==.25f);
    }
    if (overflow) check(errno==ERANGE);
}
static int runTimeCommandChecks(FILE* output) {
    const unsigned short original=control();auto provider=RF455_ClockTickSource;RF455_ClockTickSource=&testTick;
    unsigned modes=0;
    for (unsigned pc=0;pc<3;++pc) for (unsigned rc=0;rc<4;++rc) {
        const unsigned pcs[]={0,0x200,0x300};setControl((unsigned short)((original&~0xF00)|pcs[pc]|(rc<<10)|0x3F));++modes;
        runCase("%time 12",1,12);runCase("%TIME 36",1,12);runCase("%time\t6",1,6);
        runCase("%time -1",1,15);runCase("%time -24",1,16);
        runCase("%time +12junk",1,12);runCase("%time twelve",1,0);runCase("%time 0x10",1,0);
        runCase("%time 2147483648",1,7,0,true);runCase("%time -2147483649",1,8,0,true);
        runCase("%real_time 12 30",2,12,30);runCase("%REAL_TIME 36 90",2,12,30);
        runCase("%real_time -1 -1",2,15,15);runCase("%real_time x y",2,0,0);
        runCase("%real_time 12\t30 trailing",2,12,30);
        runCase("%real_time  12 34",2,12,2);
        runCase(" %time 12",1,0);runCase("prefix %time 12",1,0);
        runCase(" %real_time 12 34",2,0,12);
        runCase("%time 12 %real_time 1 2",1,12);
        runCase("%real_time 12 30 %time 1",2,12,30);
        runCase("",0);runCase("   \t\r\n",0);runCase("%time",0);runCase("%real_time 12",0);
        runCase("unknown",0);runCase("%time1 12",0);runCase("end %time 12",0);
        runCase("%fov 1 %time 12",0);runCase("%change_rgb %time 12",0);
        runCase("%max_cam_dist %time 12",0);runCase("%floor_dist %time 12",0);
        runCase(std::string(256,' ')+"%time 12",0);
        runCase(std::string("%time ")+std::string(250,'9'),1,7,0,true);
        runCase(std::string("%real_time 12")+std::string(242,' ')+"30",2,12,3);
        runCase(std::string("%real_time 12")+std::string(243,' ')+"30",0);
    }
    setControl(original);RF455_ClockTickSource=provider;
    fprintf(output,"{\"checks\":%u,\"failures\":%u,\"first_failure\":%u,\"cases\":%u,\"precision_rounding_modes\":%u,\"ascii_domain\":true}\n",checks,failures,firstFailure,cases,modes);
    return failures?1:0;
}
#if !defined(RF455_TIME_COMMANDS_EMBEDDED)
int main() { return runTimeCommandChecks(stdout); }
#endif
