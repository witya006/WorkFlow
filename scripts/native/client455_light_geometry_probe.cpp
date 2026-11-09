#define main unusedWorldEntry121
#include "client455_world_probe.cpp"
#undef main
#include <client455_bsp_light.h>
#include <array>
#include <vector>

struct Faces121{using Type=_BSP_C_FACE* CBsp::*;friend Type access(Faces121);};template struct MemberAccess<Faces121,&CBsp::mCFace>;
struct Ids121{using Type=DWORD* CBsp::*;friend Type access(Ids121);};template struct MemberAccess<Ids121,&CBsp::mCFaceId>;
struct Vertices121{using Type=Vector3f* CBsp::*;friend Type access(Vertices121);};template struct MemberAccess<Vertices121,&CBsp::mCVertex>;
struct Corners121{using Type=DWORD* CBsp::*;friend Type access(Corners121);};template struct MemberAccess<Corners121,&CBsp::mCVertexId>;
struct Normals121{using Type=Vector3f* CBsp::*;friend Type access(Normals121);};template struct MemberAccess<Normals121,&CBsp::mCNNormal>;
static FILE *fixture121,*emitted121,*trace121;
template<class T>static void read121(T* p,unsigned n=1){check(std::fread(p,sizeof(T),n,fixture121)==n,"owned fixture bounds");}
static std::vector<unsigned> batches121;static D3DMATRIX observed121;static unsigned decls121=0,worlds121=0;static long begin121;
static HRESULT WINAPI captureDraw121(IDirect3DDevice9*,D3DPRIMITIVETYPE type,UINT count,const void* data,UINT stride){check(type==D3DPT_TRIANGLELIST&&stride==16&&count<=1666,"actual light draw arguments");batches121.push_back(count*3);check(std::fwrite(data,16,count*3,emitted121)==count*3,"capture vertices");return S_OK;}
static HRESULT WINAPI captureWorld121(IDirect3DDevice9*,D3DTRANSFORMSTATETYPE type,const D3DMATRIX* matrix){check(type==D3DTS_WORLD,"actual world binding");observed121=*matrix;++worlds121;return S_OK;}
static HRESULT WINAPI captureDecl121(IDirect3DDevice9*,IDirect3DVertexDeclaration9* declaration){check(declaration==RF455_BspLightDeclaration()&&declaration!=nullptr,"actual retained declaration binding");++decls121;return S_OK;}
struct Hook121{
    // Isolated OWN D3D device,documented IDirect3DDevice9 slots44/83/87.
    // Capture only these calls during CPU fixtures;restore the original vtable.
    IDirect3DDevice9* device;void** original;std::array<void*,119> table;
    Hook121(IDirect3DDevice9* d):device(d),original(*reinterpret_cast<void***>(d)){
        std::memcpy(table.data(),original,sizeof(table));table[44]=reinterpret_cast<void*>(captureWorld121);table[83]=reinterpret_cast<void*>(captureDraw121);table[87]=reinterpret_cast<void*>(captureDecl121);*reinterpret_cast<void***>(device)=table.data();
    }
    ~Hook121(){*reinterpret_cast<void***>(device)=original;}
};
struct Fixture121{
    CBsp bsp;std::vector<_BSP_NODE> nodes;std::vector<_BSP_LEAF> leaves;std::vector<_BSP_C_FACE> faces;std::vector<DWORD> ids,corners;std::vector<std::array<float,3>> vertices;std::array<float,3> normal={{1,0,0}};
    void load(unsigned faceCount,unsigned leafCount){
        faces.resize(faceCount);leaves.resize(leafCount+1);nodes.resize((std::max)(leafCount,2u));
        for(unsigned i=0;i<faceCount;++i){BYTE info[4];float y;read121(info,4);read121(&y);auto& face=faces[i];face.Attr=info[0];face.VNum=info[1];face.Normal[1]=y;face.VStartId=unsigned(corners.size());for(unsigned j=0;j<face.VNum;++j){corners.push_back(unsigned(vertices.size()));vertices.push_back({{float(i),float(j),float(i^j)}});}}
        for(unsigned i=1;i<=leafCount;++i){unsigned count;read121(&count);leaves[i].face_start_id=unsigned(ids.size());leaves[i].face_num=WORD(count);const auto at=ids.size();ids.resize(at+count);if(count)read121(ids.data()+at,count);}
        for(unsigned i=1;i<nodes.size();++i){auto& node=nodes[i];for(unsigned j=0;j<3;++j){node.bb_min[j]=-10000;node.bb_max[j]=10000;}node.d=leafCount==1?-2.f:1.f-2.f*float(i)/float(leafCount);node.front=SHORT(-int(i)-1);node.back=leafCount==1?0:(i==leafCount-1?SHORT(-int(leafCount)-1):SHORT(i+1));}
        bsp.mNode=nodes.data();bsp.mNodeNum=DWORD(nodes.size());bsp.mLeaf=leaves.data();bsp.mLeafNum=DWORD(leaves.size());bsp.*access(Faces121{})=faces.data();bsp.*access(Ids121{})=ids.data();bsp.*access(Corners121{})=corners.data();bsp.*access(Vertices121{})=reinterpret_cast<Vector3f*>(vertices.data());bsp.*access(Normals121{})=reinterpret_cast<Vector3f*>(normal.data());
    }
};
static int run121(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);InitR3Engine();SetWarningMessageProc(warningMessage);SetErrorMessageProc(errorMessage);auto* state=GetR3State();state->mScreenXsize=640;state->mScreenYsize=480;state->mbFullScreen=FALSE;ForceFullScreen();check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"device");
    auto* declaration=RF455_BspLightDeclaration();check(declaration!=nullptr,"declaration created in ordinary device path");D3DVERTEXELEMENT9 elements[8];UINT count=8;check(SUCCEEDED(declaration->GetDeclaration(elements,&count))&&count==3,"declaration element count");check(elements[0].Stream==0&&elements[0].Offset==0&&elements[0].Type==D3DDECLTYPE_FLOAT3&&elements[0].Usage==D3DDECLUSAGE_POSITION&&elements[1].Stream==0&&elements[1].Offset==12&&elements[1].Type==D3DDECLTYPE_D3DCOLOR&&elements[1].Usage==D3DDECLUSAGE_COLOR&&elements[2].Stream==255,"actual455XYZ/color declaration");
    fixture121=std::fopen("fixtures.bin","rb");emitted121=std::fopen("emitted.bin","wb");trace121=std::fopen("geometry.jsonl","wb");check(fixture121&&emitted121&&trace121,"fixture outputs");char magic[8];read121(magic,8);check(!std::memcmp(magic,"RFLG121",8),"fixture signature");unsigned cases;read121(&cases);
    {
        Hook121 hook(GetD3dDevice());
        for(unsigned c=0;c<cases;++c){unsigned header[4];read121(header,4);float data[38];read121(data,38);Fixture121 f;f.load(header[2],header[3]);
            D3DXMATRIX identity;D3DXMatrixIdentity(&identity);check(!std::memcmp(&f.bsp.WorldMatrix455(),&identity,64)&&!std::memcmp(&f.bsp.InverseWorldMatrix455(),&identity,64),"each BSP initializes its matrices");f.bsp.SetWorldMatrices455(data,data+16);check(!std::memcmp(&f.bsp.WorldMatrix455(),data,64)&&!std::memcmp(&f.bsp.InverseWorldMatrix455(),data+16,64),"setter copies both matrices exactly");CBsp other;check(!std::memcmp(&other.WorldMatrix455(),&identity,64),"BSP owners independent");
            batches121.clear();decls121=worlds121=0;begin121=std::ftell(emitted121);if(header[1])f.bsp.DrawMagicLightSub(data+32,data+35);else f.bsp.DrawDynamicLightSub(data+32,data+35);
            check(worlds121==batches121.size()&&decls121==batches121.size(),"every draw binds world and declaration");if(worlds121)check(!std::memcmp(&observed121,data,64),"actual emitted world equals owned setter");
            std::fprintf(trace121,"{\"id\":%u,\"offset\":%ld,\"bytes\":%ld,\"batches\":[",header[0],begin121,std::ftell(emitted121)-begin121);for(unsigned i=0;i<batches121.size();++i)std::fprintf(trace121,"%s%u",i?",":"",batches121[i]);std::fprintf(trace121,"],\"matrix_exact\":true,\"declaration_exact\":true}\n");
        }
    }
    check(std::fgetc(fixture121)==EOF,"all owned fixture bytes consumed");std::fclose(fixture121);std::fclose(emitted121);std::fclose(trace121);g_MainApp.ReleaseR3D3D();check(RF455_BspLightDeclaration()==nullptr,"normal device teardown releases declaration");ReleaseR3Engine();FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"result");std::fprintf(out,"{\"status\":\"PASS\",\"cases\":%u,\"actual_BSP_methods\":true,\"owned_device_capture\":true,\"declaration_created_and_released\":true,\"full_client\":false}\n",cases);std::fclose(out);return 0;
}
int main(){try{return run121();}catch(const std::exception& e){std::fprintf(stderr,"light-geometry121:%s\n",e.what());return 1;}}
