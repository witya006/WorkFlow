#pragma once

#include "client455_character_rfs.h"
#include "client455_shader_lights.h"
#include <array>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <vector>

class RF455MapShaderLights {
public:
    bool load(const char* path)
    {
        clear();
        if (!path || !*path) return false;
        auto* cache = RF455_GetCharacterRfsCache();
        const auto source = cache->ReadLooseBytes(path, headerSize + maxLights * recordSize);
        if (source.status != RF455ResourceReadStatus::Ready || !source.bytes) return false;
        if (parse(*source.bytes)) return true;

        cache->RemoveLooseBytes(path);
        return false;
    }

    void clear() { count_ = 0; }

    const RF455ShaderLight* at(unsigned index) const
    {
        return index < count_ ? &lights_[index] : nullptr;
    }

    template<class Device>
    void bind(Device* device, std::uint32_t materialFlags, const float* inverseViewRow) const
    {
        // 455 RVA 0x4FA150 runs this before the material shader dispatcher.
        if (count_ && (materialFlags & 0x10000000u)) {
            if (const auto* light = at(materialFlags & 0xffu))
                RF455_SetShaderLightConstants(device, *light);
        } else {
            device->SetVertexShaderConstantF(18, inverseViewRow, 1);
        }
    }

private:
    static constexpr unsigned maxLights = 101;
    static constexpr unsigned headerSize = 4;
    static constexpr unsigned recordSize = 32;
    std::array<RF455ShaderLight, maxLights> lights_;
    unsigned count_ = 0;

    static std::uint32_t word(const unsigned char* bytes)
    {
        return std::uint32_t(bytes[0]) | (std::uint32_t(bytes[1]) << 8) |
               (std::uint32_t(bytes[2]) << 16) | (std::uint32_t(bytes[3]) << 24);
    }

    bool parse(const std::vector<unsigned char>& bytes)
    {
        // x86 455 RVA 0x4B3130 reads a signed count followed by eight floats per light.
        if (bytes.size() < headerSize) return false;
        const auto count = word(bytes.data());
        if (count > maxLights || bytes.size() != headerSize + count * recordSize) return false;

        const auto* next = bytes.data() + headerSize;
        for (unsigned index = 0; index < count; ++index) {
            float wire[8];
            static_assert(sizeof(float) == sizeof(std::uint32_t), "455 R3L float layout");
            for (float& field : wire) {
                const auto bits = word(next);
                next += sizeof(bits);
                std::memcpy(&field, &bits, sizeof(bits));
                if (!std::isfinite(field)) return false;
            }
            auto& light = lights_[index];
            for (unsigned axis = 0; axis < 3; ++axis) {
                light.position[axis] = wire[axis];
                light.color[axis] = wire[axis + 3];
            }
            light.scale = wire[6];
            light.radius = wire[7];
        }
        count_ = count;
        return true;
    }
};
