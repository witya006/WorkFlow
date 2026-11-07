// Separate target-ID registry while old callers still use their0.7 group IDs.
CSprite* CSpriteMgr::GetTargetSprite455(unsigned id){
    if(id>=55)return nullptr;
    if(m_targetSprites455[id])return m_targetSprites455[id];
    char path[260];if(!RF455_SelectSpritePath(id,path,sizeof(path)))return nullptr;
    // Preserve actual file-loading failure;no fabricated image/provider.
    if(_access(path,0)!=0)return nullptr;
    auto* sprite=new CSprite;sprite->LoadSprite(path);
    if(!sprite->GetMaxActions()){sprite->ReleaseSprite();delete sprite;return nullptr;}
    m_targetSprites455[id]=sprite;return sprite;
}
void CSpriteMgr::UnloadTargetSprites455(){
    for(auto*& sprite:m_targetSprites455)if(sprite){sprite->ReleaseSprite();delete sprite;sprite=nullptr;}
}
