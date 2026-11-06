#include "client455_gui_text_typing_board.h"
#include "client455_language.h"
#include <stdexcept>

namespace {
RF455TextTypingClock clockProvider=nullptr;
DWORD now(){return clockProvider?clockProvider():timeGetTime();}
}
RF455TextTypingClock RF455_SetTextTypingClock(RF455TextTypingClock provider){
    const auto previous=clockProvider;clockProvider=provider;return previous;
}
bool CGUITextTypingBoard::StartTyping455(int firstLine,int lastLine,DWORD delay){
    // Target tests signed ints before storing WORDs. Negative accepted ranges
    // lead to invalid marker/pointer reads; keep that unsupported domain explicit.
    if(lastLine>=GetTotalLineNum()||lastLine<firstLine)return false;
    if(firstLine<0||lastLine<0)throw std::invalid_argument("455 typing negative line domain is not established");
    m_firstLine=static_cast<WORD>(firstLine);m_lastLine=static_cast<WORD>(lastLine);
    m_fragment=m_offset=0xffff;m_startTime=now()+delay;m_previousTime=0;
    m_running=TRUE;m_finished=FALSE;return true;
}
void CGUITextTypingBoard::FinishTyping455(){
    // Target retains the previous cursor if the requested end marker is absent.
    GetLineEnd455(m_lastLine,m_fragment,m_offset);m_finished=TRUE;
}
void CGUITextTypingBoard::Clear(){
    m_fragment=m_offset=0xffff;CGUITextBoard::Clear();
    // Running/finished/timers intentionally survive target647BD0.
}
void CGUITextTypingBoard::Update(){
    if(!IsShow()||!m_running||m_finished)return;
    const DWORD time=now();if(time<m_startTime)return;
    if(!m_previousTime){m_previousTime=time;return;}
    if(time-m_previousTime<m_interval)return;
    WORD endFragment=0,endOffset=0;
    if(!GetLineEnd455(m_lastLine,endFragment,endOffset))
        throw std::logic_error("455 typing range no longer has an end marker");
    auto* language=RF455_GetNormalLanguagePack();
    if(!language)throw std::logic_error("455 typing requires the resource language classifier");
    // These are absolute DWORD comparisons/additions, not a replacement using
    // elapsed/interval division; their wrap and space-skip quirks are observable.
    while(m_previousTime+m_interval<=time){
        const char* text=nullptr;
        if(m_fragment==0xffff||m_offset==0xffff){
            if(!GetLineStart455(m_firstLine,m_fragment,m_offset))
                throw std::logic_error("455 typing range no longer has a start marker");
            auto* info=GetFragment455(m_fragment);if(!info)return;
            text=info->GetText();if(language->isLead(text,m_offset))++m_offset;
        }else {
            auto* info=GetFragment455(m_fragment);if(!info||!info->GetText())return;
            text=info->GetText();
            m_offset=static_cast<WORD>(m_offset+(language->isLead(text,m_offset)?2:1));
            if(m_offset>=info->GetLength455()){++m_fragment;m_offset=0;}
        }
        if(m_fragment>endFragment||(m_fragment==endFragment&&m_offset>=endOffset)){
            m_finished=TRUE;return;
        }
        // The target still indexes the previous fragment after crossing into
        // the next one. Preserve that rule within the valid stored-string range.
        if(!text||text[m_offset]!=' ')m_previousTime+=m_interval;
    }
}
BOOL CGUITextTypingBoard::Draw(){
    if(!IsShow())return FALSE;
    // Target60CAC0 draws child objects but does not paint the object's own fill.
    for(auto* child:m_listObject)child->Draw();
    if(!GetFragmentCount455()||m_fragment==0xffff||m_offset==0xffff)return TRUE;
    int visible=VisibleLines(),total=GetTotalLineNum();
    const int blank=GetAutoScroll455()&&visible>total?visible-total:0;
    const int x=m_ptPos.x+GetMarginX();int y=m_ptPos.y+GetMarginY()+blank*Stride();
    const WORD viewed=GetViewedLine455();if(visible+viewed>total)visible=total-viewed;
    for(int i=0;i<visible;++i){
        const WORD line=static_cast<WORD>(i+viewed);WORD fragment=0,offset=0;
        if(!GetLineEnd455(line,fragment,offset))return TRUE;
        if(fragment>m_fragment||(fragment==m_fragment&&offset>=m_offset)){
            if(GetLineStart455(line,fragment,offset)&&
               (fragment<m_fragment||(fragment==m_fragment&&offset<m_offset)))
                DrawLineTo455(line,x,y,m_fragment,m_offset,255);
            return TRUE;
        }
        DrawLine(line,x,y,255);y+=Stride();
    }
    return TRUE;
}
