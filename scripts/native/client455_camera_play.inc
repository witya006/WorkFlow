CAniCamera::PlayAniCamera(float matrix[4][4],float speed_scale,BOOL pause)
{
    if(!mAniCameraNum)return TRUE;
    RF455CameraPlayback playback={mPlayStartFrame,mPlayEndFrame,mFlag,mStartTick,mOldFrame,mNowFrame};
    const RF455CameraClock clock={nullptr,[](void*)->float{return R3GetTime();}};
    const bool playing=RF455_AdvanceCamera(playback,speed_scale,pause!=FALSE,clock);
    mStartTick=playback.startTick;mOldFrame=playback.oldFrame;mNowFrame=playback.nowFrame;
    GetMatrixAniCamera(mNowFrame);MatrixCopy(matrix,stMakedViewMatrix);return playing?TRUE:FALSE;
}
