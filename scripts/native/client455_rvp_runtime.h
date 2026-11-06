#pragma once
#include <cstddef>
#include <cstdint>
class CLevel;
struct RF455RvpRuntimeView {
    bool movieLoaded,cameraLoaded,playing,paused;
    std::size_t tracks,cursor;
    std::uint32_t cameraSelections,fadeIns,fadeOuts;
    float seconds,blur;
    const char* limitation;
    std::size_t actors;
    std::uint32_t visibleActors,poseUpdates,actorDraws;
    std::uint32_t waveEvents,ambientStarts,ambientStops;
};
struct RF455RvpActorRuntime;
const RF455RvpActorRuntime* RF455_RvpActorState(std::size_t);
void RF455_RvpCreate(char*,CLevel*);
void RF455_RvpRelease();
void RF455_RvpFrameMove();
void RF455_RvpRender();
void RF455_RvpStart(bool);
void RF455_RvpPause(bool);
RF455RvpRuntimeView RF455_RvpView();
