namespace {
bool itemTableFile455(const char* name,RF455RawItemTable& output){
    std::vector<unsigned char> raw,plain;
    if(!read(name,raw)||!RF455_DecodeEdf(raw.data(),raw.size(),plain)||plain.size()<8)return false;
    RF455RawItemTable next;std::memcpy(&next.count,plain.data(),4);std::memcpy(&next.stride,plain.data()+4,4);
    if(next.count&&next.stride){
        if(next.count>(plain.size()-8)/next.stride)return false;
        const auto bytes=std::size_t(next.count)*next.stride;next.bytes.assign(plain.begin()+8,plain.begin()+8+bytes);
    }
    output=std::move(next);return true;
}
}
bool RF455ClientItems::loadCashFiles(std::int32_t selector){
    if(cashInitialized)throw std::logic_error("455 cash table reload lifetime remains unported");
    const auto* nation=RF455_GetNormalNationPaths();if(!nation->configured)return false;
    const auto paths=RF455_ItemCashPaths(nation->folder,selector);
    // The target keeps its base table even when the localized count mismatches.
    if(!itemTableFile455(paths.data.c_str(),cash))return false;cashInitialized=true;
    std::vector<unsigned char> raw,plain;
    if(!read(paths.names.c_str(),raw)||!RF455_DecodeEdf(raw.data(),raw.size(),plain)||plain.size()<8)return false;
    std::uint32_t count;std::memcpy(&count,plain.data(),4);
    if(count!=cash.count||count>(plain.size()-8)/4||(count&&cash.stride<20))return false;
    for(std::uint32_t i=0;i<count;++i)std::memcpy(cash.bytes.data()+std::size_t(i)*cash.stride+16,plain.data()+8+4*i,4);
    return true;
}
bool RF455ClientItems::loadSetEffectFile(){
    if(setEffectInitialized)throw std::logic_error("455 set-effect reload lifetime remains unported");
    if(!itemTableFile455(".\\DataTable\\ItemSetEffect.edf",setEffect))return false;
    setEffectInitialized=true;return true;
}
bool RF455ClientItems::loadItemFiles(){
    const auto* nation=RF455_GetNormalNationPaths();if(!nation->configured)return false;
    std::vector<unsigned char> raw;
    // All11 pinned country vslot160 implementations return1, including Korea.
    if(!read(".\\DataTable\\Item.edf",raw)||!data.loadItemEdf(raw.data(),raw.size(),true))return false;
    const std::string names=std::string(nation->dataRoot)+"\\NDItem.edf";
    return read(names.c_str(),raw)&&data.localizeItemEdf(raw.data(),raw.size());
}
