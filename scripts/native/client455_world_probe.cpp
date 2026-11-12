#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "item/citemmgr.h"
#include "input/imeedit.h"
#include "baseheader.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "mainapp.h"
#include "client455_camera.h"
#include "jerror.h"
#include "jmalloc.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <stdexcept>
#include <cmath>
#include <memory>
extern CMainApp g_MainApp;
template<class Tag,typename Tag::Type Member>struct MemberAccess{friend typename Tag::Type access(Tag){return Member;}};
struct VertexCount{using Type=DWORD CBsp::*;friend Type access(VertexCount);};template struct MemberAccess<VertexCount,&CBsp::mCVertexNum>;
struct FaceCount{using Type=DWORD CBsp::*;friend Type access(FaceCount);};template struct MemberAccess<FaceCount,&CBsp::mCFaceNum>;
static unsigned warnings=0;
static void check(bool value,const char* why){if(!value)throw std::runtime_error(why);}
static void phase(const char* value){std::fprintf(stderr,"phase:%s\n",value);std::fflush(stderr);}
static void errorMessage(char* value){std::fprintf(stderr,"engine-error:%s\n",value);std::fflush(stderr);std::exit(2);}
static void warningMessage(char* value){if(warnings++<16)std::fprintf(stderr,"engine-warning:%s\n",value);}
static unsigned capture(const char* filename){
    IDirect3DSurface9 *target=nullptr,*memory=nullptr;auto* device=GetD3dDevice();check(SUCCEEDED(device->GetRenderTarget(0,&target)),"target");D3DSURFACE_DESC desc={};target->GetDesc(&desc);
    check(SUCCEEDED(device->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&memory,nullptr)),"surface");check(SUCCEEDED(device->GetRenderTargetData(target,memory)),"readback");D3DLOCKED_RECT lock={};check(SUCCEEDED(memory->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"lock");
    D3DVIEWPORT9 viewport={};device->GetViewport(&viewport);check(viewport.Width==640&&viewport.Height==480,"viewport");FILE* out=std::fopen(filename,"wb");check(out!=nullptr,"frame");unsigned pixels=0;
    for(unsigned y=viewport.Y;y<viewport.Y+480;++y){auto* row=reinterpret_cast<const DWORD*>(static_cast<const BYTE*>(lock.pBits)+y*lock.Pitch)+viewport.X;std::fwrite(row,4,640,out);for(unsigned x=0;x<640;++x)pixels+=(row[x]&0xffffff)!=0x102030;}
    std::fclose(out);memory->UnlockRect();memory->Release();target->Release();return pixels;
}
static int run(const char* race, bool transition){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);phase("init");InitR3Engine();SetErrorMessageProc(errorMessage);SetWarningMessageProc(warningMessage);
    auto* state=GetR3State();state->mScreenXsize=640;state->mScreenYsize=480;state->mbFullScreen=FALSE;ForceFullScreen();
    std::strcpy(state->MapPath,".\\Map\\");std::strcpy(state->EntityPath,".\\Map\\Entity\\");
    check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"D3D init");phase("device-ready");
    char path[260];std::sprintf(path,".\\Map\\%s\\%s.bsp",race,race);unsigned pixels=0,vertices=0,faces=0,leaves=0,materials=0,entities=0;const auto memoryBefore=GetDmallocSize();unsigned memoryLoaded=0,memoryReloaded=0,memoryAfter=0;BOOL collision=FALSE;float height=0;short spawnLeaf=-1;
    {
        CCamera gameCamera;g_pCamera=&gameCamera;std::unique_ptr<CLand> land(new CLand);check(land->Create()!=0,"actual land Create");phase("before-level-load");check(land->LoadLevel(path)!=0,"actual land LoadLevel");CLevel& level=*land->GetLevel();check(g_pLevel==&level,"actual global level binding");phase("after-level-load");memoryLoaded=GetDmallocSize();
        check(level.IsLoadedBsp()&&level.mBsp->IsLoaded(),"loaded flags");vertices=level.mBsp->*access(VertexCount{});faces=level.mBsp->*access(FaceCount{});leaves=level.mBsp->mLeafNum;materials=level.mBsp->GetMatGroupNum();entities=level.mBsp->mMapEntitiesListNum;
        check(vertices&&faces&&leaves&&materials,"real geometry counts");
        Vector3f spawn={2466,277,-1129};if(!std::strcmp(race,"cora")){spawn[0]=2491;spawn[1]=491;spawn[2]=-3978;}else if(!std::strcmp(race,"accretia")){spawn[0]=-4295;spawn[1]=-296;spawn[2]=165;}
        spawnLeaf=level.mBsp->GetLeafNum(spawn);check(spawnLeaf>=0&&unsigned(spawnLeaf)<leaves,"actual spawn leaf");collision=level.GetNextYpos(spawn,&height);check(!collision||std::isfinite(height),"actual collision height finite");
        CAniCamera camera;std::sprintf(path,".\\Map\\%s\\%s.cam",race,race);camera.LoadAniCamera(path);check(camera.IsLoadedAniCamera(),"real intro camera");camera.SetPrePlayCamera(0,_CAM_PLAY_FULL_FRAME,_CAM_PLAY_FULL_FRAME,_CAM_FLAG_FINAL_STOP);
        float matrix[4][4];check(camera.PlayAniCamera(matrix,1,TRUE),"camera first frame");D3DXMATRIX inverse;check(D3DXMatrixInverse(&inverse,nullptr,reinterpret_cast<D3DXMATRIX*>(matrix))!=nullptr,"camera inverse");Vector3f position={inverse._41,inverse._42,inverse._43};level.SetCameraPos(position);level.SetViewMatrix(reinterpret_cast<D3DXMATRIX*>(matrix));phase("before-frame");
        auto draw=[&](CLevel& loaded,const char* image){loaded.SetCameraPos(position);loaded.SetViewMatrix(reinterpret_cast<D3DXMATRIX*>(matrix));R3CalculateTime();loaded.FrameMove();auto* device=GetD3dDevice();check(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET|D3DCLEAR_ZBUFFER,0xff102030,1,0)),"clear");check(SUCCEEDED(device->BeginScene()),"begin");loaded.DrawSkyBoxRender();loaded.DrawMapRender();loaded.DrawMapEntitiesRender();check(SUCCEEDED(device->EndScene()),"end");return capture(image);};
        pixels=draw(level,"world.bgra");check(pixels>100,"actual map pixels");phase("captured");
        camera.ReleaseAniCamera();std::sprintf(path,".\\Map\\%s\\%s.bsp",race,race);check(land->LoadLevel(path)!=0,"actual owner reload");memoryReloaded=GetDmallocSize();check(land->GetLevel()==g_pLevel&&g_pLevel->IsLoadedBsp()&&g_pLevel->mBsp->mLeafNum==leaves,"reloaded binding/geometry");check(draw(*g_pLevel,"world-reload.bgra")>100,"real GPU render after owner reload");phase("reloaded");
        if (transition) {
            const auto* previous = land->GetLevel();
            const auto previousMemory = GetDmallocSize();
            char missing[] = ".\\Map\\missing\\missing.bsp";
            char unsupported[] = ".\\Map\\missing\\missing.ins";
            char truncated[] = ".\\Map\\preflight-truncated\\preflight-truncated.bsp";
            char next[] = ".\\Map\\neutralB\\neutralB.bsp";
            auto& maps = const_cast<RF455MapData&>(land->MapData455());
            maps.count = 2;
            maps.maps.reset(new RF455MapInfo[maps.count]);
            std::strcpy(maps.maps[0].pFileName, truncated);
            std::strcpy(maps.maps[1].pFileName, next);
            check(!land->CanLoadMap455(0) && land->CanLoadMap455(1) &&
                  !land->CanLoadMap455(2), "indexed map preflight checks file and catalog bounds");
            for (auto* invalid : {missing, unsupported, truncated}) {
                check(!land->LoadLevel(invalid) && land->GetLevel() == previous &&
                      g_pLevel == previous && g_pLevel->IsLoadedBsp() &&
                      GetDmallocSize() == previousMemory, "rejected path keeps source terrain");
            }
            check(draw(*g_pLevel, "world-preserved.bgra") > 100, "source terrain still renders");
            check(land->LoadLevel(next) && land->GetLevel() != previous &&
                  g_pLevel == land->GetLevel() && g_pLevel->IsLoadedBsp() &&
                  !_stricmp(g_pLevel->GetMapName(), "neutralB"), "destination terrain published");
            char nextCamera[] = ".\\Map\\neutralB\\neutralB.cam";
            camera.LoadAniCamera(nextCamera);
            check(camera.IsLoadedAniCamera(), "destination camera");
            camera.SetPrePlayCamera(0, _CAM_PLAY_FULL_FRAME, _CAM_PLAY_FULL_FRAME, _CAM_FLAG_FINAL_STOP);
            check(camera.PlayAniCamera(matrix, 1, TRUE) &&
                  D3DXMatrixInverse(&inverse, nullptr, reinterpret_cast<D3DXMATRIX*>(matrix)),
                  "destination view matrix");
            position[0] = inverse._41;
            position[1] = inverse._42;
            position[2] = inverse._43;
            check(draw(*g_pLevel, "world-destination.bgra") > 100, "destination terrain renders");
            camera.ReleaseAniCamera();
        }
        check(land->Destroy()!=0&&!g_pLevel,"actual owner release/global clearing");memoryAfter=GetDmallocSize();check(memoryLoaded==memoryReloaded&&memoryAfter==memoryBefore,"same-map reload and allocator release balance");char unsupported[]="owned-domain.InS";check(!land->LoadLevel(unsupported)&&!g_pLevel,"missing INS provider explicitly refused");g_pCamera=nullptr;phase("released");
    }
    g_MainApp.ReleaseR3D3D();ReleaseR3Engine();FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"result");
    std::fprintf(out,"{\"status\":\"PASS\",\"vertices\":%u,\"faces\":%u,\"leaves\":%u,\"materials\":%u,\"map_entities\":%u,\"pixels\":%u,\"warnings\":%u,\"actual_land_owner\":true,\"reload_and_global_clear\":true,\"memory_before\":%u,\"memory_loaded\":%u,\"memory_reloaded\":%u,\"memory_after\":%u,\"spawn_leaf\":%d,\"spawn_collision\":%s,\"spawn_height\":%.9g,\"INS_provider_refused\":true,\"full_ILevel\":false,\"full_Tutorial\":false",vertices,faces,leaves,materials,entities,pixels,warnings,unsigned(memoryBefore),memoryLoaded,memoryReloaded,memoryAfter,int(spawnLeaf),collision?"true":"false",double(height));
    if (transition) std::fputs(",\"destination\":\"neutralB\",\"rejected_paths\":3,\"preserved_source_frame\":true,\"destination_frame\":true", out);
    std::fputs("}\n", out);std::fclose(out);return 0;
}
static LONG filter(EXCEPTION_POINTERS* info){if(info->ExceptionRecord->ExceptionCode==0xe06d7363)return EXCEPTION_CONTINUE_SEARCH;FILE* out=std::fopen("exception.json","wb");if(out){std::fprintf(out,"{\"code\":%lu,\"address\":%lu,\"rva\":%lu}",info->ExceptionRecord->ExceptionCode,reinterpret_cast<DWORD>(info->ExceptionRecord->ExceptionAddress),reinterpret_cast<DWORD>(info->ExceptionRecord->ExceptionAddress)-reinterpret_cast<DWORD>(GetModuleHandleA(nullptr)));std::fclose(out);}return EXCEPTION_EXECUTE_HANDLER;}
static int guarded(const char* race, bool transition){__try{return run(race,transition);}__except(filter(GetExceptionInformation())){return 99;}}
int main(int argc,char** argv){try{const bool transition=argc==3&&!std::strcmp(argv[2],"--transition");check(argc==2||transition,"race and optional transition argument");return guarded(argv[1],transition);}catch(const std::exception& error){std::fprintf(stderr,"World: %s\n",error.what());return 1;}}
