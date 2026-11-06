CAniCamera::LoadAniCamera(char* name)
{
    RF455CameraDocument doc;if(!RF455_LoadCameraFile(name,doc))return;
    if(mAniCameraNum)ReleaseAniCamera();else RF455_ForgetCameraDocument(this);
    mAniCameraNum=static_cast<DWORD>(doc.cameras.size());
    if(!mAniCameraNum){RF455_StoreCameraDocument(this,std::move(doc));return;}
    mStartFrame=doc.start;mEndFrame=doc.end;
    AniCamera=static_cast<_ANI_CAMERA*>(Dmalloc(sizeof(_ANI_CAMERA)*mAniCameraNum));
    memset(AniCamera,0,sizeof(_ANI_CAMERA)*mAniCameraNum);
    auto materialize=[](_ANI_OBJECT& object,const RF455CameraNode& node){
        memset(&object,0,sizeof(object));memcpy(object.s_matrix,node.matrix,64);memcpy(object.pos,node.position,12);memcpy(object.quat,node.rotation,16);
        object.Pos_cnt=static_cast<int>(node.positions.size());object.Rot_cnt=static_cast<int>(node.rotations.size());
        const size_t pos=node.positions.size()*16,rot=node.rotations.size()*20;
        if(pos+rot){object.Pos=static_cast<_POS_TRACK*>(Dmalloc(pos+rot));object.Rot=reinterpret_cast<_ROT_TRACK*>(reinterpret_cast<BYTE*>(object.Pos)+pos);if(pos)memcpy(object.Pos,node.positions.data(),pos);if(rot)memcpy(object.Rot,node.rotations.data(),rot);}
    };
    for(DWORD i=0;i<mAniCameraNum;++i){auto& camera=AniCamera[i];const auto& from=doc.cameras[i];memcpy(camera.mName,from.name,64);camera.fov=from.fov;camera.tdist=from.distance;camera.h_num=static_cast<DWORD>(from.hierarchy.size());
        camera.obj=camera.h_num?static_cast<_ANI_OBJECT*>(Dmalloc(sizeof(_ANI_OBJECT)*camera.h_num)):nullptr;
        for(DWORD j=0;j<camera.h_num;++j)materialize(camera.obj[j],from.hierarchy[j]);
    }
    mDummyNum=static_cast<DWORD>(doc.dummies.size());mDummy=mDummyNum?static_cast<_ANI_OBJECT*>(Dmalloc(sizeof(_ANI_OBJECT)*mDummyNum)):nullptr;
    for(DWORD i=0;i<mDummyNum;++i){materialize(mDummy[i],doc.dummies[i].node);memcpy(mDummy[i].ObjectName,doc.dummies[i].name,64);memcpy(mDummy[i].ParentName,doc.dummies[i].parentName,64);}
    RF455_StoreCameraDocument(this,std::move(doc));
}
