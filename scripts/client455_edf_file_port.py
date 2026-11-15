"""Transactional EDF envelope loading and bounded legacy cursor; no table schemas."""
from client455_trade_ore_port import patch_method


def edf_file_definitions():
    """Actual emitted helper/method bodies, also usable by a standalone check.

    The real class declarations are datafile.h from `class CDataString` up to
    (excluding) `class CDataRecord`. Keep HEADER_LENGTH/MAX_KEY_LENGTH defines.
    Methods retain the return types preceding their definitions in legacy .cpp.
    """
    prefix = b'''// RF455 transactional EDF envelope
#include <windows.h>
#include "client455_character_rfs.h"
#include "client455_language.h"
#include <cstring>
#include <memory>
#include <new>
#include <stdexcept>

namespace {
bool RF455_ReadEdfSection(HANDLE file, void* buffer, DWORD size) {
    if (file == INVALID_HANDLE_VALUE || (!buffer && size)) return false;
    auto* next = static_cast<unsigned char*>(buffer);
    while (size) {
        const DWORD chunk = size > 1048576u ? 1048576u : size;
        DWORD read = 0;
        if (!ReadFile(file, next, chunk, &read, nullptr) || !read || read > chunk) return false;
        next += read; size -= read;
    }
    return true;
}

template<class DataString, std::size_t headerSize, std::size_t keySize>
BOOL RF455_PublishEdfEnvelope(char (&header)[headerSize], char (&key)[keySize], DataString& owner,
                            const unsigned char* envelope, std::size_t size) {
    static_assert(headerSize == 29 && keySize == 256, "455 EDF envelope layout");
    constexpr std::size_t envelopeOverhead = headerSize + sizeof(DWORD) + keySize;
    if (!envelope || size < envelopeOverhead) return FALSE;
    DWORD payloadSize = 0;
    memcpy(&payloadSize, envelope + headerSize, sizeof(payloadSize));
    if (payloadSize > 0x7fffffffu || payloadSize > size - envelopeOverhead) return FALSE;
    std::unique_ptr<char[]> replacement(new (std::nothrow) char[static_cast<std::size_t>(payloadSize) + 1]);
    if (!replacement || !RF455_DecodeEdf(envelope, size, replacement.get(), payloadSize)) return FALSE;
    replacement[payloadSize] = 0;
    // Reconstruct the same member type to reset its private read cursor.
    owner.~DataString();
    new (&owner) DataString();
    owner.SetStringLength(payloadSize);
    owner.SetString(replacement.release());
    memcpy(header, envelope, headerSize);
    ZeroMemory(key, keySize);
    return TRUE;
}
}
'''
    bodies = {
        (b'CDataString', b'Read'): b'''CDataString::Read(void* buffer, int size, int count) {
    if (!buffer || !m_pString || size <= 0 || count <= 0 || m_dwCurPos > m_dwStringLength) return 0;
    const std::uint64_t bytes = static_cast<std::uint64_t>(size) * static_cast<unsigned>(count);
    if (bytes > static_cast<std::uint64_t>(m_dwStringLength - m_dwCurPos)) return 0;
    const DWORD amount = static_cast<DWORD>(bytes);
    memcpy(buffer, m_pString + m_dwCurPos, amount);
    m_dwCurPos += amount; return amount;
}''',
        (b'CDataFile', b'LoadFile'): b'''CDataFile::LoadFile(char* filename) {
    if (!filename || m_hSourceFile != INVALID_HANDLE_VALUE) return FALSE;
    constexpr std::size_t maxCachedBytes = 8u * 1024u * 1024u;
    auto* cache = RF455_GetCharacterRfsCache();
    const auto budget = cache->ByteBudget();
    const auto limit = budget < maxCachedBytes ? budget : maxCachedBytes;
    // Client 455 x86 RVA 0x1EEC90/0x1EED90 reads the EDF directly.
    // Large files use the bounded chunked path with no retained encoded bytes.
    if (limit) {
        const auto source = cache->ReadLooseBytes(filename, limit);
        if (source.status == RF455ResourceReadStatus::Ready && source.bytes) {
            if (RF455_PublishEdfEnvelope(m_pHeader, m_pKey, m_cSourceData,
                                         source.bytes->data(), source.bytes->size())) return TRUE;
            // A rejected envelope must not hide a corrected file on retry.
            cache->RemoveLooseBytes(filename);
            return FALSE;
        }
        if (source.status != RF455ResourceReadStatus::ReadError || source.declaredSize <= limit)
            return FALSE;
    }
    m_hSourceFile = CreateFileA(filename, GENERIC_READ, FILE_SHARE_READ, nullptr,
        OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr);
    if (m_hSourceFile == INVALID_HANDLE_VALUE) return FALSE;
    struct CloseSource {
        HANDLE& file;
        ~CloseSource() { if (file != INVALID_HANDLE_VALUE) CloseHandle(file); file = INVALID_HANDLE_VALUE; }
    } closeSource = {m_hSourceFile};
    return LoadFile_ReadFile();
}''',
        (b'CDataFile', b'LoadFile_ReadFile'): b'''CDataFile::LoadFile_ReadFile(void) {
    if (m_hSourceFile == INVALID_HANDLE_VALUE) return FALSE;
    LARGE_INTEGER length = {}, beginning = {};
    if (!GetFileSizeEx(m_hSourceFile, &length) || length.QuadPart < 289
        || !SetFilePointerEx(m_hSourceFile, beginning, nullptr, FILE_BEGIN)) return FALSE;
    unsigned char prefix[33];
    if (!RF455_ReadEdfSection(m_hSourceFile, prefix, sizeof(prefix))) return FALSE;
    DWORD payloadSize = 0; memcpy(&payloadSize, prefix + 29, 4);
    // Existing downstream interfaces use signed sizes. Reject oversized input
    // before allocations; do not interpret arbitrary table schemas here.
    if (payloadSize > 0x7fffffffu
        || static_cast<std::uint64_t>(payloadSize) + 289u > static_cast<std::uint64_t>(length.QuadPart)) return FALSE;
    try {
        std::vector<unsigned char> envelope(static_cast<std::size_t>(payloadSize) + 289u);
        memcpy(envelope.data(), prefix, sizeof(prefix));
        if (!RF455_ReadEdfSection(m_hSourceFile, envelope.data() + 33, payloadSize + 256u)) return FALSE;
        return RF455_PublishEdfEnvelope(m_pHeader, m_pKey, m_cSourceData, envelope.data(), envelope.size());
    } catch (const std::bad_alloc&) { return FALSE; }
      catch (const std::length_error&) { return FALSE; }
}''',
        (b'CDataFile', b'LoadFile_ReadSection'): b'''CDataFile::LoadFile_ReadSection(char* buffer, int size) {
    if (size < 0 || !buffer) return FALSE;
    return RF455_ReadEdfSection(m_hSourceFile, buffer, static_cast<DWORD>(size)) ? TRUE : FALSE;
}''',
    }
    return prefix, bodies


def port_edf_file(raw, relative, section):
    if relative != 'datafile.cpp':
        return raw, False
    marker = b'// RF455 transactional EDF envelope'
    if marker in raw:
        return raw, False
    prefix, bodies = edf_file_definitions()
    raw = prefix + raw
    for (owner, name), body in bodies.items():
        raw = patch_method(raw, section, owner, name, lambda old, new=body: new)
    return raw, True
