#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "input/imeedit.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "mainapp.h"
#include "gameprogress/cgp_login.h"
#include "userinterface/gamewindow/guichatwindow.h"
#include "client455_message_dispatch.h"
#include "client455_avatar_stage.h"
#include "client455_center_messages.h"
#include "client455_chat_profile.h"
#include "client455_font.h"
#include "client455_language.h"
#include "client455_nuclear_aiming.h"
#include "client455_text_metrics.h"
#include <cstdio>
#include <cstring>
#include <stdexcept>

namespace {
RF455MessageCounters counters;
char display[1024]={};
void format(const char* value,va_list args){
    const int n=std::vsnprintf(display,sizeof(display),value,args);
    if(n<0||n>=sizeof(display))throw std::logic_error("455 system-message unsafe formatted buffer domain");
}
void center(DWORD color){
    auto* owner=RF455_GetCenterMessages();
    if(!owner)throw std::logic_error("455 system-message center owner unavailable");
    owner->Add(display,color);
}
void copy256(char* out,const char* value){
    std::memset(out,0,256);
    if(value){const auto n=std::strlen(value)+1;std::memcpy(out,value,n>=256?255:n);}
}
const char* localized(unsigned index){
    const auto* language=RF455_GetNormalLanguagePack();
    if(!language||language->records.empty()||index>=language->records.size())throw std::logic_error("455 localized system-message provider unavailable");
    return language->get(index);
}
}
RF455MessageCounters& RF455_SystemMessageCounters(){return counters;}
RF455MessageContext RF455_CurrentMessageContext(){
    auto* app=_GetMainApp();
    if(!app)throw std::logic_error("455 actual MainApp message provider unavailable");
    const BYTE stage=RF455_FromLegacyStage(app->GetGameProgressID());
    auto* login=stage==1?dynamic_cast<CGP_LogIn*>(app->GetGameProgress455()):nullptr;
    if(stage==1&&app->GetGameProgress455()&&!login)throw std::logic_error("455 login message requires its actual Login instance");
    return {stage,login,_GetChatWindow()};
}
void RF455_DispatchMessage(const RF455MessageContext& context,const char* text,BYTE category,BYTE style){
    if(context.stage==1){if(context.login)context.login->SystemMessages455().SetPrimary(text);return;}
    if((context.stage!=2&&context.stage!=3)||!context.chat)return;
    char header[32];
    if(context.stage==3){
        std::sprintf(header,"[%d]",static_cast<int>(++counters.main));
        context.chat->InsertText455(header,text,style?style:(category==9?25:2),category);
    }else{
        std::sprintf(header,"[%d]",static_cast<int>(++counters.tutorial));
        context.chat->InsertText455(header,text,2,3);
    }
}
void RF455_ShowSystemMessageV(const char* value,va_list args){
    if(!value)return;format(value,args);const auto context=RF455_CurrentMessageContext();
    if(context.stage!=0&&context.stage!=1&&context.stage!=2)center(0xffcc1f00);
    RF455_DispatchMessage(context,display,3,0);
}
void RF455_ShowSystemMessage(const char* value,...){va_list args;va_start(args,value);RF455_ShowSystemMessageV(value,args);va_end(args);}
void RF455_ShowCenterMessage(const char* value,...){if(!value)return;va_list args;va_start(args,value);format(value,args);va_end(args);center(0xffcc1f00);}
void RF455_ShowDoubleMessage(const char* value){RF455_ShowCenterMessage(value);RF455_ShowSystemMessage(value);}
void RF455_ShowOrangeMessage(const char* value,...){if(!value)return;va_list args;va_start(args,value);format(value,args);va_end(args);center(0xffffd200);}
void RF455_ShowFriendMessage(const char* value,...){if(!value)return;va_list args;va_start(args,value);format(value,args);va_end(args);RF455_DispatchMessage(RF455_CurrentMessageContext(),display,3,26);}
void RF455_RequireSystemMessageProviders(){
    // Reject uninitialized/unsafe own-source domains before mutating a real item.
    // Missing chat itself is the target's valid no-chat branch, not a fake sink.
    const auto context=RF455_CurrentMessageContext();
    if(context.stage!=0&&context.stage!=1&&context.stage!=2){
        if(!RF455_GetCenterMessages()||!RF455_TextResourcesReady())throw std::logic_error("455 message center/font providers unavailable");
    }
    if((context.stage==2||context.stage==3)&&context.chat){
        auto* profile=RF455_GetChatProfile();
        if(!profile||!profile->Ready()||!context.chat->ChatReady455())throw std::logic_error("455 real chat profile/window not initialized");
    }
}
void RF455_CancelNuclearForHover(){
    const char* message=localized(0xc1a);RF455_RequireSystemMessageProviders();
    RF455_NuclearAiming().Clear();RF455_ShowSystemMessage(message);
}
void RF455_BeginNuclearSelection(){
    const char* message=localized(0xce7);RF455_RequireSystemMessageProviders();
    _GetGBM()->SetRequestProcessState(FALSE);RF455_ShowSystemMessage(message);
    auto& aiming=RF455_NuclearAiming();if(!aiming.pending)aiming.SetPending(1);
}
void RF455LoginMessages::Clear(){std::memset(primary,0,256);std::memset(secondary,0,256);}
void RF455LoginMessages::SetPrimary(const char* value){copy256(primary,value);}
void RF455LoginMessages::SetSecondary(const char* value){
    if(value)copy256(secondary,value);else std::memset(primary,0,256); // target null-secondary quirk
}
void RF455LoginMessages::Draw()const{
    if(!*primary)return;
    if(!RF455_TextResourcesReady())throw std::logic_error("455 Login message fonts unavailable");
    const int x=(_GetUIScreen()->GetSizeX()-RF455_TextWidth(primary))/2;
    float position[4]={static_cast<float>(x),static_cast<float>(_GetUIScreen()->GetSizeY()-30),0,1};
    GetD3dDevice()->SetRenderState(D3DRS_ZENABLE,FALSE);
    const auto result=RF455_DrawTextAnsiScaled(position,primary,0xffffa670,32,1);
    GetD3dDevice()->SetRenderState(D3DRS_ZENABLE,TRUE);
    if(FAILED(result))throw std::runtime_error("455 actual Login message draw failed");
}
