void CLevel::DrawSkyBoxRender(){
    auto* state=GetR3State();auto* device=GetD3dDevice();
    D3DXMatrixPerspectiveFovLH(&state->mMatProj,state->mFov,state->mAsfectRatio,2.0f,state->mFar);
    device->SetTransform(D3DTS_PROJECTION,&state->mMatProj);
    if(mSkyBox->IsLoaded455())mSkyBox->DrawSkyBox(&mMatView);
    DrawFadeSKy();
    D3DXMatrixPerspectiveFovLH(&state->mMatProj,state->mFov,state->mAsfectRatio,state->mNear,state->mFar);
    if(state->mOrthographic){
        //4558E7A10 stores height/scale and width/scale asfloat before D3DX.
        float width,height;const float scale=state->mOrthographicScale;
        const float inputWidth=state->mScreenXsize,inputHeight=state->mScreenYsize;
        __asm{fld inputHeight
            fdiv scale
            fstp height
            fld inputWidth
            fdiv scale
            fstp width}
        D3DXMatrixIdentity(&state->mMatProj);
        D3DXMatrixOrthoLH(&state->mMatProj,width,height,-5000.0f,5000.0f);
        SetFrustumNormalPlane();
    }
    device->SetTransform(D3DTS_PROJECTION,&state->mMatProj);
}
