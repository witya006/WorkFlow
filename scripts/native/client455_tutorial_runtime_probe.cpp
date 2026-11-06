#include "client455_tutorial_runtime.h"
#include <cstdio>
#include <stdexcept>
#include <string>
#include <vector>

static void check(bool ok, const char* why) {if (!ok) throw std::runtime_error(why);}
struct Host final : RF455TutorialHost {
    bool skip = false, busy = false;
    unsigned cursor = 0, clocks = 0, ready = 0, completed = 0, queries = 0;
    std::uint32_t now = 100;
    RF455TutorialWaitState condition;
    RF455TutorialRuntime* unload = nullptr;
    std::vector<unsigned> messages;
    std::uint32_t hint = 0;
    std::uint16_t reference = 0;
    bool sawFinishedBeforeUnload = false;
    bool skipTutorial() override {return skip;}
    bool boardBusy() override {return busy;}
    std::uint32_t milliseconds() override {++clocks; return now;}
    void resetCursorButton() override {++cursor;}
    void questRefreshed() override {++ready;}
    void scriptCompleted() override {
        ++completed;
        if (unload) {sawFinishedBeforeUnload = unload->finished(); unload->clear();}
    }
    void message(std::uint8_t type, const RF455TutorialMessage* text, std::uint16_t ref) override {
        messages.push_back(type); hint = text ? text->id : 0; reference = ref;
    }
    RF455TutorialWaitState waitState(std::uint32_t) override {++queries; return condition;}
};

static RF455TutorialInstruction message(unsigned type) {
    RF455TutorialInstruction op;
    op.selector = op.dataType = static_cast<std::uint8_t>(type); op.id = 7;
    op.message.id = 0x12345678;
    if (type == 4) {op.fixed.resize(16); op.fixed[12] = 0x34; op.fixed[13] = 0x12;}
    return op;
}
static RF455TutorialInstruction wait(unsigned mode, std::uint32_t value) {
    RF455TutorialInstruction op;
    op.selector = op.dataType = 5; op.id = 8; op.fixed.resize(12); op.fixed[6] = std::uint8_t(mode);
    for (unsigned i = 0; i != 4; ++i) op.fixed[8 + i] = std::uint8_t(value >> (8 * i));
    return op;
}
static RF455TutorialScript script(std::vector<RF455TutorialInstruction> ops) {
    RF455TutorialScript s; RF455TutorialQuest q; q.id = 42; q.instructions = std::move(ops);
    s.quests.push_back(std::move(q)); return s;
}

struct Trace final : RF455TutorialProcessor {
    bool allowStart = true, allowUpdate = true, endSawDone = false;
    unsigned starts = 0, updates = 0, ends = 0;
    explicit Trace(unsigned type = 6) : RF455TutorialProcessor(std::uint8_t(type), 99) {}
    bool start(RF455TutorialHost&, RF455TutorialContext&) override {++starts; return allowStart;}
    bool update(RF455TutorialHost&, RF455TutorialContext&) override {++updates; return allowUpdate;}
    void finish(RF455TutorialHost&, RF455TutorialContext&) override {++ends; endSawDone = (flags & 2) != 0;}
};

