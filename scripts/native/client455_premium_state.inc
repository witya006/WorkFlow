//Selected state portion ofCashShop57/12. The premium window/icon481 and
//post-update condition/UI refresh still require their own ordinary migration.
//This entrypoint does not claim the complete5975C0 handler.
bool CNetworkMgr::DispatchPremiumState455(char* packet,std::size_t bytes){
    RF455PremiumUpdate update;
    if(!RF455_ReadPremiumUpdate(packet,bytes,update))return false;
    if(update.status>2)return true;
    auto* avatar=_GetAvatar();if(!avatar)return false;
    SetPremiumState455(update.status?1u:0u);
    RF455_ApplyPremiumBenefits(update,avatar->PremiumBenefits455());
    return true;
}
