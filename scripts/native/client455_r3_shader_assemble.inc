HRESULT D3DUtil_CreateVertexShader(LPDIRECT3DDEVICE9 device,TCHAR* filename,
    const D3DVERTEXELEMENT9* elements,RF455R3VertexProgram* program){
    LPD3DXBUFFER code=nullptr,errors=nullptr;
    HRESULT hr=D3DXAssembleShaderFromFile(filename,nullptr,nullptr,0,&code,&errors);
    if(errors)errors->Release();if(FAILED(hr))return hr;
    hr=device->CreateVertexDeclaration(elements,&program->declaration);
    if(SUCCEEDED(hr))hr=device->CreateVertexShader(static_cast<const DWORD*>(code->GetBufferPointer()),&program->shader);
    if(FAILED(hr) && program->declaration){program->declaration->Release();program->declaration=nullptr;}
    code->Release();return hr;
}
