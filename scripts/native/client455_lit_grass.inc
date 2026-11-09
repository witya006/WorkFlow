static RF455R3VertexProgram stLitGrass455;
void RF455_SetLitGrass(float addFrame,float* factors,float alpha,DWORD color,const float* direction){
    auto* d=GetD3dDevice();auto* state=GetR3State();D3DXMATRIX projection;
    D3DXMatrixTranspose(&projection,&state->mMatProj);d->SetVertexShaderConstantF(4,reinterpret_cast<float*>(&projection),4);
    d->SetVertexShader(stLitGrass455.shader);d->SetVertexDeclaration(stLitGrass455.declaration);
    const float fog[4]={state->mFogStart,state->mFogEnd,1.f/(state->mFogEnd-state->mFogStart),0};d->SetVertexShaderConstantF(8,fog,1);
    const float time=float(double(R3GetTime())+double(addFrame)/10.0),angle=float(double(factors[0])*time),cosine=float(cos(double(angle)));
    const float wind[4]={float(double(cosine)*double(.2f)*factors[1]),alpha,0,1};d->SetVertexShaderConstantF(9,wind,1);
    D3DLIGHT9 light;D3DMATERIAL9 material;GetMatLightFromColor(&light,&material,color,1.f);
    material.Diffuse.a=alpha;material.Diffuse.r=min(1.f,float(double(material.Diffuse.r)+.25));
    material.Diffuse.g=min(1.f,float(double(material.Diffuse.g)+double(.2f)));material.Diffuse.b=min(1.f,float(double(material.Diffuse.b)+double(.2f)));
    material.Ambient.r=float(double(material.Ambient.r)+double(.1f));material.Ambient.g=float(double(material.Ambient.g)+double(.1f));material.Ambient.b=float(double(material.Ambient.b)+double(.1f));
    //The original overreads three registers at19/21/22;only19.xyz and21/22
    //are read by the pinned shader. Deterministic unused lanes are an explicit gap.
    float lightRegisters[12]={direction[0],direction[1],direction[2]};
    d->SetVertexShaderConstantF(19,lightRegisters,3);
    d->SetVertexShaderConstantF(21,reinterpret_cast<const float*>(&material.Diffuse),3);
    d->SetVertexShaderConstantF(22,reinterpret_cast<const float*>(&material.Ambient),3);
}
