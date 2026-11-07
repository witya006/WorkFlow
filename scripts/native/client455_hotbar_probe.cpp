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
#include "client455_hotbar.h"
#include <cstdio>
#include <cstring>
#include <memory>
#include <stdexcept>
#include <vector>
extern CMainApp g_MainApp;
template<class Tag,typename Tag::Type Member>struct MemberAccess{friend typename Tag::Type access(Tag){return Member;}};
#define FIELD(Tag,T,C,member) struct Tag{using Type=T C::*;friend Type access(Tag);};template struct MemberAccess<Tag,&C::member>;
FIELD(NetworkMember,CNetworkMgr,CMainApp,m_cNetworkMgr)
FIELD(SendBuffer,_NET_BUFFER*,CNetProcess,m_pSendBuffer)
FIELD(Owner,CNetWorking*,CNetProcess,m_pNetwork)
FIELD(Hover,CBoardObject*,CBoardManager,m_pHoverObject)
FIELD(Origin,BYTE,CBoardManager,m_byOrgBoardType)
FIELD(SfData,SF_DATA*,CSFItem,m_pData)
FIELD(ItemData,ITEM_DATA*,CBaseItem,m_pData)
FIELD(UploadTime,DWORD,CLinkBoard,m_hotbarUploadTime455)
static void check(bool value,const char* message){if(!value)throw std::runtime_error(message);}

struct PacketFixture {
    CNetworkMgr& network=g_MainApp.*access(NetworkMember{});
    CNetProcess& process=network.m_Process[0];
    _NET_BUFFER send;
    std::vector<char> scratch=std::vector<char>(1000000);
    CNetworkMgr* oldNetwork=g_pNetworkMgr;
    CAvatar* oldAvatar=g_pAvatar;
    _NET_BUFFER* oldSend=process.*access(SendBuffer{});
    CNetWorking* oldOwner=process.*access(Owner{});
    CBoardObject* oldHover=_GetGBM()->*access(Hover{});
    BYTE oldOrigin=_GetGBM()->*access(Origin{});
    FILE* packets=nullptr;unsigned count=0;
    PacketFixture(){
        g_pNetworkMgr=&network;g_pAvatar=nullptr;
        check(send.Configure(1000000,1000000,scratch.data()),"send ring");
        process.*access(SendBuffer{})=&send;process.*access(Owner{})=&network;
        process.m_nIndex=0;process.m_Type.m_wSocketMaxNum=1;process.m_codec455.initializeDefault(true);
        process.m_NetSocket.GetSocket(0)->m_bAccept=true;
        _GetGBM()->*access(Hover{})=nullptr;_GetGBM()->*access(Origin{})=255;
        packets=std::fopen("packets.txt","wb");check(packets!=nullptr,"packet trace");
    }
    ~PacketFixture(){
        if(packets)std::fclose(packets);
        process.m_NetSocket.GetSocket(0)->m_bAccept=false;
        process.*access(SendBuffer{})=oldSend;process.*access(Owner{})=oldOwner;
        _GetGBM()->*access(Hover{})=oldHover;_GetGBM()->*access(Origin{})=oldOrigin;
        g_pNetworkMgr=oldNetwork;g_pAvatar=oldAvatar;
    }
    std::vector<BYTE> take(){
        int bytes=0;bool missing=false;const auto* p=send.GetSendPoint(&bytes,&missing);
        if(!p||missing)return {};
        std::vector<BYTE> wire(p,p+bytes);send.AddPopPos(bytes);
        RF455NetworkCodec peer=process.m_codec455;peer.receiveKey=peer.sendKey;
        BYTE decoded[1024];std::size_t length=0;
        check(peer.decode(wire.data(),wire.size(),decoded,sizeof(decoded),length),"actual outgoing AES/frame decode");
        std::vector<BYTE> plain(decoded,decoded+length);check(plain.size()>=4&&plain[2]==13&&plain[3]==17,"actual group13/op17");
        for(BYTE byte:plain)std::fprintf(packets,"%02x",unsigned(byte));std::fputc('\n',packets);++count;
        return {plain.begin()+4,plain.end()};
    }
    void expect(const std::vector<BYTE>& value){check(take()==value,"independent packet bytes");}
};

