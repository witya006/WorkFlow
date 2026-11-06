void CGUIObject::EventProcess(){
    for(int i=0;i<s_qEventList.GetCurNum();++i){
        auto* queued=&s_qEventList[i];const WORD id=queued->wEventID;
        if(id<10){_mouse_event event={queued->pSource,id,queued->nPosX,queued->nPosY};static_cast<IMouseObserver*>(queued->pEventHandler)->MouseEvent(event);}
        else if(id<20){_mouse_motion_event event={queued->pSource,id,queued->nPosX,queued->nPosY,queued->nMoveX,queued->nMoveY};static_cast<IMouseMotionObserver*>(queued->pEventHandler)->MouseMotionEvent(event);}
        else if(id<30){_key_event event={queued->pSource,id,queued->byKeyCode};static_cast<IKeyObserver*>(queued->pEventHandler)->KeyEvent(event);}
        else if(id<40){_scroll_event event={queued->pSource,id};static_cast<IScrollObserver*>(queued->pEventHandler)->ScrollEvent(event);}
        else if(id<50){_select_event event={queued->pSource,id,queued->wSelectIndex};static_cast<ISelectItemObserver*>(queued->pEventHandler)->SelectItemEvent(event);}
        else if(id<60){if(id==DLG_BOX_CLOSED)static_cast<CGUIWindow*>(queued->pEventHandler)->ClosingDialogBox(static_cast<CGUIDialogBox*>(queued->pSource));}
        else if(id<70){auto* window=static_cast<CGUIWindow*>(queued->pEventHandler);if(id==WINDOW_OPENED)window->Open();else if(id==WINDOW_CLOSED)window->Close();}
        else if(id<80){_focus_event455 event={queued->pSource,id};static_cast<IFocusObserver455*>(queued->pEventHandler)->FocusEvent455(event);}
        else if(id<90){_value_event455 event={queued->pSource,id,queued->nValue455};static_cast<IValueObserver455*>(queued->pEventHandler)->ValueEvent455(event);}
    }
    s_qEventList.Clear();
}
