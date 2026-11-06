#include "client455_text_metrics.h"
#include <stdexcept>

void CGUIMessagebox::SetSize(LONG width,LONG height)
{
    // Legacy callers expose SetBound. The target vtable slot12 takes width/height.
    RECT bound={m_ptPos.x,m_ptPos.y,m_ptPos.x+width,m_ptPos.y+height};
    SetBound(bound);
}

void CGUIMessagebox::SetMsg(char* message,BOOL formatted455)
{
    // Target701870 returns before clearing/changing anything for a null pointer.
    if(!message)return;
    FONT_INFO font;font.dwColor=0xffe3e0d9;
    m_uiMsgBoard.Clear();
    if(formatted455)m_uiMsgBoard.InsertFormatted455(message,&font);
    else m_uiMsgBoard.InsertText(message,&font);
    // Target643D30 reads an uninitialized newline local when its list is empty.
    // Keep that undefined sizing domain explicit rather than inventing a size.
    if(!m_uiMsgBoard.ResizeToText455())
        throw std::invalid_argument("455 modal empty fragment extent is not established");

    if(m_bScrollable){
        LONG width=m_uiMsgBoard.GetSizeX(),height=m_uiMsgBoard.GetSizeY();
        if(width<=0){
            width=m_uiMsgBoard.GetSizeX()+2*m_uiMsgBoard.GetMarginX();
            if(width>300)width=300;
        }
        const LONG required=m_uiMsgBoard.GetTotalLineNum()*
            (RF455_DefaultTextHeight()+m_uiMsgBoard.GetColumnGap())+2*m_uiMsgBoard.GetMarginY();
        if(height<=0){height=required;if(height>250)height=250;}
        m_uiMsgBoard.SetSize(width,height);
        if(height<required){
            Add(&m_uiScrollbar);
            m_uiScrollbar.SetSize(m_uiScrollbar.GetSizeX(),m_uiMsgBoard.GetSizeY());
            m_uiMsgBoard.AddScrollbar(&m_uiScrollbar);
        }
    }
    const BOOL scrollbar=IsAddedObject(&m_uiScrollbar);
    LONG width=m_uiMsgBoard.GetSizeX()+(scrollbar?m_uiScrollbar.GetSizeX()+60:30);
    LONG height=m_uiMsgBoard.GetSizeY()+m_uiOKButton.GetSizeY()+(scrollbar?45:30);
    if(width<200)width=200;if(height<100)height=100;
    SetSize(width,height);
}
