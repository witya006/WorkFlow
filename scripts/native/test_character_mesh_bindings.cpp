#include <winsock2.h>
#include "Character.h"
#include <cstdio>
#include <cstring>
#include <new>

extern "C" ObjectMesh* RFCharacterOriginal_FindByName(char*,ObjectMesh*,int);
extern "C" int RFCharacterOriginal_BindParents(ObjectMesh*,int,ObjectMesh*,int);
extern "C" int RFCharacterOriginal_RematchParents(ObjectMesh*,int,ObjectMesh*,int);
extern "C" void RFCharacterOriginal_BindBlends(ObjectMesh*,int,ObjectMesh*,int,ObjectData*);
static unsigned checks;
#define CHECK(c) do {++checks;if (!(c)) {std::fprintf(stderr,"check%u line%d\n",checks,__LINE__);return 1;}}while(0)
template<class T> static void put(void* base,unsigned offset,T value) {std::memcpy(static_cast<unsigned char*>(base)+offset,&value,sizeof(value));}
template<class T> static T get(const void* base,unsigned offset) {T value;std::memcpy(&value,static_cast<const unsigned char*>(base)+offset,sizeof(value));return value;}
static void name(ObjectMesh& mesh,const char* own,const char* parentName="") {
    std::strcpy(mesh.m_Name,own);std::strcpy(reinterpret_cast<char*>(&mesh)+64,parentName);
}
static int runCharacterMeshChecks(FILE* output) {
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX);
    ObjectMesh parents[5],left[3],right[3];
    for (auto& mesh:parents) mesh.m_pMatBlend=nullptr;
    for (auto& mesh:left) mesh.m_pMatBlend=nullptr;
    for (auto& mesh:right) mesh.m_pMatBlend=nullptr;
    for(int n=0;n<5;++n) name(parents[n],n<2?"ROOT":n==2?"ARM":n==3?"LEG":"OTHER");
    char query[][12]={"ROOT","ARM","LEG","MISSING","root",""};
    for(int count=-1;count<=5;++count) for(auto& text:query)
        CHECK(FindParent(text,parents,count)==RFCharacterOriginal_FindByName(text,parents,count));
    for(int count=-1;count<=5;++count) for(int rematch=0;rematch<2;++rematch) {
        for(int n=0;n<3;++n) {name(left[n],"MESH",n==0?"ROOT":n==1?"ARM":"MISSING");
            left[n].m_pParent=nullptr;left[n].m_HaveParent=false;put<DWORD>(&left[n],996,n&1);std::memcpy(&right[n],&left[n],sizeof(ObjectMesh));}
        int a=rematch?RematchParent(parents,count,left,3):FindParent(parents,count,left,3);
        int b=rematch?RFCharacterOriginal_RematchParents(parents,count,right,3):RFCharacterOriginal_BindParents(parents,count,right,3);
        CHECK(a==b);for(int n=0;n<3;++n) CHECK(!std::memcmp(&left[n],&right[n],sizeof(ObjectMesh)));
        if(count==2 && !rematch) {CHECK(a==2);CHECK(left[0].m_pParent==&parents[1]);}
    }
    CHECK(FindParent(nullptr,0,nullptr,0)==0);CHECK(RematchParent(nullptr,0,nullptr,-1)==0);
    FindBlendParent(nullptr,0,nullptr,0,nullptr);RFCharacterOriginal_BindBlends(nullptr,0,nullptr,-1,nullptr);CHECK(true);
    // Three 720-byte records, two 424-byte physique records per mesh. Bounded
    // <=4 unique parents fits the supplied legacy inline parent-pointer region.
    unsigned char records[3][720]={},physiques[3][2][424]={},objectData[28]={};
    put<void*>(objectData,4,records);
    for(int n=0;n<3;++n) put<void*>(records[n],704,physiques[n]);
    for(int scenario=0;scenario<8;++scenario) {
        std::memset(physiques,0,sizeof(physiques));
        for(int n=0;n<3;++n) {
            put<unsigned short>(records[n],396,scenario?2:0);
            for(int p=0;p<2;++p) {
                const int influences=scenario==1?0:scenario==2?1:2;put<int>(physiques[n][p],4,influences);
                std::strcpy(reinterpret_cast<char*>(physiques[n][p])+8,scenario==4?"MISSING":p?"LEG":"ROOT");
                std::strcpy(reinterpret_cast<char*>(physiques[n][p])+108,scenario==3?"ROOT":scenario==5?"LOCAL":scenario==7 && p?"OTHER":"ARM");
            }
            name(left[n],n==0?"LOCAL":"MESH");left[n].m_BlendNum=0;left[n].m_pMatBlend=nullptr;
            std::memcpy(&right[n],&left[n],sizeof(ObjectMesh));
        }
        FindBlendParent(parents,scenario==6?0:5,left,3,reinterpret_cast<ObjectData*>(objectData));
        RFCharacterOriginal_BindBlends(parents,scenario==6?0:5,right,3,reinterpret_cast<ObjectData*>(objectData));
        for(int n=0;n<3;++n) {
            CHECK(left[n].m_BlendNum==right[n].m_BlendNum);CHECK(left[n].m_pMatBlend!=nullptr);CHECK(right[n].m_pMatBlend!=nullptr);
            CHECK(!std::memcmp(left[n].m_pMatBlend,right[n].m_pMatBlend,64*left[n].m_BlendNum));
            for(unsigned b=0;b<left[n].m_BlendNum;++b) {
                ObjectMesh* a=get<ObjectMesh*>(&left[n],144+4*b);ObjectMesh* bptr=get<ObjectMesh*>(&right[n],144+4*b);
                if(a>=left && a<left+3) CHECK(bptr==right+(a-left));else CHECK(a==bptr);
            }
            ::operator delete(left[n].m_pMatBlend);::operator delete(right[n].m_pMatBlend);
            left[n].m_pMatBlend=right[n].m_pMatBlend=nullptr;
        }
    }
    // Actual supplied InitVertex constructs its mesh and reaches our source
    // bindings, defining the blend owner even with zero influences. No faces,
    // textures or vertex-buffer creation; real CPU vertex conversion still runs.
    {ChInterface renderer;unsigned char meshRecord[720]={},vertices[3][28]={};
    unsigned char loadedData[28]={};put<unsigned short>(loadedData,2,1);put<void*>(loadedData,4,meshRecord);
    std::strcpy(reinterpret_cast<char*>(meshRecord),"ROOT");
    put<unsigned short>(meshRecord,392,3);put<void*>(meshRecord,696,vertices);
    D3DXMATRIX identity;D3DXMatrixIdentity(&identity);
    for(unsigned offset:{200u,264u,328u})std::memcpy(meshRecord+offset,&identity,64);
    unsigned char influence[424]={};put<int>(influence,4,1);
    std::strcpy(reinterpret_cast<char*>(influence)+8,"ROOT");put<float>(influence,408,1.0f);
    for(unsigned skinned=0;skinned<2;++skinned) {
    put<unsigned short>(meshRecord,396,static_cast<unsigned short>(skinned));
    put<void*>(meshRecord,704,skinned?influence:nullptr);
    CHARACTEROBJECT character{};
    InitVertex(reinterpret_cast<ObjectData*>(loadedData),nullptr,&character,&renderer.m_TM,true);
    CHECK(character.m_MaxObj==1 && character.m_pMesh);CHECK(character.m_pMesh[0].m_BlendNum==skinned);
    CHECK(character.m_pMesh[0].m_pMatBlend!=nullptr);CHECK(!std::strcmp(character.m_pMesh[0].m_Name,"ROOT"));
    if(skinned) {CHECK(get<ObjectMesh*>(&character.m_pMesh[0],144)==character.m_pMesh);CHECK(!std::memcmp(character.m_pMesh[0].m_pMatBlend,&identity,64));}
    delete[] character.m_pMesh;character.m_pMesh=nullptr;}}
    std::fprintf(output,"{\"checks_passed\":%u,\"source_functions\":4,\"actual_init_vertex\":true,\"gpu_used\":false}\n",checks);
    return 0;
}
#ifndef RF_CHARACTER_MESH_EMBEDDED
int main() {return runCharacterMeshChecks(stdout);}
#endif
#undef CHECK
