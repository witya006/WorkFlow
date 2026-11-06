#pragma once
#include <array>
#include <cstddef>
#include <cstdint>
#include <vector>

// Source-owned wire model. These are not overlays of the original QBI objects.
// Execution of QBI commands belongs to the Tutorial runtime, still being ported.
enum class RF455TutorialKind {
    RichMessage, MessageFixed, Wait, Move, Creation, Position, Ui, Equip,
    Cursor, Combat, Item, Invalid
};

struct RF455TutorialText {
    std::array<std::uint8_t, 12> font{};
    std::vector<std::uint8_t> bytes;
};

struct RF455TutorialMessage {
    std::uint32_t id = 0;
    std::uint8_t minimumLevel = 0, maximumLevel = 0, map = 0;
    std::uint32_t action = 0, duration = 0, display = 0;
    std::vector<RF455TutorialText> texts;
};

struct RF455TutorialInstruction {
    std::uint8_t selector = 0, dataType = 0;
    std::uint16_t id = 0;
    RF455TutorialMessage message;
    // Fixed records include padding and fields whose semantics are not yet all
    // restored. Encoding publishes dataType/id over these two confirmed fields.
    std::vector<std::uint8_t> fixed;
};

struct RF455TutorialQuest {
    std::uint32_t id = 0;
    std::array<std::uint8_t, 64> name{};
    std::vector<RF455TutorialInstruction> instructions;
};

struct RF455TutorialScript {
    std::vector<RF455TutorialQuest> quests;
    std::vector<std::uint8_t> trailer;
};

RF455TutorialKind RF455_TutorialKind(std::uint8_t selector);
std::size_t RF455_TutorialFixedSize(std::uint8_t selector);
bool RF455_ParseTutorialScript(const void*, std::size_t, RF455TutorialScript&);
bool RF455_LoadTutorialScript(const char*, RF455TutorialScript&);
bool RF455_EncodeTutorialScript(const RF455TutorialScript&, std::vector<std::uint8_t>&);
