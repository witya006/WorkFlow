#ifndef RF455_EFFECT_INI_H
#define RF455_EFFECT_INI_H

#include "client455_character_rfs.h"
#include <windows.h>
#include <cstring>
#include <limits>
#include <map>
#include <new>

// These callers read a single named section/key from loose CHEF profiles.
// The index borrows its text from the immutable encoded resource for one load.
class RF455EffectIni {
    struct Text {
        const char* data = nullptr;
        std::size_t size = 0;
    };

    struct AsciiLess {
        static unsigned char lower(unsigned char ch) {
            return ch >= 'A' && ch <= 'Z' ? static_cast<unsigned char>(ch + 'a' - 'A') : ch;
        }

        bool operator()(Text a, Text b) const {
            const auto count = a.size < b.size ? a.size : b.size;
            for (std::size_t i = 0; i < count; ++i) {
                const auto left = lower(a.data[i]);
                const auto right = lower(b.data[i]);
                if (left != right) return left < right;
            }
            return a.size < b.size;
        }
    };

    using Keys = std::map<Text, Text, AsciiLess>;
    const char* path_;
    RF455ResourceBytes bytes_;
    std::map<Text, Keys, AsciiLess> sections_;
    bool indexed_ = false;

    static bool isSpace(char ch) {
        return ch == ' ' || (ch >= '\t' && ch <= '\r');
    }

    static Text trim(Text text) {
        while (text.size && isSpace(*text.data)) {
            ++text.data;
            --text.size;
        }
        while (text.size && isSpace(text.data[text.size - 1])) --text.size;
        return text;
    }

    static Text fromString(const char* text) {
        return {text, text ? std::strlen(text) : 0u};
    }

    static bool asciiName(Text text) {
        for (std::size_t i = 0; i < text.size; ++i)
            if (static_cast<unsigned char>(text.data[i]) >= 0x80) return false;
        return true;
    }

    bool index() {
        const auto size = bytes_->size();
        if (!size) return true;
        const auto* raw = bytes_->data();
        if ((size >= 2 && ((raw[0] == 0xff && raw[1] == 0xfe) ||
                           (raw[0] == 0xfe && raw[1] == 0xff))) ||
            (size >= 3 && raw[0] == 0xef && raw[1] == 0xbb && raw[2] == 0xbf) ||
            std::memchr(raw, 0, size)) return false;

        const auto* first = reinterpret_cast<const char*>(raw);
        const auto* end = first + size;
        Keys* keys = nullptr;
        unsigned indexedRows = 0;
        while (first != end) {
            const auto* last = first;
            while (last != end && *last != '\n' && *last != '\r') ++last;
            const auto line = trim({first, static_cast<std::size_t>(last - first)});
            first = last == end ? end : last + 1;
            if (!line.size || line.data[0] == ';') continue;

            if (line.data[0] == '[') {
                const auto* close = line.data + line.size;
                while (close != line.data && close[-1] != ']') --close;
                const auto* nameEnd = close == line.data ? line.data + line.size : close - 1;
                const auto section = trim({line.data + 1, static_cast<std::size_t>(nameEnd - line.data - 1)});
                if (!asciiName(section)) return false;
                if (++indexedRows > 32768) return false;
                const auto inserted = sections_.emplace(section, Keys{});
                keys = inserted.second ? &inserted.first->second : nullptr;
                continue;
            }

            if (!keys) continue;
            const auto* equals = static_cast<const char*>(std::memchr(line.data, '=', line.size));
            if (!equals) continue;
            const auto key = trim({line.data, static_cast<std::size_t>(equals - line.data)});
            if (!key.size) continue;
            if (!asciiName(key)) return false;
            if (++indexedRows > 32768) return false;
            auto value = trim({equals + 1, static_cast<std::size_t>(line.data + line.size - equals - 1)});
            if (value.size >= 2 && (value.data[0] == '"' || value.data[0] == '\'') &&
                value.data[value.size - 1] == value.data[0]) {
                ++value.data;
                value.size -= 2;
            }
            keys->emplace(key, value);
        }
        return true;
    }

    Text find(const char* section, const char* key) const {
        const auto foundSection = sections_.find(fromString(section));
        if (foundSection == sections_.end()) return {};
        const auto found = foundSection->second.find(fromString(key));
        return found == foundSection->second.end() ? Text{} : found->second;
    }

public:
    explicit RF455EffectIni(const char* path) : path_(path) {
        auto* cache = RF455_GetCharacterRfsCache();
        if (!path || !*path || !cache) return;
        // Bare filenames have special lookup rules in the Win32 profile API.
        if (!std::strchr(path, '\\') && !std::strchr(path, '/')) return;
        const auto source = cache->ReadLooseBytes(path, 2u * 1024u * 1024u);
        if (source.status != RF455ResourceReadStatus::Ready || !source.bytes) return;
        bytes_ = source.bytes;
        try {
            indexed_ = index();
        } catch (const std::bad_alloc&) {
        }
        if (!indexed_) {
            sections_.clear();
            bytes_.reset();
        }
    }

    bool usesCache() const { return indexed_; }

    DWORD readString(const char* section, const char* key, const char* defaultText,
                     char* out, DWORD capacity) const {
        if (!indexed_ || !section || !key)
            return GetPrivateProfileStringA(section, key, defaultText, out, capacity, path_);
        if (!out || !capacity) return 0;
        auto value = find(section, key);
        if (!value.data) {
            value = fromString(defaultText);
            while (value.size && value.data[value.size - 1] == ' ') --value.size;
        }
        const auto copied = value.size < capacity ? value.size : capacity - 1;
        if (copied) std::memcpy(out, value.data, copied);
        out[copied] = '\0';
        return static_cast<DWORD>(copied);
    }

    UINT readInt(const char* section, const char* key, int defaultValue) const {
        if (indexed_ && section && key) {
            const auto value = find(section, key);
            if (!value.data) return static_cast<UINT>(defaultValue);
            if (value.size && value.size <= 10) {
                std::uint64_t number = 0;
                std::size_t i = 0;
                for (; i < value.size && value.data[i] >= '0' && value.data[i] <= '9'; ++i)
                    number = number * 10 + static_cast<unsigned>(value.data[i] - '0');
                if (i == value.size && number <= (std::numeric_limits<UINT>::max)())
                    return static_cast<UINT>(number);
            }
        }
        // The registry counts are ordinary decimal. Keep native conversion for
        // custom count syntax and malformed values.
        return GetPrivateProfileIntA(section, key, defaultValue, path_);
    }
};

#endif
