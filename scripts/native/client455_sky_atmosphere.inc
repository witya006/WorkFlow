// Selected455 sky atmosphere owner. Included once by derived level.cpp.
#include "client455_sky_atmosphere.h"
#include "client455_d3d9_port.h"
#include "client455_sky_fade_math.h"
#include "r3d3dtex.h"
#include "r3math.h"
#include <cmath>
#include <cstring>
HRESULT LoadCreateShader(char*,const D3DVERTEXELEMENT9*,RF455R3VertexProgram*);
namespace {
RF455SunValues skySun={0,0,0,1,0,100};
IDirect3DVertexBuffer9* skyVB=nullptr;
IDirect3DIndexBuffer9* skyIB=nullptr;
IDirect3DTexture9* sunTexture=nullptr;
IDirect3DVertexDeclaration9* sunDeclaration=nullptr;
RF455R3VertexProgram skyShader;
unsigned skyVertexCount=0,skyPrimitiveCount=0;
float vertexVersion=0;
//901BC0/901900:five parameters followed by four RGB coefficient vectors.
float skyParams[17]={.8f,1,1,1,.001f,
    .000006954956461413531f,.00001176111436507199f,.000024387845769524574f,
    .000000415093353467455f,.0000007019397685326112f,.0000014555422467310564f,
    .00574059784412384f,.007399687077850103f,.01051431242376566f,
    .0013337875716388226f,.001734457560814917f,.002497619017958641f};
struct SkyVertex {float x,y,z,u,v;};
static_assert(sizeof(SkyVertex)==20,"455 scatter vertex");
struct SunVertex {float x,y,z,nx,ny,nz;DWORD color;float u,v;};
static_assert(sizeof(SunVertex)==36,"455 sun vertex");
const D3DVERTEXELEMENT9 skyDeclaration[]={
    {0,0,D3DDECLTYPE_FLOAT3,0,D3DDECLUSAGE_POSITION,0},
    {0,12,D3DDECLTYPE_FLOAT2,0,D3DDECLUSAGE_TEXCOORD,0},D3DDECL_END()};
const D3DVERTEXELEMENT9 sunElements[]={
    {0,0,D3DDECLTYPE_FLOAT3,0,D3DDECLUSAGE_POSITION,0},
    {0,12,D3DDECLTYPE_FLOAT3,0,D3DDECLUSAGE_NORMAL,0},
    {0,24,D3DDECLTYPE_D3DCOLOR,0,D3DDECLUSAGE_COLOR,0},
    {0,28,D3DDECLTYPE_FLOAT2,0,D3DDECLUSAGE_TEXCOORD,0},D3DDECL_END()};
float spill(double value){return float(value);}
float sunOrbit(float day){
    const double start=.25,duration=.5416666865348816,range=.949999988079071,bias=.02500000037252903;float result;
    __asm { fld day
            fsub start
            fdiv duration
            fmul range
            fadd bias
            fstp result }
    return result;
}
float sunRisingScale(float day){
    const double start=.25,eight=8.0,range=1.5;float denominator,result;
    __asm { fld day
            fsub start
            fmul eight
            fmul range
            fld1
            faddp st(1),st
            fstp denominator
            fld1
            fdiv denominator
            fstp result }
    return result;
}
float sunFallingScale(float day){
    const double start=.7083333134651184,duration=.08333337306976318,range=1.5;float denominator,result;
    __asm { fld day
            fsub start
            fdiv duration
            fmul range
            fsubr range
            fld1
            faddp st(1),st
            fstp denominator
            fld1
            fdiv denominator
            fstp result }
    return result;
}
float sunRisingAlpha(float value){
    const double ten=10;float result;
    __asm { fld value
            fmul ten
            fld1
            faddp st(1),st
            fstp result }
    return result;
}
float sunFallingAlpha(float value){
    const double start=.9750000238418579,duration=.1749999523162842;float result;
    __asm { fld value
            fsub start
            fdiv duration
            fld1
            fsubrp st(1),st
            fstp result }
    return result;
}
float sunTheta(float orbit){
    const double half=.5,angle=1.570796370506287;float result;
    __asm { fld orbit
            fsub half
            fabs
            fadd st,st
            fmul angle
            fstp result }
    return result;
}
void sunColor(float out[4]){
    //900B00/900C70:reference optical-depth approximation,including float spills.
    const float pi=3.1415927410125732421875f;
    const float beta=spill(2.0*.04608365893363953-.04586026072502136);
    const float zenith=spill(93.88500213623047-double(skySun.theta)/pi*180.0);
    const float p=spill(std::pow(double(zenith),-1.253000020980835));
    const double correction=double(p)*.1500000059604645;
    const float cosine=spill(std::cos(double(skySun.theta)));
    const float sum=spill(double(cosine)+correction);
    const float air=spill(1.0/double(sum));
    const float negative=spill(-double(air));
    const double aerosol=double(negative)*beta;
    const double rayleigh=double(negative)*.008735000155866146;
    const float wavelength[]={.6499999761581421f,.5699999928474426f,.4749999940395355f};
    for(unsigned i=0;i<3;++i){
        const float a=spill(std::pow(double(wavelength[i]),-4.079999923706055));
        const float b=spill(double(a)*rayleigh);
        const float c=spill(std::exp(double(b)));
        const float d=spill(std::pow(double(wavelength[i]),-1.299999952316284));
        const float e=spill(double(d)*aerosol);
        const float f=spill(std::exp(double(e)));
        out[i]=spill(double(f)*c);
    }
    out[3]=1;
}
void skyConstants(IDirect3DDevice9* device){
    auto* s=GetR3State();float value[4]={1,1,1,1};device->SetVertexShaderConstantF(21,value,1);
    std::memset(value,0,sizeof(value));device->SetVertexShaderConstantF(20,value,1);
    D3DXMATRIX identity,transpose;D3DXMatrixIdentity(&identity);D3DXMatrixTranspose(&transpose,&identity);device->SetVertexShaderConstantF(8,reinterpret_cast<const float*>(&transpose),4);
    D3DXMatrixTranspose(&transpose,&s->mMatView);device->SetVertexShaderConstantF(4,reinterpret_cast<const float*>(&transpose),4);
    D3DXMatrixTranspose(&transpose,&s->mMatViewProj);device->SetVertexShaderConstantF(0,reinterpret_cast<const float*>(&transpose),4);
    const float sunDirection[4]={0,-1,0,1};device->SetVertexShaderConstantF(12,sunDirection,1);
    const float reflectance[4]={.0138f,.0113f,.00800000038f,0};device->SetVertexShaderConstantF(13,reflectance,1);
    sunColor(value);value[3]=skySun.intensity;device->SetVertexShaderConstantF(15,value,1);
    float beta1[4]={},beta2[4]={},sum[4]={},inverse[4]={};
    for(unsigned i=0;i<3;++i){
        beta1[i]=spill(double(skyParams[5+i])*skyParams[3]);
        beta2[i]=spill(double(skyParams[11+i])*skyParams[4]);
        sum[i]=spill(double(beta1[i])+beta2[i]);inverse[i]=spill(1.0/double(sum[i]));
    }
    device->SetVertexShaderConstantF(30,beta1,1);device->SetVertexShaderConstantF(29,beta2,1);
    for(unsigned i=0;i<3;++i){beta1[i]=spill(double(skyParams[8+i])*skyParams[3]);beta2[i]=spill(double(skyParams[14+i])*skyParams[4]);}
    device->SetVertexShaderConstantF(27,beta1,1);device->SetVertexShaderConstantF(26,beta2,1);
    device->SetVertexShaderConstantF(24,sum,1);device->SetVertexShaderConstantF(23,inverse,1);
    const float g=skyParams[0];value[0]=spill(1.0-double(g)*g);value[1]=spill(double(g)*g+1.0);value[2]=spill(double(g)+g);value[3]=0;device->SetVertexShaderConstantF(28,value,1);
    const float log2=spill(std::log(2.0));value[0]=1;value[1]=spill(1.0/double(log2));value[2]=.5f;value[3]=0;device->SetVertexShaderConstantF(31,value,1);
    value[0]=skyParams[2];value[1]=skyParams[1];value[2]=0;value[3]=0;device->SetVertexShaderConstantF(25,value,1);
    std::memset(value,0,sizeof(value));device->SetVertexShaderConstantF(22,value,1);
}
HRESULT drawDome(IDirect3DDevice9* device){
    if(vertexVersion<1.0f)return E_FAIL;
    device->SetRenderState(D3DRS_FOGENABLE,FALSE);device->SetTexture(0,nullptr);MultiTexOff();
    HRESULT hr=device->SetStreamSource(0,skyVB,0,20);if(FAILED(hr))return hr;
    hr=device->SetIndices(skyIB);if(FAILED(hr))return hr;
    return device->DrawIndexedPrimitive(D3DPT_TRIANGLELIST,0,0,skyVertexCount,0,skyPrimitiveCount);
}
void drawSun(IDirect3DDevice9* device){
    if(!sunTexture)return;
    device->SetTexture(0,sunTexture);float world[4][4],temp[4][4];
    MatrixIdentity(world);MatrixScale(temp,skySun.scale,skySun.scale,skySun.scale);MatrixMultiply(world,temp,world);world[3][2]=1400;
    MatrixRotateX(temp,spill(double(skySun.orbit)*-180.0));MatrixMultiply(world,temp,world);
    MatrixRotateZ(temp,-30);MatrixMultiply(world,temp,world);device->SetTransform(D3DTS_WORLD,reinterpret_cast<D3DMATRIX*>(world));
    float color[4];sunColor(color);
    if(color[0]<.487017f||color[1]<.36861f||color[2]<.19005f){color[0]=.487017005443573f;color[1]=.3686099946498871f;color[2]=.1900500059127808f;}
    const DWORD a=RF455_FadeAlphaByte(skySun.alpha);DWORD r=RF455_FadeAlphaByte(color[0]);
    const double greenScale=1.149999976158142,maximum=255.0;__int64 green;unsigned short saved,truncation;
    const float greenInput=color[1];
    __asm { fld greenInput
            fmul greenScale
            fmul maximum
            fnstcw saved }
    truncation=saved|0xc00;
    __asm { fldcw truncation
            fistp green
            fldcw saved }
    DWORD g=DWORD(green);DWORD b=RF455_FadeAlphaByte(color[2]);
    if(r>=255)r=255;if(g>=255)g=255;if(b>=255)b=255;const DWORD packed=(a<<24)|(r<<16)|(g<<8)|b;
    SunVertex vertices[4]={
        {-1000,1000,0,0,0,0,packed,0,0},{1000,1000,0,0,0,0,packed,1,0},
        {-1000,-1000,0,0,0,0,packed,0,1},{1000,-1000,0,0,0,0,packed,1,1}};
    device->SetRenderState(D3DRS_ALPHABLENDENABLE,TRUE);device->SetRenderState(D3DRS_ALPHATESTENABLE,TRUE);
    device->SetRenderState(D3DRS_SRCBLEND,D3DBLEND_SRCALPHA);device->SetRenderState(D3DRS_DESTBLEND,D3DBLEND_INVSRCALPHA);
    device->SetTextureStageState(0,D3DTSS_ALPHAOP,D3DTOP_MODULATE);device->SetTextureStageState(1,D3DTSS_ALPHAOP,D3DTOP_DISABLE);
    RF455_SetVPIPTex1KeepingShader(nullptr,nullptr,sunDeclaration);device->SetTextureStageState(0,D3DTSS_COLOROP,D3DTOP_MODULATE2X);device->SetRenderState(D3DRS_ALPHATESTENABLE,FALSE);
    device->DrawPrimitiveUP(D3DPT_TRIANGLESTRIP,2,vertices,36);
    device->SetRenderState(D3DRS_ALPHATESTENABLE,FALSE);device->SetRenderState(D3DRS_ALPHABLENDENABLE,FALSE);
    MatrixIdentity(world);device->SetTransform(D3DTS_WORLD,reinterpret_cast<D3DMATRIX*>(world));device->SetTextureStageState(0,D3DTSS_COLOROP,D3DTOP_MODULATE);
}
}
const RF455SunValues& RF455_GetSunValues(){return skySun;}
IDirect3DVertexBuffer9* RF455_GetSkyDomeVertices(){return skyVB;}
IDirect3DIndexBuffer9* RF455_GetSkyDomeIndices(){return skyIB;}
IDirect3DVertexShader9* RF455_GetSkyDomeShader(){return skyShader.shader;}
IDirect3DTexture9* RF455_GetSunTexture(){return sunTexture;}

