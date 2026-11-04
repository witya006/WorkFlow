#include "client455_x87_math.h"
#include <windows.h>
#include <cstdio>
#include <cstring>
#include <cstdint>
#include <cmath>

static unsigned checks=0,failures=0;
static void check(bool condition) { ++checks; if (!condition) ++failures; }
static unsigned short control() {
    unsigned short value;
    __asm { fnstcw value }
    return value;
}
static unsigned short status() {
    unsigned short value;
    __asm { fnstsw value }
    return value;
}
static void setControl(unsigned short value) {
    __asm { fldcw value }
}
static void identity(float a[4][4]) {
    std::memset(a,0,64);
    for (unsigned i=0;i<4;++i) a[i][i]=1.0f;
}
static bool same(float a,float b) { return std::memcmp(&a,&b,4)==0; }

int main() {
    const unsigned short original=control();
    unsigned modes=0;
    for (unsigned precision=0;precision<3;++precision) {
        for (unsigned rounding=0;rounding<4;++rounding) {
            const unsigned pc[]={0,0x200,0x300};
            unsigned short wanted=(unsigned short)((original & ~0xf00)|pc[precision]|(rounding<<10)|0x3f);
            setControl(wanted);
            const unsigned short top=status()&0x3800;
            ++modes;
            float a[4][4],inv[4][4],before[4][4];
            identity(a);
            a[0][0]=2; a[1][1]=4; a[2][2]=8;
            a[3][0]=16; a[3][1]=32; a[3][2]=64;
            std::memcpy(before,a,64);
            std::memset(inv,0xcd,64);
            check(RF455_MatrixInvert(inv,a)==1);
            check(std::memcmp(a,before,64)==0);
            check(inv[0][0]==.5f && inv[1][1]==.25f && inv[2][2]==.125f);
            check(inv[3][0]==-8 && inv[3][1]==-8 && inv[3][2]==-8 && inv[3][3]==1);
            float pos[3]={1,2,3},world[3],back[3];
            RF455_Vector3fTransform(world,pos,a);
            check(world[0]==18 && world[1]==40 && world[2]==88);
            RF455_Vector3fTransform(back,world,inv);
            check(back[0]==1 && back[1]==2 && back[2]==3);
            RF455_Vector3fTransform(world,world,inv);
            check(world[0]==1 && world[1]==2 && world[2]==3);
            check(control()==wanted && (status()&0x3800)==top);
            for (unsigned index=0;index<4;++index) {
                identity(a);
                (&a[0][0])[index*4+3]=index==3?1.01f:0.01f;
                std::memset(inv,0xcd,64);
                std::memcpy(before,inv,64);
                check(RF455_MatrixInvert(inv,a)==0);
                check(std::memcmp(inv,before,64)==0);
                check(control()==wanted && (status()&0x3800)==top);
            }
            identity(a);
            a[0][3]=0.001f;
            check(RF455_MatrixInvert(inv,a)==1);
            std::uint32_t next=0; std::memcpy(&next,&a[0][3],4); ++next;
            std::memcpy(&a[0][3],&next,4);
            check(RF455_MatrixInvert(inv,a)==0);
            check(control()==wanted && (status()&0x3800)==top);
            // Affine NaN comparisons do not reject an otherwise identity matrix.
            identity(a);
            const std::uint32_t qnan=0x7fc12345;
            std::memcpy(&a[3][3],&qnan,4);
            check(RF455_MatrixInvert(inv,a)==1 && inv[0][0]==1 && inv[3][3]==1);
            check(control()==wanted && (status()&0x3800)==top);
            // Singular input is not rejected; preserve this reference quirk.
            identity(a); a[0][0]=0;
            check(RF455_MatrixInvert(inv,a)==1);
            check(!std::isfinite(inv[0][0]));
            check(control()==wanted && (status()&0x3800)==top);
        }
    }
    // Cancellation proves why binary32 intermediates cannot replace x87 here.
    setControl((unsigned short)((original&~0xf00)|0x200|0x3f));
    float a[4][4],pos[3]={1,1,1},world[3];
    identity(a); a[0][0]=16777216.0f; a[1][0]=1; a[2][0]=-16777216.0f;
    RF455_Vector3fTransform(world,pos,a);
    volatile float first=a[0][0]*pos[0]+a[1][0]*pos[1];
    volatile float scalar=first+a[2][0]*pos[2];
    check(same(world[0],1.0f) && same(scalar,0.0f));
    setControl(original);
    check(control()==original);
    std::printf("{\"checks\":%u,\"failures\":%u,\"precision_rounding_modes\":%u,\"cancellation_x87\":1,\"cancellation_binary32\":0}\n",checks,failures,modes);
    return failures?1:0;
}
