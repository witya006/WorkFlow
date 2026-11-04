#include "commonutil.h"
#include "client455_loop_clock.h"
extern DWORD (WINAPI* ptimeGetTime)();
extern "C" DWORD RF455_TestLoopNow;
extern "C" DWORD WINAPI RF455_TestLoopTimer();
extern "C" int RF455_RunLoopClockChecks(const char*,const char*,RF455LoopClock*,void (*)());
static int loopClockScenarioProbe(){
    const char* golden=std::getenv("RF_LOOP_CLOCK_GOLDEN");const char* output=std::getenv("RF_LAB_HELPER_OUTPUT");if(!golden || !output)return 226;
    RF455LoopClock* clock=RF455_GetEngineLoopClockState();const RF455LoopClock saved=*clock;const auto timer=ptimeGetTime;ptimeGetTime=RF455_TestLoopTimer;
    const DWORD allocations=GetDmallocSize();const unsigned savedControl=_control87(0,0);std::string actual=std::string(output)+".clock.json";
    const int result=RF455_RunLoopClockChecks(golden,actual.c_str(),clock,&::R3CalculateTime);
    _clearfp();_control87(_MCW_EM|_PC_53|_RC_NEAR,_MCW_EM|_MCW_PC|_MCW_RC);
    *clock=RF455LoopClock{};clock->initialized=1;clock->oldTick=100;RF455_TestLoopNow=130;::R3CalculateTime();
    unsigned failures=result?1u:0u,checks=0;auto check=[&](bool okay){++checks;if(!okay)++failures;};
    check(::R3GetLoopTime()==.03f && ::R3GetTime()==.03f);check(::R3GetToggle30fps()==1 && ::R3GetToggle15fps()==1 && ::R3GetToggle7fps()==1);
#if defined(RF_CLIENT_455_ANIMATION_TIMING)
    {AnimationFrameFixture actor;CBone bone={};bone.m_OMaxFrame=1000;actor.Setup(&bone,160,0,0,false,nullptr,1);actor.Step(0xffffffff);check(actor.Frame()==309 && bone.m_Frame==309);}
#endif
    ::R3SetLoopTime(.125f);::R3SetTime(2);::R3SetMinFPS(20);RF455_SetEngineLoopTimeScale(.5f);
    check(clock->loopSeconds==.125f && clock->realSeconds==2 && clock->maximumSeconds==.05f && clock->timeScale==.5f);
    *clock=saved;ptimeGetTime=timer;_clearfp();_control87(savedControl,_MCW_EM|_MCW_PC|_MCW_RC);
    check(GetDmallocSize()==allocations);const char* dlls[]={"mss32.dll","ABuse.dll","Adv.dll","PDLL.dll"};for(const auto* d:dlls)check(!GetModuleHandleA(d));
    FILE* f=std::fopen(output,"wb");if(!f)return 227;std::fprintf(f,"{\"status\":\"%s\",\"connected_checks\":%u,\"failures\":%u,\"frame\":309,\"dmalloc_balance\":%ld}\n",failures?"FAIL":"PASS",checks,failures,static_cast<long>(GetDmallocSize()-allocations));std::fclose(f);return failures?228:0;
}
