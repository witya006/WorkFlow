#include "client455_character_draw_internal.h"
#include "client455_enhanced_lighting.h"
#include "client455_draw_observer.h"

namespace rf455draw {
namespace {
struct EnhancedPixelConstants {
    IDirect3DDevice9* device;
    float previous[44];
    IDirect3DBaseTexture9* previousShadow=nullptr;
    const D3DSAMPLERSTATETYPE states[6]={D3DSAMP_MINFILTER,D3DSAMP_MAGFILTER,D3DSAMP_MIPFILTER,D3DSAMP_SRGBTEXTURE,D3DSAMP_ADDRESSU,D3DSAMP_ADDRESSV};
    DWORD previousSampler[6]{};
    bool captured;
    explicit EnhancedPixelConstants(IDirect3DDevice9* value):device(value),
        captured(SUCCEEDED(value->GetPixelShaderConstantF(0,previous,11))){
        value->GetTexture(6,&previousShadow);for(unsigned i=0;i<6;++i)value->GetSamplerState(6,states[i],&previousSampler[i]);
    }
    ~EnhancedPixelConstants(){
        if(captured)device->SetPixelShaderConstantF(0,previous,11);
        device->SetTexture(6,previousShadow);if(previousShadow)previousShadow->Release();
        for(unsigned i=0;i<6;++i)device->SetSamplerState(6,states[i],previousSampler[i]);
    }
};
struct BatchRecord {float depth;void* next;float palette[30][16];RF455MeshStorage* mesh;float material[17];};
static_assert(sizeof(BatchRecord)==2000,"455 deferred fixed-function record");
void alphaWave(RF455CharacterDrawContext* c,RF455MeshStorage* mesh){const auto* effect=get<const unsigned char*>(mesh,5455);const float frequency=get<float>(effect,288),a=angle(frequency,c->globals->phase);float sine;c->math.sineFloat(&sine,&a);float value=absolute(sine);if(less(value,.1f))value=.1f;if(!equal(frequency,0))put(mesh,5131,value);}
unsigned effectProgram(unsigned type){if(type==2)return 6;if(type==4)return 4;return 0;}
void projectionConstants(RF455CharacterDrawContext* c){c->state.device->SetVertexShaderConstantF(2,c->projection,4);c->state.device->SetVertexShaderConstantF(6,c->view,4);}
void bindPaletteMaterial(RF455CharacterDrawContext* c,RF455MeshStorage* mesh,const float* mat,const void* world,const void* translation,bool rebuildProjection){if(rebuildProjection)projection(c);select(c,get<unsigned>(mesh,5763));projectionConstants(c);RF455_SetCharacterMaterial(c->state.device,mat);RF455_UploadCharacterPalette(c->state.device,mesh,world,translation,&c->math.matrix);}
void secondaryProgram(RF455CharacterDrawContext* c,RF455MeshStorage* mesh,const unsigned char* effect,unsigned type){put(mesh,5763,effectProgram(type));if(type!=1 && type!=2 && type!=3 && type!=4 && get<unsigned>(effect,188) && !get<unsigned>(effect,192))c->state.device->SetTextureStageState(0,D3DTSS_ALPHAOP,D3DTOP_DISABLE);}
}
RF455CharacterDrawStatus batch(RF455CharacterDrawContext* c,RF455MeshStorage* mesh,const RF455CharacterStorage* model,const void* world){
    unsigned count=get<unsigned>(mesh,5759),capacity=get<unsigned>(mesh,5755);
    if(count>=capacity){const unsigned slot=count/10;if(slot>=20)return RF_CHARACTER_DRAW_LIMIT;
        auto* records=static_cast<BatchRecord*>(c->memory.allocate(c->memory.context,20000));if(!records)return RF_CHARACTER_DRAW_MEMORY;
        for(unsigned i=0;i<10;++i){records[i].depth=-3.4028234663852886e38f;records[i].next=nullptr;records[i].mesh=nullptr;std::memset(records[i].material,0,68);}
        put(mesh,5595+4*slot,records);auto* materials=static_cast<float*>(c->memory.allocate(c->memory.context,680));if(!materials)return RF_CHARACTER_DRAW_MEMORY;put(mesh,5675+4*slot,materials);capacity+=10;put(mesh,5755,capacity);
    }
    if(get<unsigned>(mesh,522)>30)return RF_CHARACTER_DRAW_LIMIT;
    auto* records=get<BatchRecord*>(mesh,5595+4*(count/10));auto* materialArray=get<float*>(mesh,5675+4*(count/10));auto& record=records[count%10];record.depth=-3.4028234663852886e38f;record.next=nullptr;record.mesh=mesh;capturePalette(record.palette[0],mesh,world,nullptr,&c->math.matrix);std::memcpy(record.material,reinterpret_cast<const unsigned char*>(model)+720,68);
    float* mat=materialArray+17*(count%10);std::memcpy(mat,record.material,68);for(unsigned i=0;i<3;++i)mat[8+i]=mix(mat[8+i],get<float>(mesh,5579+4*i));mat[11]=1;mat[16]=add(mat[16],get<float>(mesh,5591));put(mesh,5759,count+1);return RF_CHARACTER_DRAW_OK;
}
RF455CharacterDrawStatus enqueue(RF455CharacterDrawContext* c,RF455MeshStorage* mesh,const RF455CharacterStorage* model,unsigned part,const void* world,const void* translation,bool second){
    const auto* effect=get<const unsigned char*>(mesh,5455);const unsigned bones=get<unsigned>(mesh,522);if(bones>30)return RF_CHARACTER_DRAW_LIMIT;
    alphaWave(c,mesh);RF455TransparentPacket p={};p.depth=-3.4028234663852886e38f;p.boneCount=bones;capturePalette(p.palette[0],mesh,world,second?nullptr:translation,&c->math.matrix);
    p.primary=get<IDirect3DBaseTexture9*>(mesh,5107);p.secondary=get<IDirect3DBaseTexture9*>(mesh,second?5119:5115);p.buffer=get<IDirect3DVertexBuffer9*>(mesh,4486);p.alpha=get<float>(mesh,5131);p.vertexCount=get<unsigned>(mesh,5086);p.frequency=get<float>(effect,288);std::memcpy(p.material,reinterpret_cast<const unsigned char*>(model)+720,68);p.special=get<unsigned>(effect,160);p.textureFactor=get<unsigned>(mesh,5147);p.secondPass=get<unsigned>(effect,188);p.inverted=second?!get<unsigned>(effect,192):get<unsigned>(effect,192);p.effect=get<unsigned>(effect,second?204:200);p.scroll=get<float>(mesh,5135);p.mesh=mesh;p.part=part;
    RF455_QueueCharacterTransparency(c->transparent,&p,&c->math.matrix);return RF_CHARACTER_DRAW_OK;
}
}

