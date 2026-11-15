#pragma once

#include "client455_character_rfs.h"
#include <cstddef>
#include <memory>
#include <new>
#include <utility>
#include <vector>

struct RF455BspPosition { float coordinates[3]; };
using RF455BspPositions = std::vector<RF455BspPosition>;

// Used on the scene owner thread. Raw file leases are weak keys, so retaining
// decoded corners never extends the lifetime of a map's encoded data.
class RF455BspPositionCache {
public:
    std::shared_ptr<const RF455BspPositions> find(const RF455ResourceBytes& source, std::size_t corners)
    {
        prune();
        if (!source) return {};

        for (auto& entry : entries_) {
            if (entry.positions && entry.positions->size() == corners && sameSource(entry, source)) {
                if (&entry != &entries_[0]) std::swap(entries_[0], entry);
                return entries_[0].positions;
            }
        }
        return {};
    }

    static std::shared_ptr<RF455BspPositions> stage(std::size_t corners)
    {
        if (!corners || corners > maxCorners) return {};
        try {
            return std::make_shared<RF455BspPositions>(corners);
        } catch (const std::bad_alloc&) {
            return {};
        }
    }

    void publish(const RF455ResourceBytes& source, std::shared_ptr<const RF455BspPositions> positions)
    {
        prune();
        if (!source || !positions || positions->empty() || positions->capacity() > maxCorners) return;

        // Replace a prior entry for this lease, then evict the oldest as needed.
        if (sameSource(entries_[0], source)) entries_[0] = std::move(entries_[1]);
        entries_[1] = {};
        if (entries_[0].positions && entries_[0].positions->capacity() <= maxCorners - positions->capacity())
            entries_[1] = std::move(entries_[0]);
        entries_[0] = Entry{source, std::move(positions)};
    }

private:
    static constexpr std::size_t maxBytes = 16u * 1024u * 1024u;
    static constexpr std::size_t maxCorners = maxBytes / sizeof(RF455BspPosition);

    struct Entry {
        std::weak_ptr<RF455ResourceBytes::element_type> source;
        std::shared_ptr<const RF455BspPositions> positions;
    };
    Entry entries_[2]; // Most recent first. Capacity excludes caller-held leases.

    static bool sameSource(const Entry& entry, const RF455ResourceBytes& source)
    {
        return !entry.source.owner_before(source) && !source.owner_before(entry.source) &&
            entry.source.lock().get() == source.get();
    }

    void prune()
    {
        for (auto& entry : entries_)
            if (entry.source.expired()) entry = {};
        if (!entries_[0].positions) std::swap(entries_[0], entries_[1]);
    }
};
