#include "client455_animation_timing.h"
#include <cstdio>
#include <cstring>
#include <float.h>

extern "C" int RF455_RunAnimationTimingChecks(const char* goldenPath,const char* output){
    FILE* f=std::fopen(goldenPath,"rb");if(!f)return 1;unsigned header[3]={};if(std::fread(header,4,3,f)!=3 || header[0]!=0x35345441 || header[1]!=1){std::fclose(f);return 2;}
    unsigned checks=0,failures=0;const auto saved=_control87(0,0);const unsigned rounding[]={_RC_NEAR,_RC_DOWN,_RC_UP,_RC_CHOP};
    for(unsigned i=0;i<header[2];++i){unsigned row[7]={};if(std::fread(row,4,7,f)!=7){std::fclose(f);return 3;}const unsigned precision=row[0]==24?_PC_24:row[0]==53?_PC_53:_PC_64;_clearfp();_control87(_MCW_EM|precision|rounding[row[1]],_MCW_EM|_MCW_PC|_MCW_RC);float elapsed,speed;std::memcpy(&elapsed,row+4,4);std::memcpy(&speed,row+5,4);unsigned short before,after;__asm{fnstcw before}
        const auto value=RF455_AdvanceAnimationFrameValue(row[2],row[3],elapsed,speed);__asm{fnstcw after}++checks;if(value!=row[6] || before!=after){++failures;std::fprintf(stderr,"frame case%u p%u mode%u:got%08x expected%08x cw%04x/%04x\n",i,row[0],row[1],value,row[6],before,after);}
    }
    _clearfp();_control87(saved,_MCW_EM|_MCW_PC|_MCW_RC);unsigned char expectedControl[100],expectedState[84],control[100],state[84];if(std::fread(expectedControl,1,100,f)!=100 || std::fread(expectedState,1,84,f)!=84 || std::fgetc(f)!=EOF){std::fclose(f);return 4;}std::fclose(f);std::memset(control,0xa5,100);std::memset(state,0xa5,84);RF455_InitializeAnimationControl(control);RF455_InitializeSecondaryState(state);checks+=2;if(std::memcmp(control,expectedControl,100))++failures;if(std::memcmp(state,expectedState,84))++failures;
    f=std::fopen(output,"wb");if(!f)return 5;std::fprintf(f,"{\"status\":\"%s\",\"cases\":%u,\"checks\":%u,\"failures\":%u,\"fp_modes\":12}\n",failures?"FAIL":"PASS",header[2],checks,failures);std::fclose(f);return failures?6:0;
}
#ifndef RF455_ANIMATION_TIMING_EMBEDDED
int main(int argc,char** argv){if(argc!=3)return 2;return RF455_RunAnimationTimingChecks(argv[1],argv[2]);}
#endif