extern "C" RF455CharacterDrawStatus RF455_DrawCharacter455(RF455CharacterDrawContext* c,RF455CharacterStorage* model,const void* world,const void* translation){
    using namespace rf455draw;if(!valid(c) || !model || !world)return RF_CHARACTER_DRAW_ARGUMENT;auto* d=c->state.device;
    d->SetRenderState(D3DRS_ALPHABLENDENABLE,TRUE);d->SetRenderState(D3DRS_SRCBLEND,D3DBLEND_SRCALPHA);d->SetRenderState(D3DRS_DESTBLEND,D3DBLEND_INVSRCALPHA);
    d->SetTextureStageState(0,D3DTSS_COLORARG1,D3DTA_TEXTURE);d->SetTextureStageState(0,D3DTSS_COLORARG2,D3DTA_DIFFUSE);d->SetTextureStageState(0,D3DTSS_COLOROP,D3DTOP_MODULATE);d->SetTextureStageState(0,D3DTSS_ALPHAOP,D3DTOP_MODULATE);d->SetTextureStageState(0,D3DTSS_ALPHAARG1,D3DTA_TEXTURE);d->SetTextureStageState(0,D3DTSS_ALPHAARG2,D3DTA_DIFFUSE);
    d->SetTextureStageState(1,D3DTSS_COLORARG1,D3DTA_CURRENT);d->SetTextureStageState(1,D3DTSS_COLORARG2,D3DTA_TEXTURE);d->SetTextureStageState(1,D3DTSS_COLOROP,D3DTOP_ADD);d->SetTextureStageState(1,D3DTSS_ALPHAOP,D3DTOP_MODULATE);d->SetTextureStageState(1,D3DTSS_ALPHAARG1,D3DTA_TEXTURE);d->SetTextureStageState(1,D3DTSS_ALPHAARG2,D3DTA_CURRENT);
    const unsigned now=c->math.ticks(),last=c->globals->previousTick?c->globals->previousTick:now;c->globals->phase=advance(c->globals->phase,now-last);c->globals->previousTick=now;bindDeclaration(c);
    if(c->batchEnabled && c->capturedModels.size()<2048)c->capturedModels.push_back(model);
    auto* meshes=get<RF455MeshStorage*>(model,536);const unsigned count=get<unsigned>(model,532);if(count && !meshes)return RF_CHARACTER_DRAW_ARGUMENT;
    // The original reuses one material scratch across parts; its bump branch
    // does not initialize it. Retain the last defined material. The first bump
    // without a preceding basic material has an explicit zero seed here;
    // original uninitialized-stack behavior is not an equivalence claim.
    float mat[17]={};
    for(unsigned part=0;part<count;++part){auto* mesh=meshes+part;if(get<unsigned>(mesh,5567))continue;
        if(c->batchEnabled && !immediate(mesh) && get<unsigned>(mesh,5759)<200){const auto status=batch(c,mesh,model,world);if(status!=RF_CHARACTER_DRAW_OK)return status;continue;}
        auto* effect=get<unsigned char*>(mesh,5455);if(!effect)return RF_CHARACTER_DRAW_ARGUMENT;
        unsigned lastScroll=get<unsigned>(mesh,5139);if(!lastScroll){lastScroll=now;put(mesh,5139,now);}const float speed=get<float>(effect,180);if(greater(speed,0)){put(mesh,5135,add(get<float>(mesh,5135),delta(now-lastScroll,speed,10000)));put(mesh,5139,now);}
        const unsigned second=get<unsigned>(effect,188);const float frequency=get<float>(effect,288),alpha=get<float>(mesh,5131);
        if(get<unsigned>(effect,160) || (!second && (!equal(frequency,0) || !equal(alpha,1)))){const auto status=enqueue(c,mesh,model,part,world,translation,false);if(status!=RF_CHARACTER_DRAW_OK)return status;continue;}
        const auto texture0=get<IDirect3DBaseTexture9*>(mesh,5107),texture1=get<IDirect3DBaseTexture9*>(mesh,5115),texture2=get<IDirect3DBaseTexture9*>(mesh,5119);
        const auto bump=get<IDirect3DBaseTexture9*>(mesh,5791),specular=get<IDirect3DBaseTexture9*>(mesh,5795),grade=get<IDirect3DBaseTexture9*>(mesh,5799);
        // Modern lighting is a separate opaque pass. Effect/transparent/batch and
        // CPU-skinned routes retain their original programs and state handling.
        if (RF455_EnhancedActorLightingEnabled() && c->state.vertexMode == 4 && !c->useFvf && !c->batchEnabled && !c->orthographic &&
            !get<void*>(mesh,4506) && get<unsigned>(mesh,5086) && get<unsigned>(mesh,522) <= 30 &&
            texture0 && !texture1 && !texture2 && !grade && !second &&
            !get<unsigned>(effect,160) && get<unsigned>(effect,196) &&
            // MESH08 initializes type 1 even when there is no secondary map.
            // In that case the original primary branch is still plain slot 0.
            // Type 4 is different: it swaps primary bindings, so stays excluded.
            get<unsigned>(effect,200) <= 1 && !get<unsigned>(effect,204) &&
            equal(frequency,0) && equal(alpha,1) && (!specular || bump)) {
            float enhancedMaterial[17];
            std::memcpy(enhancedMaterial,reinterpret_cast<const unsigned char*>(model)+720,sizeof(enhancedMaterial));
            EnhancedPixelConstants savedConstants(d);
            if (savedConstants.captured && equal(enhancedMaterial[3],1) && RF455_BindEnhancedActorLighting(c->shaders,
                enhancedMaterial,c->view,c->state.light104+16,bump!=nullptr,specular!=nullptr,&c->selected)) {
                // The legacy loop carries this scratch into later bump parts.
                // Advancing the basic pass must retain that side effect even
                // though the new shader reads the source material directly.
                if (!bump && !specular) material(mat,model,mesh);
                projectionConstants(c);
                RF455_UploadCharacterPalette(d,mesh,world,translation,&c->math.matrix);
                d->SetRenderState(D3DRS_CULLMODE,get<unsigned>(mesh,5143)?D3DCULL_NONE:D3DCULL_CW);
                d->SetTexture(0,texture0);d->SetTexture(1,nullptr);d->SetTexture(2,nullptr);
                d->SetTexture(3,bump);d->SetTexture(4,specular);d->SetTexture(5,nullptr);
                RF455OpaqueGeometryObservation observe;
                const auto status=submit(c,mesh,world,nullptr);clearShaders(c);
                if(status!=RF_CHARACTER_DRAW_OK)return status;
                continue;
            }
        }
        if(!bump && !specular){
            material(mat,model,mesh);
            put<unsigned>(mesh,5763,0);d->SetRenderState(D3DRS_LIGHTING,get<unsigned>(effect,196));d->SetRenderState(D3DRS_CULLMODE,get<unsigned>(mesh,5143)?D3DCULL_NONE:D3DCULL_CW);d->SetRenderState(D3DRS_TEXTUREFACTOR,get<unsigned>(mesh,5147));
            d->SetTextureStageState(0,D3DTSS_COLOROP,D3DTOP_MODULATE);d->SetTextureStageState(0,D3DTSS_ALPHAOP,D3DTOP_MODULATE);d->SetTextureStageState(0,D3DTSS_ALPHAARG1,D3DTA_TEXTURE);
            const unsigned type=get<unsigned>(effect,200);const float scroll=get<float>(mesh,5135);const DWORD factor=get<unsigned>(mesh,5147);
            if(type==4){d->SetTexture(0,texture1);d->SetTexture(1,texture0);RF455_SetCharacterEffectStage(c,1,type,factor,-scroll);if(texture2){d->SetTexture(2,texture2);RF455_SetCharacterEffectStage(c,2,get<unsigned>(effect,204),factor,scroll);d->SetTextureStageState(2,D3DTSS_COLOROP,D3DTOP_ADD);d->SetTextureStageState(2,D3DTSS_COLORARG1,D3DTA_TEXTURE);d->SetTextureStageState(2,D3DTSS_COLORARG2,D3DTA_CURRENT);}}
            else{d->SetTexture(0,texture0);d->SetTexture(1,texture1);if(texture1){secondaryProgram(c,mesh,effect,type);RF455_SetCharacterEffectStage(c,1,type,factor,scroll);d->SetTextureStageState(1,D3DTSS_COLOROP,D3DTOP_ADD);}else d->SetTextureStageState(1,D3DTSS_COLOROP,D3DTOP_DISABLE);}
            if(get<void*>(mesh,4506)){submit(c,mesh,world,nullptr);clearShaders(c);}
            else if(get<unsigned>(mesh,5086)){bindPaletteMaterial(c,mesh,mat,world,translation,true);submit(c,mesh,world,nullptr);clearShaders(c);}else clearShaders(c);
        }else{
            d->SetTexture(0,texture0);d->SetTexture(1,texture1);if(!texture1)d->SetTextureStageState(1,D3DTSS_COLOROP,D3DTOP_DISABLE);d->SetTexture(2,texture2);if(!texture2){d->SetTextureStageState(2,D3DTSS_COLOROP,D3DTOP_DISABLE);d->SetTextureStageState(2,D3DTSS_ALPHAOP,D3DTOP_DISABLE);}
            d->SetTexture(3,bump);if(bump){put<unsigned>(mesh,5763,1);d->SetTextureStageState(0,D3DTSS_ALPHAOP,D3DTOP_MODULATE);d->SetTextureStageState(0,D3DTSS_ALPHAARG1,D3DTA_TEXTURE);d->SetTextureStageState(0,D3DTSS_ALPHAARG2,D3DTA_DIFFUSE);d->SetTextureStageState(1,D3DTSS_ALPHAARG2,D3DTA_CURRENT);}else d->SetTextureStageState(3,D3DTSS_COLOROP,D3DTOP_DISABLE);
            d->SetTexture(4,specular);if(specular)put<unsigned>(mesh,5763,2);else d->SetTextureStageState(4,D3DTSS_COLOROP,D3DTOP_DISABLE);d->SetTexture(5,grade);if(!grade)d->SetTextureStageState(5,D3DTSS_COLOROP,D3DTOP_DISABLE);
            if(get<void*>(mesh,4506))submit(c,mesh,world,nullptr);
            else if(get<unsigned>(mesh,5086)){bindPaletteMaterial(c,mesh,mat,world,translation,false);submit(c,mesh,world,nullptr);clearShaders(c);}
        }
        if(!get<unsigned>(effect,188))continue;
        if(equal(get<float>(effect,288),0) && equal(get<float>(mesh,5131),1) && !get<unsigned>(effect,160)){
            if(!get<unsigned>(effect,200)){d->SetRenderState(D3DRS_FOGENABLE,FALSE);clearShaders(c);}
            const unsigned type=get<unsigned>(effect,204);if(type){d->SetTexture(0,texture0);d->SetTexture(1,texture2);d->SetTextureStageState(0,D3DTSS_COLOROP,D3DTOP_MODULATE);d->SetTextureStageState(0,D3DTSS_ALPHAARG1,D3DTA_TEXTURE|D3DTA_ALPHAREPLICATE);d->SetTextureStageState(0,D3DTSS_ALPHAOP,D3DTOP_MODULATEALPHA_ADDCOLOR);d->SetRenderState(D3DRS_TEXTUREFACTOR,get<unsigned>(mesh,5147));float identity[16];unit(identity);d->SetTransform(D3DTS_TEXTURE0,reinterpret_cast<const D3DMATRIX*>(identity));RF455_SetCharacterEffectStage(c,1,type,get<unsigned>(mesh,5147),get<float>(mesh,5135));std::memcpy(mat,reinterpret_cast<const unsigned char*>(model)+720,68);secondaryProgram(c,mesh,effect,type);bindPaletteMaterial(c,mesh,mat,world,translation,true);}
            if(get<unsigned>(mesh,5086))submit(c,mesh,world,nullptr,true);clearShaders(c);
        }else{const auto status=enqueue(c,mesh,model,part,world,translation,true);if(status!=RF_CHARACTER_DRAW_OK)return status;}
    }
    d->SetRenderState(D3DRS_FOGENABLE,FALSE);d->SetRenderState(D3DRS_ZENABLE,D3DZB_TRUE);d->SetRenderState(D3DRS_STENCILENABLE,FALSE);return RF_CHARACTER_DRAW_OK;
}

