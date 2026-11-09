#pragma once
#include <windows.h>
#include <cstdarg>

class CGP_LogIn;
class CGUIChatWindow;
struct RF455MessageContext {BYTE stage;CGP_LogIn* login;CGUIChatWindow* chat;};
struct RF455MessageCounters {DWORD main=0,tutorial=0;};
// Actual process counters. They survive stage changes like the target globals.
RF455MessageCounters& RF455_SystemMessageCounters();
RF455MessageContext RF455_CurrentMessageContext();
// The target-ID routing core is also used by the future joint Tutorial factory.
// Calling it with stage2 does not establish an actual Tutorial instance exists.
void RF455_DispatchMessage(const RF455MessageContext&,const char*,BYTE category=3,BYTE style=0);
void RF455_ShowSystemMessageV(const char*,va_list);
void RF455_ShowSystemMessage(const char*,...);
void RF455_ShowCenterMessage(const char*,...);
void RF455_ShowDoubleMessage(const char*);
void RF455_ShowOrangeMessage(const char*,...);
void RF455_ShowFriendMessage(const char*,...);
void RF455_RequireSystemMessageProviders();
void RF455_CancelNuclearForHover();
void RF455_BeginNuclearSelection();

class RF455LoginMessages {
public:
    void Clear();
    void SetPrimary(const char*);
    void SetSecondary(const char*);
    void Draw()const;
    const char* Primary()const{return primary;}
    const char* Secondary()const{return secondary;}
private:
    char primary[256]={},secondary[256]={};
};
