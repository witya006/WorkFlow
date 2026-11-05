#include "client455_draw.h"
#include <cstring>

namespace {
template<class T> T get(const unsigned char* p,unsigned at){T value;std::memcpy(&value,p+at,sizeof(value));return value;}
}
extern "C" void RF455_SetCharacterDrawState(const RF455CharacterDrawState* state){
    auto* d=state->device;
    d->SetRenderState(D3DRS_AMBIENT,0xffffffffu);
    d->SetTextureStageState(0,D3DTSS_COLORARG1,D3DTA_TEXTURE);
    d->SetTextureStageState(0,D3DTSS_COLORARG2,D3DTA_DIFFUSE);
    d->SetTextureStageState(0,D3DTSS_COLOROP,D3DTOP_MODULATE);
    d->SetTextureStageState(0,D3DTSS_ALPHAOP,D3DTOP_MODULATE);
    d->SetTextureStageState(0,D3DTSS_ALPHAARG1,D3DTA_TEXTURE);
    d->SetTextureStageState(0,D3DTSS_ALPHAARG2,D3DTA_DIFFUSE);
    d->SetSamplerState(0,D3DSAMP_MINFILTER,D3DTEXF_LINEAR);
    d->SetSamplerState(0,D3DSAMP_MAGFILTER,D3DTEXF_LINEAR);
    d->SetTextureStageState(1,D3DTSS_COLORARG1,D3DTA_CURRENT);
    d->SetTextureStageState(1,D3DTSS_COLORARG2,D3DTA_TEXTURE);
    d->SetTextureStageState(1,D3DTSS_COLOROP,D3DTOP_ADD);
    d->SetTextureStageState(1,D3DTSS_ALPHAOP,D3DTOP_MODULATE);
    d->SetTextureStageState(1,D3DTSS_ALPHAARG1,D3DTA_TEXTURE);
    d->SetTextureStageState(1,D3DTSS_ALPHAARG2,D3DTA_DIFFUSE);
    d->SetSamplerState(1,D3DSAMP_MINFILTER,D3DTEXF_LINEAR);
    d->SetSamplerState(1,D3DSAMP_MAGFILTER,D3DTEXF_LINEAR);
    d->SetTextureStageState(1,D3DTSS_TEXCOORDINDEX,D3DTSS_TCI_CAMERASPACENORMAL);
    d->SetRenderState(D3DRS_TEXTUREFACTOR,0);
    d->SetRenderState(D3DRS_ALPHABLENDENABLE,TRUE);
    d->SetRenderState(D3DRS_SRCBLEND,D3DBLEND_SRCALPHA);
    d->SetRenderState(D3DRS_DESTBLEND,D3DBLEND_INVSRCALPHA);
    d->SetRenderState(D3DRS_ALPHATESTENABLE,TRUE);
    d->SetRenderState(D3DRS_ALPHAREF,8);
    d->SetRenderState(D3DRS_ALPHAFUNC,D3DCMP_GREATEREQUAL);
    d->SetRenderState(D3DRS_CULLMODE,D3DCULL_CW);
    if(state->vertexMode==2){d->SetRenderState(D3DRS_VERTEXBLEND,D3DVBF_1WEIGHTS);d->SetVertexDeclaration(state->declaration36);}
    else if(state->vertexMode==4){d->SetRenderState(D3DRS_VERTEXBLEND,D3DVBF_3WEIGHTS);d->SetVertexDeclaration(state->declaration64);}
    for(DWORD sampler:{3u,4u}){
        d->SetSamplerState(sampler,D3DSAMP_MINFILTER,D3DTEXF_LINEAR);
        d->SetSamplerState(sampler,D3DSAMP_MAGFILTER,D3DTEXF_LINEAR);
        d->SetSamplerState(sampler,D3DSAMP_MIPFILTER,D3DTEXF_LINEAR);
    }
    d->SetVertexShaderConstantF(10,state->light104+16,1);
    d->SetRenderState(D3DRS_SHADEMODE,D3DSHADE_GOURAUD);
    d->SetRenderState(D3DRS_ZENABLE,D3DZB_TRUE);
    if(state->specularEnable){
        d->SetRenderState(D3DRS_SPECULARENABLE,state->specularEnable);
        d->SetRenderState(D3DRS_DIFFUSEMATERIALSOURCE,D3DMCS_MATERIAL);
        d->SetRenderState(D3DRS_NORMALIZENORMALS,TRUE);
    }
    d->SetRenderState(D3DRS_FOGENABLE,FALSE);
}
extern "C" HRESULT RF455_SelectCharacterShader(RF455ShaderManager* manager,unsigned index,unsigned* selected){
    const bool valid=index!=0xffffffffu && index<manager->count;
    manager->device->SetVertexShader(valid?manager->programs[index].vertex:nullptr);
    const HRESULT result=manager->device->SetPixelShader(valid?manager->programs[index].pixel:nullptr);
    *selected=index;return result;
}
extern "C" HRESULT RF455_SetCharacterMaterial(IDirect3DDevice9* device,const void* material68){
    const auto* bytes=static_cast<const unsigned char*>(material68);
    device->SetVertexShaderConstantF(19,reinterpret_cast<const float*>(bytes+16),1);
    return device->SetVertexShaderConstantF(18,reinterpret_cast<const float*>(bytes),1);
}
extern "C" HRESULT RF455_UploadCharacterPalette(IDirect3DDevice9* device,const RF455MeshStorage* mesh,
    const void* world,const void* translationWorld,const RF455MeshMatrixOps* matrices){
    const unsigned count=get<unsigned>(mesh->bytes,522);
    float palette[16],translation[16];HRESULT result=S_OK;
    const unsigned n=count?count:1;
    for(unsigned i=0;i<n;++i){
        const void* skin=mesh->bytes+(count?646+64*i:4830);
        matrices->multiply(palette,skin,world);
        if(translationWorld){matrices->multiply(translation,skin,translationWorld);std::memcpy(palette+12,translation+12,12);}
        if(count)result=device->SetVertexShaderConstantF(100+4*i,palette,4);
        else for(unsigned k=0;k<4;++k)result=device->SetVertexShaderConstantF(100+4*k,palette,4);
    }
    return result;
}
extern "C" HRESULT RF455_SubmitSharedCharacterMesh(IDirect3DDevice9* device,unsigned mode,
    RF455VertexBufferPool* vertices36,RF455VertexBufferPool* vertices64,
    RF455IndexBufferPool* indices,const RF455MeshStorage* mesh){
    if(get<const void*>(mesh->bytes,4506))return D3DERR_INVALIDCALL;
    const unsigned count=get<unsigned>(mesh->bytes,5086);if(!count)return S_FALSE;
    const unsigned vertex=get<unsigned>(mesh->bytes,4494),index=get<unsigned>(mesh->bytes,4502);
    unsigned start=0xffffffffu;
    if(mode==2){RF455_BindVertices36(vertices36,vertex);start=(vertex%RF455_VERTEX_BLOCK_BYTES)/36;}
    else if(mode==4){RF455_BindVertices64(vertices64,vertex);start=(vertex%RF455_VERTEX_BLOCK_BYTES)>>6;}
    if(index==0xffffffffu)return device->DrawPrimitive(D3DPT_TRIANGLELIST,start,count/3);
    RF455_BindIndices(indices,index);
    return device->DrawIndexedPrimitive(D3DPT_TRIANGLELIST,0,start,count,
        (index%RF455_INDEX_BLOCK_BYTES)>>1,get<unsigned>(mesh->bytes,5090)/3);
}
