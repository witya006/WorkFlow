#include "Character.h"

void EffectList::SetEffect(CHARACTEROBJECT* object, DWORD index) {
    // Preserve the legacy SDK table representation consumed/produced by its
    // genuine loader. This is an owned bounded bridge, not an assertion that
    // the missing inline or the newer 455 map implementation was recovered.
    if (index < 500 && legacy_present[index])
        EffectObjectManager::SetPartEffect(object, legacy_files[index], MAX_PATTERN_SIZE);
}
