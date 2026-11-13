// Small Win32 debugger for a specifically staged OWN executable. Never attaches
// to another process. Optional plan stops at a verified own instruction boundary.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>
#include <cstdint>
#pragma comment(lib,"user32.lib")

namespace {
struct Module {std::uintptr_t base;DWORD size;std::wstring path;};
struct Breakpoint {DWORD rva;const char* name;BYTE original;bool active;};
void quoted(FILE* f,const std::wstring& value){
    const int n=WideCharToMultiByte(CP_UTF8,0,value.data(),static_cast<int>(value.size()),nullptr,0,nullptr,nullptr);std::string text(n,'\0');if(n)WideCharToMultiByte(CP_UTF8,0,value.data(),static_cast<int>(value.size()),&text[0],n,nullptr,nullptr);
    std::fputc('"',f);for(unsigned char c:text){if(c=='"'||c=='\\')std::fputc('\\',f);if(c<32)std::fprintf(f,"\\u%04x",c);else std::fputc(c,f);}std::fputc('"',f);
}
std::wstring fileName(HANDLE file){wchar_t path[32768];const DWORD n=file && file!=INVALID_HANDLE_VALUE?GetFinalPathNameByHandleW(file,path,32768,0):0;return n && n<32768?std::wstring(path,n):L"";}
DWORD imageSize(HANDLE process,std::uintptr_t base){IMAGE_DOS_HEADER dos={};IMAGE_NT_HEADERS32 nt={};SIZE_T read=0;if(!ReadProcessMemory(process,reinterpret_cast<void*>(base),&dos,sizeof(dos),&read)||dos.e_magic!=IMAGE_DOS_SIGNATURE)return 0;if(!ReadProcessMemory(process,reinterpret_cast<void*>(base+dos.e_lfanew),&nt,sizeof(nt),&read)||nt.Signature!=IMAGE_NT_SIGNATURE)return 0;return nt.OptionalHeader.SizeOfImage;}
bool writeByte(HANDLE process,std::uintptr_t address,BYTE value){SIZE_T written=0;DWORD original=0,discard=0;void* target=reinterpret_cast<void*>(address);if(!VirtualProtectEx(process,target,1,PAGE_EXECUTE_READWRITE,&original))return false;const bool ok=WriteProcessMemory(process,target,&value,1,&written) && written==1;VirtualProtectEx(process,target,1,original,&discard);return ok && FlushInstructionCache(process,target,1);}
// Only code addresses from our own child: no registers, payloads or raw stack.
void timeoutLocation(FILE* output,const PROCESS_INFORMATION& process,std::uintptr_t base,const std::vector<Module>& modules){
    if(SuspendThread(process.hThread)==DWORD(-1))return;
    CONTEXT context={};context.ContextFlags=CONTEXT_CONTROL;
    if(GetThreadContext(process.hThread,&context)){
        std::fprintf(output,"{\"kind\":\"timeout_location\",\"pc\":\"0x%lx\"",context.Eip);
        for(const auto& mod:modules)if(context.Eip>=mod.base&&context.Eip-mod.base<mod.size){std::fprintf(output,",\"module\":");quoted(output,mod.path);std::fprintf(output,",\"rva\":\"0x%zx\"",context.Eip-mod.base);break;}
        DWORD words[256]={};SIZE_T bytes=0;ReadProcessMemory(process.hProcess,reinterpret_cast<void*>(context.Esp),words,sizeof(words),&bytes);
        const DWORD size=imageSize(process.hProcess,base);bool comma=false;std::fputs(",\"own_stack_rva_candidates\":[",output);
        for(unsigned i=0;i<bytes/4;++i)if(words[i]>=base&&words[i]-base<size){std::fprintf(output,"%s{\"stack_offset\":%u,\"rva\":\"0x%zx\"}",comma?",":"",i*4,words[i]-base);comma=true;}
        std::fputs("]}\n",output);
    }
    ResumeThread(process.hThread);
}
}
int wmain(int argc,wchar_t** argv){
    if(argc!=5&&argc!=6&&argc!=7)return 201;FILE* output=nullptr;if(_wfopen_s(&output,argv[2],L"wb")||!output)return 202;
    const DWORD mainRva=wcstoul(argv[3],nullptr,16),stopRva=wcstoul(argv[4],nullptr,16);if(!mainRva||!stopRva){std::fclose(output);return 203;}
    const bool deviceMode=argc>=6;DWORD plan[11]={};
    if(deviceMode){FILE* file=nullptr;_wfopen_s(&file,argv[5],L"rb");bool ok=file!=nullptr;for(unsigned i=0;ok&&i<11;++i)ok=std::fscanf(file,"%lx",plan+i)==1;if(file)std::fclose(file);if(!ok||!plan[7]||!plan[8]){std::fclose(output);return 205;}}
    std::wstring target=argv[1],cwd=target.substr(0,target.find_last_of(L"\\/")),command=L"\""+target+L"\"";STARTUPINFOW startup={sizeof(startup)};PROCESS_INFORMATION process={};
    // Only an explicitly staged own-lab fixture is forwarded to the own child.
    FILE*arguments=nullptr;_wfopen_s(&arguments,(cwd+L"\\launcher-commandline.txt").c_str(),L"rb");
    if(arguments){char bytes[2048]={};const size_t n=std::fread(bytes,1,sizeof(bytes)-1,arguments);std::fclose(arguments);const int size=MultiByteToWideChar(CP_UTF8,MB_ERR_INVALID_CHARS,bytes,static_cast<int>(n),nullptr,0);if(size<=0){std::fclose(output);return 206;}std::wstring text(size,L'\0');MultiByteToWideChar(CP_UTF8,MB_ERR_INVALID_CHARS,bytes,static_cast<int>(n),&text[0],size);command+=L" "+text;}
    if(deviceMode){startup.dwFlags=STARTF_USESHOWWINDOW;startup.wShowWindow=SW_HIDE;}
    std::string firstLabel="after_sound_before_d3d";FILE* labelFile=nullptr;_wfopen_s(&labelFile,(cwd+L"\\checkpoint-label.txt").c_str(),L"rb");
    if(labelFile){char label[64]={};std::fread(label,1,sizeof(label)-1,labelFile);std::fclose(labelFile);if(deviceMode||std::string(label)!="before_client_connect"){std::fclose(output);return 207;}firstLabel=label;}
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    if(!CreateProcessW(target.c_str(),&command[0],nullptr,nullptr,FALSE,DEBUG_ONLY_THIS_PROCESS|CREATE_NO_WINDOW,nullptr,cwd.c_str(),&startup,&process)){
        std::fprintf(output,"{\"kind\":\"create_error\",\"error\":%lu}\n",GetLastError());std::fclose(output);return 204;
    }
    DebugSetProcessKillOnExit(TRUE);std::fprintf(output,"{\"kind\":\"created\",\"pid\":%lu}\n",process.dwProcessId);std::fflush(output);
    std::string finalLabel="before_character_data";bool captureLoginFrame=false,captureSeen=false,selectionMode=false;DWORD loginObject=0;ULONGLONG selectionDeadline=0,selectionSendAt=0;HWND selectionWindow=nullptr;
    if(argc==7){
        const std::wstring mode=argv[6];
        if(mode==L"after_create")finalLabel="after_client_create";
        else if(mode==L"login_create")finalLabel="before_login_create";
        else if(mode==L"login_render")finalLabel="before_login_render";
        else if(mode==L"login_frame"){finalLabel="before_login_render";captureLoginFrame=true;}
        else if(mode==L"selection"){finalLabel="before_login_render";captureLoginFrame=true;selectionMode=true;}
        else{std::fclose(output);TerminateProcess(process.hProcess,0xe0434207);CloseHandle(process.hThread);CloseHandle(process.hProcess);return 208;}
    }
    std::vector<Module> modules;Breakpoint points[]={{mainRva,"WinMain",0,false},{deviceMode?plan[7]:stopRva,firstLabel.c_str(),0,false},{deviceMode?plan[8]:0,"after_d3d_before_create",0,false},{deviceMode&&stopRva!=plan[8]?stopRva:0,finalLabel.c_str(),0,false},{0,"after_login_render_following_capture",0,false}};
    char liveObservation[2]={};const bool live=GetEnvironmentVariableA("RF455_OBSERVE_PROTOCOL",liveObservation,sizeof(liveObservation))==1&&liveObservation[0]=='1';
    char skipTitle[2]{};
    char portalObservation[2]{};
    const bool observePortal = live && selectionMode &&
        GetEnvironmentVariableA("RF455_OBSERVE_BASE_PORTAL",portalObservation,sizeof(portalObservation))==1 &&
        portalObservation[0]=='1';
    char movementObservation[2]{};
    const bool observeMovement = live && selectionMode &&
        GetEnvironmentVariableA("RF455_OBSERVE_MOVEMENT",movementObservation,sizeof(movementObservation))==1 &&
        movementObservation[0]=='1';
    char focusObservation[2]{};
    const bool observeFocus = live && selectionMode &&
        GetEnvironmentVariableA("RF455_OBSERVE_FOCUS", focusObservation, sizeof(focusObservation)) == 1 &&
        focusObservation[0] == '1';
    unsigned focusPhase = 0;
    const bool observeTitle = captureLoginFrame && GetEnvironmentVariableA("RF455_SKIP_TITLE_STAGE",skipTitle,sizeof(skipTitle))==1 &&
                              (skipTitle[0]=='1' || skipTitle[0]=='2');
    const std::string titleFrame = std::string("RF455 Protocol:title-movie-capture:") + skipTitle[0] + ":0:0";
    HWND titleWindow = nullptr;
    bool titleEscapeSent = false;
    bool portalAttempted = false;
    ULONGLONG portalSendAt = 0;
    bool lobbyMenuOpened = false;
    bool lobbyStartKeySent = false;
    bool lobbySelectionOpened = false;
    char combatObservation[2]={};const bool combat=GetEnvironmentVariableA("RF455_OBSERVE_COMBAT",combatObservation,sizeof(combatObservation))==1&&combatObservation[0]=='1';
    char approach[6]{};
    const auto approachLength = combat ? GetEnvironmentVariableA("RF455_COMBAT_APPROACH_MS", approach, sizeof(approach)) : 0;
    unsigned long selectionMs = combat ? 38000 : observeMovement ? 50000 : (observePortal || observeFocus) ? 25000 : 15000;
    if (approachLength && approachLength < sizeof(approach)) {
        char* approachEnd = nullptr;
        const auto approachMs = std::strtoul(approach, &approachEnd, 10);
        if (*approachEnd == '\0' && approachMs <= 30000) selectionMs += approachMs;
    }
    std::uintptr_t imageBase=0;bool initialBreak=false,terminating=false,exited=false,mainReached=false,stopReached=false,d3dReached=false;const auto deadline=GetTickCount64()+(live?180000:20000);
    while(!exited){
        if (portalSendAt && GetTickCount64() >= portalSendAt && !terminating) {
            DWORD childPID = 0;
            GetWindowThreadProcessId(selectionWindow, &childPID);
            const bool valid = IsWindow(selectionWindow) && childPID == process.dwProcessId;
            // The ordinary inventory pack posts this message for bag 1, slot 1.
            const bool sent = valid && PostMessageW(selectionWindow, WM_USER + 0x0107, 0, 0);
            std::fprintf(output, "{\"kind\":\"base_portal_inventory_posted\",\"own_child_validated\":%s,\"sent\":%s}\n",
                         valid ? "true" : "false", sent ? "true" : "false");
            std::fflush(output);
            portalSendAt = 0;
        }
        if(selectionSendAt&&GetTickCount64()>=selectionSendAt&&!terminating){
            DWORD childPID=0;GetWindowThreadProcessId(selectionWindow,&childPID);
            const bool valid=IsWindow(selectionWindow)&&childPID==process.dwProcessId;
            const bool sent=valid&&PostMessageW(selectionWindow,WM_KEYDOWN,VK_RETURN,1)&&PostMessageW(selectionWindow,WM_KEYUP,VK_RETURN,0xc0000001);
            const bool startsLobby = lobbyMenuOpened && !lobbyStartKeySent;
            if (startsLobby && sent) lobbyStartKeySent = true;
            std::fprintf(output,"{\"kind\":\"%s\",\"own_child_validated\":%s,\"sent\":%s}\n",
                         startsLobby ? "lobby_start_key_posted" : "selection_key_posted",
                         valid ? "true" : "false", sent ? "true" : "false");
            std::fflush(output);selectionSendAt=0;
        }
        if(selectionDeadline&&GetTickCount64()>selectionDeadline&&!terminating){
            timeoutLocation(output,process,imageBase,modules);std::fputs("{\"kind\":\"selection_observation_end\"}\n",output);TerminateProcess(process.hProcess,0xe0434200);terminating=true;
        }
        if(terminating && GetTickCount64()>deadline+5000){std::fputs("{\"kind\":\"termination_timeout\"}\n",output);break;}
        if(GetTickCount64()>deadline && !terminating){timeoutLocation(output,process,imageBase,modules);std::fputs("{\"kind\":\"timeout\"}\n",output);TerminateProcess(process.hProcess,0xe0434201);terminating=true;}
        DEBUG_EVENT event={};if(!WaitForDebugEvent(&event,100)){if(GetLastError()!=ERROR_SEM_TIMEOUT){std::fprintf(output,"{\"kind\":\"wait_error\",\"error\":%lu}\n",GetLastError());break;}continue;}
        DWORD disposition=DBG_CONTINUE;
        if(event.dwDebugEventCode==CREATE_PROCESS_DEBUG_EVENT || event.dwDebugEventCode==LOAD_DLL_DEBUG_EVENT){
            HANDLE file=event.dwDebugEventCode==CREATE_PROCESS_DEBUG_EVENT?event.u.CreateProcessInfo.hFile:event.u.LoadDll.hFile;
            const auto base=reinterpret_cast<std::uintptr_t>(event.dwDebugEventCode==CREATE_PROCESS_DEBUG_EVENT?event.u.CreateProcessInfo.lpBaseOfImage:event.u.LoadDll.lpBaseOfDll);
            const Module module={base,imageSize(process.hProcess,base),fileName(file)};modules.push_back(module);
            std::fprintf(output,"{\"kind\":\"module\",\"base\":\"0x%zx\",\"bytes\":%lu,\"path\":",base,module.size);quoted(output,module.path);std::fputs("}\n",output);if(file)CloseHandle(file);
            if(event.dwDebugEventCode==CREATE_PROCESS_DEBUG_EVENT){
                imageBase=base;
                for(auto& point:points){if(!point.rva)continue;SIZE_T read=0;if(!ReadProcessMemory(process.hProcess,reinterpret_cast<void*>(base+point.rva),&point.original,1,&read)||read!=1||!writeByte(process.hProcess,base+point.rva,0xcc)){
                        std::fprintf(output,"{\"kind\":\"breakpoint_error\",\"error\":%lu}\n",GetLastError());TerminateProcess(process.hProcess,0xe0434202);terminating=true;break;}point.active=true;}
                // The primary PROCESS_INFORMATION handles are owned separately.
                if(event.u.CreateProcessInfo.hProcess!=process.hProcess)CloseHandle(event.u.CreateProcessInfo.hProcess);
                if(event.u.CreateProcessInfo.hThread!=process.hThread)CloseHandle(event.u.CreateProcessInfo.hThread);
            }
        }else if(event.dwDebugEventCode==CREATE_THREAD_DEBUG_EVENT){CloseHandle(event.u.CreateThread.hThread);
        }else if(event.dwDebugEventCode==EXCEPTION_DEBUG_EVENT){
            const auto& exception=event.u.Exception;const DWORD code=exception.ExceptionRecord.ExceptionCode;const auto address=reinterpret_cast<std::uintptr_t>(exception.ExceptionRecord.ExceptionAddress);Breakpoint* found=nullptr;
            for(auto& point:points)if(point.active && address==imageBase+point.rva)found=&point;
            if(code==EXCEPTION_BREAKPOINT && found){
                HANDLE thread=OpenThread(THREAD_GET_CONTEXT|THREAD_SET_CONTEXT|THREAD_QUERY_INFORMATION,FALSE,event.dwThreadId);CONTEXT context={};context.ContextFlags=CONTEXT_CONTROL|CONTEXT_INTEGER;
                if(!thread||!GetThreadContext(thread,&context)||!writeByte(process.hProcess,address,found->original)){
                    std::fprintf(output,"{\"kind\":\"context_error\",\"error\":%lu}\n",GetLastError());TerminateProcess(process.hProcess,0xe0434203);terminating=true;
                }else{
                    context.Eip=static_cast<DWORD>(address);found->active=false;
                    std::fprintf(output,"{\"kind\":\"checkpoint\",\"name\":\"%s\",\"rva\":\"0x%lx\",\"eax\":%lu}\n",found->name,found->rva,context.Eax);
                    if(deviceMode&&found==points+2){
                        d3dReached=true;DWORD values[4]={};SIZE_T read=0;bool ok=true;for(unsigned i=0;i<4;++i)ok=ReadProcessMemory(process.hProcess,reinterpret_cast<void*>(imageBase+plan[2]+plan[3+i]),values+i,4,&read)&&read==4&&ok;
                        std::fprintf(output,"{\"kind\":\"device_state\",\"read\":%s,\"ready\":%lu,\"window\":\"0x%lx\",\"device\":\"0x%lx\",\"windowed\":%lu}\n",ok?"true":"false",values[0],values[1],values[2],values[3]);
                        if (ok) titleWindow = reinterpret_cast<HWND>(values[1]);
                    }
                    const bool loginEntry=captureLoginFrame&&found==points+3;
                    const bool selectionInput=selectionMode&&found==points+4&&!selectionDeadline;
                    if(found==points || (deviceMode&&found->rva!=stopRva&&found!=points+4)||loginEntry||selectionInput){
                        if(selectionInput){
                            DWORD window=0,childPID=0;SIZE_T read=0;
                            const bool valid=ReadProcessMemory(process.hProcess,reinterpret_cast<void*>(imageBase+plan[2]+plan[4]),&window,4,&read)&&read==4&&window;
                            if(valid)GetWindowThreadProcessId(reinterpret_cast<HWND>(window),&childPID);
                            //Addressed messages only:never change OS focus or emit
                            //system keyboard input. The legacy inactive main loop
                            //blocks in GetMessage,so request background updates
                            //through its own activation-message handler first.
                            const bool activated=valid&&childPID==process.dwProcessId&&PostMessageW(reinterpret_cast<HWND>(window),WM_ACTIVATEAPP,TRUE,0);
                            std::fprintf(output,"{\"kind\":\"selection_background_update_requested\",\"own_child_validated\":%s,\"sent\":%s,\"OS_focus_changed\":false}\n",valid&&childPID==process.dwProcessId?"true":"false",activated?"true":"false");
                            if (activated) {
                                selectionWindow = reinterpret_cast<HWND>(window);
                                if (lobbySelectionOpened) selectionSendAt = GetTickCount64() + 1;
                                else if (lobbyMenuOpened) selectionSendAt = GetTickCount64() + 350;
                            }
                            stopReached=true;selectionDeadline=GetTickCount64()+selectionMs;
                        }
                        if(found==points)mainReached=true;
                        if(deviceMode&&found==points+1){DWORD full=0,bits=0;SIZE_T read=0;ReadProcessMemory(process.hProcess,reinterpret_cast<void*>(imageBase+plan[0]),&full,4,&read);ReadProcessMemory(process.hProcess,reinterpret_cast<void*>(imageBase+plan[1]),&bits,4,&read);std::fprintf(output,"{\"kind\":\"render_configuration\",\"fullscreen\":%lu,\"render_bits\":%lu}\n",full,bits);}
                        if(loginEntry){
                            loginObject=context.Ecx;DWORD returnAddress=0;SIZE_T read=0;auto& after=points[4];
                            const bool ok=!captureSeen||(ReadProcessMemory(process.hProcess,reinterpret_cast<void*>(context.Esp),&returnAddress,4,&read)&&read==4&&returnAddress>=imageBase&&returnAddress-imageBase<imageSize(process.hProcess,imageBase)&&ReadProcessMemory(process.hProcess,reinterpret_cast<void*>(returnAddress),&after.original,1,&read)&&read==1&&writeByte(process.hProcess,returnAddress,0xcc));
                            if(ok&&captureSeen){after.rva=returnAddress-imageBase;after.active=true;std::fprintf(output,"{\"kind\":\"login_render_return_armed\",\"rva\":\"0x%lx\"}\n",after.rva);}
                            else if(!ok){std::fputs("{\"kind\":\"login_return_breakpoint_error\"}\n",output);TerminateProcess(process.hProcess,0xe0434208);terminating=true;}
                        }
                        if(!SetThreadContext(thread,&context)){std::fputs("{\"kind\":\"set_context_error\"}\n",output);TerminateProcess(process.hProcess,0xe0434204);terminating=true;}
                    }else {
                        stopReached=true;
                        if(finalLabel=="before_login_create"||finalLabel=="before_login_render"){
                            const DWORD object=captureLoginFrame?loginObject:context.Ecx;DWORD stage[6]={};SIZE_T stageRead=0;const bool stageOK=ReadProcessMemory(process.hProcess,reinterpret_cast<void*>(object),stage,sizeof(stage),&stageRead)&&stageRead==sizeof(stage);
                            std::fprintf(output,"{\"kind\":\"stage_state\",\"read\":%s,\"object\":\"0x%lx\",\"vtable\":\"0x%lx\",\"exit\":%lu,\"created\":%lu,\"loaded\":%lu,\"next\":%lu}\n",stageOK?"true":"false",object,stage[0],stage[1],stage[3],stage[4],stage[5]);
                        }
                        if(deviceMode&&found==points+3){DWORD owner=0,device=0;SIZE_T read=0;bool ok=ReadProcessMemory(process.hProcess,reinterpret_cast<void*>(imageBase+plan[9]),&owner,4,&read)&&read==4&&owner;ok=ok&&ReadProcessMemory(process.hProcess,reinterpret_cast<void*>(owner+plan[10]),&device,4,&read)&&read==4;
                            std::fprintf(output,"{\"kind\":\"character_owner\",\"read\":%s,\"owner\":\"0x%lx\",\"device\":\"0x%lx\"}\n",ok?"true":"false",owner,device);}
                        TerminateProcess(process.hProcess,0xe0434200);terminating=true;
                    }
                }if(thread)CloseHandle(thread);
            }else if(code==EXCEPTION_BREAKPOINT && !initialBreak){initialBreak=true;std::fputs("{\"kind\":\"initial_debugger_break\"}\n",output);
            }else{
                std::fprintf(output,"{\"kind\":\"exception\",\"code\":\"0x%08lx\",\"first_chance\":%lu,\"address\":\"0x%zx\"",code,exception.dwFirstChance,address);
                for(const auto& module:modules)if(address>=module.base && address-module.base<module.size){std::fprintf(output,",\"rva\":\"0x%zx\",\"module\":",address-module.base);quoted(output,module.path);break;}
                if(exception.ExceptionRecord.NumberParameters>=2)std::fprintf(output,",\"parameter0\":%zu,\"parameter1\":\"0x%zx\"",static_cast<std::size_t>(exception.ExceptionRecord.ExceptionInformation[0]),static_cast<std::size_t>(exception.ExceptionRecord.ExceptionInformation[1]));std::fputs("}\n",output);
                disposition=DBG_EXCEPTION_NOT_HANDLED;if(!exception.dwFirstChance){
                    HANDLE faultThread=OpenThread(THREAD_GET_CONTEXT|THREAD_QUERY_INFORMATION,FALSE,event.dwThreadId);CONTEXT fault={};fault.ContextFlags=CONTEXT_CONTROL|CONTEXT_INTEGER;
                    if(faultThread&&GetThreadContext(faultThread,&fault)){
                        std::fprintf(output,"{\"kind\":\"fatal_context\",\"eax\":\"0x%lx\",\"ecx\":\"0x%lx\",\"edx\":\"0x%lx\",\"esi\":\"0x%lx\",\"edi\":\"0x%lx\",\"esp\":\"0x%lx\",\"own_stack_rva_candidates\":[",fault.Eax,fault.Ecx,fault.Edx,fault.Esi,fault.Edi,fault.Esp);
                        //A1024-byte read crossing the stack's committed end can
                        //fail entirely even though its first words are readable.
                        //Read bounded individual words;persist only own code RVAs.
                        bool comma=false;DWORD ownSize=0;for(const auto& mod:modules)if(mod.base==imageBase)ownSize=mod.size;unsigned readable=0;
                        for(unsigned i=0;i<256;++i){DWORD word=0;SIZE_T bytes=0;if(!ReadProcessMemory(process.hProcess,reinterpret_cast<void*>(fault.Esp+i*4),&word,4,&bytes)||bytes!=4)break;++readable;
                            if(word>=imageBase&&word-imageBase<ownSize){std::fprintf(output,"%s{\"stack_offset\":%u,\"rva\":\"0x%zx\"}",comma?",":"",i*4,word-imageBase);comma=true;}}
                        std::fprintf(output,"],\"readable_stack_words\":%u}\n",readable);
                    }
                    if(faultThread)CloseHandle(faultThread);TerminateProcess(process.hProcess,0xe0434205);terminating=true;
                }
            }
        }else if(event.dwDebugEventCode==OUTPUT_DEBUG_STRING_EVENT){
            const auto& item=event.u.DebugString;if(!item.fUnicode&&item.nDebugStringLength&&item.nDebugStringLength<1024){char text[1024]={};SIZE_T read=0;if(ReadProcessMemory(process.hProcess,item.lpDebugStringData,text,item.nDebugStringLength,&read)&&read==item.nDebugStringLength){text[1023]=0;std::wstring value;for(unsigned char*c=reinterpret_cast<unsigned char*>(text);*c;++c)value.push_back(*c);std::fputs("{\"kind\":\"debug_string\",\"value\":",output);quoted(output,value);std::fputs("}\n",output);
                const std::string receivedTitleEvent = text;
                const bool skipAtFrame = !observePortal && !observeMovement && receivedTitleEvent == titleFrame;
                const bool skipAtStart = (observePortal || observeMovement) && receivedTitleEvent ==
                    std::string("RF455 Protocol:title-movie-start:") + skipTitle[0] + ":0:0";
                if (observeTitle && !titleEscapeSent && (skipAtFrame || skipAtStart)) {
                    DWORD childPID = 0;
                    GetWindowThreadProcessId(titleWindow, &childPID);
                    const bool valid = IsWindow(titleWindow) && childPID == process.dwProcessId;
                    if (valid && (observePortal || observeMovement)) PostMessageW(titleWindow, WM_ACTIVATEAPP, TRUE, 0);
                    titleEscapeSent = valid && PostMessageW(titleWindow, WM_KEYDOWN, VK_ESCAPE, 1) &&
                                      PostMessageW(titleWindow, WM_KEYUP, VK_ESCAPE, 0xc0000001);
                    std::fprintf(output, "{\"kind\":\"title_escape_posted\",\"own_child_validated\":%s,\"sent\":%s}\n",
                                 valid ? "true" : "false", titleEscapeSent ? "true" : "false");
                }
                if (observePortal && !portalAttempted && std::string(text) == "RF455 Protocol:position-mode:0:0:0") {
                    portalAttempted = true;
                    portalSendAt = GetTickCount64() + 1000;
                }
                if (observeFocus && ((focusPhase == 0 && std::string(text).rfind("RF455 WorldCapture:0:0:", 0) == 0) ||
                                     (focusPhase == 1 && std::string(text).rfind("RF455 WorldCapture:2:0:", 0) == 0))) {
                    DWORD owner = 0;
                    GetWindowThreadProcessId(selectionWindow, &owner);
                    const bool valid = IsWindow(selectionWindow) && owner == process.dwProcessId;
                    const bool activate = focusPhase == 1;
                    const bool sent = valid && PostMessageW(selectionWindow, WM_ACTIVATEAPP, activate, 0);
                    std::fprintf(output, "{\"kind\":\"world_activation_posted\",\"active\":%s,\"sent\":%s}\n",
                                 activate ? "true" : "false", sent ? "true" : "false");
                    ++focusPhase;
                }
                if (selectionMode && std::string(text) == "RF455 Protocol:lobby-menu-open:0:0:0") {
                    lobbyMenuOpened = true;
                    if (selectionWindow && !lobbyStartKeySent) selectionSendAt = GetTickCount64() + 350;
                }
                if (selectionMode && receivedTitleEvent.rfind("RF455 Protocol:lobby-selection-input-ready:", 0) == 0) {
                    lobbySelectionOpened = true;
                    if (selectionWindow) selectionSendAt = GetTickCount64() + 1;
                }
                if(captureLoginFrame&&std::string(text).rfind("RF455 LoginFrame:",0)==0){captureSeen=true;auto& entry=points[3];if(!entry.active&&!points[4].active){if(writeByte(process.hProcess,imageBase+entry.rva,0xcc))entry.active=true;else{std::fputs("{\"kind\":\"login_capture_rearm_error\"}\n",output);TerminateProcess(process.hProcess,0xe0434209);terminating=true;}}}
            }}
        }else if(event.dwDebugEventCode==EXIT_PROCESS_DEBUG_EVENT){std::fprintf(output,"{\"kind\":\"exit\",\"code\":\"0x%08lx\"}\n",event.u.ExitProcess.dwExitCode);exited=true;}
        std::fflush(output);if(!ContinueDebugEvent(event.dwProcessId,event.dwThreadId,disposition)){std::fprintf(output,"{\"kind\":\"continue_error\",\"error\":%lu}\n",GetLastError());break;}
    }
    if(!exited){TerminateProcess(process.hProcess,0xe0434206);WaitForSingleObject(process.hProcess,5000);}CloseHandle(process.hThread);CloseHandle(process.hProcess);
    if(deviceMode)std::fprintf(output,"{\"kind\":\"summary\",\"main_reached\":%s,\"after_d3d_reached\":%s,\"final_checkpoint_reached\":%s,\"exit_observed\":%s}\n",mainReached?"true":"false",d3dReached?"true":"false",stopReached?"true":"false",exited?"true":"false");
    else if(firstLabel=="before_client_connect")std::fprintf(output,"{\"kind\":\"summary\",\"main_reached\":%s,\"before_connect_reached\":%s,\"exit_observed\":%s}\n",mainReached?"true":"false",stopReached?"true":"false",exited?"true":"false");
    else std::fprintf(output,"{\"kind\":\"summary\",\"main_reached\":%s,\"after_sound_reached\":%s,\"exit_observed\":%s}\n",mainReached?"true":"false",stopReached?"true":"false",exited?"true":"false");std::fclose(output);return 0;
}
