namespace {
IDirect3DVertexDeclaration9* bspLightDeclaration455=nullptr;
DWORD bspLightFaces455[5000]; // Target1170930:shared scratch,not a reentrant API.
}
void RF455_ReleaseBspLightDeclaration(){
    if(bspLightDeclaration455)bspLightDeclaration455->Release();
    bspLightDeclaration455=nullptr;
}
HRESULT RF455_CreateBspLightDeclaration(IDirect3DDevice9* device){
    RF455_ReleaseBspLightDeclaration();
    const D3DVERTEXELEMENT9 elements[]={
        {0,0,D3DDECLTYPE_FLOAT3,D3DDECLMETHOD_DEFAULT,D3DDECLUSAGE_POSITION,0},
        {0,12,D3DDECLTYPE_D3DCOLOR,D3DDECLMETHOD_DEFAULT,D3DDECLUSAGE_COLOR,0},
        D3DDECL_END()
    };
    return device->CreateVertexDeclaration(elements,&bspLightDeclaration455);
}
IDirect3DVertexDeclaration9* RF455_BspLightDeclaration(){return bspLightDeclaration455;}

void CBsp::DrawDynamicLightSub(Vector3f lo,Vector3f hi){
    LONG leafCount=0;SHORT leaves[256];
    GetFastLeafListFromBBox(lo,hi,&leafCount,leaves,128);
    _D3DR3VERTEX_TEX0 vertices[5000];DWORD used=0,seen=0;
    const auto flush=[&](){
        auto* device=GetD3dDevice();device->SetVertexDeclaration(bspLightDeclaration455);
        device->SetTransform(D3DTS_WORLD,&mWorldMatrix455);
        device->DrawPrimitiveUP(D3DPT_TRIANGLELIST,used/3,vertices,16);used=0;
    };
    for(LONG i=0;i<leafCount;++i){
        const DWORD leaf=static_cast<DWORD>(static_cast<LONG>(leaves[i]));
        if(leaf>=mLeafNum)continue;
        const auto& entry=mLeaf[leaf];
        for(DWORD j=0;j<entry.face_num;++j){
            const DWORD id=mCFaceId[entry.face_start_id+j];const auto& face=mCFace[id];
            if(face.Attr&0x10)continue;
            DWORD k=0;while(k<seen&&bspLightFaces455[k]!=id)++k;if(k<seen)continue;
            bspLightFaces455[seen++]=id;
            for(int triangle=0;triangle<int(face.VNum)-2;++triangle){
                const DWORD corners[]={0,DWORD(triangle+1),DWORD(triangle+2)};
                for(DWORD corner:corners){const auto& point=mCVertex[mCVertexId[face.VStartId+corner]];auto& out=vertices[used++];out.x=point[0];out.y=point[1];out.z=point[2];out.color=0;}
                if(used>=3000)flush();
            }
            if(seen>=5000){if(used)flush();return;}
        }
    }
    if(used)flush();
}

void CBsp::DrawMagicLightSub(Vector3f lo,Vector3f hi){
    // The original checks X width repeatedly;do not invent Y/Z width guards.
    if(double(hi[0])-lo[0]>1000.0)return;
    if(lo[0]==hi[0]&&lo[1]==hi[1]&&lo[2]==hi[2])return;
    const auto inside=[&](const float* point){
        const auto& root=mNode[1];
        for(unsigned i=0;i<3;++i)if(!(point[i]>=root.bb_min[i]&&point[i]<=root.bb_max[i]))return false;
        return true;
    };
    if(!inside(lo)||!inside(hi))return;
    LONG leafCount=0;SHORT leaves[256];GetFastLeafListFromBBox(lo,hi,&leafCount,leaves,256);
    _D3DR3VERTEX_TEX0 vertices[5000];DWORD used=0,seen=0;
    const auto flush=[&](){
        auto* device=GetD3dDevice();device->SetVertexDeclaration(bspLightDeclaration455);
        device->SetTransform(D3DTS_WORLD,&mWorldMatrix455);
        device->DrawPrimitiveUP(D3DPT_TRIANGLELIST,used/3,vertices,16);used=0;
    };
    for(LONG i=0;i<leafCount;++i){const auto& entry=mLeaf[leaves[i]];
        for(DWORD j=0;j<entry.face_num;++j){
            const DWORD id=mCFaceId[entry.face_start_id+j];const auto& face=mCFace[id];
            if((face.Attr&0x30)||!(face.Normal[1]>0))continue;
            DWORD k=0;while(k<seen&&bspLightFaces455[k]!=id)++k;if(k<seen)continue;
            if(seen>2999)seen=2999;bspLightFaces455[seen++]=id;
            for(int triangle=0;triangle<int(face.VNum)-2;++triangle){
                const DWORD corners[]={0,DWORD(triangle+1),DWORD(triangle+2)};
                for(DWORD corner:corners){const auto& point=mCVertex[mCVertexId[face.VStartId+corner]];auto& out=vertices[used++];out.x=point[0];out.y=point[1];out.z=point[2];out.color=0;}
                if(used>=2000)flush();
            }
        }
    }
    if(used)flush();
}
