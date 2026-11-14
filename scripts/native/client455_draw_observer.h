#pragma once
#include <d3d9.h>
// Optional presentation observer. The reusable geometry kernel does not own
// or depend on an engine/shadow renderer. Null restores the original path.
using RF455GeometryObserver=void(*)(IDirect3DDevice9*,unsigned,unsigned,unsigned,unsigned,unsigned,bool);
void RF455_SetGeometryObserver(RF455GeometryObserver);
bool RF455_SetGeometryObservationEnabled(bool);
struct RF455OpaqueGeometryObservation {
    bool previous;
    RF455OpaqueGeometryObservation():previous(RF455_SetGeometryObservationEnabled(true)){}
    ~RF455OpaqueGeometryObservation(){RF455_SetGeometryObservationEnabled(previous);}
};
