#include "client455_sky_lighting_math.h"
#include <cstdio>
#include <cstring>
#include <cmath>
#include <initializer_list>

static unsigned bits127(float value){unsigned result;std::memcpy(&result,&value,4);return result;}
static unsigned short control127(){unsigned short value;__asm { fnstcw value } return value;}
static void control127(unsigned short value){__asm { fldcw value }}

int main(){
    const unsigned short saved=control127();unsigned cases=0;
    const float rgb[12][3]={{0,0,0},{1,1,1},{.5f,.5f,.5f},{.487017f,.36861f,.19005f},
        {.1f,.2f,.3f},{.9f,.8f,.7f},{1.f/255,2.f/255,3.f/255},
        {.99999994f,.33333334f,.66666669f},{.125f,.25f,.75f},
        {std::nextafter(.5f,0.f),.5f,std::nextafter(.5f,1.f)},
        {.001f,.002f,.003f},{.0138f,.0113f,.008f}};
    const DWORD fog[]={0,0xffffffff,0xff123456,0x7ffedcba};
    const float alpha[]={0,1,.1f,.33333334f,.99999994f,-.1f,1.1f};
    const DWORD bases[]={0,0xffffffff,0x80123456,0x7ffedcba,0xff010101,0x12345678,0xff808080,0xffffffff};
    const DWORD tints[]={0xffffffff,0xffffffff,0xff102030,0xfffedcba,0xff010101,0xff808080,0xff808080,0};
    const DWORD counts[]={0,1,289,289,289,289,0x80000000u,0xffffffffu};
    for(unsigned pc:{0u,2u,3u}){
        const unsigned short cw=(saved&~0xf00u)|(pc<<8);control127(cw);
        for(unsigned i=0;i<12;++i){
            const float a=alpha[i%7];const DWORD old=fog[i%4];
            const DWORD tint=RF455_SkyTintColor(rgb[i],old),direct=RF455_SunDirectColor(rgb[i],a);
            if(control127()!=cw)return 10;
            std::printf("{\"kind\":\"sun\",\"cw\":%u,\"rgb\":[%u,%u,%u],\"alpha\":%u,\"fog\":%u,\"tint\":%u,\"direct\":%u}\n",cw,bits127(rgb[i][0]),bits127(rgb[i][1]),bits127(rgb[i][2]),bits127(a),old,tint,direct);++cases;
        }
        for(unsigned i=0;i<15;++i){
            const float weight=alpha[i%7];const DWORD day=fog[i%4],night=fog[(i+1)%4];
            const float start=RF455_SkyWeightedFloat(3.125f,30.333334f,weight);
            const float end=RF455_SkyWeightedFloat(900.125f,7000.3335f,weight);
            const DWORD color=RF455_SkyFogColor(day,night,weight);
            if(control127()!=cw)return 11;
            std::printf("{\"kind\":\"fog\",\"cw\":%u,\"weight\":%u,\"day\":%u,\"night\":%u,\"start\":%u,\"end\":%u,\"color\":%u}\n",cw,bits127(weight),day,night,bits127(start),bits127(end),color);++cases;
        }
        for(unsigned i=0;i<8;++i){
            const DWORD value=RF455_ModulateSkyTint(bases[i],tints[i]);
            std::printf("{\"kind\":\"filter\",\"cw\":%u,\"base\":%u,\"tint\":%u,\"value\":%u}\n",cw,bases[i],tints[i],value);++cases;
            const float exposure=alpha[i%7];const DWORD divisor=RF455_SkyFogDivisor(counts[i],exposure);
            if(control127()!=cw)return 12;
            std::printf("{\"kind\":\"divisor\",\"cw\":%u,\"count\":%u,\"exposure\":%u,\"value\":%u}\n",cw,counts[i],bits127(exposure),divisor);++cases;
        }
    }
    control127(saved);return cases==129?0:20;
}
