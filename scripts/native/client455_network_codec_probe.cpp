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
#include "client455_network_codec.h"
#include <bcrypt.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <vector>
#pragma comment(lib,"bcrypt.lib")
extern CMainApp g_MainApp;
template<class Tag,typename Tag::Type Member>struct MemberAccess{friend typename Tag::Type access(Tag){return Member;}};
struct NetworkMember{using Type=CNetworkMgr CMainApp::*;friend Type access(NetworkMember);};
struct SendBuffer{using Type=_NET_BUFFER* CNetProcess::*;friend Type access(SendBuffer);};
struct ReceiveBuffer{using Type=_NET_BUFFER* CNetProcess::*;friend Type access(ReceiveBuffer);};
struct Owner{using Type=CNetWorking* CNetProcess::*;friend Type access(Owner);};
struct Pop{using Type=void(CNetProcess::*)(WORD);friend Type access(Pop);};
template struct MemberAccess<NetworkMember,&CMainApp::m_cNetworkMgr>;
template struct MemberAccess<SendBuffer,&CNetProcess::m_pSendBuffer>;
template struct MemberAccess<ReceiveBuffer,&CNetProcess::m_pRecvBuffer>;
template struct MemberAccess<Owner,&CNetProcess::m_pNetwork>;
template struct MemberAccess<Pop,&CNetProcess::_PopRecvMsg>;
#define REQUIRE(x) do{if(!(x)){std::fprintf(stderr,"Codec failure line%d: %s\n",__LINE__,#x);return 1;}}while(0)
static std::vector<unsigned char> oracle(const unsigned char* key,unsigned bytes,const std::vector<unsigned char>& input){
    BCRYPT_ALG_HANDLE algorithm=nullptr;BCRYPT_KEY_HANDLE handle=nullptr;std::vector<unsigned char> output(input.size());ULONG count=0;unsigned char iv[16]={};
    if(BCryptOpenAlgorithmProvider(&algorithm,BCRYPT_AES_ALGORITHM,nullptr,0)<0)std::abort();
    if(BCryptSetProperty(algorithm,BCRYPT_CHAINING_MODE,reinterpret_cast<PUCHAR>(const_cast<wchar_t*>(BCRYPT_CHAIN_MODE_CBC)),sizeof(BCRYPT_CHAIN_MODE_CBC),0)<0)std::abort();
    if(BCryptGenerateSymmetricKey(algorithm,&handle,nullptr,0,const_cast<PUCHAR>(key),bytes,0)<0)std::abort();
    if(BCryptEncrypt(handle,const_cast<PUCHAR>(input.data()),static_cast<ULONG>(input.size()),nullptr,iv,sizeof(iv),output.data(),static_cast<ULONG>(output.size()),&count,0)<0||count!=input.size())std::abort();
    BCryptDestroyKey(handle);BCryptCloseAlgorithmProvider(algorithm,0);return output;
}
static std::vector<unsigned char> plain(unsigned short type,const std::vector<unsigned char>& payload){
    std::vector<unsigned char> value(payload.size()+4);value[0]=static_cast<unsigned char>(value.size());value[1]=static_cast<unsigned char>(value.size()>>8);value[2]=static_cast<unsigned char>(type);value[3]=static_cast<unsigned char>(type>>8);std::copy(payload.begin(),payload.end(),value.begin()+4);return value;
}
static std::vector<unsigned char> wire(const RF455AesKey& key,const std::vector<unsigned char>& value){
    auto padded=value;padded.resize((padded.size()+15)&~std::size_t(15));auto result=oracle(key.expanded,24,padded);result.insert(result.begin(),{static_cast<unsigned char>(result.size()+3),static_cast<unsigned char>((result.size()+3)>>8),static_cast<unsigned char>(padded.size()-value.size())});return result;
}
struct Capture: CNetWorking {
    unsigned calls=0;std::vector<unsigned char> packet;
    bool DataAnalysis(DWORD process,DWORD index,_MSG_HEADER* header,char* data) override {
        if(process!=0||index!=0||data!=reinterpret_cast<char*>(header)+4)return false;
        ++calls;packet.assign(reinterpret_cast<unsigned char*>(header),reinterpret_cast<unsigned char*>(header)+header->m_wSize);return true;
    }
};
int main(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    for(unsigned bytes:{16u,24u,32u}){
        unsigned char key[32];for(unsigned i=0;i<bytes;++i)key[i]=static_cast<unsigned char>(i);
        RF455AesKey source;REQUIRE(source.initialize(key,bytes));std::vector<unsigned char> value(16);for(unsigned i=0;i<16;++i)value[i]=static_cast<unsigned char>(11*i);
        auto expected=oracle(key,bytes,value);unsigned char encoded[16],decoded[16];source.encrypt(value.data(),encoded);REQUIRE(!std::memcmp(expected.data(),encoded,16));source.decrypt(encoded,decoded);REQUIRE(!std::memcmp(value.data(),decoded,16));
        source.decrypt(encoded,encoded);REQUIRE(!std::memcmp(value.data(),encoded,16));
    }
    RF455NetworkCodec codec;codec.initializeDefault(true);REQUIRE(codec.configured&&codec.enabled&&codec.sendKey.rounds==12&&codec.receiveKey.rounds==12);
    unsigned char encoded[20000],decoded[20000];std::size_t written=0,count=0;
    for(unsigned size:{0u,1u,11u,12u,13u,15u,16u,17u,27u,28u,29u,31u,32u,255u,1023u,19980u}){
        std::vector<unsigned char> payload(size);for(unsigned i=0;i<size;++i)payload[i]=static_cast<unsigned char>(i*37+5);const auto value=plain(0x0703,payload);
        const auto expected=wire(codec.sendKey,value);REQUIRE(codec.encode(0x0703,payload.data(),payload.size(),encoded,sizeof(encoded),written));REQUIRE(written==expected.size()&&!std::memcmp(encoded,expected.data(),written));
        const auto incoming=wire(codec.receiveKey,value);REQUIRE(codec.decode(incoming.data(),incoming.size(),decoded,sizeof(decoded),count));REQUIRE(count==value.size()&&!std::memcmp(decoded,value.data(),count));
        for(std::size_t shortSize:{std::size_t(0),std::size_t(1),std::size_t(2),incoming.size()-1})REQUIRE(!codec.decode(incoming.data(),shortSize,decoded,sizeof(decoded),count));
    }
    REQUIRE(!codec.encode(3,encoded,19996,decoded,sizeof(decoded),written));
    const auto sample=plain(0x0703,{1,2,3,4,5});auto malformed=wire(codec.receiveKey,sample);malformed[2]=16;REQUIRE(!codec.decode(malformed.data(),malformed.size(),decoded,sizeof(decoded),count));
    codec.enabled=false;REQUIRE(codec.encode(0x0c15,nullptr,0,encoded,sizeof(encoded),written)&&written==4&&encoded[0]==4&&encoded[1]==0&&encoded[2]==21&&encoded[3]==12);
    REQUIRE(codec.decode(encoded,written,decoded,sizeof(decoded),count)&&count==4);
    auto capture=std::make_unique<Capture>();auto process=std::make_unique<CNetProcess>();_NET_BUFFER send,receive;std::vector<char> sendScratch(1000000),receiveScratch(20000);
    REQUIRE(send.Configure(1000000,1000000,sendScratch.data())&&receive.Configure(20000,20000,receiveScratch.data()));
    process.get()->*access(SendBuffer{})=&send;process.get()->*access(ReceiveBuffer{})=&receive;process.get()->*access(Owner{})=capture.get();process->m_nIndex=0;process->m_Type.m_wSocketMaxNum=1;
    process->m_codec455.initializeDefault(true);process->m_NetSocket.GetSocket(0)->m_bAccept=true;
    send.m_dwPopPnt=send.m_dwPushPnt=send.m_capacity-2;BYTE type[2]={3,7};char payload[5]={1,2,3,4,5};
    REQUIRE(process->LoadSendMsg(0,type,payload,sizeof(payload)));bool missing=true;int queued=0;char* queuedData=send.GetSendPoint(&queued,&missing);auto expected=wire(process->m_codec455.sendKey,sample);
    REQUIRE(!missing&&queued==expected.size()&&!std::memcmp(queuedData,expected.data(),queued));
    // An owned packet fixture feeds the actual ring/decoder/dispatch consumer;
    // no network listener,server emulator or authentication is involved.
    auto incoming=wire(process->m_codec455.receiveKey,sample);receive.m_dwPopPnt=receive.m_dwPushPnt=receive.m_capacity-1;
    auto push=[&](const unsigned char* data,std::size_t size){const DWORD at=receive.m_dwPushPnt,left=receive.m_capacity-at;std::memcpy(receive.m_sMainBuffer+at,data,size);if(left<size)std::memcpy(receive.m_sMainBuffer,receive.m_sMainBuffer+receive.m_capacity,size-left);receive.AddPushPos(static_cast<DWORD>(size));};
    push(incoming.data(),2);(process.get()->*access(Pop{}))(0);REQUIRE(!capture->calls);push(incoming.data()+2,incoming.size()-2);(process.get()->*access(Pop{}))(0);
    REQUIRE(capture->calls==1&&capture->packet==sample&&receive.GetTotalPush()==receive.GetTotalPop());
    process.get()->*access(SendBuffer{})=nullptr;process.get()->*access(ReceiveBuffer{})=nullptr;process.get()->*access(Owner{})=nullptr;
    REQUIRE(g_MainApp.CreateNetworkMgr455());auto& network=g_MainApp.*access(NetworkMember{});REQUIRE(network.m_dwUseProcessNum==2&&max_process==6);
    for(unsigned i=0;i<2;++i){auto& p=network.m_Process[i];auto* r=p.*access(ReceiveBuffer{});auto* s=p.*access(SendBuffer{});REQUIRE(r&&s&&r->m_capacity==20000&&s->m_capacity==1000000&&sizeof(*r)==80);}
    REQUIRE(network.m_Process[0].m_codec455.configured&&network.m_Process[0].m_codec455.enabled&&!network.m_Process[1].m_codec455.configured);
    BYTE accountType[2]={21,12};REQUIRE(!network.SendNetMessage(0,accountType,nullptr,0)&&!network.m_Process[0].m_codec455.enabled);REQUIRE(!network.SendNetMessage(0,type,payload,5)&&network.m_Process[0].m_codec455.enabled);
    FILE* result=std::fopen("result.json","wb");REQUIRE(result);std::fputs("{\"status\":\"PASS\",\"independent_cng_aes128_192_256\":true,\"directional_cbc_zero_padding\":true,\"payload_boundaries\":16,\"bounded_truncation_and_malformed\":true,\"actual_send_ring_wrap\":true,\"actual_receive_fragment_wrap_dispatch\":true,\"real_network_processes\":2,\"process_capacity\":6,\"receive_buffer\":20000,\"send_buffer\":1000000,\"buffer_record_bytes\":80,\"normal_group21_cipher_toggle\":true,\"authentication_performed\":false}\n",result);std::fclose(result);return 0;
}
