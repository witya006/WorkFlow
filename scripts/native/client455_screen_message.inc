LRESULT CGUIScreen::MsgProc(HWND window,UINT message,WPARAM source,LPARAM value){
    if(!IsShow())return 1;
    for(auto it=m_listDialogBox.rbegin();it!=m_listDialogBox.rend();++it)
        if((*it)->MsgProc(window,message,source,value))return 1;
    if(IsCaptureVisible455())m_capture455->MsgProc(window,message,source,value);
    else for(auto* object:m_listObject){auto* child=static_cast<CGUIWindow*>(object);
        if(child->IsShow()&&child->MsgProc(window,message,source,value))break;}
    return 1;
}
