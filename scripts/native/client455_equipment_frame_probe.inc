// Actual frame/ANI/Miles/attachment fixture. Callback observations accompany
// real operations;this fixture does not stand in for the ordinary player host.
class FrameHost153:public RF455EquipmentAnimationCallbacks {
    EffectActor146& actor;Effects146& backend;
public:
    std::vector<DWORD> modes,lookups;
    explicit FrameHost153(EffectActor146& value,Effects146& effects):actor(value),backend(effects){}
    void itemAnimationEffect(RF455PlayerEquipmentObject& object,DWORD mode)override{
        modes.push_back(mode);RF455EquipmentEffectOwner owner;
        owner.object=&actor;owner.index=actor.GetIndex();owner.race=actor.GetRace();owner.position=actor.GetPosition();owner.yaw=actor.GetRotY();
        object.ProcessAnimationEffect455(mode,backend,owner);
    }
    CAniData* findItemAnimation(DWORD id)override{lookups.push_back(id);return _GetAniMgr()->GetAni(5,id);}
    void adjustOwnerHeight(RF455PlayerEquipmentObject&,bool)override{
        //The cases below never request a lift. Without a real current worn
        //mount provider a fabricated height must not become a successful test.
        throw std::logic_error("Frame fixture has no current worn mount");
    }
    bool pendingOwnerLift()const override{return false;} //C0C090 starts as zero.
    void clearPendingOwnerLift()override{throw std::logic_error("No pending lift was set in this fixture");}
};
static unsigned frameTransitions153=0;
class FrameEquipment153:public RF455PlayerEquipmentObject {
public:
    //Seed an already-established state to isolate the frame guard. Public
    //Enable/Disable separately delete always effects when hiding the object.
    void seedFrameFlags(DWORD add,DWORD remove){m_dwStatusFlag=(m_dwStatusFlag|add)&~remove;}
};
static void runEquipmentFrames153(Effects146& backend){
    require(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"Frame nation/language");
    auto* engine=GetR3State();engine->mScreenXsize=640;engine->mScreenYsize=480;engine->mbFullScreen=FALSE;ForceFullScreen();
    require(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"Frame actual D3D");
    require(_CreateCharIF(GetD3dDevice())&&_CreateBoneMgr()&&_CreateMeshMgr()&&_CreateAnimationMgr()&&_CreateBoundBoxMgr(),"Frame actual resource owners");
    require(RF455_GameItems().loadItemFiles(),"Frame actual item tables");
    auto* previousLocal=backend.local;auto* previousView=backend.view;backend.loops.open();
    {
        CCharResDataMgr catalog;require(catalog.LoadData(),"Frame actual resource catalog");
        auto actor=std::unique_ptr<EffectActor146>(new EffectActor146);actor->SetIndex(17);actor->SetRace(0);actor->SetPosition(20,40,60);actor->SetRotY(0,FALSE);actor->snapshot(0,0x10000000);
        auto* bone=_GetBoneMgr()->GetBone(0,0);require(bone&&bone->m_Load,"Frame actual player skeleton");actor->bind(bone,_GetBBoxMgr()->GetBoundBox(0,0));_GetCharIF()->FrameMove(bone);
        require(actor->SetDefaultItem(BYTE(1),DWORD(0)),"Frame ordinary Avatar default setter");
        auto* body=dynamic_cast<RF455PlayerEquipmentObject*>(actor->GetDefaultItem455(1));
        require(body&&body->IsMeshWrapperKind455(1)&&!body->IsMeshWrapperKind455(2),"Ordinary default owner is CEquip wrapper,not generic CMesh wrapper");
        auto* bodyMesh=body->GetMesh455();require(bodyMesh&&bodyMesh->m_Load,"Frame actual default body model");
        _GetCharIF()->RematchParent(bone,bodyMesh);_GetCharIF()->FrameMove(bodyMesh);require(actor->PSetVertexBlending(1,bodyMesh,TRUE),"Frame live actor pose cache");
        RF455EffectPositionView view;view.actor=actor.get();view.parts[1]={true,bodyMesh,nullptr};backend.local=actor.get();backend.view=&view;
        FrameEquipment153 object;require(object.Create455(8,0),"Frame real cloak model");
        auto* item=RF455_GameItems().create(0,8,0);require(item,"Frame real cloak payload");object.SetItem455(item);object.SetOwner455(actor.get());object.BindFrameOwner455(&view);object.SetPosition(7,9,11);
        FrameHost153 host(*actor,backend);require(object.SetEquipmentAnimation455(4,host),"Frame real cloak ANI selection");
        auto* ani=object.GetAnimation()->GetAniData();require(ani&&ani->m_Load&&ani->imported,"Frame real item ANI loaded");
        require(object.Animation(0x00ffffff)&&!object.GetAnimation()->IsAnimating(),"Actual ANI reaches its end through wrapper Animation");
        host.modes.clear();object.FrameMove();
        require(host.modes==std::vector<DWORD>{3}&&object.GetAnimationID()==3&&object.GetAnimation()->IsAnimating(),"Ended cloak mode4 enters actual loop3");
        const DWORD magic=object.AnimationMagic455();auto* effect=GetMagicListFromID(magic);
        require(effect&&effect->mMagicPtr&&object.AnimationSound455()==0x50006000,"Actual frame transition owns real magic andlooped sound");
        require(static_cast<CProcessMagic*>(effect->mMagicPtr)->mCreateType==10,"Frozen loop3 script uses actor position(create_type10)");
        actor->SetPosition(25,50,75);actor->SetRotY(90,FALSE);host.modes.clear();object.FrameMove();
        float expected[3];actor->GetPosition(expected);
        effect=GetMagicListFromID(magic);require(effect&&!std::memcmp(effect->mMat[3],expected,12)&&effect->mYAngle==90,"Frame loop10 follows actual actor position andyaw");
        require(host.modes.empty(),"Running loop has no spurious transition");
        //46D9B0 scans dummies once. Poison one value after first frame to
        //distinguish retention from blindly rebinding it every frame.
        RF455EquipmentDummyPoints points;points.bind(*object.GetMesh455());
        for(unsigned n=0;n<10;++n)require(object.GetDummy455(n)==points.get(n),"Actual first-frame dummy scan");
        object.SetDummy455(9,19);object.FrameMove();require(object.GetDummy455(9)==19,"Dummy binding is one shot");
        float at[3]={1,2,3};DWORD always=StartMagicEffect(at,0,0x50006004,nullptr,0);auto* permanent=GetMagicListFromID(always);require(permanent,"Actual always magic fixture");
        float retained[3];std::memcpy(retained,permanent->mMat[3],12);object.SetEffectID(0,always);object.FrameMove();
        require(permanent->mState==1&&!std::memcmp(permanent->mMat[3],retained,12),"CEquip wrapper enables always magic without ground jitter");
        require(SetMagicState(always,0),"Set actual always state for guard fixture");object.seedFrameFlags(4096,0);object.FrameMove();require(permanent->mState==0,"Clipped always-effect frame guard");object.seedFrameFlags(0,4096);
        object.seedFrameFlags(0,2);object.FrameMove();require(permanent->mState==0,"Disabled-render always-effect frame guard");object.seedFrameFlags(2,0);object.FrameMove();require(permanent->mState==1,"Visible always-effect restore");object.SetEffectID(0,0);
        {RF455EquipmentObject copy(object);require(copy.AnimationMagic455()==object.AnimationMagic455()&&copy.AnimationSound455()==object.AnimationSound455()&&!copy.IsMeshWrapperKind455(1),"Queue base copy retains event fields andhas generic discriminator");}
        auto sound=backend.audio.Inspect(object.AnimationSound455());require(sound.sample&&AIL_3D_sample_status(static_cast<H3DSAMPLE>(sound.sample))==SMP_PLAYING,"Destroying queue copy does not invent a sound stop");
        object.SetEquipmentAnimation455(4,host);const DWORD spineMagic=object.AnimationMagic455();auto* spine=GetMagicListFromID(spineMagic);
        require(spine&&spine->mMagicPtr&&static_cast<CProcessMagic*>(spine->mMagicPtr)->mCreateType==17,"Frozen use4 script attaches to actual Spine(create_type17)");
        actor->SetPosition(31,53,79);actor->SetRotY(180,FALSE);host.modes.clear();object.FrameMove();
        require(RF455_ResolveEffectPosition(expected,view,17).defined,"Frame expected live Spine position");spine=GetMagicListFromID(spineMagic);
        require(spine&&!std::memcmp(spine->mMat[3],expected,12)&&spine->mYAngle==180&&host.modes.empty(),"Frame use17 follows cached Spine position andyaw without premature transition");
        //These frozen branches are exercised on owned in-memory metadata;
        //they do not claim a real Siege visual or a complete player route.
        struct Transition{BYTE kind;DWORD from,to;};
        const Transition cases[]={
            {8,1,3},{8,4,3},{8,2,0},{8,5,0},
            {9,4,7},{9,5,0},{9,6,6},{9,7,0},{9,8,0},{9,9,0},{9,10,0},
            {46,4,7},{46,5,0},{46,6,6},{46,7,0},{46,8,0},{46,9,0},{46,10,0},
            {0,1,0},{0,3,0},{0,4,0}};
        auto* basic=dynamic_cast<RF455BasicItem*>(item);require(basic&&basic->rawMetadata().size>88,"Frame owned metadata");
        auto* kind=const_cast<BYTE*>(basic->rawMetadata().data)+88;const BYTE saved=*kind;
        for(const auto& c:cases){*kind=c.kind;object.GetAnimation()->SetAnimationID(c.from);object.GetAnimation()->Animating(FALSE);host.modes.clear();object.FrameMove();
            require(host.modes==std::vector<DWORD>{c.to},"Frame transition versus frozen target branch");++frameTransitions153;}
        *kind=saved;object.GetAnimation()->SetAnimationID(4);object.GetAnimation()->Animating(TRUE);host.modes.clear();object.FrameMove();require(host.modes.empty(),"Unfinished ANI does not transition");
        object.SetEquipmentAnimation455(3,host);require(object.AnimationMagic455(),"Actual magic before expiration");ResetEffectManager();object.BindFrameOwner455(nullptr);object.FrameMove();require(!object.AnimationMagic455(),"Missing magic clears ID without requiring an unused pose provider");
        object.SetEquipmentAnimation455(0,host);backend.loops.stopAll([&](DWORD id,DWORD tag){backend.audio.Stop(id,tag);});ResetEffectManager();actor->bind(nullptr,nullptr);backend.view=previousView;backend.local=previousLocal;
    }
    backend.loops.close();require(RF455_GameItems().manager.size()==0,"Frame all item owners released");
    require(_DestroyBoundBoxMgr()&&_DestroyAnimationMgr()&&_DestroyMeshMgr()&&_DestroyBoneMgr()&&_DestroyCharIF(),"Frame resource teardown");g_MainApp.ReleaseR3D3D();
    FILE* report=std::fopen("frame-result.json","wb");require(report,"Frame result output");
    std::fprintf(report,"{\"status\":\"PASS\",\"actual_Avatar_derived_default_owner\":true,\"actual_ANI_end_transition\":true,\"real_magic_follows_Spine_and_yaw\":true,\"sound_uses_equipment_position\":true,\"one_shot_dummy_binding\":true,\"current_wrappers_reject_ground_kind\":true,\"always_effect_has_no_ground_jitter\":true,\"copy_retains_event_fields_without_invented_stop\":true,\"frozen_transition_branches\":%u,\"branch_metadata_is_controlled_fixture\":true,\"ordinary_full_player_connected\":false,\"full_appearance\":false}\n",frameTransitions153);std::fclose(report);
}
