#pragma once
#include <array>
#include <algorithm>
#include <cstring>
#include <cctype>
#include <stdexcept>

// Own source view of46DAD0/46DB00/7F2D60,not an overlay ofthe original ABI.
struct RF455EquipmentDummyPoints {
    std::array<BYTE,10> indices{};
    BYTE get(unsigned index)const{return index<indices.size()?indices[index]:BYTE(255);}
    void set(unsigned index,BYTE value){if(index<indices.size())indices[index]=value;}
    void bind(const CMesh& mesh){
        indices.fill(255);
        static const char* names[]={"effect1","effect2","fire1","fire2","fire3","fire4"};
        for(unsigned i=0;i<mesh.m_MaxObj;++i){
            char name[20]={};const auto size=(std::min)(std::strlen(mesh.m_pMesh[i].m_Name)+1,std::size_t(19));
            std::memcpy(name,mesh.m_pMesh[i].m_Name,size);
            for(char* p=name;*p;++p)*p=static_cast<char>(std::tolower(static_cast<unsigned char>(*p)));
            for(unsigned n=0;n<6;++n)if(!std::strcmp(name,names[n]))set(n,BYTE(i));
        }
    }
};
struct RF455EffectPositionPart {
    bool present=false;CMesh* mesh=nullptr;const RF455EquipmentDummyPoints* points=nullptr;
};
struct RF455EffectPositionView {
    CCharacter* actor=nullptr;std::array<RF455EffectPositionPart,10> parts{};
};
struct RF455EffectPositionResult {
    bool targetReturn=false;
    //Some target failure branches copy uninitialised stack data. Preserve this
    //as an explicit unknown,not a fabricated successful world-space fallback.
    bool defined=false;
};

