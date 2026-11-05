#include "client455_normal_renderer_math.h"
#include "client455_normal_renderer_constants.h"
#include <cstring>
namespace {
void copy32(float* output,const float* input){__asm{mov eax,input
    mov edx,output
    fld dword ptr[eax]
    fstp dword ptr[edx]}}
bool positive(float value){unsigned char result;__asm{fldz
    fcomp value
    fnstsw ax
    test ah,5
    setnp result}return result!=0;}
}
extern "C" void RF455_BuildNormalCharacterWorld(float* world,float* unscaled,const float* position,float yaw,float scale,const RF455NormalTransformApi* api){
    double degrees,radians;std::memcpy(&degrees,&RF455_NORMAL_DEGREES_BITS,8);std::memcpy(&radians,&RF455_NORMAL_RADIANS_BITS,8);float angle;
    __asm{fld yaw
        fsubr degrees
        fmul radians
        fstp angle}
    float conversion[16];std::memcpy(conversion,RF455_NORMAL_COORDINATE_BITS,64);
    auto build=[&](float* out,float value){
        float rotation[16],copied;copy32(&copied,&value);std::memset(out,0,64);out[0]=out[5]=out[10]=copied;out[15]=1;
        api->rotationZ(rotation,angle);api->matrix.multiply(out,out,rotation);
        copy32(out+12,position);copy32(out+14,position+1);copy32(out+13,position+2);
        api->matrix.multiply(out,out,conversion);
    };
    build(world,scale);if(unscaled)build(unscaled,1);
}
extern "C" int RF455_IsNormalModelBoxVisible(const float* minimum,const float* maximum,const float planes[6][4]){
    for(unsigned i=0;i<6;++i){const auto* plane=planes[i];const float x=positive(plane[0])?minimum[0]:maximum[0],y=positive(plane[1])?minimum[1]:maximum[1],z=positive(plane[2])?minimum[2]:maximum[2];float dot;unsigned char outside;
        __asm{mov eax,plane
            fld dword ptr[eax+4]
            fmul y
            fld dword ptr[eax]
            fmul x
            faddp st(1),st
            fld dword ptr[eax+8]
            fmul z
            faddp st(1),st
            fstp dot
            fld dot
            fadd dword ptr[eax+12]
            fldz
            fxch st(1)
            fcompp
            fnstsw ax
            test ah,41h
            setz outside}
        if(outside)return 0;
    }return 1;
}
extern "C" void RF455_UnsetNormalCharacterState(const RF455CharacterDrawState* state){
    auto* d=state->device;d->SetRenderState(D3DRS_FOGENABLE,FALSE);
    d->SetTextureStageState(0,D3DTSS_TEXTURETRANSFORMFLAGS,D3DTTFF_DISABLE);d->SetTextureStageState(1,D3DTSS_TEXTURETRANSFORMFLAGS,D3DTTFF_DISABLE);
    d->SetRenderState(D3DRS_VERTEXBLEND,D3DVBF_DISABLE);d->SetTextureStageState(0,D3DTSS_ALPHAARG1,D3DTA_TEXTURE);
    d->SetRenderState(D3DRS_ALPHATESTENABLE,TRUE);d->SetSamplerState(0,D3DSAMP_MIPFILTER,D3DTEXF_POINT);
    d->SetRenderState(D3DRS_LIGHTING,FALSE);d->SetRenderState(D3DRS_CULLMODE,D3DCULL_CCW);
    d->SetTextureStageState(1,D3DTSS_TEXCOORDINDEX,1);d->SetRenderState(D3DRS_TEXTUREFACTOR,0xffffffffu);
    if(state->specularEnable){d->SetRenderState(D3DRS_SPECULARENABLE,FALSE);d->SetRenderState(D3DRS_DIFFUSEMATERIALSOURCE,D3DMCS_MATERIAL);d->SetRenderState(D3DRS_NORMALIZENORMALS,FALSE);d->SetRenderState(D3DRS_COLORVERTEX,FALSE);}
    D3DMATRIX identity={};identity._11=identity._22=identity._33=identity._44=1;
    for(unsigned i=0;i<4;++i)d->SetTransform(static_cast<D3DTRANSFORMSTATETYPE>(256+i),&identity);
    d->SetSamplerState(3,D3DSAMP_MIPFILTER,D3DTEXF_POINT);d->SetSamplerState(4,D3DSAMP_MIPFILTER,D3DTEXF_POINT);
}