extern "C" RF455CharacterDrawStatus RF455_DrawCharacterOverlay455(RF455CharacterDrawContext* c,RF455CharacterStorage* model,const void* world){
    using namespace rf455draw;
    if(!valid(c)||!model||!world)return RF_CHARACTER_DRAW_ARGUMENT;
    const unsigned now=c->math.ticks();
    auto* meshes=get<RF455MeshStorage*>(model,536);
    const unsigned count=get<unsigned>(model,532);
    if(!meshes)return RF_CHARACTER_DRAW_OK;
    const unsigned previous=c->globals->overlayPreviousTick?c->globals->overlayPreviousTick:now;
    c->globals->overlayPhase=advance(c->globals->overlayPhase,now-previous);
    c->globals->overlayPreviousTick=now;
    bindDeclaration(c);
    if(c->batchEnabled&&c->capturedModels.size()<2048)c->capturedModels.push_back(model);
    for(unsigned part=0;part<count;++part){
        auto* mesh=meshes+part;if(get<unsigned>(mesh,5567))continue;
        if(c->batchEnabled&&!immediate(mesh)&&get<unsigned>(mesh,5759)<200){
            const auto status=batch(c,mesh,model,world);if(status!=RF_CHARACTER_DRAW_OK)return status;continue;
        }
        projection(c);projectionConstants(c);
        RF455_UploadCharacterPalette(c->state.device,mesh,world,nullptr,&c->math.matrix);
        c->state.device->SetRenderState(D3DRS_CULLMODE,get<unsigned>(mesh,5143)?D3DCULL_NONE:D3DCULL_CW);
        if(get<void*>(mesh,4506)||get<unsigned>(mesh,5086)){
            const auto status=submit(c,mesh,world,nullptr);if(status!=RF_CHARACTER_DRAW_OK)return status;
        }
    }
    select(c,0xffffffffu);return RF_CHARACTER_DRAW_OK;
}

