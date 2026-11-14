#pragma once
#ifndef RF455_BRIEFING_CONTROLS_H
#define RF455_BRIEFING_CONTROLS_H
#include "userinterface/guicontroller/guicontainer.h"
#include "userinterface/guicontroller/guitext.h"
#include <array>

struct RF455GuiAnimationReplay {
    DWORD (*milliseconds)()=nullptr;
    float (*frameSeconds)()=nullptr;
};
RF455GuiAnimationReplay RF455_SetGuiAnimationReplay(RF455GuiAnimationReplay);

// Named source bridge for the455 animation rules. Legacy0.7 CGUIObjectAni
// callers stay separate until their own layouts/callers are ported.
class RF455GuiAnimatedImage : public CGUIObjectEx {
    float m_frame=0,m_fps=10,m_uvSize[2]={0,0};
    WORD m_total=1,m_columns=1;
    BOOL m_finished=FALSE,m_paused=FALSE,m_loop=TRUE;
    DWORD m_pauseInterval=0,m_pauseTime=0;
    LONG m_uvWidth=0,m_uvHeight=0;
    void SetUV455();
public:
    RF455GuiAnimatedImage(){Reset455();}
    void Reset455();
    void SetImage455(CSprite*,WORD action,WORD frame,bool naturalSize=true);
    bool SetSheet455(BYTE columns,BYTE rows);
    void SetFrame455(WORD frame,BOOL finished=FALSE);
    void SetFPS455(float fps){m_fps=fps;}
    void SetLoop455(BOOL value){m_loop=value;}
    void SetPauseInterval455(DWORD value){m_pauseInterval=value;}
    void SetUVExtent455(LONG width,LONG height){m_uvWidth=width;m_uvHeight=height;}
    void Update() override;
    BOOL Draw() override;
    BOOL Draw(RECT&) override{return Draw();}
    float GetFrame455() const{return m_frame;}
    float GetFPS455() const{return m_fps;}
    WORD GetTotal455() const{return m_total;}
    BOOL IsFinished455() const{return m_finished;}
    BOOL IsPaused455() const{return m_paused;}
    DWORD GetPauseTime455() const{return m_pauseTime;}
};

class CGUIBriefingBoard : public CGUIContainer {
    CGUIObject m_upper,m_lower;
    DWORD m_bodyColor=0,m_borderColor=0;
    BYTE m_borderWidth=1,m_borderInset=1;
public:
    CGUIBriefingBoard();
    void SetCaps455(CSprite* common,BOOL fullWidth);
    void SetColors455(DWORD body,DWORD border){m_bodyColor=body;m_borderColor=border;}
    void SetBorder455(BYTE width,BYTE inset){m_borderWidth=width;m_borderInset=inset;}
    void SetAlpha455(BYTE alpha);
    void SetSize(LONG width,LONG height);
    void SetSize(POINT& value){SetSize(value.x,value.y);}
    BOOL Draw() override;
    BOOL Draw(RECT&) override{return Draw();}
    CGUIObject& GetUpper455(){return m_upper;}
    CGUIObject& GetLower455(){return m_lower;}
    DWORD GetBodyColor455() const{return m_bodyColor;}
    DWORD GetBorderColor455() const{return m_borderColor;}
};

class CGUITutorialKeyBoard : public CGUIContainer {
    struct Row {RF455GuiAnimatedImage first,second;CGUIObject plus;};
    Row m_rows[2];
    CGUIText m_or;
    CSprite* m_tutorial=nullptr;
    bool ConfigureKey455(BYTE key,RF455GuiAnimatedImage&);
public:
    CGUITutorialKeyBoard();
    void SetSprite455(CSprite* tutorial);
    void SetRows455(BYTE count,const std::array<std::array<BYTE,2>,2>&);
    RF455GuiAnimatedImage& GetKey455(unsigned row,unsigned key){return key?m_rows[row].second:m_rows[row].first;}
    CGUIObject& GetPlus455(unsigned row){return m_rows[row].plus;}
    CGUIText& GetOr455(){return m_or;}
};
#endif
