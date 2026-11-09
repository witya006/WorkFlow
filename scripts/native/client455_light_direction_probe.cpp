#include "client455_light_direction.inc"
#include <cstdio>
#include <cstring>
#include <cmath>

static unsigned bits131(float value){unsigned bits;std::memcpy(&bits,&value,4);return bits;}
static unsigned short cw131(){unsigned short value;__asm{fnstcw value}return value;}
static unsigned short sw131(){unsigned short value;__asm{fnstsw value}return value;}
static void cw131(unsigned short value){__asm{fldcw value}}
static void values131(FILE* f,const float* p,unsigned count){std::fputc('[',f);for(unsigned i=0;i<count;++i)std::fprintf(f,"%s%u",i?",":"",bits131(p[i]));std::fputc(']',f);}

int main(int argc,char** argv){
    if(argc!=2)return 1;FILE* trace=std::fopen(argv[1],"wb");if(!trace)return 2;
    const unsigned short saved=cw131();unsigned cases=0,failures=0;
    const float vectors[8][3]={{3,4,0},{1,2,3},{.2f,1,.3f},{.5f,-.25f,2},
        {16777216,1,-16777216},{0x1p-50f,-0x1p-49f,0x1p-48f},{0x1p50f,-0x1p49f,0x1p48f},{0,0,0}};
    const float matrices[8][16]={
        {1,0,0,0,0,1,0,0,0,0,1,0,16,32,-64,1},
        {0,1,0,0,-1,0,0,0,0,0,1,0,3,7,11,1},
        {1,0,0,0,0,0,1,0,0,-1,0,0,1,2,3,1},
        {2,0,0,0,0,.5f,0,0,0,0,4,0,10,20,30,1},
        {1,.25f,-.5f,0,.125f,1,.375f,0,-.25f,.5f,1,0,0,0,0,1},
        {1.25f,.125f,-.25f,0,.5f,2,.375f,0,-.125f,.25f,.75f,0,100,-30,17,1},
        {-2,0,0,0,0,4,0,0,0,0,-.5f,0,-5,-10,30,1},
        {.25f,.5f,0,.001f,-.5f,.25f,0,0,0,0,2,0,21,32,43,1}};
    for(unsigned pc=0;pc<3;++pc)for(unsigned rc=0;rc<4;++rc){
        const unsigned precision[]={0,0x200,0x300};const unsigned short wanted=(saved&~0xf00)|precision[pc]|(rc<<10)|0x3f;cw131(wanted);
        for(unsigned i=0;i<8;++i){
            float vector[3];std::memcpy(vector,vectors[i],12);const unsigned before=sw131();RF455_NormalizeLightVector(vector);const unsigned after=sw131();
            if(cw131()!=wanted||(before&0x3800)!=(after&0x3800))++failures;
            std::fprintf(trace,"{\"kind\":\"normal\",\"id\":%u,\"cw\":%u,\"before_status\":%u,\"after_status\":%u,\"input\":",i,wanted,before,after);values131(trace,vectors[i],3);std::fputs(",\"output\":",trace);values131(trace,vector,3);std::fputs("}\n",trace);++cases;
            float world[4][4],light[3]={.2f,1,.3f},output[3];std::memcpy(world,matrices[i],64);RF455_BuildLightDirection(output,world,light);
            if(cw131()!=wanted)++failures;
            std::fprintf(trace,"{\"kind\":\"transform\",\"id\":%u,\"cw\":%u,\"world\":",i,wanted);values131(trace,&world[0][0],16);std::fputs(",\"input\":",trace);values131(trace,light,3);std::fputs(",\"output\":",trace);values131(trace,output,3);std::fputs("}\n",trace);++cases;
        }
        for(unsigned i=0;i<4;++i){float world[4][4]={},inverse[4][4],before[4][4];for(unsigned k=0;k<4;++k)world[k][k]=1;world[i][3]=i==3?1.01f:.01f;
            std::memset(inverse,0xcd,64);std::memcpy(before,inverse,64);const int result=RF455_MatrixInvert(inverse,world);const bool untouched=std::memcmp(inverse,before,64)==0;
            if(result||!untouched||cw131()!=wanted)++failures;
            std::fprintf(trace,"{\"kind\":\"guard\",\"id\":%u,\"cw\":%u,\"result\":%d,\"output_unchanged\":%s}\n",i,wanted,result,untouched?"true":"false");++cases;
        }
    }
    cw131(saved);std::fclose(trace);std::printf("{\"status\":\"%s\",\"cases\":%u,\"failures\":%u,\"FP_modes\":12,\"full_CRT\":false}\n",failures?"FAIL":"PASS",cases,failures);return failures?3:0;
}
