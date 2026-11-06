// Small Win32 debugger for a specifically staged OWN executable. Never attaches
// to another process. Checkpoints stop before graphics/window/network creation.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <cstdio>
#include <string>
#include <vector>
#include <cstdint>

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
}
int wmain(int argc,wchar_t** argv){
    if(argc!=5)return 201;FILE* output=nullptr;if(_wfopen_s(&output,argv[2],L"wb")||!output)return 202;
    const DWORD mainRva=wcstoul(argv[3],nullptr,16),stopRva=wcstoul(argv[4],nullptr,16);if(!mainRva||!stopRva){std::fclose(output);return 203;}
    std::wstring target=argv[1],cwd=target.substr(0,target.find_last_of(L"\\/")),command=L"\""+target+L"\"";STARTUPINFOW startup={sizeof(startup)};PROCESS_INFORMATION process={};
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    if(!CreateProcessW(target.c_str(),&command[0],nullptr,nullptr,FALSE,DEBUG_ONLY_THIS_PROCESS|CREATE_NO_WINDOW,nullptr,cwd.c_str(),&startup,&process)){
        std::fprintf(output,"{\"kind\":\"create_error\",\"error\":%lu}\n",GetLastError());std::fclose(output);return 204;
    }
    DebugSetProcessKillOnExit(TRUE);std::fprintf(output,"{\"kind\":\"created\",\"pid\":%lu}\n",process.dwProcessId);std::fflush(output);
    std::vector<Module> modules;Breakpoint points[]={{mainRva,"WinMain",0,false},{stopRva,"after_sound_before_d3d",0,false}};
    std::uintptr_t imageBase=0;bool initialBreak=false,terminating=false,exited=false,mainReached=false,stopReached=false;const auto deadline=GetTickCount64()+20000;
    while(!exited){
        if(terminating && GetTickCount64()>deadline+5000){std::fputs("{\"kind\":\"termination_timeout\"}\n",output);break;}
        if(GetTickCount64()>deadline && !terminating){std::fputs("{\"kind\":\"timeout\"}\n",output);TerminateProcess(process.hProcess,0xe0434201);terminating=true;}
        DEBUG_EVENT event={};if(!WaitForDebugEvent(&event,100)){if(GetLastError()!=ERROR_SEM_TIMEOUT){std::fprintf(output,"{\"kind\":\"wait_error\",\"error\":%lu}\n",GetLastError());break;}continue;}
        DWORD disposition=DBG_CONTINUE;
        if(event.dwDebugEventCode==CREATE_PROCESS_DEBUG_EVENT || event.dwDebugEventCode==LOAD_DLL_DEBUG_EVENT){
            HANDLE file=event.dwDebugEventCode==CREATE_PROCESS_DEBUG_EVENT?event.u.CreateProcessInfo.hFile:event.u.LoadDll.hFile;
            const auto base=reinterpret_cast<std::uintptr_t>(event.dwDebugEventCode==CREATE_PROCESS_DEBUG_EVENT?event.u.CreateProcessInfo.lpBaseOfImage:event.u.LoadDll.lpBaseOfDll);
            const Module module={base,imageSize(process.hProcess,base),fileName(file)};modules.push_back(module);
            std::fprintf(output,"{\"kind\":\"module\",\"base\":\"0x%zx\",\"bytes\":%lu,\"path\":",base,module.size);quoted(output,module.path);std::fputs("}\n",output);if(file)CloseHandle(file);
            if(event.dwDebugEventCode==CREATE_PROCESS_DEBUG_EVENT){
                imageBase=base;
                for(auto& point:points){SIZE_T read=0;if(!ReadProcessMemory(process.hProcess,reinterpret_cast<void*>(base+point.rva),&point.original,1,&read)||read!=1||!writeByte(process.hProcess,base+point.rva,0xcc)){
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
                    if(found==points){mainReached=true;if(!SetThreadContext(thread,&context)){std::fputs("{\"kind\":\"set_context_error\"}\n",output);TerminateProcess(process.hProcess,0xe0434204);terminating=true;}}
                    else {stopReached=true;TerminateProcess(process.hProcess,0xe0434200);terminating=true;}
                }if(thread)CloseHandle(thread);
            }else if(code==EXCEPTION_BREAKPOINT && !initialBreak){initialBreak=true;std::fputs("{\"kind\":\"initial_debugger_break\"}\n",output);
            }else{
                std::fprintf(output,"{\"kind\":\"exception\",\"code\":\"0x%08lx\",\"first_chance\":%lu,\"address\":\"0x%zx\"",code,exception.dwFirstChance,address);
                for(const auto& module:modules)if(address>=module.base && address-module.base<module.size){std::fprintf(output,",\"rva\":\"0x%zx\",\"module\":",address-module.base);quoted(output,module.path);break;}
                if(exception.ExceptionRecord.NumberParameters>=2)std::fprintf(output,",\"parameter0\":%zu,\"parameter1\":\"0x%zx\"",static_cast<std::size_t>(exception.ExceptionRecord.ExceptionInformation[0]),static_cast<std::size_t>(exception.ExceptionRecord.ExceptionInformation[1]));std::fputs("}\n",output);
                disposition=DBG_EXCEPTION_NOT_HANDLED;if(!exception.dwFirstChance){TerminateProcess(process.hProcess,0xe0434205);terminating=true;}
            }
        }else if(event.dwDebugEventCode==EXIT_PROCESS_DEBUG_EVENT){std::fprintf(output,"{\"kind\":\"exit\",\"code\":\"0x%08lx\"}\n",event.u.ExitProcess.dwExitCode);exited=true;}
        std::fflush(output);if(!ContinueDebugEvent(event.dwProcessId,event.dwThreadId,disposition)){std::fprintf(output,"{\"kind\":\"continue_error\",\"error\":%lu}\n",GetLastError());break;}
    }
    if(!exited){TerminateProcess(process.hProcess,0xe0434206);WaitForSingleObject(process.hProcess,5000);}CloseHandle(process.hThread);CloseHandle(process.hProcess);
    std::fprintf(output,"{\"kind\":\"summary\",\"main_reached\":%s,\"after_sound_reached\":%s,\"exit_observed\":%s}\n",mainReached?"true":"false",stopReached?"true":"false",exited?"true":"false");std::fclose(output);return 0;
}