void RF455_UpdateSunValues(){
    if(!RF455_GetSkyDayEnabled())return;
    const float day=RF455_GetDayFraction();
    const float orbit=sunOrbit(day);
    skySun.orbit=orbit;float angleInput=.025f;
    if(day>.25 && day<.7916666865348816){
        angleInput=orbit;skySun.alpha=1;
        if(day<.375)skySun.scale=sunRisingScale(day);
        else if(day>.7083333134651184)skySun.scale=sunFallingScale(day);
        else skySun.scale=.4000000059604645f;
    }else{
        skySun.scale=1;
        if(orbit<=.02500000037252903){float clamped=orbit;if(clamped<-.1000000014901161f)clamped=-.1000000014901161f;if(clamped>0)clamped=0;skySun.alpha=sunRisingAlpha(clamped);}
        else if(orbit>=.9750000238418579){const float clamped=orbit>1.15?1.15f:orbit;skySun.alpha=sunFallingAlpha(clamped);}
        else skySun.alpha=0;
    }
    skySun.theta=sunTheta(angleInput);skySun.phi=angleInput<.5f?4.71238899230957f:1.570796370506287f;
    // The file-backed night parameter is.03;day parameter starts zero in BSS.
    // Console/indirect writers are not claimed by this initial-state path.
    float mie=0;
    if(day>.7708333333333334 && day<.7916666865348816){
        const double start=.7708333333333334,duration=.02083335258066654;
        const float difference=.02999999932944775f;float elapsed;
        __asm{fld day
            fsub start
            fstp elapsed
            fld elapsed
            fdiv duration
            fmul difference
            fstp mie}
    }else if(day>.7916666865348816 && day<.8333333134651184){
        const double start=.7916666865348816,duration=.04166662693023682;
        const float difference=.02999999932944775f;
        __asm{fld day
            fsub start
            fdiv duration
            fld1
            fsubrp st(1),st
            fmul difference
            fstp mie}
    }
    skyParams[4]=mie;
}

