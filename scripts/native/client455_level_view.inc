void CLevel::SetViewMatrix(D3DXMATRIX* view){
    Vector3f displacement={0,0,0};memcpy(&mMatView,view,sizeof(mMatView));
    //8E7850: CLevel vtable B38494 slot27 publishes input before sampling quake.
    //8EB7F0 belongs to the separate INS vtable B3872C,not this map class.
    GetR3State()->mMatView=mMatView;
    R3GetQuakeVector(displacement);
    for(unsigned i=0;i<3;++i)mMatView.m[3][i]=static_cast<float>(double(mMatView.m[3][i])+displacement[i]);
    GetR3State()->mMatView=mMatView;
}
