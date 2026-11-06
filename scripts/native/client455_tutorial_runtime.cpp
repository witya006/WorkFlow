#include "client455_tutorial_runtime.h"
#include <new>
#include <stdexcept>
#include <utility>

namespace {
std::uint16_t word(const std::vector<std::uint8_t>& data, std::size_t at) {
    return std::uint16_t(data[at]) | (std::uint16_t(data[at + 1]) << 8);
}
std::uint32_t dword(const std::vector<std::uint8_t>& data, std::size_t at) {
    return std::uint32_t(data[at]) | (std::uint32_t(data[at + 1]) << 8) |
           (std::uint32_t(data[at + 2]) << 16) | (std::uint32_t(data[at + 3]) << 24);
}

class Message final : public RF455TutorialProcessor {
public:
    explicit Message(const RF455TutorialInstruction& instruction)
        : RF455TutorialProcessor(instruction.dataType, instruction.id,
                                 instruction.selector < 4 ? 0 : instruction.fixed[4]),
          content(instruction.message), reference(instruction.selector < 4 ? 0xffff : word(instruction.fixed, 12)) {}
private:
    RF455TutorialMessage content;
    std::uint16_t reference;
    bool start(RF455TutorialHost& host, RF455TutorialContext&) override {
        if (type <= 4) host.message(type, type < 4 ? &content : nullptr, reference);
        return true;
    }
    bool update(RF455TutorialHost&, RF455TutorialContext&) override {return true;}
    void finish(RF455TutorialHost&, RF455TutorialContext&) override {}
};

class Wait final : public RF455TutorialProcessor {
public:
    explicit Wait(const RF455TutorialInstruction& instruction)
        : RF455TutorialProcessor(instruction.dataType, instruction.id, instruction.fixed[4]),
          mode(instruction.fixed[6]), value(dword(instruction.fixed, 8)) {}
private:
    std::uint8_t mode;
    std::uint32_t value;
    bool start(RF455TutorialHost&, RF455TutorialContext&) override {return true;}
    bool update(RF455TutorialHost& host, RF455TutorialContext& context) override {
        if (mode == 0) {
            if (std::uint32_t(context.input) != value) return false;
            context.input = 11;
            return true;
        }
        if (mode == 1) return std::uint32_t(host.milliseconds() - context.startTime) >= value;
        if (mode != 2 || value < 4 || value > 10) return false;
        const auto state = host.waitState(value);
        switch (value) {
        case 4: return state.board17Field1892 != 0 && state.board17Field1896 != 0;
        case 5: return state.avatarByte614 == 0;
        case 6: return state.avatarByte614 == 1;
        case 7: return state.avatarByte612 == 1;
        case 8: return state.avatarByte612 == 0;
        case 9: return state.avatarField24308 != 0;
        case 10: return state.avatarField24308 == 0;
        default: return false;
        }
    }
    void finish(RF455TutorialHost&, RF455TutorialContext&) override {}
};
}

bool RF455TutorialProcessor::begin(RF455TutorialHost& host, RF455TutorialContext& context) {
    if (type != 16) host.resetCursorButton();
    if (!start(host, context)) return false;
    context.startTime = host.milliseconds();
    context.input = 11;
    context.state52 = 0;
    flags |= 1;
    return true;
}

void RF455TutorialProcessor::tick(RF455TutorialHost& host, RF455TutorialContext& context) {
    if ((flags & 4) || update(host, context)) {
        flags |= 2;
        finish(host, context);
    }
}

RF455TutorialProcessor* RF455TutorialQuestState::get(std::uint16_t ordinal) {
    if (ordinal == 0xffff && current) return current;
    if (ordinal >= declaredCount || ordinal >= processors.size()) return nullptr;
    return processors[ordinal].get();
}

std::unique_ptr<RF455TutorialProcessor> RF455TutorialBasicFactory::create(const RF455TutorialInstruction& instruction) {
    if (instruction.selector < 4 && instruction.fixed.empty())
        return std::unique_ptr<RF455TutorialProcessor>(new Message(instruction));
    if (instruction.selector == 4 && instruction.fixed.size() == 16 && instruction.dataType >= 4)
        return std::unique_ptr<RF455TutorialProcessor>(new Message(instruction));
    // Fixed message records with type0..3 carry a target pointer, not owned HSD
    // data. That unsafe execution domain is not fabricated as a valid message.
    if (instruction.selector == 5 && instruction.fixed.size() == 12)
        return std::unique_ptr<RF455TutorialProcessor>(new Wait(instruction));
    return nullptr;
}

