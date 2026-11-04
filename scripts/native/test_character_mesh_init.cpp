#include <winsock2.h>
#include "Character.h"
#include "character_mesh_format.h"
#include <cstdio>
#include <cstring>
#include <vector>

extern "C" void RFCharacterOriginal_InitVertex(ObjectData*,CHARACTEROBJECT*,CHARACTEROBJECT*,TextureManager*,bool);
extern "C" void RFCharacterOriginal_ConvertVertex(CHARACTERVERTEX&,EXPTVERTEX&);
extern "C" void RFCharacterOriginal_ConvertUV(CHARACTERVERTEX&,tagTEXCOORDFLOAT);
extern "C" void RFCharacterOriginal_DecodePhysique(CHARACTERVERTEX*,int,PHYSIQUE*,int);
static unsigned checks,cases,callbackFailures,buffersAlive;
#define INIT_CHECK(c) do{++checks;if(!(c)){std::fprintf(stderr,"init check%u line%d\n",checks,__LINE__);return 1;}}while(0)
template<class T>static void set(void* base,unsigned offset,T value){std::memcpy(static_cast<unsigned char*>(base)+offset,&value,sizeof(value));}
template<class T>static T get(const void* base,unsigned offset){T value;std::memcpy(&value,static_cast<const unsigned char*>(base)+offset,sizeof(value));return value;}
static unsigned short control(){unsigned short value;__asm {fnstcw value}return value;}
static unsigned short status(){unsigned short value;__asm {fnstsw value}return value;}
static void setControl(unsigned short value){__asm {fldcw value}}

// Test-only COM doubles capture real SDK MakeVB input. Production keeps the
// actual Direct3D provider; this fixture creates no device and renders nothing.
struct CaptureDevice {void** table;int failure;unsigned creates;};
struct CaptureBuffer {void** table;std::vector<unsigned char> bytes;bool failLock;};
static void* bufferTable[14]={};
static ULONG __stdcall releaseBuffer(CaptureBuffer* buffer){--buffersAlive;delete buffer;return 0;}
static HRESULT __stdcall lockBuffer(CaptureBuffer* buffer,UINT offset,UINT size,BYTE** output,DWORD flags){
    if(offset || size!=buffer->bytes.size() || flags){++callbackFailures;return E_FAIL;}
    if(buffer->failLock)return E_FAIL;
    *output=buffer->bytes.data();return S_OK;
}
static HRESULT __stdcall unlockBuffer(CaptureBuffer*){return S_OK;}
static HRESULT __stdcall createBuffer(CaptureDevice* device,UINT size,DWORD usage,DWORD fvf,D3DPOOL pool,IDirect3DVertexBuffer8** output){
    ++device->creates;
    if(usage!=8 || fvf!=278 || pool!=D3DPOOL_MANAGED || size%36){++callbackFailures;return E_FAIL;}
    if(device->failure==1)return E_FAIL;
    auto* buffer=new CaptureBuffer{bufferTable,std::vector<unsigned char>(size,0xcd),device->failure==2};
    ++buffersAlive;*output=reinterpret_cast<IDirect3DVertexBuffer8*>(buffer);return S_OK;
}
static ULONG __stdcall releaseDevice(CaptureDevice*){return 1;}
static void makeIdentity(void* base,unsigned offset){D3DXMATRIX m;D3DXMatrixIdentity(&m);std::memcpy(static_cast<unsigned char*>(base)+offset,&m,64);}
static int parentNumber(ObjectMesh* pointer,ObjectMesh* local,unsigned count,ObjectMesh* external){
    if(!pointer)return -1;
    for(unsigned n=0;n<count;++n)if(pointer==local+n)return static_cast<int>(n);
    if(pointer==external)return 100;
    return -2;
}

