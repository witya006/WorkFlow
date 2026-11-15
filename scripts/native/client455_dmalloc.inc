#include <atomic>
#include <climits>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <limits>

namespace {
static_assert(sizeof(int) == 4, "455 Dmalloc header size");
std::atomic<std::uint64_t> allocatedBytes455{0};

int dmallocBytes455(const void* buffer)
{
    int size;
    std::memcpy(&size, static_cast<const unsigned char*>(buffer) - sizeof(size), sizeof(size));
    return size;
}
}

// 455 x86 RVA 0x4F1640 stores the requested byte count before the payload.
void* Dmalloc(int size)
{
    if (size <= 0) return nullptr;
    const auto bytes = static_cast<std::size_t>(size);
    if (bytes > (std::numeric_limits<std::size_t>::max)() - sizeof(size)) return nullptr;
    auto* block = static_cast<unsigned char*>(std::malloc(bytes + sizeof(size)));
    if (!block) return nullptr;

    std::memcpy(block, &size, sizeof(size));
    allocatedBytes455.fetch_add(bytes, std::memory_order_relaxed);
    return block + sizeof(size);
}

int GetDmallocSize()
{
    const auto bytes = allocatedBytes455.load(std::memory_order_relaxed);
    return bytes > INT_MAX ? INT_MAX : static_cast<int>(bytes);
}

void Dfree(void* buffer)
{
    if (!buffer) return;
    const int size = dmallocBytes455(buffer);
    if (size > 0) allocatedBytes455.fetch_sub(static_cast<unsigned>(size), std::memory_order_relaxed);
    std::free(static_cast<unsigned char*>(buffer) - sizeof(size));
}

// RVA 0x4F16B0 copies the common extent before releasing the old block.
void* ReAlloc(void* buffer, int oldSize, int newSize)
{
    if (newSize == 0) {
        Dfree(buffer);
        return nullptr;
    }
    if (newSize < 0 || oldSize < 0) return nullptr;
    if (!buffer) return Dmalloc(newSize);

    const int allocated = dmallocBytes455(buffer);
    if (allocated <= 0) return nullptr;
    auto* replacement = Dmalloc(newSize);
    if (!replacement) return nullptr;
    int copySize = oldSize < allocated ? oldSize : allocated;
    if (newSize < copySize) copySize = newSize;
    if (copySize) std::memcpy(replacement, buffer, static_cast<std::size_t>(copySize));
    Dfree(buffer);
    return replacement;
}
