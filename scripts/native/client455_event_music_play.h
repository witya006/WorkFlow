#ifndef RF455_EVENT_MUSIC_PLAY_H
#define RF455_EVENT_MUSIC_PLAY_H

#include <memory>

// An app-owned player. Clear the active samples before closing the Miles driver.
class RF455EventMusicPlayer {
    struct State;
    std::unique_ptr<State> state;

public:
    RF455EventMusicPlayer();
    ~RF455EventMusicPlayer();
    RF455EventMusicPlayer(const RF455EventMusicPlayer&) = delete;
    RF455EventMusicPlayer& operator=(const RF455EventMusicPlayer&) = delete;

    // A valid catalog slot owns its sample. Path is used only for first entry.
    bool Request(unsigned slot, const char* path, bool enter);
    void BeginObservation();
    bool Observe(unsigned slot, const char* path);
    void EndObservation();
    float MapGain() const;
    void Tick(float seconds);
    void Clear();
};

RF455EventMusicPlayer& RF455_GameEventMusicPlayer();

#endif