inline bool RF455_PlayerEffectActor(CCharacter& actor){const auto type=actor.GetCharTypeID();return type==0||type==15;}
inline unsigned RF455_EffectMeshBinding(const ObjectMesh& mesh,const char* name){
    if(mesh.m_pParent&&!std::strcmp(name,mesh.m_pParent->m_Name))return 1;
    if(mesh.m_BlendNum>30)throw std::out_of_range("455 effect mesh binding count");
    for(unsigned i=0;i<mesh.m_BlendNum;++i){const char* bindingName=nullptr;std::memcpy(&bindingName,mesh.bytes+526+i*4,4);
        if(!std::strcmp(name,bindingName))return i+2;
    }
    return 0;
}
inline void RF455_EffectMatrixPosition(float* out,CCharacter& actor,const D3DXMATRIX& matrix){
    D3DXMATRIX rotation,combined;const float angle=static_cast<float>(360.0-actor.GetRotY());
    MatrixRotate(rotation.m,0,0,angle);D3DXMatrixMultiply(&combined,&matrix,&rotation);
    const D3DXVECTOR3 zero(0,0,0);D3DXVECTOR4 transformed;D3DXVec3Transform(&transformed,&zero,&combined);
    const double scale=actor.GetScale();
    out[0]=static_cast<float>(actor.GetPosX()-double(transformed.x)*scale);
    out[1]=static_cast<float>(actor.GetPosY()+double(transformed.z)*scale);
    out[2]=static_cast<float>(actor.GetPosZ()-double(transformed.y)*scale);
}
inline bool RF455_EffectNamedPosition(float* out,const RF455EffectPositionView& view,const char* name){
    if(!view.actor)return false;auto& actor=*view.actor;
    if(RF455_PlayerEffectActor(actor)){
        for(unsigned part=0;part<10;++part){auto* model=view.parts[part].mesh;if(!view.parts[part].present||!model||!model->m_pMesh)continue;
            for(unsigned i=0;i<model->m_MaxObj;++i)if(RF455_EffectMeshBinding(model->m_pMesh[i],name)){
                auto* matrix=actor.GetResultMat(part,i);
                if(matrix){RF455_EffectMatrixPosition(out,actor,*matrix);return true;}
                break; //7E07B0 fails onthe first named mesh with no cached matrix.
            }
        }
        return false;
    }
    const auto type=actor.GetCharTypeID();
    if(type!=8&&type!=4&&type!=3&&type!=1&&type!=6&&type!=10)return false;
    auto* model=actor.GetBone();if(!model||!model->m_pMesh)return false;
    for(unsigned i=0;i<model->m_MaxObj;++i)if(!std::strcmp(name,model->m_pMesh[i].m_Name)){
        RF455_EffectMatrixPosition(out,actor,model->m_pMesh[i].m_MatResult);return true;
    }
    return false;
}
inline bool RF455_EffectBounds(float* out,CCharacter& actor,double factor){
    BBOX box;if(!actor.GetBoundBox(box,FALSE))return false;
    out[0]=actor.GetPosX();out[1]=static_cast<float>(actor.GetPosY()+(double(box.pMax[1])-box.pMin[1])*actor.GetScale()*factor);out[2]=actor.GetPosZ();return true;
}
inline RF455EffectPositionResult RF455_EffectWeaponPosition(float* out,const RF455EffectPositionView& view,unsigned point,bool withWeapon){
    if(!view.actor)return {};auto& actor=*view.actor;BYTE index;
    if(withWeapon){const auto* points=view.parts[6].points;index=points?points->get(point):BYTE(0);}
    else index=actor.GetDummyIndex(point);
    auto* matrix=(index==255||(withWeapon&&index==0))?nullptr:actor.GetResultMat(withWeapon?6:0,index);
    if(matrix){RF455_EffectMatrixPosition(out,actor,*matrix);return {true,true};}
    return {false,RF455_EffectBounds(out,actor,double(0.66f))};
}
inline bool RF455_EffectDamagePosition(float* out,const RF455EffectPositionView& view){
    auto& actor=*view.actor;const BYTE index=actor.GetDummyIndex(8);
    //7DCA10 zero-extends the byte then compares it with-1;255 is not excluded
    //before GetResultMat here,unlike7DCCF0/7DD140.
    if(auto* matrix=actor.GetResultMat(0,index)){RF455_EffectMatrixPosition(out,actor,*matrix);return true;}
    bool defined=RF455_EffectNamedPosition(out,view,"Bip01 Spine")||RF455_EffectNamedPosition(out,view,"Bip01 Spine1");
    if(!defined)defined=RF455_EffectBounds(out,actor,double(0.72f));
    const BYTE race=RF455_PlayerEffectActor(actor)?static_cast<CPlayer&>(actor).GetRace():BYTE(255);
    if(race==0||race==1||race==3){
        float first[3],second[3];
        if(RF455_EffectNamedPosition(first,view,"Bip01 Spine")&&RF455_EffectNamedPosition(second,view,"Bip01 Spine1")){
            for(unsigned i=0;i<3;++i)out[i]=static_cast<float>((double(second[i])-first[i])/2.0+first[i]);defined=true;
        }
    }
    return defined;
}
inline RF455EffectPositionResult RF455_ResolveEffectPosition(float* out,const RF455EffectPositionView& view,BYTE type){
    if(!view.actor)return {};auto& actor=*view.actor;actor.GetPosition(out);
    const char* name=nullptr;
    switch(type){
    case 1:{BBOX box;if(!actor.GetBoundBox(box,FALSE))return {true,false};out[1]=box.pMax[1];return {true,true};}
    case 2:return {true,RF455_EffectDamagePosition(out,view)};
    case 3:name="Bip01 R Hand";break;
    case 4:name="Bip01 L Hand";break;
    case 7:return {true,RF455_EffectBounds(out,actor,double(1.3f))};
    case 8:name="Bip01 R Foot";break;
    case 9:name="Bip01 L Foot";break;
    case 17:{const bool defined=RF455_EffectNamedPosition(out,view,"Bip01 Spine")||RF455_EffectNamedPosition(out,view,"Bip01 Spine1");return {true,defined};}
    case 5:case 6:case 11:case 12:case 13:case 14:case 15:case 16:{
        if(!RF455_PlayerEffectActor(actor)||!view.parts[6].present)return {true,false};
        const unsigned point=type==5?0:type==6?2:type==11?1:type-9;
        auto result=RF455_EffectWeaponPosition(out,view,point,true);result.targetReturn=true;return result;
    }
    default:return {true,true}; //0,10,18andallother values retain actor position.
    }
    return {true,RF455_EffectNamedPosition(out,view,name)};
}

//7E22F0 creates real magic first,then replaces translation only. Complete
//CAllEffectInfo attachment/state is a separate caller with additional rules.
inline DWORD RF455_StartMagicAtActor(const RF455EffectPositionView& view,float* position,float yaw,DWORD id,void* info,DWORD state){
    const DWORD unique=StartMagicEffect(position,yaw,id,info,state);auto* entry=GetMagicListFromID(unique);
    if(entry&&entry->mMagicPtr){float resolved[3];
        auto* script=static_cast<CProcessMagic*>(entry->mMagicPtr);
        const auto result=RF455_ResolveEffectPosition(resolved,view,script->mCreateType);
        if(result.targetReturn){
            if(!result.defined)throw std::logic_error("455 creation position depends on uninitialised target data");
            std::memcpy(entry->mMat[3],resolved,12);
        }
    }
    return unique;
}
