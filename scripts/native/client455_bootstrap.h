#pragma once
#include <cstdint>
struct RF455BootstrapSettings{std::int32_t useFG=0;};
const RF455BootstrapSettings*RF455_GetBootstrapSettings();
void RF455_LoadBootstrapSettings();
bool RF455_InstancePolicyBypassed(unsigned nation);
bool RF455_ExecutableNameMatches(const char*path);
unsigned RF455_CountClientProcesses();
enum class RF455InstanceResult{Accepted,WrongFilename,TooManyProcesses,ExistingMutex};
RF455InstanceResult RF455_CheckSingleInstance();
bool RF455_CheckStartupInstance();