extern "C" RF455CharacterDrawStatus RF455_FlushCharacterTransparency(RF455CharacterDrawContext* c){
    using namespace rf455draw;if(!valid(c))return RF_CHARACTER_DRAW_ARGUMENT;auto* q=c->transparent;if(!q->count)return RF_CHARACTER_DRAW_OK;auto* d=c->state.device;
    RF455_SetCharacterDrawState(&c->state);float identity[16];unit(identity);for(unsigned i=0;i<4;++i)d->SetTransform(static_cast<D3DTRANSFORMSTATETYPE>(256+i),reinterpret_cast<const D3DMATRIX*>(identity));bindDeclaration(c);projection(c);projectionConstants(c);
    auto* p=q->head;unsigned processed=0;
    while(p && processed<q->count){select(c,p->effect==2?6:11);RF455_SetCharacterEffectStage(c,1,p->effect,p->textureFactor,p->scroll);
        if(p->secondPass){d->SetTextureStageState(0,D3DTSS_COLOROP,D3DTOP_SELECTARG1);d->SetTextureStageState(0,D3DTSS_ALPHAARG1,p->inverted?18:2);d->SetTextureStageState(0,D3DTSS_ALPHAOP,p->inverted?13:4);d->SetTextureStageState(1,D3DTSS_COLOROP,D3DTOP_SELECTARG2);d->SetTextureStageState(1,D3DTSS_ALPHAARG1,D3DTA_CURRENT);d->SetTextureStageState(1,D3DTSS_ALPHAOP,D3DTOP_MODULATE);d->SetTextureStageState(1,D3DTSS_ALPHAARG2,D3DTA_TEXTURE);}
        else{d->SetTextureStageState(0,D3DTSS_COLORARG1,D3DTA_TEXTURE);d->SetTextureStageState(0,D3DTSS_COLORARG2,D3DTA_DIFFUSE);d->SetTextureStageState(0,D3DTSS_COLOROP,D3DTOP_MODULATE);d->SetTextureStageState(0,D3DTSS_ALPHAOP,D3DTOP_MODULATE);d->SetTextureStageState(0,D3DTSS_ALPHAARG1,D3DTA_TEXTURE);d->SetTextureStageState(0,D3DTSS_ALPHAARG2,D3DTA_DIFFUSE);d->SetTextureStageState(1,D3DTSS_COLORARG1,D3DTA_CURRENT);d->SetTextureStageState(1,D3DTSS_COLORARG2,D3DTA_TEXTURE);d->SetTextureStageState(1,D3DTSS_COLOROP,D3DTOP_ADD);d->SetTextureStageState(1,D3DTSS_ALPHAOP,D3DTOP_MODULATE);d->SetTextureStageState(1,D3DTSS_ALPHAARG1,D3DTA_TEXTURE);d->SetTextureStageState(1,D3DTSS_ALPHAARG2,D3DTA_CURRENT);}
        d->SetRenderState(D3DRS_TEXTUREFACTOR,0);d->SetTexture(0,p->primary);d->SetTexture(1,p->secondary);d->SetTextureStageState(1,D3DTSS_COLOROP,p->secondary?D3DTOP_ADD:D3DTOP_DISABLE);
        float mat[17];std::memcpy(mat,p->material,68);mat[3]=p->alpha;if(equal(p->frequency,0) || p->inverted==1)d->SetRenderState(D3DRS_DESTBLEND,D3DBLEND_INVSRCALPHA);else{d->SetRenderState(D3DRS_SRCBLEND,D3DBLEND_SRCALPHA);d->SetRenderState(D3DRS_DESTBLEND,D3DBLEND_ONE);}if(p->special && equal(p->frequency,0))mat[3]=.5f;
        d->SetVertexShaderConstantF(18,mat,1);d->SetVertexShaderConstantF(19,mat+4,1);if(p->boneCount)for(unsigned i=0;i<p->boneCount;++i)d->SetVertexShaderConstantF(100+4*i,p->palette[i],4);else for(unsigned i=0;i<4;++i)d->SetVertexShaderConstantF(100+4*i,p->palette[0],4);
        auto* mesh=p->mesh;if(!mesh)return RF_CHARACTER_DRAW_ARGUMENT;if(get<unsigned>(mesh,5086)){if(!get<void*>(mesh,4506) && get<unsigned>(mesh,4502)!=0xffffffffu)select(c,11);submit(c,mesh,identity,p->palette[0]);}
        p=p->next;++processed;
    }
    RF455_ResetCharacterTransparency(q);select(c,0xffffffffu);return RF_CHARACTER_DRAW_OK;
}

