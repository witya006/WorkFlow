//455904B60/904590 and named shader lookup/binding. Same ordinary owner as binary.
namespace {
unsigned specialParameterCursor455=0; //1175784:not reset by903870/903B90.
unsigned parameterType455(const char* token){
    static const char* names[]={"n","b","i","f","v","m44","t","timer"};
    for(unsigned i=0;i<8;++i)if(!std::strcmp(token,names[i]))return i;
    return 9;
}
IUnknown* compileSpecialFile455(const char* file,const char* profile,IUnknown** constants){
    ID3DXBuffer *code=nullptr,*errors=nullptr;ID3DXConstantTable* table=nullptr;
    const HRESULT compiled=D3DXCompileShaderFromFileA(file,nullptr,nullptr,"main",profile,0,&code,&errors,&table);*constants=table;
    if(FAILED(compiled)){
        *constants=nullptr;
        if(errors){specialWarning455(static_cast<const char*>(errors->GetBufferPointer()));errors->Release();}
        return nullptr;
    }
    IUnknown* result=nullptr;HRESULT created;
    if(!_strnicmp(profile,"vs",2)){
        IDirect3DVertexShader9* p=nullptr;created=GetD3dDevice()->CreateVertexShader(static_cast<const DWORD*>(code->GetBufferPointer()),&p);result=p;
    }else if(!_strnicmp(profile,"ps",2)){
        IDirect3DPixelShader9* p=nullptr;created=GetD3dDevice()->CreatePixelShader(static_cast<const DWORD*>(code->GetBufferPointer()),&p);result=p;
    }else return code; //904590 returns the buffer for an unrecognized prefix.
    code->Release();
    if(FAILED(created)){specialWarning455("Shader creation failed");releaseSpecial455(result);releaseSpecial455(*constants);return nullptr;}
    return result;
}
RF455SpecialProgram* namedSpecial455(const char* name,bool pixel){
    auto* rows=pixel?special455.pixels:special455.vertices;const unsigned count=pixel?special455.pixelCount:special455.vertexCount;
    for(unsigned i=0;i<count;++i)if(!std::strcmp(rows[i].name,name))return rows+i;
    return nullptr;
}
}
const RF455SpecialParameter* RF455_GetSpecialShaderParameter(unsigned object,unsigned slot){
    return reinterpret_cast<const RF455SpecialParameter*>(special455.objects[object].parameters)+slot;
}
IUnknown* RF455_GetSpecialShaderConstants(const char* name,bool pixel){auto* row=namedSpecial455(name,pixel);return row?row->constants:nullptr;}
HRESULT RF455_BindSpecialVertexShader(const char* name){
    if(!name){GetD3dDevice()->SetVertexShader(nullptr);return 0;}
    auto* row=namedSpecial455(name,false);return row?GetD3dDevice()->SetVertexShader(static_cast<IDirect3DVertexShader9*>(row->program)):1;
}
HRESULT RF455_BindSpecialPixelShader(const char* name){
    if(!name){GetD3dDevice()->SetPixelShader(nullptr);return 0;}
    auto* row=namedSpecial455(name,true);return row?GetD3dDevice()->SetPixelShader(static_cast<IDirect3DPixelShader9*>(row->program)):1;
}
int RF455_LoadSpecialShaderText(){
    FILE* f=std::fopen("./System/Shader/Init.r3s","rb");
    if(!f){specialWarning455(".\\System\\Shader\\Init.r3s");return -1;}
    initSpecial455();char token[256],path[256],profile[32],parameter[128];unsigned count;
    while(!std::feof(f)){
        //Keep the original feof/read ordering,including reprocessing a final
        //[sh_list] tag when its last token has trailing whitespace.
        std::fscanf(f,"%s",token);
        if(!std::strcmp(token,"[path]"))std::fscanf(f,"%s",path);
        else std::strcpy(path,".\\System\\Shader\\"); //The next tag resets a custom path.
        if(!std::strcmp(token,"[fx_list]"))std::fscanf(f,"%d",&count); //No FX loading body in904B60.
        for(unsigned kind=0;kind<2;++kind)if(!std::strcmp(token,kind?"[ps_list]":"[vs_list]")){
            std::fscanf(f,"%d",&count);
            for(unsigned i=0;i<count;++i){
                char file[256];std::strcpy(file,path);std::fscanf(f,"%s %s",token,profile);std::strcat(file,token);
                IUnknown* constants=nullptr;IUnknown* program=compileSpecialFile455(file,profile,&constants);
                if(program)appendSpecial455(kind?special455.pixels:special455.vertices,kind?special455.pixelCount:special455.vertexCount,token,program,constants);
                else specialWarning455(file);
            }
        }
        if(!std::strcmp(token,"[sh_list]")){
            std::fscanf(f,"%d",&count);
            for(unsigned i=0;i<count;++i){
                auto& object=special455.objects[special455.objectCount];int first=0,second=0;std::fscanf(f,"%d",&first);
                if(first>=0){object.vertex=WORD(first);object.pixel=0;std::fscanf(f,"%d",&second);object.pixel=WORD(second);}
                else{std::fscanf(f,"%d",&second);std::memcpy(&object,&second,4);}
                std::fscanf(f,"%s",parameter);
                while(std::strcmp(parameter,"}")){
                    if(std::strcmp(parameter,"{")){
                        auto* row=reinterpret_cast<RF455SpecialParameter*>(object.parameters)+specialParameterCursor455;
                        std::strcpy(row->name,parameter);std::fscanf(f,"%s",parameter);row->type=parameterType455(parameter);
                        switch(row->type){
                            case 1:case 2:std::fscanf(f,"%d",&row->integer);++specialParameterCursor455;break;
                            case 3:std::fscanf(f,"%f",row->values);++specialParameterCursor455;break;
                            case 4:std::fscanf(f,"%f%f%f%f",row->values,row->values+1,row->values+2,row->values+3);++specialParameterCursor455;break;
                            case 5:for(unsigned line=0;line<4;++line)std::fscanf(f,"%f%f%f%f",row->values+line*4,row->values+line*4+1,row->values+line*4+2,row->values+line*4+3);++specialParameterCursor455;break;
                            default:break; //n/t/timer/unknown retain this slot and consume no value.
                        }
                    }
                    std::fscanf(f,"%s",parameter);
                }
                ++special455.objectCount;specialParameterCursor455=0;
            }
        }
    }
    return std::fclose(f);
}
