#include <stdexcept>

// Same named helpers, exception classes and messages as the inspected x86
// msvcp60 exports. Build exception objects with the client's current /MT CRT;
// do not pass old string/exception object storage into modern constructors.
namespace std {
__declspec(noreturn) void __cdecl _Xlen() {
    throw length_error("string too long");
}
__declspec(noreturn) void __cdecl _Xran() {
    throw out_of_range("invalid string position");
}
}
