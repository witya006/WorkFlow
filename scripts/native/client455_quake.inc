namespace {
RF455QuakeState quake455;
float noiseQuake455(std::uint32_t x){
    x=(x<<13)^x;const std::uint32_t value=(x*(x*x*15731u+789221u)+1376312589u)&0x7fffffffu;
    return static_cast<float>(1.0-double(value)*9.31322574615478515625e-10);
}
std::uint32_t truncQuake455(double value){return static_cast<std::uint32_t>(static_cast<long long>(value));}
void cameraSway455(float* out){
    auto& s=quake455;
    if(!s.swayEnabled){out[0]=out[1]=out[2]=0;return;}
    s.swayRemaining=static_cast<float>(double(s.swayRemaining)-R3GetLoopTime());
    if(s.swayRemaining<0){
        memcpy(s.previous,s.next,12);
        const auto range=truncQuake455(256.0*s.swayDensity);
        for(unsigned i=0;i<3;++i)s.next[i]=static_cast<float>((double(unsigned(rand())%range)-double(s.swayDensity)*128.0)*0.00390625);
        const auto periodRange=truncQuake455(128.0*s.swayPeriod);
        s.swayRemaining=static_cast<float>((double(unsigned(rand())%periodRange)-double(s.swayPeriod)*64.0)*0.00390625+s.swayPeriod);
    }
    const float ratio=static_cast<float>((double(s.swayPeriod)-s.swayRemaining)/s.swayPeriod);
    const float angle=static_cast<float>(double(ratio)*3.1415927410125732421875);
    const float c=static_cast<float>(cos(double(angle)));
    const float mix=static_cast<float>((2.0-(double(c)+1.0))*0.5);
    for(unsigned i=0;i<3;++i)out[i]=static_cast<float>(double(s.next[i])*mix+double(s.previous[i])*(1.0-double(mix)));
}
}
const RF455QuakeState& RF455_QuakeState(){return quake455;}
void RF455_StartCameraSway(float density,float period){auto& s=quake455;s.swayDensity=density;s.swayPeriod=period==0?0.02f:period;s.swayRemaining=0;s.swayEnabled=true;}
void RF455_StopCameraSway(){quake455.swayEnabled=false;}
bool RF455_IsCameraSwayActive(){return quake455.swayEnabled;}
void R3EnvironmentQuake(float seconds,float density){
    auto& s=quake455;s.phase=0;s.duration=seconds;s.remaining=seconds;s.density=density;
    const float milliseconds=static_cast<float>(R3GetLoopTime()*1000.0);
    s.period=truncQuake455(42.0/milliseconds+double(0.999f))+1u;if(!s.period)s.period=1;
}
void R3GetQuakeVector(Vector3f out){
    cameraSway455(out);auto& s=quake455;if(!(s.remaining>0))return;
    const float dt=R3GetLoopTime();
    if(s.phase%s.period==0){
        auto* state=GetR3State();float x=state->mMatView.m[2][2];const float z=state->mMatView.m[2][0];
        if(fabs(double(x))<0.01f&&fabs(double(z))<0.01f)x=0;
        const float sum=static_cast<float>(double(z)*z+double(x)*x);
        const float length=static_cast<float>(sqrt(double(sum)));
        const float normalized=static_cast<float>(double(x)/length);
        const float angle=static_cast<float>(acos(double(normalized)));
        const float toggle=static_cast<float>(R3GetToggle30fps());
        const float alpha=static_cast<float>(1.0-(double(s.duration)-s.remaining)/s.duration);
        const float cx=static_cast<float>(cos(double(angle)));
        const float sx=static_cast<float>(double(cx)*toggle);
        s.amplitude[0]=static_cast<float>(double(sx)*alpha*s.density);
        const float ny=static_cast<float>(double(noiseQuake455(truncQuake455(double(dt)*1000.0+200.0)))*alpha*s.verticalScale);
        s.amplitude[1]=static_cast<float>(double(s.density)*ny);
        const float cz=static_cast<float>(sin(double(angle)));
        const float sz=static_cast<float>(double(cz)*toggle);
        s.amplitude[2]=static_cast<float>(double(sz)*alpha*s.density);
    }
    ++s.phase;for(unsigned i=0;i<3;++i)out[i]=static_cast<float>((1.0/double(s.period))*s.amplitude[i]*double(s.phase)+out[i]);
    if(s.phase>=s.period)s.phase=0;
    s.remaining=static_cast<float>(double(s.remaining)-R3GetLoopTime());if(s.remaining<0)s.remaining=0;
}
void R3GetQuakeMatrix(float matrix[4][4]){
    auto& s=quake455;if(!(s.remaining>0))return;const float dt=R3GetLoopTime();
    s.remaining=static_cast<float>(double(s.remaining)-R3GetLoopTime());if(s.remaining<0)s.remaining=0;
    const float alpha=static_cast<float>(1.0-(double(s.duration)-s.remaining)/s.duration);
    const double base=double(dt)*1000.0;
    for(unsigned i=0;i<3;++i){const float noise=static_cast<float>(double(noiseQuake455(truncQuake455(base+200.0*i)))*alpha);matrix[3][i]=static_cast<float>(double(s.density)*noise+matrix[3][i]);}
}