static int run(){
    PacketFixture transport;
    CGUIItem itemIcon;CGUISFItem sfIcon,animusIcon;
    CBoardItem item;item.SetIndex(1);item.SetServerIndex(0x4321);item.SetIcon(&itemIcon);
    SF_DATA sfData={};sfData.dwDTIndex=0x123456;CSFItem sf;sf.*access(SfData{})=&sfData;
    sf.SetIndex(2);sf.SetSFType(CAT_FORCE);sf.SetIcon(&sfIcon);
    ITEM_DATA animusData={};animusData.dwDTIndex=0x12;CAnimusItem animus;
    static_cast<CBaseItem&>(animus).*access(ItemData{})=&animusData;animus.SetIndex(3);animus.SetIcon(&animusIcon);
    std::vector<std::unique_ptr<CBoardItem>> many;
    CLinkBoard link;link.Create(6,5,10);for(BYTE i=0;i<5;++i)check(link.AddPack(i)!=0,"actual Linker banks");
    check(!link.UploadHotbar455()&&transport.take().empty(),"initialFF state/cache");
    link.HotbarWindowState455().initialized();check(link.UploadHotbar455()!=0,"state-only initial upload");
    transport.expect({0xf8,0});
    check(link.Add(0,0,&item)&&link.Add(3,9,&sf)&&link.Add(4,9,&animus),"real source container insertion");
    check(link.HotbarReference455(&item)==0x04004321&&link.HotbarReference455(&sf)==0x01123456&&
          link.HotbarReference455(&animus)==0x03000012,"actual source metadata bridge");
    check(link.UploadHotbar455()!=0,"three actual source references");
    transport.expect({0xf8,3,0,4,0x21,0x43,39,1,0x56,0x34,49,3,0x12,0});
    check(!link.UploadHotbar455()&&transport.take().empty(),"unchanged suppression");
    auto& state=link.HotbarWindowState455();state.active=2;state.bankFlags={{1,0,1,0,1}};
    check(link.UploadHotbar455()!=0,"actual source state change");transport.expect({0xaa,0});
    _GetGBM()->*access(Hover{})=&item;_GetGBM()->*access(Origin{})=6;
    check(link.Remove(0,0)&&!link.UploadHotbar455()&&transport.take().empty(),"Linker drag suppression");
    _GetGBM()->*access(Hover{})=nullptr;_GetGBM()->*access(Origin{})=255;
    check(link.UploadHotbar455()!=0,"released drag deletion");transport.expect({0xaa,1,0,255,255,255});
    item.SetServerIndex(0x12345678);check(link.Add(4,2,&item),"real source reinsert");
    transport.process.m_NetSocket.GetSocket(0)->m_bAccept=false;
    check(!link.UploadHotbar455()&&transport.take().empty(),"real transport rejection");
    transport.process.m_NetSocket.GetSocket(0)->m_bAccept=true;
    check(!link.UploadHotbar455()&&transport.take().empty(),"cache committed before failed send");
    item.SetServerIndex(0x12345679);check(link.UploadHotbar455()!=0,"post-failure change");
    transport.expect({0xaa,1,42,0x16,0x79,0x56});
    for(BYTE bank=0;bank<5;++bank)for(BYTE slot=0;slot<10;++slot){
        if(link.GetObject(bank,slot))check(link.Remove(bank,slot),"old source removal");
        auto value=std::unique_ptr<CBoardItem>(new CBoardItem);value->SetIndex(100+10*bank+slot);
        value->SetServerIndex(10000+10*bank+slot);value->SetIcon(&itemIcon);
        check(link.Add(bank,slot,value.get()),"full50 source entries");many.push_back(std::move(value));
    }
    check(link.UploadHotbar455()!=0,"maximum50 update");
    std::vector<BYTE> expected={0xaa,50};
    for(unsigned i=0;i<50;++i){expected.push_back(BYTE(i));expected.push_back(4);expected.push_back(BYTE(10000+i));expected.push_back(BYTE((10000+i)>>8));}
    check(expected.size()==202,"maximum packet size");transport.expect(expected);
    link.ResetHotbarUpload455();check(!link.UploadHotbar455()&&transport.take().empty(),"snapshot reset retains header cache");
    many.back()->SetServerIndex(0x2345);link.*access(UploadTime{})=timeGetTime()-5001;
    const DWORD before=timeGetTime();link.FrameMove();transport.expect({0xaa,1,49,4,0x45,0x23});
    check(DWORD((link.*access(UploadTime{}))-before)<1000,"ordinary FrameMove upload clock");
    link.FrameMove();check(transport.take().empty(),"ordinary periodic gate");
    check(!RF455_HotbarUploadDue(5000,0)&&RF455_HotbarUploadDue(5001,0)&&
          !RF455_HotbarUploadDue(0x10,0xfffffff0)&&RF455_HotbarUploadDue(0x2000,0xfffffff0),"strict boundary/unsigned wrap");
    RF455HotbarWindowState rawFlags;rawFlags.active=3;rawFlags.bankFlags={{-1,2,256,3,17}};
    check(rawFlags.packed()==0xbb,"raw bank flags are shifted/truncated,not normalized booleans");
    check(RF455_EncodeHotbarReference(6,0,123,0)==0x0500007b&&
          RF455_EncodeHotbarReference(7,0,456,0)==0x060001c8&&
          RF455_EncodeHotbarReference(9,0,1,1)==0xffffffff,"remaining pure encoding selectors,not bound owners");
    FILE* output=std::fopen("result.json","wb");check(output!=nullptr,"result");
    std::fprintf(output,"{\"status\":\"PASS\",\"real_source_banks\":5,\"slots_per_bank\":10,\"actual_packets\":%u,"
        "\"maximum_payload\":202,\"actual_group\":13,\"actual_opcode\":17,\"actual_send_ring_AES\":true,"
        "\"actual_metadata_bridge\":true,\"drag_suppression\":true,\"failure_commits_cache\":true,"
        "\"ordinary_FrameMove\":true,\"raw_bank_flag_packing\":true,\"full_Linker_UI_ownership\":false,\"actual_Tutorial\":false}\n",transport.count);
    std::fclose(output);return 0;
}
static LONG failure(EXCEPTION_POINTERS* info){if(info->ExceptionRecord->ExceptionCode==0xe06d7363)return EXCEPTION_CONTINUE_SEARCH;
    std::fprintf(stderr,"exception=%08lx ownRVA=%08lx\n",info->ExceptionRecord->ExceptionCode,DWORD(info->ExceptionRecord->ExceptionAddress)-DWORD(GetModuleHandleA(nullptr)));return EXCEPTION_EXECUTE_HANDLER;}
static int guarded(){__try{return run();}__except(failure(GetExceptionInformation())){return 99;}}
int main(){try{return guarded();}catch(const std::exception& error){std::fprintf(stderr,"Hotbar:%s\n",error.what());return 1;}}