static void scheduler() {
    Host host; RF455TutorialBasicFactory factory; RF455TutorialRuntime runtime;
    check(runtime.prepare(script({message(0), wait(1, 100), message(4)}), factory), "prepare basic program");
    check(runtime.get()->get(0) != nullptr && runtime.get()->id == 42, "loaded ordinal lookup");
    check(runtime.step(host) == RF455TutorialStep::Idle && host.clocks == 0, "unrefreshed program");
    check(runtime.refresh(host) && runtime.get()->id == 0xffffffff && runtime.get()->declaredCount == 0 &&
          runtime.get()->get(0) == nullptr && host.ready == 1, "refresh retained list/reset ID+count");
    runtime.context.input = 3; runtime.context.state52 = 123; runtime.context.startTime = 77;
    host.busy = true;
    check(runtime.step(host) == RF455TutorialStep::Suppressed && runtime.context.input == 3 &&
          !runtime.context.activeQuest && host.clocks == 0, "board busy gate");
    host.busy = false; host.skip = true;
    check(runtime.step(host) == RF455TutorialStep::Suppressed && host.clocks == 0, "Avatar skip gate");
    host.skip = false;
    check(runtime.step(host) == RF455TutorialStep::Running && runtime.get()->next == 1 &&
          runtime.get()->current->flags == 3 && runtime.get()->get() == runtime.get()->current,
          "one new instruction per tick");
    check(runtime.context.startTime == 100 && runtime.context.input == 11 && !runtime.context.state52 &&
          host.messages == std::vector<unsigned>{0} && host.hint == 0x12345678, "message and common reset");
    host.now = 200;
    check(runtime.step(host) == RF455TutorialStep::Running && runtime.get()->next == 2 &&
          runtime.get()->current->flags == 1 && runtime.context.startTime == 200 && host.clocks == 3,
          "wait starts after message; separate start/update clock reads");
    host.now = 299; runtime.step(host);
    check(runtime.get()->next == 2 && runtime.get()->current->flags == 1, "wait strict lower boundary");
    host.now = 300; runtime.step(host);
    check(runtime.get()->next == 2 && runtime.get()->current->flags == 3, "wait inclusive boundary");
    host.unload = &runtime;
    check(runtime.step(host) == RF455TutorialStep::Completed && host.completed == 1 &&
          host.sawFinishedBeforeUnload && runtime.quests.empty() && host.reference == 0x1234,
          "completion may unload during callback");
    check(host.messages == std::vector<unsigned>({0, 4}), "actual message dispatcher types");

    auto program = script({message(1)});
    program.quests.push_back(script({wait(0, 2)}).quests[0]);
    host = Host{};
    check(runtime.prepare(program, factory) && runtime.refresh(host), "two quest prepare");
    check(runtime.step(host) == RF455TutorialStep::QuestAdvanced && runtime.currentQuest == 1 &&
          runtime.quests[0].flags == 3 && runtime.quests[1].flags == 1 && host.ready == 2 &&
          runtime.context.activeQuest == &runtime.quests[0], "advance+refresh and active context lifetime");
    runtime.context.input = 2;
    check(runtime.step(host) == RF455TutorialStep::Running && runtime.context.input == 11,
          "new wait consumes pre-start input reset");
    runtime.context.input = 2;
    check(runtime.step(host) == RF455TutorialStep::Completed && runtime.finished() &&
          runtime.context.input == 11, "input wait and last quest");
    runtime.currentQuest = 1;
    check(runtime.refresh(host, 0) && runtime.currentQuest == 1, "refresh explicit quest keeps current ordinal");
    check(!runtime.refresh(host, 2) && !runtime.get(2), "quest ordinal bound");
    check(runtime.prepare(script({}), factory) && runtime.refresh(host) &&
          runtime.step(host) == RF455TutorialStep::Idle && !runtime.finished(), "empty quest does not auto-complete");
}

static void processorCore() {
    Host host; RF455TutorialContext context;
    context.startTime = 17; context.input = 2; context.state52 = 88;
    Trace failed; failed.allowStart = false;
    check(!failed.begin(host, context) && host.cursor == 1 && !host.clocks &&
          context.startTime == 17 && context.input == 2 && context.state52 == 88 && failed.flags == 0,
          "failed start only resets cursor");
    Trace preserve(16);
    check(preserve.begin(host, context) && host.cursor == 1 && host.clocks == 1 &&
          context.startTime == 100 && context.input == 11 && context.state52 == 0, "type16 cursor exemption");
    preserve.flags |= 4; preserve.allowUpdate = false; preserve.tick(host, context);
    check(!preserve.updates && preserve.ends == 1 && preserve.endSawDone && preserve.flags == 7,
          "flag4 bypasses update; done before finish");
    Trace pending; pending.allowUpdate = false; pending.begin(host, context); pending.tick(host, context);
    check(pending.flags == 1 && pending.updates == 1 && !pending.ends, "pending update");
    pending.allowUpdate = true; pending.tick(host, context);
    check(pending.flags == 3 && pending.endSawDone, "successful update finish");

    RF455TutorialRuntime runtime;
    runtime.quests.emplace_back(); auto& q = runtime.quests[0]; q.flags = 1;
    auto first = new Trace; first->flags = 1; first->allowUpdate = false;
    auto last = new Trace; last->flags = 1;
    q.processors.emplace_back(first); q.processors.emplace_back(last); q.next = 2; q.current = last;
    check(runtime.step(host) == RF455TutorialStep::Completed && first->updates == 1 && first->flags == 1 &&
          last->updates == 1 && last->flags == 3, "started prefix processed, final record decides completion");
    runtime.currentQuest = 0;
    check(runtime.refresh(host) && first->updates == 1 && first->flags == 0 && q.next == 0 && !q.current,
          "refresh resets flags/iterator, not processor-private fields");
    first->allowStart = false;
    check(runtime.step(host) == RF455TutorialStep::Running && q.next == 0 && !q.current, "failed begin retry state");
    first->allowStart = true;
    runtime.step(host);
    check(q.next == 1 && q.current == first && first->starts == 2, "retry starts same processor");
}

