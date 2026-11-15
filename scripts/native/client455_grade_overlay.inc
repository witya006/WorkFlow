#include "multilayer.h"
#include "r3d3dtex.h"
#include "r3render.h"
#include "client455_resource_io.h"
#include "client455_resource_text.h"
#include <array>
#include <cstdlib>
#include <cstring>

struct RF455GradeOverlayResources::State {
    std::array<_R3MATERIAL,4> materials{};
    std::array<IDirect3DTexture9*,4> textures{};
    bool attempted=false;
};
namespace {
SHORT gradeFixed455(const char* value,float scale) {
    return static_cast<SHORT>(static_cast<int>(double(static_cast<float>(std::atof(value)))*scale));
}
bool gradeLayer455(RF455ResourceText& input,_R3MATERIAL& material,unsigned index,IDirect3DTexture9*& texture) {
    auto& layer=material.m_Layer[index];layer.m_ARGB=0xffffffff;
    char token[256];
    while(input.read(token)) {
        if(!std::strcmp(token,"}")) {
            if(!layer.m_sANIAlphaFlickerAni)layer.m_sANIAlphaFlickerAni=255;
            return true;
        }
        const auto read=[&](){return input.read(token);};
        // Independent comparisons preserve the original parser's token reuse.
        if(!std::strcmp(token,"map_name")) {
            if(!read())return false;
            auto* loaded=R3LoadDDSAndTextureMem(token);
            if(texture)texture->Release();texture=loaded;
        }
#define GRADE_FIXED(name,field,bits) \
        if(!std::strcmp(token,name)){if(!read())return false;layer.field=gradeFixed455(token,256);layer.m_dwFlag|=bits;}
        GRADE_FIXED("uv_scroll_u",m_sUVScrollU,0x10)
        GRADE_FIXED("uv_scroll_v",m_sUVScrollV,0x20)
        if(!std::strcmp(token,"uv_scale")) {
            if(!read())return false;layer.m_sUVScaleStart=gradeFixed455(token,256);
            layer.m_sUVScaleEnd=layer.m_sUVScaleStart;layer.m_sUVScaleSpeed=256;layer.m_dwFlag|=0x80;
        }
        GRADE_FIXED("uv_scale_speed",m_sUVScaleSpeed,0)
        GRADE_FIXED("uv_scale_start",m_sUVScaleStart,0)
        GRADE_FIXED("uv_scale_end",m_sUVScaleEnd,0)
        GRADE_FIXED("uv_rotate",m_sUVRotate,0x40)
        if(!std::strcmp(token,"uv_lava")) {
            if(!read())return false;if(!layer.m_sUVLavaWave)layer.m_sUVLavaWave=256;
            layer.m_sUVLavaSpeed=gradeFixed455(token,256);layer.m_dwFlag|=4;
        }
        GRADE_FIXED("uv_lava_wave",m_sUVLavaWave,0)
        if(!std::strcmp(token,"uv_gradient_alpha_u")) {
            if(!read())return false;layer.m_sGradientAlpha|=static_cast<WORD>(int(double(float(std::atof(token)))*25+100))<<8;layer.m_dwFlag|=0x100;
        }
        if(!std::strcmp(token,"uv_gradient_alpha_v")) {
            if(!read())return false;layer.m_sGradientAlpha|=static_cast<WORD>(int(double(float(std::atof(token)))*25+100));layer.m_dwFlag|=0x200;
        }
        GRADE_FIXED("uv_metal_floor",m_sUVMetal,2)
        GRADE_FIXED("uv_metal_wall",m_sUVMetal,8)
        GRADE_FIXED("ani_alpha_flicker",m_sANIAlphaFlicker,0x400)
        if(!std::strcmp(token,"ani_alpha_flicker_start")) {
            if(!read())return false;layer.m_sANIAlphaFlickerAni|=static_cast<WORD>(gradeFixed455(token,255))<<8;
        }
        if(!std::strcmp(token,"ani_alpha_flicker_end")) {
            if(!read())return false;layer.m_sANIAlphaFlickerAni|=static_cast<WORD>(gradeFixed455(token,255));
        }
        GRADE_FIXED("ani_tex_speed",m_sANITexSpeed,0)
        if(!std::strcmp(token,"ani_tex_frame")) {
            if(!read())return false;layer.m_dwFlag|=0x800;layer.m_sANITexFrame=gradeFixed455(token,256);
            if(!layer.m_sANITexSpeed)layer.m_sANITexSpeed=256;
        }
#undef GRADE_FIXED
        if(!std::strcmp(token,"uv_env")){if(!read())return false;layer.m_dwFlag|=1;}
        if(!std::strcmp(token,"alpha_sort")) {
            if(!read())return false;_strupr(token);
            if(!std::strcmp(token,"TRUE")&&!index)layer.m_dwAlphaType|=0x80000000;
        }
        if(!std::strcmp(token,"tex_clamp"))layer.m_dwFlag|=0x10000;
        if(!std::strcmp(token,"zwrite"))layer.m_dwAlphaType|=0x2000;
        if(!std::strcmp(token,"bump_env"))layer.m_dwFlag|=0x8000;
        if(!std::strcmp(token,"type")){if(!read())return false;layer.m_dwAlphaType=std::atol(token);}
        if(!std::strcmp(token,"alpha")){if(!read())return false;layer.m_ARGB=(layer.m_ARGB&0xffffff)|(DWORD(std::atol(token))<<24);}
        if(!std::strcmp(token,"color")) {
            if(!read())return false;const DWORD red=std::atol(token);
            if(!read())return false;const DWORD green=std::atol(token);
            if(!read())return false;const DWORD blue=std::atol(token);
            layer.m_ARGB=(layer.m_ARGB&0xff000000)|(red<<16)|(green<<8)|blue;
        }
    }
    return false; //Target loops at EOF inside a layer;malformed-input fidelity remains open.
}
bool gradeMaterial455(const char* name,_R3MATERIAL& material,IDirect3DTexture9*& texture) {
    std::memset(&material,0,sizeof material);
    RF455ResourceText input;
    if (!input.open(name)) return false;
    char token[256];bool okay=true;
    while(input.read(token)&&std::strcmp(token,"end")&&std::strcmp(token,"}")) {
        if(std::strcmp(token,"layer"))continue;
        if(!input.read(token)){okay=false;break;}
        const long index=std::atol(token);
        if(index<0||index>=7||!gradeLayer455(input,material,unsigned(index),texture)){okay=false;break;}
    }
    if (!okay && input.hasCachedInput()) RF455_GetCharacterRfsCache()->RemoveLooseBytes(name);
    return okay;
}
}
RF455GradeOverlayResources::RF455GradeOverlayResources():state(new State){}
RF455GradeOverlayResources::~RF455GradeOverlayResources(){Release455();}
RF455GradeOverlayResources& RF455_GradeOverlays455(){static RF455GradeOverlayResources resources;return resources;}
void RF455_LoadGradeOverlays455(){RF455_GradeOverlays455().Load455();}
void RF455_ReleaseGradeOverlays455(){RF455_GradeOverlays455().Release455();}
bool RF455GradeOverlayResources::Load455() {
    Release455();RF455_SetResourceArchiveEnabled(FALSE);bool complete=true;
    static const char* names[]={".\\Chef\\GradeEffect\\Bgrade.mst",".\\Chef\\GradeEffect\\Agrade.mst",".\\Chef\\GradeEffect\\Cgrade.mst",".\\Chef\\GradeEffect\\Dgrade.mst"};
    for(unsigned i=0;i<4;++i)if(!gradeMaterial455(names[i],state->materials[i],state->textures[i]))complete=false;
    state->attempted=true;return complete;
}
void RF455GradeOverlayResources::Release455(){for(auto*& texture:state->textures){if(texture)texture->Release();texture=nullptr;}state->attempted=false;}
const _R3MATERIAL& RF455GradeOverlayResources::Material455(unsigned index)const{return state->materials.at(index);}
IDirect3DTexture9* RF455GradeOverlayResources::Texture455(unsigned index)const{return state->textures.at(index);}
void RF455GradeOverlayResources::Begin455(BYTE grade) {
    if(!grade)return;if(!state->attempted)throw std::logic_error("455 grade materials have not been initialized");
    const unsigned index=grade>4?3:grade-1;auto& material=state->materials[index];auto* device=GetD3dDevice();
    if(!device)throw std::logic_error("455 grade overlay requires the actual device");
    device->LightEnable(0,TRUE);D3DXMATRIX uv;
    const bool matrix=GetTextureMatrix(&material,0,&uv,0)!=0;
    MultiTexOff();device->SetTexture(0,state->textures[index]);device->SetTexture(1,nullptr);
    if(matrix)_GetCharIF()->SetOverlayTextureMatrix455(uv,false);
    BlendOn(material.m_Layer[0].m_dwAlphaType);device->SetRenderState(D3DRS_ZWRITEENABLE,FALSE);
    if(material.m_Layer[0].m_dwFlag&1){D3DXMatrixIdentity(&uv);_GetCharIF()->SetOverlayTextureMatrix455(uv,true);}
}
void RF455GradeOverlayResources::End455() {
    auto* device=GetD3dDevice();device->LightEnable(0,TRUE);
    device->SetTextureStageState(0,D3DTSS_TEXTURETRANSFORMFLAGS,0);device->SetRenderState(D3DRS_SPECULARENABLE,TRUE);
    BlendOff();device->SetRenderState(D3DRS_ZWRITEENABLE,TRUE);
    device->SetTextureStageState(0,D3DTSS_TEXCOORDINDEX,0);device->SetTextureStageState(0,D3DTSS_TEXTURETRANSFORMFLAGS,0);
}
