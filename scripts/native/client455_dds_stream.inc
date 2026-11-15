#include <io.h>
#include <memory>
#include <stdlib.h>
#include <cstring>

// Measure the physical extent without changing the caller's stream position.
static __int64 RF455_TextureFileEnd(FILE* stream)
{
    return _filelengthi64(_fileno(stream));
}

static bool RF455_SkipDdsMipmaps(DDSURFACEDESC2& desc, DWORD detail,
                              DWORD maxWidth, DWORD maxHeight, size_t available,
                              size_t& skipped)
{
    DWORD steps = 0;
    while (steps < desc.dwMipMapCount) {
        if (steps >= detail && desc.dwWidth <= maxWidth && desc.dwHeight <= maxHeight)
            break;
        if (desc.lPitch < 0 || static_cast<size_t>(desc.lPitch) > available - skipped)
            return false;
        skipped += static_cast<size_t>(desc.lPitch);
        if (desc.dwHeight <= 4) break;
        desc.dwHeight /= 2;
        if (desc.dwWidth <= 4) break;
        desc.dwWidth /= 2;
        desc.lPitch /= 4;
        ++steps;
    }
    desc.dwMipMapCount -= steps;
    return true;
}

// Client 455 x86 RVA 0x4F1860. Transform only a private upload buffer.
template<class Read>
static LPDIRECT3DTEXTURE9 RF455_LoadDDS(DWORD size, DWORD mipmap, DWORD maxWidth,
                                     DWORD maxHeight, const Read& read)
{
    static_assert(sizeof(_DDS_Header) == 128, "DDS x86 stream header");
    auto* device = GetD3dDevice();
    if (!device) return NULL;
    _DDS_Header header = {};
    if (size < sizeof(header) || !read(0, &header, sizeof(header))) return NULL;
    if (header.dwMagic != 0x20534444) {
        UnLockDDS(reinterpret_cast<DWORD*>(&header));
        if (header.dwMagic != 0x20534444) return NULL;
    }

    size_t skipped = 0;
    const size_t available = size - sizeof(header);
    if (!RF455_SkipDdsMipmaps(header.ddsd, mipmap, maxWidth, maxHeight, available, skipped))
        return NULL;

    const size_t payloadBytes = available - skipped;
    const size_t uploadBytes = sizeof(header) + payloadBytes;
    std::unique_ptr<BYTE, decltype(&free)> bytes(static_cast<BYTE*>(malloc(uploadBytes)), free);
    if (!bytes) return NULL;
    std::memcpy(bytes.get(), &header, sizeof(header));
    if (!read(sizeof(header) + skipped, bytes.get() + sizeof(header), payloadBytes)) return NULL;

    FixDDSHeader(bytes.get());
    LPDIRECT3DTEXTURE9 texture = NULL;
    const HRESULT status = D3DXCreateTextureFromFileInMemory(
        device, bytes.get(), static_cast<UINT>(uploadBytes), &texture);
    if (FAILED(status)) {
        if (texture) texture->Release();
        return NULL;
    }
    if (!texture) return NULL;
    stNowTexMem += static_cast<DWORD>(payloadBytes);
    return texture;
}

LPDIRECT3DTEXTURE9 R3LoadDDSFromFP(FILE* fp, DWORD size, DWORD mipmap,
                                  DWORD maxWidth=2048, DWORD maxHeight=2048)
{
    if (!fp) return NULL;
    const __int64 start = _ftelli64(fp), fileEnd = RF455_TextureFileEnd(fp);
    if (start < 0 || fileEnd < start || size > fileEnd - start) return NULL;

    // A well-framed member is consumed even when DDS parsing or upload fails.
    struct FinishMember {
        FILE* stream;
        __int64 end;
        ~FinishMember() { _fseeki64(stream, end, SEEK_SET); }
    } finish = {fp, start + size};

    return RF455_LoadDDS(size, mipmap, maxWidth, maxHeight,
        [fp, start](size_t offset, void* destination, size_t length) {
            return !_fseeki64(fp, start + static_cast<__int64>(offset), SEEK_SET) &&
                fread(destination, 1, length, fp) == length;
        });
}

static LPDIRECT3DTEXTURE9 RF455_LoadDDSFromBytes(const unsigned char* data, DWORD size, DWORD mipmap,
                                                DWORD maxWidth=2048, DWORD maxHeight=2048)
{
    return RF455_LoadDDS(size, mipmap, maxWidth, maxHeight,
        [data](size_t offset, void* destination, size_t length) {
            std::memcpy(destination, data + offset, length);
            return true;
        });
}
