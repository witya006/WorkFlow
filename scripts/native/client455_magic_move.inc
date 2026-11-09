BOOL MovePosMagicEffect(DWORD unique_id,Vector3f pos,float y_angle){
    for(DWORD i=0;i<stMLcnt;++i){
        auto& magic=stMagicList[i];if(magic.mUniqueID!=unique_id)continue;
        magic.mYOldAngle=magic.mYAngle;magic.mYAngle=y_angle;
        float matrix[4][4];MatrixRotate(matrix,0,y_angle,0);memcpy(matrix[3],pos,12);
        auto* process=static_cast<CProcessMagic*>(magic.mMagicPtr);
        for(DWORD j=0;j<magic.mEntityUniqueIDCnt;++j){
            const auto& track=process->mMagicTrack[j];float offset[3];
            for(unsigned k=0;k<3;++k)offset[k]=matrix[0][k]*track.Pos[0]+matrix[1][k]*track.Pos[1]+matrix[2][k]*track.Pos[2];
            NowMagicListPtr=&magic;
            for(unsigned k=0;k<3;++k)matrix[3][k]+=offset[k];
            MoveMatrixEffect(magic.mEntityUniqueID[j],matrix);
            for(unsigned k=0;k<3;++k)matrix[3][k]-=offset[k];
            NowMagicListPtr=nullptr;
        }
        return TRUE;
    }
    return FALSE;
}
