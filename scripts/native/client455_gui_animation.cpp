#include "client455_gui_animation.h"
#include "client455_gui_input.h"
#include "userinterface/spritemgr.h"
#include "commonutil.h"
#include "client455_d3d9_port.h"
#include <cmath>
#include <stdexcept>

namespace {
float defaultLoop(){return R3GetLoopTime();}
RF455GuiAnimationLoopTime loopTime=defaultLoop;
float advance(float frame,float elapsed,float fps){float output;
    __asm {
        fld dword ptr[elapsed]
        fmul dword ptr[fps]
        fadd dword ptr[frame]
        fstp dword ptr[output]
    }return output;
}
void readyDraw(RF455GuiAnimation& object,CSprite* sprite){
    auto* device=GetD3dDevice();if(!device)throw std::logic_error("455 ready animation requires device");
    sprite->SetAction(13);sprite->SetFrame(0);auto* texture=static_cast<IDirect3DBaseTexture9*>(sprite->GetFrameTexture455());
    if(!texture)throw std::runtime_error("455 ready animation texture missing");
    device->SetRenderState(D3DRS_ZENABLE,FALSE);device->SetRenderState(D3DRS_FOGENABLE,FALSE);device->SetRenderState(D3DRS_LIGHTING,FALSE);device->SetRenderState(D3DRS_ALPHABLENDENABLE,TRUE);
    device->SetRenderState(D3DRS_SRCBLEND,D3DBLEND_SRCALPHA);device->SetRenderState(D3DRS_DESTBLEND,D3DBLEND_ONE);
    device->SetTextureStageState(0,D3DTSS_COLORARG1,D3DTA_TEXTURE);device->SetTextureStageState(0,D3DTSS_COLORARG2,D3DTA_DIFFUSE);device->SetTextureStageState(0,D3DTSS_COLOROP,D3DTOP_MODULATE);
    device->SetTextureStageState(0,D3DTSS_ALPHAARG1,D3DTA_TEXTURE);device->SetTextureStageState(0,D3DTSS_ALPHAARG2,D3DTA_DIFFUSE);device->SetTextureStageState(0,D3DTSS_ALPHAOP,D3DTOP_MODULATE);
    device->SetTexture(0,texture);device->SetTextureStageState(1,D3DTSS_COLOROP,D3DTOP_DISABLE);device->SetTextureStageState(1,D3DTSS_ALPHAOP,D3DTOP_DISABLE);
    device->SetSamplerState(0,D3DSAMP_ADDRESSU,D3DTADDRESS_CLAMP);device->SetSamplerState(0,D3DSAMP_ADDRESSV,D3DTADDRESS_CLAMP);
    const float left=static_cast<float>(double(object.GetPosX())-.5),top=static_cast<float>(double(object.GetPosY())-.5);
    const float right=static_cast<float>(double(object.GetPosX())+object.GetSizeX()-.5),bottom=static_cast<float>(double(object.GetPosY())+object.GetSizeY()-.5);const DWORD color=object.GetARGB();const auto* u=object.GetU();const auto* v=object.GetV();
    _D3DR3TLVERTEX_TEX1 vertices[4]={{left,bottom,.1f,.5f,color,u[0],v[1]},{left,top,.1f,.5f,color,u[0],v[0]},{right,bottom,.1f,.5f,color,u[1],v[1]},{right,top,.1f,.5f,color,u[1],v[0]}};
    RF455_SetFixedVertexFormat(device,D3DFVF_XYZRHW|D3DFVF_DIFFUSE|D3DFVF_TEX1);device->DrawPrimitiveUP(D3DPT_TRIANGLESTRIP,2,vertices,28);
    device->SetRenderState(D3DRS_ALPHABLENDENABLE,FALSE);device->SetSamplerState(0,D3DSAMP_ADDRESSU,D3DTADDRESS_WRAP);device->SetSamplerState(0,D3DSAMP_ADDRESSV,D3DTADDRESS_WRAP);device->SetRenderState(D3DRS_ZENABLE,TRUE);
}
}
RF455GuiAnimationLoopTime RF455_SetGuiAnimationLoopTime(RF455GuiAnimationLoopTime provider){auto previous=loopTime;loopTime=provider?provider:defaultLoop;return previous;}
RF455GuiAnimation::RF455GuiAnimation(){Reset455();SetMouseInput455(FALSE);}
void RF455GuiAnimation::Reset455(){state.frame=0;state.totalFrames=1;state.fps=10;state.columns=1;state.paused=0;state.pauseInterval=state.pauseStarted=0;state.stepU=state.stepV=0;state.loop=1;state.cellWidth=state.cellHeight=0;state.blend=0;state.stopped=0;SetUV455(0,1,0,1);readyConfigured=FALSE;}
void RF455GuiAnimation::ConfigureGrid455(WORD originalX,WORD originalY,WORD textureX,WORD textureY,BYTE columns,BYTE rows){
    if(!columns)columns=1;if(!rows)rows=1;state.columns=columns;state.totalFrames=rows*columns;SetSize(originalX/columns,originalY/rows);
    if(textureX&&textureY){state.stepU=static_cast<float>(double(state.cellWidth?state.cellWidth:GetSizeX())/textureX);state.stepV=static_cast<float>(double(state.cellHeight?state.cellHeight:GetSizeY())/textureY);}
}
void RF455GuiAnimation::ConfigureReady455(){
    state.blend=3;state.fps=34;state.cellWidth=state.cellHeight=128;ConfigureGrid455(1024,640,1024,1024,8,5);state.loop=0;SetFrame455(0,TRUE);SetSize(128,128);readyConfigured=TRUE;
}
void RF455GuiAnimation::UpdateUV455(){
    if(!state.columns||!std::isfinite(state.frame)||state.frame>=2147483648.0f||state.frame<-2147483648.0f)throw std::logic_error("455 animation UV conversion outside admitted domain");
    const int index=static_cast<int>(state.frame);const float u=static_cast<float>(double(index%state.columns)*state.stepU),v=static_cast<float>(double(index/state.columns)*state.stepV);SetUV455(u,u+state.stepU,v,v+state.stepV);
}
void RF455GuiAnimation::SetFrame455(WORD frame,BOOL stopped){state.frame=frame;if(state.frame>=state.totalFrames)state.frame=0;UpdateUV455();state.stopped=stopped;}
void RF455GuiAnimation::Update(){
    if(!IsShow()||state.stopped)return;
    if(state.paused){if(RF455_GuiInputTime()-state.pauseStarted>state.pauseInterval)state.paused=0;return;}
    if(state.totalFrames<=1)return;state.frame=advance(state.frame,loopTime(),state.fps);
    if(state.frame>=state.totalFrames){if(state.loop){state.paused=1;state.pauseStarted=RF455_GuiInputTime();state.frame=0;}else{state.frame=state.totalFrames-1;state.stopped=1;}}
    UpdateUV455();
}
BOOL RF455GuiAnimation::Draw(){
    if(!IsShow())return FALSE;if(!readyConfigured||state.blend!=3)throw std::logic_error("455 generic GUI animation draw requires its actual sprite/blend owner");
    auto* sprite=gSpriteMgr.GetTargetSprite455(1);if(!sprite||sprite->GetMaxActions()<=13||!sprite->GetMaxFrames(13)||sprite->GetSpriteOrgXL(13,0)!=1024||sprite->GetSpriteOrgYL(13,0)!=640||sprite->GetSpriteXL(13,0)!=1024||sprite->GetSpriteYL(13,0)!=1024)throw std::runtime_error("455 ready animation sheet geometry missing");
    readyDraw(*this,sprite);return TRUE;
}
BOOL RF455GuiAnimation::Draw(RECT&){throw std::logic_error("455 ready animation clipped draw is not restored");}
