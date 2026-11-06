#include "client455_tutorial_script.h"
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iterator>
#include <stdexcept>
#include <string>
#include <vector>

using Bytes = std::vector<std::uint8_t>;
static void check(bool ok, const char* reason) { if (!ok) throw std::runtime_error(reason); }
static Bytes read(const std::string& path) {
    std::ifstream file(path, std::ios::binary);
    check(bool(file), "read fixture");
    return Bytes(std::istreambuf_iterator<char>(file), std::istreambuf_iterator<char>());
}
static void write(const std::string& path, const Bytes& data) {
    std::ofstream file(path, std::ios::binary);
    file.write(reinterpret_cast<const char*>(data.data()), data.size());
    check(bool(file), "write result");
}
static void byte(Bytes& bytes, std::uint8_t value) { bytes.push_back(value); }
static void word(Bytes& bytes, std::uint16_t value) {
    byte(bytes, std::uint8_t(value)); byte(bytes, std::uint8_t(value >> 8));
}
static void dword(Bytes& bytes, std::uint32_t value) {
    word(bytes, std::uint16_t(value)); word(bytes, std::uint16_t(value >> 16));
}
template<class Range> static void append(Bytes& out, const Range& bytes) {
    out.insert(out.end(), bytes.begin(), bytes.end());
}

// Independent semantic serialization: common fields are emitted from the named
// parsed members, not recovered by encoding and slicing the production wire.
static Bytes semantic(const RF455TutorialScript& script) {
    Bytes result;
    dword(result, static_cast<std::uint32_t>(script.quests.size()));
    for (const auto& quest : script.quests) {
        dword(result, quest.id); append(result, quest.name);
        word(result, static_cast<std::uint16_t>(quest.instructions.size()));
        for (const auto& op : quest.instructions) {
            byte(result, op.selector); byte(result, op.dataType); word(result, op.id);
            if (op.selector < 4) {
                const auto& m = op.message;
                dword(result, m.id); byte(result, m.minimumLevel);
                byte(result, m.maximumLevel); byte(result, m.map);
                dword(result, m.action); dword(result, m.duration); dword(result, m.display);
                byte(result, static_cast<std::uint8_t>(m.texts.size()));
                for (const auto& text : m.texts) {
                    append(result, text.font);
                    word(result, static_cast<std::uint16_t>(text.bytes.size()));
                    append(result, text.bytes);
                }
            } else {
                byte(result, op.fixed.at(1));
                result.insert(result.end(), op.fixed.begin() + 4, op.fixed.end());
            }
        }
    }
    return result;
}

