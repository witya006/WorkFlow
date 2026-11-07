DWORD CLinkBoard::HotbarReference455(CBoardObject* object){
    if(!object)return RF455_EMPTY_HOTBAR_REFERENCE;
    if(auto* shared=object->GetItem455()){
        if(shared->header().kind==0)return RF455_EncodeHotbarReference(0,0,0,object->GetServerIndex());
        if(auto* sf=dynamic_cast<RF455SkillForceItem*>(shared))return RF455_EncodeHotbarReference(1,sf->record().subtype,sf->tableIndex(),0);
        if(shared->header().kind==2)if(auto* item=dynamic_cast<RF455BasicItem*>(shared))return RF455_EncodeHotbarReference(2,0,item->tableIndex(),0);
        return RF455_EMPTY_HOTBAR_REFERENCE;
    }
    if(auto* item=dynamic_cast<CBoardItem*>(object))
        return RF455_EncodeHotbarReference(0,0,0,item->GetServerIndex());
    if(auto* item=dynamic_cast<CSFItem*>(object))
        return RF455_EncodeHotbarReference(1,item->GetSFType(),item->GetDTIndex(),0);
    if(auto* item=dynamic_cast<CAnimusItem*>(object))
        return RF455_EncodeHotbarReference(2,0,item->GetDTIndex(),0);
    // Gesture/Macro owners are not in the current source registry. Their real
    // providers remain required;the pure encoder already covers target tags.
    return RF455_EMPTY_HOTBAR_REFERENCE;
}
RF455HotbarSnapshot CLinkBoard::CaptureHotbar455(){
    RF455HotbarSnapshot snapshot;
    for(BYTE bank=0;bank<5;++bank)for(BYTE slot=0;slot<10;++slot)
        snapshot[10*bank+slot]=HotbarReference455(GetObject(bank,slot));
    return snapshot;
}
void CLinkBoard::ResetHotbarUpload455(){m_hotbarDelta455.reset(CaptureHotbar455());m_hotbarUploadTime455=0;}
BOOL CLinkBoard::UploadHotbar455(){
    auto* hover=_GetGBM()->GetHoverObject();
    auto packet=m_hotbarDelta455.prepare(CaptureHotbar455(),m_uiLinkWindow.HotbarState455().packed(),
        hover!=nullptr,_GetGBM()->GetOrgBoardType(),HotbarReference455(hover));
    if(packet.empty())return FALSE;
    if(!_GetNetworkMgr())throw std::logic_error("455 hotbar upload requires the actual network owner");
    // Target58A6C0/57EAC0 uses group13/op17 and client0. Legacy item_msg is7;
    // changing that global would mislabel other unrecovered legacy packets.
    BYTE type[2]={13,17};
    return _GetNetworkMgr()->SendNetMessage(0,type,packet.data(),static_cast<int>(packet.size()));
}
