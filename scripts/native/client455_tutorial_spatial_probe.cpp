#include "client455_tutorial_spatial.h"
#include <cmath>
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <string>
#include <vector>

static void check(bool ok, const char* why) {if (!ok) throw std::runtime_error(why);}
#include "testing/client455_tutorial_recording_host.h"
using Host = RF455TutorialRecordingSpatialHost<>;

static void put(std::vector<std::uint8_t>& bytes, std::size_t at, std::uint32_t value) {
    for (unsigned i = 0; i != 4; ++i) bytes[at+i] = std::uint8_t(value >> (8*i));
}
static RF455TutorialInstruction op(unsigned type, RF455TutorialVector point = {{0,0,0}}, unsigned mode = 0, std::uint32_t amount = 0) {
    RF455TutorialInstruction instruction; instruction.selector = instruction.dataType = std::uint8_t(type);
    const unsigned size = type >= 9 && type <= 11 ? 24 : 20;
    instruction.fixed.resize(size); instruction.fixed[6] = std::uint8_t(mode);
    std::memcpy(instruction.fixed.data() + (size == 24 ? 12 : 8), point.data(), 12);
    if (size == 24) put(instruction.fixed, 8, 77);
    else if (mode == 1) put(instruction.fixed, 8, amount);
    return instruction;
}

static void positions() {
    Host host; RF455TutorialCreationIds ids; RF455TutorialSpatialFactory factory(host, ids);
    RF455TutorialContext context;
    for (unsigned type : {12u,13u,14u,18u}) {
        auto p = factory.create(op(type, {{10,20,30}})); check(bool(p) && p->begin(host, context), "position start");
        p->tick(host, context); check(p->flags == 7, "position forcefinish");
    }
    check(host.position == RF455TutorialVector{{10,20,30}} && host.yaw == 20 &&
          host.orbit == RF455TutorialVector{{10,20,30}} && host.parameter == 10, "position actions");
    for (float value : {0.0f,-10.0f}) {
        auto p = factory.create(op(18, {{value,0,0}})); p->begin(host, context); check(host.parameter == 75, "parameter default");
    }
    auto p = factory.create(op(15, {{-30,40,-50}})); check(p->begin(host, context), "relative camera start");
    check(context.cameraRemaining == RF455TutorialVector{{30,40,50}} && host.relative == RF455TutorialVector{{-30,40,-50}}, "camera absolute remaining");
    host.now = 19999; p->tick(host, context); check(p->flags == 1, "camera timeout before");
    host.now = 20000; p->tick(host, context); check(p->flags == 3, "camera inclusive timeout");
    host.now = 100; const auto cursor = host.cursor;
    p = factory.create(op(16, {{2,2,2}})); p->begin(host, context);
    check(host.cursor == cursor, "camera request preserves cursor");
    context.cameraRemaining = {{1,1,1}}; const auto clocks = host.clocks; p->tick(host, context);
    check(p->flags == 3 && host.clocks == clocks, "camera remaining short circuit");
    p = factory.create(op(17)); p->begin(host, context); host.now += 30000; p->tick(host, context);
    check(p->flags == 1, "selector17 target default remains pending");
}

static void movement() {
    Host host; RF455TutorialCreationIds ids; RF455TutorialSpatialFactory factory(host, ids); RF455TutorialContext context;
    check(RF455_TutorialDistanceXZ({{0,10000,0}}, {{3,-10000,4}}) == 5 &&
          RF455_TutorialDistanceXZ({{0,0,0}}, {{9,0,12}}) == 15 &&
          RF455_TutorialDistanceXZ({{0,0,0}}, {{std::nextafter(15.0f,16.0f),0,0}}) > 15,
          "XZ sum and adjacent boundary");
    auto p = factory.create(op(6, {{100,0,0}})); p->begin(host, context);
    check(host.markers == 1 && host.turns == 1 && context.operationActive == 1, "move request");
    host.position = {{84,9000,0}}; p->tick(host, context); check(p->flags == 1, "XZ distance16");
    host.position[0] = 85; p->tick(host, context);
    check(p->flags == 3 && host.releases == 1 && !context.operationActive, "XZ inclusive15 ignores height");
    const auto turns = host.turns;
    p = factory.create(op(7, {{200,0,0}})); p->begin(host, context);
    check(host.turns == turns && host.markers == 2, "move request-only does not turn avatar");
    host.now = 0; host.position = {{1,2,3}}; host.yaw = 90; host.calls.clear();
    p = factory.create(op(6, {}, 1, 10)); p->begin(host, context);
    check(context.remainingDistance == 10 && std::fabs(host.target[0]-13) < 0.0001f &&
          host.target[1] == 2 && std::fabs(host.target[2]-3) < 0.0001f, "distance-directed target");
    check(host.calls == std::vector<std::string>({"x","yaw","y","z","yaw","path","face","state"}), "directed getter/action order");
    host.now = 19999; p->tick(host, context); check(p->flags == 1, "move timeout before");
    host.now = 20000; p->tick(host, context); check(p->flags == 3 && !context.operationActive, "move timeout equality");
    host.yaw = 90; p = factory.create(op(6, {}, 1, 0xffffffff)); p->begin(host, context);
    check(std::fabs(host.target[0]-2) < 0.0001f, "DWORD distance+2 wraps");
    p = factory.create(op(7, {}, 1, 10)); p->begin(host, context); context.remainingDistance = 1;
    const auto clocks = host.clocks; p->tick(host, context); check(p->flags == 3 && host.clocks == clocks, "distance remainder short circuit");
    for (unsigned mode : {0u,1u,2u}) {
        p = factory.create(op(8, {}, mode)); p->begin(host, context); p->tick(host, context);
        check(p->flags == 7 && host.toggle == (mode == 1) && !context.operationActive, "toggle mode");
    }
    p = factory.create(op(6, {}, 2)); p->begin(host, context); p->tick(host, context); check(p->flags == 7, "move mode2 immediate");
    p = factory.create(op(7, {}, 3)); p->begin(host, context); host.now += 30000; p->tick(host, context); check(p->flags == 1, "move unknown mode pending");
}