extern "C" RF455CharacterDrawStatus RF455_FlushCharacterMeshBatch(RF455CharacterDrawContext* c,RF455MeshStorage* mesh){
    using namespace rf455draw;if(!valid(c) || !mesh)return RF_CHARACTER_DRAW_ARGUMENT;auto* d=c->state.device;if(c->state.vertexMode==2)d->SetFVF(278);else if(c->state.vertexMode==4)d->SetFVF(282);
    const unsigned count=get<unsigned>(mesh,5759);for(unsigned i=0;i<count;++i){const auto* record=get<const BatchRecord*>(mesh,5595+4*(i/10))+i%10;const auto* mat=get<const float*>(mesh,5675+4*(i/10))+17*(i%10);auto* owner=record->mesh;d->SetTexture(0,get<IDirect3DBaseTexture9*>(owner,5107));d->SetTexture(1,nullptr);d->SetRenderState(D3DRS_CULLMODE,get<unsigned>(owner,5143)?D3DCULL_NONE:D3DCULL_CW);d->SetMaterial(reinterpret_cast<const D3DMATERIAL9*>(mat));float identity[16];unit(identity);for(unsigned j=0;j<4;++j)d->SetTransform(static_cast<D3DTRANSFORMSTATETYPE>(256+j),reinterpret_cast<const D3DMATRIX*>(identity));const unsigned bones=get<unsigned>(owner,522);for(unsigned j=0;j<(bones?bones:1);++j)d->SetTransform(static_cast<D3DTRANSFORMSTATETYPE>(256+j),reinterpret_cast<const D3DMATRIX*>(record->palette[j]));if(get<unsigned>(owner,5086))submit(c,owner,identity,record->palette[0]);}
    put<unsigned>(mesh,5759,0);return RF_CHARACTER_DRAW_OK;
}

