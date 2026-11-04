#include "client455_pose.h"
#include "client455_secondary.h"
#include <cstring>
#include <cstdio>

namespace {
template<class T>T get(const void* p,unsigned at){T v;std::memcpy(&v,static_cast<const unsigned char*>(p)+at,sizeof(v));return v;}
template<class T>void put(void* p,unsigned at,T v){std::memcpy(static_cast<unsigned char*>(p)+at,&v,sizeof(v));}
void copyFloat(void* destination,const void* source){__asm{mov eax,source
    mov edx,destination
    fld dword ptr[eax]
    fstp dword ptr[edx]}}
bool contains(const RF455PoseSpan* span,const void* p,std::size_t n){
    if(!span || !span->bytes || !p)return false;
    const auto first=reinterpret_cast<std::uintptr_t>(span->bytes),at=reinterpret_cast<std::uintptr_t>(p);
    return at>=first && at-first<=span->length && n<=span->length-(at-first);
}
bool mathValid(const RF455PoseMath* p){return p && p->matrix.inverse && p->matrix.multiply && p->slerp && p->rotationQuaternion;}
void identity(float* m){std::memset(m,0,64);m[0]=m[5]=m[10]=m[15]=1;}
float keyRatio(int numerator,unsigned denominator){
    float result;const float unsignedFix=4294967296.0f;
    __asm{cmp denominator,0
        je zero
        fild numerator
        fild denominator
        test denominator,80000000h
        jz divide
        fadd unsignedFix
    divide:
        fdivp st(1),st
        jmp store
    zero:
        fldz
    store:
        fstp result}
    return result;
}
float divideFloat(const void* a,const void* b){float r;__asm{mov eax,a
    mov edx,b
    fld dword ptr[eax]
    fdiv dword ptr[edx]
    fstp r}return r;}
float unsignedRatio(unsigned a,unsigned b){
    float r;const float fix=4294967296.0f;
    __asm{fild a
        test a,80000000h
        jz denominator
        fadd fix
    denominator:
        fild b
        test b,80000000h
        jz divide
        fadd fix
    divide:
        fdivp st(1),st
        fstp r}
    return r;
}
bool orderedLess(float a,float b){unsigned r=0;__asm{fld b
    fld a
    fcompp
    fnstsw ax
    and ah,45h
    cmp ah,1
    jne done
    mov r,1
done:}return r!=0;}
bool orderedLE(float a,float b){unsigned r=0;__asm{fld b
    fld a
    fcompp
    fnstsw ax
    and ah,45h
    cmp ah,1
    je yes
    cmp ah,40h
    jne done
yes:mov r,1
done:}return r!=0;}
void interpolate3(float* out,unsigned step,const unsigned char* a,const unsigned char* b,float t){
    for(unsigned i=0;i<3;++i){float* target=out+step*i;const auto* left=a+4*i;const auto* right=b+4*i;
        __asm{mov eax,left
            mov edx,right
            mov ecx,target
            fld dword ptr[eax]
            fld dword ptr[edx]
            fsubr st,st(1)
            fmul t
            fsubp st(1),st
            fstp dword ptr[ecx]}
    }
}
// FrameMove has three separate m32 stores for each element: no FMA or
// collapsed (1-t)*old+t*new expression may replace them.
void blend(float* out,const float* current,const float* previous,float ratio){
    float inverse;__asm{fld1
        fsub ratio
        fstp inverse}
    for(unsigned i=0;i<16;++i){float a,b;const float* p=current+i;const float* q=previous+i;float* r=out+i;
        __asm{mov eax,p
            fld dword ptr[eax]
            fmul ratio
            fstp a
            mov eax,q
            fld dword ptr[eax]
            fmul inverse
            fstp b
            fld b
            fadd a
            mov eax,r
            fstp dword ptr[eax]}
    }
}
void ramp(float* out,const float* current,const float* base,float ratio){
    for(unsigned i=0;i<16;++i){float difference,product;const float* a=current+i;const float* b=base+i;float* c=out+i;
        __asm{mov eax,a
            mov edx,b
            fld dword ptr[eax]
            fsub dword ptr[edx]
            fstp difference
            fld difference
            fmul ratio
            fstp product
            fld product
            fadd dword ptr[edx]
            mov eax,c
            fstp dword ptr[eax]}
    }
}
RF455PoseStatus modifier(float* matrix,const unsigned char* mesh,const RF455PoseMath& math){
    float translation[3];for(unsigned i=0;i<3;++i)copyFloat(translation+i,matrix+12+i);
    if(!math.matrix.multiply(matrix,matrix,mesh+5503))return RF_POSE_MATRIX;
    for(unsigned i=0;i<3;++i)copyFloat(matrix+12+i,translation+i);return RF_POSE_OK;
}
RF455PoseStatus evaluate(float* output,int frame,const RF455MeshStorage* mesh,
    const RF455AnimationData* data,const RF455PoseContext* context,bool applyModifier){
    RF455PoseSpan owner={};if(!context->resolveOwner(context->ownerContext,data,&owner))return RF_POSE_BOUNDS;
    auto status=RF455_ApplyPoseScale(output,frame,mesh,data,&owner,&context->math);if(status!=RF_POSE_OK)return status;
    if(applyModifier){status=modifier(output,mesh->bytes,context->math);if(status!=RF_POSE_OK)return status;}
    status=RF455_ApplyPoseRotation(output,frame,mesh,data,&owner,&context->math);if(status!=RF_POSE_OK)return status;
    return RF455_ApplyPoseTranslation(output,frame,mesh,data,&owner);
}
}
extern "C" RF455PoseStatus RF455_SelectPoseKeys(const RF455AnimationChannel* channel,unsigned stride,
    int frame,int linearSearch,const RF455PoseSpan* owner,RF455PoseKeyPair* output){
    if(!channel || !output || (stride!=16 && stride!=20))return RF_POSE_ARGUMENT;
    const unsigned count=static_cast<unsigned short>(channel->count);if(!count)return RF_POSE_ARGUMENT;
    if(!contains(owner,channel->keys,count*stride))return RF_POSE_BOUNDS;
    const unsigned last=count-1;unsigned selected=0;
    const auto time=[&](unsigned i){return get<int>(channel->keys+stride*i,stride-4);};
    if(frame>=time(last))selected=last?last-1:0;
    else if(linearSearch){for(unsigned i=0;i<last;++i)if(frame<time(i)){selected=i?i-1:0;break;}}
    else{unsigned lo=0,hi=last;while((hi-lo)>>1){const unsigned mid=lo+((hi-lo)>>1);if(frame>=time(mid))lo=mid;else hi=mid;}selected=lo;}
    const auto* left=channel->keys+selected*stride;const auto* right=left+stride;
    if(!contains(owner,left,2*stride))return RF_POSE_BOUNDS;
    const unsigned start=get<unsigned>(left,stride-4),delta=get<unsigned>(right,stride-4)-start;
    const unsigned difference=static_cast<unsigned>(frame)-start;int numerator;std::memcpy(&numerator,&difference,4);
    *output={left,right,selected,keyRatio(numerator,delta)};return RF_POSE_OK;
}
extern "C" RF455PoseStatus RF455_ApplyPoseScale(float* matrix,int frame,const RF455MeshStorage* mesh,
    const RF455AnimationData* data,const RF455PoseSpan* owner,const RF455PoseMath* math){
    if(!matrix || !mesh || !data || !mathValid(math))return RF_POSE_ARGUMENT;
    if(!static_cast<unsigned short>(data->channel[2].count))return math->matrix.multiply(matrix,matrix,mesh->bytes+4766)?RF_POSE_OK:RF_POSE_MATRIX;
    RF455PoseKeyPair keys={};const auto status=RF455_SelectPoseKeys(data->channel+2,16,frame,1,owner,&keys);if(status!=RF_POSE_OK)return status;
    interpolate3(matrix,5,keys.left,keys.right,keys.ratio);
    float axis[16]={};for(unsigned i=0;i<3;++i)copyFloat(axis+5*i,mesh->bytes+5483+4*i);axis[15]=1;
    return math->matrix.multiply(matrix,matrix,axis)?RF_POSE_OK:RF_POSE_MATRIX;
}
extern "C" RF455PoseStatus RF455_ApplyPoseRotation(float* matrix,int frame,const RF455MeshStorage* mesh,
    const RF455AnimationData* data,const RF455PoseSpan* owner,const RF455PoseMath* math){
    if(!matrix || !mesh || !data || !mathValid(math))return RF_POSE_ARGUMENT;
    float rotation[16];
    if(static_cast<unsigned short>(data->channel[0].count)){
        RF455PoseKeyPair keys={};const auto status=RF455_SelectPoseKeys(data->channel,20,frame,0,owner,&keys);if(status!=RF_POSE_OK)return status;
        float quaternion[4];if(!math->slerp(quaternion,keys.left,keys.right,keys.ratio))return RF_POSE_MATRIX;
        float* w=quaternion+3;__asm{mov eax,w
            fld dword ptr[eax]
            fchs
            fstp dword ptr[eax]}
        if(!math->rotationQuaternion(rotation,quaternion) || !math->matrix.multiply(matrix,matrix,rotation))return RF_POSE_MATRIX;
        for(unsigned i=0;i<3;++i)copyFloat(matrix+12+i,mesh->bytes+4750+4*i);
    }else{
        if(mesh->bytes[512]){const auto* parent=get<const RF455MeshStorage*>(mesh->bytes,518);if(!parent)return RF_POSE_ARGUMENT;float inverse[16];if(!math->matrix.inverse(inverse,nullptr,parent->bytes+5022) || !math->matrix.multiply(rotation,mesh->bytes+5022,inverse))return RF_POSE_MATRIX;}
        else std::memcpy(rotation,mesh->bytes+5022,64);
        rotation[12]=rotation[13]=rotation[14]=0;
        if(!math->matrix.multiply(matrix,matrix,rotation))return RF_POSE_MATRIX;
    }
    return RF_POSE_OK;
}
extern "C" RF455PoseStatus RF455_ApplyPoseTranslation(float* matrix,int frame,const RF455MeshStorage* mesh,
    const RF455AnimationData* data,const RF455PoseSpan* owner){
    if(!matrix || !mesh || !data)return RF_POSE_ARGUMENT;
    if(!static_cast<unsigned short>(data->channel[1].count)){for(unsigned i=0;i<3;++i)copyFloat(matrix+12+i,mesh->bytes+4750+4*i);return RF_POSE_OK;}
    RF455PoseKeyPair keys={};const auto status=RF455_SelectPoseKeys(data->channel+1,16,frame,0,owner,&keys);if(status!=RF_POSE_OK)return status;
    interpolate3(matrix+12,1,keys.left,keys.right,keys.ratio);return RF_POSE_OK;
}
extern "C" RF455PoseStatus RF455_UpdateCharacterPose(RF455CharacterStorage* model,const RF455PoseContext* context){
    if(!model)return RF_POSE_OK;
    if(!context || !context->load || !mathValid(&context->math) || !context->scratch || !context->resolveOwner)return RF_POSE_ARGUMENT;
    auto* b=reinterpret_cast<unsigned char*>(model);if(!RF455_LoadCharacter(model,0,context->load)){put<unsigned>(b,1184,0);return RF_POSE_LOAD;}
    const int count=get<int>(b,532);auto* meshes=get<RF455MeshStorage*>(b,536);if(count<0 || (count && !meshes))return RF_POSE_ARGUMENT;
    auto& scratch=*context->scratch;scratch.initialized|=31;const int frame=get<int>(b,672);const bool useRamp=get<unsigned>(b,704)!=0;
    for(int n=0;n<count;++n){auto* mesh=meshes+n;auto* m=mesh->bytes;identity(scratch.previous);identity(scratch.current);const auto* parent=get<const RF455MeshStorage*>(m,518);
        if(m[512] && !parent)return RF_POSE_ARGUMENT;
        if(get<unsigned>(b,708)){
            if(m[512]){float inverse[16];if(!context->math.matrix.inverse(inverse,nullptr,parent->bytes+4894) || !context->math.matrix.multiply(m+4958,m+4830,inverse))return RF_POSE_MATRIX;}
            else std::memcpy(m+4958,m+4830,64);
            std::memcpy(m+4894,m+4830,64);
        }
        const bool applyModifier=get<unsigned>(m,5499) && !useRamp;const auto* current=get<const RF455AnimationData*>(m,5095);
        if(m[5094] && !current){char text[1024];std::snprintf(text,sizeof(text),"FrameMove : Co:%.256s Cm:%.256s ",reinterpret_cast<char*>(b+4),reinterpret_cast<char*>(m));context->load->legacy.diagnostics.write(context->load->legacy.diagnostics.context,text);}
        if(m[5094] && current){
            auto status=evaluate(scratch.current,frame,mesh,current,context,applyModifier);if(status!=RF_POSE_OK)return status;
            auto* previous=get<RF455AnimationData*>(m,5099);
            if(previous){
                status=evaluate(scratch.previous,get<int>(b,684),mesh,previous,context,applyModifier);if(status!=RF_POSE_OK)return status;
                const float ratio=divideFloat(b+692,&context->blendDuration);
                if(orderedLE(context->blendDuration,get<float>(b,692)))copyFloat(b+692,&context->blendDuration);
                if(!orderedLess(ratio,0)){
                    if(!orderedLE(context->blendDuration,get<float>(b,692)))blend(scratch.current,scratch.current,scratch.previous,ratio);
                    else{context->load->legacy.base.memory.release(context->load->legacy.base.memory.context,previous);put<void*>(m,5099,nullptr);put<unsigned>(b,680,0);put<unsigned>(b,684,160);put<unsigned>(b,688,0);}
                }
            }
        }else if(applyModifier){const auto status=modifier(scratch.current,m,context->math);if(status!=RF_POSE_OK)return status;}
        else std::memcpy(scratch.current,m+4702,64);
        if(useRamp)ramp(scratch.current,scratch.current,reinterpret_cast<const float*>(m+4958),unsignedRatio(get<unsigned>(b,712),get<unsigned>(b,716)));
        if(m[512]){if(!context->math.matrix.multiply(m+4830,scratch.current,parent->bytes+4830))return RF_POSE_MATRIX;}
        else std::memcpy(m+4830,scratch.current,64);
        if(get<unsigned>(m,5571)){const auto status=RF455_ApplySecondaryMotion(model,mesh,context->secondary);if(status!=RF_POSE_OK)return status;}
        if(get<unsigned>(b,796)){const unsigned slot=get<unsigned>(m,5575);if(slot){if(slot>3)return RF_POSE_BOUNDS;std::memcpy(b+928+64*slot,m+4638,64);std::memcpy(b+736+64*slot,m+4830,64);}}
    }
    put<unsigned>(b,708,0);scratch.initialized|=32;
    for(int n=0;n<count;++n){auto* m=meshes[n].bytes;const unsigned bones=get<unsigned>(m,522);if(bones>50)return RF_POSE_BOUNDS;
        for(unsigned i=0;i<bones;++i){const auto* bone=get<const RF455MeshStorage*>(m,526+4*i);if(!bone)return RF_POSE_ARGUMENT;if(!context->math.matrix.multiply(m+2566+64*i,m+4574,bone->bytes+4638))return RF_POSE_MATRIX;}
        for(unsigned i=0;i<bones;++i){const auto* bone=get<const RF455MeshStorage*>(m,526+4*i);if(!bone)return RF_POSE_ARGUMENT;if(!context->math.matrix.multiply(m+646+64*i,m+2566+64*i,bone->bytes+4830))return RF_POSE_MATRIX;}
    }
    put<unsigned>(b,1184,0);return RF_POSE_OK;
}
