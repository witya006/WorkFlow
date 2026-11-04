#include "Character.h"
#include <cstring>

void ChInterface::SetTexPath(CHARACTEROBJECT* object, char* source) {
    // 455 VA 0x608140 guards Source, copies 255 bytes and leaves byte 255 alone.
    // The legacy SDK consumes the path at +272; the 455 object uses +276.
    if (source) std::strncpy(object->legacy_texture_path, source, 255);
}

void CRender::SetMipMap(DWORD value) {
    // The 455 wrapper delegates to its embedded TextureManager. Adapt to the
    // legacy manager's checked +156 field consumed by AddTexture/CHR3LoadDDS.
    m_TM.legacy_mip_skip = value;
}
