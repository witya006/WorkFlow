//4558C9230/8C94A0 and8C7E40..8C8093. Included before ordinary DrawOneMatGroup.
#include "client455_special_shaders.h"
#include "client455_shader_lights.h"
#include "client455_material_shaders.h"
namespace {
RF455MaterialShaderSelection materialShader455={};
void prepareMaterialShader455(_R3MATERIAL* mat,_BSP_MAT_GROUP* group){
    auto* d=GetD3dDevice();auto* state=GetR3State();
    if(mat->m_dwFlag&0x10000000u){materialShader455.objectIndex=int((mat->m_dwFlag>>8)&255)-1;materialShader455.lightIndex=mat->m_dwFlag&255;}
    else materialShader455.objectIndex=int(mat->m_dwFlag-0x01000001u); //Does not reset lightIndex.
    d->SetTexture(mat->m_dwLayerNum,static_cast<IDirect3DBaseTexture9*>(GetLightMapSurface(group->LgtId)));
    if(state->mIsFog)d->SetRenderState(D3DRS_FOGENABLE,FALSE);
    d->SetVertexShaderConstantF(0,reinterpret_cast<const float*>(&state->mMatProj),4);
    d->SetVertexShaderConstantF(4,reinterpret_cast<const float*>(&state->mMatView),4);
    d->SetVertexShaderConstantF(8,reinterpret_cast<const float*>(&state->mMatWorld),4);
    //1158038 is inverse-view row4,including its _44 component. No transpose.
    d->SetVertexShaderConstantF(15,&state->mInvMatView._41,1);d->SetPixelShaderConstantF(15,&state->mInvMatView._41,1);
    if(RF455_GetShaderLightCount()){
        auto* light=RF455_GetShaderLight(0);
        if(light){
            //Target reads a fourth float past the32-byte record forPS6. Its
            //unowned lane is not synthesized;equivalence for that lane is open.
            d->SetPixelShaderConstantF(6,light->color,1);d->SetVertexShaderConstantF(18,light->position,1);
        }
    }else d->SetVertexShaderConstantF(18,&state->mInvMatView._41,1);
    for(unsigned i=0;i<mat->m_dwLayerNum;++i)d->SetTexture(i,R3GetSurface(mat->m_Layer[i].m_iSurface));
    const auto& layer=mat->m_Layer[0];float values[4]={};
    if(layer.m_dwFlag&0x10)values[0]=float(double(layer.m_sUVScrollU)/256.);
    if(layer.m_dwFlag&0x20)values[1]=float(double(layer.m_sUVScrollV)/256.);
    if(layer.m_dwFlag&0x800001)values[2]=layer.m_fSpecularFlickeringScale;
    if(layer.m_dwFlag&0x800002)values[3]=layer.m_fSpecularFlickeringSpeed;
    d->SetPixelShaderConstantF(18,values,1);GetBumpFactor(values);values[3]=R3GetTime();d->SetPixelShaderConstantF(17,values,1);
    const auto* object=RF455_GetSpecialShaderObject(materialShader455.objectIndex);
    d->SetVertexShader(RF455_GetSpecialVertexShader(object->vertex));
    object=RF455_GetSpecialShaderObject(materialShader455.objectIndex);
    d->SetPixelShader(RF455_GetSpecialPixelShader(object->pixel)); //Deliberate second object indirection.
}
void finishMaterialShader455(_R3MATERIAL* mat){
    auto* d=GetD3dDevice();for(unsigned i=0;i<mat->m_dwLayerNum;++i)d->SetTexture(i,nullptr);
    d->SetVertexShader(nullptr);d->SetPixelShader(nullptr); //Lightmap slot=layerCount is retained.
}
void prepareSplatPair455(_R3MATERIAL* mat,unsigned layer){
    auto* d=GetD3dDevice();
    d->SetTextureStageState(0,D3DTSS_COLORARG1,D3DTA_TEXTURE);d->SetTextureStageState(0,D3DTSS_COLORARG2,D3DTA_DIFFUSE);d->SetTextureStageState(0,D3DTSS_COLOROP,D3DTOP_MODULATE);
    d->SetTextureStageState(0,D3DTSS_ALPHAARG2,D3DTA_DIFFUSE);d->SetTextureStageState(0,D3DTSS_ALPHAARG1,D3DTA_TEXTURE);d->SetTextureStageState(0,D3DTSS_ALPHAOP,D3DTOP_SELECTARG2);
    d->SetTexture(0,R3GetSurface(mat->m_Layer[layer].m_iSurface));
    d->SetTexture(1,R3GetSurface(mat->m_Layer[layer+1].m_iSurface));
    d->SetTextureStageState(1,D3DTSS_COLORARG1,D3DTA_TEXTURE);d->SetTextureStageState(1,D3DTSS_COLORARG2,D3DTA_CURRENT);d->SetTextureStageState(1,D3DTSS_COLOROP,D3DTOP_MODULATE);
    d->SetTextureStageState(1,D3DTSS_ALPHAARG1,D3DTA_TEXTURE);d->SetTextureStageState(1,D3DTSS_ALPHAARG2,D3DTA_CURRENT);d->SetTextureStageState(1,D3DTSS_ALPHAOP,D3DTOP_MODULATE);
    BlendOn(1);d->SetTextureStageState(1,D3DTSS_ALPHAOP,D3DTOP_MODULATE);d->SetRenderState(D3DRS_ALPHAREF,0);
}
void drawSplat455(CVertexBuffer* vb,_BSP_MAT_GROUP* group,_R3MATERIAL* mat){
    auto* d=GetD3dDevice();
    auto draw=[&](){d->DrawIndexedPrimitive(D3DPT_TRIANGLELIST,0,group->VBMinIndex,group->VCnt,group->IBMinIndex,group->TriNum);};
    for(unsigned layer=1;layer<mat->m_dwLayerNum;layer+=2){
        PreRenderSetting(layer,vb,group);prepareSplatPair455(mat,layer);draw();AfterRenderSetting(layer,vb,group);
        BlendOff();d->SetRenderState(D3DRS_ALPHAREF,8);d->SetTextureStageState(2,D3DTSS_COLOROP,D3DTOP_DISABLE);d->SetTextureStageState(2,D3DTSS_ALPHAOP,D3DTOP_DISABLE);
    }
    MultiTexOff();BlendOn(10);d->SetTexture(0,group->LgtId==-1?nullptr:static_cast<IDirect3DBaseTexture9*>(GetLightMapSurface(group->LgtId)));
    d->SetRenderState(D3DRS_ALPHAREF,0);d->SetTextureStageState(0,D3DTSS_TEXCOORDINDEX,1);draw();
    BlendOff();d->SetTextureStageState(0,D3DTSS_TEXCOORDINDEX,0);d->SetRenderState(D3DRS_ALPHAREF,8);MultiTexOn();
}
}
const RF455MaterialShaderSelection& RF455_GetMaterialShaderSelection(){return materialShader455;}