void RF455_CreateSkyResources(){
    auto* device=GetD3dDevice();D3DCAPS9 caps={};if(!device||FAILED(device->GetDeviceCaps(&caps)))return;
    vertexVersion=float(D3DSHADER_VERSION_MAJOR(caps.VertexShaderVersion))+float(D3DSHADER_VERSION_MINOR(caps.VertexShaderVersion))/10;
    device->CreateVertexDeclaration(sunElements,&sunDeclaration);
    char shaderName[]=".\\System\\shader\\Scatter.vso";
#if defined(RF_CLIENT_455_CACHED_VERTEX_SHADER)
    if(vertexVersion>=1.1f)LoadCreateShader(shaderName,skyDeclaration,&skyShader);
#else
    if(vertexVersion>=1.1f&&IsExistFile(shaderName))LoadCreateShader(shaderName,skyDeclaration,&skyShader);
#endif
    if(vertexVersion>=1.0f){
        if(SUCCEEDED(device->CreateVertexBuffer(20*4225,D3DUSAGE_WRITEONLY,258,D3DPOOL_MANAGED,&skyVB,nullptr))&&
           SUCCEEDED(device->CreateIndexBuffer(6*8192,D3DUSAGE_WRITEONLY,D3DFMT_INDEX16,D3DPOOL_MANAGED,&skyIB,nullptr))){
            skyVertexCount=4225;skyPrimitiveCount=8192;
            SkyVertex* vertices=nullptr;WORD* indices=nullptr;skyVB->Lock(0,0,reinterpret_cast<void**>(&vertices),0);skyIB->Lock(0,0,reinterpret_cast<void**>(&indices),0);
            if(vertices&&indices){
                unsigned n=0;for(int i=0;i<=64;++i)for(int j=0;j<=64;++j){const float x=float(i-32),z=float(j-32);const float squared=spill(double(x)*x+double(z)*z);const float distance=squared==0?0:spill(std::sqrt(double(squared)));const float capped=distance>32?32:distance;const float height=spill(32.0-capped);vertices[n++]={spill(double(x)*1290.0),spill(double(height)*5160.0/32.0),spill(-1290.0*z),float(i)/64,float(j)/64};}
                n=0;for(unsigned i=0;i<64;++i)for(unsigned j=0;j<64;++j){const WORD a=WORD(j+i*65),b=WORD(j+(i+1)*65);indices[n++]=a;indices[n++]=b+1;indices[n++]=b;indices[n++]=a;indices[n++]=a+1;indices[n++]=b+1;}
                skyIB->Unlock();skyVB->Unlock();
            }
        }
    }
    //8F1990:preserve the existing engine's DDS texture-format choice/filtering.
    char sunName[]=".\\system\\sun.dds";sunTexture=R3LoadDDSAndTextureMem(sunName);
}
void RF455_ReleaseSkyResources(){
    if(vertexVersion>=1){if(skyVB){skyVB->Release();skyVB=nullptr;}if(skyIB){skyIB->Release();skyIB=nullptr;}}
    if(sunTexture){sunTexture->Release();sunTexture=nullptr;}RF455_ReleaseR3VertexProgram(skyShader);
    if(sunDeclaration){sunDeclaration->Release();sunDeclaration=nullptr;}
}
void RF455_DrawSkyAtmosphere(){
    auto* device=GetD3dDevice();auto* state=GetR3State();const D3DXMATRIX view=state->mMatView,projection=state->mMatProj;
    state->mMatView._41=state->mMatView._42=state->mMatView._43=0;device->SetTransform(D3DTS_VIEW,&state->mMatView);
    device->SetRenderState(D3DRS_ZENABLE,FALSE);device->SetRenderState(D3DRS_ZWRITEENABLE,FALSE);
    D3DXMatrixPerspectiveFovLH(&state->mMatProj,state->mFov,state->mAsfectRatio,10,60000);device->SetTransform(D3DTS_PROJECTION,&state->mMatProj);MatrixMultiply(state->mMatViewProj.m,state->mMatProj.m,state->mMatView.m);device->SetRenderState(D3DRS_ALPHATESTENABLE,FALSE);
    const DWORD flags=state->mEnvironmentSceneFlags;
    if((flags&4)==0||(flags&1)==0){
        //8D88D0 runs shader binding/constants even when flag4 suppresses the dome.
        const bool available=skyShader.shader!=nullptr;
        if(available){device->SetVertexShader(skyShader.shader);device->SetVertexDeclaration(skyShader.declaration);skyConstants(device);}
        if(available&&!(flags&4))drawDome(device);
        if(!(flags&1))drawSun(device);
        device->SetVertexShader(nullptr);device->SetPixelShader(nullptr);
    }
    state->mMatProj=projection;state->mMatView=view;MatrixMultiply(state->mMatViewProj.m,state->mMatProj.m,state->mMatView.m);device->SetTransform(D3DTS_PROJECTION,&state->mMatProj);device->SetTransform(D3DTS_VIEW,&state->mMatView);RF455_SetVPIPTex1KeepingShader(nullptr,nullptr,sunDeclaration);
}
