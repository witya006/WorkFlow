"""Stage the backing allocations and LRU updates for the legacy CJcache ABI."""


def port_wave_cache(raw: bytes) -> bytes:
    if not raw.startswith(b'#include "CJcache.h"') or any(
        raw.count(b"CJcache::" + name + b"(") != 1
        for name in (
            b"CreateJcache", b"DestroyJcache", b"CJcache", b"~CJcache",
            b"GetCacheLoopID", b"HitCache", b"GetCache", b"DelCache", b"GetCacheCnt",
        )
    ):
        raise ValueError("CJcache allocation and list boundaries changed")
    return br'''#include "CJcache.h"
#include <climits>
#include <cstdint>
#include <cstring>
#include <memory>
#include <new>

#define SetCache(num) (mCacheBitBuf[(num)>>3]|=(1<<((num)&7)))
#define UnSetCache(num) (mCacheBitBuf[(num)>>3]&=(~(1<<((num)&7))))
#define IsCached(num) (mCacheBitBuf[(num)>>3]&(1<<((num)&7)))

CJcache::CJcache()
    : mCacheBuf(nullptr), mCacheBitBuf(nullptr), mCacheNum(0), mStructSize(0),
      mContent(nullptr)
{
}

CJcache::~CJcache()
{
    DestroyJcache();
}

void CJcache::CreateJcache(DWORD cache_num, DWORD struct_size)
{
    constexpr auto maxAllocation = INT_MAX - 4;
    const auto bitBytes = cache_num / 8u + 1u;
    const auto payloadBytes = std::uint64_t(cache_num) * struct_size;
    const auto contentBytes = std::uint64_t(cache_num) * sizeof(_CJCACHE_CONTENT);
    if (!cache_num || !struct_size || payloadBytes > maxAllocation || contentBytes > maxAllocation)
        throw std::bad_alloc();

    using Block = std::unique_ptr<void, decltype(&Dfree)>;
    Block bits(Dmalloc(static_cast<int>(bitBytes)), &Dfree);
    Block payload(Dmalloc(static_cast<int>(payloadBytes)), &Dfree);
    Block content(Dmalloc(static_cast<int>(contentBytes)), &Dfree);
    if (!bits || !payload || !content)
        throw std::bad_alloc();
    std::memset(bits.get(), 0, bitBytes);
    std::memset(payload.get(), 0, static_cast<std::size_t>(payloadBytes));
    std::memset(content.get(), 0, static_cast<std::size_t>(contentBytes));

    DestroyJcache();
    mCacheBitBuf = static_cast<BYTE*>(bits.release());
    mCacheBuf = static_cast<BYTE*>(payload.release());
    mContent = static_cast<_CJCACHE_CONTENT*>(content.release());
    mCacheNum = cache_num;
    mStructSize = struct_size;
}

void CJcache::DestroyJcache()
{
    mCacheList.clear();
    if (mCacheBitBuf) Dfree(mCacheBitBuf);
    if (mCacheBuf) Dfree(mCacheBuf);
    if (mContent) Dfree(mContent);
    mCacheBitBuf = nullptr;
    mCacheBuf = nullptr;
    mContent = nullptr;
    mCacheNum = 0;
    mStructSize = 0;
}

DWORD CJcache::GetCacheLoopID()
{
    for (DWORD i = 0; i < mCacheNum; ++i) {
        if (!IsCached(i)) return i;
    }
    return static_cast<DWORD>(-1);
}

LONG CJcache::HitCache(DWORD id, void** get_cache_ptr)
{
    if (!mCacheNum)
        throw std::bad_alloc();
    for (auto it = mCacheList.begin(); it != mCacheList.end(); ++it) {
        const auto* content = *it;
        if (content->mID == id) {
            *get_cache_ptr = mCacheBuf + mStructSize * content->mLoopID;
            mCacheList.splice(mCacheList.begin(), mCacheList, it);
            return _HITCACHE_RET_OLD;
        }
    }
    if (mCacheList.size() >= mCacheNum) {
        auto oldest = mCacheList.end();
        --oldest;
        auto* content = *oldest;
        *get_cache_ptr = mCacheBuf + mStructSize * content->mLoopID;
        content->mID = id;
        mCacheList.splice(mCacheList.begin(), mCacheList, oldest);
        return _HITCACHE_RET_DEL_AND_NEW;
    }

    const DWORD slot = GetCacheLoopID();
    if (slot == static_cast<DWORD>(-1))
        throw std::bad_alloc();
    mCacheList.push_front(mContent + slot);
    mContent[slot].mID = id;
    mContent[slot].mLoopID = slot;
    SetCache(slot);
    *get_cache_ptr = mCacheBuf + mStructSize * slot;
    std::memset(*get_cache_ptr, 0, mStructSize);
    return _HITCACHE_RET_NEW;
}

BOOL CJcache::GetCache(DWORD id, void** get_cache_ptr)
{
    for (const auto* content : mCacheList) {
        if (content->mID == id) {
            *get_cache_ptr = mCacheBuf + mStructSize * content->mLoopID;
            return TRUE;
        }
    }
    return FALSE;
}

BOOL CJcache::DelCache(DWORD id)
{
    for (auto it = mCacheList.begin(); it != mCacheList.end(); ++it) {
        const auto* content = *it;
        if (content->mID == id) {
            UnSetCache(content->mLoopID);
            mCacheList.erase(it);
            return TRUE;
        }
    }
    return FALSE;
}

DWORD CJcache::GetCacheCnt()
{
    return static_cast<DWORD>(mCacheList.size());
}
'''
