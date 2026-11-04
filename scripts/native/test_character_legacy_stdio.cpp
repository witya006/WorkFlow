#include "character_legacy_stdio.h"
#include <cstdio>
#include <cstring>

static unsigned checks;
#define CHECK(condition) do { ++checks; if (!(condition)) { std::fprintf(stderr, "check %u at line %d failed\n", checks, __LINE__); return 1; } } while (0)
static unsigned flags(RF_LegacyFile* stream) {
    unsigned result;
    std::memcpy(&result, reinterpret_cast<unsigned char*>(stream) + 12, sizeof(result));
    return result;
}
int main() {
    CHECK(rf_vc6_fopen("missing-does-not-exist.bin", "rb") == nullptr);
    unsigned char data[513], result[800] = {};
    for (unsigned i = 0; i < sizeof(data); ++i) data[i] = static_cast<unsigned char>(i);
    RF_LegacyFile* stream = rf_vc6_fopen("binary.bin", "w+b");
    CHECK(stream != nullptr);
    CHECK(rf_vc6_fwrite(data, 3, 171, stream) == 171);
    CHECK(rf_vc6_ftell(stream) == 513);
    CHECK(rf_vc6_fseek(stream, 0, SEEK_SET) == 0);
    CHECK(rf_vc6_fread(result, 2, 256, stream) == 256);
    CHECK(rf_vc6_fread(result + 512, 1, 1, stream) == 1);
    CHECK(std::memcmp(data, result, sizeof(data)) == 0);
    CHECK(rf_vc6_fread(result, 1, 1, stream) == 0);
    CHECK((flags(stream) & 0x10) != 0);
    CHECK(rf_vc6_fseek(stream, 0, SEEK_SET) == 0);
    CHECK((flags(stream) & 0x10) == 0);
    CHECK(rf_vc6_fread(result, 0, 100, stream) == 0 && rf_vc6_ftell(stream) == 0);
    CHECK(rf_vc6_fread(result, 4, 200, stream) == 128);
    CHECK((flags(stream) & 0x10) != 0);
    CHECK(std::memcmp(data, result, 512) == 0);
    CHECK(rf_vc6_fclose(stream) == 0);
    stream = rf_vc6_fopen("binary.bin", "rb");
    CHECK(stream != nullptr);
    CHECK(rf_vc6_fwrite(data, 1, 1, stream) == 0);
    CHECK((flags(stream) & 0x20) != 0 && (flags(stream) & 0x10) == 0);
    CHECK(rf_vc6_fclose(stream) == 0);

    const char text[] = "alpha 17 1.25\r\nbeta -2 3.5\r\n";
    stream = rf_vc6_fopen("records.txt", "wb");
    CHECK(stream != nullptr);
    CHECK(rf_vc6_fwrite(text, 1, sizeof(text) - 1, stream) == sizeof(text) - 1);
    CHECK(rf_vc6_fclose(stream) == 0);
    stream = rf_vc6_fopen("records.txt", "rt");
    CHECK(stream != nullptr);
    char line[128] = {}, name[16] = {};
    CHECK(rf_vc6_fgets(line, 6, stream) == line && std::strcmp(line, "alpha") == 0);
    CHECK(rf_vc6_fgets(line, sizeof(line), stream) == line && std::strcmp(line, " 17 1.25\n") == 0);
    int number; float value;
    for (unsigned i = 0; i < 256; ++i) {
        CHECK(rf_vc6_fseek(stream, 0, SEEK_SET) == 0);
        CHECK(rf_vc6_fscanf(stream, "%15s %d %f", name, &number, &value) == 3);
        CHECK(std::strcmp(name, "alpha") == 0 && number == 17 && value == 1.25f);
        CHECK(rf_vc6_fscanf(stream, "%15s %d %f", name, &number, &value) == 3);
        CHECK(std::strcmp(name, "beta") == 0 && number == -2 && value == 3.5f);
        CHECK(rf_vc6_fscanf(stream, "%15s %d %f", name, &number, &value) == EOF);
        CHECK((flags(stream) & 0x10) != 0);
    }
    CHECK(rf_vc6_fclose(stream) == 0);
    stream = rf_vc6_fopen("malformed.txt", "rb");
    CHECK(stream != nullptr);
    CHECK(rf_vc6_fscanf(stream, "%15s %d", name, &number) == 1);
    CHECK(std::strcmp(name, "name") == 0);
    CHECK(rf_vc6_fclose(stream) == 0);
    // The modern CRT still owns its own streams, independently of this adapter.
    FILE* modern = std::fopen("binary.bin", "rb");
    CHECK(modern != nullptr);
    CHECK(std::fread(result, 1, sizeof(result), modern) == 513);
    CHECK(std::memcmp(data, result, sizeof(data)) == 0 && std::feof(modern));
    CHECK(std::fclose(modern) == 0);
    std::printf("{\"checks_passed\":%u,\"fscanf_iterations\":256,\"stream_apis\":8}\n", checks);
}