static void waits() {
    RF455TutorialBasicFactory factory;
    Host host; RF455TutorialContext context;
    for (unsigned type = 0; type <= 4; ++type) {
        auto op = factory.create(message(type)); check(bool(op), "message factory");
        check(op->begin(host, context), "message start"); op->tick(host, context);
        check(op->flags == 3 && host.messages.back() == type, "message immediate completion");
    }
    auto unsafe = message(4); unsafe.dataType = 0;
    check(!factory.create(unsafe), "serialized foreign message pointer cannot be a source-owned hint");
    auto unknown = message(0); unknown.dataType = 255;
    auto op = factory.create(unknown); const auto before = host.messages.size();
    op->begin(host, context); op->tick(host, context);
    check(host.messages.size() == before && op->flags == 3, "target unknown message type default");
    op = factory.create(wait(0, 11)); op->begin(host, context); op->tick(host, context);
    check(op->flags == 3 && context.input == 11, "input11 equality");
    op = factory.create(wait(0, 258)); op->begin(host, context); context.input = 2; op->tick(host, context);
    check(op->flags == 1 && context.input == 2, "DWORD input value is not truncated");
    op = factory.create(wait(1, 31)); host.now = 0xfffffff0; op->begin(host, context);
    host.now = 14; op->tick(host, context); check(op->flags == 1, "clock wrap before bound");
    host.now = 15; op->tick(host, context); check(op->flags == 3, "clock wrap equality");
    op = factory.create(wait(1, 100)); host.now = 100; op->begin(host, context);
    auto later = factory.create(message(0)); host.now = 200; later->begin(host, context);
    host.now = 299; op->tick(host, context); check(op->flags == 1, "later start resets shared timer");
    host.now = 300; op->tick(host, context); check(op->flags == 3, "shared timer equality");
    for (unsigned value = 4; value <= 10; ++value) {
        op = factory.create(wait(2, value)); op->begin(host, context); host.condition = {};
        switch (value) {
        case 4: host.condition.board17Field1892 = -1; host.condition.board17Field1896 = 2; break;
        case 5: host.condition.avatarByte614 = 0; break;
        case 6: host.condition.avatarByte614 = 1; break;
        case 7: host.condition.avatarByte612 = 1; break;
        case 8: host.condition.avatarByte612 = 0; break;
        case 9: host.condition.avatarField24308 = -5; break;
        case 10: host.condition.avatarField24308 = 0; break;
        }
        const auto queries = host.queries; op->tick(host, context);
        check(op->flags == 3 && host.queries == queries + 1, "condition satisfied");
        op = factory.create(wait(2, value)); op->begin(host, context);
        switch (value) {
        case 4: host.condition.board17Field1896 = 0; break;
        case 5: case 6: host.condition.avatarByte614 = 2; break;
        case 7: case 8: host.condition.avatarByte612 = 2; break;
        case 9: host.condition.avatarField24308 = 0; break;
        case 10: host.condition.avatarField24308 = 1; break;
        }
        op->tick(host, context); check(op->flags == 1, "condition unsatisfied");
    }
    const auto queries = host.queries;
    for (unsigned mode : {2u, 3u, 255u}) {
        op = factory.create(wait(mode, 3)); op->begin(host, context); op->tick(host, context);
        check(op->flags == 1 && host.queries == queries, "unsupported wait condition remains pending");
    }
}

int main() {
    try {
        scheduler(); processorCore(); waits();
        RF455TutorialBasicFactory factory;
        unsigned records = 0, supported = 0, unsupported = 0;
        for (const char* path : {"bw.scp", "cw.scp", "ar.scp"}) {
            RF455TutorialScript data;
            check(RF455_LoadTutorialScript(path, data), "real script parse");
            for (const auto& q : data.quests) for (const auto& instruction : q.instructions) {
                ++records;
                if (factory.create(instruction)) ++supported; else ++unsupported;
            }
            RF455TutorialRuntime runtime;
            auto baseline = script({message(0)});
            check(runtime.prepare(baseline, factory), "baseline prepare");
            RF455TutorialUnsupported gap;
            check(!runtime.prepare(data, factory, &gap) && gap.selector >= 6 &&
                  runtime.quests.size() == 1 && runtime.quests[0].id == 42,
                  "real unsupported commands fail explicitly and retain previous program");
        }
        FILE* out = std::fopen("result.json", "w"); check(out != nullptr, "result file");
        std::fprintf(out, "{\"status\":\"PASS\",\"scheduler_order\":true,\"flags_and_refresh\":true,"
                     "\"shared_timer_and_wrap\":true,\"message0to4\":true,\"wait5\":true,"
                     "\"callback_unload\":true,\"real_records\":%u,\"basic_supported\":%u,"
                     "\"explicitly_unsupported\":%u,\"full47_execution\":false,"
                     "\"production_host\":false,\"full_Tutorial\":false}\n", records, supported, unsupported);
        check(std::fclose(out) == 0, "close result");
        return 0;
    } catch (const std::exception& error) {std::fprintf(stderr, "%s\n", error.what()); return 1;}
}
