static int registeredCharacterChecks(CNetworkMgr& network,CNetProcess& process,_NET_BUFFER& send,_NET_BUFFER& receive){
    static_assert(sizeof(_reged_char_result_zone)==506,"455fixed response declaration");
    BYTE packet[506]={};packet[0]=0;packet[1]=3;for(unsigned i=2;i<14;++i)packet[i]=BYTE(0xa0+i);
    const auto put32=[](BYTE* p,std::uint32_t value){for(unsigned i=0;i<4;++i)p[i]=BYTE(value>>(8*i));};
    const auto put64=[](BYTE* p,std::uint64_t value){for(unsigned i=0;i<8;++i)p[i]=BYTE(value>>(8*i));};
    const std::uint64_t times[3]={0x200000005ull,0x100000066ull,0x100000064ull};
    for(unsigned i=0;i<3;++i){BYTE* row=packet+14+164*i;std::sprintf(reinterpret_cast<char*>(row),"fixture-%u",i);if(i==2){row[0]=0xb0;row[1]=0xa1;row[2]='2';row[3]=0;}put32(row+17,0x12340000+i);row[21]=BYTE(i);row[22]=BYTE(i);
        std::memcpy(row+23,"BFB0",5);row[28]=i?BYTE(10+i):0;put64(row+29,0x100000001ull+i);put64(row+37,0x200000003ull+i);
        for(unsigned j=0;j<16;++j)row[49+j]=255;for(unsigned j=0;j<83;++j)row[73+j]=BYTE(j+i);put64(row+156,times[i]);
    }
    RF455RegisteredCharacters previous;previous.result=71;previous.count=1;previous.records[0].dalant=999;
    for(unsigned bytes:{0u,1u,13u,14u,177u,178u,341u,342u,505u}){auto parsed=previous;REQUIRE(!RF455_ReadRegisteredCharacters(packet,bytes,parsed)&&parsed.result==71&&parsed.records[0].dalant==999);}
    auto parsed=previous;REQUIRE(!RF455_ReadRegisteredCharacters(nullptr,506,parsed)&&parsed.result==71);
    packet[1]=4;REQUIRE(!RF455_ReadRegisteredCharacters(packet,506,parsed)&&parsed.result==71);packet[1]=3;
    REQUIRE(RF455_ReadRegisteredCharacters(packet,506,parsed)&&parsed.count==3&&parsed.records[2].serial==0x12340002);
    REQUIRE(parsed.headerReserved[0]==0xa2&&parsed.records[2].dalant==0x100000003ll&&parsed.records[2].gold==0x200000005ll&&parsed.records[2].reserved[82]==84&&parsed.records[2].lastConnection==0x100000064ll);
    std::fputs("registered:parsed\n",stderr);std::fflush(stderr);
    REQUIRE(!g_pAvatarDummy&&!g_ifCharIF&&!g_pBoneMgr&&!g_pCharDataMgr&&!g_pItemDataMgr);
    REQUIRE(_CreateCharIF(GetD3dDevice())&&_CreateBoneMgr()&&_CreateMeshMgr()&&_CreateAnimationMgr()&&_CreateBoundBoxMgr()&&_CreateCharDataMgr()&&_CreateItemDataMgr());
    std::fputs("registered:owners\n",stderr);std::fflush(stderr);
    _CreateAvatarDummy();REQUIRE(g_pAvatarDummy);std::fputs("registered:avatars\n",stderr);std::fflush(stderr);
    (network.*access(Active{}))[0]=1;REQUIRE(network.SystemMsg_RegedCharRequest_zone());
    const auto request=take(send);RF455NetworkCodec peer;peer.initializeDefault(true);peer.receiveKey=process.m_codec455.sendKey;peer.sendKey=process.m_codec455.receiveKey;
    BYTE plain[64]={};std::size_t bytes=0;REQUIRE(peer.decode(request.data(),request.size(),plain,sizeof(plain),bytes)&&bytes==4&&plain[2]==1&&plain[3]==8);
    const auto oldResult=network.GetResultOfUserInfo();REQUIRE(!network.DispatchRegisteredCharacters455(reinterpret_cast<char*>(packet),505)&&network.GetResultOfUserInfo()==oldResult&&network.IsSendRequestMsg());
    BYTE wire[1024]={};std::size_t wireBytes=0;REQUIRE(peer.encode(0x0901,packet,506,wire,sizeof(wire),wireBytes));
    receive.m_dwPopPnt=receive.m_dwPushPnt=receive.m_capacity-1;receive.m_dwPopRot=receive.m_dwPushRot=0;
    push(receive,wire,2);(process.*access(Pop{}))(0);REQUIRE(network.IsSendRequestMsg()&&network.GetResultOfUserInfo()==oldResult);
    std::fputs("registered:before-receiver\n",stderr);std::fflush(stderr);
    push(receive,wire+2,wireBytes-2);(process.*access(Pop{}))(0);
    std::fputs("registered:after-receiver\n",stderr);std::fflush(stderr);
    REQUIRE(network.GetResultOfUserInfo()==0&&!network.IsSendRequestMsg()&&network.GetLastestAvatarIndex()==0);
    for(unsigned i=0;i<3;++i){auto* avatar=_GetAvatarDummy(i);REQUIRE(avatar->GetIndex()==i&&avatar->GetRace()==i);
        REQUIRE(avatar->GetLevel()==(i?10+i:1)&&avatar->GetSkipTutorial455()==(i?1:0));
        REQUIRE(avatar->GetDalant()==__int64(0x100000001ull+i)&&avatar->GetGold()==__int64(0x200000003ull+i));
        REQUIRE(!std::strcmp(avatar->GetName(),parsed.records[i].name));
    }
    // Invalid slots are skipped before actor mutation and timestamp selection.
    packet[14+164+22]=255;std::strcpy(reinterpret_cast<char*>(packet+14+164),"ignored");put64(packet+14+164+156,0x7fffffffffffffffull);
    REQUIRE(network.DispatchRegisteredCharacters455(reinterpret_cast<char*>(packet),506)&&network.GetLastestAvatarIndex()==0&&!std::strcmp(_GetAvatarDummy(1)->GetName(),"fixture-1"));
    // A zero-count reply retains existing actors and the previous latest slot.
    packet[1]=0;network.SendRequestMsg();REQUIRE(network.DispatchRegisteredCharacters455(reinterpret_cast<char*>(packet),506));
    REQUIRE(network.GetLastestAvatarIndex()==0&&_GetAvatarDummy(2)->GetIndex()==2&&!network.IsSendRequestMsg());
    std::fputs("registered:before-destroy\n",stderr);std::fflush(stderr);
    _DestroyAvatarDummy();REQUIRE(_DestroyItemDataMgr()&&_DestroyCharDataMgr()&&_DestroyBoundBoxMgr()&&_DestroyAnimationMgr()&&_DestroyMeshMgr()&&_DestroyBoneMgr()&&_DestroyCharIF());
    (network.*access(Active{}))[0]=0;
    FILE* out=std::fopen("registered-characters-result.json","wb");REQUIRE(out);
    std::fputs("{\"status\":\"PASS\",\"response_bytes\":506,\"record_stride\":164,\"actual_Avatar_records\":3,\"actual_request1_8\":true,\"actual_encrypted_receiver1_9\":true,\"fragment_wrap\":true,\"full64bit_money_time\":true,\"level0_tutorial_writer\":true,\"zero_count_retains_state\":true,\"bootstrap_or_visual_selection_accepted\":false}\n",out);std::fclose(out);return 0;
}
