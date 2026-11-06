#ifndef __GUITEXTBOARD_H__
#define __GUITEXTBOARD_H__
#include "GUIContainer.h"
#include "GUIScrollbar.h"
#include "GUIText.h"
#include <deque>
#include <memory>

typedef std::deque<CGUITextInfo*> GUITextList;

// Source-owned API for the BYTE capacity contract at target7B1F40.
void RF455_CopyGuiTextBytes8(char* destination,const char* source,unsigned capacity);
bool RF455_ParseFontTag(const char* tag,FONT_INFO& font);
bool RF455_IsClosingFontTag(const char* tag);

class CGUITextBoard : public CGUIContainer, public IScrollObserver {
    struct Line {WORD fragment,offset;};
    std::deque<std::unique_ptr<CGUITextInfo>> m_fragments;
    std::deque<Line> m_lines;
    WORD m_limit=1000,m_fragmentBase=0,m_gap=0,m_viewed=0;
    POINT m_margin={0,0};
    CGUIScrollbar* m_scrollbar=nullptr;
    BOOL m_autoScroll=FALSE,m_highlight=FALSE;
    DWORD m_highlightColor=0xffffffff;

    void Layout(bool append);
    void AddLine(WORD fragment,WORD offset);
    void SetViewed(WORD line);
    void InsertFragment(char* text,FONT_INFO* font,BOOL adjustView);
protected:
    int VisibleLines() const;
    int Stride() const;
    BOOL DrawLine(WORD line,int x,int y,BYTE alpha);
    BOOL DrawLineTo455(WORD line,int x,int y,WORD lastFragment,WORD lastOffset,BYTE alpha);
public:
    CGUITextBoard();
    ~CGUITextBoard();
    void SetLimitLineNum(DWORD lines){m_limit=static_cast<WORD>(lines);}
    void SetMargin(int x,int y);
    void SetColumnGap(int gap);
    void SetAutoScroll(BOOL enabled){m_autoScroll=enabled;}
    BOOL GetAutoScroll455() const{return m_autoScroll;}
    int GetMarginX(){return m_margin.x;}
    int GetMarginY(){return m_margin.y;}
    int GetColumnGap(){return m_gap;}
    void AddScrollbar(CGUIScrollbar* scrollbar);
    void SetBound(RECT& bound);
    void SetSize(LONG width,LONG height);
    void SetSize(POINT& size){SetSize(size.x,size.y);}
    virtual void Clear();
    void InsertText(char* text);
    void InsertText(char* text,FONT_INFO* font);
    void InsertText(CGUITextInfo* text,BOOL adjustView=FALSE);
    int GetTotalLineNum(){return static_cast<int>(m_lines.size());}
    BOOL Draw();
    BOOL Draw(RECT& clipping);
    void ScrollEvent(_scroll_event& event);

    // Named source interfaces for the target's additional TextBoard operations.
    void InsertFormatted455(char* text,FONT_INFO* font);
    void ReplaceFormatted455(char* text,FONT_INFO* font){Clear();InsertFormatted455(text,font);}
    bool ResizeToText455();
    void ScrollToBottom455();
    void SetViewedLine455(WORD line){SetViewed(line);}
    WORD GetViewedLine455() const{return m_viewed;}
    WORD GetFragmentBase455() const{return m_fragmentBase;}
    unsigned GetFragmentCount455() const{return static_cast<unsigned>(m_fragments.size());}
    CGUITextInfo* GetFragment455(unsigned index) const{return index<m_fragments.size()?m_fragments[index].get():nullptr;}
    bool GetLineStart455(WORD line,WORD& fragment,WORD& offset) const;
    bool GetLineEnd455(WORD line,WORD& fragment,WORD& offset) const;
    void SetHighlight455(BOOL enabled,DWORD color){m_highlight=enabled;m_highlightColor=color;}
};
#endif
