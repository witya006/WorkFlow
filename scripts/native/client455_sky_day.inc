// Included once by the derived level.cpp, beside the ordinary map/frame owner.
// Target BF7344 starts1. Profile constructor900AB0 sets its night field to0.
static int rf455SkyDayEnabled=1;
static float rf455SkyNightWeight=0;
int RF455_SetSkyDayEnabled(int value){return rf455SkyDayEnabled=value;}
int RF455_GetSkyDayEnabled(){return rf455SkyDayEnabled;}
float RF455_GetSkyNightWeight(){return rf455SkyNightWeight;}

void RF455_UpdateSkyNightWeight(){
    //8B1F20:disabled mode preserves the last profile, even across map changes.
    if(!rf455SkyDayEnabled)return;
    const float day=RF455_GetDayFraction();
    const double duskStart=0.791666686534881591796875;
    const double duskEnd=0.854166686534881591796875;
    const double dawnStart=0.20833332836627960205078125;
    const float dawnEnd=0.3333333432674407958984375f;
    const double dawnDuration=0.12500001490116119384765625;
    const double duskRate=16.0;float result;
    if(day>duskStart && day<duskEnd){
        __asm { fld day
                fsub duskStart
                fmul duskRate
                fstp result }
    }else if(day>dawnStart && day<dawnEnd){
        __asm { fld day
                fsub dawnStart
                fdiv dawnDuration
                fld1
                fsubrp st(1),st
                fstp result }
    }else{
        // Preserve the original boundary discontinuity:exact dawnEnd is1.
        result=(day>dawnEnd && day<duskStart)?0.0f:1.0f;
    }
    rf455SkyNightWeight=result;
}
