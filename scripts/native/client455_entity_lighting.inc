#include "client455_sky_lighting.h"
#include "client455_entity_lighting.h"
#include "client455_entity_normals.h"
#include "client455_light_direction.inc"
#include "r3util.h"

//4558E3630. The light branch takes priority over the map-color-only branch.
static void prepareEntityLighting455(DWORD flags,DWORD mapColor,DWORD color){
    auto* d=GetD3dDevice();D3DMATERIAL9 material={};const float alpha=float(double(color>>24)/255.0);
    if(flags&0x40){
        d->LightEnable(0,TRUE);MultiTexOff();D3DLIGHT9 light;
        GetMatLightFromColor(&light,&material,RF455_ApplySkyTint(mapColor),1.f);
        light.Direction.x=-light.Direction.x;light.Direction.y=-light.Direction.y;light.Direction.z=-light.Direction.z;
        material.Diffuse.a=alpha;
        material.Diffuse.r=min(1.f,float(double(material.Diffuse.r)+.25));
        material.Diffuse.g=min(1.f,float(double(material.Diffuse.g)+double(.2f)));
        material.Diffuse.b=min(1.f,float(double(material.Diffuse.b)+double(.2f)));
        material.Ambient.r=min(1.f,float(double(material.Ambient.r)+double(.1f)));
        material.Ambient.g=min(1.f,float(double(material.Ambient.g)+double(.1f)));
        material.Ambient.b=min(1.f,float(double(material.Ambient.b)+double(.1f)));
        d->SetLight(0,&light);d->SetTextureStageState(0,D3DTSS_COLOROP,D3DTOP_MODULATE);
        d->SetRenderState(D3DRS_DIFFUSEMATERIALSOURCE,D3DMCS_MATERIAL);
        material.Emissive.r=material.Emissive.g=material.Emissive.b=0;material.Emissive.a=alpha;
        d->SetRenderState(D3DRS_EMISSIVEMATERIALSOURCE,D3DMCS_MATERIAL);d->LightEnable(0,TRUE);
    }else{
        material.Diffuse.a=alpha;
        //Preserve the real zero/zero behavior for zero input color components.
        volatile float r=float(double((color>>16)&255)/255.0),g=float(double((color>>8)&255)/255.0),b=float(double(color&255)/255.0);
        material.Diffuse.r=r/r;material.Diffuse.g=g/g;material.Diffuse.b=b/b;
        if((color&0xffffffu)==0xffffffu){d->SetRenderState(D3DRS_EMISSIVEMATERIALSOURCE,D3DMCS_COLOR1);d->LightEnable(0,FALSE);}
        else{material.Emissive.a=alpha;material.Emissive.r=r;material.Emissive.g=g;material.Emissive.b=b;d->SetRenderState(D3DRS_EMISSIVEMATERIALSOURCE,D3DMCS_MATERIAL);d->LightEnable(0,TRUE);}
        d->SetTextureStageState(0,D3DTSS_COLOROP,D3DTOP_MODULATE2X);d->SetRenderState(D3DRS_DIFFUSEMATERIALSOURCE,D3DMCS_COLOR1);
        if(flags&0x20){
            d->SetTextureStageState(0,D3DTSS_COLORARG2,D3DTA_TFACTOR);d->SetRenderState(D3DRS_TEXTUREFACTOR,RF455_ApplySkyTint(mapColor));
            d->SetTextureStageState(1,D3DTSS_TEXCOORDINDEX,1);d->SetTextureStageState(1,D3DTSS_COLORARG1,D3DTA_DIFFUSE);
            d->SetTextureStageState(1,D3DTSS_COLORARG2,D3DTA_CURRENT);d->SetTextureStageState(1,D3DTSS_COLOROP,D3DTOP_MODULATE2X);
        }else MultiTexOff();
    }
    d->SetRenderState(D3DRS_LIGHTING,TRUE);d->SetMaterial(&material);d->SetRenderState(D3DRS_SPECULARENABLE,FALSE);
}

static void prepareEntityShader455(DWORD flags,DWORD mapColor,float addFrame,_ENTITY_LIST* list,float world[4][4],DWORD color){
    if(list->ShaderID!=1&&list->ShaderID!=2)return;
    const float alpha=float(double(color>>24)/255.0);const DWORD tint=RF455_ApplySkyTint(mapColor);
    if(flags&0x40){
        float direction[3];RF455_BuildLightDirection(direction,world,GetR3State()->mMainLightNomal);
        RF455_SetLitGrass(addFrame,list->Factor,alpha,tint,direction);
    }else SetGrassVS(addFrame,list->Factor,alpha,tint);
}
void CEntity::SetVertexShaderID(_ENTITY_LIST* list,DWORD color){prepareEntityShader455(mFlag,mMapColor,mAddFrame,list,GetR3State()->mMatWorld.m,color);}
