#include "Character.h"
#include <cstring>

// Fields +4/+8/+12/+16 are zeroed by the inlined CObjectManager construction
// in supplied ChInterface::AddPartToMM (member_06.obj, function offsets 0x40..0x49).
// The allocator/padding bytes are opaque; establish a defined empty owned state.
CObjectManager::CObjectManager()
    : legacy_begin(nullptr), legacy_end(nullptr), legacy_capacity(nullptr), legacy_next_id(0) {
    std::memset(unknown_000, 0, sizeof(unknown_000));
    std::memset(legacy_name, 0, sizeof(legacy_name));
}

// Reconstruct the empty-container invariant consumed by the supplied algorithms,
// then use their own Init() for the counter fields (+16=0, +20=1).
// This is an owned reconstruction, not a claim to have found the original inline
// constructor. No undocumented singleton assignment is invented.
AnimationManager::AnimationManager()
    : legacy_begin(nullptr), legacy_end(nullptr), legacy_capacity(nullptr) {
    std::memset(unknown_000, 0, sizeof(unknown_000));
    Init(); // The old body has no defined int return; deliberately discard it.
}
