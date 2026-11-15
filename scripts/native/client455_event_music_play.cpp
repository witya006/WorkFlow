#include "client455_event_music_play.h"
#include "r3enginekernel.h"
#include "r3sound.h"
#include "mss.h"
#include <cmath>
#include <map>
#include <new>
#include <utility>

extern HDIGDRIVER stDigital;

namespace {
constexpr float fadeSeconds455 = 1.0f;

enum class TrackState455 { Idle, FadeIn, FadeOut };

struct EventTrack455 {
    HSAMPLE handle = nullptr;
    U32* buffer = nullptr;
    TrackState455 state = TrackState455::Idle;
    float elapsed = 0.0f;
    bool playing = false;
    bool restart = false;
    bool seen = false;

    ~EventTrack455() {
        if (handle) AIL_release_sample_handle(handle);
        if (buffer) AIL_mem_free_lock(buffer);
    }

    bool load(const char* path) {
        buffer = static_cast<U32*>(AIL_file_read(path, FILE_READ_WITH_SIZE));
        if (!buffer || !*buffer || *buffer > 0x7fffffffu) return false;
        handle = AIL_allocate_sample_handle(stDigital);
        if (!handle) return false;
        AIL_init_sample(handle);
        if (!AIL_set_named_sample_file(handle, path, buffer + 1, static_cast<S32>(*buffer), -1))
            return false;
        AIL_set_sample_loop_count(handle, 1);
        return true;
    }

    void stop() {
        if (playing) AIL_stop_sample(handle);
        playing = false;
    }
};

void fadeOutTrack455(EventTrack455& track)
{
    track.state = TrackState455::FadeOut;
    track.elapsed = 0.0f;
}

bool musicEnabled455()
{
    const auto* state = GetR3State();
    return state && state->mMusicOn;
}
}

struct RF455EventMusicPlayer::State {
    std::map<unsigned, std::unique_ptr<EventTrack455>> tracks;
    float mapGain = 1.0f;
};

RF455EventMusicPlayer::RF455EventMusicPlayer() : state(new State) {}
RF455EventMusicPlayer::~RF455EventMusicPlayer() = default;

bool RF455EventMusicPlayer::Request(unsigned slot, const char* path, bool enter)
{
    auto found = state->tracks.find(slot);
    if (!enter) {
        if (found == state->tracks.end()) return false;
        fadeOutTrack455(*found->second);
        return true;
    }
    if (!stDigital || !musicEnabled455()) return false;
    if (found == state->tracks.end()) {
        if (!path || !*path) return false;
        try {
            auto pending = std::unique_ptr<EventTrack455>(new EventTrack455);
            if (!pending->load(path)) return false;
            found = state->tracks.emplace(slot, std::move(pending)).first;
        } catch (const std::bad_alloc&) {
            return false;
        }
    }
    auto& track = *found->second;
    // 0x4BF100 re-arms the same loaded sample with a fresh fade.
    track.state = TrackState455::FadeIn;
    track.elapsed = 0.0f;
    track.restart = true;
    return true;
}

void RF455EventMusicPlayer::BeginObservation()
{
    for (auto& entry : state->tracks) entry.second->seen = false;
}

bool RF455EventMusicPlayer::Observe(unsigned slot, const char* path)
{
    if (!path || !*path) return false;
    const auto found = state->tracks.find(slot);
    if (found != state->tracks.end() && found->second->state == TrackState455::FadeIn) {
        found->second->seen = true;
        return true;
    }
    if (!Request(slot, path, true)) return false;
    state->tracks.find(slot)->second->seen = true;
    return true;
}

void RF455EventMusicPlayer::EndObservation()
{
    for (auto& entry : state->tracks) {
        auto& track = *entry.second;
        if (!track.seen && track.state == TrackState455::FadeIn) fadeOutTrack455(track);
    }
}

float RF455EventMusicPlayer::MapGain() const
{
    return state->mapGain;
}

void RF455EventMusicPlayer::Tick(float seconds)
{
    if (!stDigital) return;
    if (!musicEnabled455()) {
        // Muting silences loaded samples and keeps their cached data/fade position.
        for (auto& entry : state->tracks) entry.second->stop();
        return;
    }
    if (!std::isfinite(seconds) || seconds < 0.0f) seconds = 0.0f;
    float volume = GetGlobalMusicVolume();
    if (!std::isfinite(volume) || volume < 0.0f) volume = 0.0f;
    if (volume > 1.0f) volume = 1.0f;

    // 0x4BF2C0 keeps a requested track active after natural sample completion.
    bool eventRequested = false;
    for (auto& entry : state->tracks) {
        auto& track = *entry.second;
        if (track.state == TrackState455::Idle) continue;
        const bool fadingOut = track.state == TrackState455::FadeOut;
        if (!fadingOut) eventRequested = true;
        track.elapsed += seconds;
        if (track.elapsed > fadeSeconds455) track.elapsed = fadeSeconds455;
        const auto progress = track.elapsed / fadeSeconds455;
        AIL_set_sample_volume_pan(track.handle, volume * (fadingOut ? 1.0f - progress : progress), 0.5f);
        if (fadingOut && track.elapsed >= fadeSeconds455) {
            track.stop();
            track.state = TrackState455::Idle;
            track.restart = false;
            continue;
        }
        if (track.restart || !track.playing) {
            AIL_start_sample(track.handle);
            track.playing = true;
            track.restart = false;
        } else if (AIL_sample_status(track.handle) == SMP_DONE) {
            track.playing = false;
        }
    }
    const auto step = seconds / fadeSeconds455;
    if (eventRequested) state->mapGain = step < state->mapGain ? state->mapGain - step : 0.0f;
    else state->mapGain = step < 1.0f - state->mapGain ? state->mapGain + step : 1.0f;
}

void RF455EventMusicPlayer::Clear()
{
    state->tracks.clear();
    state->mapGain = 1.0f;
}
