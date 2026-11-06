#pragma once
#include <cstdint>
class ChInterface;
struct RF455CharacterStorage;
struct D3DXMATRIX;
class RF455RvpEffects {
public:
    RF455RvpEffects();~RF455RvpEffects();
    RF455RvpEffects(const RF455RvpEffects&)=delete;RF455RvpEffects& operator=(const RF455RvpEffects&)=delete;
    void Apply(ChInterface&,RF455CharacterStorage*,unsigned);
    void Draw(RF455CharacterStorage*,D3DXMATRIX*,unsigned);
    struct Runtime;Runtime* runtime;
};
struct RF455RvpEffectsView {
    bool present;unsigned references,particleDefinitions,entityDefinitions;
    unsigned loadedParticles,loadedEntities,particleSelections,particleDraws,entityDraws;
    float entityScroll;
};
RF455RvpEffects& RF455_AcquireRvpEffects();
void RF455_ReleaseRvpEffects();
RF455RvpEffectsView RF455_RvpEffectsState();
