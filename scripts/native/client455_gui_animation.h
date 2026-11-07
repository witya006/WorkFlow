#pragma once
#include "userinterface/guicontroller/guiobject.h"

struct RF455GuiAnimationState {
    float frame;
    WORD totalFrames;
    BOOL stopped;
    float fps;
    WORD columns;
    BOOL paused;
    DWORD pauseInterval,pauseStarted;
    float stepU,stepV;
    BOOL loop;
    LONG cellWidth,cellHeight;
    BYTE blend;
};
using RF455GuiAnimationLoopTime=float(*)();
RF455GuiAnimationLoopTime RF455_SetGuiAnimationLoopTime(RF455GuiAnimationLoopTime);

// Source-owned selected animation state;not the target private200-byte ABI.
class RF455GuiAnimation:public CGUIObjectEx {
    RF455GuiAnimationState state;
    BOOL readyConfigured=FALSE;
    void UpdateUV455();
public:
    RF455GuiAnimation();
    RF455GuiAnimationState& State455(){return state;}
    const RF455GuiAnimationState& State455()const{return state;}
    void Reset455();
    void SetUV455(float u0,float u1,float v0,float v1){m_fSpriteUV[0][0]=u0;m_fSpriteUV[0][1]=u1;m_fSpriteUV[1][0]=v0;m_fSpriteUV[1][1]=v1;}
    void ConfigureGrid455(WORD,WORD,WORD,WORD,BYTE,BYTE);
    void ConfigureReady455();
    BOOL ReadyConfigured455()const{return readyConfigured;}
    void SetFrame455(WORD,BOOL stopped);
    void Update()override;
    BOOL Draw()override;
    BOOL Draw(RECT&)override;
};
