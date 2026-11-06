#include "client455_tutorial_script.h"
#include <cstdio>
#include <cstring>
#include <limits>
#include <new>
#include <stdexcept>
#include <utility>

namespace {
struct Reader {
    const std::uint8_t* at;
    std::size_t remaining;
    bool read(void* out, std::size_t bytes) {
        if (bytes > remaining) return false;
        if (bytes) std::memcpy(out, at, bytes);
        at += bytes;
        remaining -= bytes;
        return true;
    }
    bool byte(std::uint8_t& value) { return read(&value, 1); }
    bool word(std::uint16_t& value) {
        std::uint8_t b[2];
        if (!read(b, 2)) return false;
        value = std::uint16_t(b[0]) | (std::uint16_t(b[1]) << 8);
        return true;
    }
    bool dword(std::uint32_t& value) {
        std::uint8_t b[4];
        if (!read(b, 4)) return false;
        value = std::uint32_t(b[0]) | (std::uint32_t(b[1]) << 8) |
                (std::uint32_t(b[2]) << 16) | (std::uint32_t(b[3]) << 24);
        return true;
    }
    bool bytes(std::vector<std::uint8_t>& out, std::size_t count) {
        if (count > remaining || count > out.max_size()) return false;
        out.assign(at, at + count);
        at += count;
        remaining -= count;
        return true;
    }
};

struct Writer {
    std::vector<std::uint8_t> data;
    void bytes(const void* p, std::size_t size) {
        if (!size) return;
        const auto* first = static_cast<const std::uint8_t*>(p);
        data.insert(data.end(), first, first + size);
    }
    void byte(std::uint8_t value) { data.push_back(value); }
    void word(std::uint16_t value) { byte(std::uint8_t(value)); byte(std::uint8_t(value >> 8)); }
    void dword(std::uint32_t value) {
        word(std::uint16_t(value)); word(std::uint16_t(value >> 16));
    }
};

bool readMessage(Reader& r, RF455TutorialMessage& message) {
    std::uint8_t strings;
    if (!r.dword(message.id) || !r.byte(message.minimumLevel) ||
        !r.byte(message.maximumLevel) || !r.byte(message.map) ||
        !r.dword(message.action) || !r.dword(message.duration) ||
        !r.dword(message.display) || !r.byte(strings)) return false;
    if (strings > r.remaining / 14) return false;
    message.texts.resize(strings);
    for (auto& text : message.texts) {
        std::uint16_t length;
        if (!r.read(text.font.data(), text.font.size()) || !r.word(length) ||
            !r.bytes(text.bytes, length)) return false;
    }
    return true;
}

bool readInstruction(Reader& r, RF455TutorialInstruction& instruction) {
    if (!r.byte(instruction.selector)) return false;
    if (RF455_TutorialKind(instruction.selector) == RF455TutorialKind::Invalid) return false;
    if (instruction.selector < 4) {
        return r.byte(instruction.dataType) && r.word(instruction.id) &&
               readMessage(r, instruction.message);
    }
    if (!r.bytes(instruction.fixed, RF455_TutorialFixedSize(instruction.selector))) return false;
    instruction.dataType = instruction.fixed[0];
    instruction.id = std::uint16_t(instruction.fixed[2]) |
                     (std::uint16_t(instruction.fixed[3]) << 8);
    return true;
}
}

RF455TutorialKind RF455_TutorialKind(std::uint8_t selector) {
    if (selector < 4) return RF455TutorialKind::RichMessage;
    if (selector == 4) return RF455TutorialKind::MessageFixed;
    if (selector == 5) return RF455TutorialKind::Wait;
    if (selector <= 8) return RF455TutorialKind::Move;
    if (selector <= 11) return RF455TutorialKind::Creation;
    if (selector <= 18) return RF455TutorialKind::Position;
    if (selector <= 22) return RF455TutorialKind::Ui;
    if (selector <= 26) return RF455TutorialKind::Equip;
    if (selector <= 34) return RF455TutorialKind::Cursor;
    if (selector <= 39) return RF455TutorialKind::Combat;
    if (selector <= 46) return RF455TutorialKind::Item;
    return RF455TutorialKind::Invalid;
}

