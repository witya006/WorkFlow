BOOL CNetworkMgr::SystemMsg_RegedCharRequest_zone( void )
{
    BYTE type[2]={1,8};const BOOL sent=SendNetMessage(0,type,nullptr,0);
    if(sent)SendRequestMsg();else NetLogWrite("455 registered-character request failed");return sent;
}

void CNetworkMgr::SystemMsg_RegedCharResult_zone( char* packet )
{
    RF455RegisteredCharacters reply;
    if(!RF455_ReadRegisteredCharacters(packet,RF455RegisteredCharactersBytes,reply))return;
    m_registered455=reply;m_byResultOfUserInfo=reply.result;
    std::int64_t latest=0;
    static const BYTE parts[8]={1,2,3,4,5,7,6,8};
    for(unsigned i=0;i<reply.count;++i){auto& row=reply.records[i];if(row.slot>2)continue;
        auto* avatar=_GetAvatarDummy(row.slot);if(!avatar)continue;
        avatar->SetIndex(row.slot);avatar->SetObjectTypeID(OTI_CHAR);avatar->SetCharTypeID(CTI_AVATAR);
        avatar->SetName(row.name);avatar->SetClassDTIndexByStrDTCode(0,row.classCode);
        avatar->SetRace(row.race);avatar->SetBone(row.race);avatar->SetDTIndex(row.race);
        avatar->SetSkipTutorial455(row.level?1:0);avatar->SetLevel(row.level?row.level:1);
        avatar->SetDalant(row.dalant);avatar->SetGold(row.gold);
        for(unsigned j=0;j<5;++j)avatar->SetDefaultItem(parts[j],((row.baseShape>>(4*j))&15)+16*row.race);
        for(unsigned j=0;j<8;++j){
            if(row.equipment[j]==-1){
                if(j<5){auto* item=avatar->GetDefaultItem(parts[j]);if(item)avatar->PutOnEquipment(parts[j],item->GetDTIndex());}
                else avatar->PutOffEquipment(parts[j]);
            }else{
                avatar->PutOnEquipment(parts[j],static_cast<DWORD>(row.equipment[j]));
                auto* item=avatar->GetNormalItem(parts[j]);if(item)item->SetLevel(row.upgrade[j]);
            }
        }
        avatar->PutOnEquipment(0,((row.baseShape>>20)&15)+16*row.race);
        auto* helmet=avatar->GetDefaultItem(5);if(helmet)avatar->PutOnEquipment(10,helmet->GetDTIndex());
        avatar->SetAction(0x10000000,TRUE);avatar->SetLightColor(0xff808080);
        if(latest<row.lastConnection){m_dwLastestAvatarIndex=row.slot;latest=row.lastConnection;}
    }
    ReceiveResponseMsg();
}

bool CNetworkMgr::DispatchRegisteredCharacters455(char* packet,std::size_t bytes)
{
    RF455RegisteredCharacters parsed;
    if(!RF455_ReadRegisteredCharacters(packet,bytes,parsed))return false;
    SystemMsg_RegedCharResult_zone(packet);return true;
}
