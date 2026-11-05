#include "client455_frustum.h"
#include <cstdio>
#include <cstring>
#include <float.h>
#include <xmmintrin.h>

using PublishCaller=void (*)(const float*,const float*,float (*)[4]);
extern "C" int RF455_RunFrustumChecks(const char* golden,const char* output,PublishCaller actual){
    FILE* file=std::fopen(golden,"rb");if(!file)return 230;char magic[4];unsigned version=0,matrices=0,boxes=0;
    if(std::fread(magic,4,1,file)!=1 || std::memcmp(magic,"FC45",4) || std::fread(&version,4,1,file)!=1 || version!=1 || std::fread(&matrices,4,1,file)!=1 || std::fread(&boxes,4,1,file)!=1){std::fclose(file);return 231;}
    const unsigned saved=_control87(0,0);const unsigned mxcsr=_mm_getcsr();unsigned failures=0,checks=0;
    auto check=[&](bool okay){++checks;if(!okay)++failures;};
    auto control=[](unsigned precision,unsigned mode){const unsigned pc=precision==24?_PC_24:precision==53?_PC_53:_PC_64;const unsigned rc[]={_RC_NEAR,_RC_DOWN,_RC_UP,_RC_CHOP};_clearfp();_control87(_MCW_EM|pc|rc[mode],_MCW_EM|_MCW_PC|_MCW_RC);};
    for(unsigned i=0;i<matrices;++i){unsigned pc=0,mode=0;float view[16],projection[16],clip[16],expected[6][4],value[6][4];
        if(std::fread(&pc,4,1,file)!=1 || std::fread(&mode,4,1,file)!=1 || std::fread(view,64,1,file)!=1 || std::fread(projection,64,1,file)!=1 || std::fread(clip,64,1,file)!=1 || std::fread(expected,96,1,file)!=1){std::fclose(file);return 232;}
        control(pc,mode);const unsigned before=_control87(0,0);RF455_ExtractFrustumPlanes(value,clip);
        if(std::memcmp(value,expected,96))std::fprintf(stderr,"Extract matrix%u PC%u RC%u\n",i,pc,mode);
        check(std::memcmp(value,expected,96)==0);check(_control87(0,0)==before);
        if(actual)actual(view,projection,value);else check(RF455_PublishSystemCharacterFrustum(value,view,projection)!=0);
        if(std::memcmp(value,expected,96))std::fprintf(stderr,"Publish matrix%u PC%u RC%u\n",i,pc,mode);
        check(std::memcmp(value,expected,96)==0);check(_control87(0,0)==before);
    }
    for(unsigned i=0;i<boxes;++i){unsigned pc=0,mode=0,expected=0;float minimum[3],maximum[3],plane[6][4];
        if(std::fread(&pc,4,1,file)!=1 || std::fread(&mode,4,1,file)!=1 || std::fread(minimum,12,1,file)!=1 || std::fread(maximum,12,1,file)!=1 || std::fread(plane,96,1,file)!=1 || std::fread(&expected,4,1,file)!=1){std::fclose(file);return 233;}
        control(pc,mode);const unsigned before=_control87(0,0);check(RF455_IsBBoxInFrustum(minimum,maximum,plane)==static_cast<int>(expected));check(_control87(0,0)==before);
        // MXCSR DAZ/FTZ must not alter this x87 contract.
        _mm_setcsr(_mm_getcsr()|0x8040);check(RF455_IsBBoxInFrustum(minimum,maximum,plane)==static_cast<int>(expected));_mm_setcsr(mxcsr);
    }
    check(std::fgetc(file)==EOF);std::fclose(file);_clearfp();_control87(saved,_MCW_EM|_MCW_PC|_MCW_RC);_mm_setcsr(mxcsr);
    file=std::fopen(output,"wb");if(!file)return 234;
    std::fprintf(file,"{\"status\":\"%s\",\"matrix_cases\":%u,\"bbox_cases\":%u,\"fp_modes\":12,\"checks\":%u,\"failures\":%u,\"actual_publisher\":%s}\n",failures?"FAIL":"PASS",matrices,boxes,checks,failures,actual?"true":"false");std::fclose(file);return failures?235:0;
}
#ifndef RF455_FRUSTUM_EMBEDDED
int main(int argc,char** argv){return argc==3?RF455_RunFrustumChecks(argv[1],argv[2],nullptr):236;}
#endif