std::size_t RF455_TutorialFixedSize(std::uint8_t selector) {
    switch (RF455_TutorialKind(selector)) {
    case RF455TutorialKind::MessageFixed: return 16;
    case RF455TutorialKind::Wait:
    case RF455TutorialKind::Equip:
    case RF455TutorialKind::Item: return 12;
    case RF455TutorialKind::Move:
    case RF455TutorialKind::Position:
    case RF455TutorialKind::Cursor:
    case RF455TutorialKind::Combat: return 20;
    case RF455TutorialKind::Creation: return 24;
    case RF455TutorialKind::Ui: return 8;
    default: return 0;
    }
}

bool RF455_ParseTutorialScript(const void* data, std::size_t size, RF455TutorialScript& output) {
    if (!data || size < 4) return false;
    try {
        Reader r = {static_cast<const std::uint8_t*>(data), size};
        RF455TutorialScript next;
        std::uint32_t count;
        if (!r.dword(count) || count > r.remaining / 70 || count > next.quests.max_size()) return false;
        next.quests.resize(count);
        for (auto& quest : next.quests) {
            std::uint16_t instructions;
            if (!r.dword(quest.id) || !r.read(quest.name.data(), quest.name.size()) ||
                !r.word(instructions) || instructions > r.remaining / 9) return false;
            quest.instructions.resize(instructions);
            for (auto& instruction : quest.instructions) {
                if (!readInstruction(r, instruction)) return false;
            }
        }
        if (!r.bytes(next.trailer, r.remaining)) return false;
        output = std::move(next);
        return true;
    } catch (const std::bad_alloc&) { return false; }
      catch (const std::length_error&) { return false; }
}

bool RF455_LoadTutorialScript(const char* path, RF455TutorialScript& output) {
    if (!path) return false;
    std::FILE* file = std::fopen(path, "rb");
    if (!file) return false;
    if (std::fseek(file, 0, SEEK_END)) { std::fclose(file); return false; }
    const long size = std::ftell(file);
    if (size < 0 || std::fseek(file, 0, SEEK_SET)) { std::fclose(file); return false; }
    std::vector<std::uint8_t> bytes;
    try { bytes.resize(static_cast<std::size_t>(size)); }
    catch (const std::bad_alloc&) { std::fclose(file); return false; }
    catch (const std::length_error&) { std::fclose(file); return false; }
    const bool read = std::fread(bytes.data(), 1, bytes.size(), file) == bytes.size();
    std::fclose(file);
    return read && RF455_ParseTutorialScript(bytes.data(), bytes.size(), output);
}

bool RF455_EncodeTutorialScript(const RF455TutorialScript& script, std::vector<std::uint8_t>& output) {
    if (script.quests.size() > std::numeric_limits<std::uint32_t>::max()) return false;
    try {
        Writer w;
        w.dword(static_cast<std::uint32_t>(script.quests.size()));
        for (const auto& quest : script.quests) {
            if (quest.instructions.size() > 65535) return false;
            w.dword(quest.id);
            w.bytes(quest.name.data(), quest.name.size());
            w.word(static_cast<std::uint16_t>(quest.instructions.size()));
            for (const auto& instruction : quest.instructions) {
                if (RF455_TutorialKind(instruction.selector) == RF455TutorialKind::Invalid) return false;
                w.byte(instruction.selector);
                if (instruction.selector < 4) {
                    const auto& message = instruction.message;
                    if (message.texts.size() > 255 || !instruction.fixed.empty()) return false;
                    w.byte(instruction.dataType); w.word(instruction.id); w.dword(message.id);
                    w.byte(message.minimumLevel); w.byte(message.maximumLevel); w.byte(message.map);
                    w.dword(message.action); w.dword(message.duration); w.dword(message.display);
                    w.byte(static_cast<std::uint8_t>(message.texts.size()));
                    for (const auto& text : message.texts) {
                        if (text.bytes.size() > 65535) return false;
                        w.bytes(text.font.data(), text.font.size());
                        w.word(static_cast<std::uint16_t>(text.bytes.size()));
                        w.bytes(text.bytes.data(), text.bytes.size());
                    }
                } else {
                    if (instruction.fixed.size() != RF455_TutorialFixedSize(instruction.selector)) return false;
                    auto fixed = instruction.fixed;
                    fixed[0] = instruction.dataType;
                    fixed[2] = static_cast<std::uint8_t>(instruction.id);
                    fixed[3] = static_cast<std::uint8_t>(instruction.id >> 8);
                    w.bytes(fixed.data(), fixed.size());
                }
            }
        }
        w.bytes(script.trailer.data(), script.trailer.size());
        output = std::move(w.data);
        return true;
    } catch (const std::bad_alloc&) { return false; }
      catch (const std::length_error&) { return false; }
}
