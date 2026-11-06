#include "client455_tutorial_spatial.h"
#include <cmath>
#include <cstring>

#if !defined(_M_IX86)
#error The recovered tutorial arithmetic requires the Win32 x87 ABI.
#endif
extern "C" double __cdecl _CIsqrt(void);
extern "C" void __cdecl _ftol2_sse(void);

float RF455_TutorialDistanceXZ(const RF455TutorialVector& a, const RF455TutorialVector& b) {
    const float* first = a.data(); const float* second = b.data();
    float square, result;
    __asm {
        mov eax, second
        mov ecx, first
        fld DWORD PTR [eax+8]
        fsub DWORD PTR [ecx+8]
        fld DWORD PTR [eax]
        fsub DWORD PTR [ecx]
        fmul st, st
        fld st(1)
        fmulp st(2), st
        faddp st(1), st
        fstp square
        fld square
        call _CIsqrt
        fstp result
    }
    return result;
}

std::uint16_t RF455_TutorialCoordinateWord(float value) {
    std::uint16_t result;
    __asm {fld value
           call _ftol2_sse
           mov result, ax}
    return result;
}

RF455TutorialCreationIds& RF455_GetTutorialCreationIds() {
    static RF455TutorialCreationIds ids;
    return ids; // Process lifetime, independent of runtime.clear/quest refresh.
}

