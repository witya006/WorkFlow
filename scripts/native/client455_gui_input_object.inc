CGUIObject* CGUIObject::s_pRightPressed455=nullptr;
CGUIObject* CGUIObject::s_pMouseModal455=nullptr;
CGUIObject* CGUIObject::s_pLastClick455=nullptr;
DWORD CGUIObject::s_lastClickTime455=0;

void CGUIObject::SetMouseModal455(CGUIObject* object){if(s_pMouseModal455)s_pMouseModal455->CloseMouseModal455();s_pMouseModal455=object;}
BOOL CGUIObject::InputProc(){
    if(s_pMouseDetectedObject||!IsCrossed(gMouseDev.GetX(),gMouseDev.GetY())||!m_mouseInput455)return FALSE;
    s_pMouseDetectedObject=this;
    if(!s_pPrevMouseDetectedObject)s_pPrevMouseDetectedObject=this;
    else if(s_pPrevMouseDetectedObject!=this){
        if(IS_HOVERED(s_pPrevMouseDetectedObject->GetState())){s_pPrevMouseDetectedObject->SetState(s_pPrevMouseDetectedObject->GetState()&~HOVERED);s_pPrevMouseDetectedObject->SendMouseEvent(MOUSE_LEAVED);}
        s_pPrevMouseDetectedObject=this;
    }
    if(s_pPressedObject&&s_pPressedObject!=this){
        if(IS_PRESSED(s_pPressedObject->GetState())){
            if(!gMouseDev.IsPressed(L_BUTTON)||gMouseDev.IsReleased(L_BUTTON)){s_pPressedObject->SetState(s_pPressedObject->GetState()&~PRESSED);s_pPressedObject->SendMouseEvent(MOUSE_RELEASED);s_pPressedObject=nullptr;}
            else if(gMouseDev.IsPressed(L_BUTTON)&&gMouseDev.IsDragged())s_pPressedObject->SendMouseMotionEvent(MOUSE_DRAG);
        }
    }else if(s_bIsPressedOtherObject){if(gMouseDev.IsPressed(L_BUTTON))return TRUE;s_bIsPressedOtherObject=FALSE;}
    if(gMouseDev.IsStroked(R_BUTTON)){
        if(!gMouseDev.IsPressed(L_BUTTON))SendMouseEvent(LMOUSE_STROKED);
        s_pRightPressed455=this;s_pLastClick455=nullptr;
    }else if(!gMouseDev.IsPressed(R_BUTTON))s_pRightPressed455=nullptr;
    if(!IS_PRESSED(m_wState)&&gMouseDev.IsStroked(L_BUTTON)){
        if(!s_pMouseModal455||s_pMouseModal455->IsCrossed(gMouseDev.GetX(),gMouseDev.GetY())){
            if(!s_pPressedObject){
                SetState(m_wState|PRESSED|HOVERED);
                if(s_pLastClick455==this&&RF455_GuiInputTime()-s_lastClickTime455<=300){SendMouseEvent(MOUSE_DOUBLE_STROKED);s_pLastClick455=nullptr;}
                else{SendMouseEvent(MOUSE_STROKED);s_pLastClick455=this;}
                s_lastClickTime455=RF455_GuiInputTime();s_pPressedObject=this;
            }
        }else s_pMouseModal455->CloseMouseModal455();
    }else if(IS_PRESSED(m_wState)&&gMouseDev.IsPressed(L_BUTTON)){
        if(!IS_HOVERED(m_wState))SetState(m_wState|HOVERED);
        SendMouseEvent(MOUSE_PRESSED);if(gMouseDev.IsDragged())SendMouseMotionEvent(MOUSE_DRAG);
    }else if(!gMouseDev.IsPressed(L_BUTTON)&&!gMouseDev.IsPressed(R_BUTTON)){
        if(!IS_HOVERED(m_wState)&&IS_PRESSED(m_wState)){SetState((m_wState&~(PRESSED|HOVERED))|HOVERED);SendMouseEvent(MOUSE_CLICKED);s_pPressedObject=nullptr;}
        else if(!IS_HOVERED(m_wState)){SetState(HOVERED);SendMouseEvent(MOUSE_HOVERED);}
        else if(IS_PRESSED(m_wState)){SetState(m_wState&~PRESSED);SendMouseEvent(MOUSE_CLICKED);s_pPressedObject=nullptr;}
        if(gMouseDev.IsMoved())SendMouseMotionEvent(MOUSE_MOVE);
    }
    return TRUE;
}
void CGUIObject::SendMouseEvent(WORD id){
    if(id==MOUSE_LEAVED||id==MOUSE_STROKED||id==LMOUSE_STROKED)gScreen.RemoveTooltip();
    if(IS_DISABLED(m_wState)&&id!=MOUSE_HOVERED&&id!=MOUSE_LEAVED)return;
    if(m_pMouseObserver){_event_queue_data event;event.pEventHandler=m_pMouseObserver;event.pSource=this;event.wEventID=id;event.nPosX=gMouse.x;event.nPosY=gMouse.y;SendEvent(event);}
}
void CGUIObject::SendMouseMotionEvent(WORD id){
    if(IS_DISABLED(m_wState)||!m_pMouseMotionObserver)return;
    _event_queue_data event;event.pEventHandler=m_pMouseMotionObserver;event.pSource=this;event.wEventID=id;
    event.nPosX=gMouse.x;event.nPosY=gMouse.y;event.nMoveX=gMouseDev.GetMoveX();event.nMoveY=gMouseDev.GetMoveY();SendEvent(event);
}
LRESULT CGUIObject::MsgProc(HWND,UINT message,WPARAM key,LPARAM flags){
    if(!IsFocused455())return 0;
    if((message==WM_KEYDOWN||message==WM_CHAR)&&!(RF455_GuiKeyState(VK_CONTROL)&0x8000)&&!(RF455_GuiKeyState(VK_MENU)&0x8000)&&m_pKeyObserver){
        _event_queue_data event;event.pEventHandler=m_pKeyObserver;event.pSource=this;event.wEventID=KEY_STROKED;
        event.byKeyCode=key==229?RF455_ProcessKeyScan(flags):static_cast<BYTE>(key);SendEvent(event);
    }
    return 1;
}
void CGUIObject::SendFocusEvent455(WORD id){if(m_focusObserver455){_event_queue_data event;event.pEventHandler=m_focusObserver455;event.pSource=this;event.wEventID=id;SendEvent(event);}}
BOOL CGUIObject::TryFocus455(){
    if(IsFocused455())return TRUE;
    if(s_pFocusedObject&&s_pFocusedObject!=this)s_pFocusedObject->SendFocusEvent455(FOCUS_RELEASED455);
    if(!m_bEnableFocus||!m_bActive||!m_bShow||IS_DISABLED(m_wState))return FALSE;
    s_pFocusedObject=this;SendFocusEvent455(FOCUS_ACQUIRED455);return TRUE;
}
void CGUIObject::KillFocus455(){if(IsFocused455()){SendFocusEvent455(FOCUS_RELEASED455);s_pFocusedObject=nullptr;}}
void CGUIObject::InActive(){if(s_pFocusedObject==this)KillFocus455();m_bActive=FALSE;}
void CGUIObject::DisableFocus(){if(s_pFocusedObject==this)KillFocus455();m_bEnableFocus=FALSE;}
