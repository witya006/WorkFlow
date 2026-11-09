#pragma once
//4558E1657:explicit float length/sqrt stores,then three x87 divisions.
static void RF455_NormalizeEntityNormal(float* p){
    const float x=p[0],y=p[1],z=p[2];float square,normLength,nx,ny,nz;
    __asm {fld y
        fmul y
        fld x
        fmul x
        faddp st(1),st
        fld z
        fmul z
        faddp st(1),st
        fstp square
        fld square
        fsqrt
        fstp normLength
        fld x
        fdiv normLength
        fstp nx
        fld y
        fdiv normLength
        fstp ny
        fld z
        fdiv normLength
        fstp nz
    }
    p[0]=nx;p[1]=ny;p[2]=nz;
}
