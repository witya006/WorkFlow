#define RF455_GRADE_OVERLAY_NO_MAIN
#include "client455_grade_overlay_probe.cpp"
#include "client455_player_equipment.h"
#include "client455_equipment_draw_lifecycle.h"

namespace {
LONG WINAPI crash149(EXCEPTION_POINTERS* fault){std::fprintf(stderr,"Own probe exception%08lx RVA%08lx EAX%08lx ECX%08lx EDX%08lx\n",fault->ExceptionRecord->ExceptionCode,DWORD(reinterpret_cast<std::uintptr_t>(fault->ExceptionRecord->ExceptionAddress)-reinterpret_cast<std::uintptr_t>(GetModuleHandleA(nullptr))),fault->ContextRecord->Eax,fault->ContextRecord->Ecx,fault->ContextRecord->Edx);std::fflush(stderr);return EXCEPTION_EXECUTE_HANDLER;}
class DrawEquipment149:public RF455PlayerEquipmentObject {
public:
    void white(){std::memset(&m_d3dMaterial,0,sizeof m_d3dMaterial);m_d3dMaterial.Diffuse={1,1,1,1};m_d3dMaterial.Ambient={1,1,1,1};}
};
void pose149(CMesh* model){D3DXMATRIX identity;D3DXMatrixIdentity(&identity);for(unsigned i=0;i<model->m_MaxObj;++i){auto& node=model->m_pMesh[i];node.m_MatResult=identity;for(unsigned j=0;j<node.m_BlendNum;++j)node.m_pMatBlend[j]=identity;}}
unsigned changed149(const std::vector<DWORD>& before,const std::vector<DWORD>& after){require(before.size()==after.size(),"Equal images");unsigned changed=0;for(unsigned i=0;i<before.size();++i)changed+=(before[i]&0xffffff)!=(after[i]&0xffffff);return changed;}
int runDraw149(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    SetUnhandledExceptionFilter(crash149);std::fprintf(stderr,"Equipment draw:setup\n");
    require(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"Nation/language");InitR3Engine();
    auto* state=GetR3State();state->mScreenXsize=640;state->mScreenYsize=480;state->mbFullScreen=FALSE;ForceFullScreen();
    require(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"Actual D3D");
    require(_CreateCharIF(GetD3dDevice())&&_CreateBoneMgr()&&_CreateMeshMgr()&&_CreateAnimationMgr()&&_CreateBoundBoxMgr(),"Actual model owners");
    require(RF455_GameItems().loadItemFiles()&&RF455_GradeOverlays455().Load455(),"Real Item47andgrade resources");
    std::fprintf(stderr,"Equipment draw:resources\n");
    unsigned primaryCalls=0,overlayCalls=0,matrixCalls=0,changedPixels=0,visible=0,queued=0,paletteCases=0,metadataCases=0;
    {
        CCharResDataMgr catalog;require(catalog.LoadData(),"Real nine-group catalog");FILE* fixture=std::fopen("expected.bin","rb");require(fixture,"Actual equipment fixture");char magic[4];require(std::fread(magic,1,4,fixture)==4&&!std::memcmp(magic,"EQ45",4),"Fixture signature");
        const auto plans=word(fixture);require(!std::fseek(fixture,long(plans*sizeof(PlanCase)),SEEK_CUR),"Skip plans");const auto count=word(fixture);std::vector<RealCase> cases(count);require(std::fread(cases.data(),sizeof(RealCase),count,fixture)==count,"Actual model cases");std::fclose(fixture);
        const RealCase* selected=nullptr;for(const auto& c:cases)if(c.type==1&&c.race==0){selected=&c;break;}require(selected,"Actual Bellato equipment");
        FILE* metadata=std::fopen("render-metadata.bin","rb");require(metadata,"Independent raw metadata fixture");const auto metadataCount=word(metadata);bool wideKey=false;
        for(unsigned n=0;n<metadataCount;++n){DWORD c[6];require(std::fread(c,4,6,metadata)==6,"Metadata case");RF455EquipmentObject object;auto* item=RF455_GameItems().create(0,BYTE(c[0]),c[1]);require(item,"Real unit/siege payload");object.SetItem455(item);
            require(object.UnitPart455()==c[4]&&object.EffectListKey455()==c[5],"Actual DWORD key andunitpart versusrawEDF oracle");wideKey|=object.EffectListKey455()>255;
            auto* value=dynamic_cast<RF455BasicItem*>(item);require(value&&value->recordBytes().size==200,"Actual normal grade record");auto* bytes=const_cast<unsigned char*>(value->recordBytes().data);const BYTE before=bytes[113];bytes[113]=37;require(object.EffectGrade455()==37,"Virtualgradeisnotboolean");bytes[113]=before;++metadataCases;
        }require(wideKey&&std::fgetc(metadata)==EOF,"Nontruncatedkeyandmetadataextent");std::fclose(metadata);
        std::fprintf(stderr,"Equipment draw:catalog\n");DrawEquipment149 equipment;require(equipment.Create455(BYTE(selected->type),selected->index),"Actual equipment object");auto* payload=RF455_GameItems().create(0,BYTE(selected->type),selected->index);require(payload,"Actual item owner");equipment.SetItem455(payload);
        auto* normal=dynamic_cast<RF455BasicItem*>(payload);require(normal&&normal->recordBytes().size==200,"Actual normal payload");
        auto* model=equipment.GetMesh455();require(model&&model->m_Load,"Loaded actual model");pose149(model);equipment.white();std::fprintf(stderr,"Equipment draw:model\n");equipment.SetPosition(0.0f,0.0f,0.0f);equipment.SetRotY(0.0f);equipment.PrepareOverlaySlot455(1);
        require(equipment.GetOverlayGrade455()==0&&equipment.EffectGrade455()==normal->recordBytes().data[113],"Distinct overlay andvirtualgrade producers");
        for(BYTE slot:{BYTE(6),BYTE(7)}){equipment.PrepareOverlaySlot455(slot);require(equipment.GetOverlayGrade455()==normal->rawMetadata().data[152],"Actual slots6/7readmetadata152");}
        equipment.PrepareOverlaySlot455(1);
        D3DXMATRIX view,projection;D3DXVECTOR3 eye(0,5,-25),at(0,5,0),up(0,1,0);D3DXMatrixLookAtLH(&view,&eye,&at,&up);D3DXMatrixPerspectiveFovLH(&projection,.78539816f,640.0f/480.0f,.1f,500);
        state->mMatView=view;state->mMatProj=projection;D3DXMatrixMultiply(&state->mMatViewProj,&view,&projection);auto* device=GetD3dDevice();device->SetTransform(D3DTS_VIEW,&view);device->SetTransform(D3DTS_PROJECTION,&projection);
        D3DLIGHT9 light={};light.Type=D3DLIGHT_DIRECTIONAL;light.Diffuse={1,1,1,1};light.Ambient={1,1,1,1};light.Direction.z=1;_GetCharIF()->SetLight(light);
        GradeDrawHook observation(device);
        auto frame=[&](const char* name,const D3DXMATRIX* matrix){_GetCharIF()->SetState();require(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET|D3DCLEAR_ZBUFFER,0xff101010,1,0))&&SUCCEEDED(device->BeginScene()),"Actual frame begin");gradeDrawCalls=0;require(matrix?equipment.Render455(*matrix):equipment.Render(),"Actual equipment render wrapper");require(SUCCEEDED(device->EndScene()),"Actual frame completed");return pixelsGrade(device,name);};
        std::fprintf(stderr,"Equipment draw:frames\n");const auto base=frame("equipment-base.png",nullptr);primaryCalls=gradeDrawCalls;require(primaryCalls>0,"Primary actual geometry submitted");
        for(DWORD p:base)if((p&255)>16||((p>>8)&255)>16||((p>>16)&255)>16)++visible;require(visible>0,"Primary actual model isvisible");
        equipment.SetOverlayGrade455(2);const auto overlay=frame("equipment-overlay.png",nullptr);overlayCalls=gradeDrawCalls;changedPixels=changed149(base,overlay);
        require(overlayCalls==primaryCalls*2&&changedPixels>0,"Source wrapper addsreal secondary geometry andvisible glow");
        D3DXMATRIX world,rotation,swap(1,0,0,0,0,0,1,0,0,1,0,0,0,0,0,1);D3DXMatrixRotationZ(&rotation,D3DXToRadian(180.0f));D3DXMatrixMultiply(&world,&rotation,&swap);
        frame("equipment-matrix.png",&world);matrixCalls=gradeDrawCalls;require(matrixCalls==primaryCalls,"Target matrix route hasno overlay geometry");
        equipment.SetOverlayGrade455(0);equipment.Enable(4);equipment.SetAlphaDensity(.4f);frame("equipment-alpha.png",nullptr);require(model->m_Alpha==1,"Actual alpha restoredafter wrapper");equipment.Disable(4);
        equipment.Disable(2);gradeDrawCalls=0;require(!equipment.Render()&&gradeDrawCalls==0,"Disabledmeshguard");equipment.Enable(2);equipment.Enable(4096);require(!equipment.Render()&&gradeDrawCalls==0,"Clippedmeshguard");equipment.Disable(4096);
        equipment.SetFade455(3);gradeDrawCalls=0;require(equipment.Render()&&gradeDrawCalls==0,"Fade3successwithoutgeometry");equipment.SetFade455(2,2);frame("equipment-fade.png",nullptr);require(equipment.GetFadeFrame455()==1,"Render advancesfade");frame("equipment-fade-done.png",nullptr);require(equipment.GetFade455()==4&&equipment.GetFadeFrame455()==2,"Render reachesfullfade");
        RF455EquipmentEffectQueue queue;const BYTE references=payload->header().references;
        //Independent flat cache uses the physical4-matrix node stride from ASM.
        //Five palettes deliberately alias the next node;the original count is
        //restored before resource destruction. No asset file is modified.
        require(model->m_MaxObj>=2&&model->m_MaxObj<63,"Real model suitsqueue boundaryfixture");std::vector<DWORD> counts(model->m_MaxObj);for(unsigned i=0;i<model->m_MaxObj;++i)counts[i]=model->m_pMesh[i].m_BlendNum;
        const unsigned nodes=model->m_MaxObj;std::vector<D3DXMATRIX> oracle(nodes*4+30);model->m_pMesh[0].m_BlendNum=5;
        for(unsigned i=0;i<nodes;++i){auto& node=model->m_pMesh[i];for(unsigned p=0;p<(node.m_BlendNum?node.m_BlendNum:1);++p){auto* value=node.m_BlendNum?&node.m_pMatBlend[p]:&node.m_MatResult;for(unsigned n=0;n<16;++n)value->m[n/4][n%4]=float(1000*i+100*p+n);std::memcpy(&oracle[i*4+p],value,64);}}
        queue.Add455(&equipment);require(queue.Count455()==1&&payload->header().references==BYTE(references+1),"Actual queue retainsrealpayload");
        for(unsigned i=0;i<nodes;++i){auto& node=model->m_pMesh[i];std::memset(&node.m_MatResult,0,64);std::memset(node.m_pMatBlend,0,sizeof node.m_pMatBlend);}
        require(queue.Render455()&&queue.Start455()==1,"Actual queue restoresandinvokes effectrender");
        for(unsigned i=0;i<nodes;++i){auto& node=model->m_pMesh[i];for(unsigned p=0;p<(node.m_BlendNum?node.m_BlendNum:1);++p){require(!std::memcmp(node.m_BlendNum?static_cast<void*>(&node.m_pMatBlend[p]):static_cast<void*>(&node.m_MatResult),&oracle[i*4+p],64),"Actual queue pose versusindependent aliasoracle");++paletteCases;}node.m_BlendNum=counts[i];}
        require(queue.Render455()&&queue.Start455()==2,"Queue start persistsacrosscalls");queue.Clear455();require(!queue.Count455()&&!queue.Start455()&&payload->header().references==references,"Queue clearreleasesretainedpayload");
        RF455EquipmentObject unowned;require(unowned.Create455(BYTE(selected->type),selected->index)&&!unowned.GetItem455(),"Capacityfixturehasborrowedmeshandnopayload");
        for(unsigned i=0;i<257;++i)queue.Add455(&unowned);queued=queue.Count455();require(queued==256,"Queue cap256");queue.Clear455();require(payload->header().references==references,"CapacityfixturedoesnotwrapBYTEpayloadreferences");pose149(model);
        //The global queue is connected through the ordinary source entrypoints.
        RF455_EquipmentEffects455().Add455(&equipment);RF455_ClearEquipmentEffects455();require(!RF455_EquipmentEffects455().Count455(),"Ordinary clear adapter");
        require(RF455_GameItems().manager.size()==1,"Onlytheactualmodelpayloadremains");
    }
    RF455_ClearEquipmentEffects455();require(RF455_GameItems().manager.size()==0,"Allmodelpayloadsreleased");RF455_GradeOverlays455().Release455();
    require(_DestroyBoundBoxMgr()&&_DestroyAnimationMgr()&&_DestroyMeshMgr()&&_DestroyBoneMgr()&&_DestroyCharIF(),"Actual owners teardown");g_MainApp.ReleaseR3D3D();ReleaseR3Engine();
    FILE* result=std::fopen("result.json","wb");require(result,"Result");std::fprintf(result,"{\"status\":\"PASS\",\"primary_draws\":%u,\"overlay_draws\":%u,\"matrix_draws\":%u,\"visible_model_pixels\":%u,\"changed_overlay_pixels\":%u,\"actual_alpha_restore\":true,\"fade_render_gate\":true,\"queue_cap\":%u,\"queue_palette_oracles\":%u,\"metadata_cases\":%u,\"unit_key_not_BYTE\":true,\"virtualgrade_not_boolean\":true,\"queue_four_matrix_aliasing\":true,\"queue_shared_payload_teardown\":true,\"actual_nonzero_particle_effects\":false,\"full_player_appearance\":false}\n",primaryCalls,overlayCalls,matrixCalls,visible,changedPixels,queued,paletteCases,metadataCases);std::fclose(result);return 0;
}
}
int main(){try{return runDraw149();}catch(const std::exception& e){std::fprintf(stderr,"Equipment render:%s\n",e.what());return 2;}}