static void creations() {
    Host host; RF455TutorialCreationIds ids; ids.monster = 0xffffffff; ids.item = 0xffff;
    RF455TutorialSpatialFactory factory(host, ids); RF455TutorialContext context;
    const RF455TutorialVector point{{-1.9f,32768.9f,65537.9f}};
    auto p = factory.create(op(9, point)); p->begin(host, context); p->tick(host, context);
    check(p->flags == 7 && !context.operationActive && ids.monster == 0 && host.monsters.size() == 1, "monster create and ID wrap");
    const std::array<std::uint8_t,17> monster{{0x45,0x23,1,0,255,255,255,255,255,255,0,0x80,1,0,0,0,0}};
    check(host.monsters[0] == monster, "monster17 wire fields");
    host.calls.clear();
    p = factory.create(op(10, point, 0)); p->begin(host, context); p->tick(host, context);
    check(ids.item == 0 && host.items.size() == 1 && p->flags == 7, "item create and serial wrap");
    check(host.calls == std::vector<std::string>({"item-construct","item-resolve","item-dispatch","item-destruct"}) &&
          !host.cloneActive, "temporary clone spans dispatch");
    std::array<std::uint8_t,25> item; item.fill(255); item[0] = 14; item[1] = 0x45; item[2] = 0x23; item[3] = 1;
    item[18] = 255; item[19] = 255; item[20] = 0; item[21] = 0x80; item[22] = 1; item[23] = 0;
    check(host.items[0] == item, "item known25 wire fields; no fabricated tail");
    p = factory.create(op(10, point, 46)); p->begin(host, context); p->tick(host, context); check(host.items.back()[0] == 0, "category46 pinned zero map");
    host.monsterFound = host.itemFound = false;
    const auto monsterId = ids.monster; const auto itemId = ids.item;
    for (unsigned type : {9u,10u}) {p = factory.create(op(type, point)); p->begin(host, context); p->tick(host, context); check(p->flags == 7, "missing template still finishes");}
    check(ids.monster == monsterId && ids.item == itemId, "failed lookup does not consume IDs");
    host.now = 0xfffffff0; host.pending = 1;
    p = factory.create(op(11)); p->begin(host, context); host.now = 19983; p->tick(host, context); check(p->flags == 1, "creation wait wrap before");
    host.now = 19984; p->tick(host, context); check(p->flags == 3 && !context.operationActive, "creation wait20sec equality");
    host.pending = 0; p = factory.create(op(11)); p->begin(host, context); const auto clocks = host.clocks; p->tick(host, context);
    check(p->flags == 3 && host.clocks == clocks, "creation empty short circuit");
    check(RF455_TutorialCoordinateWord(-32769.9f) == 32767 && RF455_TutorialCoordinateWord(65536.9f) == 0,
          "coordinate truncation and lowWORD wrapping");
}

int main() {
    try {
        positions(); movement(); creations();
        const auto& defaults = RF455_GetTutorialCreationIds();
        check(defaults.item == 3840 && defaults.monster == 65535, "pinned process initial counters");
        Host host; RF455TutorialCreationIds ids; RF455TutorialSpatialFactory factory(host, ids);
        FILE* mapping = std::fopen("category-map.bin","wb"); check(mapping != nullptr,"category output");
        RF455TutorialContext mapContext;
        for (unsigned category = 0; category != 47; ++category) {
            auto item = factory.create(op(10, {}, category)); item->begin(host, mapContext); item->tick(host, mapContext);
            check(std::fputc(host.items.back()[0], mapping) != EOF, "category byte");
        }
        check(std::fclose(mapping) == 0, "category close");
        unsigned records = 0, supported = 0, open = 0;
        for (const char* path : {"bw.scp","cw.scp","ar.scp"}) {
            RF455TutorialScript script; check(RF455_LoadTutorialScript(path, script), "real SCP");
            for (const auto& q : script.quests) for (const auto& instruction : q.instructions) {
                ++records; if (factory.create(instruction)) ++supported; else ++open;
            }
            RF455TutorialRuntime runtime; RF455TutorialUnsupported gap;
            check(!runtime.prepare(script, factory, &gap) && gap.selector >= 19, "remaining commands rejected explicitly");
        }
        FILE* out = std::fopen("result.json","w"); check(out != nullptr,"result");
        std::fprintf(out,"{\"status\":\"PASS\",\"position12to18\":true,\"move6to8\":true,\"creation9to11_rules\":true,"
                     "\"XZ_distance\":true,\"wire17_known25\":true,\"timeout_wrap\":true,\"counter_wrap\":true,"
                     "\"real_records\":%u,\"supported\":%u,\"open\":%u,\"production_host\":false,"
                     "\"item_tail25_resolved\":false,\"full_Tutorial\":false}\n",records,supported,open);
        check(std::fclose(out) == 0,"close result"); return 0;
    } catch (const std::exception& error) {std::fprintf(stderr,"%s\n",error.what()); return 1;}
}
