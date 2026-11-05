#include "client455_character_draw_internal.h"
#include <limits>

namespace rf455draw {
// Preserve x87 operations and every reference m32 spill. Do not allow SSE
// DAZ/FTZ to decide branches on legacy subnormal material/effect values.
float add(float a,float b){float r;__asm{fld a
    fadd b
    fstp r}return r;}
float scale(float a,double b){float r;__asm{fld a
    fmul b
    fstp r}return r;}
float mix(float a,float b){float r;const double half=.5,sevenths=.7;__asm{fld a
    fmul half
    fld b
    fmul sevenths
    faddp st(1),st
    fstp r}return r;}
float ratio(unsigned n,double divisor){const double correction=4294967296.0;float r;__asm{fild n
    test n,80000000h
    jz positive
    fadd correction
positive:
    fdiv divisor
    fstp r}return r;}
float delta(unsigned n,float rate,double divisor){const double correction=4294967296.0;float r;__asm{fild n
    test n,80000000h
    jz positive
    fadd correction
positive:
    fmul rate
    fdiv divisor
    fstp r}return r;}
float angle(float frequency,float phase){const double pi=3.1415927410125732421875;float r;__asm{fld frequency
    fmul phase
    fmul pi
    fadd st,st
    fstp r}return r;}
float absolute(float a){float r;__asm{fld a
    fabs
    fstp r}return r;}
float advance(float previous,unsigned elapsed){const double correction=4294967296.0,factor=.0001;float r;__asm{fild elapsed
    test elapsed,80000000h
    jz positive
    fadd correction
positive:
    fmul factor
    fadd previous
    fstp r}return r;}
float fourthWeight(const float* w){float r;__asm{mov eax,w
    fld dword ptr[eax+4]
    fadd dword ptr[eax]
    fadd dword ptr[eax+8]
    fld1
    fsubrp st(1),st
    fstp r}return r;}
float weighted(const float* value,const float* weight,bool reverse){float r;
    if(reverse){__asm{mov eax,value
        mov edx,weight
        fld dword ptr[eax+12]
        fmul dword ptr[edx+12]
        fld dword ptr[eax+8]
        fmul dword ptr[edx+8]
        faddp st(1),st
        fld dword ptr[eax]
        fmul dword ptr[edx]
        faddp st(1),st
        fld dword ptr[eax+4]
        fmul dword ptr[edx+4]
        faddp st(1),st
        fstp r}}
    else{__asm{mov eax,value
        mov edx,weight
        fld dword ptr[eax+4]
        fmul dword ptr[edx+4]
        fld dword ptr[eax]
        fmul dword ptr[edx]
        faddp st(1),st
        fld dword ptr[eax+8]
        fmul dword ptr[edx+8]
        faddp st(1),st
        fld dword ptr[eax+12]
        fmul dword ptr[edx+12]
        faddp st(1),st
        fstp r}}return r;
}
bool equal(float a,float b){unsigned r=0;__asm{fld a
    fcomp b
    fnstsw ax
    and ah,45h
    cmp ah,40h
    jne done
    mov r,1
done:}return r!=0;}
bool less(float a,float b){unsigned r=0;__asm{fld a
    fcomp b
    fnstsw ax
    and ah,45h
    cmp ah,1
    jne done
    mov r,1
done:}return r!=0;}
bool lessUnordered(float a,float b){unsigned r=0;__asm{fld a
    fcomp b
    fnstsw ax
    test ah,1
    jz done
    mov r,1
done:}return r!=0;}
bool greater(float a,float b){unsigned r=0;__asm{fld a
    fcomp b
    fnstsw ax
    and ah,45h
    jne done
    mov r,1
done:}return r!=0;}
bool valid(const RF455CharacterDrawContext* c){return c && c->state.device && c->shaders && c->shaders->device==c->state.device && c->vertices36 && c->vertices64 && c->indices && c->globals && c->transparent && c->transparent->entries.size()==1024 && c->math.matrix.multiply && c->math.transform3 && c->math.ticks && c->math.sineFloat && c->math.cosineFloat && c->memory.allocate && c->memory.release && c->projection && c->view && (!c->orthographic || (c->math.ortho && c->publishProjection));}
void bindDeclaration(RF455CharacterDrawContext* c){if(c->useFvf)c->state.device->SetFVF(c->fvf);else if(c->state.vertexMode==2)c->state.device->SetVertexDeclaration(c->state.declaration36);else if(c->state.vertexMode==4)c->state.device->SetVertexDeclaration(c->state.declaration64);}
void clearShaders(RF455CharacterDrawContext* c){c->state.device->SetVertexShader(nullptr);c->state.device->SetPixelShader(nullptr);}
void select(RF455CharacterDrawContext* c,unsigned index){RF455_SelectCharacterShader(c->shaders,index,&c->selected);}
void projection(RF455CharacterDrawContext* c){if(c->orthographic){float width,height;const float denominator=c->orthoScale;const float inputWidth=c->width,inputHeight=c->height;__asm{fld inputWidth
    fdiv denominator
    fstp width
    fld inputHeight
    fdiv denominator
    fstp height}c->math.ortho(c->projection,width,height,-5000,5000);c->publishProjection(c->projectionOwner,c->view,c->projection);}}
void capturePalette(float* out,const RF455MeshStorage* mesh,const void* world,const void* translation,const RF455MeshMatrixOps* math){const unsigned count=get<unsigned>(mesh,522);for(unsigned i=0;i<(count?count:1);++i){const auto* skin=mesh->bytes+(count?646+64*i:4830);math->multiply(out+16*i,skin,world);if(translation){float temporary[16];math->multiply(temporary,skin,translation);std::memcpy(out+16*i+12,temporary+12,12);}}}
void material(float* out,const RF455CharacterStorage* model,const RF455MeshStorage* mesh){std::memcpy(out,reinterpret_cast<const unsigned char*>(model)+720,68);const auto* effect=get<const unsigned char*>(mesh,5455);if(get<unsigned>(effect,196)){for(unsigned i=0;i<3;++i)out[8+i]=mix(out[8+i],get<float>(mesh,5579+4*i));out[11]=1;out[16]=add(out[16],get<float>(mesh,5591));}else{const float r=scale(out[0],2),g=scale(out[1],2),b=scale(out[2],2);std::memset(out,0,68);out[0]=out[4]=r;out[1]=out[5]=g;out[2]=out[6]=b;out[3]=out[7]=1;}}
bool immediate(const RF455MeshStorage* mesh){const auto* effect=get<const unsigned char*>(mesh,5455);if(!effect)return false;return !(equal(get<float>(mesh,5131),1) && equal(get<float>(effect,288),0) && !get<void*>(mesh,5115)) || get<unsigned>(effect,160)!=0;}
RF455CharacterDrawStatus submit(RF455CharacterDrawContext* c,RF455MeshStorage* mesh,const void* world,const float* palette,bool forceShared){if(c->beforeDraw)c->beforeDraw(c->observer,mesh,c->selected);if(!forceShared && get<void*>(mesh,4506))RF455_DrawDynamicCharacterMesh(c,mesh,world,palette);else RF455_SubmitSharedCharacterGeometry(c->state.device,c->state.vertexMode,c->vertices36,c->vertices64,c->indices,mesh);return RF_CHARACTER_DRAW_OK;}
}

