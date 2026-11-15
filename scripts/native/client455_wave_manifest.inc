#include <cerrno>
#include <climits>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <new>
#include <stdexcept>
#include <vector>

static_assert(sizeof(_WAVE_LIST) == 64, "455 WaveList record");

static DWORD ReadWaveId455(const char* token)
{
    if (token[0] == '0' && (token[1] == 'x' || token[1] == 'X')) {
        DWORD value = 0;
        for (const char* digit = token + 2; *digit; ++digit) {
            unsigned nibble;
            if (*digit >= '0' && *digit <= '9') nibble = *digit - '0';
            else if (*digit >= 'a' && *digit <= 'f') nibble = *digit - 'a' + 10;
            else if (*digit >= 'A' && *digit <= 'F') nibble = *digit - 'A' + 10;
            else return 0;
            if (value > 0x0fffffffu) return 0;
            value = (value << 4) | nibble;
        }
        return value;
    }
    char* end = nullptr;
    errno = 0;
    const auto value = std::strtoll(token, &end, 10);
    if (token == end || errno == ERANGE || value < INT_MIN || value > INT_MAX)
        return 0;
    return static_cast<DWORD>(value);
}

static bool ReadWaveRows455(RF455ResourceText& input, std::vector<_WAVE_LIST>& rows)
{
    char hole[256];
    do {
        if (!input.read(hole)) return false;
    } while (std::strcmp(hole, "[WaveList]"));

    bool hasToken = input.read(hole);
    while (hasToken) {
        const DWORD id = ReadWaveId455(hole);
        if (id) {
            if (!input.read(hole)) return false;
            _strlwr(hole);
            const auto length = std::strlen(hole);
            if (length > 58) {
                hole[58] = '\0';
                @@LONG_WARNING@@
            } else {
                _WAVE_LIST row = {};
                std::memcpy(row.name, hole, length + 1);
                row.id = id;
                hasToken = input.read(hole);
                if (hasToken && !_stricmp(hole, "loop")) {
                    row.flag = _PLAY_WAVE_LOOP;
                    hasToken = input.read(hole);
                }
                rows.push_back(row);
                continue;
            }
        }
        hasToken = input.read(hole);
    }
    return !input.failed();
}

static void ReleaseWavePayload455(_WAVE_PTR_LIST& wave)
{
    if (wave.Handle) AIL_release_sample_handle(wave.Handle);
    if (wave.ptr) AIL_mem_free_lock(wave.ptr);
    wave.Handle = nullptr;
    wave.ptr = nullptr;
}

static void DiscardWaveSamples455()
{
    for (int i = 0; i < stWaveNum; ++i) {
        const DWORD id = stWaveList[i].id;
        void* cached = nullptr;
        if (stWaveCache.GetCache(id, &cached)) {
            ReleaseWavePayload455(*static_cast<_WAVE_PTR_LIST*>(cached));
            stWaveCache.DelCache(id);
        }
    }
}

// Client 455 x86 RVA 0x4BC680 reads this loose text manifest.
void LoadWaveList(char* name)
{
    if (!name) return;
    char warningName[160] = {};
    std::strncpy(warningName, name, sizeof(warningName) - 1);
    try {
        // An explicit reload must see a repaired, replaced or removed file.
        if (stWaveList) RF455_GetCharacterRfsCache()->RemoveLooseBytes(name);
        RF455ResourceText input;
        if (!input.open(name)) {
            @@OPEN_WARNING@@
            return;
        }
        std::vector<_WAVE_LIST> rows;
        if (!ReadWaveRows455(input, rows)) {
            if (input.hasCachedInput()) RF455_GetCharacterRfsCache()->RemoveLooseBytes(name);
            Warning(warningName, " <- Invalid or incomplete WaveList");
            return;
        }

        constexpr std::size_t initialCapacity = 256;
        constexpr std::size_t growth = 64;
        constexpr std::size_t maxCapacity = (INT_MAX - 4) / sizeof(_WAVE_LIST);
        if (rows.size() >= maxCapacity) throw std::bad_alloc();
        const auto capacity = rows.size() < initialCapacity ? initialCapacity :
            initialCapacity + ((rows.size() - initialCapacity) / growth + 1) * growth;
        if (capacity > maxCapacity) throw std::bad_alloc();

        const auto bytes = capacity * sizeof(_WAVE_LIST);
        std::unique_ptr<void, decltype(&Dfree)> staged(Dmalloc(static_cast<int>(bytes)), &Dfree);
        if (!staged) throw std::bad_alloc();
        std::memset(staged.get(), 0, bytes);
        if (!rows.empty())
            std::memcpy(staged.get(), rows.data(), rows.size() * sizeof(_WAVE_LIST));

        if (!stWaveList) {
            stWaveCache.CreateJcache(_SOUND_CACHE_NUM, sizeof(_WAVE_PTR_LIST));
        } else {
            DiscardWaveSamples455();
            Dfree(stWaveList);
        }
        stWaveList = static_cast<_WAVE_LIST*>(staged.release());
        stMaxWaveNum = static_cast<int>(capacity);
        stWaveNum = static_cast<int>(rows.size());
    } catch (const std::bad_alloc&) {
        Warning(warningName, " <- WaveList allocation failed");
    } catch (const std::length_error&) {
        Warning(warningName, " <- WaveList allocation failed");
    }
}

void ReleaseWaveList()
{
    DiscardWaveSamples455();
    stWaveCache.DestroyJcache();
    if (stWaveList) Dfree(stWaveList);
    stWaveList = nullptr;
    stWaveNum = 0;
    stMaxWaveNum = 0;
}
