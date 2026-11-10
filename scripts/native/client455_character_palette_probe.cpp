#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "input/imeedit.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "mainapp.h"
#include <array>
#include <cstdio>
#include <cstring>
#include <memory>
#include <stdexcept>

static unsigned checks=0;
static void require(bool value,const char* text){if(!value)throw std::runtime_error(text);++checks;}
static void matrix(D3DXMATRIX& out,float first){for(unsigned r=0;r<4;++r)for(unsigned c=0;c<4;++c)out.m[r][c]=first+float(r*4+c);}
static int run(){
    static_assert(MAX_PARTS_RESULT==20&&RF455_PART_PALETTES==30&&MAX_EFFECT_DUMMYS==13,"455 ordinary Character cache dimensions");
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);InitR3Engine();unsigned groups=0,restored=0;
    {
        CCharacter actor;
        for(unsigned part=0;part<20;++part)require(!actor.GetResultMat(part,0),"Constructor clears all20capacity records");
        auto nodes=std::unique_ptr<ObjectMesh[]>(new ObjectMesh[4]);std::memset(nodes.get(),0,4*sizeof(ObjectMesh));
        CMesh model={};model.m_pMesh=nodes.get();model.m_MaxObj=2;nodes[0].m_BlendNum=0;nodes[1].m_BlendNum=30;
        require(!actor.PSetVertexBlending(0,nullptr,TRUE),"Null model fails");
        for(unsigned part=0;part<20;++part){
            D3DXMATRIX expectedSingle;std::array<D3DXMATRIX,30> expected;
            matrix(expectedSingle,float(part*10000+1));nodes[0].m_MatResult=expectedSingle;
            for(unsigned palette=0;palette<30;++palette){matrix(expected[palette],float(part*10000+palette*100));nodes[1].m_pMatBlend[palette]=expected[palette];}
            require(actor.PSetVertexBlending(part,&model,TRUE),"Actual save forvalidpart0..19");
            require(actor.GetResultMat(part,0)&&!std::memcmp(actor.GetResultMat(part,0),&expectedSingle,64),"Actual first cached unblended matrix");
            require(actor.GetResultMat(part,1)&&!std::memcmp(actor.GetResultMat(part,1),&expected[0],64),"Actual GetResultMat returnsfirstpalette");
            require(!actor.GetResultMat(part,2),"Current cache capacity boundary");
            std::memset(&nodes[0].m_MatResult,0,64);std::memset(nodes[1].m_pMatBlend,0,30*64);
            require(actor.PSetVertexBlending(part,&model,FALSE),"Actual restorebefore draw");
            require(!std::memcmp(&nodes[0].m_MatResult,&expectedSingle,64)&&!std::memcmp(nodes[1].m_pMatBlend,expected.data(),30*64),"All30palettes restored,not old two");
            ++groups;restored+=30;
        }
        //Eachactor keeps its own cache whilethe resource mesh is shared.
        CCharacter second;matrix(nodes[0].m_MatResult,777);require(second.PSetVertexBlending(19,&model,TRUE),"Second actor save");
        require(actor.PSetVertexBlending(19,&model,FALSE)&&nodes[0].m_MatResult.m[0][0]==190001,"First actor owns its cached pose");
        require(second.PSetVertexBlending(19,&model,FALSE)&&nodes[0].m_MatResult.m[0][0]==777,"Second actor owns a different cached pose");
        model.m_MaxObj=3;nodes[2].m_BlendNum=0;matrix(nodes[2].m_MatResult,888);require(actor.PSetVertexBlending(19,&model,TRUE),"Growing cache reallocatesall30arrays");
        require(actor.GetResultMat(19,2)&&actor.GetResultMat(19,2)->m[0][0]==888,"Growth fills newnode");
        model.m_MaxObj=1;require(actor.PSetVertexBlending(19,&model,TRUE)&&actor.GetResultMat(19,2)->m[0][0]==888,"Smaller model preserves existingcapacity/tail");
        model.m_MaxObj=4;nodes[3].m_BlendNum=0;matrix(nodes[3].m_MatResult,999);matrix(nodes[0].m_MatResult,-1);
        require(!actor.PSetVertexBlending(19,&model,FALSE),"Restorefails whennode exceeds capacity");
        require(nodes[0].m_MatResult.m[0][0]==777&&nodes[2].m_MatResult.m[0][0]==888&&nodes[3].m_MatResult.m[0][0]==999,"Failed restorekeeps earlier prefix writes andunwritten tail");
        for(unsigned point=0;point<13;++point){actor.SetDummyIndex(point,20+point);require(actor.GetDummyIndex(point)==20+point,"All13ordinaryCharacterdummy slots");}
        require(actor.GetDummyIndex(13)==255&&actor.GetDummyIndex(0xffffffff)==255,"Dummy getterboundary");
        actor.SetDummyIndex(13,77);require(actor.GetDummyIndex(12)==32,"Out-of-range dummysetter leaves lastslot");
    }
    //Both actual Character destructors have now releasedallallocated palettes.
    ReleaseR3Engine();FILE* output=std::fopen("result.json","wb");require(output,"Output");
    std::fprintf(output,"{\"status\":\"PASS\",\"ordinary_character_groups\":%u,\"palette_roundtrips\":%u,\"dummy_slots\":13,\"actual_production_SetVertexBlending\":true,\"two_actor_independence\":true,\"grow_shrink_partial_restore\":true,\"actual_teardown\":true,\"full_player_equipment_or_appearance\":false,\"checks\":%u}\n",groups,restored,checks);std::fclose(output);return 0;
}
int main(){try{return run();}catch(const std::exception& error){std::fprintf(stderr,"Character palette147:%s\n",error.what());return 2;}}
