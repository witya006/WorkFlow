BOOL SetDisapearTimeEffect(DWORD unique_id,float time){
    for(DWORD i=0;i<stELcnt;++i){
        auto& effect=stEffectList[i];if(effect.mUniqueID!=unique_id)continue;
        effect.mState=_EF_STATE_START_DISAPEAR;effect.mDisapearTime=time;effect.mDisapearFrame=effect.mFrame;
        if(time<=0){
            if(effect.mFlag&_MT_FLAG_PARTICLE){
                auto* particle=effect.mParticle;
                if(time<0){
                    if(particle){particle->ReleaseParticle();delete particle;effect.mParticle=NULL;}
                    DeleteEffectList(i);
                }else{
                    particle->SetParticleState(0);particle->SetParticleAttr(particle->GetParticleAttr()|_PARTICLE_ATTR_NO_LOOP);
                }
            }else DeleteEffectList(i);
        }
        return TRUE;
    }
    return FALSE;
}
