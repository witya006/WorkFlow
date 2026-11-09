#define main unusedWorldEntry122
#include "client455_world_probe.cpp"
#undef main
struct Normal122{using Type=Vector3f* CBsp::*;friend Type access(Normal122);};template struct MemberAccess<Normal122,&CBsp::mCNNormal>;
struct Camera122{using Type=Vector3f CBsp::*;friend Type access(Camera122);};template struct MemberAccess<Camera122,&CBsp::mTempCamera>;
static void read122(void* p,unsigned size,FILE* f){check(std::fread(p,1,size,f)==size,"owned fixture bounds");}
static int run122(){
    InitR3Engine();FILE* in=std::fopen("fixtures.bin","rb");FILE* out=std::fopen("leaf.jsonl","wb");check(in&&out,"files");unsigned count;read122(&count,4,in);
    for(unsigned i=0;i<count;++i){unsigned topology;float data[19];read122(&topology,4,in);read122(data,sizeof(data),in);CBsp bsp,other;_BSP_NODE nodes[3]={};Vector3f normals[2]={{1,0,0},{0,1,0}};
        nodes[1].f_normal_id=0;nodes[1].front=topology==1?-1:(topology>=2?0:-2);nodes[1].back=topology==2?-1:(topology==3?0:2);nodes[2].f_normal_id=1;nodes[2].front=-3;nodes[2].back=-4;
        bsp.mNode=nodes;other.mNode=nodes;bsp.*access(Normal122{})=normals;other.*access(Normal122{})=normals;D3DXMATRIX world;D3DXMatrixIdentity(&world);world._41=91;world._42=-72;world._43=53;bsp.SetWorldMatrices455(&world,data+3);
        const short leaf=bsp.GetLeafNum(data);const auto& local=bsp.*access(Camera122{});other.GetLeafNum(data);check(!std::memcmp(other.*access(Camera122{}),data,12),"independent inverse owner stays identity");
        DWORD bits[3];std::memcpy(bits,local,12);std::fprintf(out,"{\"id\":%u,\"leaf\":%d,\"local_bits\":[%u,%u,%u]}\n",i,int(leaf),bits[0],bits[1],bits[2]);
    }
    check(std::fgetc(in)==EOF,"complete fixtures");std::fclose(in);std::fclose(out);ReleaseR3Engine();return 0;
}
int main(){try{return run122();}catch(const std::exception& e){std::fprintf(stderr,"bsp-leaf122:%s\n",e.what());return 1;}}