void RF455TutorialRuntime::clear() {
    quests.clear();
    currentQuest = 0;
    context = RF455TutorialContext{};
}

bool RF455TutorialRuntime::prepare(const RF455TutorialScript& script, RF455TutorialFactory& factory,
                                   RF455TutorialUnsupported* unsupported) {
    try {
        if (script.quests.size() > 0xffffffffU) return false;
        std::vector<RF455TutorialQuestState> next;
        next.reserve(script.quests.size());
        for (std::size_t i = 0; i < script.quests.size(); ++i) {
            const auto& from = script.quests[i];
            if (from.instructions.size() > 65535) return false;
            RF455TutorialQuestState quest;
            quest.id = from.id;
            quest.declaredCount = static_cast<std::uint16_t>(from.instructions.size());
            quest.processors.reserve(from.instructions.size());
            for (std::size_t j = 0; j < from.instructions.size(); ++j) {
                auto processor = factory.create(from.instructions[j]);
                if (!processor) {
                    if (unsupported) *unsupported = {i, j, from.instructions[j].selector};
                    return false;
                }
                quest.processors.push_back(std::move(processor));
            }
            next.push_back(std::move(quest));
        }
        clear();
        quests = std::move(next);
        return true;
    } catch (const std::bad_alloc&) {return false;}
      catch (const std::length_error&) {return false;}
}

RF455TutorialQuestState* RF455TutorialRuntime::get(std::uint32_t ordinal) {
    if (ordinal == 0xffffffff) ordinal = currentQuest;
    return ordinal < quests.size() ? &quests[ordinal] : nullptr;
}

bool RF455TutorialRuntime::refresh(RF455TutorialHost& host, std::uint32_t ordinal) {
    auto* quest = get(ordinal);
    if (!quest) return false;
    // Target429F70 resets ID and the serialized count, but keeps the list and
    // processor-private state. Iteration uses the list size, not that count.
    quest->id = 0xffffffff;
    quest->declaredCount = 0;
    quest->next = 0;
    quest->current = nullptr;
    for (auto& processor : quest->processors) processor->flags = 0;
    quest->flags = 1;
    host.questRefreshed();
    return true;
}

RF455TutorialStep RF455TutorialRuntime::step(RF455TutorialHost& host) {
    if (quests.empty()) return RF455TutorialStep::Idle;
    context.activeQuest = nullptr;
    auto* quest = get();
    if (!quest || quest->processors.empty()) return RF455TutorialStep::Idle;
    if (host.skipTutorial() || host.boardBusy()) return RF455TutorialStep::Suppressed;
    if (!(quest->flags & 1) || (quest->flags & 2)) return RF455TutorialStep::Idle;
    context.activeQuest = quest;
    if (quest->next < quest->processors.size()) {
        auto* current = quest->current;
        if (!current || !(current->flags & 1) || (current->flags & 2)) {
            auto* candidate = quest->processors[quest->next].get();
            if (candidate->begin(host, context)) {
                quest->current = candidate;
                ++quest->next;
            }
        }
    }
    for (std::size_t i = 0; i < quest->next; ++i) {
        auto* processor = quest->processors[i].get();
        if ((processor->flags & 1) && !(processor->flags & 2)) processor->tick(host, context);
    }
    if (quest->next == quest->processors.size() && !(quest->flags & 2) &&
        (quest->processors.back()->flags & 2)) {
        quest->flags |= 2;
        if (quest == &quests.back()) {
            currentQuest = static_cast<std::uint32_t>(quests.size());
            host.scriptCompleted(); // May clear/unload this runtime. Do not touch members afterwards.
            return RF455TutorialStep::Completed;
        }
        ++currentQuest;
        refresh(host, currentQuest);
        return RF455TutorialStep::QuestAdvanced;
    }
    return RF455TutorialStep::Running;
}
