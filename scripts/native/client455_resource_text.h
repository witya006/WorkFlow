#ifndef RF455_RESOURCE_TEXT_H
#define RF455_RESOURCE_TEXT_H

#include "client455_character_rfs.h"
#include <cctype>
#include <cstdio>
#include <cstring>
#include <limits>
#include <memory>

// CRT text input for bounded word scanners. Each reader has its own cursor.
class RF455ResourceText {
    static constexpr std::uint64_t unlimited = (std::numeric_limits<std::uint64_t>::max)();
    RF455ResourceBytes bytes;
    std::unique_ptr<FILE, decltype(&std::fclose)> file{nullptr, &std::fclose};
    std::size_t position = 0;
    std::size_t end = 0;
    std::uint64_t remaining = unlimited;
    bool shortStream = false;

    int nextArchiveByte() {
        if (!remaining) return EOF;
        const int value = std::fgetc(file.get());
        if (value == EOF) shortStream = true;
        if (value == EOF || value == 0x1a) {
            remaining = 0;
            return EOF;
        }
        --remaining;
        return value;
    }

    template<class Next, class Failed>
    static int wholeToken(char (&value)[256], Next next, Failed failed) {
        int ch;
        do { ch = next(); } while (ch != EOF && std::isspace(static_cast<unsigned char>(ch)));
        if (ch == EOF) {
            value[0] = '\0';
            return failed() ? 0 : EOF;
        }
        std::size_t length = 0;
        bool invalid = false;
        do {
            if (length < sizeof(value) - 1) value[length++] = static_cast<char>(ch);
            else invalid = true;
            if (!ch) invalid = true;
            ch = next();
        } while (ch != EOF && !std::isspace(static_cast<unsigned char>(ch)));
        value[length] = '\0';
        return invalid || failed() ? 0 : 1;
    }

public:
    bool bind(const RF455ResourceRead& source) {
        bytes = source.status == RF455ResourceReadStatus::Ready ? source.bytes : nullptr;
        file.reset();
        position = end = 0;
        remaining = unlimited;
        shortStream = false;
        if (!bytes) return false;
        end = bytes->size();
        if (end) {
            const auto* start = bytes->data();
            const auto* eof = static_cast<const unsigned char*>(std::memchr(start, 0x1a, end));
            if (eof) end = static_cast<std::size_t>(eof - start);
        }
        return true;
    }

    bool openStream(FILE* stream, std::uint64_t byteLimit = unlimited) {
        bind({});
        file.reset(stream);
        remaining = byteLimit;
        return file != nullptr;
    }

    bool open(const char* path) {
        bind({});
        if (!path || !*path) return false;
        auto* cache = RF455_GetCharacterRfsCache();
        constexpr std::size_t maxBytes = 1024u * 1024u;
        const auto budget = cache->ByteBudget();
        const auto limit = budget < maxBytes ? budget : maxBytes;
        if (limit) {
            const auto source = cache->ReadLooseBytes(path, limit);
            if (bind(source)) return true;
            if (source.status != RF455ResourceReadStatus::ReadError || source.declaredSize <= limit)
                return false;
        }
        return openStream(std::fopen(path, "rt"));
    }

    bool hasCachedInput() const { return bytes != nullptr; }
    bool failed() const { return shortStream || (file && std::ferror(file.get()) != 0); }

    // Consume a whole token, even when it exceeds the caller's buffer.
    // Return 1 for a token, EOF for clean end, or 0 for invalid data or I/O.
    int readExact(char (&value)[256]) {
        if (file && remaining == unlimited) return readExact(file.get(), value);
        return wholeToken(value, [this]() -> int {
            if (file) return nextArchiveByte();
            return position < end ? bytes->data()[position++] : EOF;
        }, [this] { return failed(); });
    }

    // Borrow an ordinary FILE for legacy callers. The caller still owns it.
    static int readExact(FILE* stream, char (&value)[256]) {
        if (!stream) {
            value[0] = '\0';
            return 0;
        }
        return wholeToken(value, [stream] { return std::fgetc(stream); },
                          [stream] { return std::ferror(stream) != 0; });
    }

    bool read(char (&value)[256]) {
        if (file) {
            if (remaining == unlimited) return std::fscanf(file.get(), "%255s", value) == 1;
            int ch;
            do { ch = nextArchiveByte(); } while (ch != EOF && std::isspace(ch));
            std::size_t length = 0;
            while (ch != EOF && !std::isspace(ch)) {
                value[length++] = static_cast<char>(ch);
                if (length == sizeof(value) - 1) break;
                ch = nextArchiveByte();
            }
            value[length] = '\0';
            return length != 0;
        }
        if (!bytes) return false;
        // CR/LF have identical whitespace semantics here. CTRL-Z ends the
        // text before tokenization, and %255s leaves excess bytes for the next read.
        const auto* data = bytes->data();
        while (position < end && std::isspace(data[position])) ++position;
        if (position == end) return false;
        const auto start = position;
        while (position < end && position - start < 255 && !std::isspace(data[position])) ++position;
        const auto length = position - start;
        std::memcpy(value, data + start, length);
        value[length] = '\0';
        return true;
    }
};

#endif
