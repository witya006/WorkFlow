HRESULT LoadCreateShader(char* filename,const D3DVERTEXELEMENT9* elements,RF455R3VertexProgram* program){
    FILE* file=fopen(filename,"rb");if(!file)return E_FAIL;
    fseek(file,0,SEEK_END);long length=ftell(file);fseek(file,0,SEEK_SET);
    if(length<4 || length%4){fclose(file);return D3DXERR_INVALIDDATA;}
    std::vector<DWORD> code(static_cast<unsigned>(length)/4);
    bool complete=fread(code.data(),static_cast<unsigned>(length),1,file)==1;fclose(file);if(!complete)return E_FAIL;
    HRESULT hr=GetD3dDevice()->CreateVertexDeclaration(elements,&program->declaration);
    if(FAILED(hr))return hr;
    hr=GetD3dDevice()->CreateVertexShader(code.data(),&program->shader);
    if(FAILED(hr)){program->declaration->Release();program->declaration=nullptr;}
    return hr;
}
