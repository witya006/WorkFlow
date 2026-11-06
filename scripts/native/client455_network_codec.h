#pragma once
#include <cstddef>
#include <cstdint>

struct RF455AesKey {
    std::uint8_t expanded[240] = {};
    unsigned rounds = 0;
    bool initialize(const std::uint8_t* key, std::size_t bytes);
    void encrypt(const std::uint8_t* input, std::uint8_t* output) const;
    void decrypt(const std::uint8_t* input, std::uint8_t* output) const;
};

struct RF455NetworkCodec {
    RF455AesKey sendKey, receiveKey;
    bool configured = false;
    bool enabled = false;
    void initializeDefault(bool encrypted);
    bool encode(std::uint16_t type, const void* payload, std::size_t bytes,
                void* output, std::size_t capacity, std::size_t& written) const;
    bool decode(const void* wire, std::size_t available, void* output,
                std::size_t capacity, std::size_t& written) const;
};
