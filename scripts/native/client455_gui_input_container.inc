void CGUIContainer::Add(CGUIObject* object){
    if(!object||IsAddedObject(object))return;object->Show(IsShow());m_listObject.push_back(object);
}
void CGUIContainer::AddFront455(CGUIObject* object){
    if(!object||IsAddedObject(object))return;object->Show(IsShow());m_listObject.push_front(object);
}
BOOL CGUIContainer::Remove(CGUIObject* object){
    if(!object)return FALSE;
    if(s_pFocusedObject==object)object->KillFocus455();
    m_listObject.remove(object);return TRUE;
}
void CGUIContainer::RemoveAll(){
    if(s_pFocusedObject&&s_pFocusedObject->IsFocused455()&&IsAddedObject(s_pFocusedObject))s_pFocusedObject->KillFocus455();
    m_listObject.clear();
}
