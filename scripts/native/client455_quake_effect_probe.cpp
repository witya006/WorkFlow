#define RF455_QUAKE_PROBE
#define main registryEntry119
#include "client455_nuclear_registry_probe.cpp"
#undef main

namespace {
FILE* quakeTrace119=nullptr;CLevel* quakeLevel119=nullptr;D3DXMATRIX quakeBase119;unsigned quakeFrames119=0,quakeActive119=0,quakeMoved119=0;
unsigned quakeBits119(float f){unsigned u;std::memcpy(&u,&f,4);return u;}
void quakeArray119(const float* p,unsigned n){std::fputc('[',quakeTrace119);for(unsigned i=0;i<n;++i)std::fprintf(quakeTrace119,"%s%u",i?",":"",quakeBits119(p[i]));std::fputc(']',quakeTrace119);}
void quakeState119(){const auto& s=RF455_QuakeState();const float p[]={s.duration,s.remaining,s.density,s.amplitude[0],s.amplitude[1],s.amplitude[2],s.verticalScale,s.swayDensity,s.swayPeriod,s.swayRemaining,s.previous[0],s.previous[1],s.previous[2],s.next[0],s.next[1],s.next[2]};std::fprintf(quakeTrace119,"{\"phase\":%u,\"period\":%u,\"enabled\":%s,\"values\":",s.phase,s.period,s.swayEnabled?"true":"false");quakeArray119(p,16);std::fputc('}',quakeTrace119);}
}
void RF455_QuakeBeforeWorld119(){RF455_StartCameraSway(.4f,.3f);}
void RF455_QuakeBegin119(CLevel* level){
    check(!RF455_IsCameraSwayActive(),"actual successful map load stops sway");quakeLevel119=level;quakeBase119=GetR3State()->mMatView;quakeTrace119=std::fopen("quake-effects.json","wb");check(quakeTrace119!=nullptr,"quake trace");
    std::fputs("{\"camera\":",quakeTrace119);quakeArray119(GetR3State()->mInvMatView.m[3],3);std::fputs(",\"impact\":[0,0,1092616192],\"base\":",quakeTrace119);quakeArray119(&quakeBase119.m[0][0],16);std::fputs(",\"rows\":[\n",quakeTrace119);
}
void RF455_QuakeFrame119(){
    if(!quakeTrace119)return;auto* state=GetR3State();const auto& s=RF455_QuakeState();quakeActive119+=s.remaining>0;
    const bool separator=quakeFrames119!=0;++quakeFrames119;
    std::fprintf(quakeTrace119,"%s{\"frame\":%u,\"dt\":%u,\"toggle\":%d,\"before\":",separator?",\n":"",quakeFrames119,quakeBits119(R3GetLoopTime()),R3GetToggle30fps());quakeState119();
    quakeLevel119->SetViewMatrix(&quakeBase119);D3DXMatrixMultiply(&state->mMatViewProj,&state->mMatView,&state->mMatProj);check(SUCCEEDED(GetD3dDevice()->SetTransform(D3DTS_VIEW,&state->mMatView)),"publish actual quake view to device");
    D3DXMATRIX observed;check(SUCCEEDED(GetD3dDevice()->GetTransform(D3DTS_VIEW,&observed))&&!std::memcmp(&observed,&state->mMatView,64),"device retains quake matrix");
    bool moved=false;for(unsigned i=0;i<16;++i)moved|=(&quakeBase119.m[0][0])[i]!=(&state->mMatView.m[0][0])[i];quakeMoved119+=moved;
    std::fputs(",\"after\":",quakeTrace119);quakeState119();std::fputs(",\"view\":",quakeTrace119);quakeArray119(&state->mMatView.m[0][0],16);std::fputc('}',quakeTrace119);
}
int main(){const int result=registryEntry119();if(quakeTrace119){std::fprintf(quakeTrace119,"\n],\"frames\":%u,\"active_frames\":%u,\"moved_frames\":%u,\"load_stopped_sway\":true}\n",quakeFrames119,quakeActive119,quakeMoved119);std::fclose(quakeTrace119);}return result;}
