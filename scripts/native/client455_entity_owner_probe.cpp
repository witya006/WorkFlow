#define RF455_LIGHTING_CONSUMERS_NO_MAIN
#include "client455_lighting_consumers_probe.cpp"
static_assert(sizeof(_ENTITY_LIST)==84&&offsetof(_ENTITY_LIST,Flag)==72&&offsetof(_ENTITY_LIST,ShaderID)==74&&offsetof(CEntity,mFlag)==104,"455 map flags contract");

static int run132(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);InitR3Engine();SetWarningMessageProc(warningMessage);SetErrorMessageProc(errorMessage);
    auto* state=GetR3State();state->mScreenXsize=640;state->mScreenYsize=480;state->mbFullScreen=FALSE;ForceFullScreen();std::strcpy(state->MapPath,".\\Map\\");std::strcpy(state->EntityPath,".\\Map\\Entity\\");
    check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"device132");auto* device=GetD3dDevice();FILE* trace=std::fopen("entity-owner.jsonl","wb");check(trace!=nullptr,"trace132");std::setvbuf(trace,nullptr,_IONBF,0);
    unsigned frames=0;std::vector<WORD> sourceShaders;
    {
        CCamera camera;g_pCamera=&camera;CLand land;check(land.Create()!=0,"land132");
        for(unsigned pass=0;pass<2;++pass){const unsigned allowed=pass==0;state->mIsUsedVertexShader=allowed;char filename[]=".\\Map\\neutralB\\neutralB.bsp";check(land.LoadLevel(filename)!=0,"actual neutralB owner132");auto& level=*land.GetLevel();auto& bsp=*level.mBsp;
            if(!pass){for(unsigned i=0;i<bsp.mEntityListNum;++i)sourceShaders.push_back(bsp.mEntityList[i].ShaderID);}check(sourceShaders.size()==bsp.mEntityListNum,"same actual map records132");
            RF455_SetSkyDayEnabled(1);RF455_SetDayTime(12,0,0);level.FrameMove();
            for(unsigned i=0;i<bsp.mEntityListNum;++i){const auto& row=bsp.mEntityList[i];std::fprintf(trace,"{\"kind\":\"owner\",\"allowed\":%u,\"id\":%u,\"particle\":%u,\"exists\":%u,\"record_flag\":%u,\"shader\":%u,\"entity_flag\":%u}\n",allowed,i,row.IsParticle,row.IsFileExist,row.Flag,row.ShaderID,row.IsParticle?0:bsp.mEntity[i].mFlag);}
            for(unsigned mode=0;mode<2;++mode){unsigned selected=bsp.mMapEntitiesListNum;
                for(unsigned i=0;i<bsp.mMapEntitiesListNum;++i){const unsigned id=bsp.mMapEntitiesList[i].ID;const auto& row=bsp.mEntityList[id];if(row.IsFileExist&&!row.IsParticle&&(row.Flag&0x40u)&&bool(sourceShaders[id])==bool(mode)){selected=i;break;}}
                check(selected<bsp.mMapEntitiesListNum&&selected<=65535,"real placed lit entity132");const auto& instance=bsp.mMapEntitiesList[selected];auto& entity=bsp.mEntity[instance.ID];
                const float span=max(20.f,max(entity.mBBMax[0]-entity.mBBMin[0],max(entity.mBBMax[1]-entity.mBBMin[1],entity.mBBMax[2]-entity.mBBMin[2]))*std::fabs(instance.Scale));
                D3DXVECTOR3 at(instance.Pos[0],instance.Pos[1]+span*.25f,instance.Pos[2]),eye(at.x,at.y+span*.2f,at.z-span*2),up(0,1,0);D3DXMATRIX view;D3DXMatrixLookAtLH(&view,&eye,&at,&up);
                state->mNear=1;state->mFar=100000;state->mFov=.6f;state->mAsfectRatio=4.f/3;state->mIsFog=FALSE;level.SetViewMatrix(&view);D3DXMatrixPerspectiveFovLH(&state->mMatProj,state->mFov,state->mAsfectRatio,state->mNear,state->mFar);device->SetTransform(D3DTS_VIEW,&view);device->SetTransform(D3DTS_PROJECTION,&state->mMatProj);
                Vector3f cameraPos={eye.x,eye.y,eye.z};level.SetCameraPos(cameraPos);
                //Supply the inverse view normally published by the camera owner;
                //CLevel::SetViewMatrix alone deliberately does not publish it.
                D3DXMatrixInverse(&state->mInvMatView,nullptr,&state->mMatView);D3DXMatrixMultiply(&state->mMatViewProj,&state->mMatView,&state->mMatProj);level.FrameMove();
                //The normal visibility/fade queue supplies instance.Color.
                //Calling RenderOne directly before that queue would draw alpha0.
                check(SUCCEEDED(device->BeginScene()),"owner queue132");level.DrawMapRender();level.DrawMapEntitiesRender();check(SUCCEEDED(device->EndScene()),"owner queue complete132");
                check((instance.Color>>24)!=0,"real visibility queue selected entity132");
                check(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET|D3DCLEAR_ZBUFFER,0xff102030,1,0))&&SUCCEEDED(device->BeginScene()),"owner frame132");frameIndex130=frames;shaderBytes130=stride130=0;samples125.clear();
                {Hook130 observer(device);bsp.RenderOneEntityRender(WORD(selected));}check(SUCCEEDED(device->EndScene())&&!samples125.empty(),"ordinary BSP entity draw132");
                char frame[64];std::sprintf(frame,"owner-%u-%u.bgra",allowed,mode);const unsigned pixels=capture(frame);
                std::fprintf(trace,"{\"kind\":\"draw\",\"allowed\":%u,\"source_shader\":%u,\"id\":%u,\"instance\":%u,\"entity_flag\":%u,\"draws\":%u,\"pixels\":%u,\"shader_bytes\":%u,\"stride\":%u,\"color_op\":%u}\n",allowed,sourceShaders[instance.ID],instance.ID,selected,entity.mFlag,unsigned(samples125.size()),pixels,shaderBytes130,stride130,samples125.front().stage[0]);++frames;
            }
        }
        land.Destroy();g_pCamera=nullptr;
    }
    std::fclose(trace);g_MainApp.ReleaseR3D3D();ReleaseR3Engine();FILE* result=std::fopen("result.json","wb");check(result!=nullptr,"result132");std::fprintf(result,"{\"status\":\"PASS\",\"frames\":%u,\"warnings\":%u,\"full_gameplay\":false}\n",frames,warnings);std::fclose(result);return 0;
}
int main(){try{return run132();}catch(const std::exception& e){std::fprintf(stderr,"owner132:%s\n",e.what());return 1;}}
