#pragma once
#include "client455_tutorial_script.h"
#include <array>
#include <memory>
#include <vector>

class RF455TutorialProcessor;
struct RF455TutorialQuestState;

struct RF455TutorialContext {
    std::uint32_t startTime = 0;
    std::uint8_t input = 11, attackType = 255;
    std::uint32_t skillIndex = 0xffffffff, target[2] = {0xffffffff, 0xffffffff};
    // Meaning of owner+52 is not yet certified. Starting a QBI clears it.
    std::uint32_t state52 = 0;
    RF455TutorialQuestState* activeQuest = nullptr;
};

// Values queried by the 455 WAIT_CONDITION branch. Their gameplay names and
// production providers must be recovered before attaching the real host.
struct RF455TutorialWaitState {
    std::int32_t board17Field1892 = 0, board17Field1896 = 0;
    std::uint8_t avatarByte612 = 0, avatarByte614 = 0;
    std::int32_t avatarField24308 = 0;
};

class RF455TutorialHost {
public:
    virtual ~RF455TutorialHost() = default;
    virtual bool skipTutorial() = 0;           // Avatar DWORD20168 != 0
    virtual bool boardBusy() = 0;              // CTutorialBoard BYTE2286 != 0
    virtual std::uint32_t milliseconds() = 0;
    virtual void resetCursorButton() = 0;      // Global DWORD1156B70 = 0
    virtual void questRefreshed() = 0;         // CTutorialBoard BYTE2284 = 1
    virtual void scriptCompleted() = 0;        // Target board4A6080(0); may unload
    virtual void message(std::uint8_t type, const RF455TutorialMessage*, std::uint16_t reference) = 0;
    virtual RF455TutorialWaitState waitState(std::uint32_t condition) = 0;
};

class RF455TutorialProcessor {
public:
    explicit RF455TutorialProcessor(std::uint8_t type, std::uint16_t id, std::uint8_t flags = 0)
        : type(type), id(id), flags(flags) {}
    virtual ~RF455TutorialProcessor() = default;
    std::uint8_t type;
    std::uint16_t id;
    std::uint8_t flags;
    bool begin(RF455TutorialHost&, RF455TutorialContext&);
    void tick(RF455TutorialHost&, RF455TutorialContext&);
protected:
    virtual bool start(RF455TutorialHost&, RF455TutorialContext&) = 0;
    virtual bool update(RF455TutorialHost&, RF455TutorialContext&) = 0;
    virtual void finish(RF455TutorialHost&, RF455TutorialContext&) = 0;
};

struct RF455TutorialQuestState {
    std::uint32_t id = 0xffffffff;
    std::uint16_t declaredCount = 0;
    std::uint8_t flags = 0;
    std::vector<std::unique_ptr<RF455TutorialProcessor>> processors;
    std::size_t next = 0;
    RF455TutorialProcessor* current = nullptr;
    RF455TutorialProcessor* get(std::uint16_t ordinal = 0xffff);
};

class RF455TutorialFactory {
public:
    virtual ~RF455TutorialFactory() = default;
    // A missing processor is an explicit reconstruction gap, never a no-op.
    virtual std::unique_ptr<RF455TutorialProcessor> create(const RF455TutorialInstruction&) = 0;
};

class RF455TutorialBasicFactory final : public RF455TutorialFactory {
public:
    std::unique_ptr<RF455TutorialProcessor> create(const RF455TutorialInstruction&) override;
};

enum class RF455TutorialStep { Idle, Suppressed, Running, QuestAdvanced, Completed };
struct RF455TutorialUnsupported {std::size_t quest = 0, instruction = 0; std::uint8_t selector = 0;};

class RF455TutorialRuntime {
public:
    RF455TutorialContext context;
    std::uint32_t currentQuest = 0;
    std::vector<RF455TutorialQuestState> quests;
    // This is an owned unload+load transaction, not the unsafe raw target loader.
    bool prepare(const RF455TutorialScript&, RF455TutorialFactory&, RF455TutorialUnsupported* = nullptr);
    void clear();
    bool finished() const {return currentQuest >= quests.size();}
    RF455TutorialQuestState* get(std::uint32_t ordinal = 0xffffffff);
    bool refresh(RF455TutorialHost&, std::uint32_t ordinal = 0xffffffff);
    RF455TutorialStep step(RF455TutorialHost&);
};