namespace {
std::uint32_t dword(const std::vector<std::uint8_t>& data, std::size_t at) {
    return std::uint32_t(data[at]) | (std::uint32_t(data[at+1]) << 8) |
           (std::uint32_t(data[at+2]) << 16) | (std::uint32_t(data[at+3]) << 24);
}
float scalar(const std::vector<std::uint8_t>& data, std::size_t at) {
    float result; std::memcpy(&result, data.data()+at, 4); return result;
}
RF455TutorialVector vector(const std::vector<std::uint8_t>& data, std::size_t at) {
    return {{scalar(data, at), scalar(data, at+4), scalar(data, at+8)}};
}
template<std::size_t N> void word(std::array<std::uint8_t, N>& data, std::size_t at, std::uint16_t value) {
    data[at] = std::uint8_t(value); data[at+1] = std::uint8_t(value >> 8);
}
template<std::size_t N> void putDword(std::array<std::uint8_t, N>& data, std::size_t at, std::uint32_t value) {
    word(data, at, std::uint16_t(value)); word(data, at+2, std::uint16_t(value >> 16));
}
float unsignedFloat(std::uint32_t value) {
    const std::int64_t wide = value; float result;
    __asm {fild wide
           fstp result}
    return result;
}
double radians(float yaw) {
    const double tau = 6.283185307, circle = 360.0; double result;
    __asm {fld yaw
           fmul tau
           fdiv circle
           fstp result}
    return result;
}
float offset(float position, float direction, std::uint32_t distance) {
    const std::int64_t wide = distance; float result;
    __asm {fld direction
           fild wide
           fmulp st(1), st
           fadd position
           fstp result}
    return result;
}

class Spatial : public RF455TutorialProcessor {
public:
    Spatial(const RF455TutorialInstruction& instruction, RF455TutorialSpatialHost& world)
        : RF455TutorialProcessor(instruction.dataType, instruction.id, instruction.fixed[4]), world(world) {}
protected:
    RF455TutorialSpatialHost& world;
    bool bound(RF455TutorialHost& host) {return &host == &world;}
};

class Position final : public Spatial {
public:
    Position(const RF455TutorialInstruction& instruction, RF455TutorialSpatialHost& world)
        : Spatial(instruction, world), value(vector(instruction.fixed, 8)) {}
private:
    RF455TutorialVector value;
    bool start(RF455TutorialHost& host, RF455TutorialContext& context) override {
        if (!bound(host)) return false;
        switch (type) {
        case 12: world.setAvatarPosition(value, true, false); flags |= 4; break;
        case 13: world.setAvatarYaw(value[1], true, 12.0f); flags |= 4; break;
        case 14: world.setCameraOrbit(value, true); flags |= 4; break;
        case 15: case 16:
            for (unsigned i = 0; i != 3; ++i) context.cameraRemaining[i] = std::fabs(value[i]);
            if (type == 15) world.animateCameraOrbit(value);
            break;
        case 18: world.setCameraParameter276(value[0] <= 0 ? 75.0f : value[0]); flags |= 4; break;
        }
        return true;
    }
    bool update(RF455TutorialHost& host, RF455TutorialContext& context) override {
        if (!bound(host) || (type != 15 && type != 16)) return false;
        if (context.cameraRemaining[0] <= 1.0f && context.cameraRemaining[1] <= 1.0f &&
            context.cameraRemaining[2] <= 1.0f) return true;
        return std::uint32_t(host.milliseconds() - context.startTime) >= 20000;
    }
    void finish(RF455TutorialHost&, RF455TutorialContext&) override {}
};

class Move final : public Spatial {
public:
    Move(const RF455TutorialInstruction& instruction, RF455TutorialSpatialHost& world)
        : Spatial(instruction, world), mode(instruction.fixed[6]), amount(dword(instruction.fixed, 8)),
          target(vector(instruction.fixed, 8)) {}
private:
    std::uint8_t mode;
    std::uint32_t amount, marker = 0xffffffff;
    RF455TutorialVector target;
    bool start(RF455TutorialHost& host, RF455TutorialContext& context) override {
        if (!bound(host)) return false;
        if (type == 6 || type == 7) {
            if (mode == 0) {
                marker = world.placeMarker(target, 0.0f, 1358954291U, 0, 0);
                if (type == 6) requestMove();
            } else if (mode == 1) {
                context.remainingDistance = unsignedFloat(amount);
                if (type == 6) {
                    const float x = world.avatarX();
                    const float sine = static_cast<float>(std::sin(radians(world.avatarYaw())));
                    const float tx = offset(x, sine, std::uint32_t(amount + 2));
                    const float ty = world.avatarY();
                    const float z = world.avatarZ();
                    const float cosine = static_cast<float>(std::cos(radians(world.avatarYaw())));
                    RF455TutorialVector point = {{tx, ty, offset(z, cosine, std::uint32_t(amount + 2))}};
                    world.createAvatarPath(point);
                    world.turnAvatarToward(point, true, 12.0f);
                    world.avatarState(0x10000001, true);
                }
            } else if (mode == 2) flags |= 4;
        } else if (type == 8) {
            world.avatarToggle(mode == 1, false); flags |= 4;
        }
        context.operationActive = 1;
        return true;
    }
    void requestMove() {
        world.createAvatarPath(target);
        world.turnAvatarToward(target, true, 12.0f);
        world.avatarState(0x10000001, true);
    }
    bool update(RF455TutorialHost& host, RF455TutorialContext& context) override {
        if (!bound(host)) return false;
        if (mode == 0) {
            if (RF455_TutorialDistanceXZ(world.avatarPosition(), target) <= 15.0f) {
                world.releaseMarker(marker, 1.0f); return true;
            }
        } else if (mode == 1) {
            if (context.remainingDistance <= 1.0f) return true;
            return std::uint32_t(host.milliseconds() - context.startTime) >= 20000;
        }
        return false;
    }
    void finish(RF455TutorialHost&, RF455TutorialContext& context) override {context.operationActive = 0;}
};

class Creation final : public Spatial {
public:
    Creation(const RF455TutorialInstruction& instruction, RF455TutorialSpatialHost& world, RF455TutorialCreationIds& ids)
        : Spatial(instruction, world), ids(ids), category(instruction.fixed[6]),
          index(dword(instruction.fixed, 8)), position(vector(instruction.fixed, 12)) {}
private:
    RF455TutorialCreationIds& ids;
    std::uint8_t category;
    std::uint32_t index;
    RF455TutorialVector position;
    bool start(RF455TutorialHost& host, RF455TutorialContext& context) override {
        if (!bound(host)) return false;
        std::uint32_t localIndex;
        if (type == 9) {
            if (world.resolveMonster(index, localIndex)) {
                std::array<std::uint8_t, 17> packet{};
                word(packet, 0, std::uint16_t(localIndex)); word(packet, 2, 1);
                putDword(packet, 4, ids.monster++);
                for (unsigned i = 0; i != 3; ++i) word(packet, 8 + 2*i, RF455_TutorialCoordinateWord(position[i]));
                world.localMonsterSpawn(packet);
            }
            flags |= 4;
        } else if (type == 10) {
            struct CloneScope {
                RF455TutorialSpatialHost& host;
                explicit CloneScope(RF455TutorialSpatialHost& host) : host(host) {host.beginItemClone();}
                ~CloneScope() {host.endItemClone();}
            } cloneScope(world);
            if (world.resolveItem(category, index, true, localIndex)) {
                static const std::uint8_t mapping[47] = {
                    14,0,1,2,3,4,6,5,7,8,9,10,11,13,12,16,17,18,15,19,20,21,22,23,
                    24,25,26,27,28,29,30,31,32,33,34,35,36,37,0,0,0,0,0,0,0,0,0};
                if (category >= 47) return false; // Target resolver rejects this before lookup succeeds.
                std::array<std::uint8_t, 25> packet;
                packet.fill(255); packet[0] = mapping[category];
                word(packet, 1, std::uint16_t(localIndex)); packet[3] = 1; word(packet, 4, ids.item++);
                for (unsigned i = 0; i != 3; ++i) word(packet, 18+2*i, RF455_TutorialCoordinateWord(position[i]));
                world.localItemSpawnKnown25(packet);
            }
            flags |= 4;
        }
        context.operationActive = 1;
        return true;
    }
    bool update(RF455TutorialHost& host, RF455TutorialContext& context) override {
        if (!bound(host) || type != 11) return false;
        if (!world.pendingCreations()) return true;
        return std::uint32_t(host.milliseconds() - context.startTime) >= 20000;
    }
    void finish(RF455TutorialHost&, RF455TutorialContext& context) override {context.operationActive = 0;}
};
}

std::unique_ptr<RF455TutorialProcessor> RF455TutorialSpatialFactory::create(const RF455TutorialInstruction& instruction) {
    if (instruction.selector < 6) return basic.create(instruction);
    const auto size = instruction.fixed.size();
    if (instruction.selector <= 8 && size == 20)
        return std::unique_ptr<RF455TutorialProcessor>(new Move(instruction, host));
    if (instruction.selector >= 9 && instruction.selector <= 11 && size == 24)
        return std::unique_ptr<RF455TutorialProcessor>(new Creation(instruction, host, ids));
    if (instruction.selector >= 12 && instruction.selector <= 18 && size == 20)
        return std::unique_ptr<RF455TutorialProcessor>(new Position(instruction, host));
    return nullptr;
}
