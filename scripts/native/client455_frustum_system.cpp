#include "client455_frustum.h"
#include <windows.h>
#include <cwchar>

namespace {
struct MatrixRuntime {
    HMODULE module=nullptr;RF455MatrixMultiply multiply=nullptr;
    MatrixRuntime(){
        wchar_t path[MAX_PATH];const unsigned n=GetSystemDirectoryW(path,MAX_PATH);
        if(!n || n+16>=MAX_PATH)return;
        std::wcscat(path,L"\\d3dx9_36.dll");module=LoadLibraryW(path);
        if(module)multiply=reinterpret_cast<RF455MatrixMultiply>(GetProcAddress(module,"D3DXMatrixMultiply"));
    }
    ~MatrixRuntime(){if(module)FreeLibrary(module);}
};
}
extern "C" int RF455_PublishSystemCharacterFrustum(float planes[6][4],const float view[16],const float projection[16]){
    static MatrixRuntime runtime;
    if(!runtime.multiply)return 0;
    RF455_PublishCharacterFrustum(planes,view,projection,runtime.multiply);return 1;
}
