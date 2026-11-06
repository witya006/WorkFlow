#pragma once
#include "client455_tutorial_runtime.h"

using RF455TutorialVector = std::array<float, 3>;

struct RF455TutorialCreationIds {
    std::uint16_t item = 0x0f00;
    std::uint32_t monster = 0x0000ffff;
};
RF455TutorialCreationIds& RF455_GetTutorialCreationIds();

class RF455TutorialSpatialHost : public RF455TutorialHost {
public:
    virtual void setAvatarPosition(const RF455TutorialVector&, bool, bool) = 0;
    virtual void setAvatarYaw(float, bool, float speed) = 0;
    virtual void setCameraOrbit(const RF455TutorialVector&, bool dirty) = 0;
    virtual void animateCameraOrbit(const RF455TutorialVector& relative) = 0;
    // Reference camera float276; its final gameplay name/provider is not yet certified.
    virtual void setCameraParameter276(float) = 0;
    virtual RF455TutorialVector avatarPosition() = 0;
    virtual float avatarX() = 0;
    virtual float avatarY() = 0;
    virtual float avatarZ() = 0;
    virtual float avatarYaw() = 0;
    virtual void createAvatarPath(const RF455TutorialVector&) = 0; //43EEF0 -> path5EE790
    virtual void turnAvatarToward(RF455TutorialVector& target, bool, float speed) = 0; //vt84 ->7CE550
    virtual void avatarState(std::uint32_t, bool) = 0;
    virtual void avatarToggle(bool, bool) = 0; //4115B0, QBI type8
    virtual std::uint32_t placeMarker(const RF455TutorialVector&, float, std::uint32_t, int, int) = 0;
    virtual void releaseMarker(std::uint32_t, float) = 0;
    virtual bool resolveMonster(std::uint32_t index, std::uint32_t& localIndex) = 0;
    virtual void beginItemClone() = 0; // Temporary CItem461A30; alive through local dispatch.
    virtual bool resolveItem(std::uint8_t category, std::uint32_t index, bool clone, std::uint32_t& localIndex) = 0;
    virtual void endItemClone() = 0;   // CItem461AE0, also after failed lookup.
    virtual void localMonsterSpawn(const std::array<std::uint8_t, 17>&) = 0;
    // Only these25bytes are initialized by the target QBI. Handler565A90 also
    // reads DWORD+25. Do not invent that unresolved stack tail in a real host.
    virtual void localItemSpawnKnown25(const std::array<std::uint8_t, 25>&) = 0;
    virtual std::uint32_t pendingCreations() = 0; //428250 -> container size
};

float RF455_TutorialDistanceXZ(const RF455TutorialVector&, const RF455TutorialVector&);
std::uint16_t RF455_TutorialCoordinateWord(float);

class RF455TutorialSpatialFactory final : public RF455TutorialFactory {
public:
    explicit RF455TutorialSpatialFactory(RF455TutorialSpatialHost& host,
        RF455TutorialCreationIds& ids = RF455_GetTutorialCreationIds()) : host(host), ids(ids) {}
    std::unique_ptr<RF455TutorialProcessor> create(const RF455TutorialInstruction&) override;
private:
    RF455TutorialSpatialHost& host;
    RF455TutorialCreationIds& ids;
    RF455TutorialBasicFactory basic;
};
