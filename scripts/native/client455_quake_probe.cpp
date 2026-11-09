#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "client455_quake.h"
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <cstdint>

static FILE* trace;
static unsigned events;
template<class Tag,typename Tag::Type Member>struct MemberAccess{friend typename Tag::Type access(Tag){return Member;}};
struct LevelView{using Type=D3DXMATRIX CLevel::*;friend Type access(LevelView);};template struct MemberAccess<LevelView,&CLevel::mMatView>;
static unsigned bits(float f){unsigned u;std::memcpy(&u,&f,4);return u;}
static void writeFloatArray(const float* p,unsigned n){std::fputc('[',trace);for(unsigned i=0;i<n;++i)std::fprintf(trace,"%s%u",i?",":"",bits(p[i]));std::fputc(']',trace);}
static void record(const char* op,const float* input,unsigned n,const float* output=nullptr,unsigned m=0){
    const auto& s=RF455_QuakeState();std::fprintf(trace,"%s{\"op\":\"%s\",\"dt\":%u,\"toggle\":%d,\"input\":",events++?",\n":"",op,bits(R3GetLoopTime()),R3GetToggle30fps());writeFloatArray(input,n);
    std::fprintf(trace,",\"output\":");writeFloatArray(output,m);std::fprintf(trace,",\"phase\":%u,\"period\":%u,\"enabled\":%s,\"state\":",s.phase,s.period,s.swayEnabled?"true":"false");
    const float values[]={s.duration,s.remaining,s.density,s.amplitude[0],s.amplitude[1],s.amplitude[2],s.verticalScale,s.swayDensity,s.swayPeriod,s.swayRemaining,s.previous[0],s.previous[1],s.previous[2],s.next[0],s.next[1],s.next[2]};writeFloatArray(values,16);std::fputc('}',trace);
}
static void start(float duration,float density){R3EnvironmentQuake(duration,density);const float p[]={duration,density};record("start",p,2);}
static void sway(float density,float period){RF455_StartCameraSway(density,period);const float p[]={density,period};record("sway",p,2);}
static void stop(){RF455_StopCameraSway();record("stop",nullptr,0);}
static void seed(unsigned n){std::srand(n);const float p[]={float(n)};record("seed",p,1);}
static void heading(float x,float z){auto& view=GetR3State()->mMatView;D3DXMatrixIdentity(&view);view.m[2][2]=x;view.m[2][0]=z;const float p[]={x,z};record("heading",p,2);}
static void sampleVector(){float p[]={7,-8,9};const float before[]={7,-8,9};R3GetQuakeVector(p);record("vector",before,3,p,3);}
static void matrix(){float p[4][4];for(unsigned i=0;i<16;++i)(&p[0][0])[i]=float(i+1)/4;float before[16];std::memcpy(before,p,64);R3GetQuakeMatrix(p);record("matrix",before,16,&p[0][0],16);}
int main(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);trace=std::fopen("trace.json","wb");if(!trace)return 2;std::fputs("[\n",trace);
    heading(1,0);R3SetLoopTime(1.f/30);sampleVector();matrix();
    for(float dt:{1.f/30,.05f,1.f/144,.042f}){R3SetLoopTime(dt);start(.23f,150);for(unsigned i=0;i<12;++i)sampleVector();}
    heading(.6f,-.8f);R3SetLoopTime(.05f);start(.4f,-20);for(unsigned i=0;i<10;++i)sampleVector();
    start(.18f,12);sampleVector();matrix();sampleVector();matrix();matrix();sampleVector();start(0,20);sampleVector();start(-2,20);matrix();
    R3SetLoopTime(.025f);seed(413);sway(1.5f,.15f);for(unsigned i=0;i<18;++i)sampleVector();stop();sampleVector();sway(.4f,0);for(unsigned i=0;i<6;++i)sampleVector();
    start(.2f,30);for(unsigned i=0;i<12;++i)sampleVector();stop();sampleVector();
    CLevel level;R3SetLoopTime(.05f);heading(0,1);start(.3f,6);
    for(unsigned i=0;i<8;++i){D3DXMATRIX view;D3DXMatrixIdentity(&view);view.m[2][2]=i%2?0.f:1.f;view.m[2][0]=i%2?1.f:0.f;view.m[3][0]=10;view.m[3][1]=-20;view.m[3][2]=30;float input[16];std::memcpy(input,&view,64);level.SetViewMatrix(&view);float output[32];std::memcpy(output,&(level.*access(LevelView{})),64);std::memcpy(output+16,&GetR3State()->mMatView,64);record("view",input,16,output,32);}
    float camera[]={31,-17,9};for(unsigned i=0;i<3;++i)GetR3State()->mInvMatView.m[3][i]=camera[i];for(float distance:{0.f,199.99f,200.f,200.01f,500.f,799.99f,800.f,800.01f,1300.f}){float p[]={camera[0]+distance,camera[1],camera[2]},input[]={camera[0],camera[1],camera[2],p[0],p[1],p[2]},out=GetDensityFromPos(p);record("density",input,6,&out,1);}
    float point[]={100,300,-45},input[]={camera[0],camera[1],camera[2],point[0],point[1],point[2]},out=GetDensityFromPos(point);record("density",input,6,&out,1);
    std::fputs("\n]\n",trace);std::fclose(trace);std::printf("quake events=%u\n",events);return 0;
}