extern "C" void RF455_ResetCharacterTransparency(RF455CharacterTransparency* queue){
    if(queue->entries.size()!=1024)queue->entries.resize(1024);
    queue->count=0;queue->head=nullptr;for(auto& p:queue->entries){p.depth=-(std::numeric_limits<float>::max)();p.next=nullptr;p.textureFactor=0xffffffffu;p.secondPass=p.inverted=p.effect=p.part=0;p.scroll=0;p.mesh=nullptr;}
}
extern "C" int RF455_QueueCharacterTransparency(RF455CharacterTransparency* q,const RF455TransparentPacket* packet,const RF455MeshMatrixOps* math){
    if(q->count>=1024)return 0;auto* p=q->entries.data()+q->count;*p=*packet;float result[16];math->multiply(result,p->palette[0],q->sortView);p->depth=result[14];
    if(!q->head){q->head=p;++q->count;return 1;}auto* at=q->head;RF455TransparentPacket* previous=nullptr;unsigned traversed=0;
    while(rf455draw::lessUnordered(p->depth,at->depth)){if(!at->next){p->next=nullptr;at->next=p;++q->count;return 1;}previous=at;at=at->next;if(++traversed>=1024){++q->count;return 1;}}
    p->next=at;if(at==q->head)q->head=p;else previous->next=p;++q->count;return 1;
}
extern "C" void RF455_SetCharacterEffectStage(RF455CharacterDrawContext* c,unsigned stage,unsigned effect,DWORD factor,float scroll){
    using namespace rf455draw;auto* d=c->state.device;float m[16];unit(m);static const float environment[]={.5f,0,0,0,0,-.5f,0,0,0,0,1,0,.5f,.5f,0,1};
    if(effect==1 || effect==3){std::memcpy(m,environment,64);if(effect==1 && !stage)return;if(effect==3){const float a=angle(scroll,1);c->math.cosineFloat(m+1,&a);c->math.sineFloat(m+4,&a);}d->SetVertexShaderConstantF(88+4*stage,m,4);}
    else if(effect==2){m[9]=scroll;d->SetVertexShaderConstantF(88+4*stage,m,4);}
    else if(effect==4){
        if(!c->globals->bumpEpoch)c->globals->bumpEpoch=c->math.ticks();const unsigned elapsed=c->math.ticks()-c->globals->bumpEpoch;const float seconds=ratio(elapsed,1000),a=scale(seconds,3);float sine,cosine;c->math.cosineFloat(&cosine,&a);c->math.sineFloat(&sine,&a);const double rate=0.00999999977648258209228515625;
        const float bump[]={scale(cosine,rate),scale(sine,-rate),scale(sine,rate),scale(cosine,rate)};
        d->SetTextureStageState(stage,D3DTSS_TEXCOORDINDEX,0);d->SetTextureStageState(stage,D3DTSS_COLOROP,D3DTOP_BUMPENVMAP);d->SetTextureStageState(stage,D3DTSS_COLORARG1,D3DTA_TEXTURE);d->SetTextureStageState(stage,D3DTSS_COLORARG2,D3DTA_CURRENT);d->SetTextureStageState(stage,D3DTSS_ALPHAOP,D3DTOP_DISABLE);
        d->SetTextureStageState(stage+1,D3DTSS_TEXCOORDINDEX,0);d->SetTextureStageState(stage+1,D3DTSS_COLOROP,D3DTOP_SELECTARG1);d->SetTextureStageState(stage+1,D3DTSS_COLORARG1,D3DTA_TEXTURE);d->SetTextureStageState(stage+1,D3DTSS_COLORARG2,D3DTA_CURRENT);
        for(unsigned i=0;i<4;++i){DWORD bits;std::memcpy(&bits,bump+i,4);d->SetTextureStageState(stage,static_cast<D3DTEXTURESTAGESTATETYPE>(7+i),bits);}
        m[0]=m[5]=m[10]=ratio(factor,2147483264.0);m[9]=scroll;d->SetVertexShaderConstantF(92,m,4);
    }else if(effect!=5){d->SetTextureStageState(stage,D3DTSS_TEXTURETRANSFORMFLAGS,0);d->SetTextureStageState(stage,D3DTSS_TEXCOORDINDEX,0);}
}
extern "C" void RF455_DrawDynamicCharacterMesh(RF455CharacterDrawContext* c,const RF455MeshStorage* mesh,const void* world,const float* precomputed){
    using namespace rf455draw;const unsigned count=get<unsigned>(mesh,5086);if(get<unsigned>(mesh,522)!=4)return;auto* d=c->state.device;
    if(count<2048){float palettes[4][16];if(precomputed)std::memcpy(palettes,precomputed,256);else capturePalette(palettes[0],mesh,world,nullptr,&c->math.matrix);
        auto* out=c->globals->dynamicVertices;float positions[4][4]={},normals[4][4]={};
        const auto* vertices=get<const unsigned char*>(mesh,4506);
        for(unsigned i=0;i<count;++i){const auto* v=vertices+64*i;float w[]={get<float>(v,12),get<float>(v,16),get<float>(v,20),0};w[3]=fourthWeight(w);
            for(unsigned j=0;j<4;++j)if(!equal(w[j],0)){c->math.transform3(positions[j],v,palettes[j]);c->math.transform3(normals[j],v+32,mesh->bytes+646+64*j);}
            for(unsigned axis=0;axis<3;++axis){float a[4],b[4];for(unsigned j=0;j<4;++j){a[j]=positions[j][axis];b[j]=normals[j][axis];}out[i][axis]=weighted(a,w,false);out[i][3+axis]=weighted(b,w,axis==2);}std::memcpy(out[i]+6,v+44,8);
        }
        float identity[16];unit(identity);for(unsigned i=0;i<4;++i)d->SetTransform(static_cast<D3DTRANSFORMSTATETYPE>(256+i),reinterpret_cast<const D3DMATRIX*>(identity));d->SetFVF(274);d->SetStreamSource(0,nullptr,0,0);d->DrawPrimitiveUP(D3DPT_TRIANGLELIST,count/3,out,32);
    }
    d->SetFVF(278);
}
