LRESULT CGUIDialogBox::MsgProc(HWND window,UINT message,WPARAM value,LPARAM parameter)
{
    if(!m_listDialogBox.empty())return m_listDialogBox.back()->MsgProc(window,message,value,parameter);
    if(!IsActive())return 0;
    if(message==WM_KEYDOWN&&value==VK_RETURN){
        m_wResultMsg=MSG_OK;SendDialogBoxEvent(DLG_BOX_CLOSED);return 1;
    }
    if(message==WM_CHAR){
        if(value==VK_ESCAPE){
            if(!m_allowClose455)return 0;
            m_wResultMsg=MSG_CLOSE;SendDialogBoxEvent(DLG_BOX_CLOSED);return 1;
        }
        if(m_wDlgStyleID==DLG_STYLE_OK_CANCEL&&!RF455_ModalChatInputFocused()){
            if(value=='y'||value=='Y'){
                m_wResultMsg=MSG_OK;SendDialogBoxEvent(DLG_BOX_CLOSED);return 1;
            }
            if(value=='n'||value=='N'){
                m_wResultMsg=MSG_CANCEL;SendDialogBoxEvent(DLG_BOX_CLOSED);return 1;
            }
        }
    }
    CGUIContainer::MsgProc(window,message,value,parameter);
    return 1;
}
