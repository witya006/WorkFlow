#ifndef RF455_EVENT_MUSIC_H
#define RF455_EVENT_MUSIC_H

#include <cstdint>
#include <string>
#include <vector>

class RF455ItemDataStore;
bool RF455_EventMusicMonsterCode(const RF455ItemDataStore&, std::uint32_t index, std::uint32_t& code);

class RF455EventMusicCatalog {
    struct Event {
        std::uint32_t slot;
        std::uint32_t monster;
    };
    std::vector<std::string> music;
    std::vector<Event> events;

public:
    bool loadBgm(const char* path);
    bool loadEventSound(const char* path);
    void clear();
    bool hasEventTracks() const { return !music.empty() && !events.empty(); }

    // The returned path is borrowed until the next successful BGM load or clear.
    const char* musicAt(std::uint32_t slot) const;
    const char* musicForMonster(std::uint32_t code) const;
    bool trackForMonster(std::uint32_t code, std::uint32_t& slot) const;
};

RF455EventMusicCatalog& RF455_GameEventMusicCatalog();

#endif
