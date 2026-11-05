#include "client455_character_clock.h"
#include <cstdio>
#include <cstring>
#include <float.h>

void _R3CalculateTime();
float R3GetLoopTime();
void R3SetLoopTime(float);
namespace {
unsigned failures=0,frequencyCalls=0,counterCalls=0,timerCalls=0;
std::uint64_t now=0;bool initializing=false,frequencySuccess=true,counterSuccess=true;
BOOL WINAPI frequency(LARGE_INTEGER* output){++frequencyCalls;output->QuadPart=1000;return frequencySuccess?7:0;}
BOOL WINAPI counter(LARGE_INTEGER* output){output->QuadPart=initializing?100+5*counterCalls:now;++counterCalls;return counterSuccess;}
DWORD WINAPI timer(){++timerCalls;return static_cast<DWORD>(now);}
void check(bool value){if(!value)++failures;}
unsigned word(float value){unsigned result;std::memcpy(&result,&value,4);return result;}
void resetCalls(){frequencyCalls=counterCalls=timerCalls=0;}
}
int main(int argc,char** argv){
    if(argc!=3)return 201;FILE* input=std::fopen(argv[1],"rb");if(!input)return 202;
    unsigned header[3];if(std::fread(header,4,3,input)!=3 || header[0]!=0x35344343 || header[1]!=1)return 203;
    const unsigned saved=_control87(0,0);auto* normal=RF455_GetNormalCharacterClock();auto* providers=RF455_GetNormalCharacterClockProviders();const auto savedProviders=*providers;const auto savedState=*normal;
    *providers={frequency,counter,timer};const float engineBefore=R3GetLoopTime();R3SetLoopTime(.03125f);
    for(unsigned i=0;i<header[2];++i){
        unsigned row[27];if(std::fread(row,4,27,input)!=27)return 204;
        const unsigned pc=row[0]==24?_PC_24:row[0]==53?_PC_53:_PC_64;
        const unsigned rc[]={_RC_NEAR,_RC_DOWN,_RC_UP,_RC_CHOP};_clearfp();_control87(_MCW_EM|pc|rc[row[1]],_MCW_EM|_MCW_PC|_MCW_RC);
        unsigned short cwBefore,cwAfter;__asm{fnstcw cwBefore}
        now=static_cast<std::uint64_t>(row[2])|static_cast<std::uint64_t>(row[3])<<32;
        RF455CharacterClock state;std::memcpy(&state,row+4,sizeof(state));resetCalls();
        const auto returned=RF455_UpdateCharacterClock(&state,providers);
        check(!std::memcmp(&state,row+15,sizeof(state)) && returned==row[26]);
        check(!frequencyCalls && counterCalls==(row[5]?1u:0u) && timerCalls==(row[5]?0u:1u));
        std::memcpy(normal,row+4,sizeof(*normal));resetCalls();_R3CalculateTime();
        check(!std::memcmp(normal,row+15,sizeof(*normal)));check(word(R3GetLoopTime())==word(.03125f));
        __asm{fnstcw cwAfter}check(cwBefore==cwAfter);
    }
    check(std::fgetc(input)==EOF);std::fclose(input);_clearfp();_control87(_MCW_EM|_PC_53|_RC_NEAR,_MCW_EM|_MCW_PC|_MCW_RC);
    resetCalls();*normal={};initializing=true;_R3CalculateTime();
    check(frequencyCalls==1 && counterCalls==2 && !timerCalls && normal->performanceAvailable==7 && normal->deltaMilliseconds==5 && normal->elapsedMilliseconds==5);
    _R3CalculateTime();check(frequencyCalls==1 && counterCalls==3 && normal->deltaMilliseconds==5 && normal->elapsedMilliseconds==10);
    initializing=false;frequencySuccess=false;resetCalls();*normal={};now=200;_R3CalculateTime();
    check(frequencyCalls==1 && !counterCalls && timerCalls==1 && normal->samples==1 && normal->windowMilliseconds==200 && normal->deltaMilliseconds==0);
    now=201;_R3CalculateTime();check(normal->deltaMilliseconds==100.5f && !normal->samples && !normal->windowMilliseconds && normal->elapsedMilliseconds==0);
    now=202;_R3CalculateTime();check(frequencyCalls==1 && normal->deltaMilliseconds==100.5f && normal->samples==1 && normal->windowMilliseconds==1 && normal->elapsedMilliseconds==0);
    frequencySuccess=true;counterSuccess=false;initializing=true;resetCalls();*normal={};_R3CalculateTime();
    check(counterCalls==2 && normal->deltaMilliseconds==5); // BOOL ignored; output supplied.
    R3SetLoopTime(engineBefore);*providers=savedProviders;*normal=savedState;_clearfp();_control87(saved,_MCW_EM|_MCW_PC|_MCW_RC);
    FILE* output=std::fopen(argv[2],"wb");if(!output)return 205;
    std::fprintf(output,"{\"status\":\"%s\",\"state_cases\":%u,\"fp_modes\":12,\"normal_bridge\":true,\"engine_clock_independent\":true,\"initialization_and_fallback\":true,\"failures\":%u}\n",failures?"FAIL":"PASS",header[2],failures);std::fclose(output);
    return failures?206:0;
}
