#include "client455_secondary.h"
#include <cstring>

namespace {
template<class T>T get(const void* p,unsigned at){T v;std::memcpy(&v,static_cast<const unsigned char*>(p)+at,sizeof(v));return v;}
template<class T>void put(void* p,unsigned at,T v){std::memcpy(static_cast<unsigned char*>(p)+at,&v,sizeof(v));}
double number(unsigned long long bits){double result;std::memcpy(&result,&bits,8);return result;}
void copyFloat(void* destination,const void* source){__asm{mov eax,source
    mov edx,destination
    fld dword ptr[eax]
    fstp dword ptr[edx]}}
float add(float value,double step){float r;__asm{fld value
    fadd step
    fstp r}return r;}
float subtract(float a,float b){float r;__asm{fld a
    fsub b
    fstp r}return r;}
float absolute(float a){float r;__asm{fld a
    fabs
    fstp r}return r;}
float affine(float value,double factor,double bias){float r;__asm{fld value
    fmul factor
    fadd bias
    fstp r}return r;}
float multiply(float value,double factor){float r;__asm{fld value
    fmul factor
    fstp r}return r;}
bool less(float value,double limit){unsigned result=0;__asm{fld value
    fcomp limit
    fnstsw ax
    and ah,45h
    cmp ah,1
    jne done
    mov result,1
done:}return result!=0;}
bool greater(float value,double limit){unsigned result=0;__asm{fld value
    fcomp limit
    fnstsw ax
    and ah,45h
    jne done
    mov result,1
done:}return result!=0;}
bool productLess(float a,float b,double limit){unsigned result=0;__asm{fld a
    fmul b
    fcomp limit
    fnstsw ax
    and ah,45h
    cmp ah,1
    jne done
    mov result,1
done:}return result!=0;}
float relax(float value){float r;const double center=.2,factor=.8;__asm{fld value
    fld center
    fsubr st,st(1)
    fmul factor
    fsubp st(1),st
    fstp r}return r;}
void oscillator(RF455SecondaryState* state,unsigned index,float weight){
    float* value=state->value+index;int* direction=state->direction+index;float* minimum=state->minimum+index;float* maximum=state->maximum+index;
    const double margin=.3,step=.01,marginFloat=number(0x3fd3333340000000ull),rate=number(0x3f747ae140000000ull),bias=.005,half=.5;float temporary;
    // Preserve the x87 stack operation order and every m32 store of91E356..418.
    __asm{mov edx,value
        mov edi,direction
        mov esi,minimum
        mov ecx,maximum
        fld margin
        fld step
        fld marginFloat
        fld rate
        fld bias
        fld dword ptr[edx]
        fld dword ptr[ecx]
        fsub st,st(5)
        fcompp
        fnstsw ax
        test ah,5
        jp lower
        mov dword ptr[edi],0ffffffffh
        fld dword ptr[ecx]
        fsub st,st(4)
        fstp dword ptr[edx]
    lower:
        fld dword ptr[edx]
        fld dword ptr[esi]
        fadd st,st(5)
        fcompp
        fnstsw ax
        test ah,41h
        jnz integrate
        mov dword ptr[edi],1
        fld dword ptr[esi]
        fadd st,st(4)
        fstp dword ptr[edx]
        fld dword ptr[ecx]
        fld dword ptr[esi]
        fcompp
        fnstsw ax
        test ah,5
        jp integrate
        fld dword ptr[ecx]
        fmul half
        fstp temporary
        fld temporary
        fst dword ptr[ecx]
        fld dword ptr[esi]
        fadd st,st(4)
        fcompp
        fnstsw ax
        test ah,41h
        jnz integrate
        fld dword ptr[esi]
        fadd st,st(5)
        fstp dword ptr[ecx]
    integrate:
        fld dword ptr[ecx]
        fmul half
        fld dword ptr[edx]
        fsubr st,st(1)
        fstp temporary
        fld temporary
        fabs
        fstp temporary
        fsub temporary
        fmul st,st(2)
        fadd st,st(1)
        fld dword ptr[ecx]
        fsub dword ptr[esi]
        fmulp st(1),st
        fstp temporary
        fld temporary
        fild dword ptr[edi]
        fmul weight
        fmulp st(1),st
        fadd dword ptr[edx]
        fstp dword ptr[edx]
        fstp st
        fstp st
        fstp st
        fstp st
        fstp st}
}
bool valid(const RF455SecondaryContext* c){return c && c->globals && c->math.pose.matrix.multiply && c->math.pose.rotationQuaternion && c->math.rotationX && c->math.rotationY && c->math.rotationZ && c->math.quaternionMatrix && c->math.quaternionAxis && c->math.ticks && c->math.sineFloat;}
void skirtKick(RF455SecondaryState* s,unsigned time,unsigned* last,bool right){
    for(unsigned i=0;i<3;++i){s->direction[i]=-1;s->minimum[i]=0;s->maximum[i]=1.25f;}
    if(time-*last>10){*last=time;const unsigned driven=right?1:0,centered=right?0:1;s->value[driven]=add(s->value[driven],number(0x3f847ae140000000ull));s->value[2]=add(s->value[2],number(0x3f847ae140000000ull));
        if(less(s->value[centered],number(0x3fc9581068a3d70aull)) || greater(s->value[centered],number(0x3fc9db22d75c28f6ull)))s->value[centered]=relax(s->value[centered]);
        if(greater(s->value[driven],.3))s->value[driven]=.3f;if(greater(s->value[2],.3))s->value[2]=.3f;
    }
    s->maximum[2]=.5f;s->maximum[right?0:1]=.3f;
}
}
extern "C" RF455PoseStatus RF455_ApplySecondaryMotion(RF455CharacterStorage* model,RF455MeshStorage* mesh,const RF455SecondaryContext* context){
    if(!model || !mesh)return RF_POSE_ARGUMENT;
    auto* b=reinterpret_cast<unsigned char*>(model);auto* state=get<RF455SecondaryState*>(b,1184);if(!state)return RF_POSE_OK;
    if(!valid(context))return RF_POSE_SECONDARY;
    auto& math=context->math;auto& globals=*context->globals;auto* m=mesh->bytes;const unsigned time=math.ticks();
    if(time-state->lastTick>10){state->lastTick=time;const float weight[]={1.3f,1.2f,.97f,1,1};for(unsigned i=0;i<5;++i)oscillator(state,i,weight[i]);}
    if(!std::memchr(m,0,256))return RF_POSE_BOUNDS;const auto* name=reinterpret_cast<const char*>(m);
    if(!std::strcmp(name,"Bip01 Ponytail L1")){
        globals.phase=add(globals.phase,number(0x3f50624de0000000ull));
        if(time-globals.ponyTick>10){globals.ponyTick=time;const float dz=subtract(get<float>(m,4886),globals.ponyPosition[2]);const float dy=absolute(subtract(get<float>(m,4882),globals.ponyPosition[1]));
            if(greater(dy,number(0x3fc99999a0000000ull))){state->direction[3]=-1;state->minimum[3]=0;state->maximum[3]=1;if(greater(state->value[3],number(0x3fd99999a0000000ull)))state->value[3]=.4f;}
            if(less(dz,-.1)){state->direction[3]=-1;state->minimum[3]=0;state->maximum[3]=1;if(greater(state->value[3],number(0x3fd99999a0000000ull)))state->value[3]=.1f;}
            for(unsigned i=0;i<3;++i)copyFloat(globals.ponyPosition+i,m+4878+4*i);
        }
        float oldPosition[3];for(unsigned i=0;i<3;++i)copyFloat(oldPosition+i,m+4878+4*i);float sine;math.sineFloat(&sine,&globals.phase);const float angleZ=multiply(sine,.2),angleX=affine(state->value[3],.5,number(0x3fb99999a0000000ull));float z[16],x[16],base[16],quaternion[4];
        if(!math.rotationZ(z,angleZ) || !math.rotationX(x,angleX) || !math.pose.matrix.multiply(x,z,x) || !math.pose.matrix.multiply(base,m+4574,b+992) || !math.pose.matrix.multiply(m+4830,base,b+800) || !math.pose.matrix.multiply(m+4830,x,m+4830) || !math.quaternionMatrix(quaternion,m+4830) || !math.pose.rotationQuaternion(m+4830,quaternion))return RF_POSE_MATRIX;
        for(unsigned i=0;i<3;++i)copyFloat(m+4878+4*i,oldPosition+i);
    }
    if(!std::strcmp(name,"Bip01 Ponytail L11")){
        auto* parent=get<RF455MeshStorage*>(m,518);if(!parent)return RF_POSE_ARGUMENT;float rotation[16];const float angle=multiply(state->value[3],1.5);
        if(!math.pose.matrix.multiply(m+4830,m+4702,parent->bytes+4830) || !math.rotationX(rotation,angle) || !math.pose.matrix.multiply(m+4830,rotation,m+4830))return RF_POSE_MATRIX;
    }
    const bool right=!std::strcmp(name,"Bip01 R skirt"),left=!std::strcmp(name,"Bip01 L skirt");
    if(right || left){float quaternion[4];if(!math.quaternionMatrix(quaternion,b+(right?928:864)))return RF_POSE_MATRIX;
        if(productLess(quaternion[3],quaternion[2],-.2))skirtKick(state,time,right?&globals.rightTick:&globals.leftTick,right);
        const float axis[]={0,right?.2f:-.2f,-1};float axisQuaternion[4],unusedPoseQuaternion[4],base[16],rotation[16];
        if(!math.quaternionAxis(axisQuaternion,axis,state->value[right?0:1]) || !math.quaternionMatrix(unusedPoseQuaternion,m+4830) || !math.pose.matrix.multiply(base,m+4574,b+(right?1120:1056)) || !math.pose.rotationQuaternion(rotation,axisQuaternion) || !math.pose.matrix.multiply(m+4830,base,b+(right?928:864)) || !math.pose.matrix.multiply(m+4830,rotation,m+4830))return RF_POSE_MATRIX;
    }
    if(!std::strcmp(name,"Bip01 B skirt")){const float half=.5f;float angle;const float value=state->value[2];__asm{fld half
            fsub value
            fstp angle}float unused[16],rotation[16];
        if(!math.rotationY(unused,angle) || !math.rotationZ(rotation,state->value[2]) || !math.pose.matrix.multiply(m+4830,rotation,m+4830))return RF_POSE_MATRIX;
    }
    return RF_POSE_OK;
}