extern "C" RF455CharacterDrawStatus RF455_DrawCharacterShadow(RF455CharacterDrawContext* c,RF455CharacterStorage* model,const void* world){
    using namespace rf455draw;if(!valid(c) || !model || !world)return RF_CHARACTER_DRAW_ARGUMENT;c->math.ticks();bindDeclaration(c);select(c,3);auto* meshes=get<RF455MeshStorage*>(model,536);const unsigned count=get<unsigned>(model,532);if(count && !meshes)return RF_CHARACTER_DRAW_ARGUMENT;
    if(c->batchEnabled && c->capturedModels.size()<2048)c->capturedModels.push_back(model);
    for(unsigned i=0;i<count;++i){auto* mesh=meshes+i;if(get<unsigned>(mesh,5567))continue;c->state.device->SetRenderState(D3DRS_CULLMODE,get<unsigned>(mesh,5143)?D3DCULL_NONE:D3DCULL_CW);if(c->batchEnabled && !immediate(mesh) && get<unsigned>(mesh,5759)<200){const auto status=batch(c,mesh,model,world);if(status!=RF_CHARACTER_DRAW_OK)return status;}else{RF455_UploadCharacterPalette(c->state.device,mesh,world,nullptr,&c->math.matrix);if(get<unsigned>(mesh,5086))submit(c,mesh,world,nullptr,true);}}
    select(c,0xffffffffu);return RF_CHARACTER_DRAW_OK;
}
