#include "client455_effect_log.h"
#include <cstdio>
#include <cstdint>

namespace {
const char path[] = ".\\NetLog\\EffectLog.log";
std::int32_t pending_clear;
void truncate_log() {
    // The reference forwards the fopen result to fclose without another guard.
    std::fclose(std::fopen(path, "wt"));
}
}

void RF455_EffectLog(const char* text) {
    FILE* file = std::fopen(path, "rt+");
    if (!file) file = std::fopen(path, "wt");
    if (!file) return;
    const long start = std::ftell(file);
    std::fseek(file, 0, SEEK_END);
    const long end = std::ftell(file);
    std::fputs(text, file);
    std::fclose(file);
    // Reference x86 SUB followed by signed comparisons. Preserve wrap explicitly.
    const std::uint32_t bits = static_cast<std::uint32_t>(end)-static_cast<std::uint32_t>(start);
    const std::int64_t measured = bits <= 0x7fffffffU ? bits : static_cast<std::int64_t>(bits)-0x100000000LL;
    if (measured > 10000000) truncate_log();
    else if (measured > 5000000) pending_clear = 1;
}

void RF455_ClearPendingEffectLog() {
    if (pending_clear) {
        pending_clear = 0;
        truncate_log();
    }
}