int main() {
    try {
        std::ifstream list("inputs.txt"); check(bool(list), "input list");
        unsigned files = 0, quests = 0, instructions = 0, texts = 0;
        std::uint64_t textBytes = 0;
        unsigned selectors[47] = {};
        std::string path;
        while (std::getline(list, path)) {
            if (!path.empty() && path.back() == '\r') path.pop_back();
            if (path.empty()) continue;
            const auto raw = read(path);
            RF455TutorialScript script;
            check(RF455_LoadTutorialScript(path.c_str(), script), "load real SCP");
            Bytes encoded;
            check(RF455_EncodeTutorialScript(script, encoded), "encode real SCP");
            check(raw == encoded, "real SCP byte equality");
            write("roundtrip/" + path, encoded);
            write("semantic/" + path, semantic(script));
            ++files; quests += static_cast<unsigned>(script.quests.size());
            for (const auto& quest : script.quests) for (const auto& op : quest.instructions) {
                ++instructions; ++selectors[op.selector];
                for (const auto& text : op.message.texts) {
                    ++texts; textBytes += text.bytes.size();
                }
            }
        }
        const auto fixture = read("all47.scp");
        RF455TutorialScript script;
        check(RF455_ParseTutorialScript(fixture.data(), fixture.size(), script), "47-selector fixture");
        check(script.quests.size() == 1 && script.quests[0].instructions.size() == 47, "all selectors count");
        for (unsigned i = 0; i != 47; ++i) {
            const auto& op = script.quests[0].instructions[i];
            check(op.selector == i && op.dataType == (i ^ 0x80) && op.id == 1000 + i,
                  "selector vs stored type and identifier");
        }
        Bytes encoded;
        check(RF455_EncodeTutorialScript(script, encoded) && encoded == fixture, "47-selector roundtrip");
        write("all47.semantic", semantic(script));
        const auto before = semantic(script);
        unsigned prefixes = 0;
        for (std::size_t size = 0; size < fixture.size(); ++size) {
            check(!RF455_ParseTutorialScript(fixture.data(), size, script), "truncated script accepted");
            check(semantic(script) == before, "truncation mutated output"); ++prefixes;
        }
        auto malformed = fixture;
        malformed[74] = 47;
        check(!RF455_ParseTutorialScript(malformed.data(), malformed.size(), script), "unknown selector");
        malformed = fixture;
        for (unsigned i = 0; i != 4; ++i) malformed[i] = 255;
        check(!RF455_ParseTutorialScript(malformed.data(), malformed.size(), script), "unbounded count");
        check(!RF455_LoadTutorialScript("does-not-exist.scp", script), "missing input");
        check(!RF455_ParseTutorialScript(nullptr, 100, script) && semantic(script) == before,
              "failed parse/load changed owner");
        const auto unselected = read("unselected-Tutorial.scp");
        check(!RF455_ParseTutorialScript(unselected.data(), unselected.size(), script) &&
              semantic(script) == before, "unselected generic script must not masquerade as 455 SCP");
        const Bytes zero = {0, 0, 0, 0, 0xa5, 0, 0xff};
        RF455TutorialScript empty;
        check(RF455_ParseTutorialScript(zero.data(), zero.size(), empty) && empty.quests.empty() &&
              empty.trailer.size() == 3 && RF455_EncodeTutorialScript(empty, encoded) && encoded == zero,
              "empty document and trailer");
        auto invalid = script;
        invalid.quests[0].instructions[4].fixed.pop_back();
        const Bytes old = encoded;
        check(!RF455_EncodeTutorialScript(invalid, encoded) && encoded == old, "invalid encode mutation");
        invalid = script;
        invalid.quests[0].instructions[0].message.texts.resize(256);
        check(!RF455_EncodeTutorialScript(invalid, encoded) && encoded == old, "string-count overflow");
        invalid = script;
        invalid.quests[0].instructions[0].message.texts[0].bytes.resize(65536);
        check(!RF455_EncodeTutorialScript(invalid, encoded) && encoded == old, "string-length overflow");
        invalid = script;
        invalid.quests[0].instructions[4].id = 0xabcd;
        invalid.quests[0].instructions[4].dataType = 0xee;
        check(RF455_EncodeTutorialScript(invalid, encoded), "semantic edit encode");
        check(RF455_ParseTutorialScript(encoded.data(), encoded.size(), empty) &&
              empty.quests[0].instructions[4].id == 0xabcd &&
              empty.quests[0].instructions[4].dataType == 0xee, "semantic edit fields");
        const auto limit = read("max-text.scp");
        check(RF455_ParseTutorialScript(limit.data(), limit.size(), empty) &&
              empty.quests[0].instructions[0].message.texts[0].bytes.size() == 65535 &&
              RF455_EncodeTutorialScript(empty, encoded) && encoded == limit, "WORD text length bound");
        FILE* result = std::fopen("result.json", "w"); check(result != nullptr, "result");
        std::fprintf(result, "{\"status\":\"PASS\",\"files\":%u,\"quests\":%u,\"instructions\":%u,"
                     "\"texts\":%u,\"text_bytes\":%llu,\"selectors\":[", files, quests, instructions,
                     texts, static_cast<unsigned long long>(textBytes));
        for (unsigned i = 0; i != 47; ++i) std::fprintf(result, "%s%u", i ? "," : "", selectors[i]);
        std::fprintf(result, "],\"synthetic_all47\":true,\"prefixes_rejected_atomically\":%u,"
                     "\"invalid_encode_atomic\":true,\"semantic_edits\":true,\"max_text_length\":true,"
                     "\"unselected_generic_rejected\":true,"
                     "\"command_execution\":false,\"full_Tutorial\":false}\n", prefixes);
        check(std::fclose(result) == 0, "close result");
        return 0;
    } catch (const std::exception& error) {
        std::fprintf(stderr, "%s\n", error.what()); return 1;
    }
}
