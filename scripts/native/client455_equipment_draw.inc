#include "client455_equipment_draw_lifecycle.h"
#include "addcodebyyun/particlelist.h"
#include "renderparticle.h"
#include "entity.h"
#include "commonutil.h"
#include <vector>
#include <cmath>
#include <mmsystem.h>

namespace {
RF455BasicItem* equipmentPayload455(const RF455EquipmentObject& object){
    auto* payload=object.GetItem455();if(!payload)return nullptr;
    auto* normal=dynamic_cast<RF455BasicItem*>(payload);
    if(!normal)throw std::logic_error("455 equipment render requires a basic payload");
    return normal;
}
RF455ItemDataSpan equipmentMetadata455(const RF455EquipmentObject& object){
    auto* payload=equipmentPayload455(object);return payload?payload->rawMetadata():RF455ItemDataSpan{};
}
template<class T>T equipmentField455(RF455ItemDataSpan row,unsigned offset){
    if(!row.data||offset>row.size||sizeof(T)>row.size-offset)throw std::out_of_range("455 equipment render metadata extent");
    T value;std::memcpy(&value,row.data+offset,sizeof value);return value;
}
struct EquipmentClock455 {float scroll=0;DWORD previous=0;
    float advance(){const DWORD now=timeGetTime();if(!previous)previous=now;
        const float delta=static_cast<float>(double(DWORD(now-previous))*double(.0005f));previous=now;
        scroll=static_cast<float>(double(scroll)+delta);return scroll;}
};
EquipmentClock455 equipmentClock455[2];
std::unique_ptr<RF455EquipmentEffectQueue>& equipmentQueue455(){static std::unique_ptr<RF455EquipmentEffectQueue> value;return value;}
//7BC8B0,scale1/a6=0 caller in46CF10. The engine particle/entity methods are
//real source providers. Their remaining full registry/scale parity is separate.
void equipmentParticles455(CMesh* model,float* position,float yaw,DWORD color,const Vector3f* trace){
    static float scroll=0,previous=0;const float now=R3GetTime();if(previous==0)previous=now;
    const float delta=static_cast<float>(double(now)-previous)*.5f;previous=now;
    scroll=static_cast<float>(double(delta)*30.0+scroll);
    const D3DXMATRIX swap(1,0,0,0,0,0,1,0,0,1,0,0,0,0,0,1);
    for(unsigned i=0;i<model->m_MaxObj;++i){auto& mesh=model->m_pMesh[i];auto* slots=mesh.particleSlots();if(!slots)continue;
        for(unsigned j=0;j<3;++j){if(!slots[j].m_ID)continue;auto* particle=g_Particle.GetParticle(slots[j].m_ID);if(!particle)continue;
            auto* definition=g_Particle.GetCHParticle(slots[j].m_ID);
            std::memcpy(particle->mSpecialARGV,trace,2*sizeof(Vector3f));
            D3DXMATRIX world,rotation;D3DXMatrixIdentity(&world);
            if(definition->m_bAbsAxis){
                D3DXMatrixRotationY(&rotation,D3DXToRadian(-(180-yaw)));D3DXMatrixMultiply(&world,&rotation,&world);
                D3DXVECTOR3 origin(mesh.m_MatResult._41,mesh.m_MatResult._43,mesh.m_MatResult._42);D3DXVECTOR4 moved;
                D3DXVec3Transform(&moved,&origin,&rotation);world._41=position[0]+moved.x+slots[j].m_X;world._42=position[1]+moved.y+slots[j].m_Y;world._43=position[2]+moved.z+slots[j].m_Z;
            }else{
                D3DXMatrixRotationZ(&rotation,D3DXToRadian(180-yaw));D3DXMatrixMultiply(&world,&rotation,&world);D3DXMatrixMultiply(&world,&world,&swap);D3DXMatrixMultiply(&world,&mesh.m_MatResult,&world);
                world._41=position[0]+world._41+slots[j].m_X;world._42=position[1]+world._42+slots[j].m_Y;world._43=position[2]+world._43+slots[j].m_Z;
                rotation=world;rotation._41=rotation._42=rotation._43=0;
            }
            if(!particle->Loop())return;std::memcpy(particle->mRotMat,&rotation,64);particle->SetCreatePos(&world._41);
            DrawCParticle(particle,particle->mEntity,world.m,color);
        }
        const auto& slot=mesh.entitySlot();if(!slot.m_ID)continue;auto* entity=g_Particle.GetEntity(slot.m_ID);if(!entity)continue;
        auto* definition=g_Particle.GetCHEntity(slot.m_ID);D3DXMATRIX world,rotation;D3DXMatrixIdentity(&world);
        if(definition->m_bAbsAxis){
            D3DXMatrixRotationY(&rotation,D3DXToRadian(-(180-yaw)));D3DXMatrixMultiply(&world,&rotation,&world);
            D3DXVECTOR3 origin(mesh.m_MatResult._41,mesh.m_MatResult._43,mesh.m_MatResult._42);D3DXVECTOR4 moved;D3DXVec3Transform(&moved,&origin,&rotation);
            world._41=position[0]+moved.x+slot.m_X;world._42=position[1]+moved.y+slot.m_Y;world._43=position[2]+moved.z+slot.m_Z;
        }else{
            D3DXMatrixRotationZ(&rotation,D3DXToRadian(180-yaw));D3DXMatrixMultiply(&world,&rotation,&world);
            world._41=position[0]+slot.m_X;world._43=position[1]+slot.m_Y;world._42=position[2]+slot.m_Z;
            D3DXMatrixMultiply(&world,&world,&swap);D3DXMatrixMultiply(&world,&mesh.m_MatResult,&world);D3DXMATRIX inverse;D3DXMatrixInverse(&inverse,nullptr,&swap);D3DXMatrixMultiply(&world,&inverse,&world);
        }
        entity->DrawEntity(world.m,color,scroll);
    }
}
Vector3f equipmentTrace455[2]{}; //7BC7F0 retains the previous positions on failure.
}
BYTE RF455EquipmentObject::GetOverlayGrade455()const{
    if(!overlayGradeKnown455)throw std::logic_error("455 overlay604 has no verified producer for this object");return overlayGrade455;
}
void RF455EquipmentObject::PrepareOverlaySlot455(BYTE slot){
    SetOverlayGrade455(slot==6||slot==7?equipmentField455<BYTE>(equipmentMetadata455(*this),152):0);
}
BYTE RF455EquipmentObject::EffectGrade455()const{
    auto* item=equipmentPayload455(*this);if(!item)return 0;
    return equipmentField455<BYTE>(item->recordBytes(),113); //404EA0,not a boolean.
}
BYTE RF455EquipmentObject::UnitPart455()const{
    auto* item=equipmentPayload455(*this);if(!item||!item->header().data16)return 255;
    const BYTE kind=equipmentField455<BYTE>(item->rawMetadata(),88);if(kind<37||kind>43)return 255;
    return equipmentField455<BYTE>(item->rawData(),152);
}
DWORD RF455EquipmentObject::EffectListKey455()const{
    const auto row=equipmentMetadata455(*this);const DWORD index=equipmentField455<DWORD>(row,0);
    const BYTE kind=equipmentField455<BYTE>(row,88);return UnitPart455()==255?index:DWORD(kind-37)*100+index;
}
bool RF455EquipmentObject::CanRender455(){return mesh455&&!IsDisable(2)&&!IsEnable(4096);}
BOOL RF455EquipmentObject::Render(){
    if(!CResObject::Render()||!CanRender455())return FALSE;
    if(IsEnable(4))_GetCharIF()->SetAlpha(mesh455,m_fAlphaDensity);
    _GetCharIF()->SetMaterial(mesh455,m_d3dMaterial);DrawWithEffect455(renderMode455,nullptr);
    if(IsEnable(4))_GetCharIF()->SetAlpha(mesh455,1);return TRUE;
}
BOOL RF455EquipmentObject::Render455(const D3DXMATRIX& matrix){
    if(!CResObject::Render()||!CanRender455())return FALSE;
    if(IsEnable(4))_GetCharIF()->SetAlpha(mesh455,m_fAlphaDensity);
    _GetCharIF()->SetMaterial(mesh455,m_d3dMaterial);DrawWithEffect455(renderMode455,&matrix);
    if(IsEnable(4))_GetCharIF()->SetAlpha(mesh455,1);return TRUE;
}
void RF455EquipmentObject::DrawWithEffect455(BYTE mode,const D3DXMATRIX* matrix){
    auto* item=equipmentPayload455(*this);if(!item)return;
    auto& renderer=*_GetCharIF();auto& clock=equipmentClock455[matrix?1:0];clock.advance();
    renderer.InitEffect(mesh455);renderer.SetAlpha(mesh455,renderer.GetAlpha(mesh455));if(clock.scroll>1)clock.scroll=0;
    const auto row=item->rawMetadata();const BYTE kind=equipmentField455<BYTE>(row,88);
    const bool unit=UnitPart455()!=255;
    if(unit)g_EFFUnitList.SetEffect(mesh455,EffectListKey455());
    else if(kind==27)g_EFFKitList.SetEffect(mesh455,EffectListKey455());
    else SetMeshEffect(mesh455,equipmentField455<DWORD>(row,72),EffectGrade455(),(mesh455->m_ID>>20)==1||(mesh455->m_ID>>20)==3?5:0);
    //Both mode4/weapon predicates lead to the same primary/overlay bodies in
    //46C470/46C940. No predicate side effects are present in the audited calls.
    (void)mode;
    if(matrix)renderer.DrawCharacterMat(mesh455,const_cast<D3DXMATRIX*>(matrix),clock.scroll);
    else renderer.DrawCharacter(mesh455,m_vecPos,m_vecRot[1],m_fScale,clock.scroll,false);
    if(!unit&&GetOverlayGrade455()){
        auto& grade=RF455_GradeOverlays455();grade.Begin455(GetOverlayGrade455());
        if(!matrix){const float scale=static_cast<float>(double(m_fScale)*0.0+m_fScale);renderer.DrawCharacterOverlay455(mesh455,m_vecPos,m_vecRot[1],scale,clock.scroll,true);}
        grade.End455(); //The target matrix route has no second geometry draw.
    }
    if((unit||IsHaveMeshEffect(mesh455,equipmentField455<DWORD>(row,72),EffectGrade455(),0))&&mesh455->IsHaveEffect())RF455_EquipmentEffects455().Add455(this);
}
bool RF455EquipmentObject::GetTracePositions455(Vector3f* out)const{
    if(!mesh455)return false;D3DXMATRIX rotation,matrix;MatrixRotate(rotation.m,0,0,360-m_vecRot[1]);const D3DXVECTOR3 origin(0,0,0);
    for(unsigned i=0;i<2;++i){const BYTE index=GetDummy455(i);if(index==255)return false;
        if(index>=mesh455->m_MaxObj)throw std::out_of_range("455 equipment trace node outside model");
        MatrixMultiply(matrix.m,rotation.m,mesh455->m_pMesh[index].m_MatResult.m);D3DXVECTOR4 point;D3DXVec3Transform(&point,&origin,&matrix);
        out[i][0]=point.x;out[i][1]=-point.z;out[i][2]=point.y;
    }return true;
}
BOOL RF455EquipmentObject::RenderWithShadow455(){
    if(!CanRender455())return FALSE;auto& renderer=*_GetCharIF();
    if(IsEnable(4))renderer.SetAlpha(mesh455,m_fAlphaDensity);
    const auto row=equipmentMetadata455(*this);const DWORD meshID=equipmentField455<DWORD>(row,72);
    renderer.SetMaterial(mesh455,m_d3dMaterial);renderer.UnSetState();SetMeshEffect(mesh455,meshID,EffectGrade455(),0);
    renderer.SetMaterial(mesh455,m_d3dMaterial);SetMeshEffect(mesh455,meshID,EffectGrade455(),0);
    const float alpha=renderer.GetAlpha(mesh455);Vector3f trace[2];if(GetTracePositions455(trace))std::memcpy(equipmentTrace455,trace,sizeof trace);
    DWORD color=0x00ffffffu;
    if(std::isfinite(alpha)&&double(alpha)*255>=-9223372036854775808.0&&double(alpha)*255<9223372036854775808.0)color+=static_cast<DWORD>(static_cast<std::int64_t>(double(alpha)*255))<<24;
    equipmentParticles455(mesh455,m_vecPos,m_vecRot[1],color,equipmentTrace455);
    if(IsEnable(4))renderer.SetAlpha(mesh455,1);return TRUE;
}
struct RF455EquipmentEffectQueue::State {
    unsigned count=0,start=0;std::array<unsigned,256> nodes{};
    std::vector<std::unique_ptr<RF455EquipmentObject>> objects;
    //Do not zero this memory on Clear:528090 resets counts/owners only.
    std::unique_ptr<unsigned char[]> matrices{new unsigned char[256*64*4*64]};
    unsigned char* matrix(unsigned slot,unsigned node,unsigned palette){
        const std::size_t offset=(std::size_t(slot)*64*4+std::size_t(node)*4+palette)*64;
        if(offset>256*64*4*64||64>256*64*4*64-offset)throw std::out_of_range("455 effect queue palette beyond original matrix allocation");return matrices.get()+offset;
    }
};
RF455EquipmentEffectQueue::RF455EquipmentEffectQueue():state(new State){}
RF455EquipmentEffectQueue::~RF455EquipmentEffectQueue(){Clear455();}
unsigned RF455EquipmentEffectQueue::Count455()const{return state->count;}
unsigned RF455EquipmentEffectQueue::Start455()const{return state->start;}
void RF455EquipmentEffectQueue::Add455(const RF455EquipmentObject* source){
    if(!source||state->count>=256)return;
    std::unique_ptr<RF455EquipmentObject> copy(new RF455EquipmentObject(*source));auto* mesh=source->GetMesh455();
    if(!mesh)throw std::logic_error("455 effect queue source has no mesh");
    const unsigned slot=state->count;state->nodes[slot]=mesh->m_MaxObj>=64?63:mesh->m_MaxObj;
    for(unsigned i=0;i<state->nodes[slot];++i){auto& node=mesh->m_pMesh[i];
        if(node.m_BlendNum>30)throw std::out_of_range("455 effect queue source palette outside mesh record");
        for(unsigned j=0;j<(node.m_BlendNum?node.m_BlendNum:1);++j)std::memcpy(state->matrix(slot,i,j),node.m_BlendNum?static_cast<void*>(&node.m_pMatBlend[j]):static_cast<void*>(&node.m_MatResult),64);
    }
    ++state->count;state->objects.push_back(std::move(copy));
}
void RF455EquipmentEffectQueue::Clear455(){state->count=state->start=0;state->nodes.fill(0);state->objects.clear();}
BOOL RF455EquipmentEffectQueue::Render455(){
    for(auto& object:state->objects){const unsigned start=++state->start;if(!object||start>state->count)continue;
        auto* mesh=object->GetMesh455();for(unsigned i=0;i<state->nodes[start-1];++i){auto& node=mesh->m_pMesh[i];
            if(node.m_BlendNum>30)throw std::out_of_range("455 effect queue restore palette outside mesh record");
            for(unsigned j=0;j<(node.m_BlendNum?node.m_BlendNum:1);++j)std::memcpy(node.m_BlendNum?static_cast<void*>(&node.m_pMatBlend[j]):static_cast<void*>(&node.m_MatResult),state->matrix(start-1,i,j),64);
        }object->RenderWithShadow455();
    }_GetCharIF()->UnSetState();return TRUE;
}
RF455EquipmentEffectQueue& RF455_EquipmentEffects455(){auto& value=equipmentQueue455();if(!value)value.reset(new RF455EquipmentEffectQueue);return *value;}
void RF455_ClearEquipmentEffects455(){if(equipmentQueue455())equipmentQueue455()->Clear455();}
void RF455_RenderEquipmentEffects455(){if(equipmentQueue455())equipmentQueue455()->Render455();}
