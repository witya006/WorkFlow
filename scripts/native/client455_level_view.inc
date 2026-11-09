void CLevel::SetViewMatrix(D3DXMATRIX* view){
    Vector3f displacement={0,0,0};memcpy(&mMatView,view,sizeof(mMatView));
    //8EB7F0: the map level samples the previous global view,then publishes its own.
    R3GetQuakeVector(displacement);
    for(unsigned i=0;i<3;++i)mMatView.m[3][i]=static_cast<float>(double(mMatView.m[3][i])+displacement[i]);
    GetR3State()->mMatView=mMatView;
}
