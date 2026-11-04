#include "CResObject.h"
#include "client455_animation_timing.h"
#include <float.h>
#include <string>
extern "C" int RF455_RunAnimationTimingChecks(const char*,const char*);
class AnimationFrameFixture : public CResObject {
public:
    void Setup(CBone* bone,DWORD frame,DWORD carried,DWORD flags,bool interpolation,ANI_IP_INFO* ip,float speed){m_pBone=bone;m_dwOldBoneFrame=99;m_dwBoneFrame=frame;m_dwFrameNumForAStopTime=carried;m_dwStatusFlag=flags;m_bIsAniInterpolation=interpolation;m_pAniIPInfo=ip;m_Animation.SetAnimationSpeed(speed);m_dwEffectID[0]=m_dwEffectID[1]=0;}
    void Step(DWORD frame){CalculateCurrentAnimationFrame(frame);}
    DWORD Frame()const{return m_dwBoneFrame;}DWORD Old()const{return m_dwOldBoneFrame;}DWORD Carried()const{return m_dwFrameNumForAStopTime;}
    bool Interpolation()const{return m_bIsAniInterpolation!=FALSE;}bool Animating(){return m_Animation.IsAnimating()!=FALSE;}
    const void* Control()const{return &m_Animation;}
    ~AnimationFrameFixture(){m_pBone=nullptr;m_pAniIPInfo=nullptr;}
};
static int animationTimingScenarioProbe(){
    const char* output=std::getenv("RF_LAB_HELPER_OUTPUT");const char* golden=std::getenv("RF_TIMING_GOLDEN");if(!output || !golden)return 211;
    const char* dlls[]={"mss32.dll","ABuse.dll","Adv.dll","PDLL.dll"};for(const auto* d:dlls)if(GetModuleHandleA(d))return 212;
    std::string component=std::string(output)+".component.json";if(RF455_RunAnimationTimingChecks(golden,component.c_str()))return 213;
    const DWORD allocation=GetDmallocSize();const float savedTime=R3GetLoopTime();const unsigned saved=_control87(0,0);_clearfp();_control87(_MCW_EM|_PC_53|_RC_NEAR,_MCW_EM|_MCW_PC|_MCW_RC);unsigned checks=0,failures=0,cases=0;auto check=[&](bool b){++checks;if(!b)++failures;};
    struct Case {DWORD flags,current,carried,argument,maximum;bool interpolation,hasInfo;DWORD time,elapsed;float delta,speed;DWORD frame,old,carryAfter,timeAfter,elapsedAfter;bool interpolationAfter,animating;};
    const Case samples[]={
      {0,160,0,0xffffffff,1000,false,false,0,0,.03f,1,309,160,0,0,0,false,true},
      {0,160,17,777,1000,false,false,0,0,.03f,2,777,160,0,0,0,false,true},
      {0x200,160,7,777,1000,false,false,0,0,.03f,1,160,160,7,0,0,false,true},
      {0x100,160,0,0xffffffff,200,false,false,0,0,.03f,1,160,0,0,0,0,false,false},
      {0,160,0,0xffffffff,200,false,false,0,0,.03f,1,200,160,0,0,0,false,false},
      {0x800,160,0,0xffffffff,1000,true,true,100,50,.03f,1,160,160,0,0,0,false,true},
      {0x800,160,0,0xffffffff,1000,true,true,1000,50,.03f,1,160,160,0,1000,199,true,true},
      {0x800,160,0,777,1000,true,true,1000,10,.03f,1,777,160,0,1000,10,true,true},
      {0x800,160,17,0xffffffff,1000,true,false,0,0,.03f,1,160,160,0,0,0,true,true},
      {0,160,17,0xffffffff,1000,true,true,1000,10,.03f,1,160,160,0,1000,10,true,true},
      {0,160,17,0xffffffff,1000,false,false,0,0,.03f,0,160,160,0,0,0,false,true},
      {0,160,100,0xffffffff,1000,false,false,0,0,0,1,260,160,0,0,0,false,true},
      {0,0xfffffffd,0,0xffffffff,0xffffffff,false,false,0,0,.03f,0,0xfffffffd,0xfffffffd,0,0,0,false,true},
      {0,160,0,0xffffffff,1000,false,false,0,0,-1,1,1000,160,0,0,0,false,false},
      {0x100,160,0,0xffffffff,0,false,false,0,0,.03f,1,160,0,0,0,0,false,false}
    };
    for(const auto& row:samples){AnimationFrameFixture object;CBone bone={};bone.m_OMaxFrame=row.maximum;ANI_IP_INFO ip={};ip.dwAniInterpolationTime=row.time;ip.dwAniInterpolationFrame=row.elapsed;object.Setup(&bone,row.current,row.carried,row.flags,row.interpolation,row.hasInfo?&ip:nullptr,row.speed);R3SetLoopTime(row.delta);object.Step(row.argument);check(object.Frame()==row.frame && object.Old()==row.old && object.Carried()==row.carryAfter);check(object.Interpolation()==row.interpolationAfter && object.Animating()==row.animating);check(bone.m_Frame==row.frame);if(row.hasInfo)check(ip.dwAniInterpolationTime==row.timeAfter && ip.dwAniInterpolationFrame==row.elapsedAfter);++cases;}
    {AnimationFrameFixture object;object.Setup(nullptr,160,7,0,false,nullptr,1);object.Step(777);check(object.Frame()==160 && object.Old()==99 && object.Carried()==7 && !object.Animating());++cases;}
    {AnimationFrameFixture object;unsigned char expected[100]={};const unsigned invalid=0xffffffff,one=0x3f800000;std::memcpy(expected+4,&invalid,4);std::memcpy(expected+8,&one,4);for(unsigned i=0;i<10;++i)std::memcpy(expected+16+4*i,&invalid,4);check(!std::memcmp(object.Control(),expected,100));}
    R3SetLoopTime(savedTime);_clearfp();_control87(saved,_MCW_EM|_MCW_PC|_MCW_RC);check(GetDmallocSize()==allocation);for(const auto* d:dlls)check(!GetModuleHandleA(d));FILE* f=std::fopen(output,"wb");if(!f)return 214;std::fprintf(f,"{\"status\":\"%s\",\"actual_cases\":%u,\"checks\":%u,\"failures\":%u,\"dmalloc_balance\":%ld}\n",failures?"FAIL":"PASS",cases,checks,failures,static_cast<long>(GetDmallocSize()-allocation));std::fclose(f);return failures?215:0;
}
