#pragma once
#include "userinterface/guicontroller/guitextboard.h"

typedef DWORD (*RF455TextTypingClock)();
RF455TextTypingClock RF455_SetTextTypingClock(RF455TextTypingClock);

// Source-owned implementation, not the target's244-byte private object layout.
class CGUITextTypingBoard : public CGUITextBoard {
    WORD m_interval=100;
    BOOL m_running=FALSE,m_finished=FALSE;
    DWORD m_startTime=0,m_previousTime=0;
    WORD m_firstLine=0,m_lastLine=0,m_fragment=0xffff,m_offset=0xffff;
public:
    bool StartTyping455(int firstLine,int lastLine,DWORD delay=0);
    void FinishTyping455();
    void Clear() override;
    void Update() override;
    BOOL Draw() override;
    BOOL Draw(RECT&) override{return Draw();}
    void SetTypingInterval455(WORD interval){m_interval=interval;}
    BOOL IsTypingFinished455() const{return m_finished;}
    BOOL IsTypingRunning455() const{return m_running;}
    WORD GetTypingFragment455() const{return m_fragment;}
    WORD GetTypingOffset455() const{return m_offset;}
    DWORD GetTypingPreviousTime455() const{return m_previousTime;}
    DWORD GetTypingStartTime455() const{return m_startTime;}
    int GetVisibleLines455() const{return VisibleLines();}
};
