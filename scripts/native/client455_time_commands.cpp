#include "client455_time_commands.h"
#include "client455_clock.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static_assert(sizeof(long)==4,"455 decimal command arguments are signed32");

extern "C" int RF455_TryClockCommand(const char* input) {
    char copy[257],token[260];
    strncpy(copy,input,256);copy[256]=0;_strlwr(copy);
    const char* cursor=copy;
    for (;;) {
        if (sscanf(cursor,"%s",token)==EOF) return 0;
        // Deliberately preserve the reference's length-only advance, including
        // its leading/multiple-whitespace quirks. Do not replace with strtok.
        cursor+=strlen(token);
        if (!strcmp(token,"end")) return 0;
        if (!strcmp(token,"%time")) {
            if (sscanf(cursor,"%s",token)==EOF) return 0;
            // The pinned atol wrapper calls strtol(input,NULL,10), including
            // signed32 saturation before unsigned HMS wrapping.
            const unsigned hours=(unsigned)strtol(token,NULL,10);
            RF455_SetDayTime(hours,0,0);return 1;
        }
        if (!strcmp(token,"%real_time")) {
            if (sscanf(cursor,"%s",token)==EOF) return 0;
            const unsigned hours=(unsigned)strtol(token,NULL,10);
            if (sscanf(cursor+strlen(token)+1,"%s",token)==EOF) return 0;
            const unsigned minutes=(unsigned)strtol(token,NULL,10);
            RF455_SetRealDayTime(hours,minutes,0);return 1;
        }
        // Those reference directives terminate parsing before later tokens.
        // Their camera/color behavior has not yet been implemented here.
        if (!strcmp(token,"%fov") || !strcmp(token,"%change_rgb") ||
            !strcmp(token,"%max_cam_dist") || !strcmp(token,"%floor_dist")) return 0;
    }
}