static int runCharacterInitChecks(FILE* output){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX);
    bufferTable[2]=reinterpret_cast<void*>(&releaseBuffer);bufferTable[11]=reinterpret_cast<void*>(&lockBuffer);bufferTable[12]=reinterpret_cast<void*>(&unlockBuffer);
    void* deviceTable[24]={};deviceTable[2]=reinterpret_cast<void*>(&releaseDevice);deviceTable[23]=reinterpret_cast<void*>(&createBuffer);
    CaptureDevice capture={deviceTable,0,0};ChInterface renderer;renderer.legacy_device=reinterpret_cast<IDirect3DDevice8*>(&capture);
    ObjectMesh skeletonMesh;skeletonMesh.m_pMatBlend=nullptr;std::strcpy(skeletonMesh.m_Name,"ROOT");makeIdentity(&skeletonMesh,304);
    CHARACTEROBJECT skeleton{};skeleton.m_MaxObj=1;skeleton.m_pMesh=&skeletonMesh;
    const unsigned short original=control();
    struct Scenario {unsigned meshes,faces,skinned,external,failure,boneName,ignoreParent;};
    const Scenario scenarios[]={{0,0,0,0,0,0,0},{1,0,0,0,0,0,0},{1,0,1,0,0,0,0},{1,1,0,0,0,0,0},
        {1,1,1,0,0,0,0},{2,2,0,0,0,0,0},{2,2,1,1,0,0,0},{1,1,1,1,0,0,0},
        {1,2,0,0,1,0,0},{2,1,1,0,2,0,0},{1,1,0,0,0,1,0},{2,2,1,0,0,0,1}};
    for(unsigned precision:{0u,2u,3u})for(unsigned rounding=0;rounding<4;++rounding){
        const unsigned short mode=static_cast<unsigned short>((original&~0x0f00u)|0x3fu|(precision<<8)|(rounding<<10));setControl(mode);
        for(const auto& s:scenarios){
            ++cases;unsigned char records[2][720]={},physiques[2][3][424]={},faces[2][2][88]={},data[28]={};
            EXPTVERTEX vertices[2][3]={};set<unsigned short>(data,2,static_cast<unsigned short>(s.meshes));set<void*>(data,4,records);set<DWORD>(data,24,s.ignoreParent);
            for(unsigned m=0;m<s.meshes;++m){
                std::strcpy(reinterpret_cast<char*>(records[m]),s.boneName?"C:\\Meshes\\BONE ROOT":m?"C:\\Meshes\\ARM":"C:\\Meshes\\ROOT");
                if(m)std::strcpy(reinterpret_cast<char*>(records[m])+100,"C:\\Bones\\ROOT");
                set<unsigned short>(records[m],392,3);set<unsigned short>(records[m],394,static_cast<unsigned short>(s.faces));
                set<unsigned short>(records[m],396,static_cast<unsigned short>(s.skinned?3:0));
                set<void*>(records[m],696,vertices[m]);set<void*>(records[m],700,faces[m]);set<void*>(records[m],704,s.skinned?physiques[m]:nullptr);
                set<DWORD>(records[m],598,0x24681357);for(unsigned n=0;n<6;++n)set<float>(records[m],602+4*n,(n+1)*1.25f);
                for(unsigned n=0;n<4;++n)set<unsigned char>(records[m],631+n,static_cast<unsigned char>(n+3));set<unsigned char>(records[m],639,9);
                for(unsigned offset:{200u,264u,328u}){D3DXMATRIX matrix;D3DXMatrixScaling(&matrix,1.5f,2.0f,0.75f);matrix._41=3.25f;matrix._42=-1.5f;matrix._43=6;std::memcpy(records[m]+offset,&matrix,64);}
                for(unsigned v=0;v<3;++v){
                    vertices[m][v]={{v+0.5f,-1.25f,2.75f},0x12345678,{0.125f,v+0.25f,-0.5f}};
                    set<int>(physiques[m][v],0,v);set<int>(physiques[m][v],4,v?1:2);
                    std::strcpy(reinterpret_cast<char*>(physiques[m][v])+8,v==1?"ARM":"ROOT");
                    std::strcpy(reinterpret_cast<char*>(physiques[m][v])+108,"ARM");
                    set<float>(physiques[m][v],408,0.125f+0.25f*v);set<float>(physiques[m][v],412,0.875f);
                }
                for(unsigned f=0;f<s.faces;++f)for(unsigned corner=0;corner<3;++corner){set<int>(faces[m][f],4*corner,(corner+f)%3);set<float>(faces[m][f],48+12*corner,corner*.25f);set<float>(faces[m][f],52+12*corner,.125f+corner*.25f);}
            }
            CHARACTEROBJECT own{},reference{};capture.failure=s.failure;capture.creates=0;const auto top=status()&0x3800;
            InitVertex(reinterpret_cast<ObjectData*>(data),s.external?&skeleton:nullptr,&own,&renderer.m_TM,true);
            const unsigned ownCreates=capture.creates;capture.creates=0;
            RFCharacterOriginal_InitVertex(reinterpret_cast<ObjectData*>(data),s.external?&skeleton:nullptr,&reference,&renderer.m_TM,false);
            INIT_CHECK(control()==mode);INIT_CHECK((status()&0x3800)==top);INIT_CHECK(ownCreates==capture.creates);
            INIT_CHECK(own.m_MaxObj==reference.m_MaxObj && own.m_MaxObj==s.meshes);INIT_CHECK(own.unknown_108==reference.unknown_108);
            for(unsigned m=0;m<s.meshes;++m){
                ObjectMesh& a=own.m_pMesh[m];ObjectMesh& b=reference.m_pMesh[m];
                INIT_CHECK(!std::strcmp(a.m_Name,b.m_Name));INIT_CHECK(!std::strcmp(reinterpret_cast<char*>(&a)+64,reinterpret_cast<char*>(&b)+64));
                INIT_CHECK(a.m_HaveParent==b.m_HaveParent);INIT_CHECK(parentNumber(a.m_pParent,own.m_pMesh,s.meshes,&skeletonMesh)==parentNumber(b.m_pParent,reference.m_pMesh,s.meshes,&skeletonMesh));
                INIT_CHECK(!std::memcmp(reinterpret_cast<char*>(&a)+176,reinterpret_cast<char*>(&b)+176,576));
                for(unsigned offset:{752u,756u,772u,776u,780u,784u,796u,864u,960u,964u,968u,972u,976u,980u,996u,1068u})INIT_CHECK(get<DWORD>(&a,offset)==get<DWORD>(&b,offset));
                for(unsigned offset:{948u,949u,950u,956u,957u})INIT_CHECK(get<unsigned char>(&a,offset)==get<unsigned char>(&b,offset));
                INIT_CHECK(a.m_BlendNum==b.m_BlendNum);INIT_CHECK(a.m_pMatBlend && b.m_pMatBlend);INIT_CHECK(!std::memcmp(a.m_pMatBlend,b.m_pMatBlend,64*a.m_BlendNum));
                for(unsigned n=0;n<a.m_BlendNum;++n)INIT_CHECK(parentNumber(get<ObjectMesh*>(&a,144+4*n),own.m_pMesh,s.meshes,&skeletonMesh)==parentNumber(get<ObjectMesh*>(&b,144+4*n),reference.m_pMesh,s.meshes,&skeletonMesh));
                CaptureBuffer* aBuffer=get<CaptureBuffer*>(&a,164);CaptureBuffer* bBuffer=get<CaptureBuffer*>(&b,164);
                INIT_CHECK((aBuffer!=nullptr)==(bBuffer!=nullptr));if(aBuffer)INIT_CHECK(aBuffer->bytes==bBuffer->bytes);
            }
            delete[] own.m_pMesh;delete[] reference.m_pMesh;INIT_CHECK(buffersAlive==0);INIT_CHECK(callbackFailures==0);
        }
    }
    setControl(original);
    std::fprintf(output,"{\"checks_passed\":%u,\"cases\":%u,\"precision_rounding_modes\":12,\"source_init_vertex\":true,\"actual_sdk_make_vb\":true,\"test_only_com_capture\":true,\"gpu_used\":false,\"remaining_capture_buffers\":%u}\n",checks,cases,buffersAlive);
    renderer.legacy_device=nullptr;
    return 0;
}
#ifndef RF_CHARACTER_INIT_EMBEDDED
int main(){return runCharacterInitChecks(stdout);}
#endif
#undef INIT_CHECK
