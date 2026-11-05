#pragma once

using RF455MatrixMultiply = void* (__stdcall *)(void*,const void*,const void*);
extern "C" {
// Row-major matrices and six outward planes, matching 8C2A90/8C2C90.
// Normalization retains the original float spills and masked finite CRT sqrt.
void RF455_ExtractFrustumPlanes(float planes[6][4],const float clip[16]);
void RF455_PublishCharacterFrustum(float planes[6][4],const float view[16],
    const float projection[16],RF455MatrixMultiply multiply);
int RF455_IsBBoxInFrustum(const float minimum[3],const float maximum[3],const float planes[6][4]);
// Modern deployment adapter: resolves the pinned Microsoft D3DX9_36 runtime.
// Returns zero on missing runtime/export; callers must propagate the failure.
int RF455_PublishSystemCharacterFrustum(float planes[6][4],const float view[16],const float projection[16]);
}
