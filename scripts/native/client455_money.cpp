#include "client455_money.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>

void RF455_FormatMoney(__int64 value,char* destination){
    if(!destination)return;
    const bool negative=value<0;
    if(negative){
        //7B2780 spills FILD to double before fabs, then converts with __ftol2.
        //Preserve rounding above2^53 and the INT64_MIN indefinite result.
        double spilled;unsigned short saved,truncate;
        __asm {fild value
            fstp spilled
            fnstcw saved}
        truncate=saved|0x0c00;
        __asm {fldcw truncate
            fld spilled
            fabs
            fistp value
            fldcw saved}
    }
    char digits[32];_i64toa_s(value,digits,sizeof(digits),10);
    const auto length=std::strlen(digits);const auto prefix=length%3;
    std::memcpy(destination,digits,prefix);destination[prefix]=0;
    for(std::size_t i=0;i<length/3;++i){if(i||prefix)std::strcat(destination,",");std::strncat(destination,digits+prefix+3*i,3);}
    if(negative){char temporary[32]={};std::sprintf(temporary,"-%s",destination);std::strcpy(destination,temporary);}
}
char* RF455_GetMoneyText(__int64 value){static char text[32];std::memset(text,0,sizeof(text));RF455_FormatMoney(value,text);return text;}
