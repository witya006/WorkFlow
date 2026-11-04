#include "client455_loop_clock.h"
#include <cstdio>
#include <cstring>
#include <float.h>
#include <xmmintrin.h>
extern "C" {DWORD RF455_TestLoopNow=0;}
static unsigned timerCalls=0,frequencyCalls=0,counterCalls=0;
static bool frequencySuccess=true,counterSuccess=true,zeroFirstCounter=false;
extern "C" DWORD WINAPI RF455_TestLoopTimer(){++timerCalls;return RF455_TestLoopNow;}
static BOOL WINAPI frequency(LARGE_INTEGER* value){++frequencyCalls;value->QuadPart=12000000;return frequencySuccess;}
static BOOL WINAPI counter(LARGE_INTEGER* value){++counterCalls;value->QuadPart=zeroFirstCounter && counterCalls==1?0:123456;return counterSuccess;}
extern "C" int RF455_RunLoopClockChecks(const char* golden,const char* output,RF455LoopClock* active,void (*actualStep)()){
    FILE* in=std::fopen(golden,"rb");if(!in)return 220;char magic[4];unsigned version=0,count=0;
    if(std::fread(magic,4,1,in)!=1 || std::memcmp(magic,"LC45",4) || std::fread(&version,4,1,in)!=1 || version!=1 || std::fread(&count,4,1,in)!=1){std::fclose(in);return 221;}
    const unsigned saved=_control87(0,0);unsigned checks=0,failures=0;
    auto check=[&](bool okay){++checks;if(!okay)++failures;};
    for(unsigned i=0;i<count;++i){unsigned p=0,mode=0,now=0;RF455LoopClock before,expected;
        if(std::fread(&p,4,1,in)!=1 || std::fread(&mode,4,1,in)!=1 || std::fread(&now,4,1,in)!=1 || std::fread(&before,sizeof(before),1,in)!=1 || std::fread(&expected,sizeof(expected),1,in)!=1){std::fclose(in);return 222;}
        const unsigned precisions[]={_PC_24,_PC_53,_PC_64},rounding[]={_RC_NEAR,_RC_DOWN,_RC_UP,_RC_CHOP};unsigned precision=p==24?0:p==53?1:2;
        _clearfp();_control87(_MCW_EM|precisions[precision]|rounding[mode],_MCW_EM|_MCW_PC|_MCW_RC);const unsigned control=_control87(0,0);
        RF455_TestLoopNow=now;timerCalls=frequencyCalls=counterCalls=0;RF455LoopClock value=before;
        if(actualStep){*active=before;actualStep();value=*active;}else RF455_UpdateLoopClock(&value,frequency,counter,RF455_TestLoopTimer);
        if(std::memcmp(&value,&expected,sizeof(value))){++failures;std::fprintf(stderr,"Loopstate mismatch row%u/PC%u/RC%u\n",i,p,mode);}
        ++checks;check(timerCalls==1 && !frequencyCalls && !counterCalls);check(_control87(0,0)==control);
    }
    check(std::fgetc(in)==EOF);std::fclose(in);_clearfp();_control87(_MCW_EM|_PC_53|_RC_NEAR,_MCW_EM|_MCW_PC|_MCW_RC);
    for(unsigned scenario=0;scenario<3;++scenario){RF455LoopClock value;timerCalls=frequencyCalls=counterCalls=0;frequencySuccess=scenario!=1;counterSuccess=scenario!=1;zeroFirstCounter=scenario==2;RF455_TestLoopNow=100;
        RF455_UpdateLoopClock(&value,frequency,counter,RF455_TestLoopTimer);
        check(value.initialized==1 && frequencyCalls==1 && counterCalls==(scenario==2?2u:1u));
        check(value.frequency==(scenario==1?1000u:12000000u) && value.ticksPerFrame==(scenario==1?1u:12000u));
        check(value.startTicks==(scenario==1?100u:123456u) && value.ticks==value.startTicks && timerCalls==(scenario==1?2u:1u));
        check(value.loopSeconds==.1f && value.realSeconds==.1f && value.initialSecondsPerFrame==.001f);
    }
    frequencySuccess=counterSuccess=true;zeroFirstCounter=false;
    {RF455LoopClock value;value.frequency=1000;value.startTicks=123400;check(RF455_GetLoopDuration(&value,counter,RF455_TestLoopTimer)==.056f);value.startTicks=123500;check(RF455_GetLoopDuration(&value,counter,RF455_TestLoopTimer)==-.044f);}
    {const unsigned mxcsr=_mm_getcsr();_mm_setcsr(mxcsr|0x8040);RF455LoopClock value;value.initialized=1;value.oldTick=100;const unsigned negativeTiny=0x80000001;std::memcpy(&value.loopSeconds,&negativeTiny,4);RF455_TestLoopNow=100;if(actualStep){*active=value;actualStep();value=*active;}else RF455_UpdateLoopClock(&value,frequency,counter,RF455_TestLoopTimer);check(value.loopSeconds==1 && value.realSeconds==1);_mm_setcsr(mxcsr);}
    _clearfp();_control87(saved,_MCW_EM|_MCW_PC|_MCW_RC);FILE* out=std::fopen(output,"wb");if(!out)return 223;
    std::fprintf(out,"{\"status\":\"%s\",\"state_cases\":%u,\"provider_cases\":3,\"daz_ftz_cases\":1,\"checks\":%u,\"failures\":%u,\"fp_modes\":12,\"actual_engine_bridge\":%s}\n",failures?"FAIL":"PASS",count,checks,failures,actualStep?"true":"false");std::fclose(out);return failures?224:0;
}
#ifndef RF455_LOOP_CLOCK_EMBEDDED
int main(int argc,char** argv){return argc==3?RF455_RunLoopClockChecks(argv[1],argv[2],nullptr,nullptr):225;}
#endif
