#include "client455_frustum.h"

static float coefficient(float fourth,float column,bool sum){
    float result;
    if(sum){__asm {fld column
        fadd fourth
        fchs
        fstp result}}
    else {__asm {fld fourth
        fsub column
        fchs
        fstp result}}
    return result;
}
static float finiteSquareRoot(float value){
    unsigned short saved,temporary;float result;
    __asm {fnstcw saved}
    // __load_CW (888DD5) retains PC, masks exceptions and selects nearest RC.
    temporary=static_cast<unsigned short>((saved&0x300u)|0x7fu);
    __asm {fldcw temporary
        fld value
        fsqrt
        fldcw saved
        fstp result}
    return result;
}
extern "C" void RF455_ExtractFrustumPlanes(float planes[6][4],const float clip[16]){
    const unsigned columns[]={0,0,1,1,2,2};
    for(unsigned i=0;i<6;++i){float* plane=planes[i];
        for(unsigned j=0;j<4;++j)plane[j]=coefficient(clip[4*j+3],clip[4*j+columns[i]],i==0 || i==3 || i==4);
        float square,root,reciprocal;
        __asm {mov eax,plane
            fld dword ptr [eax+4]
            fmul st,st
            fld dword ptr [eax]
            fmul st,st
            faddp st(1),st
            fld dword ptr [eax+8]
            fmul st,st
            faddp st(1),st
            fstp square}
        root=finiteSquareRoot(square);
        __asm {fld1
            fdiv root
            fstp reciprocal}
        for(unsigned j=0;j<4;++j){float* element=plane+j;
            __asm {mov eax,element
                fld reciprocal
                fmul dword ptr [eax]
                fstp dword ptr [eax]}}
    }
}
extern "C" void RF455_PublishCharacterFrustum(float planes[6][4],const float view[16],const float projection[16],RF455MatrixMultiply multiply){
    float clip[16];multiply(clip,view,projection);RF455_ExtractFrustumPlanes(planes,clip);
}
static bool positive(float value){
    unsigned char result;
    __asm {fldz
        fcomp value
        fnstsw ax
        test ah,5
        setnp result}
    return result!=0;
}
extern "C" int RF455_IsBBoxInFrustum(const float minimum[3],const float maximum[3],const float planes[6][4]){
    for(unsigned i=0;i<6;++i){const float* plane=planes[i];
        const float x=positive(plane[0])?minimum[0]:maximum[0];
        const float y=positive(plane[1])?minimum[1]:maximum[1];
        const float z=positive(plane[2])?minimum[2]:maximum[2];unsigned char outside;
        __asm {mov eax,plane
            fld dword ptr [eax]
            fmul x
            fld dword ptr [eax+4]
            fmul y
            faddp st(1),st
            fld dword ptr [eax+8]
            fmul z
            faddp st(1),st
            fadd dword ptr [eax+12]
            fldz
            fxch st(1)
            fcompp
            fnstsw ax
            test ah,41h
            setz outside}
        if(outside)return 0;
    }
    return 1;
}
