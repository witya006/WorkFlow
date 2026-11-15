#include "client455_weather_parameters.h"
#include <stdlib.h>

DWORD RF455_MaterialWeather=0;
DWORD RF455_GetMaterialWeather(){return RF455_MaterialWeather;}
static DWORD weatherInteger455(double value){
    const double maximum=255;__int64 result;unsigned short saved,truncation;
    __asm{fld value
        fmul maximum
        fnstcw saved}
    truncation=saved|0xc00;
    __asm{fldcw truncation
        fistp result
        fldcw saved}
    return DWORD(result);
}
template<class Read> static bool readWeatherParameters455(Read read,char* token){
    // Caller folds case once,after environment/fog tags. Consumed argument is
    // not folded again. Preserve unchecked atof/truncation and overlapping bits.
    if(!strcmp(token,"*weather")){
        if(!read())return false;
        const DWORD value=weatherInteger455(atof(token));
        RF455_MaterialWeather=(RF455_MaterialWeather&0xffffff00u)|value;
    }
    if(!strcmp(token,"*haze")){
        if(!read())return false;
        const DWORD value=weatherInteger455(atof(token));
        RF455_MaterialWeather=(RF455_MaterialWeather&0xffff00ffu)|(value<<8);
    }
    if(!strcmp(token,"*special_weather")){
        if(!read())return false;
        const DWORD value=weatherInteger455(atof(token));
        RF455_MaterialWeather=(RF455_MaterialWeather&0xff00ffffu)|(value<<16);
    }
    return true;
}
void RF455_ReadWeatherParameters(FILE* file,char* token){
    readWeatherParameters455([&]{return file&&fscanf(file,"%255s",token)==1;},token);
}
