#include "client455_effect_log.h"
#include <cstdio>
#include <cstring>

static long size() {
    FILE* file = std::fopen(".\\NetLog\\EffectLog.log","rb");
    if (!file) return -1;
    std::fseek(file,0,SEEK_END);
    long result = std::ftell(file);
    std::fclose(file);
    return result;
}
int main(int argc,char** argv) {
    if (argc != 2) return 2;
    RF455_EffectLog("log\n");
    const long first = size();
    if (!std::strcmp(argv[1],"repeatclear")) {
        RF455_EffectLog("log\n");
        RF455_ClearPendingEffectLog();
    } else if (!std::strcmp(argv[1],"clear")) {
        RF455_ClearPendingEffectLog();
    } else if (!std::strcmp(argv[1],"shrinkclear")) {
        FILE* file = std::fopen(".\\NetLog\\EffectLog.log","wb");
        if (!file) return 3;
        std::fclose(file);
        RF455_EffectLog("log\n");
        RF455_ClearPendingEffectLog();
    } else if (std::strcmp(argv[1],"none")) return 4;
    std::printf("{\"first_size\":%ld,\"final_size\":%ld}\n",first,size());
    // No invented atexit flush: caller controls the explicit clear routine.
    return 0;
}
