#pragma once
#include <windows.h>

// Selected CProcessMagic prefix member, at+36. No implicit lifetime policy:
// the target empty DestroyMagicTrack does not release these linked nodes.
struct RF455MagicCurveNode {
    BYTE flags;BYTE padding[3];
    float begin,end,angle,curve;
    RF455MagicCurveNode* previous;RF455MagicCurveNode* next;
};
struct RF455MagicControl {
    BYTE count;BYTE padding0[3];RF455MagicCurveNode* first;RF455MagicCurveNode* last;
    BYTE multiple;BYTE padding1[3];float angle;DWORD delay;
    void Add455(BYTE,float,float,float);
    void Multiple455(BYTE n,float a,DWORD d){multiple=n;angle=a;delay=d;}
};
static_assert(sizeof(RF455MagicCurveNode)==28,"455 curve node");
static_assert(sizeof(RF455MagicControl)==24,"455 magic control member");
