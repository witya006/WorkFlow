#define RF455_GRADE_OVERLAY_NO_MAIN
#include "client455_grade_overlay_probe.cpp"
#include "client455_equipment_conditions.h"
#include "client455_tagged_audio.h"
#include "addcodebyjang/cmagicscript.h"
#include "addcodebyjang/effectcore.h"
#include "client455_effect_positions.h"
#include "mss.h"

template<class Tag,typename Tag::Type Member>struct Access154{friend typename Tag::Type access154(Tag){return Member;}};
struct CurrentProc154{using Type=CBaseProc* CPlayer::*;friend Type access154(CurrentProc154);};template struct Access154<CurrentProc154,&CPlayer::m_pResProc>;
struct EmbeddedProc154{using Type=CPlayerProc CPlayer::*;friend Type access154(EmbeddedProc154);};template struct Access154<EmbeddedProc154,&CPlayer::m_clsPlayerProc>;
struct Combat154{using Type=CCombatState* CCharacter::*;friend Type access154(Combat154);};template struct Access154<Combat154,&CCharacter::m_pCombatState>;
struct AniInfo154{using Type=CCharAniInfo* CCharacter::*;friend Type access154(AniInfo154);};template struct Access154<AniInfo154,&CCharacter::m_pCharAniInfo>;
struct Interpolation154{using Type=ANI_IP_INFO* CResObject::*;friend Type access154(Interpolation154);};template struct Access154<Interpolation154,&CResObject::m_pAniIPInfo>;
struct Network154{using Type=CNetworkMgr CMainApp::*;friend Type access154(Network154);};template struct Access154<Network154,&CMainApp::m_cNetworkMgr>;
struct Packs154{using Type=CObjectPack* CObjectBoard::*;friend Type access154(Packs154);};template struct Access154<Packs154,&CObjectBoard::m_listItemPack>;
struct LevelText154{using Type=CGUIText CGUISkFcUnit::*;friend Type access154(LevelText154);};template struct Access154<LevelText154,&CGUISkFcUnit::m_cLevelStr>;
struct Sprites154{using Type=CSpriteMgr CMainApp::*;friend Type access154(Sprites154);};template struct Access154<Sprites154,&CMainApp::m_cSpriteMgr>;
struct CombatMode156{using Type=BYTE CCharacter::*;friend Type access154(CombatMode156);};template struct Access154<CombatMode156,&CCharacter::m_byCombatMode>;
struct PrevCombat156{using Type=BYTE CCharacter::*;friend Type access154(PrevCombat156);};template struct Access154<PrevCombat156,&CCharacter::m_byPrevCombatMode>;
struct SwitchCombat156{using Type=void(CPlayer::*)();friend Type access154(SwitchCombat156);};template struct Access154<SwitchCombat156,&CPlayer::SetAction_SwitchingCombatMode>;

