void CGUIMessagebox::Init(WORD style)
{
    SetSprite();
    SetStyle(style);
    m_cBase.SetARGB(0xd8222628);
    m_cUpperOutLine.SetARGB(0xff6a6e72);
    m_cLowerOutLine.SetARGB(0xff6a6e72);
    m_cLeftOutLine.SetARGB(0xff6a6e72);
    m_cRightOutLine.SetARGB(0xff6a6e72);
    RF455_ConfigureModalCaption(m_uiOKButton,106);
    RF455_ConfigureModalCaption(m_uiCancelButton,107);
    SetMoveObject(NULL);
    SetMoveObject(&m_cBase);
    m_dwDuration=0xffffffff;
    m_uiMsgBoard.SetMargin(5,5);
    m_uiMsgBoard.SetColumnGap(4);
    SetWheelScrollObject(&m_uiScrollbar);
}

void CGUIMessagebox::SetSprite(void)
{
    RF455_ConfigureModalButton(m_uiOKButton);
    RF455_ConfigureModalButton(m_uiCancelButton);
    RF455_ConfigureModalButton(m_uiCloseButton,true);
    m_cBase.RemoveSpriteInfo();
    m_cBase.SetARGB(0xd8222628);
    RF455_ConfigureModalScrollbar(m_uiScrollbar);
    // The shared scrollbar/text-board layout/input algorithms are still open.
}

void CGUIMessagebox::SetAlpha(BYTE alpha)
{m_cBase.SetARGB((DWORD(alpha)<<24)|(m_cBase.GetARGB()&0x00ffffff));}

void CGUIMessagebox::SetBound(RECT& bound)
{
    CGUIObject::SetBound(bound);
    const LONG x=m_ptPos.x,y=m_ptPos.y,w=m_ptSize.x,h=m_ptSize.y;
    m_cBase.SetPos(x,y);m_cBase.SetSize(w,h);
    // CGUIOutlineBoard: one-pixel outline, inset by two pixels.
    m_cLeftOutLine.SetPos(x+2,y+2);m_cLeftOutLine.SetSize(1,h-4);
    m_cRightOutLine.SetPos(x+w-3,y+2);m_cRightOutLine.SetSize(1,h-4);
    m_cUpperOutLine.SetPos(x+3,y+2);m_cUpperOutLine.SetSize(w-6,1);
    m_cLowerOutLine.SetPos(x+3,y+h-3);m_cLowerOutLine.SetSize(w-6,1);
    const LONG scroll=IsAddedObject(&m_uiScrollbar)?m_uiScrollbar.GetSizeX():0;
    m_uiMsgBoard.SetPos(x+(w-m_uiMsgBoard.GetSizeX()-scroll)/2,
                       y+(h-m_uiMsgBoard.GetSizeY())/2);
    m_uiScrollbar.SetPos(x+w-m_uiScrollbar.GetSizeX()-15,m_uiMsgBoard.GetPosY());
    const LONG bw=m_uiOKButton.GetSizeX(),bh=m_uiOKButton.GetSizeY();
    if(m_wDlgStyleID==DLG_STYLE_OK_CANCEL){
        m_uiOKButton.SetPos(x+w-(2*bw+14),y+h-bh-7);
        m_uiCancelButton.SetPos(x+w-bw-7,y+h-bh-7);
    }else if(m_wDlgStyleID==DLG_STYLE_OK){
        m_uiOKButton.SetPos(x+w-bw-7,y+h-bh-7);
    }
}

void CGUIMessagebox::Open(void)
{
    CGUIDialogBox::Open();
    RF455_ConfigureModalCaption(m_uiOKButton,106);
    m_uiOKButton.Enable();
    m_dwOpenTime=timeGetTime();
    if(GetStyleID()!=DLG_STYLE_NONE)PlayWave(SND_ID_WINDOW_OPEN);
}
