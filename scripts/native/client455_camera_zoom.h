#pragma once

#include <algorithm>

// User-selected extension of the wheel range. Mode defaults and fixed cameras
// remain unchanged; only the maximum wheel distance is extended fourfold.
inline float RF455_CameraWheelDistance(float current, int wheelDelta, unsigned cameraMode) {
    const float maximum = cameraMode == 1 ? 300.0f : 240.0f;
    return (std::max)(10.0f, (std::min)(maximum, current - wheelDelta * 0.07f));
}