static std::vector<unsigned char> read154(const char* name){std::ifstream file(name,std::ios::binary);require(bool(file),"Owner binary input");return {std::istreambuf_iterator<char>(file),std::istreambuf_iterator<char>()};}
static void phase154(const char* name){std::fprintf(stderr,"Owner154:%s\n",name);std::fflush(stderr);}
static LONG WINAPI crash154(EXCEPTION_POINTERS* fault){std::fprintf(stderr,"Owner154 fault%08lx RVA%08lx\n",fault->ExceptionRecord->ExceptionCode,DWORD(reinterpret_cast<std::uintptr_t>(fault->ExceptionRecord->ExceptionAddress)-reinterpret_cast<std::uintptr_t>(GetModuleHandleA(nullptr))));std::fflush(stderr);return EXCEPTION_EXECUTE_HANDLER;}
static int runOwner154(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);SetUnhandledExceptionFilter(crash154);
    require(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"Owner nation/language");InitR3Engine();auto* state=GetR3State();state->mScreenXsize=640;state->mScreenYsize=480;state->mbFullScreen=FALSE;ForceFullScreen();
    require(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"Owner actual D3D");
    auto* previousSprites=g_pUiSpriteMgr;g_pUiSpriteMgr=&(g_MainApp.*access154(Sprites154{}));
    require(_CreateCharIF(GetD3dDevice())&&_CreateBoneMgr()&&_CreateMeshMgr()&&_CreateAnimationMgr()&&_CreateBoundBoxMgr(),"Owner actual model managers");
    CLand scene;require(scene.Create()&&scene.GetLevel()==g_pLevel&&!g_pLevel->IsLoadedBsp(),"Actual pre-world level owner for player frame effects");
    require(RF455_GameItems().loadItemFiles(),"Owner actual item tables");auto sfBytes=read154("DataTable/SkillForce.edf");require(RF455_GameItems().skillForce.loadBaseEdf(sfBytes.data(),sfBytes.size()),"Owner actual SF data");
    auto& network=g_MainApp.*access154(Network154{});require(network.Create(),"Owner actual network state");
    RF455_PrepareTaggedAudio(state->SoundPath);state->mSoundOn=TRUE;SetGlobalWavVolume(0);require(InitR3SoundSystem(".\\Snd\\WaveList.spt"),"Owner real Miles");
    require(g_MainApp.TaggedAudio455().Open(".\\Snd\\WaveList.spt",state->SoundPath),"Owner real tagged audio");const float listener[3]={};g_MainApp.TaggedAudio455().SetListener(listener);
    RF455_RpkGroup effects;effects.LoadDirectory("Effect\\");require(effects.count==2,"Owner pinned effect archives");auto* previousGroup=RF455_GetResourceGroup();RF455_SetResourceGroup(&effects);CreateEffectsList("Effect/EffectEntityList.spt");CreateMagicSptList("Effect/MagicSptList.spt");
    unsigned draws=0,visible=0,withoutPixels=0;bool restored=false;
    {
        CCharResDataMgr catalog;require(catalog.LoadData(),"Owner actual catalog");
        auto& boards=*_GetGBM();boards.Create();auto* skills=dynamic_cast<CSkillBoard*>(boards.GetBoard(7));require(skills,"Owner actual skill board7");skills->Create(7,2,3);require(skills->AddPack(0)&&skills->AddPack(1),"Owner actual skill packs");
        CGUISkFcUnit skillIcon;
        RF455SkillForceItem* sf[2];
        for(unsigned n=0;n<2;++n){sf[n]=RF455_GameItems().manager.createSkillForce(RF455_GameItems().skillForce,0,n);require(sf[n],"Owner real skill payload");
            auto wrapper=std::unique_ptr<CBoardObject>(new CBoardObject);wrapper->SetItem455(sf[n]);require((skills->*access154(Packs154{}))[n].Add(BYTE(n),wrapper.get()),"Owner actual skill cache Add");wrapper.release();}
        sf[0]->SetIconBoard455(&skillIcon);
        auto avatar=std::unique_ptr<CAvatar>(new CAvatar);auto* previousAvatar=g_pAvatar;g_pAvatar=avatar.get();avatar->SetIndex(17);avatar->SetRace(0);avatar->SetPosition(0.0f,0.0f,0.0f);avatar->SetBone(0);
        auto* proc=dynamic_cast<CPlayerProc*>(avatar.get()->*access154(CurrentProc154{}));require(proc,"Owner embedded ordinary CPlayerProc");
        {
            std::srand(154);const int expected=std::rand();std::srand(154);
            std::unique_ptr<CCharacter> copy(avatar->Clone());auto* cloned=dynamic_cast<CAvatar*>(copy.get());require(cloned,"Actual Avatar Clone remains callable");
            auto& embedded=cloned->*access154(EmbeddedProc154{});
            require(cloned->*access154(CurrentProc154{})==proc&&embedded.GetPlayer()==avatar.get(),"Target clone preserves old processor/actor links");
            require(&embedded.Equipment455()!=&proc->Equipment455()&&&embedded.EquipmentConditions455()==&proc->EquipmentConditions455(),"Independent copied equipment storage andsame borrowed actor conditions");
            for(BYTE part=0;part<12;++part)require(&embedded.Equipment455().physical455(part)!=&proc->Equipment455().physical455(part),"Twelve independently copied member objects");
            require(std::rand()==expected,"Actual Avatar member copy consumes no constructor PRNG values");
            //The old Character copy/destructor also shares three separately
            //deleted pointers. Observe the aliases,then detach only this fixture
            //copy before cleanup. FullCharacter clone lifecycle is NOT accepted.
            require(cloned->GetCombatState()==avatar->GetCombatState()&&cloned->GetCharAniInfo()==avatar->GetCharAniInfo()&&cloned->*access154(Interpolation154{})==avatar.get()->*access154(Interpolation154{}),"Legacy Character owned-pointer aliases arestill explicit");
            cloned->*access154(Combat154{})=nullptr;cloned->*access154(AniInfo154{})=nullptr;cloned->*access154(Interpolation154{})=nullptr;
        }
        phase154("actual Avatar Clone passed");
        require(avatar->GetBone()&&avatar->GetBone()->m_Load,"Owner real player skeleton");_GetCharIF()->FrameMove(avatar->GetBone());
        for(BYTE part:{BYTE(0),BYTE(1),BYTE(2),BYTE(3),BYTE(4),BYTE(10)}){
            require(avatar->PutOnEquipment(part,0),"Ordinary numeric equipment producer");auto* object=avatar->GetEquipItem455(part);require(object&&object->GetOwner455()==avatar.get()&&object->GetItem455()&&object->GetItem455()->header().references==1,"Ordinary typed slot/payload/actor ownership");}
        auto* upgraded=dynamic_cast<RF455BasicItem*>(avatar->GetNormalItem455(1));require(upgraded,"Actual worn normal-item payload");
        const auto stateBefore=upgraded->recordBytes();const std::vector<unsigned char> upgradeBefore(stateBefore.data,stateBefore.data+stateBefore.size);
        for(BYTE value:{BYTE(0),BYTE(7),BYTE(160),BYTE(255)}){
            upgraded->SetUpgradeLevel455(value);const auto after=upgraded->recordBytes();require(after.size==200&&after.data[113]==value,"462170 preserves full upgrade BYTE");
            for(unsigned i=0;i<after.size;++i)if(i!=113)require(after.data[i]==upgradeBefore[i],"Upgrade setter changes only113");
        }
        upgraded->SetUpgradeLevel455(upgradeBefore[113]);
        CBaseProc& ordinary=*proc;ordinary.Animation();
        phase154("ordinary numeric producer andAnimation passed");
        {
            std::srand(155);const int expected=std::rand();std::srand(155);CPlayerProc copy(*proc);
            for(BYTE part:{BYTE(0),BYTE(1),BYTE(2),BYTE(3),BYTE(4),BYTE(10)}){auto* from=proc->GetEquipItem455(part);auto* to=copy.GetEquipItem455(part);
                require(to&&to!=from&&to->GetItem455()==from->GetItem455()&&to->GetOwner455()==avatar.get()&&to->GetItem455()->header().references==1,"Target member copy shares payload/owner without retaining");
                require(to->GetRandom455()==from->GetRandom455()&&to->GetMesh455()==from->GetMesh455(),"Copied mesh andrandom state");}
            require(std::rand()==expected,"Populated processor copy consumes no PRNG");
            //Fixture cleanup only:the target shallow copy's destructor releases
            //the shared payload. Restore a reference AFTER observing no-retain
            //so this observation does not retire the still-used original actor.
            for(BYTE part:{BYTE(0),BYTE(1),BYTE(2),BYTE(3),BYTE(4),BYTE(10)})copy.GetEquipItem455(part)->RetainSharedItem455();
        }
        phase154("populated member copy passed");
        for(BYTE part:{BYTE(0),BYTE(1),BYTE(2),BYTE(3),BYTE(4),BYTE(10)})require(avatar->GetResultMat(part,0),"Ordinary Animation populates actual actor part cache");
        avatar->SetLightColor(0xffffffff);D3DMATERIAL9 material={};material.Diffuse={1,1,1,1};material.Ambient={1,1,1,1};avatar->SetMaterial(&material);proc->MaterialEquipment455();
        auto* device=GetD3dDevice();D3DXMATRIX view,projection;D3DXVECTOR3 eye(0,8,-35),at(0,8,0),up(0,1,0);
        D3DXMatrixLookAtLH(&view,&eye,&at,&up);D3DXMatrixPerspectiveFovLH(&projection,.78539816f,640.0f/480.0f,.1f,500);state->mMatView=view;state->mMatProj=projection;D3DXMatrixMultiply(&state->mMatViewProj,&view,&projection);device->SetTransform(D3DTS_VIEW,&view);device->SetTransform(D3DTS_PROJECTION,&projection);
        D3DLIGHT9 light={};light.Type=D3DLIGHT_DIRECTIONAL;light.Diffuse={1,1,1,1};light.Ambient={1,1,1,1};light.Direction.z=1;_GetCharIF()->SetLight(light);GradeDrawHook observation(device);
        auto frame=[&](const char* name){_GetCharIF()->SetState();require(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET|D3DCLEAR_ZBUFFER,0xff101010,1,0))&&SUCCEEDED(device->BeginScene()),"Owner real frame begin");gradeDrawCalls=0;ordinary.Render();require(SUCCEEDED(device->EndScene()),"Owner ordinary render completed");return pixelsGrade(device,name);};
        const auto dressed=frame("player-owner-dressed.png");draws=gradeDrawCalls;for(DWORD p:dressed)visible+=((p&255)>16||((p>>8)&255)>16||((p>>16)&255)>16);require(draws&&visible,"Actual primary controller draws visible assembled parts");
        phase154("primary controller produced visible frame");
        require(avatar->CPlayer::PutOffEquipment(1)&&!avatar->GetEquipItem455(1),"Ordinary base-player removal clears primary slot");const auto bare=frame("player-owner-without-shirt.png");for(unsigned p=0;p<bare.size();++p)withoutPixels+=(bare[p]&0xffffff)!=(dressed[p]&0xffffff);require(withoutPixels,"Removing through ordinary base API changes real rendered model");
        require(avatar->PutOnEquipment(1,0),"Ordinary replacement producer");ordinary.Animation();avatar->SetLightColor(0xffffffff);proc->MaterialEquipment455();const auto again=frame("player-owner-restored.png");restored=again==dressed;require(restored,"Ordinary replace restores controlled frame");
        require(avatar->SetDefaultItem(BYTE(1),DWORD(0))&&avatar->PutOffEquipment(1),"Actual Avatar removal restores typed default clothing");
        require(avatar->GetEquipItem455(1)&&avatar->GetEquipItem455(1)->GetItem455()==avatar->GetDefaultItem455(1)->GetItem455()&&avatar->GetDefaultItem455(1)->GetItem455()->header().references==2,"Restored default andworn wrapper share the actual payload");
        //Controlled owned metadata selects the real equipment→Avatar→board→SF
        //producer. This is not a claim that all skill-board population is ported.
        require(avatar->CPlayer::PutOffEquipment(1),"Remove before changing owned metadata");auto metadata=RF455_GameItems().data.getItem(1,0);require(metadata.size>=196,"Owner option metadata");auto* own=const_cast<BYTE*>(metadata.data);BYTE saved[12];std::memcpy(saved,own+184,12);own[184]=1;own[185]=8;float bonus=2;std::memcpy(own+192,&bonus,4);
        require(avatar->PutOnEquipment(1,0)&&sf[0]->record().flag101==2&&sf[1]->record().flag101==2,"Real numeric producer updates SF payloads inboth actual packs");
        require(sf[0]->EffectiveLevel455()==2&&std::string((skillIcon.*access154(LevelText154{})).GetString())=="Lv 2","Real icon receives effective skill level");
        require(avatar->CPlayer::PutOffEquipment(1)&&!sf[0]->record().flag101&&!sf[1]->record().flag101,"Detached removal reverses actual board bonuses");std::memcpy(own+184,saved,12);require(avatar->PutOnEquipment(1,0),"Restore real metadata item");
        phase154("actual Avatar skillboard callback passed");
        require(avatar->PutOnEquipment(8,0),"Ordinary real cloak owner");auto* cloak=avatar->GetEquipItem455(8);require(cloak,"Owner typed cloak");cloak->SetPosition(7,9,11);proc->SetItemAnimation455(8,3);
        auto audio=g_MainApp.TaggedAudio455().Inspect(0x50006000);require(audio.sample&&AIL_3D_sample_status(static_cast<H3DSAMPLE>(audio.sample))==SMP_PLAYING&&audio.relative[0]==7&&audio.relative[1]==9&&audio.relative[2]==11,"Production owner plays real loop at equipment position");
        proc->SetItemAnimation455(8,4);auto* magic=GetMagicListFromID(cloak->AnimationMagic455());require(magic&&magic->mMagicPtr&&static_cast<CProcessMagic*>(magic->mMagicPtr)->mCreateType==17,"Production owner creates real Spine magic");ordinary.Animation();
        require(!avatar->PutOffEquipment(8)&&!avatar->GetEquipItem455(8),"Actual cloak removal returnsfalse after detaching when specialskill pack ismissing");ordinary.Animation();
        phase154("production cloak magic andMiles passed");
        require(avatar->PutOnEquipment(6,0)&&avatar->PutOnEquipment(7,0),"Actual transition weapon andshield");
        auto* transitionWeapon=avatar->GetEquipItem455(6);auto* transitionShield=avatar->GetEquipItem455(7);
        require(transitionWeapon&&transitionShield,"Both embedded equipment wrappers populated");
        const float savedFPS=g_fFPS;avatar->SetUnitMountState(UMS_MOUNT);
        for(float fps:{0.0f,61.75f,316.75f})for(BYTE mode:{BYTE(0),BYTE(1)}){
            g_fFPS=fps;avatar.get()->*access154(CombatMode156{})=mode;avatar.get()->*access154(PrevCombat156{})=BYTE(1-mode);
            (avatar.get()->*access154(SwitchCombat156{}))();
            BYTE maximum=BYTE(int(fps));if(!maximum)maximum=60;
            for(auto* object:{transitionWeapon,transitionShield}){
                require(object->GetFade455()==(mode?2:1)&&object->GetFadeFrame455()==(mode?0:maximum),"Mounted transition sets both real fade states withtruncated lowBYTE budget");
                object->SetFade455(4,31);
            }
            avatar.get()->*access154(PrevCombat156{})=mode;(avatar.get()->*access154(SwitchCombat156{}))();
            require(transitionWeapon->GetFade455()==4&&transitionShield->GetFade455()==4,"Unchanged combat state performs no fade write");
        }
        g_fFPS=savedFPS;avatar->SetUnitMountState(UMS_DISMOUNT);
        avatar->CPlayer::PutOffEquipment(6);avatar->CPlayer::PutOffEquipment(7);
        phase154("actual mounted combat-mode weapon/shield transitions passed");
        sf[0]->SetIconBoard455(nullptr);g_pAvatar=previousAvatar;avatar.reset();
        //These wrappers were inserted through the actual pack cache,without
        //constructing the unported fullskill-window population. Match that
        //allocation route for cleanup instead ofcalling its uninitialised UI.
        for(BYTE pack=0;pack<skills->GetMaxPackNum();++pack)(skills->*access154(Packs154{}))[pack].Clear();
    }
    require(RF455_GameItems().manager.size()==0,"Owner all payload/cache references released");ResetEffectManager();DestroyEffectsList();DestroyMagicSptList();RF455_SetResourceGroup(previousGroup);effects.Release();g_MainApp.TaggedAudio455().Close();RF455_CloseEquipmentSounds455();ReleaseR3SoundSystem();network.Destroy();
    require(scene.Destroy(),"Actual pre-world scene teardown");
    require(_DestroyBoundBoxMgr()&&_DestroyAnimationMgr()&&_DestroyMeshMgr()&&_DestroyBoneMgr()&&_DestroyCharIF(),"Owner resource teardown");g_pUiSpriteMgr=previousSprites;g_MainApp.ReleaseR3D3D();ReleaseR3Engine();
    FILE* output=std::fopen("result.json","wb");require(output,"Owner result");
    std::fprintf(output,"{\"status\":\"PASS\",\"primary_typed_controller_connected\":true,"
        "\"ordinary_numeric_puton_baseputoff\":true,\"actual_Avatar_default_restore\":true,\"upgrade_BYTE_only113\":true,\"actual_mounted_weapon_shield_transition\":true,\"combat_transition_lowBYTE_FPS\":true,"
        "\"actual_actor_part_cache\":true,\"real_controlled_draws\":%u,\"visible_pixels\":%u,"
        "\"removal_changes_pixels\":%u,\"replacement_restores_frame\":%s,\"controlled_camera_and_lighting\":true,"
        "\"independent_member_copy_raw_links_no_rand_or_retain\":true,"
        "\"clone_cleanup_compensated_only_in_fixture\":true,\"full_Character_clone_lifecycle\":false,"
        "\"real_equipment_Avatar_skillboard_payload_icon_route\":true,\"controlled_owned_option_metadata\":true,"
        "\"production_cloak_magic_and_Miles\":true,\"cloak_missing_specialskill_returnsfalse_after_detach\":true,"
        "\"legacy_mixed_consumers_complete\":false,\"full455_UI\":false,\"full_player_appearance_or_selection\":false,\"full_client\":false}\n",
        draws,visible,withoutPixels,restored?"true":"false");std::fclose(output);return 0;
}
int main(){try{return runOwner154();}catch(const std::exception& error){std::fprintf(stderr,"Owner154:%s\n",error.what());std::fflush(stderr);ExitProcess(2);}}
