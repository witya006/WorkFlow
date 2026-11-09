namespace {
WORD effectQuality455=2; // pinned PE initial WORD at RVA7ddcac
bool qualityFamily455(DWORD id){
    if((id>>20)!=287)return false;
    switch(id<<20){
    case 369098752:case 370147328:case 371195904:case 385875968:
    case 520093696:case 521142272:case 0x20000000:return true;
    default:return false;
    }
}
bool forcedEffect455(DWORD id){return id>=301928452&&id<=301928456;}
bool additionalEffect455(DWORD id){return id==301400449||id==301531522||id==301203843;}
bool highEffect455(DWORD id){return id>0xf0000000u&&id<0xffffff00u;}
}
WORD GetEffectQuality455(){return effectQuality455;}
void ApplyEffectOption455(BOOL enable,WORD option){
    // The 455 R3-state option producer/UI caller remains a separate migration;
    // the actual scheduling owner receives its low WORD explicitly here.
    effectQuality455=enable==1?(option==0?0:option==3?1:2):2;
    if(effectQuality455>1||!stMLcnt)return;
    for(DWORD i=0;i<stMLcnt;++i){
        DWORD id=stMagicList[i].mMagicID;
        if(id==1358041392||id==1358041648||id==1358041136||id==1358041904
           ||forcedEffect455(id)||additionalEffect455(id)||highEffect455(id)
           ||(effectQuality455==1&&qualityFamily455(id)))continue;
        if(!id||!stMLcnt)return;
        DeleteMagicList(i--,TRUE);
    }
}
static void FrameMoveMagicEffects(){
    for(DWORD i=0;i<stMLcnt;++i){
        auto& magic=stMagicList[i];magic.mOldFrame=magic.mFrame;
        magic.mFrame=float(double(magic.mFrame)+R3GetLoopTime()*30.0);
        LONG first=0;auto* process=static_cast<CProcessMagic*>(magic.mMagicPtr);
        const LONG count=process->GetEntityIDs(magic.mOldFrame,magic.mFrame,&first);
        if(count<0){
            if(count==-2&&(magic.mState==0||magic.mState==2||magic.mState==4)&&IsAllDisapear(&magic))DeleteMagicList(i--);
            continue;
        }
        for(LONG j=first;j<first+count;++j){
            auto& track=process->mMagicTrack[j];
            if(track.Flag&0x1000)throw std::runtime_error("455 screen blur provider remains open");
            if(track.Flag&_MT_FLAG_QUAKE){float density=GetDensityFromPos(magic.mMat[3]);if(density>0)R3EnvironmentQuake(track.QuakeTime,track.QuakeDensity*density);continue;}
            if(track.Flag&_MT_FLAG_SKY_FADE){SetFadeSky(track.Color,track.SkyFadeTime);continue;}
            if(track.Flag&_MT_FLAG_TEX_FADE){SetFadeTex(track.Color,track.TexFadeTime,GetFirstTexureFromEffectEntityList(track.EntityID));continue;}
            if(track.Flag&_MT_FLAG_CHECK_DAMAGE)EFUtil_PushEffectValue(&magic.mEInfo,TRUE);
            const float frame=float(double(magic.mFrame)-double(track.Time)*30.0);
            float matrix[4][4];MatrixRotate(matrix,0,track.Yangle,0);
            memcpy(matrix[3],track.Pos,12);MatrixMultiply(matrix,magic.mMat,matrix);
            if(track.Flag&_MT_FLAG_ENTITY_FADE){MatrixIdentity(matrix);auto* state=GetR3State();matrix[3][0]=state->mMatView.m[3][0];matrix[3][1]=state->mMatView.m[3][2];MatrixCopy(matrix,state->mInvMatView.m);}
            const auto emit=[&](){StartEffectTrack(matrix,&track,magic.mState,frame,magic.mEntityUniqueID[j]);};
            const DWORD id=magic.mMagicID;
            if(id==1358041392||id==1358041648)emit(); // target permits a second emission below
            if(GetEffectQuality455()>1)emit();
            else{
                if(forcedEffect455(id))emit();
                if(GetEffectQuality455()==1&&qualityFamily455(id))emit();
                if(highEffect455(id))emit();
                if(additionalEffect455(id))emit();
                if(id==1358041904)emit();
            }
            if(stELcnt&&magic.mSpecialID){auto& effect=stEffectList[stELcnt-1];effect.mSpecialID=magic.mSpecialID;memcpy(effect.mVectorArgv1,magic.mVectorArgv1,12);memcpy(effect.mVectorArgv2,magic.mVectorArgv2,12);}
        }
    }
}
